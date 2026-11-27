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


# ---------------------------------------------------------------- fetch: games, stage clocks, 1-minute prices
import tennis   # k_minutes (1-minute bid / ask, live + /historical), kfee, quote_at, per100

ESPN = "https://site.api.espn.com/apis/site/v2/sports/"
SPORTS = {   # sport: (ESPN path, extra scoreboard params, Kalshi game series, Kalshi stage series used as a second clock)
    "nba": ("basketball/nba", "", "KXNBAGAME", ("KXNBA1Q", "KXNBA1H", "KXNBA3Q")),
    "wnba": ("basketball/wnba", "", "KXWNBAGAME", ()),
    "ncaamb": ("basketball/mens-college-basketball", "&groups=50", "KXNCAAMBGAME", ("KXNCAAMB1H",)),
    "ncaawb": ("basketball/womens-college-basketball", "&groups=50", "KXNCAAWBGAME", ()),
    "nfl": ("football/nfl", "", "KXNFLGAME", ("KXNFL1Q", "KXNFL1H", "KXNFL3Q")),
    "ncaaf": ("football/college-football", "&groups=80", "KXNCAAFGAME", ("KXNCAAF1Q", "KXNCAAF1H")),
    "nhl": ("hockey/nhl", "", "KXNHLGAME", ("KXNHL1P", "KXNHL2P")),
    "mlb": ("baseball/mlb", "", "KXMLBGAME", ()),
}
ESPORTS = {  # game: (Kalshi match series, Kalshi map series = the clock)
    "cs2": ("KXCS2GAME", "KXCS2MAP"), "lol": ("KXLOLGAME", "KXLOLMAP"), "dota2": ("KXDOTA2GAME", "KXDOTA2MAP"),
    "valorant": ("KXVALORANTGAME", "KXVALORANTMAP"), "cod": ("KXCODGAME", "KXCODMAP"),
}


def ejson(url):
    for i in range(4):
        try:
            return json.loads(raw(url, timeout=30))
        except Exception as e:
            if "404" in str(e) or i == 3:
                raise
            time.sleep(2 + 3 * i)


def espn_day(sport, d0):
    path, extra, _, _ = SPORTS[sport]
    d = time.strftime("%Y%m%d", time.gmtime(d0))
    j = ejson(f"{ESPN}{path}/scoreboard?dates={d}&limit=900{extra}")
    out = []
    for e in j.get("events") or []:
        c = (e.get("competitions") or [{}])[0]
        if not ((c.get("status") or e.get("status") or {}).get("type") or {}).get("completed"):
            continue
        teams = {}
        for x in c.get("competitors") or []:
            t = x.get("team") or {}
            teams[x.get("homeAway")] = {"ab": t.get("abbreviation"), "name": t.get("displayName"), "loc": t.get("location"),
                                        "short": t.get("shortDisplayName"), "nick": t.get("name"), "score": bot.fnum(x.get("score"), None)}
        if "home" in teams and "away" in teams:
            out.append({"id": e["id"], "date": e.get("date"), "home": teams["home"], "away": teams["away"]})
    return out


def _plays(j):
    """Every play dict with a wall-clock time, from 'plays' or from NFL-style 'drives'."""
    out = list(j.get("plays") or [])
    dr = j.get("drives") or {}
    for d in (dr.get("previous") or []) + ([dr["current"]] if isinstance(dr.get("current"), dict) else []):
        out += d.get("plays") or []
    return out


def espn_game(sport, gid):
    """Stage ends of one finished game: [[period, end unix (last play of the period), away score, home score]], first play time."""
    j = ejson(f"{ESPN}{SPORTS[sport][0]}/summary?event={gid}")
    per = {}
    first = None
    for p in _plays(j):
        w = its(p.get("wallclock"))
        n = ((p.get("period") or {}).get("number"))
        if not w or not n:
            continue
        first = w if first is None else min(first, w)
        a, h = bot.fnum(p.get("awayScore"), None), bot.fnum(p.get("homeScore"), None)
        cur = per.get(n)
        if cur is None or w >= cur[0]:
            per[n] = [w, a if a is not None else (cur[1] if cur else None), h if h is not None else (cur[2] if cur else None)]
    ends = [[n, v[0], v[1], v[2]] for n, v in sorted(per.items())]
    return {"first": first, "ends": ends, "n": len(_plays(j))}


def espn_fetch(sport, days):
    d_dir = os.path.join(CACHE, sport)
    gpath = os.path.join(d_dir, "espn_games.json.gz")
    games = rj(gpath, {}) or {}
    dpath = os.path.join(d_dir, "espn_days.json.gz")
    done_days = set(rj(dpath, []) or [])
    today = int(time.time()) // DAY * DAY
    todo = [d0 for d0 in range(today - days * DAY, today - DAY, DAY) if d0 not in done_days]
    print(f"{sport}: ESPN days to read {len(todo)}, games known {len(games)}", flush=True)

    def day(d0):
        try:
            return d0, espn_day(sport, d0), ""
        except Exception as e:
            return d0, None, str(e)[:80]
    with ThreadPoolExecutor(6) as ex:
        for d0, got, err in ex.map(day, todo):
            if got is None:
                print("  day failed", time.strftime("%Y-%m-%d", time.gmtime(d0)), err, flush=True)
                continue
            for g in got:
                games.setdefault(g["id"], g)
            done_days.add(d0)
    wj(dpath, sorted(done_days))
    need = [g for g in games.values() if "ends" not in g]
    print(f"{sport}: {len(games)} finished games, {len(need)} need play-by-play", flush=True)

    def one(g):
        try:
            return g, espn_game(sport, g["id"]), ""
        except Exception as e:
            return g, None, str(e)[:80]
    k = 0
    with ThreadPoolExecutor(8) as ex:
        for g, got, err in ex.map(one, need):
            k += 1
            if got:
                g.update(got)
            elif "404" in err:
                g["ends"] = []
            if k % 300 == 0:
                wj(gpath, games)
                print(f"  {k}/{len(need)} play-by-play ({(time.time() - T0) / 60:.0f} min)", flush=True)
            if time.time() - T0 > 200 * 60:
                break
    wj(gpath, games)
    ok = [g for g in games.values() if len(g.get("ends") or []) >= 2]
    print(f"{sport}: {len(ok)} games with stage end times", flush=True)
    return games


def k_events(series, days=400):
    """{event: [market rows]} of every settled market of a series that closed in the last `days` days (both lists)."""
    t1 = int(time.time())
    rows = []
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(200):
            p = {"series_ticker": series, "min_close_ts": t1 - days * DAY, "max_close_ts": t1, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = yesno.kget(path, p)
            except Exception as e:
                print(f"  {series} {path}: {str(e)[:90]}", flush=True)
                break
            got = r.get("markets") or []
            good = [m for m in got if str(m.get("event_ticker", "")).startswith(series)]
            rows += good
            cur = r.get("cursor")
            if not cur or not got or not good:
                break
    evs, seen = collections.defaultdict(list), set()
    for m in rows:
        tk, res = m.get("ticker"), str(m.get("result") or "")
        if tk in seen or res not in ("yes", "no"):
            continue
        seen.add(tk)
        evs[m["event_ticker"]].append({"t": tk, "ev": m["event_ticker"], "w": str(m.get("yes_sub_title") or "")[:60],
                                       "open": its(m.get("open_time")), "close": its(m.get("close_time")),
                                       "exp": its(m.get("expected_expiration_time")), "res": res,
                                       "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0)})
    print(f"  {series}: {len(seen)} settled markets, {len(evs)} events ({(time.time() - T0) / 60:.0f} min)", flush=True)
    return dict(evs)


def gkey(ev):
    return ev.split("-", 1)[1] if "-" in ev else ev


def norm_toks(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower().replace("&", " ")
    return {t for t in re.split(r"[^a-z0-9]+", s) if len(t) >= 2}


def team_ok(km_, et):
    """Kalshi market (its yes name + ticker suffix) is this ESPN team?"""
    ab = km_["t"].rsplit("-", 1)[-1].upper()
    if et.get("ab") and ab == str(et["ab"]).upper():
        return 3
    w = norm_toks(km_["w"])
    full = norm_toks(et.get("name")) | norm_toks(et.get("short")) | norm_toks(et.get("loc"))
    w = {t for t in w if len(t) > 1}
    if w and w <= full:
        return 2 if len(w) >= 2 or len(next(iter(w))) >= 4 else 1
    return 0


def match_espn(evs, games):
    """{kalshi event: (espn game id, yes side 'home'/'away' of the first market)}"""
    by_day = collections.defaultdict(list)
    for g in games.values():
        d = its(g.get("date"))
        if d and len(g.get("ends") or []) >= 2:
            by_day[(d - 5 * 3600) // DAY].append(g)          # US evening games: ESPN date is UTC, Kalshi's is local
    out = {}
    for ev, mm in evs.items():
        mm = sorted([m for m in mm if not m["t"].endswith("-TIE")], key=lambda m: m["t"])
        if len(mm) != 2:
            continue
        mm_close = mm[0]["close"]
        best = None
        for dd in (-1, 0, 1):
            for g in by_day.get((mm_close - 5 * 3600) // DAY + dd, []):
                if not (its(g["date"]) - 3600 <= mm_close <= its(g["date"]) + 9 * 3600):
                    continue
                for side, other in (("home", "away"), ("away", "home")):
                    a, b = team_ok(mm[0], g[side]), team_ok(mm[1], g[other])
                    if a and b and (best is None or a + b > best[0]):
                        best = (a + b, g["id"], side)
        if best:
            out[ev] = (best[1], best[2])
    return out


def min_fetch(sport, rows, tag):
    """rows: [(market ticker, series, t0, t1)] -> shards min_<tag>_<nnn>.json.gz of 1-minute [t, bid, ask, contracts, bid low, ask high]."""
    d_dir = os.path.join(CACHE, sport)
    rows = sorted(rows)
    n_sh = (len(rows) + 399) // 400
    for i in range(n_sh):
        tp = os.path.join(d_dir, f"min_{tag}_{i:03d}.json.gz")
        old = rj(tp, {}) or {}
        chunk = [r for r in rows[i * 400:(i + 1) * 400] if not old.get(r[0])]
        if not chunk:
            continue
        if time.time() - T0 > 260 * 60:
            print("  out of time, run again to continue", flush=True)
            return

        def one(r):
            return r[0], tennis.k_minutes(r[1], r[0], r[2], r[3])
        with ThreadPoolExecutor(8) as ex:
            for tk, m in ex.map(one, chunk):
                old[tk] = m
        wj(tp, old)
        print(f"  {sport} minutes file {i + 1}/{n_sh}: {sum(1 for v in old.values() if v)}/{len(old)} with prices ({(time.time() - T0) / 60:.0f} min)", flush=True)


def fetch_sport(sport, days=400):
    d_dir = os.path.join(CACHE, sport)
    games = espn_fetch(sport, days)
    _, _, gser, sser = SPORTS[sport]
    evs = k_events(gser, days)
    wj(os.path.join(d_dir, f"k_{gser}.json.gz"), evs)
    for s in sser:
        wj(os.path.join(d_dir, f"k_{s}.json.gz"), k_events(s, days))
    mt = match_espn(evs, games)
    wj(os.path.join(d_dir, "match.json.gz"), mt)
    print(f"{sport}: Kalshi games {len(evs)}, matched to ESPN {len(mt)}", flush=True)
    rows = []
    for ev, (gid, side) in mt.items():
        g = games[gid]
        mm = sorted([m for m in evs[ev] if not m["t"].endswith("-TIE")], key=lambda m: m["t"])
        a = (g.get("first") or its(g["date"])) - 20 * 60
        b = min(mm[0]["close"], g["ends"][-1][1] + 3600) + 60
        rows.append((mm[0]["t"], gser, a, b))
    min_fetch(sport, rows, gser)


def fetch_esport(game, days=400):
    d_dir = os.path.join(CACHE, game)
    gser, mser = ESPORTS[game]
    evs, maps = k_events(gser, days), k_events(mser, days)
    wj(os.path.join(d_dir, f"k_{gser}.json.gz"), evs)
    wj(os.path.join(d_dir, f"k_{mser}.json.gz"), maps)
    first_map = {}
    for ev, mm in maps.items():
        k = gkey(ev).rsplit("-", 1)[0]
        first_map[k] = min(first_map.get(k, 9e18), min(m["close"] for m in mm))
    rows = []
    for ev, mm in evs.items():
        k = gkey(ev)
        if k not in first_map or len(mm) != 2:
            continue
        m = sorted(mm, key=lambda m: m["t"])[0]
        rows.append((m["t"], gser, first_map[k] - 90 * 60, m["close"] + 60))
    print(f"{game}: matches with a map clock {len(rows)}", flush=True)
    min_fetch(game, rows, gser)


def fetch(what, days=400):
    for w in what.split(","):
        if w in SPORTS:
            fetch_sport(w, days)
        elif w in ESPORTS:
            fetch_esport(w, days)
        else:
            print("unknown", w)


# ---------------------------------------------------------------- report: buy the leader after a stage
STAGE_NAME = {"nba": "quarter", "wnba": "quarter", "nfl": "quarter", "ncaaf": "quarter", "ncaamb": "half", "ncaawb": "quarter",
              "nhl": "period", "mlb": "inning"}


def load_mins(sport, tag):
    d_dir = os.path.join(CACHE, sport)
    out, i = {}, 0
    while True:
        d = rj(os.path.join(d_dir, f"min_{tag}_{i:03d}.json.gz"))
        if d is None:
            break
        out.update(d)
        i += 1
    return out


def load_sport(sport):
    """-> list of games: {ev, yes (market row of the YES team), side ('home'/'away' = YES team), res (1 YES won),
    stages: [[n, end unix, yes score, other score]], mins}"""
    d_dir = os.path.join(CACHE, sport)
    gser = SPORTS[sport][2]
    games = rj(os.path.join(d_dir, "espn_games.json.gz"), {}) or {}
    evs = rj(os.path.join(d_dir, f"k_{gser}.json.gz"), {}) or {}
    mt = rj(os.path.join(d_dir, "match.json.gz"), {}) or {}
    mins = load_mins(sport, gser)
    out = []
    for ev, (gid, side) in mt.items():
        g = games.get(gid)
        mm = sorted([m for m in evs.get(ev, []) if not m["t"].endswith("-TIE")], key=lambda m: m["t"])
        if not g or len(mm) != 2 or not mins.get(mm[0]["t"]):
            continue
        st = []
        for n, t, a, h in g.get("ends") or []:
            if a is None or h is None:
                continue
            ys, os_ = (h, a) if side == "home" else (a, h)
            st.append([n, t, ys, os_])
        fin = g[side]["score"], g["away" if side == "home" else "home"]["score"]
        res = 1 if mm[0]["res"] == "yes" else 0
        if fin[0] is not None and fin[1] is not None and fin[0] != fin[1] and (fin[0] > fin[1]) != bool(res):
            continue          # ESPN final and Kalshi result disagree: drop (wrong match)
        out.append({"ev": ev, "yes": mm[0], "side": side, "res": res, "stages": st, "mins": mins[mm[0]["t"]], "close": mm[0]["close"]})
    return out


def buy(g, t, yes, stake=25.0, max_spread=8):
    q = tennis.quote_at(g["mins"], t, max_spread=max_spread)
    if not q or t >= g["close"] - 60:
        return None
    px = q[1] if yes else 1 - q[0]
    if not 0 < px < 1:
        return None
    n = int(stake / px)
    if n < 1:
        return None
    win = g["res"] == (1 if yes else 0)
    return {"ev": g["ev"], "t": t, "px": px, "cost": n * px + tennis.kfee(px, n), "pay": float(n) if win else 0.0, "win": win}


def stage_bets(gs, stage, lag, lo, hi, who="leader", min_lead=1, max_lead=999):
    out = []
    for g in gs:
        st = [x for x in g["stages"] if x[0] == stage]
        if not st or stage >= max(x[0] for x in g["stages"]):
            continue
        n, te, ys, os_ = st[0]
        lead = ys - os_
        if abs(lead) < min_lead or abs(lead) > max_lead:
            continue
        yes = lead > 0 if who == "leader" else lead < 0
        b = buy(g, te + lag * 60, yes)
        if b and lo <= b["px"] < hi:
            b["lead"] = abs(lead)
            out.append(b)
    out.sort(key=lambda b: b["t"])
    return out


def line(bets):
    h = len(bets) // 2
    w = sum(b["win"] for b in bets)
    ap = sum(b["px"] for b in bets) / len(bets) if bets else 0
    return (f"{len(bets)} bets, won {w} ({(w / len(bets) * 100 if bets else 0):.0f} in 100, avg price {ap * 100:.0f}c), "
            f"{tennis.per100(bets):+.2f} per $100 (halves {tennis.per100(bets[:h]):+.2f} / {tennis.per100(bets[h:]):+.2f})")


def report_sport(sport):
    gs = load_sport(sport)
    print(f"\n=== {sport}: {len(gs)} games with stage times, Kalshi minute prices and an agreeing result ===", flush=True)
    if not gs:
        return {}
    # clock check: how stale is the price at the stage end? spread there
    maxst = collections.Counter(max(x[0] for x in g["stages"]) for g in gs)
    print("  stages per game:", dict(maxst))
    keep = {}
    nst = 3 if sport in ("nba", "wnba", "nfl", "ncaaf", "ncaawb") else 2 if sport in ("nhl",) else 1 if sport == "ncaamb" else 8
    for stage in range(1, nst + 1):
        print(f"\n  after {STAGE_NAME[sport]} {stage}:")
        # calibration of the leader's price
        for lag in (1, 3, 5, 10):
            for lo, hi in ((0.5, 0.8), (0.8, 0.95), (0.2, 0.5)):
                bl = stage_bets(gs, stage, lag, lo, hi, "leader")
                bt = stage_bets(gs, stage, lag, 1 - hi, 1 - lo, "trailer")
                keep[(stage, lag, lo, "L")] = bl
                print(f"    +{lag:2d} min, leader at {lo * 100:.0f}-{hi * 100:.0f}c: {line(bl)}")
            if lag == 3:
                bt = stage_bets(gs, stage, lag, 0.2, 0.5, "trailer")
                print(f"    +{lag:2d} min, trailer at 20-50c: {line(bt)}")
    return keep


def report_esport(game):
    d_dir = os.path.join(CACHE, game)
    gser, mser = ESPORTS[game]
    evs = rj(os.path.join(d_dir, f"k_{gser}.json.gz"), {}) or {}
    maps = rj(os.path.join(d_dir, f"k_{mser}.json.gz"), {}) or {}
    mins = load_mins(game, gser)
    by = collections.defaultdict(dict)
    for ev, mm in maps.items():
        k, num = gkey(ev).rsplit("-", 1)
        win = [m for m in mm if m["res"] == "yes"]
        if num.isdigit() and len(win) == 1:
            by[k][int(num)] = (max(m["close"] for m in mm), win[0]["w"])
    gs = []
    for ev, mm in evs.items():
        mm = sorted(mm, key=lambda m: m["t"])
        if len(mm) != 2 or not mins.get(mm[0]["t"]) or gkey(ev) not in by:
            continue
        mp = by[gkey(ev)]
        yesn, othn = mm[0]["w"], mm[1]["w"]
        st, ys, os_ = [], 0, 0
        for num in sorted(mp):
            t, w = mp[num]
            if w == yesn:
                ys += 1
            elif w == othn:
                os_ += 1
            else:
                break
            st.append([num, t, ys, os_])
        gs.append({"ev": ev, "yes": mm[0], "res": 1 if mm[0]["res"] == "yes" else 0, "stages": st, "mins": mins[mm[0]["t"]], "close": mm[0]["close"]})
    print(f"\n=== {game}: {len(gs)} matches with map clocks and minute prices ===", flush=True)
    keep = {}
    for stage in (1, 2, 3):
        print(f"\n  after map {stage} (clock: Kalshi's map market closed):")
        for lag in (0, 1, 3, 5):
            for lo, hi in ((0.5, 0.8), (0.8, 0.95), (0.2, 0.5)):
                bl = stage_bets(gs, stage, lag, lo, hi, "leader")
                keep[(stage, lag, lo, "L")] = bl
                print(f"    +{lag} min, map leader at {lo * 100:.0f}-{hi * 100:.0f}c: {line(bl)}")
    return keep


def report(what):
    for w in what.split(","):
        if w in SPORTS:
            report_sport(w)
        elif w in ESPORTS:
            report_esport(w)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan_kalshi()
        scan_clocks()
    elif cmd == "fetch":
        fetch(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 400)
    elif cmd == "espntest":
        g = espn_day(sys.argv[2], int(time.time()) // DAY * DAY - 2 * DAY)
        print(len(g), short(g[:2], 800))
        print(short(espn_game(sys.argv[2], g[0]["id"]), 1500))
    elif cmd == "report":
        report(sys.argv[2])
    elif cmd == "peek":
        peek()
    elif cmd == "clocks":
        scan_clocks()
    else:
        print(__doc__)
