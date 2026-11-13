#!/usr/bin/env python3
"""Box office markets ("Will 'Movie' 3rd weekend box office be between 20m and 25m?") vs the daily ticket numbers.

  python3 boxoffice.py peek     can we read the daily numbers (Box Office Mojo / The Numbers) from here?
  python3 boxoffice.py fetch    every finished box office market + real trades, and the daily numbers -> bt_cache/bo/
"""
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import html
import os
import re
import sys
import time
import urllib.request

import backtest as bt
import bot

G = bt.G
CACHE = os.path.join(bt.CACHE, "bo")
TAG = 51                      # Gamma tag "Box Office"
SHARD = 400
T0 = time.time()
BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def raw(url, ua=BROWSER):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*", "Accept-Language": "en-US,en;q=0.8",
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
        return b.decode("utf-8", "replace")


def money(s):
    s = re.sub(r"[^0-9.]", "", s or "")
    return float(s) if s else None


def mojo_day(day):
    """Box Office Mojo's table for one day: [(title, dollars that day, theaters, dollars so far, days out)]."""
    t = raw(f"https://www.boxofficemojo.com/date/{day}/")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        td = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(td) >= 10 and td[3].startswith("$"):
            rows.append([td[2], money(td[3]), money(td[6]), money(td[8]), money(td[9])])
    return rows


def peek():
    for u in ("https://www.boxofficemojo.com/date/2026-10-10/", "https://www.boxofficemojo.com/weekend/2026W41/",
              "https://www.the-numbers.com/box-office-chart/daily/2026/10/10", "https://www.the-numbers.com/movie/Avatar-Fire-and-Ash-(2025)#tab=box-office"):
        for ua in (BROWSER, bot.UA):
            try:
                t = raw(u, ua)
                print(f"\n== {u} [{ua[:12]}] {len(t)} chars, tables {t.count('<table')}, rows {t.count('<tr')}", flush=True)
                txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S))))
                i = txt.find("Daily")
                print("   ", txt[max(0, i - 100):i + 900])
                break
            except Exception as e:
                print(f"\n== {u} [{ua[:12]}] FAILED {str(e)[:150]}", flush=True)
    try:
        r = mojo_day("2026-10-10")
        print("\nmojo_day rows", len(r), r[:8])
    except Exception as e:
        print("mojo_day failed", str(e)[:200])


def pages(closed="true"):
    out, cur = [], None
    for _ in range(400):
        p = {"tag_id": TAG, "closed": closed, "limit": 50}
        if cur:
            p["after_cursor"] = cur
        r = bot.http_json(f"{G}/events/keyset", p)
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        out += rows
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur:
            break
    return out


def slim(e, m):
    m = dict(m)
    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
    s = bt.slim_market(m)
    s["cid"] = m.get("conditionId")
    s["title"] = e.get("title")
    s["desc"] = str(m.get("description") or "")[:1500]
    s["item"] = m.get("groupItemTitle")
    return s


def fetch():
    import btcheck
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    ms = {}
    for e in pages():
        for m in e.get("markets") or []:
            if isinstance(m, dict):
                s = slim(e, m)
                if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                    ms[s["id"]] = s
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    n_all = len(ms)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}          # the holdout stays unseen until 21 Dec
    bt.wjson(os.path.join(CACHE, "markets.json.gz"), ms)
    print(f"box office markets {n_all}, before the holdout {len(ms)}, events {len({m['ev_slug'] for m in ms.values()})}", flush=True)
    want = sorted((m for m in ms.values() if m.get("closed") and (m.get("vol") or 0) >= 200),
                  key=lambda m: hashlib.md5(("bo" + m["ev_slug"]).encode()).hexdigest())
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
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)
    # the daily ticket numbers, every day from a year before the first market
    dpath = os.path.join(CACHE, "daily.json.gz")
    days = bt.rjson(dpath, {}) or {}
    first = min(m["end"] for m in ms.values() if m["end"] > 1700000000)
    d = dt.date.fromtimestamp(max(first, time.time() - 900 * 86400)) - dt.timedelta(days=400)
    todo = []
    while d < dt.date.today() - dt.timedelta(days=2):
        if d.isoformat() not in days:
            todo.append(d.isoformat())
        d += dt.timedelta(days=1)
    print(f"daily numbers: have {len(days)} days, need {len(todo)} more", flush=True)
    bad = 0
    with cf.ThreadPoolExecutor(4) as ex:
        def one(day):
            for k in range(3):
                try:
                    return day, mojo_day(day)
                except Exception as e:
                    err = e
                    time.sleep(2 + 3 * k)
            return day, str(err)[:100]
        for n, (day, rows) in enumerate(ex.map(one, todo)):
            if isinstance(rows, str) or not rows:
                bad += 1
                if bad <= 5:
                    print("   day failed", day, rows)
                continue
            days[day] = rows
            if n % 200 == 199:
                bt.wjson(dpath, days)
                print(f"   {n + 1}/{len(todo)} days ({(time.time() - T0) / 60:.0f} min), failed {bad}", flush=True)
    bt.wjson(dpath, days)
    print(f"daily numbers: {len(days)} days saved, {bad} failed")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch}[cmd]()
