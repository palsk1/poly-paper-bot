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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek}[cmd]()
