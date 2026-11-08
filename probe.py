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


def fast():
    """Fast-resolving markets (weather, daily crypto, sports games) and the free outside data that could price them."""
    import datetime as dt
    G = "https://gamma-api.polymarket.com"
    now = dt.datetime.now(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    for tag in ("weather", "temperature", "daily-temperature", "crypto", "bitcoin", "crypto-prices", "sports", "nba",
                "nfl", "nhl", "soccer", "games"):
        try:
            r = get(f"{G}/events", {"tag_slug": tag, "closed": "false", "limit": 100,
                                    "end_date_max": (now + dt.timedelta(days=3)).strftime(fmt)})
            evs = r if isinstance(r, list) else (r.get("events") or r.get("data") or [])
            print(f"== tag {tag}: {len(evs)} events ending within 3 days")
            for e in evs[:8]:
                print("   ", e.get("endDate"), "|", e.get("title"), "|", e.get("slug"), "| markets", len(e.get("markets") or []))
        except Exception as e:
            print(f"tag {tag} failed: {e}")
    # one weather event in full
    try:
        r = get(f"{G}/events", {"tag_slug": "weather", "closed": "false", "limit": 50})
        evs = r if isinstance(r, list) else (r.get("events") or [])
        wx = [e for e in evs if "temperature" in str(e.get("title")).lower()]
        print("== weather temperature events:", len(wx))
        for e in wx[:40]:
            print("   ", e.get("endDate"), "|", e.get("title"), "|", e.get("slug"))
        if wx:
            e = wx[0]
            print("event keys:", sorted(e.keys()))
            show("event (no markets)", {k: v for k, v in e.items() if k != "markets"}, 3000)
            for m in (e.get("markets") or [])[:12]:
                print("   ", {k: m.get(k) for k in ("question", "groupItemTitle", "outcomes", "outcomePrices", "bestAsk", "bestBid",
                                                 "feesEnabled", "feeSchedule", "endDate", "liquidityNum", "volumeNum",
                                                 "acceptingOrders", "negRisk", "clobTokenIds")})
            show("market description", (e.get("markets") or [{}])[0].get("description"), 2000)
            show("market resolutionSource", (e.get("markets") or [{}])[0].get("resolutionSource"), 500)
    except Exception as e:
        print("weather detail failed:", e)
    # markets ending within 48h: what kinds exist
    try:
        out, cur = [], None
        for _ in range(20):
            p = {"closed": "false", "limit": 500, "end_date_min": now.strftime(fmt),
                 "end_date_max": (now + dt.timedelta(hours=48)).strftime(fmt)}
            if cur:
                p["after_cursor"] = cur
            r = get(f"{G}/markets/keyset", p)
            ms = r.get("markets") or []
            out += ms
            cur = r.get("next_cursor")
            if not cur or not ms:
                break
        print("== markets ending within 48h:", len(out))
        kinds = {}
        for m in out:
            q = str(m.get("question") or "").lower()
            k = ("temperature" if "temperature" in q else "updown" if "up or down" in q else
                 "crypto_strike" if any(w in q for w in ("bitcoin", "ethereum", "solana", "xrp")) else
                 "sports" if (m.get("sportsMarketType") or m.get("gameId")) else "other")
            kinds.setdefault(k, []).append(m)
        for k, ms in kinds.items():
            liq = sorted((float(m.get("liquidityNum") or 0) for m in ms), reverse=True)
            print(f"-- {k}: {len(ms)} markets, liquidity top/median {liq[:1]} {liq[len(liq)//2] if liq else 0}")
            for m in ms[:6]:
                print("   ", {x: m.get(x) for x in ("question", "endDate", "outcomePrices", "bestAsk", "feesEnabled",
                                                  "feeSchedule", "liquidityNum", "volumeNum", "sportsMarketType",
                                                  "gameStartTime", "gameId", "eventStartTime")})
        for k in ("crypto_strike", "sports"):
            if kinds.get(k):
                show(f"{k} full market sample", kinds[k][0], 5000)
    except Exception as e:
        print("48h scan failed:", e)
    outside = [
        ("open-meteo forecast", "https://api.open-meteo.com/v1/forecast",
         {"latitude": 40.7769, "longitude": -73.874, "daily": "temperature_2m_max", "temperature_unit": "fahrenheit",
          "timezone": "America/New_York", "forecast_days": 3, "models": "gfs_seamless,ecmwf_ifs025,icon_seamless"}),
        ("open-meteo ensemble", "https://ensemble-api.open-meteo.com/v1/ensemble",
         {"latitude": 40.7769, "longitude": -73.874, "daily": "temperature_2m_max", "temperature_unit": "fahrenheit",
          "timezone": "America/New_York", "forecast_days": 3, "models": "gfs025,ecmwf_ifs025"}),
        ("metar KLGA", "https://aviationweather.gov/api/data/metar", {"ids": "KLGA,EGLC", "format": "json", "hours": 6}),
        ("espn nba", "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", None),
        ("espn nfl", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", None),
        ("coinbase candles", "https://api.exchange.coinbase.com/products/BTC-USD/candles", {"granularity": 3600}),
        ("binance vision klines", "https://data-api.binance.vision/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1h", "limit": 3}),
        ("kalshi KXHIGHNY", BASES[1] + "/markets", {"series_ticker": "KXHIGHNY", "status": "open", "limit": 3}),
    ]
    for label, url, params in outside:
        try:
            res = get(url, params)
            if label.startswith("espn"):
                evs = res.get("events") or []
                print(f"== {label}: {len(evs)} games")
                for e in evs[:3]:
                    c = (e.get("competitions") or [{}])[0]
                    print("   ", e.get("date"), e.get("name"), "| status", (e.get("status") or {}).get("type", {}).get("state"))
                    show("   odds", c.get("odds"), 1500)
                    show("   competitors", [{k: x.get(k) for k in ("homeAway", "team")} for x in c.get("competitors", [])], 800)
            else:
                show(label, res, 2500)
        except Exception as e:
            print(label, "failed:", e)


def fast2():
    """Current fast markets only: weather and crypto events ending in the next 3 days, plus METAR history."""
    import datetime as dt
    from collections import Counter
    G = "https://gamma-api.polymarket.com"
    now = dt.datetime.now(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    for tag in ("daily-temperature", "weather", "crypto", "bitcoin", "ethereum", "crypto-prices", "up-or-down", "nba", "nfl",
                "nhl", "soccer", "tennis", "esports"):
        evs, off = [], 0
        try:
            while off < 1500:
                r = get(f"{G}/events", {"tag_slug": tag, "closed": "false", "limit": 500, "offset": off,
                                        "end_date_min": now.strftime(fmt),
                                        "end_date_max": (now + dt.timedelta(days=3)).strftime(fmt)})
                rows = r if isinstance(r, list) else (r.get("events") or r.get("data") or [])
                evs += rows
                if len(rows) < 500:
                    break
                off += 500
        except Exception as e:
            print(f"tag {tag} failed: {e}")
        kinds = Counter()
        for e in evs:
            t = str(e.get("title") or "")
            import re
            kinds[re.sub(r"[0-9]+", "#", re.sub(r" (in|on) [A-Z][^?]*", " in X", t))[:60]] += 1
        print(f"== tag {tag}: {len(evs)} events ending within 3 days; title shapes:")
        for k, n in kinds.most_common(15):
            print(f"    {n:4d}  {k}")
        liq = sorted(((float(e.get("liquidity") or 0), e.get("title"), e.get("endDate"), e.get("slug")) for e in evs), reverse=True)
        for x in liq[:6]:
            print("    top liq:", x)
        if tag == "daily-temperature" and evs:
            cities = Counter(re.sub(r" on .*", "", str(e.get("title"))) for e in evs)
            print("    cities:", dict(cities))
            e = sorted(evs, key=lambda e: e.get("endDate") or "")[0]
            print("    soonest:", e.get("title"), e.get("endDate"), e.get("slug"), "tags", [t.get("slug") for t in e.get("tags") or []])
            print("    resolutionSource:", e.get("resolutionSource"), "| desc:", str(e.get("description"))[:400])
            for m in e.get("markets") or []:
                print("     ", {k: m.get(k) for k in ("groupItemTitle", "outcomePrices", "bestAsk", "bestBid", "lastTradePrice",
                                                     "liquidityNum", "volumeNum", "acceptingOrders", "closed", "endDate",
                                                     "umaResolutionStatuses", "feeSchedule")})
            srcs = Counter(re.sub(r".*/", "", str(x.get("resolutionSource") or "")) for x in evs)
            print("    stations:", dict(srcs))
            urls = {}
            for x in evs:
                urls.setdefault(re.sub(r" on .*", "", str(x.get("title"))), x.get("resolutionSource") or
                                (re.findall(r"https://www.wunderground.com/\S+", str(x.get("description"))) or [""])[0])
            for k, v in urls.items():
                print("     ", k, "->", v)
        if tag in ("crypto", "bitcoin") and evs:
            for e in evs:
                t = str(e.get("title")).lower()
                if "up or down" not in t and ("above" in t or "price" in t):
                    print("    strike event:", e.get("title"), e.get("endDate"), e.get("slug"), "liq", e.get("liquidity"))
                    for m in (e.get("markets") or [])[:4]:
                        print("      ", {k: m.get(k) for k in ("question", "groupItemTitle", "outcomePrices", "bestAsk", "bestBid",
                                                             "liquidityNum", "feeSchedule")})
                    print("      desc:", str((e.get("markets") or [{}])[0].get("description"))[:700])
                    break
            ud = [e for e in evs if "up or down" in str(e.get("title")).lower()]
            durs = Counter(re.sub(r".*-(5m|15m|1h|4h|daily|hourly).*", r"\1", str(e.get("slug"))) if re.search(r"-(5m|15m|1h|4h)-", str(e.get("slug"))) else "other" for e in ud)
            print("    up/down by length:", dict(durs))
            for e in sorted(ud, key=lambda e: -float(e.get("liquidity") or 0))[:5]:
                print("     ", e.get("title"), e.get("slug"), "liq", e.get("liquidity"))
    try:
        res = get("https://aviationweather.gov/api/data/metar", {"ids": "KLGA", "format": "json", "hours": 24})
        print("== METAR KLGA 24h rows:", len(res), "keys:", sorted(res[0].keys()) if res else None)
        for x in res[:30]:
            print("   ", x.get("reportTime"), x.get("temp"), x.get("maxT"), x.get("minT"), x.get("maxT24"), "|", x.get("rawOb"))
    except Exception as e:
        print("metar failed:", e)


def fast3():
    """Weather rules text, today's (past endDate, not closed) weather buckets vs METAR so far, crypto ladders vs Binance."""
    import datetime as dt
    import re
    G = "https://gamma-api.polymarket.com"
    now = dt.datetime.now(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    evs = []
    for off in (0, 500):
        r = get(f"{G}/events", {"tag_slug": "daily-temperature", "closed": "false", "limit": 500, "offset": off,
                                "end_date_min": (now - dt.timedelta(hours=40)).strftime(fmt),
                                "end_date_max": (now + dt.timedelta(hours=60)).strftime(fmt)})
        rows = r if isinstance(r, list) else (r.get("events") or [])
        evs += rows
        if len(rows) < 500:
            break
    print("== weather events:", len(evs))
    for slug in ("highest-temperature-in-nyc-on-november-9-2026", "highest-temperature-in-london-on-november-9-2026"):
        for e in evs:
            if e.get("slug") == slug:
                m = (e.get("markets") or [{}])[0]
                print("== full rules", slug)
                print(m.get("description"))
                print("buckets:", [x.get("groupItemTitle") for x in e.get("markets") or []])
                print("market keys:", sorted(m.keys()))
    past = [e for e in evs if (e.get("endDate") or "") < now.strftime(fmt)]
    print("== past endDate, still open:", len(past))
    ids = sorted({re.search(r"ids=([A-Z0-9]+)", str(e.get("resolutionSource"))).group(1) for e in past
                  if re.search(r"ids=([A-Z0-9]+)", str(e.get("resolutionSource")))})
    obs = {}
    for i in range(0, len(ids), 30):
        try:
            for x in get("https://aviationweather.gov/api/data/metar", {"ids": ",".join(ids[i:i + 30]), "format": "json", "hours": 30}):
                obs.setdefault(x.get("icaoId"), []).append(x)
        except Exception as ex:
            print("metar failed", ex)
    for e in sorted(past, key=lambda e: -float(e.get("liquidity") or 0))[:25]:
        src = str(e.get("resolutionSource"))
        mm = re.search(r"ids=([A-Z0-9]+).*date=([0-9T:-]+Z)", src)
        if not mm:
            print("  no source:", e.get("title"))
            continue
        icao, end = mm.group(1), dt.datetime.strptime(mm.group(2), fmt).replace(tzinfo=dt.timezone.utc)
        lo, hi = end - dt.timedelta(hours=27), end - dt.timedelta(hours=3)
        vals = []
        for x in obs.get(icao, []):
            raw = str(x.get("rawOb") or "")
            t = re.search(r" T([01])(\d{3})([01])(\d{3})", raw)
            ts = dt.datetime.fromtimestamp(x.get("obsTime") or 0, dt.timezone.utc)
            if t and raw.startswith("METAR") and lo <= ts < hi:
                vals.append((-1 if t.group(1) == "1" else 1) * int(t.group(2)) / 10)
        hi_c = max(vals) if vals else None
        lo_c = min(vals) if vals else None
        print(f"-- {e.get('title')} | {icao} local day {lo:%m-%d %H}Z..{hi:%m-%d %H}Z | obs {len(vals)} max {hi_c} min {lo_c} "
              f"| liq {float(e.get('liquidity') or 0):.0f} | closed {e.get('closed')}")
        for m in e.get("markets") or []:
            print("     ", m.get("groupItemTitle"), "| prices", m.get("outcomePrices"), "| ask", m.get("bestAsk"), "bid", m.get("bestBid"),
                  "| liq", round(float(m.get("liquidityNum") or 0)), "| uma", m.get("umaResolutionStatuses"), "| closed", m.get("closed"))
    # crypto ladders
    try:
        px = get("https://data-api.binance.vision/api/v3/ticker/price", {"symbols": '["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT"]'})
        print("== binance spot", px)
    except Exception as ex:
        print("binance failed", ex)
    for slug in ("bitcoin-above-on-november-9-2026", "bitcoin-price-on-november-9-2026", "ethereum-above-on-november-9-2026"):
        try:
            r = get(f"{G}/events", {"slug": slug})
            e = (r if isinstance(r, list) else r.get("events") or [])[0]
            print("== crypto", slug, "end", e.get("endDate"), "liq", e.get("liquidity"))
            for m in e.get("markets") or []:
                print("     ", m.get("groupItemTitle"), "| prices", m.get("outcomePrices"), "| ask", m.get("bestAsk"), "bid", m.get("bestBid"),
                      "| liq", round(float(m.get("liquidityNum") or 0)), "| spread", m.get("spread"))
        except Exception as ex:
            print(slug, "failed", ex)
    try:
        r = get(f"{G}/events", {"tag_slug": "up-or-down", "closed": "false", "limit": 200,
                                "end_date_min": now.strftime(fmt), "end_date_max": (now + dt.timedelta(hours=3)).strftime(fmt)})
        rows = r if isinstance(r, list) else (r.get("events") or [])
        for e in rows[:12]:
            m = (e.get("markets") or [{}])[0]
            print("  updown:", e.get("title"), e.get("endDate"), "| start", m.get("eventStartTime") or e.get("startTime"),
                  "| prices", m.get("outcomePrices"), "| ask", m.get("bestAsk"), "bid", m.get("bestBid"), "| fee", m.get("feeSchedule"))
        if rows:
            print("  updown rules:", str((rows[0].get("markets") or [{}])[0].get("description"))[:900])
    except Exception as ex:
        print("updown failed", ex)


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
    if what == "fast3":
        fast3()
    if what == "fast2":
        fast2()
    if what == "fast":
        fast()
    if what == "lab":
        lab()


def marks(what):
    """marks_<track>: every open position of one track with its live mark, market state and best bid/ask."""
    import bot
    name = what[len("marks_"):] or "endgame_sell98"
    tr = bot.load_tracks()[name]
    bot.prefetch_markets(p.get("slug") for p in tr["positions"].values())
    tot = 0.0
    for tok, p in tr["positions"].items():
        m = bot.market_by_slug(p.get("slug"))
        px = bot.mark(p, tok)
        u = p["shares"] * px - (p["shares"] * p["entry"] + p.get("entry_fee", 0.0))
        tot += u
        bk = bot.book(tok) or {}
        bid = (bk.get("bids") or [[None]])[0][0]
        ask = (bk.get("asks") or [[None]])[0][0]
        print(f"{u:+7.2f} entry {p['entry']:.3f} mark {px:.3f} bid {bid} ask {ask} closed {m and m.get('closed')} "
              f"uma {m and m.get('umaResolutionStatus')} prices {m and m.get('outcomePrices')} | {p.get('tier')} | {p.get('title','')[:70]} [{p.get('outcome')}]")
    print(f"total unrealized {tot:+.2f} on {len(tr['positions'])} open")


if __name__ == "__main__" and sys.argv[1:] and sys.argv[1].startswith("marks"):
    marks(sys.argv[1])
