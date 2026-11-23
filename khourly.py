#!/usr/bin/env python3
"""Kalshi's hourly and daily crypto rounds: the kc_maker_safe_usd bid replayed there (23 Nov 2026, Jan's ask).

PAPER ONLY. Reads public history and never trades.

    python3 khourly.py scan        # probe khr_scan: which crypto series exist on Kalshi (how often, fees, size), what one
                                   # hourly round looks like, and which hourly / daily crypto bets Polymarket lists
"""
import collections
import datetime as dt
import json
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
                side = kc.leader(row) if row else None
                if side and kc.side_view(row, side)[0] >= 0.95 - 1e-9:
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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = None
    if "_" in cmd:
        cmd, arg = cmd.split("_", 1)
    {"scan": scan, "fetch": lambda: fetch(arg)}[cmd]()
