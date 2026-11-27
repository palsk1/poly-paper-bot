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


# ================================================================ fetch
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}


def sched(ev):
    """Scheduled start (unix) from the event ticker: KXLIGAPROMATCH-26NOV271100STRORL = 27 Nov 2026 11:00 New York time.
    Never the close time (that leaks the result)."""
    import re
    from zoneinfo import ZoneInfo
    m = re.search(r"-(\d\d)([A-Z]{3})(\d\d)(\d\d)(\d\d)", ev or "")
    if not m or m.group(2) not in MON:
        return 0
    y, mo, d, h, mi = 2000 + int(m.group(1)), MON[m.group(2)], int(m.group(3)), int(m.group(4)), int(m.group(5))
    try:
        return int(dt.datetime(y, mo, d, h, mi, tzinfo=ZoneInfo("America/New_York")).timestamp())
    except Exception:
        return 0


def list_series(s):
    rows = []
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(400):
            p = {"series_ticker": s, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  {s} {path} failed: {str(e)[:100]}", flush=True)
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    out, seen = {}, set()
    for m in rows:
        tk = str(m.get("ticker") or "")
        if not tk or tk in seen or not str(m.get("event_ticker") or "").startswith(s):
            continue
        seen.add(tk)
        out[tk] = {"t": tk, "ev": m.get("event_ticker"), "name": m.get("yes_sub_title"), "res": m.get("result"),
                   "sv": m.get("settlement_value_dollars"), "open": its(m.get("open_time")), "close": its(m.get("close_time")),
                   "start": sched(m.get("event_ticker")), "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0),
                   "rule": str(m.get("rules_primary") or "")[:300], "strike": m.get("custom_strike")}
    return out


def crow(c):
    def px(b, k="close"):
        d = c.get(b) or {}
        v = d.get(k + "_dollars")
        if v in (None, ""):
            v = d.get(k)
            if v in (None, ""):
                return None
            v = float(v) / 100
        return round(float(v) * 100, 2)
    pr = c.get("price") or {}
    last = pr.get("close_dollars") or pr.get("close")
    return [int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask"), round(bot.fnum(c.get("volume_fp") or c.get("volume"), 0), 2),
            None if last in (None, "") else round(float(last) * 100, 2), px("yes_ask", "low"), px("yes_bid", "high")]


def fetch(only=None):
    for s in SERIES:
        if only and s not in only:
            continue
        mp = os.path.join(CACHE, f"mk_{s}.json.gz")
        have = rj(mp, {}) or {}
        new = list_series(s)
        have.update(new)
        wj(mp, have)
        res = collections.Counter(m["res"] for m in have.values())
        print(f"{s}: {len(have)} markets, {len({m['ev'] for m in have.values()})} events, results {dict(res)}, "
              f"no start {sum(1 for m in have.values() if not m['start'])} ({time.time() - T0:.0f}s)", flush=True)
        cp = os.path.join(CACHE, f"c_{s}.json.gz")
        cs = rj(cp, {}) or {}
        todo = sorted([m for m in have.values() if m["t"] not in cs and m["res"] in ("yes", "no") and m["start"] and m["open"]],
                      key=lambda m: m["start"])
        groups = [todo[i:i + 20] for i in range(0, len(todo), 20)]

        def one(g):
            a = max(min(max(m["open"] - 60, m["start"] - PRE * 60) for m in g), 0)
            b = max(m["start"] for m in g) + 120
            for _ in range(3):
                try:
                    r = kget("/markets/candlesticks", {"market_tickers": ",".join(m["t"] for m in g), "start_ts": a, "end_ts": b, "period_interval": 1})
                    out = {}
                    for x in r.get("markets") or []:
                        out[x.get("market_ticker")] = [crow(c) for c in x.get("candlesticks") or []]
                    return g, out
                except Exception as e:
                    err = e
                    time.sleep(3)
            return g, err
        bad = 0
        with ThreadPoolExecutor(6) as ex:
            for i, (g, out) in enumerate(ex.map(one, groups)):
                if isinstance(out, Exception):
                    bad += 1
                    if bad < 4:
                        print("   candles failed", str(out)[:200], flush=True)
                    continue
                for m in g:
                    st = m["start"]
                    cs[m["t"]] = [r for r in out.get(m["t"]) or [] if st - PRE * 60 - 3600 <= r[0] <= st + 120]
                if i and i % 200 == 0:
                    wj(cp, cs)
                    print(f"   {s} candles {i}/{len(groups)} ({time.time() - T0:.0f}s)", flush=True)
                if time.time() - T0 > 110 * 60:
                    break
        wj(cp, cs)
        print(f"  {s}: candles for {sum(1 for v in cs.values() if v)} of {len(cs)} markets, {bad} failed calls ({time.time() - T0:.0f}s)", flush=True)
        if time.time() - T0 > 110 * 60:
            print("out of time, run again", flush=True)
            return


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    if cmd == "peek":
        peek()
    elif cmd == "fetch":
        fetch(sys.argv[2:] or None)
