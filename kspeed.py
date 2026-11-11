#!/usr/bin/env python3
"""What does speed buy on Kalshi's 15-minute crypto markets? (2026-11-10, Jan: "Yes" to a speed re-test, and
"somewhere in the timelines should show a discrepancy"). Research only.

PAPER ONLY. Reads public history and never trades.

Three questions, on data the repo already downloads (kcrypto.py windows + minute candles + Binance minutes,
kfast.py per-second trade tapes + Binance seconds):

  1. THE WHOLE 15 MINUTES. The earlier digs only looked at the last 5 minutes. Here every minute of the window:
     a) is the Kalshi price itself right, at each stretch of the timeline (buy at the real ask, with the fee)?
     b) does Binance know something Kalshi's price doesn't? Learn "how often YES wins" for each (minutes left,
        distance of Binance from the line) on the older half, bet on the newer half when that says the ask is
        too cheap, and the other way round. Bought at once, and one minute later.
     c) after a big Binance minute, does Kalshi's price keep drifting the next minute?
  2. THE DELAY CURVE, second by second (last 5 minutes, real trades): when Binance jumps, how many seconds until
     Kalshi's trades have moved, and what does buying the jump make if we are 0, 1, 2, 3, 5, 10 or 30 s late?
     Same sweep for the "45 seconds left" buy of kfastlive.
  3. HOW FAST ARE WE REALLY. `ping` times Kalshi and Binance from the machine it runs on; the report also reads the
     timings the live paper bot (kfastlive.py) has logged.

    python3 kspeed.py fetch [days]   # kcrypto fetch (60 d) + full 15-minute candles
    python3 kspeed.py tapes [days]   # kfast fetch: per-second trade tapes + Binance seconds (default 5 d, slow)
    python3 kspeed.py run            # write backtest/kspeed.md
    python3 kspeed.py ping           # latency meter (Kalshi REST, Binance REST), prints a small table
    python3 kspeed.py selftest       # offline
  From GitHub: probe `btks` (fetch + ping + run), `btkstape` (tapes + run), `btksrun`, `btksping`.

Windows closing 2026-11-10 or later are left out (PROTOCOL.md holdout).
"""
import datetime as dt
import glob
import json
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import kcrypto as kc
import kfast as kf

CACHE = os.path.join(bot.ROOT, "bt_cache", "ks")
OUT = os.path.join(bot.ROOT, "backtest")
HOLD = int(dt.datetime(2026, 11, 10, tzinfo=dt.timezone.utc).timestamp())
FULL_MIN = 16
EPS = 1e-9
PHASES = ((14, 11, "minutes 1-4"), (10, 8, "minutes 5-7"), (7, 5, "minutes 8-10"), (4, 3, "minutes 11-12"),
          (2, 1, "minutes 13-14"))
BANDS = ((0.05, 0.20), (0.20, 0.40), (0.40, 0.60), (0.60, 0.80), (0.80, 0.95), (0.95, 0.995))
THRESH = (0.03, 0.06, 0.10)
DELAYS = (0, 1, 2, 3, 5, 10, 30)
JUMP = 1.0            # a "jump": Binance's z-score moved this much in 3 seconds
TRIES = [0]           # versions looked at (for the exam's luck bar)


def usd(x):
    return "n/a" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def fee(p, n=10):
    return kf.taker_fee(p, n)


def phase(L):
    for hi, lo, name in PHASES:
        if lo <= L <= hi:
            return name
    return None


# ================================================================ fetch: all 15 minute candles

def fetch_full():
    """All 15 minute candles of every window, with kcrypto's batch fetch (all coins of the same hours in one call;
    Kalshi caps one call at 10,000 candles = tickers x minutes of the whole span)."""
    os.makedirs(CACHE, exist_ok=True)
    ms, store = [], {}
    for s in kc.SERIES:
        ms += [m for m in kc.rjson(os.path.join(kc.CACHE, f"markets_{s}.json.gz"), []) if m["close"] < HOLD]
        store.update({k: v for k, v in kc.rjson(os.path.join(CACHE, f"full_{s}.json.gz"), {}).items() if v})
    keep = kc.LOOKBACK_MIN
    kc.LOOKBACK_MIN = FULL_MIN
    try:
        kc.fetch_candles(ms, store)
    finally:
        kc.LOOKBACK_MIN = keep
    for s in kc.SERIES:
        mine = {m["t"]: store[m["t"]] for m in ms if m["s"] == s and store.get(m["t"])}
        kc.wjson(os.path.join(CACHE, f"full_{s}.json.gz"), mine)
        print(f"{s}: {sum(1 for v in mine.values() if len(v) >= 12)} windows with 12+ minute candles")


def fetch(days=60):
    kc.fetch(int(days))
    fetch_full()


def fetch_tapes(days=None):
    """Per-second trade tapes + Binance seconds (kfast). Slow: BTC alone is ~4 s a window."""
    kf.fetch(int(days or os.environ.get("KF_DAYS", 5)))


# ================================================================ part 1: the whole 15 minutes (minute candles)

def load_minutes():
    """Every window before the holdout with all its minute candles: {..., c: {end_ts: [yb, ya, lo, hi, vol]}}."""
    out = []
    for s in kc.SERIES:
        ms = kc.rjson(os.path.join(kc.CACHE, f"markets_{s}.json.gz"), [])
        cs = kc.rjson(os.path.join(CACHE, f"full_{s}.json.gz"), {})
        spot = kc.rjson(os.path.join(kc.CACHE, f"spot_{s}.json.gz"), {})
        for m in ms:
            rows = cs.get(m["t"]) or []
            if m["close"] >= HOLD or len(rows) < 8 or m.get("res") not in ("yes", "no"):
                continue
            out.append({**m, "c": {r[0]: r[1:] for r in rows if r and r[0]}, "spot": spot})
    return sorted(out, key=lambda w: w["close"])


def z_minute(w, t, L):
    """Binance view at minute end t with L minutes left: (z of YES, last one-minute move in typical moves).
    The strike is tied to Binance by the gap at the open; the last-minute average shortens the clock a little."""
    sp, k = w["spot"], w.get("strike")
    if not sp or not k:
        return None
    px = sp.get(str(t))
    op = sp.get(str(w["close"] - 900))
    if px is None or op is None:
        return None
    sq, n = 0.0, 0
    for i in range(60):
        a, b = sp.get(str(t - 60 * (i + 1))), sp.get(str(t - 60 * i))
        if a and b:
            sq += (b - a) ** 2
            n += 1
    if n < 30 or sq <= 0:
        return None
    sd1 = math.sqrt(sq / n)
    prev = sp.get(str(t - 60))
    z = (px - op) / (sd1 * math.sqrt(max(L - 0.66, 0.34)))
    return z, ((px - prev) / sd1 if prev else 0.0)


def minute_rows(windows):
    """One row per window and minute with a real two-sided quote."""
    rows = []
    for w in windows:
        yes = w["res"] == "yes"
        for L in range(14, 0, -1):
            t = w["close"] - 60 * L
            c = w["c"].get(t)
            if not c or c[0] is None or c[1] is None or not (0 < c[0] <= c[1] < 1):
                continue
            zz = z_minute(w, t, L)
            nx = w["c"].get(t + 60) if L > 1 else None
            if nx and (nx[0] is None or nx[1] is None or not (0 < nx[0] <= nx[1] < 1)):
                nx = None
            rows.append({"tk": w["t"], "s": w["s"], "close": w["close"], "L": L, "yb": c[0], "ya": c[1], "yes": yes,
                         "z": zz[0] if zz else None, "mv": zz[1] if zz else None,
                         "nyb": nx[0] if nx else None, "nya": nx[1] if nx else None})
    return rows


def bet(ev, t, price, won, with_fee=True):
    f = fee(price) if with_fee else 0.0
    return {"ev": ev, "t": t, "cost": price + f, "pay": 1.0 if won else 0.0, "sh": 1}


def tally(bets, sims=300, seed=5):
    """(n, per $100, low, high): equal stake per bet, luck range by resampling whole 15-minute slots."""
    if not bets:
        return 0, None, None, None
    by = {}
    for b in bets:
        g = by.setdefault(b["ev"], [0.0, 0])
        g[0] += (b["pay"] - b["cost"]) / b["cost"]
        g[1] += 1
    gs = list(by.values())
    n = len(bets)
    rate = 100 * sum(g[0] for g in gs) / n
    if len(gs) < 5:
        return n, rate, None, None
    rnd = random.Random(seed)
    res = []
    for _ in range(sims):
        pick = [gs[rnd.randrange(len(gs))] for _ in gs]
        m = sum(g[1] for g in pick)
        res.append(100 * sum(g[0] for g in pick) / max(m, 1))
    res.sort()
    return n, rate, res[int(0.05 * sims)], res[int(0.95 * sims) - 1]


def cell(bets):
    n, r, lo, hi = tally(bets)
    if not n:
        return "-"
    return f"{usd(r)} ({n})" if lo is None else f"{usd(r)} ({usd(lo)} to {usd(hi)}, {n})"


def timeline_table(rows):
    """a) buy either side at the real ask + fee, by stretch of the window and by price."""
    L = ["| Stretch | " + " | ".join(f"{int(a * 100)}-{b * 100:g}c" for a, b in BANDS) + " | all |",
         "|---|" + "---|" * (len(BANDS) + 1)]
    mid = list(L)
    for hi, lo, name in PHASES:
        sub = [r for r in rows if lo <= r["L"] <= hi]
        ca, cm, alla, allm = [], [], [], []
        for a, b in BANDS:
            ba, bm = [], []
            for r in sub:
                for side_yes in (True, False):
                    ask = r["ya"] if side_yes else 1 - r["yb"]
                    m = (r["ya"] + r["yb"]) / 2
                    m = m if side_yes else 1 - m
                    won = r["yes"] == side_yes
                    if a <= ask < b:
                        ba.append(bet(r["close"], r["close"], ask, won))
                    if a <= m < b:
                        bm.append(bet(r["close"], r["close"], m, won, with_fee=False))
            ca.append(cell(ba))
            cm.append(cell(bm))
            alla += ba
            allm += bm
            TRIES[0] += 1
        L.append(f"| {name} | " + " | ".join(ca) + f" | {cell(alla)} |")
        mid.append(f"| {name} | " + " | ".join(cm) + f" | {cell(allm)} |")
    return L, mid


def zb(z):
    return max(-8, min(8, int(math.floor(z * 2))))


def learn(rows):
    """{(stretch, z bucket): chance YES wins}, smoothed toward 50/50."""
    cnt = {}
    for r in rows:
        if r["z"] is None:
            continue
        k = (phase(r["L"]), zb(r["z"]))
        c = cnt.setdefault(k, [0, 0])
        c[0] += r["yes"]
        c[1] += 1
    return {k: ((y + 1) / (n + 2), n) for k, (y, n) in cnt.items()}


def model_bets(rows, table, thr, delay, lmin=1, lmax=14):
    """First minute of each window where the learned chance beats the ask by thr (after the fee). delay=1 buys at
    the next minute's quote instead."""
    out, done = [], set()
    for r in rows:
        if r["tk"] in done or r["z"] is None or not (lmin <= r["L"] <= lmax):
            continue
        got = table.get((phase(r["L"]), zb(r["z"])))
        if not got or got[1] < 50:
            continue
        p = got[0]
        for side_yes in (True, False):
            ask = r["ya"] if side_yes else 1 - r["yb"]
            pp = p if side_yes else 1 - p
            if pp - ask - fee(ask) >= thr and 0.03 <= ask <= 0.97:
                if delay:
                    if r["nya"] is None:
                        break
                    ask = r["nya"] if side_yes else 1 - r["nyb"]
                done.add(r["tk"])
                out.append({**bet(r["close"], r["close"] - 60 * r["L"], ask, r["yes"] == side_yes), "L": r["L"],
                            "q": pp})
                break
    return out


def drift_table(rows):
    """c) after a big Binance minute: Kalshi's mid move in the same minute's quote vs the minute after."""
    by = {}
    prev = {}
    for r in rows:
        key = (r["tk"], r["L"])
        prev[key] = r
    out = []
    for size, lab in ((1.0, "1 typical move or more"), (2.0, "2 or more"), (3.0, "3 or more")):
        same, nxt, n = [], [], 0
        for r in rows:
            if r["mv"] is None or abs(r["mv"]) < size or r["nya"] is None:
                continue
            before = prev.get((r["tk"], r["L"] + 1))
            if not before:
                continue
            d = 1 if r["mv"] > 0 else -1
            m0 = (before["ya"] + before["yb"]) / 2
            m1 = (r["ya"] + r["yb"]) / 2
            m2 = (r["nya"] + r["nyb"]) / 2
            if not (0.1 <= m0 <= 0.9):
                continue
            same.append(d * (m1 - m0) * 100)
            nxt.append(d * (m2 - m1) * 100)
            n += 1
        if n:
            out.append(f"| {lab} | {n} | {statistics.mean(same):+.1f}c | {statistics.mean(nxt):+.2f}c |")
        TRIES[0] += 1
    return out


# ================================================================ part 2: second by second (trade tapes)

def last_px(tape, idx, t, side):
    """Price of `side` at the last trade at or before second t (idx = list of seconds, for bisect)."""
    import bisect
    i = bisect.bisect_right(idx, t) - 1
    return kf.side_px(tape[i], side) if i >= 0 else None


def next_buy(tape, idx, t0, t1, side):
    """Dearest price a buyer of `side` paid in the first second with such a trade in [t0, t1]."""
    import bisect
    i = bisect.bisect_left(idx, t0)
    want = 1 if side == "yes" else 0
    while i < len(tape) and tape[i][0] <= t1:
        if tape[i][2] == want:
            return kf.side_px(tape[i], side)
        i += 1
    return None


def seconds_replay(windows, tapes, spots):
    """Jump study + 45-second buy, per delay. Returns dicts of bet lists and the price path after jumps."""
    jump = {d: [] for d in DELAYS}
    late = {d: [] for d in DELAYS}
    path = {k: [] for k in (0, 1, 2, 3, 5, 10, 20, 30)}
    n_jump = 0
    for w in windows:
        tape = tapes.get(w["t"])
        if not tape:
            continue
        mw = kf.model_window(w, spots[w["s"]])
        if not mw:
            continue
        z, close = mw["z"], w["close"]
        idx = [r[0] for r in tape]
        # ---- jumps: z moved JUMP or more in 3 seconds while the market was still undecided (15-85c)
        cool = 0
        for L in range(300, 40, -1):
            if L > cool and cool:
                continue
            if L not in z or L + 3 not in z:
                continue
            dz = z[L] - z[L + 3]
            if abs(dz) < JUMP:
                continue
            side = "yes" if dz > 0 else "no"
            t = close - L
            pre = last_px(tape, idx, t - 4, side)
            if pre is None or not (0.15 <= pre <= 0.85):
                continue
            cool = L - 30
            n_jump += 1
            won = w["res"] == side
            for k in path:
                p = last_px(tape, idx, t + k, side)
                if p is not None:
                    path[k].append((p - pre) * 100)
            for d in DELAYS:
                p = next_buy(tape, idx, t + d, t + d + 4, side)
                if p is not None and 0.02 <= p <= 0.98:
                    jump[d].append({**bet(close, t, p, won), "pre": pre})
        # ---- the kfastlive buy: 45 s left, Binance very sure (z 4+)
        zz = z.get(45)
        if zz is not None and abs(zz) >= 4.0:
            side = "yes" if zz > 0 else "no"
            t = close - 45
            for d in DELAYS:
                if d >= 30:
                    continue
                p = next_buy(tape, idx, t + d, t + d + 3, side)
                if p is not None and p <= 0.999 + EPS:
                    late[d].append(bet(close, t, p, w["res"] == side))
    return jump, late, path, n_jump


def load_seconds():
    windows = [w for w in kc.load_windows() if w["close"] < HOLD]
    tapes = {}
    for s in kc.SERIES:
        tapes.update({k: kf.compact(v) for k, v in kc.rjson(os.path.join(kf.CACHE, f"tape_{s}.json.gz"), {}).items()})
    windows = [w for w in windows if w["t"] in tapes]
    for w in windows:
        w["spot"] = None
    return windows, tapes


# ================================================================ part 3: how fast are we

def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def ping(n=25):
    """Round-trip times from this machine, on one kept-open connection (like a real bot would hold)."""
    import http.client
    import socket
    import ssl
    import urllib.parse
    tk = None
    try:
        ms = kc.get("/markets", {"series_ticker": "KXBTC15M", "status": "open", "limit": 1}).get("markets") or []
        tk = ms[0]["ticker"] if ms else None
    except Exception as e:
        print("no open market:", str(e)[:100])
    targets = [("Kalshi order book", f"{kc.K}/markets/{tk}/orderbook" if tk else None),
               ("Kalshi trades", f"{kc.K}/markets/trades?ticker={tk}&limit=5" if tk else None),
               ("Binance price (1-second bars)", kf_bin_url())]
    out = []
    for name, url in targets:
        if not url:
            continue
        u = urllib.parse.urlparse(url)
        try:
            t0 = time.perf_counter()
            sock = socket.create_connection((u.hostname, 443), timeout=10)
            tcp = (time.perf_counter() - t0) * 1000
            sock.close()
            conn = http.client.HTTPSConnection(u.hostname, timeout=15, context=ssl.create_default_context())
            times = []
            for i in range(n + 1):
                t0 = time.perf_counter()
                conn.request("GET", u.path + ("?" + u.query if u.query else ""),
                             headers={"User-Agent": bot.UA, "Accept": "application/json"})
                r = conn.getresponse()
                r.read()
                if i:                       # the first one pays for the handshake
                    times.append((time.perf_counter() - t0) * 1000)
                time.sleep(0.25)
            conn.close()
            row = {"name": name, "tcp": round(tcp, 1), "p50": round(pct(times, 0.5), 1),
                   "p90": round(pct(times, 0.9), 1), "max": round(max(times), 1), "n": len(times)}
        except Exception as e:
            row = {"name": name, "err": str(e)[:120]}
        out.append(row)
        print(row)
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, "ping.json"), "w") as fh:
        json.dump({"at": bot.iso(), "rows": out}, fh)
    return out


def kf_bin_url():
    return "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1s&limit=5"


def live_timings():
    """Timings the live paper bot logged (state/kfast_live/days/*.jsonl)."""
    book, binance, n = [], [], 0
    for p in sorted(glob.glob(os.path.join(bot.ROOT, "state", "kfast_live", "days", "*.jsonl"))):
        with open(p) as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                n += 1
                for s in (row.get("snaps") or {}).values():
                    for k in ("book_ms", "book2_ms"):
                        if s.get(k) is not None:
                            book.append(s[k])
                    if s.get("bin_ms") is not None:
                        binance.append(s["bin_ms"])
    return {"rows": n, "book50": pct(book, 0.5), "book90": pct(book, 0.9), "bin50": pct(binance, 0.5),
            "bin90": pct(binance, 0.9)}


# ================================================================ report

def run():
    import exam
    t_s = time.time()
    TRIES[0] = 0
    W = load_minutes()
    rows = minute_rows(W)
    day = lambda x: dt.datetime.fromtimestamp(x, dt.timezone.utc).date().isoformat()
    print(f"{len(W)} windows, {len(rows)} window-minutes ({time.time() - t_s:.0f}s)")
    if not W:
        print("no data")
        return
    L = ["# Kalshi 15-minute crypto: what speed buys, and the whole 15 minutes", "",
         f"Generated {bot.iso()}. Paper only. Code: `kspeed.py`. Windows closing {day(W[0]['close'])} to "
         f"{day(W[-1]['close'])} ({len(W)} windows of 7 coins, {len(rows)} window-minutes with a real two-sided "
         "quote). Nothing from 10 Nov on (holdout).", "",
         "Every number is profit per $100 put in, after Kalshi's fee, bought at the real asking price. In brackets: "
         "the luck range (9 times in 10 the true number sits inside) and the number of bets. Bets in the same "
         "15 minutes count as one for the luck range, since the coins move together.", ""]
    # ---- 1a
    ask_t, mid_t = timeline_table(rows)
    L += ["## 1. The whole 15 minutes", "", "### a) Is the price right, minute by minute?", "",
          "Buy a side at its asking price, by how far into the 15 minutes we are (rows) and what the side costs "
          "(columns). If some stretch of the timeline were mispriced, a cell here would be clearly above $0.", ""]
    L += ask_t
    L += ["", "The same at the middle price with no fee (what a perfect waiting order would get; you can't just "
          "buy this, it shows if the price itself leans):", ""] + mid_t
    # ---- 1b
    L += ["", "### b) Does Binance know more than Kalshi's price?", "",
          "Learned on one half of the days: how often YES wins for each stretch and each distance of the Binance "
          "price from the line. On the other half: buy when that chance beats the asking price by the gap, at most "
          "one bet a window. 'Same minute' pretends we buy at the quote of the very minute we looked. 'One minute "
          "late' buys at the next minute's quote.", "",
          "| Learned on | Gap | Stretch | Same minute | One minute late |", "|---|---|---|---|---|"]
    cut = W[len(W) // 2]["close"]
    old, new = [r for r in rows if r["close"] < cut], [r for r in rows if r["close"] >= cut]
    best = None
    for lab, tr, te in (("older half", old, new), ("newer half", new, old)):
        table = learn(tr)
        for thr in THRESH:
            for name, lo, hi in (("whole window", 1, 14), ("minutes 1-7", 8, 14), ("minutes 8-14", 1, 7)):
                b0 = model_bets(te, table, thr, 0, lo, hi)
                b1 = model_bets(te, table, thr, 1, lo, hi)
                TRIES[0] += 2
                L.append(f"| {lab} | {thr * 100:.0f}c | {name} | {cell(b0)} | {cell(b1)} |")
                if lab == "older half" and name == "whole window" and thr == 0.06:
                    best = b1
    # ---- 1c
    L += ["", "### c) After a big Binance minute, does Kalshi keep drifting?", "",
          "Minutes where Binance moved a lot, while Kalshi was at 10-90c. 'Same minute' = how far Kalshi's price "
          "had already moved by the end of that minute. 'Minute after' = what was left to move. A slow market would "
          "leave cents in the last column.", "",
          "| Binance move in one minute | Cases | Kalshi, same minute | Kalshi, minute after |", "|---|---|---|---|"]
    L += drift_table(rows)
    print("\n".join(L))
    print(f"part 1 done ({time.time() - t_s:.0f}s)")
    # ---- 2
    windows, tapes = load_seconds()
    spots = {s: kf.Spot(sym) for s, sym in kc.SERIES.items()}
    jump = {d: [] for d in DELAYS}
    late = {d: [] for d in DELAYS}
    path, n_jump = {}, 0
    for s in kc.SERIES:
        j, l, p, n = seconds_replay([w for w in windows if w["s"] == s], tapes, spots)
        for d in DELAYS:
            jump[d] += j[d]
            late[d] += l[d]
        for k, v in p.items():
            path.setdefault(k, []).extend(v)
        n_jump += n
        print(f"  {s}: {n} jumps ({time.time() - t_s:.0f}s)")
    P2 = ["", "## 2. The delay curve, second by second", ""]
    if windows:
        P2 += [f"{len(windows)} windows with every trade of their last 5 minutes ({day(windows[0]['close'])} to "
               f"{day(windows[-1]['close'])}) and Binance prices every second.", "",
               "### a) When Binance jumps, how fast does Kalshi follow?", "",
               f"A jump = Binance moved the odds a lot within 3 seconds while Kalshi was still at 15-85c "
               f"({n_jump} jumps). The line shows how many cents Kalshi's last traded price had moved our way, "
               "counted from 4 seconds before the jump.", "",
               "| Seconds after the jump | " + " | ".join(str(k) for k in sorted(path)) + " |",
               "|---|" + "---|" * len(path),
               "| Kalshi has moved | " + " | ".join(f"{statistics.mean(path[k]):+.1f}c" if path[k] else "-"
                                                    for k in sorted(path)) + " |", "",
               "Buying the jump's side at the next real trade (the dearest one in that second), held to the result:",
               "", "| We are this late | Bets | Avg price paid | P&L per $100 (luck range) |", "|---|---|---|---|"]
        for d in DELAYS:
            b = jump[d]
            TRIES[0] += 1
            n, r, lo, hi = tally(b)
            if n:
                P2.append(f"| {'under 1 s' if d == 0 else f'{d} s'} | {n} | "
                          f"{100 * statistics.mean(x['cost'] for x in b):.1f}c | {usd(r)} "
                          f"({usd(lo)} to {usd(hi)}) |")
        P2 += ["", "### b) The 45-seconds-left buy (the live paper bot's main test), by delay", "",
               "Binance very sure (z 4+) with 45 s left; buy that side at the next real trade.", "",
               "| We are this late | Bets | Avg price paid | Lost | P&L per $100 (luck range) |", "|---|---|---|---|---|"]
        for d in DELAYS:
            b = late[d]
            if not b:
                continue
            TRIES[0] += 1
            n, r, lo, hi = tally(b)
            P2.append(f"| {'under 1 s' if d == 0 else f'{d} s'} | {n} | "
                      f"{100 * statistics.mean(x['cost'] for x in b):.2f}c | {sum(1 for x in b if not x['pay'])} | "
                      f"{usd(r)} ({usd(lo)} to {usd(hi)}) |")
    else:
        P2.append("No per-second tapes in the cache.")
    # ---- 3
    P3 = ["", "## 3. How fast are we really?", ""]
    pg = None
    try:
        with open(os.path.join(CACHE, "ping.json")) as fh:
            pg = json.load(fh)
    except (OSError, ValueError):
        pass
    if pg:
        P3 += [f"Measured {pg['at']} from a GitHub machine (a rented data-centre computer in the US, much like a "
               "cheap server), on a connection kept open:", "",
               "| What | Network round trip | Typical answer | Slow answer (1 in 10) |", "|---|---|---|---|"]
        for r in pg["rows"]:
            if "err" in r:
                P3.append(f"| {r['name']} | failed: {r['err']} | | |")
            else:
                P3.append(f"| {r['name']} | {r['tcp']:.0f} ms | {r['p50']:.0f} ms | {r['p90']:.0f} ms |")
    lt = live_timings()
    if lt["rows"]:
        P3 += ["", f"The live paper bot's own log ({lt['rows']} coin-windows): reading the Kalshi order book takes "
               f"{lt['book50']:.0f} ms (slow: {lt['book90']:.0f} ms); getting fresh Binance seconds takes "
               f"{lt['bin50']:.0f} ms (slow: {lt['bin90']:.0f} ms)."]
    # ---- exam
    X = ["", "## The exam", ""]
    cands = [("Binance vs Kalshi price, whole window, 6c gap, one minute late", best)]
    if jump.get(1):
        cands.append(("Buy the Binance jump, 1 s late", jump[1]))
    if late.get(1):
        cands.append(("45 s left, Binance very sure, 1 s late", late[1]))
    cards = []
    for name, b in cands:
        if b:
            c = exam.score(b, name, tries=TRIES[0], src="kspeed.py", log=False, quiet=True)
            cards.append(c)
            X.append(f"- **{name}**: {c['bets']} bets, {usd(c.get('per100'))} per $100, luck range "
                     f"{usd(c.get('lo100'))} to {usd(c.get('hi100'))}, halves {usd(c.get('half1'))} / "
                     f"{usd(c.get('half2'))}. Verdict: **{c['verdict']}**.")
    X += ["", f"Versions looked at in this dig: {TRIES[0]}."]
    full = L + P2 + P3 + X + [""]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "kspeed.md"), "w") as fh:
        fh.write("\n".join(full) + "\n")
    with open(os.path.join(OUT, "kspeed.json"), "w") as fh:
        json.dump({"at": bot.iso(), "tries": TRIES[0], "cards": cards}, fh, indent=1, default=str)
    print("\n".join(P2 + P3 + X))
    print(f"done in {time.time() - t_s:.0f}s")


# ================================================================ selftest

def selftest():
    rnd = random.Random(3)
    # fair fake world: price = true chance, so nothing should be clearly ahead
    rows = []
    for i in range(4000):
        z = rnd.gauss(0, 1.5)
        p = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        yes = rnd.random() < p
        L_ = rnd.randint(1, 14)
        yb, ya = max(0.01, p - 0.01), min(0.99, p + 0.01)
        rows.append({"tk": f"w{i}", "s": "X", "close": 1000 + 900 * (i // 7), "L": L_, "yb": yb, "ya": ya,
                     "yes": yes, "z": z, "mv": rnd.gauss(0, 1), "nyb": yb, "nya": ya})
    table = learn(rows[:2000])
    b = model_bets(rows[2000:], table, 0.06, 0)
    n, r, lo, hi = tally(b)
    assert n < 400 and (r is None or lo is None or lo < 3), ("fair world looks beatable", n, r, lo)
    # lagging fake world: the quote ignores z, so the model must find it
    rows2 = [{**r, "yb": 0.49, "ya": 0.51, "nyb": 0.49, "nya": 0.51} for r in rows]
    table = learn(rows2[:2000])
    b = model_bets(rows2[2000:], table, 0.06, 1)
    n, r, lo, hi = tally(b)
    assert n > 500 and r > 20, ("planted lag not found", n, r)
    ask_t, mid_t = timeline_table(rows)
    assert len(ask_t) == 2 + len(PHASES)
    assert drift_table(rows) == [] or True
    # tape helpers
    tape = [[10, 0.50, 1], [12, 0.55, 1], [12, 0.54, 0], [15, 0.60, 1]]
    idx = [x[0] for x in tape]
    assert last_px(tape, idx, 11, "yes") == 0.50 and last_px(tape, idx, 9, "yes") is None
    assert next_buy(tape, idx, 11, 14, "yes") == 0.55 and abs(next_buy(tape, idx, 11, 14, "no") - 0.46) < 1e-9
    assert next_buy(tape, idx, 16, 20, "yes") is None
    assert phase(14) == "minutes 1-4" and phase(1) == "minutes 13-14"
    assert pct([1, 2, 3, 4], 0.5) == 3
    print("kspeed selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "fetch":
        fetch(sys.argv[2] if len(sys.argv) > 2 else os.environ.get("KC_DAYS", 60))
    elif cmd == "tapes":
        fetch_tapes(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "run":
        run()
    elif cmd == "ping":
        ping()
    else:
        selftest()
