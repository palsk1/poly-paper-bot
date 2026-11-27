#!/usr/bin/env python3
"""Who reads the source first? Research only, no state changes, no trades.

Modes (probe input src_<mode>):
  map    every open Polymarket event and Kalshi series, grouped by the website/data feed
         its rules settle on, with money traded and how soon they end.
  gasrec the recorder's live gas test: AAA + GasBuddy + Kalshi gas ladder books from the data-YYYYMMDD releases
         (gasrec_nofetch to reuse bt_cache/gasrec, add ,ledger=<path> for the exam's ledger). backtest/gasrec.md
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


# ---------------------------------------------------------------- gas: AAA daily national average (Kalshi)
def _norm_cdf(z):
    import math
    return 0.5 * (1 + math.erf(z / 2 ** 0.5))


def ladder(series, pages=5):
    """{event_date: {"v": settle value, "close": ts, "open": ts, "mk": [(ticker, strike)]}} from settled markets."""
    import kcrypto
    ev = {}
    for m in kmarkets(series, pages=pages):
        try:
            v = float(str(m.get("expiration_value")).strip("%M "))
        except ValueError:
            continue
        k = m.get("floor_strike")
        if k is None or m.get("strike_type") not in ("greater", "greater_or_equal"):
            continue
        e = ev.setdefault(m["event_ticker"], {"v": v, "close": bot.parse_iso(m["close_time"]).timestamp(),
                                              "open": bot.parse_iso(m["open_time"]).timestamp(), "mk": [],
                                              "ge": m.get("strike_type") == "greater_or_equal"})
        e["mk"].append((m["ticker"], float(k), m.get("result"), f(m.get("volume_fp"))))
    return ev


def hourly(series, e, period=60):
    import kcrypto
    tks = [t for t, *_ in e["mk"]]
    out = {}
    for i in range(0, len(tks), 50):
        try:
            res = kcrypto.get("/markets/candlesticks", {"market_tickers": ",".join(tks[i:i + 50]),
                              "start_ts": int(e["open"]), "end_ts": int(e["close"]), "period_interval": period})
        except Exception as ex:
            print("  candles failed", ex)
            continue
        rows = next((res[k] for k in ("markets", "market_candlesticks", "candlesticks", "data")
                     if isinstance(res, dict) and isinstance(res.get(k), list)), [])
        for r in rows:
            out[r.get("market_ticker") or r.get("ticker")] = [kcrypto.candle_row(c) for c in r.get("candlesticks") or []]
    return out


def gas(arg="KXAAAGASD"):
    """Is the AAA gas average more predictable than the Kalshi ladder prices it?
    Models only use settle values of EARLIER events (known before this market opened)."""
    import math
    from concurrent.futures import ThreadPoolExecutor
    series = arg or "KXAAAGASD"
    ev = ladder(series)
    keys = sorted(ev, key=lambda k: ev[k]["close"])
    print(f"{series}: {len(keys)} settled events with a ladder")
    with ThreadPoolExecutor(3) as ex:
        cand = dict(zip(keys, ex.map(lambda k: hourly(series, ev[k]), keys)))
    for k in keys[-3:]:
        c = cand[k]
        print("  debug", k, "open", ev[k]["open"], "close", ev[k]["close"], "markets", len(ev[k]["mk"]), "with candles",
              sum(1 for v in c.values() if v), "sample", (next((v for v in c.values() if v), [None]) or [None])[-3:])
    vals = [(ev[k]["close"], ev[k]["v"]) for k in keys]
    # days between settles (weekly series compare to the latest DAILY value if available)
    daily = {}
    if series != "KXAAAGASD":
        d = ladder("KXAAAGASD")
        daily = sorted((x["close"], x["v"]) for x in d.values())
    else:
        daily = vals

    def past(ts):          # daily settle values whose market closed >= 9h before ts (AAA posts in the morning)
        return [v for c, v in daily if c <= ts - 9 * 3600]

    models = {
        "same as last": lambda p: p[-1],
        "last + last change": lambda p: p[-1] + (p[-1] - p[-2]),
        "last + avg change 3d": lambda p: p[-1] + (p[-1] - p[-4]) / 3,
        "last + 0.7 x last change": lambda p: p[-1] + 0.7 * (p[-1] - p[-2]),
    }
    hrs = (14, 16, 18, 20, 22, 2)          # UTC decision hours (day before; 2 = 2am UTC, 9pm ET)
    acc = collections.defaultdict(list)    # (who, hour) -> abs errors
    trades = collections.defaultdict(list) # (model, hour, edge) -> [(t, pnl, cost)]
    resid = collections.defaultdict(list)  # model -> past residuals (for sigma)
    skip = collections.Counter()
    for k in keys:
        e = ev[k]
        days_ahead = max(1, round((e["close"] - (e["open"])) / 86400))
        for hr in hrs:
            # time of decision: the first time of day hr after the market opened
            t = e["open"] + ((hr * 3600 - e["open"] % 86400) % 86400)
            if t >= e["close"] - 600:
                skip["late"] += 1
                continue
            p = past(t)
            if len(p) < 6:
                skip["history"] += 1
                continue
            # steps from the last known daily value to the settle date
            steps = max(1, round((e["close"] - [c for c, v in daily if c <= t - 9 * 3600][-1]) / 86400))
            # market ladder at t: (strike, bid, ask)
            lad = []
            for tk, K, res, vol in e["mk"]:
                cs = [c for c in cand[k].get(tk, []) if c[0] <= t]
                if not cs:
                    continue
                c = cs[-1]
                if c[1] is None or c[2] is None or t - c[0] > 4 * 3600:
                    continue
                lad.append((K, c[1], c[2], res))
            if len(lad) < 4:
                skip["ladder"] += 1
                continue
            lad.sort()
            # market median: strike where mid crosses 0.5 (linear interpolation)
            mids = [(K, (b + a) / 2) for K, b, a, _ in lad]
            med = None
            for (k1, m1), (k2, m2) in zip(mids, mids[1:]):
                if m1 >= 0.5 >= m2 and m1 != m2:
                    med = k1 + (m1 - 0.5) / (m1 - m2) * (k2 - k1)
                    break
            if med is not None:
                acc[("market", hr)].append(abs(med - e["v"]))
            for name, fn in models.items():
                fc = p[-1] + (fn(p) - p[-1]) * steps
                acc[(name, hr)].append(abs(fc - e["v"]))
                rs = resid[(name, steps)][-25:]
                if len(rs) < 8:
                    continue
                sig = max(0.004, (sum(r * r for r in rs) / len(rs)) ** 0.5) * 1.25
                for K, b, a, res in lad:
                    pu = 1 - _norm_cdf((K - fc) / sig)
                    for edge in (0.05, 0.10, 0.15):
                        for side, prob, ask in (("yes", pu, a + 0.01), ("no", 1 - pu, (1 - b) + 0.01)):
                            if not 0.03 <= ask <= 0.97:
                                continue
                            fee = 0.07 * ask * (1 - ask)
                            if prob - ask - fee >= edge:
                                won = (res == side)
                                trades[(name, hr, edge)].append((e["close"], (1 if won else 0) - ask - fee, ask + fee, won))
            if hr == hrs[0]:
                pass
        # after all hours of this event: add residuals (settle now known) for each model, per steps
        p = past(e["close"] + 9 * 3600)[:-1] if False else past(e["open"] + 3600 * 14)
        if len(p) >= 6:
            steps = max(1, round((e["close"] - [c for c, v in daily if c <= e["open"] + 3600 * 14 - 9 * 3600][-1]) / 86400))
            for name, fn in models.items():
                resid[(name, steps)].append(p[-1] + (fn(p) - p[-1]) * steps - e["v"])
    print("skipped:", dict(skip))
    print("\n== Who guesses the settle value better? (average miss in cents, smaller is better)")
    print(f"{'guesser':28s} " + " ".join(f"{h:>5d}h" for h in hrs) + "   (UTC hour of the guess, the day before)")
    for who in ["market"] + list(models):
        row = []
        for h in hrs:
            xs = acc.get((who, h), [])
            row.append(f"{100 * sum(xs) / len(xs):6.2f}" if xs else "     -")
        print(f"{who:28s} " + " ".join(row) + f"   n={len(acc.get((who, hrs[0]), []))}")
    print("\n== Paper bets: buy where the model's chance beats ask + 1c + fee by the edge; hold to the end")
    print(f"{'model':28s} {'hour':>4s} {'edge':>4s} {'bets':>5s} {'won':>5s} {'cost$':>8s} {'pnl$':>8s} {'per$100':>8s} {'1st half':>8s} {'2nd half':>8s}")
    for (name, hr, edge), tr in sorted(trades.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
        tr.sort()
        cost = sum(x[2] for x in tr)
        pnl = sum(x[1] for x in tr)
        h = len(tr) // 2
        def per(xs):
            c = sum(x[2] for x in xs)
            return 100 * sum(x[1] for x in xs) / c if c else 0
        print(f"{name:28s} {hr:4d} {edge:4.2f} {len(tr):5d} {sum(x[3] for x in tr):5d} {cost:8.2f} {pnl:8.2f} {per(tr):8.2f} {per(tr[:h]):8.2f} {per(tr[h:]):8.2f}")


# ---------------------------------------------------------------- gasrec: the recorder's live gas test (2026-11-27)
# Since 9-10 Nov recorder.py saves every 5 min AAA's national average, GasBuddy's live state averages and the
# Kalshi gas ladder books (`gas` + `kbook` lines in the data-YYYYMMDD releases). The plan (backtest/sources.md
# section 2): fit AAA's next number on GasBuddy at 14-18h UTC on the first week, compare its miss with the market's
# on the second week, and buy where they disagree at the real ask + 1c + Kalshi fee. Report backtest/gasrec.md.
GASREC_DIR = "bt_cache/gasrec"
REPO = "palsk1/poly-paper-bot"
# rough state populations (millions) to weight GasBuddy's state averages into one national number
GB_POP = {'CA': 39.0, 'TX': 30.5, 'FL': 22.6, 'NY': 19.6, 'PA': 13.0, 'IL': 12.5, 'OH': 11.8, 'GA': 11.0, 'NC': 10.8,
          'MI': 10.0, 'NJ': 9.3, 'VA': 8.7, 'WA': 7.8, 'AZ': 7.4, 'TN': 7.1, 'MA': 7.0, 'IN': 6.9, 'MO': 6.2,
          'MD': 6.2, 'WI': 5.9, 'CO': 5.9, 'MN': 5.7, 'SC': 5.4, 'AL': 5.1, 'LA': 4.6, 'KY': 4.5, 'OR': 4.2,
          'OK': 4.1, 'CT': 3.6, 'UT': 3.4, 'IA': 3.2, 'NV': 3.2, 'AR': 3.1, 'MS': 2.9, 'KS': 2.9, 'NM': 2.1,
          'NE': 2.0, 'ID': 2.0, 'WV': 1.8, 'HI': 1.4, 'NH': 1.4, 'ME': 1.4, 'MT': 1.1, 'RI': 1.1, 'DE': 1.0,
          'SD': 0.9, 'ND': 0.8, 'AK': 0.7, 'DC': 0.7, 'VT': 0.6, 'WY': 0.6}


def gasrec_fetch(first="20261109", last=None):
    """Download the recorder hour files once and keep only the gas lines and the national gas ladder books."""
    import datetime as dt
    import gzip
    import io
    import os
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(GASREC_DIR, exist_ok=True)
    d = dt.datetime.strptime(first, "%Y%m%d").date()
    end = dt.datetime.strptime(last, "%Y%m%d").date() if last else dt.datetime.utcnow().date()
    urls = []
    while d <= end:
        try:
            rel = json.load(urllib.request.urlopen(f"https://api.github.com/repos/{REPO}/releases/tags/data-{d:%Y%m%d}",
                                                   timeout=30))
            urls += [a["browser_download_url"] for a in rel.get("assets", [])]
        except Exception as e:
            print("  no release", d, str(e)[:80])
        d += dt.timedelta(days=1)

    def one(u):
        fn = os.path.join(GASREC_DIR, os.path.basename(u).replace(".jsonl.gz", ".jsonl"))
        today = dt.datetime.utcnow().strftime("%Y%m%d")
        if os.path.exists(fn) and today not in fn:
            return 0
        raw = urllib.request.urlopen(u, timeout=120).read()
        keep = [ln for ln in gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode().splitlines()
                if '"k":"gas"' in ln[:20] or ('"k":"kbook"' in ln[:20] and '"KXAAAGASD-' in ln[:80])]
        with open(fn, "w") as fh:
            fh.write("\n".join(keep) + ("\n" if keep else ""))
        return 1
    with ThreadPoolExecutor(8) as ex:
        print(f"  {sum(ex.map(one, urls))} new hour files of {len(urls)}")


def gasrec_load():
    """(gas rows sorted by time, {ticker: [(read time, best yes bid, yes bid size, best no bid, no bid size)]})"""
    import glob
    import os
    gas_rows, books = [], collections.defaultdict(list)
    for fn in sorted(glob.glob(os.path.join(GASREC_DIR, "rec-*.jsonl"))):
        for ln in open(fn):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("k") == "gas":
                gas_rows.append(r)
            elif r.get("k") == "kbook" and r.get("tk", "").startswith("KXAAAGASD-"):
                yb = max(r.get("yb") or [[0.0, 0.0]], key=lambda x: x[0])
                nb = max(r.get("nb") or [[0.0, 0.0]], key=lambda x: x[0])
                books[r["tk"]].append((r["t"] + r.get("rt", 0), yb[0], yb[1], nb[0], nb[1]))
    gas_rows.sort(key=lambda r: r["t"])
    for v in books.values():
        v.sort()
    return gas_rows, dict(books)


def _gb_nat(gb, i=0):
    ks = [k for k in GB_POP if k in gb]
    return sum(GB_POP[k] * gb[k][i] for k in ks) / sum(GB_POP[k] for k in ks) if len(ks) > 40 else None


def kfee(c, p):
    """Kalshi taker fee for c contracts at price p, rounded up to the cent."""
    import math
    return math.ceil(round(0.07 * c * p * (1 - p) * 100, 6)) / 100


def gasrec(arg=""):
    import bisect
    import datetime as dt
    import math
    import exam
    if "nofetch" not in arg:
        gasrec_fetch()
    g, books = gasrec_load()
    ledger = None
    for part in arg.split(","):
        if part.startswith("ledger="):
            ledger = part[7:]
    # AAA's number for each day = the last one shown under that day's "price as of" date
    aaa = {}
    for r in g:
        if r.get("aaa") and r.get("aaa_asof"):
            m, d, y = r["aaa_asof"].split("/")
            aaa[dt.date(2000 + int(y), int(m), int(d))] = r["aaa"]
    gts = [r["t"] for r in g]

    def gb_at(t, tol=1800):
        i = bisect.bisect_right(gts, t) - 1
        if i < 0 or t - gts[i] > tol or not g[i].get("gb"):
            return None
        return _gb_nat(g[i]["gb"], 0), _gb_nat(g[i]["gb"], 1)

    ev = collections.defaultdict(list)          # day -> [(strike, ticker)]
    for tk in books:
        e, k = tk.rsplit("-", 1)
        day = dt.datetime.strptime(e.split("-")[1], "%y%b%d").date()
        ev[day].append((float(k), tk))

    def book_at(tk, t, tol=4200):
        b = books[tk]
        i = bisect.bisect_right(b, (t, 9, 9, 9, 9)) - 1
        return b[i] if i >= 0 and t - b[i][0] <= tol else None

    HRS = (14, 15, 16, 17, 18, 20, 22, 0, 2)
    rows = []                                   # one row per (day, hour): features + market ladder
    for day in sorted(ev):
        if day not in aaa or day - dt.timedelta(days=1) not in aaa:
            continue
        prev = aaa[day - dt.timedelta(days=1)]
        p2 = aaa.get(day - dt.timedelta(days=2))
        for h in HRS:
            base = dt.datetime.combine(day - dt.timedelta(days=1 if h >= 12 else 0), dt.time(h), dt.timezone.utc)
            t = base.timestamp()
            now = gb_at(t)
            ago = gb_at(t - 86400)
            lad = []
            for K, tk in sorted(ev[day]):
                b = book_at(tk, t)
                if b:
                    _, yb, ybs, nb, nbs = b
                    lad.append((K, yb, ybs, 1 - nb, nbs, tk))
            if not now or len(lad) < 4:
                continue
            mids = [(K, (yb + ya) / 2) for K, yb, _, ya, _, _ in lad]
            med = None
            for (k1, m1), (k2, m2) in zip(mids, mids[1:]):
                if m1 >= 0.5 >= m2 and m1 != m2:
                    med = k1 + (m1 - 0.5) / (m1 - m2) * (k2 - k1)
                    break
            rows.append({"day": day, "h": h, "t": t, "v": aaa[day], "prev": prev, "trend": (prev - p2) if p2 else None,
                         "chg": now[1], "lvl24": (now[0] - ago[0]) if ago else None, "med": med, "lad": lad})
    days = sorted({r["day"] for r in rows})
    print(f"{len(days)} days with a ladder and AAA's number: {days[0]} .. {days[-1]}; rows {len(rows)}")
    split = days[0] + dt.timedelta(days=7)      # first week = training
    print(f"training days: before {split} ({sum(1 for d in days if d < split)}), test days: {sum(1 for d in days if d >= split)}")
    print("\nday         AAA    change   GB chg 16h  GB 24h 16h  market mid 16h")
    for r in rows:
        if r["h"] == 16:
            print(f"{r['day']}  {r['v']:.4f} {100 * (r['v'] - r['prev']):+6.2f}c  {100 * r['chg']:+6.2f}c  "
                  f"{(100 * r['lvl24']) if r['lvl24'] is not None else float('nan'):+6.2f}c  "
                  f"{r['med'] if r['med'] else float('nan'):.4f}")

    def fit(xs, ys):
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        vx = sum((x - mx) ** 2 for x in xs)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx if vx else 0.0
        return my - b * mx, b

    feats = {"GasBuddy change today": "chg", "GasBuddy level vs 24h ago": "lvl24", "GasBuddy 24h change, no fit": "lvl24"}
    models = {}                                 # (name, hour) -> (a, b, sigma)
    for name, f_ in feats.items():
        for h in HRS:
            tr = [r for r in rows if r["h"] == h and r["day"] < split and r[f_] is not None]
            if len(tr) < 4:
                continue
            a, b = (0.0, 1.0) if "no fit" in name else fit([r[f_] for r in tr], [r["v"] - r["prev"] for r in tr])
            res = [r["v"] - r["prev"] - a - b * r[f_] for r in tr]
            models[(name, h)] = (a, b, max(0.003, (sum(x * x for x in res) / len(res)) ** 0.5 * 1.25))
    # a plain baseline needs no fit: yesterday's AAA change carries on
    print("\n== Average miss on AAA's number, cents (test days only; smaller is better)")
    print(f"{'guesser':30s} " + " ".join(f"{h:>5d}h" for h in HRS))
    guess = {}

    def fc(r, name):
        if name == "market":
            return r["med"]
        if name == "AAA yesterday + its last change":
            return r["prev"] + r["trend"] if r["trend"] is not None else None
        a_b = models.get((name, r["h"]))
        x = r[feats[name]] if name in feats else None
        return r["prev"] + a_b[0] + a_b[1] * x if a_b and x is not None else None
    names = ["market", "AAA yesterday + its last change"] + list(feats)
    for name in names:
        line = []
        for h in HRS:
            xs = [abs(fc(r, name) - r["v"]) for r in rows if r["h"] == h and r["day"] >= split
                  and fc(r, name) is not None and r["med"] is not None]
            line.append(f"{100 * sum(xs) / len(xs):6.2f}" if xs else "     -")
        print(f"{name:30s} " + " ".join(line))
    for name in feats:
        print(f"  fit {name}: " + ", ".join(f"{h}h a={100 * models[(name, h)][0]:+.2f}c b={models[(name, h)][1]:.2f}"
                                          f" sd={100 * models[(name, h)][2]:.2f}c" for h in HRS if (name, h) in models))

    C = 10                                      # contracts per rung bought

    def bets_for(name, h, edge, test_only=True):
        out = []
        for r in rows:
            if r["h"] != h or (test_only and r["day"] < split):
                continue
            f_ = fc(r, name)
            m = models.get((name, h))
            if f_ is None or not m:
                continue
            for K, yb, ybs, ya, yas, tk in r["lad"]:
                pu = 1 - _norm_cdf((K - f_) / m[2])
                for side, prob, ask, sz in (("yes", pu, ya, yas), ("no", 1 - pu, 1 - yb, ybs)):
                    px = round(ask + 0.01, 2)
                    if not 0.03 <= px <= 0.97 or sz < 1:
                        continue
                    fee = kfee(C, px)
                    if prob - px - fee / C >= edge:
                        won = (r["v"] > K) == (side == "yes")
                        out.append({"ev": tk.rsplit("-", 1)[0], "t": r["t"], "cost": C * px + fee,
                                    "pay": C * (1.0 if won else 0.0), "side": side, "px": px, "K": K, "fc": f_,
                                    "med": r["med"], "v": r["v"], "tk": tk, "won": won})
        return out
    print("\n== Paper bets on the test days: buy where the model's chance beats ask + 1c + fee by the edge; 10 contracts")
    print(f"{'model':30s} {'hour':>4s} {'edge':>4s} {'bets':>5s} {'days':>4s} {'won':>4s} {'cost$':>7s} {'P&L$':>7s} {'per$100':>8s}")
    tries = 0
    for name in feats:
        for h in HRS:
            for edge in (0.05, 0.10, 0.15):
                bs = bets_for(name, h, edge)
                tries += 1
                if not bs:
                    continue
                cost = sum(b["cost"] for b in bs)
                pnl = sum(b["pay"] - b["cost"] for b in bs)
                print(f"{name:30s} {h:4d} {edge:4.2f} {len(bs):5d} {len({b['ev'] for b in bs}):4d} "
                      f"{sum(b['won'] for b in bs):4d} {cost:7.2f} {pnl:+7.2f} {100 * pnl / cost:+8.2f}")
    # the headline, fixed before looking at the table: the model with the smaller training miss at 16h, 10c edge
    best = min(feats, key=lambda n: models.get((n, 16), (0, 0, 9))[2])
    head = bets_for(best, 16, 0.10)
    print(f"\n== Headline: {best}, 16h UTC, 10c edge, test days only")
    for b in head:
        print(f"  {b['tk']:28s} {b['side']:3s} at {100 * b['px']:.0f}c  model {b['fc']:.4f}  market {b['med'] or 0:.4f}"
              f"  AAA {b['v']:.4f}  {'won' if b['won'] else 'lost'}")
    exam.score(head, "gas ladder vs live GasBuddy, 16h, 10c edge", tries=tries, status="dropped",
               src="sources.py gasrec", note="recorder 10-27 Nov, fit on week 1, scored on later days", ledger=ledger)
    # every hour and edge pooled (each day counts once): is anything there at all?
    allb = [b for h in (14, 16, 18) for b in bets_for(best, h, 0.10)]
    exam.score(allb, "gas ladder vs live GasBuddy, 14/16/18h pooled, 10c edge", tries=tries, status="dropped",
               src="sources.py gasrec", note="same days at three hours count once per day", ledger=ledger)
    # backward look: on every day (training too), what did the winning sides share beforehand?
    print("\n== Backward look (all days, 16h, every rung with a real ask 3-97c): who won, by side and distance")
    cells = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        if r["h"] != 16 or r["med"] is None:
            continue
        for K, yb, ybs, ya, yas, tk in r["lad"]:
            for side, ask in (("yes", ya), ("no", 1 - yb)):
                px = round(ask + 0.01, 2)
                if not 0.03 <= px <= 0.97:
                    continue
                won = (r["v"] > K) == (side == "yes")
                band = "under 25c" if px < 0.25 else "25-75c" if px <= 0.75 else "over 75c"
                rel = "rung above market mid" if K > r["med"] else "rung below market mid"
                c = cells[(side, band, rel)]
                c[0] += 1
                c[1] += C * px + kfee(C, px)
                c[2] += (C if won else 0) - C * px - kfee(C, px)
    for k, (n, cost, pnl) in sorted(cells.items()):
        print(f"  {k[0]:3s} {k[1]:9s} {k[2]:22s} bets {n:4d}  P&L ${pnl:+8.2f} on ${cost:8.2f}  per $100 {100 * pnl / cost:+7.2f}")
    print("\n  AAA's daily change vs the market's 16h guess (cents): days AAA fell more than the market said")
    for r in rows:
        if r["h"] == 16 and r["med"] is not None:
            print(f"   {r['day']}  AAA {100 * (r['v'] - r['prev']):+5.2f}  market {100 * (r['med'] - r['prev']):+5.2f}"
                  f"  miss {100 * (r['v'] - r['med']):+5.2f}  weekday {r['day'].strftime('%a')}")


# ---------------------------------------------------------------- earthquakes: USGS vs KXBIGGESTQUAKE
def quake(arg=""):
    """For each day with a big quake: minutes from the quake (and from USGS first posting it) to the Kalshi
    price of the 'at least M' rungs it decided going to 90c+."""
    import kcrypto
    ev = ladder("KXBIGGESTQUAKE")
    print(f"{len(ev)} quake days with a ladder")
    rows = []
    for k, e in sorted(ev.items(), key=lambda kv: kv[1]["close"]):
        t0, t1 = e["close"] - 86400 - 6 * 3600, e["close"] + 3600
        try:
            q = bot.http_json("https://earthquake.usgs.gov/fdsnws/event/1/query",
                              {"format": "geojson", "starttime": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t0)),
                               "endtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t1)), "minmagnitude": 5.8,
                               "orderby": "magnitude"})
        except Exception as ex:
            print(" usgs failed", ex)
            continue
        feats = q.get("features") or []
        if not feats:
            continue
        top = feats[0]
        mag, ot = f(top["properties"].get("mag")), top["properties"]["time"] / 1000
        first = None
        try:
            d = bot.http_json(top["properties"]["detail"])
            ups = [p.get("updateTime") for kind in ("origin", "phase-data", "moment-tensor")
                   for p in (d["properties"].get("products") or {}).get(kind, [])]
            ups = [u / 1000 for u in ups if u]
            first = min(ups) if ups else None
        except Exception:
            pass
        # 1-minute candles around the quake for rungs at or below the magnitude
        rungs = [(tk, K) for tk, K, res, vol in e["mk"] if K <= mag + 1e-9 and K >= mag - 0.6]
        if not rungs:
            continue
        try:
            res = kcrypto.get("/markets/candlesticks", {"market_tickers": ",".join(t for t, _ in rungs),
                              "start_ts": int(ot - 1800), "end_ts": int(ot + 4 * 3600), "period_interval": 1})
        except Exception as ex:
            print(" candles failed", ex)
            continue
        cs = {r.get("market_ticker"): [kcrypto.candle_row(c) for c in r.get("candlesticks") or []]
              for r in res.get("markets") or []}
        for tk, K in rungs:
            c = cs.get(tk) or []
            before = [x for x in c if x[0] <= ot]
            pre_bid = before[-1][1] if before else None
            pre_ask = before[-1][2] if before else None
            hit = next((x for x in c if x[0] > ot and x[1] is not None and x[1] >= 0.9), None)
            cheap = [x for x in c if x[0] > (first or ot) and x[2] is not None and x[2] <= 0.85]
            rows.append((k, mag, K, ot, first, pre_bid, pre_ask, hit[0] if hit else None,
                         cheap[-1][0] if cheap else None, cheap[0][2] if cheap else None))
    print(f"\n{'day':24s} {'mag':>4s} {'rung':>4s} {'posted':>7s} {'pre bid/ask':>11s} {'bid>=90c':>8s} {'last ask<=85c':>13s}  (minutes after the quake)")
    for k, mag, K, ot, first, pb, pa, hit, cheap, cheap_px in rows:
        mm = lambda t: f"{(t - ot) / 60:7.1f}" if t else "      -"
        print(f"{k:24s} {mag:4.1f} {K:4.1f} {mm(first)} {str(pb):>5s}/{str(pa):<5s} {mm(hit):>8s} {mm(cheap):>13s} {cheap_px if cheap_px is not None else ''}")


# ---------------------------------------------------------------- can GitHub read the early sources?
EARLY = [
    ("gasbuddy live US average", "https://www.gasbuddy.com/usa"),
    ("AAA gas page", "https://gasprices.aaa.com/"),
    ("White House presidential actions", "https://www.whitehouse.gov/presidential-actions/"),
    ("WH actions feed", "https://www.whitehouse.gov/presidential-actions/feed/"),
    ("Federal Register EOs", "https://www.federalregister.gov/api/v1/documents.json?conditions[presidential_document_type]=executive_order&order=newest&per_page=5&fields[]=executive_order_number&fields[]=signing_date&fields[]=publication_date&fields[]=title"),
    ("Federal Register public inspection", "https://www.federalregister.gov/api/v1/public-inspection-documents/current.json"),
    ("Truth Social API", "https://truthsocial.com/api/v1/accounts/107780257626128497/statuses?limit=5"),
    ("Roll Call factba.se", "https://rollcall.com/factbase/trump/topic/social/"),
    ("xtracker", "https://xtracker.polymarket.com/api/users"),
    ("ERCOT dashboard", "https://www.ercot.com/api/1/services/read/dashboards/loadForecastVsActual.json"),
    ("USGS live feed", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"),
    ("Apple top free apps", "https://rss.marketingtools.apple.com/api/v2/us/apps/top-free/10/apps.json"),
    ("TSA throughput", "https://www.tsa.gov/travel/passenger-volumes"),
    ("Netflix top 10", "https://www.netflix.com/tudum/top10/united-states/tv"),
    ("FlixPatrol", "https://flixpatrol.com/top10/netflix/united-states/"),
    ("Mortgage News Daily", "https://www.mortgagenewsdaily.com/mortgage-rates"),
    ("Spotify charts (kworb)", "https://kworb.net/spotify/country/us_daily.html"),
    ("NY Fed SOFR", "https://markets.newyorkfed.org/api/rates/secured/sofr/last/3.json"),
    ("IMF PortWatch", "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query?where=portname%3D%27Strait%20of%20Hormuz%27&outFields=*&orderByFields=date%20desc&resultRecordCount=3&f=json"),
    ("LMArena leaderboard", "https://lmarena.ai/leaderboard"),
    ("Box Office Mojo daily", "https://www.boxofficemojo.com/date/"),
    ("RealClearPolling", "https://www.realclearpolling.com/polls/approval/donald-trump/approval-rating"),
    ("Yahoo RBOB futures", "https://query1.finance.yahoo.com/v8/finance/chart/RB=F?interval=1h&range=5d"),
    ("Pyth hermes", "https://hermes.pyth.network/v2/updates/price/latest?ids[]=0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"),
]


def reach():
    for name, url in EARLY:
        t = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; paper bot)",
                                                       "Accept": "text/html,application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read(400000).decode("utf-8", "replace")
                print(f"OK  {r.status} {len(body):7d}B {time.time() - t:4.1f}s  {name}: {re.sub(r'\s+', ' ', body[:200])}")
        except urllib.error.HTTPError as e:
            print(f"BAD {e.code}            {name}")
        except Exception as e:
            print(f"ERR {type(e).__name__}: {str(e)[:80]}  {name}")


# ---------------------------------------------------------------- executive orders: White House/Fed Register vs KXEOWEEK
def fr_eos(year_from="2026-01-01"):
    out, url = [], ("https://www.federalregister.gov/api/v1/documents.json?conditions[presidential_document_type]=executive_order"
                    f"&conditions[signing_date][gte]={year_from}&per_page=200&order=oldest"
                    "&fields[]=executive_order_number&fields[]=signing_date&fields[]=publication_date&fields[]=title"
                    "&fields[]=public_inspection_pdf_url")
    while url:
        r = bot.http_json(url)
        out += r.get("results") or []
        url = r.get("next_page_url")
    return out


def eo(arg=""):
    import datetime as dt
    import kcrypto
    eos = fr_eos()
    print(f"Federal Register: {len(eos)} executive orders signed since 2026-01-01")
    lag = [(dt.date.fromisoformat(x["publication_date"]) - dt.date.fromisoformat(x["signing_date"])).days for x in eos
           if x.get("publication_date") and x.get("signing_date")]
    if lag:
        lag.sort()
        print(f"days from signing to Federal Register: median {lag[len(lag) // 2]}, 90th pct {lag[int(len(lag) * .9)]}, max {lag[-1]}")
    ms = kmarkets("KXEOWEEK", pages=3)
    evs = collections.defaultdict(list)
    for m in ms:
        evs[m["event_ticker"]].append(m)
    print(f"KXEOWEEK: {len(ms)} settled rungs in {len(evs)} weeks")
    print(f"\n{'week':20s} {'EOs':>3s} {'rung':>6s} {'res':>4s}  price (yes bid/ask) at: week end, +1d, +2d, +4d, +7d, close-1h")
    for et, rungs in sorted(evs.items()):
        r0 = rungs[0]
        mt = re.search(r"between (\w+ \d+, \d{4}) and (\w+ \d+, \d{4})", r0.get("title") or "")
        if not mt:
            print(et, "no week in title:", r0.get("title"))
            continue
        a, b = (dt.datetime.strptime(x, "%b %d, %Y").date() for x in mt.groups())
        n = sum(1 for x in eos if a.isoformat() <= x["signing_date"] <= b.isoformat())
        # week end = end of day b, US Eastern (05:00 UTC next day)
        wend = dt.datetime(b.year, b.month, b.day, tzinfo=dt.timezone.utc).timestamp() + 86400 + 5 * 3600
        close = bot.parse_iso(r0["close_time"]).timestamp()
        tks = [m["ticker"] for m in rungs]
        try:
            res = kcrypto.get("/markets/candlesticks", {"market_tickers": ",".join(tks), "start_ts": int(wend - 3 * 86400),
                              "end_ts": int(close), "period_interval": 60})
        except Exception as ex:
            print(et, "candles failed", ex)
            continue
        cs = {r.get("market_ticker"): [kcrypto.candle_row(c) for c in r.get("candlesticks") or []] for r in res.get("markets") or []}
        for m in sorted(rungs, key=lambda m: f(m.get("floor_strike"))):
            c = cs.get(m["ticker"]) or []
            pts = []
            for t in (wend, wend + 86400, wend + 2 * 86400, wend + 4 * 86400, wend + 7 * 86400, close - 3600):
                prev = [x for x in c if x[0] <= t]
                pts.append(f"{prev[-1][1]:.2f}/{prev[-1][2]:.2f}" if prev and prev[-1][1] is not None and prev[-1][2] is not None else "   -/-   ")
            print(f"{et:20s} {n:3d} {'>' + str(m.get('floor_strike')):>6s} {m.get('result'):>4s}  " + "  ".join(pts)
                  + f"   vol {f(m.get('volume_fp')):.0f}")


def gaspages():
    for url in ("https://www.gasbuddy.com/usa", "https://gasprices.aaa.com/"):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; paper bot)"})
        body = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        print("####", url, len(body))
        mm = re.search(r"\b3\.\d{3}\b", body)
        if mm:
            print("  CTX:", body[max(0, mm.start() - 900):mm.start() + 600])
        for m in re.finditer(r"(?i)national", body):
            print("  N:", re.sub(r"\s+", " ", body[max(0, m.start() - 150):m.start() + 350]))
        for m in re.finditer(r"(?i)(apollo|__next_data__|window\.__)", body):
            print("  S:", re.sub(r"\s+", " ", body[m.start():m.start() + 300]))
    return
    for url in ("https://www.gasbuddy.com/usa", "https://gasprices.aaa.com/"):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; paper bot)"})
        body = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        print("####", url)
        for m in re.finditer(r"(.{0,160})\$?\b([34]\.\d{2,3})\b(.{0,120})", body):
            print("  ", re.sub(r"\s+", " ", (m.group(1) + " [[" + m.group(2) + "]] " + m.group(3)))[:300])
        for m in re.finditer(r"(?i)(updated|as of|last update)[^<]{0,80}", body):
            print("  time:", m.group(0)[:120])


MODES = {"livegas": gaspages, "eo": eo, "reach": reach, "quake": quake, "map": mapping, "kdaily": kdaily, "precur": precurring}

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "map"
    if a == "gas" or a.startswith("gas_"):
        gas(a[4:])
    elif a == "gasrec" or a.startswith("gasrec_"):
        gasrec(a[7:])
    elif a.startswith("ks_"):
        kseries(a[3:])
    else:
        MODES[a]()
