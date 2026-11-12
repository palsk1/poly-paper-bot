#!/usr/bin/env python3
"""Post-count markets ("Will Elon Musk post 90-114 tweets from ... to ...?"): a counting model vs Polymarket's price.

  python3 tweets.py peek     what the counter site (xtracker, the settle source) gives us
"""
import json
import sys
import urllib.request

import bot

X = "https://xtracker.polymarket.com/api"


def raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def peek():
    urls = [f"{X}/users", f"{X}/users/elonmusk", f"{X}/users/elonmusk?platform=X", f"{X}/trackings", f"{X}/trackings?activeOnly=false",
            f"{X}/users/elonmusk/trackings", f"{X}/users/elonmusk/posts?startDate=2026-11-01&endDate=2026-11-03",
            f"{X}/users/elonmusk/posts?startDate=2026-03-01T00:00:00.000Z&endDate=2026-03-02T00:00:00.000Z",
            f"{X}/users/elonmusk/posts", f"{X}/metrics/elonmusk?type=daily&startDate=2026-03-01&endDate=2026-03-10",
            f"{X}/posts?handle=elonmusk&startDate=2026-11-01&endDate=2026-11-02", "https://xtracker.polymarket.com/"]
    seen = {}
    for u in urls:
        try:
            t = raw(u)
            print(f"\n== {u}\n   {len(t)} chars: {t[:1500]}", flush=True)
            seen[u] = t
        except Exception as e:
            print(f"\n== {u}\n   FAILED {str(e)[:200]}", flush=True)
    # follow ids found in the answers
    try:
        d = json.loads(seen.get(f"{X}/users/elonmusk") or "{}")
        d = d.get("data", d)
        uid = d.get("id")
        tr = d.get("trackings") or []
        print("\nuser id", uid, "trackings", len(tr), json.dumps(tr[:3])[:800])
        for u in ([f"{X}/metrics/{uid}?type=daily&startDate=2026-03-01&endDate=2026-03-10",
                   f"{X}/metrics/{uid}?type=hourly&startDate=2026-03-01&endDate=2026-03-03"] if uid else []) + \
                 [f"{X}/trackings/{t.get('id')}?includeStats=true" for t in tr[:2]]:
            try:
                t = raw(u)
                print(f"\n== {u}\n   {len(t)} chars: {t[:2500]}", flush=True)
            except Exception as e:
                print(f"\n== {u}\n   FAILED {str(e)[:200]}", flush=True)
    except Exception as e:
        print("follow failed", e)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek}.get(cmd, lambda: sys.exit(f"unknown command {cmd}"))()
