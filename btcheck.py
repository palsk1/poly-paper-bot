#!/usr/bin/env python3
"""Backtest sanity checks (2026-11-09): does the backtester itself tell the truth, and do the "leads" survive harder tests?

PAPER ONLY. Reads bt_cache/ (filled by `backtest.py fetch`), never trades. Written after a Reddit post on backtest
hygiene: "my biggest early edge was a backtest bug". See backtest/PROTOCOL.md for the test-before-results rules.

    python3 btcheck.py selftest   # offline: engine on fake fair markets + a planted bug that must be caught
    python3 btcheck.py run        # all checks on the real cache, writes backtest/checks.md
    python3 btcheck.py holdout    # the one-time holdout test (refuses before HOLDOUT_OPEN, and refuses a second run)
    (probe workflow: btcheck / btcheckself / btholdout)

The checks
1. Fair-coin world: fake markets whose price is a true probability (a Bayesian forecaster's running estimate, so
   every price is exactly right on average). Every strategy run through the real engine must lose about its
   costs there, no more and no less. A planted bug (stop-loss booked at the stop price even when the price
   gapped through it) must show up as a fake profit, so we know the check can catch one.
2. A second, separate simulator (this file, it doesn't call the engine's pricing or exit code) re-walks every
   backtest trade from the raw price history: entry price, fee, take-profit / stop / payout, profit. It must agree.
   It also counts exits booked BETTER than the live bot could get: history is 12-hourly, so a take-profit seen
   at 90c may have been crossed at 80c hours earlier. The pessimistic number sells at the target instead.
3. Random entries on the same real data, held to the end, should lose about the costs.
4. Each strategy vs random entries with the same exits (same day window, same price band, same take-profit /
   stop rules, same costs). If it doesn't beat those, the "edge" is in the exits or the price band, not the signal.
5. Pessimistic costs: +1 tick worse (2c instead of 1c) and a later entry (1 hour, and "the next recorded price").
6. Walk-forward for the panic family: sweep the drop size on one half, test the winner on the other half.
7. mention_no rebuilt from scratch (its own code, one bet per event, entry when the market first enters the
   7-day window), with random-side and other-topics controls, halves and pessimistic costs.
Holdout: markets that end on/after HOLDOUT_FROM are kept out of every check above and are looked at once.
"""
import bisect
import datetime as dt
import json
import math
import os
import random
import re
import sys
import time
from collections import defaultdict

import backtest as bt
import bot

DAY = 86400
UTC = dt.timezone.utc
HOLDOUT_FROM = "2026-11-10"   # markets ending on/after this day are the holdout (see backtest/PROTOCOL.md)
HOLDOUT_OPEN = "2026-12-21"   # the holdout may be scored once, from this day on
SPLIT = "2026-07-01"          # fallback split; halves normally split at the middle trade
OUT = bt.OUT


def T(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=UTC).timestamp())


def pt(iso):
    return int(bot.parse_iso(iso).timestamp())


def money(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.2f}"


def m100(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


# ================================================================ the second simulator (independent of the engine)
# Its own price lookup, fee, payout and exit walk. It must not call bot.quote / bot.paper_close / bt.Feed / bt.payout.

def price_at(h, t, side):
    """Last recorded price of outcome `side` at or before t, and when it was recorded."""
    if not h or not h[0]:
        return None, None
    k = bisect.bisect_right(h[0], t) - 1
    if k < 0:
        return None, None
    p = h[1][k]
    return (p if side == 0 else round(1 - p, 6)), h[0][k]


def next_print(h, t):
    """First recorded price strictly after t (the 'wait for the next print' entry)."""
    if not h or not h[0]:
        return None
    k = bisect.bisect_right(h[0], t)
    return h[0][k] if k < len(h[0]) else None


def fee_of(shares, p, rate):
    return rate * shares * p * (1.0 - p)


def settle_value(mk, side):
    f = mk.get("final") or []
    if not mk.get("closed") or side >= len(f) or f[side] is None:
        return None
    v = f[side]
    if v >= 0.99:
        return 1.0
    if v <= 0.01:
        return 0.0
    return v if mk.get("uma") == "resolved" else None


def walk(mk, h, side, t0, entry, shares, slip, target=None, stop=None, cap_target=False):
    """Hold from t0: sell at the first recorded price >= target or <= stop (checked on the hour, like the engine),
    else take the payout when the market closes. Returns (exit_price, exit_fee, reason, t_exit) or None if unsettled.
    cap_target: sell at the target itself (not the higher price first seen), the pessimistic reading of a gap."""
    ct = mk.get("closed_t")
    if target or stop:
        T_, P_ = h
        k = bisect.bisect_right(T_, t0)
        while k < len(T_):
            tk = T_[k]
            # the engine looks once an hour: a print is acted on at the next full hour after it
            th = tk if tk % 3600 == 0 else tk - tk % 3600 + 3600
            if ct is not None and th >= ct:
                break
            # the hour it is acted on sees the LAST print at or before that hour
            k2 = bisect.bisect_right(T_, th) - 1
            px = P_[k2] if side == 0 else round(1 - P_[k2], 6)
            hit = "take profit" if target and px >= target else "stop loss" if stop and px <= stop else None
            if hit:
                if hit == "take profit" and cap_target:
                    px = min(px, target)
                fill = max(0.001, px - slip)
                return fill, fee_of(shares, fill, mk["fee"]), hit, th
            k = k2 + 1
    pay = settle_value(mk, side)
    if pay is None:
        return None
    return pay, 0.0, "resolved", ct


def ratio_stats(rows):
    """rows of (profit, stake) -> per $100, its 90% band, n."""
    rows = [r for r in rows if r[1] > 0]
    n = len(rows)
    if not n:
        return None
    P = sum(p for p, _ in rows)
    S = sum(s for _, s in rows)
    rate = P / S
    var = sum((p - rate * s) ** 2 for p, s in rows) / (S * S) * (n / max(1, n - 1))
    se = math.sqrt(var)
    return {"per100": 100 * rate, "lo": 100 * (rate - 1.645 * se), "hi": 100 * (rate + 1.645 * se), "se": 100 * se,
            "n": n, "profit": P, "staked": S}


def band(s):
    return "-" if not s else f"{m100(s['lo'])} to {m100(s['hi'])}"


# ================================================================ engine helpers

class Delay:
    """Entry delay applied on top of the backtest's history fills: 0 = none, seconds, or 'next' = next recorded price."""
    how = 0
    feed = None
    by_tok = {}


_orig_patch = bt.patch_bot


def _patch(slip):
    _orig_patch(slip)
    base_quote = bot.quote

    def quote(token, side, shares, m=None):
        if side != "buy" or not Delay.how or token not in Delay.by_tok:
            return base_quote(token, side, shares, m)
        mk, i = Delay.by_tok[token]
        h = Delay.feed.h.get(mk["id"])
        now_t = bt.Clock.t
        t2 = next_print(h, now_t) if Delay.how == "next" else now_t + Delay.how
        if t2 is None or t2 - now_t > 2 * DAY or (mk["closed_t"] is not None and t2 >= mk["closed_t"]) or t2 >= mk["end"]:
            return None, shares, "none"
        p0 = Delay.feed.at(mk["id"], t2)
        if p0 is None:
            return None, shares, "none"
        px = p0 if i == 0 else 1 - p0
        return min(0.999, px + slip), shares, "history"
    bot.quote = quote


bt.patch_bot = _patch


def engine(markets, hist, slip, names=None, delay=0, uncapped=True):
    feed = bt.Feed(hist)
    Delay.how, Delay.feed = delay, feed
    Delay.by_tok = {tok: (m, i) for m in markets.values() for i, tok in enumerate(m["toks"])}
    real = bt.Clock.real_now
    try:
        return bt.replay_rules(markets, feed, slip, uncapped, names)
    finally:
        Delay.how = 0
        bot.now = lambda: real


def recheck(trs, markets, hist, slip, delay=0):
    """Second simulator vs engine, trade by trade. Returns per-track dicts."""
    by_tok = {tok: (m, i) for m in markets.values() for i, tok in enumerate(m["toks"])}
    out = {}
    for n, tr in trs.items():
        r = bot.rules_for(n)
        d = {"n": 0, "bad_entry": 0, "bad_exit": 0, "bad_pnl": 0, "max_diff": 0.0, "tp": 0, "tp_over": 0,
             "tp_over_usd": 0.0, "sl": 0, "sl_gap": 0, "rows": [], "rows_cap": [], "future": 0, "examples": []}
        for c in tr["closed"]:
            mk, side = by_tok[c["token"]]
            h = hist[mk["id"]]
            t0 = pt(c["opened"])
            raw, t_raw = price_at(h, t0, side)
            sh = c["shares"]
            d["n"] += 1
            if raw is None:
                d["bad_entry"] += 1
                continue
            if not delay:
                e = min(0.999, raw + slip)
                if abs(e - c["entry"]) > 1e-4:
                    d["bad_entry"] += 1
                    if len(d["examples"]) < 3:
                        d["examples"].append(f"{c['title'][:60]}: entry {c['entry']} vs raw {e}")
            e = c["entry"]
            ef = fee_of(sh, e, mk["fee"])
            if abs(ef - c.get("entry_fee", 0)) > 1e-4:
                d["bad_entry"] += 1
            t1 = pt(c["closed_at"])
            if c["reason"] == "resolved":
                x, xf = settle_value(mk, side), 0.0
                if mk["closed_t"] is not None and t1 < mk["closed_t"]:
                    d["future"] += 1
            else:
                k = bisect.bisect_right(h[0], t1) - 1
                px = h[1][k] if side == 0 else round(1 - h[1][k], 6)
                x = max(0.001, px - slip)
                xf = fee_of(sh, x, mk["fee"])
            if x is None or abs(x - c["exit"]) > 1e-4:
                d["bad_exit"] += 1
                if len(d["examples"]) < 3:
                    d["examples"].append(f"{c['title'][:60]}: exit {c['exit']} ({c['reason']}) vs raw {x}")
                continue
            pnl = sh * x - xf - sh * e - ef
            diff = abs(pnl - c["pnl"])
            d["max_diff"] = max(d["max_diff"], diff)
            if diff > 1e-3:
                d["bad_pnl"] += 1
            stake = sh * e + ef
            d["rows"].append((pnl, stake, t0))
            # pessimistic exit: a take-profit seen above its target is sold at the target
            pnl_cap = pnl
            if c["reason"] == "take profit":
                d["tp"] += 1
                tgt = c.get("target") or r.get("take_profit")
                if tgt and px > tgt + 1e-9:
                    d["tp_over"] += 1
                    x2 = max(0.001, tgt - slip)
                    pnl_cap = sh * x2 - fee_of(sh, x2, mk["fee"]) - sh * e - ef
                    d["tp_over_usd"] += pnl - pnl_cap
            elif c["reason"] == "stop loss":
                d["sl"] += 1
                stp = c.get("stop") or r.get("stop_loss")
                if stp and px < stp - 1e-9:
                    d["sl_gap"] += 1
            d["rows_cap"].append((pnl_cap, stake, t0))
        out[n] = d
    return out


# ================================================================ check 1: fair-coin world (offline)

def fair_markets(n=3000, seed=11):
    """Markets whose price is the exact probability: a Bayesian forecaster's running estimate from noisy clues,
    with an occasional big piece of news (scares and jumps). Price points 12-hourly, hourly in the last 3 days."""
    rng = random.Random(seed)
    base = T(bt.START)
    markets, hist = {}, {}
    for k in range(n):
        start = base - 20 * DAY + rng.randrange(170) * DAY + rng.randrange(24) * 3600
        end = start + rng.choice([2, 4, 8, 15, 25, 40, 70, 110]) * DAY
        p0 = rng.choice([rng.uniform(0.02, 0.98), rng.uniform(0.80, 0.99), rng.uniform(0.01, 0.2)])
        y = 1 if rng.random() < p0 else 0
        L = math.log(p0 / (1 - p0))
        t = start
        steps = []
        while t < end:
            steps.append(t)
            t += 3600 if t > end - 3 * DAY else 43200
        N = len(steps)
        mu = math.sqrt(3.0 / max(N, 1))
        Tm, Pm = [], []
        for t in steps:
            m_ = 0.9 if rng.random() < 0.03 else mu      # big news now and then
            s = rng.gauss(m_ if y else -m_, 1.0)
            L += 2 * m_ * s                               # exact log-likelihood ratio for N(+-m, 1)
            L = max(-9, min(9, L))
            p = 1 / (1 + math.exp(-L))
            Tm.append(t)
            Pm.append(round(min(0.999, max(0.001, p)), 4))
        mid = f"f{k}"
        markets[mid] = {"id": mid, "q": f"Will thing {k} happen by the deadline?", "outs": ["Yes", "No"],
                        "toks": [f"{mid}y", f"{mid}n"], "end": end, "start": start, "closed": True,
                        "closed_t": end + 3600, "final": [1.0, 0.0] if y else [0.0, 1.0], "uma": "resolved",
                        "vol": 300000, "fee": 0.04 if k % 2 else 0.0, "sports": False, "slug": mid, "ev": f"e{k}",
                        "ev_slug": f"e{k}"}
        hist[mid] = bt.squeeze(list(zip(Tm, Pm)), 0)
    return markets, hist


def cost_of(c, mk, slip):
    """What a trade pays in costs (fees + slippage) versus a fill at the fair price."""
    sh = c["shares"]
    cost = c.get("entry_fee", 0) + c.get("exit_fee", 0) + slip * sh
    if c["reason"] != "resolved":
        cost += slip * sh
    return cost


def fair_world(slip=0.01, bug=False, names=None, n=3000):
    markets, hist = fair_markets(n)
    bt.Clock.real_now = bt.utc(max(m["closed_t"] for m in markets.values()) + DAY)
    by_tok = {tok: m for m in markets.values() for tok in m["toks"]}
    saved = bot.paper_close
    if bug:  # the Reddit bug: a stop exit is booked at the stop price even when the price already went past it
        def buggy(track, name, token, price, fee, reason):
            pos = track["positions"].get(token) or {}
            stp = pos.get("stop") or bot.rules_for(name).get("stop_loss")
            if reason == "stop loss" and stp and price < stp:
                price = stp
            return saved(track, name, token, price, fee, reason)
        bot.paper_close = buggy
    try:
        trs = engine(markets, hist, slip, names)
    finally:
        bot.paper_close = saved
    res = {}
    for n_, tr in trs.items():
        rows = [(c["pnl"] + cost_of(c, by_tok[c["token"]], slip), c["shares"] * c["entry"] + c.get("entry_fee", 0))
                for c in tr["closed"]]
        raw = [(c["pnl"], c["shares"] * c["entry"] + c.get("entry_fee", 0)) for c in tr["closed"]]
        res[n_] = {"excess": ratio_stats(rows), "raw": ratio_stats(raw)}
    return res, trs, markets, hist


def fair_table(res, z=2.58):
    L = ["| Track | Trades | Profit per $100 | Same, costs added back (should be ~$0) | 99% band | OK? |", "|---|---|---|---|---|---|"]
    bad = []
    for n, r in sorted(res.items(), key=lambda kv: -(kv[1]["excess"] or {}).get("n", 0)):
        e = r["excess"]
        if not e or e["n"] < 20:
            continue
        lo, hi = e["per100"] - z * e["se"], e["per100"] + z * e["se"]
        ok = lo <= 0 <= hi
        if not ok:
            bad.append(n)
        L.append(f"| `{n}` | {e['n']} | {m100(r['raw']['per100'])} | {m100(e['per100'])} | {m100(lo)} to {m100(hi)} | {'yes' if ok else '**NO**'} |")
    return L, bad


# ================================================================ check 3+4: random entries

def pool_index(markets, hist, until_t):
    mks = [m for m in markets.values() if hist.get(m["id"]) and hist[m["id"]][0] and m["end"] < until_t]
    mks.sort(key=lambda m: m["end"])
    return mks, [m["end"] for m in mks]


def random_twin(rng, mks, ends, hist, t, lo_d, hi_d, plo, phi, tries=300):
    """A random market open at t with end in [t+lo_d, t+hi_d], random side priced in [plo, phi] at t."""
    i0 = bisect.bisect_left(ends, t + lo_d * DAY)
    i1 = bisect.bisect_right(ends, t + hi_d * DAY)
    if i1 <= i0:
        return None
    for _ in range(tries):
        mk = mks[rng.randrange(i0, i1)]
        if (mk["start"] or 0) > t or (mk["closed_t"] is not None and mk["closed_t"] <= t):
            continue
        h = hist[mk["id"]]
        side = rng.randrange(2)
        p, tp = price_at(h, t, side)
        if p is None or t - tp > 3 * DAY or not (plo <= p <= phi):
            continue
        return mk, side, p
    return None


def random_vs_strategy(trs, markets, hist, slip, seed=5, k=3):
    """For each strategy trade: the second simulator replays it, and k random twins with the same exits."""
    rng = random.Random(seed)
    mks, ends = pool_index(markets, hist, T(HOLDOUT_FROM))
    by_tok = {tok: (m, i) for m in markets.values() for i, tok in enumerate(m["toks"])}
    out = {}
    for n, tr in trs.items():
        r = bot.rules_for(n)
        if not tr["closed"]:
            continue
        S, R_same, R_any = [], [], []
        for c in tr["closed"]:
            mk, side = by_tok[c["token"]]
            t0 = pt(c["opened"])
            sh = c["shares"]
            days_left = (mk["end"] - t0) / DAY
            lo_d, hi_d = (r["min_days"], r["max_days"]) if "min_days" in r and "max_days" in r else \
                (max(0.0, days_left * 0.5), days_left * 2 + 1)
            tgt_abs, stp_abs = r.get("take_profit"), r.get("stop_loss")
            tgt_gap = (c["target"] - c["entry"]) if c.get("target") else None
            e = c["entry"]
            res = walk(mk, hist[mk["id"]], side, t0, e, sh, slip, c.get("target") or tgt_abs, c.get("stop") or stp_abs,
                       cap_target=True)
            if res:
                x, xf, _, _ = res
                ef = fee_of(sh, e, mk["fee"])
                S.append((sh * x - xf - sh * e - ef, sh * e + ef))
            plo, phi = r.get("min_price", 0.05), r.get("max_price", 0.95)
            for rows, (a, b) in ((R_same, (plo, phi)), (R_any, (0.05, 0.95))):
                for _ in range(k):
                    tw = random_twin(rng, mks, ends, hist, t0, lo_d, hi_d, a, b)
                    if not tw:
                        continue
                    mk2, s2, p2 = tw
                    e2 = min(0.999, p2 + slip)
                    tgt = min(0.97, e2 + tgt_gap) if tgt_gap else tgt_abs
                    res2 = walk(mk2, hist[mk2["id"]], s2, t0, e2, sh, slip, tgt, stp_abs, cap_target=True)
                    if not res2:
                        continue
                    x2, xf2, _, _ = res2
                    ef2 = fee_of(sh, e2, mk2["fee"])
                    rows.append((sh * x2 - xf2 - sh * e2 - ef2, sh * e2 + ef2))
        out[n] = {"strat": ratio_stats(S), "same": ratio_stats(R_same), "any": ratio_stats(R_any)}
    return out


def random_hold(markets, hist, n=30000, seed=9):
    """Random market, random moment in its life, random side, held to the end. Should lose about the costs."""
    rng = random.Random(seed)
    mks = [m for m in markets.values() if hist.get(m["id"]) and hist[m["id"]][0] and m["end"] < T(HOLDOUT_FROM)
           and settle_value(m, 0) in (0.0, 1.0)]
    rows = {s: [] for s in (0.0, 0.01, 0.02)}
    bands = defaultdict(list)
    got = 0
    for _ in range(n * 4):
        if got >= n or not mks:
            break
        mk = rng.choice(mks)
        h = hist[mk["id"]]
        lo = max(h[0][0] + DAY, mk["start"] or 0)
        hi = min(mk["end"], mk["closed_t"] or mk["end"]) - 3600
        if hi <= lo:
            continue
        t = rng.randrange(lo, hi)
        side = rng.randrange(2)
        p, tp = price_at(h, t, side)
        if p is None or t - tp > 3 * DAY or not 0.02 <= p <= 0.98:
            continue
        pay = settle_value(mk, side)
        got += 1
        for s in rows:
            e = min(0.999, p + s)
            f = fee_of(1, e, mk["fee"])
            rows[s].append((pay - e - f, e + f))
            if s == 0.01:
                b = "2-20c" if p < 0.2 else "20-50c" if p < 0.5 else "50-80c" if p < 0.8 else "80-98c"
                bands[b].append((pay - e - f, e + f, s + f))
    costs = {}
    for b, rs in bands.items():
        st = sum(x[1] for x in rs)
        costs[b] = (ratio_stats([(x[0], x[1]) for x in rs]), 100 * sum(x[2] for x in rs) / st)
    return {s: ratio_stats(v) for s, v in rows.items()}, costs, got


# ================================================================ check 6: sweep + walk-forward (panic family)

SWEEP = [(d, p) for d in (0.04, 0.06, 0.08, 0.10, 0.12, 0.15) for p in (0.45, 0.55)]


def add_sweep_tracks():
    names = []
    for d, p in SWEEP:
        key = f"_sw_{int(d * 100)}_{int(p * 100)}"
        bot.CFG["rules"][key] = {"inherit": "panic_fade_10c", "min_drop": d, "min_price": p}
        bot.CFG["tracks"][key] = {"start_cash": 500, "source": "panic", "rules": key}
        names.append(key)
    return names


def drop_sweep_tracks(names):
    for k in names:
        bot.CFG["rules"].pop(k, None)
        bot.CFG["tracks"].pop(k, None)


def halves_of(rows, split=None):
    """Older / newer half. split: a fixed time; default = the middle trade, so both halves have data (the panic
    rules stop new entries ~4 months before the data ends, so a fixed mid-year date leaves the 2nd half nearly empty)."""
    if not rows:
        return None, None
    s = split if split is not None else sorted(t for _, _, t in rows)[len(rows) // 2]
    a = ratio_stats([(p, b) for p, b, t in rows if t < s])
    b = ratio_stats([(p, b) for p, b, t in rows if t >= s])
    return a, b


WF = {}


def walk_forward(chk, names):
    L = ["| Variant (drop, lowest price) | Trades | Per $100 (TP capped) | 1st half | 2nd half |", "|---|---|---|---|---|"]
    stats = {}
    every = sorted(t for n in names for _, _, t in chk[n]["rows_cap"])
    split = every[len(every) // 2] if every else T(SPLIT)
    WF["split"] = bt.iso_t(split)[:10]
    for n in names:
        rows = chk[n]["rows_cap"]
        a, b = halves_of(rows, split)
        allr = ratio_stats([(p, s) for p, s, _ in rows])
        stats[n] = (allr, a, b)
        L.append(f"| {n[4:].replace('_', 'c drop, ', 1)}c | {allr['n'] if allr else 0} | {m100(allr and allr['per100'])} | "
                 f"{m100(a and a['per100'])} ({a['n'] if a else 0}) | {m100(b and b['per100'])} ({b['n'] if b else 0}) |")
    ok = lambda s: s and s["n"] >= 30
    best_a = max((n for n in names if ok(stats[n][1])), key=lambda n: stats[n][1]["per100"], default=None)
    best_b = max((n for n in names if ok(stats[n][2])), key=lambda n: stats[n][2]["per100"], default=None)
    lines = []
    if best_a:
        a, b = stats[best_a][1], stats[best_a][2]
        lines.append(f"- Best on the 1st half: `{best_a}` at {m100(a['per100'])}. On the 2nd half it made "
                     f"{m100(b and b['per100'])} (band {band(b)}).")
    if best_b:
        a, b = stats[best_b][1], stats[best_b][2]
        lines.append(f"- Best on the 2nd half: `{best_b}` at {m100(b['per100'])}. On the 1st half it made "
                     f"{m100(a and a['per100'])} (band {band(a)}).")
    return L, lines


# ================================================================ check 7: mention_no from scratch

MENTION_RE = re.compile(r"\bsays?\b|\bsaid\b|\bmention", re.I)
MENTION_SKIP = ("tweets", " posts ", "truth social post", "up or down")


def mention_bets(markets, hist, side_rule="no", lo=0.25, hi=0.90, days=7, slip=0.02, delay=None, rng=None,
                 topic_filter="mention", t_from=None, t_to=None):
    """One bet per event: the first moment a market of the event is within `days` of its end and the chosen side
    is priced lo..hi, buy it (+slip, + fee) and hold. side_rule: 'no', 'yes' or 'random'."""
    first = {}
    for mk in markets.values():
        q = mk["q"]
        is_m = bool(MENTION_RE.search(q)) and not any(w in q.lower() for w in MENTION_SKIP)
        if (topic_filter == "mention") != is_m:
            continue
        if t_from is not None and mk["end"] < t_from or t_to is not None and mk["end"] >= t_to:
            continue
        h = hist.get(mk["id"])
        if not h or not h[0]:
            continue
        outs = [o.lower() for o in mk["outs"]]
        if side_rule == "random":
            side = (rng or random).randrange(2)
        else:
            if side_rule not in outs:
                continue
            side = outs.index(side_rule)
        pay = settle_value(mk, side)
        if pay not in (0.0, 1.0):
            continue
        t = max(mk["end"] - days * DAY, h[0][0] + DAY, mk["start"] or 0)
        t -= t % 3600
        stop_t = min(mk["end"], mk["closed_t"] or mk["end"]) - 3600
        while t < stop_t:
            p, tp = price_at(h, t, side)
            if p is not None and t - tp <= 3 * DAY and lo <= p <= hi:
                break
            k = bisect.bisect_right(h[0], t)
            t = h[0][k] if k < len(h[0]) else stop_t
        else:
            continue
        if t >= stop_t:
            continue
        if delay == "next":
            t2 = next_print(h, t)
            if t2 is None or t2 >= stop_t:
                continue
            p, _ = price_at(h, t2, side)
        ev = mk.get("ev") or mk["id"]
        if ev in first and first[ev][0] <= t:
            continue
        e = min(0.99, p + slip)
        f = fee_of(1, e, mk["fee"])
        first[ev] = (t, pay - e - f, e + f, mk["q"])
    return [(v[1], v[2], v[0]) for v in first.values()]


QUIET_SKIP = ("up or down", "temperature")


def quiet_bets(markets, hist, lo=0.50, hi=0.75, max_range=0.02, d_from=3, d_to=1, slip=0.02, t_from=None, t_to=None,
               complete=None):
    """quiet_no, as the live track trades it (bot.quiet_candidates): scanning hourly from d_from to d_to days before
    the end, the first hour the second answer is priced lo..hi and the first answer's price moved less than max_range
    over the 7 days before. Buy 1 hour later at the history price + slip + fee, hold. One bet per event (earliest).
    complete: event ids to keep (whole events, ideas.load_full), or None for all."""
    first = {}
    for mk in markets.values():
        if mk.get("sports") or any(w in mk["q"].lower() for w in QUIET_SKIP) or len(mk.get("toks") or []) != 2:
            continue
        if t_from is not None and mk["end"] < t_from or t_to is not None and mk["end"] >= t_to:
            continue
        ev = mk.get("ev") or mk["id"]
        if complete is not None and ev not in complete:
            continue
        h = hist.get(mk["id"])
        if not h or not h[0]:
            continue
        pay = settle_value(mk, 1)
        if pay not in (0.0, 1.0):
            continue
        T_, P_ = h
        t = mk["end"] - d_from * DAY
        t -= t % 3600
        stop_t = min(mk["end"] - d_to * DAY, (mk["closed_t"] or mk["end"]) - 2 * 3600)
        hit = None
        while t < stop_t:
            p0, tp = price_at(h, t, 0)
            if p0 is not None and t - tp <= 3 * DAY and lo <= 1 - p0 <= hi:
                a, _ = price_at(h, t - 7 * DAY, 0)
                k0, k1 = bisect.bisect_right(T_, t - 7 * DAY), bisect.bisect_right(T_, t)
                w = P_[k0:k1] + ([a] if a is not None else [])
                if a is not None and max(w) - min(w) < max_range:
                    hit = t
                    break
            t += 3600
        if hit is None:
            continue
        p, _ = price_at(h, hit + 3600, 1)
        if p is None or (ev in first and first[ev][0] <= hit):
            continue
        e = min(0.99, p + slip)
        f = fee_of(1, e, mk["fee"])
        first[ev] = (hit, pay - e - f, e + f, mk["q"])
    return [(v[1], v[2], v[0]) for v in first.values()]


def quiet_check():
    """In-sample reference for quiet_no with the exact live rule (markets ending before HOLDOUT_FROM, whole events)."""
    import ideas
    markets, hist, complete = ideas.load_full()
    cut = T(HOLDOUT_FROM)
    print(f"whole events: {'yes' if complete is not None else 'NO (run btideasfetch)'}")
    for label, kw in (("+2c", {}), ("+5c", {"slip": 0.05})):
        rows = quiet_bets(markets, hist, t_to=cut, complete=complete, **kw)
        s = ratio_stats([(a, b) for a, b, _ in rows])
        a, b = halves_of(rows)
        print(f"quiet_no in-sample {label}: {s['n'] if s else 0} events, {m100(s and s['per100'])} per $100, band {band(s)}, "
              f"halves {m100(a and a['per100'])} / {m100(b and b['per100'])}")


def mention_table(markets, hist, t_to):
    L = ["| Test | Events | Per $100 | 90% band | 1st half / 2nd half |", "|---|---|---|---|---|"]

    def row(label, rows):
        s = ratio_stats([(a, b) for a, b, _ in rows])
        a, b = halves_of(rows)
        L.append(f"| {label} | {s['n'] if s else 0} | {m100(s and s['per100'])} | {band(s)} | "
                 f"{m100(a and a['per100'])} / {m100(b and b['per100'])} |")
        return s
    main = row("**mention_no rule, NO 25-90c, +2c**", mention_bets(markets, hist, t_to=t_to))
    row("same, +1c", mention_bets(markets, hist, slip=0.01, t_to=t_to))
    row("same, +3c (1 tick worse)", mention_bets(markets, hist, slip=0.03, t_to=t_to))
    row("same, +3c and wait for the next price print", mention_bets(markets, hist, slip=0.03, delay="next", t_to=t_to))
    row("same, +5c (thin books)", mention_bets(markets, hist, slip=0.05, t_to=t_to))
    row("control: YES side instead, +2c", mention_bets(markets, hist, side_rule="yes", t_to=t_to))
    rng = random.Random(4)
    row("control: random side, +2c", mention_bets(markets, hist, side_rule="random", rng=rng, t_to=t_to))
    row("control: same rule on all OTHER topics, +2c",
        mention_bets(markets, hist, topic_filter="other", t_to=t_to))
    return L, main


# ================================================================ data loading

def load_cache():
    markets = bt.rjson(os.path.join(bt.CACHE, "markets.json.gz"), {}).get("markets", {})
    hist = bt.rjson(os.path.join(bt.CACHE, "hist.json.gz"), {})
    return markets, hist


def in_sample(markets):
    cut = T(HOLDOUT_FROM)
    return {k: m for k, m in markets.items() if m["end"] < cut}


# ================================================================ run

def run():
    t_all = time.time()
    real_now = bot.now()
    bt.Clock.real_now = real_now
    markets_all, hist = load_cache()
    small = bt.rjson(os.path.join(bt.CACHE, "small_markets.json.gz"), {}) or {}
    shist = bt.rjson(os.path.join(bt.CACHE, "small_hist.json.gz"), {}) or {}
    markets = in_sample(markets_all)
    print(f"markets {len(markets_all)} cached, {len(markets)} in-sample (end before {HOLDOUT_FROM})")
    L = [f"# Backtest sanity checks", "",
         f"Generated {bot.iso(real_now)} by `btcheck.py` (probe `btcheck`). Paper only. {len(markets):,} finished "
         f"markets that ended before {HOLDOUT_FROM}; later ones are the holdout (backtest/PROTOCOL.md). "
         "Money is per $100 staked.", ""]

    # 1. fair-coin world
    t0 = time.time()
    fres, _, _, _ = fair_world(0.01)
    ftab, fbad = fair_table(fres)
    bres, _, _, _ = fair_world(0.01, bug=True, names=["panic_fade", "panic_fade_10c", "claude", "fav_cut_losses"])
    btab, bbad = fair_table(bres)
    L += ["## 1. Fair-coin world (fake markets where every price is exactly right)", "",
          "Every strategy, run through the real backtest engine at +1c. With the costs added back, each should land "
          "near $0. A track outside its band would mean the engine invents or loses money by itself.", ""] + ftab
    L += ["", f"Result: {'all inside their band' if not fbad else 'OUTSIDE: ' + ', '.join(fbad)}.", "",
          "Planted bug (stop-loss booked at the stop price even when the price had gapped past it, the Reddit "
          "poster's bug). The check must flag it:", ""] + btab
    L += ["", f"Result: {'caught: ' + ', '.join(bbad) if bbad else 'NOT caught (the check is too weak)'}. ({time.time() - t0:.0f}s)", ""]
    print("\n".join(L))

    # 2+5. engine on real data, second simulator, pessimistic costs
    passes = [("1c", 0.01, 0, None), ("2c", 0.02, 0, None), ("2c + 1h later", 0.02, 3600, None),
              ("2c + next print", 0.02, "next", None)]
    allres, chk1, trs1 = {}, None, None
    for label, slip, delay, names in passes:
        t0 = time.time()
        trs = engine(markets, hist, slip, names, delay)
        chk = recheck(trs, markets, hist, slip, delay)
        allres[label] = chk
        if label == "1c":
            chk1, trs1 = chk, trs
        print(f"pass {label}: {sum(len(t['closed']) for t in trs.values())} trades in {time.time() - t0:.0f}s")
    L += ["## 2. Second simulator vs the backtest engine (real data, +1c)", "",
          "A separate, small simulator re-walked every trade from the raw price history.", "",
          "| Track | Trades | Entry off | Exit off | Profit off | Biggest gap | Take-profits (seen above target) | Extra profit from those | Stops gapped through |",
          "|---|---|---|---|---|---|---|---|---|"]
    tot_bad = 0
    for n, d in sorted(chk1.items(), key=lambda kv: -kv[1]["n"]):
        if not d["n"]:
            continue
        tot_bad += d["bad_entry"] + d["bad_exit"] + d["bad_pnl"] + d["future"]
        L.append(f"| `{n}` | {d['n']} | {d['bad_entry']} | {d['bad_exit']} | {d['bad_pnl']} | ${d['max_diff']:.4f} | "
                 f"{d['tp']} ({d['tp_over']}) | {money(d['tp_over_usd'])} | {d['sl']} ({d['sl_gap']}) |")
    ex = [e for d in chk1.values() for e in d["examples"]][:6]
    L += ["", f"Disagreements: {tot_bad}." + (" Examples: " + "; ".join(ex) if ex else ""), "",
          "History is 12-hourly until the last 2 days, so a take-profit is often first SEEN well above its target. "
          "The engine sells at the price it sees, but the live bot (every 5 minutes) would have sold near the target. "
          "The pessimistic numbers below sell at the target.", ""]

    L += ["## 5. Pessimistic costs", "",
          "Per $100, take-profits capped at the target. 1c = the old main case. 2c = one tick worse. "
          "'1h later' = buy at the price an hour after the signal. 'next print' = buy at the next recorded price "
          "(often 12 hours later in this history).", "",
          "| Track | 1c, as before | 1c, TP capped | 2c | 2c + 1h later | 2c + next print | 1st / 2nd half (2c + 1h) |",
          "|---|---|---|---|---|---|---|"]
    order = sorted(chk1, key=lambda n: -(ratio_stats([(p, s) for p, s, _ in chk1[n]["rows_cap"]]) or {"per100": -999})["per100"])
    for n in order:
        cells = []
        r0 = ratio_stats([(p, s) for p, s, _ in chk1[n]["rows"]])
        if not r0:
            continue
        cells.append(m100(r0["per100"]))
        for label in ("1c", "2c", "2c + 1h later", "2c + next print"):
            s = ratio_stats([(p, b) for p, b, _ in allres[label][n]["rows_cap"]])
            cells.append(f"{m100(s and s['per100'])} ({s['n'] if s else 0})")
        a, b = halves_of(allres["2c + 1h later"][n]["rows_cap"])
        L.append(f"| `{n}` | " + " | ".join(cells) + f" | {m100(a and a['per100'])} / {m100(b and b['per100'])} |")
    L.append("")
    print("\n".join(L[-40:]))

    # 3. random entries, held
    t0 = time.time()
    rh, rb, got = random_hold(markets, hist)
    L += ["## 3. Random entries on the real data, held to the end", "",
          f"{got:,} random (market, moment, side) picks. If prices are fair on average, this loses about the costs.", "",
          "| Slippage | Per $100 | 90% band |", "|---|---|---|"]
    for s, v in rh.items():
        L.append(f"| +{int(s * 100)}c | {m100(v and v['per100'])} | {band(v)} |")
    L += ["", "By price at +1c (costs = slippage + fee per $100 staked):", "", "| Price | Bets | Per $100 | Costs alone |",
          "|---|---|---|---|"]
    for b in ("2-20c", "20-50c", "50-80c", "80-98c"):
        if b in rb:
            s, c = rb[b]
            L.append(f"| {b} | {s['n']} | {m100(s['per100'])} | -${c:.2f} |")
    L += ["", f"({time.time() - t0:.0f}s)", ""]

    # 4. strategy vs random twins with the same exits
    t0 = time.time()
    rv = random_vs_strategy(trs1, markets, hist, 0.01)
    L += ["## 4. Each strategy vs random entries with the same exits (+1c, take-profits at the target)", "",
          "Twins: random markets open at the same hour, same days-to-end window, same take-profit / stop rules. "
          "'Same band' = the twin's side is also in the strategy's price band; 'any' = any side at 5-95c. "
          "Strategy column is the second simulator's own replay of the strategy's trades.", "",
          "| Track | Trades | Strategy | Random, same band | Random, any price | Beats same-band twins by | 90% band of that |",
          "|---|---|---|---|---|---|---|"]
    for n in order:
        v = rv.get(n)
        if not v or not v["strat"]:
            continue
        s, a, b = v["strat"], v["same"], v["any"]
        if a:
            d = s["per100"] - a["per100"]
            se = math.sqrt(s["se"] ** 2 + a["se"] ** 2)
            dd, db = m100(d), f"{m100(d - 1.645 * se)} to {m100(d + 1.645 * se)}"
        else:
            dd = db = "-"
        L.append(f"| `{n}` | {s['n']} | {m100(s['per100'])} | {m100(a and a['per100'])} | {m100(b and b['per100'])} | {dd} | {db} |")
    L += ["", f"({time.time() - t0:.0f}s)", ""]

    # 6. sweep + walk-forward
    t0 = time.time()
    sw = add_sweep_tracks()
    try:
        trs = engine(markets, hist, 0.02, sw, 3600)
        chk = recheck(trs, markets, hist, 0.02, 3600)
        wf, wl = walk_forward(chk, sw)
    finally:
        drop_sweep_tracks(sw)
    L += ["## 6. Panic family: sweep on one half, test on the other (2c + 1h later, TP capped)", "",
          f"12 versions of the panic rule (drop size x lowest price). Halves split at {WF.get('split')} (the middle "
          "trade of the family).", ""] + wf + [""] + wl
    L += ["", f"({time.time() - t0:.0f}s)", ""]

    # 7. mention_no from scratch
    allm = dict(markets_all)
    allm.update({k: v for k, v in small.items() if k not in allm})
    allh = dict(hist)
    allh.update(shist)
    mt, main = mention_table(allm, allh, T(HOLDOUT_FROM))
    L += ["## 7. mention_no rebuilt from scratch", "",
          "Own code: one bet per event, bought the first time a 'will X say Y' market is within 7 days of its end "
          "with NO at 25-90c, held to the result. Includes the small-market sample. calib.md said +$15 per $100.", ""] + mt
    L += ["", f"Total run {time.time() - t_all:.0f}s.", ""]
    os.makedirs(OUT, exist_ok=True)
    txt = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "checks.md"), "w") as fh:
        fh.write(txt)
    print(txt)


# ================================================================ holdout (one time)

HOLDOUT_TESTS = {
    "mention_no": "mention_no rule as in section 7: NO 25-90c, +2c, one bet per event",
    "panic_fade_10c": "panic_fade_10c through the engine at 2c + 1h later, take-profit capped at the target",
}


def holdout(force=False):
    path = os.path.join(OUT, "holdout.md")
    now_ = bot.now()
    if now_ < dt.datetime.fromisoformat(HOLDOUT_OPEN).replace(tzinfo=UTC) and not force:
        print(f"Holdout is closed until {HOLDOUT_OPEN}. Not looking.")
        return
    if os.path.exists(path) and not force:
        print("The holdout has already been used (backtest/holdout.md in the repo). A second look would turn it into "
              "in-sample data.")
        return
    bt.Clock.real_now = now_
    bt.fetch()  # bring the cache up to date: the holdout markets are the newest ones
    markets_all, hist = load_cache()
    cut = T(HOLDOUT_FROM)
    hold = {k: m for k, m in markets_all.items() if m["end"] >= cut}
    L = ["# Holdout result (one-time)", "", f"Run {bot.iso(now_)}. Markets ending {HOLDOUT_FROM} or later: {len(hold):,}.", ""]
    rows = mention_bets(markets_all, hist, t_from=cut)
    s = ratio_stats([(a, b) for a, b, _ in rows])
    L.append(f"- mention_no: {s['n'] if s else 0} events, {m100(s and s['per100'])} per $100, band {band(s)}")
    trs = engine(hold, hist, 0.02, ["panic_fade_10c"], 3600)
    chk = recheck(trs, hold, hist, 0.02, 3600)
    s = ratio_stats([(p, b) for p, b, _ in chk["panic_fade_10c"]["rows_cap"]])
    L.append(f"- panic_fade_10c: {s['n'] if s else 0} trades, {m100(s and s['per100'])} per $100, band {band(s)}")
    L += ["", "Pass bar (written before looking, PROTOCOL.md): ahead at these pessimistic costs AND the band's low end "
              "above -$5 per $100. A pass is not proof; it only means the lead survived one fresh look."]
    txt = "\n".join(L) + "\n"
    with open(path, "w") as fh:
        fh.write(txt)
    print(txt)


# ================================================================ offline selftest

def selftest():
    bt.Clock.real_now = None
    t0 = time.time()
    res, trs, markets, hist = fair_world(0.01, n=1500)
    tab, bad = fair_table(res, z=3.0)
    print("\n".join(tab))
    total = sum(len(t["closed"]) for t in trs.values())
    assert total > 300, total
    assert not bad, f"engine shows money in a fair world: {bad}"
    chk = recheck(trs, markets, hist, 0.01)
    off = sum(d["bad_entry"] + d["bad_exit"] + d["bad_pnl"] for d in chk.values())
    assert off == 0, {n: (d["bad_entry"], d["bad_exit"], d["bad_pnl"], d["examples"]) for n, d in chk.items() if d["examples"]}
    bres, _, _, _ = fair_world(0.01, bug=True, names=["panic_fade", "panic_fade_10c", "claude", "fav_cut_losses"], n=1500)
    btab, bbad = fair_table(bres, z=3.0)
    print("\n".join(btab))
    assert bbad, "planted stop-loss bug was not caught"
    print(f"BTCHECK SELFTEST OK: {total} fair-world trades, engine and second simulator agree, planted bug caught "
          f"({', '.join(bbad)}) in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "run").replace("btcheck", "").replace("bt", "") or "run"
    {"quiet": quiet_check, "run": run, "self": selftest, "selftest": selftest, "holdout": holdout,
     "holdout_force": lambda: holdout(True)}[cmd]()
