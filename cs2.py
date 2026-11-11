#!/usr/bin/env python3
"""CS2 match bets vs public team ratings (2026-11-11, Jan's ask: "compare cs2 and hltv"). Research only.

PAPER ONLY. Reads data, never trades, never writes state/.

    python3 cs2.py sources       # probe `cs2_sources`: which rating sites a robot can read at all
"""
import json
import re
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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sources":
        sources()
    elif cmd == "fetch":
        fetch(*sys.argv[2:3])
    else:
        print(__doc__)
