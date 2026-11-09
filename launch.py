#!/usr/bin/env python3
"""Launch test (2026-11-09): are brand-new markets mispriced in their first hours?

PAPER ONLY. Reads public history, never trades.

    python3 launch.py peek      # API shapes for new-listing data (probe: btlaunchpeek)
"""
import datetime as dt
import json
import math
import os
import random
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import btcheck
import calib

G, C, D, K = bot.GAMMA, bot.CLOB, bot.DATA, bot.KALSHI
DAY = 86400


def show(name, fn, n=2500):
    print(f"\n===== {name}")
    try:
        r = fn()
        s = json.dumps(r, indent=1, default=str)
        print(s[:n] + (" ...(cut)" if len(s) > n else ""))
        return r
    except Exception as e:
        print("FAILED:", e)
        return None


def slim(m):
    keep = ("id", "question", "conditionId", "slug", "startDate", "createdAt", "acceptingOrdersTimestamp", "endDate",
            "closedTime", "volumeNum", "outcomePrices", "clobTokenIds", "enableOrderBook", "negRisk", "events",
            "deployingTimestamp", "umaResolutionStatus")
    out = {k: m.get(k) for k in keep if k in m}
    if isinstance(out.get("events"), list):
        out["events"] = [{k: e.get(k) for k in ("id", "slug", "createdAt", "startDate")} for e in out["events"][:1]]
    return out


def peek():
    now = int(time.time())
    # 1. Polymarket: markets by START date, no volume floor
    lo = dt.datetime(2026, 9, 15, tzinfo=dt.timezone.utc)
    r = show("gamma keyset by start date", lambda: [slim(m) for m in bot.envelope_rows(bot.http_json(
        f"{G}/markets/keyset", {"closed": "true", "limit": 500, "start_date_min": bot.iso(lo),
                                "start_date_max": bot.iso(lo + dt.timedelta(hours=6))}), "markets", "data")][:3])
    rows = bot.envelope_rows(bot.http_json(f"{G}/markets/keyset", {"closed": "true", "limit": 500, "start_date_min": bot.iso(lo),
                                                                     "start_date_max": bot.iso(lo + dt.timedelta(days=1))}), "markets", "data")
    print("rows for one day by start:", len(rows), "vol>0:", sum(1 for m in rows if bot.fnum(m.get("volumeNum"), 0) > 0),
          "vol>1k:", sum(1 for m in rows if bot.fnum(m.get("volumeNum"), 0) > 1000))
    starts = sorted(str(m.get("startDate"))[:16] for m in rows)
    print("start range:", starts[:2], starts[-2:])
    print("createdAt vs startDate (first 8):", [(str(m.get("createdAt"))[:19], str(m.get("startDate"))[:19],
                                                str(m.get("acceptingOrdersTimestamp"))[:19]) for m in rows[:8]])
    big = sorted(rows, key=lambda m: -bot.fnum(m.get("volumeNum"), 0))
    mk = big[len(big) // 10] if big else None   # a fairly busy one
    small = big[len(big) // 2] if big else None
    for tag, m in (("busy", mk), ("median", small)):
        if not m:
            continue
        print(f"\n### {tag}: {m.get('question')} vol {m.get('volumeNum')} start {m.get('startDate')} "
              f"accept {m.get('acceptingOrdersTimestamp')}")
        tok = bot.market_tokens(m)[0]
        s = int(bot.parse_iso(m.get("acceptingOrdersTimestamp") or m.get("startDate")).timestamp())
        for fid in (1, 5, 60):
            show(f"{tag} prices-history start..+2d fidelity {fid}", lambda: (lambda h: {"n": len(h), "first": h[:6], "last": h[-2:]})(
                bot.envelope_rows(bot.http_json(f"{C}/prices-history", {"market": tok, "startTs": s - 3600, "endTs": s + 2 * DAY,
                                                                        "fidelity": fid}), "history")), 800)
        cid = m.get("conditionId")
        for p in ({"condition_id": cid, "limit": 5}, {"condition_id": cid, "limit": 5, "sortDirection": "ASC"},
                  {"condition_id": cid, "limit": 5, "start": s, "end": s + 3600},
                  {"condition_id": cid, "limit": 5, "offset": 3000}):
            show(f"{tag} v2/trades {p}", lambda: [{k: t.get(k) for k in ("timestamp", "price", "size", "side", "outcome", "outcomeIndex")}
                                                   for t in bot.envelope_rows(bot.http_json(f"{D}/v2/trades", p), "data", "trades")], 900)
        show(f"{tag} v2/trades raw keys", lambda: (lambda res: {"type": type(res).__name__, "keys": list(res.keys()) if isinstance(res, dict) else None,
                                                                "row": (bot.envelope_rows(res, "data", "trades") or [None])[0]})(
            bot.http_json(f"{D}/v2/trades", {"condition_id": cid, "limit": 2})), 1500)
    # 2. Polymarket: brand-new listings right now
    show("gamma newest listings", lambda: [slim(m) for m in bot.envelope_rows(bot.http_json(
        f"{G}/markets", {"limit": 8, "order": "createdAt", "ascending": "false", "closed": "false"}), "markets", "data")], 4000)
    show("gamma newest by startDate", lambda: [(m.get("question"), m.get("createdAt"), m.get("startDate"), m.get("volumeNum"))
                                               for m in bot.envelope_rows(bot.http_json(
        f"{G}/markets", {"limit": 15, "order": "startDate", "ascending": "false", "closed": "false"}), "markets", "data")], 3000)
    show("gamma events newest", lambda: [(e.get("title"), e.get("createdAt"), e.get("startDate"), len(e.get("markets") or []))
                                         for e in bot.envelope_rows(bot.http_json(
        f"{G}/events", {"limit": 10, "order": "createdAt", "ascending": "false", "closed": "false"}), "events", "data")], 3000)
    # 3. Kalshi
    show("kalshi cutoff", lambda: bot.http_json(f"{K}/historical/cutoff"))
    res = show("kalshi settled sample", lambda: (lambda r: {"n": len(r.get("markets") or []), "cursor": bool(r.get("cursor")),
                                                            "first": [(m.get("ticker"), m.get("event_ticker"), m.get("open_time"), m.get("created_time"),
                                                                       m.get("close_time"), m.get("result"), m.get("volume_fp") or m.get("volume"))
                                                                      for m in (r.get("markets") or [])[:12]]})(
        bot.http_json(f"{K}/markets", {"status": "settled", "min_close_ts": now - 3 * DAY, "max_close_ts": now - 2 * DAY,
                                       "limit": 1000})), 3500)
    show("kalshi events newest", lambda: (lambda r: [(e.get("event_ticker"), e.get("series_ticker"), e.get("title"), e.get("category"))
                                                     for e in (r.get("events") or [])[:10]])(
        bot.http_json(f"{K}/events", {"status": "open", "limit": 10})), 2000)
    km = bot.http_json(f"{K}/markets", {"status": "settled", "min_close_ts": now - 3 * DAY, "max_close_ts": now - 2 * DAY, "limit": 1000})
    ms = [m for m in km.get("markets") or [] if not str(m.get("ticker", "")).startswith("KXMVE")]
    print("non-combo settled in that day-ish page:", len(ms))
    if ms:
        ms.sort(key=lambda m: -bot.fnum(m.get("volume_fp") or m.get("volume"), 0))
        m = ms[min(len(ms) - 1, 20)]
        o = int(bot.parse_iso(m.get("open_time")).timestamp())
        ser = m.get("series_ticker") or str(m.get("event_ticker", "")).split("-")[0]
        print("kalshi pick:", m.get("ticker"), m.get("title"), m.get("open_time"), m.get("close_time"), ser)
        show("kalshi candles at open", lambda: (lambda r: (r.get("candlesticks") or [])[:4])(
            bot.http_json(f"{K}/series/{ser}/markets/{m['ticker']}/candlesticks", {"start_ts": o, "end_ts": o + 3 * 3600,
                                                                                    "period_interval": 1})), 3000)
        show("kalshi trades at open", lambda: (lambda r: (r.get("trades") or [])[:5])(
            bot.http_json(f"{K}/markets/trades", {"ticker": m["ticker"], "min_ts": o, "max_ts": o + 3 * 3600, "limit": 1000})), 1500)


def peek2():
    now = int(time.time())
    lo = dt.datetime(2026, 9, 15, tzinfo=dt.timezone.utc)
    r = bot.http_json(f"{G}/markets/keyset", {"closed": "true", "limit": 500, "start_date_min": bot.iso(lo),
                                              "start_date_max": bot.iso(lo + dt.timedelta(days=1))})
    print("keyset keys:", list(r.keys()) if isinstance(r, dict) else type(r), "rows", len(bot.envelope_rows(r, "markets", "data")),
          "cursor", str(r.get("next_cursor"))[:40] if isinstance(r, dict) else None)
    n, cur, pages = 0, None, 0
    qs = []
    while pages < 80:
        p = {"closed": "true", "limit": 500, "start_date_min": bot.iso(lo), "start_date_max": bot.iso(lo + dt.timedelta(days=1))}
        if cur:
            p["after_cursor"] = cur
        r = bot.http_json(f"{G}/markets/keyset", p)
        rows = bot.envelope_rows(r, "markets", "data")
        n += len(rows)
        pages += 1
        qs += [str(m.get("question")) for m in rows]
        cur = r.get("next_cursor")
        if not cur or not rows:
            break
    print(f"one day by start: {n} markets in {pages} pages")
    import random
    random.seed(1)
    for q in random.sample(qs, min(60, len(qs))):
        print("  ", q[:90])
    res = bot.http_json(f"{D}/v2/trades", {"condition_id": "0x6c78c989142c1d38f72780a3fbccef82b95d36e982aeb323f797d0f5c0ef777c", "limit": 500})
    print("trades pagination:", res.get("pagination"), "rows", len(res.get("data") or []))
    pg = res.get("pagination") or {}
    for k in ("next_cursor", "cursor", "nextCursor", "next"):
        if pg.get(k):
            r2 = bot.http_json(f"{D}/v2/trades", {"condition_id": "0x6c78c989142c1d38f72780a3fbccef82b95d36e982aeb323f797d0f5c0ef777c",
                                                  "limit": 500, "cursor": pg[k]})
            print("page2 via cursor:", r2.get("pagination"), len(r2.get("data") or []),
                  (r2.get("data") or [{}])[-1].get("timestamp"))
    for f in ("exclude", None):
        p = {"status": "settled", "min_close_ts": now - 3 * DAY, "max_close_ts": now - 2 * DAY, "limit": 1000}
        if f:
            p["mve_filter"] = f
        try:
            r = bot.http_json(f"{K}/markets", p)
            ms = r.get("markets") or []
            print(f"kalshi mve_filter={f}: {len(ms)} rows, non-combo {sum(1 for m in ms if not m['ticker'].startswith('KXMVE'))}")
            if f:
                import collections
                print("  series:", collections.Counter(m["event_ticker"].split("-")[0] for m in ms).most_common(25))
                kms = ms
        except Exception as e:
            print("kalshi failed", f, e)
    ms = [m for m in kms if not m["ticker"].startswith("KXMVE")]
    ms.sort(key=lambda m: -bot.fnum(m.get("volume_fp") or m.get("volume"), 0))
    for m in ms[5:7] + ms[len(ms) // 3:len(ms) // 3 + 1]:
        o = int(bot.parse_iso(m.get("open_time")).timestamp())
        ser = m.get("series_ticker") or m["event_ticker"].split("-")[0]
        print("\nkalshi:", m["ticker"], m.get("title"), "open", m.get("open_time"), "close", m.get("close_time"), "vol", m.get("volume_fp"))
        show("candles", lambda: (lambda r: (r.get("candlesticks") or [])[:3])(
            bot.http_json(f"{K}/series/{ser}/markets/{m['ticker']}/candlesticks", {"start_ts": o, "end_ts": o + 3 * 3600, "period_interval": 1})), 2500)
        show("trades", lambda: (lambda r: [(t.get("created_time"), t.get("yes_price_dollars") or t.get("yes_price"), t.get("count_fp") or t.get("count"), t.get("taker_side"))
                                           for t in (r.get("trades") or [])][-8:])(
            bot.http_json(f"{K}/markets/trades", {"ticker": m["ticker"], "min_ts": o, "max_ts": o + 3 * 3600, "limit": 1000})), 1200)
    # live: book of the newest non-crypto listings
    rows = bot.envelope_rows(bot.http_json(f"{G}/markets", {"limit": 100, "order": "createdAt", "ascending": "false", "closed": "false"}), "markets")
    print("\nnewest 100 listings age (min):", [round((now - bot.parse_iso(m.get("createdAt")).timestamp()) / 60) for m in rows][::10])
    for m in [m for m in rows if "Up or Down" not in str(m.get("question"))][:6]:
        tok = bot.market_tokens(m)[0]
        b = bot.http_json(f"{C}/book", {"token_id": tok})
        bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids") or []), reverse=True)[:4]
        asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks") or [])[:4]
        print(m.get("question")[:70], "| age min", round((now - bot.parse_iso(m.get("createdAt")).timestamp()) / 60), "| bids", bids, "| asks", asks)


# ================================================================ categories

CATS = (
    ("crypto up/down", r"up or down"),
    ("esports", r"counter-strike|\bcs2\b|dota|league of legends|\blol\b|valorant|rainbow six|overwatch|call of duty|"
                r"\bmap \d|kills|honor of kings|mobile legends|rocket league|starcraft"),
    ("weather", r"temperature|°[cf]|\brain\b|\bsnow|hurricane"),
    ("crypto price", r"bitcoin|ethereum|solana|\bxrp\b|\bbtc\b|\beth\b|dogecoin|\bbnb\b|zcash|hyperliquid"),
    ("mentions", r"\bsays?\b|\bsaid\b|\bmention"),
    ("post counts", r"tweets|\bposts\b|# of |truth social"),
    ("sports", r"\bvs\.?\b|o/u|over/under|handicap|spread|winner|goalscorer|\bnfl\b|\bnba\b|\bmlb\b|\bnhl\b|\bufc\b|"
               r"touchdown|strikeouts|rebounds|assists|\bset \d|innings?|\bwin on 20|both teams|exact score|top scorer|"
               r"\bgoal|corners|hits|home runs|bases|yards|\bpoints\b|\bmvp\b|champion|\bseason\b|\bweek \d"),
)
_CAT_RE = [(n, re.compile(rx, re.I)) for n, rx in CATS]


def category(q, sports_flag=False):
    for n, rx in _CAT_RE:
        if n == "sports" and sports_flag:
            return n
        if rx.search(q):
            return n
    if sports_flag:
        return "sports"
    t = calib.topic(q)
    return {"other": "other (one-off questions)"}.get(t, t)


KSPORT = re.compile(r"NCAA|NFL|NBA|MLB|NHL|WNBA|MLS|EPL|SERIEA|LALIGA|BUNDES|LIGUE|UCL|UEL|SOCCER|ATP|WTA|ITF|UFC|"
                    r"PGA|LPGA|NASCAR|F1|BOXING|CRICKET|IPL|RUGBY|AFL|LNB|KBO|NPB|EUROLEAGUE|GAME$|SPREAD|TOTAL|"
                    r"MATCH|GOAL|SCORE|ESPORT|CS2|LOL|DOTA|VALORANT|TENNIS|GOLF|NCAAF|NCAAMB|CFB|CBB")


def kcategory(series, title):
    s = series.upper()
    if re.search(r"BTC|ETH|SOL|XRP|DOGE|CRYPTO|BNB|SHIBA|HYPE", s):
        return "crypto price"
    if re.search(r"HIGH|LOWT|TEMP|RAIN|SNOW|WEATHER|HURR", s):
        return "weather"
    if re.search(r"MENTION|SAY", s):
        return "mentions"
    if KSPORT.search(s):
        return "sports"
    return category(title or "")


# ================================================================ Polymarket download

CACHE = os.path.join(bt.CACHE, "launch")
P_MK = os.path.join(CACHE, "poly_markets.json.gz")
P_H = os.path.join(CACHE, "poly_hist.json.gz")
K_MK = os.path.join(CACHE, "kalshi_markets.json.gz")
K_H = os.path.join(CACHE, "kalshi_hist.json.gz")
START = os.environ.get("LAUNCH_START", "2026-03-01")
LAST_END = btcheck.HOLDOUT_FROM          # only markets that ended before the holdout day
PER_CAT_DAY = int(os.environ.get("LAUNCH_PER_CAT", "12"))
WORKERS = int(os.environ.get("LAUNCH_WORKERS", "12"))
T0 = time.time()
BUDGET_MIN = float(os.environ.get("LAUNCH_MIN", "200"))


def tsec(x):
    d = bot.parse_iso(x) if isinstance(x, str) else None
    return int(d.timestamp()) if d else None


def poly_day(d):
    """Every market that STARTED on day d and is closed (no volume floor), then a random sample per category."""
    rows, cur = [], None
    for _ in range(400):
        p = {"closed": "true", "limit": 500, "start_date_min": bot.iso(d), "start_date_max": bot.iso(d + dt.timedelta(days=1))}
        if cur:
            p["after_cursor"] = cur
        try:
            r = bot.http_json(f"{G}/markets/keyset", p)
        except Exception as e:
            print(f"  {d:%Y-%m-%d} page failed: {e}")
            break
        got = [m for m in bot.envelope_rows(r, "markets", "data") if isinstance(m, dict)]
        rows += got
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not cur or not got:
            break
    by = defaultdict(list)
    for m in rows:
        sm = bt.slim_market(m)
        if len(sm["toks"]) != 2 or not sm["end"] or not sm["start"]:
            continue
        acc = tsec(m.get("acceptingOrdersTimestamp"))
        sm["t0"] = max(sm["start"], acc or 0)
        sm["cid"] = m.get("conditionId")
        sm["neg"] = bool(m.get("negRisk"))
        if bot.iso(dt.datetime.fromtimestamp(sm["end"], dt.timezone.utc))[:10] >= LAST_END:
            continue
        sm["cat"] = category(sm["q"], sm["sports"])
        by[sm["cat"]].append(sm)
    rng = random.Random(int(d.timestamp()))
    out = []
    for cat, ms in by.items():
        rng.shuffle(ms)
        out += ms[:PER_CAT_DAY]
    return d, len(rows), {c: len(v) for c, v in by.items()}, out


def poly_trades(cid, t0, pages=6):
    """Trades in the first 48h, newest-first API paged back. complete=False when we ran out of pages first."""
    out, cur = [], None
    for _ in range(pages):
        p = {"condition_id": cid, "limit": 500}
        if cur:
            p["cursor"] = cur
        r = bot.http_json(f"{D}/v2/trades", p)
        rows = r.get("data") or [] if isinstance(r, dict) else []
        for t in rows:
            ts_ = int(t.get("timestamp") or 0)
            if t0 - 600 <= ts_ <= t0 + 2 * DAY:
                out.append([ts_, int(t.get("outcome_index") or 0), 1 if t.get("side") == "BUY" else -1,
                            round(float(t.get("price") or 0), 4), round(float(t.get("size") or 0), 2)])
        pg = r.get("pagination") or {} if isinstance(r, dict) else {}
        cur = pg.get("next_cursor")
        if not pg.get("has_more") or not cur or (rows and int(rows[-1].get("timestamp") or 0) < t0):
            return sorted(out), True
    return sorted(out), False


def poly_one(mk):
    tok = mk["toks"][0]
    t0 = mk["t0"]
    h = {}
    try:
        h["l"] = bt.squeeze(bt.hist_points(bot.http_json(f"{C}/prices-history", {"market": tok, "startTs": t0 - 600,
                                                                                    "endTs": t0 + 2 * DAY, "fidelity": 5})), 0)
        h["w"] = bt.squeeze(bt.hist_points(bot.http_json(f"{C}/prices-history", {"market": tok, "interval": "max",
                                                                                    "fidelity": 60})), 0)
    except Exception as e:
        print(f"  history failed {mk['id']}: {e}")
        return mk["id"], None
    try:
        h["tr"], h["trc"] = poly_trades(mk["cid"], t0) if mk.get("cid") else ([], False)
    except Exception as e:
        h["tr"], h["trc"] = [], False
    return mk["id"], h


def fetch_poly():
    os.makedirs(CACHE, exist_ok=True)
    have = bt.rjson(P_MK, {"days": {}, "markets": {}, "counts": {}})
    start = dt.datetime.fromisoformat(START).replace(tzinfo=dt.timezone.utc)
    last = dt.datetime.fromisoformat(LAST_END).replace(tzinfo=dt.timezone.utc) - dt.timedelta(days=1)
    days, d = [], start
    while d < last:
        if bot.iso(d)[:10] not in have["days"]:
            days.append(d)
        d += dt.timedelta(days=1)
    print(f"poly listing: {len(have['days'])} days cached, {len(days)} to read")
    with ThreadPoolExecutor(6) as ex:
        for d, n, counts, ms in ex.map(poly_day, days):
            k = bot.iso(d)[:10]
            have["days"][k] = n
            have["counts"][k] = counts
            for m in ms:
                have["markets"][m["id"]] = m
            print(f"  {k}: {n} listed, kept {len(ms)} ({time.time() - T0:.0f}s) {dict(sorted(counts.items()))}")
            if time.time() - T0 > BUDGET_MIN * 30:
                break
    bt.wjson(P_MK, have)
    hist = bt.rjson(P_H, {}) or {}
    todo = [m for m in have["markets"].values() if m["id"] not in hist]
    print(f"poly history: {len(hist)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(WORKERS) as ex:
        for c in range(0, len(todo), 1500):
            if time.time() - T0 > BUDGET_MIN * 60:
                print("  time budget used up, run again for the rest")
                break
            for mid, h in ex.map(poly_one, todo[c:c + 1500]):
                if h:
                    hist[mid] = h
            print(f"  {min(c + 1500, len(todo))}/{len(todo)} ({time.time() - T0:.0f}s)")
            bt.wjson(P_H, hist)
    bt.wjson(P_H, hist)


# ================================================================ Kalshi download

K_START = os.environ.get("LAUNCH_K_START", "2026-09-11")   # the live endpoint keeps markets settled after its cutoff
K_PER_SERIES_DAY = int(os.environ.get("LAUNCH_K_PER", "3"))


def kalshi_day(d):
    t0, t1 = int(d.timestamp()), int(d.timestamp()) + DAY
    rows, cur = [], None
    for _ in range(300):
        p = {"status": "settled", "min_close_ts": t0, "max_close_ts": t1, "limit": 1000, "mve_filter": "exclude"}
        if cur:
            p["cursor"] = cur
        try:
            r = bot.http_json(f"{K}/markets", p)
        except Exception as e:
            print(f"  kalshi {d:%Y-%m-%d} failed: {e}")
            break
        got = r.get("markets") or []
        rows += got
        cur = r.get("cursor")
        if not cur or not got:
            break
    by = defaultdict(list)
    for m in rows:
        tk = str(m.get("ticker") or "")
        if tk.startswith("KXMVE") or str(m.get("result") or "").lower() not in ("yes", "no"):
            continue
        ser = str(m.get("event_ticker") or "").split("-")[0]
        o, c = tsec(m.get("open_time")), tsec(m.get("close_time"))
        if not o or not c or c - o < 3 * 3600:
            continue
        by[ser].append({"t": tk, "s": ser, "ev": m.get("event_ticker"), "q": f"{m.get('title') or ''} {m.get('yes_sub_title') or ''}".strip(),
                        "open": o, "close": c, "res": str(m.get("result")).lower(),
                        "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0)})
    rng = random.Random(t0)
    out = []
    for ser, ms in by.items():
        evs = defaultdict(list)
        for m in ms:
            evs[m["ev"]].append(m)
        picks = [rng.choice(v) for v in evs.values()]   # one market per event, events capped per series
        rng.shuffle(picks)
        for m in picks[:K_PER_SERIES_DAY]:
            m["cat"] = kcategory(ser, m["q"])
            out.append(m)
    return d, len(rows), out


def kcandle(c):
    def px(block):
        v = (c.get(block) or {}).get("close_dollars")
        return None if v in (None, "") else round(float(v), 4)
    return [int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask"), round(bot.fnum(c.get("volume_fp"), 0), 2)]


def kalshi_one(m):
    o = m["open"]
    out = {}
    try:
        for key, a, b, per in (("l", o, min(m["close"], o + 6 * 3600), 1), ("w", o, m["close"], 60)):
            r = bot.http_json(f"{K}/series/{m['s']}/markets/{m['t']}/candlesticks", {"start_ts": a, "end_ts": b, "period_interval": per})
            out[key] = [kcandle(c) for c in (r.get("candlesticks") or [])]
    except Exception as e:
        return m["t"], None
    return m["t"], out


def fetch_kalshi():
    os.makedirs(CACHE, exist_ok=True)
    have = bt.rjson(K_MK, {"days": {}, "markets": {}})
    start = dt.datetime.fromisoformat(K_START).replace(tzinfo=dt.timezone.utc)
    last = dt.datetime.fromisoformat(LAST_END).replace(tzinfo=dt.timezone.utc) - dt.timedelta(days=1)
    days, d = [], start
    while d < last:
        if bot.iso(d)[:10] not in have["days"]:
            days.append(d)
        d += dt.timedelta(days=1)
    print(f"kalshi listing: {len(days)} days to read")
    with ThreadPoolExecutor(3) as ex:
        for d, n, ms in ex.map(kalshi_day, days):
            have["days"][bot.iso(d)[:10]] = n
            for m in ms:
                have["markets"][m["t"]] = m
            print(f"  {d:%Y-%m-%d}: {n} settled, kept {len(ms)} ({time.time() - T0:.0f}s)")
    bt.wjson(K_MK, have)
    hist = bt.rjson(K_H, {}) or {}
    todo = [m for m in have["markets"].values() if m["t"] not in hist]
    print(f"kalshi candles: {len(hist)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(4) as ex:
        for c in range(0, len(todo), 1000):
            if time.time() - T0 > BUDGET_MIN * 60:
                print("  time budget used up")
                break
            for t, h in ex.map(kalshi_one, todo[c:c + 1000]):
                if h:
                    hist[t] = h
            print(f"  {min(c + 1000, len(todo))}/{len(todo)} ({time.time() - T0:.0f}s)")
            bt.wjson(K_H, hist)
    bt.wjson(K_H, hist)


# ================================================================ analysis

AGES = (("10 min", 600), ("1 hour", 3600), ("6 hours", 6 * 3600))
BANDS = ((0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98))
SLIP, SLIP_HARD = 0.02, 0.05
SEASON_AGE = DAY            # "seasoned" twins: the same kind of market, at least a day old
MIN_EV = 30
DISC_T, ALPHA = 2.0, 0.10


def band_of(q):
    for i, (a, b) in enumerate(BANDS):
        if a <= q < b:
            return i
    return None


def bname(i):
    a, b = BANDS[i]
    return f"{a * 100:.0f}-{b * 100:.0f}c"


def dte_bucket(secs):
    d = secs / DAY
    return 0 if d < 1 else 1 if d < 3 else 2 if d < 14 else 3


def price_at(T, P, t, stale=2 * 3600):
    import bisect
    k = bisect.bisect_right(T, t) - 1
    if k < 0 or t - T[k] > stale:
        return None
    return P[k]


def poly_rows():
    """Launch rows and seasoned rows. Row: (venue, cat, label, side, q_entry_mid, pay, fee_rate, t, ev, dte, kind)."""
    mk = bt.rjson(P_MK, {}).get("markets", {})
    hist = bt.rjson(P_H, {}) or {}
    L, S, info = [], [], defaultdict(lambda: defaultdict(float))
    rng = random.Random(7)
    for mid, m in mk.items():
        h = hist.get(mid)
        pay0 = bt.payout(m, 0)
        if not h or pay0 not in (0.0, 1.0):
            continue
        cat, t0 = m["cat"], m["t0"]
        stop = min(m["end"], m.get("closed_t") or m["end"]) - 3600
        T, P = h["l"]
        tr = h.get("tr") or []
        I = info[cat]
        I["markets"] += 1
        I["traded_1h"] += 1 if any(t <= t0 + 3600 for t, *_ in tr) else 0
        I["traded_48h"] += 1 if tr else 0
        p10 = price_at(T, P, t0 + 600)
        p24 = price_at(T, P, t0 + DAY, 6 * 3600) or price_at(*h["w"], t0 + DAY, 6 * 3600) if h.get("w") else None
        if p10 is not None and abs(p10 - 0.5) <= 0.015:
            I["at50_10m"] += 1
        if p10 is not None and p24 is not None and t0 + DAY < stop:
            I["n_move"] += 1
            I["abs_move"] += abs(p24 - p10)
            I["brier10"] += (pay0 - p10) ** 2
            I["brier24"] += (pay0 - p24) ** 2
        for lab, a in AGES:
            t = t0 + a
            if t >= stop:
                continue
            p = price_at(T, P, t)
            if p is None or not 0.01 < p < 0.99:
                continue
            real = any(t0 - 600 <= x[0] <= t + 3600 for x in tr)   # someone traded by then: the price was a real book
            if not real:
                continue
            p_prev = price_at(T, P, t0 + 300) if a > 600 else None
            at50 = abs(p - 0.5) <= 0.015 and (p_prev is None or abs(p_prev - 0.5) <= 0.015)
            for side in (0, 1):
                q = p if side == 0 else 1 - p
                pay = pay0 if side == 0 else 1 - pay0
                L.append(("poly", cat, lab, side, q, pay, m["fee"], t, m.get("ev") or mid, dte_bucket(m["end"] - t), at50))
        W = h.get("w") or [[], []]
        pts = [k for k, t in enumerate(W[0]) if t >= t0 + SEASON_AGE and t < stop]
        for k in rng.sample(pts, min(3, len(pts))):
            p, t = W[1][k], W[0][k]
            if not 0.01 < p < 0.99:
                continue
            for side in (0, 1):
                q = p if side == 0 else 1 - p
                pay = pay0 if side == 0 else 1 - pay0
                S.append(("poly", cat, "seasoned", side, q, pay, m["fee"], t, m.get("ev") or mid, dte_bucket(m["end"] - t), False))
    return L, S, info


def kalshi_rows():
    mk = bt.rjson(K_MK, {}).get("markets", {})
    hist = bt.rjson(K_H, {}) or {}
    L, S, info = [], [], defaultdict(lambda: defaultdict(float))
    rng = random.Random(8)
    for tk, m in mk.items():
        h = hist.get(tk)
        if not h:
            continue
        pay0 = 1.0 if m["res"] == "yes" else 0.0
        cat, t0, stop = m["cat"], m["open"], m["close"] - 3600
        I = info[cat]
        I["markets"] += 1
        C = h.get("l") or []
        Ct = [c[0] for c in C]

        def quote(Cs, Cts, t):
            import bisect
            k = bisect.bisect_right(Cts, t) - 1
            if k < 0:
                return None
            b, a = Cs[k][1], Cs[k][2]
            if b is None or a is None or b <= 0 or a >= 1 or a <= b:
                return None
            return b, a
        q10 = quote(C, Ct, t0 + 600)
        I["two_sided_10m"] += 1 if q10 else 0
        if q10:
            I["spread10"] += q10[1] - q10[0]
            I["n_spread10"] += 1
        W = h.get("w") or []
        Wt = [c[0] for c in W]
        q24 = quote(W, Wt, t0 + DAY)
        if q10 and q24 and t0 + DAY < stop:
            m10, m24 = sum(q10) / 2, sum(q24) / 2
            I["n_move"] += 1
            I["abs_move"] += abs(m24 - m10)
            I["brier10"] += (pay0 - m10) ** 2
            I["brier24"] += (pay0 - m24) ** 2
        for lab, a in AGES:
            t = t0 + a
            if t >= stop:
                continue
            qa = quote(C, Ct, t) if a <= 6 * 3600 else None
            if not qa:
                continue
            b, ask = qa
            for side in (0, 1):
                q = ask if side == 0 else 1 - b        # real buy price: the ask (Kalshi lists bids only: NO ask = 1 - YES bid)
                pay = pay0 if side == 0 else 1 - pay0
                L.append(("kalshi", cat, lab, side, q, pay, "k", t, m["ev"], dte_bucket(m["close"] - t), False))
        pts = [k for k, t in enumerate(Wt) if t >= t0 + SEASON_AGE and t < stop]
        for k in rng.sample(pts, min(3, len(pts))):
            qa = quote(W, Wt, Wt[k])
            if not qa:
                continue
            b, ask = qa
            for side in (0, 1):
                q = ask if side == 0 else 1 - b
                pay = pay0 if side == 0 else 1 - pay0
                S.append(("kalshi", cat, "seasoned", side, q, pay, "k", Wt[k], m["ev"], dte_bucket(m["close"] - Wt[k]), False))
    return L, S, info


def ret(row, slip):
    """(profit, stake) for one share. Poly: mid + slip + fee. Kalshi: the real ask + (slip - 2c) + fee."""
    v, cat, lab, side, q, pay, fee, t, ev, dte, at50 = row
    e = min(0.99, q + (slip if v == "poly" else max(0.0, slip - SLIP)))
    f = 0.07 * e * (1 - e) if fee == "k" else fee * e * (1 - e)
    return pay - e - f, e + f


def twin_rates(S):
    """Return per $1 staked of seasoned bets, by (venue, cat, side, band, dte), at +2c. Falls back to (venue, side, band, dte)."""
    acc, acc2 = defaultdict(lambda: [0.0, 0.0]), defaultdict(lambda: [0.0, 0.0])
    for r in S:
        b = band_of(r[4])
        if b is None:
            continue
        p, s = ret(r, SLIP)
        for a, k in ((acc, (r[0], r[1], r[3], b, r[9])), (acc2, (r[0], r[3], b, r[9]))):
            a[k][0] += p
            a[k][1] += s
    out = {}
    for k, (p, s) in acc.items():
        if s >= 20:
            out[k] = p / s
    for k, (p, s) in acc2.items():
        out[("*",) + k] = p / s if s else 0.0
    return out


def twin_of(rates, r, b):
    return rates.get((r[0], r[1], r[3], b, r[9]), rates.get(("*", r[0], r[3], b, r[9]), 0.0))


def cells(L, rates, split):
    """Per cell: per half, per event sums of (profit2, stake, excess, profit5)."""
    acc = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0]))
    for r in L:
        b = band_of(r[4])
        if b is None:
            continue
        p2, s = ret(r, SLIP)
        p5, s5 = ret(r, SLIP_HARD)
        x = p2 - twin_of(rates, r, b) * s
        half = "A" if r[7] < split else "B"
        keys = [(r[0], r[1], r[2], r[3], b), (r[0], "ALL", r[2], r[3], b)]
        if r[10]:
            keys += [(r[0], r[1], r[2] + " still at 50c", r[3], -1), (r[0], "ALL", r[2] + " still at 50c", r[3], -1)]
        for k in keys:
            e = acc[(half,) + k][r[8]]
            e[0] += p2
            e[1] += s
            e[2] += x
            e[3] += p5 * s / s5 if s5 else 0
            e[4] += 1
    return acc


def cstat(evs):
    """Events as units: mean excess per $1, its t, return +2c, +5c."""
    if not evs or len(evs) < 2:
        return None
    rows = list(evs.values())
    n = len(rows)
    S = sum(e[1] for e in rows)
    xs = [e[2] / e[1] for e in rows if e[1] > 0]
    mx = sum(e[2] for e in rows) / S
    var = sum((e[2] - mx * e[1]) ** 2 for e in rows) / (S * S) * n / max(1, n - 1)
    se = math.sqrt(var) or 1e-9
    r2 = sum(e[0] for e in rows) / S
    var2 = sum((e[0] - r2 * e[1]) ** 2 for e in rows) / (S * S) * n / max(1, n - 1)
    return {"n": n, "x": mx, "t": mx / se, "r2": r2, "lo2": r2 - 1.645 * math.sqrt(var2), "r5": sum(e[3] for e in rows) / S,
            "bets": sum(e[4] for e in rows)}


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def select(acc):
    keys = {k[1:] for k in acc}
    out, info = {}, {"cells": len(keys)}
    for disc, conf in (("A", "B"), ("B", "A")):
        cand = [k for k in keys if (lambda s: s and s["n"] >= MIN_EV and s["t"] >= DISC_T)(cstat(acc.get((disc,) + k)))]
        K = max(1, len(cand))
        info[f"cand_{disc}"] = len(cand)
        for k in cand:
            s, sd = cstat(acc.get((conf,) + k)), cstat(acc.get((disc,) + k))
            if s and s["n"] >= MIN_EV and norm_sf(s["t"]) < ALPHA / K and s["r2"] > 0 and sd["r2"] > 0:
                out.setdefault(k, []).append(disc)
    return out, info


def m100(x):
    return f"{'+' if x >= 0 else '-'}${abs(x) * 100:.2f}"


def describe(k):
    v, cat, lab, side, b = k
    sd = "Yes" if side == 0 else "No"
    return f"{v} {cat}, {lab} after launch, buy {sd}" + (f" at {bname(b)}" if b >= 0 else " (price still at 50c)")


def run(out_name="launch.md"):
    L, S, info, split = [], [], {}, None
    for name, fn in (("poly", poly_rows), ("kalshi", kalshi_rows)):
        try:
            l, s, i = fn()
        except Exception as e:
            print(f"{name} rows failed: {e}")
            continue
        L += l
        S += s
        info[name] = i
        print(f"{name}: {len(l)} launch bets, {len(s)} seasoned bets, {sum(int(v['markets']) for v in i.values())} markets")
    if not L:
        print("no data")
        return
    rates = twin_rates(S)
    accs, sels = {}, {}
    for v in ("poly", "kalshi"):
        Lv = [r for r in L if r[0] == v]
        if not Lv:
            continue
        split = sorted(r[7] for r in Lv)[len(Lv) // 2]
        accs[v] = cells(Lv, rates, split)
        sels[v] = select(accs[v])
    W = ["# Brand-new markets: are they mispriced in their first hours?", "",
         f"Made by `launch.py run` (probe `btlaunchrun`) on {bot.iso()[:16]}Z. Paper research only.", "",
         "How it works: markets are sampled by the day they **started** (no volume floor, so small markets that died "
         "quiet are in, unlike bt_cache). For each market we look at the price 10 minutes, 1 hour and 6 hours after "
         "launch, and buy one side, held to the end. Polymarket: history price + 2c + fee, and only if someone had "
         "already traded the market by then (so the price was a real book, not the empty 50c placeholder). "
         "Kalshi: the real ask from the minute candles + fee. Each bet is compared with **seasoned twins**: bets on the "
         "same kind of market, same side, same price band, same time left, but at least one day old. Events count once. "
         "Discovery on one half (by date), confirm on the other, both ways, corrected for the number of tries.", ""]
    for v, I in info.items():
        W += [f"## {v.title()}: what launch looks like", "",
              "| Kind | Markets | Traded in 1st hour | Still at 50c after 10 min | Avg move launch -> 24h | Error at launch | Error at 24h |"
              if v == "poly" else
              "| Kind | Markets | Real two-sided quote after 10 min | Avg gap bid/ask after 10 min | Avg move launch -> 24h | Error at launch | Error at 24h |",
              "|---|---|---|---|---|---|---|"]
        for cat, x in sorted(I.items(), key=lambda kv: -kv[1]["markets"]):
            n = x["markets"] or 1
            nm = x["n_move"] or 0
            mv_ = f"{100 * x['abs_move'] / nm:.1f}c" if nm else "-"
            b10 = f"{x['brier10'] / nm:.3f}" if nm else "-"
            b24 = f"{x['brier24'] / nm:.3f}" if nm else "-"
            if v == "poly":
                W.append(f"| {cat} | {int(x['markets'])} | {x['traded_1h'] / n * 100:.0f} in 100 | {x['at50_10m'] / n * 100:.0f} in 100 | {mv_} | {b10} | {b24} |")
            else:
                sp = f"{100 * x['spread10'] / x['n_spread10']:.1f}c" if x["n_spread10"] else "-"
                W.append(f"| {cat} | {int(x['markets'])} | {x['two_sided_10m'] / n * 100:.0f} in 100 | {sp} | {mv_} | {b10} | {b24} |")
        W += ["", "Error = average squared miss of the price vs the result (0 = perfect, 0.25 = coin flip). It always "
              "shrinks with time because news arrives; a launch edge needs launch prices that are wrong in a direction "
              "you can bet on, which the tables below test.", ""]
    for v, acc in accs.items():
        out, si = sels[v]
        W += [f"## {v.title()}: which launch bets beat their seasoned twins", "",
              f"{si['cells']} cells tried (kind x launch age x side x price band, plus 'still at 50c'). "
              f"Candidates: {si['cand_A']} on the first half, {si['cand_B']} on the second. **Survivors: {len(out)}.**", ""]
        rows = []
        for k in {kk[1:] for kk in acc}:
            a, b = cstat(acc.get(("A",) + k)), cstat(acc.get(("B",) + k))
            if a and b and a["n"] >= MIN_EV and b["n"] >= MIN_EV:
                rows.append((min(a["t"], b["t"]), k, a, b))
        rows.sort(key=lambda r: -r[0])
        W += ["Top 25 by the weaker half (per $100 staked):", "",
              "| Bet | Events A / B | vs twins A / B | +2c A / B | +5c A / B | Survived |", "|---|---|---|---|---|---|"]
        for _, k, a, b in rows[:25]:
            W.append(f"| {describe(k)} | {a['n']} / {b['n']} | {m100(a['x'])} / {m100(b['x'])} | {m100(a['r2'])} / {m100(b['r2'])} | "
                     f"{m100(a['r5'])} / {m100(b['r5'])} | {'yes' if k in out else ''} |")
        W += ["", "All launch bets together, by kind (both halves, +2c):", "",
              "| Kind | Launch age | Side | Events | Per $100 | vs twins |", "|---|---|---|---|---|---|"]
        tot = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0]))
        for (half, vv, cat, lab, side, b), evs in acc.items():
            if b == -1 or "50c" in lab:
                continue
            for ev, e in evs.items():
                t = tot[(cat, lab, side)][ev]
                for i in range(5):
                    t[i] += e[i]
        for (cat, lab, side), evs in sorted(tot.items()):
            s = cstat(evs)
            if s and s["n"] >= MIN_EV and lab == "1 hour":
                W.append(f"| {cat} | {lab} | {'Yes' if side == 0 else 'No'} | {s['n']} | {m100(s['r2'])} | {m100(s['x'])} |")
        W.append("")
        # still at 50c
        W += ["Still sitting at the 50c opening price (nobody has moved it yet):", "",
              "| Kind | Age | Side | Events | Per $100 at +2c | +5c |", "|---|---|---|---|---|---|"]
        for (half, vv, cat, lab, side, b) in sorted({k for k in acc if k[5] == -1 and k[0] == "A"}):
            evs = dict(acc.get(("A", vv, cat, lab, side, b), {}))
            for ev, e in acc.get(("B", vv, cat, lab, side, b), {}).items():
                evs[ev] = e
            s = cstat(evs)
            if s and s["n"] >= 20:
                W.append(f"| {cat} | {lab} | {'Yes' if side == 0 else 'No'} | {s['n']} | {m100(s['r2'])} | {m100(s['r5'])} |")
        W.append("")
    txt = "\n".join(W) + "\n"
    os.makedirs(bt.OUT, exist_ok=True)
    with open(os.path.join(bt.OUT, out_name), "w") as fh:
        fh.write(txt)
    print(txt)



def selftest():
    """Offline: fake markets priced right, plus one planted launch edge. The edge must survive, nothing else."""
    import tempfile
    global P_MK, P_H, K_MK, K_H
    tmp = tempfile.mkdtemp()
    P_MK, P_H = os.path.join(tmp, "pm.json.gz"), os.path.join(tmp, "ph.json.gz")
    K_MK, K_H = os.path.join(tmp, "km.json.gz"), os.path.join(tmp, "kh.json.gz")
    rng = random.Random(1)
    mk, hist = {}, {}
    base = 1780000000
    for i in range(12000):
        cat = rng.choice(["sports", "weather", "other (one-off questions)", "planted"])
        t0 = base + i * 1800
        life = rng.choice([2, 5, 20]) * DAY
        truth = rng.uniform(0.05, 0.95)
        y = 1.0 if rng.random() < truth else 0.0
        p_launch = truth
        if cat == "planted":            # launch price is 15c too low; fixed within a day
            p_launch = max(0.03, truth - 0.15)
        T = [t0 + k * 300 for k in range(0, 576)]
        P = [round(p_launch if t < t0 + 12 * 3600 else truth, 3) for t in T]
        WT = [t0 + k * 3600 for k in range(0, int(life // 3600))]
        WP = [round(p_launch if t < t0 + 12 * 3600 else truth, 3) for t in WT]   # a fair price after the first day
        mid = str(i)
        mk[mid] = {"id": mid, "q": "x", "cat": cat, "t0": t0, "start": t0, "end": t0 + life, "closed": True,
                   "closed_t": t0 + life, "final": [y, 1 - y], "uma": "resolved", "fee": 0.0, "ev": mid}
        hist[mid] = {"l": [T, P], "w": [WT, WP], "tr": [[t0 + 60, 0, 1, p_launch, 5]], "trc": True}
    bt.wjson(P_MK, {"markets": mk})
    bt.wjson(P_H, hist)
    bt.wjson(K_MK, {"markets": {}})
    bt.wjson(K_H, {})
    run(out_name="launch_selftest.md")
    txt = open(os.path.join(bt.OUT, "launch_selftest.md")).read()
    surv = [l for l in txt.splitlines() if l.endswith("| yes |")]
    print("\nsurvivor lines:", len(surv))
    bad = [l for l in surv if "planted" not in l and "ALL" not in l]
    good = [l for l in surv if "planted" in l and "buy Yes" in l]
    assert good, "planted edge not found"
    assert not bad, f"noise survived: {bad[:3]}"
    os.remove(os.path.join(bt.OUT, "launch_selftest.md"))
    print("selftest OK")



# ================================================================ live: watch brand-new listings (the "fast bot" check)

LIVE_AGES_MIN = (1, 3, 5, 10, 20, 30, 60, 90, 120)


def walk_cost(asks, dollars):
    """Average price paid per share to spend `dollars` walking the asks [(p, size)], or None if the book is too thin."""
    left, sh, spent = dollars, 0.0, 0.0
    for p, sz in asks:
        take = min(sz, left / p) if p > 0 else 0
        sh += take
        spent += take * p
        left -= take * p
        if left <= 1e-6:
            return spent / sh
    return None


def poly_book(tok):
    b = bot.http_json(f"{C}/book", {"token_id": tok})
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids") or []), reverse=True)
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks") or [])
    return bids, asks


def snap_poly(m):
    bids, asks = poly_book(m["tok"])
    no_asks = sorted((round(1 - p, 4), s) for p, s in bids)          # one mirrored book: NO ask = 1 - YES bid
    bb, ba = (bids[0][0] if bids else None), (asks[0][0] if asks else None)
    return {"bb": bb, "ba": ba, "y10": walk_cost(asks, 10), "y25": walk_cost(asks, 25), "n10": walk_cost(no_asks, 10),
            "n25": walk_cost(no_asks, 25), "depth5": round(sum(s * p for p, s in asks if ba and p <= ba + 0.05), 2)}


def snap_kalshi(m):
    r = bot.kalshi_asks(m["tok"])
    if r is None:
        return None
    ya, na = r
    ba = ya[0][0] if ya else None
    bb = round(1 - na[0][0], 4) if na else None
    return {"bb": bb, "ba": ba, "y10": walk_cost(ya, 10), "y25": walk_cost(ya, 25), "n10": walk_cost(na, 10),
            "n25": walk_cost(na, 25), "depth5": round(sum(s * p for p, s in ya if ba and p <= ba + 0.05), 2)}


def new_poly(seen, now_t):
    rows = bot.envelope_rows(bot.http_json(f"{G}/markets", {"limit": 200, "order": "createdAt", "ascending": "false",
                                                          "closed": "false"}), "markets", "data")
    out = []
    for m in rows:
        mid = str(m.get("id"))
        c = tsec(m.get("createdAt"))
        if mid in seen or not c or now_t - c > 900:
            continue
        seen.add(mid)
        toks = bot.market_tokens(m)
        if len(toks) != 2:
            continue
        out.append({"v": "poly", "id": mid, "tok": toks[0], "q": str(m.get("question") or ""), "born": c,
                    "cat": category(str(m.get("question") or ""), bot.is_sports(m)), "end": tsec(m.get("endDate")), "snaps": {}})
    return out


_KNEW = [None]


def new_kalshi(seen, now_t):
    if _KNEW[0] is False:
        return []
    try:
        r = bot.http_json(f"{K}/markets", {"status": "open", "min_created_ts": now_t - 900, "limit": 1000, "mve_filter": "exclude"})
        _KNEW[0] = True
    except Exception as e:
        print(f"kalshi new-market list failed ({e}); Kalshi left out")
        _KNEW[0] = False
        return []
    out = []
    for m in r.get("markets") or []:
        tk = str(m.get("ticker") or "")
        c = tsec(m.get("created_time")) or tsec(m.get("open_time"))
        if tk in seen or not c or now_t - c > 900 or tk.startswith("KXMVE"):
            continue
        seen.add(tk)
        ser = str(m.get("event_ticker") or "").split("-")[0]
        out.append({"v": "kalshi", "id": tk, "tok": tk, "q": f"{m.get('title') or ''} {m.get('yes_sub_title') or ''}".strip(),
                    "born": c, "cat": kcategory(ser, str(m.get("title") or "")), "end": tsec(m.get("close_time")), "snaps": {}})
    return out


def live(minutes=120, follow=120, cap_per_cat=40):
    """Spot new listings every minute for `minutes`, then keep snapping each one's book until it is `follow` minutes old.
    Writes backtest/launch_live.md and launch_live.json (records only, never trades)."""
    minutes, follow = int(minutes), int(follow)
    t_end_new, seen, track = time.time() + minutes * 60, set(), []
    per_cat = defaultdict(int)
    t_stop = t_end_new + follow * 60
    ex = ThreadPoolExecutor(8)
    while time.time() < t_stop:
        t_loop = time.time()
        now_t = int(t_loop)
        if t_loop < t_end_new:
            got = []
            for fn in (new_poly, new_kalshi):
                try:
                    got += fn(seen, now_t)
                except Exception as e:
                    print(f"listing failed: {e}")
            for m in got:
                key = (m["v"], m["cat"])
                if per_cat[key] < cap_per_cat:
                    per_cat[key] += 1
                    track.append(m)
        due = []
        for m in track:
            age = (now_t - m["born"]) / 60
            for a in LIVE_AGES_MIN:
                if a not in m["snaps"] and age >= a and age < a + 10:
                    due.append((m, a))
                    break
        def one(x):
            m, a = x
            try:
                return m, a, (snap_poly(m) if m["v"] == "poly" else snap_kalshi(m))
            except Exception as e:
                return m, a, {"err": str(e)[:80]}
        for m, a, sn in ex.map(one, due):
            m["snaps"][a] = sn
        if int(t_loop) % 600 < 60:
            print(f"{bot.iso()[:16]} tracking {len(track)} ({dict(per_cat)}), {len(due)} snaps this minute")
        time.sleep(max(1, 60 - (time.time() - t_loop)))
    with open(os.path.join(bt.OUT, "launch_live.json"), "w") as fh:
        json.dump(track, fh)
    live_report(track)


def live_report(track):
    import statistics as st
    W = ["# Brand-new listings, watched live", "", f"`launch.py live` on {bot.iso()[:16]}Z: every new market spotted within "
         "a minute or two, then its order book checked at set ages. Cost = cents per share paid above the middle of the "
         "book when buying $10 or $25 of the cheaper side by walking the asks. Records only.", ""]
    for v in ("poly", "kalshi"):
        ms = [m for m in track if m["v"] == v]
        if not ms:
            continue
        W += [f"## {v.title()} ({len(ms)} new markets)", "",
              "| Kind | Age | Markets checked | Any seller at all | Both sides quoted | Gap bid/ask (median) | Extra cost $10 | Extra cost $25 | $ on sale within 5c of best |",
              "|---|---|---|---|---|---|---|---|---|"]
        for cat in sorted({m["cat"] for m in ms}):
            for a in LIVE_AGES_MIN:
                sn = [m["snaps"].get(a) or m["snaps"].get(str(a)) for m in ms if m["cat"] == cat]
                sn = [x for x in sn if x and "err" not in x]
                if len(sn) < 3:
                    continue
                anyask = sum(1 for x in sn if x["ba"] is not None)
                two = [x for x in sn if x["ba"] is not None and x["bb"] is not None]
                gaps = [x["ba"] - x["bb"] for x in two]
                c10, c25 = [], []
                for x in two:
                    mid = (x["ba"] + x["bb"]) / 2
                    cheap_yes = mid <= 0.5
                    for lst, ky, kn in ((c10, "y10", "n10"), (c25, "y25", "n25")):
                        cost = x[ky] if cheap_yes else x[kn]
                        ref = mid if cheap_yes else 1 - mid
                        lst.append(None if cost is None else cost - ref)
                f10 = [c for c in c10 if c is not None]
                f25 = [c for c in c25 if c is not None]
                dep = [x["depth5"] for x in two]
                W.append(f"| {cat} | {a} min | {len(sn)} | {anyask * 100 // len(sn)} in 100 | {len(two) * 100 // len(sn)} in 100 | "
                         f"{(f'{100 * st.median(gaps):.1f}c' if gaps else '-')} | "
                         f"{(f'{100 * st.median(f10):.1f}c' if f10 else '-')} ({len(c10) - len(f10)} too thin) | "
                         f"{(f'{100 * st.median(f25):.1f}c' if f25 else '-')} ({len(c25) - len(f25)} too thin) | "
                         f"{(f'${st.median(dep):.0f}' if dep else '-')} |")
        # how much the middle moves after the first two-sided quote
        W += ["", "How far the middle price moved from the first two-sided quote to 2 hours old (median, by kind):", ""]
        for cat in sorted({m["cat"] for m in ms}):
            mv = []
            for m in ms:
                if m["cat"] != cat:
                    continue
                q = [(a, m["snaps"].get(a) or m["snaps"].get(str(a))) for a in LIVE_AGES_MIN]
                q = [(a, x) for a, x in q if x and "err" not in x and x.get("ba") is not None and x.get("bb") is not None]
                if len(q) >= 2 and q[-1][0] >= 60:
                    f, l = q[0][1], q[-1][1]
                    mv.append(abs((l["ba"] + l["bb"]) / 2 - (f["ba"] + f["bb"]) / 2))
            if len(mv) >= 3:
                W.append(f"- {cat}: {100 * st.median(mv):.1f}c (n={len(mv)}, a quarter moved {100 * sorted(mv)[3 * len(mv) // 4]:.1f}c or more)")
        W.append("")
    txt = "\n".join(W) + "\n"
    with open(os.path.join(bt.OUT, "launch_live.md"), "w") as fh:
        fh.write(txt)
    print(txt)


CMDS = {"peek": peek, "peek2": peek2, "fetchpoly": fetch_poly, "fetchkalshi": fetch_kalshi,
        "fetch": lambda: (fetch_kalshi(), fetch_poly()), "run": run, "selftest": selftest,
        "live": lambda: live(*(sys.argv[2:4] or [120, 120])),
        "all": lambda: (fetch_kalshi(), fetch_poly(), run())}

if __name__ == "__main__":
    CMDS[sys.argv[1] if len(sys.argv) > 1 else "run"]()
