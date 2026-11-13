#!/usr/bin/env python3
"""Stock strike markets on Polymarket ("will NVDA close above $X on Friday?") against the stock's own price.

Research only, paper only. Daily "Up or Down" was tested in census.py (dropped); this is the strike ladders.

  python3 stocks.py peek     what is there (tickers, shapes, timing, money) + which price sources Actions can read
"""
import collections
import json
import re
import statistics
import sys
import time

import backtest as bt
import bot
import boxoffice

G = bot.GAMMA if hasattr(bot, "GAMMA") else "https://gamma-api.polymarket.com"
TAG = 604
CACHE_DIR = "stk"

SHAPES = (("week_above", re.compile(r"^will (.+?) \(([A-Z.\-]+)\) finish (?:the )?week of (.+?) above \$?([\d,.]+)", re.I)),
          ("day_above", re.compile(r"^will (.+?) \(([A-Z.\-]+)\) close above \$?([\d,.]+) on (.+?)\?", re.I)),
          ("week_range", re.compile(r"^will (.+?) \(([A-Z.\-]+)\) close at \$?([\d,.]+)-\$?([\d,.]+) on the final day", re.I)),
          ("updown", re.compile(r"\(([A-Z.\-]+)\) up or down", re.I)))


def shape(q):
    for nm, rx in SHAPES:
        if rx.search(q or ""):
            return nm
    return "other"


def pages(closed="true", max_pages=400):
    out, cur = [], None
    for _ in range(max_pages):
        p = {"tag_id": TAG, "closed": closed, "limit": 50}
        if cur:
            p["after_cursor"] = cur
        r = bot.http_json(f"{boxoffice.G}/events/keyset", p)
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        out += rows
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur:
            break
    return out


def try_source(name, url):
    try:
        t0 = time.time()
        s = boxoffice.raw(url)
        print(f"  {name}: OK {len(s)} bytes in {time.time() - t0:.1f}s | {s[:300]!r}")
        return s
    except Exception as ex:
        print(f"  {name}: FAILED {type(ex).__name__} {str(ex)[:200]}")


def peek():
    ev = pages()
    print(f"{len(ev)} finished events under tag stocks")
    by, ex, tick, life, endh, vol, months = collections.Counter(), {}, collections.defaultdict(collections.Counter), collections.defaultdict(list), collections.defaultdict(collections.Counter), collections.defaultdict(list), collections.defaultdict(collections.Counter)
    for e in ev:
        for m in e.get("markets") or []:
            q = m.get("question") or ""
            sh = shape(q)
            by[sh] += 1
            ex.setdefault(sh, []).append(m)
            mt = re.search(r"\(([A-Z.\-]+)\)", q)
            tick[sh][mt.group(1) if mt else "?"] += 1
            st, en = bot.parse_iso(m.get("startDate") or m.get("createdAt")), bot.parse_iso(m.get("endDate"))
            if st and en:
                life[sh].append((en.timestamp() - st.timestamp()) / 3600)
                endh[sh][en.strftime("%a %H:%M")] += 1
                months[sh][en.strftime("%Y-%m")] += 1
            vol[sh].append(bot.fnum(m.get("volumeNum") or m.get("volume")))
    for sh, n in by.most_common():
        v = sorted(vol[sh])
        print(f"\n== {sh}: {n} markets, traded: middle ${statistics.median(v):,.0f}, top tenth ${v[int(len(v) * .9)]:,.0f}, $1000+ {sum(1 for x in v if x >= 1000)}, total ${sum(v):,.0f}")
        if life[sh]:
            L = sorted(life[sh])
            print(f"   hours from open to end: a tenth under {L[len(L) // 10]:.0f}, middle {statistics.median(L):.0f}, a tenth over {L[int(len(L) * .9)]:.0f}")
        print(f"   ends at (UTC): {endh[sh].most_common(6)}")
        print(f"   by month: {sorted(months[sh].items())}")
        print(f"   tickers: {tick[sh].most_common(40)}")
        for m in ex[sh][:2] + ex[sh][-2:]:
            print(f"   e.g. {m.get('question')} | prices {m.get('outcomePrices')} | start {m.get('startDate')} end {m.get('endDate')} | fee {m.get('feesEnabled')} {m.get('feeType')} | vol {m.get('volumeNum')}")
            print(f"        rules: {str(m.get('description') or '')[:700]!r}")
    op = pages("false", 20)
    c = collections.Counter(shape(m.get("question")) for e in op for m in e.get("markets") or [])
    print(f"\nopen now: {len(op)} events, shapes {c.most_common()}")
    for e in op[:400]:
        for m in (e.get("markets") or [])[:1]:
            if shape(m.get("question")) in ("week_above", "day_above", "week_range"):
                print(f"   open e.g. {m.get('question')} | prices {m.get('outcomePrices')} | bid {m.get('bestBid')} ask {m.get('bestAsk')} | liq {m.get('liquidityNum')} | start {m.get('startDate')} end {m.get('endDate')}")
                break
    print("\nprice sources from this machine:")
    now = int(time.time())
    try_source("yahoo 1h 730d", "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?interval=1h&range=730d")
    try_source("yahoo 5m 60d", "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?interval=5m&range=60d")
    try_source("yahoo 1m 7d", "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?interval=1m&range=7d")
    try_source("yahoo 1d 2y", "https://query2.finance.yahoo.com/v8/finance/chart/NVDA?interval=1d&range=2y")
    try_source("yahoo VIX 1h", "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1h&range=730d")
    try_source("stooq daily", "https://stooq.com/q/d/l/?s=nvda.us&i=d")
    try_source("stooq 5m", "https://stooq.com/q/d/l/?s=nvda.us&i=5")
    try_source("nasdaq hist", "https://api.nasdaq.com/api/quote/NVDA/historical?assetclass=stocks&fromdate=2025-10-01&limit=9999&todate=2026-11-13")
    try_source("pyth benchmarks 5m", f"https://benchmarks.pyth.network/v1/shims/tradingview/history?symbol=Equity.US.NVDA%2FUSD&resolution=5&from={now - 5 * 86400}&to={now}")
    try_source("pyth benchmarks 5m old", f"https://benchmarks.pyth.network/v1/shims/tradingview/history?symbol=Equity.US.NVDA%2FUSD&resolution=5&from={now - 300 * 86400}&to={now - 295 * 86400}")


def src():
    """Which intraday price sources can this machine read?"""
    now = int(time.time())
    P = "https://benchmarks.pyth.network/v1/shims/tradingview"
    try_source("pyth symbols", f"{P}/symbols?symbol=Equity.US.NVDA/USD")
    try_source("pyth search", f"{P}/search?query=NVDA&limit=10")
    for res, back, span in (("5", 3, 2), ("1", 3, 1), ("5", 200, 5), ("60", 300, 20), ("1", 300, 1), ("D", 400, 300)):
        try_source(f"pyth res {res}, {back} days back", f"{P}/history?symbol=Equity.US.NVDA/USD&resolution={res}&from={now - back * 86400}&to={now - (back - span) * 86400}")
    try_source("nasdaq chart", "https://api.nasdaq.com/api/quote/NVDA/chart?assetclass=stocks&fromdate=2026-10-01&todate=2026-11-13")
    try_source("yahoo query2 1h", "https://query2.finance.yahoo.com/v8/finance/chart/NVDA?interval=1h&range=730d")
    try_source("yahoo spark", "https://query1.finance.yahoo.com/v7/finance/spark?symbols=NVDA&range=60d&interval=5m")
    try_source("binance xstock", "https://data-api.binance.vision/api/v3/klines?symbol=NVDAXUSDT&interval=5m&limit=5")
    try_source("bybit xstock", "https://api.bybit.com/v5/market/kline?category=spot&symbol=NVDAXUSDT&interval=5&limit=5")
    try_source("kraken xstock", "https://api.kraken.com/0/public/OHLC?pair=NVDAxUSD&interval=5")
    try_source("hyperliquid", "https://api.hyperliquid.xyz/info")


# ================================================================ collect
CACHE = __import__("os").path.join(bt.CACHE, CACHE_DIR)
SHARD = 500
ETF = {"SPY", "QQQ", "EWY", "GLD", "SLV", "IWM", "DIA"}
RX_ABOVE = re.compile(r"\(([A-Z.]+)\)\s+(?:finish(?:es)? (?:the )?week of .+? above|closes? above)\s+\$?([\d,]+(?:\.\d+)?)", re.I)
RX_RANGE = re.compile(r"\(([A-Z.]+)\)\s+closes? at\s+\$?([\d,]+(?:\.\d+)?)\s*-\s*\$?([\d,]+(?:\.\d+)?)", re.I)
RX_EDGE = re.compile(r"\(([A-Z.]+)\)\s+closes? at\s+(<|>|less than|below|above|greater than|more than)\s*\$?([\d,]+(?:\.\d+)?)", re.I)


def parse(q):
    """-> (ticker, kind, low, high): the closing price must be above low and/or below high for Yes."""
    f = lambda x: float(x.replace(",", ""))
    q = q or ""
    m = RX_ABOVE.search(q)
    if m:
        return m.group(1).upper(), "week" if re.search("week", q, re.I) else "day", f(m.group(2)), None
    m = RX_RANGE.search(q)
    if m:
        return m.group(1).upper(), "range", f(m.group(2)), f(m.group(3))
    m = RX_EDGE.search(q)
    if m:
        up = m.group(2).lower() in (">", "above", "greater than", "more than")
        return m.group(1).upper(), "range", f(m.group(3)) if up else None, None if up else f(m.group(3))
    return None


def nasdaq_daily(tk):
    import datetime as dt
    cls = "etf" if tk in ETF else "stocks"
    r = json.loads(boxoffice.raw(f"https://api.nasdaq.com/api/quote/{tk}/historical?assetclass={cls}&fromdate=2025-06-01&limit=9999&todate={dt.date.today()}"))
    out = {}
    n = lambda x: float(str(x).replace("$", "").replace(",", ""))
    for row in (((r.get("data") or {}).get("tradesTable") or {}).get("rows") or []):
        try:
            mo, d, y = row["date"].split("/")
            out[f"{y}-{mo}-{d}"] = [n(row["open"]), n(row["high"]), n(row["low"]), n(row["close"])]
        except Exception:
            pass
    return out


def fetch():
    import concurrent.futures as cf
    import hashlib
    import os
    import btcheck
    import optfair
    T0 = time.time()
    os.makedirs(CACHE, exist_ok=True)
    ms, skipped = {}, collections.Counter()
    for e in pages():
        for m in e.get("markets") or []:
            if not isinstance(m, dict):
                continue
            p = parse(m.get("question"))
            if not p:
                skipped[shape(m.get("question"))] += 1
                continue
            m = dict(m)
            m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
            s = bt.slim_market(m)
            s["cid"] = m.get("conditionId")
            s["tk"], s["kind"], s["lo"], s["hi"] = p
            s["pyth"] = "pyth" in str(m.get("description") or "").lower()
            if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                ms[s["id"]] = s
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    n_all = len(ms)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}          # the holdout stays unseen until 21 Dec
    bt.wjson(os.path.join(CACHE, "markets.json.gz"), ms)
    print(f"strike markets {n_all}, before the holdout {len(ms)}, events {len({m['ev_slug'] for m in ms.values()})}, "
          f"kinds {collections.Counter(m['kind'] for m in ms.values()).most_common()}, not strike markets: {skipped.most_common()}", flush=True)
    tks = sorted({m["tk"] for m in ms.values()})
    dpath = os.path.join(CACHE, "daily.json.gz")
    daily = bt.rjson(dpath, {}) or {}
    for tk in tks:
        try:
            d = nasdaq_daily(tk)
            if d:
                daily[tk] = d
            print(f"  daily {tk}: {len(d)} days {min(d) if d else ''}..{max(d) if d else ''}", flush=True)
        except Exception as ex:
            print(f"  daily {tk}: FAILED {str(ex)[:120]}", flush=True)
        time.sleep(1.0)
    bt.wjson(dpath, daily)
    want = sorted((m for m in ms.values() if m.get("closed") and (m.get("vol") or 0) >= 200),
                  key=lambda m: hashlib.md5(("stk" + m["ev_slug"]).encode()).hexdigest())
    n_sh = (len(want) + SHARD - 1) // SHARD
    print(f"tapes wanted: {len(want)} markets with $200+ traded, {n_sh} files", flush=True)
    for i in range(n_sh):
        path = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if os.path.exists(path):
            continue
        if time.time() - T0 > 100 * 60:
            print("  out of time, run again to continue", flush=True)
            break
        chunk = want[i * SHARD:(i + 1) * SHARD]
        out = {}
        with cf.ThreadPoolExecutor(8) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                if r is not None:
                    out[mid] = r
        bt.wjson(path, out)
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "src": src, "fetch": fetch}[cmd]()
