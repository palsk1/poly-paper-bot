#!/usr/bin/env python3
"""Live paper test of the "last 45 seconds" idea on Kalshi 15-minute crypto (2026-11-10, Jan: "build it so we'll
know for sure").

PAPER ONLY. Reads public data and never places an order.

The backtest (kfast.py, backtest/kfast.md) found one small lead: with 45 seconds left, the settlement average is
three-quarters known, so buying the side Binance says is very safe made about +$0.40 per $100. It could not
answer how many contracts really fill, or how fast a bot sees the book. This bot answers both with live data:

  - It wakes up 60, 45 and 30 seconds before every 15-minute close and, for all 7 coins at once, reads Binance's
    1-second prices and the Kalshi order book.
  - It decides like the backtest (same z formula as kfast.model_window). Then it reads the book a second time and
    buys at that book's real asks, for 10 and for 100 contracts. That copies the delay a real order would have.
  - Maker bids (99.5c / 99.8c) count the contracts already waiting at our price and only fill from real trades
    after them. If our bid would cross the ask, it's a taker buy at the ask (with the fee).
  - After the close it reads Kalshi's result and the trade tape, and writes one line per coin and window.

The pre-registered tests (fixed 2026-11-10, before any live data) are MAIN below. The others are there to
compare. The bar is the repo's proof rule (bot.proof): the 90% upper bound on the loss rate has to sit below
what one bet earns per contract.

Runs in GitHub Actions (`kfastlive.yml`, ~5h40m a run, the next run queued, like the recorder). Saves to
state/kfast_live/ (days/YYYY-MM-DD.jsonl, pending.json, report.md) and pushes every hour.

    python3 kfastlive.py loop [minutes]   # watch and paper-trade (default 340)
    python3 kfastlive.py once             # one snapshot of every coin right now, no trades (connectivity check)
    python3 kfastlive.py report           # rewrite state/kfast_live/report.md
    python3 kfastlive.py selftest         # offline
"""
import datetime as dt
import glob
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

SERIES = dict(bot.KMAKER_SPOT)
BIN = "https://data-api.binance.vision/api/v3/klines"
DIR = os.path.join(bot.ROOT, "state", "kfast_live")
SNAP_L = (60, 45, 30)
SIZES = (10, 100)
MAX_PRICE = 0.999
EPS = 1e-9
UTC = dt.timezone.utc

# kind: "take" = buy at the asks of the second book; "bid" = resting maker bid at a fixed price; "fav" = control,
# buy the side with the higher price at 45 s, no Binance model.
VARIANTS = {
    "take45_z4": {"L": 45, "kind": "take", "zmin": 4.0, "main": True},
    "take45_z6": {"L": 45, "kind": "take", "zmin": 6.0, "main": True},
    "bid995_45_z4": {"L": 45, "kind": "bid", "price": 0.995, "zmin": 4.0, "main": True},
    "bid998_45_z2": {"L": 45, "kind": "bid", "price": 0.998, "zmin": 2.0, "main": True},
    "take60_z4": {"L": 60, "kind": "take", "zmin": 4.0},
    "take30_z4": {"L": 30, "kind": "take", "zmin": 4.0},
    "fav45": {"L": 45, "kind": "fav"},
}
LABEL = {
    "take45_z4": "Buy now, 45 s left, Binance very sure (z 4+)",
    "take45_z6": "Buy now, 45 s left, Binance extremely sure (z 6+)",
    "bid995_45_z4": "Wait at 99.5c, 45 s left (z 4+)",
    "bid998_45_z2": "Wait at 99.8c, 45 s left (z 2+)",
    "take60_z4": "Buy now, 60 s left (z 4+)",
    "take30_z4": "Buy now, 30 s left (z 4+)",
    "fav45": "Control: buy the favourite at 45 s, no Binance",
}


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def rjson(p, default):
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def wjson(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as fh:
        json.dump(obj, fh, separators=(",", ":"))
    os.replace(p + ".tmp", p)


# ================================================================ data

def timed(fn, *a):
    t0 = time.time()
    try:
        return fn(*a), round((time.time() - t0) * 1000)
    except Exception as e:
        print(f"  {fn.__name__} failed: {e}")
        return None, round((time.time() - t0) * 1000)


def spot_seconds(sym, limit=1000, start=None):
    """{second: price}: price known at second t = close of the 1-second kline that opened at t-1 (as kfast.Spot)."""
    p = {"symbol": sym, "interval": "1s", "limit": limit}
    if start is not None:
        p["startTime"] = int(start * 1000)
    rows = bot.http_json(BIN, p, retries=2)
    return {int(r[0]) // 1000 + 1: float(r[4]) for r in rows}


def book(ticker):
    return bot.kalshi_book_sides(ticker)


def window_market(series, close):
    for m in bot.kmaker_open_markets(series):
        c = bot.parse_iso(m.get("close_time"))
        if c and abs(c.timestamp() - close) < 2:
            return {"tk": m.get("ticker"), "strike": bot.fnum(m.get("floor_strike"), None)}
    return None


# ================================================================ model (same formula as kfast.model_window)

def live_z(px, open_t, close, strike, t_dec):
    """(z_yes, info) from per-second prices up to the decision. z_yes > 0: Binance favours YES."""
    if not strike:
        return None, "no strike"
    pre = [px[s] for s in range(open_t - 59, open_t + 1) if s in px]
    if len(pre) < 50:
        return None, "no pre-open prices"
    basis = strike - sum(pre) / len(pre)
    t = max((s for s in px if s <= t_dec), default=None)
    if t is None or t_dec - t > 3:
        return None, "stale spot"
    # carry the last price forward over gaps, like kfast.Spot.run
    seq, last = {}, None
    for s in range(t - 360, t + 1):
        last = px.get(s, last)
        seq[s] = last
    d2 = [(seq[s] - seq[s - 1]) ** 2 for s in range(t - 299, t + 1) if seq.get(s) is not None and seq.get(s - 1) is not None]
    if len(d2) < 200:
        return None, "thin spot"
    sig2 = sum(d2) / len(d2)
    S, L = seq[t], close - t
    if L >= 60:
        mean, var = S, sig2 * (L - 60 + 20.5)
    else:
        known = [seq[s] for s in range(close - 59, t + 1)]
        if any(v is None for v in known):
            return None, "gap in the last minute"
        mean = (sum(known) + L * S) / 60
        var = sig2 * L * (L + 1) * (2 * L + 1) / 6 / 3600
    sd = math.sqrt(var) if var > 0 else 1e-12
    return (mean + basis - strike) / sd, {"basis": round(basis, 6), "spot": S, "spot_age": t_dec - t, "L": L}


# ================================================================ paper fills

def side_asks(bk, side):
    """Asks for `side` [(price, size)] cheapest first: buying YES = selling to the best NO bids."""
    other = "no" if side == "yes" else "yes"
    return sorted(((round(1 - p, 4), sz) for p, sz in bk.get(other, [])), key=lambda r: r[0])


def fee(n, avg):
    return math.ceil(0.07 * n * avg * (1 - avg) * 100 - 1e-9) / 100 if n > 0 else 0.0


def take(bk, side, n, cap=MAX_PRICE):
    """Walk the asks up to `cap` for n contracts -> {filled, avg, fee}."""
    got, cost = 0.0, 0.0
    for p, sz in side_asks(bk, side):
        if p > cap + EPS or got >= n:
            break
        q = min(sz, n - got)
        got, cost = got + q, cost + q * p
    if got <= 0:
        return {"filled": 0, "avg": None, "fee": 0.0}
    avg = cost / got
    return {"filled": round(got, 2), "avg": round(avg, 5), "fee": fee(got, avg)}


def place_bid(bk, side, price, n):
    """A resting bid at `price`. If it crosses the ask it fills there as a taker; else it waits behind the queue."""
    asks = side_asks(bk, side)
    if asks and asks[0][0] <= price + EPS:
        return {"crossed": True, **take(bk, side, n, cap=price)}
    queue = sum(sz for p, sz in bk.get(side, []) if abs(p - price) < 1e-6)
    return {"crossed": False, "queue": round(queue, 2)}


def tape_fill(trades, side, price, queue, t_place, n):
    """Contracts a resting bid gets from the real tape after t_place (same rule as bot.kmaker_fill)."""
    o = {"placed": iso(t_place), "side": side, "price": price, "queue": queue, "shares": n}
    filled, through = bot.kmaker_fill(o, trades, n)
    return round(filled, 2), through


# ================================================================ one window

def snapshot(w, L):
    """At L seconds left, for one coin: Binance z, book, decisions, second book, paper orders."""
    close, s = w["close"], w["series"]
    t_dec = int(time.time())
    px, bin_ms = timed(spot_seconds, SERIES[s], 330)   # 5.5 minutes: volatility + the last minute
    if px is not None:
        if "pre" not in w:   # the minute before the open, read once per window
            got, _ = timed(spot_seconds, SERIES[s], 62, close - 961)
            w["pre"] = {str(k): v for k, v in (got or {}).items()}
        px.update({int(k): v for k, v in w["pre"].items()})
    bk1, b1_ms = timed(book, w["tk"])
    z, info = live_z(px or {}, close - 900, close, w["strike"], t_dec) if px else (None, "no spot")
    snap = {"t": iso(time.time()), "bin_ms": bin_ms, "book_ms": b1_ms,
            "z": None if z is None else round(z, 3), "info": info}
    if bk1 and bk1.get("yes") and bk1.get("no"):
        snap["yb"], snap["ya"] = bk1["yes"][0][0], round(1 - bk1["no"][0][0], 4)
    todo = [k for k, v in VARIANTS.items() if v["L"] == L]
    want = []
    for k in todo:
        v = VARIANTS[k]
        if v["kind"] == "fav":
            if "yb" in snap and 0 < snap["yb"] < snap["ya"] < 1:
                side = "yes" if (snap["yb"] + snap["ya"]) / 2 >= 0.5 else "no"
                want.append((k, side))
        elif z is not None and abs(z) >= v["zmin"]:
            want.append((k, "yes" if z > 0 else "no"))
    if not want:
        w["snaps"][str(L)] = snap
        return
    bk2, b2_ms = timed(book, w["tk"])     # the book our order would really meet
    snap["book2_ms"] = b2_ms
    t_place = time.time()
    for k, side in want:
        v = VARIANTS[k]
        bet = {"side": side, "z": snap["z"], "t": iso(t_place)}
        if not bk2:
            bet["error"] = "no book"
        elif v["kind"] in ("take", "fav"):
            for n in SIZES:
                bet[str(n)] = take(bk2, side, n)
        else:
            for n in SIZES:
                bet[str(n)] = place_bid(bk2, side, v["price"], n)
            bet["price"] = v["price"]
        w["bets"][k] = bet
    w["snaps"][str(L)] = snap


def settle(w):
    """Fill the resting bids from the tape, score every bet. True when done."""
    close = w["close"]
    bot._kalshi_cache.pop(w["tk"], None)      # the cache would keep an old "no result yet"
    m = bot.kalshi_market(w["tk"])
    res = str((m or {}).get("result") or "").lower()
    if res not in ("yes", "no"):
        if time.time() - close > 6 * 3600:
            w["result"] = "none"
            return True
        return False
    w["result"] = res
    # Binance's own guess of the result, to count how often it disagrees with Kalshi (BRTI)
    try:
        px = spot_seconds(SERIES[w["series"]], 130, start=close - 961)
        px.update(spot_seconds(SERIES[w["series"]], 70, start=close - 62))
        pre = [px[s] for s in range(close - 959, close - 899) if s in px]
        fin = [px[s] for s in range(close - 59, close + 1) if s in px]
        if len(pre) >= 50 and len(fin) >= 50 and w.get("strike"):
            w["bin_yes"] = (sum(fin) / len(fin)) + (w["strike"] - sum(pre) / len(pre)) >= w["strike"]
    except Exception as e:
        print(f"  binance check failed for {w['tk']}: {e}")
    trades = None
    for k, bet in w["bets"].items():
        if "error" in bet:
            continue
        pay = 1.0 if res == bet["side"] else 0.0
        bet["won"] = pay > 0
        for n in SIZES:
            f = bet[str(n)]
            if VARIANTS[k]["kind"] == "bid" and not f.get("crossed"):
                if trades is None:
                    t0 = min(bot.parse_iso(b["t"]).timestamp() for b in w["bets"].values())
                    try:
                        trades, complete = bot.kalshi_trades(w["tk"], t0 - 1, close)
                        w["tape_complete"] = complete
                    except Exception as e:
                        print(f"  trades failed for {w['tk']}: {e}")
                        return False
                got, through = tape_fill(trades, bet["side"], bet["price"], f["queue"],
                                         bot.parse_iso(bet["t"]).timestamp(), n)
                f.update({"filled": got, "avg": bet["price"] if got else None, "fee": 0.0, "through": through})
            if f.get("filled"):
                f["pnl"] = round(f["filled"] * (pay - f["avg"]) - f["fee"], 4)
    return True


# ================================================================ loop

def save_day(w):
    day = dt.datetime.fromtimestamp(w["close"], UTC).date().isoformat()
    p = os.path.join(DIR, "days", f"{day}.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as fh:
        fh.write(json.dumps(w, separators=(",", ":")) + "\n")


def git_save():
    report()
    if os.environ.get("KFL_NOSAVE"):
        print("KFL_NOSAVE set: not pushing")
        return
    cmd = ("git add state/kfast_live && (git diff --cached --quiet || (git commit -q -m \"kfastlive: $(date -u +%Y-%m-%dT%H:%MZ)\" "
           "&& for i in 1 2 3 4; do git pull -q --rebase -X theirs origin main && git push -q && exit 0; "
           "git rebase --abort 2>/dev/null; sleep $((i*10)); done; exit 1))")
    r = subprocess.run(["bash", "-c", cmd], cwd=bot.ROOT)
    print(f"saved (git exit {r.returncode})")


def settle_pending(pending):
    left = []
    for w in pending:
        if time.time() < w["close"] + 75:
            left.append(w)
            continue
        try:
            done = settle(w)
        except Exception as e:
            print(f"  settle failed for {w['tk']}: {e}")
            done = False
        if done:
            w.pop("pre", None)
            save_day(w)
            bets = ", ".join(f"{k} {b['side']} {'won' if b.get('won') else 'LOST'}" for k, b in w["bets"].items() if "won" in b)
            print(f"settled {w['tk']}: {w['result']}" + (f" ({bets})" if bets else ""))
        else:
            left.append(w)
    return left


def sleep_until(t):
    while True:
        d = t - time.time()
        if d <= 0:
            return
        time.sleep(min(d, 5))


def loop(minutes=340):
    end = time.time() + float(minutes) * 60
    pp = os.path.join(DIR, "pending.json")
    pending = rjson(pp, [])
    last_save = time.time()
    while time.time() < end - 120:
        close = (int(time.time()) // 900 + 1) * 900
        if close - time.time() < SNAP_L[0] + 20:
            close += 900
        if close > end:
            break
        sleep_until(close - SNAP_L[0] - 40)
        with ThreadPoolExecutor(len(SERIES)) as ex:
            mk = dict(zip(SERIES, ex.map(lambda s: window_market(s, close), SERIES)))
        ws = [{"series": s, "close": close, "tk": m["tk"], "strike": m["strike"], "snaps": {}, "bets": {}}
              for s, m in mk.items() if m and m["tk"]]
        def pre(w):
            got, _ = timed(spot_seconds, SERIES[w["series"]], 62, close - 961)
            if got:
                w["pre"] = {str(k): v for k, v in got.items()}
        with ThreadPoolExecutor(len(ws) or 1) as ex:
            list(ex.map(pre, ws))
        print(f"{iso(close)}: {len(ws)} coins")
        for L in SNAP_L:
            sleep_until(close - L)
            with ThreadPoolExecutor(len(ws) or 1) as ex:
                list(ex.map(lambda w: snapshot(w, L), ws))
        for w in ws:
            if w["bets"]:
                print(f"  {w['series']}: " + ", ".join(f"{k} {b['side']}" for k, b in w["bets"].items()))
        pending += ws
        wjson(pp, pending)
        sleep_until(close + 80)
        pending = settle_pending(pending)
        wjson(pp, pending)
        if time.time() - last_save > 3600:
            git_save()
            last_save = time.time()
    pending = settle_pending(pending)
    wjson(pp, pending)
    git_save()


def once():
    close = (int(time.time()) // 900 + 1) * 900
    for s in SERIES:
        m = window_market(s, close)
        if not m:
            print(f"{s}: no market for {iso(close)}")
            continue
        w = {"series": s, "close": close, "tk": m["tk"], "strike": m["strike"], "snaps": {}, "bets": {}}
        px, ms = timed(spot_seconds, SERIES[s])
        z, info = live_z(px or {}, close - 900, close, m["strike"], int(time.time()))
        bk, bms = timed(book, m["tk"])
        depth = {sd: round(sum(sz for _, sz in bk.get(sd, [])), 0) for sd in ("yes", "no")} if bk else None
        print(f"{s} {m['tk']} strike {m['strike']} | binance {len(px or {})} s in {ms} ms, z {z} {info} | "
              f"book {bms} ms, top yes {bk and bk['yes'][:2]}, no {bk and bk['no'][:2]}, depth {depth}")


# ================================================================ report

def rows():
    out = []
    for p in sorted(glob.glob(os.path.join(DIR, "days", "*.jsonl"))):
        with open(p) as fh:
            out += [json.loads(x) for x in fh if x.strip()]
    return out


def score(ws, k, n):
    bets = [w["bets"][k] for w in ws if k in w["bets"] and "won" in w["bets"][k]]
    fills = [b[str(n)] for b in bets if b[str(n)].get("filled")]
    paired = [(b, b[str(n)]) for b in bets if b[str(n)].get("filled")]
    stake = sum(f["filled"] * f["avg"] + f["fee"] for f in fills)
    pnl = sum(f["pnl"] for f in fills)
    lost = sum(1 for b, f in paired if not b["won"])
    contracts = sum(f["filled"] for f in fills)
    full = sum(1 for f in fills if f["filled"] >= n - EPS)
    edge = (sum(f["filled"] * (1 - f["avg"]) - f["fee"] for f in fills) / contracts) if contracts else None
    return {"signals": len(bets), "fills": len(fills), "full": full, "lost": lost, "stake": stake, "pnl": pnl,
            "contracts": contracts, "edge": edge,
            "avg": (sum(f["filled"] * f["avg"] for f in fills) / contracts) if contracts else None}


def report():
    ws = [w for w in rows() if w.get("result") in ("yes", "no")]
    if not ws:
        txt = "# Fast Kalshi paper bot (last 45 seconds)\n\nNo finished windows yet.\n"
    else:
        t0, t1 = min(w["close"] for w in ws), max(w["close"] for w in ws)
        chk = [w for w in ws if "bin_yes" in w]
        miss = sum(1 for w in chk if w["bin_yes"] != (w["result"] == "yes"))
        lat = sorted(s.get("book_ms", 0) for w in ws for s in w["snaps"].values())
        L = ["# Fast Kalshi paper bot (last 45 seconds)", "",
             f"Live paper test, `kfastlive.py`. {len(ws)} coin-windows from {iso(t0)[:16]} to {iso(t1)[:16]} UTC "
             f"({len({w['close'] for w in ws})} closes watched). Paper only, nothing is really bought.", "",
             f"Binance guessed Kalshi's result wrong on **{miss} of {len(chk)}** windows. "
             f"Reading the Kalshi book takes about {lat[len(lat) // 2] if lat else '?'} ms "
             f"(slowest 1 in 10: {lat[int(len(lat) * 0.9)] if lat else '?'} ms).", "",
             "P&L is after Kalshi's fee. \"Full\" = how often the whole order got filled. The proof line uses the "
             "repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet "
             "earns, with 90% confidence.", ""]
        for n in SIZES:
            L += [f"## Orders of {n} contracts", "",
                  "| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for k in VARIANTS:
                s = score(ws, k, n)
                if s["fills"]:
                    pr = bot.proof(s["fills"], s["lost"], max(s["edge"], 1e-4), s["pnl"], "bets", "losses")
                    proof_txt = "**PROVEN**" if pr["proven"] else f"needs ~{pr['more_needed']} more bets with no loss"
                    per100 = 100 * s["pnl"] / s["stake"] if s["stake"] else 0
                    L.append(f"| {LABEL[k]}{' (main)' if VARIANTS[k].get('main') else ''} | {s['signals']} | "
                             f"{s['fills']} | {s['full']} | {s['lost']} | {s['avg'] * 100:.2f}c | "
                             f"${s['pnl']:+.2f} | ${per100:+.2f} | {proof_txt} |")
                else:
                    L.append(f"| {LABEL[k]}{' (main)' if VARIANTS[k].get('main') else ''} | {s['signals']} | 0 | "
                             f"0 | 0 | - | $0.00 | - | no bets yet |")
            L.append("")
        txt = "\n".join(L) + "\n"
    os.makedirs(DIR, exist_ok=True)
    with open(os.path.join(DIR, "report.md"), "w") as fh:
        fh.write(txt)
    return txt


# ================================================================ selftest

def selftest():
    close, open_t, k = 1_800_000_900, 1_800_000_000, 100.0
    px = {s: 100.0 + 0.01 * math.sin(s) for s in range(close - 1000, close - 44)}
    for s in range(close - 400, close - 44):
        px[s] += 0.5                            # spot well above the strike in the last minutes
    z, info = live_z(px, open_t, close, k, close - 45)
    assert z is not None and z > 6, (z, info)
    px2 = {s: v - (1.0 if s >= close - 400 else 0) for s, v in px.items()}
    z2, _ = live_z(px2, open_t, close, k, close - 45)
    assert z2 < -6, z2
    assert live_z(px, open_t, close, k, close - 30)[0] is None    # stale
    bk = {"yes": [(0.993, 40), (0.99, 500)], "no": [(0.004, 30), (0.002, 1000)]}
    t = take(bk, "yes", 10)
    assert t["filled"] == 10 and abs(t["avg"] - 0.996) < 1e-9 and t["fee"] == 0.01, t
    t = take(bk, "yes", 100)
    assert t["filled"] == 100 and abs(t["avg"] - (30 * 0.996 + 70 * 0.998) / 100) < 1e-9, t
    assert take(bk, "yes", 100, cap=0.995)["filled"] == 0
    b = place_bid(bk, "yes", 0.995, 10)
    assert b == {"crossed": False, "queue": 0}, b
    b = place_bid(bk, "yes", 0.993, 10)
    assert b["queue"] == 40
    b = place_bid(bk, "yes", 0.998, 100)
    assert b["crossed"] and b["filled"] == 100, b
    trades = [{"created_time": iso(close - 20), "yes_price_dollars": "0.9950", "taker_side": "no", "count_fp": "15"},
              {"created_time": iso(close - 10), "yes_price_dollars": "0.9950", "taker_side": "no", "count_fp": "30"}]
    assert tape_fill(trades, "yes", 0.995, 40, close - 44, 10) == (5.0, False)
    assert tape_fill(trades, "yes", 0.995, 0, close - 44, 100) == (45.0, False)
    print("kfastlive selftest OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "loop":
        loop(*(sys.argv[2:3]))
    elif cmd == "once":
        once()
    elif cmd == "report":
        print(report())
    else:
        selftest()
