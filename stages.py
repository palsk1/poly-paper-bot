"""In-game "leader after a stage" bets in other sports (27 Nov 2026).

Tennis found one lead: on Kalshi, the winner of set 1 at 50-80c is a little too cheap for the next 10-15 minutes
(tennis.py, backtest/tennis.md). This tool asks the same question for basketball (after a quarter / the half),
hockey (after a period), baseball (after an inning) and esports (after a map), on Kalshi and Polymarket.

Commands (probe `stg_<cmd>`):
  scan      every Kalshi sports series that looks like a game winner or a stage winner, with size; free clocks test
  fetch ... (later) settled games + 1-minute bid / ask + stage times -> bt_cache/stg/ (shared price store)
"""
import collections
import gzip
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import bot
import yesno

CACHE = os.path.join("bt_cache", "stg")
DAY = 86400
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
T0 = time.time()


def raw(url, timeout=25, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json,text/html,*/*"}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def short(x, n=400):
    s = x if isinstance(x, str) else json.dumps(x, separators=(",", ":"), default=str)
    return s[:n]


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def its(s):
    d = bot.parse_iso(s) if s else None
    return int(d.timestamp()) if d else None


# ---------------------------------------------------------------- scan
WANT = re.compile(r"NBA|WNBA|NHL|MLB|NFL|NCAA|COLLEGE|BASKET|HOCKEY|BASEBALL|FOOTBALL|EUROLEAGUE|KHL|SHL|NPB|KBO|"
                  r"LOL|LEAGUE OF LEGENDS|CS2|CSGO|COUNTER|VALORANT|DOTA|ESPORT|OVERWATCH|RAINBOW|R6|ROCKET|CALL OF DUTY|"
                  r"QUARTER|HALF|PERIOD|INNING|MAP|GAME \d|SET", re.I)
STAGE = re.compile(r"quarter|half|period|inning|map|1h|2h|q1|q2|q3|q4|first five|f5|game \d|set\b|round", re.I)


def recent_settled(series, days=21):
    t1 = int(time.time())
    rows, cur = [], None
    for _ in range(30):
        p = {"series_ticker": series, "status": "settled", "min_close_ts": t1 - days * DAY, "limit": 1000}
        if cur:
            p["cursor"] = cur
        try:
            r = yesno.kget("/markets", p)
        except Exception as e:
            return series, rows, str(e)[:80]
        got = r.get("markets") or []
        rows += [m for m in got if str(m.get("event_ticker", "")).startswith(series)]
        cur = r.get("cursor")
        if not cur or not got:
            break
    return series, rows, ""


def scan_kalshi():
    ser = yesno.kget("/series", {"category": "Sports"}).get("series") or []
    if not ser:
        ser = [s for s in yesno.kget("/series", {}).get("series") or [] if s.get("category") == "Sports"]
    print(f"Kalshi sports series: {len(ser)}", flush=True)
    pick = {s["ticker"]: s for s in ser if s.get("ticker") and (WANT.search(str(s.get("title"))) or WANT.search(s["ticker"]))}
    print(f"look like our sports: {len(pick)}", flush=True)
    out = {}
    with ThreadPoolExecutor(8) as ex:
        for s, rows, err in ex.map(recent_settled, sorted(pick)):
            if not rows:
                continue
            evs = {m["event_ticker"] for m in rows}
            vol = sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in rows)
            top = max(rows, key=lambda m: bot.fnum(m.get("volume_fp") or m.get("volume"), 0))
            out[s] = {"title": str(pick[s].get("title"))[:70], "n": len(rows), "ev": len(evs), "vol": vol,
                      "stage": bool(STAGE.search(str(pick[s].get("title"))) or STAGE.search(s)),
                      "ex": [str(top.get("title"))[:90], str(top.get("yes_sub_title"))[:40], top.get("open_time"), top.get("close_time"),
                             top.get("expected_expiration_time"), int(bot.fnum(top.get("volume_fp") or top.get("volume"), 0))]}
    os.makedirs(CACHE, exist_ok=True)
    wj(os.path.join(CACHE, "kscan.json.gz"), out)
    print("\n| series | title | stage? | markets 21d | events | contracts 21d | biggest market (title / yes / open / close / exp / contracts) |")
    print("|---|---|---|---|---|---|---|")
    for s, d in sorted(out.items(), key=lambda kv: -kv[1]["vol"]):
        if d["vol"] < 20000:
            continue
        print(f"| {s} | {d['title']} | {'yes' if d['stage'] else ''} | {d['n']} | {d['ev']} | {int(d['vol']):,} | {' / '.join(str(x) for x in d['ex'])} |")
    print(f"\n(+ {sum(1 for d in out.values() if d['vol'] < 20000)} smaller series left out)")


def try_url(name, url, n=700, headers=None):
    try:
        s = raw(url, headers=headers)
        print(f"  OK  {name}: {len(s)} bytes | {short(s, n)}", flush=True)
        return s
    except Exception as e:
        print(f"  BAD {name}: {str(e)[:150]}", flush=True)
        return None


def scan_clocks():
    """Free sources that tell when a quarter / period / inning / map ended, in wall-clock time."""
    print("\n=== free stage clocks ===", flush=True)
    s = try_url("MLB schedule", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-09-20", 300)
    pk = None
    if s:
        try:
            pk = json.loads(s)["dates"][0]["games"][0]["gamePk"]
        except Exception:
            pass
    if pk:
        f = try_url("MLB live feed", f"https://statsapi.mlb.com/api/v1.1/game/{pk}/feed/live", 200)
        if f:
            j = json.loads(f)
            pl = j.get("liveData", {}).get("plays", {}).get("allPlays", [])
            print("    plays", len(pl), "first", short([p.get("about") for p in pl[:2]], 400))
    s = try_url("NBA schedule (cdn)", "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json", 200)
    gid = None
    if s:
        try:
            j = json.loads(s)
            for d in j["leagueSchedule"]["gameDates"]:
                for g in d["games"]:
                    if g.get("gameStatus") == 3:
                        gid = g["gameId"]
            print("    last finished game", gid)
        except Exception as e:
            print("    parse", e)
    if gid:
        f = try_url("NBA play-by-play (cdn)", f"https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{gid}.json", 200)
        if f:
            a = json.loads(f)["game"]["actions"]
            print("    actions", len(a), short([(x.get("period"), x.get("clock"), x.get("timeActual"), x.get("actionType")) for x in a if x.get("actionType") in ("period",)], 600))
    try_url("NBA older pbp (2025 playoffs)", "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0042400401.json", 200)
    try_url("NHL schedule", "https://api-web.nhle.com/v1/schedule/2026-11-20", 300)
    f = try_url("NHL play-by-play", "https://api-web.nhle.com/v1/gamecenter/2025020300/play-by-play", 300)
    if f:
        j = json.loads(f)
        pl = j.get("plays", [])
        print("    plays", len(pl), "period-end:", short([p for p in pl if p.get("typeDescKey") in ("period-end", "period-start")][:3], 600))
        print("    top keys", list(j.keys())[:40])
    for nm, u in (("ESPN site NBA summary", "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"),
                  ("ESPN core NHL", "https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/events?limit=2"),
                  ("ESPN cdn", "https://cdn.espn.com/core/nba/scoreboard?xhr=1"),
                  ("365 basketball", "https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=1&sports=2&startDate=20/11/2026&endDate=20/11/2026&showOdds=false&onlyMajorGames=true"),
                  ("365 hockey", "https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=1&sports=4&startDate=20/11/2026&endDate=20/11/2026&showOdds=false&onlyMajorGames=true"),
                  ("bo3.gg CS2 matches", "https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=2&sort=-start_date&filter[matches.status][in]=finished&with=games"),
                  ("lolesports livestats window (no key)", "https://feed.lolesports.com/livestats/v1/window/113475798006748990"),
                  ("Kalshi live_data milestones nba", "https://api.elections.kalshi.com/trade-api/v2/milestones?limit=3&category=Sports&minimum_start_date=2026-11-20T00:00:00Z")):
        s = try_url(nm, u, 900)
        if s and "365" in nm:
            try:
                g = json.loads(s)["games"][0]
                print("    365 game keys", list(g.keys())[:50])
                print("    stages", short(g.get("stages"), 600))
            except Exception as e:
                print("    365 parse", e)


# ---------------------------------------------------------------- peek: what the stage markets look like
PEEK = ("KXNBA1Q", "KXNBA1H", "KXNBA3Q", "KXNBAGAME", "KXNFL1Q", "KXNFL1H", "KXNFLGAME", "KXNCAAF1H", "KXNCAAMB1H", "KXNCAAMBGAME",
        "KXNHL1P", "KXNHL2P", "KXNHLGAME", "KXCS2MAP", "KXCS2GAME", "KXLOLMAP", "KXLOLGAME", "KXDOTA2MAP", "KXDOTA2GAME",
        "KXVALORANTMAP", "KXVALORANTGAME", "KXCODMAP", "KXMLBGAME", "KXMLBF5", "KXMLB1I", "KXWNBAGAME", "KXUEFANL1H")


def first_close(series):
    """Oldest settled market of a series (historical list first)."""
    for path in ("/historical/markets", "/markets"):
        try:
            p = {"series_ticker": series, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            r = yesno.kget(path, p)
            got = [m for m in r.get("markets") or [] if str(m.get("event_ticker", "")).startswith(series)]
            if got:
                return min(got, key=lambda m: m.get("close_time") or "z").get("close_time"), path, len(got), bool(r.get("cursor"))
        except Exception as e:
            print("   ", series, path, str(e)[:80])
    return None, None, 0, False


def peek():
    for s in PEEK:
        _, rows, err = recent_settled(s, 10)
        fc = first_close(s)
        print(f"\n== {s}: {len(rows)} settled in 10 days {err} | oldest seen {fc}", flush=True)
        for m in rows[:4]:
            print("  ", m.get("ticker"), "|", m.get("event_ticker"), "|", str(m.get("title"))[:70], "|", str(m.get("yes_sub_title"))[:30],
                  "| open", m.get("open_time"), "| close", m.get("close_time"), "| exp", m.get("expected_expiration_time"), "| res", m.get("result"),
                  "| vol", m.get("volume_fp") or m.get("volume"))
        if rows:
            print("   rules:", str(rows[0].get("rules_primary"))[:300])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan_kalshi()
        scan_clocks()
    elif cmd == "peek":
        peek()
    elif cmd == "clocks":
        scan_clocks()
    else:
        print(__doc__)
