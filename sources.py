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


if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "map")
    {"map": mapping}[mode]()
