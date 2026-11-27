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


# ================================================================ gaps: same event, same second
STOP = {"fc", "afc", "cf", "the", "de", "club", "sc", "ac", "cd", "rc", "ud", "real", "city", "united", "of", "and", "vs", "will",
        "win", "to", "sl", "cfc", "hotspur", "albion", "wanderers"}


def toks(name):
    t = str(name).lower()
    for a, b in (("é", "e"), ("á", "a"), ("ó", "o"), ("í", "i"), ("ü", "u"), ("ñ", "n"), ("ö", "o"), ("ã", "a")):
        t = t.replace(a, b)
    return {x for x in re.findall(r"[a-z0-9]+", t) if x not in STOP and len(x) > 2}


def kv(desc):
    out = {}
    for part in str(desc).split("|"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k] = v
    return out


def hl_book(coin):
    bk = hl({"type": "l2Book", "coin": coin})
    lv = bk.get("levels") if isinstance(bk, dict) else None
    if not lv:
        return None
    return {"bids": [(f(b["px"]), f(b["sz"])) for b in lv[0]], "asks": [(f(a["px"]), f(a["sz"])) for a in lv[1]]}


def walk_usd(levels, usd):
    """Buy up to `usd` dollars along ascending ask levels: (avg price, shares) or None if too thin."""
    left, sh, cost = usd, 0.0, 0.0
    for p, z in levels:
        if p <= 0:
            continue
        take = min(z, left / p)
        sh += take
        cost += take * p
        left -= take * p
        if left <= 1e-6:
            return cost / sh, sh
    return None


def flip(levels):
    """Bids of Yes seen as asks of No (merged book)."""
    return sorted(((1 - p, z) for p, z in levels), key=lambda x: x[0])


def hl_items():
    meta = hl({"type": "outcomeMeta"})
    outs = {o["outcome"]: o for o in meta.get("outcomes", [])}
    items = []
    for o in outs.values():
        d = kv(o.get("description"))
        if o.get("name") == "template:sportsContestWinner":
            items.append({"kind": "game2", "a": d.get("participantA"), "b": d.get("participantB"), "comp": d.get("competition"),
                          "start": d.get("scheduledStart"), "coin": f"#{10 * o['outcome']}",
                          "label": f"{d.get('participantA')} beat {d.get('participantB')}"})
    for q in meta.get("questions", []):
        d = kv(q.get("description"))
        if q.get("name") == "template:sportsContestResult":
            for oid in q.get("namedOutcomes", []):
                part = kv((outs.get(oid) or {}).get("description")).get("participant")
                items.append({"kind": "soccer3", "a": d.get("participantA"), "b": d.get("participantB"), "comp": d.get("competition"),
                              "start": d.get("scheduledStart"), "pick": part or "Draw", "coin": f"#{10 * oid}",
                              "label": f"{d.get('participantA')} v {d.get('participantB')}: {part or 'Draw'}"})
        elif q.get("name") == "template:sportsTournamentWinner":
            for oid in q.get("namedOutcomes", []):
                part = kv((outs.get(oid) or {}).get("description")).get("participant")
                if part:
                    items.append({"kind": "future", "comp": d.get("competition"), "pick": part, "coin": f"#{10 * oid}",
                                  "label": f"{d.get('competition')} winner: {part}"})
    return items


PM_TAGS = ["nfl", "nba", "nhl", "epl", "la-liga", "serie-a", "bundesliga", "ligue-1", "ucl", "champions-league", "soccer", "ncaab", "college-football"]


def pm_events():
    sys.path.insert(0, ".")
    import bot
    evs, seen = [], set()
    for tag in PM_TAGS:
        for off in (0, 500):
            try:
                r = bot.http_json(f"{bot.GAMMA}/events", {"tag_slug": tag, "closed": "false", "limit": 500, "offset": off})
            except Exception as e:
                say(f"  gamma {tag}: {e}")
                break
            if not r:
                break
            for e in r:
                if e.get("id") not in seen:
                    seen.add(e.get("id"))
                    evs.append(e)
            if len(r) < 500:
                break
    for q in ["Super Bowl Champion 2027", "NBA Champion 2027", "Premier League Winner", "Champions League Winner", "La Liga Winner"]:
        try:
            r = bot.http_json(f"{bot.GAMMA}/public-search", {"q": q, "limit_per_type": 5})
            for e in (r or {}).get("events") or []:
                if e.get("id") not in seen and not e.get("closed"):
                    seen.add(e.get("id"))
                    evs.append(bot.http_json(f"{bot.GAMMA}/events/{e['id']}"))
        except Exception as e:
            say(f"  search {q}: {e}")
    return evs


def pm_index(evs):
    sys.path.insert(0, ".")
    import bot
    rows = []
    for e in evs:
        for m in e.get("markets") or []:
            if m.get("closed") or not m.get("active", True):
                continue
            outs = bot.jlist(m.get("outcomes"))
            tks = bot.market_tokens(m)
            if len(outs) != 2 or len(tks) != 2:
                continue
            rows.append({"et": e.get("title") or "", "q": m.get("question") or "", "git": m.get("groupItemTitle") or "", "outs": outs,
                         "tks": tks, "start": m.get("gameStartTime") or e.get("startTime") or "", "m": m, "smt": m.get("sportsMarketType")})
    return rows


def ts(s, fmt):
    import calendar
    try:
        return calendar.timegm(time.strptime(s, fmt))
    except Exception:
        return None


def match(items, rows):
    pairs = []
    for it in items:
        best = None
        if it["kind"] in ("game2", "soccer3"):
            ta, tb = toks(it["a"]), toks(it["b"])
            t0 = ts(it.get("start") or "", "%Y%m%d-%H%M")
            for r in rows:
                text = toks(r["et"])
                if not (ta & text and tb & text):
                    continue
                st = ts(str(r["start"])[:19].replace(" ", "T"), "%Y-%m-%dT%H:%M:%S") if r["start"] else None
                if t0 and st and abs(st - t0) > 30 * 3600:
                    continue
                q = r["q"].lower()
                if it["kind"] == "game2":
                    if r["smt"] not in (None, "moneyline") or "draw" in q or "spread" in q or "o/u" in q:
                        continue
                    o0, o1 = toks(r["outs"][0]), toks(r["outs"][1])
                    if o0 & ta and o1 & tb:
                        best = (r, 0)
                        break
                    if o0 & tb and o1 & ta:
                        best = (r, 1)
                        break
                    continue
                if r["outs"][0].lower() != "yes":
                    continue
                if it["pick"] == "Draw":
                    if "draw" in q:
                        best = (r, 0)
                        break
                elif toks(it["pick"]) & toks(r["git"] or r["q"]) and "draw" not in q and " win" in " " + q:
                    best = (r, 0)
                    break
        else:
            tp = toks(it["pick"])
            c = str(it["comp"]).lower()
            comp = toks(c) | ({"super", "bowl"} if "football league" in c else set()) | ({"nba"} if "nba" in c else set())
            for r in rows:
                if r["outs"][0].lower() != "yes" or not tp or not (comp & toks(r["et"])):
                    continue
                g = toks(r["git"] or r["q"])
                if tp <= g or (r["git"] and toks(r["git"]) and toks(r["git"]) <= tp):
                    best = (r, 0)
                    break
        if best:
            pairs.append((it, best[0], best[1]))
    return pairs


def gaps(rounds=None, wait=None):
    sys.path.insert(0, ".")
    import bot
    rounds, wait = int(rounds or 6), int(wait or 90)
    items = hl_items()
    say(f"HL items {len(items)}: " + str({k: sum(1 for i in items if i['kind'] == k) for k in ('game2', 'soccer3', 'future')}))
    evs = pm_events()
    rows = pm_index(evs)
    say(f"PM events {len(evs)}, two-outcome markets {len(rows)}")
    pairs = match(items, rows)
    say(f"matched pairs {len(pairs)}")
    for it, r, side in pairs:
        say(f"  PAIR {it['label'][:58]!r} <-> {r['et'][:40]!r} / {r['q'][:50]!r} -> {r['outs'][side]}")
    got = {id(p[0]) for p in pairs}
    say(f"unmatched HL items {sum(1 for i in items if id(i) not in got)}: {[i['label'][:38] for i in items if id(i) not in got][:50]}")
    log, track, USD = [], {}, 25.0
    for rd in range(rounds):
        t0 = time.time()
        n_lock = 0
        for it, r, side in pairs:
            hb = hl_book(it["coin"])
            if not hb or not hb["asks"] or not hb["bids"]:
                continue
            pb_yes, pb_no = bot.book(r["tks"][side]), bot.book(r["tks"][1 - side])
            if not pb_yes or not pb_no or not pb_yes["asks"] or not pb_yes["bids"]:
                continue
            rate = bot.fee_rate(r["m"])
            rec = {"t": round(time.time(), 1), "rd": rd, "k": it["kind"], "lab": it["label"][:70], "hb": hb["bids"][0][0], "ha": hb["asks"][0][0],
                   "pb": pb_yes["bids"][0][0], "pa": pb_yes["asks"][0][0], "rate": rate,
                   "hdepth": round(sum(p * z for p, z in hb["asks"][:5])), "pdepth": round(sum(p * z for p, z in pb_yes["asks"][:5]))}
            for name, hl_lv, pm_lv in (("hlY_pmN", hb["asks"], pb_no["asks"]), ("hlN_pmY", flip(hb["bids"]), pb_yes["asks"])):
                if not pm_lv:
                    continue
                top = hl_lv[0][0] + pm_lv[0][0] + rate * pm_lv[0][0] * (1 - pm_lv[0][0]) + 0.001
                rec[name + "_top"] = round(1 - top, 4)
                a, b = walk_usd(hl_lv, USD / 2), walk_usd(pm_lv, USD / 2)
                if a and b:
                    rec[name] = round(1 - (a[0] + b[0] + rate * b[0] * (1 - b[0]) + 0.001), 4)
                if top < 1:
                    n_lock += 1
                    track.setdefault((it["label"], name), []).append((rd, rec[name + "_top"], rec.get(name)))
            log.append(rec)
        say(f"round {rd}: {len(log)} reads so far, {time.time() - t0:.0f}s, top-of-book locks after fees this round {n_lock}")
        if rd < rounds - 1:
            time.sleep(max(0, wait - (time.time() - t0)))
    with gzip.open(os.path.join(CACHE, f"gaps_{int(time.time())}.json.gz"), "wt") as fh:
        json.dump(log, fh)
    say("\n== HL middle minus Polymarket middle ==")
    for k in ("game2", "soccer3", "future"):
        xs = sorted((x["hb"] + x["ha"]) / 2 - (x["pb"] + x["pa"]) / 2 for x in log if x["k"] == k)
        if not xs:
            continue
        say(f"  {k}: reads {len(xs)}, median {100 * xs[len(xs) // 2]:+.2f}c, 10%/90% {100 * xs[len(xs) // 10]:+.2f}c/{100 * xs[9 * len(xs) // 10]:+.2f}c, "
            f"2c+ apart {sum(1 for x in xs if abs(x) >= 0.02)}")
        sh = sorted(x["ha"] - x["hb"] for x in log if x["k"] == k)
        sp = sorted(x["pa"] - x["pb"] for x in log if x["k"] == k)
        dh = sorted(x["hdepth"] for x in log if x["k"] == k)
        dp = sorted(x["pdepth"] for x in log if x["k"] == k)
        say(f"     gap bid-ask: HL median {100 * sh[len(sh) // 2]:.2f}c, PM {100 * sp[len(sp) // 2]:.2f}c; $ on the first 5 asks: HL {dh[len(dh) // 2]}, PM {dp[len(dp) // 2]}")
    say("\n== locks: buy one side on each site, after fees ==")
    for (lab, name), v in sorted(track.items(), key=lambda x: -max(y[1] for y in x[1]))[:40]:
        say(f"  {lab[:58]!r} {name}: rounds {[y[0] for y in v]} per $1 at the top {[y[1] for y in v]} at $25 {[y[2] for y in v]}")
    allv = [x[n] for x in log for n in ("hlY_pmN", "hlN_pmY") if n in x]
    say(f"  lock checks at $25: {len(allv)}, above $0: {sum(1 for v in allv if v > 0)}, best {max(allv) if allv else None}")
    say("=== DONE ===")


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = sys.argv[2:] or [None]
    globals()[cmd](*arg)
