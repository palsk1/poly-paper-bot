#!/usr/bin/env python3
"""Treasury yield "how high / how low" bets (Polymarket tag `treasuries`, started Sep-Nov 2026) vs a simple touch model
on the free yield history. backtest/tyield.md. PAPER ONLY: reads public data, never trades, never writes state/.

  python3 tyield.py fetch     (probe nfx_tyield_fetch: every event of the families with rules, markets, real trades
                               in 5-minute steps; FRED DGS2/5/10/30 + Treasury.gov par curve; Kalshi rate/Treasury
                               series with hourly bid/ask + trades -> bt_cache/nf/ty/)
  python3 tyield.py run       (offline, after `python3 store.py pull bt_cache/nf`: model vs price, rules, exam)
"""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

G = bot.GAMMA
UTC = dt.timezone.utc
DAY = 86400
CACHE = os.path.join(bot.ROOT, "bt_cache", "nf", "ty")
BUA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TENORS = {"2": "DGS2", "5": "DGS5", "10": "DGS10", "30": "DGS30"}


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        json.dump(obj, f)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def raw(url, timeout=60):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": BUA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", None), str(e).encode()


def its(s):
    try:
        return int(dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp())
    except Exception:
        return 0


# ================================================================ fetch
def tag_events(slug):
    import families
    try:
        tid = bot.http_json(f"{G}/tags/slug/{slug}").get("id")
    except Exception as e:
        print(f"tag {slug}: none ({str(e)[:60]})", flush=True)
        return []
    out = []
    for closed in ("true", "false"):
        got = families.pages(tid, closed, max_pages=200)
        print(f"tag {slug} id {tid} closed={closed}: {len(got)} events", flush=True)
        out += got
    return out


def series_events(slug):
    try:
        r = bot.http_json(f"{G}/series", {"slug": slug})
    except Exception as e:
        print("series", slug, "failed", str(e)[:80])
        return []
    rows = r if isinstance(r, list) else bot.envelope_rows(r, "series", "data")
    evs = []
    for s in rows or []:
        for e in s.get("events") or []:
            evs.append(e)
    print(f"series {slug}: {len(rows or [])} series, {len(evs)} events", flush=True)
    return evs


def full_event(eid):
    try:
        return bot.http_json(f"{G}/events/{eid}")
    except Exception:
        return None


def fetch():
    import backtest as bt
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    # ---- yields
    yp = os.path.join(CACHE, "fred.json.gz")
    Y = {}
    for ten, sid in TENORS.items():
        code, body = raw(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        rows = {}
        if code == 200:
            for r in csv.reader(io.StringIO(body.decode("utf-8", "replace"))):
                if len(r) == 2 and re.match(r"\d{4}-", r[0]):
                    try:
                        rows[r[0]] = float(r[1])
                    except ValueError:
                        pass
        Y[ten] = rows
        print("FRED", sid, code, len(rows), "last", max(rows) if rows else "-", flush=True)
    wj(yp, Y)
    tp_ = os.path.join(CACHE, "ust_par.json.gz")
    par = {}
    for y in (2024, 2025, 2026):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
               f"{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv")
        code, body = raw(url)
        if code == 200:
            rows = list(csv.DictReader(io.StringIO(body.decode("utf-8", "replace"))))
            par[str(y)] = rows
            print("treasury par", y, len(rows), (rows[0] if rows else {}), flush=True)
        else:
            print("treasury par", y, code, body[:120], flush=True)
    wj(tp_, par)
    # ---- Polymarket events
    evs = {}
    for slug in ("treasuries", "treasury", "bonds", "yields", "interest-rates"):
        for e in tag_events(slug):
            evs[str(e.get("id"))] = e
    for ten in ("2", "5", "10", "30"):
        for hl in ("high", "low"):
            for e in series_events(f"how-{hl}-{ten}-year-treasury"):
                evs.setdefault(str(e.get("id")), e)
            for e in series_events(f"how-{hl}-will-{ten}-year-treasury-yield-go"):
                evs.setdefault(str(e.get("id")), e)
    keep = {}
    for eid, e in evs.items():
        t = (str(e.get("title")) + " " + str(e.get("slug"))).lower()
        if "treasury" in t or "yield" in t:
            keep[eid] = e
    print("treasury/yield events", len(keep), "of", len(evs), flush=True)
    ms = {}
    for eid, e in keep.items():
        if not e.get("markets") or not (e.get("markets") or [{}])[0].get("description"):
            e = full_event(eid) or e
        for m in e.get("markets") or []:
            if not isinstance(m, dict):
                continue
            m = dict(m)
            m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
            s = bt.slim_market(m)
            s["cid"] = m.get("conditionId")
            s["title"] = e.get("title")
            s["eslug"] = e.get("slug")
            s["series"] = [x.get("slug") for x in e.get("series") or []]
            s["desc"] = str(m.get("description") or e.get("description") or "")[:2500]
            s["item"] = m.get("groupItemTitle")
            s["tags"] = [x.get("slug") for x in e.get("tags") or []]
            s["fee_raw"] = [m.get("feesEnabled"), m.get("feeSchedule"), m.get("makerBaseFee"), m.get("takerBaseFee")]
            ms[s["id"]] = s
    wj(os.path.join(CACHE, "markets.json.gz"), ms)
    fam = collections.Counter(re.sub(r"\d", "#", str(m["eslug"])) for m in ms.values())
    print("markets", len(ms), "closed", sum(m["closed"] for m in ms.values()), flush=True)
    for f, n in fam.most_common(40):
        print(f"  {n:4d}  {f}")
    for eslug in sorted({m["eslug"] for m in ms.values()})[:200]:
        mm = [m for m in ms.values() if m["eslug"] == eslug]
        print(f"EV {eslug} | {mm[0]['title']} | {len(mm)} rungs closed {sum(m['closed'] for m in mm)} vol "
              f"{sum(m['vol'] or 0 for m in mm):.0f} end {dt.datetime.utcfromtimestamp(mm[0]['end'] or 0).date()} "
              f"fee {mm[0]['fee']} {mm[0]['fee_raw']}")
    shown = set()
    for m in ms.values():
        f = re.sub(r"\d", "#", str(m["eslug"]))
        if f in shown:
            continue
        shown.add(f)
        print(f"\nRULES {m['eslug']} / {m['q']}\n  {m['desc'][:1400]}")
    # ---- trades
    tpath = os.path.join(CACHE, "tapes.json.gz")
    tp = rj(tpath, {}) or {}
    todo = [m for m in ms.values() if m.get("cid") and (m.get("vol") or 0) >= 50 and
            (m["id"] not in tp or not m["closed"] or not tp[m["id"]].get("closed"))]
    print("tapes to fetch", len(todo), flush=True)
    with ThreadPoolExecutor(8) as ex:
        for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in todo]):
            if r is not None:
                r["closed"] = ms[mid]["closed"]
                tp[mid] = r
    wj(tpath, tp)
    print("tapes", len(tp), "trades", sum(v["n"] for v in tp.values()), "cut", sum(v["cut"] for v in tp.values()), flush=True)
    # ---- Kalshi
    kfetch()


def kfetch():
    import yesno
    try:
        ser = yesno.kget("/series", {}).get("series") or []
    except Exception as e:
        print("kalshi series failed", e)
        return
    hit = []
    for s in ser:
        t = (str(s.get("ticker")) + " " + str(s.get("title"))).lower()
        if re.search(r"treasur|yield|tnote|10y|2y|30y|bond|t-note|tbill|mortgage", t):
            hit.append(s)
    print("\nKalshi series matching treasury/yield/bond:", len(hit), flush=True)
    import kmentions as km
    import dates
    have = {}
    for s in hit:
        tk = s["ticker"]
        try:
            _, ok, n = km.series_markets(tk)
        except Exception as e:
            ok, n = {}, str(e)[:60]
        have[tk] = ok
        print(f"  {tk:22s} {str(s.get('title'))[:70]:70s} freq {s.get('frequency')} settled {len(ok)} "
              f"src {[y.get('url') for y in (s.get('settlement_sources') or []) if isinstance(y, dict)][:2]}", flush=True)
    wj(os.path.join(CACHE, "kmarkets.json.gz"), have)
    t0 = time.time()
    for tk, ok in have.items():
        mm = [m for m in ok.values() if (m.get("vol") or 0) >= 200]
        if not mm:
            continue
        path = os.path.join(CACHE, f"ktapes_{tk}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in mm if m["t"] not in got]
        with ThreadPoolExecutor(6) as ex:
            for t, d in ex.map(dates.tape_one, todo):
                got[t] = d
        wj(path, got)
        print(f"  ktapes {tk}: {len(got)} ({time.time() - t0:.0f}s)", flush=True)
        if time.time() - t0 > 3 * 3600:
            break


# ================================================================ model + test (filled in after the first fetch)
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "fetch":
        fetch()
    elif cmd == "kfetch":
        kfetch()
    elif cmd == "run":
        run(*sys.argv[2:])
    else:
        print(__doc__)


def run(*a):
    print("not yet")


if __name__ == "__main__":
    main()
