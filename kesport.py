#!/usr/bin/env python3
"""Kalshi's new round-the-clock families (27 Nov 2026): table tennis (Liga Pro, TT Elite, TT Star), eBasketball,
eSoccer, eFootball. Research only, PAPER ONLY: reads public history, never trades, never writes state/.

Question: these leagues are new, niche and run all day. Does anything beat Kalshi's own pre-game price?
  a) Elo rating per player (or per eBasketball "team (player)") from Kalshi's own settled results, walk-forward.
  b) price-only cuts (price band, hour of day, matches already played that day, eSoccer ties).
  c) backward look from the upsets.

    python3 kesport.py peek            # probe nfx_kesport_peek: one market / milestone / candle sample per series
    python3 kesport.py fetch [series]  # probe nfx_kesport_fetch: settled markets + start times + 1-minute candles
    python3 kesport.py report          # offline: backtest/kesport.md (after `store.py pull bt_cache/nf`)

Data: bt_cache/nf/kes/ (shared store folder bt_cache/nf).
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "nf", "kes")
OUT = os.path.join(ROOT, "backtest", "kesport.md")
SERIES = ["KXLIGAPROMATCH", "KXTTELITEMATCH", "KXTTSTARMATCH", "KXEBASKETBALLGAME", "KXESOCCERGAME", "KXEFOOTBALLGAME"]
kget = yesno.kget
T0 = time.time()
PRE = 180          # minutes of 1-minute candles before the start


def its(x):
    if not x:
        return 0
    try:
        return int(bot.parse_iso(x).timestamp())
    except Exception:
        return 0


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def short(x, n=1500):
    s = json.dumps(x, default=str)
    return s[:n]


# ================================================================ peek
def peek():
    try:
        print("CUTOFF", short(kget("/historical/cutoff")))
    except Exception as e:
        print("cutoff failed", e)
    for s in SERIES:
        print("=" * 30, s)
        try:
            print("SERIES", short(kget(f"/series/{s}"), 1200))
        except Exception as e:
            print("series failed", str(e)[:200])
        try:
            r = kget("/markets", {"series_ticker": s, "status": "settled", "limit": 6})
        except Exception as e:
            print("markets failed", str(e)[:200])
            continue
        ms = r.get("markets") or []
        if not ms:
            continue
        m = ms[0]
        print("MARKET", short(m, 3000))
        for x in ms[1:]:
            print("  other", x.get("ticker"), x.get("yes_sub_title"), x.get("result"), x.get("open_time"), x.get("close_time"),
                  x.get("expected_expiration_time"), x.get("volume_fp") or x.get("volume"))
        ev = m.get("event_ticker")
        try:
            print("EVENT", short(kget(f"/events/{ev}"), 1500))
        except Exception as e:
            print("event failed", str(e)[:200])
        for p in ({"limit": 5, "related_event_ticker": ev}, {"limit": 5, "event_ticker": ev}):
            try:
                print("MILESTONE", p, short(kget("/milestones", p), 1500))
            except Exception as e:
                print("milestone failed", p, str(e)[:200])
        o, c = its(m.get("open_time")), its(m.get("close_time"))
        try:
            r = kget("/markets/candlesticks", {"market_tickers": ",".join(x["ticker"] for x in ms[:4]), "start_ts": o, "end_ts": c, "period_interval": 1})
            for mm in r.get("markets") or []:
                cs = mm.get("candlesticks") or []
                print("CANDLES", mm.get("market_ticker"), len(cs), "first", short(cs[:1], 700), "last", short(cs[-1:], 700))
                act = [x for x in cs if bot.fnum(x.get("volume_fp") or x.get("volume"), 0) > 0]
                print("  minutes with trades", len(act), "first trade minute", (act[0].get("end_period_ts") - o) / 60 if act else None,
                      "close-open min", (c - o) / 60)
        except Exception as e:
            print("candles failed", str(e)[:200])
        try:
            r = kget("/markets/trades", {"ticker": m["ticker"], "limit": 1000})
            tr = r.get("trades") or []
            print("TRADES", len(tr), short(tr[:2], 800))
            if tr:
                ts = sorted(its(t.get("created_time")) for t in tr)
                print("  trade span min from open", (ts[0] - o) / 60, (ts[-1] - o) / 60, "close", (c - o) / 60)
        except Exception as e:
            print("trades failed", str(e)[:200])
    # milestones with these competitions: what kinds exist
    try:
        r = kget("/milestones", {"limit": 500, "minimum_start_date": bot.iso(dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=6))})
        rows = r.get("milestones") or []
        kinds = collections.Counter((x.get("category"), x.get("type")) for x in rows)
        print("MILESTONE KINDS", kinds.most_common(30))
        for x in rows:
            evs = " ".join((x.get("related_event_tickers") or []) + (x.get("primary_event_tickers") or []))
            if any(s in evs for s in SERIES):
                print("MS HIT", short(x, 800))
                break
    except Exception as e:
        print("milestones list failed", str(e)[:200])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    if cmd == "peek":
        peek()
