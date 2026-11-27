#!/usr/bin/env python3
"""Kalshi's new 15-minute "up in the next 15 minutes?" families outside crypto (27 Nov 2026): Brent oil, USD/CAD,
AUD/USD, the S&P 500, Treasury yields (2y / 5y / 10y / 30y), plus any siblings. Do our crypto 15-minute rules work there?

PAPER ONLY. Reads public Kalshi history and never trades.

    python3 k15x.py scan          # probe nfx_k15x_scan: every non-crypto 15-minute / hourly "up or down" series, fees,
                                  # settle source, rules, one market in full, size -> bt_cache/nf/k15x/scan.txt
    python3 k15x.py fetch [S,..]  # probe nfx_k15x_fetch: settled windows, 1-minute candles of the whole window, every
                                  # trade of the last 6 minutes (resumable, saves as it goes) -> bt_cache/nf/k15x/
    python3 k15x.py run [log]     # replay kc_maker (bid one tick in front of the leader's best bid late in the window,
                                  # fills only from contracts really sold into it), the 45-second buy, the backward look
                                  # -> backtest/k15x.md tables; `log` adds the exam lines to backtest/ledger.json

Rules replayed (fixed before the first result, copied from the crypto tracks):
  kc_maker   with M minutes left (main M = 3), the leading side (middle 50c+), its best bid 95c+ (also 90c+ looked at):
             bid one tick above it (join when there is no room), hold to the result, maker = no fee on these series?
             (fee read from /series). Fills: contracts really sold into our price after the bid ("tape"): all sales
             below our price + sales at our price only when we were alone there.
  cushion    the outside price is not free for these (FX / yields / Brent / S&P to the minute), so the z check uses
             Kalshi's own per-second settle number from /live_data when it exists (like bot.kmaker_kz).
  kfast      45 s before the close buy the leading side at the first real trade where someone bought that side
             (taker), if that price is 90c-99.5c, pay the taker fee.
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import kcrypto as kc
import yesno

UTC = dt.timezone.utc
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "nf", "k15x")
OUT = os.path.join(ROOT, "backtest")
kget = yesno.kget
EPS = 1e-9
TARGETS = ["KXBRENT15M", "KXUSDCAD15M", "KXAUDUSD15M", "KXINX15M", "KX2YRRATE15M", "KX5YRRATE15M", "KX10YRRATE15M",
           "KX30YRRATE15M"]
LOOK = 16          # candle minutes kept per window (the whole window)
TAPE_SEC = 360     # trade list: the last 6 minutes

_LOG = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    _LOG.append(line)


def save_log(name):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M")


def vol_of(m):
    return bot.fnum(m.get("volume_fp") or m.get("volume"), 0)


def p(series, kind):
    return os.path.join(CACHE, f"{kind}_{series}.json.gz")


# ================================================================ scan
def all_series():
    out, cur = [], None
    for _ in range(50):
        q = {"limit": 1000}
        if cur:
            q["cursor"] = cur
        res = kget("/series", q)
        out += res.get("series") or []
        cur = res.get("cursor")
        if not cur:
            break
    return out


def scan(arg=None):
    ser = all_series()
    say("Kalshi series in all:", len(ser))
    pick = []
    for s in ser:
        tk = str(s.get("ticker") or "")
        t = str(s.get("title") or "").lower()
        if (s.get("category") or "") == "Crypto":
            continue
        if "15M" in tk or "15 min" in t or "next 15" in t or tk.endswith("1H") or tk.endswith("H") and "hour" in t \
                or "up or down" in t or tk in TARGETS:
            pick.append(s)
    say("Non-crypto short up/down candidates:", len(pick))
    now = int(time.time())
    for s in sorted(pick, key=lambda s: s.get("ticker")):
        tk = s.get("ticker")
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000, "min_close_ts": now - 3 * 86400}).get("markets") or []
        except Exception as e:
            say("  failed", tk, str(e)[:80])
            continue
        say(f"  {tk:18s} | {s.get('category')} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | "
            f"3 days: {len(ms)} settled, {sum(map(vol_of, ms)):,.0f} contracts | {str(s.get('title'))[:70]}")
        if tk in TARGETS or ms and sum(map(vol_of, ms)) > 50000:
            say(f"     settle: {json.dumps(s.get('settlement_sources'))[:300]} | tags {s.get('tags')}")
    for tk in TARGETS:
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 200}).get("markets") or []
        except Exception as e:
            say(tk, "failed", e)
            continue
        if not ms:
            say(tk, "no settled markets")
            continue
        m = sorted(ms, key=lambda m: -vol_of(m))[len(ms) // 3]
        say(f"\n== {tk}: one market in full")
        say(json.dumps({k: v for k, v in m.items() if k not in ("rules_secondary",)})[:2500])
        say("rules2:", str(m.get("rules_secondary"))[:600])
        byh = collections.Counter()
        for x in ms:
            byh[dt.datetime.fromtimestamp(kc.tsec(x.get("close_time")) or 0, UTC).strftime("%a %H")] += 1
        say("closes by weekday+hour (last 200):", " ".join(f"{k}:{v}" for k, v in sorted(byh.items())))
        say("per event markets:", collections.Counter(collections.Counter(x.get("event_ticker") for x in ms).values()))
        say("results:", collections.Counter(x.get("result") for x in ms), "middle volume", sorted(map(vol_of, ms))[len(ms) // 2])
        try:
            d = (kget(f"/live_data/events/{m.get('event_ticker')}").get("live_data") or {}).get("details") or {}
            ts = d.get("timeseries") or []
            say(f"live settle number: {len(ts)} points; first {ts[:2]} last {ts[-2:]}; keys {list(d)[:12]}")
        except Exception as e:
            say("live settle number failed", str(e)[:120])
        try:
            res = kget(f"/series/{tk}/markets/{m.get('ticker')}/candlesticks",
                       {"start_ts": kc.tsec(m.get("close_time")) - 900, "end_ts": kc.tsec(m.get("close_time")), "period_interval": 1})
            cs = res.get("candlesticks") or []
            say(f"candles: {len(cs)}; one: {json.dumps(cs[len(cs) // 2])[:600] if cs else None}")
        except Exception as e:
            say("candles failed", str(e)[:120])
        try:
            tr = kget("/markets/trades", {"ticker": m.get("ticker"), "limit": 5}).get("trades") or []
            say("trade sample:", json.dumps(tr[:2])[:600])
        except Exception as e:
            say("trades failed", str(e)[:120])
    try:
        say("historical cutoff", json.dumps(kget("/historical/cutoff")))
    except Exception as e:
        say("cutoff failed", str(e)[:80])
    save_log("scan.txt")


# ================================================================ fetch
START = int(dt.datetime(2026, 10, 1, tzinfo=UTC).timestamp())


def slim(m, series):
    return {"t": m.get("ticker"), "ev": m.get("event_ticker"), "s": series, "close": kc.tsec(m.get("close_time")),
            "open": kc.tsec(m.get("open_time")), "strike": bot.fnum(m.get("floor_strike"), None),
            "cap": bot.fnum(m.get("cap_strike"), None), "st": m.get("strike_type"),
            "settle": bot.fnum(m.get("expiration_value"), None), "res": str(m.get("result") or "").lower(), "vol": vol_of(m)}


def list_all(series, t0, t1):
    out, seen = [], set()
    cut = kc.hist_cutoff()
    for path in ("/markets", "/historical/markets"):
        if path == "/historical/markets" and (not cut or t0 >= cut):
            continue
        cur = None
        for _ in range(300):
            q = {"series_ticker": series, "min_close_ts": t0, "max_close_ts": t1, "limit": 1000}
            if path == "/markets":
                q["status"] = "settled"
            if cur:
                q["cursor"] = cur
            try:
                res = kget(path, q)
            except Exception as e:
                say(f"  {series} {path} failed: {str(e)[:120]}")
                break
            rows = res.get("markets") or []
            for m in rows:
                sm = slim(m, series)
                if sm["t"] and sm["t"] not in seen and sm["res"] in ("yes", "no") and sm["close"]:
                    seen.add(sm["t"])
                    out.append(sm)
            cur = res.get("cursor")
            if not cur or not rows:
                break
    return sorted(out, key=lambda m: m["close"])


def tape(m):
    """Every trade of the last TAPE_SEC seconds: [ts, yes_price, contracts, taker 'y'/'n'], oldest first. None = failed."""
    paths = ["/markets/trades", "/historical/trades"]
    if kc.hist_cutoff() and m["close"] < kc.hist_cutoff():
        paths = paths[::-1]
    for path in paths:
        out, cur, ok = [], None, False
        for _ in range(40):
            q = {"ticker": m["t"], "min_ts": m["close"] - TAPE_SEC, "max_ts": m["close"] + 5, "limit": 1000}
            if cur:
                q["cursor"] = cur
            try:
                res = kget(path, q)
            except Exception:
                break
            rows = res.get("trades") or []
            for x in rows:
                d = bot.parse_iso(x.get("created_time"))
                yp = bot.fnum(x.get("yes_price_dollars"), None)
                if yp is None and x.get("yes_price") is not None:
                    yp = bot.fnum(x.get("yes_price"), 0) / 100
                if d and yp is not None:
                    out.append([round(d.timestamp(), 2), yp, bot.fnum(x.get("count_fp") or x.get("count"), 0),
                                str(x.get("taker_side") or "")[:1]])
            cur = res.get("cursor")
            if not cur or not rows:
                ok = True
                break
        if ok and out:
            return sorted(out)
        if ok and path == paths[-1]:
            return []
    return None


def live_idx(ev):
    """Kalshi's own settle number: {second: value} for the hour before the close (None = failed)."""
    try:
        d = (kget(f"/live_data/events/{ev}").get("live_data") or {}).get("details") or {}
    except Exception as e:
        return None
    ts = d.get("timeseries") or []
    return {str(int(bot.fnum(q.get("t"), 0)) // 1000): round(float(q["v"]), 8) for q in ts if q.get("v") is not None}


def fetch(arg=None):
    t_go = time.time()
    names = [x for x in (arg.split(",") if arg else TARGETS)]
    budget = float(os.environ.get("K15X_MIN", "150")) * 60
    kc.LOOKBACK_MIN = LOOK
    t1 = int(time.time()) - 300
    for series in names:
        t_s = time.time()
        ms = list_all(series, START, t1)
        old = {m["t"]: m for m in (rj(p(series, "markets"), []) or [])}
        for m in ms:
            old[m["t"]] = m
        ms = sorted(old.values(), key=lambda m: m["close"])
        wj(p(series, "markets"), ms)
        say(f"{series}: {len(ms)} settled windows, {iso(ms[0]['close']) if ms else '-'} to {iso(ms[-1]['close']) if ms else '-'}, "
            f"{sum(m['vol'] for m in ms):,.0f} contracts ({time.time() - t_s:.0f}s)")
        if not ms:
            continue
        ms = [m for m in ms if m["vol"] > 0]
        # candles: the whole window by the minute
        cs = rj(p(series, "candles"), {}) or {}
        kc._SAVE[0] = lambda: wj(p(series, "candles"), cs)
        kc._BATCH_OK[0] = None
        kc.fetch_candles(ms, cs)
        kc._SAVE[0] = None
        wj(p(series, "candles"), cs)
        say(f"  candles: {sum(1 for m in ms if cs.get(m['t']))} of {len(ms)} windows ({time.time() - t_s:.0f}s)")
        # trade lists of the last 6 minutes, newest windows first (older ones may come from /historical)
        tr = rj(p(series, "trades"), {}) or {}
        want = [m for m in sorted(ms, key=lambda m: -m["close"]) if m["t"] not in tr]
        bad = 0
        with ThreadPoolExecutor(kc.WORKERS) as ex:
            for c0 in range(0, len(want), 400):
                part = want[c0:c0 + 400]
                for m, out in zip(part, ex.map(tape, part)):
                    if out is None:
                        bad += 1
                    else:
                        tr[m["t"]] = out
                wj(p(series, "trades"), tr)
                print(f"   trades {c0 + len(part)}/{len(want)} ({time.time() - t_s:.0f}s)", flush=True)
                if time.time() - t_go > budget:
                    break
        wj(p(series, "trades"), tr)
        say(f"  trade lists: {len(want)} asked, {bad} failed, {len(tr)} kept, {sum(len(v) for v in tr.values()):,} trades ({time.time() - t_s:.0f}s)")
        # Kalshi's own settle number, by the second for the last 16 minutes, by the minute for the hour
        ix = rj(p(series, "idx"), {}) or {}
        evs = sorted({m["ev"] for m in ms if m["ev"] not in ix}, reverse=True)
        bad = 0
        if time.time() - t_go < budget:
            with ThreadPoolExecutor(4) as ex:
                for c0 in range(0, len(evs), 400):
                    part = evs[c0:c0 + 400]
                    for e, kv in zip(part, ex.map(live_idx, part)):
                        if not kv:
                            bad += 1
                            ix[e] = {}
                            continue
                        last = max(int(k) for k in kv)
                        ix[e] = {k: v for k, v in kv.items() if int(k) % 60 == 0 or int(k) > last - 16 * 60}
                    wj(p(series, "idx"), ix)
                    if time.time() - t_go > budget:
                        break
        wj(p(series, "idx"), ix)
        say(f"  settle number: {len(evs)} asked, {bad} empty/failed, {sum(1 for v in ix.values() if v)} kept ({time.time() - t_s:.0f}s)")
        save_log(f"fetch_{'_'.join(names)[:50]}.txt")
        if time.time() - t_go > budget:
            say("time budget used up; run again to continue")
            break
    save_log(f"fetch_{'_'.join(names)[:50]}.txt")


# ================================================================ replay
ALL = TARGETS + ["KXGOLD15M", "KXSILVER15M", "KXWTI15M", "KXNATGAS15M", "KXCOPPER15M", "KXEURUSD15M", "KXGBPUSD15M",
                 "KXUSDJPY15M", "KXPLATINUM15M", "KXPALLADIUM15M"]
NAMES = {"KXBRENT15M": "Brent oil", "KXUSDCAD15M": "USD/CAD", "KXAUDUSD15M": "AUD/USD", "KXINX15M": "S&P 500",
         "KX2YRRATE15M": "2-year yield", "KX5YRRATE15M": "5-year yield", "KX10YRRATE15M": "10-year yield",
         "KX30YRRATE15M": "30-year yield", "KXGOLD15M": "Gold", "KXSILVER15M": "Silver", "KXWTI15M": "WTI oil",
         "KXNATGAS15M": "Natural gas", "KXCOPPER15M": "Copper", "KXEURUSD15M": "EUR/USD", "KXGBPUSD15M": "GBP/USD",
         "KXUSDJPY15M": "USD/JPY", "KXPLATINUM15M": "Platinum", "KXPALLADIUM15M": "Palladium"}
GROUP = {"FX": ["KXUSDCAD15M", "KXAUDUSD15M", "KXEURUSD15M", "KXGBPUSD15M", "KXUSDJPY15M"],
         "Yields": ["KX2YRRATE15M", "KX5YRRATE15M", "KX10YRRATE15M", "KX30YRRATE15M"],
         "Oil and gas": ["KXBRENT15M", "KXWTI15M", "KXNATGAS15M"],
         "Metals": ["KXGOLD15M", "KXSILVER15M", "KXCOPPER15M", "KXPLATINUM15M", "KXPALLADIUM15M"], "S&P 500": ["KXINX15M"]}


NEWS = ("08:45", "09:00", "09:45", "10:00", "10:15", "14:15", "14:30", "16:00", "16:15")   # New York closes right after data / open / close


def leader(row):
    """khourly.leader: a 99c / $1.00 book counts (1c steps here), empty books (gap over 50c) have none."""
    yb, ya = row[0], row[1]
    if yb is None or ya is None or not (0 <= yb <= ya <= 1) or ya - yb > 0.5:
        return None
    return "yes" if (yb + ya) / 2 >= 0.5 else "no"


def load(series):
    ms = rj(p(series, "markets"), []) or []
    cs = rj(p(series, "candles"), {}) or {}
    tr = rj(p(series, "trades"), {}) or {}
    ix = rj(p(series, "idx"), {}) or {}
    ws = []
    for m in ms:
        c = {r[0]: r[1:] for r in cs.get(m["t"]) or [] if r and r[0]}
        if not c or m["t"] not in tr or not m.get("strike"):
            continue
        kc.fix_cents(c)
        kv = {int(k): v for k, v in (ix.get(m["ev"]) or {}).items()}
        ws.append({**m, "c": c, "tr": tr[m["t"]], "kv": kv})
    return ws


def zk(w, t, minutes, side):
    """Cushion on Kalshi's own settle number (a point price here, not an average: no 1.5 fix): how many usual moves
    until the close the number sits on our side of the target. Last hour's 1-minute moves."""
    import kdocs
    mins = {k: v for k, v in w["kv"].items() if k % 60 == 0}
    return kdocs.zk_minute(mins, w, t, minutes, side, fix=1.0)


def tape_fill(tr, t_place, side, price, front):
    below = at = 0.0
    for ts, yp, n, taker in tr or []:
        if ts <= t_place or taker != ("n" if side == "yes" else "y"):
            continue
        px = yp if side == "yes" else 1 - yp
        if px < price - EPS:
            below += n
        elif px <= price + EPS:
            at += n
    return below + (at if front else 0.0)


def maker_rows(ws, minutes=3, level=0.95):
    out = []
    for w in ws:
        t = w["close"] - 60 * minutes
        row = w["c"].get(t)
        side = leader(row) if row else None
        if not side:
            continue
        bid, ask, _, _ = kc.side_view(row, side)
        if bid < level - EPS or bid >= 1 - EPS:
            continue
        price = round(bid + 0.01, 2)
        front = price < ask - EPS
        if not front:
            price = bid
        out.append({"tk": w["t"], "s": w["s"], "t": t, "close": w["close"], "side": side, "bid": bid, "ask": ask, "price": price,
                    "front": front, "won": w["res"] == side, "sold": tape_fill(w["tr"], t, side, price, front),
                    "z": zk(w, t, minutes, side), "m": minutes, "w": w})
    return out


def fee(c, px):
    return math.ceil(0.07 * c * px * (1 - px) * 100 - 1e-9) / 100


def taker_rows(ws, sec=45, lo=0.90, hi=0.99, look=60):
    """The 45-second buy: the leader at the minute mark before, then the first real trade from `sec` before the close
    where someone BOUGHT that side; we pay that price + the taker fee, at most the contracts bought that second."""
    out = []
    for w in ws:
        t0 = w["close"] - sec
        row = w["c"].get(w["close"] - look)
        side = leader(row) if row else None
        if not side:
            continue
        hit = None
        for ts, yp, n, tk in w["tr"]:
            if ts < t0 or ts >= w["close"]:
                continue
            if tk == ("y" if side == "yes" else "n"):
                px = yp if side == "yes" else 1 - yp
                if hit is None:
                    hit = [ts, px, 0.0]
                if int(ts) == int(hit[0]) and abs(px - hit[1]) < EPS:
                    hit[2] += n
                elif ts > hit[0] + 1:
                    break
        if not hit or not (lo - EPS <= hit[1] <= hi + EPS):
            continue
        out.append({"tk": w["t"], "s": w["s"], "t": hit[0], "close": w["close"], "side": side, "price": hit[1], "sold": hit[2],
                    "won": w["res"] == side, "z": zk(w, w["close"] - 60, 1, side), "taker": True, "w": w})
    return out


def money(x, d=2):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.{d}f}"


def bets_of(rows, usd=4):
    """Bets at `usd` a bid; contracts = what really traded into us (at most our size)."""
    out = []
    for r in rows:
        need = int(usd / r["price"] + EPS)
        got = min(need, int(r["sold"] or 0))
        if got < 1:
            continue
        f = fee(got, r["price"]) if r.get("taker") else 0.0
        out.append({"cost": got * r["price"] + f, "pay": float(got) if r["won"] else 0.0, "t": r["t"], "ev": str(r["close"]),
                    "sh": got, "s": r["s"], "won": r["won"], "price": r["price"], "full": got >= need, "tk": r["tk"]})
    return out


def card(bs):
    cost = sum(b["cost"] for b in bs)
    pnl = sum(b["pay"] - b["cost"] for b in bs)
    return len(bs), sum(not b["won"] for b in bs), cost, pnl, (pnl / cost * 100 if cost else 0.0)


def fmt(bs, days):
    n, lost, cost, pnl, per = card(bs)
    return f"{n} | {lost} | {money(per)} | {money(pnl)} | {money(pnl / days if days else 0)}"


def calib(ws, minutes):
    """Is the leader's price fair late in the window? Leader's mid by band vs how often it won."""
    bands = [(0.5, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 0.98), (0.98, 1.0)]
    out = {b: [0, 0, 0.0, 0.0] for b in bands}
    for w in ws:
        row = w["c"].get(w["close"] - 60 * minutes)
        side = leader(row) if row else None
        if not side:
            continue
        bid, ask, _, _ = kc.side_view(row, side)
        mid = (bid + ask) / 2
        for b in bands:
            if b[0] <= mid < b[1] + (EPS if b[1] == 1.0 else 0):
                o = out[b]
                o[0] += 1
                o[1] += w["res"] == side
                o[2] += mid
                o[3] += bid
    return out


def run(arg=None):
    import exam
    log = arg == "log"
    L = []

    def P(*a):
        line = " ".join(str(x) for x in a)
        print(line, flush=True)
        L.append(line)
    data = {}
    for s in ALL:
        ws = load(s)
        if ws:
            data[s] = ws
    if not data:
        print("no data; pull bt_cache/nf/k15x first")
        return
    P("## Data\n")
    P("| Series | What | Windows with candles + trade list | From | To | Days | Contracts a window (middle) |")
    P("|---|---|---|---|---|---|---|")
    span = {}
    for s, ws in data.items():
        d = (ws[-1]["close"] - ws[0]["close"]) / 86400
        span[s] = (ws[0]["close"], ws[-1]["close"], max(d, 1))
        v = sorted(w["vol"] for w in ws)
        P(f"| {s} | {NAMES.get(s, s)} | {len(ws):,} | {iso(ws[0]['close'])[:10]} | {iso(ws[-1]['close'])[:10]} | {d:.0f} | {v[len(v) // 2]:,.0f} |")
    # 1. fairness
    P("\n## 1. Is the late price fair? Leader's middle price vs how often it won (3 minutes and 1 minute left)\n")
    P("| Group | Left | 50-70c | 70-80c | 80-90c | 90-95c | 95-98c | 98c+ |")
    P("|---|---|---|---|---|---|---|---|")
    for g, ss in GROUP.items():
        ws = [w for s in ss if s in data for w in data[s]]
        if not ws:
            continue
        for mnt in (3, 1):
            c = calib(ws, mnt)
            cells = []
            for b, (n, won, msum, _) in c.items():
                cells.append(f"{n}: won {won / n * 100:.0f} of 100 at {msum / n * 100:.0f}c" if n else "-")
            P(f"| {g} | {mnt} min | " + " | ".join(cells) + " |")
    # 2. maker rule grid on the first half, per group
    P("\n## 2. kc_maker (bid 1c in front of the leader's best bid, hold to the result), $4 bids, fills = contracts really sold into us\n")
    P("First half of each series' days picks; second half checks. Bets | lost | per $100 | profit | per day.\n")
    P("| Group | Minutes left | Best bid at least | Cushion bar | First half | Fresh second half |")
    P("|---|---|---|---|---|---|")
    grid = []
    tries = 0
    for g, ss in GROUP.items():
        have = [s for s in ss if s in data]
        if not have:
            continue
        mids = {s: (span[s][0] + span[s][1]) / 2 for s in have}
        for mnt in (1, 2, 3, 5):
            for lev in (0.90, 0.95):
                rows = [r for s in have for r in maker_rows(data[s], mnt, lev)]
                for bar in (None, 2.0, 2.3, 3.0):
                    tries += 1
                    rr = [r for r in rows if bar is None or (r["z"] is not None and r["z"] >= bar)]
                    b1 = bets_of([r for r in rr if r["t"] < mids[r["s"]]])
                    b2 = bets_of([r for r in rr if r["t"] >= mids[r["s"]]])
                    d1 = max(span[s][2] for s in have) / 2
                    grid.append((g, mnt, lev, bar, b1, b2, d1))
                    P(f"| {g} | {mnt} | {lev * 100:.0f}c | {bar or 'none'} | {fmt(b1, d1)} | {fmt(b2, d1)} |")
    # the crypto rules as they are (fixed before): plain kc_maker = 3 min, 95c, no cushion; safe = cushion 2.3
    P("\n## 3. The crypto rules unchanged, every series pooled (3 minutes left, 95c+), exam\n")
    allws = [w for ws in data.values() for w in ws]
    allmid = {s: (span[s][0] + span[s][1]) / 2 for s in data}
    days_all = max(v[2] for v in span.values())
    cards = {}
    for name, bar in (("kc_maker", None), ("kc_maker_safe_usd (cushion 2.3 on Kalshi's number)", 2.3)):
        rows = [r for s in data for r in maker_rows(data[s], 3, 0.95) if bar is None or (r["z"] is not None and r["z"] >= bar)]
        for usd in (4, 10):
            bs = bets_of(rows, usd)
            b1 = [b for b in bs if b["t"] < allmid[b["s"]]]
            b2 = [b for b in bs if b["t"] >= allmid[b["s"]]]
            P(f"- {name}, ${usd} bids: all {fmt(bs, days_all)}; first half {fmt(b1, days_all / 2)}; fresh half {fmt(b2, days_all / 2)}")
        bs = bets_of(rows, 4)
        fresh = [b for b in bs if b["t"] >= allmid[b["s"]]]
        c2 = exam.score(fresh, f"{name}, fresh second half only", tries=1, prereg=True, log=False, quiet=True)
        P(f"  EXAM fresh half only (rule fixed before): {c2['verdict']} | {c2['bets']} bets, {c2.get('groups')} separate | "
          f"{money(c2.get('per100') or 0)} per $100 (luck {c2.get('lo100')} to {c2.get('hi100')}) | worst case {c2.get('floor100')}")
        cards[name + " (fresh half)"] = c2
        cards[name] = exam.score(bs, f"{name} on Kalshi's new non-crypto 15-minute windows (FX, yields, oil, metals, S&P; $4 bids, tape fills)",
                                 tries=tries, src="k15x.py run, backtest/k15x.md", log=log, quiet=False)
        P(f"  EXAM {name}: {cards[name]['verdict']} | {cards[name]['bets']} bets, {cards[name].get('groups')} separate | "
          f"{money(cards[name].get('per100') or 0)} per $100 (luck {cards[name].get('lo100')} to {cards[name].get('hi100')}) | "
          f"halves {cards[name].get('half1')} / {cards[name].get('half2')} | worst case {cards[name].get('floor100')}")
        per_s = collections.defaultdict(list)
        for b in bs:
            per_s[b["s"]].append(b)
        P("  per series: " + "; ".join(f"{NAMES.get(s, s)} {fmt(v, span[s][2])}" for s, v in sorted(per_s.items())))
    # 3b. harder fill check and by group for the cushion-2.3 rule
    P("\n## 3b. kc_maker_safe_usd, harder checks ($4 bids)\n")
    safe = [r for s in data for r in maker_rows(data[s], 3, 0.95) if r["z"] is not None and r["z"] >= 2.3]
    strict = [dict(r, sold=tape_fill(r["w"]["tr"], r["t"], r["side"], r["price"], False)) for r in safe]
    late = [dict(r, sold=tape_fill(r["w"]["tr"], r["t"] + 20, r["side"], r["price"], r["front"])) for r in safe]
    for nm, rr in (("only contracts sold BELOW our price count", strict), ("our bid placed 20 s late", late)):
        bs = bets_of(rr, 4)
        b1 = [b for b in bs if b["t"] < allmid[b["s"]]]
        b2 = [b for b in bs if b["t"] >= allmid[b["s"]]]
        P(f"- {nm}: all {fmt(bs, days_all)}; first half {fmt(b1, days_all / 2)}; fresh half {fmt(b2, days_all / 2)}")
    for g, ss in GROUP.items():
        bs = bets_of([r for r in safe if r["s"] in ss], 4)
        c = exam.score(bs, f"kc_maker_safe_usd on Kalshi 15-minute {g}", tries=tries, log=False, quiet=True)
        P(f"- {g}: {fmt(bs, days_all)} | exam {c['verdict']} ({money(c.get('per100') or 0)} per $100, luck {c.get('lo100')} to {c.get('hi100')}, halves {c.get('half1')} / {c.get('half2')})")
    bys = collections.defaultdict(lambda: [0.0, 0])
    for b in bets_of(safe, 4):
        wk = dt.datetime.fromtimestamp(b["t"], UTC).strftime("%G-W%V")
        bys[wk][0] += b["pay"] - b["cost"]
        bys[wk][1] += 1
    P("- by week: " + "; ".join(f"{k} {money(v[0])} ({v[1]} bets)" for k, v in sorted(bys.items())))
    bb = sorted(bets_of(safe, 4), key=lambda b: b["pay"] - b["cost"])
    tot = sum(b["pay"] - b["cost"] for b in bb)
    P(f"- without the best 20 wins: {money(tot - sum(b['pay'] - b['cost'] for b in bb[-20:]))} (all {money(tot)}); one loss costs about "
      f"{money(-(bb[0]['pay'] - bb[0]['cost']))}, a typical win {money(sorted(b['pay'] - b['cost'] for b in bb)[len(bb) // 2])}")
    # 4. the 45-second buy
    P("\n## 4. The 45-second buy (kfast): first real buy of the leader in the last 45 s at 90-99c, taker fee paid, $10\n")
    for zbar in (None, 4.0):
        rows = [r for s in data for r in taker_rows(data[s]) if zbar is None or (r["z"] is not None and r["z"] >= zbar)]
        bs = bets_of(rows, 10)
        b1 = [b for b in bs if b["t"] < allmid[b["s"]]]
        b2 = [b for b in bs if b["t"] >= allmid[b["s"]]]
        P(f"- cushion {zbar or 'none'}: all {fmt(bs, days_all)}; first half {fmt(b1, days_all / 2)}; fresh half {fmt(b2, days_all / 2)}")
        for band in ((0.90, 0.95), (0.95, 0.98), (0.98, 0.995)):
            g = [b for b in bs if band[0] - EPS <= b["price"] < band[1] - EPS]
            P(f"    bought at {band[0] * 100:.0f}-{band[1] * 100:.1f}c: {fmt(g, days_all)}")
        nm = (f"kfast {'plain' if zbar is None else 'cushion 4+'}: 45-second buy on Kalshi's non-crypto 15-minute windows ($10)")
        c = exam.score(bs, nm, tries=tries + 2, src="k15x.py run", log=log)
        cards[nm] = c
        P(f"  EXAM: {c['verdict']} | {c['bets']} bets | {money(c.get('per100') or 0)} per $100 | halves {c.get('half1')} / {c.get('half2')}")
    # 4b. backward-look lead: the leader looks too cheap at 50-90c in the last minutes (table 1). Buy it at the first
    # real buy on the tape (taker price + fee), 2 minutes and 1 minute left, by price band; first half vs fresh half.
    P("\n## 4b. Backward look: buy the leader at 50-90c with 1-2 minutes left at the first real buy on the tape, fee paid, $10\n")
    P("| Group | Left | Bought at | All: bets / lost / per $100 / profit / a day | First half | Fresh half |")
    P("|---|---|---|---|---|---|")
    for g, ss in list(GROUP.items()) + [("All", list(data))]:
        have = [s for s in ss if s in data]
        if not have:
            continue
        for sec in (120, 60):
            for band in ((0.5, 0.7), (0.7, 0.8), (0.8, 0.9)):
                rows = [r for s in have for r in taker_rows(data[s], sec, band[0], band[1] - 0.001, look=sec + 60)]
                bs = bets_of(rows, 10)
                b1 = [b for b in bs if b["t"] < allmid[b["s"]]]
                b2 = [b for b in bs if b["t"] >= allmid[b["s"]]]
                P(f"| {g} | {sec // 60} min | {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {fmt(bs, days_all)} | {fmt(b1, days_all / 2)} | {fmt(b2, days_all / 2)} |")
                if g == "All":
                    nm = f"buy the 15-minute leader at {band[0] * 100:.0f}-{band[1] * 100:.0f}c with {sec // 60} min left, Kalshi non-crypto (taker, $10)"
                    c = exam.score(bs, nm, tries=tries + 20, src="k15x.py run (backward look)", log=log, quiet=True)
                    cards[nm] = c
                    P(f"|  | EXAM | {c['verdict']} | {c['bets']} bets, {c.get('groups')} separate, {money(c.get('per100') or 0)} per $100, luck {c.get('lo100')} to {c.get('hi100')} | halves {c.get('half1')} | {c.get('half2')} |")
    # 5. the losses one by one (main maker rule)
    rows = [r for s in data for r in maker_rows(data[s], 3, 0.95)]
    bs = {b["tk"]: b for b in bets_of(rows, 4)}
    P("\n## 5. Biggest losses of kc_maker (3 min, 95c+, $4), one by one\n")
    P("| Close (UTC) | Series | Side | Our bid | Cushion | Contracts sold into us | Target | Settle | Lost |")
    P("|---|---|---|---|---|---|---|---|---|")
    lost = sorted([r for r in rows if r["tk"] in bs and not r["won"]], key=lambda r: bs[r["tk"]]["pay"] - bs[r["tk"]]["cost"])
    for r in lost[:25]:
        w = r["w"]
        zt = "-" if r["z"] is None else f"{r['z']:.1f}"
        P(f"| {iso(r['close'])} | {NAMES.get(r['s'])} | {r['side']} | {r['price'] * 100:.0f}c | {zt} | "
          f"{r['sold']:,.0f} | {w['strike']} | {w.get('settle')} | {money(bs[r['tk']]['pay'] - bs[r['tk']]['cost'])} |")
    # 6. backward look: what did losing leaders share?
    P("\n## 6. Backward look: leaders at 95c+ with 3 minutes left, by what they had beforehand (all signals, not only filled)\n")
    feats = {
        "cushion on Kalshi's number": lambda r: "none" if r["z"] is None else ("under 1" if r["z"] < 1 else "1-2" if r["z"] < 2 else "2-3" if r["z"] < 3 else "3+"),
        "hour (UTC)": lambda r: f"{dt.datetime.fromtimestamp(r['close'], UTC).hour // 4 * 4:02d}-{dt.datetime.fromtimestamp(r['close'], UTC).hour // 4 * 4 + 3:02d}",
        "weekday": lambda r: dt.datetime.fromtimestamp(r["close"], UTC).strftime("%a"),
        "best bid": lambda r: f"{r['bid'] * 100:.0f}c",
        "gap to the ask": lambda r: f"{round((r['ask'] - r['bid']) * 100)}c",
        "series group": lambda r: next((g for g, ss in GROUP.items() if r["s"] in ss), "?"),
        "side": lambda r: r["side"],
        "close time (New York)": lambda r: (dt.datetime.fromtimestamp(r["close"], UTC) - dt.timedelta(hours=5 if r["close"] > 1793570400 else 4)).strftime("%H:%M")
        if (dt.datetime.fromtimestamp(r["close"], UTC) - dt.timedelta(hours=5 if r["close"] > 1793570400 else 4)).strftime("%H:%M") in NEWS else "other",
    }
    for fname, fn in feats.items():
        agg = collections.defaultdict(lambda: [0, 0, 0.0])
        for r in rows:
            a = agg[fn(r)]
            a[0] += 1
            a[1] += not r["won"]
            a[2] += r["price"]
        P(f"- {fname}: " + "; ".join(f"{k}: {a[1]} lost of {a[0]} (price says {a[0] - a[2]:.1f})" for k, a in sorted(agg.items())))
    # 7. size: how many contracts really trade into the bid
    P("\n## 7. Size: profit at bigger bids (kc_maker_safe_usd, 3 min, 95c+), and how often the whole bid filled\n")
    rows2 = [r for r in rows if r["z"] is not None and r["z"] >= 2.3]
    for usd in (4, 10, 25, 50, 100, 250):
        for nm, rr in (("plain", rows), ("cushion 2.3", rows2)):
            bs2 = bets_of(rr, usd)
            n, lost_, cost, pnl, per = card(bs2)
            full = sum(b["full"] for b in bs2)
            byday = collections.defaultdict(float)
            for b in bs2:
                byday[b["t"] // 86400] += b["pay"] - b["cost"]
            worst = min(byday.values()) if byday else 0
            out = collections.defaultdict(float)
            for b in bs2:
                out[b["ev"]] += b["cost"]
            o = sorted(out.values())
            omax, o99 = (o[-1], o[int(len(o) * 0.99)]) if o else (0, 0)
            P(f"- ${usd} bids, {nm}: {n} bets ({full} filled whole), {money(pnl)} in all, {money(pnl / days_all)} a day, "
              f"{money(per)} per $100, worst day {money(worst)}, money out at one close: most {money(omax)}, 99 in 100 under {money(o99)}")
    with open(os.path.join(CACHE, "run.txt"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    with open(os.path.join(CACHE, "cards.json"), "w") as fh:
        json.dump(cards, fh, default=str)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    {"scan": scan, "fetch": fetch, "run": run}[cmd](arg)
