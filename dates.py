#!/usr/bin/env python3
"""Date-ladder bets: "Will X happen before <date>?" on Kalshi (Starship flights, AI model releases, and every other
Kalshi series whose answers are dates). Do these ladders price "soon" too high, because things slip? backtest/dates.md.

PAPER ONLY. Reads public Kalshi data, never trades, never writes state/.

  python3 dates.py scan      (probe dl_scan: every Kalshi series whose answers look like dates, with size)
  python3 dates.py fetch     (probe dl_fetch: settled markets + hourly bid/ask + every trade -> bt_cache/dl/)
  python3 dates.py report [log]
"""
import collections
import datetime as dt
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import khouse
import kmentions as km
import yesno

CACHE = os.path.join(bt.CACHE, "dl")
MK = os.path.join(CACHE, "markets.json.gz")
SCAN = os.path.join(CACHE, "scan.json.gz")
rj, wj = khouse.rj, khouse.wj
d10 = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")
MON = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
# an answer that is a deadline: "Before May 22", "By Dec 31, 2026", "Before 2027", "Before Q3"
DATE_W = re.compile(rf"^\s*(before|by|on or before|prior to)\s+({MON}|\d{{4}}|q[1-4]|end of|the end)", re.I)
TITLE_RX = re.compile(r"\bwhen\b|release|launch|before|announce|debut|unveil|\bipo\b|land|happen|first|date|"
                      r"open|ship|return|resume|confirm|arrive|reach|end\b|start|deliver|available|out\b", re.I)
SKIP_CAT = ("Sports", "Mentions", "Crypto", "Climate and Weather")
LIFE = 120 * 86400          # tapes: at most the last 120 days of a market (date ladders live for months)


def scan():
    """Every series whose settled answers are mostly deadlines ("Before X"), sorted by contracts traded."""
    os.makedirs(CACHE, exist_ok=True)
    ser = yesno.kget("/series", {}).get("series") or []
    pick = [s for s in ser if s.get("ticker") and s.get("category") not in SKIP_CAT
            and TITLE_RX.search(str(s.get("title")) + " " + s["ticker"])]
    print("Kalshi series", len(ser), "| looked at", len(pick), flush=True)
    info = {s["ticker"]: s for s in pick}
    out = {}
    with ThreadPoolExecutor(6) as ex:
        for t, ok, n in ex.map(km.series_markets, sorted(info)):
            if not ok:
                continue
            v = list(ok.values())
            dl = [m for m in v if DATE_W.search(m["w"]) or DATE_W.search(m["q"].split("?")[0][-40:] or "")]
            if len(dl) >= max(3, len(v) // 2):
                s = info[t]
                out[t] = {"title": str(s.get("title"))[:100], "cat": s.get("category"), "freq": s.get("frequency"),
                          "n": len(v), "dl": len(dl), "ev": len({m["ev"] for m in v}), "vol": sum(m["vol"] for m in v),
                          "yes": sum(m["res"] == "yes" for m in v), "first": d10(min(m["close"] for m in v)),
                          "last": d10(max(m["close"] for m in v)),
                          "ex": [(m["w"], m["res"], int(m["vol"])) for m in sorted(v, key=lambda m: -m["vol"])[:4]]}
    wj(SCAN, out)
    print("| series | category | title | markets | events | yes won | contracts | first close | last close |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"]):
        print(f"| {t} | {s['cat']} | {s['title']} | {s['n']} | {s['ev']} | {s['yes']} | {s['vol']:,.0f} | {s['first']} | {s['last']} |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"])[:40]:
        print("EX", t, s["ex"], flush=True)


def tape_one(m):
    a, b = max(m["open"], m["close"] - LIFE), m["close"]
    cs = []
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = yesno.kget(path, {"start_ts": a - 3600, "end_ts": b, "period_interval": 60})
        except Exception:
            continue
        got = r.get("candlesticks") if isinstance(r, dict) else None
        if got:
            for c in got:
                t, bid, ask = yesno.k_candle(c)
                cs.append([t, bid, ask, bot.fnum(c.get("volume_fp") or c.get("volume"), 0)])
            break
    tr, done, path = khouse.trades_span(m["t"], a, b, 8)
    tr.sort()
    return m["t"], {"c": cs, "tr": tr, "full": done}


def fetch(min_vol=2000, min_ser=20000):
    """Markets of every scanned date-ladder series with 20,000+ contracts traded, then their tapes."""
    sc = rj(SCAN, {}) or {}
    keep = sorted(t for t, s in sc.items() if s["vol"] >= min_ser)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    for t in keep:
        if t in have["series"]:
            continue
        _, ok, _ = km.series_markets(t)
        have["series"][t] = sc[t]
        have["markets"].update(ok)
        print(t, len(ok), "settled", flush=True)
        wj(MK, have)
    t0 = time.time()
    by = collections.defaultdict(list)
    for m in have["markets"].values():
        if m["vol"] >= min_vol:
            by[m["s"]].append(m)
    for t, ms in sorted(by.items()):
        path = os.path.join(CACHE, f"tapes_{t}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in ms if m["t"] not in got]
        for i in range(0, len(todo), 150):
            with ThreadPoolExecutor(6) as ex:
                for tk, dd in ex.map(tape_one, todo[i:i + 150]):
                    got[tk] = dd
            wj(path, got)
        if time.time() - t0 > 4.5 * 3600:
            print("time's up, run again to go on", flush=True)
            break
        print(f"{t}: {len(got)} of {len(ms)} markets, {sum(len(x['tr']) for x in got.values())} trades ({time.time() - t0:.0f}s)", flush=True)


# ---------------------------------------------------------------- the test
STEP = 7 * 86400       # one look a week at each ladder, counted from the ladder's first opening (never from a close: closes leak)
GAP = 0.10             # only quotes with a buyer-seller gap of 10c or less


def k_fee(p):
    import math
    return math.ceil(7 * p * (1 - p) - 1e-9) / 100


def load(extra_aim=("KXSPACEXSTARSHIP",)):
    """Settled date-ladder markets + hourly quotes (100-times-too-small quote trap repaired). Also takes the Starship
    ladder already fetched by aim.py (bt_cache/aim)."""
    import glob
    import aim
    have = rj(MK, {}) or {"series": {}, "markets": {}}
    ms = dict(have.get("markets") or {})
    files = sorted(glob.glob(os.path.join(CACHE, "tapes_*.json.gz")))
    for s in extra_aim:
        for t, m in ((rj(aim.MK, {}) or {}).get("markets") or {}).items():
            if m["s"] == s:
                ms[t] = m
        files.append(os.path.join(aim.CACHE, f"ktapes_{s}.json.gz"))
    ms = {t: m for t, m in ms.items() if DATE_W.search(m["w"]) or DATE_W.search(m["q"])}
    tp = {}
    for f in files:
        for tk, v in (rj(f, {}) or {}).items():
            if tk not in ms:
                continue
            vals = [x for c in v["c"] for x in c[1:3] if x is not None]
            if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
                for c in v["c"]:
                    c[1] = None if c[1] is None else round(c[1] * 100, 4)
                    c[2] = None if c[2] is None else round(c[2] * 100, 4)
            tp[tk] = v
    return ms, tp, have.get("series") or {}


def looks(ms, tp):
    """Weekly looks at every ladder (event): every rung still open with a live quote. -> list of look dicts.
    Rung order inside a look comes from the price (a nearer deadline is the cheaper Yes), so nothing peeks ahead."""
    evs = collections.defaultdict(list)
    for t, m in ms.items():
        if t in tp:
            evs[m["ev"]].append(m)
    out = []
    for ev, v in evs.items():
        t0 = min(m["open"] for m in v)
        t1 = max(m["close"] for m in v)
        k = 0
        while t0 + (k + 1) * STEP < t1:
            T = t0 + (k + 1) * STEP
            k += 1
            rungs = []
            for m in v:
                if not (m["open"] < T < m["close"]):
                    continue
                q = None
                for c in tp[m["t"]]["c"]:
                    if c[0] > T:
                        break
                    if T - c[0] <= 3 * 3600:
                        q = c
                if not q or q[1] is None or q[2] is None or q[1] <= 0 or q[2] >= 1 or q[2] - q[1] > GAP:
                    continue
                rungs.append({"m": m, "bid": q[1], "ask": q[2], "T": T})
            if not rungs:
                continue
            rungs.sort(key=lambda r: r["ask"] + r["bid"])
            for i, r in enumerate(rungs):
                r["i"], r["n"], r["wk"] = i, len(rungs), k
                r["life"] = (T - t0) / 86400
                out.append(r)
    return out


def bet(r, yes, extra=0.0):
    p = r["ask"] if yes else 1 - r["bid"]
    p = min(0.99, p + extra)
    cost = p + k_fee(p)
    won = r["m"]["res"] == "yes"
    return {"ev": r["m"]["ev"], "t": r["T"], "cost": cost, "pay": 1.0 if won == yes else 0.0, "tk": r["m"]["t"],
            "s": r["m"]["s"], "p": p}


def first(R, sel, yes, extra=0.0):
    """One bet per rung: the first weekly look where the rule says buy."""
    o, seen = [], set()
    for r in sorted(R, key=lambda r: r["T"]):
        tk = r["m"]["t"]
        if tk in seen or not sel(r):
            continue
        seen.add(tk)
        o.append(bet(r, yes, extra))
    return o


def per100(b):
    c = sum(x["cost"] for x in b)
    return (sum(x["pay"] for x in b) - c) / c * 100 if c else 0.0


HEAD = ("| rule | bets | ladders | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |\n"
        "|---|---|---|---|---|---|---|---|---|")


def line(name, b, tries, log=False, status="dropped"):
    import exam
    b = sorted(b, key=lambda x: x["t"])
    c = exam.score(b, name, tries=tries, log=log, quiet=True, status=status, src="dates.py, backtest/dates.md")
    h = len(b) // 2
    f = lambda x: f"{'+' if x >= 0 else '-'}${abs(x):.2f}"
    print(f"| {name} | {len(b)} | {len({x['ev'] for x in b})} | {sum(1 for x in b if x['pay'] > 0)} | {f(per100(b)) if b else '-'} | "
          f"{f(per100(b[:h])) if h else '-'} / {f(per100(b[h:])) if h else '-'} | "
          f"{c.get('lo100')} to {c.get('hi100')} | {c.get('floor100')} | {c.get('verdict')} |", flush=True)
    return c


BANDS = [(0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98)]


def comb(R, title):
    print(f"\n### {title}: Yes price at the look (real asking price + fee, one bet per rung, first weekly look in the band)\n")
    print("| Yes price | rungs | ladders | Yes won | buy Yes per $100 | buy No per $100 |\n|---|---|---|---|---|---|")
    for lo, hi in BANDS:
        sel = lambda r, lo=lo, hi=hi: lo <= (r["bid"] + r["ask"]) / 2 < hi
        y, n = first(R, sel, True), first(R, sel, False)
        if not y:
            continue
        print(f"| {lo * 100:.0f}-{hi * 100:.0f}c | {len(y)} | {len({x['ev'] for x in y})} | {sum(x['pay'] > 0 for x in y)} | "
              f"{per100(y):+.2f} | {per100(n):+.2f} |")


def kind(s):
    if re.search(r"GPT|CLAUDE|GEMINI|GROK|LLAMA|DEEPSEEK|AIREVIEW", s) and "IPO" not in s:
        return "AI release"
    if "STARSHIP" in s or "ARTEMIS" in s or "LAUNCH" in s:
        return "rockets"
    if "IPO" in s:
        return "IPO"
    if re.search(r"OUT$|DROPOUT|LEAVE|RETIRE|WITHDRAW|ANNOUNCEOUT", s):
        return "someone leaves"
    if re.search(r"ALBUM|SONG|MEDIA|TVSEASON|TRAILER|SPOTIFY|MOVIE|IPHONE|GTA|GAME", s):
        return "entertainment/product"
    return "politics/other"


TRIES = 60       # cuts looked at: 12 band x side cells, 6 kinds x 2, 4 ladder ages, nearest rung, halves, size checks


def report(log=False):
    import statistics
    ms, tp, ser = load()
    R = looks(ms, tp)
    for r in R:
        r["k"] = kind(r["m"]["s"])
    mid = lambda r: (r["bid"] + r["ask"]) / 2
    print(f"## {len(ms)} settled date-ladder markets, {len(tp)} with prices, {len({m['ev'] for m in ms.values()})} ladders, "
          f"{len({r['m']['s'] for r in R})} series, {len(R)} rung-looks\n")
    comb(R, "All ladders")
    print("\n### By kind of ladder\n\n| kind | No at Yes 25-90c: bets | ladders | per $100 | Yes at 2-25c per $100 |\n|---|---|---|---|---|")
    for k in sorted({r["k"] for r in R}):
        S = [r for r in R if r["k"] == k]
        b = first(S, lambda r: .25 <= mid(r) < .90, False)
        y = first(S, lambda r: .02 <= mid(r) < .25, True)
        print(f"| {k} | {len(b)} | {len({x['ev'] for x in b})} | {per100(b):+.2f} | {per100(y):+.2f} |")
    print("\n### The exam\n\n" + HEAD)
    main = first(R, lambda r: .25 <= mid(r) < .90, False)
    line("Date ladders on Kalshi: No where Yes is 25-90c (first weekly look)", main, TRIES, log)
    line("same, 2c extra a share", first(R, lambda r: .25 <= mid(r) < .90, False, 0.02), TRIES)
    line("No where Yes is 50-90c", first(R, lambda r: .50 <= mid(r) < .90, False), TRIES)
    line("No on the nearest open rung only (the 'it will slip' bet), Yes 25-90c",
         first(R, lambda r: .25 <= mid(r) < .90 and r["i"] == 0, False), TRIES, log)
    line("AI model release ladders (KXGPT, KXCLAUDE, KXGEMINI...): No where Yes is 25-90c",
         first([r for r in R if r["k"] == "AI release"], lambda r: .25 <= mid(r) < .90, False), TRIES, log)
    st = [r for r in R if "STARSHIP" in r["m"]["s"]]
    line("Starship flight dates: No where Yes is 2-50c", first(st, lambda r: .02 <= mid(r) < .50, False), TRIES, log,
         status="re-check")
    line("Starship, same, 4c extra", first(st, lambda r: .02 <= mid(r) < .50, False, 0.04), TRIES)
    pl, cs = collections.defaultdict(float), collections.defaultdict(float)
    for x in main:
        pl[x["ev"]] += x["pay"] - x["cost"]
        cs[x["ev"]] += x["cost"]
    top = sorted(pl, key=lambda e: -pl[e])[:5]
    print(f"\nWho carries it: profit ${sum(pl.values()):.2f} on ${sum(cs.values()):.2f} bet ($1 a share). Best 5 ladders: "
          + ", ".join(f"{e} +${pl[e]:.2f}" for e in top)
          + f". Without them: {per100([x for x in main if x['ev'] not in top]):+.2f} per $100.")
    print("\n| ladder age at the look | bets | per $100 |\n|---|---|---|")
    for lo, hi in [(0, 15), (15, 45), (45, 120), (120, 9999)]:
        b = first(R, lambda r, lo=lo, hi=hi: .25 <= mid(r) < .90 and lo <= r["life"] < hi, False)
        print(f"| {lo}-{hi if hi < 9999 else ''} days | {len(b)} | {per100(b):+.2f} |")
    sz = []
    for x in main:
        T = x["t"]
        sz.append(sum(c for t, p, c, s in tp[x["tk"]]["tr"] if T <= t < T + 86400 and s == 0 and 1 - p / 1000 <= x["p"] + 1e-9))
    days = (max(x["t"] for x in main) - min(x["t"] for x in main)) / 86400
    print(f"\nSize: in the 24 hours after a look, No buyers paid our price or less for {statistics.median(sz):.0f} contracts in the "
          f"middle rung (average {statistics.mean(sz):.0f}). Signals: about {len(main) / days * 30:.0f} a month over {days:.0f} days.")
    sb = first(st, lambda r: .02 <= mid(r) < .50, False)
    print("\nStarship bets one by one:")
    for x in sorted(sb, key=lambda x: x["t"]):
        print(f"- {d10(x['t'])} {x['tk']}: No at {x['p'] * 100:.0f}c, {'won' if x['pay'] else 'lost'}")

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    if a == "scan":
        scan()
    elif a == "fetch":
        fetch()
    elif a == "all":
        scan()
        fetch()
    elif a == "report":
        report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
    else:
        print(__doc__)
