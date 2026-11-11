#!/usr/bin/env python3
"""CS2 match bets vs public team ratings (2026-11-11, Jan's ask: "compare cs2 and hltv"). Research only.

PAPER ONLY. Reads data, never trades, never writes state/.

    python3 cs2.py sources       # probe `cs2_sources`: which rating sites a robot can read at all
    python3 cs2.py fetch         # probe `cs2_fetch`: Valve standings + bo3.gg results -> bt_cache/cs2/ (price store)
    python3 cs2.py chart         # offline: ratings vs prices and the rule grid on chart prices (Polymarket sports cache)
    python3 cs2.py exam [ids]    # probe `cs2_exam` / `cs2_exam_fav24,ai1`: the rules at REAL buy prices, shared exam
    CS2_HOLDOUT=1 python3 cs2.py exam fav24,fav24b   # 21 Dec ONLY: the registered fresh-data look (PROTOCOL 5),
                                 # after fresh fetches (census sports fetch, cs2_fetch, cs2_ai). Don't run it earlier.

Why: Jan (11 Nov) "can we find something between cs2 and hltv? people are dumb, would be nice to just go against
gamblers not the elite quants". HLTV itself blocks robots (Cloudflare 403 from GitHub too), so the stand-ins are
Valve's official monthly team standings (GitHub repo ValveSoftware/counter-strike_regional_standings, points per
team) and bo3.gg's public match results (18,000 CS2 matches since Sep 2025), from which we build our own rating.
Polymarket side: every CS2 match-winner market in the sports cache (bt_cache/sports, census.py), March to 9 Nov 2026.
Holdout rule: games from 10 Nov 2026 on are left out.
"""
import bisect
import collections
import datetime as dt
import difflib
import gzip
import json
import math
import os
import re
import statistics
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def get(url, timeout=25, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*", "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:2000]
    except Exception as e:
        return 0, repr(e).encode()


def sources():
    urls = [
        "https://www.hltv.org/ranking/teams",
        "https://www.hltv.org/ranking/teams/2026/june/1",
        "https://www.hltv.org/results?offset=0",
        "https://www.hltv.org/valve-ranking/teams",
        "https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live",
        "https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026",
        "https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/invitation",
        "https://api.bo3.gg/api/v1/teams?page[limit]=2",
        "https://api.bo3.gg/api/v1/matches?page[limit]=2&sort=-start_date&filter[matches.status][in]=finished",
        "https://bo3.gg/teams/earnings",
        "https://liquipedia.net/counterstrike/api.php?action=query&meta=siteinfo&format=json",
        "https://www.vlr.gg/",
        "https://api.elections.kalshi.com/trade-api/v2/series?category=Sports&limit=1000",
        "https://web.archive.org/cdx/search/cdx?url=hltv.org/ranking/teams/2026*&output=json&limit=400&filter=statuscode:200&collapse=urlkey",
        "https://web.archive.org/cdx/search/cdx?url=hltv.org/ranking/teams&output=json&limit=400&from=20260201&filter=statuscode:200&collapse=timestamp:8",
    ]
    for u in urls:
        st, body = get(u)
        txt = body.decode("utf-8", "replace")
        print(f"\n== {st} {len(body)} bytes  {u}")
        if "kalshi" in u and st == 200:
            ser = json.loads(txt).get("series") or []
            hit = [(s.get("ticker"), s.get("title")) for s in ser
                   if re.search(r"counter|cs2|csgo|esport|valorant|league of|dota", json.dumps(s), re.I)]
            print(len(ser), "sports series;", len(hit), "esports:", hit[:60])
        elif "api.github.com" in u and st == 200:
            print([x.get("name") for x in json.loads(txt)][:400])
        elif "archive.org" in u and st == 200:
            rows = json.loads(txt) if txt.strip() else []
            print(len(rows), "rows;", [(r[1], r[2]) for r in rows[1:]][:400])
        else:
            print(re.sub(r"\s+", " ", txt)[:700])


def jget(url, tries=4, headers=None):
    import time
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = e
            time.sleep(2 + 3 * i)
    print("  failed:", url[:120], repr(err)[:120])
    return None


def fetch(since="2025-09-01"):
    """Probe `cs2_fetch`: Valve's official monthly team standings + bo3.gg match results -> bt_cache/cs2/ (price store)."""
    import gzip
    import os
    import subprocess
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "cs2")
    os.makedirs(d, exist_ok=True)
    tok = os.environ.get("GH_TOKEN")
    hd = {"Authorization": "Bearer " + tok} if tok else {}
    base = "https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/"
    valve = {}
    for yr in ("2025", "2026"):
        for f in jget(base + yr, headers=hd) or []:
            m = re.match(r"standings_global_(\d{4})_(\d\d)_(\d\d)\.md$", f.get("name") or "")
            if not m or "-".join(m.groups()) < "2025-09":
                continue
            st, body = get(f["download_url"])
            rows = []
            for ln in body.decode("utf-8", "replace").splitlines():
                c = [x.strip() for x in ln.strip().strip("|").split("|")]
                if len(c) >= 3 and c[0].isdigit():
                    rows.append([int(c[0]), c[1], c[2], c[3] if len(c) > 3 else ""])
            valve["-".join(m.groups())] = rows
            print("valve", "-".join(m.groups()), st, len(rows), rows[:2])
    json.dump(valve, gzip.open(os.path.join(d, "valve.json.gz"), "wt"))

    api = "https://api.bo3.gg/api/v1/"
    first = jget(api + "matches?page[offset]=0&page[limit]=100&sort=-start_date&filter[matches.status][in]=finished")
    print("bo3 total", (first or {}).get("total"), "keys", sorted(((first or {}).get("results") or [{}])[0])[:80])
    lim = len((first or {}).get("results") or []) or 50
    keep = ("id", "slug", "team1_id", "team2_id", "winner_team_id", "team1_score", "team2_score", "bo_type",
            "start_date", "end_date", "tier", "tier_rank", "tournament_id", "discipline_id", "stars", "maps_score")
    matches, off = [], 0
    while off < 60000:
        r = first if off == 0 else jget(api + f"matches?page[offset]={off}&page[limit]={lim}&sort=-start_date"
                                              "&filter[matches.status][in]=finished")
        res = (r or {}).get("results") or []
        if not res:
            break
        matches += [{k: x.get(k) for k in keep} for x in res]
        off += lim
        if off % (lim * 20) == 0:
            print("  bo3 matches", len(matches), res[-1].get("start_date"))
        if (res[-1].get("start_date") or "9") < since:
            break
    json.dump(matches, gzip.open(os.path.join(d, "bo3_matches.json.gz"), "wt"))
    print("bo3 matches saved", len(matches), matches[-1]["start_date"] if matches else None)
    need = {m[k] for m in matches for k in ("team1_id", "team2_id") if m.get(k)}
    teams, off = {}, 0
    while off < 20000:
        r = jget(api + f"teams?page[offset]={off}&page[limit]={lim}")
        res = (r or {}).get("results") or []
        if not res:
            break
        for x in res:
            teams[x["id"]] = {k: x.get(k) for k in ("name", "slug", "acronym", "rank", "discipline_id")}
        off += lim
    json.dump(teams, gzip.open(os.path.join(d, "bo3_teams.json.gz"), "wt"))
    print("bo3 teams saved", len(teams), "of the", len(need), "needed:", len(need & set(teams)))
    if os.environ.get("GITHUB_ACTIONS"):
        subprocess.run([sys.executable, "store.py", "push", "bt_cache"], check=False)


def peek(team="mouz"):
    """Probe `cs2_peek_<team>`: what bo3.gg stores per match (prediction bot? bookmaker odds?), for a few finished games."""
    api = "https://api.bo3.gg/api/v1/"
    r = jget(api + "matches?page[offset]=0&page[limit]=100&sort=-start_date&filter[matches.status][in]=finished") or {}
    t = jget(api + f"teams?filter[teams.slug][eq]={team}") or {}
    print("team lookup", json.dumps(t)[:600])
    ms = [x for x in r.get("results") or [] if team in (x.get("slug") or "")][:2] or (r.get("results") or [])[:2]
    for x in ms:
        sl, mid = x["slug"], x["id"]
        print("\n#####", sl, mid, "bet_updates:", json.dumps(x.get("bet_updates"))[:1500])
        for u in [api + f"matches/{sl}", api + f"matches/{mid}", api + f"matches/{sl}?with=teams,predictions,bets,odds",
                  api + f"matches/{mid}/predictions", api + f"matches/{mid}/prediction", api + f"predictions?filter[predictions.match_id][eq]={mid}",
                  api + f"matches/{mid}/bets", api + f"matches/{mid}/odds", api + f"bets?filter[bets.match_id][eq]={mid}",
                  api + f"matches/{mid}/ai_prediction", api + f"ai_predictions?filter[match_id][eq]={mid}",
                  f"https://bo3.gg/matches/{sl}"]:
            st, body = get(u)
            txt = body.decode("utf-8", "replace")
            print(f"\n== {st} {len(body)}  {u}")
            if u.startswith("https://bo3.gg/"):
                for k in re.finditer(r"(predict|odds|coef|winProb|win_prob|probab|bookmaker)", txt, re.I):
                    print("   ...", re.sub(r"\s+", " ", txt[max(0, k.start() - 150):k.start() + 250]))
                    if k.start() > 0 and txt.count("predict") > 40:
                        break
            else:
                print(re.sub(r"\s+", " ", txt)[:2500])


def pprobe(slug="spirit-vs-fut-cs2-11-11-2026", mid="132592"):
    """Probe `cs2_pprobe`: find where bo3.gg keeps per-player ratings for a match (Jan, 11 Nov: "what about players'
    rating the last couple of days?")."""
    api = "https://api.bo3.gg/api/v1/"
    st, body = get(f"https://bo3.gg/matches/{slug}")
    html = body.decode("utf-8", "replace")
    js = sorted(set(re.findall(r'(/_nuxt/[A-Za-z0-9_.-]+\.js)', html)))
    seen, todo, paths = set(), list(js), collections.Counter()
    while todo and len(seen) < 400:
        u = todo.pop()
        if u in seen:
            continue
        seen.add(u)
        t = get("https://bo3.gg" + u)[1].decode("utf-8", "replace")
        for x in re.findall(r'["\'`](?:\./)?([A-Za-z0-9_.-]+\.js)["\'`]', t):
            todo.append("/_nuxt/" + x)
        for ep in re.findall(r'["\'`](/?(?:api/v\d/)?[a-z_]*(?:player|stat|game|round|rating)[a-z_/${}.:-]{0,70})["\'`]', t):
            paths[ep] += 1
    print("page", st, "scripts read", len(seen))
    for pth, n in sorted(paths.items()):
        print(f"  {n:3}  {pth}")
    for u in [f"matches/{slug}", f"matches/{mid}", f"matches/{slug}?with=games,players,players_stats",
              f"games?filter[games.match_id][eq]={mid}", f"matches/{slug}/games", f"matches/{slug}/players_stats",
              f"matches/{mid}/players_stats", f"matches/{slug}/player_stats", f"players_stats?filter[match_id][eq]={mid}",
              f"player_stats?filter[player_stats.match_id][eq]={mid}", f"matches/{slug}/stats", f"matches/{slug}/lineups",
              f"matches/{slug}/players", f"game_player_stats?filter[match_id][eq]={mid}"]:
        st, b = get(api + u)
        t = b.decode("utf-8", "replace")
        print("TRY", st, len(t), u, "::", re.sub(r"\s+", " ", t)[:700])
    # follow a game id if we found one
    st, b = get(api + f"games?filter[games.match_id][eq]={mid}")
    try:
        g = json.loads(b)
        gid = (g.get("results") or g.get("data") or [{}])[0].get("id")
    except Exception:
        gid = None
    if gid:
        for u in [f"games/{gid}", f"games/{gid}/players_stats", f"games/{gid}/player_stats", f"games/{gid}/stats",
                  f"games/{gid}/rounds", f"players_stats?filter[game_id][eq]={gid}"]:
            st, b = get(api + u)
            print("GAME", st, u, "::", re.sub(r"\s+", " ", b.decode("utf-8", "replace"))[:900])


def jsapi(slug="sokerorg-vs-mouz-nxt-09-11-2026"):
    """Probe `cs2_jsapi`: read bo3.gg's page scripts to find which API paths its prediction widget calls."""
    st, pb = get("https://bo3.gg/predictions")
    print("predictions page", st, len(pb), re.sub(r"\s+", " ", pb.decode("utf-8", "replace"))[:1500])
    st, body = get(f"https://bo3.gg/matches/{slug}")
    html = body.decode("utf-8", "replace")
    js = sorted(set(re.findall(r'(/_nuxt/[A-Za-z0-9_.-]+\.js)', html)))
    print(st, len(html), "scripts", len(js))
    seen, todo, paths = set(), list(js), collections.Counter()
    while todo and len(seen) < 400:
        u = todo.pop()
        if u in seen:
            continue
        seen.add(u)
        st, b = get("https://bo3.gg" + u)
        t = b.decode("utf-8", "replace")
        for x in re.findall(r'["\'`](?:\./)?([A-Za-z0-9_.-]+\.js)["\'`]', t):
            todo.append("/_nuxt/" + x)
        for k in re.finditer(r"predict|forecast|ai_|odds|probabilit|winrate|win_rate", t, re.I):
            seg = t[max(0, k.start() - 120):k.start() + 160]
            for pth in re.findall(r'["\'`](/?(?:api/)?v\d/[^"\'`]{3,80}|/[a-z_]+/[a-z_/{}$.:-]{3,60})["\'`]', seg):
                paths[pth] += 1
    print("scripts read", len(seen))
    for u in sorted(seen):
        t = get("https://bo3.gg" + u)[1].decode("utf-8", "replace")
        for ep in re.findall(r"apiService\.(?:get|post)\(\s*([`'\"][^`'\"]{2,140}[`'\"])", t):
            paths["API " + ep] += 1
        if "match-prediction" in t or "ai_predict" in t or "aiPredict" in t:
            for k in re.finditer(r"ai_predict|aiPredict|prediction_|predictions?\b[^\"]{0,3}[:=]", t):
                print("  WIDGET", u, "::", re.sub(r"\s+", " ", t[max(0, k.start() - 250):k.start() + 250]))
        for k in re.finditer(r"prediction", t):
            seg = t[max(0, k.start() - 200):k.start() + 200]
            if re.search(r"/v\d|api|\$fetch|useFetch|get\(|url", seg) and "predictions\"" not in seg[:5]:
                print("  JS", u, "::", re.sub(r"\s+", " ", seg))
    for pth, n in sorted(paths.items()):
        print(f"  {n:3}  {pth}")
    for u in ["matches/%s/predictions" % slug, "predictions/matches/%s" % slug, "matches/%s/ai_predictions" % slug,
              "ai/predictions?filter[match_slug][eq]=%s" % slug, "matches/%s/forecast" % slug, "games/predictions",
              "match_predictions?filter[match_predictions.match_slug][eq]=%s" % slug, "predictions?page[limit]=2",
              "articles?filter[articles.type][eq]=prediction&page[limit]=2", "predictions/matches?page[limit]=2",
              "matches/%s/bet_updates" % slug, "bet_updates?filter[bet_updates.match_id][eq]=133431"]:
        for base in ("https://api.bo3.gg/api/v1/", "https://api.bo3.gg/api/v2/"):
            st, b = get(base + u)
            print(st, len(b), base + u, b[:300].decode("utf-8", "replace") if st == 200 else "")


def ai(since="2026-02-15"):
    """Probe `cs2_ai`: bo3.gg's own AI prediction per finished match (field ai_predictions, asked with
    with=ai_predictions) plus the bookmaker odds it shows (bet_updates) -> bt_cache/cs2/bo3_ai.json.gz (price store)."""
    import subprocess
    d = os.path.join(ROOT, "bt_cache", "cs2")
    os.makedirs(d, exist_ok=True)
    api = "https://api.bo3.gg/api/v1/matches?page[limit]=100&sort=-start_date&filter[matches.status][in]=finished&with=ai_predictions"
    out, off, shown = [], 0, 0
    while off < 40000:
        r = jget(api + f"&page[offset]={off}")
        res = (r or {}).get("results") or []
        if not res:
            print("stop at", off, json.dumps(r)[:300])
            break
        for x in res:
            if x.get("ai_predictions") and shown < 4:
                print("SAMPLE", x["slug"], x["start_date"], json.dumps(x["ai_predictions"])[:1500])
                shown += 1
            out.append({k: x.get(k) for k in ("id", "slug", "team1_id", "team2_id", "winner_team_id", "start_date",
                                              "end_date", "bo_type", "tier", "ai_predictions", "bet_updates")})
        off += 100
        if off % 2000 == 0:
            print("  ", off, res[-1]["start_date"], "with ai:", sum(1 for x in out if x.get("ai_predictions")))
        if res[-1]["start_date"] < since:
            break
    json.dump(out, gzip.open(os.path.join(d, "bo3_ai.json.gz"), "wt"))
    print("saved", len(out), "with ai:", sum(1 for x in out if x.get("ai_predictions")),
          "with odds:", sum(1 for x in out if x.get("bet_updates")))
    if os.environ.get("GITHUB_ACTIONS"):
        subprocess.run([sys.executable, "store.py", "push", "bt_cache"], check=False)


def pstats(since="2025-12-01"):
    """Probe `cs2_pstats`: bo3.gg per-player stats for every finished match since `since`
    (api matches/{slug}/players_stats: one row per player per match, bo3.gg's own rating ~6 = average)
    -> bt_cache/cs2/bo3_pstats.json.gz (price store). Jan, 11 Nov: "what about players' rating the last couple of days?"."""
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    d = os.path.join(ROOT, "bt_cache", "cs2")
    M = [x for x in load(FILES[2]) if (x.get("start_date") or "") >= since and x.get("slug")]
    print("matches to read", len(M))
    api = "https://api.bo3.gg/api/v1/matches/"

    def one(x):
        r = jget(api + x["slug"] + "/players_stats", tries=3)
        if not isinstance(r, list):
            return x["id"], None
        rows = []
        for p in r:
            tid = (p.get("team_clan") or {}).get("team_id")
            rows.append([p.get("steam_profile_id"), tid, p.get("player_rating"), p.get("kills"), p.get("death"),
                         p.get("adr"), p.get("kast")])
        return x["id"], rows
    out, bad, shown = {}, 0, False
    with ThreadPoolExecutor(8) as ex:
        for i, (mid, rows) in enumerate(ex.map(one, M)):
            if rows is None:
                bad += 1
            elif rows:
                out[mid] = rows
                if not shown:
                    print("SAMPLE", mid, rows[:3])
                    shown = True
            if i % 1000 == 0:
                print("  ", i, "with stats", len(out), "failed", bad)
    json.dump(out, gzip.open(os.path.join(d, "bo3_pstats.json.gz"), "wt"))
    print("saved", len(out), "matches with player stats; failed", bad, "of", len(M))
    if os.environ.get("GITHUB_ACTIONS"):
        subprocess.run([sys.executable, "store.py", "push", "bt_cache"], check=False)


# ======================================================================== the test
ROOT = os.path.dirname(os.path.abspath(__file__))
REL = "https://github.com/palsk1/poly-paper-bot/releases/download/price-store/"
FILES = ["bt_cache/sports/markets.json.gz", "bt_cache/sports/hist.json.gz", "bt_cache/cs2/bo3_matches.json.gz",
         "bt_cache/cs2/bo3_teams.json.gz", "bt_cache/cs2/valve.json.gz", "bt_cache/cs2/bo3_ai.json.gz"]
HOLD = dt.datetime(2026, 11, 10, tzinfo=dt.timezone.utc).timestamp()
H = 3600


def load(name):
    p = os.path.join(ROOT, name)
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        print("download", name)
        st, body = get(REL + name.replace("/", "--"), timeout=300)
        if st != 200:
            raise SystemExit(f"could not download {name}: {st}")
        open(p, "wb").write(body)
    return json.load(gzip.open(p, "rt"))


def nm(s):
    s = (s or "").lower().replace("&", "and")
    s = re.sub(r"^ex-|\b(team|esports|esport|gaming|club|e-sports|gg)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _at(h, t):
    i = bisect.bisect_right(h[0], t) - 1
    if i < 0 or t - h[0][i] > 6 * H:
        return None
    return h[1][i]


def build():
    """Finished CS2 match-winner markets with chart prices 1h/6h/24h before the start, the result, our rating
    (Elo from bo3.gg results, only matches finished before the start), Valve's points (last list before the start)."""
    mk = load(FILES[0])["markets"]
    mk = list(mk.values()) if isinstance(mk, dict) else mk
    hist = load(FILES[1])
    M, T, V = load(FILES[2]), load(FILES[3]), load(FILES[4])
    rows = []
    for m in mk:
        if not (m.get("slug") or "").startswith("cs2-") or m.get("smt") != "moneyline" or not m.get("gst"):
            continue
        f = m.get("final")
        if not f or max(f) < 0.99:
            continue
        if os.environ.get("CS2_HOLDOUT"):     # the 21 Dec look: ONLY games from 10 Nov on (PROTOCOL 5)
            if m["gst"] < HOLD:
                continue
        elif m["gst"] > HOLD - 6 * H or (m.get("end") or 0) >= HOLD:
            continue
        h = hist.get(str(m["id"]))
        if not h or not h[0]:
            continue
        bo = re.search(r"\(BO(\d)\)", m["q"])
        rows.append(dict(id=m["id"], cid=m.get("cid"), toks=m.get("toks"), ev=m.get("ev"), q=m["q"], a=m["outs"][0],
                         b=m["outs"][1], w=0 if f[0] > 0.5 else 1, gst=m["gst"], vol=m.get("vol") or 0,
                         fee=m.get("fee") or 0, bo=int(bo.group(1)) if bo else 0,
                         p1=_at(h, m["gst"] - H), p6=_at(h, m["gst"] - 6 * H), p24=_at(h, m["gst"] - 24 * H)))
    rows.sort(key=lambda r: r["gst"])
    # our rating: Elo over every finished bo3.gg CS2 match, in the order they ended
    for x in M:
        x["t"] = dt.datetime.fromisoformat(x["start_date"]).timestamp()
        x["te"] = dt.datetime.fromisoformat(x["end_date"]).timestamp() if x.get("end_date") else x["t"] + 3 * H
    ev = [x for x in M if x.get("team1_id") and x.get("team2_id") and x.get("winner_team_id") in (x["team1_id"], x["team2_id"])]
    R, N, hist_r = collections.defaultdict(lambda: 1500.0), collections.Counter(), collections.defaultdict(lambda: ([], []))
    for x in sorted(ev, key=lambda x: x["te"]):
        a, b = x["team1_id"], x["team2_id"]
        e = 1 / (1 + 10 ** ((R[b] - R[a]) / 400))
        s = 1.0 if x["winner_team_id"] == a else 0.0
        k = ((60 if N[a] < 10 else 32) + (60 if N[b] < 10 else 32)) / 2 * (1.25 if (x.get("bo_type") or 1) >= 3 else 1)
        R[a] += k * (s - e)
        R[b] -= k * (s - e)
        N[a] += 1
        N[b] += 1
        for tid in (a, b):
            hist_r[tid][0].append(x["te"])
            hist_r[tid][1].append((R[tid], N[tid]))

    def rating(tid, t):
        ts_, vs = hist_r.get(tid, ([], []))
        i = bisect.bisect_left(ts_, t) - 1
        return vs[i] if i >= 0 else (1500.0, 0)
    tn = {int(k): nm(v["name"]) for k, v in T.items()}
    ta = {int(k): nm(v.get("acronym") or "") for k, v in T.items()}
    byday = collections.defaultdict(list)
    for x in ev:
        byday[int(x["t"] // 86400)].append(x)

    def same(a, b, acr):
        return a == b or a == acr or (len(a) >= 3 and len(b) >= 3 and (a in b or b in a)) or \
            difflib.SequenceMatcher(None, a, b).ratio() >= 0.85
    vd = sorted(V)
    vmap = {}
    for d in vd:     # first (best-ranked) team wins when two names look the same after cleaning
        vmap[d] = {}
        for r in V[d]:
            vmap[d].setdefault(nm(r[2]), (int(r[1]), r[0]))
    for r in rows:
        A, B = nm(r["a"]), nm(r["b"])
        best = None
        for dd in (-1, 0, 1):
            for x in byday.get(int(r["gst"] // 86400) + dd, []):
                if abs(x["t"] - r["gst"]) > 8 * H:
                    continue
                i1, i2 = x["team1_id"], x["team2_id"]
                if same(A, tn.get(i1, ""), ta.get(i1)) and same(B, tn.get(i2, ""), ta.get(i2)):
                    best = (x, i1, i2)
                elif same(A, tn.get(i2, ""), ta.get(i2)) and same(B, tn.get(i1, ""), ta.get(i1)):
                    best = (x, i2, i1)
        r["elo"] = None
        if best:
            x, ia, ib = best
            (ra, na), (rb, nb) = rating(ia, r["gst"] - 60), rating(ib, r["gst"] - 60)
            r.update(bo3_id=x["id"], ia=ia, ib=ib, tier=x.get("tier"), agree=(x["winner_team_id"] == ia) == (r["w"] == 0), na=na, nb=nb,
                     elo=1 / (1 + 10 ** ((rb - ra) / 400)))
        d = dt.datetime.fromtimestamp(r["gst"], dt.timezone.utc).strftime("%Y-%m-%d")
        i = bisect.bisect_right(vd, d) - 1
        va, vb = (vmap[vd[i]].get(A), vmap[vd[i]].get(B)) if i >= 0 else (None, None)
        r["valve"] = (va[0], vb[0]) if va and vb else None
    # bo3.gg's own AI pick (a predicted map score, e.g. 2-1). Its bookmaker odds (bet_updates) are NOT used: they
    # are the LAST odds seen, often from during or after the game (they "predict" the winner far too well: average
    # surprise 0.33 vs 0.60 for the Polymarket price an hour before).
    AI = {x["id"]: x.get("ai_predictions") or {} for x in load(FILES[5])}
    for r in rows:
        a = AI.get(r.get("bo3_id")) or {}
        r["ai"] = None
        if r.get("agree") and a.get("prediction_winner_team_id") in (r.get("ia"), r.get("ib")):
            sc = sorted([a.get("prediction_team1_score") or 0, a.get("prediction_team2_score") or 0])
            r["ai"] = {"side": 0 if a["prediction_winner_team_id"] == r["ia"] else 1, "sweep": sc[0] == 0}
    return rows


VALVE_SCALE = 850     # Valve points -> chance: 1 / (1 + 10^(-(a-b)/850)), the best-fitting scale on these games


def side_p(r, s, key):
    p = r[key]
    return p if s == 0 else 1 - p


def model_p(r, s, kind):
    if kind == "elo":
        e = r["elo"]
    else:
        a, b = r["valve"]
        e = 1 / (1 + 10 ** ((b - a) / VALVE_SCALE))
    return e if s == 0 else 1 - e


def _ts(s):
    try:
        return dt.datetime.fromisoformat(s).timestamp() if s else None
    except ValueError:
        return None


def add_form(rows):
    """Team form from bo3.gg results that ENDED before the match (no look-ahead): r['form'][side] =
    won5 / lost3 / lost2 / new (under 15 past matches) / rest (hours since its last match) / roster (Valve list
    changed by 1+ player since the month before, or None)."""
    M = load("bt_cache/cs2/bo3_matches.json.gz")
    hist = collections.defaultdict(list)
    for x in M:
        a_, b_, w_ = x.get("team1_id"), x.get("team2_id"), x.get("winner_team_id")
        if not a_ or not b_ or w_ not in (a_, b_):
            continue
        t0 = _ts(x.get("start_date"))
        te = _ts(x.get("end_date")) or (t0 + 3 * H if t0 else None)
        if not te:
            continue
        for tid in (a_, b_):
            hist[tid].append((te, w_ == tid))
    for h in hist.values():
        h.sort()
    ends = {k: [y[0] for y in h] for k, h in hist.items()}
    V = load("bt_cache/cs2/valve.json.gz")
    vd = sorted(V)
    ros = {d: {} for d in vd}
    for d in vd:
        for _, _, tm, pl in V[d]:
            ros[d].setdefault(nm(tm), frozenset(p.strip().lower() for p in pl.split(",") if p.strip()))

    def roster(name, t):
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")
        i = bisect.bisect_right(vd, d) - 1
        if i < 1:
            return None
        a_, b_ = ros[vd[i]].get(name), ros[vd[i - 1]].get(name)
        return None if a_ is None or b_ is None else len(a_ - b_) >= 1

    for r in rows:
        r["form"] = None
        if not r.get("agree"):
            continue
        f = []
        for tid, name in ((r["ia"], r["a"]), (r["ib"], r["b"])):
            h = hist.get(tid, [])
            pst = h[:bisect.bisect_left(ends.get(tid, []), r["gst"] - 60)]
            if len(pst) < 5:
                break
            f.append({"won5": all(y[1] for y in pst[-5:]), "lost3": not any(y[1] for y in pst[-3:]),
                      "lost2": not pst[-1][1] and not pst[-2][1], "new": len(pst) < 15,
                      "rest": (r["gst"] - pst[-1][0]) / H, "roster": roster(nm(name), r["gst"])})
        if len(f) == 2:
            r["form"] = f
    return rows


def add_players(rows, days=3):
    """Players' recent form (Jan, 11 Nov). For each team in each match: the five players who played it (lineups are
    announced before the match), each player's average bo3.gg rating in matches that ENDED in the last `days` days
    before the start (`hot`), and over the 60 days before that (`base`). r['pf'][side] = {hot, base, delta, n}
    where delta = hot - base averaged over players with both, n = players with recent matches."""
    P = load("bt_cache/cs2/bo3_pstats.json.gz")
    M = {x["id"]: x for x in load(FILES[2])}
    hist = collections.defaultdict(list)      # player -> [(end, rating)]
    lineup = {}
    for mid, ps in P.items():
        x = M.get(int(mid))
        if not x:
            continue
        te = _ts(x.get("end_date")) or ((_ts(x.get("start_date")) or 0) + 3 * H)
        lu = collections.defaultdict(list)
        for sp, tid, rt, *_ in ps:
            if sp is None or rt is None:
                continue
            hist[sp].append((te, rt))
            lu[tid].append(sp)
        lineup[int(mid)] = lu
    for h in hist.values():
        h.sort()
    ends = {k: [y[0] for y in h] for k, h in hist.items()}

    def form(sp, t):
        h, e = hist.get(sp, []), ends.get(sp, [])
        j = bisect.bisect_left(e, t - 60)
        i = bisect.bisect_left(e, t - days * 86400)
        k = bisect.bisect_left(e, t - 60 * 86400)
        hot = [y[1] for y in h[i:j]]
        base = [y[1] for y in h[k:i]]
        return (statistics.mean(hot) if hot else None, statistics.mean(base) if len(base) >= 3 else None)
    for r in rows:
        r["pf"] = None
        lu = lineup.get(r.get("bo3_id"))
        if not lu or not r.get("agree"):
            continue
        out = []
        for tid in (r["ia"], r["ib"]):
            fs = [form(sp, r["gst"]) for sp in lu.get(tid, [])]
            if len(fs) < 4:
                break
            hot = [a for a, b in fs if a is not None]
            dl = [a - b for a, b in fs if a is not None and b is not None]
            base = [b for a, b in fs if b is not None]
            out.append({"hot": statistics.mean(hot) if hot else None, "base": statistics.mean(base) if base else None,
                        "delta": statistics.mean(dl) if len(dl) >= 3 else None, "n": len(hot)})
        if len(out) == 2:
            r["pf"] = out
    return rows


def players():
    """`python3 cs2.py players`: does the players' last few days say anything the price doesn't?"""
    for days in (2, 3, 7):
        rows = add_players(build(), days)
        R = [r for r in rows if r["p1"] is not None and 0.03 < r["p1"] < 0.97 and r["pf"]
             and r["pf"][0]["delta"] is not None and r["pf"][1]["delta"] is not None]
        R.sort(key=lambda r: r["gst"])
        print(f"\n=== last {days} days: {len(R)} matches with both teams' recent player form ===")
        # 1) does recent form (hot - base, team vs team) predict on top of the price? split into 5 groups
        def g(r):
            return r["pf"][0]["delta"] - r["pf"][1]["delta"]
        qs = sorted(g(r) for r in R)
        cuts = [qs[int(len(qs) * f)] for f in (0.2, 0.4, 0.6, 0.8)]
        print("| Team A's players hot minus team B's | Matches | A won per 100: price said / really | Back A per $100 | Back B per $100 |")
        print("|---|---|---|---|---|")
        for lo, hi, lab in ((-9, cuts[0], "B much hotter"), (cuts[0], cuts[1], "B a bit hotter"), (cuts[1], cuts[2], "even"),
                            (cuts[2], cuts[3], "A a bit hotter"), (cuts[3], 9, "A much hotter")):
            sel = [r for r in R if lo <= g(r) < hi]
            a = [100 / (r["p1"] + 0.01) * (r["w"] == 0) - 100 for r in sel]
            b = [100 / (1 - r["p1"] + 0.01) * (r["w"] == 1) - 100 for r in sel]
            print(f"| {lab} ({lo:+.2f} to {hi:+.2f}) | {len(sel)} | {100 * statistics.mean(r['p1'] for r in sel):.1f} / "
                  f"{100 * statistics.mean(r['w'] == 0 for r in sel):.1f} | {statistics.mean(a):+.2f} | {statistics.mean(b):+.2f} |")
        # 2) rules: back the hotter team (gap 0.3+ / 0.5+), and only when it's the underdog
        for gap in (0.3, 0.5):
            for dog in (False, True):
                sel = []
                for r in R:
                    for s_ in (0, 1):
                        d = (g(r) if s_ == 0 else -g(r))
                        q = side_p(r, s_, "p1")
                        if d >= gap and (not dog or q < 0.5):
                            sel.append((r, s_, q, 1))
                print(chart_line(f"back the team whose players are {gap}+ hotter{' (underdog only)' if dog else ''}", sel))
        # 3) also: hot level, not change (players' recent average vs opponent's)
        sel = [(r, s_, side_p(r, s_, "p1"), 1) for r in R for s_ in (0, 1)
               if r["pf"][s_]["hot"] is not None and r["pf"][1 - s_]["hot"] is not None
               and r["pf"][s_]["hot"] - r["pf"][1 - s_]["hot"] >= 0.5 and side_p(r, s_, "p1") < 0.5]
        print(chart_line("underdog whose players' recent rating is 0.5+ above the favorite's", sel))
        h = len(R) // 2
        for lab, part in (("first half", R[:h]), ("second half", R[h:])):
            sel = [(r, s_, side_p(r, s_, "p1"), 1) for r in part for s_ in (0, 1) if (g(r) if s_ == 0 else -g(r)) >= 0.5]
            print("   ", chart_line(lab + ", hotter by 0.5+", sel))


def rated(rows, kind):
    if kind == "elo":
        return [r for r in rows if r.get("elo") is not None and r.get("agree") and min(r["na"], r["nb"]) >= 15]
    return [r for r in rows if r.get("valve")]


# The rules (fixed before the real-price check). key = chart price used, hours = when the bot would buy.
RULES = [
    ("elo10", "CS2: back the team our rating likes, 10c+ over the price, 1h before", "p1", 1,
     lambda r, s, q: r.get("elo") is not None and r.get("agree") and min(r["na"], r["nb"]) >= 15
     and model_p(r, s, "elo") - q >= 0.10),
    ("valve10", "CS2: back the team Valve's ranking likes, 10c+ over the price, 1h before", "p1", 1,
     lambda r, s, q: r.get("valve") and model_p(r, s, "valve") - q >= 0.10),
    ("fav24", "CS2: favorite at 70-97c a day before the match", "p24", 24, lambda r, s, q: 0.70 <= q < 0.97),
    ("fav24b", "CS2: favorite at 70-97c a day before, minor leagues (bo3.gg tier B)", "p24", 24,
     lambda r, s, q: 0.70 <= q < 0.97 and r.get("tier") == "b"),
    ("fav1", "CS2: favorite at 70-97c an hour before the match", "p1", 1, lambda r, s, q: 0.70 <= q < 0.97),
    # Jan, 11 Nov: "if we just used bo3.gg's prediction model, would we have gained money?"
    ("ai1", "CS2: back bo3.gg's AI pick, 1h before", "p1", 1, lambda r, s, q: r.get("ai") and r["ai"]["side"] == s),
    ("aisweep", "CS2: back bo3.gg's AI pick when it predicts a 2-0, 1h before", "p1", 1,
     lambda r, s, q: r.get("ai") and r["ai"]["side"] == s and r["ai"]["sweep"]),
    ("ai24", "CS2: back bo3.gg's AI pick, a day before", "p24", 24, lambda r, s, q: r.get("ai") and r["ai"]["side"] == s),
    # Jan, 11 Nov: "what do the losers have in common? Upsets? Roster changes? Start of a losing streak?"
    # Picked from the `upsets` table (34 patterns x 2 sides), so the luck bar counts them all.
    ("dogclose", "CS2: back the underdog in a close match (favorite 50-60c), 1h before", "p1", 1,
     lambda r, s, q: 0.40 < q < 0.50),
    ("dogstreak", "CS2: back the underdog when the favorite won its last 5, 1h before", "p1", 1,
     lambda r, s, q: q < 0.50 and r.get("form") and r["form"][1 - s]["won5"]),
    ("favdrop", "CS2: back the favorite after its price fell 5c+ since a day before, 1h before", "p1", 1,
     lambda r, s, q: 0.50 <= q < 0.97 and r["p24"] is not None and q - side_p(r, s, "p24") <= -0.05),
    ("bo1fav", "CS2: favorite at 60-97c in a best-of-1, 1h before", "p1", 1,
     lambda r, s, q: r.get("bo") == 1 and 0.60 <= q < 0.97),
    ("doglost3", "CS2: back the favorite when the underdog lost its last 3, 1h before", "p1", 1,
     lambda r, s, q: q >= 0.50 and r.get("form") and r["form"][1 - s]["lost3"]),
]
TRIES = 155    # first dig 65 (rating gaps, bands, tiers, timing, drift, volume, months, 14 AI bets) + upset hunt 90
#                (34 patterns x 2 sides, price-drop at 3/5/8c from 24h and 6h, bands x patterns)


def picks(rows, rule):
    _, _, key, hrs, f = rule
    out = []
    for r in rows:
        p = r[key]
        if p is None or not 0.03 < p < 0.97:
            continue
        for s in (0, 1):
            q = side_p(r, s, key)
            if f(r, s, q):
                out.append((r, s, q, hrs))
    return out


def chart_line(name, sel, add=0.01):
    pl = [(100 / (q + add)) * (r["w"] == s) - 100 for r, s, q, _ in sel]
    if len(pl) < 5:
        return f"| {name} | {len(pl)} | | | |"
    n, m = len(pl), statistics.mean(pl)
    se = statistics.pstdev(pl) / math.sqrt(n)
    return f"| {name} | {n} | {m:+.2f} | {m - 1.645 * se:+.2f} to {m + 1.645 * se:+.2f} | {sum(1 for r, s, q, _ in sel if r['w'] == s)} won |"


def logloss(rs, f):
    return -sum(math.log(max(1e-6, f(r) if r["w"] == 0 else 1 - f(r))) for r in rs) / len(rs)


def chart():
    rows = add_form(build())
    p1 = [r for r in rows if r["p1"] is not None and 0.03 < r["p1"] < 0.97]
    print(f"{len(rows)} finished CS2 match-winner markets, {len(p1)} with a price 1h before; matched to bo3.gg "
          f"{sum(1 for r in rows if r.get('elo') is not None)}, results agree {sum(1 for r in rows if r.get('agree'))}, "
          f"Valve points for both teams {sum(1 for r in rows if r.get('valve'))}")
    for kind in ("elo", "valve"):
        rs = rated(p1, kind)
        print(f"{kind}: {len(rs)} games. Average surprise (lower = better): price {logloss(rs, lambda r: r['p1']):.4f}, "
              f"rating {logloss(rs, lambda r: model_p(r, 0, kind)):.4f}, "
              f"price + 10% rating {logloss(rs, lambda r: 0.9 * r['p1'] + 0.1 * model_p(r, 0, kind)):.4f}")
    print("\n| Rule (chart price +1c, no fee) | Bets | Per $100 | Luck range | |\n|---|---|---|---|---|")
    for rule in RULES:
        print(chart_line(rule[1], picks(rows, rule)))
    return rows


def upsets():
    """Jan, 11 Nov: what do the losers have in common? Each pattern: how often the favorite lost (price said vs
    really) and what backing the underdog / the favorite made per $100 at chart prices 1h before +1c (no fee),
    with the luck range and first/second half. Positive "really" minus "price said" = upsets happen MORE often."""
    rows = add_form(build())
    R = []
    for r in rows:
        if r["p1"] is None or not 0.03 < r["p1"] < 0.97 or not r["form"]:
            continue
        fs = 0 if r["p1"] >= 0.5 else 1
        q, F, U = side_p(r, fs, "p1"), r["form"][fs], r["form"][1 - fs]
        mv = None if r["p24"] is None else q - side_p(r, fs, "p24")
        R.append({"q": q, "up": r["w"] != fs, "t": r["gst"], "pat": {
            "favorite won its last 5": F["won5"], "favorite lost its last 2": F["lost2"],
            "underdog lost its last 3": U["lost3"], "underdog won its last 5": U["won5"],
            "favorite is a new team (under 15 matches)": F["new"], "underdog is a new team": U["new"],
            "favorite played in the last 12h": F["rest"] < 12, "underdog played in the last 12h": U["rest"] < 12,
            "favorite rested 14+ days": F["rest"] > 336, "underdog rested 14+ days": U["rest"] > 336,
            "favorite changed a player this month": F["roster"] is True,
            "underdog changed a player this month": U["roster"] is True,
            "best-of-1": r.get("bo") == 1, "best-of-3": r.get("bo") == 3,
            "top events (tier S/A)": r.get("tier") in ("s", "a"), "small events (tier B/C)": r.get("tier") in ("b", "c"),
            "favorite's price fell 5c+ since a day before": mv is not None and mv <= -0.05,
            "favorite's price rose 5c+ since a day before": mv is not None and mv >= 0.05,
            "close match (favorite 50-60c)": q < 0.60, "big favorite (75c+)": q >= 0.75}})
    R.sort(key=lambda f: f["t"])

    def pl(sel, dog):
        return [100 / ((1 - f["q"] if dog else f["q"]) + 0.01) * (f["up"] == dog) - 100 for f in sel]

    print(f"{len(R)} matches with both teams' form, {sum(f['up'] for f in R)} upsets\n")
    print("| Pattern | Matches | Upsets per 100: price said / really | Back underdog per $100 (halves) "
          "| Back favorite per $100 (halves) |\n|---|---|---|---|---|")
    for k in ["(all matches)"] + list(R[0]["pat"]):
        sel = R if k.startswith("(") else [f for f in R if f["pat"][k]]
        if len(sel) < 60:
            continue
        h, cell = len(sel) // 2, []
        for dog in (True, False):
            a = pl(sel, dog)
            se = 1.645 * statistics.pstdev(a) / math.sqrt(len(a))
            cell.append(f"{statistics.mean(a):+.2f} ±{se:.2f} ({statistics.mean(a[:h]):+.1f} / {statistics.mean(a[h:]):+.1f})")
        print(f"| {k} | {len(sel)} | {100 * sum(1 - f['q'] for f in sel) / len(sel):.1f} / "
              f"{100 * sum(f['up'] for f in sel) / len(sel):.1f} | {cell[0]} | {cell[1]} |")


def exam_run(only=None):
    import exam
    rows = chart()
    import informed
    cache = {}

    def tape_fn(sg):
        cid = sg["cid"]
        if cid not in cache:
            out, cur = [], None
            for _ in range(80):        # newest first: page back until we're before the buy time
                pr = {"condition_id": cid, "limit": 500}
                if cur:
                    pr["cursor"] = cur
                r, cur, _ = informed.trades_page(pr)
                out += r
                ts_ = [float(x.get("timestamp") or 0) for x in r]
                if not cur or not r or (ts_ and min(t / 1000 if t > 1e11 else t for t in ts_) < sg["t"] - 600):
                    break
            cache[cid] = out
        return cache[cid]
    print()
    for rule in RULES:
        if only and rule[0] not in only.split(","):
            continue
        sel = picks(rows, rule)
        sig = [{"cid": r["cid"], "toks": r["toks"], "oi": s, "t": r["gst"] - hrs * H, "end": r["gst"],
                "pay": 1.0 if r["w"] == s else 0.0, "ev": r["ev"], "q": q, "fee": r["fee"]} for r, s, q, hrs in sel]
        info = {}
        bets = exam.fills(sig, window=3 * H, tape_fn=tape_fn, workers=10, info=info)
        # selection check: did the bets we COULD price (someone else bought in the window) do better on the chart
        # than the ones nobody bought? If so, "a real buy happened" is itself a tip-off and the real-price result flatters.
        got = {str(b["ev"]) for b in bets}
        for lab, part in (("priced", [x for x in sel if str(x[0]["ev"]) in got]),
                          ("nobody bought", [x for x in sel if str(x[0]["ev"]) not in got])):
            print("  chart result, " + chart_line(lab, part))
        gap = [b["px"] - b["q"] for b in bets if b.get("q") is not None]
        if gap:
            print(f"  {rule[1]}: real first buy minus chart price, median {100 * statistics.median(gap):+.1f}c")
        exam.score(bets, rule[1], tries=TRIES, src="cs2.py exam", note=f"chart {len(sel)} picks, {info}")
        print()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sources":
        sources()
    elif cmd == "fetch":
        fetch(*sys.argv[2:3])
    elif cmd == "peek":
        peek(*sys.argv[2:3])
    elif cmd == "pstats":
        pstats(*sys.argv[2:3])
    elif cmd == "pprobe":
        pprobe(*sys.argv[2:4])
    elif cmd == "jsapi":
        jsapi(*sys.argv[2:3])
    elif cmd == "ai":
        ai(*sys.argv[2:3])
    elif cmd == "chart":
        chart()
    elif cmd == "players":
        players()
    elif cmd == "upsets":
        upsets()
    elif cmd == "exam":
        exam_run(*sys.argv[2:3])
    else:
        print(__doc__)
