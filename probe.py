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


def endgame():
    """Open markets past or near their end date: how 'result submitted' shows up."""
    import datetime as dt
    from collections import Counter
    now = dt.datetime.now(dt.timezone.utc)
    f = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"closed": "false", "limit": 100, "end_date_min": f(now - dt.timedelta(days=30)),
              "end_date_max": f(now + dt.timedelta(days=1))}
    ms, cursor = [], None
    for _ in range(30):
        p = dict(params)
        if cursor:
            p["after_cursor"] = cursor
        r = get("https://gamma-api.polymarket.com/markets/keyset", p)
        ms += r.get("markets") or []
        cursor = r.get("next_cursor")
        if not cursor:
            break
    print(f"== endgame window: {len(ms)} open markets ending between -30d and +1d")
    st = Counter(json.dumps(m.get("umaResolutionStatuses")) for m in ms)
    print("umaResolutionStatuses values:", st.most_common(12))
    print("other status-ish keys:", sorted({k for m in ms for k in m if any(s in k.lower() for s in
          ("resol", "uma", "accept", "closed", "active", "automatic", "archiv", "ready", "pending"))}))
    print("acceptingOrders:", Counter(str(m.get("acceptingOrders")) for m in ms).most_common())
    hi = []
    for m in ms:
        try:
            pr = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except ValueError:
            continue
        if pr and max(pr) >= 0.95 and max(pr) < 0.995:
            hi.append(m)
    print(f"== {len(hi)} with a side at 95-99.5c. Samples:")
    for m in hi[:25]:
        print({k: m.get(k) for k in ("question", "endDateIso", "outcomePrices", "bestBid", "bestAsk", "acceptingOrders",
                                     "umaResolutionStatuses", "umaEndDate", "liquidityNum", "sportsMarketType",
                                     "feesEnabled", "closedTime", "resolvedBy")})


def events():
    """Multi-candidate events: event fields, negRisk flags and nested market fields."""
    r = get("https://gamma-api.polymarket.com/events/keyset", {"closed": "false", "limit": 100})
    evs = r.get("events") or []
    print("== events page:", len(evs), "keys:", sorted(r.keys()))
    if evs:
        print("event keys:", sorted(evs[0].keys()))
    shown = 0
    for e in evs:
        ms = e.get("markets") or []
        if len(ms) >= 3 and (e.get("negRisk") or e.get("enableNegRisk")):
            print("\n-- event:", {k: e.get(k) for k in ("title", "slug", "negRisk", "enableNegRisk", "negRiskAugmented",
                                                      "showAllOutcomes", "endDate", "liquidity", "mutuallyExclusive")})
            print("   nested market keys:", sorted(ms[0].keys()))
            asks = [float(m.get("bestAsk") or 0) for m in ms]
            print(f"   markets {len(ms)}, sum bestAsk {sum(asks):.3f}")
            for m in ms[:12]:
                print("   ", {k: m.get(k) for k in ("groupItemTitle", "bestAsk", "bestBid", "outcomePrices", "negRiskOther",
                                                     "active", "closed", "acceptingOrders")})
            shown += 1
            if shown >= 3:
                break


def activity():
    addr = json.load(open("config.json"))["leader"]["address"]
    for path in ("v2/activity", "v2/trades", "v2/user/activity", "v2/users/activity", "v2/trades/user",
                 "v2/closed-positions", "activity", "trades"):
        try:
            res = get(f"https://data-api.polymarket.com/{path}", {"user": addr, "limit": 3})
            show(f"data-api /{path} (his last 3)", res, 2000)
        except Exception as e:
            print(f"/{path} failed: {e}")


def sells():
    """All his SELL trades in the last 500 trades, one line each (used to backfill state/his_exits.json)."""
    addr = json.load(open("config.json"))["leader"]["address"]
    res = get("https://data-api.polymarket.com/v2/trades", {"user": addr, "limit": 500})
    rows = res.get("data", []) if isinstance(res, dict) else res
    print("== his sells (ts, token, size, price, outcome, title)")
    for r in rows:
        if str(r.get("side")).upper() == "SELL":
            print("SELL", json.dumps([r.get("timestamp"), r.get("token_id"), r.get("size"), r.get("price"),
                                      r.get("outcome"), r.get("title"), r.get("slug")]))
    print("total trades returned:", len(rows), "oldest ts:", min((r.get("timestamp") or 0) for r in rows) if rows else None)


def exits_study():
    """His trades grouped per token, with each market's end date and final price: when does he sell early?"""
    addr = json.load(open("config.json"))["leader"]["address"]
    rows, cursor = [], None
    for _ in range(20):
        params = {"user": addr, "limit": 500}
        if cursor:
            params["cursor"] = cursor
        res = get("https://data-api.polymarket.com/v2/trades", params)
        rows += res.get("data", []) if isinstance(res, dict) else res
        cursor = ((res.get("pagination") or {}) if isinstance(res, dict) else {}).get("next_cursor")
        if not cursor:
            break
    print("trades:", len(rows))
    by = {}
    for r in rows:
        by.setdefault(r.get("token_id"), []).append(r)
    for tok, rs in by.items():
        sells = [r for r in rs if str(r.get("side")).upper() == "SELL"]
        if not sells:
            continue
        buys = [r for r in rs if str(r.get("side")).upper() == "BUY"]
        slug = rs[0].get("slug")
        end, final = None, None
        try:
            m = get(f"https://gamma-api.polymarket.com/markets/slug/{urllib.parse.quote(slug)}")
            m = m[0] if isinstance(m, list) else m
            end = m.get("endDateIso") or m.get("endDate")
            toks = json.loads(m.get("clobTokenIds") or "[]")
            prices = json.loads(m.get("outcomePrices") or "[]")
            if m.get("closed") and tok in toks:
                final = prices[toks.index(tok)]
        except Exception as e:
            end = f"err {e}"
        out = {"t": rs[0].get("title"), "o": rs[0].get("outcome"), "end": end, "final": final,
               "buys": [[b.get("timestamp"), round(float(b.get("size") or 0), 2), round(float(b.get("price") or 0), 4)] for b in buys],
               "sells": [[s.get("timestamp"), round(float(s.get("size") or 0), 2), round(float(s.get("price") or 0), 4)] for s in sells]}
        print("X", json.dumps(out))


def lab():
    """Shapes for the strategy lab: leaderboards, a wallet's closed positions, sports and ladder markets."""
    D = "https://data-api.polymarket.com"
    tried = [("v1/leaderboard", {"category": "OVERALL", "timePeriod": "MONTH", "orderBy": "PNL", "limit": 5}),
             ("v2/leaderboard", {"category": "OVERALL", "timePeriod": "MONTH", "orderBy": "PNL", "limit": 5}),
             ("v2/leaderboard", {"window": "1m", "limit": 5}),
             ("leaderboard", {"window": "1m", "limit": 5}),
             ("v1/leaderboard", {"category": "SPORTS", "timePeriod": "WEEK", "orderBy": "PNL", "limit": 3}),
             ("v1/leaderboard", {"category": "POLITICS", "timePeriod": "ALL", "orderBy": "PNL", "limit": 3})]
    first = None
    for path, params in tried:
        try:
            res = get(f"{D}/{path}", params)
            show(f"/{path} {params}", res, 2500)
            rows = res if isinstance(res, list) else (res.get("data") or res.get("leaderboard") or [])
            if rows and not first:
                first = rows[0]
        except Exception as e:
            print(f"/{path} {params} failed: {e}")
    for url, params in (("https://lb-api.polymarket.com/profit", {"window": "1m", "limit": 3}),
                        ("https://lb-api.polymarket.com/volume", {"window": "1m", "limit": 3})):
        try:
            show(url, get(url, params), 1500)
        except Exception as e:
            print(url, "failed:", e)
    addr = None
    if isinstance(first, dict):
        addr = first.get("proxyWallet") or first.get("proxy_wallet") or first.get("address") or first.get("user")
    addr = addr or json.load(open("config.json"))["leader"]["address"]
    for path in ("v2/closed-positions", "v1/closed-positions", "closed-positions", "v2/value", "value", "v2/traded", "traded"):
        try:
            show(f"/{path} for {addr}", get(f"{D}/{path}", {"user": addr, "limit": 3}), 1500)
        except Exception as e:
            print(f"/{path} failed: {e}")
    try:
        res = get(f"{D}/v2/positions", {"user": addr, "limit": 500})
        rows = res.get("data", []) if isinstance(res, dict) else res
        print("positions page 1 rows:", len(rows), "pagination:", res.get("pagination") if isinstance(res, dict) else None)
    except Exception as e:
        print("positions failed:", e)
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    f = {"closed": "false", "limit": 500, "end_date_min": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "end_date_max": (now + dt.timedelta(hours=30)).strftime("%Y-%m-%dT%H:%M:%SZ"), "liquidity_num_min": 2000}
    try:
        res = get("https://gamma-api.polymarket.com/markets/keyset", f)
        ms = res.get("markets") or res.get("data") or []
        print("markets ending within 30h:", len(ms), "next:", bool(res.get("next_cursor")))
        sp = [m for m in ms if m.get("sportsMarketType") or m.get("gameId")]
        print("sports among them:", len(sp))
        for m in sp[:3]:
            show("sports market", {k: m.get(k) for k in ("question", "slug", "sportsMarketType", "gameId", "gameStartTime",
                 "startDate", "endDate", "endDateIso", "outcomes", "outcomePrices", "liquidityNum", "volumeNum",
                 "bestBid", "bestAsk", "feesEnabled", "feeSchedule", "events")}, 2000)
        if sp:
            show("sports market keys", sorted(sp[0].keys()), 3000)
        ud = [m for m in ms if "up or down" in str(m.get("question", "")).lower()]
        print("up-or-down among them:", len(ud))
    except Exception as e:
        print("sports scan failed:", e)
    try:
        res = get("https://gamma-api.polymarket.com/events/keyset", {"closed": "false", "limit": 100})
        evs = res.get("events") or res.get("data") or []
        n = 0
        for e in evs:
            ms = e.get("markets") or []
            if e.get("negRisk") or len(ms) < 2:
                continue
            qs = [str(m.get("question")) for m in ms]
            if sum((" by " in q.lower() or " before " in q.lower()) for q in qs) >= 2 or sum(("above" in q.lower()) for q in qs) >= 2:
                show("ladder-like event", {"title": e.get("title"), "slug": e.get("slug"),
                     "markets": [[m.get("question"), m.get("endDate"), m.get("outcomePrices"), m.get("bestAsk")] for m in ms[:8]]}, 2000)
                n += 1
                if n >= 4:
                    break
        print("ladder-like events shown:", n, "of", len(evs))
    except Exception as e:
        print("events scan failed:", e)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "kalshi"):
        kalshi()
    if what in ("all", "poly"):
        poly()
    if what in ("all", "endgame"):
        endgame()
    if what in ("all", "events"):
        events()
    if what in ("all", "activity"):
        activity()
    if what == "sells":
        sells()
    if what == "exits":
        exits_study()
    if what == "lab":
        lab()
