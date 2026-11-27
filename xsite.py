#!/usr/bin/env python3
"""Kalshi vs Polymarket on the SAME non-sports question: follow the leader? (27 Nov 2026). Research only.
PAPER ONLY. Reads public history, never trades, never writes state/.

The question (Jan: "go crazy", coordinator: "follow the leader, not arbitrage"): when one question (politics,
economy, weather, culture, ...) is listed on both sites and the two prices differ, does one site's price know the
winner better? And when one site moves first, does the other follow, late enough for a slow bot to buy?
Sports arb (~$1.04 a pair) and the 15-minute crypto pairs (~$1.05) were dropped before and are not redone here.

    python3 xsite.py klist        # probe xs_klist: every settled non-sports Kalshi market, 1 Mar-9 Nov (resumable)
    python3 xsite.py match        # offline: pair them with bt_cache Polymarket markets -> bt_cache/xs/pairs.json.gz
    python3 xsite.py tapes        # probe xs_tapes: hourly Kalshi bid/ask + every Polymarket trade for each pair
    python3 xsite.py run          # offline: report backtest/xsite.md

Data: bt_cache/xs/ in the shared price store. Markets ending on/after 10 Nov (the holdout) stay out.
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import khouse
import launch
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "xs")
KDAYS = os.path.join(CACHE, "kdays")
DAY = 86400
FIRST, LAST = "2026-03-01", "2026-11-09"
T0 = time.time()
BUDGET_MIN = float(os.environ.get("XS_MIN", "270"))
rj, wj, tsec = khouse.rj, khouse.wj, khouse.tsec


def left():
    return BUDGET_MIN - (time.time() - T0) / 60


# ================================================================ Kalshi list
def kday(d0):
    p = os.path.join(KDAYS, f"{d0}.json.gz")
    if os.path.exists(p):
        return d0, None
    try:
        _, n, ok = khouse.list_day(d0)
    except Exception as e:
        print(f"  day {d0} failed {str(e)[:80]}", flush=True)
        return d0, None
    keep = []
    for m in ok:
        cat = launch.kcategory(m["s"], m["q"])
        if cat in ("sports", "esports"):
            continue
        m["cat"] = cat
        keep.append(m)
    wj(p, {"n": n, "m": keep})
    return d0, (n, len(keep))


def klist():
    os.makedirs(KDAYS, exist_ok=True)
    days = list(range(tsec(FIRST), tsec(LAST) + 1, DAY))
    with ThreadPoolExecutor(int(os.environ.get("XS_WORKERS", "4"))) as ex:
        for d0, r in ex.map(kday, days):
            if r:
                print(f"{dt.datetime.utcfromtimestamp(d0):%Y-%m-%d}: {r[0]} settled, {r[1]} non-sports kept ({(time.time() - T0) / 60:.0f} min)", flush=True)
            if left() < 5:
                print("time budget used, stop (re-run resumes)")
                break
    allm = {}
    for f in sorted(os.listdir(KDAYS)):
        for m in (rj(os.path.join(KDAYS, f), {}) or {}).get("m", []):
            allm[m["t"]] = m
    wj(os.path.join(CACHE, "kmarkets.json.gz"), allm)
    c = collections.Counter(m["cat"] for m in allm.values())
    print(f"kalshi non-sports settled markets: {len(allm)}; by kind: {dict(c.most_common())}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"klist": klist}[cmd]()
