#!/usr/bin/env python3
"""What do kc_maker's losing bets have in common? (26 Nov 2026, Jan: "how can we make it have more days like this?"
after paper kc_maker made +$22 in a day with no losses.)

PAPER ONLY. Reads cached public history and never trades.

kc_maker bids one tick above the best bid on the winning side of a Kalshi 15-minute crypto window when that bid is
95c+, from 5.5 to 0.75 minutes left, and holds to the result. A win pays about 30c on a $10 bid, a flip costs about
$9.60, so a good day is a day with no flips. This dig builds every bet the rule would have made in the 4-month
history (the live bot's way: the first minute end that fits, one bid a window, fills from later real trades at or
below the bid), writes down what the market looked like at the moment of the bid, and asks which of those things
the flips share. Skip rules are picked on the find months (before 15 Oct) and only then scored on the check months
(15 Oct - 24 Nov).

    python3 kcflip.py run      # writes backtest/kcflip.md
Data: `python3 store.py pull bt_cache/kc bt_cache/kidx` (same as kearly.py).
"""
import datetime as dt
import math
import os
import random
from collections import defaultdict

import bot
import kcrypto as kc

UTC = dt.timezone.utc
OUT = os.path.join(bot.ROOT, "backtest")
SPLIT = int(dt.datetime(2026, 10, 15, tzinfo=UTC).timestamp())
EPS = 1e-9
STAKE = 10.0


def tick(p):
    return 0.001 if p >= 0.9 - EPS else 0.01


def spot_ret(w, t, k):
    """log return of Binance over the last k minutes, None without data."""
    a, b = w["spot"].get(str(t - 60 * k)), w["spot"].get(str(t))
    return math.log(b / a) if a and b else None


def sd_1m(w, t, n):
    rets = []
    for i in range(n):
        a, b = w["spot"].get(str(t - 60 * (i + 1))), w["spot"].get(str(t - 60 * i))
        if a and b:
            rets.append(math.log(b / a))
    if len(rets) < max(5, n // 2):
        return None
    return math.sqrt(sum(r * r for r in rets) / len(rets))


def bet_in(w, kx):
    """kc_maker's bet in window w (first minute end from 5 to 1 minutes left with the leader's bid 95c+ and room
    to improve), with the conditions at that moment. None if the rule never bids."""
    import kdocs
    for M in (5, 4, 3, 2, 1):
        t = w["close"] - 60 * M
        r = w["c"].get(t)
        if not r:
            continue
        side = kc.leader(r)
        if not side:
            continue
        bid, ask, _, _ = kc.side_view(r, side)
        if bid is None or ask is None or bid < 0.95 - EPS:
            continue
        price = round(bid + tick(bid), 4)
        if price >= ask - EPS:
            continue
        filled = False
        si = side
        tt = t + 60
        fill_t = None
        while tt <= w["close"]:
            rr = w["c"].get(tt)
            if rr:
                lo = kc.side_view(rr, si)[2]
                if lo is not None and lo <= price + EPS:
                    filled, fill_t = True, tt
                    break
            tt += 60
        sgn = 1 if side == "yes" else -1
        zu = kc.zscore_usd(w, t, M, side)
        zb = kc.zscore(w, t, M, side)
        mins = (kx.get(w["s"]) or ({}, {}))[0]
        zk = kdocs.zk_minute(mins, w, t, M, side) if mins else None
        sd10, sd60 = sd_1m(w, t, 10), sd_1m(w, t, 60)
        r1, r3 = spot_ret(w, t, 1), spot_ret(w, t, 3)
        # Kalshi book 2 minutes before: how fresh is the lead
        old = w["c"].get(t - 120)
        bid_old = kc.side_view(old, side)[0] if old else None
        vols = [v[4] for k, v in sorted(w["c"].items()) if k <= t and len(v) > 4 and v[4] is not None]
        kvr = (vols[-1] / (sum(vols) / len(vols))) if vols and sum(vols) > 0 else None
        # share of the window's lead time this side has led (minute ends so far)
        led = [kc.leader(v) for k, v in sorted(w["c"].items()) if k <= t]
        led_share = sum(1 for x in led if x == side) / len(led) if led else None
        return {"tk": w["t"], "s": w["s"].replace("KX", "").replace("15M", ""), "t": t, "close": w["close"], "M": M,
                "side": side, "bid": bid, "ask": ask, "price": price, "spread": ask - bid, "filled": filled,
                "fill_m": None if fill_t is None else (w["close"] - fill_t) / 60,
                "won": w["res"] == side, "zu": zu, "zb": zb, "zk": zk,
                "volr": (sd10 / sd60) if sd10 and sd60 else None,
                "mom1": (sgn * r1 / sd60) if r1 is not None and sd60 else None,     # last minute's move, in typical minutes; + = toward our side
                "mom3": (sgn * r3 / (sd60 * math.sqrt(3))) if r3 is not None and sd60 else None,
                "bid_rise": (bid - bid_old) if bid_old is not None else None,
                "kvr": kvr, "led": led_share, "vol": w.get("vol")}
    return None


def build():
    import kdocs
    kx = kdocs.load_kidx()
    W = kc.load_windows()
    bets = [b for b in (bet_in(w, kx) for w in W) if b]
    # round features: other coins in the same 15 minutes
    by_close = defaultdict(list)
    for w in W:
        r = w["c"].get(w["close"] - 180)
        if r:
            sd = kc.leader(r)
            if sd:
                by_close[w["close"]].append((w["s"], sd, kc.zscore_usd(w, w["close"] - 180, 3, sd)))
    for b in bets:
        others = [x for x in by_close.get(b["close"], []) if x[0].replace("KX", "").replace("15M", "") != b["s"]]
        same = [x for x in others if (x[1] == b["side"])]
        b["n_same"] = len(same)
        b["n_others"] = len(others)
        zs = [x[2] for x in others if x[2] is not None]
        b["oth_minz"] = min(zs) if zs else None
    return bets


def pnl(b):
    return (1.0 - b["price"]) / b["price"] * STAKE if b["won"] else -STAKE


def summary(bs):
    f = [b for b in bs if b["filled"]]
    if not f:
        return {"bets": 0, "lost": 0, "usd": 0.0, "days": 0, "per100": 0.0}
    days = defaultdict(float)
    for b in f:
        days[b["t"] // 86400] += pnl(b)
    lost = sum(1 for b in f if not b["won"])
    usd = sum(days.values())
    return {"bets": len(f), "lost": lost, "usd": usd, "days": len(days), "per100": usd / (len(f) * STAKE) * 100,
            "per_day": usd / len(days), "worst": min(days.values()), "clean": sum(1 for v in days.values() if v > 0),
            "best": max(days.values())}


def all_days(bs):
    return sorted({b["t"] // 86400 for b in bs})


def daily(bs, days):
    d = {x: 0.0 for x in days}
    for b in bs:
        if b["filled"]:
            d[b["t"] // 86400] += pnl(b)
    return d


def luck(bs, days, sims=2000):
    d = list(daily(bs, days).values())
    rng = random.Random(7)
    outs = sorted(sum(d[rng.randrange(len(d))] for _ in d) / len(d) for _ in range(sims))
    return outs[int(sims * 0.05)], outs[int(sims * 0.95)]


def money(x):
    return f"{'-' if x < 0 else '+'}${abs(x):.2f}"


def loss_rate_table(bs, key, cuts, label):
    f = [b for b in bs if b["filled"] and b.get(key) is not None]
    rows = [f"| {label} | Bets | Lost | 1 loss in | $ per bet |", "|---|---|---|---|---|"]
    for lo, hi in cuts:
        g = [b for b in f if lo <= b[key] < hi]
        if not g:
            continue
        lost = sum(1 for b in g if not b["won"])
        rows.append(f"| {lo:g} to {hi:g} | {len(g):,} | {lost} | {len(g) // lost if lost else '-'} | "
                    f"{money(sum(pnl(b) for b in g) / len(g))} |")
    return rows


FEATS = {
    "zu": [(-99, 0), (0, 1), (1, 1.5), (1.5, 2), (2, 2.3), (2.3, 3), (3, 4), (4, 6), (6, 99)],
    "zk": [(-99, 0), (0, 1), (1, 1.5), (1.5, 2), (2, 2.3), (2.3, 3), (3, 4), (4, 6), (6, 99)],
    "M": [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
    "bid": [(0.95, 0.96), (0.96, 0.97), (0.97, 0.98), (0.98, 0.99), (0.99, 1)],
    "spread": [(0, 0.011), (0.011, 0.021), (0.021, 0.04), (0.04, 1)],
    "volr": [(0, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, 1.6), (1.6, 2.5), (2.5, 99)],
    "mom1": [(-99, -2), (-2, -1), (-1, -0.3), (-0.3, 0.3), (0.3, 1), (1, 2), (2, 99)],
    "mom3": [(-99, -2), (-2, -1), (-1, -0.3), (-0.3, 0.3), (0.3, 1), (1, 2), (2, 99)],
    "bid_rise": [(-1, 0), (0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 1)],
    "kvr": [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2.5), (2.5, 999)],
    "led": [(0, 0.5), (0.5, 0.8), (0.8, 0.99), (0.99, 1.01)],
    "n_same": [(0, 1), (1, 3), (3, 5), (5, 7)],
    "oth_minz": [(-99, -1), (-1, 0), (0, 1), (1, 2), (2, 99)],
}

# candidate skip rules: (name, test(b) -> True = skip). Written as families; thresholds picked on find only.
def rules():
    R = []
    for z in (1.0, 1.5, 2.0, 2.3, 2.5, 3.0):
        R.append((f"cushion under {z}", lambda b, z=z: b["zu"] is None or b["zu"] < z))
    for z in (1.0, 1.5, 2.0):
        R.append((f"Kalshi's own cushion under {z}", lambda b, z=z: b["zk"] is None or b["zk"] < z))
    for z in (1.0, 1.5, 2.0):
        R.append((f"lower of both cushions under {z}",
                  lambda b, z=z: min(b["zu"] if b["zu"] is not None else -9, b["zk"] if b["zk"] is not None else 9) < z))
    for m in (-0.5, -1.0, -1.5):
        R.append((f"last minute moved {abs(m):g}+ typical minutes against us",
                  lambda b, m=m: b["mom1"] is not None and b["mom1"] < m))
    for v in (1.5, 2.0, 2.5):
        R.append((f"coin {v:g}x jumpier than its last hour", lambda b, v=v: b["volr"] is not None and b["volr"] > v))
    for r in (0.1, 0.2):
        R.append((f"bid jumped {r * 100:.0f}c+ in 2 min", lambda b, r=r: b["bid_rise"] is not None and b["bid_rise"] >= r))
    for s in (0.021, 0.04):
        R.append((f"gap {s * 100:.0f}c+ wide", lambda b, s=s: b["spread"] >= s))
    R.append(("bid under 97c", lambda b: b["bid"] < 0.97 - EPS))
    R.append(("4-5 minutes left", lambda b: b["M"] >= 4))
    R.append(("led under 80% of the window", lambda b: b["led"] is not None and b["led"] < 0.8))
    R.append(("busy minute (2.5x usual trading)", lambda b: b["kvr"] is not None and b["kvr"] > 2.5))
    # combos built from the families above, cheap first
    for z in (1.0, 1.5, 2.0):
        for m in (-0.5, -1.0):
            R.append((f"cushion under {z} OR last minute {abs(m):g}+ against",
                      lambda b, z=z, m=m: (b["zu"] is None or b["zu"] < z) or (b["mom1"] is not None and b["mom1"] < m)))
        for v in (1.5, 2.0):
            R.append((f"cushion under {z} OR coin {v:g}x jumpier",
                      lambda b, z=z, v=v: (b["zu"] is None or b["zu"] < z) or (b["volr"] is not None and b["volr"] > v)))
    for z in (1.5, 2.0):
        R.append((f"cushion under {z}, but under {z + 1:g} when 4-5 min left",
                  lambda b, z=z: b["zu"] is None or b["zu"] < (z + 1 if b["M"] >= 4 else z)))
    for z in (1.0, 1.5, 2.0):
        R.append((f"cushion under {z} unless bid 99c+", lambda b, z=z: b["bid"] < 0.99 - EPS and (b["zu"] is None or b["zu"] < z)))
    return R


def score_rule(bs, days, test):
    keep = [b for b in bs if not test(b)]
    s = summary(keep)
    s["lo"], s["hi"] = luck(keep, days)
    d = daily(keep, days)
    s["per_day"] = sum(d.values()) / len(d)
    s["worst"] = min(d.values())
    s["clean"] = sum(1 for v in d.values() if v >= 0)
    s["ndays"] = len(d)
    return s


def run():
    bs = build()
    find = [b for b in bs if b["t"] < SPLIT]
    chk = [b for b in bs if b["t"] >= SPLIT]
    fd, cd = all_days(find), all_days(chk)
    f_all = [b for b in bs if b["filled"]]
    lost = [b for b in f_all if not b["won"]]
    L = ["# What kc_maker's losing bets have in common (26 Nov 2026)", "",
         f"Generated {bot.iso()}. Paper only. Code: `kcflip.py`. History: every Kalshi 15-minute crypto window of the 7 "
         f"coins, {dt.datetime.fromtimestamp(bs[0]['t'], UTC):%d %b} to {dt.datetime.fromtimestamp(bs[-1]['t'], UTC):%d %b %Y}. "
         "kc_maker's rule the live way: the first minute end from 5 to 1 minutes left where the winning side's best bid "
         "is 95c+, bid 1 tick above it, filled when a later trade prints at or below our bid, held to the result. "
         "$10 a bid. 'Find' = before 15 Oct (rules picked here), 'check' = 15 Oct to 24 Nov (looked at only after).", "",
         f"All filled bets: {len(f_all):,}, lost {len(lost)} (1 in {len(f_all) // max(1, len(lost))}).", "",
         "**Short answer (26 Nov):** the flips have one thing in common: the coin sat close to its start price when "
         "we bid (a small cushion). Once you know the cushion, everything else adds little or nothing: how fast the coin moved, how jumpy "
         "it was, the hour, the gap, how busy Kalshi was, other coins. Skipping bids with a cushion under 1.5 (the live "
         "bot uses 2.3, kc_maker uses none) keeps about 2 in 3 bets and drops about 3 in 4 flips. On the paper "
         "track's own 16 days (never used to pick it): +$122 instead of +$105, worst day -$3.45 instead of -$10.17, "
         "9 days with no loss instead of 1. History check months (15 Oct - 24 Nov): +$4.73 a day, worst day -$38.61, "
         "against plain +$2.32 / -$69.64, cushion 2.0 +$4.59 / -$21.24 and the live bot's 2.3 +$2.70 / -$26.23 "
         "(all at $10 bids). So 1.5 to 2.0 is the sweet spot; 2.3 gives away money. Exam: Promising, needs more bets. Caveat: the real bot checks every 15 s, so it bids the moment a coin "
         "first clears the bar, which is riskier than the paper bot's every-5-minutes look.", ""]
    # feature tables on find only
    L += ["## 1. What the flips look like (find months only)", ""]
    for k, cuts in FEATS.items():
        L += [f"### {k}", ""] + loss_rate_table(find, k, cuts, k) + [""]
    # coin and hour
    L += ["### coin", "", "| Coin | Bets | Lost | 1 loss in | $ per bet |", "|---|---|---|---|---|"]
    for c in sorted({b["s"] for b in bs}):
        g = [b for b in find if b["filled"] and b["s"] == c]
        lo = sum(1 for b in g if not b["won"])
        L.append(f"| {c} | {len(g):,} | {lo} | {len(g) // lo if lo else '-'} | {money(sum(pnl(b) for b in g) / max(1, len(g)))} |")
    L += ["", "### hour (UTC) of the bid", "", "| Hour | Bets | Lost | 1 loss in |", "|---|---|---|---|"]
    for h in range(24):
        g = [b for b in find if b["filled"] and dt.datetime.fromtimestamp(b["t"], UTC).hour == h]
        lo = sum(1 for b in g if not b["won"])
        L.append(f"| {h:02d} | {len(g):,} | {lo} | {len(g) // lo if lo else '-'} |")
    L.append("")

    # rules
    R = rules()
    base_f, base_c = score_rule(find, fd, lambda b: False), score_rule(chk, cd, lambda b: False)
    scored = []
    for name, test in R:
        sf = score_rule(find, fd, test)
        scored.append((name, test, sf))
    scored.sort(key=lambda x: -x[2]["per_day"])

    def row(name, s, base):
        return (f"| {name} | {s['bets']:,} ({s['bets'] / max(1, base['bets']) * 100:.0f} in 100 kept) | {s['lost']} | "
                f"{money(s['per_day'])} | {money(s['lo'])} to {money(s['hi'])} | {money(s['worst'])} | "
                f"{s['clean']} of {s['ndays']} |")
    head = ["| Skip rule | Bets | Lost | $ a day | Luck range | Worst day | Days not in the red |",
            "|---|---|---|---|---|---|---|"]
    L += ["## 2. Skip rules on the find months, best $ a day first", "", f"$10 bids, {len(fd)} days."] + [""] + head
    L.append(row("none (plain kc_maker)", base_f, base_f))
    for name, test, s in scored:
        L.append(row(name, s, base_f))
    top = scored[:6]
    L += ["", "## 3. The 6 best from the find months, scored on the check months (never seen)", "",
          f"{len(cd)} days."] + [""] + head
    L.append(row("none (plain kc_maker)", base_c, base_c))
    res = {}
    for name, test, _ in top:
        s = score_rule(chk, cd, test)
        res[name] = s
        L.append(row(name, s, base_c))
    for name in ("cushion under 1.5", "cushion under 2.0", "cushion under 2.3"):
        test = dict((n, t) for n, t in R)[name]
        s = score_rule(chk, cd, test)
        L.append(row(name + {"cushion under 2.0": " (like kc_maker_safe)", "cushion under 2.3": " (like the live bot)"}.get(name, " (the pick)"), s, base_c))
    L += live_check()
    L += exam_lines(bs)
    return bs, L, scored, res


def live_check(track="kc_maker", bars=(None, 1.0, 1.5, 2.0, 2.3)):
    """The paper track's own bets (real tape fills, 9 Nov on) with the cushion each had when placed, recomputed from
    the cached Binance minutes. These bets were never used to pick a rule."""
    import json
    W = {w["t"]: w for w in kc.load_windows()}
    T = json.load(open(os.path.join(bot.ROOT, "state", "tracks.json")))
    T = T.get("tracks", T)
    cl = (T.get(track) or {}).get("closed") or []
    rows = []
    for c in cl:
        w = W.get(c["ticker"])
        if not w:
            continue
        t = int(dt.datetime.fromisoformat(c["placed"].replace("Z", "+00:00")).timestamp())
        tm = t - t % 60
        zu = kc.zscore_usd(w, tm, (w["close"] - tm) / 60, c["side"])
        rows.append({"day": c["closed_at"][:10], "pnl": c["pnl"], "zu": zu, "cost": c["cost"], "tk": c["ticker"],
                     "t": t})
    days = sorted({r["day"] for r in rows})
    L = ["", f"## 4. Fresh test: the live paper track `{track}`'s own bets", "",
         f"{len(rows):,} of its {len(cl):,} finished bets fall inside the cached history ({days[0]} to {days[-1]}); "
         "real fills from Kalshi's trade list, its real $10 bids. Each bet's cushion is worked out from Binance at the "
         "minute it was placed. None of these bets were used to pick anything.", "",
         "| Skip when cushion is under | Bets kept | Lost | Total | $ a day | Worst day | Days with 0 losses |",
         "|---|---|---|---|---|---|---|"]
    for bar in bars:
        g = [r for r in rows if bar is None or (r["zu"] is not None and r["zu"] >= bar)]
        d = {x: [0.0, 0] for x in days}
        for r in g:
            d[r["day"]][0] += r["pnl"]
            d[r["day"]][1] += r["pnl"] < 0
        tot = sum(v[0] for v in d.values())
        L.append(f"| {'nothing (plain kc_maker)' if bar is None else bar} | {len(g):,} | {sum(r['pnl'] < 0 for r in g)} | "
                 f"{money(tot)} | {money(tot / len(d))} | {money(min(v[0] for v in d.values()))} | "
                 f"{sum(1 for v in d.values() if v[1] == 0)} of {len(d)} |")
    L.append("")
    return L


def exam_lines(bs):
    import exam
    out = ["## 5. Exam", ""]
    for name, test in (("kc_maker skip cushion under 1.5, check months", lambda b: b["zu"] is None or b["zu"] < 1.5),):
        g = [b for b in bs if b["filled"] and b["t"] >= SPLIT and not test(b)]
        card = exam.score([{"cost": b["price"] * STAKE, "pay": STAKE if b["won"] else 0.0, "t": b["t"], "ev": b["tk"]}
                           for b in g], name, tries=len(rules()), src="kcflip.py", quiet=True)
        out.append(f"- {name}: {card['bets']:,} bets, {card.get('verdict')}")
    out.append("")
    return out


if __name__ == "__main__":
    import sys
    bs, L, scored, res = run()
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        open(os.path.join(OUT, "kcflip.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
