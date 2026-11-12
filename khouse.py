#!/usr/bin/env python3
"""Kalshi "be the patient buyer" test (2026-11-12). Research only.

PAPER ONLY. Reads public history, never trades, never writes state/.

The gap this fills: every Kalshi dig so far BOUGHT at the asking price and lost the cost of buying ($4-25 per $100),
while the middle price came out fair. Nobody asked who collects that cost. Outside the 15-minute crypto windows
(kcrypto.py) we never tested the other chair: leave a buy order a cent above the best one and wait for somebody
in a hurry to sell to us. Polymarket's version died (tiny gaps, picked off). Kalshi's gaps are much wider.

Two questions, both answered from Kalshi's REAL trade list (every trade says which side was in a hurry):
  1. who earned: for every real trade, how did the patient side do when the market finished?
  2. the bot rule: once an hour, on the side the price favors, put a $10 buy order 1c above the best one (only when
     that is still below the asking price). It is filled only by contracts that were REALLY sold at our price or
     lower during the next hour (never more than was sold). Held to the result. One bet per market.
     Hourly orders are staler than the live bot's 5 minutes, so this is the harsh version.

    python3 khouse.py fetch       # probe kh_fetch: sample settled markets, hourly quotes + trade lists (resumes)
    python3 khouse.py run         # probe kh_run (or locally, data is in the price store): report backtest/khouse.md
    python3 khouse.py selftest    # offline

Data: bt_cache/khouse/ (markets.json.gz, tapes_NNN.json.gz), saved to the shared price store.
What it can't see: our order was never really in the book. Other robots may jump in front of a real order, and
that would cost us good fills more than bad ones. Only a live test with real orders can measure that.
"""
import collections
import datetime as dt
import gzip
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import exam
import launch
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "khouse")
MK = os.path.join(CACHE, "markets.json.gz")
OUT = os.path.join(ROOT, "backtest", "khouse.md")
DAY = 86400
FIRST, LAST = "2026-09-11", "2026-11-09"       # close days; 2026-11-10 on is the holdout (PROTOCOL.md)
PER_DAY = {"sports": int(os.environ.get("KH_SPORTS", "70")), "other": int(os.environ.get("KH_OTHER", "110"))}
MIN_VOL = 100
LOOKBACK = 7 * DAY
BUDGET_MIN = float(os.environ.get("KH_MIN", "150"))
WORKERS = int(os.environ.get("KH_WORKERS", "6"))
SHARD = 500
T0 = time.time()
kget = yesno.kget


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def tsec(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())


def its(x):
    d = bot.parse_iso(x) if isinstance(x, str) else None
    return int(d.timestamp()) if d else None


# ================================================================ fetch
def list_day(d0):
    """Settled markets closing on day d0 with their volume (yesno.k_day drops it)."""
    t0, t1 = d0, d0 + DAY - 1
    rows, cut = [], yesno.k_cutoff()
    for path in ("/markets", "/historical/markets"):
        if path == "/historical/markets" and (not cut or t0 >= cut):
            continue
        if path == "/markets" and cut and t1 < cut:
            continue
        cur = None
        for _ in range(400):
            p = {"min_close_ts": t0, "max_close_ts": t1, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
                p["mve_filter"] = "exclude"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  list {path} {d0} failed: {str(e)[:100]}")
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    ok, seen = [], set()
    for m in rows:
        tk = str(m.get("ticker") or "")
        ev = str(m.get("event_ticker") or "")
        s = ev.split("-")[0]
        if not tk or tk in seen or tk.startswith("KXMVE") or s.endswith("15M"):
            continue
        seen.add(tk)
        res = str(m.get("result") or "").lower()
        o, c = its(m.get("open_time")), its(m.get("close_time"))
        vol = bot.fnum(m.get("volume_fp") or m.get("volume"), 0)
        if res not in ("yes", "no") or not o or not c or not t0 <= c <= t1 or vol < MIN_VOL:
            continue
        ok.append({"t": tk, "s": s, "ev": ev, "q": f"{m.get('title') or ''} {m.get('yes_sub_title') or ''}".strip()[:140],
                   "open": o, "close": c, "exp": its(m.get("expected_expiration_time")), "res": res, "vol": vol})
    return d0, len(rows), ok


def klass(m):
    return "sports" if launch.kcategory(m["s"], m["q"]) in ("sports", "esports") else "other"


def pick_day(d0, ok):
    """One random market per event, then up to PER_DAY events per class. Returns picks and the day's weights."""
    rng = random.Random(d0)
    by_ev = collections.defaultdict(list)
    for m in ok:
        by_ev[m["ev"]].append(m)
    per = collections.defaultdict(list)
    for ev in sorted(by_ev):
        m = rng.choice(by_ev[ev])
        per[klass(m)].append(m)
    picks, info = [], {}
    for k, ms in per.items():
        got = rng.sample(ms, min(PER_DAY[k], len(ms)))
        info[k] = [len(ms), len(got)]
        picks += got
    return picks, info


def trade_row(t):
    ts = its(t.get("created_time"))
    yp = bot.fnum(t.get("yes_price_dollars"), None)
    if yp is None:
        yp = bot.fnum(t.get("yes_price"), 0) / 100
    n = bot.fnum(t.get("count_fp") or t.get("count"), 0)
    side = str(t.get("taker_side") or "")
    if ts is None or n <= 0 or side not in ("yes", "no") or not 0 < yp < 1:
        return None
    return [ts, round(yp * 1000), round(n, 2), 1 if side == "yes" else 0]


def trades_span(tk, t0, t1, pages):
    """Trades in [t0, t1], newest first. -> (rows, complete, path used)."""
    for path in ("/markets/trades", "/historical/trades"):
        out, cur, done = [], None, False
        try:
            for _ in range(pages):
                p = {"ticker": tk, "min_ts": int(t0), "max_ts": int(t1) + 1, "limit": 1000}
                if cur:
                    p["cursor"] = cur
                r = kget(path, p)
                got = r.get("trades") or []
                out += [x for x in map(trade_row, got) if x]
                cur = r.get("cursor")
                if not cur or not got:
                    done = True
                    break
        except Exception:
            continue
        if out:
            return out, done, path
    return [], True, ""


def fetch_one(m):
    a, b = max(m["open"], m["close"] - LOOKBACK), m["close"]
    cs = []
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = kget(path, {"start_ts": a - 3600, "end_ts": b, "period_interval": 60})
        except Exception:
            continue
        got = r.get("candlesticks") if isinstance(r, dict) else None
        if got:
            for c in got:
                t, bid, ask = yesno.k_candle(c)
                cs.append([t, bid, ask, bot.fnum(c.get("volume_fp") or c.get("volume"), 0)])
            break
    tr, done, path = trades_span(m["t"], a, b, 2)
    cov = [[a if done else min((x[0] for x in tr), default=b), b]]
    if not done:        # busy market (mostly live sports): also take the stretch that ends 4 hours before the close
        tr2, done2, _ = trades_span(m["t"], a, b - 4 * 3600, 3)
        if tr2:
            cov.append([a if done2 else min(x[0] for x in tr2), b - 4 * 3600])
            have = {tuple(x) for x in tr}
            tr += [x for x in tr2 if tuple(x) not in have]
    tr.sort()
    return m["t"], {"c": cs, "tr": tr, "cov": cov, "p": path}


def shard_path(i):
    return os.path.join(CACHE, f"tapes_{i:03d}.json.gz")


def fetch():
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"days": {}, "markets": {}, "fees": {}}
    days = [d for d in range(tsec(FIRST), tsec(LAST) + 1, DAY) if str(d) not in have["days"]]
    print(f"days listed before {len(have['days'])}, to list {len(days)}")
    with ThreadPoolExecutor(3) as ex:
        for d0, n, ok in ex.map(list_day, days):
            picks, info = pick_day(d0, ok)
            if not n:
                print(f"  {d0}: empty list, will retry next time")
                continue
            have["days"][str(d0)] = info
            for m in picks:
                have["markets"][m["t"]] = m
            print(f"  {dt.datetime.utcfromtimestamp(d0).date()}: {n} settled, {len(ok)} with volume, picked {info} ({time.time() - T0:.0f}s)")
    wj(MK, have)
    for s in sorted({m["s"] for m in have["markets"].values()} - set(have["fees"])):
        if time.time() - T0 > BUDGET_MIN * 60:
            break
        try:
            r = kget(f"/series/{s}").get("series") or {}
            have["fees"][s] = [r.get("fee_type"), r.get("fee_multiplier")]
        except Exception as e:
            print(f"  series {s} failed: {str(e)[:80]}")
    wj(MK, have)
    print("fee types:", collections.Counter(str(v[0]) for v in have["fees"].values()).most_common())
    order = sorted(have["markets"])
    random.Random(1).shuffle(order)
    for i in range(0, len(order), SHARD):
        if time.time() - T0 > BUDGET_MIN * 60:
            print("time budget used, run again to resume")
            break
        sp = shard_path(i // SHARD)
        got = rj(sp, {}) or {}
        todo = [have["markets"][t] for t in order[i:i + SHARD] if t not in got]
        if not todo:
            continue
        with ThreadPoolExecutor(WORKERS) as ex:
            for tk, d in ex.map(fetch_one, todo):
                got[tk] = d
        wj(sp, got)
        nt = sum(len(d["tr"]) for d in got.values())
        print(f"  shard {i // SHARD}: {len(got)} markets, {nt} trades, "
              f"{sum(1 for d in got.values() if not d['c'])} without quotes, {sum(1 for d in got.values() if not d['tr'])} without trades, "
              f"paths {collections.Counter(d['p'] for d in got.values()).most_common()} ({time.time() - T0:.0f}s)")


# ================================================================ analysis
FAMS = ("sports before the game", "sports, game on", "crypto price", "stocks", "weather", "slow questions")


def family(m, t):
    c = launch.kcategory(m["s"], m["q"])
    if c in ("sports", "esports"):
        return "sports before the game" if t < m["close"] - 4.5 * 3600 else "sports, game on"
    if c in ("crypto price", "stocks", "weather"):
        return c
    return "slow questions"


def pband(p):
    for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .8), (.8, .9), (.9, .97), (.97, 1.01)):
        if lo <= p < hi:
            return f"{lo * 100:.0f}-{min(hi, 1) * 100:.0f}c"


def left_band(sec):
    return "under 6h left" if sec < 6 * 3600 else "6-24h left" if sec < DAY else "1-7 days left"


def maker_fee(fees, s, p, n):
    ft = (fees.get(s) or [None, None])
    if "maker" not in str(ft[0] or ""):
        return 0.0
    import math
    return math.ceil(0.0175 * (bot.fnum(ft[1], 1) or 1) * n * p * (1 - p) * 100 - 1e-9) / 100


def load():
    have = rj(MK, {}) or {}
    tapes = {}
    i = 0
    while os.path.exists(shard_path(i)):
        tapes.update(rj(shard_path(i), {}) or {})
        i += 1
    return have, tapes


def covered(d, t):
    return any(a <= t <= b for a, b in d["cov"])


def who_earned(have, tapes):
    """Per real trade: the patient side's result. -> {key: [stake, profit, contracts]} and per-event rows."""
    tot = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    evs = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for tk, d in tapes.items():
        m = have["markets"][tk]
        yes = m["res"] == "yes"
        for ts, yp, n, ty in d["tr"]:
            yp = yp / 1000
            n = min(n, 500)
            # taker bought YES -> the patient side bought NO at 1 - yp
            p, pay = (1 - yp, 0.0 if yes else 1.0) if ty else (yp, 1.0 if yes else 0.0)
            fam = family(m, ts)
            for key in ((fam,), (fam, pband(p)), ("all", pband(p)), ("all",)):
                x = tot[key]
                x[0] += n * p
                x[1] += n * (pay - p)
                x[2] += n
                e = evs[key][m["ev"]]
                e[0] += n * p
                e[1] += n * (pay - p)
    return tot, evs


def band90(ev_rows):
    """Luck range of profit per $100 from whole events (each event counts once)."""
    rows = list(ev_rows.values())
    if len(rows) < 10:
        return None
    S = sum(r[0] for r in rows)
    r0 = sum(r[1] for r in rows) / S
    var = sum((r[1] - r0 * r[0]) ** 2 for r in rows) / S ** 2
    se = var ** 0.5
    return (r0 - 1.645 * se) * 100, (r0 + 1.645 * se) * 100


def sim(have, tapes, lo, hi, min_gap, side_mode="fav", usd=10.0, improve=0.01, fams=None, left=None, stale=3600):
    """The bot rule on hourly quotes + the real trade list. -> bets for exam.score (with extras)."""
    bets = []
    fees = have.get("fees") or {}
    for tk, d in tapes.items():
        m = have["markets"][tk]
        tr = d["tr"]
        if not tr or not d["c"]:
            continue
        j = 0
        for ci, (h, bid, ask, _v) in enumerate(d["c"]):
            if bid is None or ask is None or not 0 < bid < ask < 1 or h >= m["close"] - 300:
                continue
            fav_yes = (bid + ask) / 2 >= 0.5
            side_yes = fav_yes if side_mode == "fav" else not fav_yes
            b, a = (bid, ask) if side_yes else (1 - ask, 1 - bid)
            if not lo <= b < hi or a - b < min_gap - 1e-9:
                continue
            p = round(b + improve, 4)
            if p >= a - 1e-9:
                continue
            fam = family(m, h)
            if fams and fam not in fams:
                continue
            lb = left_band(m["close"] - h)
            if left and lb not in left:
                continue
            end = min(h + stale, m["close"])
            if not covered(d, h) or not covered(d, end - 1):
                continue
            want = max(1, int(usd / p))
            got, t_fill = 0.0, None
            while j < len(tr) and tr[j][0] <= h + 60:
                j += 1
            k = j
            while k < len(tr) and tr[k][0] <= end:
                ts, yp, n, ty = tr[k]
                k += 1
                if bool(ty) == side_yes:
                    continue                      # a hurried BUYER of our side doesn't sell to us
                px = yp / 1000 if side_yes else 1 - yp / 1000
                if px <= p + 1e-9:
                    got += n
                    t_fill = t_fill or ts
                    if got >= want:
                        break
            if got <= 0:
                continue
            n = min(want, got)
            win = (m["res"] == "yes") == side_yes
            fee = maker_fee(fees, m["s"], p, n)
            nxt = d["c"][ci + 1] if ci + 1 < len(d["c"]) else None
            mark = None
            if nxt and nxt[1] is not None and nxt[2] is not None and 0 < nxt[1] < nxt[2] < 1 and nxt[2] - nxt[1] <= 0.15:
                mid = (nxt[1] + nxt[2]) / 2
                mark = (mid if side_yes else 1 - mid) - p
            bets.append({"ev": m["ev"], "t": t_fill, "cost": n * p + fee, "pay": n if win else 0.0, "sh": n,
                         "fam": fam, "left": lb, "p": p, "gap": a - b, "mark": mark, "tk": tk, "s": m["s"]})
            break                                 # one bet per market
    return bets


def per100(bets):
    c = sum(b["cost"] for b in bets)
    return None if not c else (sum(b["pay"] for b in bets) - c) / c * 100


def halves(bets):
    if len(bets) < 20:
        return None, None
    bs = sorted(bets, key=lambda b: b["t"])
    return per100(bs[:len(bs) // 2]), per100(bs[len(bs) // 2:])


def ev_band(bets):
    g = collections.defaultdict(lambda: [0.0, 0.0])
    for b in bets:
        g[b["ev"]][0] += b["cost"]
        g[b["ev"]][1] += b["pay"] - b["cost"]
    return band90(g), len(g)


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


GRID_BANDS = ((0.5, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.97))
GRID_GAPS = (0.02, 0.05)


def run(score=True):
    have, tapes = load()
    L = []
    P = L.append
    nt = sum(len(d["tr"]) for d in tapes.values())
    P("# Kalshi: be the patient buyer (khouse.py)\n")
    P(f"Generated {bot.iso()}. Settled Kalshi markets that closed {FIRST} to {LAST} with 100+ contracts traded "
      f"(no 15-minute crypto, no combos): one market per event, up to {PER_DAY['sports']} sports and {PER_DAY['other']} other events a day. "
      f"{len(tapes)} markets with data, {nt:,} real trades from their last 7 days.\n")
    tot, evs = who_earned(have, tapes)
    P("## 1. Who earned on the real trades\n")
    P("Every trade has a side in a hurry (it took the price on offer) and a patient side (its order was waiting). "
      "This is the patient side's profit per $100 it put in, held to the result, before any fee. Trades over 500 contracts count as 500.\n")
    P("| kind | patient side per $100 | luck range | contracts | events |")
    P("|---|---|---|---|---|")
    for fam in ("all",) + FAMS:
        x = tot.get((fam,))
        if not x or not x[0]:
            continue
        bd = band90(evs[(fam,)])
        P(f"| {fam} | {usd(x[1] / x[0] * 100)} | {'-' if not bd else usd(bd[0]) + ' to ' + usd(bd[1])} | {x[2]:,.0f} | {len(evs[(fam,)])} |")
    P("\nBy the price the patient side paid:\n")
    bands = [pband(x) for x in (.05, .2, .4, .6, .75, .85, .93, .98)]
    P("| kind | " + " | ".join(bands) + " |")
    P("|---|" + "---|" * len(bands))
    for fam in ("all",) + FAMS:
        cells = []
        for b in bands:
            x = tot.get((fam, b))
            cells.append("-" if not x or len(evs[(fam, b)]) < 25 else f"{usd(x[1] / x[0] * 100)} ({len(evs[(fam, b)])})")
        P(f"| {fam} | " + " | ".join(cells) + " |")
    P("\n(In brackets: events. Cells with under 25 events are left out.)\n")

    P("## 2. The bot rule: a $10 buy order 1c above the best one, refreshed once an hour\n")
    P("Filled only by contracts really sold at our price or lower in the next hour. One bet per market, held to the result. "
      "'Price after' = how the middle price stood at the next hour mark compared with what we paid (minus = we were sold to just before it fell).\n")
    cells = []
    for mode in ("fav", "dog"):
        for lo, hi in GRID_BANDS:
            for g in GRID_GAPS:
                bets = sim(have, tapes, lo, hi, g, mode)
                for fam in FAMS:
                    fb = [b for b in bets if b["fam"] == fam]
                    if len(fb) < 40:
                        continue
                    h1, h2 = halves(fb)
                    bd, ne = ev_band(fb)
                    mk = [b["mark"] for b in fb if b["mark"] is not None]
                    cells.append({"mode": mode, "lo": lo, "hi": hi, "gap": g, "fam": fam, "n": len(fb), "ev": ne, "r": per100(fb),
                                  "h1": h1, "h2": h2, "band": bd, "mark": sum(mk) / len(mk) * 100 if mk else None,
                                  "won": sum(1 for b in fb if b["pay"] > 0)})
    tries = len(cells)
    P(f"{tries} versions looked at (side x price x gap x kind of market, 40+ bets each).\n")
    P("| side | best buy order at | gap at least | kind | bets | won | per $100 | luck range | first half | second half | price after |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in sorted(cells, key=lambda c: (c["mode"], FAMS.index(c["fam"]), c["lo"], c["gap"])):
        bd = c["band"]
        P(f"| {'the likely side' if c['mode'] == 'fav' else 'the unlikely side'} | {c['lo'] * 100:.0f}-{c['hi'] * 100:.0f}c | {c['gap'] * 100:.0f}c | {c['fam']} | {c['n']} | {c['won']} | "
          f"{usd(c['r'])} | {'-' if not bd else usd(bd[0]) + ' to ' + usd(bd[1])} | {usd(c['h1'])} | {usd(c['h2'])} | "
          f"{'-' if c['mark'] is None else f'{c['mark']:+.1f}c'} |")
    good = [c for c in cells if c["h1"] is not None and c["h1"] > 0 and c["h2"] > 0 and c["band"] and c["band"][0] > 0]
    P(f"\nAhead in both halves with the low end of the luck range above $0: **{len(good)} of {tries}**. "
      f"Luck alone would give about {tries * 0.05 * 0.5:.0f}-{tries * 0.05:.0f}.\n")
    for c in good:
        P(f"- {c['mode']} {c['lo'] * 100:.0f}-{c['hi'] * 100:.0f}c gap {c['gap'] * 100:.0f}c+ {c['fam']}: {usd(c['r'])} on {c['n']} bets")

    P("\n## 3. The exam\n")
    # Fixed before looking: the plain rule. Likely side, best buy order at 80-97c, gap 2c+, no live sports.
    main = [b for b in sim(have, tapes, 0.80, 0.97, 0.02, "fav") if b["fam"] != "sports, game on"]
    cards = []
    for name, bets in (("Kalshi patient buyer: likely side at 80-97c, buy order 1c above the best one, hourly, no live sports", main),):
        if len(bets) < 10:
            P(f"{name}: only {len(bets)} bets, no card.\n")
            continue
        card = exam.score([{k: b[k] for k in ("ev", "t", "cost", "pay", "sh")} for b in bets], name, tries=max(1, tries),
                          src="khouse.py, backtest/khouse.md", log=score, quiet=True)
        cards.append(card)
        P("```\n" + exam.card_text(card) + "\n```\n")
        by = collections.defaultdict(list)
        for b in bets:
            by[b["fam"]].append(b)
        P("| kind | bets | won | per $100 | first half | second half |")
        P("|---|---|---|---|---|---|")
        for fam in FAMS:
            fb = by.get(fam)
            if fb:
                h1, h2 = halves(fb)
                P(f"| {fam} | {len(fb)} | {sum(1 for b in fb if b['pay'] > 0)} | {usd(per100(fb))} | {usd(h1)} | {usd(h2)} |")
        days = (tsec(LAST) - tsec(FIRST)) / DAY + 1
        P(f"\nBets in this sample: about {len(bets) / days:.0f} a day. The sample is a slice of Kalshi, so a live bot would see more.\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return cells, cards


# ================================================================ selftest
def selftest():
    m = {"t": "A-1", "s": "KXFOO", "ev": "A", "q": "Will it happen?", "open": 0, "close": 100000, "exp": None, "res": "yes", "vol": 500}
    have = {"markets": {"A-1": m}, "fees": {"KXFOO": ["quadratic", 1]}}
    # hour mark 3600: YES bid 90 ask 95 -> our bid 91c. A seller hits 90c at 4000 (5 contracts), then 20 more at 91c.
    tapes = {"A-1": {"c": [[3600, 0.90, 0.95, 5], [7200, 0.92, 0.94, 3]], "cov": [[0, 100000]],
                     "tr": [[3620, 900, 50, 0], [4000, 900, 5, 0], [4100, 950, 9, 1], [4200, 910, 20, 0]]}}
    b = sim(have, tapes, 0.8, 0.97, 0.02)
    assert len(b) == 1 and b[0]["sh"] == 10 and abs(b[0]["cost"] - 9.1) < 1e-9 and b[0]["pay"] == 10, b
    assert abs(b[0]["mark"] - 0.02) < 1e-9
    # the trade 20 s after the hour mark is before our order could be in: not ours. Only 5 sold -> 5 filled.
    tapes["A-1"]["tr"] = tapes["A-1"]["tr"][:3]
    b = sim(have, tapes, 0.8, 0.97, 0.02)
    assert b[0]["sh"] == 5, b
    # gap of 1c: no room to step in front -> no bet. Unlikely side: NO bid 5c -> outside the band.
    tapes["A-1"]["c"] = [[3600, 0.90, 0.91, 5]]
    assert not sim(have, tapes, 0.8, 0.97, 0.01)
    # who earned: taker sold YES at 90c to a patient buyer, YES won -> patient side +10c on 90c
    tot, _ = who_earned(have, {"A-1": {"tr": [[4000, 900, 10, 0]], "c": [], "cov": [[0, 1e9]]}})
    x = tot[("all",)]
    assert abs(x[0] - 9) < 1e-9 and abs(x[1] - 1) < 1e-9
    have["fees"]["KXFOO"] = ["quadratic_with_maker_fees", 1]
    assert maker_fee(have["fees"], "KXFOO", 0.5, 10) == 0.05
    assert trade_row({"created_time": "2026-10-01T00:00:00Z", "yes_price": 37, "count": 3, "taker_side": "no"})[1:] == [370, 3, 0]
    print("khouse selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "fetch":
        fetch()
    elif cmd == "run":
        run()
    elif cmd == "all":
        fetch()
        run()
    elif cmd == "peek":
        d0, n, ok = list_day(tsec("2026-10-20"))
        print("listed", n, "ok", len(ok), "cutoff", yesno.k_cutoff())
        picks, info = pick_day(d0, ok)
        print(info, collections.Counter(launch.kcategory(m["s"], m["q"]) for m in picks).most_common())
        for m in sorted(picks, key=lambda m: -m["vol"])[:3] + picks[:6]:
            tk, d = fetch_one(m)
            print(m)
            print("  candles", len(d["c"]), d["c"][-3:], "trades", len(d["tr"]), d["tr"][:2], d["tr"][-2:], "cov", d["cov"], d["p"])
        print(kget(f"/series/{picks[0]['s']}"))
        print(kget("/markets/trades", {"ticker": picks[0]["t"], "limit": 2}))
    elif cmd == "selftest":
        selftest()
    else:
        sys.exit(f"unknown command {cmd}")
