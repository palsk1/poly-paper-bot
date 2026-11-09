#!/usr/bin/env python3
"""Economic data markets vs free professional forecasts (2026-11-09).

PAPER ONLY. Reads public data, never trades.

Kalshi (and some Polymarket) list bucket/range markets on CPI, jobs, jobless claims, GDP and Fed decisions.
Free forecasts exist: Cleveland Fed inflation nowcast, Atlanta Fed GDPNow, and simple models from past data
(FRED). This tool tests, on finished markets, whether those forecasts beat the market price after costs.

    python3 econ.py scan       # print API shapes and which forecast sources answer (debugging)
  From GitHub: probe workflow with what = econ_scan.
"""
import csv
import datetime as dt
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

import bot

K = bot.KALSHI
G = bot.GAMMA
UTC = dt.timezone.utc


def raw(url, n=None):
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read()
            return r.status, b, r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400], None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode(), None


def kget(path, params=None):
    return bot.http_json(K + path, params)


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


SOURCES = {
    "cleveland nowcast page": "https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting",
    "gdpnow page": "https://www.atlantafed.org/cqer/research/gdpnow",
    "gdpnow xlsx": "https://www.atlantafed.org/-/media/documents/cqer/researchcq/gdpnow/GDPTrackingModelDataAndForecasts.xlsx",
    "fred ICSA": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=ICSA",
    "fred PAYEMS": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PAYEMS",
    "alfred PAYEMS vintage": "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=2026-06-01",
    "fred GDPNOW": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPNOW",
    "philly fed SPF": "https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters",
}


def scan():
    for name, url in SOURCES.items():
        st, body, ct = raw(url)
        print(f"\n== source {name}: HTTP {st}, {len(body)} bytes, {ct}")
        txt = body.decode("utf-8", "replace") if body and not (ct or "").startswith("application/vnd") else ""
        if url.endswith(".csv") or "csv" in url:
            print("  ", txt[:150].replace("\n", " | "), " ... ", txt[-120:].replace("\n", " | "))
        elif txt:
            links = sorted(set(re.findall(r'["\'(]([^"\'()\s]+\.(?:json|csv|xlsx|xls|zip)[^"\'()\s]*)', txt)))
            print("   data links:", links[:60])
            apis = sorted(set(re.findall(r'["\'](/api/[^"\']+|https?://[^"\']*api[^"\']*)["\']', txt)))
            print("   api-ish:", apis[:40])
        elif body:
            print("   binary, starts", body[:8])
    show("kalshi econ series", lambda: [(s.get("ticker"), s.get("title"), s.get("frequency"))
                                        for s in (kget("/series", {"category": "Economics"}).get("series") or [])], 6000)
    show("historical cutoff", lambda: kget("/historical/cutoff"))
    for s in ("KXCPI", "KXCPIYOY", "KXCPICORE", "KXPAYROLLS", "KXU3", "KXGDP", "KXJOBLESSCLAIMS", "KXFED",
              "KXFEDDECISION", "KXECONSTATCPI", "CPI", "FED"):
        def one(s=s):
            r = kget("/markets", {"series_ticker": s, "status": "settled", "limit": 200})
            ms = r.get("markets") or []
            h = kget("/historical/markets", {"series_ticker": s, "limit": 200})
            hs = h.get("markets") or []
            ex = (ms or hs or [{}])[0]
            keep = {k: ex.get(k) for k in ("ticker", "event_ticker", "title", "subtitle", "yes_sub_title", "close_time",
                                           "expiration_time", "result", "strike_type", "floor_strike", "cap_strike",
                                           "volume", "volume_fp", "rules_primary", "last_price_dollars")}
            return {"settled_live": len(ms), "historical": len(hs), "events": len({m.get("event_ticker") for m in ms + hs}),
                    "example": keep}
        show(f"kalshi series {s}", one, 1800)
    for tag in ("economy", "fed-rates", "inflation", "cpi", "jobs-report", "economic-policy", "fed"):
        show(f"poly tag {tag}", lambda tag=tag: [(e.get("title"), e.get("endDate"), len(e.get("markets") or []),
                                                  round(bot.fnum(e.get("volume"), 0)))
                                                 for e in bot.http_json(f"{G}/events", {"tag_slug": tag, "closed": "true",
                                                                                         "limit": 30, "order": "endDate",
                                                                                         "ascending": "false"})], 2500)


def scan2():
    base = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/"
    for f in ("nowcast_month.json", "nowcast_year.json"):
        st, b, ct = raw(base + f + "?sc_lang=en")
        print(f"\n== {f}: HTTP {st} {len(b)} bytes")
        try:
            j = json.loads(b.decode("utf-8-sig"))
        except Exception as e:
            print("not json", e, b[:300]); continue
        def walk(o, path="", depth=0):
            if depth > 5: return
            if isinstance(o, dict):
                print("  " * depth + f"{path} dict keys={list(o.keys())[:15]}")
                for k in list(o.keys())[:4]:
                    walk(o[k], f"{path}.{k}", depth + 1)
            elif isinstance(o, list):
                print("  " * depth + f"{path} list len={len(o)} first={json.dumps(o[0], default=str)[:300] if o else None}")
                if o: walk(o[0], path + "[0]", depth + 1)
                if len(o) > 1: print("  " * depth + f"   last={json.dumps(o[-1], default=str)[:300]}")
        walk(j)
        print("  head:", json.dumps(j)[:1500])
    for url in ("https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/gdpnow/GDPTrackingModelDataAndForecasts.xlsx",
                "https://www.frbatlanta.org/-/media/Documents/cqer/researchcq/gdpnow/GDPTrackingModelDataAndForecasts.xlsx",
                "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/gdpnow/GDPNowcastDataReleaseDates.xlsx"):
        st, b, ct = raw(url)
        print(f"\n== {url}: HTTP {st} {len(b)} bytes {ct}")
        if st == 200 and b[:2] == b"PK":
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
            for ws in wb.worksheets:
                rows = list(ws.iter_rows(max_row=6, values_only=True))
                print(f"  sheet {ws.title!r} dims={ws.max_row}x{ws.max_column}")
                for r in rows:
                    print("    ", [str(x)[:22] for x in r[:14]])
    # Kalshi candles on an old CPI market, hourly
    for tk, ser in (("KXCPI-25JUN-T0.3", "KXCPI"), ("KXJOBLESSCLAIMS-26NOV05-220000", "KXJOBLESSCLAIMS")):
        for path in (f"/series/{ser}/markets/{tk}/candlesticks", f"/historical/markets/{tk}/candlesticks"):
            show(f"candles {path}", lambda path=path: (lambda r: {"n": len(r.get("candlesticks") or []),
                 "first": (r.get("candlesticks") or [None])[0], "last": (r.get("candlesticks") or [None])[-1]})(
                 kget(path, {"start_ts": int(time.time()) - 86400 * 600, "end_ts": int(time.time()), "period_interval": 60})), 2500)
    # how far back each series goes
    for s in ("KXCPI", "KXCPICORE", "KXCPIYOY", "KXGDP", "KXJOBLESSCLAIMS", "KXU3", "KXPAYROLLS", "KXECONSTATCPI"):
        evs, cur = set(), None
        oldest = None
        for _ in range(30):
            p = {"series_ticker": s, "limit": 1000}
            if cur: p["cursor"] = cur
            r = kget("/historical/markets", p)
            for m in r.get("markets") or []:
                evs.add(m.get("event_ticker"))
                c = m.get("close_time")
                oldest = c if oldest is None or (c and c < oldest) else oldest
            cur = r.get("cursor")
            if not cur or not r.get("markets"): break
        print(f"\n== {s} historical: {len(evs)} events, oldest close {oldest}")
    ev = kget("/markets", {"event_ticker": "KXJOBLESSCLAIMS-26OCT29"}).get("markets") or []
    print("\n== claims event strikes:", [(m.get("ticker"), m.get("strike_type"), m.get("floor_strike"), m.get("result"), m.get("volume_fp")) for m in ev])



# ================================================================ fetch

import gzip
import math
import os
import random
import statistics
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

CACHE = os.path.join(bot.ROOT, "econ_cache")
OUT = os.path.join(bot.ROOT, "backtest")
HOLDOUT_TS = int(dt.datetime(2026, 11, 10, tzinfo=UTC).timestamp())   # PROTOCOL.md: never look past this
CLE = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/"
GDPNOW_XLSX = ("https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/gdpnow/"
               "GDPTrackingModelDataAndForecasts.xlsx")
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
ALFRED = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id="
# series -> (what it measures, reporting step)
SERIES = {"KXCPI": ("cpi", 0.1), "KXCPICORE": ("core", 0.1), "KXCPIYOY": ("cpi_yoy", 0.1),
          "KXECONSTATCPI": ("cpi", 0.1), "KXGDP": ("gdp", 0.1), "KXJOBLESSCLAIMS": ("claims", 1000),
          "KXU3": ("u3", 0.1), "KXPAYROLLS": ("payrolls", 1000)}
HOURS = (1, 6, 24, 72)
WORKERS = 12


def tsec(x):
    if not x:
        return None
    try:
        return int(dt.datetime.fromisoformat(str(x).replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def save(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(os.path.join(CACHE, name + ".json.gz"), "wt") as f:
        json.dump(obj, f)


def load(name):
    pth = os.path.join(CACHE, name + ".json.gz")
    if not os.path.exists(pth):
        return None
    with gzip.open(pth, "rt") as f:
        return json.load(f)


def fetch_cleveland():
    """{kind: {"YYYY-MM": {"now": [[date, value], ...], "actual": value, "actual_date": date}}}"""
    out = {}
    names = {"month": {"CPI Inflation": "cpi", "Core CPI Inflation": "core"},
             "year": {"CPI Inflation": "cpi_yoy", "Core CPI Inflation": "core_yoy"}}
    for f, nm in names.items():
        st, b, _ = raw(CLE + f"nowcast_{f}.json?sc_lang=en")
        j = json.loads(b.decode("utf-8-sig"))
        for blk in j:
            sub = (blk.get("chart") or {}).get("subcaption", "")
            mt = re.match(r"(\d{4})-(\d{1,2})", sub)
            if not mt:
                continue
            ty, tm = int(mt.group(1)), int(mt.group(2))
            cats = [c.get("label") for c in (blk.get("categories") or [{}])[0].get("category", []) if not c.get("vline")]
            dates = []
            for lab in cats:
                mm = re.match(r"(\d{1,2})/(\d{1,2})", lab or "")
                if not mm:
                    dates.append(None)
                    continue
                m_, d_ = int(mm.group(1)), int(mm.group(2))
                y_ = ty + (1 if m_ < tm - 6 else 0)
                dates.append(f"{y_:04d}-{m_:02d}-{d_:02d}")
            for ds in blk.get("dataset") or []:
                sn = (ds.get("seriesname") or "").strip()
                act = sn.startswith("Actual ")
                kind = nm.get(sn[7:] if act else sn)
                if not kind:
                    continue
                rec = out.setdefault(kind, {}).setdefault(f"{ty:04d}-{tm:02d}", {"now": []})
                for d, pt in zip(dates, ds.get("data") or []):
                    v = pt.get("value")
                    if d is None or v in ("", None):
                        continue
                    if act:
                        rec["actual"], rec["actual_date"] = float(v), d
                    else:
                        rec["now"].append([d, float(v)])
    for k, v in out.items():
        n_act = sum(1 for r in v.values() if "actual" in r)
        print(f"  cleveland {k}: {len(v)} target months, {n_act} with actual")
    return out


def fetch_gdpnow():
    import openpyxl
    st, b, _ = raw(GDPNOW_XLSX)
    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
    out = {"now": [], "actual": {}}
    for sheet in ("TrackingDeepArchives", "TrackingArchives"):
        ws = wb[sheet]
        rows = ws.iter_rows(values_only=True)
        hdr = [str(x or "") for x in next(rows)]
        gi = next((i for i, h in enumerate(hdr) if h.strip().lower() in ("gdp", "gdpnow", "real gdp")), None)
        if gi is None:
            gi = next((i for i, h in enumerate(hdr) if "gdp" in h.lower()), None)
        print(f"  gdpnow {sheet}: header {hdr[:3]} ... gdp column {gi}={hdr[gi] if gi is not None else None}")
        if gi is None:
            continue
        for r in rows:
            d, q, v = r[0], r[1], r[gi]
            if isinstance(d, dt.datetime) and isinstance(q, dt.datetime) and isinstance(v, (int, float)):
                out["now"].append([d.date().isoformat(), q.date().isoformat(), float(v)])
    ws = wb["TrackRecord"]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if isinstance(r[0], dt.datetime) and isinstance(r[2], (int, float)):
            out["actual"][r[0].date().isoformat()] = [float(r[2]), r[3].date().isoformat() if isinstance(r[3], dt.datetime) else None,
                                                      float(r[1]) if isinstance(r[1], (int, float)) else None]
    out["now"] = sorted({(a, b_, c) for a, b_, c in out["now"]})
    print(f"  gdpnow: {len(out['now'])} daily nowcasts, {len(out['actual'])} quarters with advance estimate")
    return out


def fred_csv(url):
    st, b, _ = raw(url)
    if st != 200:
        raise RuntimeError(f"HTTP {st} {url}")
    rows = list(csv.reader(io.StringIO(b.decode("utf-8", "replace"))))
    out = []
    for r in rows[1:]:
        try:
            out.append([r[0], float(r[1])])
        except Exception:
            pass
    return out


def kslim(m, series):
    return {"t": m.get("ticker"), "e": m.get("event_ticker"), "s": series, "close": tsec(m.get("close_time")),
            "st": m.get("strike_type"), "lo": m.get("floor_strike"), "hi": m.get("cap_strike"),
            "sub": m.get("yes_sub_title"), "res": str(m.get("result") or "").lower(),
            "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0), "rules": (m.get("rules_primary") or "")[:300]}


def kalshi_markets(series):
    out, seen = [], set()
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(50):
            p = {"series_ticker": series, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  {series} {path} failed: {e}")
                break
            for m in r.get("markets") or []:
                sm = kslim(m, series)
                if sm["t"] and sm["t"] not in seen and sm["res"] in ("yes", "no") and sm["close"]:
                    seen.add(sm["t"])
                    out.append(sm)
            cur = r.get("cursor")
            if not cur or not r.get("markets"):
                break
    return out


def kpx(v, suffixed):
    """Kalshi price in dollars. '*_dollars' fields are dollars; the old un-suffixed fields are integer cents on the
    live API but dollar strings like "0.36" on /historical (found 2026-11-09: reading them as cents gave 100x too
    small prices)."""
    if v in (None, ""):
        return None
    if suffixed:
        return bot.fnum(v, None)
    if isinstance(v, str) and "." in v or isinstance(v, float):
        return bot.fnum(v, None)
    return bot.fnum(v, 0) / 100


_SHOWN = set()


def candle_row(c, path=""):
    if path not in _SHOWN:
        _SHOWN.add(path)
        print(f"  raw candle from {path}: {json.dumps(c)[:600]}")

    def px(block, key):
        blk = c.get(block) or {}
        if blk.get(f"{key}_dollars") not in (None, ""):
            return kpx(blk.get(f"{key}_dollars"), True)
        return kpx(blk.get(key), False)
    return [int(c.get("end_period_ts") or 0), px("yes_bid", "close"), px("yes_ask", "close"),
            bot.fnum(c.get("volume_fp") or c.get("volume"), 0)]


def kalshi_candles(m):
    p = {"start_ts": m["close"] - 8 * 86400, "end_ts": m["close"], "period_interval": 60}
    errs = []
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = kget(path, p)
        except Exception as e:
            errs.append(str(e)[:80])
            continue
        cs = r.get("candlesticks") if isinstance(r, dict) else None
        if cs:
            return [candle_row(c, path.split('/')[1]) for c in cs]
    return []


def fetch():
    t0 = time.time()
    cle = load("cleveland") or {}
    if not cle:
        cle = fetch_cleveland()
        save("cleveland", cle)
    if not load("gdpnow"):
        save("gdpnow", fetch_gdpnow())
    if not load("fred"):
        save("fred", {k: fred_csv(FRED + k) for k in ("ICSA", "UNRATE", "PAYEMS")})
    print(f"forecasts done ({time.time() - t0:.0f}s)")
    mk = load("markets") or {}
    for s in SERIES:
        if s not in mk:
            mk[s] = [m for m in kalshi_markets(s) if m["close"] < HOLDOUT_TS]
            print(f"  {s}: {len(mk[s])} settled markets, {len({m['e'] for m in mk[s]})} events")
    save("markets", mk)
    # ALFRED vintages: what was known the day before each release (claims, jobs)
    vint = load("vintages") or {}
    need = set()
    for s, sid in (("KXJOBLESSCLAIMS", "ICSA"), ("KXU3", "UNRATE"), ("KXPAYROLLS", "PAYEMS")):
        for m in mk.get(s, []):
            d = dt.datetime.fromtimestamp(m["close"], UTC).date()
            need.add((sid, (d - dt.timedelta(days=1)).isoformat()))
            need.add((sid, (d + dt.timedelta(days=1)).isoformat()))   # first print, for checking
    todo = [x for x in sorted(need) if f"{x[0]}|{x[1]}" not in vint]
    print(f"  alfred vintages: {len(todo)} to fetch")

    def one(x):
        sid, d = x
        try:
            rows = fred_csv(f"{ALFRED}{sid}&vintage_date={d}")
            return f"{sid}|{d}", rows[-30:]
        except Exception as e:
            return f"{sid}|{d}", None
    with ThreadPoolExecutor(4) as ex:
        for k, v in ex.map(one, todo):
            if v:
                vint[k] = v
    save("vintages", vint)
    print(f"  vintages cached: {len(vint)} ({time.time() - t0:.0f}s)")
    cd = load("candles2") or {}
    allm = [m for ms in mk.values() for m in ms if m["t"] not in cd]
    print(f"  candles to fetch: {len(allm)}")
    done = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for m, c in zip(allm, ex.map(kalshi_candles, allm)):
            cd[m["t"]] = c
            done += 1
            if done % 500 == 0:
                print(f"    {done}/{len(allm)} ({time.time() - t0:.0f}s)")
                save("candles2", cd)
    save("candles2", cd)
    print(f"  candles: {sum(1 for v in cd.values() if v)} of {len(cd)} markets have history ({time.time() - t0:.0f}s)")
    for s in SERIES:
        try:
            r = kget(f"/series/{s}").get("series") or {}
            print(f"  fee {s}: {r.get('fee_type')} x{r.get('fee_multiplier')}")
        except Exception as e:
            print(f"  fee {s}: {e}")


# ================================================================ test

MON = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1)}
COVID = ("2020-03-01", "2021-12-31")
THRESH = (0.0, 0.03, 0.05, 0.10)
CONTRACTS = 20


def dstr(ts):
    return dt.datetime.fromtimestamp(ts, UTC).date().isoformat()


def ev_month(e):
    mt = re.search(r"-(\d{2})([A-Z]{3})", e or "")
    return f"20{mt.group(1)}-{MON[mt.group(2)]:02d}" if mt and mt.group(2) in MON else None


def prev_month(ym):
    y, m = map(int, ym.split("-"))
    return f"{y - (m == 1):04d}-{(m - 2) % 12 + 1:02d}"


def kfee(p):
    return math.ceil(0.07 * CONTRACTS * p * (1 - p) * 100 - 1e-9) / 100 / CONTRACTS


def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def sat(v, m):
    st, lo, hi = m["st"], m["lo"], m["hi"]
    e = 1e-9
    if st == "greater":
        return v > lo + e
    if st == "greater_or_equal":
        return v >= lo - e
    if st == "less":
        return v < hi - e
    if st == "less_or_equal":
        return v <= hi + e
    if st == "between":
        return lo - e <= v <= hi + e
    sub = (m.get("sub") or "").lower().replace(",", "")
    x = re.search(r"(-?\d+(?:\.\d+)?)", sub)
    if not x:
        return None
    x = float(x.group(1))
    if "exactly" in sub:
        return abs(v - x) < 1e-6
    if "above" in sub or "more than" in sub:
        return v > x + e
    if "below" in sub or "less than" in sub:
        return v < x - e
    if "at least" in sub or "or more" in sub:
        return v >= x - e
    return None


def rnd(v, step):
    return round(round(v / step) * step, 6)


def prob(mu, sd, step, m):
    """P(the reported number, rounded to step, makes this market YES) with value ~ Normal(mu, sd)."""
    lo_r, hi_r = rnd(mu - 6 * sd, step), rnd(mu + 6 * sd, step)
    n = int(round((hi_r - lo_r) / step)) + 1
    p = 0.0
    for i in range(n):
        r = round(lo_r + i * step, 6)
        w = ncdf((r + step / 2 - mu) / sd) - ncdf((r - step / 2 - mu) / sd)
        if w > 1e-12 and sat(r, m):
            p += w
    return min(max(p, 0.0), 1.0)


class Models:
    """forecast(kind, event, t) -> (mu, sd) as known at time t, and actual(kind, event)."""

    def __init__(self):
        self.cle = load("cleveland") or {}
        self.gdp = load("gdpnow") or {"now": [], "actual": {}}
        self.fred = load("fred") or {}
        self.vint = load("vintages") or {}

    # --- inflation (Cleveland Fed nowcast)
    def _cle_at(self, kind, ym, before):
        rec = self.cle.get(kind, {}).get(ym)
        if not rec:
            return None
        pts = [v for d, v in rec["now"] if d < before]
        return pts[-1] if pts else None

    def _cle_sd(self, kind, today, lag):
        errs = []
        for ym, rec in self.cle.get(kind, {}).items():
            ad = rec.get("actual_date")
            if "actual" not in rec or not ad or ad >= today:
                continue
            before = (dt.date.fromisoformat(ad) - dt.timedelta(days=lag - 1)).isoformat()
            f = self._cle_at(kind, ym, before)
            if f is not None:
                errs.append(rec["actual"] - f)
        if len(errs) < 24:
            return None
        return math.sqrt(sum(e * e for e in errs) / len(errs))

    # --- jobs/claims (FRED vintages)
    def _vint(self, sid, d):
        return self.vint.get(f"{sid}|{d}")

    def _hist_sd(self, sid, today, n, fn):
        rows = [(d, v) for d, v in self.fred.get(sid, []) if d < today]
        rows = rows[-(n + 4):]
        errs = []
        for i in range(4, len(rows)):
            if COVID[0] <= rows[i][0] <= COVID[1] or COVID[0] <= rows[i - 4][0] <= COVID[1]:
                continue
            errs.append(fn(rows, i))
        if len(errs) < 20:
            return None
        return math.sqrt(sum(e * e for e in errs) / len(errs))

    def forecast(self, kind, m, t):
        today = dstr(t)
        lag = max(1, math.ceil((m["close"] - t) / 86400))
        if kind in ("cpi", "core", "cpi_yoy"):
            ym = ev_month(m["e"])
            mu = self._cle_at(kind, ym, today) if ym else None
            sd = self._cle_sd(kind, today, lag)
            return (mu, sd) if mu is not None and sd else None
        if kind == "gdp":
            q = self._quarter(m)
            pts = [v for d, qq, v in self.gdp["now"] if qq == q and d < today]
            errs = [a - f for qq, (a, rd, f) in self.gdp["actual"].items()
                    if f is not None and (dt.date.fromisoformat(qq) + dt.timedelta(days=40)).isoformat() < today]
            if not pts or len(errs) < 12:
                return None
            return pts[-1], math.sqrt(sum(e * e for e in errs) / len(errs))
        cd = dt.date.fromisoformat(dstr(m["close"]))
        vb = self._vint({"claims": "ICSA", "u3": "UNRATE", "payrolls": "PAYEMS"}[kind], (cd - dt.timedelta(days=1)).isoformat())
        if not vb:
            return None
        if kind == "claims":
            sd = self._hist_sd("ICSA", today, 104, lambda r, i: r[i][1] - r[i - 1][1])
            return (vb[-1][1], sd) if sd else None
        if kind == "u3":
            ym = ev_month(m["e"])
            last = [v for d, v in vb if d[:7] == prev_month(ym)]
            sd = self._hist_sd("UNRATE", today, 120, lambda r, i: r[i][1] - r[i - 1][1])
            return (last[0], sd) if last and sd else None
        if kind == "payrolls":
            ch = [(vb[i][0], (vb[i][1] - vb[i - 1][1]) * 1000) for i in range(1, len(vb))]
            ym = ev_month(m["e"])
            prior = [c for d, c in ch if d[:7] < ym][-3:]
            sd = self._hist_sd("PAYEMS", today, 120,
                               lambda r, i: ((r[i][1] - r[i - 1][1]) - sum(r[j][1] - r[j - 1][1] for j in (i - 1, i - 2, i - 3)) / 3) * 1000)
            return (sum(prior) / 3, sd) if len(prior) == 3 and sd else None
        return None

    def _quarter(self, m):
        d = dt.date.fromisoformat(dstr(m["close"]))
        qe = [dt.date(d.year - 1, 12, 31), dt.date(d.year, 3, 31), dt.date(d.year, 6, 30), dt.date(d.year, 9, 30)]
        return max(x for x in qe if x < d - dt.timedelta(days=14)).isoformat()

    def actual(self, kind, m):
        if kind in ("cpi", "core", "cpi_yoy"):
            rec = self.cle.get(kind, {}).get(ev_month(m["e"]) or "")
            return rec.get("actual") if rec else None
        if kind == "gdp":
            a = self.gdp["actual"].get(self._quarter(m))
            return a[0] if a else None
        cd = dt.date.fromisoformat(dstr(m["close"]))
        sid = {"claims": "ICSA", "u3": "UNRATE", "payrolls": "PAYEMS"}[kind]
        va = self._vint(sid, (cd + dt.timedelta(days=1)).isoformat())
        vb = self._vint(sid, (cd - dt.timedelta(days=1)).isoformat())
        if not va or not vb:
            return None
        if kind == "claims":
            new = [v for d, v in va if d > vb[-1][0]]
            return new[0] if new else None
        ym = ev_month(m["e"])
        if kind == "u3":
            x = [v for d, v in va if d[:7] == ym]
            return x[0] if x else None
        x = [i for i, (d, v) in enumerate(va) if d[:7] == ym]
        return (va[x[0]][1] - va[x[0] - 1][1]) * 1000 if x and x[0] > 0 else None


def quote(cs, t):
    """(yes_bid, yes_ask) from the last hourly candle ending at or before t, at most 12 hours stale."""
    best = None
    for row in cs or []:
        if t - 12 * 3600 <= row[0] <= t and row[2] is not None:
            best = row
    if not best:
        return None
    bid = best[1] or 0.0
    ask = best[2]
    if not (0 < ask < 1) or bid >= ask:
        return None
    return bid, ask


def build_points(models, placebo=False):
    """One row per (market, hours before the close): model chance, market quotes, result."""
    mk, cd = load("markets") or {}, load("candles2") or {}
    pts, checks = [], defaultdict(lambda: [0, 0, 0])   # kind -> [events ok, events mismatched, no actual]
    for s, ms in mk.items():
        kind, step = SERIES[s]
        by_ev = defaultdict(list)
        for m in ms:
            if m["close"] < HOLDOUT_TS:
                by_ev[m["e"]].append(m)
        evs = sorted(by_ev, key=lambda e: by_ev[e][0]["close"])
        good = []
        for e in evs:
            a = models.actual(kind, by_ev[e][0])
            if a is None:
                checks[s][2] += 1
                continue
            ok = all(sat(rnd(a, step), m) == (m["res"] == "yes") for m in by_ev[e] if sat(rnd(a, step), m) is not None)
            checks[s][0 if ok else 1] += 1
            if ok:
                good.append(e)
        # placebo: give each event the forecast of an event half the list away (a wrong month)
        shift = {e: good[(i + len(good) // 2) % len(good)] for i, e in enumerate(good)} if placebo and good else {}
        for e in good:
            for m in by_ev[e]:
                for h in HOURS:
                    t = m["close"] - h * 3600
                    src = by_ev[shift[e]][0] if placebo else m
                    f = models.forecast(kind, dict(m, e=src["e"], close=src["close"]) if placebo else m,
                                        src["close"] - h * 3600 if placebo else t)
                    q = quote(cd.get(m["t"]), t)
                    if not f or not q:
                        continue
                    p = prob(f[0], f[1], step, m)
                    if p is None:
                        continue
                    pts.append({"s": s, "kind": kind, "e": e, "t": m["t"], "close": m["close"], "h": h, "p": p,
                                "mu": f[0], "sd": f[1], "bid": q[0], "ask": q[1], "y": 1 if m["res"] == "yes" else 0})
    return pts, checks


def bets(pts, thr, slip=0.0, band=(0.0, 1.0)):
    out = []
    for r in pts:
        cy = r["ask"] + slip
        cn = 1 - r["bid"] + slip
        ey = r["p"] - cy - kfee(r["ask"]) if cy < 1 else -1
        en = (1 - r["p"]) - cn - kfee(1 - r["bid"]) if r["bid"] > 0 and cn < 1 else -1
        side, cost = (1, cy + kfee(r["ask"])) if ey >= en else (0, cn + kfee(1 - r["bid"]))
        if max(ey, en) < thr or not (band[0] <= cost <= band[1]):
            continue
        won = r["y"] == side
        # the twin: same market, same moment, the side picked by a coin (its expected result)
        cy_all, cn_all = cy + kfee(r["ask"]), cn + kfee(1 - r["bid"])
        twin_pnl = 0.5 * ((r["y"] - cy_all) + ((1 - r["y"]) - cn_all)) if r["bid"] > 0 else (r["y"] - cy_all)
        twin_cost = 0.5 * (cy_all + cn_all) if r["bid"] > 0 else cy_all
        out.append(dict(r, side=side, cost=cost, pnl=(1.0 if won else 0.0) - cost, won=won, twin_pnl=twin_pnl,
                        twin_cost=twin_cost))
    return out


def per100(bs, key="pnl", ckey="cost"):
    c = sum(b[ckey] for b in bs)
    return 100 * sum(b[key] for b in bs) / c if c else 0.0


def band90(bs, n=1000):
    evs = defaultdict(list)
    for b in bs:
        evs[b["e"]].append(b)
    keys = list(evs)
    if len(keys) < 5:
        return None
    rng = random.Random(7)
    vals = []
    for _ in range(n):
        pick = [b for k in (rng.choice(keys) for _ in keys) for b in evs[k]]
        vals.append(per100(pick))
    vals.sort()
    return vals[int(0.05 * n)], vals[int(0.95 * n)]


def brier(pts):
    if not pts:
        return None
    bm = sum((r["p"] - r["y"]) ** 2 for r in pts) / len(pts)
    bk = sum(((r["bid"] + r["ask"]) / 2 - r["y"]) ** 2 for r in pts) / len(pts)
    return bm, bk


def money(x):
    return ("+" if x >= 0 else "-") + f"${abs(x):.2f}"


def line(bs):
    if not bs:
        return "no bets"
    b = band90(bs)
    evs = len({x["e"] for x in bs})
    w = sum(1 for x in bs if x["won"])
    return (f"{len(bs)} bets on {evs} releases, won {w}, staked ${sum(x['cost'] for x in bs):.2f}, "
            f"P&L {money(sum(x['pnl'] for x in bs))} = {money(per100(bs))} per $100"
            + (f" (luck range {money(b[0])} to {money(b[1])})" if b else "")
            + f"; coin-flip side on the same markets {money(per100(bs, 'twin_pnl', 'twin_cost'))} per $100")


def halves(bs):
    if not bs:
        return ""
    evs = sorted({(x["close"], x["e"]) for x in bs})
    if len(evs) < 4:
        return ""
    cut = evs[len(evs) // 2][0]
    a = [x for x in bs if x["close"] < cut]
    b = [x for x in bs if x["close"] >= cut]
    return f"first half {money(per100(a))} per $100 ({len(a)} bets), second half {money(per100(b))} ({len(b)} bets)"


def run():
    models = Models()
    pts, checks = build_points(models)
    placebo, _ = build_points(models, placebo=True)
    L = ["# Economic data markets vs free forecasts (econ.py)", "",
         f"Written by `python3 econ.py run` on {dt.date.today().isoformat()}. Kalshi markets that closed before 2026-11-10 "
         "(the holdout date in PROTOCOL.md). Every strike of every event is used, whatever its volume, so the "
         "bt_cache volume hole doesn't apply here.", "",
         "Forecasts: Cleveland Fed inflation nowcast (CPI, core CPI, CPI year-on-year), Atlanta Fed GDPNow (GDP), "
         "and plain 'same as last time' models from FRED's as-first-published numbers for jobless claims, "
         "unemployment and payrolls (these are the dumb control: we expect them to lose). The forecast is always "
         "the one published on an EARLIER day than the bet. Its spread comes from its own past misses, using only "
         "releases before the bet.", "",
         "Bets: buy YES at the ask or NO at 1 minus the bid, from Kalshi's hourly quotes (at most 12 hours old), "
         f"plus Kalshi's taker fee for a {CONTRACTS}-contract order, held to the result. A bet is made when the forecast says the side is "
         "worth at least the threshold more than it costs. 'Coin-flip side' = same markets, same moment, random side: "
         "what costs alone do. 'Wrong month' = each release gets another release's forecast: a real edge must vanish there.", "",
         "## Data checks", ""]
    for s, (ok, bad, na) in sorted(checks.items()):
        L.append(f"- {s}: {ok} releases where our number reproduces every Kalshi result, {bad} that don't (dropped), "
                 f"{na} without a number")
    L += ["", "## Who guesses better? (lower is better, all quoted strikes)", "",
          "| Series | Hours before | Strikes | Forecast score | Market score |", "|---|---|---|---|---|"]
    for s in SERIES:
        for h in HOURS:
            sub = [r for r in pts if r["s"] == s and r["h"] == h]
            b = brier(sub)
            if b:
                L.append(f"| {s} | {h} | {len(sub)} | {b[0]:.4f} | {b[1]:.4f} |")
    L += ["", "## Betting the forecast", ""]
    summary = {}
    for h in HOURS:
        for thr in THRESH:
            for slip in (0.0, 0.01):
                bs = bets([r for r in pts if r["h"] == h], thr, slip)
                summary[(h, thr, slip)] = bs
    for h in HOURS:
        L.append(f"### {h} hour{'s' if h > 1 else ''} before the release")
        L.append("")
        for thr in THRESH:
            bs = summary[(h, thr, 0.0)]
            L.append(f"- forecast beats price by {int(thr * 100)}c+: {line(bs)}")
            if bs:
                L.append(f"  - {halves(bs)}; with 1c worse prices {money(per100(summary[(h, thr, 0.01)]))} per $100")
                pl = bets([r for r in placebo if r["h"] == h], thr)
                L.append(f"  - wrong-month forecast: {line(pl)}")
        L.append("")
    L += ["## By series (24 hours before, 3c+ threshold)", ""]
    for s in SERIES:
        bs = [b for b in summary[(24, 0.03, 0.0)] if b["s"] == s]
        L.append(f"- {s}: {line(bs)}")
        if bs:
            L.append(f"  - {halves(bs)}")
    L += ["", "## By series (1 hour before, 3c+ threshold)", ""]
    for s in SERIES:
        bs = [b for b in summary[(1, 0.03, 0.0)] if b["s"] == s]
        L.append(f"- {s}: {line(bs)}")
        if bs:
            L.append(f"  - {halves(bs)}")
    L += ["", "## By price paid (24 hours before, 3c+ threshold)", ""]
    for lo, hi in ((0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.01)):
        bs = [b for b in summary[(24, 0.03, 0.0)] if lo <= b["cost"] < hi]
        L.append(f"- paid {int(lo * 100)}-{min(100, int(hi * 100))}c: {line(bs)}")
    txt = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "econ.md"), "w") as f:
        f.write(txt)
    print(txt)
    # a few raw rows to eyeball
    print("\n== sample rows")
    rng = random.Random(1)
    for r in rng.sample(pts, min(25, len(pts))):
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


def fetch_run():
    fetch()
    run()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"scan": scan, "scan2": scan2, "fetch": fetch, "run": run, "all": fetch_run}[cmd]()
