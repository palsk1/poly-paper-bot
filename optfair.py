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
import json
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
FOUND = 6                       # the first 6 files (3,000 markets) were used to look around; the rest are fresh
TRIES = 80                      # versions looked at in this dig
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


# ================================================================ real trades (5-minute buckets) and 1-minute spot
def fetch_spot1m(symbol, path):
    """1-minute Binance candles since T_START as {"t0": first minute, "c": closes, "h": highs, "l": lows} (None = no candle)."""
    d = bt.rjson(path, None) or {"t0": T_START - T_START % 60, "c": [], "h": [], "l": []}
    t = (d["t0"] + 60 * len(d["c"])) * 1000
    n = 0
    while True:
        rows = bot.http_json(BINANCE, {"symbol": symbol, "interval": "1m", "startTime": t, "limit": 1000})
        if not rows:
            break
        for r in rows:
            i = int(r[0] // 1000 - d["t0"]) // 60
            while len(d["c"]) < i:
                for k in "chl":
                    d[k].append(None)
            if len(d["c"]) == i:
                d["c"].append(float(r[4])); d["h"].append(float(r[2])); d["l"].append(float(r[3]))
        n += 1
        if n % 100 == 0:
            print(f"  {symbol} 1m: {len(d['c'])} minutes", flush=True)
        if len(rows) < 1000:
            break
        t = rows[-1][0] + 60000
    bt.wjson(path, d)
    return d


def order_key(mid):
    """A fixed shuffle of the markets that has nothing to do with their result: any first N are a fair sample."""
    import hashlib
    return hashlib.md5(("opt" + str(mid)).encode()).hexdigest()


MAX_PAGES = int(os.environ.get("OPT_PAGES", "1200"))


def fetch_tape(job):
    """Every trade of one market, squeezed to 5-minute buckets in YES terms: [bucket, first, last, low, high, dollars, trades]."""
    import informed
    m, cid = job
    try:
        rows, cut = informed.tape(cid, MAX_PAGES)
    except Exception as ex:
        return m["id"], None
    tt = []
    for r in rows:
        t = bot.fnum(bot.pick(r, "timestamp", "time"))
        t = t / 1000 if t > 1e11 else t
        px, sh = bot.fnum(r.get("price")), bot.fnum(r.get("size"))
        oi = r.get("outcome_index", r.get("outcomeIndex"))
        if oi not in (0, 1):
            tok = str(bot.pick(r, "token_id", "asset", default=""))
            oi = 0 if tok == m["toks"][0] else 1 if tok == m["toks"][1] else None
        if not t or oi is None or not 0 < px < 1 or sh <= 0:
            continue
        tt.append((int(t), px if oi == 0 else 1 - px, px * sh))
    tt.sort()
    B = []
    for t, p, usd_ in tt:
        b = t // 300 * 300
        p = round(p, 4)
        if B and B[-1][0] == b:
            x = B[-1]
            x[2] = p; x[3] = min(x[3], p); x[4] = max(x[4], p); x[5] += usd_; x[6] += 1
        else:
            B.append([b, p, p, p, p, usd_, 1])
    for x in B:
        x[5] = round(x[5], 1)
    return m["id"], {"cut": bool(cut), "n": len(tt), "b": B}


SHARD = 500


def tapes(limit=None):
    """Download trade lists for the markets in the fixed shuffled order, in files of SHARD markets (resumable)."""
    import ideas, informed
    os.makedirs(CACHE, exist_ok=True)
    for coin, (sym, _) in COINS.items():
        d = fetch_spot1m(sym, os.path.join(CACHE, f"spot1m_{coin}.json.gz"))
        print(f"{coin}: {len(d['c'])} spot minutes", flush=True)
    markets, _, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m["final"]}
    order = sorted(ms, key=order_key)
    if limit:
        order = order[:limit]
    nsh = (len(order) + SHARD - 1) // SHARD
    tot = cutn = 0
    for si in range(nsh):
        path = os.path.join(CACHE, f"tapes_{si:02d}.json.gz")
        ids = order[si * SHARD:(si + 1) * SHARD]
        have = bt.rjson(path, {}) or {}
        todo = [i for i in ids if i not in have]
        if todo:
            cids = informed.cids_for(todo)
            jobs = [(ms[i], cids[i]) for i in todo if cids.get(i)]
            with cf.ThreadPoolExecutor(WORKERS) as ex:
                for mid, r in ex.map(fetch_tape, jobs):
                    if r is not None:
                        have[mid] = r
            bt.wjson(path, have)
        tot += len(have)
        cutn += sum(1 for r in have.values() if r["cut"])
        print(f"  shard {si + 1}/{nsh}: {len(have)}/{len(ids)} markets, {sum(r['n'] for r in have.values())} trades, "
              f"{sum(1 for r in have.values() if r['cut'])} cut short ({(time.time() - T0) / 60:.0f} min)", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break
    print(f"tapes saved: {tot} markets, {cutn} cut short at {MAX_PAGES} pages")


# ================================================================ the test on real trades
def load_tapes(first=None, last=None):
    """Trade lists by shard: {market id: {"cut", "n", "b": [[bucket, first, last, low, high, dollars, trades], ...]}}."""
    out, i = {}, first or 0
    while last is None or i < last:
        p = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if not os.path.exists(p):
            break
        out.update(bt.rjson(p, {}) or {})
        i += 1
    return out


def load_spot1m():
    return {c: bt.rjson(os.path.join(CACHE, f"spot1m_{c}.json.gz"), None) for c in COINS}


def tbets(ms, tp, dvol, s1m, gap=0.05, lo=0.05, hi=0.95, min_left=6 * 3600, max_left=45 * 86400, min_age=3600,
          vol_mult=1.0, kinds=None, sides=(0, 1), extra=0.01, stake=10.0, wait=1800, max_gap=1.0, first_only=True, fairs=None):
    """Bets at prices people really paid. Every 5 minutes with a real trade: Polymarket's price = the last trade of those
    5 minutes, the coin's price = Binance's last finished minute, the swing size = Deribit's DVOL. If the two disagree by
    `gap` or more, buy the cheap side at the FIRST real trade of a later 5 minutes (within `wait` s), + `extra` + fee.
    One bet per market (the first)."""
    out = []
    for mid, r in tp.items():
        m = ms.get(mid)
        if not m or r.get("cut") or (kinds and m["kind"] not in kinds):
            continue
        sp, dv, B = s1m[m["coin"]], dvol[m["coin"]], r["b"]
        t0, C, H, Lw = sp["t0"], sp["c"], sp["h"], sp["l"]
        touch = m["kind"] in ("up", "down")
        mi = max(0, (m["start"] - t0) // 60)                 # minute pointer for the "already touched" check
        dead = False
        for i, x in enumerate(B[:-1]):
            T_ = x[0] + 300
            left = m["end"] - T_
            if left < min_left:
                break
            j = (T_ - t0) // 60 - 1                          # the minute that finished at T_
            if j < 0 or j >= len(C) or C[j] is None:
                continue
            if touch:
                while mi <= j:
                    if H[mi] is not None and (H[mi] >= m["k"] if m["kind"] == "up" else Lw[mi] <= m["k"]):
                        dead = True
                        break
                    mi += 1
                if dead:
                    break
            p = x[2]
            if left > max_left or T_ - m["start"] < min_age or not lo <= p <= hi:
                continue
            v = dv.at(T_ - 3600, 6 * 3600)
            if v is None:
                continue
            q = fair(m, C[j], v / 100 * vol_mult, left / YEAR)
            if fairs is not None:
                fairs.append((m["kind"], q, p, m["final"][0], mid))
            side = 0 if q - p >= gap else 1 if p - q >= gap else None
            if side is None or side not in sides or abs(q - p) > max_gap:
                continue
            y = B[i + 1]
            if y[0] - T_ > wait or y[0] >= m["end"]:
                continue
            px = y[1] if side == 0 else 1 - y[1]
            c = min(0.99, px + extra)
            if c <= 0.01:
                continue
            sh = stake / c
            fee = bot.taker_fee(sh, c, m["fee"])
            win = (m["final"][0] == 1.0) == (side == 0)
            out.append({"ev": m["ev"], "t": y[0], "cost": stake + fee, "pay": sh if win else 0.0, "sh": sh, "id": mid,
                        "kind": m["kind"], "coin": m["coin"], "side": side, "left": left, "p": p if side == 0 else 1 - p,
                        "fair": q if side == 0 else 1 - q, "px": px, "age": T_ - m["start"], "usd": y[5], "title": m["q"], "q": p if side == 0 else 1 - p})
            if first_only:
                break
    return out


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
            kinds=None, step=1, first_only=True, min_age=6 * 3600):
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
            if t - m["start"] < min_age:           # new markets open with a made-up 50c price (launch.py): skip the first hours
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
                        "kind": m["kind"], "coin": m["coin"], "left": left, "fee": m["fee"], "age": t - m["start"],
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
                     "kind": s["kind"], "coin": s["coin"], "side": s["side"], "left": s["left"], "p": s["p"], "fair": s["fair"], "age": s.get("age"), "id": s["id"]})
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
            if left > 3 * 86400 or left < 6 * 3600 or t - m["start"] < 6 * 3600:
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
    P("## 2. The trap: hourly chart prices\n")
    P("New Polymarket markets open with a made-up price near 50c and the chart keeps showing it until real trades come in. "
      "Buying \"where the two disagree\" at chart prices looks like a money machine, and is not real:\n")
    P(HEAD)
    for fam, kinds in (("touch (reach / dip)", ("up", "down")), ("end price (above / below / between)", ("above", "below", "between"))):
        for age, nm in ((0, "any hour of the chart"), (6 * 3600, "skipping the first 6 hours")):
            P(line(f"{fam}, gap 5c+, {nm}", to_bets(signals(have, charts, dvol, spot, gap=0.05, kinds=kinds, min_age=age))))
    P("")
    s1m = load_spot1m()
    found, fresh = load_tapes(0, FOUND), load_tapes(FOUND, None)
    P("## 3. The real test: prices people really paid\n")
    P(f"Every real trade of the markets, in 5-minute steps, in a fixed shuffled order that has nothing to do with the results. "
      f"The first {len(found)} markets were used to look around; the other {len(fresh)} were only opened once, for the rules marked "
      f"\"fixed before\". Rule: every 5 minutes with a real trade, Polymarket's price = the last trade, the coin = Binance's last "
      f"finished minute, swing size = Deribit's DVOL. If they disagree by the gap, buy the cheap side at the first real trade of a "
      f"later 5 minutes (within 30 min), + 1c + the fee. One bet per market, $10 each.\n")
    fams = (("end price", ("above", "below", "between")), ("touch", ("up", "down")))
    P("### Who is closer, on real trades (one random look per market)\n")
    P("| kind | markets | options miss | Polymarket miss | half-half miss | when 5c+ apart: markets | options miss | Polymarket miss |")
    P("|---|---|---|---|---|---|---|---|")
    F = []
    tbets(ms, dict(found, **fresh), dvol, s1m, gap=9, fairs=F, first_only=False)
    by = collections.defaultdict(list)
    for k, q, p, y, mid in F:
        by[mid].append((k, q, p, y))
    import random
    rng = random.Random(7)
    for fam, kinds in fams:
        rows = [rng.choice(v) for _, v in sorted(by.items()) if v[0][0] in kinds]
        d = [r for r in rows if abs(r[1] - r[2]) >= 0.05]
        br = lambda rr, f: sum((f(r) - r[3]) ** 2 for r in rr) / max(1, len(rr))
        P(f"| {fam} | {len(rows)} | {br(rows, lambda r: r[1]):.4f} | {br(rows, lambda r: r[2]):.4f} | {br(rows, lambda r: (r[1] + r[2]) / 2):.4f} "
          f"| {len(d)} | {br(d, lambda r: r[1]):.4f} | {br(d, lambda r: r[2]):.4f} |")
    P("\n(\"Miss\" = average squared distance between the forecast and what happened; smaller is better.)\n")
    cards = []
    for title, tp in (("Markets used to look around", found), ("Fresh markets (rules fixed before)", fresh)):
        if not tp:
            continue
        P(f"### {title}: {len(tp)}\n")
        P(HEAD)
        for fam, kinds in fams:
            for gap in (0.03, 0.05, 0.10):
                b = tbets(ms, tp, dvol, s1m, gap=gap, kinds=kinds)
                P(line(f"{fam}, 6h+ left, gap {gap * 100:.0f}c+", b))
                if gap == 0.05:
                    for side, nm in ((0, "buy Yes"), (1, "buy No")):
                        P(line(f"&nbsp;&nbsp;{nm}", [x for x in b if x["side"] == side]))
                    P(line("&nbsp;&nbsp;price did not run away (2c or less)", [x for x in b if x["px"] - x["p"] <= 0.02]))
            b = tbets(ms, tp, dvol, s1m, gap=0.05, kinds=kinds, min_left=1800, max_left=6 * 3600)
            P(line(f"{fam}, last 30 min to 6 hours, gap 5c+", b))
            for vm in (0.8, 1.2):
                P(line(f"{fam}, 6h+ left, gap 5c+, swing size x{vm}", tbets(ms, tp, dvol, s1m, gap=0.05, kinds=kinds, vol_mult=vm)))
        P("")
    if score:
        both = dict(found, **fresh)
        tests = [("Options price vs Polymarket: BTC/ETH end-price markets, 5c+ apart, real trades", both, dict(kinds=fams[0][1]), False, "dropped"),
                 ("Options price vs Polymarket: BTC/ETH reach/dip markets, 5c+ apart, real trades", both, dict(kinds=fams[1][1]), False, "dropped"),
                 ("Options price vs Polymarket: reach/dip, last 30 min to 6 hours (fresh markets only)", fresh,
                  dict(kinds=fams[1][1], min_left=1800, max_left=6 * 3600), True, "dropped")]
        P("## 4. The exam\n")
        for name, tp, kw, prereg, status in tests:
            b = tbets(ms, tp, dvol, s1m, gap=0.05, **kw)
            if not b:
                continue
            card = exam.score(b, name, tries=TRIES if not prereg else 3, prereg=prereg, src="optfair.py", status=status, quiet=True)
            cards.append(card)
            print("LEDGER ROW " + json.dumps(card))
            P(f"- **{name}**: {card['bets']} bets, {usd(card.get('per100'))} per $100, verdict **{card.get('verdict')}**.")
        P("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return cards


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
    if cmd.startswith("tapes"):
        tapes(int(cmd[5:].strip("_") or 0) or None)
    else:
        {"fetch": fetch, "run": run, "selftest": selftest}.get(cmd, lambda: sys.exit(f"unknown command {cmd}"))()
