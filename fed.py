#!/usr/bin/env python3
"""Fed rate decision and CPI bets (Kalshi + Polymarket) vs what futures / options markets imply.
backtest/fed.md. PAPER ONLY: reads public data, never trades, never writes state/.

  python3 fed.py src      (probe fed_src: which free futures / options histories Actions can read, and the markets)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

import bot

K, G = bot.KALSHI, bot.GAMMA
UTC = dt.timezone.utc
BUA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CACHE = os.path.join(bot.ROOT, "bt_cache", "fed")


def raw(url, ua=BUA, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        try:
            body = e.read()[:300]
        except Exception:
            body = b""
        return e.code, body, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode(), None


YH = "https://query{}.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d"


def src():
    now = int(dt.datetime.now(UTC).timestamp())
    tries = {}
    for sym in ("ZQ=F", "ZQZ26.CBT", "ZQF27.CBT", "ZQZ25.CBT", "ZQU25.CBT", "ZQH24.CBT", "SR3=F", "SR3Z26.CME"):
        tries[f"yahoo {sym}"] = YH.format(1, sym, now - 3 * 365 * 86400, now)
    tries.update({
        "yahoo2 ZQZ25.CBT": YH.format(2, "ZQZ25.CBT", now - 3 * 365 * 86400, now),
        "stooq zq.f": "https://stooq.com/q/d/l/?s=zq.f&i=d",
        "stooq zqz25.f": "https://stooq.com/q/d/l/?s=zqz25.f&i=d",
        "atlanta MPT xlsx": "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/market-probability-tracker/mpt_histdata.xlsx",
        "fred DFF": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF",
        "fred DTB4WK": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB4WK",
        "fred DGS1MO": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS1MO",
        "fred SOFR": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR",
        "fred T5YIE": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T5YIE",
        "treasury bills daily": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?type=daily_treasury_bill_rates&field_tdr_date_value=2025&page&_format=csv",
        "cme fedwatch page": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
        "cme zq quotes": "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G",
        "rateprobability latest": "https://rateprobability.com/api/latest",
        "investing zq": "https://www.investing.com/rates-bonds/30-day-fed-fund-futures-historical-data",
        "barchart zq": "https://www.barchart.com/futures/quotes/ZQZ25/price-history/historical",
        "nyfed sofr api": "https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json",
    })
    for name, url in tries.items():
        code, body, ct = raw(url)
        head = body[:260].decode("utf-8", "replace").replace("\n", " | ")
        extra = ""
        if name.startswith("yahoo") and code == 200:
            try:
                j = json.loads(body)
                r = j["chart"]["result"][0]
                ts = r.get("timestamp") or []
                cl = r["indicators"]["quote"][0].get("close") or []
                extra = f" ROWS {len(ts)} first {dt.datetime.utcfromtimestamp(ts[0]).date() if ts else '-'} last " \
                        f"{dt.datetime.utcfromtimestamp(ts[-1]).date() if ts else '-'} close[-3:] {cl[-3:]}"
            except Exception as e:
                extra = f" parse {e}"
        print(f"== {name}: HTTP {code} {ct} {len(body)} bytes{extra}\n   {head[:260]}", flush=True)
    # Kalshi: every series about the Fed, rates or inflation
    try:
        ser = bot.http_json(f"{K}/series", {}).get("series") or []
        words = ("fed", "fomc", "rate", "cpi", "inflation", "pce", "powell", "cut", "hike")
        hit = [s for s in ser if any(w in (str(s.get("title")) + " " + str(s.get("ticker"))).lower() for w in words)]
        print(f"\nKalshi series {len(ser)}, matching {len(hit)}")
        for s in hit:
            print("KS", s.get("ticker"), "|", s.get("category"), "|", s.get("frequency"), "|", str(s.get("title"))[:90])
    except Exception as e:
        print("kalshi series failed", e)
    for t in ("KXFED", "KXFEDDECISION", "FED", "FEDDECISION", "KXRATECUT", "KXCPI"):
        try:
            r = bot.http_json(f"{K}/markets", {"series_ticker": t, "limit": 5, "status": "settled"})
            ms = r.get("markets") or []
            print("\nKM", t, len(ms))
            for m in ms[:5]:
                print("   ", m.get("ticker"), "|", str(m.get("title"))[:80], "|", m.get("yes_sub_title"), "|",
                      m.get("result"), "| vol", m.get("volume_fp") or m.get("volume"), "| close", m.get("close_time"))
            r = bot.http_json(f"{K}/historical/markets", {"series_ticker": t, "limit": 3})
            for m in (r.get("markets") or [])[:3]:
                print("   hist", m.get("ticker"), "|", str(m.get("title"))[:80], "|", m.get("result"), "|", m.get("close_time"))
        except Exception as e:
            print("KM", t, "failed", str(e)[:120])
    # Polymarket: Fed and CPI events
    for slug in ("fed-rates", "fed", "economic-policy", "inflation", "cpi", "economy"):
        try:
            tg = bot.http_json(f"{G}/tags/slug/{slug}")
            tid = tg.get("id")
            r = bot.http_json(f"{G}/events", {"tag_id": tid, "closed": "true", "limit": 100, "order": "volume",
                                              "ascending": "false"})
            ev = bot.envelope_rows(r, "events", "data")
            print(f"\nPM tag {slug} id {tid}: {len(ev)} closed events (top by volume)")
            for e in ev[:25]:
                print("   ", e.get("slug"), "| $", int(float(e.get("volume") or 0)), "| end", str(e.get("endDate"))[:10],
                      "| mk", len(e.get("markets") or []))
        except Exception as e:
            print("PM tag", slug, "failed", str(e)[:120])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "src"
    {"src": src}[cmd]()
