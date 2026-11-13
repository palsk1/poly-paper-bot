#!/usr/bin/env python3
"""Stock strike markets on Polymarket ("will NVDA close above $X on Friday?") against the stock's own price.

Research only, paper only. Daily "Up or Down" was tested in census.py (dropped); this is the strike ladders.

  python3 stocks.py peek     what is there (tickers, shapes, timing, money) + which price sources Actions can read
  python3 stocks.py src      which minute-by-minute price sources this machine can read
  python3 stocks.py fetch    strike markets + real trades + daily prices -> bt_cache/stk/
  python3 stocks.py run      the test -> backtest/stocks.md
  python3 stocks.py comb     second pass, patterns in the prices alone -> backtest/stocks_comb.md
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


# ================================================================ the test
OUT = "backtest/stocks.md"
TRIES = 40
FEE = 0.04                 # today's fee on these markets
MIN_PRINT = 5.0            # 5-minute steps with under $5 traded are dropped: such crumbs are often booked on the wrong side


def load():
    """markets whose result the daily closing prices reproduce, + their real trades (crumbs dropped) + daily prices."""
    import os
    ms = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}
    D = bt.rjson(os.path.join(CACHE, "daily.json.gz"), {}) or {}
    tp, i = {}, 0
    while os.path.exists(os.path.join(CACHE, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(CACHE, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    for v in tp.values():
        v["b"] = [x for x in v["b"] if x[5] >= MIN_PRINT]
    good, n_bad = {}, 0
    for k, m in ms.items():
        d = D.get(m["tk"], {}).get(_day(m["end"]))
        if not d or (m["tk"] == "NFLX" and _day(m["end"]) < "2025-12"):     # holiday weeks; Netflix before its share split
            n_bad += 1
            continue
        yes = (m["lo"] is None or d[3] > m["lo"]) and (m["hi"] is None or d[3] < m["hi"])
        if yes != (m["final"][0] == 1.0):
            n_bad += 1
            continue
        good[k] = m
    return good, tp, D, len(ms), n_bad


def _day(t):
    return time.strftime("%Y-%m-%d", time.gmtime(t))


def _ncdf(x):
    import math
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def model_chance(m, s, sd):
    """Chance of Yes if the stock is at s now and its log move until the close has a typical size sd."""
    import math
    above = lambda k: 1.0 if k <= 0 else 1 - _ncdf(math.log(k / s) / sd)
    p = 1.0
    if m["lo"] is not None:
        p = above(m["lo"])
    if m["hi"] is not None:
        p -= above(m["hi"])
    return min(1.0, max(0.0, p))


def looks(m, D, order, idx):
    """The moments we can price a market from daily numbers alone: the open of the result day, and the close of each
    of up to 4 trading days before. -> [(label, time, model chance)]. Swings come from the 60 trading days before."""
    import datetime as dt
    import math
    tk, de = m["tk"], _day(m["end"])
    i = idx[tk].get(de)
    if i is None or i < 30:
        return []
    v, ds = D[tk], order[tk]
    rng = range(max(1, i - 60), i)
    f = lambda a: math.sqrt(sum(x * x for x in a) / len(a))
    cc = f([math.log(v[ds[j]][3] / v[ds[j - 1]][3]) for j in rng])
    oc = f([math.log(v[ds[j]][3] / v[ds[j]][0]) for j in rng])
    out = [("open", m["end"] - 6.5 * 3600 + 300, model_chance(m, v[ds[i]][0], oc))]
    for k in (1, 2, 3, 4):
        if i - k < 0:
            break
        t = m["end"] - (dt.date.fromisoformat(de) - dt.date.fromisoformat(ds[i - k])).days * 86400
        if t < (m["start"] or 0) + 3600:
            break
        out.append((f"close-{k}", t + 300, model_chance(m, v[ds[i - k]][3], cc * math.sqrt(k))))
    return out


def buy(m, b, t, yes, extra=0.01, stake=10.0, lo=0.05, hi=0.95, window=7200):
    """Like earn.buy: the worst price anyone paid over the next `window` seconds + extra + fee."""
    nxt = [x for x in b if t <= x[0] < min(t + window, m["end"] - 1800)]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if not lo <= px <= hi:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    win = (m["final"][0] == 1.0) == yes
    return {"ev": m["ev_slug"], "t": nxt[0][0], "cost": stake + bot.taker_fee(sh, c, FEE), "pay": sh if win else 0.0, "sh": sh,
            "px": px, "yes": yes, "id": m["id"]}


def rows_of(ms, tp, D):
    import earn
    order = {tk: sorted(v) for tk, v in D.items()}
    idx = {tk: {d: i for i, d in enumerate(ds)} for tk, ds in order.items()}
    rows = []
    for k, m in ms.items():
        b = (tp.get(k) or {}).get("b")
        if not b:
            continue
        for lab, t, pm in looks(m, D, order, idx):
            pp = earn.last_before(b, t)
            if pp is None or not any(t - 3 * 3600 <= x[0] and x[0] + 300 <= t for x in b):   # needs a trade in the 3 hours before
                continue
            rows.append((k, m, lab, t, pm, pp))
    return rows


def gap_bets(rows, tp, gap=0.10, labs=None, kinds=None, extra=0.01, window=7200, side=None):
    out = []
    for k, m, lab, t, pm, pp in rows:
        if (labs and lab not in labs) or (kinds and m["kind"] not in kinds) or abs(pm - pp) < gap:
            continue
        yes = pm > pp
        if side is not None and yes != side:
            continue
        x = buy(m, tp[k]["b"], t, yes, extra, window=window)
        if x and (pm if yes else 1 - pm) - x["px"] >= gap / 2:          # still cheap at the price paid
            out.append(x)
    return out


def run():
    import btcheck
    import earn
    import exam
    ms, tp, D, n_all, n_bad = load()
    rows = rows_of(ms, tp, D)
    L = []
    P = L.append
    P("# Stock price markets against the stock's own swings (stocks.py)\n")
    P(f"Generated {bot.iso()}. Paper only. The holdout from {btcheck.HOLDOUT_FROM} is not in here.\n")
    P("\"Will Nvidia close above $180 on Friday?\", \"Will Apple finish the week above $240?\", \"Will Tesla close at $330-$340?\" "
      f"Polymarket has run these every day and week since late 2025: {n_all:,} finished markets on {len(D)} stocks, "
      f"{sum(1 for k in ms if (tp.get(k) or {}).get('b')):,} with real trades. Daily prices (open, high, low, close) from Nasdaq's website "
      f"reproduce the result of {n_all - n_bad:,} of them; the rest are holiday weeks and Netflix before its share split, left out.\n")
    P("They trade thinly: the middle market saw about $350, and the gap between buyers and sellers is often 5-20c.\n")
    P("## The idea\n")
    P("A stock's price right now and how much it usually moves in a day give a fair chance of ending above a line. "
      "Compare that with Polymarket's price at moments when the stock's price is known exactly from daily numbers: at the "
      "open of the result day, and at the close 1 to 4 trading days before. Only markets that traded in the 3 hours before.\n")
    P("## Who forecasts better?\n")
    P("Score = average squared miss, smaller is better.\n")
    P("| moment | kind | markets | the model | Polymarket | half and half |")
    P("|---|---|---|---|---|---|")
    y = lambda m: m["final"][0]
    names = {"day": "above a line, one day", "week": "above a line, end of week", "range": "inside a bracket, end of week"}
    for lab in ("open", "close-1", "close-2", "close-3", "close-4"):
        for kind in ("day", "week", "range"):
            R = [r for r in rows if r[2] == lab and r[1]["kind"] == kind]
            if len(R) < 150:
                continue
            br = lambda f: sum((f(r) - y(r[1])) ** 2 for r in R) / len(R)
            P(f"| {'the open of the last day' if lab == 'open' else 'the close ' + lab[-1] + ' day(s) before'} | {names[kind]} | {len(R):,} | "
              f"{br(lambda r: r[4]):.4f} | {br(lambda r: r[5]):.4f} | {br(lambda r: (r[4] + r[5]) / 2):.4f} |")
    P("\nA tie. A plain \"usual swing\" model is as good as the market, and no better.\n")
    P("## Buying where the two disagree\n")
    P("$10 on the side the model calls cheap, at the worst price anyone paid in the next 2 hours + 1c + the fee, and only "
      "if it is still cheap at that price.\n")
    P(earn.HEAD)
    main = gap_bets(rows, tp, 0.10)
    after = gap_bets(rows, tp, 0.10, labs=("close-1", "close-2", "close-3", "close-4"))
    quick = gap_bets(rows, tp, 0.10, window=300)
    for g in (0.05, 0.10, 0.15, 0.25):
        P(earn.line(f"all, model and price {g * 100:.0f}c+ apart", gap_bets(rows, tp, g)))
    P(earn.line("at the open of the last day, 10c+", gap_bets(rows, tp, 0.10, labs=("open",))))
    P(earn.line("after a close, 1-4 days before, 10c+", after))
    for kind in ("day", "week", "range"):
        P(earn.line(f"{names[kind]}, 10c+", gap_bets(rows, tp, 0.10, kinds=(kind,))))
    P(earn.line("only buying Yes, 10c+", gap_bets(rows, tp, 0.10, side=True)))
    P(earn.line("only buying No, 10c+", gap_bets(rows, tp, 0.10, side=False)))
    P(earn.line("10c+, at the next 5 minutes' worst price instead of 2 hours", quick))
    P("\nIt loses at the open and is about even after a close (126 bets, first half up, second half down). Where the price disagrees with the model, the price usually knows "
      "something the daily numbers don't (news, the stock moving before the open), and the gap between buyers and sellers "
      "eats the rest.\n")
    P("## The exam\n")
    import json
    for name, bb in (("Stock price markets: buy where a swing model and the price are 10c+ apart", main),
                     ("Stock price markets: same, only after a close 1-4 days before", after),
                     ("Stock price markets: same, priced at the next 5 minutes instead of 2 hours", quick)):
        card = exam.score(bb, name, tries=TRIES, src="stocks.py, backtest/stocks.md", status="dropped", quiet=True)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {earn.usd(card.get('per100'))} per $100, "
          f"luck range {earn.usd(card.get('lo100'))} to {earn.usd(card.get('hi100'))}, verdict **{card.get('verdict')}**.")
    P("\n**Verdict: dropped, no track.** Same story as the Bitcoin price markets (`optfair.md`): the market is as good "
      "as the model, and thin trading makes every disagreement expensive to buy.\n")
    P("## Traps found\n")
    P(f"- **Crumb trades on the wrong side.** Trades of under $1 often show up at the mirror price (a 5c market \"trading\" at "
      f"95c). When such a crumb is the only trade in the buying window, a backtest buys the winning side for pennies. 5-minute "
      f"steps with under ${MIN_PRINT:.0f} traded are dropped here; without that, \"buy No on long shots after the close\" looked like +$26 per $100.")
    P("- **No free minute-by-minute stock prices.** From GitHub: Yahoo answers 429, Stooq wants a browser check, Pyth's old "
      "chart address is gone. Nasdaq's website gives daily open/high/low/close (`stocks.nasdaq_daily`), which is why the test "
      "only looks at opens and closes.")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


# ================================================================ second pass: patterns in the prices alone
OUT2 = "backtest/stocks_comb.md"
TRIES2 = 150
MOMENTS = ((30, "the afternoon before"), (24, "a day before the close"), (6.4, "just after the open"), (4, "4 hours before the close"),
           (2, "2 hours before the close"), (1, "1 hour before the close"))


def _price(b, t, fresh=3 * 3600):
    """Last real trade price before t, only if there was a trade in the `fresh` seconds before."""
    p, ok = None, False
    for x in b:
        if x[0] + 300 <= t:
            p, ok = x[2], x[0] >= t - fresh
        else:
            break
    return p if ok else None


def comb_rows(ms, tp):
    R = []
    for k, m in ms.items():
        b = (tp.get(k) or {}).get("b")
        if not b:
            continue
        for H, _ in MOMENTS:
            t = m["end"] - H * 3600
            if t < (m["start"] or 0) + 1800:
                continue
            pp = _price(b, t)
            if pp is not None:
                R.append((k, m, H, t, pp))
    return R


def comb_bets(R, tp, sel, yes, lo=0.03, hi=0.97, window=900, extra=0.02):
    """sel(k, m, H, t, price) -> falsy to skip; with yes=None its sign picks the side. Default buy: the worst price of
    the next 15 minutes + 2c + fee. (Two hours is too harsh while the stock market is open: the stock itself moves.)"""
    out = []
    for k, m, H, t, pp in R:
        s_ = sel(k, m, H, t, pp)
        if not s_:
            continue
        x = buy(m, tp[k]["b"], t, yes if yes is not None else s_ > 0, extra, lo=lo, hi=hi, window=window)
        if x:
            out.append(x)
    return out


def comb():
    import json
    import btcheck
    import earn
    import exam
    ms, tp, D, n_all, n_bad = load()
    R = comb_rows(ms, tp)
    B = lambda sel, yes, **kw: comb_bets(R, tp, sel, yes, **kw)
    cell = lambda b: f"{earn.usd(earn.per100(b))} ({len(b)})" if len(b) >= 20 else f"- ({len(b)})"
    L = []
    P = L.append
    P("# Stock price markets, second pass: patterns in the prices alone (stocks.py comb)\n")
    P(f"Generated {bot.iso()}. Paper only. The holdout from {btcheck.HOLDOUT_FROM} is not in here. Jan's ask (13 Nov): "
      "\"we have so much data downloaded, it's worth combing through it\". The first pass (`stocks.md`) only compared "
      "the price with a swing model.\n")
    P(f"{len(R):,} looks at {len({r[0] for r in R}):,} markets, at six moments of each market's life, only where it had traded in "
      "the 3 hours before. Every buy is $10 at the worst price anyone paid in the next 15 minutes + 2c + the fee. About "
      f"{TRIES2} cuts were looked at, so the exam's luck bar is set for that.\n")
    P("## 1. Every price band, every moment, both sides\n")
    P("Per $100 (number of bets).\n")
    bands = ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97))
    P("| moment | side | " + " | ".join(f"Yes at {a * 100:.0f}-{b * 100:.0f}c" for a, b in bands) + " |")
    P("|---|---|" + "---|" * len(bands))
    for H, nm in MOMENTS:
        for yes in (True, False):
            P(f"| {nm} | buy {'Yes' if yes else 'No'} | " + " | ".join(
                cell(B(lambda k, m, h, t, pp, a=a, b=b: h == H and a <= pp < b, yes)) for a, b in bands) + " |")
    P("\nBuying Yes loses almost everywhere, and long shots (Yes under 25c) lose most: $25 to $90 per $100. People overpay "
      "for the small chance. The other side of that, No on long shots, is the only corner that is ahead.\n")
    P("## 2. The one lean: No on long shots in the afternoon\n")
    P(earn.HEAD)
    ls = lambda Hs, kinds=None: (lambda k, m, h, t, pp: h in Hs and .05 <= pp < .25 and (not kinds or m["kind"] in kinds))
    lead = B(ls((4, 2)), False)
    lead_day = B(ls((4, 2), ("day",)), False)
    P(earn.line("No where Yes is 5-25c, 4 and 2 hours before the close", lead))
    P(earn.line("the same, one-day markets only", lead_day))
    P(earn.line("the same, end-of-week line markets", B(ls((4, 2), ("week",)), False)))
    P(earn.line("the same, end-of-week bracket markets", B(ls((4, 2), ("range",)), False)))
    harsh = B(ls((4, 2)), False, window=7200, extra=0.01)
    P(earn.line("all kinds, at the worst price of the next 2 hours + 1c", harsh))
    P(earn.line("all kinds, at the worst price of the next 15 minutes + 4c", B(ls((4, 2)), False, extra=0.04)))
    P(earn.line("just after the open instead", B(ls((6.4,)), False)))
    P(earn.line("1 hour before the close instead", B(ls((1,)), False)))
    P(earn.line("a day before instead", B(ls((30, 24)), False)))
    P("\nAhead with 4 and 2 hours left, behind at the open and in the last hour, and behind if the buy costs what the "
      "worst buyer of the next 2 hours paid. A thin lean that lives or dies on the price you really get.\n")
    P("## 3. Other cuts\n")
    P(earn.HEAD)
    P(earn.line("Yes on favorites (Yes at 75-97c), last 4 hours", B(lambda k, m, h, t, pp: h in (4, 2, 1) and .75 <= pp < .97, True)))

    def mv(H, sign):
        def f(k, m, h, t, pp):
            if h != H:
                return 0
            p0 = _price(tp[k]["b"], t - 3 * 3600, fresh=10 ** 9)
            if p0 is None or abs(pp - p0) < 0.08:
                return 0
            return sign if pp > p0 else -sign
        return f
    for H, nm in MOMENTS[2:]:
        P(earn.line(f"price moved 8c+ in 3 hours, follow it, {nm}", B(mv(H, 1), None, lo=.10, hi=.90)))
        P(earn.line(f"price moved 8c+ in 3 hours, bet against it, {nm}", B(mv(H, -1), None, lo=.10, hi=.90)))
    P("\nBy stock, all moments, buys at 10-90c (Yes side / No side per $100):\n")
    P("| stock | buy Yes | buy No |")
    P("|---|---|---|")
    for tk in sorted({m["tk"] for m in ms.values()}):
        y, n = (B(lambda k, m, h, t, pp, s_=s_: m["tk"] == tk and .1 <= pp <= .9, s_, lo=.10, hi=.90) for s_ in (True, False))
        if len(y) >= 30:
            P(f"| {tk} | {cell(y)} | {cell(n)} |")
    P("\nNo stock stands out: No beats Yes on most of them, and both lose. Following or betting against a move loses at "
      "every moment. Brackets that don't add up to $1 and lines priced out of order are too rare to bet on (under 25 "
      "cases at any moment).\n")
    P("## The exam\n")
    for name, bb, st in (("Stock price markets: No on long shots (Yes 5-25c), 4 and 2 hours before the close", lead, "lean: thin, depends on the buy price"),
                         ("Stock price markets: same, one-day markets only", lead_day, "lean: thin, depends on the buy price"),
                         ("Stock price markets: same, at the worst price of the next 2 hours", harsh, "dropped")):
        card = exam.score(bb, name, tries=TRIES2, src="stocks.py comb, backtest/stocks_comb.md", status=st, quiet=True)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {earn.usd(card.get('per100'))} per $100, "
          f"luck range {earn.usd(card.get('lo100'))} to {earn.usd(card.get('hi100'))}, worst case {earn.usd(card.get('floor100'))} per $100, "
          f"verdict **{card.get('verdict')}**.")
    open(OUT2, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "src": src, "fetch": fetch, "run": run, "comb": comb}[cmd]()
