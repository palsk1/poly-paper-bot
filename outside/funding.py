"""Crypto perpetual futures funding rates as a small-bank edge (outside-venue research, paper only).

Commands (probe input out_funding_<cmd>_<args>):
  scan            one call to every source, prints what comes back
  fetch [months]  Binance dumps (funding all perps, 1h perp + spot candles for a chosen set), Hyperliquid funding
                  + 1h candles (top coins), OKX funding (last ~3 months), Kraken Futures funding, dYdX funding
  report          carry / cross-venue / first-half-second-half tests, backward look
Data: bt_cache/out_funding/ (shared price store). Reads public data only. No keys, no orders.
"""
import sys, os, re, json, gzip, io, csv, time, zipfile, math, statistics, calendar, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

D = "bt_cache/out_funding"
UA = {"User-Agent": "Mozilla/5.0 (research script)"}
BV = "https://data.binance.vision/data"
HL = "https://api.hyperliquid.xyz/info"
H = 3600000


def get(url, data=None, tries=4, timeout=30, raw=False):
    for i in range(tries):
        try:
            h = dict(UA)
            body = None
            if data is not None:
                h["Content-Type"] = "application/json"
                body = json.dumps(data).encode()
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h), timeout=timeout) as r:
                b = r.read()
                return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (404, 403, 451, 400):
                return None
            time.sleep(2 + 4 * i)
        except Exception:
            time.sleep(2 + 4 * i)
    return None


def save(name, obj):
    os.makedirs(D, exist_ok=True)
    with gzip.open(f"{D}/{name}.json.gz", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))


def load(name, default=None):
    p = f"{D}/{name}.json.gz"
    if not os.path.exists(p):
        return default
    with gzip.open(p, "rt") as f:
        return json.load(f)


def iso_ms(s):
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")) * 1000


def months(n):
    """last n full months as 'YYYY-MM' (Binance monthly dumps), oldest first."""
    t = time.gmtime()
    y, m = t.tm_year, t.tm_mon
    out = []
    for _ in range(n):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        out.append(f"{y}-{m:02d}")
    return out[::-1]


def bv_csv(path):
    b = get(f"{BV}/{path}", raw=True, tries=3)
    if not b:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        txt = z.read(z.namelist()[0]).decode()
    except Exception:
        return None
    rows = list(csv.reader(io.StringIO(txt)))
    if rows and rows[0] and not rows[0][0][:1].isdigit():
        rows = rows[1:]
    return rows


# ---------------------------------------------------------------- scan
def scan():
    now = int(time.time() * 1000)
    tests = [
        ("HL meta", lambda: str(get(HL, {"type": "metaAndAssetCtxs"}))[:300]),
        ("HL funding", lambda: str(get(HL, {"type": "fundingHistory", "coin": "BTC", "startTime": now - 86400000}))[:300]),
        ("HL candles", lambda: str(get(HL, {"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "startTime": now - 7200000, "endTime": now}}))[:300]),
        ("HL spotMeta", lambda: str(get(HL, {"type": "spotMeta"}))[:200]),
        ("OKX funding", lambda: str(get("https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=3"))[:300]),
        ("OKX instruments", lambda: str(get("https://www.okx.com/api/v5/public/instruments?instType=SWAP"))[:200]),
        ("Kraken fut funding", lambda: str(get("https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=PF_XBTUSD"))[:300]),
        ("Kraken fut tickers", lambda: str(get("https://futures.kraken.com/derivatives/api/v3/tickers"))[:200]),
        ("dYdX funding", lambda: str(get("https://indexer.dydx.trade/v4/historicalFunding/BTC-USD?limit=3"))[:300]),
        ("BV funding", lambda: str((bv_csv("futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2026-10.zip") or [])[:3])),
        ("BV fut 1h", lambda: str((bv_csv("futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-10.zip") or [])[:2])),
        ("BV spot 1h", lambda: str((bv_csv("spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-10.zip") or [])[:2])),
        ("S3 list", lambda: str(get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/fundingRate/", raw=True))[:300]),
        ("Bybit (expect 403)", lambda: str(get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=2"))[:200]),
        ("Gate funding", lambda: str(get("https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract=BTC_USDT&limit=2"))[:200]),
        ("Deribit funding", lambda: str(get(f"https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL&start_timestamp={now-7200000}&end_timestamp={now}"))[:200]),
    ]
    for name, f in tests:
        try:
            print(f"{name}: {f()}")
        except Exception as e:
            print(f"{name}: ERR {e}")


# ---------------------------------------------------------------- fetch
def bn_symbols():
    """every USDT-M perp that has a funding folder on data.binance.vision (incl. delisted)."""
    out, marker = [], ""
    base = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/fundingRate/"
    for _ in range(50):
        b = get(base + (f"&marker={marker}" if marker else ""), raw=True)
        if not b:
            break
        t = b.decode()
        found = re.findall(r"<Prefix>data/futures/um/monthly/fundingRate/([A-Z0-9_]+)/</Prefix>", t)
        out += found
        if "<IsTruncated>true" in t and found:
            marker = f"data/futures/um/monthly/fundingRate/{found[-1]}/"
        else:
            break
    return sorted(set(out))


def bn_funding(sym, ms):
    rows = []
    for m in ms:
        r = bv_csv(f"futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{m}.zip")
        if r:
            rows += [[int(x[0]), float(x[2]), int(x[1])] for x in r if len(x) >= 3]
    return sorted(rows)


def bn_klines(kind, sym, ms):
    rows = []
    pre = "futures/um" if kind == "fut" else "spot"
    for m in ms:
        r = bv_csv(f"{pre}/monthly/klines/{sym}/1h/{sym}-1h-{m}.zip")
        if r:
            for x in r:
                t = int(x[0])
                if t > 1e14:  # spot dumps in microseconds since 2025
                    t //= 1000
                rows.append([t, float(x[2]), float(x[3]), float(x[4]), round(float(x[7]))])  # high low close $volume
    return sorted(rows)


def hl_funding(coin, start):
    out, t = [], start
    now = int(time.time() * 1000)
    while t < now:
        r = get(HL, {"type": "fundingHistory", "coin": coin, "startTime": t})
        time.sleep(2.0)
        if not r:
            break
        out += [[int(x["time"]), float(x["fundingRate"]), float(x["premium"])] for x in r]
        nt = int(r[-1]["time"]) + 1
        if nt <= t or len(r) < 2:
            break
        t = nt
    return out


def hl_candles(coin, start):
    out, t = [], start
    now = int(time.time() * 1000)
    while t < now:
        r = get(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": t, "endTime": now}})
        time.sleep(4)
        if not r:
            break
        out += [[int(x["t"]), float(x["h"]), float(x["l"]), float(x["c"]), round(float(x["v"]) * float(x["c"]))] for x in r]
        nt = int(r[-1]["t"]) + 1
        if nt <= t or len(r) < 2:
            break
        t = nt
    d = {x[0]: x for x in out}
    return [d[k] for k in sorted(d)]


def okx_funding(coin):
    out, after = [], ""
    for _ in range(20):
        r = get(f"https://www.okx.com/api/v5/public/funding-rate-history?instId={coin}-USDT-SWAP&limit=400" + (f"&after={after}" if after else ""))
        time.sleep(0.25)
        if not r or not r.get("data"):
            break
        data = r["data"]
        out += [(int(x["fundingTime"]), float(x.get("realizedRate") or x["fundingRate"])) for x in data]
        after = data[-1]["fundingTime"]
        if len(data) < 2:
            break
    return sorted(set(out))


def kraken_funding(coin):
    k = {"BTC": "XBT"}.get(coin, coin)
    r = get(f"https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=PF_{k}USD")
    if not r or not r.get("rates"):
        return []
    out = []
    for x in r["rates"]:
        try:
            out.append([iso_ms(x["timestamp"]), float(x["relativeFundingRate"])])
        except Exception:
            pass
    return out


def dydx_funding(coin, start):
    out, before = [], None
    for _ in range(120):
        u = f"https://indexer.dydx.trade/v4/historicalFunding/{coin}-USD?limit=100"
        if before:
            u += f"&effectiveBeforeOrAt={before}"
        r = get(u, tries=2)
        if not r or not r.get("historicalFunding"):
            break
        h = r["historicalFunding"]
        out += [(iso_ms(x["effectiveAt"]), float(x["rate"])) for x in h]
        if out[-1][0] < start or len(h) < 100:
            break
        before = h[-1]["effectiveAt"]
        time.sleep(0.2)
    return sorted(set(out))


def fetch(nmonths=12, nhl=40):
    nmonths, nhl = int(nmonths), int(nhl)
    ms = months(nmonths)
    start = calendar.timegm(time.strptime(ms[0] + "-01", "%Y-%m-%d")) * 1000
    print("months", ms[0], "..", ms[-1], flush=True)
    meta = get(HL, {"type": "metaAndAssetCtxs"})
    uni = load("hl_meta", [])
    if meta:
        uni = []
        for a, c in zip(meta[0]["universe"], meta[1]):
            uni.append({"coin": a["name"], "delisted": bool(a.get("isDelisted")), "maxlev": a.get("maxLeverage"),
                        "oi_usd": float(c.get("openInterest") or 0) * float(c.get("markPx") or 0),
                        "vol": float(c.get("dayNtlVlm") or 0)})
        save("hl_meta", uni)
    print("HL coins", len(uni), "delisted", sum(u["delisted"] for u in uni), flush=True)
    syms = load("bn_syms") or bn_symbols()
    save("bn_syms", syms)
    syms = [s for s in syms if s.endswith("USDT")]
    print("Binance USDT perps (incl. delisted)", len(syms), flush=True)
    have = load("bn_funding", {})
    todo = [s for s in syms if s not in have]
    with ThreadPoolExecutor(24) as ex:
        for s, rows in zip(todo, ex.map(lambda s: bn_funding(s, ms), todo)):
            have[s] = rows
    save("bn_funding", have)
    print("Binance funding symbols", sum(1 for v in have.values() if v), "rows", sum(len(v) for v in have.values()), flush=True)
    top_hl = [u["coin"] for u in sorted(uni, key=lambda u: -u["oi_usd"]) if not u["delisted"]][:nhl]
    avg = {}
    for s, rows in have.items():
        if len(rows) >= 90:
            avg[s] = sum(r[1] for r in rows) / ((rows[-1][0] - rows[0][0]) / 86400000 + 1)
    hi = [s for s, _ in sorted(avg.items(), key=lambda kv: -abs(kv[1]))][:60]
    kset = sorted(set([c + "USDT" for c in top_hl if have.get(c + "USDT")] + hi))
    save("kset", kset)
    print("kline set", len(kset), flush=True)
    kl = load("bn_kl", {})
    todo = [s for s in kset if s not in kl]

    def both(s):
        return {"fut": bn_klines("fut", s, ms), "spot": bn_klines("spot", s, ms)}
    with ThreadPoolExecutor(16) as ex:
        for s, r in zip(todo, ex.map(both, todo)):
            kl[s] = r
    save("bn_kl", kl)
    print("Binance klines", len(kl), "with spot", sum(1 for v in kl.values() if v["spot"]), flush=True)
    for name, fn in (("okx", okx_funding), ("kraken", kraken_funding), ("dydx", lambda c: dydx_funding(c, start))):
        cur = load(name, {})
        for c in top_hl:
            if c not in cur:
                try:
                    cur[c] = fn(c)
                except Exception:
                    cur[c] = []
        save(name, cur)
        print(name, "coins with data", sum(1 for v in cur.values() if v), "rows", sum(len(v) for v in cur.values()), flush=True)
    hf = load("hl_funding", {})
    for c in top_hl:
        if not hf.get(c):
            hf[c] = hl_funding(c, start)
            save("hl_funding", hf)
    print("HL funding coins", sum(1 for v in hf.values() if v), "rows", sum(len(v) for v in hf.values()), flush=True)
    hc = load("hl_candles", {})
    for c in top_hl[:25]:
        if not hc.get(c):
            hc[c] = hl_candles(c, start)
            save("hl_candles", hc)
    print("HL candle coins", sum(1 for v in hc.values() if v), flush=True)


# ---------------------------------------------------------------- report
DAY = 86400000
BANK = 300.0
# taker fees per side (fraction of notional) and a small slippage guess per side
FEE = {"bn_spot": 0.001, "bn_perp": 0.0005, "hl_perp": 0.00045, "hl_spot": 0.0007, "kr_perp": 0.0005,
       "kr_spot": 0.0040, "okx_perp": 0.0005}
MAJORS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


def daily(rows, tcol=0, rcol=1):
    """{day index: summed funding rate paid to a SHORT that day}."""
    out = {}
    for r in rows:
        d = int(r[tcol] // DAY)
        out[d] = out.get(d, 0.0) + r[rcol]
    return out


def closes(rows):
    return {int(r[0]): r for r in rows}


def dstr(d):
    return time.strftime("%Y-%m-%d", time.gmtime(d * 86400))


class Coin:
    """one coin on one carry setup: daily funding, prices at each day start, daily high of the perp."""

    def __init__(self, name, fund, perp, spot):
        self.name = name
        self.f = fund                      # {day: rate}
        self.pf, self.ps, self.hi, self.lo = {}, {}, {}, {}
        pc, sc = closes(perp), closes(spot)
        for t, r in pc.items():
            if (t + H) % DAY == 0:         # bar that closes exactly at a day start
                d = (t + H) // DAY
                if t in sc:
                    self.pf[d] = r[3]
                    self.ps[d] = sc[t][3]
            d0 = t // DAY
            self.hi[d0] = max(self.hi.get(d0, 0), r[1])
            self.lo[d0] = min(self.lo.get(d0, 1e18), r[2])
        self.vol = {}
        for t, r in pc.items():
            d0 = t // DAY
            self.vol[d0] = self.vol.get(d0, 0) + r[4]

    def ok(self, d):
        return d in self.pf and d in self.f

    def trail(self, d, L):
        v = [self.f.get(x) for x in range(d - L, d)]
        if any(x is None for x in v):
            return None
        return sum(v) / L


def episode(c, d0, d1, N, fee_side, slip, lev, rb=0.25):
    """short perp + long spot of notional N from day d0 start to day d1 start. Returns (pnl, info)."""
    fund = sum(c.f.get(d, 0.0) for d in range(d0, d1)) * N
    p0f, p0s, p1f, p1s = c.pf[d0], c.ps[d0], c.pf[d1], c.ps[d1]
    gap = N * ((p1s / p0s) - (p1f / p0f))
    fees = N * 2 * (fee_side + slip)
    # liquidation / rebalance check on the perp short (margin N/lev, rebalanced back to N/lev at day starts
    # whenever the price moved more than rb since the last rebalance)
    ref, reb, liq = p0f, 0.0, False
    for d in range(d0, d1):
        h = c.hi.get(d, ref)
        if h / ref - 1 > 1.0 / lev - 0.02:
            liq = True
            break
        p = c.pf.get(d + 1, ref)
        if abs(p / ref - 1) > rb:
            reb += N * abs(p / ref - 1) * (fee_side + slip)  # move the gain from one side to the other
            ref = p
    if liq:
        fees += N * 0.01            # liquidation penalty guess, then both legs closed
    return fund + gap - fees - reb, {"fund": fund, "gap": gap, "fees": fees, "reb": reb, "liq": liq}


def run_rule(coins, days, L, E, X, lev, fee_side, slip, min_hold=1):
    """one position at a time with the whole $300: each day start, if holding and the coin's average daily
    funding over the last L days is below X, close; if flat, open the coin with the highest L-day average above E."""
    N = BANK * lev / (1 + lev)
    hold, d_in, eps = None, None, []
    for d in days:
        if hold is not None:
            c = coins[hold]
            tr = c.trail(d, L)
            last = d == days[-1]
            if (not c.ok(d)) or last or (d - d_in >= min_hold and (tr is None or tr < X)):
                d_out = d if c.ok(d) else max(x for x in c.pf if x < d)
                if d_out > d_in:
                    pnl, info = episode(c, d_in, d_out, N, fee_side, slip, lev)
                    eps.append({"coin": hold, "d0": d_in, "d1": d_out, "pnl": pnl, **info})
                hold = None
        if hold is None and d != days[-1]:
            best, bv = None, E
            for k, c in coins.items():
                if c.ok(d):
                    tr = c.trail(d, L)
                    if tr is not None and tr > bv:
                        best, bv = k, tr
            if best is not None:
                hold, d_in = best, d
    return eps


def summ(eps, ndays):
    p = sum(e["pnl"] for e in eps)
    return {"n": len(eps), "pnl": p, "per_day": p / max(1, ndays), "per100_day": p / max(1, ndays) / BANK * 100,
            "liq": sum(e["liq"] for e in eps), "fund": sum(e["fund"] for e in eps),
            "fees": sum(e["fees"] + e["reb"] for e in eps), "gap": sum(e["gap"] for e in eps),
            "held": sum(e["d1"] - e["d0"] for e in eps)}


def fmt(s):
    return (f"{s['n']:4d} trades, held {s['held']:4d} days, P&L ${s['pnl']:8.2f} = ${s['per_day']:.3f}/day at $300 "
            f"(${s['per100_day']:.4f} per $100 a day); funding ${s['fund']:.2f}, price gap ${s['gap']:.2f}, "
            f"fees ${s['fees']:.2f}, liquidations {s['liq']}")


def kraken_candles(coin, start):
    k = {"BTC": "XBT"}.get(coin, coin)
    out, t = [], start // 1000
    now = int(time.time())
    for _ in range(40):
        r = get(f"https://futures.kraken.com/api/charts/v1/trade/PF_{k}USD/1h?from={t}&to={now}")
        if not r or not r.get("candles"):
            break
        cs = r["candles"]
        out += [[int(x["time"]), float(x["high"]), float(x["low"]), float(x["close"]), round(float(x.get("volume") or 0) * float(x["close"]))] for x in cs]
        nt = int(cs[-1]["time"]) // 1000 + 3600
        if nt <= t or not r.get("more_candles"):
            break
        t = nt
        time.sleep(0.3)
    d = {x[0]: x for x in out}
    return [d[k_] for k_ in sorted(d)]


def fetch2(nmonths=12):
    """Kraken Futures 1h candles for the coins that have Kraken funding."""
    ms = months(int(nmonths))
    start = calendar.timegm(time.strptime(ms[0] + "-01", "%Y-%m-%d")) * 1000
    kr = load("kraken", {})
    kc = load("kraken_candles", {})
    for c, v in kr.items():
        if v and not kc.get(c):
            kc[c] = kraken_candles(c, start)
            if c == "BTC":
                print("BTC kraken candles", len(kc[c]), kc[c][:2])
    save("kraken_candles", kc)
    print("Kraken candle coins", sum(1 for v in kc.values() if v), "rows", sum(len(v) for v in kc.values()))


def fetch3():
    """Kraken SPOT daily candles (USD pairs) for the coins with Kraken Futures funding: does the spot exist, and how
    far is the perp from it at each day's end."""
    kr = load("kraken", {})
    ap = get("https://api.kraken.com/0/public/AssetPairs") or {}
    pairs = {}
    for name, p in (ap.get("result") or {}).items():
        alt = p.get("altname", "")
        if alt.endswith("USD") and p.get("quote") in ("ZUSD", "USD"):
            pairs[alt[:-3]] = name
    alias = {"BTC": "XBT", "DOGE": "XDG"}
    out = {}
    for coin, v in kr.items():
        if not v:
            continue
        pn = pairs.get(alias.get(coin, coin)) or pairs.get(coin)
        if not pn:
            out[coin] = None
            continue
        r = get(f"https://api.kraken.com/0/public/OHLC?pair={pn}&interval=1440")
        time.sleep(1.2)
        rows = []
        for k_, val in ((r or {}).get("result") or {}).items():
            if k_ != "last":
                rows = [[int(x[0]) * 1000, float(x[2]), float(x[3]), float(x[4]), float(x[6]) * float(x[4])] for x in val]
        out[coin] = rows
    save("kraken_spot", out)
    print("Kraken spot: coins with a USD spot pair", sum(1 for v in out.values() if v), "missing",
          sorted(k for k, v in out.items() if not v))


def report(*a):
    bf = load("bn_funding", {})
    kl = load("bn_kl", {})
    hf = load("hl_funding", {})
    hc = load("hl_candles", {})
    meta = {u["coin"]: u for u in load("hl_meta", [])}
    okx, kr, dy = load("okx", {}), load("kraken", {}), load("dydx", {})
    print(f"data: Binance funding {len(bf)} symbols, klines {len(kl)}, HL funding {len(hf)}, HL candles {len(hc)}, "
          f"OKX {sum(1 for v in okx.values() if v)}, Kraken {sum(1 for v in kr.values() if v)}, dYdX {sum(1 for v in dy.values() if v)}")

    # ---- 1. how much funding does a short collect, per venue, on the big coins
    print("\n== 1. Funding paid to a short, dollars per $100 of short per day (avg), share of days negative, sign flips ==")
    rows = []
    for coin in ["BTC", "ETH", "SOL", "XRP", "DOGE", "HYPE", "BNB", "SUI", "LINK", "AVAX"]:
        line = [coin]
        for nm, src in (("BN", daily(bf.get(coin + "USDT", []))), ("HL", daily(hf.get(coin, []))),
                        ("OKX", daily(okx.get(coin, []))), ("KR", daily(kr.get(coin, []))), ("DYDX", daily(dy.get(coin, [])))):
            ds = sorted(src)[1:-1]
            if len(ds) < 20:
                line.append(f"{nm} -")
                continue
            v = [src[d] for d in ds]
            neg = sum(1 for x in v if x < 0) / len(v)
            flips = sum(1 for i in range(1, len(v)) if (v[i] < 0) != (v[i - 1] < 0))
            line.append(f"{nm} ${statistics.mean(v)*100:.4f} ({len(v)}d, neg {neg*100:.0f}/100 days, {flips} flips)")
        print("  " + " | ".join(line))

    # common window: OKX has ~3 months, compare all venues on the same days
    print("\n== 1b. Same days only (OKX window): $ per $100 short per day ==")
    for coin in ["BTC", "ETH", "SOL", "XRP", "DOGE", "HYPE"]:
        srcs = {"BN": daily(bf.get(coin + "USDT", [])), "HL": daily(hf.get(coin, [])), "OKX": daily(okx.get(coin, [])),
                "KR": daily(kr.get(coin, [])), "DYDX": daily(dy.get(coin, []))}
        common = None
        for s in srcs.values():
            if len(s) > 20:
                common = set(s) if common is None else common & set(s)
        if not common:
            continue
        common = sorted(common)[1:-1]
        print(f"  {coin} {len(common)} days: " + ", ".join(f"{k} ${statistics.mean(s[d] for d in common)*100:.4f}"
                                                         for k, s in srcs.items() if len(s) > 20))

    # ---- 2. delta-neutral carry on Binance (spot long + perp short), always on, per coin
    coins = {}
    for s, v in kl.items():
        if v.get("spot") and v.get("fut") and bf.get(s):
            coins[s] = Coin(s, daily(bf[s]), v["fut"], v["spot"])
    alld = sorted(set(d for c in coins.values() for d in c.pf))
    if not alld:
        print("no kline data")
        return
    d_first, d_last = alld[0], alld[-1]
    mid = d_first + (d_last - d_first) // 2
    print(f"\ncarry days {dstr(d_first)} .. {dstr(d_last)}, split at {dstr(mid)}; {len(coins)} coins with spot+perp")
    fee_bn = FEE["bn_spot"] / 2 + FEE["bn_perp"] / 2  # per side averaged over the two legs (both legs trade)
    fee_bn = FEE["bn_spot"] + FEE["bn_perp"]          # per side: spot + perp both trade once on entry, once on exit
    print("\n== 2. Hold spot + short perp on Binance the whole time, $300 at 1x (=$150 each side) ==")
    res = []
    for s, c in coins.items():
        ds = sorted(c.pf)
        if len(ds) < 60:
            continue
        a, b = ds[0], ds[-1]
        pnl, info = episode(c, a, b, BANK / 2, fee_bn, 0.0002, 1)
        delisted = b < d_last - 3
        px = [c.pf[d] for d in ds]
        maxup = max(c.hi.get(d, 0) / c.pf[ds[0]] for d in ds) - 1
        dd = min(px[i] / max(px[:i + 1]) for i in range(len(px))) - 1
        res.append((pnl / (b - a), s, b - a, pnl, info, delisted, maxup, dd))
    res.sort(reverse=True)
    for r in [x for x in res if x[1] in MAJORS + ["XRPUSDT", "DOGEUSDT", "BNBUSDT"]]:
        print(f"  {r[1]:12s} {r[2]:3d}d P&L ${r[3]:7.2f} (${r[0]:.3f}/day) funding ${r[4]['fund']:.2f} gap ${r[4]['gap']:.2f} "
              f"fees ${r[4]['fees']+r[4]['reb']:.2f} liq {r[4]['liq']}")
    print(f"  all {len(res)} coins: median ${statistics.median(x[0] for x in res):.3f}/day; "
          f"{sum(1 for x in res if x[3] > 0)} ahead, {sum(1 for x in res if x[3] <= 0)} behind, liquidated at 1x: {sum(1 for x in res if x[4]['liq'])}")

    # ---- 5. backward look: which coins paid most, and what happened to them
    print("\n== 5. Backward look: top 15 coins by average funding (Binance, all perps with 90+ days) ==")
    avg = []
    for s, rows_ in bf.items():
        dd_ = daily(rows_)
        if len(dd_) >= 90:
            ds = sorted(dd_)
            avg.append((statistics.mean(dd_[d] for d in ds), s, len(ds), ds[-1] < d_last - 3,
                        sum(1 for d in ds if dd_[d] < 0) / len(ds)))
    avg.sort(reverse=True)
    byname = {r[1]: r for r in res}
    for a_, s, n, dl, neg in avg[:15]:
        r = byname.get(s)
        extra = (f"carry P&L at 1x ${r[3]:.2f} over {r[2]}d, biggest rise {r[6]*100:.0f}/100, biggest fall {r[7]*100:.0f}/100, liq {r[4]['liq']}"
                 if r else "no Binance spot: carry impossible there")
        print(f"  {s:14s} ${a_*100:.3f} per $100/day over {n}d, neg {neg*100:.0f}/100 days, delisted {dl}; {extra}")
    print(f"  perps with 90+ days: {len(avg)}; delisted before the end: {sum(1 for x in avg if x[3])}; "
          f"of the top 30 by funding: {sum(1 for x in avg[:30] if x[3])} delisted, "
          f"{sum(1 for x in avg[:30] if x[1] not in byname)} without spot klines here")
    top30 = [byname[x[1]] for x in avg[:30] if x[1] in byname]
    if top30:
        print(f"  top-30 coins that have spot: {len(top30)}, carry at 1x ahead {sum(1 for r in top30 if r[3] > 0)}, "
              f"liquidated {sum(1 for r in top30 if r[4]['liq'])}, total P&L ${sum(r[3] for r in top30):.2f} "
              f"(each with $300)")

    # ---- 3. rule picked on the first half, checked on the second half
    print("\n== 3. Rotation rule (one coin at a time, whole $300), picked on the first half ==")
    liquid = sorted(coins, key=lambda s: -sum(coins[s].vol.values()))
    sets = {"majors3": [s for s in MAJORS if s in coins], "top10": liquid[:10], "top30": liquid[:30], "all": liquid}
    first = [d for d in alld if d <= mid]
    second = [d for d in alld if d >= mid]
    grid = []
    tries = 0
    for sn, ss in sets.items():
        sub = {k: coins[k] for k in ss}
        for L in (1, 3, 7):
            for E in (0.0002, 0.0004, 0.0008, 0.0015, 0.003):
                for X in (0.0, E / 2):
                    for lev in (1, 2):
                        tries += 1
                        e1 = run_rule(sub, first, L, E, X, lev, fee_bn, 0.0005 if sn in ("top30", "all") else 0.0002, min_hold=1)
                        s1 = summ(e1, len(first))
                        grid.append((s1["per_day"], sn, L, E, X, lev, s1))
    grid.sort(key=lambda g: (g[6]["n"] < 3, -g[0]))
    for g in grid[:8]:
        print(f"  first half {g[1]:8s} L{g[2]} enter>{g[3]*100:.3f} exit<{g[4]*100:.3f} lev{g[5]}: {fmt(g[6])}")
    best = grid[0]
    sn, L, E, X, lev = best[1:6]
    sub = {k: coins[k] for k in sets[sn]}
    e2 = run_rule(sub, second, L, E, X, lev, fee_bn, 0.0005 if sn in ("top30", "all") else 0.0002)
    s2 = summ(e2, len(second))
    print(f"  CHOSEN ({tries} tries) {sn} L{L} E{E} X{X} lev{lev}")
    print(f"  second half (unseen): {fmt(s2)}")
    for e in e2[:40]:
        print(f"    {e['coin']:12s} {dstr(e['d0'])}..{dstr(e['d1'])} P&L ${e['pnl']:.2f} fund ${e['fund']:.2f} gap ${e['gap']:.2f} liq {e['liq']}")
    # simple fixed baselines on both halves
    for nm, ss, L_, E_, X_ in (("BTC always", ["BTCUSDT"], 1, -1, -9), ("ETH always", ["ETHUSDT"], 1, -1, -9),
                               ("majors3, 3-day avg > 0", sets["majors3"], 3, 0.0, 0.0)):
        sub_ = {k: coins[k] for k in ss}
        for half, dd_ in (("1st", first), ("2nd", second)):
            print(f"  baseline {nm:24s} {half}: {fmt(summ(run_rule(sub_, dd_, L_, E_, X_, 1, fee_bn, 0.0002), len(dd_)))}")
    try:
        sys.path.insert(0, ".")
        import exam
        bets = [{"cost": BANK, "pay": BANK + e["pnl"], "t": e["d0"] * 86400, "ev": f"{e['coin']}-{e['d0']}"} for e in e2]
        exam.score(bets, "funding carry rotation (Binance spot+perp), 2nd half", tries=tries, src="outside/funding.py",
                   note="picked on first half", log=False)
    except Exception as ex:
        print("exam skipped:", ex)

    # ---- 2b. HL short + Binance spot (HL pays the 11-a-year interest part to shorts)
    print("\n== 2b. Short on Hyperliquid + spot on Binance, always on, $300 at 1x, from the first HL candle ==")
    for coin in list(hc)[:25]:
        s = coin + "USDT"
        if not hc.get(coin) or s not in kl or not kl[s].get("spot") or not hf.get(coin):
            continue
        c = Coin(coin, daily(hf[coin]), hc[coin], kl[s]["spot"])
        ds = sorted(c.pf)
        if len(ds) < 30:
            continue
        pnl, info = episode(c, ds[0], ds[-1], BANK / 2, FEE["hl_perp"] + FEE["bn_spot"], 0.0002, 1)
        print(f"  {coin:6s} {ds[-1]-ds[0]:3d}d P&L ${pnl:7.2f} (${pnl/(ds[-1]-ds[0]):.3f}/day) funding ${info['fund']:.2f} gap ${info['gap']:.2f} liq {info['liq']}")

    # ---- price-move risk for modest leverage
    print("\n== Price moves that would hit a leveraged leg (Binance perp, day highs/lows) ==")
    for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT"]:
        if s not in coins:
            continue
        c = coins[s]
        ds = sorted(c.pf)
        up1 = max(c.hi[d] / c.pf[d] - 1 for d in ds if d in c.hi)
        dn1 = max(1 - c.lo[d] / c.pf[d] for d in ds if d in c.lo)
        up7 = max(max(c.hi.get(x, 0) for x in range(d, d + 7)) / c.pf[d] - 1 for d in ds[:-7])
        print(f"  {s}: worst 1-day rise {up1*100:.0f}/100, worst 1-day fall {dn1*100:.0f}/100, worst 7-day rise {up7*100:.0f}/100")

    # ---- 2c. the Sweden-legal version: Kraken Pro spot + Kraken Futures short (funding from Kraken itself)
    print("\n== 2c. Kraken spot + Kraken Futures short, always on (Kraken funding; price gap ignored) ==")
    print("   $300 all in: buy $300 of the coin, use it as collateral, short $300 of the perp (one account)")
    kfee = FEE["kr_spot"] + FEE["kr_perp"]
    rows2 = []
    for coin, v in kr.items():
        dd_ = daily(v)
        ds = sorted(d for d in dd_ if d_first <= d < d_last)
        if len(ds) < 300:
            continue
        h1 = [dd_[d] for d in ds if d <= mid]
        h2 = [dd_[d] for d in ds if d > mid]
        f1, f2 = sum(h1) * BANK, sum(h2) * BANK
        rows2.append((f1 + f2 - BANK * 2 * kfee, coin, f1 - BANK * 2 * kfee, f2 - BANK * 2 * kfee, len(ds)))
    rows2.sort(reverse=True)
    for r in rows2[:8] + [x for x in rows2 if x[1] in ("BTC", "ETH")]:
        print(f"  {r[1]:6s} {r[4]}d: full year ${r[0]:.2f} (${r[0]/r[4]:.3f}/day); 1st half alone ${r[2]:.2f}, 2nd half alone ${r[3]:.2f}")
    if rows2:
        print(f"  {len(rows2)} coins: ahead over the year {sum(1 for r in rows2 if r[0] > 0)}, median ${statistics.median(r[0] for r in rows2):.2f}")
        # rule: pick the 3 best coins of the first half, hold them in the second half ($100 each)
        best3 = [r[1] for r in sorted(rows2, key=lambda r: -r[2])[:3]]
        p2 = sum(r[3] for r in rows2 if r[1] in best3) / 3
        print(f"  pick the 3 best of the 1st half ({', '.join(best3)}), $100 each, 2nd half: ${p2:.2f} on $300 "
              f"(${p2/max(1, d_last-mid):.3f}/day)")
        # rolling version: every 30 days pick the 3 coins with the best Kraken funding over the last 90 days,
        # $100 each; switching a coin costs Kraken spot + perp fees both ways plus a 0.3/100 price-gap guess per side
        kd = {coin: daily(v) for coin, v in kr.items() if v}
        t_ = d_first + 90
        held, tot, months_ = set(), 0.0, []
        while t_ + 30 <= d_last:
            sc = []
            for coin, dd_ in kd.items():
                w = [dd_.get(x) for x in range(t_ - 90, t_)]
                if sum(1 for x in w if x is not None) >= 80:
                    sc.append((sum(x for x in w if x is not None), coin))
            pick = set(c for _, c in sorted(sc, reverse=True)[:3])
            cost = len(pick - held) * 100 * 2 * (kfee + 0.003) / 2 + len(held - pick) * 100 * 2 * (kfee + 0.003) / 2
            earn = sum(sum(kd[c].get(x, 0.0) for x in range(t_, t_ + 30)) * 100 for c in pick)
            months_.append((dstr(t_), sorted(pick), earn - cost))
            tot += earn - cost
            held = pick
            t_ += 30
        tot -= len(held) * 100 * (kfee + 0.003)
        print(f"  rolling monthly top-3 by last 90 days (picked blind each month): ${tot:.2f} over {len(months_)} months "
              f"on $300 (${tot/max(1, 30*len(months_)):.3f}/day)")
        for m in months_:
            print(f"    {m[0]} {','.join(m[1]):24s} ${m[2]:.2f}")
        # price check: Kraken perp vs Binance spot at day starts, and the coin's own price path
        kcand = load("kraken_candles", {})
        for coin in best3 + ["BTC", "ETH"]:
            kp = {r[0]: r for r in kcand.get(coin, [])}
            sp = {r[0]: r for r in (kl.get(coin + "USDT") or {}).get("spot", [])}
            ds = [d for d in range(d_first, d_last) if (d * DAY - H) in kp]
            if not ds:
                print(f"  {coin}: no Kraken candles")
                continue
            px = [kp[d * DAY - H][3] for d in ds]
            g = [kp[d * DAY - H][3] / sp[d * DAY - H][3] - 1 for d in ds if (d * DAY - H) in sp]
            gs = (f"Kraken perp vs Binance spot: typical {statistics.median(abs(x) for x in g)*1e4:.0f} in 10,000, "
                  f"worst {max(abs(x) for x in g)*1e4:.0f} in 10,000" if g else "no Binance spot to compare")
            dv = statistics.median(kp[d * DAY - H][4] for d in ds[-30:])
            print(f"  {coin}: price {px[0]:.4g} -> {px[-1]:.4g} (low {min(px):.4g}, high {max(px):.4g}); {gs}; "
                  f"Kraken perp volume about ${dv*24:,.0f} a day lately")

    # ---- Swedish tax drag on a hedged pair: the winning leg is taxed 30, the losing leg only deducted at 70 of 100
    print("\n== Swedish tax drag on a hedged $150/$150 pair held a year (gain taxed 30/100, loss deducted 21/100) ==")
    for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
        if s in coins:
            c = coins[s]
            ds = sorted(c.pf)
            mv = abs(c.ps[ds[-1]] / c.ps[ds[0]] - 1) * BANK / 2
            print(f"  {s}: price moved {mv/(BANK/2)*100:.0f}/100 over the year -> one leg +${mv:.2f}, other -${mv:.2f}, "
                  f"extra tax about ${0.09*mv:.2f} (on top of 30/100 tax on the funding itself)")

    # ---- 4. cross-venue: short the perp where funding is higher, long where lower
    kc = load("kraken_candles", {})
    venues = {
        "HL": ({c: daily(v) for c, v in hf.items() if v}, {c: {r[0]: r for r in v} for c, v in hc.items() if v}, FEE["hl_perp"]),
        "BN": ({s[:-4]: daily(v) for s, v in bf.items() if v}, {s[:-4]: {r[0]: r for r in v["fut"]} for s, v in kl.items() if v.get("fut")}, FEE["bn_perp"]),
        "KR": ({c: daily(v) for c, v in kr.items() if v}, {c: {r[0]: r for r in v} for c, v in kc.items() if v}, FEE["kr_perp"]),
    }
    for va, vb in (("HL", "BN"), ("HL", "KR"), ("KR", "BN")):
        cross(va, vb, venues)


def cross(va, vb, venues):
    """A minus B: short the venue with the higher recent funding, long the other, $150 margin on each venue."""
    FA, PA, fa_fee = venues[va]
    FB, PB, fb_fee = venues[vb]
    print(f"\n== 4. Cross-venue perps {va} vs {vb}, $300 split $150 / $150 over the two venues ==")
    xs = []
    for coin in sorted(set(FA) & set(FB) & set(PA) & set(PB)):
        fh, fb, ph, pb = FA[coin], FB[coin], PA[coin], PB[coin]
        ds = sorted(d for d in fh if d in fb and (d * DAY - H) in ph and (d * DAY - H) in pb)
        if len(ds) < 30:
            continue
        xs.append((coin, fh, fb, ph, pb, ds))
        spread = [fh[d] - fb[d] for d in ds[1:-1]]
        gaps = [ph[d * DAY - H][3] / pb[d * DAY - H][3] - 1 for d in ds]
        print(f"  {coin:6s} {len(spread)}d {dstr(ds[0])}..: {va} minus {vb} funding avg ${statistics.mean(spread)*100:.4f} per $100/day, "
              f"typical size ${statistics.median(abs(x) for x in spread)*100:.4f}, {va} higher on {sum(1 for x in spread if x>0)} days; "
              f"price gap at day start: typical {statistics.median(abs(g) for g in gaps)*1e4:.1f} in 10,000, worst {max(abs(g) for g in gaps)*1e4:.0f}")
    if not xs:
        print("  no coins with both venues' data")
        return

    def xrun(days_, L, E, X, lev, static=False):
        N = BANK / 2 * lev
        eps = []
        for coin, fh, fb, ph, pb, ds in xs:
            dset = set(ds)
            hold = None
            for d in days_:
                if d not in dset:
                    continue
                tr = None
                if all((x in fh and x in fb) for x in range(d - L, d)):
                    tr = sum(fh[x] - fb[x] for x in range(d - L, d)) / L
                if hold:
                    sgn, d0 = hold
                    end = d == days_[-1] or d == ds[-1]
                    if end or (not static and (tr is None or sgn * tr < X)):
                        fund = sum(sgn * (fh.get(x, 0) - fb.get(x, 0)) for x in range(d0, d)) * N
                        a0, b0 = ph[d0 * DAY - H][3], pb[d0 * DAY - H][3]
                        a1, b1 = ph[d * DAY - H][3], pb[d * DAY - H][3]
                        gap = sgn * N * ((b1 / b0) - (a1 / a0))     # sgn=+1: short A, long B
                        fees = N * 2 * (fa_fee + fb_fee + 0.0004)
                        liq, ref = False, a0
                        for x in range(d0, d):
                            hs = [ph[t][1] for t in range(x * DAY, x * DAY + DAY, H) if t in ph]
                            ls = [ph[t][2] for t in range(x * DAY, x * DAY + DAY, H) if t in ph]
                            if hs and max(max(hs) / ref - 1, 1 - min(ls) / ref) > 1.0 / lev - 0.03:
                                liq = True      # one of the two legs (short hurt by rises, long by falls) is gone
                                break
                            nxt = ph.get((x + 1) * DAY - H)
                            if nxt and abs(nxt[3] / ref - 1) > 0.5 / lev:   # rebalance margin between venues
                                fees += N * abs(nxt[3] / ref - 1) * 0.0005 + 1.0   # + $1 to move USDC across
                                ref = nxt[3]
                        if liq:
                            fees += N * 0.01
                        eps.append({"coin": coin, "d0": d0, "d1": d, "pnl": fund + gap - fees, "fund": fund, "gap": gap,
                                    "fees": fees, "reb": 0.0, "liq": liq})
                        hold = None
                if not hold and d != days_[-1] and d != ds[-1]:
                    if static:
                        hold = (1, d)
                    elif tr is not None and abs(tr) > E:
                        hold = (1 if tr > 0 else -1, d)
        return eps

    xd = sorted(set(d for x in xs for d in x[5]))
    xmid = xd[0] + (xd[-1] - xd[0]) // 2
    x1, x2 = [d for d in xd if d <= xmid], [d for d in xd if d >= xmid]
    print(f"  days {dstr(xd[0])}..{dstr(xd[-1])}, split {dstr(xmid)}; numbers below are PER COIN (each coin its own $300)")
    nc = max(1, len(xs))
    for lev in (2, 3):
        for half, dd_ in (("1st", x1), ("2nd", x2)):
            s_ = summ(xrun(dd_, 1, 0, 0, lev, static=True), len(dd_))
            print(f"  static short {va} / long {vb}, {lev}x per leg, {half} half: per coin ${s_['pnl']/nc:.2f} "
                  f"(${s_['per_day']/nc:.3f}/day at $300), liquidations {s_['liq']} of {s_['n']}")
    g2, xt = [], 0
    for L in (1, 3, 7):
        for E in (0.0002, 0.0005, 0.001, 0.002):
            for X in (0.0, E / 2):
                for lev in (2, 3):
                    xt += 1
                    e1 = xrun(x1, L, E, X, lev)
                    g2.append((summ(e1, len(x1))["pnl"] / nc, L, E, X, lev, summ(e1, len(x1))))
    g2.sort(key=lambda g: (g[5]["n"] < 3, -g[0]))
    for g in g2[:4]:
        print(f"  first half L{g[1]} E{g[2]} X{g[3]} lev{g[4]}: {fmt(g[5])}")
    L, E, X, lev = g2[0][1:5]
    e2x = xrun(x2, L, E, X, lev)
    s2x = summ(e2x, len(x2))
    print(f"  CHOSEN ({xt} tries + 2 static) second half, all coins: {fmt(s2x)}  (per coin: ${s2x['per_day']/nc:.3f}/day)")
    byc = {}
    for e in e2x:
        byc.setdefault(e["coin"], []).append(e["pnl"])
    print("  by coin: " + ", ".join(f"{k} ${sum(v):.2f}/{len(v)}" for k, v in sorted(byc.items(), key=lambda kv: -sum(kv[1]))))
    try:
        sys.path.insert(0, ".")
        import exam
        bets = [{"cost": BANK, "pay": BANK + e["pnl"], "t": e["d0"] * 86400, "ev": f"{e['coin']}-{e['d0']}"} for e in e2x]
        exam.score(bets, f"funding cross-venue {va} vs {vb}, 2nd half", tries=xt + 2, src="outside/funding.py",
                   note="picked on first half", log=False)
        st = xrun(x2, 1, 0, 0, 3, static=True)
        exam.score([{"cost": BANK, "pay": BANK + e["pnl"], "t": e["d0"] * 86400, "ev": e["coin"]} for e in st],
                   f"funding static short {va} long {vb} 3x, 2nd half", tries=xt + 2, src="outside/funding.py", log=False)
    except Exception as ex:
        print("exam skipped:", ex)




if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    a = sys.argv[2:]
    {"scan": scan, "fetch": fetch, "fetch2": fetch2, "fetch3": fetch3, "report": report}[cmd](*a)
    print("=== DONE ===")
