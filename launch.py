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


CMDS = {"peek": peek, "peek2": peek2, "fetchpoly": fetch_poly, "fetchkalshi": fetch_kalshi,
        "fetch": lambda: (fetch_kalshi(), fetch_poly())}

if __name__ == "__main__":
    CMDS[sys.argv[1] if len(sys.argv) > 1 else "run"]()
