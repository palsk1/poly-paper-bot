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


# ================================================================ fetch

CACHE = os.path.join(bot.ROOT, "wx_cache")
OUT = os.path.join(bot.ROOT, "backtest")
HOLDOUT_DAY = "2026-11-10"          # PROTOCOL.md: days from here on are the holdout, never looked at
FIRST_DAY = "2025-12-28"            # Polymarket's oldest closed temperature event ends 2025-12-30
T0 = time.time()
BUDGET_MIN = float(os.environ.get("WX_BUDGET_MIN", "250"))
HOURS_BEFORE = 62                   # keep prices from 62 h before the local day starts
HOURS_AFTER = 8                     # ... to 8 h after it starts


def tsec(x):
    if not x:
        return None
    try:
        return int(dt.datetime.fromisoformat(str(x).replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def save(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    tmp = os.path.join(CACHE, name + ".tmp.gz")
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f)
    os.replace(tmp, os.path.join(CACHE, name + ".json.gz"))


def load(name, default=None):
    pth = os.path.join(CACHE, name + ".json.gz")
    if not os.path.exists(pth):
        return default
    with gzip.open(pth, "rt") as f:
        return json.load(f)


def out_of_time(margin=0):
    return time.time() - T0 > (BUDGET_MIN - margin) * 60


# ---- Polymarket

PEV = "poly_events_v2"   # v1 kept only METAR-settled events (from about Oct 2026); v2 adds the Wunderground ones
MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"), 1)}


def wunder_info(e):
    """(kind, ICAO, local day) for an event that settles on a wunderground.com/history/daily/.../KXXX page, or None."""
    t = str(e.get("title") or "").lower()
    kind = "high" if t.startswith("highest temperature") else "low" if t.startswith("lowest temperature") else None
    src = " ".join([str(e.get("resolutionSource") or ""), str(e.get("description") or "")] +
                   [str(m.get("resolutionSource") or "") + " " + str(m.get("description") or "") for m in (e.get("markets") or [])[:1]])
    ms = re.search(r"wunderground\.com/history/daily/[^\s\"')]*?/([A-Z]{4})\b", src)
    md = re.search(r" on ([a-z]+) (\d{1,2})\b", t)
    end = tsec(e.get("endDate"))
    if not kind or not ms or not md or md.group(1) not in MONTHS or not end:
        return None
    ref = dt.datetime.fromtimestamp(end, UTC).date()
    best = None
    for y in (ref.year - 1, ref.year, ref.year + 1):
        try:
            d = dt.date(y, MONTHS[md.group(1)], int(md.group(2)))
        except ValueError:
            continue
        if best is None or abs((d - ref).days) < abs((best - ref).days):
            best = d
    if best is None or abs((best - ref).days) > 5:
        return None
    return kind, ms.group(1), best.isoformat()


def poly_fix_times(evs, stations):
    """Fill the local calendar day's UTC start/end for Wunderground events (the page shows the local day)."""
    from zoneinfo import ZoneInfo
    n = bad = 0
    for e in evs.values():
        if e.get("s") is not None:
            continue
        tz = (stations.get(e["st"]) or {}).get("tz")
        if not tz:
            bad += 1
            continue
        d = dt.date.fromisoformat(e["day"])
        z = ZoneInfo(tz)
        e["s"] = int(dt.datetime(d.year, d.month, d.day, tzinfo=z).timestamp())
        d2 = d + dt.timedelta(days=1)
        e["e"] = int(dt.datetime(d2.year, d2.month, d2.day, tzinfo=z).timestamp())
        n += 1
    if n:
        save(PEV, evs)
    print(f"poly local days filled: {n}, no time zone: {bad}")


def poly_events():
    """Every closed daily temperature event, slimmed: kind, station, local day (UTC start/end), buckets."""
    have = load(PEV, {})
    if have and not os.environ.get("WX_REFRESH"):
        print(f"poly events cached: {len(have)}")
        return have
    out, cur, n, drop = {}, None, 0, Counter()
    for _ in range(2000):
        p = {"tag_slug": "daily-temperature", "closed": "true", "limit": 100}
        if cur:
            p["after_cursor"] = cur
        try:
            res = bot.http_json(G + "/events/keyset", p)
        except Exception as e:
            print("keyset failed", e)
            break
        evs = bot.envelope_rows(res, "events", "data")
        for e in evs:
            n += 1
            info = bot.wx_event_info(e)
            if info:
                kind, icao, start, end = info
                day = (start + dt.timedelta(hours=12)).date().isoformat()
                s0, e0 = int(start.timestamp()), int(end.timestamp())
            else:
                # older events settle on Wunderground's daily history page: station from its link,
                # day from the title; the local day's start/end is filled in once the station's time zone is known
                old = wunder_info(e)
                if not old:
                    drop["no station/day"] += 1
                    continue
                kind, icao, day = old
                s0 = e0 = None
            if not (FIRST_DAY <= day < HOLDOUT_DAY):
                drop["outside dates"] += 1
                continue
            ms = []
            for m in e.get("markets") or []:
                lab = m.get("groupItemTitle") or ""
                b = bot.wx_bucket(lab)
                toks = bot.market_tokens(m)
                fin = [bot.fnum(x, None) for x in bot.jlist(m.get("outcomePrices"))]
                if not b or len(toks) != 2 or len(fin) != 2:
                    continue
                ms.append({"id": str(m.get("id")), "lab": lab, "lo": None if b[0] == -math.inf else round(b[0], 3),
                           "hi": None if b[1] == math.inf else round(b[1], 3), "u": b[2], "tok": toks[0],
                           "y": 1 if (fin[0] or 0) > 0.5 else 0, "fee": bot.fee_rate(m),
                           "vol": bot.fnum(m.get("volumeNum") or m.get("volume"), 0), "open": tsec(m.get("startDate"))})
            if len(ms) < 3 or sum(x["y"] for x in ms) != 1:
                drop["buckets/winner"] += 1
            else:
                out[str(e.get("id"))] = {"kind": kind, "st": icao, "day": day, "s": s0, "src": "metar" if info else "wunderground",
                                        "e": e0, "title": e.get("title"), "ms": ms,
                                        "open": tsec(e.get("startDate"))}
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not cur or not evs:
            break
    print(f"poly events read: {n}, kept {len(out)} (one winning bucket, in {FIRST_DAY}..{HOLDOUT_DAY}); "
          f"dropped {dict(drop)}; settle source {Counter(x['src'] for x in out.values())}")
    save(PEV, out)
    return out


def hourly_grid(pts, t0, n):
    """[price at the last point at or before each hour t0 + k*3600, at most 3 h stale] for k < n."""
    pts = sorted((int(t), p) for t, p in pts if t is not None and p is not None)
    out, j, last = [], 0, None
    for k in range(n):
        t = t0 + k * 3600
        while j < len(pts) and pts[j][0] <= t:
            last = pts[j]
            j += 1
        out.append(round(last[1], 4) if last and t - last[0] <= 3 * 3600 else None)
    return out


def poly_hist_one(job):
    mid, tok, s = job
    t0 = s - HOURS_BEFORE * 3600
    n = HOURS_BEFORE + HOURS_AFTER + 1
    try:
        res = bot.http_json(C + "/prices-history", {"market": tok, "startTs": t0 - 4 * 3600, "endTs": t0 + n * 3600, "fidelity": 60})
        pts = [(bot.pick(x, "t", "timestamp"), bot.fnum(bot.pick(x, "p", "price"), None))
               for x in bot.envelope_rows(res, "history", "data") if isinstance(x, dict)]
        return mid, hourly_grid(pts, t0, n)
    except Exception as e:
        return mid, None


def poly_fetch():
    evs = poly_events()
    hist = load("poly_hist", {})
    evs = {k: e for k, e in evs.items() if e.get("s") is not None}
    jobs = [(m["id"], m["tok"], e["s"]) for e in sorted(evs.values(), key=lambda e: -e["s"]) for m in e["ms"]
            if m["id"] not in hist]
    print(f"poly price history: {len(hist)} cached, {len(jobs)} to fetch")
    done, fails = 0, 0
    with ThreadPoolExecutor(16) as ex:
        for c in range(0, len(jobs), 3000):
            if out_of_time(15):
                print(f"  time budget used: {len(jobs) - c} left for the next run")
                break
            for mid, g in ex.map(poly_hist_one, jobs[c:c + 3000]):
                if g is None:
                    fails += 1
                else:
                    hist[mid] = g
            done = min(c + 3000, len(jobs))
            save("poly_hist", hist)
            print(f"  {done}/{len(jobs)} ({time.time() - T0:.0f}s, {fails} failed)")
    save("poly_hist", hist)


# ---- Kalshi

def kalshi_series_list():
    r = bot.http_json(K + "/series", {"category": "Climate and Weather"})
    out = []
    for s in r.get("series") or []:
        t, title = s.get("ticker") or "", (s.get("title") or "").lower()
        if s.get("frequency") != "daily" or not ("high" in title or "low" in title or "max" in title or "min" in title):
            continue
        if "hourly" in title or "rain" in title or "snow" in title:
            continue
        out.append(t)
    return sorted(out)


def kslim(m, series):
    return {"t": m.get("ticker"), "e": m.get("event_ticker"), "s": series, "close": tsec(m.get("close_time")),
            "open": tsec(m.get("open_time")), "st": m.get("strike_type"), "lo": m.get("floor_strike"),
            "hi": m.get("cap_strike"), "res": str(m.get("result") or "").lower(),
            "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0), "rules": (m.get("rules_primary") or "")[:400],
            "xv": m.get("expiration_value")}


def kalshi_markets(series):
    out, seen = [], set()
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(60):
            p = {"series_ticker": series, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = bot.http_json(K + path, p)
            except Exception as e:
                print(f"  {series} {path} failed: {e}")
                break
            stop = False
            for m in r.get("markets") or []:
                sm = kslim(m, series)
                if not sm["t"] or sm["t"] in seen or sm["res"] not in ("yes", "no") or not sm["close"]:
                    continue
                day = kday(sm["e"])
                if not day or day < FIRST_DAY:
                    stop = path == "/historical/markets" and bool(day)
                    continue
                if day >= HOLDOUT_DAY:
                    continue
                seen.add(sm["t"])
                out.append(sm)
            cur = r.get("cursor")
            if not cur or not r.get("markets"):
                break
    return out


MON = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1)}


def kday(event_ticker):
    mt = re.search(r"-(\d\d)([A-Z]{3})(\d\d)$", str(event_ticker or ""))
    if not mt or mt.group(2) not in MON:
        return None
    return f"20{mt.group(1)}-{MON[mt.group(2)]:02d}-{int(mt.group(3)):02d}"


def kpx(blk, key):
    blk = blk or {}
    v = blk.get(f"{key}_dollars")
    if v not in (None, ""):
        return bot.fnum(v, None)
    v = blk.get(key)
    if v in (None, ""):
        return None
    if isinstance(v, str) and "." in v or isinstance(v, float):
        return bot.fnum(v, None)
    return bot.fnum(v, 0) / 100


def kcandles_one(m):
    p = {"start_ts": max(m.get("open") or 0, m["close"] - 4 * 86400), "end_ts": m["close"], "period_interval": 60}
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = bot.http_json(K + path, p)
        except Exception:
            continue
        cs = r.get("candlesticks") if isinstance(r, dict) else None
        if cs:
            return m["t"], [[int(c.get("end_period_ts") or 0), kpx(c.get("yes_bid"), "close"), kpx(c.get("yes_ask"), "close"),
                             bot.fnum(c.get("volume_fp") or c.get("volume"), 0)] for c in cs]
    return m["t"], []


def kalshi_fetch():
    mk = load("kalshi_markets", {})
    if not mk:
        ser = kalshi_series_list()
        print(f"kalshi daily temperature series: {len(ser)}: {' '.join(ser)}")
        for s in ser:
            if out_of_time(60):
                break
            mk[s] = kalshi_markets(s)
            print(f"  {s}: {len(mk[s])} settled markets, {len({m['e'] for m in mk[s]})} days")
        save("kalshi_markets", mk)
    cd = load("kalshi_candles", {})
    todo = [m for ms in mk.values() for m in ms if m["t"] not in cd]
    todo.sort(key=lambda m: -m["close"])
    print(f"kalshi candles: {len(cd)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(10) as ex:
        for c in range(0, len(todo), 2000):
            if out_of_time(15):
                print(f"  time budget used: {len(todo) - c} left for the next run")
                break
            for t, rows in ex.map(kcandles_one, todo[c:c + 2000]):
                cd[t] = rows
            save("kalshi_candles", cd)
            print(f"  {min(c + 2000, len(todo))}/{len(todo)} ({time.time() - T0:.0f}s)")
    save("kalshi_candles", cd)


def cli_code(rules):
    mt = re.search(r"\((CLI[A-Z]{3})\)", rules or "")
    return mt.group(1) if mt else None


# ---- stations, forecasts, observations

def station_info(icaos):
    have = load("stations", {})
    todo = sorted(set(icaos) - set(have))
    for i in range(0, len(todo), 20):
        try:
            rows = bot.http_json("https://aviationweather.gov/api/data/stationinfo", {"ids": ",".join(todo[i:i + 20]), "format": "json"})
        except Exception as e:
            print("stationinfo failed", e)
            continue
        for x in rows if isinstance(rows, list) else []:
            sid = x.get("icaoId") or x.get("id")
            if sid and x.get("lat") is not None:
                have[sid] = {"lat": x["lat"], "lon": x["lon"], "elev": x.get("elev")}
    for sid in todo:
        if sid in have and "tz" not in have[sid]:
            try:
                r = bot.http_json(PREV, {"latitude": have[sid]["lat"], "longitude": have[sid]["lon"], "hourly": "temperature_2m",
                                         "timezone": "auto", "forecast_days": 1})
                have[sid]["tz"] = r.get("timezone")
            except Exception as e:
                print("tz failed", sid, e)
            time.sleep(0.3)
    save("stations", have)
    missing = sorted(set(icaos) - set(have))
    print(f"stations: {len(have)} known, missing {missing}")
    return have


MODELS = ("gfs_seamless", "ecmwf_ifs025", "ncep_nbm_conus")
LEADS = (1, 2, 3)


def forecast_one(job):
    sid, lat, lon, model, d0, d1 = job
    hv = ",".join(f"temperature_2m_previous_day{n}" for n in LEADS)
    for attempt in range(4):
        try:
            r = bot.http_json(PREV, {"latitude": lat, "longitude": lon, "hourly": hv, "models": model, "start_date": d0,
                                     "end_date": d1, "timezone": "GMT"}, retries=2)
            h = r.get("hourly") or {}
            times = h.get("time") or []
            if not times:
                return job, None
            t0 = int(dt.datetime.fromisoformat(times[0]).replace(tzinfo=UTC).timestamp())
            cols = {}
            for n in LEADS:
                v = [k for k in h if k.startswith(f"temperature_2m_previous_day{n}")]
                cols[str(n)] = h[v[0]] if v else []
            return job, {"t0": t0, "cols": cols}
        except Exception as e:
            msg = str(e)
            if "400" in msg:
                return job, {"err": msg[:200]}
            time.sleep(20 * (attempt + 1))
    return job, None


def forecasts_fetch(stations, need):
    """need: {station: (first day, last day, us?)}. Open-Meteo previous runs, in 100-day chunks."""
    fc = load("forecasts", {})
    jobs = []
    for sid, (a, b, us) in sorted(need.items()):
        st = stations.get(sid)
        if not st:
            continue
        for model in MODELS:
            if model == "ncep_nbm_conus" and not us:
                continue
            d = dt.date.fromisoformat(a) - dt.timedelta(days=2)
            end = dt.date.fromisoformat(b) + dt.timedelta(days=1)
            while d <= end:
                d1 = min(end, d + dt.timedelta(days=99))
                key = f"{sid}|{model}|{d.isoformat()}"
                if key not in fc:
                    jobs.append((sid, st["lat"], st["lon"], model, d.isoformat(), d1.isoformat()))
                d = d1 + dt.timedelta(days=1)
    print(f"forecasts: {len(fc)} chunks cached, {len(jobs)} to fetch")
    errs = Counter()
    with ThreadPoolExecutor(3) as ex:
        for job, res in ex.map(forecast_one, jobs):
            if res is None:
                errs["no answer"] += 1
                continue
            if "err" in res:
                errs[f"{job[3]}: {res['err'][:120]}"] += 1
            fc[f"{job[0]}|{job[3]}|{job[4]}"] = res
    save("forecasts", fc)
    print(f"forecasts: {len(fc)} chunks; problems {dict(errs)}")


def cli_fetch(icaos):
    """NWS daily climate reports (what Kalshi settles on), from the Iowa State archive."""
    cli = load("cli", {})
    for sid in sorted(icaos):
        for yr in (2025, 2026):
            key = f"{sid}|{yr}"
            if key in cli and yr == 2025:
                continue
            try:
                r = bot.http_json(IEM + "/json/cli.py", {"station": sid, "year": yr})
                cli[key] = [[x.get("valid"), x.get("high"), x.get("low")] for x in r.get("results") or []]
            except Exception as e:
                print("cli failed", key, e)
            time.sleep(1.5)
    save("cli", cli)
    print(f"cli: {sum(len(v) for v in cli.values())} station-days")


def fetch():
    evs = poly_events()
    mk = load("kalshi_markets", {})
    if not mk:
        kalshi_fetch()
        mk = load("kalshi_markets", {})
    # Kalshi station from the rules: '(CLINYC)' -> KNYC
    kst = {}
    for s, ms in mk.items():
        codes = Counter(cli_code(m["rules"]) for m in ms if cli_code(m["rules"]))
        if codes:
            kst[s] = "K" + codes.most_common(1)[0][0][3:]
    print(f"kalshi series -> station: {kst}")
    no_code = sorted(set(mk) - set(kst))
    if no_code:
        print(f"  series without a CLI code (skipped): {no_code}")
        for s in no_code[:5]:
            if mk[s]:
                print(f"   {s}: {mk[s][0]['rules'][:250]}")
    save("kalshi_stations", kst)
    need = {}
    for e in evs.values():
        a, b, _ = need.get(e["st"], (e["day"], e["day"], False))
        need[e["st"]] = (min(a, e["day"]), max(b, e["day"]), e["st"].startswith("K"))
    for s, ms in mk.items():
        if s in kst and ms:
            days = [kday(m["e"]) for m in ms]
            a, b, _ = need.get(kst[s], (min(days), max(days), True))
            need[kst[s]] = (min(a, min(days)), max(b, max(days)), True)
    stations = station_info(need)
    poly_fix_times(evs, stations)
    forecasts_fetch(stations, need)
    cli_fetch(set(kst.values()))
    poly_fetch()     # Polymarket first: Kalshi's candles are slow (about 2 a second) and were fetched in earlier runs
    kalshi_fetch()
    print(f"fetch done in {time.time() - T0:.0f}s")


# ================================================================ test

SLOTS = {"2 days ahead (10am two days before)": 38, "1 day ahead (10am the day before)": 14,
         "evening before (6pm the day before)": 6}
THRESH = (0.03, 0.05, 0.10, 0.15)
PUB_LAG_H = 8                       # a model run counts as public 8 h after its start time (both models need ~4-7 h)
TRAIN_DAYS = 60
MIN_TRAIN = 15
KCONTRACTS = 10
NDIST = None


def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


class Forecasts:
    """Hourly forecasts per (station, model, lead in days) as made public, on one hourly grid."""

    def __init__(self):
        fc = load("forecasts", {})
        self.grid = defaultdict(dict)     # (sid, model) -> {lead: {hour_ts: val}}
        bad = Counter()
        for key, v in fc.items():
            sid, model, _ = key.split("|")
            if not v or "cols" not in v:
                bad[model] += 1
                continue
            g = self.grid[(sid, model)]
            for n, col in v["cols"].items():
                d = g.setdefault(int(n), {})
                for i, x in enumerate(col or []):
                    if x is not None:
                        d[v["t0"] + i * 3600] = x
        self.models = sorted({m for _, m in self.grid})
        print(f"forecast grids: {len(self.grid)} (station, model) pairs, models {self.models}, empty chunks {dict(bad)}")

    def extreme(self, sid, model, kind, s, e, t):
        """Day's max (or min) of the hourly forecast over [s, e), each hour from the newest run public at t, °C."""
        g = self.grid.get((sid, model))
        if not g:
            return None
        vals = []
        for T in range(s, e, 3600):
            v = None
            for n in sorted(g):
                if T - n * 86400 + PUB_LAG_H * 3600 <= t:
                    v = g[n].get(T)
                    break
            if v is None:
                return None
            vals.append(v)
        return max(vals) if kind == "high" else min(vals)


def lst_day_start(day, tzname):
    """Local midnight in STANDARD time (the NWS climate day), as a UTC timestamp."""
    from zoneinfo import ZoneInfo
    z = ZoneInfo(tzname)
    d = dt.date.fromisoformat(day)
    off = dt.datetime(d.year, 1, 15, 12, tzinfo=z).utcoffset()
    return int((dt.datetime(d.year, d.month, d.day) - off).replace(tzinfo=UTC).timestamp())


def c2f(x):
    return x * 1.8 + 32


def targets():
    """One row per (platform, event): station, kind, day, local window, unit, actual value, buckets with results."""
    out = []
    st = load("stations", {})
    # Polymarket: buckets in °C (Fahrenheit buckets were converted), actual = middle of the winning bucket
    for eid, e in load(PEV, {}).items():
        if e.get("s") is None:
            continue
        win = [m for m in e["ms"] if m["y"]][0]
        if win["lo"] is None and win["hi"] is None:
            continue
        a = (win["lo"] + win["hi"]) / 2 if win["lo"] is not None and win["hi"] is not None else \
            (win["hi"] - 0.4 if win["lo"] is None else win["lo"] + 0.4)
        out.append({"pf": "poly", "id": eid, "st": e["st"], "kind": e["kind"], "day": e["day"], "s": e["s"], "e": e["e"],
                    "unit": "C", "actual": a, "ms": [{"id": m["id"], "lo": m["lo"], "hi": m["hi"], "y": m["y"], "fee": m["fee"],
                                                      "vol": m["vol"]} for m in e["ms"]]})
    # Kalshi: strikes in °F, actual = the settled value
    kst = load("kalshi_stations", {})
    by_ev = defaultdict(list)
    for s, ms in load("kalshi_markets", {}).items():
        if s not in kst:
            continue
        for m in ms:
            by_ev[(s, m["e"])].append(m)
    nodata = Counter()
    for (s, ev), ms in by_ev.items():
        sid = kst[s]
        tz = (st.get(sid) or {}).get("tz")
        day = kday(ev)
        if not tz or not day:
            nodata["no tz"] += 1
            continue
        xv = Counter(v for v in (bot.fnum(m.get("xv"), None) for m in ms if m.get("xv") not in (None, "")) if v is not None)
        if not xv:
            nodata["no settle value"] += 1
            continue
        a = xv.most_common(1)[0][0]
        kind = "low" if "LOW" in s.upper() or "MIN" in s.upper() else "high"
        S = lst_day_start(day, tz)
        bks = []
        for m in ms:
            lo = hi = None
            if m["st"] == "between" and m["lo"] is not None and m["hi"] is not None:
                lo, hi = m["lo"] - 0.5, m["hi"] + 0.5
            elif m["st"] == "greater" and m["lo"] is not None:
                lo = m["lo"] + 0.5
            elif m["st"] == "less" and m["hi"] is not None:
                hi = m["hi"] - 0.5
            else:
                continue
            bks.append({"id": m["t"], "lo": lo, "hi": hi, "y": 1 if m["res"] == "yes" else 0, "vol": m["vol"]})
        if bks:
            out.append({"pf": "kalshi", "id": ev, "series": s, "st": sid, "kind": kind, "day": day, "s": S, "e": S + 86400,
                        "unit": "F", "actual": a, "ms": bks})
    print(f"targets: {Counter(t['pf'] for t in out)}; skipped {dict(nodata)}")
    return out


def settle_check(tg):
    """Kalshi: does the settled value put every strike on the side it settled? (catches strike-reading bugs)"""
    ok = bad = 0
    for t in tg:
        if t["pf"] != "kalshi":
            continue
        a = t["actual"]
        for m in t["ms"]:
            inside = (m["lo"] is None or a >= m["lo"]) and (m["hi"] is None or a < m["hi"])
            ok += inside == bool(m["y"])
            bad += inside != bool(m["y"])
    return ok, bad


def build(tg, fcs, placebo=False):
    """Per target and slot: blended forecast, its bias-corrected centre and spread from past errors only."""
    models = [m for m in ("gfs_seamless", "ecmwf_ifs025", "ncep_nbm_conus") if m in fcs.models]
    raw = {}   # (pf, st, kind, slot) -> list of (day, s, e, {model: F}, actual)
    for t in tg:
        for slot, hb in SLOTS.items():
            dec = t["s"] - hb * 3600
            F = {}
            for md in models:
                x = fcs.extreme(t["st"], md, t["kind"], t["s"], t["e"], dec)
                if x is not None:
                    F[md] = c2f(x) if t["unit"] == "F" else x
            if F:
                raw.setdefault((t["pf"], t["st"], t["kind"], slot), []).append((t["day"], t["s"], t["e"], F, t["actual"], t["id"]))
    rows = {}   # (pf, id, slot) -> {"mu", "sd", "F": per model corrected, "n"}
    errs = defaultdict(list)   # (pf, slot, model) -> abs errors after correction
    for key, lst in raw.items():
        pf, sid, kind, slot = key
        lst.sort()
        hb = SLOTS[slot]
        by_day = {x[0]: x for x in lst}
        for i, (day, s, e, F, actual, tid) in enumerate(lst):
            dec = s - hb * 3600
            # training: past days of this station/kind/slot whose result was known 6 h before the decision
            past = [x for x in lst[max(0, i - TRAIN_DAYS - 5):i] if x[2] + 6 * 3600 <= dec][-TRAIN_DAYS:]
            if len(past) < MIN_TRAIN:
                continue
            corr, bias = {}, {}
            for md in F:
                res = [x[4] - x[3][md] for x in past if md in x[3]]
                if len(res) >= MIN_TRAIN:
                    bias[md] = sum(res) / len(res)
                    corr[md] = F[md] + bias[md]
            if not corr:
                continue
            blend_res = [x[4] - sum(x[3][md] + bias[md] for md in corr) / len(corr)
                         for x in past if all(md in x[3] for md in corr)]
            mu = sum(corr.values()) / len(corr)
            if len(blend_res) < MIN_TRAIN:
                continue
            bb = sum(blend_res) / len(blend_res)
            sd = math.sqrt(sum((r - bb) ** 2 for r in blend_res) / (len(blend_res) - 1))
            sd = max(sd, 1.0 if pf == "kalshi" else 0.5)   # never surer than +-1°F / +-0.5°C
            if placebo:
                # the same station's forecast for a day a week earlier: a real forecast, wrong day
                d7 = (dt.date.fromisoformat(day) - dt.timedelta(days=7)).isoformat()
                if d7 not in by_day:
                    continue
                F7 = by_day[d7][3]
                vals = [F7[md] + bias[md] for md in corr if md in F7]
                if not vals:
                    continue
                mu = sum(vals) / len(vals)
            rows[(pf, tid, slot)] = {"mu": mu, "sd": sd, "n": len(blend_res), "models": sorted(corr)}
            if not placebo:
                for md, v in corr.items():
                    errs[(pf, slot, md)].append(abs(actual - v))
                errs[(pf, slot, "blend")].append(abs(actual - mu))
    return rows, errs


def bucket_p(mu, sd, lo, hi):
    a = 0.0 if lo is None else ncdf((lo - mu) / sd)
    b = 1.0 if hi is None else ncdf((hi - mu) / sd)
    return max(0.0, min(1.0, b - a))


def kfee(p):
    return math.ceil(0.07 * KCONTRACTS * p * (1 - p) * 100 - 1e-9) / 100 / KCONTRACTS


def kquote(rows, t):
    best = None
    for r in rows or []:
        if t - 3 * 3600 <= r[0] <= t and r[2] is not None:
            best = r
    if not best:
        return None
    bid, ask = best[1] or 0.0, best[2]
    if not (0 < ask < 1) or bid >= ask:
        return None
    return bid, ask


def points(tg, rows, slip_poly=0.02):
    """Every (target, bucket, slot) with a forecast chance and a price: the costs of YES and NO, and the result."""
    ph, kc = load("poly_hist", {}), load("kalshi_candles", {})
    pts = []
    for t in tg:
        for slot, hb in SLOTS.items():
            r = rows.get((t["pf"], t["id"], slot))
            if not r:
                continue
            dec = t["s"] - hb * 3600
            for m in t["ms"]:
                p = bucket_p(r["mu"], r["sd"], m["lo"], m["hi"])
                if t["pf"] == "poly":
                    g = ph.get(m["id"])
                    k = (dec - (t["s"] - HOURS_BEFORE * 3600)) // 3600
                    if not g or not (0 <= k < len(g)) or g[k] is None or not (0.005 <= g[k] <= 0.995):
                        continue
                    px = g[k]
                    fr = m.get("fee") or 0.0
                    cy = px + slip_poly + fr * px * (1 - px)
                    cn = (1 - px) + slip_poly + fr * px * (1 - px)
                    mid = px
                else:
                    q = kquote(kc.get(m["id"]), dec)
                    if not q:
                        continue
                    bid, ask = q
                    cy = ask + kfee(ask)
                    cn = (1 - bid) + kfee(1 - bid) if bid > 0 else None
                    mid = (bid + ask) / 2
                pts.append({"pf": t["pf"], "id": t["id"], "st": t["st"], "kind": t["kind"], "day": t["day"], "slot": slot,
                            "m": m["id"], "p": p, "mid": mid, "cy": cy, "cn": cn, "y": m["y"], "vol": m.get("vol", 0)})
    return pts


def choose(pts, thr, lo=0.0, hi=1.0):
    """At most one bet per event and slot: the bucket and side where the forecast beats the cost the most."""
    best = {}
    for r in pts:
        for side, cost in ((1, r["cy"]), (0, r["cn"])):
            if cost is None or not (0 < cost < 1) or not (lo <= cost <= hi):
                continue
            edge = (r["p"] if side else 1 - r["p"]) - cost
            if edge < thr:
                continue
            k = (r["pf"], r["id"], r["slot"])
            if k not in best or edge > best[k]["edge"]:
                won = r["y"] == side
                best[k] = dict(r, side=side, cost=cost, edge=edge, won=won, pnl=(1.0 if won else 0.0) - cost)
    return list(best.values())


def twins(bets, pts, rng):
    """Two controls per bet. Coin: same bucket, same moment, the side picked by a coin. Band: a random other
    event's bucket+side at the same slot and platform costing within 3c, so the price level alone is matched."""
    pool = defaultdict(list)
    for r in pts:
        for side, cost in ((1, r["cy"]), (0, r["cn"])):
            if cost is not None and 0 < cost < 1:
                pool[(r["pf"], r["slot"], int(cost * 100))].append((r["id"], (1.0 if r["y"] == side else 0.0) - cost, cost))
    for b in bets:
        cs = [c for c in (b["cy"], b["cn"]) if c is not None and 0 < c < 1]
        b["coin_pnl"] = sum((1.0 if (b["y"] == (1 if c == b["cy"] else 0)) else 0.0) - c for c in cs) / len(cs)
        b["coin_cost"] = sum(cs) / len(cs)
        cand = []
        c0 = int(b["cost"] * 100)
        for cc in range(c0 - 3, c0 + 4):
            cand += [x for x in pool.get((b["pf"], b["slot"], cc), []) if x[0] != b["id"]]
        if cand:
            picks = [rng.choice(cand) for _ in range(20)]
            b["band_pnl"] = sum(x[1] for x in picks) / len(picks)
            b["band_cost"] = sum(x[2] for x in picks) / len(picks)
        else:
            b["band_pnl"], b["band_cost"] = 0.0, b["cost"]
    return bets


def per100(bs, key="pnl", ckey="cost"):
    c = sum(b[ckey] for b in bs)
    return 100 * sum(b[key] for b in bs) / c if c else 0.0


def luck_band(bs, n=1000):
    """90% range of $ per $100 when whole days are re-drawn (one day's weather moves many cities at once)."""
    days = defaultdict(list)
    for b in bs:
        days[b["day"]].append(b)
    keys = list(days)
    if len(keys) < 8:
        return None
    rng = random.Random(11)
    vals = sorted(per100([b for k in (rng.choice(keys) for _ in keys) for b in days[k]]) for _ in range(n))
    return vals[int(0.05 * n)], vals[int(0.95 * n)]


def money(x):
    return ("+" if x >= 0 else "-") + f"${abs(x):.2f}"


def split_days(bs):
    ds = sorted({b["day"] for b in bs})
    if len(ds) < 4:
        return [], []
    cut = ds[len(ds) // 2]
    return [b for b in bs if b["day"] < cut], [b for b in bs if b["day"] >= cut]


def row(name, bs):
    if not bs:
        return f"| {name} | 0 | | | | | | | |"
    lb = luck_band(bs)
    a, b = split_days(bs)
    w = sum(1 for x in bs if x["won"])
    avg = sum(x["cost"] for x in bs) / len(bs)
    return (f"| {name} | {len(bs)} | {w} | {100 * avg:.0f}c | {money(per100(bs))} | "
            + (f"{money(lb[0])} to {money(lb[1])}" if lb else "-")
            + f" | {money(per100(a)) if a else '-'} / {money(per100(b)) if b else '-'} | "
              f"{money(per100(bs, 'coin_pnl', 'coin_cost'))} | {money(per100(bs, 'band_pnl', 'band_cost'))} |")


HDR = ("| Rule | Bets | Won | Avg cost | P&L per $100 | Luck range (90%) | Older / newer half | Coin-flip side | "
       "Same price, other market |\n|---|---|---|---|---|---|---|---|---|")


def brier_rows(pts):
    out = []
    for pf in ("kalshi", "poly"):
        for slot in SLOTS:
            ps = [r for r in pts if r["pf"] == pf and r["slot"] == slot]
            if not ps:
                continue
            bf = sum((r["p"] - r["y"]) ** 2 for r in ps) / len(ps)
            bm = sum((r["mid"] - r["y"]) ** 2 for r in ps) / len(ps)
            mix = sum((0.5 * r["p"] + 0.5 * r["mid"] - r["y"]) ** 2 for r in ps) / len(ps)
            out.append(f"| {pf} | {slot} | {len(ps)} | {bf:.4f} | {bm:.4f} | {mix:.4f} |")
    return out


def calib_rows(pts):
    """Where forecast and price disagree: what really happened."""
    out = []
    for pf in ("kalshi", "poly"):
        g = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
        for r in pts:
            if r["pf"] != pf:
                continue
            d = r["p"] - r["mid"]
            k = "forecast 15c+ lower" if d <= -0.15 else "5-15c lower" if d <= -0.05 else "within 5c" if d < 0.05 \
                else "5-15c higher" if d < 0.15 else "forecast 15c+ higher"
            x = g[k]
            x[0] += 1
            x[1] += r["p"]
            x[2] += r["mid"]
            x[3] += r["y"]
        for k in ("forecast 15c+ lower", "5-15c lower", "within 5c", "5-15c higher", "forecast 15c+ higher"):
            n, sp, sm, sy = g[k]
            if n:
                out.append(f"| {pf} | {k} | {n} | {100 * sp / n:.0f}c | {100 * sm / n:.0f}c | {100 * sy / n:.0f} in 100 |")
    return out


def walk_forward(pts_by_slip):
    """Pick the best threshold on one half, score it on the other, both ways."""
    out = []
    for pf in ("kalshi", "poly"):
        pts = pts_by_slip[pf]
        days = sorted({r["day"] for r in pts})
        if len(days) < 10:
            continue
        cut = days[len(days) // 2]
        A = [r for r in pts if r["day"] < cut]
        B = [r for r in pts if r["day"] >= cut]
        for name, tr, te in (("pick on older, score newer", A, B), ("pick on newer, score older", B, A)):
            best = max(THRESH, key=lambda th: per100(choose(tr, th)) if choose(tr, th) else -1e9)
            bs = choose(te, best)
            out.append(f"| {pf} | {name} | {int(best * 100)}c | {money(per100(choose(tr, best)))} | {len(bs)} bets, {money(per100(bs))} |")
    return out


def run():
    tg = targets()
    ok, bad = settle_check(tg)
    fcs = Forecasts()
    rows, errs = build(tg, fcs)
    prow, _ = build(tg, fcs, placebo=True)
    P = {pf: [r for r in points(tg, rows) if r["pf"] == pf] for pf in ("kalshi", "poly")}
    P5 = [r for r in points(tg, rows, slip_poly=0.05) if r["pf"] == "poly"]
    PP = points(tg, prow)
    rng = random.Random(5)
    L = ["# Weather forecasts vs weather markets (wxcast.py)", "",
         f"Written by `python3 wxcast.py run` on {dt.date.today().isoformat()}. Research only, no track. "
         f"Days {FIRST_DAY} to {HOLDOUT_DAY} (the holdout from PROTOCOL.md is left out).", "",
         "**Question:** do free professional forecasts (NOAA's GFS, Europe's ECMWF, NOAA's National Blend where it "
         "exists, all as Open-Meteo stored them *when they were made*) know tomorrow's high or low temperature better "
         "than Kalshi and Polymarket prices, by enough to pay the costs?", "",
         "**How:** for every finished daily high/low market, at three moments (10am two days before, 10am the day "
         "before, 6pm the day before), take the forecast that was public then (a run counts 8 hours after it started), "
         f"correct it by how far it missed at that station over the last {TRAIN_DAYS} finished days (only days already "
         "settled at the time), and turn it into a chance per bucket with the spread of those past misses. "
         "Then buy the one bucket+side per market where the forecast beats the cost by the most, if by at least the "
         "threshold. Kalshi: the real hourly ask (YES) or bid (NO buys at 1 - bid), plus the taker fee for 10 "
         "contracts. Polymarket: history has no order book, so the listed price **+2c** plus the fee "
         "(PROTOCOL.md pessimistic case), and +5c as a stress test. Held to the result.", "",
         f"Kalshi settle check: {ok} strikes agree with the settled temperature, {bad} don't "
         "(should be about 0; non-zero means a strike-reading bug).", ""]
    L += ["## Who knows the temperature better? (lower is better)", "",
          "Average miss in degrees (Kalshi in °F, Polymarket in °C) of each forecast after the bias fix. "
          "For comparison, 1°F is about half a bucket on Kalshi, 1°C is one bucket on Polymarket.", "",
          "| Market | When | Model | Days | Average miss |", "|---|---|---|---|---|"]
    for (pf, slot, md), v in sorted(errs.items()):
        L.append(f"| {pf} | {slot} | {md} | {len(v)} | {sum(v) / len(v):.2f}° |")
    L += ["", "Score per bucket (Brier: 0 = perfect, lower is better). 'Half and half' averages the two.", "",
          "| Market | When | Buckets | Forecast | Market price | Half and half |", "|---|---|---|---|---|---|"]
    L += brier_rows(P["kalshi"] + P["poly"])
    L += ["", "When the forecast and the price disagree, who was right? (average forecast chance, average price, "
          "how often the bucket really won)", "",
          "| Market | Forecast vs price | Buckets | Forecast said | Price said | Really won |", "|---|---|---|---|---|---|"]
    L += calib_rows(P["kalshi"] + P["poly"])
    for pf, label in (("kalshi", "Kalshi (real asks and bids, fee for 10 contracts)"),
                      ("poly", "Polymarket (listed price +2c, plus fee)")):
        L += ["", f"## Betting the forecast: {label}", "", HDR]
        for th in THRESH:
            bs = twins(choose(P[pf], th), P[pf], rng)
            L.append(row(f"forecast beats cost by {int(th * 100)}c+, all moments", bs))
        for slot in SLOTS:
            bs = twins(choose([r for r in P[pf] if r["slot"] == slot], 0.05), P[pf], rng)
            L.append(row(f"5c+, {slot}", bs))
        for lo, hi, nm in ((0.0, 0.25, "cost under 25c"), (0.25, 0.75, "cost 25-75c"), (0.75, 1.0, "cost over 75c")):
            bs = twins(choose(P[pf], 0.05, lo, hi), P[pf], rng)
            L.append(row(f"5c+, {nm}", bs))
        for kind in ("high", "low"):
            bs = twins(choose([r for r in P[pf] if r["kind"] == kind], 0.05), P[pf], rng)
            L.append(row(f"5c+, daily {kind}s only", bs))
        bs = twins(choose([r for r in P[pf] if r["vol"] >= 5000], 0.05), P[pf], rng)
        L.append(row("5c+, buckets that traded $5k+", bs))
        pl = [r for r in PP if r["pf"] == pf]
        bs = twins(choose(pl, 0.05), pl, rng)
        L.append(row("PLACEBO: a week-old forecast for the wrong day, 5c+", bs))
        if pf == "poly":
            bs = twins(choose(P5, 0.05), P5, rng)
            L.append(row("5c+, stress: listed price +5c", bs))
    L += ["", "## Walk-forward (pick the threshold on one half, score it on the other)", "",
          "| Market | Direction | Picked | On the picking half | On the other half |", "|---|---|---|---|---|"]
    L += walk_forward(P)
    # per-station view for the 5c rule, to see if one city carries it
    L += ["", "## By station (5c+ rule, all moments)", "", "| Market | Station | Bets | P&L per $100 |", "|---|---|---|---|"]
    for pf in ("kalshi", "poly"):
        bs = choose(P[pf], 0.05)
        by = defaultdict(list)
        for b in bs:
            by[b["st"]].append(b)
        for sid, x in sorted(by.items(), key=lambda kv: -len(kv[1]))[:25]:
            L.append(f"| {pf} | {sid} | {len(x)} | {money(per100(x))} |")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "wxcast.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


def run_all():
    fetch()
    if not out_of_time(5):
        run()


MODES = {"scan": scan, "fetch": fetch, "run": run, "all": run_all}

if __name__ == "__main__":
    MODES[sys.argv[1] if len(sys.argv) > 1 else "scan"]()
