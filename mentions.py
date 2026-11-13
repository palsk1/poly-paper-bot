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
    for u, p in [(f"{G}/tags/slug/mentions", {}), (f"{G}/tags/slug/mention-markets", {}), (f"{G}/tags", {"limit": 5}),
                 (f"{G}/events", {"tag_slug": "mentions", "closed": "true", "limit": 3}),
                 (f"{G}/events", {"tag_slug": "mentions", "closed": "false", "limit": 3}),
                 (f"{G}/events/keyset", {"tag_slug": "mentions", "closed": "true", "limit": 3}),
                 (f"{G}/events/keyset", {"tag_slug": "mentions", "closed": "true", "limit": 3, "order": "endDate", "ascending": "true"})]:
        try:
            r = bot.http_json(u, p)
            rows = bot.envelope_rows(r, "events", "data") if "events" in u else None
            if rows:
                print(f"\n== {u} {p}\n   {len(rows)} rows, keys {list(r.keys()) if isinstance(r, dict) else 'list'}")
                for e in rows[:3]:
                    print("   ", e.get("id"), e.get("slug"), e.get("endDate"), "markets", len(e.get("markets") or []),
                          "tags", [t.get("slug") for t in e.get("tags") or []], "series", [s.get("slug") for s in e.get("series") or []])
                    for m in (e.get("markets") or [])[:2]:
                        print("       ", m.get("id"), m.get("question"), m.get("outcomePrices"), m.get("volumeNum"), m.get("conditionId"), m.get("endDate"), m.get("closedTime"))
                        print("        desc:", str(m.get("description"))[:400].replace("\n", " "))
            else:
                print(f"\n== {u} {p}\n   {str(r)[:600]}")
        except Exception as e:
            print(f"\n== {u} {p}\n   FAILED {str(e)[:200]}")
    # how many: page through closed events with the tag, 100 at a time, count only
    for tag in TAGS:
        n = nm = 0
        first = last = None
        fam = collections.Counter()
        off = 0
        while off < 60000:
            try:
                r = bot.http_json(f"{G}/events", {"tag_slug": tag, "closed": "true", "limit": 100, "offset": off, "order": "endDate", "ascending": "true"})
            except Exception as e:
                print("  page failed", off, str(e)[:120])
                break
            rows = bot.envelope_rows(r, "events", "data")
            if not rows:
                break
            for e in rows:
                n += 1
                nm += len(e.get("markets") or [])
                d = str(e.get("endDate"))[:7]
                first = first or d
                last = d
                fam[re.sub(r"[-0-9]+$", "", re.sub(r"\d+", "", str(e.get("slug"))))[:38]] += 1
            off += 100
        print(f"\ntag {tag}: {n} finished events, {nm} markets, months {first} .. {last}")
        print("  biggest families:", fam.most_common(60))


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


def fetch():
    """Every finished mention market (any size, back to the start) and the real trades of the ones before the holdout."""
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    mpath = os.path.join(CACHE, "markets.json.gz")
    ms = {}
    for tag in TAGS:
        off = 0
        while off < 80000:
            try:
                r = bot.http_json(f"{G}/events", {"tag_slug": tag, "closed": "true", "limit": 100, "offset": off, "order": "endDate", "ascending": "true"})
            except Exception as e:
                print("  page failed, once more", off, str(e)[:120], flush=True)
                time.sleep(3)
                try:
                    r = bot.http_json(f"{G}/events", {"tag_slug": tag, "closed": "true", "limit": 100, "offset": off, "order": "endDate", "ascending": "true"})
                except Exception:
                    break
            rows = bot.envelope_rows(r, "events", "data")
            if not rows:
                break
            for e in rows:
                for m in e.get("markets") or []:
                    if isinstance(m, dict):
                        s = slim(e, m)
                        if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                            ms[s["id"]] = s
            off += 100
            if off % 2000 == 0:
                print(f"  {tag}: {off} events read, {len(ms)} markets ({(time.time() - T0) / 60:.0f} min)", flush=True)
        print(f"tag {tag}: {len(ms)} markets so far", flush=True)
    bt.wjson(mpath, ms)
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
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
