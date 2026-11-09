#!/usr/bin/env python3
"""Kalshi 15-minute crypto: what a FAST bot could do that our 5-minute bot can't (2026-11-09, Jan's follow-up).

PAPER ONLY. Reads public history and never trades.

kcrypto.py showed that a slow resting bid on the leading side is about break-even: the fills come when the coin is
about to flip. Two things a fast bot (a server checking every second) could add, tested here on past data:

  A. "Pull the bid when the price turns": rest the same bid, but cancel it the moment Binance spot says the lead is
     in danger (z below a line), with 1-10 seconds of reaction time. Fills that land before the cancel still count.
  B. "Bid in the last seconds": the result is the 60-second average before the close, so with 20 seconds left two
     thirds of it is already fixed. Buy the side the running average favours (taker at the next real trade price,
     or a maker bid that only fills from real trades).

Data (cached in bt_cache/kf/, re-runs only fetch what's new):
  - Kalshi's trade tape for the last 330 seconds of every window kcrypto.py has cached (time to the microsecond,
    price, which side the taker bought, size).
  - Binance 1-second spot klines (data.binance.vision daily files).
Kalshi settles on CF Benchmarks' BRTI, not Binance. We correct for the gap with the Binance average in the minute
before the window opened vs Kalshi's strike, and report how often our Binance estimate agrees with Kalshi's result.
Every loss from a disagreement counts, as it would for a real bot using Binance.

    python3 kfast.py fetch [D]   # trades + 1s spot for the last D days of cached windows (default 30)
    python3 kfast.py run         # backtest/kfast.md
    python3 kfast.py incentives  # Kalshi's public incentive programs on the 15-minute crypto series
    python3 kfast.py selftest    # offline
  From GitHub: probe with what = btkf (fetch + run), btkffetch, btkfrun, kf_incentives. Needs kcrypto's cache
  (btkcfetch) for the window list and minute candles.
"""
import array
import datetime as dt
import io
import json
import math
import os
import sys
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

import bot
import kcrypto as kc

CACHE = os.path.join(bot.ROOT, "bt_cache", "kf")
OUT = os.path.join(bot.ROOT, "backtest")
TAPE_SEC = 330            # trade tape kept per window: the last 5.5 minutes
WORKERS = int(os.environ.get("KF_WORKERS", "16"))
BIN_ZIP = "https://data.binance.vision/data/spot/daily/klines/{s}/1s/{s}-1s-{d}.zip"
NAN = float("nan")
EPS = 1e-9


# ================================================================ fetch: trade tape

def parse_ts(s):
    """'2026-11-09T18:57:16.123456Z' -> epoch seconds as float."""
    if not s:
        return None
    s = s.rstrip("Z")
    frac = 0.0
    if "." in s:
        s, f = s.split(".", 1)
        frac = float("0." + "".join(ch for ch in f if ch.isdigit()) or "0")
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp() + frac
    except ValueError:
        return None


def tape_row(t):
    yp = bot.fnum(t.get("yes_price_dollars"), None)
    if yp is None:
        yp = bot.fnum(t.get("yes_price"), 0) / 100
    n = bot.fnum(t.get("count_fp"), None)
    if n is None:
        n = bot.fnum(t.get("count"), 0)
    ts = parse_ts(t.get("created_time"))
    if ts is None:
        return None
    return [round(ts, 3), round(yp, 4), 1 if str(t.get("taker_side")).lower() == "yes" else 0, round(n, 2)]


def compact(tape):
    """Squeeze a raw tape [[ts, yes_price, taker_yes, count], ...] to at most 5 rows a second that keep everything
    the replay asks: per second the highest and lowest YES price paid by YES takers, the lowest and highest by NO
    takers (worst prices first, so 'next buy' sees the dearest fill), then the second's last trade.
    Rows become [second, yes_price, taker_yes]. Already compact tapes pass through."""
    if not tape or len(tape[0]) == 3:
        return tape
    by = {}
    for ts, yp, tk, _ in tape:
        sec = int(ts)
        d = by.setdefault(sec, {"y": [], "n": [], "last": None})
        d["y" if tk else "n"].append(yp)
        d["last"] = (yp, tk)
    out = []
    for sec in sorted(by):
        d, rows = by[sec], []
        if d["y"]:
            rows += [(max(d["y"]), 1), (min(d["y"]), 1)]
        if d["n"]:
            rows += [(min(d["n"]), 0), (max(d["n"]), 0)]
        rows.append(d["last"])
        seen = []
        for r in rows:
            if r not in seen or r is rows[-1]:
                seen.append(r)
        out += [[sec, yp, tk] for yp, tk in seen]
    return out


def fetch_tape(m):
    """Trades in the last TAPE_SEC of one window, oldest first. None if the download failed."""
    t1, t0 = m["close"], m["close"] - TAPE_SEC
    paths = ["/markets/trades"]
    if kc.hist_cutoff() and m["close"] < kc.hist_cutoff():
        paths = ["/historical/trades", "/markets/trades"]
    for path in paths:
        rows, cur, ok = [], None, False
        for _ in range(30):
            p = {"ticker": m["t"], "min_ts": int(t0), "max_ts": int(t1) + 1, "limit": 1000}
            if cur:
                p["cursor"] = cur
            try:
                res = kc.get(path, p)
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                    continue
                break
            rows += res.get("trades") or []
            cur = res.get("cursor")
            if not cur or not res.get("trades"):
                ok = True
                break
        if ok:
            out = [r for r in (tape_row(t) for t in rows) if r and t0 - 1 <= r[0] <= t1 + 1]
            return compact(sorted(out))
    return None


def fetch_tapes(days):
    t_end = int(time.time())
    t0 = t_end - int(days) * 86400
    for s in kc.SERIES:
        path = os.path.join(CACHE, f"tape_{s}.json.gz")
        store = {k: compact(v) for k, v in kc.rjson(path, {}).items()}
        ms = [m for m in kc.rjson(os.path.join(kc.CACHE, f"markets_{s}.json.gz"), [])
              if m["close"] >= t0]
        todo = [m for m in ms if m["t"] not in store]
        t_s, done, failed = time.time(), 0, 0
        print(f"{s}: {len(ms)} windows in range, {len(todo)} to fetch")
        for i in range(0, len(todo), 400):
            chunk = todo[i:i + 400]
            with ThreadPoolExecutor(WORKERS) as ex:
                res = list(ex.map(fetch_tape, chunk))
            for m, r in zip(chunk, res):
                if r is None:
                    failed += 1
                else:
                    store[m["t"]] = r
                    done += 1
            kc.wjson(path, store)
            el = time.time() - t_s
            print(f"  {s}: {done + failed}/{len(todo)} ({failed} failed), {el:.0f}s, "
                  f"{(done + failed) / max(el, 1):.1f} windows/s")
        n_tr = sum(len(v) for k, v in store.items())
        print(f"{s}: {len(store)} windows cached, {n_tr} trades")


# ================================================================ fetch: Binance 1-second spot

def spot_path(sym, day):
    return os.path.join(CACHE, "spot1s", f"{sym}-{day}.bin")


def fetch_spot_day(sym, day):
    """One UTC day of 1-second closes as float32 x 86400 (NaN where missing). True if saved."""
    p = spot_path(sym, day)
    if os.path.exists(p):
        return True
    url = BIN_ZIP.format(s=sym, d=day)
    data = None
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": bot.UA}), timeout=60) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            time.sleep(3 + 3 * i)
        except Exception:
            time.sleep(3 + 3 * i)
    if not data:
        return False
    arr = array.array("f", [NAN]) * 86400
    d0 = int(dt.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        with z.open(z.namelist()[0]) as fh:
            for line in io.TextIOWrapper(fh):
                parts = line.split(",", 6)
                if len(parts) < 5 or not parts[0][:1].isdigit():
                    continue
                ot = int(parts[0])
                ot = ot // 1_000_000 if ot > 10 ** 14 else ot // 1000   # microseconds since 2025, ms before
                k = ot - d0
                if 0 <= k < 86400:
                    arr[k] = float(parts[4])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "wb") as fh:
        arr.tofile(fh)
    os.replace(p + ".tmp", p)
    return True


def fetch_spot(days):
    today = dt.datetime.now(dt.timezone.utc).date()
    jobs = [(sym, (today - dt.timedelta(days=i)).isoformat()) for sym in kc.SERIES.values()
            for i in range(1, int(days) + 2)]
    t_s = time.time()
    with ThreadPoolExecutor(6) as ex:
        ok = list(ex.map(lambda j: fetch_spot_day(*j), jobs))
    miss = [f"{a} {b}" for (a, b), o in zip(jobs, ok) if not o]
    print(f"spot 1s: {sum(ok)}/{len(jobs)} coin-days ({time.time() - t_s:.0f}s); missing: {miss[:12]}")


def fetch(days=30):
    os.makedirs(CACHE, exist_ok=True)
    fetch_spot(days)
    fetch_tapes(days)


# ================================================================ spot access + settlement model

class Spot:
    """Price known at second t = close of the 1-second kline that ended at t."""

    def __init__(self, sym):
        self.sym, self.days = sym, {}

    def day(self, d0):
        if d0 not in self.days:
            p = spot_path(self.sym, dt.datetime.fromtimestamp(d0, dt.timezone.utc).date().isoformat())
            a = array.array("f")
            if os.path.exists(p):
                with open(p, "rb") as fh:
                    a.frombytes(fh.read())
            self.days[d0] = a if len(a) == 86400 else None
            if len(self.days) > 4:   # windows are processed in time order
                self.days.pop(min(self.days))
        return self.days[d0]

    def px(self, t):
        t = int(t) - 1
        a = self.day(t - t % 86400)
        if a is None:
            return None
        v = a[t % 86400]
        return None if v != v else float(v)

    def run(self, t0, t1):
        """Prices at seconds t0+1..t1, last known value carried forward (None if the first is missing)."""
        out, last = [], None
        for t in range(int(t0) + 1, int(t1) + 1):
            v = self.px(t)
            last = v if v is not None else last
            out.append(last)
        return out


def model_window(w, sp):
    """Per-second Binance view of one window: {sec: (z_yes, est)} for the last TAPE_SEC seconds, plus the Binance
    estimate of the result. z_yes > 0 means spot favours YES; it counts how many 'typical moves until the
    settlement average is fixed' the expected average sits above the strike."""
    close, k = w["close"], w.get("strike")
    if not k:
        return None
    pre = sp.run(w["open"] - 60, w["open"]) if w.get("open") else []
    pre = [x for x in pre if x is not None]
    if len(pre) < 50:
        return None
    basis = k - sum(pre) / len(pre)       # BRTI-vs-Binance gap at the open
    seq = sp.run(close - TAPE_SEC - 301, close)   # 300 s of history before the tape starts, for the volatility
    if sum(1 for x in seq if x is None) > 30 or seq[0] is None:
        return None
    base = close - TAPE_SEC - 301   # seq[i] = price at second base+1+i
    final = seq[-60:]
    est_yes = sum(final) / 60 + basis >= k
    z = {}
    # rolling sum of squared 1-second moves over the last 300 seconds
    d2 = [((b - a) ** 2 if a is not None and b is not None else None) for a, b in zip(seq, seq[1:])]   # d2[j]: j->j+1
    pre_sum = [0.0]
    pre_n = [0]
    for x in d2:
        pre_sum.append(pre_sum[-1] + (x or 0.0))
        pre_n.append(pre_n[-1] + (x is not None))
    cum = [0.0]
    for x in seq:
        cum.append(cum[-1] + (x if x is not None else 0.0))
    for L in range(TAPE_SEC, 0, -1):     # L = seconds left
        t = close - L
        i = t - base - 1
        n = pre_n[i] - pre_n[i - 300]
        if n < 200 or seq[i] is None:
            continue
        sig2 = (pre_sum[i] - pre_sum[i - 300]) / n
        S = seq[i]
        if L >= 60:
            mean, var = S, sig2 * (L - 60 + 20.5)   # 20.5 = 60*61*121/6/3600
        else:
            known = cum[i + 1] - cum[i + 1 - (60 - L)]
            mean = (known + L * S) / 60
            var = sig2 * L * (L + 1) * (2 * L + 1) / 6 / 3600
        sd = math.sqrt(var) if var > 0 else 1e-12
        z[L] = (mean + basis - k) / sd
    return {"z": z, "est_yes": est_yes, "basis": basis}


# ================================================================ replay

def side_px(row, side):
    """Price of `side` for a tape row [ts, yes_price, taker_yes, count]."""
    return row[1] if side == "yes" else round(1 - row[1], 4)


def first_fills(tape, side, price, t_from):
    """(first time a trade printed through our price, first time one touched it) after t_from; inf if never."""
    inf = float("inf")
    through = touch = inf
    for r in tape:
        if r[0] <= t_from:
            continue
        p = side_px(r, side)
        if p < price - EPS:
            through = r[0]
            touch = min(touch, r[0])
            break
        if touch == inf and p <= price + EPS and (r[2] == 1) != (side == "yes"):
            touch = r[0]
    return through, touch


def maker_fill(tape, side, price, front, t_from, t_until):
    """(strict, fair, touch) for a bid on `side` at `price`, resting from t_from to t_until (exclusive)."""
    strict = touch = False
    for r in tape:
        if r[0] <= t_from or r[0] >= t_until:
            continue
        p = side_px(r, side)
        if p < price - EPS:
            strict = touch = True
            break
        if p <= price + EPS and (r[2] == 1) != (side == "yes"):   # someone sold our side into the bid
            touch = True
    return strict, (touch if front else strict), touch


def taker_fee(p, n=100):
    """Kalshi taker fee per contract on an order of n contracts: ceil(0.07 x n x p x (1-p)) to the cent."""
    return math.ceil(0.07 * n * p * (1 - p) * 100 - 1e-9) / 100 / n


CANCEL_Z = (None, 0.5, 1.0, 1.5, 2.0)
LATENCY = (1, 3, 10)
A_MINUTES = (1, 2, 3, 5)
B_SECONDS = (45, 30, 20, 10, 5)
B_ZMIN = (2.0, 3.0, 4.0, 6.0)
B_MAKER = (0.98, 0.99, 0.995, 0.998)


def replay(windows, tapes, spots):
    """All variant rows. Returns (rows by variant key, diagnostics)."""
    rows = {}
    diag = {"windows": 0, "modelled": 0, "agree": 0, "tape_trades": 0}

    def add(key, r):
        rows.setdefault(key, []).append(r)

    for w in windows:
        tape = tapes.get(w["t"])
        if tape is None:
            continue
        diag["windows"] += 1
        diag["tape_trades"] += len(tape)
        mw = model_window(w, spots[w["s"]])
        if not mw:
            continue
        diag["modelled"] += 1
        diag["agree"] += (mw["est_yes"] == (w["res"] == "yes"))
        z, close, day = mw["z"], w["close"], w["close"] // 86400
        base = {"day": day, "s": w["s"], "tk": w["t"]}
        # ---- A: the kcrypto bid (one tick in front of the best bid, 90c/95c+), with fast cancels
        for M in A_MINUTES:
            T = close - 60 * M
            c = w["c"].get(T)
            if not c:
                continue
            side = kc.leader(c)
            if not side:
                continue
            bid, ask, _, _ = kc.side_view(c, side)
            for level in (0.90, 0.95):
                if bid < level - EPS:
                    continue
                tick = 0.001 if bid >= 0.9 - EPS else 0.01
                price, front = round(bid + tick, 4), True
                if price >= ask - EPS:
                    price, front = bid, False
                won = w["res"] == side
                thr, tch = first_fills(tape, side, price, T)
                zs = [(L, (z[L] if side == "yes" else -z[L])) for L in range(60 * M - 1, 0, -1) if L in z]
                for cz in CANCEL_Z:
                    first_bad = None if cz is None else next((L for L, v in zs if v < cz), None)
                    for lat in (LATENCY if cz is not None else (0,)):
                        until = close + 1 if first_bad is None else close - first_bad + lat
                        st, to = thr < until, tch < until
                        add(("A", level, M, cz, lat), {**base, "t": T, "price": price, "fee": 0.0, "won": won,
                                                       "fills": (st, to if front else st, to)})
        # ---- B: last seconds, side picked by the Binance running-average model
        for L in B_SECONDS:
            zz = z.get(L)
            if zz is None:
                continue
            side = "yes" if zz > 0 else "no"
            za = abs(zz)
            won = w["res"] == side
            t = close - L
            fcache = {}
            for zmin in B_ZMIN:
                if za < zmin:
                    continue
                # taker: the next real trade where someone bought our side, 1-4 s after we decide
                buy = next((r for r in tape if t + 1 <= r[0] <= t + 4 and (r[2] == 1) == (side == "yes")), None)
                p = side_px(buy, side) if buy else None
                ok = p is not None and p <= 0.999 + EPS
                add(("Bt", L, zmin), {**base, "t": t, "price": p if ok else 0.99, "fee": taker_fee(p) if ok else 0.0,
                                      "won": won, "fills": (ok, ok, ok)})
                # maker: a bid at a fixed price from t+1 to the close, only if the last trade was at or above it
                last = next((r for r in reversed(tape) if r[0] <= t), None)
                if last:
                    lp = side_px(last, side)
                    for lv in B_MAKER:
                        if lp >= lv - EPS:
                            if lv not in fcache:
                                fcache[lv] = maker_fill(tape, side, lv, lp > lv + EPS, t + 1, close + 1)
                            f = fcache[lv]
                            add(("Bm", L, zmin, lv), {**base, "t": t, "price": lv, "fee": 0.0, "won": won,
                                                      "fills": f})
            # twin without the model: the side the market favours (last trade >= 50c), same timing, taker
            last = next((r for r in reversed(tape) if r[0] <= t), None)
            if last:
                ms = "yes" if last[1] >= 0.5 else "no"
                buy = next((r for r in tape if t + 1 <= r[0] <= t + 4 and (r[2] == 1) == (ms == "yes")), None)
                if buy:
                    p = side_px(buy, ms)
                    if 0.90 <= p <= 0.999 + EPS:
                        add(("Bmkt", L), {**base, "t": t, "price": p, "fee": taker_fee(p), "won": w["res"] == ms,
                                          "fills": (True, True, True)})
    return rows, diag


# ================================================================ report

def run():
    t_s = time.time()
    windows = kc.load_windows()
    tapes = {}
    for s in kc.SERIES:
        tapes.update({k: compact(v) for k, v in kc.rjson(os.path.join(CACHE, f"tape_{s}.json.gz"), {}).items()})
    windows = [w for w in windows if w["t"] in tapes]
    for w in windows:
        w["spot"] = None   # the minute spot isn't needed here
    spots = {s: Spot(sym) for s, sym in kc.SERIES.items()}
    print(f"{len(windows)} windows with a tape ({time.time() - t_s:.0f}s)")
    rows, diag = {}, {}
    for s in kc.SERIES:   # one coin at a time keeps the spot cache small
        r, d = replay([w for w in windows if w["s"] == s], tapes, spots)
        for k, v in r.items():
            rows.setdefault(k, []).extend(v)
        for k, v in d.items():
            diag[k] = diag.get(k, 0) + v
        print(f"  {s}: {d} ({time.time() - t_s:.0f}s)")
    if not windows:
        print("no data")
        return
    first = min(w["close"] for w in windows)
    last = max(w["close"] for w in windows)
    day = lambda x: dt.datetime.fromtimestamp(x, dt.timezone.utc).date().isoformat()
    L = ["# Kalshi 15-minute crypto: what a fast bot could add", "",
         f"Generated {bot.iso()}. {diag['windows']} windows with a trade tape ({diag['tape_trades']} trades in their "
         f"last {TAPE_SEC // 60} minutes), closing {day(first)} to {day(last)}. Paper only. Code: `kfast.py`.", "",
         f"Binance 1-second spot was usable on {diag['modelled']} of them. Our Binance estimate of the settlement "
         f"average agreed with Kalshi's result on **{diag['agree']} of {diag['modelled']}** "
         f"({diag['modelled'] - diag['agree']} disagreements: BRTI is not Binance).", "",
         "P&L per $100 staked. Fill models as in kcrypto.md: strict (a trade printed below our price), fair (front of "
         "the line: a trade at our price counts), touch (optimistic). Taker rows pay the fee on a 100-contract order "
         "and buy at the price of the next real trade on our side, 1-4 seconds after the decision. The 90% band "
         "resamples whole days.", ""]
    L += ["## A. The slow bid, but pulled when Binance says the lead is in danger", "",
          "Same bid as `kc_maker` (one tick in front of the best bid, placed with M minutes left). Cancel when the "
          "Binance z-score of our side drops below the line; the order is really gone `latency` seconds later. "
          "No cancel = the slow bot.", ""]
    L += kc.HEAD
    for level in (0.95, 0.90):
        for M in A_MINUTES:
            for cz in CANCEL_Z:
                for lat in (LATENCY if cz is not None else (0,)):
                    key = ("A", level, M, cz, lat)
                    if key in rows:
                        lab = (f"{level * 100:.0f}c+, {M} min, " +
                               ("no cancel" if cz is None else f"cancel z<{cz}, {lat}s"))
                        L.append(kc.line(lab, kc.stats(rows[key], 1)))
    L += ["", "Strict fills for the same rows (only trades through our price):", ""] + kc.HEAD
    for level in (0.95,):
        for M in A_MINUTES:
            for cz in (None, 1.0, 2.0):
                for lat in (LATENCY if cz is not None else (0,)):
                    key = ("A", level, M, cz, lat)
                    if key in rows:
                        lab = f"{level * 100:.0f}c+, {M} min, " + ("no cancel" if cz is None else f"cancel z<{cz}, {lat}s")
                        L.append(kc.line(lab, kc.stats(rows[key], 0)))
    L += ["", "## B. The last seconds: buy what the running average says", "",
          "With L seconds left, the side the Binance running average favours, if z is at least the minimum. "
          "Taker = buy at the next real trade price on that side. 'Market favourite' = same timing, side by the "
          "last Kalshi trade, no model (90-99.5c), to show what the model adds.", ""] + kc.HEAD
    for Ls in B_SECONDS:
        for zmin in B_ZMIN:
            key = ("Bt", Ls, zmin)
            if key in rows:
                L.append(kc.line(f"taker, {Ls}s left, z {zmin}+", kc.stats(rows[key], 1)))
        if ("Bmkt", Ls) in rows:
            L.append(kc.line(f"market favourite, {Ls}s left", kc.stats(rows[("Bmkt", Ls)], 1)))
    L += ["", "Maker bids at a fixed price in the last seconds (fair fills; touch in the next table):", ""] + kc.HEAD
    for Ls in B_SECONDS:
        for zmin in B_ZMIN:
            for lv in B_MAKER:
                key = ("Bm", Ls, zmin, lv)
                if key in rows:
                    L.append(kc.line(f"bid {lv * 100:g}c, {Ls}s left, z {zmin}+", kc.stats(rows[key], 1)))
    L += ["", "Same, touch fills (optimistic: any trade at our price fills us):", ""] + kc.HEAD
    for Ls in (30, 10):
        for zmin in (3.0,):
            for lv in B_MAKER:
                key = ("Bm", Ls, zmin, lv)
                if key in rows:
                    L.append(kc.line(f"bid {lv * 100:g}c, {Ls}s left, z {zmin}+", kc.stats(rows[key], 2)))
    L += ["", "## By coin (A: 95c+, 3 min, cancel z<1, 3s; B: taker 20s left, z 3+)", "", "| Coin | A | B |",
          "|---|---|---|"]
    for s in kc.SERIES:
        cells = []
        for key, mdl in ((("A", 0.95, 3, 1.0, 3), 1), (("Bt", 20, 3.0), 1)):
            st = kc.stats([r for r in rows.get(key, []) if r["s"] == s], mdl)
            cells.append(f"{st['fills']} fills, {kc.money(st['per100'])}" if st.get("fills") else "-")
        L.append(f"| {s} | {cells[0]} | {cells[1]} |")
    L.append("")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "kfast.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"done in {time.time() - t_s:.0f}s")


# ================================================================ incentives

def incentives():
    """Kalshi's public incentive programs (liquidity / volume rewards), all pages, filtered to the 15-minute crypto
    series. Rewards are for US members only (help.kalshi.com), so for Jan in Sweden this is context, not income."""
    for status in ("active", "upcoming", None):
        progs, cur = [], None
        for _ in range(100):
            p = {"limit": 1000}
            if status:
                p["status"] = status
            if cur:
                p["cursor"] = cur
            try:
                res = kc.get("/incentive_programs", p)
            except Exception as e:
                print(status, "FAILED", e)
                break
            progs += res.get("incentive_programs") or []
            cur = res.get("next_cursor") or res.get("cursor")
            if not cur or not res.get("incentive_programs"):
                break
        kinds = {}
        for x in progs:
            k = (x.get("market_ticker") or "?").split("-")[0]
            kinds[k] = kinds.get(k, 0) + 1
        hit = [x for x in progs if (x.get("market_ticker") or "").split("-")[0] in kc.SERIES]
        crypto = sorted((k, n) for k, n in kinds.items() if "BTC" in k or "ETH" in k or "SOL" in k)
        print(f"status={status}: {len(progs)} programs over {len(kinds)} series; crypto series: {crypto[:30]}")
        print(f"  15-minute crypto programs: {len(hit)}")
        for x in hit[:10]:
            print("   ", json.dumps(x)[:400])


# ================================================================ selftest

def selftest():
    # settlement model: a flat price far above the strike must give a large positive z, and one far below negative
    class Flat:
        def __init__(self, f):
            self.f = f

        def run(self, t0, t1):
            return [self.f(t) for t in range(int(t0) + 1, int(t1) + 1)]

    close = 1_000_000 * 900
    w = {"close": close, "open": close - 900, "strike": 100.0, "t": "X", "s": "KXBTC15M", "res": "yes",
         "c": {}}
    up = Flat(lambda t: 100.0 + (0.02 if t % 2 else -0.02) + (2.0 if t > close - 900 else 0))
    m = model_window(w, up)
    assert m and m["est_yes"] and m["z"][10] > m["z"][300] > 3, m and (m["z"][10], m["z"][300])
    dn = Flat(lambda t: 100.0 + (0.02 if t % 2 else -0.02) - (2.0 if t > close - 900 else 0))
    m2 = model_window(w, dn)
    assert m2 and not m2["est_yes"] and m2["z"][10] < -3
    # fills: a YES bid at 95c; a NO-taker trade at 95c (front) fills fair; a 94c print fills strict; cancel before it
    tape = [[close - 100, 0.96, 1, 5], [close - 50, 0.95, 0, 5], [close - 20, 0.94, 0, 5]]
    raw = [[close - 9.5, 0.97, 1, 1], [close - 9.4, 0.99, 1, 1], [close - 9.2, 0.96, 0, 1], [close - 9.1, 0.98, 1, 1]]
    assert compact(raw) == [[close - 10, 0.99, 1], [close - 10, 0.97, 1], [close - 10, 0.96, 0], [close - 10, 0.98, 1]], compact(raw)
    assert compact(compact(raw)) == compact(raw)
    assert maker_fill(tape, "yes", 0.95, True, close - 120, close + 1) == (True, True, True)
    assert maker_fill(tape, "yes", 0.95, True, close - 120, close - 30) == (False, True, True)
    assert maker_fill(tape, "yes", 0.95, False, close - 120, close - 30) == (False, False, True)
    assert maker_fill(tape, "no", 0.03, True, close - 120, close - 60) == (False, False, False)
    for side, pr, fr, a, b in (("yes", 0.95, True, close - 120, close - 30), ("yes", 0.95, False, close - 120, close + 1),
                               ("no", 0.05, True, close - 120, close - 60), ("yes", 0.96, True, close - 99, close - 10)):
        thr, tch = first_fills(tape, side, pr, a)
        st = thr < b
        assert maker_fill(tape, side, pr, fr, a, b) == (st, (tch < b) if fr else st, tch < b), (side, pr)
    assert abs(taker_fee(0.99) - 0.0007) < 1e-9 and abs(taker_fee(0.5) - 0.0175) < 1e-9
    assert abs(parse_ts("2026-11-09T18:57:16.25Z") % 60 - 16.25) < 1e-6
    # replay end to end on one made-up window
    w["c"] = {close - 180: [0.96, 0.97, 0.96, 0.97, 10]}
    spots = {"KXBTC15M": up}
    tape = compact(tape)
    rows, diag = replay([w], {"X": tape}, spots)
    assert diag["modelled"] == 1 and diag["agree"] == 1, diag
    a = rows[("A", 0.95, 3, None, 0)][0]
    assert a["price"] == 0.961 and a["fills"][0], a   # one tick in front of 96c; the 94c print goes through
    print("kfast selftest OK", len(rows), "variants")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "fetch":
        fetch(sys.argv[2] if len(sys.argv) > 2 else os.environ.get("KF_DAYS", 14))
    elif cmd.startswith("fetch_"):
        fetch(cmd.split("_", 1)[1])
    else:
        {"run": run, "selftest": selftest, "incentives": incentives}[cmd]()
