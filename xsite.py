#!/usr/bin/env python3
"""Kalshi vs Polymarket on the SAME non-sports question: follow the leader? (27 Nov 2026). Research only.
PAPER ONLY. Reads public history, never trades, never writes state/.

The question (Jan: "go crazy", coordinator: "follow the leader, not arbitrage"): when one question (politics,
economy, weather, culture, ...) is listed on both sites and the two prices differ, does one site's price know the
winner better? And when one site moves first, does the other follow, late enough for a slow bot to buy?
Sports arb (~$1.04 a pair) and the 15-minute crypto pairs (~$1.05) were dropped before and are not redone here.

    python3 xsite.py klist        # probe xs_klist: every settled non-sports Kalshi market, 1 Mar-9 Nov (resumable)
    python3 xsite.py match        # offline: pair them with bt_cache Polymarket markets -> bt_cache/xs/pairs.json.gz
    python3 xsite.py tapes        # probe xs_tapes: hourly Kalshi bid/ask + every Polymarket trade for each pair
    python3 xsite.py run          # offline: report backtest/xsite.md

Data: bt_cache/xs/ in the shared price store. Markets ending on/after 10 Nov (the holdout) stay out.
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import khouse
import launch
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "xs")
DAY = 86400
FIRST, LAST = "2026-03-01", "2026-11-09"
T0 = time.time()
BUDGET_MIN = float(os.environ.get("XS_MIN", "270"))
rj, wj, tsec = khouse.rj, khouse.wj, khouse.tsec


def left():
    return BUDGET_MIN - (time.time() - T0) / 60


# ================================================================ Kalshi list
SKIP_CAT = {"Sports", "Crypto", "Mentions"}   # sports arb and crypto pairs were dug before; mentions cross is in kmentions.py


def klist():
    """Every settled market of every non-sports Kalshi series, closing 1 Mar-9 Nov. By series, because
    /historical/markets ignores the close-time filters (found 27 Nov: a day-by-day list read 400,000 rows a day
    and kept none). Resumable: finished series are kept in bt_cache/xs/kser.json.gz."""
    import kmentions
    path = os.path.join(CACHE, "kser.json.gz")
    done = rj(path, {}) or {}
    ser = yesno.kget("/series", {}).get("series") or []
    pick = {x["ticker"]: x for x in ser if x.get("ticker") and x.get("category") not in SKIP_CAT}
    todo = sorted(t for t in pick if t not in done)
    print(f"series {len(ser)}, non-sports {len(pick)}, already listed {len(done)}, to list {len(todo)}", flush=True)
    a, b = tsec(FIRST), tsec(LAST) + DAY
    ex = ThreadPoolExecutor(int(os.environ.get("XS_WORKERS", "6")))
    futs = [ex.submit(kmentions.series_markets, t) for t in todo]
    n = 0
    for f in futs:
        if left() < 6:
            break
        t, ok, nrows = f.result()
        cat = pick[t].get("category")
        done[t] = [dict(m, q=(m["q"] + " " + m["w"]).strip()[:200], cat=cat) for m in ok.values()
                   if a <= m["close"] < b and m["vol"] >= 100]
        n += 1
        if n % 200 == 0:
            wj(path, done)
            print(f"  {len(done)} series listed ({(time.time() - T0) / 60:.0f} min)", flush=True)
    ex.shutdown(wait=False, cancel_futures=True)
    wj(path, done)
    allm = {m["t"]: m for v in done.values() for m in v}
    wj(os.path.join(CACHE, "kmarkets.json.gz"), allm)
    c = collections.Counter(m["cat"] for m in allm.values())
    print(f"kalshi non-sports settled markets 1 Mar-9 Nov: {len(allm)} from {len(done)} series; by category: {dict(c.most_common())}")
    if len(done) < len(pick):
        print("not finished: run again to resume")


# ================================================================ pairing
HOLD = tsec("2026-11-10")
PAIRS = os.path.join(ROOT, "backtest", "xs_pairs.json.gz")     # in git, so a probe on the branch can read it
TOL = 2 * DAY          # Polymarket end within 2 days of Kalshi's close or planned expiry
MIN_SCORE = float(os.environ.get("XS_SCORE", "0.55"))


def nums(txt):
    return bot.sig_numbers(re.sub(r"[°%$]", " ", str(txt or "")))


MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
_MD = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\b")
CITY = {"NY": "new york|nyc", "NYC": "new york|nyc", "CHI": "chicago", "MIA": "miami", "AUS": "austin",
        "DEN": "denver", "LAX": "los angeles", "PHIL": "philadelphia", "HOU": "houston", "SAN": "san antonio",
        "NOLA": "new orleans", "ATL": "atlanta", "BOS": "boston", "MIN": "minneapolis", "PHX": "phoenix",
        "LV": "las vegas", "EWR": "newark", "SEA": "seattle", "DAL": "dallas", "OKC": "oklahoma",
        "SDF": "louisville", "SFO": "san francisco", "DC": "washington|d.c", "TTN": "trenton"}
UP = {"above", "over", "more", "least", "higher", "exceed", "exceeds", "increase"}
DOWN = {"below", "under", "less", "fewer", "lower", "decrease"}
NEG = {"no", "not", "without", "dip"}


def toks(txt):
    import unicodedata
    t = unicodedata.normalize("NFKD", str(txt or "")).encode("ascii", "ignore").decode()
    return bot.text_tokens(t)


def ktitle(q):
    """Kalshi q = title + yes_sub_title; the title is everything up to the last '?'."""
    return q[:q.rfind("?") + 1] if "?" in q else q


def cover(a, b, df, w):
    """Weighted share of a's rare words that b also has (1.0 when a has none)."""
    ra = {t for t in a if df[t] <= 300}
    return sum(w[t] for t in ra & b) / sum(w[t] for t in ra) if ra else 1.0


def mday(txt):
    m = _MD.search(str(txt or "").lower())
    return (m.group(1), int(m.group(2))) if m else None


def direction(tk):
    u, d = bool(tk & UP), bool(tk & DOWN)
    return "up" if u and not d else "down" if d and not u else None


def is_wx(k):
    return bool(re.match(r"KX(HIGH|LOWT|TEMP)", k["s"]))


def weather_ok(k, p):
    """Kalshi daily high/low series -> same city and same kind on Polymarket. Hourly KXTEMP* rounds have no twin."""
    s = k["s"]
    m = re.match(r"KX(HIGH|LOWT)T?([A-Z]+)$", s)
    if not m:
        return False
    city = CITY.get(m.group(2))
    q = p["q"].lower()
    if not city or not re.search(city, q):
        return False
    return ("lowest" in q) == (m.group(1) == "LOWT")


def twin_ok(k, p):
    if launch.kcategory(k["s"], k["q"]) in ("sports", "esports", "crypto price"):   # dug before (arbhunt, xvenue, optfair)
        return False
    if is_wx(k) and not weather_ok(k, p):
        return False
    a, b = mday(k["q"]), mday(p["q"])
    if a and b and a != b:
        return False
    da, db = direction(k["_tk"]), direction(p["_tk"])
    if da and db and da != db:
        return False
    if bool(k["_tk"] & NEG) != bool(p["_tk"] & NEG):
        return False
    return True


def p_load():
    import backtest as bt
    ms = bt.rjson(os.path.join(ROOT, "bt_cache", "markets.json.gz"))["markets"]
    out = []
    for m in ms.values():
        if m.get("sports") or len(m.get("toks") or []) != 2 or not m.get("end") or m["end"] >= HOLD:
            continue
        if m.get("final") not in ([1.0, 0.0], [0.0, 1.0]):
            continue
        out.append(m)
    return out


def match():
    """Text + date + defining numbers only. No price filter: a price filter would hide the very gaps we test."""
    K = [m for m in (rj(os.path.join(CACHE, "kmarkets.json.gz"), {}) or {}).values()
         if not m["s"].startswith("KXMVE") and launch.kcategory(m["s"], m["q"]) not in ("sports", "esports", "crypto price")]
    P = p_load()
    print(f"kalshi {len(K)} non-sports settled, polymarket {len(P)} non-sports finished two-way")
    for x in K:
        x["_tk"] = toks(x["q"])
        x["_tt"] = toks(ktitle(x["q"]))
        x["_n"] = nums(x["q"])
    for x in P:
        txt = f"{x['q']} {x.get('ev_slug', '').replace('-', ' ')}"
        x["_tk"] = toks(x["q"])
        x["_n"] = nums(x["q"])
    df = collections.Counter()
    for x in K + P:
        df.update(x["_tk"])
    N = len(K) + len(P)
    w = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    for x in K + P:
        x["_norm"] = math.sqrt(sum(w[t] ** 2 for t in x["_tk"])) or 1.0
    # index Polymarket by day bucket and token
    idx = collections.defaultdict(list)
    for i, p in enumerate(P):
        d = int(p["end"] // DAY)
        for t in p["_tk"]:
            if df[t] <= 3000:
                for dd in (d - 2, d - 1, d, d + 1, d + 2):
                    idx[(dd, t)].append(i)
    best_k = {}
    for k in K:
        ends = [x for x in (k["close"], k.get("exp")) if x]
        pool = collections.Counter()
        for t in k["_tk"]:
            for i in idx.get((int(k["close"] // DAY), t), ()):
                pool[i] += 1
        best = None
        for i, _ in pool.most_common(80):
            p = P[i]
            if min(abs(p["end"] - e) for e in ends) > TOL:
                continue
            if k["_n"] != p["_n"] or not twin_ok(k, p):
                continue
            s = sum(w[t] ** 2 for t in k["_tk"] & p["_tk"]) / (k["_norm"] * p["_norm"])
            if s >= (0.3 if is_wx(k) else MIN_SCORE) and (best is None or s > best[0]):
                best = (s, i)
        if best:
            best_k[k["t"]] = best
    # one Kalshi market per Polymarket market (the best text match)
    by_p = {}
    for kt, (s, i) in best_k.items():
        if i not in by_p or s > by_p[i][0]:
            by_p[i] = (s, kt)
    Kd = {k["t"]: k for k in K}
    pairs = []
    for i, (s, kt) in by_p.items():
        p, k = P[i], Kd[kt]
        p_yes = p["final"][0] == 1.0
        k_yes = k["res"] == "yes"
        pairs.append({"k": {a: k[a] for a in ("t", "s", "ev", "q", "open", "close", "exp", "res", "vol", "cat")},
                      "p": {a: p.get(a) for a in ("id", "q", "slug", "ev_slug", "toks", "start", "end", "closed_t", "final", "vol", "fee")},
                      "score": round(s, 3), "same_result": p_yes == k_yes})
    pairs.sort(key=lambda x: -x["score"])
    wj(PAIRS, pairs)
    c = collections.Counter(x["k"]["cat"] for x in pairs)
    agree = sum(x["same_result"] for x in pairs)
    print(f"pairs: {len(pairs)}, same result {agree}; by kind {dict(c.most_common())}")
    return pairs


# ================================================================ price tapes for each pair
LOOK = 30 * DAY


def k_hours(k):
    a, b = max(k["open"], k["close"] - LOOK), k["close"]
    for path in (f"/series/{k['s']}/markets/{k['t']}/candlesticks", f"/historical/markets/{k['t']}/candlesticks"):
        try:
            r = yesno.kget(path, {"start_ts": a - 3600, "end_ts": b, "period_interval": 60})
        except Exception:
            continue
        got = r.get("candlesticks") if isinstance(r, dict) else None
        if got:
            out = []
            for c in got:
                t, bid, ask = yesno.k_candle(c)
                out.append([t, bid, ask, bot.fnum(c.get("volume_fp") or c.get("volume"), 0)])
            return out
    return []


def tape_one(job):
    import optfair
    x, cid = job
    kc = k_hours(x["k"])
    pt = optfair.fetch_tape((x["p"], cid))[1] if cid else None
    return x["k"]["t"] + "|" + x["p"]["id"], {"kc": kc, "pt": pt}


def tapes():
    import informed
    pairs = rj(PAIRS, []) or []
    path = os.path.join(CACHE, "tapes.json.gz")
    have = rj(path, {}) or {}
    todo = [x for x in pairs if x["k"]["t"] + "|" + x["p"]["id"] not in have]
    print(f"pairs {len(pairs)}, tapes already {len(have)}, to fetch {len(todo)}", flush=True)
    for i in range(0, len(todo), 200):
        chunk = todo[i:i + 200]
        cids = informed.cids_for([x["p"]["id"] for x in chunk])
        with ThreadPoolExecutor(int(os.environ.get("XS_WORKERS", "6"))) as ex:
            for key, r in ex.map(tape_one, [(x, cids.get(str(x["p"]["id"]))) for x in chunk]):
                have[key] = r
        wj(path, have)
        print(f"  {len(have)} done ({(time.time() - T0) / 60:.0f} min)", flush=True)
        if left() < 8:
            print("time budget used, stop (re-run resumes)")
            break


# ================================================================ the test
STAKE = 10.0
EXTRA = float(os.environ.get("XS_EXTRA", "0.01"))   # Polymarket: worst trade of the next hour + this


def k_fee(px, n):
    return math.ceil(0.07 * n * px * (1 - px) * 100 - 1e-9) / 100


def fix_scale(kc):
    vals = [v for c in kc for v in (c[1], c[2]) if v is not None]
    if vals and max(vals) <= 0.0101:             # /historical candles in dollars read as cents (TOOLS.md trap)
        return [[c[0], None if c[1] is None else c[1] * 100, None if c[2] is None else c[2] * 100, c[3]] for c in kc]
    return kc


def rows_of(x, tp):
    """Hourly looks while both sites trade: Kalshi real bid/ask (gap 10c or less) and Polymarket's last trade (2 h or
    newer, $5+ steps). Nothing after the first of the two closes minus one hour."""
    import bisect
    kc = fix_scale(tp.get("kc") or [])
    pt = tp.get("pt") or {}
    b = [y for y in (pt.get("b") or []) if y[5] >= 5]
    if not kc or not b:
        return [], b
    bt_ = [y[0] for y in b]
    stop = min(x["k"]["close"], x["p"]["end"], x["p"].get("closed_t") or 1e18) - 3600
    out = []
    for c in kc:
        t, kb, ka = c[0], c[1], c[2]
        if t > stop:
            break
        if kb is None or ka is None or not (0.01 <= kb < ka <= 0.99) or ka - kb > 0.10:
            continue
        i = bisect.bisect_right(bt_, t) - 1
        if i < 0 or t - bt_[i] > 7200:
            continue
        out.append({"t": t, "kb": kb, "ka": ka, "km": (kb + ka) / 2, "pp": b[i][2], "i": i})
    return out, b


def p_buy(x, b, r, side):
    """Polymarket buy at the worst real trade of the next hour (never cheaper than the signal) + EXTRA + fee."""
    t, pp = r["t"], r["pp"]
    nx = [y for y in b[r["i"] + 1:r["i"] + 300] if t < y[0] <= t + 3600]
    if not nx:
        return None
    raw = max(y[4] for y in nx) if side == "yes" else 1 - min(y[3] for y in nx)
    sig = pp if side == "yes" else 1 - pp
    if raw - sig > 0.15:
        return None
    px = max(raw, sig) + EXTRA
    if px >= 0.99:
        return None
    sh = STAKE / px
    fee = bot.taker_fee(sh, px, x["p"].get("fee") or 0)
    win = (x["p"]["final"][0] == 1.0) == (side == "yes")
    return {"site": "poly", "px": px, "cost": STAKE + fee, "pay": sh if win else 0.0}


def k_buy(x, r, side):
    px = r["ka"] if side == "yes" else 1 - r["kb"]
    if px >= 0.99:
        return None
    n = math.floor(STAKE / px)
    if n < 1:
        return None
    fee = k_fee(px, n)
    win = (x["k"]["res"] == "yes") == (side == "yes")
    return {"site": "kalshi", "px": px, "cost": n * px + fee, "pay": float(n) if win else 0.0}


def bet(x, r, buy):
    if not buy:
        return None
    buy.update(ev=x["k"]["ev"], t=r["t"], pnl=buy["pay"] - buy["cost"], cat=x["k"]["cat"], same=x["same_result"],
               title=x["p"]["q"][:90], kt=x["k"]["t"])
    return buy


def rule_bets(pairs, tps, rule, gap, lag=1):
    """rule follow_k: Kalshi says more -> buy on Polymarket. follow_p: Polymarket says more -> buy on Kalshi.
    lead_k / lead_p: that site moved `gap`+ in the last `lag` hours, the other moved 1c or less and still lags 3c+."""
    out = []
    for x in pairs:
        tp = tps.get(x["k"]["t"] + "|" + x["p"]["id"])
        if not tp:
            continue
        rows, b = rows_of(x, tp)
        by_t = {r["t"]: r for r in rows}
        for r in rows:
            got = None
            if rule == "follow_k":
                if r["kb"] - r["pp"] >= gap:
                    got = p_buy(x, b, r, "yes")
                elif r["pp"] - r["ka"] >= gap:
                    got = p_buy(x, b, r, "no")
            elif rule == "follow_p":
                if r["pp"] - r["ka"] >= gap:
                    got = k_buy(x, r, "yes")
                elif r["kb"] - r["pp"] >= gap:
                    got = k_buy(x, r, "no")
            else:
                o = by_t.get(r["t"] - lag * 3600)
                if not o:
                    continue
                dk, dp = r["km"] - o["km"], r["pp"] - o["pp"]
                if rule == "lead_k" and abs(dk) >= gap and abs(dp) <= 0.01:
                    if dk > 0 and r["kb"] - r["pp"] >= 0.03:
                        got = p_buy(x, b, r, "yes")
                    elif dk < 0 and r["pp"] - r["ka"] >= 0.03:
                        got = p_buy(x, b, r, "no")
                elif rule == "lead_p" and abs(dp) >= gap and abs(dk) <= 0.01:
                    if dp > 0 and r["pp"] - r["ka"] >= 0.03:
                        got = k_buy(x, r, "yes")
                    elif dp < 0 and r["kb"] - r["pp"] >= 0.03:
                        got = k_buy(x, r, "no")
            got = bet(x, r, got)
            if got:
                out.append(got)
                break
    return out


def accuracy(pairs, tps, hours_before):
    """Brier score (lower = better) of each site's price N hours before the stop, on pairs whose results agree."""
    bk = bp = 0.0
    n = closer_k = closer_p = 0
    for x in pairs:
        if not x["same_result"]:
            continue
        tp = tps.get(x["k"]["t"] + "|" + x["p"]["id"])
        if not tp:
            continue
        rows, _ = rows_of(x, tp)
        if not rows:
            continue
        stop = rows[-1]["t"]
        cand = [r for r in rows if r["t"] <= stop - (hours_before - 1) * 3600]
        if not cand:
            continue
        r = cand[-1]
        y = 1.0 if x["k"]["res"] == "yes" else 0.0
        bk += (r["km"] - y) ** 2
        bp += (r["pp"] - y) ** 2
        n += 1
        if abs(r["km"] - r["pp"]) >= 0.05:
            if abs(r["km"] - y) < abs(r["pp"] - y):
                closer_k += 1
            else:
                closer_p += 1
    return {"n": n, "brier_k": bk / n if n else None, "brier_p": bp / n if n else None, "closer_k": closer_k, "closer_p": closer_p}


def per100(bets):
    c = sum(b["cost"] for b in bets)
    return 100 * sum(b["pnl"] for b in bets) / c if c else 0.0


RULES = [("follow_k", 0.05, 1), ("follow_k", 0.10, 1), ("follow_p", 0.05, 1), ("follow_p", 0.10, 1),
         ("lead_k", 0.05, 1), ("lead_k", 0.05, 3), ("lead_p", 0.05, 1), ("lead_p", 0.05, 3)]
NAMES = {"follow_k": "Buy on Polymarket where Kalshi's price is {g}c+ away (follow Kalshi)",
         "follow_p": "Buy on Kalshi where Polymarket's price is {g}c+ away (follow Polymarket)",
         "lead_k": "Kalshi moved {g}c+ in {h}h, Polymarket stood still: buy on Polymarket",
         "lead_p": "Polymarket moved {g}c+ in {h}h, Kalshi stood still: buy on Kalshi"}


def run(score=True):
    import exam
    pairs = rj(PAIRS, []) or []
    tps = rj(os.path.join(CACHE, "tapes.json.gz"), {}) or {}
    pairs = [x for x in pairs if x["k"]["t"] + "|" + x["p"]["id"] in tps and x.get("rev", "Y") == os.environ.get("XS_REV", "Y")]
    lines = [f"pairs with prices on both sites: {len(pairs)}, same result on both sites: {sum(x['same_result'] for x in pairs)}"]
    for h in (72, 24, 6, 1):
        a = accuracy(pairs, tps, h)
        if a["n"]:
            lines.append(f"{h}h before: {a['n']} pairs, Brier Kalshi {a['brier_k']:.4f} / Polymarket {a['brier_p']:.4f}; "
                         f"5c+ apart: Kalshi closer {a['closer_k']}, Polymarket closer {a['closer_p']}")
    res = {}
    for rule, g, h in RULES:
        bets = rule_bets(pairs, tps, rule, g, h)
        name = NAMES[rule].format(g=round(g * 100), h=h)
        res[(rule, g, h)] = bets
        cats = collections.Counter(b["cat"] for b in bets)
        lines.append(f"{name}: {len(bets)} bets, {per100(bets):+.2f} per $100, won {sum(b['pay'] > 0 for b in bets)}, "
                     f"results differ {sum(not b['same'] for b in bets)}; {dict(cats.most_common(5))}")
        if score and bets:
            exam.score(bets, "Kalshi vs Polymarket: " + name, tries=len(RULES), src="xsite.py run", status="dropped", log=True)
    print("\n".join(lines))
    return res, lines


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"klist": klist, "match": match, "tapes": tapes, "run": run}[cmd]()
