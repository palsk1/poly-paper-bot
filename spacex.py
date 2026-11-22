#!/usr/bin/env python3
"""Rocket launch count bets: "How many SpaceX launches in November?" (Kalshi KXSPACEXCOUNT and friends, Polymarket tag
spacex) against the public launch record. backtest/spacex.md.

  python3 spacex.py src       (probe spx_src: Jonathan McDowell's free launch list GCAT -> bt_cache/spx/launches.json.gz)
  python3 spacex.py report [log]
"""
import collections
import datetime as dt
import os
import sys

import backtest as bt

CACHE = os.path.join(bt.CACHE, "spx")
LP = os.path.join(CACHE, "launches.json.gz")
GCAT = ("https://planet4589.org/space/gcat/tsv/launch/launch.tsv", "https://planet4589.org/space/gcat/tsv/derived/launchlog.tsv")


def src():
    """Every launch since 2015 with its day, rocket, maker and result. GCAT dates look like '2025 Nov  3 0412:30'."""
    import urllib.request
    os.makedirs(CACHE, exist_ok=True)
    rows = []
    for url in GCAT:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "poly-paper-bot research (github.com/palsk1/poly-paper-bot)"})
            raw = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
        except Exception as e:
            print(url, "failed", str(e)[:200], flush=True)
            continue
        lines = [l for l in raw.split("\n") if l.strip()]
        head = lines[0].lstrip("#").split("\t")
        print(url, len(lines), "lines; columns:", head[:30], flush=True)
        for l in lines[1:6]:
            print("   ", l[:300], flush=True)
        col = {h.strip(): i for i, h in enumerate(head)}
        for l in lines[1:]:
            if l.startswith("#"):
                continue
            f = l.split("\t")
            g = lambda k: f[col[k]].strip() if k in col and col[k] < len(f) else ""
            d = parse_day(g("Launch_Date"))
            if not d or d < "2015-01-01":
                continue
            rows.append({"tag": g("Launch_Tag"), "day": d, "t": g("Launch_Date"), "lv": g("LV_Type"), "var": g("Variant"),
                         "ag": g("Agency"), "code": g("Launch_Code"), "site": g("Launch_Site"), "mis": g("Mission")[:60],
                         "cat": g("Category")})
        if rows:
            break
    bt.wjson(LP, {"src": url if rows else None, "rows": rows, "got": dt.datetime.now(dt.timezone.utc).isoformat()})
    c = collections.Counter((r["day"][:7], r["ag"]) for r in rows if r["day"] >= "2025-10")
    print("saved", len(rows), "launches; by month and maker (since Oct 2025):", sorted(c.items())[-40:], flush=True)
    print("codes:", collections.Counter(r["code"] for r in rows).most_common(12), "makers:", collections.Counter(r["ag"] for r in rows).most_common(12))
    print("rockets:", collections.Counter(r["lv"] for r in rows if r["day"] >= "2025").most_common(15))
    print("newest:", rows and sorted(rows, key=lambda r: r["day"])[-5:])


def parse_day(s):
    p = s.split()
    if len(p) < 3:
        return None
    try:
        return dt.date(int(p[0]), dt.datetime.strptime(p[1][:3], "%b").month, int(p[2].rstrip("?"))).isoformat()
    except ValueError:
        return None


# ================================================================ the test
import math
import re

import aim
import exam

TRIES = 120
STAKE = 10.0


def launch_times():
    """SpaceX launch times (UTC seconds) from the GCAT list. GCAT time 'HHMM' or 'HHMM:SS' after the date; noon if missing."""
    out = []
    for r in (bt.rjson(LP, {}) or {}).get("rows") or []:
        if r["ag"] != "SPX":
            continue
        p = r["t"].split()
        hh, mm = 12, 0
        if len(p) > 3 and p[3][:4].isdigit():
            hh, mm = int(p[3][:2]), int(p[3][2:4])
        y, mo, d = map(int, r["day"].split("-"))
        out.append(int(dt.datetime(y, mo, d, hh, mm, tzinfo=dt.timezone.utc).timestamp()))
    return sorted(out)


ET = dt.timezone(dt.timedelta(hours=-5))


def month_of(ts):
    return dt.datetime.fromtimestamp(ts, ET).strftime("%Y-%m")


def month_bounds(mon):
    y, m = map(int, mon.split("-"))
    a = dt.datetime(y, m, 1, tzinfo=ET)
    b = dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=ET)
    return int(a.timestamp()), int(b.timestamp())


def pois_gt(k, lam):
    """P(N > k) for N ~ Poisson(lam)."""
    if k < 0:
        return 1.0
    p, term = 0.0, math.exp(-lam)
    for i in range(int(k) + 1):
        p += term
        term *= lam / (i + 1)
    return max(0.0, 1.0 - p)


def model(T, mon, X, t, back=60):
    """Chance of more than X launches in the month: count so far + Poisson at the pace of the last `back` days."""
    a, b = month_bounds(mon)
    n = sum(1 for x in T if a <= x < t)
    rate = sum(1 for x in T if t - back * 86400 <= x < t) / back
    return pois_gt(X - n, rate * max(0.0, (b - t) / 86400)), n


def k_load():
    have = (bt.rjson(aim.MK, {}) or {}).get("markets") or {}
    ms = {}
    for t, m in have.items():
        if m["s"] != "KXSPACEXCOUNT" or re.search(r"-\d\d$", m["ev"]):   # monthly only, not the yearly total
            continue
        x = re.findall(r"[\d.]+", m["w"])
        if not x:
            continue
        m = dict(m)
        m["X"] = float(x[0])
        e = re.search(r"-(\d\d)([A-Z]{3})", m["ev"])      # the month is in the event name (26JAN); the close comes a day or more later
        m["mon"] = f"20{e.group(1)}-{dt.datetime.strptime(e.group(2), '%b').month:02d}"
        m["won"] = m["res"] == "yes"
        ms[t] = m
    tp = {}
    for tk, v in (bt.rjson(os.path.join(aim.CACHE, "ktapes_KXSPACEXCOUNT.json.gz"), {}) or {}).items():
        if tk not in ms:
            continue
        vals = [x for c in v["c"] for x in c[1:3] if x is not None]
        if vals and max(vals) <= 0.0101 and v["tr"]:
            for c in v["c"]:
                c[1] = None if c[1] is None else round(c[1] * 100, 4)
                c[2] = None if c[2] is None else round(c[2] * 100, 4)
        tp[tk] = v
    return ms, tp


def rows(ms, tp, T):
    out = []
    for k, m in ms.items():
        a, b = month_bounds(m["mon"])
        for c in (tp.get(k) or {}).get("c") or []:
            ts, bid, ask = c[0], c[1], c[2]
            if bid is None or ask is None or not 0 < ask < 1 or ask <= bid or ts >= m["close"] - 1800:
                continue
            p, n = model(T, m["mon"], m["X"], ts)
            out.append({"k": k, "t": ts, "bid": bid, "ask": ask, "pp": (bid + ask) / 2, "pm": p, "n": n, "X": m["X"],
                        "need": m["X"] + 1 - n, "dleft": (b - ts) / 86400, "won": m["won"], "ev": m["ev"]})
    out.sort(key=lambda r: r["t"])
    return out


def bets(ms, R, sel, yes, max_gap=0.15):
    out, seen = [], set()
    for r in R:
        if r["k"] in seen or r["ask"] - r["bid"] > max_gap or not sel(r):
            continue
        px = r["ask"] if yes else 1 - r["bid"]
        if not 0.03 <= px <= 0.97:
            continue
        seen.add(r["k"])
        sh = STAKE / (px + aim.k_fee(px))
        out.append({"ev": r["ev"], "t": r["t"], "cost": STAKE, "pay": sh if r["won"] == yes else 0.0, "px": px, "yes": yes, "id": r["k"],
                    "dleft": r["dleft"], "need": r["need"], "pm": r["pm"]})
    return out


def per100(b):
    c = sum(x["cost"] for x in b)
    return 100 * (sum(x["pay"] for x in b) - c) / c if c else 0.0


def usd(v):
    return ("+" if v >= 0 else "-") + f"${abs(v):.2f}"


HEAD = "| rule | bets | won | months | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |\n|---|---|---|---|---|---|---|---|---|"


def line(name, b, log):
    b = sorted(b, key=lambda x: x["t"])
    c = exam.score(b, name, tries=TRIES, log=log, quiet=True, status="dropped", src="spacex.py, backtest/spacex.md")
    h = len(b) // 2
    print(f"| {name} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {len({x['ev'] for x in b})} | {usd(per100(b)) if b else '-'} | "
          f"{usd(per100(b[:h])) if h else '-'} / {usd(per100(b[h:])) if h else '-'} | {c.get('lo100')} to {c.get('hi100')} | "
          f"{c.get('floor100')} | {c.get('verdict')} |", flush=True)
    return c


def cell(b, n=8):
    return f"{usd(per100(b))} ({len(b)}, {sum(1 for x in b if x['pay'] > 0)} won)" if len(b) >= n else f"- ({len(b)})"


def report(log=False):
    T = launch_times()
    ms, tp = k_load()
    R = rows(ms, tp, T)
    evs = sorted({m["ev"] for m in ms.values()})
    print(f"## The data\n\n- Kalshi KXSPACEXCOUNT, monthly: {len(ms)} finished 'more than X launches' markets in {len(evs)} months, "
          f"{sum(1 for k in ms if (tp.get(k) or {}).get('c'))} with hourly prices, {len(R)} hourly looks, "
          f"${sum(m['vol'] for m in ms.values()):,.0f} traded.")
    print(f"- Launch list: {len(T)} SpaceX launches in GCAT since 2015.\n")
    print("### Who forecasts better (Brier score, lower is better)\n\n| days left | looks | price | count + pace |\n|---|---|---|---|")
    for a, b in ((20, 40), (10, 20), (5, 10), (2, 5), (0, 2)):
        v = [r for r in R if a <= r["dleft"] < b]
        if len(v) >= 20:
            print(f"| {a}-{b} | {len(v)} | {sum((r['pp'] - r['won']) ** 2 for r in v) / len(v):.3f} | {sum((r['pm'] - r['won']) ** 2 for r in v) / len(v):.3f} |")
    print("\n### The tests\n\n$10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c, one bet per market at the first hour that fits.\n")
    print(HEAD)
    line("Yes where count + pace is 10c+ above the price", bets(ms, R, lambda r: r["pm"] - r["pp"] >= 0.10, True), log)
    line("No where count + pace is 10c+ below the price", bets(ms, R, lambda r: r["pp"] - r["pm"] >= 0.10, False), log)
    line("Yes where count + pace is 20c+ above the price", bets(ms, R, lambda r: r["pm"] - r["pp"] >= 0.20, True), log)
    line("No where count + pace is 20c+ below the price", bets(ms, R, lambda r: r["pp"] - r["pm"] >= 0.20, False), log)
    line("Same, 10c+, last 10 days only, Yes", bets(ms, R, lambda r: r["dleft"] < 10 and r["pm"] - r["pp"] >= 0.10, True), log)
    line("Same, 10c+, last 10 days only, No", bets(ms, R, lambda r: r["dleft"] < 10 and r["pp"] - r["pm"] >= 0.10, False), log)
    line("Always Yes, first look", bets(ms, R, lambda r: True, True), log)
    line("Always No, first look", bets(ms, R, lambda r: True, False), log)
    print("\n### Prices alone (per $100, bets, won)\n\n| price | side | 10+ days left | 3-10 days | last 3 days |\n|---|---|---|---|---|")
    for lo, hi in ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97)):
        for yes in (True, False):
            cs = [cell(bets(ms, R, lambda r, lo=lo, hi=hi, a=a, b=b: lo <= r["pp"] < hi and a <= r["dleft"] < b, yes)) for a, b in ((10, 99), (3, 10), (0, 3))]
            print(f"| {lo * 100:.0f}-{hi * 100:.0f}c | {'Yes' if yes else 'No'} | " + " | ".join(cs) + " |")
    backward(ms, R, log)
    poly(log)
    return ms, tp, R, T


def backward(ms, R, log):
    b = bets(ms, R, lambda r: r["dleft"] >= 10 and 0.10 <= r["pp"] < 0.97, False)
    by = collections.defaultdict(list)
    for x in b:
        by[x["ev"]].append(x)
    ahead = sum(1 for v in by.values() if sum(x["pay"] - x["cost"] for x in v) > 0)
    print("\n### Backward look\n\nThe table above says No paid early in the month at every price. Month by month it is a coin toss:\n")
    print(HEAD)
    line("No at 10-97c with 10+ days left", b, log)
    print(f"\nAhead in {ahead} of {len(by)} months; " + ", ".join(f"{e.split('-')[1]} {usd(sum(x['pay'] - x['cost'] for x in v))}"
                                                     for e, v in sorted(by.items(), key=lambda kv: min(x['t'] for x in kv[1]))) + ".")


def poly(log):
    """Polymarket's own monthly SpaceX count lists (tag spacex): prices alone, first look a day after the list opens."""
    import families
    import stocks
    ms, tp = families.load("spacex")
    ms = {k: m for k, m in ms.items() if re.search(r"How many SpaceX launches in [A-Z][a-z]+( \d{4})?\?", str(m.get("title"))) and (tp.get(k) or {}).get("b")}
    out = {True: [], False: []}
    for k, m in ms.items():
        t = (m.get("start") or 0) + 86400
        pp = stocks._price(tp[k]["b"], t, fresh=7 * 86400)
        for yes in (True, False):
            x = aim.buy(m, tp[k]["b"], t, yes, pp=pp) if pp is not None else None
            if x:
                out[yes].append(x)
    print(f"\n### Polymarket check\n\n{len(ms)} markets in {len({m['ev_slug'] for m in ms.values()})} monthly lists with real trades "
          "(small: most lists trade under $10,000). $10 at the worst price of the next 2 hours + 2c + fee, a day after the list opens.\n")
    print(HEAD)
    line("Polymarket: always Yes, a day in", out[True], log)
    line("Polymarket: always No, a day in", out[False], log)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "src":
        src()
    elif cmd == "report":
        report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
