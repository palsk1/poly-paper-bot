#!/usr/bin/env python3
"""Earthquake count markets on Polymarket ("how many 6.5+ earthquakes this week?") against a plain counting model.

Research only, paper only. Big earthquakes come at a steady average pace, so "count so far + the usual pace for the
time left" gives a fair chance for every bracket. Does Polymarket's price match it?

  python3 quakes.py fetch    markets + real trades + the USGS earthquake list -> bt_cache/qk/
  python3 quakes.py run      the test -> backtest/quakes.md
"""
import collections
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import time

import backtest as bt
import bot
import boxoffice

TAG = 103038
CACHE = os.path.join(bt.CACHE, "qk")
SHARD = 500
USGS = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def pages(closed="true"):
    out, cur = [], None
    for _ in range(100):
        p = {"tag_id": TAG, "closed": closed, "limit": 50}
        if cur:
            p["after_cursor"] = cur
        r = bot.http_json(f"{boxoffice.G}/events/keyset", p)
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        out += rows
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur:
            break
    return out


def usgs(start, end, minmag=4.5):
    """[[unix time, magnitude, id, last updated unix]] for one stretch, straight from the USGS catalog."""
    url = f"{USGS}?format=csv&starttime={start}&endtime={end}&minmagnitude={minmag}&orderby=time-asc&limit=20000"
    txt = boxoffice.raw(url)
    rows = []
    lines = txt.strip().split("\n")
    head = lines[0].split(",")
    it, im, ii, iu = head.index("time"), head.index("mag"), head.index("id"), head.index("updated")
    import csv
    for r in csv.reader(lines[1:]):
        try:
            t = bot.parse_iso(r[it]).timestamp()
            u = bot.parse_iso(r[iu]).timestamp()
            rows.append([int(t), float(r[im]), r[ii], int(u)])
        except Exception:
            pass
    return rows


def fetch():
    import btcheck
    import optfair
    T0 = time.time()
    os.makedirs(CACHE, exist_ok=True)
    ms = {}
    for e in pages():
        for m in e.get("markets") or []:
            if not isinstance(m, dict):
                continue
            m = dict(m)
            m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
            s = bt.slim_market(m)
            s["cid"] = m.get("conditionId")
            s["title"] = e.get("title")
            s["desc"] = str(m.get("description") or "")[:1200]
            s["item"] = m.get("groupItemTitle")
            if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                ms[s["id"]] = s
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    n_all = len(ms)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}          # the holdout stays unseen until 21 Dec
    bt.wjson(os.path.join(CACHE, "markets.json.gz"), ms)
    print(f"earthquake markets {n_all}, before the holdout {len(ms)}, events {len({m['ev_slug'] for m in ms.values()})}", flush=True)
    cat, d = [], dt.date(2021, 1, 1)
    while d < dt.date.today():
        e = min(dt.date(d.year + (d.month > 6), 1 if d.month > 6 else 7, 1), dt.date.today() + dt.timedelta(days=1))
        for k in range(3):
            try:
                rows = usgs(d.isoformat(), e.isoformat())
                break
            except Exception as ex:
                rows = None
                print("   usgs failed", d, str(ex)[:100], flush=True)
                time.sleep(5)
        if rows:
            cat += rows
            print(f"  usgs {d}..{e}: {len(rows)} quakes of 4.5+", flush=True)
        d = e
        time.sleep(1)
    bt.wjson(os.path.join(CACHE, "usgs.json.gz"), cat)
    want = sorted((m for m in ms.values() if m.get("closed") and (m.get("vol") or 0) >= 200),
                  key=lambda m: hashlib.md5(("qk" + m["ev_slug"]).encode()).hexdigest())
    n_sh = (len(want) + SHARD - 1) // SHARD
    for i in range(n_sh):
        path = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if os.path.exists(path):
            continue
        chunk = want[i * SHARD:(i + 1) * SHARD]
        out = {}
        with cf.ThreadPoolExecutor(8) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                if r is not None:
                    out[mid] = r
        bt.wjson(path, out)
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min)", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"fetch": fetch}[cmd]()
