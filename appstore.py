#!/usr/bin/env python3
"""App Store bets: "Will ChatGPT be the #1 free app in the US App Store on November 7?" on Polymarket (tag app-store)
and Kalshi (KXAPPRANKFREE = #1, KXAPPRANKFREE2 = #2, daily). backtest/appstore.md.

Outside number: the bets settle on Apple's own chart, and the past bets themselves tell us which app was #1 every day
(Kalshi from Nov 2024, Polymarket from 2025). Apple's live chart has no free history, so the "model" is the record:
how often the app that was #1 yesterday stays #1 today, by how many days in a row it has held the top.

  python3 appstore.py report [log]     (needs bt_cache/fam_app_store from probe famf_app-store and Kalshi tapes from aim_kall-app)
"""
import collections
import datetime as dt
import math
import os
import re
import sys

import aim
import backtest as bt
import exam
import families

ET = dt.timezone(dt.timedelta(hours=-5))
d10 = lambda t: dt.datetime.fromtimestamp(t, ET).strftime("%Y-%m-%d")
TRIES = 170        # cuts looked at: the price tables (both sites, holder / other, band x time, both sides) + the record tests + the backward look
STAKE = 10.0


def norm(name):
    """One key per app: 'Sora by OpenAI' = 'Sora', 'Threads, an Instagram app' = 'Threads'."""
    s = str(name or "").lower().replace("’", "'")
    s = re.split(r" by |:| - | – |,|\(", s)[0]
    return re.sub(r"[^a-z0-9]", "", s)[:14]


RANK_RX = re.compile(r"#(\d) (Free|Paid) App in the US Apple App Store on ([A-Z][a-z]+) (\d+)", re.I)
NY = None


def read_time(day):
    """The chart is read at 12:00 PM New York time on the day in the question."""
    global NY
    if NY is None:
        from zoneinfo import ZoneInfo
        NY = ZoneInfo("America/New_York")
    y, mo, d = map(int, day.split("-"))
    return int(dt.datetime(y, mo, d, 12, 0, tzinfo=NY).timestamp())


def p_load():
    """Polymarket 'which app is #N on day D' markets (free and paid charts) + real trades. Ladders ('out as #1 by') aside.
    Trap: the listed end is midnight UTC, but the chart is read at noon New York time, so the day comes from the question."""
    ms, tp = families.load("app-store")
    try:
        m2, t2 = families.load("ai")
        for k, m in m2.items():
            if RANK_RX.search(str(m.get("title"))) and k not in ms:
                ms[k], tp[k] = m, t2.get(k) or {}
    except Exception:
        pass
    out = {}
    for k, m in ms.items():
        r = RANK_RX.search(str(m.get("title")))
        if not r or not m.get("item"):
            continue
        try:
            mo = dt.datetime.strptime(r.group(3)[:3], "%b").month
        except ValueError:
            continue
        y = dt.datetime.fromtimestamp(m["end"], dt.timezone.utc).year
        day = dt.date(y, mo, int(r.group(4)))
        if (day - dt.datetime.fromtimestamp(m["end"], dt.timezone.utc).date()).days > 200:
            day = day.replace(year=y - 1)
        m["rank"], m["chart"], m["day"] = int(r.group(1)), r.group(2).lower(), day.isoformat()
        m["end"] = read_time(m["day"])
        m["app"] = norm(m["item"])
        m["won"] = m["final"][0] == 1.0
        out[k] = m
    return out, tp


def k_load():
    """Kalshi KXAPPRANKFREE (#1) / FREE2 (#2) settled markets + hourly real bid/ask (quotes 100 times too small repaired)."""
    import glob
    have = (bt.rjson(aim.MK, {}) or {}).get("markets") or {}
    ms = {}
    for t, m in have.items():
        if m["s"] not in ("KXAPPRANKFREE", "KXAPPRANKFREE2"):
            continue
        m = dict(m)
        m["rank"], m["chart"] = (1 if m["s"] == "KXAPPRANKFREE" else 2), "free"
        m["day"] = d10(m["close"] - 3600)
        m["app"] = norm(m["w"])
        m["won"] = m["res"] == "yes"
        ms[t] = m
    tp = {}
    for f in glob.glob(os.path.join(aim.CACHE, "ktapes_KXAPPRANK*.json.gz")):
        for tk, v in (bt.rjson(f, {}) or {}).items():
            if tk not in ms:
                continue
            vals = [x for c in v["c"] for x in c[1:3] if x is not None]
            if vals and max(vals) <= 0.0101 and v["tr"]:
                for c in v["c"]:
                    c[1] = None if c[1] is None else round(c[1] * 100, 4)
                    c[2] = None if c[2] is None else round(c[2] * 100, 4)
            tp[tk] = v
    return ms, tp


def history(P, K):
    """{(chart, rank): {day: app}} from every settled market on both sites."""
    H = collections.defaultdict(dict)
    clash = []
    for src in (K, P):
        for m in src.values():
            if m["won"]:
                key = (m["chart"], m["rank"])
                old = H[key].get(m["day"])
                if old and old != m["app"]:
                    clash.append((m["day"], key, old, m["app"]))
                    continue
                H[key][m["day"]] = m["app"]
    return dict(H), clash


def gap(d1, d0):
    return (dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days


def last_known(H, key, t):
    """The newest chart result public before time t: (day, app), or (None, None)."""
    best = None
    for d in H.get(key, {}):
        if read_time(d) + 600 <= t and (best is None or d > best):
            best = d
    return (best, H[key][best]) if best else (None, None)


GB = ((1, 1, "next day"), (2, 4, "2-4 days later"), (5, 8, "5-8 days later"), (9, 9999, "9+ days later"))


def gbin(g):
    for a, b, lab in GB:
        if a <= g <= b:
            return lab
    return "?"


def stay_pairs(H):
    """Every pair (an earlier known day, the next known day) per chart: did the same app stay on top?"""
    out = []
    for key, dd in H.items():
        ds = sorted(dd)
        for a, b in zip(ds, ds[1:]):
            out.append((b, key, gbin(gap(b, a)), dd[a] == dd[b]))
    return sorted(out)


def record(pairs, key, g, day):
    """The chance the holder is still there after g days, from pairs that finished before `day` (light prior to 75 in 100)."""
    lab = gbin(g)
    v = [s for d, k, gl, s in pairs if d < day and k == key and gl == lab]
    return (sum(v) + 3) / (len(v) + 4), len(v)


LOOKS = (144, 96, 72, 48, 24, 12, 6, 3, 1)      # hours before the chart is read


def row(m, key, t, h, pp, H, pairs, extra=None):
    kd, holder = last_known(H, key, t)
    if not holder or kd >= m["day"]:
        return None
    g = gap(m["day"], kd)
    inc = m["app"] == holder
    r = {"t": t, "h": h, "pp": pp, "inc": inc, "g": g, "rec": record(pairs, key, g, m["day"])[0] if inc else None,
         "won": m["won"], "day": m["day"], "app": m["app"], "chart": m["chart"], "rank": m["rank"]}
    if extra:
        r.update(extra)
    return r


def p_rows(ms, tp, H, pairs):
    """Each Polymarket market at each look: the last real price, whether it holds the spot at the last known reading, the record."""
    import stocks
    out = []
    for k, m in ms.items():
        b = (tp.get(k) or {}).get("b")
        if not b:
            continue
        for h in LOOKS:
            t = m["end"] - h * 3600
            if t < (m.get("start") or 0) + 1800:
                continue
            pp = stocks._price(b, t, fresh=24 * 3600)
            if pp is None:
                continue
            r = row(m, (m["chart"], m["rank"]), t, h, pp, H, pairs, {"k": k})
            if r:
                out.append(r)
    out.sort(key=lambda r: r["t"])
    return out


def p_bets(ms, tp, rows, sel, yes):
    out, seen = [], set()
    for r in rows:
        if r["k"] in seen or not sel(r):
            continue
        seen.add(r["k"])
        x = aim.buy(ms[r["k"]], tp[r["k"]]["b"], r["t"], yes, pp=r["pp"], window=3600)
        if x:
            x.update(h=r["h"], pp=r["pp"], inc=r["inc"], day=r["day"], app=r["app"], chart=r["chart"], rank=r["rank"], g=r["g"])
            out.append(x)
    return out


def k_rows(ms, tp, H, pairs):
    out = []
    for k, m in ms.items():
        v = tp.get(k)
        if not v:
            continue
        for c in v["c"]:
            ts, bid, ask = c[0], c[1], c[2]
            if bid is None or ask is None or not 0 < ask < 1 or ask <= bid or ts >= m["close"] - 1800:
                continue
            r = row(m, (m["chart"], m["rank"]), ts, (m["close"] - ts) / 3600, (bid + ask) / 2, H, pairs, {"k": k, "bid": bid, "ask": ask})
            if r:
                out.append(r)
    out.sort(key=lambda r: r["t"])
    return out


def k_bets(ms, rows, sel, yes, max_gap=0.15):
    out, seen = [], set()
    for r in rows:
        if r["k"] in seen or r["ask"] - r["bid"] > max_gap or not sel(r):
            continue
        px = r["ask"] if yes else 1 - r["bid"]
        if not 0.03 <= px <= 0.97:
            continue
        seen.add(r["k"])
        n = STAKE / (px + aim.k_fee(px))
        out.append({"ev": ms[r["k"]]["ev"], "t": r["t"], "cost": STAKE, "pay": n if r["won"] == yes else 0.0, "px": px, "yes": yes,
                    "id": r["k"], "h": r["h"], "inc": r["inc"], "day": r["day"], "app": r["app"], "chart": r["chart"], "rank": r["rank"], "g": r["g"]})
    return out


def per100(b):
    c = sum(x["cost"] for x in b)
    return 100 * (sum(x["pay"] for x in b) - c) / c if c else 0.0


def usd(v):
    return ("+" if v >= 0 else "-") + f"${abs(v):.2f}"


def cell(b, n=12):
    return f"{usd(per100(b))} ({len(b)}, {sum(1 for x in b if x['pay'] > 0)} won)" if len(b) >= n else f"- ({len(b)})"


def line(name, b, log, tries=TRIES, status="dropped"):
    b = sorted(b, key=lambda x: x["t"])
    c = exam.score(b, name, tries=tries, log=log, quiet=True, status=status, src="appstore.py, backtest/appstore.md")
    h = len(b) // 2
    print(f"| {name} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b)) if b else '-'} | "
          f"{usd(per100(b[:h])) if h else '-'} / {usd(per100(b[h:])) if h else '-'} | "
          f"{c.get('lo100')} to {c.get('hi100')} | {c.get('floor100')} | {c.get('verdict')} |", flush=True)
    return c


HEAD = "| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |\n|---|---|---|---|---|---|---|---|"


def tables(P, tpP, K, tpK):
    H, clash = history(P, K)
    pairs = stay_pairs(H)
    return H, clash, pairs, p_rows(P, tpP, H, pairs), k_rows(K, tpK, H, pairs)


def report(log=False):
    P, tpP = p_load()
    K, tpK = k_load()
    H, clash, pairs, prow, krow = tables(P, tpP, K, tpK)
    span = lambda v: f"{min(m['day'] for m in v)} to {max(m['day'] for m in v)}" if v else "-"
    print("## The data\n")
    print(f"- Polymarket: {len(P)} finished app markets in {len({m['ev_slug'] for m in P.values()})} lists (free and paid chart, #1 and #2), "
          f"{sum(1 for k in P if (tpP.get(k) or {}).get('b'))} with real trades, {span(list(P.values()))}, usually one list a week.")
    print(f"- Kalshi: {len(K)} finished markets (#1 and #2 of the free chart, daily), {sum(1 for k in K if (tpK.get(k) or {}).get('c'))} with hourly prices, {span(list(K.values()))}.")
    print(f"- Known chart results: " + ", ".join(f"{c} #{r} {len(v)} days" for (c, r), v in sorted(H.items())) + f"; the sites disagree on {len(clash)} days.\n")
    st = collections.defaultdict(lambda: [0, 0])
    for d, key, g, sty in pairs:
        st[(key, g)][0] += sty
        st[(key, g)][1] += 1
    print("### How often the app on top at the last reading is still there\n\n| chart | next reading | pairs | still there |\n|---|---|---|---|")
    for (key, g), v in sorted(st.items()):
        if v[1] >= 5:
            print(f"| {key[0]} #{key[1]} | {g} | {v[1]} | {v[0]} ({100 * v[0] / v[1]:.0f} in 100) |")
    print()
    for key in sorted(H):
        if len(H[key]) >= 10:
            print(f"- most days at {key[0]} #{key[1]}: " + ", ".join(f"{a} {n}" for a, n in collections.Counter(H[key].values()).most_common(8)))
    print("\n### Who forecasts better: the price or the record (the app holding the spot at the last reading)\n")
    print("Brier score, lower is better.\n\n| site | hours before the reading | looks | price | record | held on |\n|---|---|---|---|---|---|")
    for site, rows in (("Polymarket", prow), ("Kalshi", krow)):
        for a, b in ((72, 999), (24, 72), (6, 24), (0, 6)):
            v = [r for r in rows if r["inc"] and a <= r["h"] < b]
            if len(v) >= 10:
                print(f"| {site} | {a}-{b if b < 999 else ''} | {len(v)} | {sum((r['pp'] - r['won']) ** 2 for r in v) / len(v):.3f} | "
                      f"{sum((r['rec'] - r['won']) ** 2 for r in v) / len(v):.3f} | {sum(r['won'] for r in v)} |")
    PB = lambda s, y: p_bets(P, tpP, prow, s, y)
    KB = lambda s, y: k_bets(K, krow, s, y)
    print("\n### The tests\n\nPolymarket: $10 at the worst price anyone paid in the next hour (never better than the price seen) + 2c + fee. "
          "Kalshi: $10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c. One bet per market, first look that fits.\n")
    print(HEAD)
    for site, B in (("Polymarket", PB), ("Kalshi", KB)):
        line(f"{site}: Yes on the holder where the record is 10c+ above the price", B(lambda r: r["inc"] and r["rec"] - r["pp"] >= 0.10, True), log)
        line(f"{site}: No on the holder where the record is 10c+ below the price", B(lambda r: r["inc"] and r["pp"] - r["rec"] >= 0.10, False), log)
        line(f"{site}: always Yes on the holder, first look", B(lambda r: r["inc"], True), log)
        line(f"{site}: always No on the holder, first look", B(lambda r: r["inc"], False), log)
        line(f"{site}: always Yes on any other app, first look", B(lambda r: not r["inc"], True), log)
        line(f"{site}: always No on any other app, first look", B(lambda r: not r["inc"], False), log)
    print("\n### Prices alone (per $100, bets, won)\n")
    for site, B in (("Polymarket", PB), ("Kalshi", KB)):
        for who, f in (("the holder", lambda r: r["inc"]), ("other apps", lambda r: not r["inc"])):
            print(f"\n**{site}, {who}**\n\n| price | side | 24h+ before | 6-24h | under 6h |\n|---|---|---|---|---|")
            for lo, hi in ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97)):
                for yes in (True, False):
                    cs = [cell(B(lambda r, lo=lo, hi=hi, a=a, b=b: f(r) and lo <= r["pp"] < hi and a <= r["h"] < b, yes))
                          for a, b in ((24, 999), (6, 24), (0, 6))]
                    print(f"| {lo * 100:.0f}-{hi * 100:.0f}c | {'Yes' if yes else 'No'} | " + " | ".join(cs) + " |")
    backward(P, tpP, K, prow, krow, log)
    return P, tpP, K, tpK, H, pairs, prow, krow


def top_share(b, n=10):
    tot = sum(x["pay"] - x["cost"] for x in b)
    top = sum(sorted((x["pay"] - x["cost"] for x in b), reverse=True)[:n])
    return tot, top


def backward(P, tpP, K, prow, krow, log):
    """From the upsets back: the app priced as the favourite 1-2 days ahead loses more often than its price says."""
    PB = lambda s, y: p_bets(P, tpP, prow, s, y)
    KB = lambda s, y: k_bets(K, krow, s, y)
    fav = lambda r: 0.5 <= r["pp"] < 0.97 and r["h"] >= 24
    print("\n### Backward look: what came before the upsets\n")
    print("On Kalshi the app priced at 50-97c a day or two before the reading lost more often than its price said, "
          "most of all on the #2 spot. Found by looking at the tables above. The fresh check is Polymarket's own #1 and #2 lists (Oct 2025 to Nov 2026), "
          "which the Kalshi rule never saw, but whose price tables were already on screen.\n")
    print(HEAD)
    rules = [("Kalshi: No on the favourite (50-97c) 24h+ before", KB(fav, False)),
             ("Kalshi: No on the favourite 24h+ before, #1 spot", KB(lambda r: fav(r) and r["rank"] == 1, False)),
             ("Kalshi: No on the favourite 24h+ before, #2 spot", KB(lambda r: fav(r) and r["rank"] == 2, False)),
             ("Kalshi: No on the favourite 6-24h before", KB(lambda r: 0.5 <= r["pp"] < 0.97 and 6 <= r["h"] < 24, False)),
             ("Kalshi: Yes on the favourite 24h+ before", KB(fav, True)),
             ("Polymarket check: No on the favourite 24h+ before", PB(fav, False)),
             ("Polymarket check: No on the favourite 24h+ before, #2 spot", PB(lambda r: fav(r) and r["rank"] == 2, False)),
             ("Polymarket check: No on the favourite 6-24h before", PB(lambda r: 0.5 <= r["pp"] < 0.97 and 6 <= r["h"] < 24, False))]
    for name, b in rules:
        line(name, b, log)
    print()
    for name, b in (rules[0], rules[5]):
        tot, top = top_share(b)
        print(f"- {name}: profit ${tot:.0f} in all, the 10 best bets made ${top:.0f} (more than all of it: long-shot No bets at 5-15c that came in).")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
