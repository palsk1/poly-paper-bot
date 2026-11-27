#!/usr/bin/env python3
"""Kalshi's new 15-minute "up in the next 15 minutes?" families outside crypto (27 Nov 2026): Brent oil, USD/CAD,
AUD/USD, the S&P 500, Treasury yields (2y / 5y / 10y / 30y), plus any siblings. Do our crypto 15-minute rules work there?

PAPER ONLY. Reads public Kalshi history and never trades.

    python3 k15x.py scan          # probe nfx_k15x_scan: every non-crypto 15-minute / hourly "up or down" series, fees,
                                  # settle source, rules, one market in full, size -> bt_cache/nf/k15x/scan.txt
    python3 k15x.py fetch [S,..]  # probe nfx_k15x_fetch: settled windows, 1-minute candles of the whole window, every
                                  # trade of the last 6 minutes (resumable, saves as it goes) -> bt_cache/nf/k15x/
    python3 k15x.py run [log]     # replay kc_maker (bid one tick in front of the leader's best bid late in the window,
                                  # fills only from contracts really sold into it), the 45-second buy, the backward look
                                  # -> backtest/k15x.md tables; `log` adds the exam lines to backtest/ledger.json

Rules replayed (fixed before the first result, copied from the crypto tracks):
  kc_maker   with M minutes left (main M = 3), the leading side (middle 50c+), its best bid 95c+ (also 90c+ looked at):
             bid one tick above it (join when there is no room), hold to the result, maker = no fee on these series?
             (fee read from /series). Fills: contracts really sold into our price after the bid ("tape"): all sales
             below our price + sales at our price only when we were alone there.
  cushion    the outside price is not free for these (FX / yields / Brent / S&P to the minute), so the z check uses
             Kalshi's own per-second settle number from /live_data when it exists (like bot.kmaker_kz).
  kfast      45 s before the close buy the leading side at the first real trade where someone bought that side
             (taker), if that price is 90c-99.5c, pay the taker fee.
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
import kcrypto as kc
import yesno

UTC = dt.timezone.utc
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "nf", "k15x")
OUT = os.path.join(ROOT, "backtest")
kget = yesno.kget
EPS = 1e-9
TARGETS = ["KXBRENT15M", "KXUSDCAD15M", "KXAUDUSD15M", "KXINX15M", "KX2YRRATE15M", "KX5YRRATE15M", "KX10YRRATE15M",
           "KX30YRRATE15M"]
LOOK = 16          # candle minutes kept per window (the whole window)
TAPE_SEC = 360     # trade list: the last 6 minutes

_LOG = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    _LOG.append(line)


def save_log(name):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


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


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M")


def vol_of(m):
    return bot.fnum(m.get("volume_fp") or m.get("volume"), 0)


def p(series, kind):
    return os.path.join(CACHE, f"{kind}_{series}.json.gz")


# ================================================================ scan
def all_series():
    out, cur = [], None
    for _ in range(50):
        q = {"limit": 1000}
        if cur:
            q["cursor"] = cur
        res = kget("/series", q)
        out += res.get("series") or []
        cur = res.get("cursor")
        if not cur:
            break
    return out


def scan(arg=None):
    ser = all_series()
    say("Kalshi series in all:", len(ser))
    pick = []
    for s in ser:
        tk = str(s.get("ticker") or "")
        t = str(s.get("title") or "").lower()
        if (s.get("category") or "") == "Crypto":
            continue
        if "15M" in tk or "15 min" in t or "next 15" in t or tk.endswith("1H") or tk.endswith("H") and "hour" in t \
                or "up or down" in t or tk in TARGETS:
            pick.append(s)
    say("Non-crypto short up/down candidates:", len(pick))
    now = int(time.time())
    for s in sorted(pick, key=lambda s: s.get("ticker")):
        tk = s.get("ticker")
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000, "min_close_ts": now - 3 * 86400}).get("markets") or []
        except Exception as e:
            say("  failed", tk, str(e)[:80])
            continue
        say(f"  {tk:18s} | {s.get('category')} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | "
            f"3 days: {len(ms)} settled, {sum(map(vol_of, ms)):,.0f} contracts | {str(s.get('title'))[:70]}")
        if tk in TARGETS or ms and sum(map(vol_of, ms)) > 50000:
            say(f"     settle: {json.dumps(s.get('settlement_sources'))[:300]} | tags {s.get('tags')}")
    for tk in TARGETS:
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 200}).get("markets") or []
        except Exception as e:
            say(tk, "failed", e)
            continue
        if not ms:
            say(tk, "no settled markets")
            continue
        m = sorted(ms, key=lambda m: -vol_of(m))[len(ms) // 3]
        say(f"\n== {tk}: one market in full")
        say(json.dumps({k: v for k, v in m.items() if k not in ("rules_secondary",)})[:2500])
        say("rules2:", str(m.get("rules_secondary"))[:600])
        byh = collections.Counter()
        for x in ms:
            byh[dt.datetime.fromtimestamp(kc.tsec(x.get("close_time")) or 0, UTC).strftime("%a %H")] += 1
        say("closes by weekday+hour (last 200):", " ".join(f"{k}:{v}" for k, v in sorted(byh.items())))
        say("per event markets:", collections.Counter(collections.Counter(x.get("event_ticker") for x in ms).values()))
        say("results:", collections.Counter(x.get("result") for x in ms), "middle volume", sorted(map(vol_of, ms))[len(ms) // 2])
        try:
            d = (kget(f"/live_data/events/{m.get('event_ticker')}").get("live_data") or {}).get("details") or {}
            ts = d.get("timeseries") or []
            say(f"live settle number: {len(ts)} points; first {ts[:2]} last {ts[-2:]}; keys {list(d)[:12]}")
        except Exception as e:
            say("live settle number failed", str(e)[:120])
        try:
            res = kget(f"/series/{tk}/markets/{m.get('ticker')}/candlesticks",
                       {"start_ts": kc.tsec(m.get("close_time")) - 900, "end_ts": kc.tsec(m.get("close_time")), "period_interval": 1})
            cs = res.get("candlesticks") or []
            say(f"candles: {len(cs)}; one: {json.dumps(cs[len(cs) // 2])[:600] if cs else None}")
        except Exception as e:
            say("candles failed", str(e)[:120])
        try:
            tr = kget("/markets/trades", {"ticker": m.get("ticker"), "limit": 5}).get("trades") or []
            say("trade sample:", json.dumps(tr[:2])[:600])
        except Exception as e:
            say("trades failed", str(e)[:120])
    try:
        say("historical cutoff", json.dumps(kget("/historical/cutoff")))
    except Exception as e:
        say("cutoff failed", str(e)[:80])
    save_log("scan.txt")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    {"scan": scan}[cmd](arg)
