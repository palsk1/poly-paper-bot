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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"scan": scan, "scan2": scan2}[cmd]()
