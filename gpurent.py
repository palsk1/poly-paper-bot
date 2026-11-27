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
    try:
        arch()
    except Exception as e:
        print("arch failed", e, flush=True)


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


def slow(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as f:
                return json.loads(f.read().decode("utf-8", "replace"))
        except Exception as e:
            last = str(e)[:120]
            time.sleep(5 + 10 * i)
    return {"_err": last}


def arch():
    """Older index days: every archived copy (web.archive.org) of the free index-history JSON, merged per GPU and day.
    Each copy holds the 3 months before it was saved, so the copies together reach back further than today's free window."""
    snaps = []
    for u in ["api.ornnai.com/api/gpu/*", "data.ornn.com/api/public-index/gpu/*", "api.ornnai.com/api/*",
              "data.ornn.com/api/public-index/*"]:
        r = slow("https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
            {"url": u, "output": "json", "limit": 3000, "filter": "statuscode:200"}))
        if isinstance(r, list):
            snaps += [row for row in r[1:] if "index-history" in row[2]]
        else:
            print("cdx", u, r, flush=True)
    print(f"archived index-history copies: {len(snaps)}", flush=True)
    merged = collections.defaultdict(dict)
    for n, dd in (rj(os.path.join(CACHE, "ornn_arch.json.gz"), {}) or {}).items():
        merged[n].update(dd)
    seen, want = set(), []
    for row in sorted(snaps, key=lambda r: r[1]):
        m = re.search(r"/gpu/([^/]+)/index-history", row[2])
        name = urllib.parse.unquote(m.group(1)).replace("+", " ") if m else "?"
        if "startDate" in row[2] or row[1][:8] >= "20260901":      # the free window covers Sep onwards
            continue
        key = (name, row[1][:6], row[1][6:8] >= "15")               # two copies a month per GPU are enough
        if key in seen:
            continue
        seen.add(key)
        want.append((row, name))
    print(f"copies to read: {len(want)}", flush=True)
    for row, name in want:
        j = None
        for i in range(4):
            try:
                req = urllib.request.Request(f"https://web.archive.org/web/{row[1]}id_/{row[2]}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as f:
                    j = json.loads(f.read().decode("utf-8", "replace"))
                break
            except Exception as e:
                err = str(e)[:60]
                time.sleep(10 + 20 * i)
        if j is None:
            print("  copy failed", row[1], row[2][:90], err, flush=True)
            continue
        rows = j.get("data") if isinstance(j, dict) else None
        n_new = 0
        for x in rows or []:
            d = str(x.get("timestamp") or x.get("date"))[:10]
            v = x.get("index_value")
            if v is None:
                continue
            old = merged[name].get(d)
            if old is None:
                n_new += 1
            elif abs(old[0] - v) > 0.005:
                merged[name][d] = [old[0], old[1], v, row[1]]     # keep the first copy, note the change
                continue
            merged[name].setdefault(d, [v, row[1]])
        print(f"  {row[1]} {name}: {len(rows or [])} days, {n_new} new", flush=True)
        time.sleep(4)
    wj(os.path.join(CACHE, "ornn_arch.json.gz"), merged)
    for n, dd in merged.items():
        ks = sorted(dd)
        ch = sum(1 for v in dd.values() if len(v) > 2)
        print(f"ARCH {n}: {len(ks)} days {ks[0]} .. {ks[-1]}, changed later {ch}", flush=True)


# ---------------------------------------------------------------- the test (offline, after store.py pull bt_cache/nf)
DAY = 86400
FEE_EXTRA = 0.02
STAKE = 10.0
NAME = {"A100": "A100 SXM4", "B200": "B200", "B300": "B300", "H100": "H100 SXM", "H200": "H200", "RTX 5090": "RTX 5090",
        "RTX 6000": "RTX PRO 6000 WS"}


def index_days():
    """{gpu: {day: value}} from today's free window plus any archived copies (the free window wins)."""
    out = collections.defaultdict(dict)
    a = rj(os.path.join(CACHE, "ornn_arch.json.gz"), {}) or {}
    for n, dd in a.items():
        for d, v in dd.items():
            out[n][d] = v[0]
    files = sorted(f for f in os.listdir(CACHE) if re.match(r"ornn_\d{8}\.json\.gz$", f))
    for f in files:
        o = rj(os.path.join(CACHE, f), {})
        for n, h in (o.get("hist") or {}).items():
            for r in h["rows"]:
                out[n][r["timestamp"][:10]] = float(r["index_value"])
    return out


def d2t(d):
    return int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


def known(series, t):
    """Days whose value was public and final at time t: the value dated D is taken as known from D+1 06:00 UTC
    (Ornn settles at midnight New York time; being a day late on purpose costs us, never helps us)."""
    return [(d, v) for d, v in sorted(series.items()) if d2t(d) + DAY + 6 * 3600 <= t]


MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def parse(m):
    """-> dict(gpu, kind, lo, hi, day / month) or None. Kinds: 'on' (value on one day in [lo, hi)), 'hit' (touch),
    'avg' (average over a month above lo)."""
    q = m["q"]
    g = re.search(r"Ornn (A100|B200|B300|H100|H200|RTX 5090|RTX 6000)", q)
    if not g:
        return None
    gpu = NAME[g.group(1)]
    num = [float(x) for x in re.findall(r"\$(\d+(?:\.\d+)?)", q)]
    dm = re.search(r"on (\w+) (\d+), (\d{4})", q)
    if dm and m["title"].lower().find("hit") < 0:
        day = f"{dm.group(3)}-{MONTHS[dm.group(1).lower()]:02d}-{int(dm.group(2)):02d}"
        if "between" in q:
            lo, hi = num[0], num[1]
        elif "at least" in q or "above" in q or "greater" in q:
            lo, hi = num[0], 1e9
        elif "less than" in q or "below" in q:
            lo, hi = -1.0, num[0]
        else:
            return None
        return {"gpu": gpu, "kind": "on", "lo": lo, "hi": hi, "day": day}
    hm = re.search(r"hit \$(\d+(?:\.\d+)?) \((HIGH|LOW)\) by (\w+) (\d+), (\d{4})", q)
    if hm:
        day = f"{hm.group(5)}-{MONTHS[hm.group(3).lower()]:02d}-{int(hm.group(4)):02d}"
        return {"gpu": gpu, "kind": "hit", "k": float(hm.group(1)), "up": hm.group(2) == "HIGH", "day": day}
    am = re.search(r"average Ornn \S+ rental price in (\w+) (\d{4}) be above \$(\d+(?:\.\d+)?)", q)
    if am:
        mo = MONTHS[am.group(1).lower()]
        return {"gpu": gpu, "kind": "avg", "lo": float(am.group(3)), "year": int(am.group(2)), "month": mo,
                "day": f"{am.group(2)}-{mo:02d}-28"}
    return None


def spread(kn):
    """Day-to-day noise around the 7-day mean (s0) and the daily wander of the 7-day mean (sd), log terms, from known
    days only. Pooled over every GPU by the caller."""
    v = [math.log(x) for _, x in kn]
    res, mov = [], []
    for i in range(7, len(v)):
        m7 = sum(v[i - 7:i]) / 7
        res.append(v[i] - m7)
        if i >= 8:
            mov.append(m7 - sum(v[i - 8:i - 1]) / 7)
    return res, mov


WIDE = os.environ.get("GPU_WIDE", "1") == "1"


def wide_sd(idx, H=30):
    """Daily wander that matches the real 30-day moves (pooled, whole free window: the index trends, so the
    day-to-day wander of the 7-day mean understates a month's move about threefold). Uses days after the look, so
    this variant knows how big moves were (not which way)."""
    ch = []
    for n, s in idx.items():
        v = [math.log(x) for _, x in sorted(s.items())]
        for i in range(7, len(v) - H):
            ch.append(v[i + H] - sum(v[i - 7:i]) / 7)
    return math.sqrt(statistics.pstdev(ch) ** 2 / H) if len(ch) > 20 else None


def model(idx, t):
    """Shared spread numbers at time t from every GPU's known days."""
    res, mov = [], []
    for n, s in idx.items():
        r, m = spread(known(s, t))
        res += r
        mov += m
    if len(res) < 40:
        return None
    M = {"s0": statistics.pstdev(res), "sd": statistics.pstdev(mov), "n": len(res)}
    if WIDE:
        w = wide_sd(idx)
        if w:
            M["sd"] = max(M["sd"], w)
    return M


def prob(p, idx, t, M, sims=4000, seed=1):
    """Chance of Yes at time t: the 7-day mean wanders like a random walk (sd a day), each day's print sits around it
    with noise s0. No drift."""
    import random
    kn = known(idx.get(p["gpu"], {}), t)
    if len(kn) < 8:
        return None
    last_d = kn[-1][0]
    m7 = sum(math.log(x) for _, x in kn[-7:]) / 7
    end = p["day"]
    if p["kind"] == "avg":
        first = f"{p['year']}-{p['month']:02d}-01"
        nxt = dt.date(p["year"] + (p["month"] == 12), p["month"] % 12 + 1, 1)
        days = [d for d in (str(dt.date.fromisoformat(first) + dt.timedelta(i)) for i in range(31)) if d < str(nxt)]
        end = days[-1]
    h = (d2t(end) - d2t(last_d)) // DAY
    if h <= 0:
        return None
    rnd = random.Random(seed)
    if p["kind"] == "on":
        s = math.sqrt(M["s0"] ** 2 + h * M["sd"] ** 2)
        def cdf(x):
            return 0.5 * (1 + math.erf((math.log(x) - m7) / (s * math.sqrt(2)))) if x > 0 else 0.0
        return max(0.0, min(1.0, (cdf(p["hi"]) if p["hi"] < 1e8 else 1.0) - cdf(p["lo"])))
    if p["kind"] == "hit":
        done = [x for d, x in kn if d2t(d) >= t - 40 * DAY]
        hit = 0
        for _ in range(sims):
            c = m7
            ok = False
            for _ in range(int(h)):
                c += rnd.gauss(0, M["sd"])
                x = math.exp(c + rnd.gauss(0, M["s0"]))
                if (x >= p["k"]) if p["up"] else (x <= p["k"]):
                    ok = True
                    break
            hit += ok
        return hit / sims
    if p["kind"] == "avg":
        inside = [x for d, x in kn if d in days]
        future = [d for d in days if d > last_d]
        win = 0
        for _ in range(sims // 4):
            c = m7
            tot = sum(inside)
            for d in sorted(set(future) | {str(dt.date.fromisoformat(last_d) + dt.timedelta(i)) for i in range(1, int(h) + 1)}):
                c += rnd.gauss(0, M["sd"])
                if d in days and d > last_d:
                    tot += math.exp(c + rnd.gauss(0, M["s0"]))
            win += round(tot / len(days), 2) > p["lo"]
        return win / (sims // 4)
    return None


def last_before(b, t):
    p = None
    for x in b:
        if x[0] + 300 <= t:
            p = x[2]
        else:
            break
    return p


def buy(m, b, t, yes, extra=FEE_EXTRA, stake=STAKE, window=7200, lo=0.03, hi=0.97, ref=None):
    """Worst real trade of the next `window` seconds (never better than the price seen), + extra + fee."""
    nxt = [x for x in b if t <= x[0] < t + window]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if ref is not None:
        px = max(px, ref)
    if not lo <= px <= hi:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    win = (m["final"][0] == 1.0) == yes
    return {"t": nxt[0][0], "cost": stake + bot.taker_fee(sh, c, m["fee"] or 0), "pay": sh if win else 0.0, "sh": sh,
            "px": px, "yes": yes, "id": m["id"], "question": m["q"], "month": m["_p"]["day"][:7]}


LOOKS = (28, 21, 14, 10, 7, 5, 3, 2, 1)


def looks(ms, tp, idx):
    """One row per (market, look): days left, price, model chance."""
    rows = []
    cache = {}
    for m in ms.values():
        p = m["_p"]
        b = tp.get(m["id"], {}).get("b") or []
        endt = d2t(p["day"]) + DAY
        for L in LOOKS:
            t = endt - L * DAY
            if t > time.time() or (m["start"] and t < m["start"]):
                continue
            px = last_before(b, t)
            if px is None or px - 0 < 0.005 and False:
                continue
            key = t // DAY
            if key not in cache:
                cache[key] = model(idx, t)
            M = cache[key]
            if not M:
                continue
            q = prob(p, idx, t, M)
            if q is None:
                continue
            rows.append({"m": m, "b": b, "t": t, "left": L, "px": px, "q": q})
    return rows


def disagree(rows, gap=0.10, side=None, sel=None):
    """First look per market where the model is `gap` or more away from the last price: buy the side the model likes."""
    out, seen, miss = [], set(), 0
    for r in sorted(rows, key=lambda r: r["t"]):
        mid = r["m"]["id"]
        if mid in seen or (sel and not sel(r)):
            continue
        d = r["q"] - r["px"]
        if abs(d) < gap:
            continue
        yes = d > 0
        if side is not None and yes != side:
            continue
        x = buy(r["m"], r["b"], r["t"], yes, ref=r["px"] if yes else 1 - r["px"])
        seen.add(mid)
        if not x:
            miss += 1
            continue
        out.append(dict(x, ev=x["month"], qm=r["q"], left=r["left"], seen=r["px"]))
    return out, miss


def per100(b):
    c = sum(x["cost"] for x in b)
    return 100 * sum(x["pay"] - x["cost"] for x in b) / c if c else None


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def line(name, b, miss=None):
    w = sum(1 for x in b if x["pay"] > 0)
    mo = len({x["ev"] for x in b})
    extra = f", {miss} signals found no seller in 2 hours" if miss is not None else ""
    return (f"| {name} | {len(b)} | {w} | {mo} | {usd(sum(x['pay'] - x['cost'] for x in b))} | {usd(per100(b))} |{extra}")


def report():
    import exam
    ms = rj(os.path.join(CACHE, "markets.json.gz"), {})
    tp = rj(os.path.join(CACHE, "tapes.json.gz"), {})
    idx = index_days()
    print("index days per GPU:", {n: f"{min(d)}..{max(d)} ({len(d)})" for n, d in idx.items()})
    for m in ms.values():
        m["_p"] = parse(m)
    odd = [m["q"] for m in ms.values() if not m["_p"]]
    print(f"markets {len(ms)}, settled {sum(m['closed'] for m in ms.values())}, not read: {len(odd)} e.g. {odd[:3]}")
    # check our reading of the rules against the settled results
    ok = bad = 0
    for m in ms.values():
        p = m["_p"]
        if not p or not m["closed"] or p["kind"] != "on":
            continue
        v = idx.get(p["gpu"], {}).get(p["day"])
        if v is None:
            continue
        yes = p["lo"] <= v < p["hi"]
        if yes == (m["final"][0] == 1.0):
            ok += 1
        else:
            bad += 1
            print("   mismatch", m["q"], v, m["final"])
    print(f"rule check (day-value markets with the index known): {ok} match, {bad} do not")
    done = {k: m for k, m in ms.items() if m["closed"] and m["_p"] and m["final"] and max(m["final"]) == 1.0}
    rows = looks(done, tp, idx)
    print(f"looks with a price and a model chance: {len(rows)} on {len({r['m']['id'] for r in rows})} settled markets, "
          f"months {sorted({r['m']['_p']['day'][:7] for r in rows})}")
    # calibration: model vs price at each look
    def brier(key):
        return sum((r[key] - (r["m"]["final"][0] == 1.0)) ** 2 for r in rows) / max(1, len(rows))
    print(f"\nforecast score (lower is better): price {brier('px'):.4f}, model {brier('q'):.4f}, {len(rows)} looks")
    by = collections.defaultdict(list)
    for r in rows:
        by[("last 3 days" if r["left"] <= 3 else "4-10 days" if r["left"] <= 10 else "11+ days")].append(r)
    for k, rr in sorted(by.items()):
        bp = sum((r["px"] - (r["m"]["final"][0] == 1.0)) ** 2 for r in rr) / len(rr)
        bm = sum((r["q"] - (r["m"]["final"][0] == 1.0)) ** 2 for r in rr) / len(rr)
        print(f"   {k}: price {bp:.4f}, model {bm:.4f} ({len(rr)} looks)")
    print("\n| rule | bets | won | months | P&L | per $100 |\n|---|---|---|---|---|---|")
    tries = 0
    cards = []
    for name, kw in [("model 10c+ off the price, either side", {}),
                     ("model 10c+ above the price: buy Yes", {"side": True}),
                     ("model 10c+ below the price: buy No", {"side": False}),
                     ("model 20c+ off the price", {"gap": 0.20}),
                     ("model 10c+ off, last 7 days only", {"sel": lambda r: r["left"] <= 7}),
                     ("model 10c+ off, day-value brackets only", {"sel": lambda r: r["m"]["_p"]["kind"] == "on"})]:
        b, miss = disagree(rows, **kw)
        tries += 1
        print(line(name, b, miss))
        cards.append((name, b))
    # backward look: what did the winners share beforehand? the bracket holding today's value, by days left and price
    print("\nBackward look: the bracket that holds the newest known value, bought at the worst trade of the next 2 hours + 2c + fee")
    print("| days left | side | Yes 3-25c | Yes 25-50c | Yes 50-75c | Yes 75-97c |\n|---|---|---|---|---|---|")
    bands = [(0.03, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.97)]
    back = {}
    for L in (21, 14, 7, 3, 1):
        for holds in (True, False):
            for yes in (True, False):
                cells = []
                for lo, hi in bands:
                    bb = []
                    for r in rows:
                        p = r["m"]["_p"]
                        if r["left"] != L or p["kind"] != "on" or not lo <= r["px"] < hi:
                            continue
                        kn = known(idx[p["gpu"]], r["t"])
                        h = p["lo"] <= kn[-1][1] < p["hi"]
                        if h != holds:
                            continue
                        x = buy(r["m"], r["b"], r["t"], yes, ref=r["px"] if yes else 1 - r["px"])
                        if x:
                            bb.append(dict(x, ev=x["month"]))
                    tries += 1
                    back[(L, holds, yes, lo)] = bb
                    w = sum(1 for x in bb if x["pay"] > 0)
                    cells.append(f"{usd(per100(bb))} ({len(bb)}, {w} won)" if len(bb) >= 5 else f"- ({len(bb)})")
                print(f"| {L} ({'holds' if holds else 'other'}) | {'Yes' if yes else 'No'} | " + " | ".join(cells) + " |")
    # the best-looking cell gets the exam, with every cell counted as a try
    best = max(((k, v) for k, v in back.items() if len({x['ev'] for x in v}) >= 2 and len(v) >= 8),
               key=lambda kv: per100(kv[1]) or -1e9, default=None)
    print(f"\ntries counted: {tries}")
    for name, b in cards[:1]:
        exam.score(b, "GPU rental bets: Ornn index model 10c+ off the price", tries=tries, src="gpurent.py",
                   note="Polymarket Ornn GPU rental brackets/touch markets, settled Aug-Oct 2026; counted by settle month")
    for name, b in cards[1:3]:
        exam.score(b, "GPU rental bets: " + name, tries=tries, src="gpurent.py", log=False)
    if best:
        (L, holds, yes, lo), b = best
        nm = f"GPU rental bets: {'holder' if holds else 'non-holder'} bracket {L} days left, {'Yes' if yes else 'No'} at Yes {int(lo*100)}c+"
        print("\nbest backward-look cell:", nm)
        for x in sorted(b, key=lambda x: -(x["pay"] - x["cost"]))[:8]:
            print(f"   {x['question'][:80]} paid {x['px']:.2f} {'Yes' if x['yes'] else 'No'} -> {usd(x['pay'] - x['cost'])}")
        exam.score(b, nm, tries=tries, src="gpurent.py", note="found by looking (backward look)")
    for name, b in cards[:1]:
        print(f"\nbiggest wins of '{name}':")
        for x in sorted(b, key=lambda x: -(x["pay"] - x["cost"]))[:10]:
            print(f"   {x['month']} {x['question'][:78]} | {x['left']}d left, model {x['qm']:.2f}, seen {x['seen']:.2f}, paid "
                  f"{x['px']:.2f} {'Yes' if x['yes'] else 'No'} -> {usd(x['pay'] - x['cost'])}")
        print("biggest losses:")
        for x in sorted(b, key=lambda x: (x["pay"] - x["cost"]))[:6]:
            print(f"   {x['month']} {x['question'][:78]} | {x['left']}d left, model {x['qm']:.2f}, seen {x['seen']:.2f}, paid "
                  f"{x['px']:.2f} {'Yes' if x['yes'] else 'No'} -> {usd(x['pay'] - x['cost'])}")
    now_table(ms, tp, idx)


def now_table(ms, tp, idx):
    """Open markets today: last trade vs the model, for the new monthly-average series and the open day-value ones."""
    t = max(max((x[0] for x in r.get("b") or [[0]]), default=0) for r in tp.values()) + 600
    M = model(idx, t)
    print(f"\nOPEN MARKETS NOW (prices = last trade before {dt.datetime.utcfromtimestamp(t):%d %b %H:%M} UTC; model noise "
          f"{M['s0']:.3f}, wander {M['sd']:.3f} a day)")
    print("| bet | last trade (Yes) | model | traded | last trade |\n|---|---|---|---|---|")
    rows = []
    for m in ms.values():
        p = m["_p"]
        if m["closed"] or not p or p["day"] > "2027-03-31":
            continue
        b = tp.get(m["id"], {}).get("b") or []
        if not b:
            continue
        q = prob(p, idx, t, M)
        if q is None:
            continue
        rows.append((p["day"], m, b[-1][2], q, b[-1][0]))
    for d, m, px, q, lt in sorted(rows, key=lambda r: (r[0], r[1]["q"])):
        flag = " **" if abs(q - px) >= 0.10 else ""
        print(f"| {m['q'][:90]} | {100 * px:.0f}c | {100 * q:.0f}c{flag} | ${m['vol'] or 0:,.0f} | {dt.datetime.utcfromtimestamp(lt):%d %b} |")
    print(f"{sum(1 for r in rows if abs(r[3] - r[2]) >= 0.10)} of {len(rows)} open markets are 10c+ apart (marked **)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"fetch": fetch, "ornn": ornn, "arch": arch, "report": report}.get(cmd, lambda: print(__doc__))()
