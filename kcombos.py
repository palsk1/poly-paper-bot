#!/usr/bin/env python3
"""Kalshi combos (parlays): can a small account be the house? (2026-11-22). Research only.

PAPER ONLY. Reads public data, never trades, never writes state/. No key, no login.

Kalshi combos ("multivariate events", tickers KXMVE...) are priced by request-for-quote: a buyer asks, makers
answer through the API, the best quote trades. Every combo trade is public (`/markets/trades`), and so are the
legs. So the Polymarket combo question (combos.py) can be asked here without a server:
  1. what did combo buyers pay, against the same legs' own prices at that minute?
  2. how did the seller (the house) do once the games finished, after Kalshi's maker fee on combos?
  3. would a house that sells at "legs multiplied + a margin" have won trades, and at a profit?
  4. how much money does one sold combo lock up (does $30 go anywhere)?

    python3 kcombos.py peek            # probe kcb_peek: raw shapes of collections, combo markets, trades, legs
    python3 kcombos.py fetch [days]    # probe kcb_fetch: settled combo markets, their trades, each leg's minute quotes
    python3 kcombos.py run             # probe kcb_run (or locally, data is in the price store): backtest/kcombos.md
    python3 kcombos.py selftest        # offline

Data: kcb_cache/ (its own folder in the shared price store, so a run needn't download the whole store:
`python3 store.py pull kcb_cache`).
"""
import collections
import datetime as dt
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import exam
import khouse
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "kcb_cache")
OUT = os.path.join(ROOT, "backtest", "kcombos.md")
DAY = 86400
kget = yesno.kget
rj, wj, its = khouse.rj, khouse.wj, khouse.its
T0 = time.time()


def shape(x, depth=0, maxd=3):
    if isinstance(x, dict):
        if depth >= maxd:
            return "{...}"
        return {k: shape(v, depth + 1, maxd) for k, v in list(x.items())[:60]}
    if isinstance(x, list):
        return [shape(x[0], depth + 1, maxd), f"... x{len(x)}"] if x else []
    s = str(x)
    return s if len(s) <= 90 else s[:90] + "..."


def show(label, fn):
    print(f"\n===== {label}")
    try:
        r = fn()
        print(json.dumps(shape(r), indent=1)[:6000])
        return r
    except Exception as e:
        print("  FAILED:", str(e)[:300])
        return None


def peek():
    cols = show("collections", lambda: kget("/multivariate_event_collections", {"limit": 200}))
    rows = (cols or {}).get("multivariate_contracts") or (cols or {}).get("multivariate_event_collections") or []
    print("\ncollections:", len(rows))
    for c in rows[:80]:
        print("  ", c.get("collection_ticker"), "|", str(c.get("title"))[:70], "|", c.get("open_date"), c.get("close_date"),
              "| events", len(c.get("associated_events") or []), "| size", c.get("size_min"), c.get("size_max"),
              "| ordered", c.get("is_ordered"), "| single/event", c.get("is_single_market_per_event"))
    show("events/multivariate", lambda: kget("/events/multivariate", {"limit": 3, "with_nested_markets": "true"}))
    now = int(time.time())
    for st in ("settled", "open", "closed"):
        r = show(f"markets mve_filter=only status={st}", lambda: kget("/markets", {"mve_filter": "only", "status": st, "limit": 1000}))
        ms = (r or {}).get("markets") or []
        vols = sorted((bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ms), reverse=True)
        print(f"  {st}: {len(ms)} on page 1, cursor={'yes' if (r or {}).get('cursor') else 'no'}, with volume {sum(1 for v in vols if v > 0)}, "
              f"top volumes {vols[:10]}")
        if ms:
            cl = sorted(its(m.get("close_time")) or 0 for m in ms)
            print("  close range", dt.datetime.utcfromtimestamp(cl[0]), dt.datetime.utcfromtimestamp(cl[-1]))
            print("  results", collections.Counter(str(m.get("result")) for m in ms).most_common(6))
            print("  prefixes", collections.Counter(str(m.get("ticker")).split("-")[0] for m in ms).most_common(12))
            traded = [m for m in ms if bot.fnum(m.get("volume_fp") or m.get("volume"), 0) > 0]
            for m in traded[:3]:
                print("\n  --- one traded combo, every field")
                print(json.dumps(m, indent=1)[:5000])
                tk = m.get("ticker")
                tr = show(f"trades {tk}", lambda: kget("/markets/trades", {"ticker": tk, "limit": 100}))
                for t in ((tr or {}).get("trades") or [])[:8]:
                    print("   ", json.dumps(t)[:400])
                show(f"orderbook {tk}", lambda: kget(f"/markets/{tk}/orderbook"))
                legs = m.get("mve_selected_legs") or []
                for lg in legs[:4]:
                    lt = lg.get("market_ticker")
                    lm = show(f"leg {lt}", lambda: kget(f"/markets/{lt}"))
    # how many settled combo markets a day, and how many traded: one day, all pages
    for back in (1, 3):
        d0 = (now // DAY - back) * DAY
        n = tr_n = 0
        vol = 0.0
        cur = None
        pages = 0
        for _ in range(60):
            p = {"mve_filter": "only", "status": "settled", "limit": 1000, "min_close_ts": d0, "max_close_ts": d0 + DAY - 1}
            if cur:
                p["cursor"] = cur
            try:
                r = kget("/markets", p)
            except Exception as e:
                print("  day list failed", str(e)[:200])
                break
            ms = r.get("markets") or []
            pages += 1
            n += len(ms)
            for m in ms:
                v = bot.fnum(m.get("volume_fp") or m.get("volume"), 0)
                if v > 0:
                    tr_n += 1
                    vol += v
            cur = r.get("cursor")
            if not cur or not ms:
                break
        print(f"\nday -{back}: {n} settled combo markets ({pages} pages{', more left' if cur else ''}), {tr_n} traded, {vol:,.0f} contracts")
    show("fee changes", lambda: kget("/series/fee_changes"))
    show("all trades, newest (any market)", lambda: kget("/markets/trades", {"limit": 5}))
    show("communications rfqs without a key", lambda: kget("/communications/rfqs", {"limit": 5}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek}[cmd](*sys.argv[2:])
