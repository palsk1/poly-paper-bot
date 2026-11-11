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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sources":
        sources()
    else:
        print(__doc__)
