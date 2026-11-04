#!/usr/bin/env python3
"""Manual API probe (no pushes, no state changes). Prints raw shapes so the bot can be fixed from the logs."""
import json
import sys
import urllib.parse
import urllib.request

UA = "poly-paper-bot/1.0 (paper trading only)"
BASES = ["https://external-api.kalshi.com/trade-api/v2", "https://api.elections.kalshi.com/trade-api/v2"]


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def show(label, obj, n=2500):
    print(f"== {label}")
    print(json.dumps(obj, indent=None)[:n])


def kalshi():
    base = None
    for b in BASES:
        try:
            res = get(f"{b}/markets", {"limit": 3, "status": "open"})
            base = b
            print("kalshi base OK:", b)
            break
        except Exception as e:
            print("kalshi base FAIL:", b, e)
    if not base:
        return
    show("markets keys", sorted(res.keys()))
    ms = res.get("markets") or []
    if ms:
        show("market keys", sorted(ms[0].keys()))
        show("market sample", ms[0], 4000)
    for params in ({"limit": 5, "status": "open", "mve_filter": "exclude"},
                   {"limit": 5, "status": "open", "min_close_ts": 1793750400, "max_close_ts": 1798761600}):
        try:
            r = get(f"{base}/markets", params)
            print("params OK:", params, "->", [m.get("ticker") for m in r.get("markets", [])], "cursor:", bool(r.get("cursor")))
        except Exception as e:
            print("params FAIL:", params, e)
    # a liquid, non-combo market for orderbook + single lookup
    try:
        r = get(f"{base}/events", {"limit": 5, "status": "open", "with_nested_markets": "true"})
        show("events keys", sorted(r.keys()))
        evs = r.get("events") or []
        if evs:
            show("event keys", sorted(evs[0].keys()))
            show("event sample (trimmed)", {k: v for k, v in evs[0].items() if k != "markets"})
            mk = (evs[0].get("markets") or [{}])[0]
            t = mk.get("ticker")
            if t:
                show("single market", get(f"{base}/markets/{t}"), 3000)
                show("orderbook", get(f"{base}/markets/{t}/orderbook"), 2000)
    except Exception as e:
        print("events/orderbook FAIL:", e)
    # settled market example
    try:
        r = get(f"{base}/markets", {"limit": 2, "status": "settled"})
        for m in r.get("markets", []):
            print("settled:", {k: m.get(k) for k in ("ticker", "status", "result", "settlement_value",
                                                     "settlement_value_dollars", "close_time", "expiration_time")})
    except Exception as e:
        print("settled FAIL:", e)


def poly():
    r = get("https://gamma-api.polymarket.com/markets/keyset", {"closed": "false", "limit": 2})
    ms = r.get("markets") or []
    if ms:
        m = ms[0]
        print("poly description sample:", str(m.get("description"))[:600])
        print("poly resolutionSource:", m.get("resolutionSource"), "| umaResolutionStatuses:", m.get("umaResolutionStatuses"))
    # page size actually served
    r = get("https://gamma-api.polymarket.com/markets/keyset", {"closed": "false", "limit": 500})
    print("poly keyset page size served:", len(r.get("markets") or []))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "kalshi"):
        kalshi()
    if what in ("all", "poly"):
        poly()
