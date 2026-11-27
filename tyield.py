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
K_DIR = r"KX(10|30|2|5|7)YRDIR(HM|LM|HW|LW)|KXUST10A|KXUST2A"
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
    print("polymarket part done", flush=True)


def kfetch(pat=None):
    import yesno
    try:
        ser = yesno.kget("/series", {}).get("series") or []
    except Exception as e:
        print("kalshi series failed", e)
        return
    hit = []
    if pat:
        ser = [s for s in ser if re.fullmatch(pat, str(s.get("ticker")))]
    for s in ser:
        t = (str(s.get("ticker")) + " " + str(s.get("title"))).lower()
        if re.search(r"treasur|yield|tnote|t-note|\b(2|5|10|30)[- ]year|\b(2|5|10|30)y\b|kx(10|2|5|30)y|mortgage rate", t):
            hit.append(s)
    print("\nKalshi series matching treasury/yield:", len(hit), [s["ticker"] for s in hit][:80], flush=True)
    hit = hit[:40]
    import kmentions as km
    import dates
    have = rj(os.path.join(CACHE, "kmarkets.json.gz"), {}) or {}
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
        if pat and not re.fullmatch(pat, tk):
            continue
        mm = [m for m in ok.values() if (m.get("vol") or 0) >= 50]
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
        if time.time() - t0 > 40 * 60:
            break


# ================================================================ model + test
def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def load_yields():
    """{tenor: [(day, close)]} from Treasury.gov's Daily Par Yield Curve (the settle source), sorted."""
    par = rj(os.path.join(CACHE, "ust_par.json.gz"), {}) or {}
    out = {k: {} for k in TENORS}
    for rows in par.values():
        for r in rows:
            try:
                d = dt.datetime.strptime(r["Date"], "%m/%d/%Y").strftime("%Y-%m-%d")
            except Exception:
                continue
            for k in TENORS:
                v = r.get(f"{k} Yr")
                try:
                    out[k][d] = float(v)
                except (TypeError, ValueError):
                    pass
    return {k: sorted(v.items()) for k, v in out.items()}


MDAY = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:,\s*(\d{4}))?"


def dates_of(m):
    """(first day, last day, kind) from the rule text: kind 'touch' (any day in the span) or 'day' (one day's value)."""
    d = str(m.get("desc") or "")
    yr = dt.datetime.utcfromtimestamp(m["end"] - 1).year

    def mk(mon, dd, y):
        return dt.date(int(y or yr), MONTHS[mon.lower()], int(dd))
    x = re.search(r"between\s+" + MDAY + r"\s+and\s+(?:market close on\s+)?" + MDAY, d)
    if x:
        a = mk(x.group(1), x.group(2), x.group(3) or x.group(6))
        b = mk(x.group(4), x.group(5), x.group(6))
        return a, b, "touch"
    x = re.search(r"any day in\s+(\w+)\s+(\d{4})", d)
    if x and x.group(1).lower() in MONTHS:
        a = dt.date(int(x.group(2)), MONTHS[x.group(1).lower()], 1)
        b = (dt.date(a.year + (a.month == 12), a.month % 12 + 1, 1) - dt.timedelta(days=1))
        return a, b, "touch"
    x = re.search(r"yield on (?:on )?" + MDAY + r"\s+is greater than", d)
    if x:
        a = mk(x.group(1), x.group(2), x.group(3))
        return a, a, "day"
    return None


def parse(m):
    """(tenor, 'high'|'low', level in %) from a rung, or None."""
    t = f"{m.get('title')} {m.get('q')}"
    mt = re.search(r"(\d+)-year", t, re.I)
    lv = re.findall(r"(\d+\.\d+|\d+)\s*%", str(m.get("item") or "") + " " + str(m.get("q")))
    if not mt or not lv:
        return None
    hl = "high" if re.search(r"how high|reach|above|hit|>|greater|\u2191", t, re.I) else "low" if re.search(r"how low|dip|below|\u2193", t, re.I) else None
    if re.search(r"how high", str(m.get("title")), re.I):
        hl = "high"
    if re.search(r"how low", str(m.get("title")), re.I):
        hl = "low"
    return (mt.group(1), hl, float(lv[0])) if hl and mt.group(1) in TENORS else None


def bdays(a, b):
    """US business days strictly after day a up to and including day b (dates)."""
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def state(series, t, start_day, look=60, end_day=None):
    """Last close known at time t (a close of day d is known from d 21:00 UTC), running max/min of closes since
    start_day, daily swing (sd of the last `look` daily changes)."""
    known = [(d, v) for d, v in series if its(d + "T00:00:00Z") + DAY + 3600 <= t]
    if len(known) < look + 2:
        return None
    since = [v for d, v in known if start_day <= d <= (end_day or "9999")]
    ch = [known[i][1] - known[i - 1][1] for i in range(len(known) - look, len(known))]
    mu = sum(ch) / len(ch)
    sd = math.sqrt(sum((c - mu) ** 2 for c in ch) / (len(ch) - 1))
    return {"y": known[-1][1], "day": known[-1][0], "hi": max(since) if since else known[-1][1],
            "lo": min(since) if since else known[-1][1], "sd": sd}


BG = 0.5826


def p_touch(y, k, sd, n, up, intraday=0.0):
    """Chance a driftless random walk with daily sd touches k within n more daily closes (reflection rule).
    intraday widens the barrier test by a typical intraday overshoot (in yield points)."""
    if n <= 0 or sd <= 0:
        return 0.0
    dist = (k - y) if up else (y - k)
    dist -= intraday
    if dist <= 0:
        return 1.0
    dist += BG * sd           # daily closes, not a continuous path: shift the barrier out (Broadie-Glasserman)
    return min(1.0, 2 * (1 - ncdf(dist / (sd * math.sqrt(n)))))


def last_before(b, t):
    p = None
    for x in b:
        if x[0] + 300 <= t:
            p = x[2]
        else:
            break
    return p


def fill(m, b, t, yes, extra=0.01, stake=10.0, window=7200):
    nxt = [x for x in b if t <= x[0] < t + window]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if not 0.02 <= px <= 0.97:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    return {"t": nxt[0][0], "px": px, "c": c, "sh": sh, "cost": stake + bot.taker_fee(sh, c, m.get("fee") or 0.0)}


def settle(m, tp):
    """1.0 / 0.0 for a settled rung, else None."""
    f = m.get("final") or []
    if m.get("closed") and f in ([1.0, 0.0], [0.0, 1.0]):
        return f[0]
    return None
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "fetch":
        fetch()
    elif cmd == "all":
        fetch()
        kfetch()
    elif cmd == "kfetch":
        arg = sys.argv[2] if len(sys.argv) > 2 else None
        kfetch(K_DIR if arg == "dir" else arg)
    elif cmd == "run":
        run(*sys.argv[2:])
    else:
        print(__doc__)


DONE_BY = "2026-11-20"
MONTHS = {m: i + 1 for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                          "september", "october", "november", "december"))}


def period_start(m):
    """First day the yield counts: the 1st of the named month for monthly events, else the market's start day."""
    t = str(m.get("title") or "").lower()
    for name, i in MONTHS.items():
        if re.search(rf"\bin {name}\b", t):
            y = dt.datetime.utcfromtimestamp(m["end"] - 1).year
            return f"{y}-{i:02d}-01"
    return dt.datetime.utcfromtimestamp(m.get("start") or m["end"]).strftime("%Y-%m-%d")


def load():
    ms = rj(os.path.join(CACHE, "markets.json.gz"), {}) or {}
    tp = rj(os.path.join(CACHE, "tapes.json.gz"), {}) or {}
    Y = load_yields()
    out = {}
    for mid, m in ms.items():
        p = parse(m)
        if not p or mid not in tp or not m.get("end"):
            continue
        dd = dates_of(m)
        if not dd:
            continue
        m = dict(m, ten=p[0], hl=p[1], k=p[2], p0=dd[0].isoformat(), p1=dd[1].isoformat(), kind=dd[2])
        m["res"] = settle(m, tp)
        m["done"] = m["p1"] <= DONE_BY       # the whole span is over: every rung has its answer (no early-Yes bias)
        m["b"] = tp[mid]["b"]
        out[mid] = m
    return out, Y


def looks(m, Y, step=DAY, hour=2, intraday=0.0):
    """One look a day at `hour` UTC (US closed, last Treasury close published): (t, model chance, last real price,
    state, already decided by the closes so far, business days left)."""
    ser = Y.get(m["ten"]) or []
    b = m["b"]
    if not b:
        return []
    t0 = max(b[0][0], (m.get("start") or b[0][0]))
    t = (t0 // DAY + 1) * DAY + hour * 3600
    last = dt.date.fromisoformat(m["p1"])
    stop = min(its(m["p1"] + "T20:00:00Z"), m.get("closed_t") or m["end"])
    rows = []
    up = m["hl"] == "high"
    while t < stop:
        st = state(ser, t, m["p0"], end_day=m["p1"])
        p = last_before(b, t)
        if st and p is not None:
            n = bdays(max(dt.date.fromisoformat(st["day"]), dt.date.fromisoformat(m["p0"]) - dt.timedelta(days=1)), last)
            if m["kind"] == "touch":
                started = st["day"] >= m["p0"]
                touched = started and (st["hi"] >= m["k"] if up else st["lo"] < m["k"])
                P = 1.0 if touched else p_touch(st["y"], m["k"], st["sd"], n, up, intraday)
            else:
                touched = n <= 0
                z = (st["y"] - m["k"]) / max(1e-9, st["sd"] * math.sqrt(max(n, 1e-9)))
                P = ncdf(z if up else -z)
            rows.append((t, P, p, st, touched, n))
        t += step
    return rows


def bets(ms, Y, gap=0.10, extra=0.01, stake=10.0, side="both", intraday=0.0, sel=None, once=True, bg=True):
    global BG
    BG = 0.5826 if bg else 0.0
    out = []
    for mid, m in ms.items():
        if sel and not sel(m):
            continue
        for t, P, p, st, touched, n in looks(m, Y, intraday=intraday):
            if touched:
                continue
            yes = P - p >= gap and side in ("both", "yes")
            no = p - P >= gap and side in ("both", "no")
            if not (yes or no):
                continue
            f = fill(m, m["b"], t, yes, extra, stake)
            if not f or not 0.05 <= f["px"] <= 0.95:
                continue
            res = m["res"]
            mark = res if res is not None else (m["b"][-1][2])
            win_val = mark if yes else 1 - mark
            out.append({"ev": m["p1"][:7] + ("" if m["kind"] == "touch" and m["p0"][:7] == m["p1"][:7] else "-" + m["kind"] + m["p0"]),
                        "event": m["eslug"], "t": f["t"], "cost": f["cost"], "pay": f["sh"] * win_val, "sh": f["sh"],
                        "px": f["px"], "q": p if yes else 1 - p, "yes": yes, "id": mid, "P": P, "settled": res is not None,
                        "k": m["k"], "ten": m["ten"], "hl": m["hl"], "y": st["y"], "n": n, "done": m["done"]})
            if once:
                break
    return out


def usd(x):
    return ("-" if x < 0 else "") + f"${abs(x):,.2f}"


def line(name, bb):
    if not bb:
        return f"  {name}: 0 bets"
    c = sum(b["cost"] for b in bb)
    p = sum(b["pay"] - b["cost"] for b in bb)
    return (f"  {name}: {len(bb)} bets on {len({b['ev'] for b in bb})} events, staked {usd(c)}, P&L {usd(p)} = "
            f"{usd(100 * p / c)} per $100 (settled {sum(b['settled'] for b in bb)})")


def run(*a):
    import exam
    ms, Y = load()
    done = {k: m for k, m in ms.items() if m["done"]}
    print("rungs with tape + rule parsed:", len(ms), "settled", sum(m["res"] is not None for m in ms.values()),
          "events", len({m["eslug"] for m in ms.values()}))
    print("finished spans (every rung answered):", len(done), "rungs,", len({m["eslug"] for m in done.values()}), "events,",
          sum(m["res"] == 1.0 for m in done.values()), "paid Yes, unsettled", sum(m["res"] is None for m in done.values()))
    ev = collections.defaultdict(list)
    for m in ms.values():
        ev[m["eslug"]].append(m)
    for e, mm in sorted(ev.items(), key=lambda x: x[1][0]["p1"]):
        st = [x for x in mm if x["res"] is not None]
        print(f"  {mm[0]['p0']}..{mm[0]['p1']} {e[:62]:62s} {len(mm):2d} rungs, {len(st):2d} settled ({sum(x['res'] == 1.0 for x in st)} Yes)"
              f" ${sum(x['vol'] or 0 for x in mm):>10,.0f} fee {mm[0]['fee']} {'DONE' if mm[0]['done'] else 'open'}")
    for bg in (True, False):
        global BG
        BG = 0.5826 if bg else 0.0
        rows = [(P, p, m["res"], m) for m in done.values() if m["res"] is not None
                for t, P, p, st, touched, n in looks(m, Y) if not touched]
        bm = sum((P - r) ** 2 for P, p, r, m in rows) / len(rows)
        bp = sum((p - r) ** 2 for P, p, r, m in rows) / len(rows)
        print(f"\nfinished spans, daily looks {len(rows)} ({'daily-close correction' if bg else 'plain reflection'}): "
              f"model miss {bm:.4f}, price miss {bp:.4f} (lower is better)")
        for kind in ("touch", "day"):
            r2 = [x for x in rows if x[3]["kind"] == kind]
            if r2:
                print(f"   {kind}: {len(r2)} looks, model {sum((P - r) ** 2 for P, p, r, m in r2) / len(r2):.4f}, "
                      f"price {sum((p - r) ** 2 for P, p, r, m in r2) / len(r2):.4f}")
        # calibration in bands
        for lo_, hi_ in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
            r2 = [x for x in rows if lo_ <= x[1] < hi_]
            if r2:
                print(f"   price {lo_:.1f}-{hi_:.1f}: {len(r2):5d} looks, paid {sum(x[2] for x in r2) / len(r2):.2f}, "
                      f"price avg {sum(x[1] for x in r2) / len(r2):.2f}, model avg {sum(x[0] for x in r2) / len(r2):.2f}")
    BG = 0.5826
    rules = (("both sides, 10c gap", {}), ("Yes only, 10c gap", {"side": "yes"}), ("No only, 10c gap", {"side": "no"}),
             ("both sides, 20c gap", {"gap": 0.20}), ("both sides, 10c gap, +2c", {"extra": 0.02}),
             ("both sides, 10c gap, no daily-close fix", {"bg": False}),
             ("both sides, 10c gap, touch ladders only", {"sel": lambda m: m["kind"] == "touch"}),
             ("both sides, 10c gap, one-day Friday bets only", {"sel": lambda m: m["kind"] == "day"}))
    res = {}
    print("\nRULES (one bet per rung, first look where model and price are 10c+ apart, $10 a bet, worst real trade of the "
          "next 2 h + 1c + fee). Finished spans only; open spans shown apart, marked at the last trade:")
    for name, kw in rules:
        bb = bets(ms, Y, **kw)
        res[name] = [b for b in bb if b["done"]]
        print(line(name, res[name]))
        print(line("     open spans, marked", [b for b in bb if not b["done"]]))
        ev_p = collections.defaultdict(float)
        for b in res[name]:
            ev_p[b["ev"]] += b["pay"] - b["cost"]
        print("     by month group: " + ", ".join(f"{k} {usd(v)}" for k, v in sorted(ev_p.items())))
        if ev_p:
            top = sorted(ev_p.items(), key=lambda x: -x[1])
            print(f"     events ahead {sum(v > 0 for v in ev_p.values())} of {len(ev_p)}; best event {top[0][0][:50]} "
                  f"{usd(top[0][1])}; without the best 3 events {usd(sum(v for k, v in top[3:]))}")
        BG = 0.5826
    print("\nbiggest wins / losses (both sides, 10c gap, finished spans):")
    bb = sorted(res["both sides, 10c gap"], key=lambda b: b["pay"] - b["cost"])
    for b in bb[:6] + bb[-10:]:
        print(f"  {b['event'][:58]:58s} {b['ten']}y {b['hl']} {b['k']:.2f} y={b['y']:.2f} n={b['n']} "
              f"{'Yes' if b['yes'] else 'No'} at {b['px']:.2f} (last {b['q']:.2f}) model {b['P']:.2f} P&L {usd(b['pay'] - b['cost'])} "
              f"{dt.datetime.utcfromtimestamp(b['t']).date()}")
    # backward look on finished spans
    print("\nbackward look, finished spans: first look of each rung, by distance (yield gap / (daily swing x root of days left))")
    bk = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    cuts = 0
    for m in done.values():
        if m["res"] is None or m["kind"] != "touch":
            continue
        L = [x for x in looks(m, Y) if not x[4]]
        if not L:
            continue
        t, P, p, st, touched, n = L[0]
        z = abs(m["k"] - st["y"]) / max(1e-6, st["sd"] * math.sqrt(max(1, n)))
        for key in (("dist", "<0.5" if z < 0.5 else "0.5-1" if z < 1 else "1-2" if z < 2 else "2+"),
                    ("side", m["hl"]), ("tenor", m["ten"] + "y"),
                    ("span", "month" if (dt.date.fromisoformat(m["p1"]) - dt.date.fromisoformat(m["p0"])).days < 40 else "long")):
            bk[key][0] += 1
            bk[key][1] += m["res"] == 1.0
            bk[key][2] += p
            bk[key][3] += P
    for k_, (n_, w, ps, Ps) in sorted(bk.items()):
        cuts += 1
        print(f"  {k_[0]:5s} {k_[1]:6s}: {n_:3d} rungs, {w:3d} paid ({w / n_:.2f}), first price {ps / n_:.2f}, model {Ps / n_:.2f}")
    if "noexam" not in a:
        tries = len(rules) + cuts
        for name in ("both sides, 10c gap", "Yes only, 10c gap", "No only, 10c gap", "both sides, 20c gap"):
            exam.score(res[name], f"Treasury yield ladders (Polymarket): {name}", tries=tries, src="tyield.py",
                       note="how high / how low Treasury yield vs a touch model on Treasury.gov par closes; finished spans")

if __name__ == "__main__":
    main()
