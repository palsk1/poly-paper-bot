#!/usr/bin/env python3
"""Who reads the source first? Research only, no state changes, no trades.

Modes (probe input src_<mode>):
  map    every open Polymarket event and Kalshi series, grouped by the website/data feed
         its rules settle on, with money traded and how soon they end.
"""
import collections
import json
import re
import sys
import time
import urllib.parse
import urllib.request

import bot

GAMMA = bot.GAMMA
KAL = "https://api.elections.kalshi.com/trade-api/v2"
URL_RE = re.compile(r"https?://(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})(/[^\s\"'<>)\]]*)?", re.I)
SKIP_DOMAINS = {"polymarket.com", "kalshi.com", "docs.polymarket.com", "x.com/polymarket"}


def f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def domains(text):
    out = []
    for m in URL_RE.finditer(text or ""):
        d = m.group(1).lower()
        if d.endswith("polymarket.com") or d.endswith("kalshi.com"):
            continue
        out.append(d)
    return out


def poly_events(pages=200):
    evs, cursor = [], None
    for page in range(pages):
        params = {"closed": "false", "limit": 100}
        if cursor:
            params["after_cursor"] = cursor
        try:
            res = bot.http_json(f"{GAMMA}/events/keyset", params)
        except Exception as e:
            print("poly page", page, "failed:", e)
            break
        rows = bot.envelope_rows(res, "events", "data")
        evs += [e for e in rows if isinstance(e, dict)]
        cursor = res.get("next_cursor") if isinstance(res, dict) else None
        if not cursor or not rows:
            break
    return evs


def kalshi_series():
    try:
        res = bot.http_json(f"{KAL}/series", {"include_volume": "true"})
    except Exception as e:
        print("kalshi series failed:", e)
        return []
    return res.get("series") or []


def kalshi_events(pages=60):
    evs, cursor = [], None
    for page in range(pages):
        params = {"status": "open", "limit": 200, "with_nested_markets": "true"}
        if cursor:
            params["cursor"] = cursor
        try:
            res = bot.http_json(f"{KAL}/events", params)
        except Exception as e:
            print("kalshi events page", page, "failed:", e)
            break
        rows = res.get("events") or []
        evs += rows
        cursor = res.get("cursor")
        if not cursor or not rows:
            break
    return evs


def mapping():
    now = bot.now()
    # ---- Polymarket
    evs = poly_events()
    print(f"polymarket: {len(evs)} open events")
    agg = collections.defaultdict(lambda: {"n": 0, "vol24": 0.0, "liq": 0.0, "soon": 0, "ex": []})
    for e in evs:
        ms = [m for m in (e.get("markets") or []) if isinstance(m, dict)]
        text = " ".join([str(e.get("resolutionSource") or ""), str(e.get("description") or "")]
                        + [str(m.get("resolutionSource") or "") + " " + str(m.get("description") or "") for m in ms[:3]])
        ds = domains(text)
        key = collections.Counter(ds).most_common(1)[0][0] if ds else "(no link: news/consensus)"
        a = agg[key]
        a["n"] += 1
        a["vol24"] += f(e.get("volume24hr"))
        a["liq"] += f(e.get("liquidity"))
        end = bot.parse_iso(e.get("endDate"))
        if end and (end - now).total_seconds() < 3 * 86400:
            a["soon"] += 1
        if len(a["ex"]) < 3:
            a["ex"].append(str(e.get("title"))[:70])
    print("\n== POLYMARKET by settle source (top 70 by money traded in 24h)")
    print(f"{'source':38s} {'events':>6s} {'end<3d':>6s} {'vol24h$':>10s} {'liq$':>10s}  examples")
    for k, a in sorted(agg.items(), key=lambda kv: -kv[1]["vol24"])[:70]:
        print(f"{k[:38]:38s} {a['n']:6d} {a['soon']:6d} {a['vol24']:10.0f} {a['liq']:10.0f}  {' | '.join(a['ex'])}")

    # ---- Kalshi
    ser = kalshi_series()
    print(f"\nkalshi: {len(ser)} series")
    src = {}
    for s in ser:
        names = [(x.get("name") or "") + " " + (x.get("url") or "") for x in (s.get("settlement_sources") or [])]
        ds = domains(" ".join(names)) or [x.strip().lower() for x in names if x.strip()]
        src[s.get("ticker")] = (ds[0] if ds else "(none listed)", s.get("title"), s.get("category"), s.get("frequency"))
    kev = kalshi_events()
    print(f"kalshi: {len(kev)} open events")
    kagg = collections.defaultdict(lambda: {"n": 0, "vol24": 0.0, "oi": 0.0, "soon": 0, "ex": set(), "freq": collections.Counter()})
    for e in kev:
        s = src.get(e.get("series_ticker"), ("(unknown series)", None, None, None))
        a = kagg[s[0]]
        a["n"] += 1
        for m in e.get("markets") or []:
            a["vol24"] += f(m.get("volume_24h_fp") or m.get("volume_24h")) * f(m.get("last_price_dollars") or 0.5, 0.5)
            a["oi"] += f(m.get("open_interest_fp") or m.get("open_interest"))
        ct = bot.parse_iso((e.get("markets") or [{}])[0].get("close_time")) if e.get("markets") else None
        if ct and (ct - now).total_seconds() < 3 * 86400:
            a["soon"] += 1
        if len(a["ex"]) < 4:
            a["ex"].add(f"{e.get('series_ticker')}:{str(s[1])[:40]}")
        a["freq"][s[3]] += 1
    print("\n== KALSHI by settle source (top 70 by approx $ traded in 24h)")
    print(f"{'source':38s} {'events':>6s} {'end<3d':>6s} {'~vol24h$':>10s} {'openint':>10s}  freq | examples")
    for k, a in sorted(kagg.items(), key=lambda kv: -kv[1]["vol24"])[:70]:
        fr = ",".join(f"{x}" for x, _ in a["freq"].most_common(2))
        print(f"{str(k)[:38]:38s} {a['n']:6d} {a['soon']:6d} {a['vol24']:10.0f} {a['oi']:10.0f}  {fr} | {' | '.join(sorted(a['ex']))}")



def kdaily():
    """Kalshi series that repeat often (hourly/daily/weekly), by settle source, with lifetime volume."""
    ser = kalshi_series()
    agg = collections.defaultdict(lambda: {"vol": 0.0, "n": 0, "ex": []})
    for s in ser:
        fr = s.get("frequency")
        if fr not in ("hourly", "daily", "weekly", "fifteen_min", "15min", "minutely"):
            continue
        names = [(x.get("name") or "") + " " + (x.get("url") or "") for x in (s.get("settlement_sources") or [])]
        ds = domains(" ".join(names)) or [x.strip().lower()[:40] for x in names if x.strip()] or ["(none)"]
        k = (ds[0], fr)
        a = agg[k]
        v = f(s.get("volume_fp") or s.get("volume"))
        a["vol"] += v
        a["n"] += 1
        a["ex"].append((v, s.get("ticker"), str(s.get("title"))[:35]))
    print(f"{'source':34s} {'freq':8s} {'series':>6s} {'volume':>14s}  top series")
    for (d, fr), a in sorted(agg.items(), key=lambda kv: -kv[1]["vol"])[:80]:
        top = sorted(a["ex"], reverse=True)[:4]
        print(f"{d[:34]:34s} {str(fr):8s} {a['n']:6d} {a['vol']:14.0f}  " + " | ".join(f"{t}:{ti}({v:.0f})" for v, t, ti in top))


def precurring():
    """Polymarket events that belong to a repeating series, by series, with 24h volume and settle source."""
    evs = poly_events()
    agg = collections.defaultdict(lambda: {"n": 0, "vol24": 0.0, "src": collections.Counter(), "ex": ""})
    for e in evs:
        ss = e.get("series") or []
        if not ss:
            continue
        s = ss[0] if isinstance(ss, list) else ss
        k = (s.get("slug") or s.get("title") or "?", s.get("recurrence") or "")
        a = agg[k]
        a["n"] += 1
        a["vol24"] += f(e.get("volume24hr"))
        text = str(e.get("resolutionSource") or "") + " " + str(e.get("description") or "")
        for d in domains(text)[:1]:
            a["src"][d] += 1
        a["ex"] = a["ex"] or str(e.get("title"))[:50]
    print(f"{'series':40s} {'recur':8s} {'events':>6s} {'vol24h$':>10s}  source | example")
    for (sl, rc), a in sorted(agg.items(), key=lambda kv: -kv[1]["vol24"])[:120]:
        src = a["src"].most_common(1)[0][0] if a["src"] else "-"
        print(f"{sl[:40]:40s} {rc[:8]:8s} {a['n']:6d} {a['vol24']:10.0f}  {src} | {a['ex']}")

def kmarkets(series, status="settled", pages=10, **extra):
    out, cursor = [], None
    for _ in range(pages):
        p = {"series_ticker": series, "status": status, "limit": 1000, **extra}
        if cursor:
            p["cursor"] = cursor
        try:
            r = bot.http_json(f"{KAL}/markets", p)
        except Exception as e:
            print(" markets failed", series, e)
            break
        out += r.get("markets") or []
        cursor = r.get("cursor")
        if not cursor or not r.get("markets"):
            break
    return out


def kcandles(series, ticker, start, end, period=1):
    r = bot.http_json(f"{KAL}/series/{series}/markets/{ticker}/candlesticks",
                      {"start_ts": int(start), "end_ts": int(end), "period_interval": period})
    return r.get("candlesticks") or []


def kseries(arg):
    """Look at a few Kalshi families: rules, how many settled, settle values, volume, candle shape."""
    for s in arg.split(","):
        ms = kmarkets(s, pages=3)
        print(f"\n######## {s}: {len(ms)} settled markets (first 3000)")
        if not ms:
            continue
        m = ms[0]
        print("keys:", sorted(m.keys()))
        for k in ("ticker", "event_ticker", "title", "subtitle", "yes_sub_title", "rules_primary", "rules_secondary",
                  "open_time", "close_time", "expiration_time", "expiration_value", "result", "strike_type",
                  "floor_strike", "cap_strike", "volume_fp", "volume", "last_price_dollars"):
            print(f"  {k}: {str(m.get(k))[:700]}")
        vol = sum(f(x.get("volume_fp") or x.get("volume")) for x in ms)
        evs = collections.Counter(x.get("event_ticker") for x in ms)
        print(f"  events {len(evs)}, markets/event ~{len(ms)/max(1,len(evs)):.1f}, total contracts {vol:.0f}")
        seen = []
        for x in ms:
            if x.get("event_ticker") not in [e for e, _ in seen]:
                seen.append((x.get("event_ticker"), x.get("expiration_value")))
            if len(seen) >= 12:
                break
        print("  recent settle values:", seen)
        try:
            ct = bot.parse_iso(m.get("close_time")).timestamp()
            c = kcandles(s, m["ticker"], ct - 6 * 3600, ct, 1)
            print(f"  candles last 6h at 1-min: {len(c)}; sample: {json.dumps(c[-1])[:600] if c else None}")
        except Exception as e:
            print("  candles failed:", e)


MODES = {"map": mapping, "kdaily": kdaily, "precur": precurring}

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "map"
    if a.startswith("ks_"):
        kseries(a[3:])
    else:
        MODES[a]()
