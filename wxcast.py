#!/usr/bin/env python3
"""Weather forecasts vs weather markets (2026-11-10). RESEARCH ONLY, PAPER ONLY: reads public data, never trades.

Question: do free professional forecasts (NWS's National Blend of Models via the Iowa State MOS archive, and the
GFS / ECMWF runs Open-Meteo keeps as "previous runs") know the day's high or low temperature better than the
Kalshi and Polymarket prices 1-3 days ahead, by enough to pay the costs?

Every forecast is the one that was public at the moment of the bet (no peeking at later runs).

    python3 wxcast.py scan     # API shapes and which sources answer from GitHub (debugging)
    python3 wxcast.py fetch    # markets, prices, forecasts -> wx_cache/ (own Actions cache)
    python3 wxcast.py run      # the test -> backtest/wxcast.md
  From GitHub: probe workflow with what = wx_scan / wx_fetch / wx_run / wx_all.
"""
import datetime as dt
import gzip
import json
import math
import os
import random
import re
import sys
import time
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

import bot

K = bot.KALSHI
G = bot.GAMMA
C = bot.CLOB
UTC = dt.timezone.utc
PREV = "https://previous-runs-api.open-meteo.com/v1/forecast"
IEM = "https://mesonet.agron.iastate.edu"


def show(name, fn, cut=2500):
    print(f"\n== {name}")
    try:
        r = fn()
        s = json.dumps(r, indent=1, default=str)
        print(s[:cut] + (" ...(cut)" if len(s) > cut else ""))
        return r
    except Exception as e:
        print("FAILED:", e)
        return None


def raw_text(url, params=None):
    import urllib.parse
    import urllib.request
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def scan():
    # Kalshi weather series
    ser = show("kalshi series Climate and Weather", lambda: bot.http_json(K + "/series", {"category": "Climate and Weather"}), 400)
    rows = (ser or {}).get("series") or []
    print(f"{len(rows)} series")
    for s in rows:
        print(f"  {s.get('ticker')} | {s.get('title')} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')}"
              f" | {str(s.get('settlement_sources'))[:120]}")
    for sr in ("KXHIGHNY", "KXLOWTNYC", "KXRAINNYC"):
        r = show(f"kalshi settled {sr}", lambda: bot.http_json(K + "/markets", {"series_ticker": sr, "status": "settled", "limit": 3}), 3000)
        ms = (r or {}).get("markets") or []
        if ms:
            m = ms[0]
            close = int(dt.datetime.fromisoformat(m["close_time"].replace("Z", "+00:00")).timestamp())
            show(f"candles {m['ticker']}", lambda: bot.http_json(K + f"/series/{sr}/markets/{m['ticker']}/candlesticks",
                                                                 {"start_ts": close - 3 * 86400, "end_ts": close, "period_interval": 60}), 1500)
        show(f"kalshi historical {sr}", lambda: bot.http_json(K + "/historical/markets", {"series_ticker": sr, "limit": 2}), 1500)
    # Polymarket closed temperature events
    r = show("poly closed daily-temperature events", lambda: bot.http_json(G + "/events", {"tag_slug": "daily-temperature", "closed": "true", "limit": 2, "order": "endDate", "ascending": "false"}), 5000)
    n, cur, oldest = 0, None, None
    for _ in range(400):
        p = {"tag_slug": "daily-temperature", "closed": "true", "limit": 100}
        if cur:
            p["after_cursor"] = cur
        try:
            res = bot.http_json(G + "/events/keyset", p)
        except Exception as e:
            print("keyset failed", e)
            break
        evs = bot.envelope_rows(res, "events", "data")
        n += len(evs)
        for e in evs:
            ed = str(e.get("endDate") or "")
            oldest = ed if not oldest or ed < oldest else oldest
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not cur or not evs:
            break
    print(f"poly closed temperature events: {n}, oldest end {oldest}")
    # Forecast sources
    show("open-meteo previous runs (gfs, ecmwf)", lambda: bot.http_json(PREV, {
        "latitude": 40.78, "longitude": -73.97, "hourly": "temperature_2m,temperature_2m_previous_day1,temperature_2m_previous_day2",
        "models": "gfs_seamless,ecmwf_ifs025", "start_date": "2026-06-01", "end_date": "2026-06-01", "temperature_unit": "fahrenheit",
        "timezone": "GMT"}), 3000)
    show("open-meteo previous runs 2025", lambda: bot.http_json(PREV, {
        "latitude": 40.78, "longitude": -73.97, "hourly": "temperature_2m_previous_day1",
        "models": "gfs_seamless,ecmwf_ifs025,icon_seamless,gem_seamless", "start_date": "2025-03-01", "end_date": "2025-03-01",
        "timezone": "GMT"}), 1500)
    show("IEM MOS NBS csv", lambda: raw_text(IEM + "/cgi-bin/request/mos.py", {"station": "KNYC", "model": "NBS",
                                                                               "sts": "2026-06-01T00:00Z", "ets": "2026-06-01T08:00Z", "format": "csv"})[:2500])
    show("IEM MOS api json", lambda: bot.http_json(IEM + "/api/1/mos.json", {"station": "KNYC", "model": "NBS",
                                                                           "runtime": "2026-06-01T01:00Z"}), 2500)
    show("IEM MOS GFS MAV", lambda: raw_text(IEM + "/cgi-bin/request/mos.py", {"station": "KNYC", "model": "GFS",
                                                                               "sts": "2026-06-01T00:00Z", "ets": "2026-06-01T07:00Z", "format": "csv"})[:1500])
    show("IEM CLI KNYC", lambda: bot.http_json(IEM + "/json/cli.py", {"station": "KNYC", "year": 2026}), 1500)
    show("IEM daily ASOS KLGA", lambda: raw_text(IEM + "/cgi-bin/request/daily.py", {"network": "NY_ASOS", "stations": "LGA",
                                                                                     "year1": 2026, "month1": 6, "day1": 1, "year2": 2026, "month2": 6, "day2": 3})[:1000])


MODES = {"scan": scan}

if __name__ == "__main__":
    MODES[sys.argv[1] if len(sys.argv) > 1 else "scan"]()
