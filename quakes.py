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


# ================================================================ the test
OUT = "backtest/quakes.md"
TRIES = 70                 # versions looked at in this dig
MON = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}
LAGS = (1800, 7200)        # how long after a quake we assume to know about it
MIRROR_USD = 25.0          # 5-minute steps under this many dollars that sit at the mirror of the last price are dropped
NEAR = 0.15                # a buy price more than this from the last real price is thrown out (wrong-side trades, see Traps)


def _et(s, year):
    from zoneinfo import ZoneInfo
    m = re.search(r"([A-Z][a-z]+) (\d{1,2})(?:, (\d{4}))?,? (\d{1,2}):(\d{2}) ?([AP]M) ET", s)
    if not m or m.group(1).lower() not in MON:
        return None
    h = int(m.group(4)) % 12 + (12 if m.group(6) == "PM" else 0)
    return dt.datetime(int(m.group(3) or year), MON[m.group(1).lower()], int(m.group(2)), h, int(m.group(5)),
                       tzinfo=ZoneInfo("America/New_York")).timestamp()


def parse(m):
    """What a market asks: kind 'count' (how many quakes of `mag`+ between a and b: lo..hi) or 'big' (the day's biggest
    quake between lo and hi). None when the question is another kind ("another 7.0 by...", "megaquake")."""
    q, d = m["q"], m.get("desc") or ""
    mb = re.search(r"biggest earthquake on ([A-Z][a-z]+) (\d+), (\d{4}) be (under ([\d.]+)|([\d.]+) to ([\d.]+)|([\d.]+) or more)", q)
    if mb and mb.group(1).lower() in MON:
        day = dt.datetime(int(mb.group(3)), MON[mb.group(1).lower()], int(mb.group(2)), tzinfo=dt.timezone.utc).timestamp()
        if mb.group(5):
            lo, hi = 0.0, float(mb.group(5)) - 0.1
        elif mb.group(8):
            lo, hi = float(mb.group(8)), 99.0
        else:
            lo, hi = float(mb.group(6)), float(mb.group(7))
        return {"kind": "big", "a": day, "b": day + 86400, "lo": lo, "hi": hi}
    mm = re.search(r"between (.+?ET),? and (.+?ET)", d)
    mg = re.search(r"of (?:magnitude )?([\d.]+) or (?:higher|above)", q)
    if not mm or not mg:
        return None
    yr = time.gmtime(m["end"]).tm_year
    a, b = _et(mm.group(1), yr), _et(mm.group(2), yr)
    if a and b and a > b:
        a = _et(mm.group(1), yr - 1)
    if not a or not b:
        return None
    for rx, f in ((r"exactly (\d+)", lambda n: (n, n)), (r"more than (\d+)", lambda n: (n + 1, 999)), (r"(\d+) or fewer", lambda n: (0, n)),
                  (r"≤(\d+)", lambda n: (0, n)), (r"(\d+) or more", lambda n: (n, 999)), (r"(\d+)\+ earthquakes", lambda n: (n, 999)),
                  (r"be (\d+) earthquakes? of", lambda n: (n, n))):
        x = re.search(rx, q)
        if x:
            lo, hi = f(int(x.group(1)))
            return {"kind": "count", "a": a, "b": b + 60, "mag": float(mg.group(1)), "lo": lo, "hi": hi}
    return None


class Cat:
    """The USGS list, with fast 'quakes between a and b' and the usual pace of quakes of a size."""

    def __init__(self, rows):
        import bisect
        self.rows = sorted(rows)
        self.T = [c[0] for c in self.rows]
        self._bis = bisect.bisect_left
        self._rate = {}

    def window(self, a, b):
        return self.rows[self._bis(self.T, a):self._bis(self.T, b)]

    def rate(self, x, t, years=3):
        """Quakes of x+ per second over the `years` before t (only what was known by then)."""
        k = (round(x, 2), int(t // 86400))
        if k not in self._rate:
            span = years * 365 * 86400.0
            self._rate[k] = sum(1 for c in self.window(t - span, t) if c[1] >= x - 1e-9) / span
        return self._rate[k]


def pois_cdf(n, mu):
    if n < 0:
        return 0.0
    s = term = math.exp(-mu)
    for i in range(1, int(n) + 1):
        term *= mu / i
        s += term
    return min(1.0, s)


def model(p, t, cat, lag=1800):
    """Fair chance of Yes at time t: what has happened so far (known `lag` seconds late) + the usual pace for the rest."""
    a, b = p["a"], p["b"]
    seen = cat.window(a, max(a, min(t - lag, b)))
    rem = max(0.0, b - max(a, t - lag))
    if p["kind"] == "count":
        n0 = sum(1 for c in seen if c[1] >= p["mag"] - 1e-9)
        mu = cat.rate(p["mag"], a) * rem
        if p["hi"] - n0 < 0:
            return 0.0
        return pois_cdf(min(p["hi"] - n0, 400), mu) - pois_cdf(p["lo"] - n0 - 1, mu)
    mx = round(max((c[1] for c in seen), default=0), 1)
    up = (1.0 if mx <= p["hi"] + 1e-9 else 0.0) * math.exp(-cat.rate(p["hi"] + 0.05, a) * rem) if p["hi"] < 90 else 1.0
    dn = (1.0 if mx < p["lo"] - 1e-9 else 0.0) * math.exp(-cat.rate(p["lo"] - 0.05, a) * rem) if p["lo"] > 0 else 0.0
    return max(0.0, up - dn)


def close_call(p, t, cat):
    """True when a quake so far sits within 0.1 of a line that matters: USGS often revises a magnitude by 0.1 in the
    first day, and this list only has the final numbers."""
    seen = cat.window(p["a"], max(p["a"], min(t, p["b"])))
    if p["kind"] == "count":
        return any(abs(c[1] - p["mag"]) <= 0.1 + 1e-9 for c in seen)
    mx = max((c[1] for c in seen), default=0)
    return any(abs(mx - e) <= 0.1 + 1e-9 for e in (p["lo"], p["hi"] + 0.1) if 0 < e < 90)


def load():
    import stocks
    ms = bt.rjson(os.path.join(CACHE, "markets.json.gz"))
    cat = Cat(bt.rjson(os.path.join(CACHE, "usgs.json.gz")))
    tp, i = {}, 0
    while os.path.exists(os.path.join(CACHE, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(CACHE, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    n_mirror = 0
    for v in tp.values():
        keep = []
        for x in v.get("b") or []:
            if x[5] < stocks.MIN_PRINT:
                continue
            if keep and x[5] < MIRROR_USD and abs(x[2] - keep[-1][2]) > 0.3 and abs(x[2] - (1 - keep[-1][2])) < 0.08:
                n_mirror += 1                               # a small trade at the mirror of the last price: booked on the wrong side
                continue
            keep.append(x)
        v["b"] = keep
    P, n_fin, n_un, n_bad = {}, 0, 0, 0
    for k, m in ms.items():
        if m["final"] not in ([1.0, 0.0], [0.0, 1.0]):
            continue
        n_fin += 1
        p = parse(m)
        if not p:
            n_un += 1
            continue
        w = cat.window(p["a"], p["b"])
        if p["kind"] == "count":
            n = sum(1 for c in w if c[1] >= p["mag"] - 1e-9)
            yes = p["lo"] <= n <= p["hi"]
        else:
            mx = round(max((c[1] for c in w), default=0), 1)
            yes = p["lo"] - 1e-9 <= mx <= p["hi"] + 1e-9
        if yes == (m["final"][0] == 1.0):
            P[k] = p
        else:
            n_bad += 1
    return ms, tp, cat, P, {"finished": n_fin, "other": n_un, "off": n_bad, "mirror": n_mirror}


def series(ms, tp, cat, P, step=3600, fresh=6 * 3600):
    """Every market hour by hour: (t, share of the window gone, last real price, model at each lag, close call?)."""
    import stocks
    S = {}
    for k, p in P.items():
        m = ms[k]
        b = (tp.get(k) or {}).get("b")
        if not b:
            continue
        t = math.ceil(max((m["start"] or 0) + 3600, p["a"] - 0.2 * (p["b"] - p["a"])) / step) * step
        rows = []
        while t < p["b"] - 1800:
            pp = stocks._price(b, t, fresh=fresh)
            if pp is not None:
                rows.append((t, (t - p["a"]) / (p["b"] - p["a"]), pp, tuple(model(p, t, cat, lag) for lag in LAGS), close_call(p, t, cat)))
            t += step
        if rows:
            S[k] = rows
    return S


def gap_bets(ms, tp, P, S, gap=0.20, lag=1, window=900, extra=0.02, kinds=None, side=None, lo=0.05, hi=0.95, fmin=-1, fmax=2,
             no_close=False, keep=None, near=NEAR):
    """One bet per market: the first hour where the model and the price are `gap` apart, on the side the model calls cheap."""
    import stocks
    out = []
    for k, rows in S.items():
        p = P[k]
        if kinds and p["kind"] not in kinds:
            continue
        for t, f, pp, pm, cc in rows:
            if not fmin <= f <= fmax or abs(pm[lag] - pp) < gap or (no_close and cc):
                continue
            yes = pm[lag] > pp
            if side is not None and yes != side:
                continue
            if keep and not keep(p, f, pp, pm[lag], yes):
                continue
            x = stocks.buy(ms[k], tp[k]["b"], t, yes, extra, lo=lo, hi=hi, window=window)
            if x and abs(x["px"] - (pp if yes else 1 - pp)) > near:
                continue                                   # a "price" that far from the last one is a trade booked on the wrong side
            if x and (pm[lag] if yes else 1 - pm[lag]) - x["px"] >= gap / 2:
                x.update(pm=pm[lag], pp=pp, f=f, kind=p["kind"])
                out.append(x)
                break
    return out


def blind_bets(ms, tp, P, S, sel, yes, window=900, extra=0.02, lo=0.03, hi=0.97, near=NEAR):
    """Price only, one bet per market: the first hour where sel(p, share gone, price) holds."""
    import stocks
    out = []
    for k, rows in S.items():
        for t, f, pp, pm, cc in rows:
            if sel(P[k], f, pp):
                x = stocks.buy(ms[k], tp[k]["b"], t, yes, extra, lo=lo, hi=hi, window=window)
                if x and abs(x["px"] - (pp if yes else 1 - pp)) <= near:
                    x.update(f=f, kind=P[k]["kind"])
                    out.append(x)
                    break
    return out


def run():
    import json
    import statistics
    import btcheck
    import earn
    import exam
    ms, tp, cat, P, n = load()
    S = series(ms, tp, cat, P)
    G = lambda **kw: gap_bets(ms, tp, P, S, **kw)
    B = lambda sel, yes, **kw: blind_bets(ms, tp, P, S, sel, yes, **kw)
    cell = lambda b: f"{earn.usd(earn.per100(b))} ({len(b)})" if len(b) >= 15 else f"- ({len(b)})"
    L = []
    W = L.append
    W("# Earthquake markets against a counting model (quakes.py)\n")
    W(f"Generated {bot.iso()}. Paper only. The holdout from {btcheck.HOLDOUT_FROM} is not in here.\n")
    W("\"How many earthquakes of 6.5 or stronger this week?\" and \"How big will today's biggest earthquake be?\" Polymarket has "
      f"run these since October 2025: {n['finished']} finished markets. {n['other']} ask something else (\"another 7.0 by...\") and are "
      f"left out. The USGS earthquake list ({len(cat.rows):,} quakes of 4.5+ since 2021) reproduces the result of {len(P)} of the rest; "
      f"{n['off']} don't match, because USGS changed a magnitude after the market closed. {len(S)} markets in "
      f"{len({ms[k]['ev_slug'] for k in S})} events have real trades; the middle one saw about ${statistics.median(ms[k]['vol'] for k in S):,.0f}.\n")
    W("## The idea\n")
    W("Big earthquakes come at a steady average pace and don't follow the news. So \"what has happened so far + the usual pace "
      "(last 3 years) for the time left\" gives a fair chance for every bracket, hour by hour. Is the price ever far from it?\n")
    W("## Who forecasts better?\n")
    W("Score = average squared miss, smaller is better. Model knows each quake 30 minutes late.\n")
    W("| share of the window gone | kind | markets | the model | Polymarket |")
    W("|---|---|---|---|---|")
    for kind, nm in (("count", "how many this week"), ("big", "biggest of the day")):
        for fa, fb in ((-1, 0), (0, .25), (.25, .5), (.5, .75), (.75, 2)):
            R = []
            for k, rows in S.items():
                if P[k]["kind"] != kind:
                    continue
                r = next((r for r in rows if fa <= r[1] < fb), None)
                if r:
                    R.append((r[3][0], r[2], ms[k]["final"][0]))
            if len(R) >= 40:
                W(f"| {'before the start' if fb == 0 else f'{max(fa, 0) * 100:.0f} to {min(fb, 1) * 100:.0f} in 100'} | {nm} | {len(R)} | "
                  f"{sum((a - y) ** 2 for a, b, y in R) / len(R):.4f} | {sum((b - y) ** 2 for a, b, y in R) / len(R):.4f} |")
    W("\nAbout a tie early on; the model is a little better late in the window. But it reads the final USGS numbers, and live "
      "magnitudes are often revised by 0.1 in the first day, so part of that is hindsight.\n")
    W("## Buying where the two disagree\n")
    W("One $10 bet per market: the first hour where the model and the last real price are that far apart, on the side the model "
      "calls cheap, only if it is still cheap at the price paid. Fee included.\n")
    W(earn.HEAD)
    for lag in (0, 1):
        for win_, extra, nm in ((900, .02, "worst price of the next 15 min + 2c"), (7200, .01, "worst price of the next 2 hours + 1c")):
            for gap in (.10, .20, .30):
                W(earn.line(f"{gap * 100:.0f}c+ apart, quakes known {LAGS[lag] // 60} min late, {nm}", G(gap=gap, lag=lag, window=win_, extra=extra)))
    main = G(gap=.20)
    wide = G(gap=.10)
    safe = G(gap=.20, no_close=True)
    W(earn.line("20c+, 2 hours late, 15 min + 2c, no quake within 0.1 of a line so far", safe))
    for kind, nm in (("count", "how many this week"), ("big", "biggest of the day")):
        for side in (True, False):
            W(earn.line(f"10c+, {nm}, buying {'Yes' if side else 'No'}", G(gap=.10, kinds=(kind,), side=side)))
    for a, b, nm in ((0, .33, "first third of the window"), (.33, .66, "middle third"), (.66, 2, "last third")):
        W(earn.line(f"10c+, {nm}", G(gap=.10, fmin=a, fmax=b)))
    top = sorted(main, key=lambda x: -(x["pay"] - x["cost"]))
    tot = sum(x["pay"] - x["cost"] for x in main)
    t3 = sum(x["pay"] - x["cost"] for x in top[:3])
    W(f"\nThe 20c+ rows look great and are not. The main version (20c+, quakes known 2 hours late, 15 min + 2c) made "
      f"{earn.usd(tot)} in total on {len(main)} bets, and its 3 best bets made {earn.usd(t3)} of that; the other {len(main) - 3} "
      f"together made {earn.usd(tot - t3)}. The best one: \"{ms[top[0]['id']]['q']}\", {'Yes' if top[0]['yes'] else 'No'} bought at "
      f"{top[0]['px'] * 100:.0f}c while the model said that side was worth {(top[0]['pm'] if top[0]['yes'] else 1 - top[0]['pm']) * 100:.0f}c. "
      "Looked at one by one, these big wins are not real chances: either the trade list shows trades on the wrong side "
      "(a market at 2c that still \"trades\" at 87c hours after the quake), or the price fits a quake count that USGS changed later. "
      "A live bot would not have got those prices. At 10c+ apart the first half of the year is ahead and the second half is behind, at either buy price.\n")
    W("## The prices alone (the comb)\n")
    W("No model. One $10 bet per market the first time its price is in the band, at the worst price of the next 15 minutes + 2c. Per $100 (bets).\n")
    bands = ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97))
    W("| when | side | " + " | ".join(f"Yes at {a * 100:.0f}-{b * 100:.0f}c" for a, b in bands) + " |")
    W("|---|---|" + "---|" * len(bands))
    for nm, fa, fb in (("first third", 0, .33), ("middle third", .33, .66), ("last third", .66, 2)):
        for yes in (True, False):
            W(f"| {nm} | {'Yes' if yes else 'No'} | " + " | ".join(cell(B(lambda p, f, pp, a=a, b=b: fa <= f < fb and a <= pp < b, yes)) for a, b in bands) + " |")
    W("")
    W(earn.HEAD)
    for nm, sel in (("\"exactly N\" brackets", lambda p: p["kind"] == "count" and p["lo"] == p["hi"] and p["hi"] > 0),
                    ("\"exactly 0\"", lambda p: p["kind"] == "count" and p["hi"] == 0),
                    ("\"more than N\"", lambda p: p["kind"] == "count" and p["hi"] > 900),
                    ("5.5+ counts", lambda p: p.get("mag") == 5.5), ("6.5+ counts", lambda p: p.get("mag") == 6.5),
                    ("biggest of the day", lambda p: p["kind"] == "big")):
        for yes in (True, False):
            W(earn.line(f"{nm}, always {'Yes' if yes else 'No'}", B(lambda p, f, pp: sel(p) and f >= 0, yes)))
    nolong = B(lambda p, f, pp: f >= .33 and .03 <= pp < .25, False)
    W(earn.line("No on long shots (Yes 3-25c), from the middle of the window on", nolong))
    W("\nYes buyers lose a lot, most on long shots ($20-65 per $100). No buyers get about their money back, never more. "
      "Following a 10-15c price jump loses $15-20 per $100 and betting against one is about even. Nothing to build on.\n")
    W("## The exam\n")
    for name, bb in (("Earthquake markets: buy where a counting model and the price are 20c+ apart", main),
                     ("Earthquake markets: same, 10c+ apart", wide),
                     ("Earthquake markets: No on long shots (Yes 3-25c), prices alone", nolong)):
        card = exam.score(bb, name, tries=TRIES, src="quakes.py, backtest/quakes.md", status="dropped", quiet=True)
        print("LEDGER ROW " + json.dumps(card))
        W(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {earn.usd(card.get('per100'))} per $100, "
          f"luck range {earn.usd(card.get('lo100'))} to {earn.usd(card.get('hi100'))}, worst case {earn.usd(card.get('floor100'))} per $100, "
          f"verdict **{card.get('verdict')}**.")
    W("\n**Verdict: dropped, no track.** The model is fine, the market is about as good, and the big wins are not real. "
      "The family is also small: about 2 events a week.\n")
    W("## Traps found\n")
    W("- **The USGS list is the final version.** Magnitudes move by 0.1 in the first day (the market waits 24 hours for that). "
      "A backtest that counts from the final list knows things nobody knew live. `close_call()` marks hours where a quake "
      "sits within 0.1 of a line.")
    W(f"- **Wrong-side trades again, and not only crumbs.** Right after a quake the trade list mixes Yes and No prices, in trades of $50 "
      f"and more. `load()` drops {n['mirror']} small steps that sit at the mirror of the last price, and buys more than "
      f"{NEAR * 100:.0f}c from the last price are thrown out, but some get through. Read the biggest wins one by one before believing a total.")
    W("- **Week windows are in US Eastern time**, written in the market's description, not the question.")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"fetch": fetch, "run": run}[cmd]()
