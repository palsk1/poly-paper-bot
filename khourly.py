#!/usr/bin/env python3
"""Kalshi's hourly and daily crypto rounds: the kc_maker_safe_usd bid replayed there (23 Nov 2026, Jan's ask).

PAPER ONLY. Reads public history and never trades.

    python3 khourly.py scan        # probe khr_scan: which crypto series exist on Kalshi (how often, fees, size), what one
                                   # hourly round looks like, and which hourly / daily crypto bets Polymarket lists
"""
import collections
import datetime as dt
import json
import math
import os
import re
import sys
import time

import bot
import kcrypto as kc
import yesno

UTC = dt.timezone.utc
CACHE = os.path.join(bot.ROOT, "bt_cache", "khr")
OUT = os.path.join(bot.ROOT, "backtest")
kget = yesno.kget


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M")


_LOG = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    _LOG.append(line)


def save_log(name):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


def vol_of(m):
    return bot.fnum(m.get("volume_fp") or m.get("volume"), 0)


def scan():
    """Everything lands in bt_cache/khr/scan.txt (price store), so the workspace can read it without the run log."""
    ser = kget("/series", {"category": "Crypto"}).get("series") or []
    say("Kalshi Crypto series:", len(ser), collections.Counter(s.get("frequency") for s in ser).most_common())
    now = int(time.time())
    keep = {}
    for s in sorted(ser, key=lambda s: s.get("ticker") or ""):
        tk = s.get("ticker")
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000,
                                   "min_close_ts": now - 2 * 86400}).get("markets") or []
        except Exception as e:
            say("  failed", tk, str(e)[:80])
            continue
        if not ms:
            continue
        ev = collections.defaultdict(list)
        for m in ms:
            ev[m.get("event_ticker")].append(m)
        life = sorted((kc.tsec(m.get("close_time")) or 0) - (kc.tsec(m.get("open_time")) or 0) for m in ms)
        keep[tk] = ev
        say(f"  {tk:18s} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | 2 days: {len(ev)} rounds, "
            f"{len(ms)} markets{'+' if len(ms) == 1000 else ''}, {sum(map(vol_of, ms)):,.0f} contracts | open for "
            f"{life[len(life) // 2] / 3600:.1f} h (middle) | {str(s.get('title'))[:60]}")
    for tk, ev in sorted(keep.items(), key=lambda kv: -sum(vol_of(m) for mm in kv[1].values() for m in mm)):
        if tk.endswith("15M"):
            continue
        byh = collections.defaultdict(float)
        for e, mm in ev.items():
            c = kc.tsec(mm[0].get("close_time")) or 0
            byh[dt.datetime.fromtimestamp(c, UTC).hour] += sum(map(vol_of, mm))
        say(f"\n== {tk}: contracts by close hour (UTC): {' '.join(f'{h}:{round(v)}' for h, v in sorted(byh.items()))}")
        ek = sorted(ev, key=lambda e: -sum(map(vol_of, ev[e])))
        for e in ek[:1] + ek[len(ek) // 2:len(ek) // 2 + 1]:
            mm = sorted(ev[e], key=lambda m: bot.fnum(m.get("floor_strike"), 0) or bot.fnum(m.get("cap_strike"), 0))
            m0 = mm[len(mm) // 2]
            say(f"  round {e}: {len(mm)} markets, open {m0.get('open_time')} close {m0.get('close_time')} settle {m0.get('expiration_value')} "
                f"| tick {json.dumps(m0.get('price_ranges'))} | rule: {str(m0.get('rules_primary'))[:230]}")
            for m in [m for m in mm if vol_of(m) > 0][:60]:
                say(f"    {m.get('ticker'):34s} {m.get('strike_type')} {m.get('floor_strike')} {m.get('cap_strike')} vol {vol_of(m):,.0f} {m.get('result')}")
        try:
            d = (kget(f"/live_data/events/{ek[0]}").get("live_data") or {}).get("details") or {}
            ts = d.get("timeseries") or []
            say(f"  live settle number for {ek[0]}: {len(ts)} points, first {ts[:1]}, last {ts[-1:]}")
        except Exception as e:
            say("  live settle number failed", str(e)[:100])
    try:
        say("historical cutoff", json.dumps(kget("/historical/cutoff")))
    except Exception as e:
        say("cutoff failed", str(e)[:80])
    pm_scan()
    save_log("scan.txt")


def get_trades(ticker, limit=1000):
    return kget("/markets/trades", {"ticker": ticker, "limit": limit})


def pm_scan():
    """Polymarket: does it list hourly / 4-hour / daily crypto rounds? Looked up by the slug of a recent round."""
    import habits
    G = habits.G
    now = dt.datetime.now(UTC)
    et = now - dt.timedelta(hours=5)
    h1 = (et - dt.timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    hh = f"{(h1.hour % 12) or 12}{'am' if h1.hour < 12 else 'pm'}"
    mon = h1.strftime("%B").lower()
    t4 = (int(time.time()) // 14400 - 2) * 14400
    t1 = (int(time.time()) // 3600 - 3) * 3600
    yday = et - dt.timedelta(days=1)
    names = {"bitcoin": "btc", "ethereum": "eth", "solana": "sol", "xrp": "xrp", "dogecoin": "doge", "hyperliquid": "hype", "bnb": "bnb"}
    slugs = []
    for long, short in names.items():
        slugs += [f"{long}-up-or-down-{mon}-{h1.day}-{hh}-et", f"{long}-up-or-down-{mon}-{h1.day}-{h1.year}-{hh}-et",
                  f"{short}-updown-4h-{t4}", f"{short}-updown-1h-{t1}", f"{short}-updown-15m-{t1}",
                  f"{long}-above-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}", f"{long}-above-on-{yday.strftime('%B').lower()}-{yday.day}",
                  f"{long}-price-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}",
                  f"{long}-up-or-down-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}", f"{long}-up-or-down-on-{yday.strftime('%B').lower()}-{yday.day}"]
    say("\nPolymarket, by slug:")
    for sl in slugs:
        try:
            r = bot.http_json(f"{G}/events", {"slug": sl})
        except Exception as e:
            say("  failed", sl, str(e)[:80])
            continue
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        if not rows:
            say(f"  none: {sl}")
            continue
        e = rows[0]
        mk = e.get("markets") or []
        m0 = mk[0] if mk else {}
        say(f"  FOUND {sl}: {len(mk)} markets, ${float(e.get('volume') or 0):,.0f} traded, start {str(m0.get('startDate'))[:16]} end {str(m0.get('endDate'))[:16]}, "
            f"fee {m0.get('feeType')} {json.dumps(m0.get('feeSchedule'))}, tick {m0.get('orderPriceMinTickSize')}, rewards min {m0.get('rewardsMinSize')} "
            f"spread {m0.get('rewardsMaxSpread')}, settles on {str(m0.get('resolutionSource'))[:70]} | {str(m0.get('description'))[:260]!r}")


# ================================================================ fetch (probe khr_fetch or khr_fetch_KXBTCD,KXETHD)
# The hourly "above / below" series and the Binance pair used for the cushion. The range series (KXBTC, KXETH, ...)
# trade 30 times less and are left out.
SERIES = {"KXBTCD": "BTCUSDT", "KXETHD": "ETHUSDT", "KXSOLD": "SOLUSDT", "KXXRPD": "XRPUSDT", "KXDOGED": "DOGEUSDT",
          "KXBNBD": "BNBUSDT", "KXHYPED": "HYPEUSDT"}
NEAR = 0.012        # keep markets whose line is within 1.2% of where the round ended
LOOK = 31           # minutes of candles kept before each close
SIG_MIN = (2, 3, 5)  # trade lists are downloaded for markets where the rule could bid at one of these minutes
DAYS = int(os.environ.get("KHR_DAYS", "61"))


def leader(row):
    """kcrypto.leader, but a book of 99c bid / $1.00 ask (or 0c / 1c) counts too: with 1c steps that is the usual
    look of a safe market here. Empty books (bid and ask more than 50c apart) have no leader."""
    yb, ya = row[0], row[1]
    if yb is None or ya is None or not (0 <= yb <= ya <= 1) or ya - yb > 0.5:
        return None
    return "yes" if (yb + ya) / 2 >= 0.5 else "no"


def sampled(close):
    """Every third round, shifting by a hour each day: the rounds whose 99c markets get their trade lists too."""
    return (close // 3600 + close // 86400) % 3 == 0


def p(series, kind):
    return os.path.join(CACHE, f"{kind}_{series}.json.gz")


def list_day(series, t0, t1):
    out, cur = [], None
    for _ in range(60):
        q = {"series_ticker": series, "status": "settled", "min_close_ts": t0, "max_close_ts": t1, "limit": 1000}
        if cur:
            q["cursor"] = cur
        res = kget("/markets", q)
        rows = res.get("markets") or []
        for m in rows:
            c, k, v = kc.tsec(m.get("close_time")), bot.fnum(m.get("floor_strike"), None), bot.fnum(m.get("expiration_value"), None)
            r = str(m.get("result") or "").lower()
            if not c or not k or not v or r not in ("yes", "no") or m.get("strike_type") != "greater":
                continue
            out.append({"t": m.get("ticker"), "ev": m.get("event_ticker"), "close": c, "open": kc.tsec(m.get("open_time")),
                        "strike": k, "settle": v, "res": r, "vol": vol_of(m)})
        cur = res.get("cursor")
        if not cur or not rows:
            break
    return out


def fetch(arg=None):
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(CACHE, exist_ok=True)
    cut = kc.hist_cutoff()
    t1 = int(time.time()) - 600
    t0 = max(cut + 3600, t1 - DAYS * 86400)
    names = [x for x in (arg.split(",") if arg else SERIES) if x in SERIES]
    for series in names:
        t_s = time.time()
        # 1. every settled market, slimmed; per round also how many contracts traded in all its markets
        old = kc.rjson(p(series, "markets"), {}) or {}
        ms, rounds = {m["t"]: m for m in old.get("m", [])}, dict(old.get("rounds", {}))
        done_to = old.get("to") if old.get("from") and old["from"] <= t0 + 86400 else t0
        days = [(a, min(a + 86400, t1)) for a in range(max(done_to, t0), t1, 86400)]
        with ThreadPoolExecutor(6) as ex:
            for got in ex.map(lambda d: list_day(series, d[0] + 1, d[1]), days):
                for m in got:
                    r = rounds.setdefault(m["ev"], {"close": m["close"], "open": m["open"], "settle": m["settle"], "vol": 0.0, "n": 0})
                    r["vol"] += m["vol"]
                    r["n"] += 1
                    r["open"] = min(r["open"] or m["open"], m["open"] or r["open"])
                    if m["vol"] > 0 and abs(m["strike"] - m["settle"]) / m["settle"] <= NEAR:
                        ms[m["t"]] = m
        kc.wjson(p(series, "markets"), {"m": list(ms.values()), "rounds": rounds, "to": t1, "from": t0})
        say(f"{series}: {len(rounds)} rounds, {len(ms)} markets kept near the line ({time.time() - t_s:.0f}s)")
        # 2. Kalshi's own settle number, minute marks of the 3 hours before each close
        idx = kc.rjson(p(series, "idx"), {}) or {}
        idx.setdefault("done", [])
        idx.setdefault("min", {})
        done = set(idx["done"])
        todo = sorted((e for e in rounds if e not in done), key=lambda e: rounds[e]["close"])

        def live(e):
            try:
                d = (kget(f"/live_data/events/{e}").get("live_data") or {}).get("details") or {}
                return e, d.get("timeseries") or []
            except Exception as ex_:
                return e, ex_
        bad = 0
        with ThreadPoolExecutor(4) as ex:
            for i, (e, ts) in enumerate(ex.map(live, todo)):
                if isinstance(ts, Exception) or not ts:
                    bad += 1
                    continue
                for q in ts:
                    t = int(q["t"]) // 1000
                    if t % 60 == 0 and q.get("v") is not None:
                        idx["min"][str(t)] = round(float(q["v"]), 8)
                idx["done"].append(e)
                if i and i % 400 == 0:
                    kc.wjson(p(series, "idx"), idx)
        kc.wjson(p(series, "idx"), idx)
        say(f"  settle number: {len(todo)} rounds asked, {bad} failed, {len(idx['min'])} minutes ({time.time() - t_s:.0f}s)")
        # 3. Binance one-minute prices
        sym = SERIES[series]
        spot = kc.fetch_spot(sym, t0 - 7200, t1, kc.rjson(p(series, "spot"), {}))
        kc.wjson(p(series, "spot"), spot)
        say(f"  Binance: {len(spot)} minutes ({time.time() - t_s:.0f}s)")
        # 4. one-minute candles of the last LOOK minutes, 90 markets a call
        cs = kc.rjson(p(series, "candles"), {}) or {}
        byc = collections.defaultdict(list)
        for m in ms.values():
            if m["t"] not in cs:
                byc[m["close"]].append(m)
        groups = [g[i:i + 90] for _, g in sorted(byc.items()) for i in range(0, len(g), 90)]

        def cand(g):
            c = g[0]["close"]
            try:
                res = kget("/markets/candlesticks", {"market_tickers": ",".join(m["t"] for m in g), "start_ts": c - LOOK * 60,
                                                     "end_ts": c, "period_interval": 1})
            except Exception as ex_:
                return g, ex_
            out = {}
            for r in res.get("markets") or []:
                out[r.get("market_ticker")] = [row for row in (kc.candle_row(x) for x in r.get("candlesticks") or []) if c - LOOK * 60 < row[0] <= c]
            return g, out
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for i, (g, out) in enumerate(ex.map(cand, groups)):
                if isinstance(out, Exception):
                    bad += 1
                    if bad < 4:
                        say("   candles failed:", str(out)[:160])
                    continue
                for m in g:
                    cs[m["t"]] = out.get(m["t"]) or []
                if i and i % 300 == 0:
                    kc.wjson(p(series, "candles"), cs)
                    print(f"   candles {i}/{len(groups)} ({time.time() - t_s:.0f}s)", flush=True)
        kc.wjson(p(series, "candles"), cs)
        say(f"  candles: {len(groups)} calls, {bad} failed, {sum(1 for v in cs.values() if v)} of {len(cs)} markets have some ({time.time() - t_s:.0f}s)")
        # 5. every trade of the last 6 minutes where the rule could bid
        tr = kc.rjson(p(series, "trades"), {}) or {}
        want = []
        for m in ms.values():
            if m["t"] in tr:
                continue
            c = {r[0]: r[1:] for r in cs.get(m["t"]) or []}
            kc.fix_cents(c)
            for mn in SIG_MIN:
                row = c.get(m["close"] - 60 * mn)
                side = leader(row) if row else None
                if not side:
                    continue
                bid, ask = kc.side_view(row, side)[:2]
                if bid >= 0.95 - 1e-9 and (ask < 1 - 1e-9 or (mn == 3 and sampled(m["close"]))):
                    want.append(m)
                    break

        def tape(m):
            out, cur = [], None
            try:
                for _ in range(30):
                    q = {"ticker": m["t"], "min_ts": m["close"] - 360, "max_ts": m["close"] + 5, "limit": 1000}
                    if cur:
                        q["cursor"] = cur
                    res = kget("/markets/trades", q)
                    rows = res.get("trades") or []
                    for x in rows:
                        d = bot.parse_iso(x.get("created_time"))
                        yp = bot.fnum(x.get("yes_price_dollars"), None)
                        if d and yp is not None:
                            out.append([round(d.timestamp(), 2), yp, bot.fnum(x.get("count_fp") or x.get("count"), 0), str(x.get("taker_side") or "")[:1]])
                    cur = res.get("cursor")
                    if not cur or not rows:
                        break
            except Exception as ex_:
                return m, ex_
            return m, sorted(out)
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for i, (m, out) in enumerate(ex.map(tape, want)):
                if isinstance(out, Exception):
                    bad += 1
                    if bad < 4:
                        say("   trades failed:", str(out)[:160])
                    continue
                tr[m["t"]] = out
                if i and i % 3000 == 0:
                    kc.wjson(p(series, "trades"), tr)
                    print(f"   trades {i}/{len(want)} ({time.time() - t_s:.0f}s)", flush=True)
        kc.wjson(p(series, "trades"), tr)
        say(f"  trade lists: {len(want)} asked, {bad} failed, {len(tr)} kept, {sum(len(v) for v in tr.values()):,} trades ({time.time() - t_s:.0f}s)")
    save_log(f"fetch_{'_'.join(names)[:60]}.txt")


# ================================================================ replay
# The rule, written down before the first result (23 Nov): exactly kc_maker_safe_usd, moved to the hourly rounds.
#   - with M minutes left (main case M = 3, as in the 15-minute history test), in every "above X" market of the round:
#     the leading side (middle price 50c+), best bid 95c+, bid one tick (1c here) above it, or join it when there is
#     no room under the ask. Hold to the result. Makers pay no fee on these series (fee_type quadratic, 23 Nov).
#   - cushion: Binance sits 2+ "typical moves until the close" on our side of the line (kcrypto.zscore), AND still
#     at least BAR (2.0 paper, 2.3 real bot since 23 Nov, 2.5) after moving Binance onto Kalshi's price scale. The
#     15-minute rule reads the Binance-vs-Kalshi gap at the window's start; an hourly round has no such start line,
#     so the gap is read at the last quarter hour from Kalshi's own number (the same moment, the same number).
#   - fills: "tape" = only contracts really sold into bids after our bid: everything sold BELOW our price, plus sales
#     AT our price when we were alone at a new price. Sales at a price we merely joined are not counted (the line in
#     front of us is unknown), so this is the careful end. "candle" = kcrypto.py's 'fair' model, for comparison.
BARS = (2.0, 2.3, 2.5)
SIZES = (4, 10, 20, 40)
EPS = 1e-9


def load(series):
    mk = kc.rjson(p(series, "markets"), {}) or {}
    cs = kc.rjson(p(series, "candles"), {}) or {}
    idx = {int(k): v for k, v in ((kc.rjson(p(series, "idx"), {}) or {}).get("min") or {}).items()}
    spot = kc.rjson(p(series, "spot"), {}) or {}
    tr = kc.rjson(p(series, "trades"), {}) or {}
    ws = []
    for m in mk.get("m", []):
        c = {r[0]: r[1:] for r in cs.get(m["t"]) or [] if r and r[0]}
        if not c:
            continue
        kc.fix_cents(c)
        ws.append({**m, "s": series, "c": c, "spot": spot})
    return {"series": series, "w": ws, "rounds": mk.get("rounds", {}), "idx": idx, "spot": spot, "tr": tr,
            "from": mk.get("from"), "to": mk.get("to")}


def gap_at(D, t):
    """Binance / Kalshi's number at the last quarter hour at or before t (None without data)."""
    t0 = t - t % 900
    a, b, k = D["spot"].get(str(t0)), D["spot"].get(str(t0 - 60)), D["idx"].get(t0)
    if not a or not k:
        return None
    return ((a + b) / 2 if b else a) / k


def tape_fill(tr, t_place, side, price, front):
    """Contracts sold into bids we would have been in front of, after t_place. [below our price, at our price]."""
    below = at = 0.0
    for ts, yp, n, taker in tr or []:
        if ts <= t_place:
            continue
        if taker != ("n" if side == "yes" else "y"):
            continue
        px = yp if side == "yes" else 1 - yp
        if px < price - EPS:
            below += n
        elif px <= price + EPS:
            at += n
    return below + (at if front else 0.0), at


def bets(D, minutes=3, level=0.95, tick=0.01):
    """One row per market where the rule could bid with `minutes` left; cushions and fills attached."""
    import kdocs
    out = []
    for w in D["w"]:
        t = w["close"] - 60 * minutes
        row = w["c"].get(t)
        side = leader(row) if row else None
        if not side:
            continue
        bid, ask, _, _ = kc.side_view(row, side)
        if bid < level - EPS:
            continue
        price = round(bid + tick, 4)
        front = price < ask - EPS
        if not front:
            price = bid
        z = kc.zscore(w, t, minutes, side)
        g = gap_at(D, t)
        zu = kc.zscore(dict(w, strike=w["strike"] * g), t, minutes, side) if g else None
        zk = kdocs.zk_minute(D["idx"], w, t, minutes, side)
        if z is None or zu is None:
            continue
        sold, at = tape_fill(D["tr"].get(w["t"]), t, side, price, front) if w["t"] in D["tr"] else (None, None)
        out.append({"tk": w["t"], "ev": w["ev"], "s": w["s"], "t": t, "close": w["close"], "side": side, "bid": bid, "ask": ask,
                    "price": price, "front": front, "z": z, "zu": zu, "zk": zk, "won": w["res"] == side, "sold": sold, "at": at,
                    "candle": kc.fill_after(w, t, side, price, front)[1], "m": minutes,
                    "long": (w["close"] - (w.get("open") or w["close"])) > 7200, "top": ask >= 1 - EPS,
                    "touch": kc.fill_after(w, t, side, price, front)[2]})
    return out


def keep(rows, bar, zmin=2.0):
    return [r for r in rows if r["z"] >= zmin and r["zu"] >= bar]


def nearest(rows):
    """One bet per round and coin: the passing market whose price is lowest (the one nearest the line)."""
    best = {}
    for r in rows:
        k = (r["ev"], r["s"])
        if k not in best or r["price"] < best[k]["price"]:
            best[k] = r
    return list(best.values())


def card(rows, usd=4, model="tape"):
    """Money numbers for bids of `usd` each. tape: contracts filled = what was really sold to us, at most our size."""
    n = lost = 0
    cost = pnl = 0.0
    full = 0
    out_by_round = collections.defaultdict(float)
    for r in rows:
        need = int(usd / r["price"] + EPS)
        if need < 1:
            continue
        if model == "tape":
            if r["sold"] is None:
                continue
            got = min(need, int(r["sold"]))
        else:
            got = need if r["candle"] else 0
        if got < 1:
            continue
        n += 1
        full += got >= need
        lost += not r["won"]
        cost += got * r["price"]
        pnl += got * ((1.0 if r["won"] else 0.0) - r["price"])
        out_by_round[r["close"]] += got * r["price"]
    o = sorted(out_by_round.values())
    return {"signals": len(rows), "bets": n, "full": full, "lost": lost, "cost": cost, "pnl": pnl,
            "per100": pnl / cost * 100 if cost else 0.0, "out_max": o[-1] if o else 0.0, "out_mid": o[len(o) // 2] if o else 0.0}


def money(x, d=2):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.{d}f}"


def exam_bets(rows, usd=4):
    out = []
    for r in rows:
        need = int(usd / r["price"] + EPS)
        got = min(need, int(r["sold"] or 0))
        if got >= 1:
            out.append({"cost": got * r["price"], "pay": got * 1.0 if r["won"] else 0.0, "t": r["t"], "ev": str(r["close"])})
    return out


def run(arg=None):
    import exam
    names = [s for s in SERIES if os.path.exists(p(s, "markets"))]
    Ds = {s: load(s) for s in names}
    Ds = {s: D for s, D in Ds.items() if D["rounds"]}
    names = list(Ds)
    days = max((D["to"] - D["from"]) / 86400 for D in Ds.values())
    say(f"Data: {', '.join(names)}; {iso(min(D['from'] for D in Ds.values()))} to {iso(max(D['to'] for D in Ds.values()))} UTC ({days:.0f} days)")
    for s, D in Ds.items():
        rv = sorted(r["vol"] for r in D["rounds"].values())
        lg = sum(1 for r in D["rounds"].values() if (r["close"] - (r["open"] or r["close"])) > 7200)
        say(f"  {s}: {len(D['rounds'])} rounds ({lg} open longer than 2 hours), contracts a round: middle {rv[len(rv) // 2]:,.0f}, "
            f"busiest {rv[-1]:,.0f}; {len(D['w'])} markets with candles, {len(D['tr'])} trade lists, {len(D['idx'])} minutes of Kalshi's number")
    ALL = {m: [r for D in Ds.values() for r in bets(D, m)] for m in (2, 3, 5)}
    B = {m: [r for r in ALL[m] if not r["top"]] for m in ALL}      # there is a seller under $1.00: bids of 95c to 98c
    T = [r for r in ALL[3] if r["top"]]                            # no seller under $1.00: nearly always a bid joined at 99c
    say("\n## A. All coins together: minutes left x cushion bar ($4 bids, tape fills)")
    say("| Min left | Bar | Signals | Bets filled | Filled in full | Lost | Per $100 | Profit | Bets a day | $ a day | Most $ out in one round |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    for m in (2, 3, 5):
        for bar in (None,) + BARS:
            rows = B[m] if bar is None else keep(B[m], bar)
            c = card(rows)
            say(f"| {m} | {'no check' if bar is None else bar} | {c['signals']} | {c['bets']} | {c['full']} | {c['lost']} | {money(c['per100'])} | {money(c['pnl'])} | "
                f"{c['bets'] / days:.1f} | {money(c['pnl'] / days)} | ${c['out_max']:.0f} |")
    say("\n## B. By coin, 3 minutes left ($4 bids, tape fills)")
    say("| Coin | Bar | Signals | Bets filled | Lost | Per $100 | Profit | Bets a day | $ a day |")
    say("|---|---|---|---|---|---|---|---|---|")
    for s in names:
        for bar in BARS:
            c = card([r for r in keep(B[3], bar) if r["s"] == s])
            say(f"| {s} | {bar} | {c['signals']} | {c['bets']} | {c['lost']} | {money(c['per100'])} | {money(c['pnl'])} | {c['bets'] / days:.1f} | {money(c['pnl'] / days)} |")
    say("\n## C. Bid size, 3 minutes left, all coins (tape fills: only what was really sold to us)")
    say("| Bar | Bid size | Bets with any fill | Filled in full | Lost | $ really bought | Per $100 | Profit | $ a day | Most $ out in one round | Usual $ out in a round |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    for bar in BARS:
        for usd in SIZES:
            c = card(keep(B[3], bar), usd)
            say(f"| {bar} | ${usd} | {c['bets']} | {c['full']} | {c['lost']} | ${c['cost']:,.0f} | {money(c['per100'])} | {money(c['pnl'])} | {money(c['pnl'] / days)} | "
                f"${c['out_max']:.0f} | ${c['out_mid']:.0f} |")
    say("\n## D. By our price, 3 minutes left, bar 2.3 ($4 bids)")
    say("| Our price | Signals | Front of the line | Bets filled (tape) | Lost | Per $100 | Profit | Candle-model bets | Candle per $100 |")
    say("|---|---|---|---|---|---|---|---|---|")
    for lo, hi in ((0.95, 0.96), (0.97, 0.97), (0.98, 0.98), (0.99, 0.99)):
        rows = [r for r in keep(B[3], 2.3) if lo - EPS <= r["price"] <= hi + EPS]
        c, c2 = card(rows), card(rows, model="candle")
        say(f"| {lo * 100:.0f}c{'' if lo == hi else f'-{hi * 100:.0f}c'} | {c['signals']} | {sum(r['front'] for r in rows)} | {c['bets']} | {c['lost']} | {money(c['per100'])} | {money(c['pnl'])} | "
            f"{c2['bets']} | {money(c2['per100'])} |")
    say("\n## E. Other ways to cut it, 3 minutes left ($4 bids, tape fills)")
    say("| Version | Signals | Bets filled | Lost | Per $100 | Profit | $ a day |")
    say("|---|---|---|---|---|---|---|")
    cuts = [("bar 2.3, candle fills (kcrypto 'fair' model)", keep(B[3], 2.3), "candle"),
            ("bar 2.3, one bet a round and coin (nearest the line)", nearest(keep(B[3], 2.3)), "tape"),
            ("bar 2.3, only prices under 99c", [r for r in keep(B[3], 2.3) if r["price"] < 0.985], "tape"),
            ("bar 2.3, only yes side", [r for r in keep(B[3], 2.3) if r["side"] == "yes"], "tape"),
            ("bar 2.3, only no side", [r for r in keep(B[3], 2.3) if r["side"] == "no"], "tape"),
            ("Binance check only, 2.0 (kc_maker_safe)", [r for r in B[3] if r["z"] >= 2], "tape"),
            ("Kalshi's own number 2.0 (kprice twin)", [r for r in B[3] if r["zk"] is not None and r["zk"] >= 2], "tape"),
            ("Kalshi's own number 3.0", [r for r in B[3] if r["zk"] is not None and r["zk"] >= 3], "tape"),
            ("bar 3.0", keep(B[3], 3.0), "tape"), ("bar 4.0", keep(B[3], 4.0), "tape"),
            ("bar 2.3, rounds open longer than 2 hours (the 'daily' ones)", [r for r in keep(B[3], 2.3) if r["long"]], "tape")]
    for label, rows, model in cuts:
        c = card(rows, model=model)
        say(f"| {label} | {c['signals']} | {c['bets']} | {c['lost']} | {money(c['per100'])} | {money(c['pnl'])} | {money(c['pnl'] / days)} |")
    say("\n## F. Every lost bet, 3 minutes left, bar 2.0 (tape fills)")
    say("| Round closes (UTC) | Market | Side | Our price | Cushion Binance | After the gap fix | On Kalshi's number | Sold to us |")
    say("|---|---|---|---|---|---|---|---|")
    for r in sorted(keep(B[3], 2.0), key=lambda r: r["t"]):
        if not r["won"] and r["sold"]:
            say(f"| {iso(r['close'])} | {r['tk']} | {r['side']} | {r['price'] * 100:.0f}c | {r['z']:.2f} | {r['zu']:.2f} | {'' if r['zk'] is None else format(r['zk'], '.2f')} | {r['sold']:,.0f} |")
    say("\n## H. The 99c line: markets with no seller under $1.00, 3 minutes left (a joined bid at 99c wins 1c a contract)")
    say("| Coin | Bar | Signals a day | Lost, of all signals | Sure fills (something sold under our price): bets / lost / per $100 | Best case (any sale at our price fills us): bets / lost / per $100 | "
        "Trade lists read | Contracts sold at our price after our bid: middle market | Markets with 100+ sold | with 1,000+ sold |")
    say("|---|---|---|---|---|---|---|---|---|---|")

    def c3(g, key):
        f = [r for r in g if r[key]]
        cost = sum(r["price"] for r in f)
        return f"{len(f)} / {sum(not r['won'] for r in f)} / {money(sum((1.0 if r['won'] else 0.0) - r['price'] for r in f) / cost * 100 if cost else 0)}"
    for s in names + ["all"]:
        for bar in BARS:
            g = [r for r in keep(T, bar) if s in (r["s"], "all")]
            tp = sorted(r["at"] for r in g if r["sold"] is not None)
            say(f"| {s} | {bar} | {len(g) / days:.0f} | {sum(not r['won'] for r in g)} of {len(g)} | {c3(g, 'candle')} | {c3(g, 'touch')} | {len(tp)} | "
                f"{tp[len(tp) // 2] if tp else 0:,.0f} | {sum(1 for x in tp if x >= 100)} | {sum(1 for x in tp if x >= 1000)} |")
    say("\n## H2. The 99c line if we were always FIRST in it (we would not be: the best case), bar 2.3, 3 minutes left, scaled up from the rounds whose trade lists were read")
    say("| Coin | Bid size | Bids a day | Bids that get anything | Lost | $ bought a day | Wins a day, best case | Wins a day counting only sales BELOW our price (the sure ones) | Losses a day (every loser of the full 61 days fills in full) | Best case after losses | Sure fills after losses |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in [x for x in ("KXBTCD", "KXETHD") if x in names]:
        g = [r for r in keep(T, 2.3) if s in (r["s"], "all") and r["sold"] is not None and sampled(r["close"])]
        losers = [r for r in keep(T, 2.3) if r["s"] == s and not r["won"]]
        dd = days / 3
        for usd in SIZES:
            n = lost = 0
            cost = pnl = sure = 0.0
            for r in g:
                need = int(usd / r["price"] + EPS)
                below = r["sold"] - (r["at"] if r["front"] else 0)
                got = min(need, int(below + r["at"]))
                if got < 1 or not r["won"]:
                    continue
                n += 1
                cost += got * r["price"]
                pnl += got * (1.0 - r["price"])
                sure += min(need, int(below)) * (1.0 - r["price"])
            ld = sum(int(usd / r["price"] + EPS) * r["price"] for r in losers) / days
            say(f"| {s} | ${usd} | {len(g) / dd:.0f} | {n / dd:.0f} | {len(losers)} in {days:.0f} days | ${cost / dd:,.0f} | {money(pnl / dd)} | {money(sure / dd)} | {money(-ld)} | "
                f"{money(pnl / dd - ld)} | {money(sure / dd - ld)} |")
    say("\n## I. Bidding earlier in the hour (candles only, bar 2.3, all coins)")
    say("| Min left | Bids of 95c-98c: signals / sure fills / lost / per $100 | 99c line: signals a day / lost of all / sure fills: bets, lost, per $100 / best case: bets, lost, per $100 |")
    say("|---|---|---|")
    for m in (3, 5, 10, 20):
        rows = keep([r for D in Ds.values() for r in bets(D, m)], 2.3)
        lo_, top_ = [r for r in rows if not r["top"]], [r for r in rows if r["top"]]
        say(f"| {m} | {len(lo_)} / {c3(lo_, 'candle')} | {len(top_) / days:.0f} / {sum(not r['won'] for r in top_)} of {len(top_)} / {c3(top_, 'candle')} / {c3(top_, 'touch')} |")
    say("\n## G. The exam")
    tries = 60
    for bar in BARS:
        exam.score(exam_bets(keep(B[3], bar)), f"kc_maker_safe_usd on Kalshi hourly crypto rounds, bar {bar} (history, 3 min, $4 bids)", tries=tries,
                   src="khourly.py run, backtest/khourly.md", log=arg == "log", status="dropped",
                   note="The real Kalshi bot's rule moved from the 15-minute rounds to the hourly above/below rounds. Tape fills.")
    os.makedirs(CACHE, exist_ok=True)
    save_log("run.txt")
    return B


# ================================================================ Polymarket's hourly and daily crypto rounds
# Hourly: "<coin>-updown-1h-<start>", Up if Chainlink's price at the end is at or above the price at the start.
# Daily: "<coin>-above-on-<month>-<day>[-<year>]", a ladder of "above $X" lines, read off Binance's one-minute close
# at noon New York time. Makers pay no fee on either. No order-book history exists, so (as in kcrypto.py pm_bets)
# the bid is rebuilt from the trades of the 15 seconds before we look, and filled only by later real trades.
PM_COINS = {"btc": ("bitcoin", "KXBTCD"), "eth": ("ethereum", "KXETHD"), "sol": ("solana", "KXSOLD"), "xrp": ("xrp", "KXXRPD")}
PM_KEEP = 480


def _pm_rows(slugs):
    from concurrent.futures import ThreadPoolExecutor

    def batch(chunk):
        try:
            return bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"slug": chunk, "closed": "true", "limit": 100}), "markets", "data")
        except Exception as e:
            print(f"  gamma batch failed: {str(e)[:100]}")
            return []
    out = []
    with ThreadPoolExecutor(6) as ex:
        for rows in ex.map(batch, [slugs[i:i + 20] for i in range(0, len(slugs), 20)]):
            out += [m for m in rows if isinstance(m, dict)]
    return out


def _pm_result(m, first):
    try:
        names = json.loads(m.get("outcomes") or "[]")
        prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception:
        return None
    i = [j for j, n in enumerate(names) if str(n).lower() == first]
    if len(prices) == 2 and sorted(prices) == [0.0, 1.0] and i and m.get("conditionId"):
        return int(prices[i[0]] == 1.0)
    return None


def _pm_tape(cid, close, first, max_pages=40):
    """Trades of the last PM_KEEP seconds as [seconds before close, price of the first outcome, size]; (rows, complete)."""
    rows, cur, done = [], None, False
    for _ in range(max_pages):
        q = {"condition_id": cid, "limit": 500}
        if cur:
            q["cursor"] = cur
        res = bot.http_json(f"{bot.DATA}/v2/trades", q)
        page = bot.envelope_rows(res, "data", "trades")
        cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
        ts = []
        for r in page:
            t = bot.fnum(r.get("timestamp"))
            t = t / 1000 if t > 1e11 else t
            px, sz = bot.fnum(r.get("price")), bot.fnum(r.get("size"))
            ts.append(t)
            if not 0 < px < 1 or sz <= 0 or not (close - PM_KEEP <= t <= close):
                continue
            rows.append([round(close - t, 1), round(px if str(r.get("outcome", "")).lower() == first else 1 - px, 4), round(sz, 2)])
        newest_first = len(ts) < 2 or ts[0] >= ts[-1]
        if not page or not cur or (newest_first and ts and min(ts) < close - PM_KEEP):
            done = True
            break
    rows.sort(key=lambda r: -r[0])
    return rows, done


def pm_fetch(arg=None):
    from concurrent.futures import ThreadPoolExecutor
    days_h, days_d = 30, 61
    os.makedirs(CACHE, exist_ok=True)
    now = int(time.time()) - 7200
    for short, (long, _) in PM_COINS.items():
        t_s = time.time()
        path = os.path.join(CACHE, f"pm_{short}.json.gz")
        have = kc.rjson(path, {}) or {}
        jobs = []
        starts = [st for st in range(now - now % 3600 - days_h * 86400, now - 3600, 3600) if f"h{st + 3600}" not in have]
        for m in _pm_rows([f"{short}-updown-1h-{st}" for st in starts]):
            res = _pm_result(m, "up")
            if res is None:
                continue
            st = int(str(m.get("slug")).rsplit("-", 1)[1])
            jobs.append((f"h{st + 3600}", m["conditionId"], st + 3600, "up", {"kind": "h", "close": st + 3600, "p": res, "vol": bot.fnum(m.get("volume"), 0)}))
        # before about 18 Nov 2026 the hourly round was "<coin>-up-or-down-<month>-<day>-<year>-<hour>-et", settled on Binance's 1-hour candle
        got_h = {j[0] for j in jobs} | set(have)
        old = []
        for st in range(now - now % 3600 - days_h * 86400, now - 3600, 3600):
            if f"h{st + 3600}" in got_h or f"b{st + 3600}" in got_h:
                continue
            et = dt.datetime.fromtimestamp(st - (4 if st < 1793512800 else 5) * 3600, UTC)   # US clocks went back 1 Nov 2026 06:00 UTC
            old.append((st, f"{long}-up-or-down-{et.strftime('%B').lower()}-{et.day}-{et.year}-{et.hour % 12 or 12}{'am' if et.hour < 12 else 'pm'}-et"))
        days_ = []
        for d in range(1, days_d + 1):
            day = dt.datetime.fromtimestamp(now - d * 86400, UTC)
            days_.append(f"{long}-above-on-{day.strftime('%B').lower()}-{day.day}-{day.year}")
        with ThreadPoolExecutor(8) as ex:
            evs_h = list(ex.map(lambda x: bot.event_by_slug(x[1]), old))
            evs = [e for e in ex.map(bot.event_by_slug, days_) if e]
        for (st, sl), e in zip(old, evs_h):
            m = ((e or {}).get("markets") or [None])[0]
            res = _pm_result(m, "up") if m else None
            end = kc.tsec(m.get("endDate")) if m else None
            if res is None or not end or abs(end - (st + 3600)) > 120:
                continue
            jobs.append((f"b{st + 3600}", m["conditionId"], st + 3600, "up", {"kind": "b", "close": st + 3600, "p": res, "vol": bot.fnum(m.get("volume"), 0)}))
        for e in evs:
            for m in e.get("markets") or []:
                end = kc.tsec(m.get("endDate"))
                k = re.search(r"above \$([\d,.]+)", str(m.get("question")))
                res = _pm_result(m, "yes")
                if not end or end < now - (days_d + 2) * 86400 or not k or res is None or f"d{m.get('conditionId')}" in have:
                    continue
                jobs.append((f"d{m['conditionId']}", m["conditionId"], end, "yes", {"kind": "d", "close": end, "p": res, "strike": float(k.group(1).replace(",", "")),
                                                                                    "vol": bot.fnum(m.get("volume"), 0), "ev": e.get("slug")}))

        def one(j):
            try:
                tr, ok = _pm_tape(j[1], j[2], j[3])
                return j, tr, ok
            except Exception as ex_:
                return j, ex_, False
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for i, (j, tr, ok) in enumerate(ex.map(one, jobs)):
                if isinstance(tr, Exception):
                    bad += 1
                    continue
                have[j[0]] = dict(j[4], tr=tr, ok=ok)
                if i and i % 1000 == 0:
                    kc.wjson(path, have)
        kc.wjson(path, have)
        hh = [v for v in have.values() if v["kind"] in ("h", "b")]
        dd = [v for v in have.values() if v["kind"] == "d"]
        say(f"Polymarket {short}: {len(hh)} hourly rounds (${sum(v['vol'] for v in hh):,.0f} traded, middle round ${sorted(v['vol'] for v in hh)[len(hh) // 2] if hh else 0:,.0f}), "
            f"{len(dd)} daily-ladder markets in {len({v['ev'] for v in dd})} days (${sum(v['vol'] for v in dd):,.0f}); {bad} failed, "
            f"incomplete tapes {sum(1 for v in have.values() if not v.get('ok'))} ({time.time() - t_s:.0f}s)")
    save_log("pmfetch.txt")


def pm_bets(minutes=3, look=15, level=0.95):
    out = []
    for short, (long, series) in PM_COINS.items():
        have = kc.rjson(os.path.join(CACHE, f"pm_{short}.json.gz"), {}) or {}
        if not have or not os.path.exists(p(series, "spot")):
            continue
        D = load(series)
        for key, row in have.items():
            if not row.get("ok") or not row.get("tr"):
                continue
            left = 60 * minutes
            before = [r for r in row["tr"] if left <= r[0] <= left + look]
            if len(before) < 2:
                continue
            side = "yes" if before[-1][1] >= 0.5 else "no"
            f = (lambda x: x) if side == "yes" else (lambda x: round(1 - x, 4))
            lo, hi = min(f(r[1]) for r in before), max(f(r[1]) for r in before)
            if lo < level - EPS or lo >= 1 - EPS:
                continue
            tick = 0.001 if lo >= 0.96 - EPS else 0.01
            front = hi > lo + tick + EPS
            price = round(lo + tick, 4) if front else lo
            later = [(f(r[1]), r[2]) for r in row["tr"] if 0 <= r[0] < left]
            sold = sum(n for px, n in later if px < price - EPS or (front and px <= price + EPS))
            t = row["close"] - left
            if row["kind"] == "b":                           # old hourly round: Binance's own 1-hour candle, close at or above its open
                k = D["spot"].get(str(row["close"] - 3600))
                z = zu = kc.zscore({"spot": D["spot"], "strike": k}, t, minutes, side) if k else None
            elif row["kind"] == "h":
                k = D["idx"].get(row["close"] - 3600)       # the start price, on Kalshi's (US dollar) number
                g = gap_at(D, t)
                if not k or not g:
                    continue
                w = {"spot": D["spot"], "strike": k}
                z = kc.zscore(w, t, minutes, side)
                zu = kc.zscore(dict(w, strike=k * g), t, minutes, side)
            else:
                z = zu = kc.zscore({"spot": D["spot"], "strike": row["strike"]}, t, minutes, side)   # settles on Binance itself: no gap
            if z is None or zu is None:
                continue
            out.append({"kind": "h" if row["kind"] == "b" else row["kind"], "s": short, "t": t, "close": row["close"], "ev": f"{short}{row['close']}", "side": side, "price": price,
                        "front": front, "z": z, "zu": zu, "won": (row["p"] == 1) == (side == "yes"), "sold": sold, "vol": row.get("vol")})
    return out


def pm_card(rows, usd=4):
    n = lost = 0
    cost = pnl = 0.0
    for r in rows:
        got = min(int(usd / r["price"] + EPS), int(r["sold"]))
        if got < 1:
            continue
        n += 1
        lost += not r["won"]
        cost += got * r["price"]
        pnl += got * ((1.0 if r["won"] else 0.0) - r["price"])
    return {"signals": len(rows), "bets": n, "lost": lost, "cost": cost, "pnl": pnl, "per100": pnl / cost * 100 if cost else 0.0}


def pm_run(arg=None):
    import exam
    say("\n## P. Polymarket ($4 and $40 bids, filled only by later real trades)")
    say("| Rounds | Min left | Bar | Signals | Bets filled | Lost | Per $100 | Profit at $4 | Days | Bets a day | Profit at $40 bids |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    keepers = {}
    for kind, label in (("h", "hourly up / down"), ("d", "daily noon ladder")):
        for m in (2, 3, 5):
            rows = [r for r in pm_bets(m) if r["kind"] == kind]
            if not rows:
                continue
            days = max(1.0, (max(r["t"] for r in rows) - min(r["t"] for r in rows)) / 86400)
            for bar in (None,) + BARS:
                g = rows if bar is None else keep(rows, bar)
                c, c40 = pm_card(g), pm_card(g, 40)
                say(f"| {label} | {m} | {'no check' if bar is None else bar} | {c['signals']} | {c['bets']} | {c['lost']} | {money(c['per100'])} | {money(c['pnl'])} | "
                    f"{days:.0f} | {c['bets'] / days:.1f} | {money(c40['pnl'])} |")
                if m == 3 and bar == 2.3:
                    keepers[label] = g
    for label, g in keepers.items():
        bl = [{"cost": min(int(4 / r["price"] + EPS), int(r["sold"])) * r["price"], "pay": min(int(4 / r["price"] + EPS), int(r["sold"])) * (1.0 if r["won"] else 0.0),
               "t": r["t"], "ev": str(r["close"])} for r in g]
        exam.score(bl, f"kc_maker_safe_usd on Polymarket {label} crypto rounds, bar 2.3 (history, 3 min, $4 bids)", tries=60, src="khourly.py pmrun, backtest/khourly.md",
                   log=arg == "log", status="dropped: about 1 bet a day", note="The real Kalshi bot's rule on Polymarket's hourly up/down and daily noon ladder. Bid rebuilt from trades.")
    save_log("pmrun.txt")


# ================================================================ live look at the line in front of us (probe khr_queue_<minutes>)
def queue(arg=None):
    """History has no order-book sizes. This watches live: 3 minutes before each hourly close it reads the real order
    books of the markets the rule would bid in (bid 95c+ on the leading side), notes how many contracts already wait at
    the price we would join, and after the close counts how many were really sold at that price or lower."""
    minutes = int(arg or 240)
    end = time.time() + minutes * 60
    names = ("KXBTCD", "KXETHD", "KXSOLD", "KXXRPD")
    out = kc.rjson(os.path.join(CACHE, "queue.json.gz"), []) or []
    while time.time() < end:
        nxt = (int(time.time()) // 3600 + 1) * 3600
        wait = nxt - 180 - time.time()
        if wait > 0:
            if time.time() + wait + 240 > end + 600:
                break
            time.sleep(wait)
        elif wait < -40:
            time.sleep(nxt + 5 - time.time())
            continue
        snap = []
        for s in names:
            try:
                ms = kget("/markets", {"series_ticker": s, "status": "open", "min_close_ts": nxt - 30, "max_close_ts": nxt + 30, "limit": 1000}).get("markets") or []
                ks = bot.http_json(f"{bot.BINANCE}/klines", {"symbol": SERIES[s], "interval": "1m", "limit": 62})
                cl = [float(k[4]) for k in ks]
                rets = [math.log(b / a) for a, b in zip(cl[:-1], cl[1:])][-60:]
                sd = math.sqrt(sum(r * r for r in rets) / len(rets)) * cl[-1] * math.sqrt(3)
            except Exception as e:
                print("  snapshot failed", s, str(e)[:100], flush=True)
                continue
            for m in ms:
                yb, ya = bot.fnum(m.get("yes_bid_dollars"), 0), bot.fnum(m.get("yes_ask_dollars"), 1)
                side = leader([yb, ya])
                k = bot.fnum(m.get("floor_strike"), None)
                if not side or not k or m.get("strike_type") != "greater":
                    continue
                bid, ask = (yb, ya) if side == "yes" else (1 - ya, 1 - yb)
                if bid < 0.95 - EPS:
                    continue
                z = (cl[-1] - k) / sd * (1 if side == "yes" else -1)
                if z < 2 or z > 12:
                    continue
                bk = bot.kalshi_book_sides(m["ticker"]) or {}
                lv = bk.get(side) or []
                best = lv[0] if lv else (bid, 0)
                front = round(best[0] + 0.01, 4) < ask - EPS
                snap.append({"s": s, "tk": m["ticker"], "close": nxt, "t": time.time(), "side": side, "bid": best[0], "ask": ask, "z": round(z, 2),
                             "line": best[1], "front": front, "price": round(best[0] + 0.01, 4) if front else best[0]})
        print(f"{iso(nxt)}: {len(snap)} markets watched, read {nxt - time.time():.0f}s before the close", flush=True)
        time.sleep(max(0, nxt + 45 - time.time()))
        for r in snap:
            try:
                trs = get_trades(r["tk"], 1000).get("trades") or []
                mk = (kget(f"/markets/{r['tk']}").get("market") or {})
            except Exception as e:
                print("  after-close read failed", str(e)[:100], flush=True)
                continue
            below = at = 0.0
            for x in trs:
                d = bot.parse_iso(x.get("created_time"))
                if not d or d.timestamp() <= r["t"] or str(x.get("taker_side") or "")[:1] != ("n" if r["side"] == "yes" else "y"):
                    continue
                yp = bot.fnum(x.get("yes_price_dollars"), None)
                px = yp if r["side"] == "yes" else 1 - yp
                n = bot.fnum(x.get("count_fp") or x.get("count"), 0)
                if px < r["price"] - EPS:
                    below += n
                elif px <= r["price"] + EPS:
                    at += n
            r.update(below=below, at=at, res=str(mk.get("result") or ""), more=len(trs) >= 1000)
            out.append(r)
        kc.wjson(os.path.join(CACHE, "queue.json.gz"), out)
    queue_report(out)
    save_log("queue.txt")


def queue_report(out=None):
    out = out if out is not None else (kc.rjson(os.path.join(CACHE, "queue.json.gz"), []) or [])
    say(f"\n## Q. Live: the line in front of us, {len({r['close'] for r in out})} hourly closes, {len(out)} markets (bid 95c+, Binance cushion 2+, read 3 min before the close)")
    say("| Coin | Our price | Markets | Could step in front | Line at the price we join (middle / smallest / biggest) | Sold at our price afterwards (middle) | Sold below our price | Reached a $4 bid at the back | a $40 bid | Lost among those reached |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    for s in sorted({r["s"] for r in out}):
        for px in (0.99, 0.98, 0.97, 0.96, 0.95):
            g = [r for r in out if r["s"] == s and abs(r["price"] - px) < 0.005 and "at" in r]
            if not g:
                continue
            ln = sorted(r["line"] for r in g if not r["front"]) or [0]
            at = sorted(r["at"] for r in g)

            def reach(r, usd):
                ahead = 0 if r["front"] else r["line"]
                return r["below"] > 0 or r["at"] >= ahead + usd / r["price"]
            r4, r40 = [r for r in g if reach(r, 4)], [r for r in g if reach(r, 40)]
            say(f"| {s} | {px * 100:.0f}c | {len(g)} | {sum(r['front'] for r in g)} | {ln[len(ln) // 2]:,.0f} / {ln[0]:,.0f} / {ln[-1]:,.0f} | {at[len(at) // 2]:,.0f} | "
                f"{sum(1 for r in g if r['below'] > 0)} markets | {len(r4)} | {len(r40)} | {sum(1 for r in r4 if r['res'] and r['res'] != r['side'])} |")


# ================================================================ two more 15-minute coins (probe khr_more15)
MORE15 = {"KXNEAR15M": "NEARUSDT", "KXZEC15M": "ZECUSDT"}
CACHE15 = os.path.join(CACHE, "kc15")


def more15(arg=None):
    """Kalshi also lists 15-minute rounds for NEAR and Zcash, which the bots don't bid on. Same download as kcrypto.py
    fetch, into bt_cache/khr/kc15/."""
    kc.SERIES, kc.CACHE = dict(MORE15), CACHE15
    kc.fetch(int(arg or 61))


def run15(arg=None):
    """The 15-minute rule (kcrypto.py's own replay: bid one tick in front at 95c+, 3 minutes left, 'fair' candle fills)
    on NEAR and Zcash next to the 7 coins the bots already bid on, same days, by cushion bar."""
    import exam
    sets = [("new", CACHE15, MORE15)]
    if os.path.exists(os.path.join(bot.ROOT, "bt_cache", "kc", "candles_KXBTC15M.json.gz")):
        sets.append(("the 7 we have", os.path.join(bot.ROOT, "bt_cache", "kc"), dict(kc.SERIES)))
    allr = {}
    for label, cache, series in sets:
        kc.CACHE = cache
        for sname in series:
            ws = kc.load_windows([sname])
            if not ws:
                continue
            sigs = kc.signals(ws, 3)
            bys = {x["w"]["t"]: x for x in sigs}
            rows = []
            for r in kc.variant_trades(sigs, "improve", 0.95, None):
                x = bys[r["tk"]]
                r["z"], r["zu"] = kc.zscore(x["w"], x["t"], 3, x["side"]), kc.zscore_usd(x["w"], x["t"], 3, x["side"])
                if r["fills"][1] and r["z"] is not None and r["zu"] is not None:
                    rows.append(r)
            allr[sname] = (label, rows, ws)
    t_lo = max(min(w["close"] for w in ws) for _, _, ws in allr.values())
    t_hi = min(max(w["close"] for w in ws) for _, _, ws in allr.values())
    days = (t_hi - t_lo) / 86400
    say(f"\n## N. Two more 15-minute coins: the same rule, 3 minutes left, candle fills, {iso(t_lo)} to {iso(t_hi)} UTC ({days:.0f} days, $4 bids)")
    say("| Coin | Bar | Bets | Lost | 1 loss per | Per $100 | Profit at $4 bids | Bets a day | $ a day | Contracts a round (middle) |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    for sname, (label, rows, ws) in allr.items():
        vv = sorted(w["vol"] for w in ws if t_lo <= w["close"] <= t_hi)
        for bar in BARS:
            g = [r for r in rows if t_lo <= r["t"] <= t_hi and r["z"] >= 2 and r["zu"] >= bar]
            lost = sum(not r["won"] for r in g)
            cost = sum(r["price"] for r in g)
            pnl = sum((1.0 if r["won"] else 0.0) - r["price"] for r in g)
            usd = sum(((1.0 if r["won"] else 0.0) - r["price"]) / r["price"] * 4 for r in g)
            say(f"| {sname} ({label}) | {bar} | {len(g)} | {lost} | {len(g) / lost if lost else 0:.0f} | {money(pnl / cost * 100 if cost else 0)} | {money(usd)} | "
                f"{len(g) / days:.1f} | {money(usd / days)} | {vv[len(vv) // 2] if vv else 0:,.0f} |")
    for sname in MORE15:
        if sname in allr:
            g = [r for r in allr[sname][1] if r["z"] >= 2 and r["zu"] >= 2.3]
            exam.score([{"cost": r["price"] * 4, "pay": 4.0 if r["won"] else 0.0, "t": r["t"], "ev": r["t"]} for r in g],
                       f"kc_maker_safe_usd on {sname}, bar 2.3 (history, 3 min, candle fills)", tries=6, src="khourly.py run15, backtest/khourly.md",
                       log=arg == "log", status="lead: untested live", note="The real Kalshi bot's rule on a 15-minute coin it does not bid on yet.")
    save_log("run15.txt")


# ================================================================ every 15-minute coin, real trade lists (probe khr_grow15)
# 27 Nov 2026 (Jan: "go crazy"; thread "Grow the Kalshi bid bot to more coins"). Which Kalshi 15-minute crypto rounds
# does the real bot (kc_maker_safe_usd) not bid on, and would they add money at $4 / $25 / $40 bids? Replays the real
# bot's own way of betting: from 5 to 1 minutes left it looks once a minute (the real bot every 15 s) and bids the first
# time the leading side's best bid is 95c+ and both Binance cushions pass (plain >= 2.0, price-gap-corrected >= 2.3),
# one tick in front of the best bid, held to the result. Fills come from the window's real trade list after the bid,
# the big_kalshi way (bigbets.kalshi_fill): contracts sold AT our price after the line that stood there first, plus
# everything sold BELOW it. In front of the line (the usual case) nobody stands ahead of us; when there was no room in
# front, sales at our price don't count at all (the line ahead is unknown), so those bids only get sales below us.
ALL15 = os.path.join(CACHE, "kc15")
SIZES15 = (4, 25, 40)
GROW_BAR = 2.3
REAL7 = {"KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M", "KXHYPE15M", "KXBNB15M"}   # the coins the real bot trades (bot.KMAKER_SPOT also has paper-only coins since 27 Nov)


def scan15():
    """Every Kalshi crypto series with 15-minute rounds settled in the last 2 days, and a Binance pair for each."""
    ser = kget("/series", {"category": "Crypto"}).get("series") or []
    now = int(time.time())
    out = {}
    for s in sorted(ser, key=lambda s: s.get("ticker") or ""):
        tk = s.get("ticker") or ""
        if "15M" not in tk:
            continue
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 400, "min_close_ts": now - 2 * 86400}).get("markets") or []
        except Exception as e:
            say("  failed", tk, str(e)[:80])
            continue
        coin = tk[2:].split("15M")[0]
        sym = bot.KMAKER_SPOT.get(tk) or f"{coin}USDT"
        try:
            ok = bool(bot.http_json("https://data-api.binance.vision/api/v3/klines", {"symbol": sym, "interval": "1m", "limit": 2}))
        except Exception:
            ok = False
        vol = sum(map(vol_of, ms))
        m0 = ms[0] if ms else {}
        say(f"  {tk:14s} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | 2 days: {len(ms)} rounds, "
            f"{vol:,.0f} contracts | Binance {sym}: {'yes' if ok else 'NO'} | covered by the real bot: {'yes' if tk in REAL7 else 'no'} "
            f"| tick {json.dumps(m0.get('price_ranges'))[:120]} | {str(s.get('title'))[:50]}")
        if ms and ok:
            out[tk] = sym
    os.makedirs(ALL15, exist_ok=True)
    kc.wjson(os.path.join(ALL15, "series.json.gz"), out)
    return out


def _sig15(w, bar=2.0):
    """The real bot's first bid in this window (looks at 5, 4, 3, 2, 1 minutes left), or None."""
    for mn in (5, 4, 3, 2, 1):
        t = w["close"] - 60 * mn
        row = w["c"].get(t)
        if not row:
            continue
        side = kc.leader(row)
        if not side:
            continue
        bid, ask, _, _ = kc.side_view(row, side)
        if bid is None or ask is None or bid < 0.95 - EPS:
            continue
        z, zu = kc.zscore(w, t, mn, side), kc.zscore_usd(w, t, mn, side)
        if z is None or zu is None or z < 2.0 or zu < bar:
            continue
        tick = bot.kmaker_tick(bid)
        price = round(bid + tick, 4)
        front = price < ask - EPS
        if not front:
            price = bid
        return {"t": t, "mn": mn, "side": side, "price": price, "front": front, "z": z, "zu": zu, "bid": bid, "ask": ask}
    return None


def _tape15(w):
    out, cur = [], None
    try:
        for _ in range(60):
            q = {"ticker": w["t"], "min_ts": w["close"] - 330, "max_ts": w["close"] + 5, "limit": 1000}
            if cur:
                q["cursor"] = cur
            res = kget("/markets/trades", q)
            rows = res.get("trades") or []
            for x in rows:
                d = bot.parse_iso(x.get("created_time"))
                yp = bot.fnum(x.get("yes_price_dollars"), None)
                if yp is None:
                    yp = bot.fnum(x.get("yes_price"), 0) / 100
                if d:
                    out.append([round(d.timestamp(), 2), round(yp, 4), bot.fnum(x.get("count_fp") or x.get("count"), 0), str(x.get("taker_side") or "")[:1]])
            cur = res.get("cursor")
            if not cur or not rows:
                break
    except Exception as e:
        return w, e
    return w, sorted(out)


def fetch15(arg=None):
    """Markets, last-11-minute candles and Binance minutes of every 15-minute coin (bt_cache/khr/kc15/), then the real
    trade list of the last 5.5 minutes of every window where the real bot would have bid (tape_<series>.json.gz)."""
    from concurrent.futures import ThreadPoolExecutor
    ser = scan15()
    kc.SERIES, kc.CACHE = dict(ser), ALL15
    kc.fetch(int(arg or 64))
    for series in ser:
        t_s = time.time()
        path = os.path.join(ALL15, f"tape_{series}.json.gz")
        tr = kc.rjson(path, {}) or {}
        ws = kc.load_windows([series])
        want = [w for w in ws if w["t"] not in tr and _sig15(w)]
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for i, (w, out) in enumerate(ex.map(_tape15, want)):
                if isinstance(out, Exception):
                    bad += 1
                    continue
                tr[w["t"]] = out
                if i and i % 1500 == 0:
                    kc.wjson(path, tr)
        kc.wjson(path, tr)
        say(f"{series}: {len(ws)} windows, {len(want)} tapes asked, {bad} failed, {len(tr)} kept ({time.time() - t_s:.0f}s)")
    save_log("fetch15.txt")


def _fill15(s, tape, want):
    at = below = 0.0
    for ts, yp, n, taker in tape:
        if ts <= s["t"] or ts > s["close"] + 1:
            continue
        if taker == s["side"][0]:
            continue                           # a buyer of our side doesn't sell to our bid
        px = yp if s["side"] == "yes" else round(1 - yp, 4)
        if abs(px - s["price"]) < 1e-6:
            at += n
        elif px < s["price"] - 1e-6:
            below += n
    return min(float(want), (at if s["front"] else 0.0) + below)


def grow_rows(bar=GROW_BAR):
    """One row per bid: coin, round, price, won, contracts filled at each bid size."""
    ser = kc.rjson(os.path.join(ALL15, "series.json.gz"), {}) or {}
    kc.SERIES, kc.CACHE = dict(ser), ALL15
    rows = []
    for series in ser:
        tr = kc.rjson(os.path.join(ALL15, f"tape_{series}.json.gz"), {}) or {}
        for w in kc.load_windows([series]):
            s = _sig15(w, bar)
            if not s or w["t"] not in tr:
                continue
            s["close"] = w["close"]
            r = {"s": series, "tk": w["t"], "close": w["close"], "t": s["t"], "mn": s["mn"], "side": s["side"], "price": s["price"],
                 "front": s["front"], "won": w["res"] == s["side"], "vol": w["vol"], "f": {}}
            for S in SIZES15:
                want = max(1, int(S / s["price"] + 1e-9))
                r["f"][S] = (_fill15(s, tr[w["t"]], want), want)
            rows.append(r)
    return rows


def _pnl(r, S):
    f = r["f"][S][0]
    return f * ((1.0 if r["won"] else 0.0) - r["price"]), f * r["price"]


def grow15(arg=None):
    import exam
    rows = grow_rows()
    if not rows:
        say("no rows")
        save_log("grow15.txt")
        return
    t_lo, t_hi = min(r["close"] for r in rows), max(r["close"] for r in rows)
    days = (t_hi - t_lo) / 86400
    say(f"\n## The real bot's rule on every Kalshi 15-minute coin, real trade lists, {iso(t_lo)} to {iso(t_hi)} UTC ({days:.1f} days)")
    say("Bar 2.3 (the real bot's), looks once a minute from 5 to 1 minutes left, one tick in front of the best bid at 95c+.\n")
    say("| Coin | Bot has it? | Bids | Got anything ($4) | Lost (filled) | " + " | ".join(f"${S}: P&L / a day / per $100" for S in SIZES15) + " | Worst day at $40 |")
    say("|---|---|---|---|---|" + "---|" * len(SIZES15) + "---|")
    byser = collections.defaultdict(list)
    for r in rows:
        byser[r["s"]].append(r)
    tot = {}
    for series in sorted(byser, key=lambda x: (x in REAL7, x)):
        g = byser[series]
        got = [r for r in g if r["f"][4][0] > 0]
        cells = []
        for S in SIZES15:
            pnl = sum(_pnl(r, S)[0] for r in g)
            cost = sum(_pnl(r, S)[1] for r in g)
            cells.append(f"{money(pnl)} / {money(pnl / days)} / {money(100 * pnl / cost if cost else 0)}")
        byday = collections.defaultdict(float)
        for r in g:
            byday[iso(r["close"])[:10]] += _pnl(r, 40)[0]
        say(f"| {series} | {'yes' if series in REAL7 else 'NO'} | {len(g)} | {len(got)} | {sum(1 for r in got if not r['won'])} | "
            + " | ".join(cells) + f" | {money(min(byday.values()))} |")
    for label, keep in (("The 7 the bot has", lambda s: s in REAL7), ("The new ones", lambda s: s not in REAL7), ("All together", lambda s: True)):
        g = [r for r in rows if keep(r["s"])]
        cells = []
        for S in SIZES15:
            pnl = sum(_pnl(r, S)[0] for r in g)
            cost = sum(_pnl(r, S)[1] for r in g)
            cells.append(f"{money(pnl)} / {money(pnl / days)} / {money(100 * pnl / cost if cost else 0)}")
            tot[(label, S)] = (pnl, cost)
        say(f"| **{label}** | | {len(g)} | {sum(1 for r in g if r['f'][4][0] > 0)} | {sum(1 for r in g if r['f'][4][0] > 0 and not r['won'])} | " + " | ".join(cells) + " | |")

    # losing together: rounds (same close time) where two or more coins lost
    say("\n### Do coins lose at the same moment?\n")
    byround = collections.defaultdict(list)
    for r in rows:
        if r["f"][4][0] > 0:
            byround[r["close"]].append(r)
    for label, keep in (("The 7 the bot has", lambda s: s in REAL7), ("All together", lambda s: True)):
        multi = 0
        losers_by_round = collections.Counter()
        worst = []
        for c, g in byround.items():
            g = [r for r in g if keep(r["s"])]
            lost = [r for r in g if not r["won"]]
            if lost:
                losers_by_round[len(lost)] += 1
            if len(lost) >= 2:
                multi += 1
            worst.append((sum(_pnl(r, 40)[0] for r in g), c, [r["s"] for r in lost]))
        worst.sort()
        nl = sum(k * v for k, v in losers_by_round.items())
        say(f"- {label}: {nl} lost bids in {sum(losers_by_round.values())} rounds; rounds with 1 / 2 / 3+ coins losing: "
            f"{losers_by_round[1]} / {losers_by_round[2]} / {sum(v for k, v in losers_by_round.items() if k >= 3)}. "
            f"Worst 3 rounds at $40: " + "; ".join(f"{iso(c)} {money(p)} ({', '.join(x.replace('KX', '').replace('15M', '') for x in l)})" for p, c, l in worst[:3]))
    # chance two coins lose together if they were unrelated
    nr = len(byround)
    p_loss = sum(1 for g in byround.values() for r in g if not r["won"]) / max(1, sum(len(g) for g in byround.values()))
    exp2 = sum(1 - (1 - p_loss) ** len(g) - len(g) * p_loss * (1 - p_loss) ** (len(g) - 1) for g in byround.values())
    say(f"- If losses had nothing to do with each other (1 filled bid in {1 / p_loss if p_loss else 0:.0f} loses), "
        f"rounds with 2+ coins losing would happen about {exp2:.1f} times in these {nr} rounds.")

    # new coins one by one, exam on the whole set of new ones
    newr = [r for r in rows if r["s"] not in REAL7 and r["f"][25][0] > 0]
    if newr:
        exam.score([{"cost": _pnl(r, 25)[1], "pay": r["f"][25][0] if r["won"] else 0.0, "t": r["close"], "ev": r["close"]} for r in newr],
                   "kc_maker_safe_usd on the 15-minute coins the real bot lacks (real trade lists, $25 bids)", tries=4,
                   src="khourly.py grow15, backtest/kgrow15.md", log=arg == "log", status="lead: untested live",
                   note="The real Kalshi bot's rule on the coins it does not bid on yet, fills from real trade lists.")
    oldr = [r for r in rows if r["s"] in REAL7 and r["f"][25][0] > 0]
    if oldr:
        exam.score([{"cost": _pnl(r, 25)[1], "pay": r["f"][25][0] if r["won"] else 0.0, "t": r["close"], "ev": r["close"]} for r in oldr],
                   "kc_maker_safe_usd replay on its own 7 coins (yardstick, real trade lists, $25 bids)", tries=4, log=False, quiet=False)
    # how many bids at once (money needed)
    ev = sorted([(r["t"], 1) for r in rows] + [(r["close"], -1) for r in rows])
    cur = top = 0
    for _, d in ev:
        cur += d
        top = max(top, cur)
    ev7 = sorted([(r["t"], 1) for r in rows if r["s"] in REAL7] + [(r["close"], -1) for r in rows if r["s"] in REAL7])
    cur = top7 = 0
    for _, d in ev7:
        cur += d
        top7 = max(top7, cur)
    say(f"\nMost bids open at once: {top7} with the 7 coins, {top} with all of them (money needed is about that many bids).")
    # check against the real bot: same days
    try:
        import bigbets
        real = bigbets.real_bids()
        if real:
            r0 = min(bot.parse_iso(o["placed"]).timestamp() for o in real)
            mine = [r for r in rows if r["s"] in REAL7 and r["t"] >= r0]
            say(f"Check against the real bot since {iso(r0)}: real bids {len(real)}, lost {sum(1 for o in real if o['exit'] < 0.5)}, "
                f"real contracts bought {sum(o['real_filled'] or 0 for o in real):,.0f}; this replay: {len(mine)} bids, "
                f"{sum(1 for r in mine if r['f'][4][0] > 0 and not r['won'])} lost, contracts at $4 {sum(r['f'][4][0] for r in mine):,.0f}, "
                f"P&L at $4 {money(sum(_pnl(r, 4)[0] for r in mine))}. Same windows: {len(set(o['ticker'] for o in real) & set(r['tk'] for r in mine))}.")
    except Exception as e:
        say("real-bot check failed:", str(e)[:120])
    kc.wjson(os.path.join(ALL15, "grow_rows.json.gz"), rows)
    save_log("grow15.txt")


# ================================================================ the other side: offering the safe side at 99c early (probe khr_lsfetch)
LS_MIN = (30, 20, 10)


def ls_fetch(arg=None):
    """Trade lists of the last half hour (only trades at 95c+ / 5c or less) for every market whose leading side sat at
    90c+ with a cushion of 1.5 to 5 at 30, 20 or 10 minutes before the close. Saved as bt_cache/khr/ls_<series>.json.gz."""
    from concurrent.futures import ThreadPoolExecutor
    for series in [x for x in (arg.split(",") if arg else SERIES) if x in SERIES]:
        t_s = time.time()
        D = load(series)
        if not D["w"]:
            continue
        path = os.path.join(CACHE, f"ls_{series}.json.gz")
        tr = kc.rjson(path, {}) or {}
        want = []
        for w in D["w"]:
            if w["t"] in tr:
                continue
            for mn in LS_MIN:
                t = w["close"] - 60 * mn
                row = w["c"].get(t)
                side = leader(row) if row else None
                g = gap_at(D, t) if side else None
                if not g or kc.side_view(row, side)[0] < 0.9 - EPS:
                    continue
                z = kc.zscore(dict(w, strike=w["strike"] * g), t, mn, side)
                if z is not None and 1.5 <= z < 5:
                    want.append(w)
                    break

        def tape(w):
            out, cur = [], None
            try:
                for _ in range(40):
                    q = {"ticker": w["t"], "min_ts": w["close"] - 1830, "max_ts": w["close"] + 5, "limit": 1000}
                    if cur:
                        q["cursor"] = cur
                    res = kget("/markets/trades", q)
                    rows = res.get("trades") or []
                    for x in rows:
                        d = bot.parse_iso(x.get("created_time"))
                        yp = bot.fnum(x.get("yes_price_dollars"), None)
                        if d and yp is not None and (yp >= 0.95 - EPS or yp <= 0.05 + EPS):
                            out.append([round(d.timestamp(), 2), yp, bot.fnum(x.get("count_fp") or x.get("count"), 0), str(x.get("taker_side") or "")[:1]])
                    cur = res.get("cursor")
                    if not cur or not rows:
                        break
            except Exception as ex_:
                return w, ex_
            return w, sorted(out)
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for i, (w, out) in enumerate(ex.map(tape, want)):
                if isinstance(out, Exception):
                    bad += 1
                    continue
                tr[w["t"]] = out
                if i and i % 2000 == 0:
                    kc.wjson(path, tr)
                    print(f"   {series} {i}/{len(want)} ({time.time() - t_s:.0f}s)", flush=True)
        kc.wjson(path, tr)
        say(f"{series}: {len(want)} asked, {bad} failed, {len(tr)} kept, {sum(len(v) for v in tr.values()):,} trades ({time.time() - t_s:.0f}s)")
    save_log("lsfetch.txt")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = None
    if "_" in cmd:
        cmd, arg = cmd.split("_", 1)
    {"scan": scan, "fetch": lambda: fetch(arg), "run": lambda: run(arg), "pmfetch": lambda: pm_fetch(arg), "pmrun": lambda: pm_run(arg), "queue": lambda: queue(arg), "queuereport": queue_report, "more15": lambda: more15(arg), "lsfetch": lambda: ls_fetch(arg), "run15": lambda: run15(arg), "scan15": scan15, "fetch15": lambda: fetch15(arg), "grow15": lambda: grow15(arg), "all15": lambda: (fetch15(arg), grow15())}[cmd]()
