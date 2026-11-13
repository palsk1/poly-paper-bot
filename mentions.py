#!/usr/bin/env python3
"""Mention markets ("Will Trump say 'Tariff' during ...?"): a word-history model vs Polymarket's price.

  python3 mentions.py peek     how Polymarket tags these markets, how many there are
  python3 mentions.py fetch    every finished mention market + real trades -> bt_cache/men/
  python3 mentions.py run      the test -> backtest/mentions.md
"""
import collections
import concurrent.futures as cf
import hashlib
import json
import math
import os
import re
import sys
import time

import backtest as bt
import bot
import btcheck

CACHE = os.path.join(bt.CACHE, "men")
G = bt.G
WORKERS = 8
T0 = time.time()
BUDGET_MIN = float(os.environ.get("MEN_BUDGET_MIN", "150"))
TAGS = ("mentions", "mention-markets")


def peek():
    tests = []
    for lim in (5, 20, 50, 100):
        tests.append((f"{G}/events", {"tag_slug": "mention-markets", "closed": "true", "limit": lim}))
    tests += [(f"{G}/events", {"tag_slug": "mention-markets", "closed": "true", "limit": 20, "offset": 20}),
              (f"{G}/events", {"tag_slug": "mention-markets", "closed": "false", "limit": 100}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20, "order": "endDate", "ascending": "false"}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20, "end_date_min": "2026-10-01T00:00:00Z", "end_date_max": "2026-10-03T00:00:00Z"}),
              (f"{G}/events/keyset", {"tag_slug": "mention-markets", "closed": "true", "limit": 20}),
              (f"{G}/events/keyset", {"tag_id": 100343, "closed": "true", "limit": 20}),
              (f"{G}/events/keyset", {"tag_id": 100343, "closed": "true", "limit": 20, "end_date_min": "2026-10-01T00:00:00Z", "end_date_max": "2026-10-03T00:00:00Z"}),
              (f"{G}/events/pagination", {"tag_slug": "mention-markets", "closed": "true", "limit": 20}),
              (f"{G}/markets", {"tag_id": 100343, "closed": "true", "limit": 100}),
              (f"{G}/markets/keyset", {"tag_id": 100343, "closed": "true", "limit": 100}),
              (f"{G}/markets", {"tag_id": 100343, "closed": "true", "limit": 100, "offset": 100, "order": "endDate", "ascending": "true"})]
    for u, p in tests:
        try:
            r = bot.http_json(u, p)
            key = "events" if "/events" in u else "markets"
            rows = bot.envelope_rows(r, key, "data")
            print(f"\n== {u} {p}\n   {len(rows)} rows, keys {list(r.keys())[:8] if isinstance(r, dict) else 'list'}", flush=True)
            for e in rows[:3]:
                if key == "events":
                    print("   ", e.get("id"), e.get("slug"), e.get("endDate"), "markets", len(e.get("markets") or []),
                          "tags", [t.get("slug") for t in e.get("tags") or []][:6], "series", [s.get("slug") for s in e.get("series") or []])
                    for m in (e.get("markets") or [])[:1]:
                        print("       ", m.get("id"), m.get("question"), m.get("outcomePrices"), m.get("volumeNum"), m.get("conditionId"), m.get("endDate"), m.get("closedTime"))
                        print("        desc:", str(m.get("description"))[:300].replace("\n", " "))
                else:
                    print("   ", e.get("id"), e.get("question"), e.get("endDate"), e.get("outcomePrices"), e.get("volumeNum"),
                          [x.get("slug") for x in e.get("events") or []])
        except Exception as e:
            print(f"\n== {u} {p}\n   FAILED {str(e)[:200]}", flush=True)


def slim(e, m):
    m = dict(m)
    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
    s = bt.slim_market(m)
    s["cid"] = m.get("conditionId")
    s["title"] = e.get("title")
    s["series"] = [x.get("slug") for x in e.get("series") or [] if isinstance(x, dict)]
    s["ev_start"] = e.get("startDate") or e.get("creationDate")
    s["desc"] = str(m.get("description") or "")[:600]
    s["item"] = m.get("groupItemTitle")
    return s


def pages():
    """Every finished event carrying the Mentions tag. Tries the listing styles Gamma has, keeps the first that answers."""
    tries = [("keyset", {"tag_id": 100343}), ("offset", {"tag_id": 100343})]   # more than 50 a page answers HTTP 406
    for kind, base in tries:
        out, cur, off, bad = [], None, 0, 0
        for _ in range(6000):
            p = dict(base, closed="true", limit=50)
            if kind == "keyset" and cur:
                p["after_cursor"] = cur
            if kind == "offset":
                p["offset"] = off
            try:
                r = bot.http_json(f"{G}/events/keyset" if kind == "keyset" else f"{G}/events", p)
            except Exception as e:
                bad += 1
                print(f"  {kind} {base} failed: {str(e)[:120]}", flush=True)
                if bad > 3 or not out:
                    break
                time.sleep(3)
                continue
            rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
            if not rows:
                break
            out += rows
            off += 50
            cur = r.get("next_cursor") if isinstance(r, dict) else None
            if len(out) % 2000 == 0:
                print(f"  {kind} {base}: {len(out)} events ({(time.time() - T0) / 60:.0f} min)", flush=True)
            if kind == "keyset" and not cur:
                break
            if len(out) > 120000:
                break
        tagged = sum(1 for e in out if any((t.get("slug") == "mention-markets") for t in e.get("tags") or [] if isinstance(t, dict)))
        print(f"{kind} {base}: {len(out)} events, {tagged} carry the tag", flush=True)
        if len(out) >= 200:
            if tagged and tagged < len(out):
                out = [e for e in out if any((t.get("slug") == "mention-markets") for t in e.get("tags") or [] if isinstance(t, dict))]
            return out
    return []


def fetch():
    """Every finished mention market (any size, back to the start) and the real trades of the ones before the holdout."""
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    mpath = os.path.join(CACHE, "markets.json.gz")
    ms = {}
    evs = pages()
    fam = collections.Counter()
    for e in evs:
        fam[re.sub(r"[-0-9]+$", "", re.sub(r"\d+", "", str(e.get("slug"))))[:40]] += 1
        for m in e.get("markets") or []:
            if isinstance(m, dict):
                s = slim(e, m)
                if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                    ms[s["id"]] = s
    ends = sorted(m["end"] for m in ms.values())
    print(f"events {len(evs)}, markets {len(ms)}, ends {time.strftime('%Y-%m-%d', time.gmtime(ends[0])) if ends else '-'} .. "
          f"{time.strftime('%Y-%m-%d', time.gmtime(ends[-1])) if ends else '-'}", flush=True)
    print("biggest families:", fam.most_common(80), flush=True)
    if not ms:
        return
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}   # the holdout stays unseen until 21 Dec
    bt.wjson(mpath, ms)
    want = [m for m in ms.values() if m["end"] < cut and m.get("closed") and (m.get("vol") or 0) >= 200]
    want.sort(key=lambda m: order_key(m["ev_slug"]))
    print(f"markets: {len(ms)}, before the holdout with $200+ traded: {len(want)}", flush=True)
    n_sh = (len(want) + SHARD - 1) // SHARD
    for i in range(n_sh):
        path = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if os.path.exists(path):
            continue
        chunk = want[i * SHARD:(i + 1) * SHARD]
        out = {}
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                if r is not None:
                    out[mid] = r
        bt.wjson(path, out)
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), "
              f"cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break


SHARD = 1000


def order_key(ev):
    return hashlib.md5(("men" + str(ev)).encode()).hexdigest()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch}[cmd]()
