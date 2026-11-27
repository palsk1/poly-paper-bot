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


def report(*a):
    raise SystemExit("report not written yet")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    a = sys.argv[2:]
    {"scan": scan, "fetch": fetch, "report": report}[cmd](*a)
    print("=== DONE ===")
