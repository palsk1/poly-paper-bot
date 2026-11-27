"""Cross-exchange, triangular and stablecoin price gaps on spot crypto venues a Swede can use.

Research only: reads public market data, never trades, no keys.
  python3 outside/crossx.py hosts                 which venues answer from here
  python3 outside/crossx.py sample MIN SEC        sample every venue's best bid/ask every SEC s for MIN minutes,
                                                  re-check every candidate gap on the full books at once, then report
  python3 outside/crossx.py report                report on saved snapshots (bt_cache/out_crossx/)
  python3 outside/crossx.py depeg                 stablecoin dips under $0.99 in Binance's public history + a buy rule
Taker fees are the lowest-tier, small-account public rates (see FEES; rough, checked Nov 2026).
"""
import gzip, io, json, os, sys, time, zipfile, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

DIR = "bt_cache/out_crossx"
UA = {"User-Agent": "Mozilla/5.0 (research script)"}
# taker fee per trade, small account (rough): kraken pro 0.40, stable/fx pairs 0.20; bitstamp 0.40; coinbase advanced
# 1.20; bitvavo 0.25; okx 0.10; binance 0.10; bitfinex 0.20
FEES = {"kraken": 0.0040, "bitstamp": 0.0040, "coinbase": 0.0120, "bitvavo": 0.0025, "okx": 0.0010,
        "binance": 0.0010, "bitfinex": 0.0020, "firi": 0.0070}
STABLE_FEE = {"kraken": 0.0020, "bitstamp": 0.0040, "coinbase": 0.0000, "bitvavo": 0.0025, "okx": 0.0010,
              "binance": 0.0010, "bitfinex": 0.0020}
STABLES = {"USDC", "USDT", "EURC", "USDG", "PYUSD", "DAI", "EURQ", "EURR", "RLUSD", "USDE", "FDUSD", "EURI", "USD1"}
QUOTES = {"EUR", "BTC", "USD", "SEK", "USDC"}


def fee(v, base, quote):
    if base in STABLES or (base, quote) in (("EUR", "USD"),):
        return STABLE_FEE.get(v, FEES.get(v, 0.004))
    return FEES.get(v, 0.004)


def get(url, timeout=10):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def norm(c):
    c = c.upper()
    return {"XBT": "BTC", "XXBT": "BTC", "XDG": "DOGE", "XXDG": "DOGE", "ZEUR": "EUR", "ZUSD": "USD", "XETH": "ETH"}.get(c, c)


# ---------- discovery: (venue, base, quote) -> symbol ----------
def discover():
    m = {}
    try:
        ap = get("https://api.kraken.com/0/public/AssetPairs")["result"]
        for k, v in ap.items():
            ws = v.get("wsname", "")
            if "/" not in ws or k.endswith(".d"):
                continue
            b, q = [norm(x) for x in ws.split("/")]
            if q in QUOTES:
                m[("kraken", b, q)] = k
    except Exception as e:
        print("kraken discover", e)
    try:
        for p in get("https://www.bitstamp.net/api/v2/trading-pairs-info/"):
            if p.get("trading") != "Enabled":
                continue
            b, q = [norm(x) for x in p["name"].split("/")]
            if q in QUOTES:
                m[("bitstamp", b, q)] = p["url_symbol"]
    except Exception as e:
        print("bitstamp discover", e)
    try:
        for p in get("https://api.exchange.coinbase.com/products"):
            if p.get("status") != "online" or p.get("trading_disabled"):
                continue
            b, q = p["base_currency"], p["quote_currency"]
            if q in ("EUR", "BTC", "USDC"):
                m[("coinbase", b, q)] = p["id"]
    except Exception as e:
        print("coinbase discover", e)
    try:
        for p in get("https://api.bitvavo.com/v2/markets"):
            if p.get("status") == "trading":
                m[("bitvavo", p["base"], p["quote"])] = p["market"]
    except Exception as e:
        print("bitvavo discover", e)
    try:
        for p in get("https://www.okx.com/api/v5/public/instruments?instType=SPOT")["data"]:
            if p.get("state") == "live" and p["quoteCcy"] in QUOTES:
                m[("okx", p["baseCcy"], p["quoteCcy"])] = p["instId"]
    except Exception as e:
        print("okx discover", e)
    try:
        for p in get("https://data-api.binance.vision/api/v3/exchangeInfo?permissions=SPOT", 20)["symbols"]:
            if p.get("status") == "TRADING" and p["quoteAsset"] in QUOTES:
                m[("binance", p["baseAsset"], p["quoteAsset"])] = p["symbol"]
    except Exception as e:
        print("binance discover", e)
    try:
        for s in get("https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange")[0]:
            if ":" in s:
                b, q = s.split(":")
            else:
                b, q = s[:3], s[3:]
            b = {"UST": "USDT", "UDC": "USDC", "DOG": "DOGE"}.get(b, b)
            q = {"UST": "USDT"}.get(q, q)
            if q in QUOTES:
                m[("bitfinex", b, q)] = "t" + s
    except Exception as e:
        print("bitfinex discover", e)
    for s in ("BTCSEK", "ETHSEK", "SOLSEK", "XRPSEK", "ADASEK", "LTCSEK", "USDCSEK", "DAISEK", "BTCEUR", "ETHEUR"):
        m[("firi", s[:-3], s[-3:])] = s
    return m


# ---------- top of book, one call per venue where possible ----------
def tops(m):
    by = {}
    for (v, b, q), s in m.items():
        by.setdefault(v, {})[s] = (b, q)
    out = {}

    def put(v, s, bid, bs, ask, az):
        bq = by[v].get(s)
        if bq and bid and ask and float(bid) > 0 and float(ask) > 0:
            out[(v,) + bq] = (float(bid), float(bs or 0), float(ask), float(az or 0), time.time())

    def kraken():
        keys = list(by.get("kraken", {}))
        for i in range(0, len(keys), 120):
            r = get("https://api.kraken.com/0/public/Ticker?pair=" + ",".join(keys[i:i + 120]))
            for k, t in r.get("result", {}).items():
                put("kraken", k, t["b"][0], t["b"][2], t["a"][0], t["a"][2])

    def binance():
        for t in get("https://data-api.binance.vision/api/v3/ticker/bookTicker", 20):
            put("binance", t["symbol"], t["bidPrice"], t["bidQty"], t["askPrice"], t["askQty"])

    def okx():
        for t in get("https://www.okx.com/api/v5/market/tickers?instType=SPOT")["data"]:
            put("okx", t["instId"], t["bidPx"], t["bidSz"], t["askPx"], t["askSz"])

    def bitvavo():
        for t in get("https://api.bitvavo.com/v2/ticker/book"):
            put("bitvavo", t["market"], t.get("bid"), t.get("bidSize"), t.get("ask"), t.get("askSize"))

    def bitfinex():
        for t in get("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL"):
            if t[0].startswith("t") and len(t) > 4:
                put("bitfinex", t[0], t[1], t[2], t[3], t[4])

    def bitstamp():  # no sizes in the ticker: size 0 = unknown, checked on the full book later
        for t in get("https://www.bitstamp.net/api/v2/ticker/"):
            s = t["pair"].replace("/", "").lower()
            put("bitstamp", s, t.get("bid"), 0, t.get("ask"), 0)

    def coinbase():
        syms = list(by.get("coinbase", {}))
        def one(s):
            try:
                r = get(f"https://api.exchange.coinbase.com/products/{s}/book?level=1", 8)
                put("coinbase", s, r["bids"][0][0], r["bids"][0][1], r["asks"][0][0], r["asks"][0][1])
            except Exception:
                pass
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(one, syms))

    def firi():
        for s in by.get("firi", {}):
            try:
                r = get(f"https://api.firi.com/v2/markets/{s}/depth", 8)
                bb, aa = lvls(r.get("bids")), lvls(r.get("asks"))
                if bb and aa:
                    put("firi", s, bb[0][0], bb[0][1], aa[0][0], aa[0][1])
            except Exception:
                pass

    fns = [kraken, binance, okx, bitvavo, bitfinex, bitstamp, coinbase, firi]
    errs = {}
    def run(f):
        try:
            f()
        except Exception as e:
            errs[f.__name__] = str(e)[:80]
    with ThreadPoolExecutor(len(fns)) as ex:
        list(ex.map(run, fns))
    return out, errs


def lvls(x):
    o = []
    for e in x or []:
        if isinstance(e, dict):
            p = e.get("price"); a = e.get("amount", e.get("size", e.get("quantity", e.get("volume"))))
        else:
            p, a = e[0], e[1]
        try:
            o.append((float(p), abs(float(a))))
        except Exception:
            pass
    return o


def book(v, sym):
    """Full-ish book: (bids high->low, asks low->high)."""
    if v == "kraken":
        r = get(f"https://api.kraken.com/0/public/Depth?pair={sym}&count=25")["result"]
        r = list(r.values())[0]
        return lvls(r["bids"]), lvls(r["asks"])
    if v == "binance":
        r = get(f"https://data-api.binance.vision/api/v3/depth?symbol={sym}&limit=25")
    elif v == "okx":
        r = get(f"https://www.okx.com/api/v5/market/books?instId={sym}&sz=25")["data"][0]
    elif v == "bitvavo":
        r = get(f"https://api.bitvavo.com/v2/{sym}/book?depth=25")
    elif v == "coinbase":
        r = get(f"https://api.exchange.coinbase.com/products/{sym}/book?level=2")
    elif v == "bitstamp":
        r = get(f"https://www.bitstamp.net/api/v2/order_book/{sym}/")
    elif v == "firi":
        r = get(f"https://api.firi.com/v2/markets/{sym}/depth")
    elif v == "bitfinex":
        raw = get(f"https://api-pub.bitfinex.com/v2/book/{sym}/P0?len=25")
        return ([(p, a) for p, c, a in raw if a > 0], [(p, -a) for p, c, a in raw if a < 0])
    else:
        return [], []
    b, a = lvls(r.get("bids")), lvls(r.get("asks"))
    return sorted(b, key=lambda x: -x[0])[:40], sorted(a)[:40]


def walk(levels, qty):
    """Average price to fill qty on these levels, or None if too thin."""
    got, cost = 0.0, 0.0
    for p, a in levels:
        take = min(a, qty - got)
        got += take; cost += take * p
        if got >= qty - 1e-12:
            return cost / qty
    return None


def cross_profit(ask_lv, fa, bid_lv, fb, eur):
    """Buy eur worth on A at asks, sell the same coins on B at bids; profit in eur after both taker fees."""
    if not ask_lv or not bid_lv:
        return None
    q = eur / ask_lv[0][0]
    pa, pb = walk(ask_lv, q), walk(bid_lv, q)
    if pa is None or pb is None:
        return None
    return q * pb * (1 - fb) - q * pa * (1 + fa)


# ---------- sampling ----------
def sample(minutes=60, every=15):
    os.makedirs(DIR, exist_ok=True)
    m = discover()
    vc = {}
    for (v, b, q) in m:
        vc[v] = vc.get(v, 0) + 1
    print("pairs found per venue:", vc)
    # keep coins quoted in EUR on 2+ venues for the cross check; cross pairs for triangles; stable/fx pairs
    eurv = {}
    for (v, b, q) in m:
        if q == "EUR":
            eurv.setdefault(b, set()).add(v)
    keep = {k: s for k, s in m.items() if k[0] == "firi" or (k[2] == "EUR" and len(eurv.get(k[1], ())) >= 2)
            or (k[2] == "BTC" and k[0] in eurv.get(k[1], ()) and k[0] in eurv.get("BTC", ()))
            or k[1] in STABLES or (k[1], k[2]) in (("EUR", "USD"), ("BTC", "USD"), ("ETH", "USD"))}
    # coinbase per-product calls: cap
    cb = [k for k in keep if k[0] == "coinbase"]
    cb.sort(key=lambda k: (-len(eurv.get(k[1], ())), k))
    for k in cb[60:]:
        keep.pop(k)
    print("kept pairs:", len(keep), " coins on 2+ EUR venues:", sum(1 for b, s in eurv.items() if len(s) >= 2))
    fn = f"{DIR}/snap_{time.strftime('%Y%m%dT%H%M', time.gmtime())}.jsonl.gz"
    t_end = time.time() + minutes * 60
    n = 0; nchk = 0
    eursek = fx_sek()
    with gzip.open(fn, "at") as f:
        while time.time() < t_end:
            t0 = time.time()
            top, errs = tops(keep)
            # candidates: cross-venue gross gap > fees on top of book
            cands = []
            byc = {}
            for (v, b, q), t in top.items():
                if q == "EUR":
                    byc.setdefault(b, []).append((v, t))
            for b, lst in byc.items():
                for va, ta in lst:
                    for vb, tb in lst:
                        if va == vb:
                            continue
                        fa, fb = fee(va, b, "EUR"), fee(vb, b, "EUR")
                        if tb[0] * (1 - fb) > ta[2] * (1 + fa):
                            cands.append((b, va, vb))
            # triangles with top of book: EUR->C->BTC->EUR and back
            tri = []
            for v in set(k[0] for k in top):
                be = top.get((v, "BTC", "EUR"))
                if not be:
                    continue
                for (vv, c, q), cb_ in top.items():
                    if vv != v or q != "BTC":
                        continue
                    ce = top.get((v, c, "EUR"))
                    if not ce:
                        continue
                    f3 = (1 - fee(v, c, "EUR")) ** 3
                    g1 = (1 / ce[2]) * cb_[0] * be[0]          # buy C/EUR, sell C/BTC, sell BTC/EUR
                    g2 = (1 / be[2]) * (1 / cb_[2]) * ce[0]    # buy BTC/EUR, buy C/BTC, sell C/EUR
                    tri.append((v, c, round((g1 - 1) * 1e4, 1), round((g2 - 1) * 1e4, 1), round((g1 * f3 - 1) * 1e4, 1),
                                round((g2 * f3 - 1) * 1e4, 1)))
            # re-check candidates on full books right away (cap per snapshot)
            checks = []
            def chk(c):
                b, va, vb = c
                try:
                    t1 = time.time()
                    with ThreadPoolExecutor(2) as ex:
                        fa_ = ex.submit(book, va, keep[(va, b, "EUR")]); fb_ = ex.submit(book, vb, keep[(vb, b, "EUR")])
                        A, B = fa_.result(), fb_.result()
                    r = {"b": b, "buy": va, "sell": vb, "ms": int((time.time() - t1) * 1000)}
                    for eur in (50, 100, 300):
                        p = cross_profit(A[1], fee(va, b, "EUR"), B[0], fee(vb, b, "EUR"), eur)
                        r[str(eur)] = None if p is None else round(p, 3)
                    r["ga"] = A[1][0][0] if A[1] else None; r["gb"] = B[0][0][0] if B[0] else None
                    return r
                except Exception as e:
                    return {"b": b, "buy": va, "sell": vb, "err": str(e)[:60]}
            cands.sort()
            with ThreadPoolExecutor(6) as ex:
                checks = list(ex.map(chk, cands[:24]))
            nchk += len(checks)
            rec = {"t": round(t0, 1), "top": {"|".join(k): [round(x, 10) for x in v[:4]] for k, v in top.items()},
                   "cands": [list(c) for c in cands], "checks": checks, "tri": tri, "errs": errs, "eursek": eursek}
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
            n += 1
            if n % 20 == 1:
                print(time.strftime("%H:%M:%S"), "snap", n, "pairs", len(top), "cands", len(cands), "errs", errs, flush=True)
            if n % 40 == 0:
                eursek = fx_sek() or eursek
            time.sleep(max(0, every - (time.time() - t0)))
    print("snapshots", n, "checked", nchk, "file", fn)
    report()


def fx_sek():
    try:
        return get("https://api.frankfurter.app/latest?from=EUR&to=SEK,USD")["rates"]
    except Exception:
        try:
            r = get("https://open.er-api.com/v6/latest/EUR")["rates"]
            return {"SEK": r["SEK"], "USD": r["USD"]}
        except Exception:
            return None


# ---------- report ----------
def load():
    recs = []
    for fn in sorted(os.listdir(DIR)) if os.path.isdir(DIR) else []:
        if fn.startswith("snap_"):
            with gzip.open(f"{DIR}/{fn}", "rt") as f:
                for line in f:
                    try:
                        recs.append(json.loads(line))
                    except Exception:
                        pass
    return recs


def report():
    R = load()
    if not R:
        print("no snapshots"); return
    print(f"\n=== REPORT: {len(R)} snapshots, {time.strftime('%Y-%m-%d %H:%M', time.gmtime(R[0]['t']))} to "
          f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(R[-1]['t']))} UTC ===")
    # 1. cross-venue
    pos = {}
    tot = {"50": 0, "100": 0, "300": 0}
    best = []
    ncand = sum(len(r["cands"]) for r in R)
    nchk = 0
    prev = set()
    episodes = {}
    for r in R:
        cur = set()
        for c in r["checks"]:
            if "err" in c:
                continue
            nchk += 1
            key = (c["b"], c["buy"], c["sell"])
            for e in ("50", "100", "300"):
                if c.get(e) is not None and c[e] > 0:
                    pos.setdefault(key, {"50": [], "100": [], "300": []})[e].append(c[e])
            if c.get("100") is not None and c["100"] > 0:
                cur.add(key)
                if key not in prev:
                    episodes.setdefault(key, []).append([c["100"], c.get("300") or 0, 1])
                else:
                    ep = episodes[key][-1]; ep[0] = max(ep[0], c["100"]); ep[1] = max(ep[1], c.get("300") or 0); ep[2] += 1
            best.append((c.get("100") or -99, c))
        prev = cur
    print(f"\n1) CROSS-VENUE (EUR pairs): top-of-book candidates {ncand}, re-checked on full books {nchk}")
    n100 = sum(len(v["100"]) for v in pos.values()); n300 = sum(len(v["300"]) for v in pos.values())
    print(f"   re-checks still positive after both taker fees: at EUR100 {n100}, at EUR300 {n300}")
    neps = sum(len(v) for v in episodes.values())
    e100 = sum(ep[0] for v in episodes.values() for ep in v); e300 = sum(ep[1] for v in episodes.values() for ep in v)
    hours = (R[-1]["t"] - R[0]["t"]) / 3600 or 1
    print(f"   separate episodes (one trade per gap until it closes): {neps}; take each once: "
          f"EUR{e100:.2f} at EUR100 a trade, EUR{e300:.2f} at EUR300, over {hours:.1f} h")
    rows = sorted(((sum(v['100']), k, len(v['100']), len(episodes.get(k, [])), sum(v['300']), len(v['300']))
                   for k, v in pos.items()), reverse=True)[:20]
    print("   coin buy->sell | positive looks | episodes | sum EUR at 100 | at 300 (n)")
    for s, k, n, ne, s3, n3 in rows:
        print(f"   {k[0]:7s} {k[1]:>8s}->{k[2]:<8s} {n:4d} {ne:4d}  {s:8.2f}  {s3:8.2f} ({n3})")
    # gross gaps on top of book, by coin, how often > 1 per mille ignoring fees (to show how far fees are)
    gg = {}
    for r in R:
        byc = {}
        for k, v in r["top"].items():
            vn, b, q = k.split("|")
            if q == "EUR" and b not in STABLES:
                byc.setdefault(b, []).append((vn, v))
        for b, lst in byc.items():
            if len(lst) < 2:
                continue
            hb = max(lst, key=lambda x: x[1][0]); la = min(lst, key=lambda x: x[1][2])
            if hb[0] != la[0]:
                g = (hb[1][0] / la[1][2] - 1) * 1e4
                gg.setdefault(b, []).append(g)
    print("\n   gross gap best bid elsewhere vs cheapest ask, per coin (cents per EUR100, before fees): median / 90th pct / max, looks")
    rows = []
    for b, l in gg.items():
        l.sort()
        rows.append((l[int(len(l) * .9)], b, l[len(l) // 2], l[-1], len(l)))
    rows.sort(reverse=True)
    for p90, b, med, mx, n in rows[:25]:
        print(f"   {b:8s} {med:8.1f} {p90:8.1f} {mx:9.1f} {n:5d}")
    print("   (100 = EUR1.00 per EUR100 before fees; the cheapest pair of taker fees is 2 x 0.10 = 20 on okx+binance)")
    print("   biggest single re-checked results at EUR100:")
    for p, c in sorted(best, key=lambda x: -x[0])[:8]:
        print("   ", c)
    # 2. triangles
    print("\n2) TRIANGLES inside one venue (EUR->coin->BTC->EUR and back), cents per EUR100")
    tri = {}
    for r in R:
        for v, c, g1, g2, n1, n2 in r["tri"]:
            tri.setdefault((v, c), []).append((max(g1, g2), max(n1, n2)))
    rows = []
    for k, l in tri.items():
        g = sorted(x[0] for x in l); nn = sorted(x[1] for x in l)
        rows.append((nn[-1], k, g[len(g) // 2], g[-1], sum(1 for x in nn if x > 0), len(l)))
    rows.sort(reverse=True)
    print("   venue coin | best-way gross median | gross max | positive after 3 taker fees / looks | best net")
    for mx, k, gm, gx, npos, n in rows[:20]:
        print(f"   {k[0]:8s} {k[1]:6s} {gm:7.1f} {gx:7.1f}   {npos}/{n}   {mx:7.1f}")
    print(f"   triangles tracked: {len(tri)}, with any net-positive look: {sum(1 for r_ in rows if r_[4] > 0)}")
    # 3. stablecoins and SEK
    print("\n3) STABLECOINS vs EUR/USD, and SEK prices vs EUR x EURSEK")
    st = {}
    for r in R:
        top = r["top"]
        eu = top.get("kraken|EUR|USD")
        fxr = r.get("eursek") or {}
        eurusd = (eu[0] + eu[2]) / 2 if eu else fxr.get("USD")
        if not eurusd:
            continue
        for k, v in top.items():
            vn, b, q = k.split("|")
            if b in ("USDC", "USDT") and q == "EUR":
                # fair EUR price of one dollar = 1/eurusd; buy premium in cents per 100
                fair = 1 / eurusd
                st.setdefault((vn, b, "buy"), []).append((v[2] / fair - 1) * 1e4)
                st.setdefault((vn, b, "sell"), []).append((v[0] / fair - 1) * 1e4)
            if b in ("USDC", "USDT") and q == "USD":
                st.setdefault((vn, b + "/USD", "mid"), []).append(((v[0] + v[2]) / 2 - 1) * 1e4)
            if b == "EURC" and q in ("EUR", "USDC", "USD"):
                fair = 1.0 if q == "EUR" else eurusd
                st.setdefault((vn, "EURC/" + q, "mid"), []).append(((v[0] + v[2]) / 2 / fair - 1) * 1e4)
    print("   venue pair side | median / min / max (cents per 100 above fair; buy side >0 = you pay more)")
    for k in sorted(st):
        l = sorted(st[k])
        print(f"   {k[0]:8s} {k[1]:10s} {k[2]:4s} {l[len(l)//2]:7.1f} {l[0]:7.1f} {l[-1]:7.1f}  n={len(l)}")
    # stable triangle on kraken: EUR->USDC->USD->EUR
    tk = []
    for r in R:
        t = r["top"]
        a = t.get("kraken|USDC|EUR"); b = t.get("kraken|USDC|USD"); c = t.get("kraken|EUR|USD")
        if a and b and c:
            g1 = (1 / a[2]) * b[0] / c[2]     # buy USDC with EUR, sell for USD, buy EUR with USD
            g2 = c[0] * (1 / b[2]) * a[0]     # sell EUR for USD, buy USDC, sell USDC for EUR
            tk.append(max(g1, g2))
    if tk:
        tk.sort()
        f = (1 - 0.002) ** 3
        print(f"   kraken EUR->USDC->USD->EUR best way gross: median {(tk[len(tk)//2]-1)*1e4:.1f}, max {(tk[-1]-1)*1e4:.1f}; "
              f"after 3 x 0.20 fee max {(tk[-1]*f-1)*1e4:.1f} cents per 100, positive looks {sum(1 for x in tk if x*f>1)}/{len(tk)}")
    sek = {}
    for r in R:
        fxr = r.get("eursek") or {}
        if not fxr.get("SEK"):
            continue
        for k, v in r["top"].items():
            vn, b, q = k.split("|")
            if q != "SEK":
                continue
            ref = [x for kk, x in r["top"].items() if kk.split("|")[1] == b and kk.split("|")[2] == "EUR" and kk.split("|")[0] in ("kraken", "bitstamp", "bitvavo")]
            if not ref:
                continue
            mid_eur = sorted((x[0] + x[2]) / 2 for x in ref)[len(ref) // 2]
            fair = mid_eur * fxr["SEK"]
            sek.setdefault((vn, b), []).append(((v[2] / fair - 1) * 1e4, (v[0] / fair - 1) * 1e4, (v[2] / v[0] - 1) * 1e4))
    print("   SEK books (vs median EUR mid x ECB EURSEK): buy premium median / sell premium median / own spread median, cents per 100")
    for k, l in sorted(sek.items()):
        a = sorted(x[0] for x in l); s = sorted(x[1] for x in l); sp = sorted(x[2] for x in l)
        print(f"   {k[0]:6s} {k[1]:5s} buy {a[len(a)//2]:7.1f} (min {a[0]:.1f})  sell {s[len(s)//2]:7.1f} (max {s[-1]:.1f})  spread {sp[len(sp)//2]:.1f}  n={len(l)}")
    errs = {}
    for r in R:
        for k in r.get("errs", {}):
            errs[k] = errs.get(k, 0) + 1
    print("   venue errors (snapshots):", errs)
    print("=== DONE ===")


# ---------- depeg history ----------
def kl(sym, iv, ym):
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/{iv}/{sym}-{iv}-{ym}.zip"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        rows = []
        for line in z.read(z.namelist()[0]).decode().splitlines():
            p = line.split(",")
            if not p[0].isdigit():
                continue
            t = int(p[0]); t = t // 1000 if t > 1e14 else t  # 2025+ files are in microseconds
            rows.append((t / 1000, float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[7])))
        return rows
    except urllib.error.HTTPError:
        return None
    except Exception as e:
        print("kl", sym, ym, e); return None


def depeg():
    os.makedirs(DIR, exist_ok=True)
    syms = ["USDCUSDT", "BUSDUSDT", "TUSDUSDT", "USDPUSDT", "PAXUSDT", "DAIUSDT", "FDUSDUSDT", "USTUSDT", "USTCUSDT",
            "USDTDAI", "EURCUSDT", "PYUSDUSDT", "USD1USDT", "USDEUSDT", "XUSDUSDT", "BFUSDUSDT", "AEURUSDT", "RLUSDUSDT"]
    months = [f"{y}-{mo:02d}" for y in range(2019, 2027) for mo in range(1, 13) if f"{y}-{mo:02d}" <= "2026-10"]
    cache = f"{DIR}/depeg_daily.json"
    D = json.load(open(cache)) if os.path.exists(cache) else {}
    for s in syms:
        if s in D:
            continue
        rows = []
        def one(ym):
            return kl(s, "1d", ym) or []
        with ThreadPoolExecutor(12) as ex:
            for r in ex.map(one, months):
                rows += r
        D[s] = sorted(rows)
        print(s, "days", len(rows), flush=True)
    json.dump(D, open(cache, "w"))
    print("\nDaily lows under $0.99 (pair price in USDT; USDTDAI = USDT in DAI):")
    bad = {}
    for s, rows in D.items():
        dips = [r for r in rows if r[3] < 0.99 and r[5] > 0]
        if s == "USTUSDT":
            dips = [r for r in rows if r[3] < 0.99]
        if dips:
            print(f"  {s:10s} {len(dips):4d} days, lowest {min(r[3] for r in dips):.4f} on "
                  f"{time.strftime('%Y-%m-%d', time.gmtime(min(dips, key=lambda r: r[3])[0]))}, first "
                  f"{time.strftime('%Y-%m-%d', time.gmtime(dips[0][0]))}")
            bad[s] = sorted(set(time.strftime('%Y-%m', time.gmtime(r[0])) for r in dips))
    # hourly rule: buy $100 when an hourly close is under X, at next hour's open + 0.1c slip, fee 0.10 each way;
    # sell at first hourly close >= 0.998, else hold to the end of data (marked at last close)
    print("\nRule: buy $100 at the next hour's open after an hourly close under the bar; sell at the first hourly close "
          "at $0.998+ (taker fee 0.10 each way). One bet per coin per dip (rearm after recovery).")
    H = {}
    for s, mlist in bad.items():
        allm = set()
        for ym in mlist:
            y, mo = map(int, ym.split("-"))
            for d in range(0, 4):
                mm = mo + d; yy = y + (mm - 1) // 12; mm = (mm - 1) % 12 + 1
                if f"{yy}-{mm:02d}" <= "2026-10":
                    allm.add(f"{yy}-{mm:02d}")
        rows = []
        with ThreadPoolExecutor(8) as ex:
            for r in ex.map(lambda ym: kl(s, "1h", ym) or [], sorted(allm)):
                rows += r
        H[s] = sorted(rows)
    bets_all = {}
    for bar in (0.995, 0.99, 0.98, 0.97):
        tot = []
        for s, rows in H.items():
            armed = True; i = 0
            while i < len(rows) - 1:
                if armed and rows[i][4] < bar and rows[i][5] > 0:
                    buy = rows[i + 1][1] + 0.001
                    j = i + 1
                    while j < len(rows) and rows[j][4] < 0.998:
                        j += 1
                    sell = rows[j][4] if j < len(rows) else rows[-1][4]
                    days = ((rows[j][0] if j < len(rows) else rows[-1][0]) - rows[i + 1][0]) / 86400
                    ret = 100 * (sell * 0.999) / (buy * 1.001) - 100
                    tot.append((s, time.strftime('%Y-%m-%d %H:00', time.gmtime(rows[i + 1][0])), round(buy, 4),
                                round(sell, 4), round(days, 1), round(ret, 2)))
                    armed = False; i = j
                elif rows[i][4] >= 0.998:
                    armed = True
                i += 1
        bets_all[bar] = tot
        win = sum(1 for t in tot if t[5] > 0)
        print(f"\n bar ${bar}: {len(tot)} bets, {win} won, total ${sum(t[5] for t in tot):.2f} on $100 each, "
              f"without UST/USTC ${sum(t[5] for t in tot if not t[0].startswith('UST')):.2f}")
        for t in tot:
            print("   ", t)
    json.dump({str(k): v for k, v in bets_all.items()}, open(f"{DIR}/depeg_bets.json", "w"))
    try:
        sys.path.insert(0, ".")
        import exam
        b = [{"ev": t[0] + t[1][:7], "t": time.mktime(time.strptime(t[1], "%Y-%m-%d %H:00")), "cost": 100.0, "pay": 100.0 + t[5], "sh": 100.0}
             for t in bets_all[0.99] if not t[0].startswith("UST")]
        if b:
            exam.score(b, "crossx stablecoin dip buy (<$0.99, Binance hourly, no UST)", tries=4)
    except Exception as e:
        print("exam skipped:", e)
    print("=== DONE ===")


def hosts():
    for u in ["https://api.kraken.com/0/public/Time", "https://www.bitstamp.net/api/v2/ticker/btceur/",
              "https://api.exchange.coinbase.com/products/BTC-EUR/ticker", "https://api.bitvavo.com/v2/time",
              "https://www.okx.com/api/v5/public/time", "https://data-api.binance.vision/api/v3/time",
              "https://api-pub.bitfinex.com/v2/platform/status", "https://api.firi.com/v2/markets",
              "https://api.bitpanda.com/v1/ticker", "https://api.onetrading.com/fast/v1/time",
              "https://api.frankfurter.app/latest?from=EUR&to=SEK", "https://api.gemini.com/v1/pubticker/btceur",
              "https://api.kucoin.com/api/v1/timestamp", "https://api.gateio.ws/api/v4/spot/time",
              "https://api.mexc.com/api/v3/time", "https://www.safello.com/", "https://btcx.se/"]:
        t = time.time()
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read(150)
            print(f"OK  {int((time.time()-t)*1000):5d} ms {u} {body[:100]!r}")
        except Exception as e:
            print(f"ERR {int((time.time()-t)*1000):5d} ms {u} {str(e)[:100]}")
    # bitpanda SEK vs EUR implied rate
    try:
        tk = get("https://api.bitpanda.com/v1/ticker"); fx = fx_sek()
        for c in ("BTC", "ETH", "USDC", "USDT"):
            if c in tk:
                print("bitpanda", c, "EUR", tk[c].get("EUR"), "SEK", tk[c].get("SEK"), "implied EURSEK",
                      round(float(tk[c]["SEK"]) / float(tk[c]["EUR"]), 4), "ECB", fx and fx.get("SEK"))
    except Exception as e:
        print("bitpanda ticker", e)
    print("=== DONE ===")


if __name__ == "__main__":
    a = sys.argv[1:] or ["hosts"]
    if a[0] == "hosts":
        hosts()
    elif a[0] == "sample":
        sample(int(a[1]) if len(a) > 1 else 60, int(a[2]) if len(a) > 2 else 15)
    elif a[0] == "report":
        report()
    elif a[0] == "depeg":
        depeg()
    elif a[0] == "all":
        hosts(); depeg(); sample(int(a[1]) if len(a) > 1 else 60, int(a[2]) if len(a) > 2 else 15)
