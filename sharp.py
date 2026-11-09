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


PIN = "https://guest.api.arcadia.pinnacle.com/0.1"


def pin(path, params=None):
    return bot.http_json(f"{PIN}{path}", params)


def probe2():
    print("== polymarket sport codes")
    sp = bot.http_json(f"{G}/sports")
    print(" ".join(f"{s.get('sport')}:{s.get('series')}" for s in sp))
    want = {s.get("sport"): s.get("series") for s in sp}
    for code in ("epl", "nba", "nfl", "nhl", "atp"):
        ser = want.get(code)
        if not ser:
            continue
        for closed in ("true", "false"):
            try:
                evs = bot.http_json(f"{G}/events", {"series_id": ser, "closed": closed, "limit": 3, "order": "startDate",
                                                    "ascending": "false"})
            except Exception as e:
                print(code, "events failed", e)
                continue
            for ev in evs[:2]:
                print(f"\n  {code} EVENT {ev.get('slug')} | {ev.get('title')} | startTime {ev.get('startTime')} "
                      f"| gameId {ev.get('gameId')} | eventMetadata {ev.get('eventMetadata')}")
                for m in (ev.get("markets") or [])[:5]:
                    print("    ", {k: m.get(k) for k in ("question", "sportsMarketType", "gameStartTime", "outcomes",
                                                        "outcomePrices", "feeSchedule", "volumeNum", "bestAsk",
                                                        "bestBid", "line", "groupItemTitle", "umaResolutionStatus")})
    print("\n== pinnacle guest api")
    for path in ("/leagues/1980/matchups", "/leagues/1980/markets/straight", "/sports/29/markets/straight?primaryOnly=true",
                 "/leagues/487/matchups"):
        st, body = raw(PIN + path)
        print(path, "HTTP", st, len(body), "bytes")
        try:
            js = json.loads(body)
        except Exception:
            print("  ", body[:300])
            continue
        rows = js if isinstance(js, list) else [js]
        print("   rows", len(rows))
        for r in rows[:3]:
            print("   ", json.dumps(r)[:900])


def probe3():
    """Raw shapes needed for matching: Pinnacle matchups + moneyline prices; Polymarket game events in the next 2 days."""
    for sid in (29, 4):
        mus = pin(f"/sports/{sid}/matchups")
        mks = pin(f"/sports/{sid}/markets/straight", {"primaryOnly": "true"})
        print(f"\n== pinnacle sport {sid}: {len(mus)} matchups, {len(mks)} markets; types",
              sorted({(m.get('type'), m.get('key')) for m in mks})[:12])
        reg = [m for m in mus if m.get("type") == "matchup" and not m.get("isLive")][:2]
        for m in reg:
            print("  MATCHUP", json.dumps({k: m.get(k) for k in ("id", "type", "startTime", "isLive", "parentId", "units",
                                                               "participants", "status")})[:700],
                  "| league", (m.get("league") or {}).get("name"))
            for mk in mks:
                if mk.get("matchupId") == m.get("id") and mk.get("type") == "moneyline":
                    print("    ML", json.dumps(mk)[:500])
    now = bot.now()
    import datetime as dt
    evs = bot.gamma_events({"tag_id": 100639, "closed": "false", "end_date_min": bot.iso(now),
                            "end_date_max": bot.iso(now + dt.timedelta(days=2))}, max_pages=3)
    print(f"\n== polymarket game events ending within 2 days: {len(evs)}")
    soc = [e for e in evs if any("win on" in str(m.get("question", "")) for m in e.get("markets") or [])][:2]
    for e in evs[:2] + soc:
        print(f"  EVENT {e.get('slug')} | {e.get('title')} | startTime {e.get('startTime')} | series "
              f"{[s.get('slug') for s in e.get('series') or []]} | tags {[t.get('slug') for t in e.get('tags') or []][:6]}")
        for m in (e.get("markets") or []):
            if m.get("sportsMarketType") == "moneyline":
                print("    ", {k: m.get(k) for k in ("question", "outcomes", "outcomePrices", "bestAsk", "bestBid",
                                                    "gameStartTime", "groupItemTitle", "liquidityNum", "feeSchedule")})


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "probe"
    {"probe": probe, "probe2": probe2, "probe3": probe3}[what]()
