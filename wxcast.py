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

def poly_events():
    """Every closed daily temperature event, slimmed: kind, station, local day (UTC start/end), buckets."""
    have = load("poly_events", {})
    if have and not os.environ.get("WX_REFRESH"):
        print(f"poly events cached: {len(have)}")
        return have
    out, cur, n = {}, None, 0
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
            if not info:
                continue
            kind, icao, start, end = info
            day = (start + dt.timedelta(hours=12)).date().isoformat()
            if not (FIRST_DAY <= day < HOLDOUT_DAY):
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
            if len(ms) >= 3 and sum(x["y"] for x in ms) == 1:
                out[str(e.get("id"))] = {"kind": kind, "st": icao, "day": day, "s": int(start.timestamp()),
                                        "e": int(end.timestamp()), "title": e.get("title"), "ms": ms,
                                        "open": tsec(e.get("startDate"))}
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not cur or not evs:
            break
    print(f"poly events read: {n}, kept {len(out)} (one winning bucket, in {FIRST_DAY}..{HOLDOUT_DAY})")
    save("poly_events", out)
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
    forecasts_fetch(stations, need)
    cli_fetch(set(kst.values()))
    kalshi_fetch()
    poly_fetch()
    print(f"fetch done in {time.time() - T0:.0f}s")


MODES = {"scan": scan, "fetch": fetch}

if __name__ == "__main__":
    MODES[sys.argv[1] if len(sys.argv) > 1 else "scan"]()
