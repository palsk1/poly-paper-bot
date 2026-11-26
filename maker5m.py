#!/usr/bin/env python3
"""Being the seller (maker) on Polymarket's Bitcoin 5-minute windows (26 Nov 2026, Jan: "If they have this sellers
advantage doesn't it make more sense to be one?"). PAPER ONLY, research: reads the speed check's logs, never trades.

The idea: keep a small waiting offer on both sides of the Up book (sell Up at the best ask = buy Down at 1 - ask,
and buy Up at the best bid), follow the best price as it moves, and pull an offer when Bitcoin jumps against it.
A waiting order pays no fee and can earn Polymarket's maker rebate. The danger is being "picked off": a fast buyer
takes our old offer right after Bitcoin moved, and we hold the losing side to the end.

Data: the speed check box (quoter/speedcheck.py), release `speed-data`: the top of the Up book ("bk": best bid / ask
and their sizes, written when a best price moves or its size changes 20+ in 100), every trade ("tr": price, shares,
taker side on that token, Polymarket's match time `e`), Binance Bitcoin prices ("bn"), window results ("res").

How a fill is counted (no guesses about our own place beyond what the log shows):
  - Our order joins the BACK of the queue at the best price. Shares ahead of us = the size shown at that price.
    That number only shrinks (trades at our price, or the shown size dropping below it).
  - A trade fills us only if it is on our side, at our price or through it, and after the shares ahead of us.
    A trade at a price through ours (a sweep) fills our whole order.
  - Every action (new order, move, pull) takes effect `delay` ms after the event that caused it, measured on
    this box's clock. The box already hears Polymarket ~22 ms late. A trade's match time on our clock is taken
    as its arrival time minus 22 ms. Polymarket holds buys on crypto windows 150 ms before matching (since 4 Sep);
    a seller's pull is not held, so a pull that lands before the match saves us. That is what the delays test.
  - Our order is not in the real log, so a buyer who took ours would not have taken someone else's. Small sizes
    (5 shares) keep that effect small.

    python3 maker5m.py prep speed-2026111*.jsonl.gz      # one pass over the logs -> bt_cache/mk5/<day>.pkl.gz
    python3 maker5m.py run                                # every rule x delay -> backtest/maker5m_tables.md
"""
import bisect
import collections
import glob
import gzip
import json
import math
import os
import pickle
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "bt_cache", "mk5")
WIN = 300
FEE = 0.07            # taker fee rate we measured on real fills on 17 Nov (docs now say 0.05)
REBATE = 0.20         # makers' share of the taker fee on their fills (the old flat program; moving to volume tiers)
FEED_LAG = 22         # median ms from Polymarket's match time to this box hearing the trade


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ---------------------------------------------------------------- prep: logs -> per-window event lists
def prep(paths):
    os.makedirs(CACHE, exist_ok=True)
    for p in sorted(paths):
        day = os.path.basename(p).split("-")[1][:8]
        bn, wins, res = [], collections.defaultdict(lambda: {"bk": [], "tr": []}), {}
        op = gzip.open if p.endswith(".gz") else open
        with op(p, "rt") as fh:
            for line in fh:
                if line.startswith(('{"k":"c', '{"k":"a', '{"k":"k', '{"k":"b', '{"k":"p')) and not line.startswith(('{"k":"bn"', '{"k":"bk"')):
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                k = o.get("k")
                if k == "bn":
                    bn.append((o["r"], o["p"]))
                elif k in ("bk", "tr", "res") and o.get("c", "btc") != "btc":
                    continue
                elif k == "bk" and o.get("o") == "Up":
                    wins[o["w"]]["bk"].append((o["r"], o.get("bb"), o.get("bs") or 0.0, o.get("ba"), o.get("as") or 0.0))
                elif k == "tr":
                    # in Up-book terms: side "a" = a buyer took an Up sell offer (Up BUY, or Down SELL at 1-p),
                    # side "b" = a seller hit an Up buy offer (Up SELL, or Down BUY at 1-p)
                    up = o["o"] == "Up"
                    buy = str(o.get("sd")).upper() == "BUY"
                    side = "a" if up == buy else "b"
                    px = o["p"] if up else round(1 - o["p"], 4)
                    wins[o["w"]]["tr"].append((o["r"], side, px, float(o.get("s") or 0)))
                elif k == "res":
                    res[o["w"]] = o["up_won"]
        bn.sort()
        out = {"bn": bn, "res": res, "wins": {w: {"bk": sorted(v["bk"], key=lambda x: x[0]), "tr": sorted(v["tr"], key=lambda x: x[0])} for w, v in wins.items()}}
        with gzip.open(os.path.join(CACHE, f"{day}.pkl.gz"), "wb") as fh:
            pickle.dump(out, fh, protocol=4)
        print(day, len(bn), "prices", len(out["wins"]), "windows", len(res), "results", flush=True)


def load_days():
    days = {}
    for f in sorted(glob.glob(os.path.join(CACHE, "*.pkl.gz"))):
        with gzip.open(f, "rb") as fh:
            days[os.path.basename(f)[:8]] = pickle.load(fh)
    return days


# ---------------------------------------------------------------- the seller replay
class Side:
    __slots__ = ("q", "ahead", "rem", "live", "target", "pend")

    def __init__(self):
        self.q = None        # price of our live order (None = no order)
        self.ahead = 0.0     # shares in front of us at q
        self.rem = 0.0       # our shares still waiting
        self.live = 0        # time our order became live
        self.target = None   # price we last decided on (None = stay out)
        self.pend = []       # [(time it takes effect, price or None)]


def window_fair(bn_t, bn_p, w):
    """fair_up(r) like speedcheck.score: Binance move since the start, volatility from the last 15 minutes."""
    def price_at(r):
        i = bisect.bisect_right(bn_t, r) - 1
        return bn_p[i] if i >= 0 else None
    s0 = price_at(w * 1000)
    if not s0:
        return None
    hist = [price_at((w - k) * 1000) for k in range(0, 901, 5)]
    rets = [math.log(hist[i] / hist[i + 1]) for i in range(len(hist) - 1) if hist[i] and hist[i + 1]]
    if len(rets) < 100:
        return None
    sig = statistics.pstdev(rets) / math.sqrt(5)
    if sig <= 0:
        return None

    def fair_up(r, s=None):
        s = s or price_at(r)
        left = (w + WIN) - r / 1000
        if not s or left <= 1:
            return None
        return norm_cdf(math.log(s / s0) / (sig * math.sqrt(left)))
    return fair_up


def replay(win, w, up_won, fair_up, bn_t, bn_p, delay=250, rule="plain", size=5.0, cap=20.0, side_max=60.0,
           stop_left=20, band=(0.05, 0.95), jump=0.02, hold=2000, guard=0.0):
    """One window. Rules:
         plain  - always join the best bid and best ask, follow them as they move
         pull   - plain, but when Binance moves a side's fair price `jump`+ within 2 s, pull the offer that move
                  hurts for `hold` ms (Up fair up -> pull our Up sell offer; down -> pull our Up buy offer)
         guard  - only keep an offer while it is at least `guard` away from the Binance fair price on the safe side
                  (sell >= fair + guard, buy <= fair - guard), checked at every price and book change
       Each fill is a bet held to the result. Returns a list of fills (time, side, price, shares)."""
    sides = {"a": Side(), "b": Side()}
    fills = []
    net = 0.0                 # Up shares we hold (+ after buy fills, - after sell fills)
    done = {"a": 0.0, "b": 0.0}
    bb = ba = None
    bs = as_ = 0.0
    fair = None
    blocked = {"a": 0, "b": 0}
    end = (w + WIN - stop_left) * 1000

    # merged event stream: (time, kind, payload)
    ev = [(x[0], 1, x) for x in win["bk"]] + [(x[0] - FEED_LAG, 2, x) for x in win["tr"]]
    if rule != "plain":
        i0 = bisect.bisect_left(bn_t, w * 1000 - 3000)
        i1 = bisect.bisect_left(bn_t, (w + WIN) * 1000)
        ev += [(bn_t[i], 0, bn_p[i]) for i in range(i0, i1)]
    ev.sort(key=lambda e: (e[0], e[1]))
    hist = collections.deque()     # (time, fair) of the last 2 s

    def apply_pending(s, now):
        while s.pend and s.pend[0][0] <= now:
            t, px = s.pend.pop(0)
            if px is None:
                s.q, s.rem = None, 0.0
                continue
            s.q, s.rem, s.live = px, size, t
            top_px, top_sz = (ba, as_) if s is sides["a"] else (bb, bs)
            if top_px is None:
                s.ahead = 0.0
            elif abs(px - top_px) < 1e-9:
                s.ahead = top_sz
            elif (s is sides["a"] and px < top_px) or (s is sides["b"] and px > top_px):
                s.ahead = 0.0          # the book moved away: we are alone at the front
            else:
                s.ahead = 1e12         # the book moved past us: only a sweep through our price fills us

    def decide(now):
        for k, s in sides.items():
            want = None
            top = ba if k == "a" else bb
            ok = (top is not None and bb is not None and ba is not None and ba - bb > 0.005
                  and band[0] <= top <= band[1] and now < end and now >= blocked[k])
            if ok:
                if k == "a" and (net <= -cap or done["a"] >= side_max):
                    ok = False
                if k == "b" and (net >= cap or done["b"] >= side_max):
                    ok = False
            if ok and rule == "guard":
                if fair is None:
                    ok = False
                elif k == "a" and top < fair + guard:
                    ok = False
                elif k == "b" and top > fair - guard:
                    ok = False
            if ok:
                want = round(top, 4)
            if want != s.target:
                s.target = want
                s.pend.append((now + delay, want))

    for t, kind, x in ev:
        for s in sides.values():
            apply_pending(s, t)
        if kind == 0:              # Binance price
            f = fair_up(t, x)
            if f is None:
                continue
            fair = f
            if rule == "pull":
                hist.append((t, f))
                while hist and hist[0][0] < t - 2000:
                    hist.popleft()
                d = f - hist[0][1]
                if d >= jump and blocked["a"] < t:
                    blocked["a"] = t + hold
                    hist.clear()
                elif d <= -jump and blocked["b"] < t:
                    blocked["b"] = t + hold
                    hist.clear()
            decide(t)
        elif kind == 1:            # book top
            _, bb, bs, ba, as_ = x
            for k, s in sides.items():
                top_px, top_sz = (ba, as_) if k == "a" else (bb, bs)
                if s.q is not None and top_px is not None and abs(s.q - top_px) < 1e-9:
                    s.ahead = min(s.ahead, top_sz)
            decide(t)
        else:                      # trade, t = match time on our clock
            _, sd, px, z = x
            s = sides[sd]
            if s.q is None or s.rem <= 0 or s.live > t:
                continue
            through = px > s.q + 1e-9 if sd == "a" else px < s.q - 1e-9
            at = abs(px - s.q) < 1e-9
            if not (through or at):
                continue
            if through:
                got = s.rem
                s.ahead = 0.0
            else:
                got = min(s.rem, max(0.0, z - s.ahead))
                s.ahead = max(0.0, s.ahead - z)
            if got <= 0:
                continue
            s.rem -= got
            done[sd] += got
            net += got if sd == "b" else -got
            fills.append((t, sd, s.q, got))
            if s.rem <= 1e-9:      # filled: put a fresh order at the back after our delay
                s.q, s.target = None, None
            decide(t)
    out = []
    for t, sd, q, sh in fills:
        if sd == "a":              # sold Up at q = bought Down at 1 - q
            cost, pay = sh * (1 - q), sh * (0 if up_won else 1)
        else:
            cost, pay = sh * q, sh * (1 if up_won else 0)
        out.append({"t": t, "sd": sd, "q": q, "sh": sh, "cost": cost, "pay": pay,
                    "rebate": REBATE * FEE * sh * q * (1 - q)})
    return out


def run_all(days, delay, rule, **kw):
    per_win = []
    for day, d in sorted(days.items()):
        bn_t = [x[0] for x in d["bn"]]
        bn_p = [x[1] for x in d["bn"]]
        for w, win in sorted(d["wins"].items()):
            if w not in d["res"] or not win["bk"]:
                continue
            fu = window_fair(bn_t, bn_p, w)
            if fu is None:
                continue
            f = replay(win, w, d["res"][w], fu, bn_t, bn_p, delay=delay, rule=rule, **kw)
            per_win.append({"w": w, "day": day, "fills": f})
    return per_win


def summary(per_win, seed=3):
    rows = []
    for x in per_win:
        c = sum(f["cost"] for f in x["fills"])
        p = sum(f["pay"] for f in x["fills"])
        rb = sum(f["rebate"] for f in x["fills"])
        a = sum(f["sh"] for f in x["fills"] if f["sd"] == "a")
        b = sum(f["sh"] for f in x["fills"] if f["sd"] == "b")
        rows.append({"w": x["w"], "day": x["day"], "cost": c, "pnl": p - c, "rb": rb, "pairs": min(a, b), "n": len(x["fills"])})
    cost = sum(r["cost"] for r in rows)
    pnl = sum(r["pnl"] for r in rows)
    rb = sum(r["rb"] for r in rows)
    byday = collections.defaultdict(float)
    for r in rows:
        byday[r["day"]] += r["pnl"]
    nd = max(1, len(byday))
    rnd = random.Random(seed)
    act = [r for r in rows if r["cost"] > 0]
    bs = []
    for _ in range(400):
        smp = [act[rnd.randrange(len(act))] for _ in act] if act else []
        c = sum(r["cost"] for r in smp)
        bs.append(100 * sum(r["pnl"] for r in smp) / c if c else 0)
    bs.sort()
    return {"windows": len(rows), "active": len(act), "fills": sum(r["n"] for r in rows), "cost": cost, "pnl": pnl,
            "rb": rb, "per100": 100 * pnl / cost if cost else 0, "lo": bs[20] if bs else 0, "hi": bs[380] if bs else 0,
            "day_pnl": pnl / nd, "day_rb": rb / nd, "worst_day": min(byday.values()) if byday else 0,
            "best_day": max(byday.values()) if byday else 0, "byday": dict(byday),
            "max_out": max((r["cost"] for r in rows), default=0), "worst_win": min((r["pnl"] for r in rows), default=0),
            "rows": rows}


def report(days, say=print):
    import exam
    for rule, kw, d in (("pull", {"jump": 0.01}, 100), ("pull", {"jump": 0.02}, 250), ("plain", {}, 250)):
        pw = run_all(days, d, rule, **kw)
        s = summary(pw)
        say(f"== {rule} {kw} {d} ms: {s['fills']} fills, ${s['cost']:,.0f} locked in bets, P&L ${s['pnl']:,.0f} "
            f"({s['per100']:+.2f} per $100, range {s['lo']:+.2f}..{s['hi']:+.2f}), rebate at most ${s['rb']:,.0f}")
        say("   by day:", {k[4:]: round(v) for k, v in sorted(s["byday"].items())})
        # where it comes from: Binance fair move in the 2 s before each fill, from our side's view
        bk = collections.defaultdict(lambda: [0.0, 0.0, 0])
        band = collections.defaultdict(lambda: [0.0, 0.0, 0])
        for day, dd in sorted(days.items()):
            bn_t = [x[0] for x in dd["bn"]]
            bn_p = [x[1] for x in dd["bn"]]
            for x in (y for y in pw if y["day"] == day):
                fu = window_fair(bn_t, bn_p, x["w"])
                for f in x["fills"]:
                    a, b0 = fu(f["t"]), fu(f["t"] - 2000)
                    if a is None or b0 is None:
                        continue
                    mv = (a - b0) * (1 if f["sd"] == "b" else -1)   # + = Bitcoin moved our way
                    key = "moved against us 1c+" if mv <= -0.01 else ("moved our way 1c+" if mv >= 0.01 else "quiet")
                    for tab, kk in ((bk, key), (band, f"{int(f['q'] * 10) * 10}-{int(f['q'] * 10) * 10 + 10}c")):
                        tab[kk][0] += f["pay"] - f["cost"]
                        tab[kk][1] += f["cost"]
                        tab[kk][2] += 1
        for name, tab in (("Bitcoin in the 2 s before the fill", bk), ("price of our offer (Up book)", band)):
            say("  ", name)
            for kk, (p, c, n) in sorted(tab.items()):
                say(f"     {kk:24} {n:6} fills, ${c:9,.0f} locked, P&L ${p:8,.0f} = {100 * p / c if c else 0:+.2f} per $100")
        bets = [{"ev": x["w"], "t": x["w"], "cost": r["cost"], "pay": r["cost"] + r["pnl"]}
                for x, r in zip(pw, s["rows"]) if r["cost"] > 0]
        exam.score(bets, f"BTC 5-min seller {rule} {kw} {d}ms", tries=len(GRID) * 4, src="maker5m.py report",
                   log=(rule == "pull" and d == 250))
    # the smallest set-up a $100 bank could run: 5-share offers, at most 5 shares one way, 10 a side per window
    for d in (100, 250):
        s = summary(run_all(days, d, "pull", jump=0.02, cap=5.0, side_max=10.0))
        say(f"== small bank: pull 2c, {d} ms, 5-share offers, cap 5 one way, 10 a side: {s['fills']} fills, "
            f"${s['cost']:,.0f} locked, {s['per100']:+.2f} per $100, ${s['day_pnl']:,.2f} a day, rebate at most "
            f"${s['day_rb']:,.2f} a day, worst day ${s['worst_day']:,.0f}, most in one window ${s['max_out']:,.0f}")


GRID = [("plain", {}), ("pull", {"jump": 0.02}), ("pull", {"jump": 0.03}), ("pull", {"jump": 0.01}),
        ("guard", {"guard": 0.0}), ("guard", {"guard": 0.01}), ("guard", {"guard": 0.02}), ("guard", {"guard": 0.04})]
_DAYS = None


def _init():
    global _DAYS
    _DAYS = load_days()


def _job(a):
    rule, delay, kw = a
    s = summary(run_all(_DAYS, delay, rule, **kw))
    return {"rule": rule, "kw": kw, "delay": delay,
            **{k: round(v, 3) if isinstance(v, float) else v for k, v in s.items() if k != "rows"}}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "prep":
        prep(sys.argv[2:])
        return
    days = load_days()
    if cmd == "grid":          # python3 maker5m.py grid <part> <parts>: one process, prints a line per job
        part, parts = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
        global _DAYS
        _DAYS = days
        jobs = [(r, d, kw) for d in (0, 100, 250, 500) for r, kw in GRID]
        for i, j in enumerate(jobs):
            if i % parts == part:
                print(json.dumps(_job(j)), flush=True)
        return
    if cmd == "report":        # breakdowns + the exam, for the write-up
        report(days)
        return
    if cmd == "one":
        rule, delay = sys.argv[2], int(sys.argv[3])
        s = summary(run_all(days, delay, rule))
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items() if k not in ("rows", "byday")})
        print({k: round(v, 2) for k, v in sorted(s["byday"].items())})


if __name__ == "__main__":
    main()
