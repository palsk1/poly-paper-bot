#!/usr/bin/env python3
"""'What will Trump / Elon post this week' markets against the words they really post (2026-11-15). Research only.

PAPER ONLY. Reads public history, never trades, never writes state/.

The outside number: every post of the account with its text (Polymarket's own counter site xtracker). For each
listed word we count in how many of the earlier weeks it really showed up, and compare that with the price.

    python3 postwords.py fetch    # probe pw_fetch: every post with its text -> bt_cache/pw/posts_<handle>.json.gz
    python3 postwords.py run      # report backtest/postwords.md (markets and trades come from mentions.py's data)
"""
import collections
import gzip
import json
import os
import sys
import time

import tweets

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "pw")
HANDLES = ("realDonaldTrump", "elonmusk")
X = tweets.X


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def fetch():
    for h in HANDLES:
        path = os.path.join(CACHE, f"posts_{h}.json.gz")
        seen = rj(path, {}) or {}
        a, now, shown = tweets.ts("2025-06-01T00:00:00"), int(time.time()), 0
        if seen:
            a = max(a, max(v["t"] for v in seen.values()) - 3 * 86400)
        while a < now:
            b = min(a + 10 * 86400, now + 86400)
            f = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))
            try:
                d = json.loads(tweets.raw(f"{X}/users/{h}/posts?startDate={f(a)}&endDate={f(b)}")).get("data") or []
            except Exception as e:
                print("  posts failed", h, f(a), str(e)[:120], flush=True)
                d = []
            for p in d:
                if shown < 3:
                    shown += 1
                    print("  sample", h, json.dumps(p)[:900], flush=True)
                try:
                    seen[str(p["id"])] = {"t": tweets.ts(p["createdAt"]), "seen": tweets.ts(p["importedAt"]) if p.get("importedAt") else None,
                                          "x": {k: v for k, v in p.items() if k not in ("createdAt", "importedAt", "id", "userId", "user")}}
                except Exception as e:
                    print("  bad post", str(e)[:80], flush=True)
            a = b
        wj(path, seen)
        ts_ = sorted(v["t"] for v in seen.values())
        mon = collections.Counter(time.strftime("%Y-%m", time.gmtime(t)) for t in ts_)
        print(f"{h}: {len(seen)} posts, by month {sorted(mon.items())}", flush=True)
        keys = collections.Counter(k for v in seen.values() for k in v["x"])
        print("  fields:", keys.most_common(20), flush=True)


if __name__ == "__main__":
    {"fetch": fetch}[sys.argv[1] if len(sys.argv) > 1 else "fetch"]()
