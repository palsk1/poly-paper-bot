#!/usr/bin/env python3
"""Post-count markets ("Will Elon Musk post 90-114 tweets from ... to ...?"): a counting model vs Polymarket's price.

  python3 tweets.py peek     what the counter site (xtracker, the settle source) gives us
  python3 tweets.py fetch    counter windows, post times and real trades -> bt_cache/tw/
"""
import calendar
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

import backtest as bt
import bot
import btcheck

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



# ================================================================ data
CACHE = os.path.join(bt.CACHE, "tw")
T0 = time.time()
BUDGET_MIN = float(os.environ.get("TW_MIN", "200"))
WORKERS = int(os.environ.get("TW_WORKERS", "8"))
NUM = r"(\d[\d,]*)"
UNIT = r"(?:Truth Social )?(?:tweets|posts|times)"


def bucket(q):
    """The count range in a market's title: (low, high) both included; high = 10**9 for "240+"."""
    n = lambda x: int(x.replace(",", ""))
    g = re.search(rf"(?:post|tweet|have) (?:between )?{NUM}\s*(?:-|–|to|and)\s*{NUM} {UNIT}", q)
    if g:
        return n(g.group(1)), n(g.group(2))
    g = re.search(rf"(?:post|tweet) (?:<|less than |fewer than |under ){NUM}", q)
    if g:
        return 0, n(g.group(1)) - 1
    g = re.search(rf"(?:post|tweet) {NUM}(?:\+| or more| or greater)", q)
    if g:
        return n(g.group(1)), 10 ** 9
    g = re.search(rf"(?:post|tweet) (?:more than |over |>){NUM}", q)
    if g:
        return n(g.group(1)) + 1, 10 ** 9
    return None


def pick_markets(markets):
    out = {}
    for m in markets.values():
        q = m.get("q") or ""
        if not re.search(r"^Will .+ (post|tweet|have) ", q) or not re.search(r"\b(tweets?|posts?|times)\b", q, re.I):
            continue
        b = bucket(q)
        if not b or not m.get("toks") or not m.get("ev_slug"):
            continue
        out[m["id"]] = dict(m, lo=b[0], hi=b[1])
    return out


def ts(iso):
    return int(calendar.timegm(time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")))


def order_key(ev):
    return hashlib.md5(("tw" + str(ev)).encode()).hexdigest()


def fetch():
    """Counter windows (trackings), every post's time (when posted, when the counter saw it; no text) and trade lists."""
    import ideas, informed, optfair
    os.makedirs(CACHE, exist_ok=True)
    tr = json.loads(raw(f"{X}/trackings?activeOnly=false"))["data"]
    rows, handles = [], {}
    for t in tr:
        u = t.get("user") or {}
        slug = (t.get("marketLink") or "").rstrip("/").split("/")[-1]
        if not slug or not u.get("handle"):
            continue
        rows.append({"id": t["id"], "handle": u["handle"], "platform": u.get("platform"), "title": t.get("title"),
                     "start": ts(t["startDate"]), "end": ts(t["endDate"]), "slug": slug})
        handles[u["handle"]] = u.get("platform")
    bt.wjson(os.path.join(CACHE, "trackings.json.gz"), rows)
    print(f"counter windows: {len(rows)}, accounts: {handles}", flush=True)
    posts = {}
    for h in handles:
        seen = {}
        day0, now = ts("2025-11-01T00:00:00"), int(time.time())
        a = day0
        while a < now:
            b = min(a + 20 * 86400, now + 86400)
            u = f"{X}/users/{h}/posts?startDate={time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(a))}&endDate={time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(b))}"
            try:
                d = json.loads(raw(u)).get("data") or []
            except Exception as e:
                print("  posts failed", h, str(e)[:100], flush=True)
                d = []
            for p in d:
                try:
                    seen[p["id"]] = [ts(p["createdAt"]), ts(p["importedAt"]) if p.get("importedAt") else ts(p["createdAt"])]
                except Exception:
                    pass
            a = b
        posts[h] = sorted(seen.values())
        v = posts[h]
        print(f"  {h}: {len(v)} posts, first {time.strftime('%Y-%m-%d', time.gmtime(v[0][0])) if v else '-'}, "
              f"last {time.strftime('%Y-%m-%d', time.gmtime(v[-1][0])) if v else '-'}", flush=True)
    bt.wjson(os.path.join(CACHE, "posts.json.gz"), posts)
    markets, _, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m.get("final")}
    slugs = {r["slug"] for r in rows}
    print(f"markets: {len(ms)}, events: {len({m['ev_slug'] for m in ms.values()})}, "
          f"with a counter window: {len({m['ev_slug'] for m in ms.values() if m['ev_slug'] in slugs})}", flush=True)
    path = os.path.join(CACHE, "tapes.json.gz")
    have = bt.rjson(path, {}) or {}
    todo = [k for k in ms if k not in have]
    for i in range(0, len(todo), 400):
        chunk = todo[i:i + 400]
        cids = informed.cids_for(chunk)
        jobs = [(ms[k], cids[k]) for k in chunk if cids.get(k)]
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for mid, r in ex.map(optfair.fetch_tape, jobs):
                if r is not None:
                    have[mid] = r
        bt.wjson(path, have)
        print(f"  tapes {len(have)}/{len(ms)} ({(time.time() - T0) / 60:.0f} min), cut short {sum(1 for r in have.values() if r['cut'])}", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break
    print(f"tapes saved: {len(have)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch}.get(cmd, lambda: sys.exit(f"unknown command {cmd}"))()
