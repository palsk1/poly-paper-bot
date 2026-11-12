#!/usr/bin/env python3
"""Options price as the fair price for Polymarket's Bitcoin / Ethereum price markets (2026-11-12).

The question: professional options traders on Deribit price how much Bitcoin and Ethereum are expected to move
(the DVOL index, public, hourly). Polymarket has thousands of "Will Bitcoin reach $X this week / month?",
"Will Bitcoin dip to $X?" and "Will the price of Bitcoin be above $X on <day>?" markets. If Polymarket's price is
far from what the options market says, buy the cheap side and hold to the result.

    python3 optfair.py fetch      # Deribit DVOL + Binance hourly candles + hourly Polymarket charts (Actions only)
    python3 optfair.py run        # backtest/optfair.md
    python3 optfair.py selftest

Data in bt_cache/opt/ (shared price store). Only markets that ended before the holdout day are used.
"""
import bisect
import collections
import concurrent.futures as cf
import math
import os
import re
import sys
import time

import backtest as bt
import bot
import btcheck

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(bt.CACHE, "opt")
OUT = os.path.join(bt.OUT, "optfair.md")
DERIBIT = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
BINANCE = "https://data-api.binance.vision/api/v3/klines"
CLOB = "https://clob.polymarket.com"
T_START = 1771113600            # 2026-02-15
COINS = {"BTC": ("BTCUSDT", re.compile(r"\b(bitcoin|btc)\b", re.I)), "ETH": ("ETHUSDT", re.compile(r"\b(ethereum|eth)\b", re.I))}
YEAR = 365.25 * 86400
T0 = time.time()
BUDGET_MIN = float(os.environ.get("OPT_MIN", "200"))
WORKERS = int(os.environ.get("OPT_WORKERS", "8"))


def T(day):
    return btcheck.T(day)


# ================================================================ which markets
def num(s):
    s = s.replace(",", "").replace("$", "").strip().lower()
    mult = 1
    if s.endswith("k"):
        mult, s = 1000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1e6, s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return None


NUM = r"\$?([0-9][0-9,]*\.?[0-9]*[km]?)"


def parse(q):
    """-> dict(coin, kind, k or (lo, hi)) or None. kinds: up (reach), down (dip), above, below, between."""
    ql = q.lower()
    if "up or down" in ql:
        return None
    coin = next((c for c, (_, pat) in COINS.items() if pat.search(q)), None)
    if not coin or sum(1 for _, pat in COINS.values() if pat.search(q)) > 1:
        return None
    m = re.search(r"will (?:the price of )?(?:bitcoin|btc|ethereum|eth) (reach|hit|dip to|drop to|fall to) " + NUM, ql)
    if m:
        k = num(m.group(2))
        return {"coin": coin, "kind": "up" if m.group(1) in ("reach", "hit") else "down", "k": k} if k else None
    m = re.search(r"price of (?:bitcoin|btc|ethereum|eth) be between " + NUM + r" and " + NUM + r" on ", ql)
    if m:
        a, b = num(m.group(1)), num(m.group(2))
        return {"coin": coin, "kind": "between", "k": (a, b)} if a and b and a < b else None
    m = re.search(r"price of (?:bitcoin|btc|ethereum|eth) be (above|greater than|below|less than) " + NUM + r" on ", ql)
    if m:
        k = num(m.group(2))
        return {"coin": coin, "kind": "above" if m.group(1) in ("above", "greater than") else "below", "k": k} if k else None
    return None


def pick_markets(markets):
    out = {}
    for mid, m in markets.items():
        p = parse(m.get("q", ""))
        if not p or len(m.get("toks") or []) != 2 or not m.get("end") or not m.get("start"):
            continue
        if [str(o).lower() for o in m.get("outs", [])] != ["yes", "no"]:
            continue
        out[mid] = dict(p, id=mid, q=m["q"], start=m["start"], end=m["end"], final=m.get("final"), fee=m.get("fee") or 0.0,
                        vol=m.get("vol") or 0, ev=m.get("ev") or mid, tok=m["toks"][0], toks=m["toks"], closed_t=m.get("closed_t"))
    return out


# ================================================================ download
def fetch_dvol(coin, have):
    """Hourly DVOL closes {hour ts: vol in percent}. Deribit pages backwards with a continuation stamp."""
    end = int(time.time() * 1000)
    start = T_START * 1000
    for _ in range(400):
        res = bot.http_json(DERIBIT, {"currency": coin, "start_timestamp": start, "end_timestamp": end, "resolution": 3600}).get("result") or {}
        rows = res.get("data") or []
        for r in rows:
            have[str(int(r[0] // 1000))] = r[4]
        cont = res.get("continuation")
        if not cont or not rows or cont <= start:
            break
        end = cont
    return have


def fetch_spot(symbol, have):
    """Hourly Binance candles {hour ts: [open, high, low, close]}."""
    t = max([int(k) for k in have] or [T_START]) * 1000
    while True:
        rows = bot.http_json(BINANCE, {"symbol": symbol, "interval": "1h", "startTime": t, "limit": 1000})
        if not rows:
            break
        for r in rows:
            have[str(int(r[0] // 1000))] = [float(r[1]), float(r[2]), float(r[3]), float(r[4])]
        if len(rows) < 1000:
            break
        t = rows[-1][0] + 1
    return have


def fetch_chart(m):
    """Hourly price of YES over the market's whole life."""
    pts, s = [], m["start"]
    e_all = min(m.get("closed_t") or m["end"], m["end"]) + 3600
    while s < e_all:
        e = min(s + 14 * 86400, e_all)
        try:
            pts += bt.hist_points(bot.http_json(f"{CLOB}/prices-history", {"market": m["tok"], "startTs": s, "endTs": e, "fidelity": 60}))
        except Exception as ex:
            if "400" not in str(ex):
                return m["id"], None
        s = e
    pts = sorted({int(t): p for t, p in pts if t and p is not None}.items())
    return m["id"], [[t for t, _ in pts], [round(p, 4) for _, p in pts]]


def fetch():
    import ideas
    os.makedirs(CACHE, exist_ok=True)
    for coin, (sym, _) in COINS.items():
        p = os.path.join(CACHE, f"dvol_{coin}.json.gz")
        d = fetch_dvol(coin, bt.rjson(p, {}) or {})
        bt.wjson(p, d)
        p = os.path.join(CACHE, f"spot_{coin}.json.gz")
        s = fetch_spot(sym, bt.rjson(p, {}) or {})
        bt.wjson(p, s)
        ks = sorted(int(k) for k in d)
        print(f"{coin}: {len(d)} DVOL hours ({ks[0] if ks else '-'} to {ks[-1] if ks else '-'}), {len(s)} spot hours, "
              f"last DVOL {d.get(str(ks[-1])) if ks else '-'}", flush=True)
    markets, _, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m["final"]}
    print("markets", len(ms), collections.Counter((m["coin"], m["kind"]) for m in ms.values()).most_common(), flush=True)
    hp = os.path.join(CACHE, "charts.json.gz")
    charts = bt.rjson(hp, {}) or {}
    todo = [m for k, m in ms.items() if k not in charts]
    todo.sort(key=lambda m: -m["vol"])
    done = 0
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for mid, h in ex.map(fetch_chart, todo):
            if h is not None:
                charts[mid] = h
            done += 1
            if done % 1000 == 0:
                bt.wjson(hp, charts)
                print(f"  charts {done}/{len(todo)} ({(time.time() - T0) / 60:.0f} min)", flush=True)
            if (time.time() - T0) / 60 > BUDGET_MIN:
                print("time budget used, run again to continue")
                break
    bt.wjson(hp, charts)
    print(f"charts saved: {len(charts)}, with points: {sum(1 for h in charts.values() if h[0])}")


# ================================================================ the model
def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def p_above(s, k, vol, t):
    """Chance the price ends above k after t years (no drift in the log price besides the usual -vol^2/2)."""
    if t <= 0 or vol <= 0:
        return 1.0 if s > k else 0.0
    return ncdf((math.log(s / k) - 0.5 * vol * vol * t) / (vol * math.sqrt(t)))


def p_touch(s, k, vol, t):
    """Chance the price touches k at some point within t years (reflection rule with the -vol^2/2 drift)."""
    if (k >= s and s >= k) or t <= 0 or vol <= 0:
        return 1.0 if s == k else 0.0
    mu = -0.5 * vol * vol
    b = abs(math.log(k / s))
    up = k > s
    m = mu if up else -mu                      # drift toward the barrier
    sd = vol * math.sqrt(t)
    return min(1.0, ncdf((-b + m * t) / sd) + math.exp(2 * m * b / (vol * vol)) * ncdf((-b - m * t) / sd))


def fair(m, s, vol, t):
    k = m["k"]
    if m["kind"] == "up":
        return 1.0 if s >= k else p_touch(s, k, vol, t)
    if m["kind"] == "down":
        return 1.0 if s <= k else p_touch(s, k, vol, t)
    if m["kind"] == "above":
        return p_above(s, k, vol, t)
    if m["kind"] == "below":
        return 1 - p_above(s, k, vol, t)
    return p_above(s, k[0], vol, t) - p_above(s, k[1], vol, t)


class Series:
    def __init__(self, d):
        self.t = sorted(int(k) for k in d)
        self.v = [d[str(k)] for k in self.t]

    def at(self, ts, max_age=3 * 3600):
        """Last value at or before ts."""
        i = bisect.bisect_right(self.t, ts) - 1
        if i < 0 or ts - self.t[i] > max_age:
            return None
        return self.v[i]

    def window(self, a, b):
        i, j = bisect.bisect_left(self.t, a), bisect.bisect_right(self.t, b)
        return self.v[i:j]


def load():
    import ideas
    markets, hist, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m["final"] and m["final"][0] in (0.0, 1.0)}
    charts = bt.rjson(os.path.join(CACHE, "charts.json.gz"), {}) or {}
    dvol = {c: Series(bt.rjson(os.path.join(CACHE, f"dvol_{c}.json.gz"), {}) or {}) for c in COINS}
    spot = {c: Series(bt.rjson(os.path.join(CACHE, f"spot_{c}.json.gz"), {}) or {}) for c in COINS}
    return ms, charts, hist, dvol, spot


def touched_since(m, spot, t):
    """Did the coin already touch the line between the market's start and t (hourly highs / lows)?"""
    rows = spot.window(m["start"] - m["start"] % 3600, t - 3600)
    if m["kind"] == "up":
        return any(r[1] >= m["k"] for r in rows)
    return any(r[2] <= m["k"] for r in rows)


def signals(ms, charts, dvol, spot, gap=0.05, lo=0.05, hi=0.95, min_left=6 * 3600, max_left=45 * 86400, vol_mult=1.0,
            kinds=None, step=1, first_only=True):
    """Walk each market's hourly chart; where the options price disagrees with Polymarket by `gap` or more
    (after the fee), that is a signal to buy the cheap side. One signal per market (the first)."""
    out = []
    for mid, m in ms.items():
        if kinds and m["kind"] not in kinds:
            continue
        h = charts.get(mid)
        if not h or not h[0]:
            continue
        dv, sp = dvol[m["coin"]], spot[m["coin"]]
        for i in range(0, len(h[0]), step):
            t, p = h[0][i], h[1][i]
            left = m["end"] - t
            if left < min_left or left > max_left or not lo <= p <= hi:
                continue
            c = sp.at(t - 3600, 2 * 3600)          # the candle that CLOSED before t (candle stamps are opens)
            v = dv.at(t - 3600, 6 * 3600)
            if c is None or v is None:
                continue
            s = c[3]
            if m["kind"] in ("up", "down") and touched_since(m, sp, t):
                break
            q = fair(m, s, v / 100 * vol_mult, left / YEAR)
            side = None
            if q - p >= gap:
                side, price, fairp = 0, p, q
            elif p - q >= gap:
                side, price, fairp = 1, 1 - p, 1 - q
            if side is None:
                continue
            out.append({"id": mid, "t": t, "side": side, "p": price, "fair": fairp, "end": m["end"], "ev": m["ev"], "toks": m["toks"],
                        "kind": m["kind"], "coin": m["coin"], "left": left, "fee": m["fee"],
                        "win": (m["final"][0] == 1.0) == (side == 0), "q": m["q"]})
            if first_only:
                break
    return out


def to_bets(sigs, extra=0.01, stake=10.0):
    """Chart-price bets (a first look; real buys come from exam.fills)."""
    bets = []
    for s in sigs:
        c = min(0.99, s["p"] + extra)
        sh = stake / c
        fee = bot.taker_fee(sh, c, s["fee"])
        bets.append({"ev": s["ev"], "t": s["t"], "cost": sh * c + fee, "pay": sh if s["win"] else 0.0, "sh": sh,
                     "kind": s["kind"], "coin": s["coin"], "side": s["side"], "left": s["left"], "p": s["p"], "fair": s["fair"]})
    return bets


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def per100(b):
    c = sum(x["cost"] for x in b)
    return None if not c else (sum(x["pay"] for x in b) - c) / c * 100


def line(name, b):
    if len(b) < 10:
        return f"| {name} | {len(b)} | - | - | - | - |"
    bs = sorted(b, key=lambda x: x["t"])
    h = len(bs) // 2
    return (f"| {name} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b))} | {usd(per100(bs[:h]))} | {usd(per100(bs[h:]))} |")


HEAD = "| what | bets | won | per $100 | first half | second half |\n|---|---|---|---|---|---|"


def calibration(ms, charts, dvol, spot):
    """How well does the options price forecast on its own? Buckets of the model's chance vs how often it happened."""
    rows = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    for mid, m in ms.items():
        h = charts.get(mid)
        if not h or not h[0]:
            continue
        dv, sp = dvol[m["coin"]], spot[m["coin"]]
        # one look per market: the first chart point with 1-3 days left (or the first point at all for short markets)
        for t, p in zip(h[0], h[1]):
            left = m["end"] - t
            if left > 3 * 86400 or left < 6 * 3600:
                continue
            c, v = sp.at(t - 3600, 2 * 3600), dv.at(t - 3600, 6 * 3600)
            if c is None or v is None or not 0.02 <= p <= 0.98:
                break
            if m["kind"] in ("up", "down") and touched_since(m, sp, t):
                break
            q = fair(m, c[3], v / 100, left / YEAR)
            fam = "touch" if m["kind"] in ("up", "down") else "end price"
            for key in ((fam, min(9, int(q * 10))), (fam, "all")):
                r = rows[key]
                r[0] += 1
                r[1] += q
                r[2] += p
                r[3] += m["final"][0]
            break
    return rows


def run(score=True):
    import exam
    ms, charts, hist, dvol, spot = load()
    L = []
    P = L.append
    P("# Options price vs Polymarket's Bitcoin and Ethereum markets (optfair.py)\n")
    have = {k: m for k, m in ms.items() if charts.get(k) and charts[k][0]}
    P(f"Generated {bot.iso()}. {len(have)} finished Polymarket markets on Bitcoin / Ethereum prices with an hourly chart "
      f"(ended before {btcheck.HOLDOUT_FROM}): " + ", ".join(f"{n} {k}" for k, n in collections.Counter(m['kind'] for m in have.values()).most_common()) + ".\n")
    rows = calibration(have, charts, dvol, spot)
    P("## 1. Who forecasts better, the options market or Polymarket?\n")
    P("One look per market, 1-3 days before the end (or at the start for shorter ones).\n")
    P("| kind | options said | markets | options (avg) | Polymarket (avg) | it happened |")
    P("|---|---|---|---|---|---|")
    for fam in ("touch", "end price"):
        for b in list(range(10)) + ["all"]:
            r = rows.get((fam, b))
            if r and r[0] >= 20:
                P(f"| {fam} | {'all' if b == 'all' else f'{b * 10}-{b * 10 + 10} in 100'} | {r[0]} | {r[1] / r[0] * 100:.0f} | {r[2] / r[0] * 100:.0f} | {r[3] / r[0] * 100:.0f} |")
    P("")
    P("## 2. Buy where the two disagree (chart prices + 1c + fee, $10 a bet, first disagreement per market)\n")
    P(HEAD)
    grid = []
    for fam, kinds in (("touch (reach / dip)", ("up", "down")), ("end price (above / below / between)", ("above", "below", "between"))):
        for gap in (0.03, 0.05, 0.08, 0.12):
            sg = signals(have, charts, dvol, spot, gap=gap, kinds=kinds)
            b = to_bets(sg)
            grid.append((fam, gap, b, sg))
            P(line(f"{fam}, gap {gap * 100:.0f}c+", b))
            for side, nm in ((0, "buy Yes"), (1, "buy No")):
                P(line(f"&nbsp;&nbsp;{nm}", [x for x in b if x["side"] == side]))
    P("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return grid


def selftest():
    assert parse("Will Bitcoin reach $105,000 in April?") == {"coin": "BTC", "kind": "up", "k": 105000.0}
    assert parse("Will Ethereum dip to $1,900 in June?") == {"coin": "ETH", "kind": "down", "k": 1900.0}
    assert parse("Will the price of Bitcoin be between $76,000 and $78,000 on October 5?")["k"] == (76000.0, 78000.0)
    assert parse("Will the price of Ethereum be above $2,200 on September 8?")["kind"] == "above"
    assert parse("Will Bitcoin reach $150k in 2026?")["k"] == 150000.0
    assert parse("Bitcoin Up or Down - 5 minutes") is None
    assert abs(p_above(100, 100, 0.5, 1 / 365) - 0.5) < 0.01
    assert p_above(100, 120, 0.5, 7 / 365) < 0.01 and p_above(100, 80, 0.5, 7 / 365) > 0.99
    # touch is about twice the end-above chance for a far line, and symmetric-ish up/down
    a, t2 = p_above(100, 110, 0.6, 30 / 365), p_touch(100, 110, 0.6, 30 / 365)
    assert 1.7 < t2 / a < 2.4, (a, t2)
    assert 0 < p_touch(100, 90, 0.6, 30 / 365) < 1 and p_touch(100, 100.0001, 0.6, 30 / 365) > 0.99
    # Monte Carlo check of the touch rule
    import random
    rng = random.Random(1)
    n, hit, vol, days = 4000, 0, 0.6, 30
    for _ in range(n):
        x, steps = 0.0, days * 24
        dtt = 1 / (365.25 * 24)
        for _ in range(steps):
            x += -0.5 * vol * vol * dtt + vol * math.sqrt(dtt) * rng.gauss(0, 1)
            if x >= math.log(1.1):
                hit += 1
                break
    mc = hit / n
    assert abs(mc - p_touch(100, 110, vol, days / 365.25)) < 0.04, (mc, p_touch(100, 110, vol, days / 365.25))
    s = Series({"3600": 1, "7200": 2})
    assert s.at(7300) == 2 and s.at(3700) == 1 and s.at(100) is None and s.at(7200 + 4 * 3600) is None
    print("optfair selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"fetch": fetch, "run": run, "selftest": selftest}.get(cmd, lambda: sys.exit(f"unknown command {cmd}"))()
