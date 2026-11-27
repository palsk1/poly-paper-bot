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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    {"scan": scan, "fetch": fetch}[cmd](arg)
