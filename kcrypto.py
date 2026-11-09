#!/usr/bin/env python3
"""Kalshi 15-minute crypto markets: the "late favorite maker" idea (2026-11-09, from a Reddit post).

PAPER ONLY. Never trades.

    python3 kcrypto.py scan      # print API shapes: series, fees, a market, trades, history endpoints
"""
import json
import sys
import time

import bot

K = bot.KALSHI
SERIES = ("KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M", "KXHYPE15M", "KXBNB15M")


def get(path, params=None):
    return bot.http_json(f"{K}{path}", params)


def show(label, fn):
    print(f"\n===== {label}")
    try:
        r = fn()
        s = json.dumps(r, indent=1)
        print(s[:3500] + (" ...(cut)" if len(s) > 3500 else ""))
        return r
    except Exception as e:
        print("FAILED:", e)
        return None


def scan():
    for s in SERIES:
        show(f"series {s}", lambda: get(f"/series/{s}"))
    show("fee changes", lambda: get("/series/fee_changes", {"series_ticker": "KXBTC15M"}))
    show("historical cutoff", lambda: get("/historical/cutoff"))
    open_m = show("open BTC 15m", lambda: get("/markets", {"series_ticker": "KXBTC15M", "status": "open", "limit": 2}))
    done = show("settled BTC 15m", lambda: get("/markets", {"series_ticker": "KXBTC15M", "status": "settled", "limit": 2}))
    t = None
    try:
        t = done["markets"][0]["ticker"]
    except Exception:
        pass
    if t:
        show(f"trades {t}", lambda: get("/markets/trades", {"ticker": t, "limit": 12}))
        r = get("/markets/trades", {"ticker": t, "limit": 1000})
        print("trades in one page:", len(r.get("trades", [])), "cursor:", bool(r.get("cursor")))
        show(f"candles {t}", lambda: get(f"/series/KXBTC15M/markets/{t}/candlesticks",
                                         {"period_interval": 1, "start_ts": int(time.time()) - 3600,
                                          "end_ts": int(time.time())}))
    try:
        ot = open_m["markets"][0]["ticker"]
        show(f"book {ot}", lambda: get(f"/markets/{ot}/orderbook"))
        show(f"open trades {ot}", lambda: get("/markets/trades", {"ticker": ot, "limit": 15}))
    except Exception:
        pass
    old = int(time.time()) - 40 * 86400
    show("historical markets", lambda: get("/historical/markets", {"series_ticker": "KXBTC15M", "limit": 2}))
    show("historical trades", lambda: get("/historical/trades", {"limit": 3}))
    show("settled BTC 15m 40 days ago", lambda: get("/markets", {"series_ticker": "KXBTC15M", "status": "settled",
                                                                "max_close_ts": old, "limit": 2}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"scan": scan}[cmd]()
