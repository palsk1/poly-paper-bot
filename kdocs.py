"""Kalshi docs read-through (19 Nov 2026): try the public Kalshi endpoints we have never used.

Jan asked whether we had read Kalshi's API docs (docs.kalshi.com). We read all of them (write-up
`backtest/kalshi_docs.md`). Most new features need a logged-in API key (order tools, the CF Benchmarks
price feed, every websocket). This script only tries the ones that need no login, from GitHub Actions:

    python3 kdocs.py check   # probe kd_check: live price chart behind a 15-minute crypto event, fee changes,
                             # exchange schedule, many order books in one call, weather index, endpoint costs
    python3 kdocs.py depth   # probe kd_depth: how many days back that per-second chart goes
    python3 kdocs.py agree   # probe kd_agree: recent windows, Kalshi's own number vs Binance at 45 s / 3 min left
    python3 kdocs.py fetch [D]   # Kalshi's number for D days (default 125), 7 coins -> bt_cache/kidx/<series>.json.gz
    python3 kdocs.py run         # re-test kc_maker_safe's check and the 45-second buy with it -> backtest/kprice.md
    python3 kdocs.py retest      # probe kd_retest: kcrypto fetch + fetch + kfast tapes + run, all in one

No key, no orders, read-only.
"""
import datetime as dt
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

K = bot.KALSHI
UTC = dt.timezone.utc


def get(path, params=None):
    return bot.http_json(f"{K}{path}", params)


def show(label, fn):
    t = time.time()
    try:
        r = fn()
    except Exception as e:  # report and go on: this is a survey
        print(f"--- {label}: FAILED {e}")
        return None
    s = json.dumps(r)
    print(f"--- {label}: ok, {len(s)} bytes, {time.time() - t:.1f}s")
    print("    " + s[:1500])
    return r


def shape(x, depth=0):
    """Keys and list lengths, so we can see a new payload without dumping it."""
    if depth > 4:
        return "..."
    if isinstance(x, dict):
        return {k: shape(v, depth + 1) for k, v in list(x.items())[:25]}
    if isinstance(x, list):
        return [f"list[{len(x)}]", shape(x[0], depth + 1)] if x else "list[0]"
    return type(x).__name__


def points(live):
    """Find the longest list of (time, value) looking points anywhere in a live_data payload."""
    best = []

    def walk(x):
        nonlocal best
        if isinstance(x, list) and len(x) > len(best) and x and isinstance(x[0], (dict, list)):
            best = x
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x[:3]:
                walk(v)
    walk(live)
    return best


def binance_close(symbol, t_ms):
    """Binance 1-second candles around a time (what kc_maker_safe compares against)."""
    r = bot.http_json("https://data-api.binance.vision/api/v3/klines",
                      {"symbol": symbol, "interval": "1s", "startTime": t_ms - 60000, "endTime": t_ms})
    return [float(c[4]) for c in r]


def check():
    print("Kalshi public endpoints we never used, read-only, no key\n")
    # 1. the live price chart behind 15-minute crypto events (changelog 30 Jul 2026)
    for series, sym in (("KXBTC15M", "BTCUSDT"), ("KXETH15M", "ETHUSDT")):
        evs = []
        for status in ("open", "settled"):
            r = show(f"{series} events {status}",
                     lambda: get("/events", {"series_ticker": series, "status": status, "limit": 5,
                                             "with_nested_markets": "true"}))
            evs += [(status, e) for e in ((r or {}).get("events") or [])[:3]]
        for status, e in evs:
            ev = e.get("event_ticker")
            for params in ({}, {"range": "15min"}, {"range": "1h"}):
                live = show(f"live_data {ev} ({status}) {params}", lambda: get(f"/live_data/events/{ev}", params))
                if not live:
                    continue
                print("    shape:", json.dumps(shape(live))[:1200])
                pts = points(live)
                if pts:
                    print(f"    longest point list: {len(pts)} points, first {json.dumps(pts[0])[:200]}, "
                          f"last {json.dumps(pts[-1])[:200]}")
            for m in (e.get("markets") or [])[:1]:
                print(f"    market {m.get('ticker')}: floor_strike {m.get('floor_strike')}, result {m.get('result')!r}, "
                      f"close {m.get('close_time')}, expiration_value {m.get('expiration_value')!r}")
                try:
                    t = int(dt.datetime.fromisoformat(m["close_time"].replace("Z", "+00:00")).timestamp() * 1000)
                    if t < time.time() * 1000:
                        b = binance_close(sym, t)
                        if b:
                            print(f"    Binance {sym} last 60 s before close: average {sum(b) / len(b):.2f} "
                                  f"over {len(b)} seconds, last {b[-1]:.2f}")
                except Exception as ex:
                    print("    Binance check failed:", ex)
        # how far back does it go? one event per week back
        r = show(f"{series} settled, older", lambda: get("/events", {"series_ticker": series, "status": "settled",
                                                                    "limit": 200}))
        old = ((r or {}).get("events") or [])
        for e in old[::60][:4]:
            ev = e.get("event_ticker")
            live = show(f"live_data older {ev}", lambda: get(f"/live_data/events/{ev}"))
            if live:
                pts = points(live)
                print(f"    {len(pts)} points")
    # 2. scheduled fee changes (a maker fee on the 15-minute crypto series would hit kc_maker_safe)
    show("series fee changes (all, with history)", lambda: get("/series/fee_changes", {"show_historical": "true"}))
    for s in ("KXBTC15M", "KXETH15M", "KXSOL15M"):
        show(f"fee changes {s}", lambda: get("/series/fee_changes", {"series_ticker": s, "show_historical": "true"}))
        r = show(f"series {s}", lambda: get(f"/series/{s}"))
        if r:
            ser = r.get("series") or {}
            print(f"    fee_type {ser.get('fee_type')!r}, fee_multiplier {ser.get('fee_multiplier')!r}, "
                  f"settlement_sources {ser.get('settlement_sources')}")
    show("event fee changes", lambda: get("/events/fee_changes"))
    # 3. exchange schedule and status (Thursday maintenance)
    show("exchange schedule", lambda: get("/exchange/schedule"))
    show("exchange status", lambda: get("/exchange/status"))
    # 4. many order books in one call (up to 100 tickers)
    r = get("/markets", {"series_ticker": "KXBTC15M", "status": "open", "limit": 5})
    tks = [m["ticker"] for m in (r.get("markets") or [])]
    if tks:
        show(f"orderbooks for {len(tks)} markets in one call", lambda: get("/markets/orderbooks", {"tickers": ",".join(tks)}))
    # 5. weather index (minute series behind hourly temperature markets)
    show("weather index miami last hour", lambda: get("/live_data/weather/miami", {"last_sec": 3600}))
    # 6. costs and the price feed without a key (expect a refusal)
    show("endpoint costs", lambda: get("/account/endpoint_costs"))
    show("CF Benchmarks passthrough without a key", lambda: get("/cfbenchmarks/values", {"id": "BRTI"}))
    show("incentive programs, active, first page", lambda: get("/incentive_programs", {"status": "active", "limit": 5}))


MON = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def ev_ticker(series, close_utc):
    """Kalshi 15-minute event tickers name the close in New York time, e.g. KXBTC15M-26NOV190145."""
    et = close_utc - dt.timedelta(hours=5 if close_utc.month in (11, 12, 1, 2) or (close_utc.month == 3 and close_utc.day < 9) else 4)
    return f"{series}-{et:%y}{MON[et.month - 1]}{et:%d%H%M}"


def series_of(ev):
    r = get(f"/live_data/events/{ev}")
    return ((r.get("live_data") or {}).get("details") or {}).get("timeseries") or []


def depth():
    """How far back does the per-second chart go? Try one window a day back to 120 days."""
    now = dt.datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    for days in (1, 3, 7, 14, 21, 30, 45, 60, 90, 120):
        c = now - dt.timedelta(days=days)
        ev = ev_ticker("KXBTC15M", c)
        try:
            ts = series_of(ev)
            print(f"{days:4d} days back {ev}: {len(ts)} points"
                  + (f", {dt.datetime.fromtimestamp(ts[0]['t'] / 1000, UTC):%m-%d %H:%M:%S} to "
                     f"{dt.datetime.fromtimestamp(ts[-1]['t'] / 1000, UTC):%m-%d %H:%M:%S}" if ts else ""))
        except Exception as e:
            print(f"{days:4d} days back {ev}: FAILED {e}")


def agree(n=300):
    """Recent settled windows: does Kalshi's own per-second number tell the result, and how often does Binance
    (what kc_maker_safe and the fast Kalshi tests look at) point the other way, at 45 s and 3 minutes before the close?"""
    syms = {"KXBTC15M": "BTCUSDT", "KXETH15M": "ETHUSDT"}
    for series, sym in syms.items():
        ms, cur = [], None
        while len(ms) < n:
            p = {"series_ticker": series, "status": "settled", "limit": 200}
            if cur:
                p["cursor"] = cur
            r = get("/markets", p)
            ms += r.get("markets") or []
            cur = r.get("cursor")
            if not cur:
                break
        ms = ms[:n]
        tally = {"n": 0, "end_ok": 0, "k45": 0, "b45": 0, "k180": 0, "b180": 0, "b45_wrong_k_right": 0,
                 "k45_wrong_b_right": 0, "gap": []}
        for m in ms:
            try:
                close = dt.datetime.fromisoformat(m["close_time"].replace("Z", "+00:00"))
                t = int(close.timestamp() * 1000)
                fs = float(m.get("floor_strike"))
                res = m.get("result")
                ts = series_of(m["event_ticker"])
                if not ts or res not in ("yes", "no"):
                    continue
                kv = {p["t"] // 1000: p["v"] for p in ts}
                kl = bot.http_json("https://data-api.binance.vision/api/v3/klines",
                                   {"symbol": sym, "interval": "1s", "startTime": t - 240000, "endTime": t})
                bv = {int(c[0]) // 1000: float(c[4]) for c in kl}
            except Exception as e:
                print("skip", m.get("ticker"), e)
                continue
            T = t // 1000
            win = res == "yes"
            tally["n"] += 1
            tally["end_ok"] += ((kv.get(T, kv[max(kv)]) >= fs) == win)
            for lead, key in ((45, "45"), (180, "180")):
                k = kv.get(T - lead)
                # Binance: the 60 s average as of that second (the bot's habit), not the raw price
                b = [bv[s] for s in range(T - lead - 59, T - lead + 1) if s in bv]
                if k is None or not b:
                    continue
                kr = (k >= fs) == win
                br = (sum(b) / len(b) >= fs) == win
                tally["k" + key] += kr
                tally["b" + key] += br
                if key == "45":
                    tally["b45_wrong_k_right"] += (kr and not br)
                    tally["k45_wrong_b_right"] += (br and not kr)
                    tally["gap"].append((sum(b) / len(b) - k) / k * 10000)
        g = sorted(tally.pop("gap"))
        print(series, json.dumps(tally), f"Binance minus Kalshi at 45 s, in 1/100 of a percent: median "
              f"{g[len(g) // 2]:.1f}" if g else "")


# ================================================================ 4-month download + re-test (19 Nov, Jan said go)
#
# Rule fixed BEFORE the results (19 Nov, 07:50 UTC): the paper twin `kc_maker_safe_kprice` is kc_maker_safe with
# the Binance check swapped for the same check on Kalshi's own number. z = (Kalshi number now - strike) /
# (typical 1-minute move of the Kalshi number over the last hour x sqrt(1.5) x Kalshi number x sqrt(minutes left)),
# bid only when z >= 2. The sqrt(1.5): Kalshi's number is a 60-second average, which moves only about 2/3 as much
# per minute as the raw price (variance of a 60 s average over a 60 s step = 2/3 of the raw one), so without it the
# check would be looser than the Binance one. Everything else (95c+, one tick in front, 0.75-5.5 min, $10) unchanged.

KIDX = os.path.join(bot.ROOT, "bt_cache", "kidx")
SEC_KEEP = 120      # seconds of the Kalshi number kept before each close
VOL_FIX = math.sqrt(1.5)


def kidx_path(series):
    return os.path.join(KIDX, f"{series}.json.gz")


def fetch(days=125):
    """Kalshi's per-second settle number for every hour of the last `days` days, all 7 coins, from the events that
    close on the hour (each call = the hour before that close). Keeps every minute mark + the last SEC_KEEP seconds
    of each 15-minute window. Resumable. Needs kcrypto's window list (run kcrypto fetch first)."""
    import kcrypto as kc
    os.makedirs(KIDX, exist_ok=True)
    t_end = int(time.time()) - 120
    t0 = t_end - int(days) * 86400
    for series in kc.SERIES:
        t_s = time.time()
        store = kc.rjson(kidx_path(series), {}) or {}
        store.setdefault("done", [])
        store.setdefault("min", {})
        store.setdefault("sec", {})
        done = set(store["done"])
        ms = kc.rjson(os.path.join(kc.CACHE, f"markets_{series}.json.gz"), [])
        evs = sorted({m["t"].rsplit("-", 1)[0]: m["close"] for m in ms
                      if m["close"] % 3600 == 0 and t0 <= m["close"] <= t_end}.items(), key=lambda x: x[1])
        todo = [(e, c) for e, c in evs if e not in done]

        def one(job):
            e, c = job
            try:
                return e, c, series_of(e)
            except Exception as ex:
                return e, c, ex
        bad = 0
        with ThreadPoolExecutor(4) as ex:
            for e, c, ts in ex.map(one, todo):
                if isinstance(ts, Exception) or not ts:
                    bad += 1
                    continue
                kv = {int(p["t"]) // 1000: float(p["v"]) for p in ts if p.get("v") is not None}
                for t, v in kv.items():
                    if t % 60 == 0:
                        store["min"][str(t)] = round(v, 8)
                for close in (c - 2700, c - 1800, c - 900, c):
                    seq = [kv.get(t) for t in range(close - SEC_KEEP + 1, close + 1)]
                    if sum(x is not None for x in seq) >= SEC_KEEP - 5:
                        store["sec"][str(close)] = [None if x is None else round(x, 8) for x in seq]
                store["done"].append(e)
        kc.wjson(kidx_path(series), store)
        print(f"{series}: {len(evs)} hours wanted, {len(todo)} new, {bad} failed, {len(store['min'])} minutes, "
              f"{len(store['sec'])} windows with seconds ({time.time() - t_s:.0f}s)")


def load_kidx():
    import kcrypto as kc
    out = {}
    for series in kc.SERIES:
        st = kc.rjson(kidx_path(series), {}) or {}
        out[series] = ({int(k): v for k, v in (st.get("min") or {}).items()},
                       {int(k): v for k, v in (st.get("sec") or {}).items()})
    return out


def zk_minute(mins, w, t, minutes, side, fix=VOL_FIX):
    """The twin's check: kcrypto.zscore on Kalshi's own number instead of Binance. Positive = our side."""
    k = w.get("strike")
    px = mins.get(t)
    if not k or px is None:
        return None
    rets = []
    for i in range(60):
        a, b = mins.get(t - 60 * (i + 1)), mins.get(t - 60 * i)
        if a and b:
            rets.append(math.log(b / a))
    if len(rets) < 30:
        return None
    sd = math.sqrt(sum(r * r for r in rets) / len(rets)) * fix * px * math.sqrt(max(minutes, 0.5))
    if sd <= 0:
        return None
    z = (px - k) / sd
    return z if side == "yes" else -z


def _row(g):
    lost = sum(1 for r in g if not r["won"])
    pnl = [(1.0 if r["won"] else 0.0) - r["price"] for r in g]
    cost = sum(r["price"] for r in g)
    return {"bets": len(g), "lost": lost, "per100": sum(pnl) / cost * 100 if cost else 0.0,
            "usd10": sum(p / r["price"] * 10 for r, p in zip(g, pnl))}


def retest_maker(kx, L):
    """kc_maker_safe (Binance), kc_maker_safe_usd (Binance + gap) and the twin (Kalshi's number) on the same windows."""
    import exam
    import kcrypto as kc
    windows = [w for w in kc.load_windows() if kx.get(w["s"]) and kx[w["s"]][0]]
    first, last = min(w["close"] for w in windows), max(w["close"] for w in windows)
    day = lambda x: dt.datetime.fromtimestamp(x, UTC).date().isoformat()
    L += ["## 1. kc_maker_safe's check: Binance vs Kalshi's own number", "",
          f"{len(windows)} windows with Kalshi's number, closing {day(first)} to {day(last)}, all 7 coins. Same bid "
          "as the live tracks (one tick in front of the best bid on the leading side, 95c+), placed with M minutes "
          "left, filled only from real trades (kcrypto.py 'fair' fills). Only bids where all three checks could be "
          "computed are counted, so every line uses the same windows. P&L per $100 staked; '$10 bets' = total "
          "if every bet was $10.", "",
          "| Minutes left | Check | Bets | Lost | Per $100 | $10 bets |", "|---|---|---|---|---|---|"]
    keep = {}
    for m in (1, 2, 3, 4, 5):
        sigs = kc.signals(windows, m)
        bys = {s["w"]["t"]: s for s in sigs}
        f = []
        for r in kc.variant_trades(sigs, "improve", 0.95, None):
            if not r["fills"][1]:
                continue
            s = bys[r["tk"]]
            mins = kx[s["w"]["s"]][0]
            r["z"] = kc.zscore(s["w"], s["t"], m, s["side"])
            r["zu"] = kc.zscore_usd(s["w"], s["t"], m, s["side"])
            r["zk"] = zk_minute(mins, s["w"], s["t"], m, s["side"])
            r["zk0"] = zk_minute(mins, s["w"], s["t"], m, s["side"], fix=1.0)
            if None not in (r["z"], r["zu"], r["zk"]):
                f.append(r)
        groups = {"no check (kc_maker)": f,
                  "Binance z 2+ (kc_maker_safe)": [r for r in f if r["z"] >= 2],
                  "Binance + gap (kc_maker_safe_usd)": [r for r in f if r["z"] >= 2 and r["zu"] >= 2],
                  "**Kalshi's number z 2+ (twin)**": [r for r in f if r["zk"] >= 2],
                  "Kalshi's number, no 1.5 fix": [r for r in f if r["zk0"] >= 2],
                  "Kalshi's number z 3+": [r for r in f if r["zk"] >= 3]}
        for k, g in groups.items():
            row = _row(g)
            L.append(f"| {m} | {k} | {row['bets']} | {row['lost']} | {money(row['per100'])} | {money(row['usd10'])} |")
        keep[m] = groups
        print(f"maker {m} min: " + ", ".join(f"{k}: {_row(g)}" for k, g in groups.items()))
    # where they disagree, 3 minutes left
    g = keep[3]
    only_b = [r for r in g["Binance z 2+ (kc_maker_safe)"] if r["zk"] < 2]
    only_k = [r for r in g["**Kalshi's number z 2+ (twin)**"] if r["z"] < 2]
    L += ["", "Where the two checks disagree (3 minutes left):", "",
          "| Bets | Count | Lost | Per $100 |", "|---|---|---|---|"]
    for lab, grp in (("Binance says yes, Kalshi's number says no (the twin skips these)", only_b),
                     ("Kalshi's number says yes, Binance says no (only the twin bets)", only_k)):
        row = _row(grp)
        L.append(f"| {lab} | {row['bets']} | {row['lost']} | {money(row['per100'])} |")
    # by coin, 3 minutes
    L += ["", "By coin, 3 minutes left (bets / lost / per $100):", "", "| Coin | Binance (kc_maker_safe) | Twin |",
          "|---|---|---|"]
    for s in kc.SERIES:
        a = _row([r for r in g["Binance z 2+ (kc_maker_safe)"] if r["s"] == s])
        b = _row([r for r in g["**Kalshi's number z 2+ (twin)**"] if r["s"] == s])
        L.append(f"| {s} | {a['bets']} / {a['lost']} / {money(a['per100'])} | {b['bets']} / {b['lost']} / {money(b['per100'])} |")
    verdicts = {}
    for lab, key in (("kc_maker_safe check on Binance (re-test, 3 min)", "Binance z 2+ (kc_maker_safe)"),
                     ("kc_maker_safe check on Kalshi's own number (twin rule, 3 min)", "**Kalshi's number z 2+ (twin)**")):
        bets = [{"cost": r["price"] * 10, "pay": 10.0 if r["won"] else 0.0, "t": r["t"], "ev": r["tk"]} for r in g[key]]
        verdicts[lab] = exam.score(bets, lab, tries=6, src="kdocs.py run",
                                   note="19 Nov, Kalshi docs dig: same bid, the spot check done on Kalshi's free "
                                        "per-second settle number instead of Binance. Rule fixed before the run.")
    L += ["", "Exam (3 minutes left, $10 bets):", ""]
    for lab, v in verdicts.items():
        L.append(f"- {lab}: {json.dumps(v, default=str)[:600]}")
    L.append("")
    return keep


def retest_fast(kx, L):
    """The 45-second buy (kfastlive): kfast's replay with its Binance model swapped for Kalshi's number."""
    import kcrypto as kc
    import kfast as kf
    windows = kc.load_windows()
    tapes = {}
    for s in kc.SERIES:
        tapes.update({k: kf.compact(v) for k, v in kc.rjson(os.path.join(kf.CACHE, f"tape_{s}.json.gz"), {}).items()})
    windows = [w for w in windows if w["t"] in tapes and w["close"] in kx[w["s"]][1]]
    for w in windows:
        w["spot"] = None
    if not windows:
        L += ["## 2. The 45-second buy", "", "No windows with both a trade tape and Kalshi's number.", ""]
        return
    # one scale per seconds-left, from all windows: how far Kalshi's number moves in its last L seconds,
    # measured in its own recent 1-second moves (a scale only; the side and the line come from the data)
    def recent(sec, L):
        seq = sec[: SEC_KEEP - L]
        d = [b - a for a, b in zip(seq[-61:], seq[-60:]) if a is not None and b is not None]
        return math.sqrt(sum(x * x for x in d) / len(d)) if len(d) > 30 else None
    scale = {}
    for Ls in kf.B_SECONDS:
        xs = []
        for w in windows:
            sec = kx[w["s"]][1][w["close"]]
            a, b, s1 = sec[SEC_KEEP - 1 - Ls], sec[-1], recent(sec, Ls)
            if a is not None and b is not None and s1:
                xs.append(((b - a) / s1) ** 2)
        scale[Ls] = math.sqrt(sum(xs) / len(xs)) if xs else None

    def model_k(w, sp):
        sec = kx[w["s"]][1].get(w["close"])
        k = w.get("strike")
        if not sec or not k:
            return None
        z = {}
        for Ls in kf.B_SECONDS:
            a, s1 = sec[SEC_KEEP - 1 - Ls], recent(sec, Ls)
            if a is None or not s1 or not scale.get(Ls):
                continue
            z[Ls] = (a - k) / (scale[Ls] * s1)
        return {"z": z, "est_yes": (sec[-1] or 0) >= k, "basis": 0.0}
    spots = {s: kf.Spot(sym) for s, sym in kc.SERIES.items()}
    out = {}
    orig = kf.model_window
    for lab, fn in (("Binance", orig), ("Kalshi", model_k)):
        kf.model_window = fn
        rows = {}
        for s in kc.SERIES:
            r, _ = kf.replay([w for w in windows if w["s"] == s], tapes, spots)
            for k, v in r.items():
                rows.setdefault(k, []).extend(v)
        out[lab] = rows
    kf.model_window = orig
    first, last = min(w["close"] for w in windows), max(w["close"] for w in windows)
    day = lambda x: dt.datetime.fromtimestamp(x, UTC).date().isoformat()
    L += ["## 2. The last-seconds buy (the kfastlive idea): Binance vs Kalshi's own number", "",
          f"{len(windows)} windows with a real trade tape and Kalshi's number, closing {day(first)} to {day(last)}. "
          "kfast.py's replay, unchanged, once with its Binance model and once with Kalshi's number deciding the side "
          "and the z. Taker = buy at the next real trade 1-4 s later, with fee; bid = a waiting order filled only by "
          "real trades ('fair'). The z scale for Kalshi's number is set from all windows (one number per "
          "seconds-left), so treat small differences as noise.", "", "| Test | Model | Bets | Lost | Per $100 | $10 bets |",
          "|---|---|---|---|---|---|"]
    tests = [("bid 99.8c, 45 s left, z 2+ (kfastlive main)", ("Bm", 45, 2.0, 0.998)),
             ("bid 99.5c, 45 s left, z 2+", ("Bm", 45, 2.0, 0.995)),
             ("taker, 45 s left, z 4+", ("Bt", 45, 4.0)), ("taker, 45 s left, z 2+", ("Bt", 45, 2.0)),
             ("taker, 20 s left, z 3+", ("Bt", 20, 3.0)), ("bid 99.8c, 20 s left, z 3+", ("Bm", 20, 3.0, 0.998))]
    for lab, key in tests:
        for mdl in ("Binance", "Kalshi"):
            rr = [r for r in out[mdl].get(key, []) if r["fills"][1]]
            row = _row([dict(r, price=r["price"] + r["fee"]) for r in rr])
            L.append(f"| {lab} | {mdl} | {row['bets']} | {row['lost']} | {money(row['per100'])} | {money(row['usd10'])} |")
        print("fast", lab, {m: _row([r for r in out[m].get(key, []) if r["fills"][1]]) for m in out})
    L.append("")


def money(x):
    return f"{'-' if x < 0 else '+'}${abs(x):.2f}"


def run():
    kx = load_kidx()
    L = ["# Kalshi's own settle number vs Binance: the 15-minute crypto tracks re-tested", "",
         f"Generated {bot.iso()}. Code `kdocs.py run` (probe `kd_retest`). Paper only. Jan (19 Nov): \"Download and "
         "do the re-test. After make a paper twin no matter the result, name it clearly.\"", "",
         "Kalshi's number = `GET /live_data/events/{event}`, the CF Benchmarks 60-second average Kalshi settles on, "
         "one value a second, no login (`backtest/kalshi_docs.md`). Binance = what the tracks use today.", ""]
    for s, (mins, sec) in kx.items():
        print(f"{s}: {len(mins)} minutes, {len(sec)} windows with seconds")
    retest_maker(kx, L)
    try:
        retest_fast(kx, L)
    except Exception as e:  # tapes may be missing; the maker part still stands
        import traceback
        traceback.print_exc()
        L += ["## 2. The last-seconds buy", "", f"Not run: {e}", ""]
    os.makedirs(os.path.join(bot.ROOT, "backtest"), exist_ok=True)
    with open(os.path.join(bot.ROOT, "backtest", "kprice.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "retest":   # probe kd_retest: kcrypto 125 days + Kalshi's number + kfast tapes, then the report
        import kcrypto
        import kfast
        kcrypto.fetch(int(os.environ.get("KC_DAYS", 125)))
        fetch(int(os.environ.get("KC_DAYS", 125)))
        kfast.fetch(int(os.environ.get("KF_DAYS", 14)))
        run()
    else:
        {"check": check, "depth": depth, "agree": agree, "fetch": fetch, "run": run}[cmd]()
