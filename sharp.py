#!/usr/bin/env python3
"""Sharp-bookmaker research: is a Polymarket sports price cheaper than Pinnacle's fair price (its odds minus its margin)?

PAPER ONLY. Reads public data, never trades.

    python3 sharp.py probe   # which odds sources answer from GitHub Actions, and what Polymarket soccer games look like
"""
import csv
import io
import json
import sys
import urllib.error
import urllib.request

import bot

G = bot.GAMMA

SOURCES = {
    "football-data (free CSV, Pinnacle closing odds)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "football-data last season": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "the-odds-api (no key: expect 401)": "https://api.the-odds-api.com/v4/sports/soccer_epl/odds?regions=eu&bookmakers=pinnacle",
    "oddspapi (no key: expect 401)": "https://api.oddspapi.io/v4/sports",
    "pinnacle guest site api": "https://guest.api.arcadia.pinnacle.com/0.1/sports/29/leagues?all=false",
    "pinnodds": "https://pinnodds.com/",
}


def raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode()


def probe():
    print("== odds sources")
    for name, url in SOURCES.items():
        st, body = raw(url)
        print(f"{name}: HTTP {st}, {len(body)} bytes")
        if url.endswith(".csv") and st == 200:
            rows = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig", "replace"))))
            cols = list(rows[0].keys()) if rows else []
            print("  columns:", ",".join(cols))
            for r in rows[-3:]:
                print("  ", {k: r.get(k) for k in ("Date", "Time", "HomeTeam", "AwayTeam", "FTR", "PSH", "PSD", "PSA",
                                                   "PSCH", "PSCD", "PSCA", "AvgCH", "MaxCH", "B365CH")})
        else:
            print("  ", body[:200])
    print("\n== polymarket sports list")
    try:
        sp = bot.http_json(f"{G}/sports")
        for s in sp[:80] if isinstance(sp, list) else []:
            print("  ", {k: s.get(k) for k in ("sport", "series", "tags", "resolution")})
    except Exception as e:
        print("  /sports failed:", e)
    print("\n== a few EPL game events (closed and open)")
    for closed in ("true", "false"):
        try:
            evs = bot.http_json(f"{G}/events", {"tag_slug": "epl", "closed": closed, "limit": 5, "order": "endDate",
                                                "ascending": "false"})
        except Exception as e:
            print("  events failed:", e)
            continue
        for ev in evs[:3]:
            print(f"\n  EVENT {ev.get('slug')} | {ev.get('title')} | start {ev.get('startTime')} end {ev.get('endDate')}"
                  f" | gameId {ev.get('gameId')} | keys {sorted(ev.keys())[:60]}")
            for m in (ev.get("markets") or [])[:4]:
                print("    ", {k: m.get(k) for k in ("question", "slug", "sportsMarketType", "gameStartTime", "outcomes",
                                                    "outcomePrices", "feesEnabled", "feeSchedule", "volumeNum",
                                                    "bestAsk", "bestBid", "closed", "groupItemTitle")})


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "probe"
    {"probe": probe}[what]()
