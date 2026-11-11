#!/usr/bin/env python3
"""CS2 match bets vs public team ratings (2026-11-11, Jan's ask: "compare cs2 and hltv"). Research only.

PAPER ONLY. Reads data, never trades, never writes state/.

    python3 cs2.py sources       # probe `cs2_sources`: which rating sites a robot can read at all
    python3 cs2.py fetch         # probe `cs2_fetch`: Valve standings + bo3.gg results -> bt_cache/cs2/ (price store)
    python3 cs2.py chart         # offline: ratings vs prices and the rule grid on chart prices (Polymarket sports cache)
    python3 cs2.py exam          # probe `cs2_exam`: the picked rules at REAL buy prices (trade tape), shared exam

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
        for k in re.finditer(r"prediction", t):
            seg = t[max(0, k.start() - 200):k.start() + 200]
            if re.search(r"/v\d|api|\$fetch|useFetch|get\(|url", seg) and "predictions\"" not in seg[:5]:
                print("  JS", u, "::", re.sub(r"\s+", " ", seg))
    for pth, n in paths.most_common(80):
        print(f"  {n:3}  {pth}")
    for u in ["matches/%s/predictions" % slug, "predictions/matches/%s" % slug, "matches/%s/ai_predictions" % slug,
              "ai/predictions?filter[match_slug][eq]=%s" % slug, "matches/%s/forecast" % slug, "games/predictions",
              "match_predictions?filter[match_predictions.match_slug][eq]=%s" % slug, "predictions?page[limit]=2",
              "articles?filter[articles.type][eq]=prediction&page[limit]=2", "predictions/matches?page[limit]=2",
              "matches/%s/bet_updates" % slug, "bet_updates?filter[bet_updates.match_id][eq]=133431"]:
        for base in ("https://api.bo3.gg/api/v1/", "https://api.bo3.gg/api/v2/"):
            st, b = get(base + u)
            print(st, len(b), base + u, b[:300].decode("utf-8", "replace") if st == 200 else "")


# ======================================================================== the test
ROOT = os.path.dirname(os.path.abspath(__file__))
REL = "https://github.com/palsk1/poly-paper-bot/releases/download/price-store/"
FILES = ["bt_cache/sports/markets.json.gz", "bt_cache/sports/hist.json.gz", "bt_cache/cs2/bo3_matches.json.gz",
         "bt_cache/cs2/bo3_teams.json.gz", "bt_cache/cs2/valve.json.gz"]
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
        if not f or max(f) < 0.99 or m["gst"] > HOLD - 6 * H or (m.get("end") or 0) >= HOLD:
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
            r.update(tier=x.get("tier"), agree=(x["winner_team_id"] == ia) == (r["w"] == 0), na=na, nb=nb,
                     elo=1 / (1 + 10 ** ((rb - ra) / 400)))
        d = dt.datetime.fromtimestamp(r["gst"], dt.timezone.utc).strftime("%Y-%m-%d")
        i = bisect.bisect_right(vd, d) - 1
        va, vb = (vmap[vd[i]].get(A), vmap[vd[i]].get(B)) if i >= 0 else (None, None)
        r["valve"] = (va[0], vb[0]) if va and vb else None
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
]
TRIES = 50     # versions looked at in this dig (rating gaps x4 x2, bands, tiers x4 x4, timing, drift, volume, months)


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
    rows = build()
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


def exam_run():
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
    elif cmd == "jsapi":
        jsapi(*sys.argv[2:3])
    elif cmd == "chart":
        chart()
    elif cmd == "exam":
        exam_run()
    else:
        print(__doc__)
