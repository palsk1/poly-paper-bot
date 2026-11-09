#!/usr/bin/env python3
"""Launch test (2026-11-09): are brand-new markets mispriced in their first hours?

PAPER ONLY. Reads public history, never trades.

    python3 launch.py peek      # API shapes for new-listing data (probe: btlaunchpeek)
"""
import datetime as dt
import json
import sys
import time

import bot

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


if __name__ == "__main__":
    {"peek": peek}[sys.argv[1] if len(sys.argv) > 1 else "peek"]()
