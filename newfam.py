#!/usr/bin/env python3
"""New market families (27 Nov 2026): which repeating bet families did Kalshi or Polymarket start in the last few months?

  python3 newfam.py scan [since]     # probe nf_scan: every Kalshi series with its first market's opening day, size and
                                     # settled count; every Polymarket event family (slug with dates/numbers removed) and
                                     # Gamma series with first start day. Writes bt_cache/nf/scan.json.gz and prints the
                                     # families whose first market opened on or after `since` (default 2026-08-27).

Idea: new families may have fewer pros pricing them. The scan only lists; each dig on a family lives in its own module.
"""
import collections
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import yesno
import habits

G = bt.G
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "nf")


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


def its(s):
    try:
        return int(dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp())
    except Exception:
        return 0


def day(t):
    return dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d") if t else "-"


def k_series_info(s):
    """First opening, market count, settled count, volume of one Kalshi series (live endpoint, plus whether any market
    is already in /historical, which means the series is older than the historical cutoff)."""
    rows, cur = [], None
    for _ in range(15):
        p = {"series_ticker": s, "limit": 1000}
        if cur:
            p["cursor"] = cur
        try:
            r = yesno.kget("/markets", p)
        except Exception as e:
            return s, {"err": str(e)[:80]}
        got = r.get("markets") or []
        rows += got
        cur = r.get("cursor")
        if not cur or not got:
            break
    hist = 0
    try:
        h = yesno.kget("/historical/markets", {"series_ticker": s, "limit": 5})
        hist = len([m for m in (h.get("markets") or []) if str(m.get("event_ticker") or "").startswith(s)])
    except Exception:
        hist = -1
    rows = [m for m in rows if str(m.get("event_ticker") or "").startswith(s)]
    opens = [its(m.get("open_time")) for m in rows if its(m.get("open_time"))]
    vol = sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) or 0 for m in rows)
    settled = [m for m in rows if str(m.get("result") or "").lower() in ("yes", "no")]
    evs = {m.get("event_ticker") for m in rows}
    sev = {m.get("event_ticker") for m in settled}
    return s, {"n": len(rows), "settled": len(settled), "ev": len(evs), "sev": len(sev), "vol": vol,
               "first": min(opens) if opens else 0, "last": max(opens) if opens else 0, "hist": hist,
               "ex": str((rows[0].get("title") if rows else "") or "")[:110]}


def scan(since="2026-08-27"):
    t_since = its(since + "T00:00:00Z")
    out = {"made": int(time.time()), "kalshi": {}, "poly_fam": {}, "poly_series": []}
    # ---- Kalshi
    try:
        ser = yesno.kget("/series", {}).get("series") or []
    except Exception as e:
        ser = []
        print("kalshi /series failed", str(e)[:120], flush=True)
    print("Kalshi series", len(ser), flush=True)
    meta = {x["ticker"]: x for x in ser if x.get("ticker")}
    done = 0
    with ThreadPoolExecutor(8) as ex:
        for s, info in ex.map(k_series_info, sorted(meta)):
            x = meta[s]
            info.update({"cat": x.get("category"), "freq": x.get("frequency"), "title": str(x.get("title") or "")[:110],
                         "fee": [x.get("fee_type"), x.get("fee_multiplier")],
                         "src": [y.get("url") for y in (x.get("settlement_sources") or []) if isinstance(y, dict)][:3]})
            out["kalshi"][s] = info
            done += 1
            if done % 500 == 0:
                print("  kalshi series done", done, flush=True)
    wj(os.path.join(CACHE, "scan.json.gz"), out)
    # ---- Polymarket event families (all events, open and closed, that started since June)
    F = collections.defaultdict(lambda: {"n": 0, "closed": 0, "vol": 0.0, "mk": 0, "tags": collections.Counter(),
                                         "ex": "", "first": 99999999999, "last": 0, "series": collections.Counter()})
    for closed in ("true", "false"):
        cur, n = None, 0
        for _ in range(2000):
            p = {"closed": closed, "limit": 50, "start_date_min": "2026-06-01T00:00:00Z"}
            if cur:
                p["after_cursor"] = cur
            try:
                r = bot.http_json(f"{G}/events/keyset", p)
            except Exception as e:
                print("   page failed", str(e)[:100], flush=True)
                break
            rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
            for e in rows:
                f = F[habits.fam(e.get("slug"))]
                f["n"] += 1
                f["closed"] += closed == "true"
                f["vol"] += float(e.get("volume") or 0)
                f["mk"] += len(e.get("markets") or [])
                f["tags"].update(str(t.get("slug")) for t in (e.get("tags") or []) if isinstance(t, dict))
                for sr in (e.get("series") or []):
                    if isinstance(sr, dict):
                        f["series"][str(sr.get("slug") or sr.get("ticker"))] += 1
                f["ex"] = str(e.get("title"))[:90]
                st = its(e.get("startDate") or e.get("creationDate") or e.get("createdAt"))
                if st:
                    f["first"] = min(f["first"], st)
                    f["last"] = max(f["last"], st)
            n += len(rows)
            cur = r.get("next_cursor") if isinstance(r, dict) else None
            if not rows or not cur:
                break
        print(f"Polymarket events closed={closed} since June: {n}", flush=True)
    for k, f in F.items():
        out["poly_fam"][k] = {"n": f["n"], "closed": f["closed"], "vol": f["vol"], "mk": f["mk"],
                              "tags": [t for t, _ in f["tags"].most_common(5)], "ex": f["ex"], "first": f["first"],
                              "last": f["last"], "series": [s for s, _ in f["series"].most_common(2)]}
    # ---- Polymarket series objects (they carry a creation date)
    off = 0
    while off < 20000:
        try:
            r = bot.http_json(f"{G}/series", {"limit": 100, "offset": off})
        except Exception as e:
            print("   series page failed", str(e)[:100], flush=True)
            break
        rows = [x for x in bot.envelope_rows(r, "series", "data") if isinstance(x, dict)]
        for x in rows:
            out["poly_series"].append({"slug": x.get("slug"), "title": str(x.get("title") or "")[:100],
                                       "created": its(x.get("createdAt")), "start": its(x.get("startDate")),
                                       "rec": x.get("recurrence"), "vol": bot.fnum(x.get("volume"), 0),
                                       "vol24": bot.fnum(x.get("volume24hr"), 0), "type": x.get("seriesType"),
                                       "closed": x.get("closed"), "active": x.get("active")})
        if len(rows) < 100:
            break
        off += 100
    wj(os.path.join(CACHE, "scan.json.gz"), out)
    report(out, t_since)


SKIP = re.compile(r"MVE|^KXMVE", re.I)


def report(out=None, t_since=None):
    out = out or rj(os.path.join(CACHE, "scan.json.gz"), {})
    t_since = t_since or its("2026-08-27T00:00:00Z")
    K = out.get("kalshi") or {}
    new = [(s, i) for s, i in K.items() if i.get("first") and i["first"] >= t_since and i.get("hist") == 0 and not SKIP.search(s)]
    print(f"\n=== KALSHI: {len(new)} of {len(K)} series whose first live market opened on/after {day(t_since)} and none in /historical ===")
    print("cat | freq | series | first open | markets | settled | events settled | volume | title | example")
    for s, i in sorted(new, key=lambda kv: -(kv[1].get("vol") or 0))[:300]:
        print(f"K | {i.get('cat')} | {i.get('freq')} | {s} | {day(i['first'])} | {i['n']} | {i['settled']} | {i['sev']} | "
              f"{i['vol']:,.0f} | {i.get('title')} | {i.get('ex')}")
    cats = collections.Counter(i.get("cat") for _, i in new)
    vcat = collections.defaultdict(float)
    for _, i in new:
        vcat[i.get("cat")] += i.get("vol") or 0
    print("new Kalshi series by category (count, contracts):", [(c, n, round(vcat[c])) for c, n in cats.most_common()])
    P = out.get("poly_fam") or {}
    newp = [(k, f) for k, f in P.items() if f["first"] >= t_since and f["n"] >= 3]
    print(f"\n=== POLYMARKET: {len(newp)} event families (3+ events) first started on/after {day(t_since)} (looked back to 1 June) ===")
    print("events | closed | markets | volume | first..last start | family | example | tags | series")
    for k, f in sorted(newp, key=lambda kv: -kv[1]["vol"])[:300]:
        print(f"P | {f['n']} | {f['closed']} | {f['mk']} | ${f['vol']:,.0f} | {day(f['first'])}..{day(f['last'])} | {k} | {f['ex']} | {f['tags']} | {f['series']}")
    S = [x for x in (out.get("poly_series") or []) if (x.get("created") or 0) >= t_since]
    print(f"\n=== POLYMARKET series objects created on/after {day(t_since)}: {len(S)} of {len(out.get('poly_series') or [])} ===")
    for x in sorted(S, key=lambda x: -(x.get("vol") or 0))[:150]:
        print(f"S | {day(x['created'])} | {x.get('rec')} | ${x.get('vol') or 0:,.0f} | 24h ${x.get('vol24') or 0:,.0f} | {x.get('slug')} | {x.get('title')}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan(*(sys.argv[2:3] or []))
    elif cmd == "report":
        report()
    else:
        print("usage: newfam.py scan [since] | report")
