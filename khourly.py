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


def scan():
    ser = kget("/series", {"category": "Crypto"}).get("series") or []
    print("Kalshi Crypto series:", len(ser), collections.Counter(s.get("frequency") for s in ser).most_common())
    now = int(time.time())
    rows = []
    for s in sorted(ser, key=lambda s: s.get("ticker") or ""):
        tk = s.get("ticker")
        if s.get("frequency") in ("one_off", "custom", "annual", "yearly"):
            continue
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000,
                                   "min_close_ts": now - 2 * 86400}).get("markets") or []
        except Exception as e:
            print("  failed", tk, str(e)[:80])
            continue
        if not ms:
            continue
        ev = collections.Counter(m.get("event_ticker") for m in ms)
        vol = sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ms)
        life = sorted((kc.tsec(m.get("close_time")) or 0) - (kc.tsec(m.get("open_time")) or 0) for m in ms)
        rows.append((vol, tk))
        print(f"  {tk:18s} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | 2 days: {len(ev)} rounds, "
              f"{len(ms)} markets{'+' if len(ms) == 1000 else ''}, {vol:,.0f} contracts | open for {life[len(life) // 2] / 3600:.1f} h (middle) | "
              f"{str(s.get('title'))[:60]}", flush=True)
    for _, tk in sorted(rows, reverse=True):
        if tk.endswith("15M"):
            continue
        ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000,
                               "min_close_ts": now - 2 * 86400}).get("markets") or []
        ev = collections.defaultdict(list)
        for m in ms:
            ev[m.get("event_ticker")].append(m)
        ek = sorted(ev, key=lambda e: -sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ev[e]))
        print(f"\n===== {tk}: rounds by close hour (UTC) and size")
        byh = collections.defaultdict(float)
        for e, mm in ev.items():
            c = kc.tsec(mm[0].get("close_time")) or 0
            byh[dt.datetime.fromtimestamp(c, UTC).hour] += sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in mm)
        print("  contracts by close hour:", {h: round(v) for h, v in sorted(byh.items())})
        e = ek[len(ek) // 2] if ek else None
        if not e:
            continue
        mm = sorted(ev[e], key=lambda m: bot.fnum(m.get("floor_strike"), 0) or bot.fnum(m.get("cap_strike"), 0))
        print(f"  a middle-sized round {e}: {len(mm)} markets, open {mm[0].get('open_time')} close {mm[0].get('close_time')}")
        print("  full market:", json.dumps({k: v for k, v in mm[len(mm) // 2].items() if "rules_secondary" not in k})[:2500])
        for m in mm:
            v = bot.fnum(m.get("volume_fp") or m.get("volume"), 0)
            if v > 0:
                print(f"    {m.get('ticker'):38s} {m.get('strike_type')} floor {m.get('floor_strike')} cap {m.get('cap_strike')} "
                      f"vol {v:,.0f} result {m.get('result')} settle {m.get('expiration_value')}")
        busy = max(mm, key=lambda m: bot.fnum(m.get("volume_fp") or m.get("volume"), 0))
        kc.show(f"trades {busy.get('ticker')}", lambda: get_trades(busy.get("ticker"), 6))
        c = kc.tsec(busy.get("close_time"))
        kc.show("candles last 5 min", lambda: kget("/markets/candlesticks", {"market_tickers": busy.get("ticker"), "start_ts": c - 300,
                                                                            "end_ts": c, "period_interval": 1}))
        def live():
            r = kget(f"/live_data/events/{e}")
            d = (r.get("live_data") or {}).get("details") or {}
            ts = d.get("timeseries") or []
            return {"keys": list(d)[:20], "points": len(ts), "first": ts[:2], "last": ts[-2:]}
        kc.show(f"live_data {e}", live)
    pm_scan()


def get_trades(ticker, limit=1000):
    return kget("/markets/trades", {"ticker": ticker, "limit": limit})


def pm_scan():
    """Polymarket: which crypto events closed in the last 3 days, grouped into families (names without dates)."""
    import habits
    G = habits.G
    since = dt.datetime.fromtimestamp(time.time() - 3 * 86400, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    F = collections.defaultdict(lambda: {"n": 0, "vol": 0.0, "mk": 0, "ex": None, "life": []})
    for tag in ("crypto", "crypto-prices", "up-or-down", "bitcoin"):
        off = 0
        for _ in range(80):
            try:
                r = bot.http_json(f"{G}/events", {"closed": "true", "limit": 50, "offset": off, "tag_slug": tag,
                                                  "end_date_min": since, "order": "endDate", "ascending": "false"})
            except Exception as e:
                print("  gamma failed", tag, str(e)[:100])
                break
            rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
            for e in rows:
                k = habits.fam(e.get("slug"))
                f = F[k]
                if e.get("slug") in f.setdefault("seen", set()):
                    continue
                f["seen"].add(e.get("slug"))
                f["n"] += 1
                f["vol"] += float(e.get("volume") or 0)
                f["mk"] += len(e.get("markets") or [])
                f["ex"] = e
            off += 50
            if len(rows) < 50:
                break
        print(f"Polymarket tag {tag}: scanned to offset {off}", flush=True)
    print("Polymarket crypto families that closed in the last 3 days:")
    for k, f in sorted(F.items(), key=lambda kv: -kv[1]["vol"])[:80]:
        e = f["ex"]
        m0 = (e.get("markets") or [{}])[0]
        print(f"  {f['n']:4d} events | {f['mk']:5d} markets | ${f['vol']:12,.0f} | {k} | e.g. {e.get('slug')} | start {str(m0.get('startDate'))[:16]} "
              f"end {str(m0.get('endDate'))[:16]} | fee {m0.get('feeType') or m0.get('fee')} maker {m0.get('makerBaseFee')} taker {m0.get('takerBaseFee')} "
              f"| settles on {str(m0.get('resolutionSource'))[:60]}", flush=True)
    for pat in ("up-or-down", "above", "price-on"):
        ex = next((f["ex"] for k, f in sorted(F.items(), key=lambda kv: -kv[1]["vol"]) if pat in k and "bitcoin" in k and "m" not in k.split("-")[-1:]), None)
        if ex:
            m0 = (ex.get("markets") or [{}])[0]
            print(f"\n== {ex.get('slug')}: {json.dumps({k: m0.get(k) for k in ('question', 'description', 'feesEnabled', 'feeType', 'feeSchedule', 'rewardsMinSize', 'rewardsMaxSpread', 'volume', 'orderPriceMinTickSize', 'conditionId')})[:1800]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = None
    if "_" in cmd:
        cmd, arg = cmd.split("_", 1)
    {"scan": scan}[cmd]()
