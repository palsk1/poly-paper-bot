"""Kalshi docs read-through (19 Nov 2026): try the public Kalshi endpoints we have never used.

Jan asked whether we had read Kalshi's API docs (docs.kalshi.com). We read all of them (write-up
`backtest/kalshi_docs.md`). Most new features need a logged-in API key (order tools, the CF Benchmarks
price feed, every websocket). This script only tries the ones that need no login, from GitHub Actions:

    python3 kdocs.py check   # probe kd_check: live price chart behind a 15-minute crypto event, fee changes,
                             # exchange schedule, many order books in one call, weather index, endpoint costs

No key, no orders, read-only.
"""
import datetime as dt
import json
import sys
import time

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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check}[cmd]()
