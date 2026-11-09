#!/usr/bin/env python3
"""Kalshi 15-minute crypto markets: backtest of the "late favorite maker" (2026-11-09, from a Reddit post).

PAPER ONLY. Reads public history and never trades.

The idea (inferred from a Reddit post, "$50 to $3,000"): in Kalshi's 15-minute "BTC/ETH/SOL... up or down" markets,
a few minutes before the close, rest a buy order (maker, no fee on these series) at 90-99c on whichever side is
winning, and hold to the result. Wins 1-10c a contract most of the time, loses the whole price when the coin flips
in the last minutes.

    python3 kcrypto.py scan        # print API shapes (series, fees, a market, trades, history endpoints)
    python3 kcrypto.py fetch [D]   # download the last D days (default 60) of settled windows + 1-minute candles
                                   # + Binance 1-minute spot into bt_cache/kc/ (re-runs only fetch what's new)
    python3 kcrypto.py run         # write backtest/kcrypto.md (+ kcrypto.json)
    python3 kcrypto.py selftest    # offline check on made-up candles
  From GitHub: probe workflow with what = btkc (fetch + run), btkcfetch, btkcrun; cache and report are kept.
  (probe `kc_scan` prints the API shapes.)

Reusable pieces: load_windows() returns every cached window with its minute candles, so other 15-minute ideas can be
tested on the same data without downloading again.

How fills are modelled (the crux: a resting bid only fills when someone sells into it)
- History has 1-minute candles per market: best bid/ask at each minute's end, plus the low/high of real TRADES.
- We place our bid at the end of the minute that has M minutes left, and only look at later minutes.
- strict: filled only if a later trade printed BELOW our price. Price-time priority means every bid at our price
  (ours included) was used up first. Certain, but it ignores fills that happen exactly at our price.
- fair (the main case): if our price was above the best bid (we were first in line at a new price), a trade AT our
  price fills us; if we joined an existing level or sat below it, strict.
- touch (optimistic bound): any trade at or below our price fills us.
- Adverse selection shows up directly: compare the win rate of FILLED orders with the win rate of all signals.
- Settlement is Kalshi's own result field. Maker fee is 0 (series fee_type "quadratic", checked 2026-11-09); the
  taker comparison pays 0.07 x p x (1-p) a contract.
- Size: the candles can't tell how many contracts would have filled. Kalshi trades 100k-1M+ contracts a window on
  BTC, so 10-100 contracts is fine; thousands (the Reddit size) would not all fill.
"""
import datetime as dt
import json
import math
import os
import random
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import bot

K = bot.KALSHI
UTC = dt.timezone.utc
CACHE = os.path.join(bot.ROOT, "bt_cache", "kc")
OUT = os.path.join(bot.ROOT, "backtest")
SERIES = {"KXBTC15M": "BTCUSDT", "KXETH15M": "ETHUSDT", "KXSOL15M": "SOLUSDT", "KXXRP15M": "XRPUSDT",
          "KXDOGE15M": "DOGEUSDT", "KXHYPE15M": "HYPEUSDT", "KXBNB15M": "BNBUSDT"}
BINANCE = "https://data-api.binance.vision/api/v3/klines"
LOOKBACK_MIN = 11          # candles kept per window: the last 11 minutes
WORKERS = int(os.environ.get("KC_WORKERS", "8"))
LEVELS = (0.90, 0.93, 0.95, 0.97, 0.98, 0.99)
MINUTES = (1, 2, 3, 5, 7, 10)
JOIN_MIN = (0.90, 0.95, 0.97, 0.99)
TAKER_RATE = 0.07
EPS = 1e-9


def get(path, params=None):
    return bot.http_json(f"{K}{path}", params)


def wjson(path, obj):
    import gzip
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as fh:
        json.dump(obj, fh, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def rjson(path, default=None):
    import gzip
    if not os.path.exists(path):
        return default
    with gzip.open(path, "rt") as fh:
        return json.load(fh)


def tsec(s):
    d = bot.parse_iso(s)
    return int(d.timestamp()) if d else None


# ================================================================ scan (API shapes)

def show(label, fn):
    print(f"\n===== {label}")
    try:
        r = fn()
        s = json.dumps(r, indent=1)
        print(s[:3500] + (" ...(cut)" if len(s) > 3500 else ""))
        return r
    except Exception as e:
        print("FAILED:", e)
        return None


def scan():
    for s in SERIES:
        show(f"series {s}", lambda: {k: v for k, v in (get(f"/series/{s}").get("series") or {}).items()
                                     if k in ("ticker", "fee_type", "fee_multiplier", "frequency", "last_updated_ts")})
    show("fee changes", lambda: get("/series/fee_changes", {"series_ticker": "KXBTC15M"}))
    show("historical cutoff", lambda: get("/historical/cutoff"))
    done = show("settled BTC 15m", lambda: get("/markets", {"series_ticker": "KXBTC15M", "status": "settled", "limit": 1}))
    t = ((done or {}).get("markets") or [{}])[0].get("ticker")
    if t:
        show(f"trades {t}", lambda: get("/markets/trades", {"ticker": t, "limit": 5}))
        now_t = int(time.time())
        show("batch candles", lambda: get("/markets/candlesticks", {"market_tickers": t, "start_ts": now_t - 3600,
                                                                     "end_ts": now_t, "period_interval": 1}))


# ================================================================ fetch

def slim_market(m, series):
    return {"t": m.get("ticker"), "s": series, "close": tsec(m.get("close_time")), "open": tsec(m.get("open_time")),
            "strike": bot.fnum(m.get("floor_strike"), None), "res": str(m.get("result") or "").lower(),
            "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0)}


_CUTOFF = [None]


def hist_cutoff():
    """Markets that settled before this moved to /historical endpoints."""
    if _CUTOFF[0] is None:
        try:
            _CUTOFF[0] = tsec(get("/historical/cutoff").get("market_settled_ts")) or 0
        except Exception as e:
            print(f"historical cutoff failed: {e}")
            _CUTOFF[0] = 0
    return _CUTOFF[0]


def list_markets(series, t0, t1):
    """Settled windows closing in [t0, t1]: the live endpoint, then /historical for anything older than its cutoff."""
    out, seen = [], set()
    cut = hist_cutoff()
    for path in ("/markets", "/historical/markets"):
        if path == "/historical/markets" and (not cut or t0 >= cut):
            continue
        cur, pages, t_s = None, 0, time.time()
        for _ in range(200):
            p = {"series_ticker": series, "min_close_ts": t0, "max_close_ts": t1, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                res = get(path, p)
            except Exception as e:
                print(f"  {series} {path} failed: {e}")
                break
            pages += 1
            rows = res.get("markets") or []
            for m in rows:
                sm = slim_market(m, series)
                if sm["t"] and sm["t"] not in seen and sm["res"] in ("yes", "no") and sm["close"] and t0 <= sm["close"] <= t1:
                    seen.add(sm["t"])
                    out.append(sm)
            cur = res.get("cursor")
            oldest = min((tsec(m.get("close_time")) or 0 for m in rows), default=0)
            if not cur or not rows or oldest < t0:   # in case the endpoint ignores the time filter
                break
        print(f"  {series} {path}: {pages} pages, {len(out)} windows so far ({time.time() - t_s:.0f}s)")
    return sorted(out, key=lambda m: m["close"])


def candle_row(c):
    """[end_ts, yes_bid, yes_ask, trade_low, trade_high, volume] from one Kalshi candle (prices in dollars)."""
    def px(block, key):
        v = (c.get(block) or {}).get(f"{key}_dollars")
        if v in (None, ""):
            v = (c.get(block) or {}).get(key)
            return None if v in (None, "") else bot.fnum(v, 0) / 100
        return bot.fnum(v, None)
    return [int(c.get("end_period_ts") or 0), px("yes_bid", "close"), px("yes_ask", "close"),
            px("price", "low"), px("price", "high"), bot.fnum(c.get("volume_fp") or c.get("volume"), 0)]


_BATCH_OK = [None]   # None = untested, True/False after the first try


def candles_batch(ms):
    """Candles for many windows in one call (GET /markets/candlesticks, up to 100 tickers and 10,000 candles);
    None if that endpoint doesn't answer as expected. Each window keeps only its own last LOOKBACK_MIN minutes."""
    t0 = min(m["close"] for m in ms) - LOOKBACK_MIN * 60
    t1 = max(m["close"] for m in ms)
    res = get("/markets/candlesticks", {"market_tickers": ",".join(m["t"] for m in ms), "start_ts": t0, "end_ts": t1,
                                        "period_interval": 1})
    rows = None
    if isinstance(res, dict):
        rows = next((res[k] for k in ("markets", "market_candlesticks", "candlesticks", "data")
                     if isinstance(res.get(k), list)), None)
    if not isinstance(rows, list):
        if _BATCH_OK[0] is None:
            print("  batch candles: unexpected answer:", json.dumps(res)[:600])
        return None
    close = {m["t"]: m["close"] for m in ms}
    out = {}
    for r in rows:
        tk = r.get("market_ticker") or r.get("ticker")
        if tk in close:
            lo = close[tk] - LOOKBACK_MIN * 60
            out[tk] = [row for row in (candle_row(c) for c in r.get("candlesticks") or []) if lo < row[0] <= close[tk]]
    return out


def candles_one(m):
    p = {"start_ts": m["close"] - LOOKBACK_MIN * 60, "end_ts": m["close"], "period_interval": 1}
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            res = get(path, p)
        except Exception:
            continue
        cs = res.get("candlesticks") if isinstance(res, dict) else None
        if cs:
            return [candle_row(c) for c in cs]
    return []


def batch_groups(todo, max_tickers=70, max_candles=9000):
    """Windows grouped for one batch call: neighbours in time (all coins close together), under the API caps."""
    todo = sorted(todo, key=lambda m: m["close"])
    groups, cur = [], []
    for m in todo:
        cand = cur + [m]
        span = (cand[-1]["close"] - cand[0]["close"]) // 60 + LOOKBACK_MIN + 1
        if cur and (len(cand) > max_tickers or span * len(cand) > max_candles):
            groups.append(cur)
            cand = [m]
        cur = cand
    if cur:
        groups.append(cur)
    return groups


def fetch_candles(ms, store):
    todo = [m for m in ms if m["t"] not in store]
    print(f"  candles: {len(ms)} windows, {len(todo)} to download")
    if not todo:
        return
    t_start = time.time()
    groups = batch_groups(todo)
    try:
        first = candles_batch(groups[0])
        _BATCH_OK[0] = bool(first) and any(first.values())
        if not _BATCH_OK[0]:
            print("  batch candles gave nothing; one call per window instead", str(first)[:300])
    except Exception as e:
        print(f"  batch candles endpoint failed ({e}); one call per window instead")
        _BATCH_OK[0] = False
    if _BATCH_OK[0]:
        store.update(first)

        def one(g):
            try:
                return candles_batch(g) or {}
            except Exception as e:
                print(f"   batch failed: {e}")
                return {}
        with ThreadPoolExecutor(WORKERS) as ex:
            for i, got in enumerate(ex.map(one, groups[1:])):
                store.update(got)
                if i % 100 == 0:
                    print(f"   batch {i}/{len(groups)} ({time.time() - t_start:.0f}s)")
    todo = [m for m in todo if m["t"] not in store]
    if todo:
        print(f"  {len(todo)} windows one by one")
        with ThreadPoolExecutor(WORKERS) as ex:
            for i, (m, cs) in enumerate(zip(todo, ex.map(candles_one, todo))):
                store[m["t"]] = cs
                if i % 500 == 0:
                    print(f"   single {i}/{len(todo)} ({time.time() - t_start:.0f}s)")


def fetch_spot(symbol, t0, t1, have):
    """Binance 1-minute closes {minute_end_ts: close}. Kalshi settles on CF Benchmarks' index, not Binance: this
    is only used to measure how far the coin was from the strike. Fills whatever is missing before and after the
    cached stretch."""
    out = dict(have or {})
    keys = sorted(int(k) for k in out)
    gaps = [(t0 - 3600, t1)] if not keys else [(t0 - 3600, keys[0]), (keys[-1], t1)]
    for g0, g1 in gaps:
        start = g0 * 1000
        while start < g1 * 1000:
            try:
                rows = bot.http_json(BINANCE, {"symbol": symbol, "interval": "1m", "startTime": start, "limit": 1000})
            except Exception as e:
                print(f"  binance {symbol} failed: {e}")
                break
            if not rows:
                break
            for r in rows:
                out[str(int(r[6]) // 1000 + 1)] = float(r[4])   # close time is end-1ms
            start = int(rows[-1][0]) + 60000
            if len(rows) < 1000:
                break
    return out


def fetch(days=60):
    days = int(days)
    t1 = int(time.time()) - 120
    t0 = t1 - days * 86400
    os.makedirs(CACHE, exist_ok=True)
    all_ms = {}
    for series, sym in SERIES.items():
        t_s = time.time()
        mpath = os.path.join(CACHE, f"markets_{series}.json.gz")
        spath = os.path.join(CACHE, f"spot_{series}.json.gz")
        old = {m["t"]: m for m in rjson(mpath, []) if t0 <= m["close"] <= t1}
        have_t = min((m["close"] for m in old.values()), default=None)
        newest = max((m["close"] for m in old.values()), default=None)
        fresh = []
        if have_t is None or have_t > t0 + 900:
            fresh += list_markets(series, t0, have_t or t1)
        if newest:
            fresh += list_markets(series, newest, t1)
        for m in fresh:
            old[m["t"]] = m
        ms = sorted(old.values(), key=lambda m: m["close"])
        wjson(mpath, ms)
        all_ms[series] = ms
        spot = fetch_spot(sym, t0, t1, rjson(spath, {}))
        wjson(spath, spot)
        print(f"{series}: {len(ms)} windows, {len(spot)} spot minutes ({time.time() - t_s:.0f}s)")
    stores = {s: rjson(os.path.join(CACHE, f"candles_{s}.json.gz"), {}) for s in SERIES}
    merged = {}
    for s in SERIES:
        merged.update(stores[s])
    fetch_candles([m for ms in all_ms.values() for m in ms], merged)
    for s, ms in all_ms.items():
        keep = {m["t"]: merged[m["t"]] for m in ms if m["t"] in merged}
        wjson(os.path.join(CACHE, f"candles_{s}.json.gz"), keep)
        print(f"{s}: {sum(1 for v in keep.values() if v)} of {len(ms)} windows with candles")


# ================================================================ replay

def load_windows(series=None):
    """Every cached window: {t, s, close, strike, res, vol, c: {end_ts: [bid, ask, lo, hi, vol]}, spot: {ts: px}}."""
    out = []
    for s in (series or SERIES):
        ms = rjson(os.path.join(CACHE, f"markets_{s}.json.gz"), [])
        cs = rjson(os.path.join(CACHE, f"candles_{s}.json.gz"), {})
        spot = rjson(os.path.join(CACHE, f"spot_{s}.json.gz"), {})
        for m in ms:
            rows = cs.get(m["t"]) or []
            if not rows:
                continue
            out.append({**m, "c": {r[0]: r[1:] for r in rows if r and r[0]}, "spot": spot})
    return sorted(out, key=lambda w: w["close"])


def side_view(row, side):
    """(bid, ask, trade_low, trade_high) of one side from a YES candle row [bid, ask, lo, hi, vol]."""
    yb, ya, lo, hi = row[0], row[1], row[2], row[3]
    if side == "yes":
        return yb, ya, lo, hi
    return (None if ya is None else 1 - ya, None if yb is None else 1 - yb,
            None if hi is None else 1 - hi, None if lo is None else 1 - lo)


def leader(row):
    yb, ya = row[0], row[1]
    if yb is None or ya is None or not (0 < yb <= ya < 1):
        return None
    return "yes" if (yb + ya) / 2 >= 0.5 else "no"


def zscore(w, t, minutes, side):
    """How many 'typical moves until the close' the coin sat on the right side of the strike, from Binance.
    Positive = spot agrees with the leading side. None if no spot data."""
    sp, k = w["spot"], w.get("strike")
    if not sp or not k:
        return None
    px = sp.get(str(t))
    if px is None:
        return None
    rets = []
    for i in range(60):
        a, b = sp.get(str(t - 60 * (i + 1))), sp.get(str(t - 60 * i))
        if a and b:
            rets.append(math.log(b / a))
    if len(rets) < 30:
        return None
    sd = math.sqrt(sum(r * r for r in rets) / len(rets)) * px * math.sqrt(max(minutes, 0.5))
    if sd <= 0:
        return None
    z = (px - k) / sd
    return z if side == "yes" else -z


def fill_after(w, t_place, side, price, front):
    """(strict, fair, touch) fills for a bid at `price` placed at t_place, looking at later minutes only."""
    strict = touch = False
    for t in sorted(w["c"]):
        if t <= t_place or t > w["close"]:
            continue
        _, _, lo, _ = side_view(w["c"][t], side)
        if lo is None:
            continue
        if lo < price - EPS:
            strict = touch = True
            break
        if lo <= price + EPS:
            touch = True
    return strict, (touch if front else strict), touch


def signals(windows, minutes):
    """One row per window with a book at M minutes left: the leading side and its bid/ask then."""
    out = []
    for w in windows:
        t = w["close"] - 60 * minutes
        row = w["c"].get(t)
        if not row:
            continue
        side = leader(row)
        if not side:
            continue
        bid, ask, _, _ = side_view(row, side)
        out.append({"w": w, "t": t, "side": side, "bid": bid, "ask": ask, "won": w["res"] == side,
                    "day": t // 86400, "m": minutes})
    return out


def variant_trades(sigs, kind, level, zmin=None):
    """kind: 'level' (bid at a fixed price while the leader's mid is at or above it), 'join' (bid = best bid, leader
    bid >= level), 'improve' (one tick above the best bid), 'taker' (buy at the ask, pay the taker fee)."""
    rows = []
    for s in sigs:
        bid, ask = s["bid"], s["ask"]
        if kind == "level":
            if (bid + ask) / 2 < level - EPS or ask <= level + EPS:
                continue
            price, front = level, level > bid + EPS
        elif kind == "join":
            if bid < level - EPS:
                continue
            price, front = bid, False
        elif kind == "improve":
            if bid < level - EPS:
                continue
            tick = 0.001 if bid >= 0.9 - EPS else 0.01
            price = round(bid + tick, 4)
            if price >= ask - EPS:
                price, front = bid, False   # no room inside the spread: join instead
            else:
                front = True
        else:  # taker
            if ask < level - EPS or ask >= 1 - EPS:
                continue
            price = ask
        if zmin is not None:
            z = zscore(s["w"], s["t"], s["m"], s["side"])
            if z is None or z < zmin:
                continue
        if kind == "taker":
            f = (True, True, True)
            fee = TAKER_RATE * price * (1 - price)
        else:
            f = fill_after(s["w"], s["t"], s["side"], price, front)
            fee = 0.0
        rows.append({"t": s["t"], "day": s["day"], "s": s["w"]["s"], "price": price, "fee": fee, "won": s["won"],
                     "fills": f, "tk": s["w"]["t"]})
    return rows


def stats(rows, model):
    """model 0/1/2 = strict/fair/touch. Per-contract numbers; P&L per $100 staked."""
    f = [r for r in rows if r["fills"][model]]
    n_sig, n = len(rows), len(f)
    if not n:
        return {"signals": n_sig, "fills": 0}
    pnl = [(1.0 if r["won"] else 0.0) - r["price"] - r["fee"] for r in f]
    cost = sum(r["price"] + r["fee"] for r in f)
    wins = [p for p in pnl if p > 0]
    losses = [p for p in pnl if p <= 0]
    # staking $10 on every fill, in time order: biggest peak-to-trough fall
    eq = peak = dd = 0.0
    for r, p in sorted(zip(f, pnl), key=lambda x: x[0]["t"]):
        eq += p / (r["price"] + r["fee"]) * 10
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    by_day = defaultdict(lambda: [0.0, 0.0])
    for r, p in zip(f, pnl):
        by_day[r["day"]][0] += p
        by_day[r["day"]][1] += r["price"] + r["fee"]
    days = list(by_day.values())
    rng = random.Random(7)
    boots = []
    for _ in range(400):
        smp = [days[rng.randrange(len(days))] for _ in days]
        c = sum(x[1] for x in smp)
        boots.append(sum(x[0] for x in smp) / c * 100 if c else 0)
    boots.sort()
    mid = sorted(r["t"] for r in f)[n // 2]
    half = []
    for part in ([x for x in zip(f, pnl) if x[0]["t"] < mid], [x for x in zip(f, pnl) if x[0]["t"] >= mid]):
        c = sum(r["price"] + r["fee"] for r, _ in part)
        half.append(sum(p for _, p in part) / c * 100 if c else 0)
    won_all = sum(1 for r in rows if r["won"])
    avg_win = sum(wins) / len(wins) if wins else 0
    return {"signals": n_sig, "fills": n, "fill_rate": n / n_sig, "won": len(wins), "lost": len(losses),
            "win_rate": len(wins) / n, "win_rate_all": won_all / n_sig, "avg_price": cost / n,
            "avg_win": avg_win, "worst": min(pnl), "per100": sum(pnl) / cost * 100, "pnl_per_contract": sum(pnl) / n,
            "band": (boots[20], boots[379]), "halves": half, "dd10": dd, "pnl10": sum(p / (r["price"] + r["fee"]) * 10 for r, p in zip(f, pnl)),
            "days": len(days),
            "wins_per_loss": (abs(sum(losses) / len(losses)) / avg_win) if losses and avg_win else None}


def money(x):
    return f"{'-' if x < 0 else '+'}${abs(x):.2f}"


def line(label, s):
    if not s.get("fills"):
        return f"| {label} | {s.get('signals', 0)} | 0 | | | | | | | | |"
    wpl = f"{s['wins_per_loss']:.0f}" if s.get("wins_per_loss") else "-"
    lo, hi = s["band"]
    return (f"| {label} | {s['signals']} | {s['fills']} ({s['fill_rate'] * 100:.0f} in 100) | "
            f"{s['won']}/{s['lost']} | {s['win_rate_all'] * 100:.1f} vs {s['win_rate'] * 100:.1f} | "
            f"{s['avg_price'] * 100:.1f}c | {s['avg_win'] * 100:.2f}c | {wpl} | {money(s['per100'])} | "
            f"{money(lo)} to {money(hi)} | {money(s['halves'][0])} / {money(s['halves'][1])} |")


HEAD = ["| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract "
        "| One loss eats N wins | P&L per $100 | 90% band | Older / newer half |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]


def run():
    windows = load_windows()
    if not windows:
        print("no cached windows: run `kcrypto.py fetch` first")
        return
    t0, t1 = windows[0]["close"], windows[-1]["close"]
    by_m = {m: signals(windows, m) for m in MINUTES}
    res = {}
    L = ["# Kalshi 15-minute crypto: the 'late favorite maker' backtest", "",
         f"Generated {bot.iso()}. {len(windows)} settled windows ({', '.join(sorted({w['s'] for w in windows}))}), "
         f"closing {bot.iso(dt.datetime.fromtimestamp(t0, UTC))[:10]} to "
         f"{bot.iso(dt.datetime.fromtimestamp(t1, UTC))[:10]}. Paper only. Code: `kcrypto.py`.", "",
         "The idea: with M minutes left, rest a buy order on the side that's winning and hold it to the close. Makers "
         "pay no fee on these series. A resting order only fills when someone sells into it, so fills are modelled "
         "from later trades (see the top of kcrypto.py). 'Won out of 100' compares all signals with the ones that "
         "actually filled: if filled orders win less often, the fills are picked off (adverse selection).", "",
         "Main fill model: **fair**. P&L per $100 staked. The 90% band resamples whole days.", ""]
    L += ["## 1. Fixed price, by minutes left (fair fills)", "",
          "Bid at the fixed price while the leader's mid-price is at or above it (and its ask is above it).", ""] + HEAD
    for lv in LEVELS:
        for m in MINUTES:
            s = stats(variant_trades(by_m[m], "level", lv), 1)
            res[f"level_{lv:.2f}_m{m}"] = s
            L.append(line(f"{lv * 100:.0f}c, {m} min left", s))
    L += ["", "## 2. Join the best bid / step one tick in front of it (fair fills)", "",
          "join = same price as the best bid, back of the line (strict fills only). improve = one tick (0.1c) above "
          "the best bid, front of the line.", ""] + HEAD
    for kind in ("join", "improve"):
        for lv in JOIN_MIN:
            for m in MINUTES:
                s = stats(variant_trades(by_m[m], kind, lv), 1)
                res[f"{kind}_{lv:.2f}_m{m}"] = s
                L.append(line(f"{kind}, leader bid {lv * 100:.0f}c+, {m} min left", s))
    L += ["", "## 3. Same orders, three fill models", "",
          "strict = only when a trade printed below our price; touch = any trade at our price (optimistic).", ""] + HEAD
    for kind, lv, m in (("improve", 0.95, 3), ("improve", 0.97, 2), ("level", 0.97, 3), ("level", 0.95, 5),
                        ("join", 0.95, 3), ("improve", 0.90, 5)):
        rows = variant_trades(by_m[m], kind, lv)
        for mi, mn in enumerate(("strict", "fair", "touch")):
            L.append(line(f"{kind} {lv * 100:.0f}c, {m} min, {mn}", stats(rows, mi)))
    L += ["", "## 4. Taker comparison: buy at the ask and pay the fee", ""] + HEAD
    for lv in (0.90, 0.95, 0.97):
        for m in (1, 3, 5):
            s = stats(variant_trades(by_m[m], "taker", lv), 1)
            res[f"taker_{lv:.2f}_m{m}"] = s
            L.append(line(f"taker, ask {lv * 100:.0f}c+, {m} min left", s))
    L += ["", "## 5. Spot safety filter (Binance): only when the coin is z typical moves past the strike", "",
          "Typical move = last hour's 1-minute moves scaled to the minutes left. Binance is a stand-in for CF "
          "Benchmarks' index, which settles the market.", ""] + HEAD
    for kind, lv, m in (("improve", 0.95, 3), ("level", 0.97, 3), ("improve", 0.90, 5)):
        for z in (None, 1.5, 2.0, 3.0):
            s = stats(variant_trades(by_m[m], kind, lv, z), 1)
            res[f"{kind}_{lv:.2f}_m{m}_z{z}"] = s
            L.append(line(f"{kind} {lv * 100:.0f}c, {m} min, z {z or 'any'}", s))
    L += ["", "## 6. By coin (improve, leader bid 95c+, 3 min left, fair)", ""] + HEAD
    rows = variant_trades(by_m[3], "improve", 0.95)
    for s in sorted({r["s"] for r in rows}):
        L.append(line(s, stats([r for r in rows if r["s"] == s], 1)))
    # the worst single minutes: how bad do the flips get?
    L += ["", "## 7. Worst stretch", ""]
    best = max(((k, v) for k, v in res.items() if v.get("fills", 0) >= 200 and not k.startswith("taker")),
               key=lambda kv: kv[1]["per100"], default=None)
    if best:
        k, v = best
        L.append(f"Best maker variant with 200+ fills: `{k}`: {money(v['per100'])} per $100 over {v['fills']} fills, "
                 f"band {money(v['band'][0])} to {money(v['band'][1])}. Staking $10 on every fill it would have made "
                 f"{money(v['pnl10'])} over {v['days']} days; the deepest fall from a high on the way was "
                 f"{money(-v['dd10'])}. With ~{len(res)} variants tried, the best one is "
                 "flattered by luck: judge it by its band and halves, not its headline.")
    os.makedirs(OUT, exist_ok=True)
    txt = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "kcrypto.md"), "w") as fh:
        fh.write(txt)
    with open(os.path.join(OUT, "kcrypto.json"), "w") as fh:
        json.dump({"generated": bot.iso(), "windows": len(windows), "results": res}, fh, indent=1, default=str)
    print(txt)


# ================================================================ selftest

def selftest():
    close = 10_000 * 900
    def win(rows, res, strike=100.0):
        return {"t": "X", "s": "KXBTC15M", "close": close, "strike": strike, "res": res, "spot": {},
                "c": {close - 60 * i: r for i, r in rows.items()}}
    # 3 min left: YES leads at 96/97. Later trades: 95.5 low -> a 96c bid fills strict; 97c leader mid
    w = win({3: [0.96, 0.97, 0.96, 0.97, 1], 2: [0.95, 0.96, 0.955, 0.96, 1], 1: [0.99, 1.0, 0.99, 0.999, 1]}, "yes")
    s = signals([w], 3)
    assert s and s[0]["side"] == "yes" and s[0]["bid"] == 0.96 and s[0]["won"]
    assert fill_after(w, close - 180, "yes", 0.96, False) == (True, True, True)
    assert fill_after(w, close - 180, "yes", 0.955, True) == (False, True, True)
    assert fill_after(w, close - 180, "yes", 0.95, False) == (False, False, False)
    # NO side: YES at 3/4 -> NO bid 96, ask 97; a YES trade high of 4.5 = NO traded at 95.5
    w2 = win({3: [0.03, 0.04, 0.03, 0.04, 1], 2: [0.04, 0.05, 0.04, 0.045, 1]}, "yes")
    s2 = signals([w2], 3)
    assert s2[0]["side"] == "no" and abs(s2[0]["bid"] - 0.96) < 1e-9 and not s2[0]["won"]
    assert fill_after(w2, close - 180, "no", 0.96, False)[0]
    r = variant_trades(s2, "improve", 0.95)
    assert r and abs(r[0]["price"] - 0.961) < 1e-9 and r[0]["fills"][1]
    st = stats(r, 1)
    assert st["lost"] == 1 and abs(st["worst"] + 0.961) < 1e-9
    t = variant_trades(s, "taker", 0.95)
    assert abs(t[0]["fee"] - 0.07 * 0.97 * 0.03) < 1e-9
    print("kcrypto selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd.startswith("fetch_"):
        cmd, arg = "fetch", cmd.split("_", 1)[1]
    {"scan": scan, "fetch": lambda: fetch(arg or 60), "run": run, "selftest": selftest,
     "all": lambda: (fetch(arg or 60), run())}[cmd]()
