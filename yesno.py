#!/usr/bin/env python3
"""Bet $1 on Yes in every open market vs $1 on No in every open market, every day at 12:00 UTC (2026-11-10).

Research only, PAPER ONLY. Jan's "I know this is dumb, I just have to know". Reads data, never trades, never
writes state/.

Window: the 92 noons from 2026-08-10 to 2026-11-09 (12:00 UTC). Only markets that ended before the holdout day
(2026-11-10) count, so we know how they ended and the holdout stays untouched.

Polymarket: bt_cache + whole events (ideas.load_full). Yes = outcome 0 of a Yes/No market (also Up / Over).
  Price at noon = the last chart point at or before noon (12-hourly, hourly near the end). Three prices:
  "chart" (the dream, no extra cost), "chart +1c" (+ the fee) and a "real buys" sample: for a random set of
  market-days, the first real buy of that side on the trade tape within 3 hours after noon (+ the fee).
Kalshi: settled markets (live + /historical endpoints), no combo (MVE) markets. A random sample of up to
  YESNO_K_PER_DAY markets per close day among those open at some noon in the window, weighted back up to every
  market that closed that day. Price = the real ask at noon from the hourly candles (Yes = yes_ask,
  No = 1 - yes_bid), + Kalshi's taker fee (0.07 x P x (1-P) a contract).

    python3 backtest.py btyesno      # probe `btyesno` (fetch Kalshi + run both), report backtest/yesno.md
    python3 yesno.py selftest        # offline checks
"""
import bisect
import collections
import datetime as dt
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import backtest as bt

DAY = 86400
FIRST_NOON = "2026-08-10"
LAST_NOON = "2026-11-09"
HOLDOUT_FROM = "2026-11-10"
K = bot.KALSHI
CACHE = os.path.join(bt.CACHE, "yesno")
K_MK = os.path.join(CACHE, "kalshi_markets.json.gz")
K_H = os.path.join(CACHE, "kalshi_noon.json.gz")
K_PER_DAY = int(os.environ.get("YESNO_K_PER_DAY", "400"))
TAPE_N = int(os.environ.get("YESNO_TAPE_N", "1500"))
T0 = time.time()
BANDS = [(0, 0.10, "under 10c"), (0.10, 0.30, "10-30c"), (0.30, 0.50, "30-50c"), (0.50, 0.70, "50-70c"),
         (0.70, 0.90, "70-90c"), (0.90, 0.97, "90-97c"), (0.97, 1.01, "97c+")]
YES_WORDS = {"yes", "up", "over"}


def tsec(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())


NOONS = list(range(tsec(FIRST_NOON) + 12 * 3600, tsec(LAST_NOON) + 12 * 3600 + 1, DAY))
CUT = tsec(HOLDOUT_FROM)
HALF = NOONS[len(NOONS) // 2]


def band(p):
    for a, b, name in BANDS:
        if a <= p < b:
            return name
    return BANDS[-1][2]


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.2f}"


def iso_ts(x):
    if not x:
        return None
    d = bot.parse_iso(x) if isinstance(x, str) else None
    return int(d.timestamp()) if d else None


# ================================================================ one $1 bet
def bet(price, pay, fee_fn, w=1.0):
    """$1 (times weight w) on a side priced `price` that pays `pay` per share. -> (profit, stake)."""
    f = fee_fn(price)
    cost_per_share = price + f
    shares = 1.0 / cost_per_share
    return w * (shares * pay - 1.0), w


class Tally:
    """profit and stake by key (side, band, half)."""
    def __init__(self):
        self.d = collections.defaultdict(lambda: [0.0, 0.0, 0])

    def add(self, keys, pr, st):
        for k in keys:
            e = self.d[k]
            e[0] += pr
            e[1] += st
            e[2] += 1

    def per100(self, k):
        e = self.d.get(k)
        return (100 * e[0] / e[1]) if e and e[1] else None

    def row(self, k):
        return self.d.get(k) or [0.0, 0.0, 0]


# ================================================================ Polymarket
def poly_side_index(mk):
    """index of the 'Yes' outcome, or None if the market isn't a Yes/No (or Up/Down, Over/Under) market."""
    outs = [o.strip().lower() for o in mk.get("outs") or []]
    if len(outs) != 2:
        return None
    if outs[0] in YES_WORDS:
        return 0
    if outs[1] in YES_WORDS:
        return 1
    return None


def poly_signals():
    import ideas
    import calib
    markets, hist, complete = ideas.load_full()
    print(f"poly: {len(markets):,} markets loaded, {len(hist):,} with history, "
          f"{'no whole-event list' if complete is None else f'{len(complete):,} complete events'}")
    out, skipped = [], collections.Counter()
    for mid, mk in markets.items():
        if not mk.get("end") or mk["end"] >= CUT:
            skipped["ends in holdout"] += 1
            continue
        yi = poly_side_index(mk)
        if yi is None:
            skipped["not yes/no"] += 1
            continue
        y0 = calib.outcome0(mk)
        if y0 is None:
            skipped["not cleanly settled"] += 1
            continue
        h = hist.get(mid)
        if not h or not h[0]:
            skipped["no history"] += 1
            continue
        T, P = h
        stop = min(mk["end"], mk.get("closed_t") or mk["end"])
        pay_yes = y0 if yi == 0 else 1 - y0
        for noon in NOONS:
            if noon >= stop or (mk.get("start") and noon < mk["start"]):
                continue
            k = bisect.bisect_right(T, noon) - 1
            if k < 0 or noon - T[k] > 13 * 3600:
                continue
            p0 = P[k]
            if not 0 < p0 < 1:
                continue
            p_yes = p0 if yi == 0 else 1 - p0
            out.append((mid, noon, p_yes, pay_yes, mk.get("fee") or 0.0, mk.get("ev") or mid, yi, noon - T[k]))
    print(f"poly: {len(out):,} market-days (one Yes bet and one No bet each). Skipped markets: {dict(skipped)}")
    return markets, out


def poly_tally(sigs, extra, max_age=1e9):
    t = Tally()
    for mid, noon, p_yes, pay_yes, fee, ev, yi, age in sigs:
        if age > max_age:
            continue
        h = "first half" if noon < HALF else "second half"
        for side, p, pay in (("Yes", p_yes, pay_yes), ("No", 1 - p_yes, 1 - pay_yes)):
            c = min(0.999, p + extra)
            pr, st = bet(c, pay, lambda x: fee * x * (1 - x))
            t.add([(side,), (side, band(p)), (side, h)], pr, st)
    return t


def poly_tape_sample(markets, sigs, n=TAPE_N, window=3 * 3600):
    """Random market-days per side: the first real buy of that side within `window` after noon."""
    import informed
    rng = random.Random(11)
    picks = rng.sample(sigs, min(n, len(sigs)))
    ids = sorted({s[0] for s in picks})
    cids = informed.cids_for(ids)
    print(f"poly tape: {len(picks)} market-days, {len(cids)} of {len(ids)} condition ids found")
    tapes = {}

    def one(mid):
        try:
            return mid, informed.tape(cids[mid], 40)[0]
        except Exception:
            return mid, None
    with ThreadPoolExecutor(8) as ex:
        for mid, rows in ex.map(one, [m for m in ids if m in cids]):
            tapes[mid] = rows
    print(f"poly tape: {sum(1 for v in tapes.values() if v)} tapes read ({time.time() - T0:.0f}s)")
    t, same, gap, miss = Tally(), Tally(), collections.defaultdict(list), collections.Counter()
    for mid, noon, p_yes, pay_yes, fee, ev, yi, age in picks:
        rows = tapes.get(mid)
        if not rows:
            miss["no tape"] += 2
            continue
        mk = markets[mid]
        for side, oi, p_chart, pay in (("Yes", yi, p_yes, pay_yes), ("No", 1 - yi, 1 - p_yes, 1 - pay_yes)):
            first = None
            for r in rows:
                ts = bot.fnum(bot.pick(r, "timestamp", "time"))
                ts = ts / 1000 if ts > 1e11 else ts
                if not noon <= ts < noon + window:
                    continue
                o = r.get("outcome_index", r.get("outcomeIndex"))
                if o not in (0, 1):
                    tok = str(bot.pick(r, "token_id", "asset", default=""))
                    o = 0 if mk.get("toks") and tok == mk["toks"][0] else 1 if mk.get("toks") and tok == mk["toks"][1] else None
                px = bot.fnum(r.get("price"))
                if o == oi and str(r.get("side") or "").upper().startswith("B") and 0 < px < 1:
                    if first is None or ts < first[0]:
                        first = (ts, px)
            if not first:
                miss["nobody bought in 3h"] += 1
                continue
            px = first[1]
            pr, st = bet(px, pay, lambda x: fee * x * (1 - x))
            t.add([(side,), (side, band(p_chart))], pr, st)
            same.add([(side,), (side, band(p_chart))], *bet(p_chart, pay, lambda x: fee * x * (1 - x)))
            gap[side].append(px - p_chart)
            gap[band(p_chart)].append(px - p_chart)
    print(f"poly tape: misses {dict(miss)}")
    return t, same, gap, miss


# ================================================================ Kalshi
_CUT = [None]


def kget(path, p=None):
    """Kalshi GET with a few slow retries on 429 (too many requests), which cut short the first listing."""
    for i in range(5):
        try:
            return bot.http_json(f"{K}{path}", p)
        except Exception as e:
            if "429" not in str(e) or i == 4:
                raise
            time.sleep(2 * 2 ** i)


def k_cutoff():
    if _CUT[0] is None:
        try:
            _CUT[0] = iso_ts(kget("/historical/cutoff").get("market_settled_ts")) or 0
        except Exception as e:
            print("kalshi cutoff failed", e)
            _CUT[0] = 0
    return _CUT[0]


def k_day(d0):
    """All settled non-combo markets closing on day d0 (unix), live endpoint + /historical."""
    t0, t1 = d0, d0 + DAY - 1
    rows, cut = [], k_cutoff()
    for path in ("/markets", "/historical/markets"):
        if path == "/historical/markets" and (not cut or t0 >= cut):
            continue
        if path == "/markets" and cut and t1 < cut:
            continue
        cur = None
        for _ in range(400):
            p = {"min_close_ts": t0, "max_close_ts": t1, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
                p["mve_filter"] = "exclude"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  kalshi {path} {bot.iso(dt.datetime.fromtimestamp(d0, dt.timezone.utc))[:10]} failed: {str(e)[:120]}")
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    seen, ok = set(), []
    for m in rows:
        tk = str(m.get("ticker") or "")
        if not tk or tk in seen or tk.startswith("KXMVE"):
            continue
        seen.add(tk)
        res = str(m.get("result") or "").lower()
        o, c = iso_ts(m.get("open_time")), iso_ts(m.get("close_time"))
        if res not in ("yes", "no") or not o or not c or not t0 <= c <= t1:
            continue
        noons = [n for n in NOONS if o <= n < c]
        if not noons:
            continue
        ok.append({"t": tk, "s": str(m.get("event_ticker") or "").split("-")[0], "ev": m.get("event_ticker"),
                   "q": f"{m.get('title') or ''} {m.get('yes_sub_title') or ''}".strip()[:140],
                   "open": o, "close": c, "res": res, "n1": noons[0], "n2": noons[-1]})
    return d0, len(rows), ok


def k_candle(c):
    def px(block):
        b = c.get(block) or {}
        v = b.get("close_dollars")
        if v not in (None, ""):
            return bot.fnum(v, None)
        v = b.get("close")
        return None if v in (None, "") else bot.fnum(v, 0) / 100
    return int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask")


def k_noon_quotes(m):
    """{noon: [yes_bid, yes_ask]} from hourly candles; one call per market (two for very long ones)."""
    out = {}
    spans, a = [], m["n1"] - 3600
    while a < m["n2"]:
        b = min(m["n2"], a + 180 * DAY)
        spans.append((a, b))
        a = b
    for a, b in spans:
        got = None
        for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
            try:
                r = kget(path, {"start_ts": a, "end_ts": b, "period_interval": 60})
            except Exception:
                continue
            cs = r.get("candlesticks") if isinstance(r, dict) else None
            if cs:
                got = cs
                break
        if got is None:
            continue
        noonset = set(NOONS)
        for c in got:
            t, bid, ask = k_candle(c)
            if t in noonset:
                out[str(t)] = [bid, ask]
    return m["t"], out


def fetch_kalshi():
    os.makedirs(CACHE, exist_ok=True)
    have = bt.rjson(K_MK, {"days": {}, "markets": {}}) or {"days": {}, "markets": {}}
    days = [d for d in range(tsec(FIRST_NOON), tsec(LAST_NOON) + 1, DAY) if str(d) not in have["days"]]
    print(f"kalshi: {len(have['days'])} days listed before, {len(days)} to list (cutoff {k_cutoff()})")
    with ThreadPoolExecutor(4) as ex:
        for d0, n, ok in ex.map(k_day, days):
            rng = random.Random(d0)
            pick = rng.sample(ok, min(K_PER_DAY, len(ok)))
            have["days"][str(d0)] = {"listed": n, "eligible": len(ok), "sampled": len(pick)}
            for m in pick:
                have["markets"][m["t"]] = m
            print(f"  {bot.iso(dt.datetime.fromtimestamp(d0, dt.timezone.utc))[:10]}: {n} settled, {len(ok)} open at a noon, "
                  f"sampled {len(pick)} ({time.time() - T0:.0f}s)")
    bt.wjson(K_MK, have)
    hist = bt.rjson(K_H, {}) or {}
    todo = [m for m in have["markets"].values() if m["t"] not in hist]
    print(f"kalshi candles: {len(hist)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(6) as ex:
        for i in range(0, len(todo), 2000):
            for tk, q in ex.map(k_noon_quotes, todo[i:i + 2000]):
                hist[tk] = q
            bt.wjson(K_H, hist)
            print(f"  {min(i + 2000, len(todo))}/{len(todo)} ({time.time() - T0:.0f}s)")
    bt.wjson(K_H, hist)


def kalshi_tally():
    import launch
    have = bt.rjson(K_MK, {}) or {}
    hist = bt.rjson(K_H, {}) or {}
    days = have.get("days") or {}
    t, cats, info = Tally(), Tally(), collections.Counter()
    tu, tight, mid = Tally(), Tally(), Tally()
    for tk, m in (have.get("markets") or {}).items():
        d0 = str(m["close"] - m["close"] % DAY)
        dd = days.get(d0) or {}
        w = (dd.get("eligible") or 0) / max(1, dd.get("sampled") or 0)
        q = hist.get(tk)
        if q is None:
            info["no candles"] += 1
            continue
        pay_yes = 1.0 if m["res"] == "yes" else 0.0
        cat = launch.kcategory(m["s"], m["q"])
        for n in NOONS:
            if not m["open"] <= n < m["close"]:
                continue
            ba = q.get(str(n))
            if not ba:
                info["noon without a quote"] += 1
                continue
            bid, ask = ba
            sp = None if bid is None or ask is None else ask - bid
            info["spread 5c or less" if sp is not None and sp <= 0.05 else "spread over 5c (or one side empty)"] += 1
            if sp is not None and 0 < bid and ask < 1 and sp > 0:
                mp = (bid + ask) / 2
                for side, p, pay in (("Yes", mp, pay_yes), ("No", 1 - mp, 1 - pay_yes)):
                    mid.add([(side,), (side, band(p))], *bet(p, pay, lambda x: 0.0, w))
            h = "first half" if n < HALF else "second half"
            kfee = lambda x: 0.07 * x * (1 - x)
            for side, p, pay in (("Yes", ask, pay_yes), ("No", None if bid is None else 1 - bid, 1 - pay_yes)):
                if p is None or not 0 < p < 1:
                    info[f"{side}: nobody selling"] += 1
                    continue
                pr, st = bet(p, pay, kfee, w)
                t.add([(side,), (side, band(p)), (side, h)], pr, st)
                cats.add([(side, cat)], pr, st)
                tu.add([(side,), (side, band(p))], *bet(p, pay, kfee))
                if sp is not None and sp <= 0.05:
                    tight.add([(side,), (side, band(p))], pr, st)
            info["market-days"] += 1
    info["markets sampled"] = len(have.get("markets") or {})
    info["markets that closed in the window (all)"] = sum((d.get("eligible") or 0) for d in days.values())
    return t, cats, info, tu, tight, mid


# ================================================================ report
def table(title, tallies, note=""):
    """tallies: [(column name, Tally)]"""
    L = [f"### {title}", "", note, "" if note else None]
    L = [x for x in L if x is not None]
    head = "| What you bought | " + " | ".join(n for n, _ in tallies) + " |"
    L += [head, "|" + "---|" * (len(tallies) + 1)]
    for side in ("Yes", "No"):
        cells = []
        for n, t in tallies:
            v = t.per100((side,))
            cells.append("-" if v is None else f"**{usd(v)}**")
        L.append(f"| **All {side}** | " + " | ".join(cells) + " |")
        for _, _, b in BANDS:
            cells = []
            for n, t in tallies:
                v = t.per100((side, b))
                cnt = t.row((side, b))[2]
                cells.append("-" if v is None else f"{usd(v)} ({cnt:,})")
            L.append(f"| {side} at {b} | " + " | ".join(cells) + " |")
    return L + [""]


def run():
    L = ["# All Yes vs all No (2026-11-10, `yesno.py`)", "",
         "Research only. Jan's question: what if you put $1 on Yes in **every** open market every day, or $1 on No in every "
         f"open market, at 12:00 UTC, for 3 months ({FIRST_NOON} to {LAST_NOON}, {len(NOONS)} days)? Polymarket and Kalshi "
         "separately. Numbers are profit per $100 bet. In brackets: how many $1 bets.", ""]
    # ---- Polymarket
    try:
        markets, sigs = poly_signals()
    except Exception as e:
        print("poly failed", e)
        markets, sigs = {}, []
    if sigs:
        dream, plus1 = poly_tally(sigs, 0.0), poly_tally(sigs, 0.01)
        plus03, fresh = poly_tally(sigs, 0.003), poly_tally(sigs, 0.003, max_age=3600)
        tape, same, gap, miss = poly_tape_sample(markets, sigs)
        n_m = len({s[0] for s in sigs})
        L += [f"## Polymarket ({n_m:,} markets, {len(sigs):,} market-days)", ""]
        cols = [("Chart price (the dream)", dream), ("Chart +0.3c + fee", plus03), ("Same, only prices under 1h old", fresh),
                ("Chart +1c + fee", plus1), (f"Real buys (sample of {min(TAPE_N, len(sigs)):,} days)", tape),
                ("Same sample at chart price", same)]
        L += table("Profit per $100", cols, "Real buys = the first time a real person bought that side within 3 hours after noon, "
                   "on the trade tape. That's what a slow bot would really pay.")
        for side in ["Yes", "No"] + [b for _, _, b in BANDS]:
            g = sorted(gap.get(side) or [])
            if g:
                L.append(f"- {side}: real buyers paid a median {100 * g[len(g) // 2]:+.1f}c vs the chart "
                         f"({len(g)} buys).")
        L += [f"- Tape misses: {dict(miss)}", ""]
        L += ["Halves (chart +0.3c): " + ", ".join(f"{s} {h} {usd(plus03.per100((s, h)) or 0)}"
                                                  for s in ("Yes", "No") for h in ("first half", "second half")), ""]
        for side in ("Yes", "No"):
            pr, st, n = plus1.row((side,))
            print(f"POLY {side}: {n:,} bets, ${st:,.0f} bet, profit {usd(pr)} = {usd(100 * pr / st)} per $100 (chart +1c)")
            print(f"POLY {side}: dream {usd(dream.per100((side,)))}, real-buy sample {usd(tape.per100((side,)) or 0)}")
    # ---- Kalshi
    kt, kc, info, ku, ktight, kmid = kalshi_tally()
    if kt.d:
        L += [f"## Kalshi (sample of {info['markets sampled']:,} of {info['markets that closed in the window (all)']:,} "
              f"markets, weighted back to all of them)", ""]
        L += table("Profit per $100, at the real ask + fee", [("Middle of bid and ask, no fee (the dream)", kmid),
                   ("Real ask + fee", kt), ("Same, not scaled up", ku), ("Real ask, only tight prices (bid and ask 5c apart or less)", ktight)],
                   "Kalshi's history has the real best bid and ask each hour, so 'real ask' is what you'd really pay. "
                   "Many quiet Kalshi markets show silly prices like 'buy at 99c, sell at 1c'; the last column skips those.")
        L += ["Halves: " + ", ".join(f"{s} {h} {usd(kt.per100((s, h)) or 0)}" for s in ("Yes", "No")
                                     for h in ("first half", "second half")), ""]
        cl = sorted({k[1] for k in kc.d})
        L += ["### Kalshi by kind of market (per $100)", "", "| Kind | Yes | No |", "|---|---|---|"]
        for c in cl:
            y, n = kc.per100(("Yes", c)), kc.per100(("No", c))
            L.append(f"| {c} | {'-' if y is None else usd(y)} | {'-' if n is None else usd(n)} |")
        L += ["", f"Data notes: {dict(info)}", ""]
        for side in ("Yes", "No"):
            pr, st, n = kt.row((side,))
            print(f"KALSHI {side}: {n:,} sampled bets, weighted ${st:,.0f} bet, profit {usd(pr)} = {usd(100 * pr / st)} per $100")
    L += ["## Limits", "",
          "- Only markets that ended before 2026-11-10 count (we need the result, and later ones are the holdout). So on "
          "the last days of the window only short markets are in.",
          "- Polymarket: bt_cache only has markets that ended with $20k+ traded, plus every choice of those events. "
          "Tiny markets are missing. Chart prices are 12-hourly, so 'noon' can be up to 13 hours old.",
          "- Kalshi: a random sample per close day, scaled up. Fee as if orders were big enough not to round up.", ""]
    os.makedirs(bt.OUT if hasattr(bt, "OUT") else "backtest", exist_ok=True)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "yesno.md")
    with open(path, "w") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


# ================================================================ selftest
def selftest():
    # a fair coin at 50c, both sides: dream loses only the fee
    pr, st = bet(0.5, 1.0, lambda x: 0.0)
    assert abs(pr - 1.0) < 1e-9 and st == 1.0, (pr, st)
    pr, st = bet(0.5, 0.0, lambda x: 0.0)
    assert abs(pr + 1.0) < 1e-9
    # a fairly priced world: Yes at p wins with chance p -> about zero
    rng = random.Random(1)
    t = Tally()
    for _ in range(200000):
        p = rng.uniform(0.02, 0.98)
        y = 1.0 if rng.random() < p else 0.0
        for side, q, pay in (("Yes", p, y), ("No", 1 - p, 1 - y)):
            t.add([(side,)], *bet(q, pay, lambda x: 0.0))
    assert abs(t.per100(("Yes",))) < 2 and abs(t.per100(("No",))) < 2, (t.per100(("Yes",)), t.per100(("No",)))
    # weights scale both profit and stake
    pr, st = bet(0.25, 1.0, lambda x: 0.0, w=3)
    assert abs(pr - 9.0) < 1e-9 and st == 3
    assert band(0.05) == "under 10c" and band(0.95) == "90-97c" and band(0.99) == "97c+"
    assert poly_side_index({"outs": ["Yes", "No"]}) == 0 and poly_side_index({"outs": ["Down", "Up"]}) == 1
    assert poly_side_index({"outs": ["Lakers", "Celtics"]}) is None
    assert len(NOONS) == 92 and NOONS[0] % DAY == 12 * 3600
    print("yesno selftest OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"selftest": selftest, "run": run, "fetch": fetch_kalshi, "all": lambda: (fetch_kalshi(), run())}[cmd]()
