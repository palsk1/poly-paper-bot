"""Onchain / new prediction markets beyond Polymarket and Kalshi (research only, listen only, no keys).

    python3 outside/onchain.py scan            # probe out_onchain_scan: every venue, volume, books, reward programmes
    python3 outside/onchain.py hl [minutes]    # probe out_onchain_hl_60: Hyperliquid outcome books + perp price, lag test
    python3 outside/onchain.py gaps [rounds]   # probe out_onchain_gaps_10: same-event prices, HL / XO / Limitless vs Polymarket / Kalshi
    python3 outside/onchain.py rewards         # probe out_onchain_rewards: reward pools in cash on XO / Limitless, real books
    python3 outside/onchain.py winners         # probe out_onchain_winners: top wallets on Hyperliquid outcomes

Nothing here signs, logs in or places orders. Data goes to bt_cache/out_onchain/.
"""
import json, os, re, sys, time, gzip, math, urllib.request, urllib.parse

CACHE = "bt_cache/out_onchain"
UA = "Mozilla/5.0 (research script)"
HL = "https://api.hyperliquid.xyz/info"


def say(*a):
    print(*a, flush=True)


def get(url, params=None, post=None, headers=None, timeout=25, raw=False):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    data = None
    if post is not None:
        data = json.dumps(post).encode()
        h["Content-Type"] = "application/json"
    try:
        req = urllib.request.Request(url, data=data, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read()
            if raw:
                return b.decode("utf-8", "replace")
            return json.loads(b.decode())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:200]
        except Exception:
            body = ""
        return {"_err": f"HTTP {e.code} {body}"}
    except Exception as e:
        return {"_err": str(e)[:200]}


def hl(body):
    return get(HL, post=body)


def f(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d


def short(x, n=300):
    return json.dumps(x)[:n]


# ================================================================ scan
def hl_outcomes():
    meta = hl({"type": "outcomeMeta"})
    outs = meta.get("outcomes", []) if isinstance(meta, dict) else []
    qs = meta.get("questions", []) if isinstance(meta, dict) else []
    mids = hl({"type": "allMids"})
    ctx = hl({"type": "spotMetaAndAssetCtxs"})
    vol = {}
    if isinstance(ctx, list) and len(ctx) == 2:
        for c in ctx[1]:
            coin = str(c.get("coin", ""))
            if coin.startswith("#"):
                vol[coin] = (f(c.get("dayNtlVlm")), c.get("markPx"), c.get("midPx"))
    return meta, outs, qs, mids if isinstance(mids, dict) else {}, vol


def scan_hl():
    say("\n== Hyperliquid outcomes (HIP-4) ==")
    meta, outs, qs, mids, vol = hl_outcomes()
    say(f"  outcomes {len(outs)}, questions {len(qs)}, keys {list(meta.keys()) if isinstance(meta, dict) else meta}")
    say(f"  sample outcome: {short(outs[:1], 400)}")
    say(f"  sample question: {short(qs[:1], 400)}")
    say(f"  deployers: {short(meta.get('deployers'), 400) if isinstance(meta, dict) else ''}")
    say(f"  outcome coins with ctx {len(vol)}, 24h traded ${sum(v[0] for v in vol.values()):,.0f}; '#' mids {sum(1 for k in mids if k.startswith('#'))}")
    names = {o.get("outcome"): (o.get("name"), str(o.get("description"))) for o in outs}
    kinds = {}
    for coin, v in vol.items():
        oid = int(coin[1:]) // 10
        nm, ds = names.get(oid, ("?", "?"))
        k = re.search(r"class:(\w+)", ds)
        k = k.group(1) if k else (nm or "?")[:30]
        kinds.setdefault(k, [0, 0])
        kinds[k][0] += 1
        kinds[k][1] += v[0]
    for k, (n, v) in sorted(kinds.items(), key=lambda x: -x[1][1])[:15]:
        say(f"   kind {k}: {n} sides, ${v:,.0f} 24h")
    top = sorted(vol.items(), key=lambda x: -x[1][0])[:25]
    for coin, v in top:
        oid = int(coin[1:]) // 10
        nm, ds = names.get(oid, ("?", "?"))
        say(f"   ${v[0]:>10,.0f} {coin} mid={v[2]} {nm} | {ds[:110]}")
    # depth on some books
    for coin, v in top[:6]:
        bk = hl({"type": "l2Book", "coin": coin})
        lv = bk.get("levels") if isinstance(bk, dict) else None
        if lv:
            bids, asks = lv[0][:3], lv[1][:3]
            say(f"   book {coin}: bids {[(b['px'], b['sz']) for b in bids]} asks {[(a['px'], a['sz']) for a in asks]}")
    tmpl = hl({"type": "outcomeTemplates"})
    say(f"  templates: {short(tmpl, 300)}")
    # recent trades on the busiest crypto outcome
    for coin, v in top[:2]:
        tr = hl({"type": "recentTrades", "coin": coin})
        say(f"   recentTrades {coin}: n={len(tr) if isinstance(tr, list) else tr} {short(tr[:2] if isinstance(tr, list) else tr, 300)}")


def scan_limitless():
    say("\n== Limitless (Base) ==")
    rows = []
    for page in range(1, 20):
        r = get("https://api.limitless.exchange/markets/active", {"limit": 25, "page": page})
        if not isinstance(r, dict) or "_err" in r:
            say("  ", r); break
        d = r.get("data") or []
        if not d:
            break
        rows += d
        if page == 1:
            say(f"  total {r.get('totalMarketsCount')} keys {sorted(d[0].keys())}")
    say(f"  read {len(rows)}")
    rew = [m for m in rows if any(k for k in m if "reward" in k.lower()) or "reward" in json.dumps(m.get("settings") or {}).lower()]
    say(f"  markets mentioning rewards: {len(rew)}")
    if rows:
        say(f"  settings sample: {short(rows[0].get('settings'), 400)}")
    tot = 0
    for m in sorted(rows, key=lambda m: -f(m.get("volumeFormatted")))[:12]:
        s = m.get("settings") or {}
        say(f"   vol={m.get('volumeFormatted')} {str(m.get('title'))[:60]!r} type={m.get('tradeType')} exp={m.get('expirationDate')} rewards={s.get('dailyReward') or s.get('rewardsEpoch')} spread={s.get('maxSpread')} min={s.get('minSize')}")
    for m in rows:
        s = m.get("settings") or {}
        tot += f(s.get("dailyReward"))
    say(f"  sum of settings.dailyReward over active markets: {tot}")
    api = get("https://api.limitless.exchange/api-json")
    if isinstance(api, dict) and "paths" in api:
        ps = [p for p in api["paths"] if re.search(r"reward|point|leader", p, re.I)]
        say(f"  openapi paths with reward/point/leader: {ps[:30]}")


def scan_xo():
    say("\n== XO Market ==")
    r = get("https://api-mainnet.xo.market/api/markets", {"marketScope": "onlyClob", "take": 20, "sortBy": "totalVolumeInUSD", "sortOrder": "DESC", "status": "ACTIVE"})
    d = r.get("data") if isinstance(r, dict) else None
    say(f"  {short(r.get('meta') if isinstance(r, dict) else r, 300)}")
    if d:
        say(f"  keys {sorted(d[0].keys())[:60]}")
        for m in d[:15]:
            say(f"   vol=${m.get('totalVolumeInUSD')} notional=${m.get('totalNotionalInUSD')} {str(m.get('title'))[:60]!r} type={m.get('type')} end={m.get('expiresAt') or m.get('endDate')}")
    for p in ["/api/public/liquidity-rewards/earning-pools", "/api/public/liquidity-rewards/pools", "/api/public/liquidity-rewards/programs",
              "/api/public/liquidity-rewards/config", "/api/public/liquidity-rewards/markets"]:
        x = get("https://api-mainnet.xo.market" + p)
        say(f"  {p}: {short(x, 500)}")
    x = get("https://orderbooks.xo.market/openapi.json")
    if isinstance(x, dict) and "paths" in x:
        say(f"  orderbook openapi paths: {list(x['paths'])[:30]}")
    else:
        for p in ["/docs/openapi.json", "/api-json", "/swagger.json", "/v1/openapi.json"]:
            x = get("https://orderbooks.xo.market" + p)
            if isinstance(x, dict) and "paths" in x:
                say(f"  orderbook openapi {p}: {list(x['paths'])[:30]}"); break
        else:
            say(f"  orderbook openapi not found: {short(x, 150)}")


def scan_predict():
    say("\n== Predict.fun (BNB) ==")
    for u in ["https://api.predict.fun/v1/markets?first=20", "https://api.predict.fun/v1/categories?first=10", "https://api.predict.fun/v1/markets"]:
        x = get(u)
        say(f"  {u}: {short(x, 400)}")
    x = get("https://predict.fun/", raw=True)
    say(f"  website reachable: {isinstance(x, str)} {len(x) if isinstance(x, str) else short(x, 100)}")


def scan_opinion():
    say("\n== Opinion (BNB) ==")
    for u in ["https://openapi.opinion.trade/openapi/market?status=activated&sortBy=5&limit=20",
              "https://proxy.opinion.trade:8443/api/bsc/api/v2/topic?limit=20&sortBy=5&status=2"]:
        x = get(u)
        say(f"  {u}: {short(x, 600)}")


def scan_misc():
    say("\n== SX Bet ==")
    r = get("https://api.sx.bet/markets/active", {"onlyMainLine": "true"})
    d = (r.get("data") or {}).get("markets") if isinstance(r, dict) else None
    say(f"  active main-line markets: {len(d) if d else short(r, 200)}")
    if d:
        sports = {}
        for m in d:
            sports[m.get("sportLabel") or m.get("sportId")] = sports.get(m.get("sportLabel") or m.get("sportId"), 0) + 1
        say(f"  by sport {sports}")
        say(f"  sample {short(d[0], 300)}")
    x = get("https://api.sx.bet/orders", {"marketHashes": d[0]["marketHash"]} if d else None)
    say(f"  orders sample: {short(x, 300)}")
    say("\n== Myriad ==")
    x = get("https://api-v2.myriadprotocol.com/markets", {"sort": "volume_24h", "order": "desc", "limit": 10, "state": "open"})
    rows = x.get("data") if isinstance(x, dict) else x
    if isinstance(rows, list):
        for m in rows[:8]:
            say(f"   vol24h={m.get('volume_24h')} vol={m.get('volume')} {str(m.get('title'))[:60]!r} tok={m.get('token', {}).get('symbol') if isinstance(m.get('token'), dict) else ''}")
    else:
        say(f"  {short(x, 300)}")
    say("\n== Overtime ==")
    for u in ["https://api.overtime.io/overtime-v2/networks/10/markets", "https://api.overtime.io/overtime-v2/sports"]:
        say(f"  {u}: {short(get(u), 200)}")
    say("\n== Drift BET / Azuro / Truemarkets / Probable ==")
    for u in ["https://data.api.drift.trade/contracts", "https://api.truemarkets.org/markets", "https://api.probable.markets/markets",
              "https://api.onchainfeed.org/api/v1/public/market-manager/events?limit=5", "https://gateway.azuro.org/api/v1/public/gateway/games?limit=3"]:
        say(f"  {u}: {short(get(u), 200)}")


def scan(arg=None):
    for fn in (scan_hl, scan_limitless, scan_xo, scan_predict, scan_opinion, scan_misc):
        try:
            fn()
        except Exception as e:
            say(f"  !! {fn.__name__}: {e!r}")
    say("=== DONE ===")


# ================================================================ peek (structures)
def peek(arg=None):
    meta, outs, qs, mids, vol = hl_outcomes()
    seen = {}
    for o in outs:
        k = o.get("name")
        seen.setdefault(k, 0)
        if seen[k] < 2:
            say("HL outcome", short(o, 700), "| vol", vol.get(f"#{10*o['outcome']}"), vol.get(f"#{10*o['outcome']+1}"))
        seen[k] += 1
    for q in qs[:6]:
        say("HL question", short(q, 900))
    say("feeScale", meta.get("feeScale"))
    x = get("https://api-mainnet.xo.market/api/public/liquidity-rewards/earning-pools")
    d = x.get("data") if isinstance(x, dict) else None
    say("XO pools:", len(d) if d else short(x, 300), "keys", short({k: v for k, v in x.items() if k != "data"}, 300) if isinstance(x, dict) else "")
    for p in (d or [])[:3]:
        say("XO pool", short(p, 1500))
    for p in (d or []):
        say("XO pool short", short({k: p.get(k) for k in p if k != "market"}, 400), (p.get("market") or {}).get("title"))
    x = get("https://api-mainnet.xo.market/api/markets", {"marketScope": "onlyClob", "take": 10})
    say("XO markets", short(x, 1200))
    x = get("https://openapi.opinion.trade/openapi/market", {"status": "activated", "sortBy": 5, "limit": 5})
    lst = (x.get("result") or {}).get("list") if isinstance(x, dict) else None
    say("Opinion total", (x.get("result") or {}).get("total") if isinstance(x, dict) else x)
    if lst:
        say("Opinion market", short(lst[0], 1500))
        tok = lst[0].get("yesTokenId")
        say("Opinion book", short(get("https://openapi.opinion.trade/openapi/token/orderbook", {"token_id": tok}), 800))
        for m in lst:
            say("  ", m.get("marketTitle"), m.get("volume24h"), m.get("volume"))
    for u, body in [("https://graphql.predict.fun/graphql", {"query": "{ categories(first: 3) { edges { node { slug title } } } }"}),
                    ("https://api.predict.fun/graphql", {"query": "{ __typename }"})]:
        say("Predict", u, short(get(u, post=body), 400))
    say("=== DONE ===")


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = sys.argv[2:] or [None]
    globals()[cmd](*arg)
