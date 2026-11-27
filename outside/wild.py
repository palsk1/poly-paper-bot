"""Wild-card outside research (paper only, read-only public data, no keys, no orders).

Commands (probe input out_wild_<cmd>_<args>):
  hosts            which outside hosts answer from GitHub Actions
  vol              sell a weekly BTC / ETH straddle or put on Deribit: Deribit's own DVOL (implied swing) vs the real
                   swing that followed, every Friday since 2021 (Deribit public API, no key)
  defi             stablecoin lending: what Aave / Morpho / Compound etc. really paid over the last year (DeFiLlama),
                   and same-chain lend-vs-borrow gaps
  pendle           Pendle fixed yields (PT) vs what the floating yield then really paid
  skins            CS2 skins on Skinport: listings under the recent sale price (snapshot; run twice to see if they last)
Writes caches under bt_cache/out_wild/. Ends with === DONE ===.
"""
import gzip, json, math, os, statistics as st, sys, time, urllib.request, urllib.error

CACHE = "bt_cache/out_wild"
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (research script)", "Accept": "application/json"}


def get(url, data=None, headers=None, tries=3, raw=False):
    h = dict(UA); h.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read()
                enc = r.headers.get("Content-Encoding", "")
                if enc == "br":
                    import brotli
                    b = brotli.decompress(b)
                elif enc == "gzip":
                    b = gzip.decompress(b)
                return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(3); continue
            raise


def save(name, obj):
    with gzip.open(f"{CACHE}/{name}.json.gz", "wt") as f:
        json.dump(obj, f)


def load(name):
    p = f"{CACHE}/{name}.json.gz"
    if os.path.exists(p):
        with gzip.open(p, "rt") as f:
            return json.load(f)
    return None


# ---------------------------------------------------------------- hosts
def hosts():
    for u in ["https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd",
              "https://yields.llama.fi/pools", "https://api-v2.pendle.finance/core/v1/1/markets/active",
              "https://api.skinport.com/v1/items?app_id=730&currency=EUR",
              "https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=AK-47%20%7C%20Redline%20(Field-Tested)",
              "https://api.nasdaq.com/api/nordic/instruments/SSE101/chart?assetClass=SHARES",
              "https://www.avanza.se/_api/market-guide/stock/5247",
              "https://forecastex-public-data.s3.amazonaws.com/prices/daily_prices_20261122.csv",
              "https://api.coinbase.com/v2/prices/BTC-USD/spot", "https://www.bitstamp.net/api/v2/ticker/btcusd/"]:
        try:
            b = get(u, raw=True, headers={"Accept-Encoding": "br"} if "skinport" in u else None)
            print("OK ", u[:90], len(b), b[:100])
        except Exception as e:
            print("ERR", u[:90], str(e)[:120])


# ---------------------------------------------------------------- vol (Deribit DVOL vs real swing)
def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_put(S, K, s, T):
    if T <= 0 or s <= 0:
        return max(K - S, 0)
    d1 = (math.log(S / K) + 0.5 * s * s * T) / (s * math.sqrt(T)); d2 = d1 - s * math.sqrt(T)
    return K * ncdf(-d2) - S * ncdf(-d1)


def bs_call(S, K, s, T):
    return bs_put(S, K, s, T) + S - K


def deribit_daily(cur):
    """Daily DVOL closes and daily index closes (BTC-PERPETUAL as a stand-in for the index) since 2021."""
    c = load(f"dvol_{cur}")
    if c:
        return c
    end = int(time.time() * 1000); start = 1617235200000  # 1 Apr 2021
    dv = {}
    t1 = end
    while t1 > start:
        r = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={cur}"
                f"&start_timestamp={start}&end_timestamp={t1}&resolution=86400")["result"]
        rows = r.get("data") or []
        for ts, o, h, l, cl in rows:
            dv[int(ts) // 1000] = cl
        cont = r.get("continuation")
        if not rows or not cont or cont >= t1:
            break
        t1 = cont
        time.sleep(0.2)
    px = {}
    t0 = start // 1000
    while t0 < end // 1000:
        t2 = min(end // 1000, t0 + 86400 * 900)
        r = get(f"https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name={cur}-PERPETUAL"
                f"&start_timestamp={t0*1000}&end_timestamp={t2*1000}&resolution=60")["result"]
        for ts, o in zip(r.get("ticks", []), r.get("open", [])):
            px[int(ts) // 1000] = o
        t0 = t2
        time.sleep(0.2)
    out = {"dvol": dv, "px": px}
    save(f"dvol_{cur}", out)
    return out


def vol():
    for cur in ["BTC", "ETH"]:
        d = deribit_daily(cur)
        dv = {int(k): v for k, v in d["dvol"].items()}; px = {int(k): v for k, v in d["px"].items()}
        print(f"\n== {cur}: {len(dv)} DVOL days, {len(px)} hourly prices")
        # every Friday 08:00 UTC (Deribit weekly expiry) -> next Friday 08:00
        fri = []
        t = 1617955200 + 8 * 3600  # Fri 9 Apr 2021 08:00 UTC
        while t + 7 * 86400 < time.time():
            fri.append(t); t += 7 * 86400
        res = {"straddle": [], "put10": []}
        ratio = []
        for t0 in fri:
            S0 = px.get(t0); S1 = px.get(t0 + 7 * 86400)
            day0 = t0 - t0 % 86400
            iv = dv.get(day0) or dv.get(day0 - 86400)
            if not (S0 and S1 and iv):
                continue
            s = iv / 100.0 - 0.01      # sell 1 vol point under DVOL (bid side), DVOL is the 30-day swing
            T = 7 / 365.0
            # realized: hourly log moves over the week
            rets = []
            for h in range(7 * 24):
                a, b = px.get(t0 + h * 3600), px.get(t0 + (h + 1) * 3600)
                if a and b:
                    rets.append(math.log(b / a))
            if len(rets) > 100:
                rv = math.sqrt(sum(x * x for x in rets) / len(rets) * 24 * 365)
                ratio.append(rv / (iv / 100))
            fee = 2 * 0.0003 * S0 + 2 * 0.00015 * S0           # trade fee each leg + delivery fee, in USD
            prem = bs_put(S0, S0, s, T) + bs_call(S0, S0, s, T)
            pay = abs(S1 - S0)
            res["straddle"].append((t0, prem, pay, fee, S0))
            # 10-delta-ish put: strike 1.3 weekly swings under
            K = S0 * math.exp(-1.28 * s * math.sqrt(T))
            p = bs_put(S0, K, s + 0.03, T)               # put skew: puts sell ~3 vol points over DVOL
            res["put10"].append((t0, p, max(K - S1, 0), min(0.0003 * S0, 0.125 * p) + min(0.00015 * S0, 0.125 * p), S0))
        if ratio:
            print(f"real swing / implied swing, weekly: median {st.median(ratio):.2f}, mean {st.mean(ratio):.2f}, "
                  f"weeks real > implied: {sum(r > 1 for r in ratio)} of {len(ratio)}")
        for k, rows in res.items():
            if not rows:
                continue
            # per $100 of margin: Deribit needs about 15% of underlying for a short straddle (rough), 10% for a far put
            m = 0.15 if k == "straddle" else 0.10
            pnl = [(prem - pay - fee) for t0, prem, pay, fee, S0 in rows]
            per100 = [100 * (prem - pay - fee) / (m * S0) for t0, prem, pay, fee, S0 in rows]
            cum = 0; peak = 0; dd = 0
            for x in per100:
                cum += x; peak = max(peak, cum); dd = min(dd, cum - peak)
            half = len(per100) // 2
            years = {}
            for (t0, *_), x in zip(rows, per100):
                y = time.strftime("%Y", time.gmtime(t0)); years.setdefault(y, []).append(x)
            print(f"{k}: {len(rows)} weeks, per $100 of margin a week: mean {st.mean(per100):+.2f}, "
                  f"halves {st.mean(per100[:half]):+.2f} / {st.mean(per100[half:]):+.2f}, worst week {min(per100):+.1f}, "
                  f"worst run {dd:+.1f}, weeks lost {sum(x < 0 for x in per100)}")
            print("   by year: " + ", ".join(f"{y} {st.mean(v):+.2f} ({len(v)})" for y, v in sorted(years.items())))
            print(f"   one contract (0.1 {cur}) at today's price: premium ~${rows[-1][1]*0.1:.0f}, margin ~${m*rows[-1][4]*0.1:.0f}")
            if k == "put10":
                try:
                    sys.path.insert(0, "."); import exam
                    bets = [{"ev": t0, "t": t0, "cost": m * S0, "pay": m * S0 + (prem - pay - fee)}
                            for t0, prem, pay, fee, S0 in rows]
                    exam.score(bets, f"wild: sell weekly far put {cur} (Deribit DVOL, model prices)", tries=4,
                               src="outside/wild.py vol", log=False)
                except Exception as e:
                    print("exam skipped:", e)
    # live check: what a real weekly put really sells for vs our model
    try:
        r = get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option")["result"]
        ins = get("https://www.deribit.com/api/v2/public/get_instruments?currency=BTC&kind=option&expired=false")["result"]
        print("\nDeribit BTC options live:", len(r), "books; min trade", sorted({i['min_trade_amount'] for i in ins}),
              "BTC; tick", sorted({i['tick_size'] for i in ins})[:3])
        idx = get("https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd")["result"]["index_price"]
        near = sorted({i["expiration_timestamp"] for i in ins})[:3]
        for e in near:
            puts = [x for x in r if x["instrument_name"] in {i["instrument_name"] for i in ins
                    if i["expiration_timestamp"] == e and i["option_type"] == "put"}]
            for x in sorted(puts, key=lambda x: -float(x["instrument_name"].split("-")[2]))[:40]:
                K = float(x["instrument_name"].split("-")[2])
                if 0.88 * idx < K < 0.96 * idx and x.get("bid_price"):
                    print(f"  {x['instrument_name']}: bid {x['bid_price']} ask {x['ask_price']} BTC "
                          f"(= ${x['bid_price']*idx*0.1:.2f} / ${(x['ask_price'] or 0)*idx*0.1:.2f} per 0.1 BTC), "
                          f"mark iv {x.get('mark_iv')}")
    except Exception as e:
        print("live check failed:", e)


# ---------------------------------------------------------------- defi
def defi():
    pools = get("https://yields.llama.fi/pools")["data"]
    lend = [p for p in pools if p.get("stablecoin") and (p.get("tvlUsd") or 0) > 50e6 and p.get("exposure") == "single"
            and p.get("project") in ("aave-v3", "morpho-blue", "compound-v3", "spark", "fluid-lending", "euler-v2",
                                     "sky-lending", "maple", "morpho-v1")]
    lend.sort(key=lambda p: -(p.get("apy") or 0))
    print(f"{len(pools)} pools; {len(lend)} big single-stablecoin lending pools")
    for p in lend[:25]:
        print(f"  {p['project']:14} {p['chain']:10} {p['symbol']:10} tvl ${p['tvlUsd']/1e6:7.0f}M  apy {p['apy']:.2f} "
              f"(base {p.get('apyBase') or 0:.2f} reward {p.get('apyReward') or 0:.2f}) 30d mean {p.get('apyMean30d') or 0:.2f}")
    # one year of history for the biggest USDC pools on cheap chains
    picks = [p for p in lend if p["symbol"] in ("USDC", "USDT", "EURC") and p["chain"] in ("Base", "Arbitrum", "Ethereum", "Optimism", "Polygon")]
    picks.sort(key=lambda p: -p["tvlUsd"])
    for p in picks[:8]:
        try:
            ch = get(f"https://yields.llama.fi/chart/{p['pool']}")["data"]
        except Exception as e:
            print("chart fail", e); continue
        last = [x for x in ch if x.get("apyBase") is not None][-365:]
        if not last:
            continue
        a = [x["apyBase"] for x in last]
        print(f"  history {p['project']} {p['chain']} {p['symbol']}: {len(a)} days, base apy mean {st.mean(a):.2f}, "
              f"low {min(a):.2f}, high {max(a):.2f}  -> $300 for a year about ${3*st.mean(a):.2f}")
    # same-chain stablecoin lend vs borrow gap
    try:
        lb = {x["pool"]: x for x in get("https://yields.llama.fi/lendBorrow")}
        rows = [p for p in pools if p["pool"] in lb and p.get("stablecoin") and (p.get("tvlUsd") or 0) > 5e6]
        best = []
        for chain in {p["chain"] for p in rows}:
            c = [p for p in rows if p["chain"] == chain]
            for a in c:
                for b in c:
                    if a is b or a["symbol"] != b["symbol"]:
                        continue
                    br = (lb[b["pool"]].get("apyBaseBorrow") or 0) - (lb[b["pool"]].get("apyRewardBorrow") or 0)
                    if lb[b["pool"]].get("apyBaseBorrow") is None:
                        continue
                    gap = (a.get("apy") or 0) - br
                    best.append((gap, chain, a["symbol"], a["project"], b["project"], a.get("apy"), br, lb[b["pool"]].get("ltv")))
        best.sort(reverse=True)
        print("\nsame-coin lend here / borrow there gaps (yearly %, before gas, needs collateral):")
        for g in best[:10]:
            print("  gap %.2f %s %s lend %s %.2f borrow %s %.2f ltv %s" % (g[0], g[1], g[2], g[3], g[5], g[4], g[6], g[7]))
    except Exception as e:
        print("lendBorrow failed", e)


# ---------------------------------------------------------------- pendle
def pendle():
    out = []
    for chain in (1, 42161, 8453):
        mk = []
        for path in (f"https://api-v2.pendle.finance/core/v1/{chain}/markets/inactive",
                     f"https://api-v2.pendle.finance/core/v1/{chain}/markets/active"):
            try:
                r = get(path)
                mk += r.get("markets", r if isinstance(r, list) else [])
            except Exception as e:
                print("pendle list fail", path, str(e)[:100])
        print(f"chain {chain}: {len(mk)} markets; keys {list(mk[0].keys())[:12] if mk else None}")
        for m in mk:
            addr = m.get("address"); exp = m.get("expiry")
            name = m.get("name") or m.get("symbol")
            if not addr:
                continue
            out.append((chain, addr, name, exp))
    print("markets total", len(out))
    rows = []
    stable_words = ("USD", "DAI", "USDe", "GHO", "FRAX", "crvUSD")
    for chain, addr, name, exp in out:
        if not any(w.lower() in str(name).lower() for w in stable_words):
            continue
        try:
            h = get(f"https://api-v2.pendle.finance/core/v2/{chain}/markets/{addr}/historical-data?time_frame=day")
        except Exception as e:
            try:
                h = get(f"https://api-v2.pendle.finance/core/v1/{chain}/markets/{addr}/historical-data?time_frame=day")
            except Exception as e2:
                continue
        ts = h.get("timestamp") or []
        imp = h.get("impliedApy") or []
        und = h.get("underlyingApy") or []
        tvl = h.get("tvl") or [0] * len(ts)
        if len(ts) < 40 or len(imp) != len(ts) or len(und) != len(ts):
            continue
        # buy the fixed yield at day i, hold to the end of the history (or expiry): fixed - floating that followed
        n = len(ts)
        for i in range(0, n - 30, 7):
            fut = [u for u in und[i:] if u is not None]
            if not fut or imp[i] is None:
                continue
            rows.append((name, chain, ts[i], imp[i], st.mean(fut), (tvl[i] or 0), n - i))
        time.sleep(0.15)
    if not rows:
        print("no pendle rows"); return
    gaps = [r[3] - r[4] for r in rows]
    print(f"stablecoin Pendle looks (weekly, to the end): {len(rows)} from {len({r[0] for r in rows})} markets")
    print(f"  fixed minus floating that followed (yearly, as share): median {st.median(gaps):+.4f}, mean {st.mean(gaps):+.4f}, "
          f"fixed won {sum(g > 0 for g in gaps)} of {len(gaps)}")
    big = [r for r in rows if r[5] > 20e6]
    if big:
        g2 = [r[3] - r[4] for r in big]
        print(f"  pools over $20M: {len(big)} looks, median {st.median(g2):+.4f}, fixed won {sum(g > 0 for g in g2)}")
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(r[3] - r[4])
    worst = sorted(by.items(), key=lambda kv: st.mean(kv[1]))
    print("  worst markets:", [(k, round(st.mean(v), 3)) for k, v in worst[:5]])
    print("  best markets:", [(k, round(st.mean(v), 3)) for k, v in worst[-5:]])


# ---------------------------------------------------------------- skins
def skins(tag="now"):
    hdr = {"Accept-Encoding": "br"}
    items = get("https://api.skinport.com/v1/items?app_id=730&currency=EUR&tradable=0", headers=hdr)
    time.sleep(2)
    hist = get("https://api.skinport.com/v1/sales/history?app_id=730&currency=EUR", headers=hdr)
    hs = {h["market_hash_name"]: h for h in hist}
    snap = {"t": int(time.time()), "items": {i["market_hash_name"]: [i.get("min_price"), i.get("quantity"), i.get("suggested_price")]
                                              for i in items}}
    old = load("skins_snap")
    save("skins_snap", snap)
    print(f"{len(items)} items listed, {len(hist)} with sale history")
    SELL_FEE = 0.08     # Skinport seller fee for private sellers (rough; 6% above a sales level)
    rows = []
    for i in items:
        h = hs.get(i["market_hash_name"])
        mp = i.get("min_price")
        if not h or not mp:
            continue
        w7 = h.get("last_7_days") or {}; w30 = h.get("last_30_days") or {}
        if (w7.get("volume") or 0) < 20 or not w7.get("median") or not w30.get("median"):
            continue
        ref = min(w7["median"], w30["median"])
        back = ref * (1 - SELL_FEE)
        if back > mp * 1.05 and mp >= 1:
            rows.append((back / mp - 1, i["market_hash_name"], mp, w7["median"], w30["median"], w7["volume"], i.get("quantity")))
    rows.sort(reverse=True)
    print(f"items with 20+ sales a week where the cheapest listing is 5%+ under what a resale brings after the 8% fee: {len(rows)}")
    tot = sum(r[3] * (1 - SELL_FEE) - r[2] for r in rows)
    print(f"  one of each: buy EUR {sum(r[2] for r in rows):.0f}, resale after fee EUR {sum(r[3]*(1-SELL_FEE) for r in rows):.0f}, "
          f"paper gain EUR {tot:.0f}")
    for r in rows[:15]:
        print(f"  {r[0]*100:5.0f}%  {r[1][:50]:50} min {r[2]:.2f} med7 {r[3]:.2f} med30 {r[4]:.2f} vol7 {r[5]} listed {r[6]}")
    if old:
        dt = (snap["t"] - old["t"]) / 3600
        gone = same = 0
        for name, (mp, q, sp) in old["items"].items():
            now = snap["items"].get(name)
            h = hs.get(name)
            if not h or not mp or not now:
                continue
            w7 = h.get("last_7_days") or {}
            if (w7.get("volume") or 0) < 20 or not w7.get("median"):
                continue
            if min(w7["median"], (h.get("last_30_days") or {}).get("median") or 1e9) * (1 - SELL_FEE) > mp * 1.05 and mp >= 1:
                if now[0] and now[0] > mp * 1.001:
                    gone += 1
                else:
                    same += 1
        print(f"vs snapshot {dt:.1f} h ago: of last time's cheap listings, {gone} were bought (price went up), {same} still there")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "hosts"
    {"hosts": hosts, "vol": vol, "defi": defi, "pendle": pendle, "skins": skins}[cmd](*sys.argv[2:])
    print("=== DONE ===")
