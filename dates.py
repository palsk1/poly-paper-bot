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
        import dates_report
        dates_report.report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
    else:
        print(__doc__)
