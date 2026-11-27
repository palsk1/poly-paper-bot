#!/usr/bin/env python3
"""Polymarket GPU rental price bets vs the Ornn compute price index (27 Nov 2026).

  python3 gpurent.py fetch      # probe nfx_gpurent_fetch: every event of the six GPU rental series (open and closed),
                                # markets + rules text, every real trade (5-minute steps), and Ornn's free index history
                                # (trailing 3 months, daily) -> bt_cache/nf/gpu/
  python3 gpurent.py report     # offline: what settled, prices vs the index, the tests (exam.score)

Families (Gamma series slugs): b200-, b300-, h100-, h200-average-rental-price, rtx-6000-, rtx-5090-rental-price.
Settles on the Ornn Compute Price Index (OCPI), USD per GPU-hour, data.ornn.com. Free without a key: the latest value and
the trailing 3 months of daily settles (api.ornnai.com/api/gpu/<name>/index-history).
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot

G = bt.G
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "nf", "gpu")
SERIES = ["b200-average-rental-price", "b300-average-rental-price", "h100-average-rental-price",
          "h200-average-rental-price", "rtx-6000-rental-price", "rtx-5090-rental-price"]
GPUS = ["H100 SXM", "H200", "B200", "B300", "A100 SXM4", "RTX PRO 6000 WS", "RTX 5090", "RTX PRO 6000"]
ORNN = ["https://api.ornnai.com", "https://data.ornn.com/api/public-index", "https://index.ornn.com"]


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


def get(url, params=None):
    try:
        return bot.http_json(url, params, retries=2)
    except Exception as e:
        return {"_err": str(e)[:200]}


def events_of(slug):
    """Every event of one Gamma series, open and closed, tried three ways."""
    out = {}
    for closed in ("true", "false"):
        for p in ({"series_slug": slug}, {"slug_contains": slug}):
            off = 0
            for _ in range(40):
                r = get(f"{G}/events", dict(p, closed=closed, limit=50, offset=off))
                rows = [e for e in (r if isinstance(r, list) else bot.envelope_rows(r, "events", "data")) if isinstance(e, dict)]
                hit = 0
                for e in rows:
                    if any(isinstance(s, dict) and s.get("slug") == slug for s in e.get("series") or []) or \
                            slug.split("-")[0] in str(e.get("slug")):
                        out[str(e.get("id"))] = e
                        hit += 1
                if len(rows) < 50 or not hit:
                    break
                off += 50
    s = get(f"{G}/series", {"slug": slug})
    ser = s[0] if isinstance(s, list) and s else s if isinstance(s, dict) else {}
    ids = [str(e.get("id")) for e in ser.get("events") or [] if isinstance(e, dict)]
    for i in ids:
        if i not in out:
            e = get(f"{G}/events/{i}")
            if isinstance(e, dict) and e.get("id"):
                out[i] = e
    return out, len(ids)


def tag_events(tag):
    import families
    try:
        tid = bot.http_json(f"{G}/tags/slug/{tag}").get("id")
    except Exception:
        return []
    return families.pages(tid, "true") + families.pages(tid, "false")


def fetch():
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    evs = {}
    for s in SERIES:
        got, n_ser = events_of(s)
        print(f"series {s}: {len(got)} events (series lists {n_ser})", flush=True)
        for k, e in got.items():
            e["_series"] = s
            evs[k] = e
    for tag in ("ornn", "compute"):
        extra = [e for e in tag_events(tag) if str(e.get("id")) not in evs]
        print(f"tag {tag}: {len(extra)} more events: {[e.get('title') for e in extra][:30]}", flush=True)
        for e in extra:
            if re.search(r"rental|gpu|h100|h200|b200|b300|rtx", str(e.get("title")) + str(e.get("slug")), re.I):
                e["_series"] = "tag:" + tag
                evs[str(e.get("id"))] = e
    ms = {}
    for e in evs.values():
        for m in e.get("markets") or []:
            if not isinstance(m, dict):
                continue
            m = dict(m)
            m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
            x = bt.slim_market(m)
            x.update(cid=m.get("conditionId"), title=e.get("title"), series=e.get("_series"), item=m.get("groupItemTitle"),
                     desc=str(m.get("description") or "")[:3000], ev_end=e.get("endDate"), ev_start=e.get("startDate"),
                     created=m.get("createdAt"), fees=m.get("feesEnabled"), fs=m.get("feeSchedule"),
                     line=m.get("groupItemThreshold"), active=m.get("active"))
            if x.get("cid") and len(x["toks"]) == 2:
                ms[x["id"]] = x
    wj(os.path.join(CACHE, "markets.json.gz"), ms)
    print(f"\n{len(evs)} events, {len(ms)} markets, closed {sum(m['closed'] for m in ms.values())}, "
          f"traded ${sum(m['vol'] or 0 for m in ms.values()):,.0f}", flush=True)
    by = collections.defaultdict(list)
    for m in ms.values():
        by[m["title"]].append(m)
    for t, xs in sorted(by.items(), key=lambda kv: str(kv[1][0]["ev_end"])):
        print(f"  {str(xs[0]['ev_end'])[:10]} {t} | {len(xs)} mkts, closed {sum(m['closed'] for m in xs)}, "
              f"${sum(m['vol'] or 0 for m in xs):,.0f} | {xs[0]['series']}", flush=True)
    seen = set()
    for m in ms.values():
        if m["series"] not in seen:
            seen.add(m["series"])
            print(f"\nRULES {m['series']}: {m['q']} fee {m['fee']} {m['fs']}\n{m['desc'][:1500]}", flush=True)
    # every real trade
    tp = {}
    with ThreadPoolExecutor(8) as ex:
        for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in ms.values()]):
            if r is not None:
                tp[mid] = r
    wj(os.path.join(CACHE, "tapes.json.gz"), tp)
    print(f"\ntapes {len(tp)}/{len(ms)}, trades {sum(r['n'] for r in tp.values())}, cut {sum(r['cut'] for r in tp.values())}",
          flush=True)
    ornn()


def ornn():
    """Ornn's free index: gpu list, latest values, trailing 3 months daily per GPU, and a try at older history."""
    out = {"t": int(time.time())}
    for base in ORNN:
        out[base + " types"] = get(f"{base}/api/gpu-types")
        out[base + " all"] = get(f"{base}/api/daily-index/all")
    names = set(GPUS)
    for v in out.values():
        for x in (v.get("data") if isinstance(v, dict) else None) or []:
            if isinstance(x, dict):
                n = x.get("gpu_type") or x.get("gpu_name") or x.get("name")
                if n:
                    names.add(n)
            elif isinstance(x, str):
                names.add(x)
    hist = {}
    for n in sorted(names):
        q = urllib.parse.quote(n)
        for base in ORNN[:2]:
            r = get(f"{base}/api/gpu/{q}/index-history", {"startDate": "2025-01-01", "endDate": "2026-12-31"})
            rows = r.get("data") if isinstance(r, dict) else None
            if rows:
                hist[n] = {"src": base, "access": r.get("access"), "rows": rows}
                break
            out[f"hist {n} {base}"] = r
        out[f"range {n}"] = get(f"{ORNN[0]}/api/gpu/{q}/history-range", {"startDate": "2025-06-01", "endDate": "2026-08-31"})
        out[f"now {n}"] = get(f"{ORNN[0]}/api/gpu/{q}")
        out[f"vol {n}"] = get(f"{ORNN[0]}/api/gpu/{q}/volatility")
        h = hist.get(n)
        print(f"ornn {n}: {len(h['rows']) if h else 0} days {h and h['rows'][0]} .. {h and h['rows'][-1]} access "
              f"{h and h.get('access')} | range {str(out[f'range {n}'])[:160]}", flush=True)
    out["hist"] = hist
    # older days: archived copies of the free JSON / market pages (web.archive.org), and the old dashboard
    arch = {}
    for u in ["data.ornn.com/api/public-index/*", "api.ornnai.com/api/*", "data.ornn.com/markets/*", "dashboard.ornnai.com*",
              "index.ornn.com*", "ornnai.com/api/*"]:
        r = get("https://web.archive.org/cdx/search/cdx", {"url": u, "output": "json", "limit": 400, "filter": "statuscode:200"})
        arch[u] = r
        print(f"archive {u}: {len(r) - 1 if isinstance(r, list) else r}", flush=True)
        if isinstance(r, list):
            for row in r[1:12]:
                print("   ", row[1], row[2][:140], row[3], flush=True)
    out["archive"] = arch
    for path in ("/ocpi", "/markets", "/markets/h100-sxm", "/methodology", "/docs/methodology", "@https://dashboard.ornnai.com"):
        try:
            req = urllib.request.Request(path[1:] if path[0] == "@" else "https://data.ornn.com" + path, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as f:
                txt = f.read().decode("utf-8", "replace")
            out["page " + path] = txt[:200000]
            print(f"page {path}: {len(txt)} chars, json links {sorted(set(re.findall(r'/api/[A-Za-z0-9_/%.-]+', txt)))[:20]}",
                  flush=True)
        except Exception as e:
            print(f"page {path}: {str(e)[:100]}", flush=True)
    wj(os.path.join(CACHE, f"ornn_{dt.datetime.utcnow():%Y%m%d}.json.gz"), out)
    for k, v in out.items():
        if not k.startswith(("page", "hist")) and k != "t":
            print(f"  {k}: {json.dumps(v)[:300]}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"fetch": fetch, "ornn": ornn}.get(cmd, lambda: print(__doc__))()
