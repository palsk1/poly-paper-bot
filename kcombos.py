#!/usr/bin/env python3
"""Kalshi combos (parlays): can a small account be the house? (2026-11-22). Research only.

PAPER ONLY. Reads public data, never trades, never writes state/. No key, no login.

Kalshi combos ("multivariate events", tickers KXMVE...) are priced by request-for-quote: a buyer asks, makers
answer through the API, the best quote trades. Every combo trade is public (`/markets/trades`), and so are the
legs. So the Polymarket combo question (combos.py) can be asked here without a server:
  1. what did combo buyers pay, against the same legs' own prices at that minute?
  2. how did the seller (the house) do once the games finished, after Kalshi's maker fee on combos?
  3. would a house that sells at "legs multiplied + a margin" have won trades, and at a profit?
  4. how much money does one sold combo lock up (does $30 go anywhere)?

    python3 kcombos.py peek            # probe kcb_peek: raw shapes of collections, combo markets, trades, legs
    python3 kcombos.py fetch [days]    # probe kcb_fetch: settled combo markets, their trades, each leg's minute quotes
    python3 kcombos.py run             # probe kcb_run (or locally, data is in the price store): backtest/kcombos.md
    python3 kcombos.py selftest        # offline

Data: kcb_cache/ (its own folder in the shared price store, so a run needn't download the whole store:
`python3 store.py pull kcb_cache`).
"""
import collections
import datetime as dt
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import exam
import khouse
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "kcb_cache")
OUT = os.path.join(ROOT, "backtest", "kcombos.md")
DAY = 86400
kget = yesno.kget
rj, wj, its = khouse.rj, khouse.wj, khouse.its
T0 = time.time()


def shape(x, depth=0, maxd=3):
    if isinstance(x, dict):
        if depth >= maxd:
            return "{...}"
        return {k: shape(v, depth + 1, maxd) for k, v in list(x.items())[:60]}
    if isinstance(x, list):
        return [shape(x[0], depth + 1, maxd), f"... x{len(x)}"] if x else []
    s = str(x)
    return s if len(s) <= 90 else s[:90] + "..."


def show(label, fn):
    print(f"\n===== {label}")
    try:
        r = fn()
        print(json.dumps(shape(r), indent=1)[:6000])
        return r
    except Exception as e:
        print("  FAILED:", str(e)[:300])
        return None


def peek():
    cols = show("collections", lambda: kget("/multivariate_event_collections", {"limit": 200}))
    rows = (cols or {}).get("multivariate_contracts") or (cols or {}).get("multivariate_event_collections") or []
    print("\ncollections:", len(rows))
    for c in rows[:80]:
        print("  ", c.get("collection_ticker"), "|", str(c.get("title"))[:70], "|", c.get("open_date"), c.get("close_date"),
              "| events", len(c.get("associated_events") or []), "| size", c.get("size_min"), c.get("size_max"),
              "| ordered", c.get("is_ordered"), "| single/event", c.get("is_single_market_per_event"))
    show("events/multivariate", lambda: kget("/events/multivariate", {"limit": 3, "with_nested_markets": "true"}))
    now = int(time.time())
    for st in ("settled", "open", "closed"):
        r = show(f"markets mve_filter=only status={st}", lambda: kget("/markets", {"mve_filter": "only", "status": st, "limit": 1000}))
        ms = (r or {}).get("markets") or []
        vols = sorted((bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ms), reverse=True)
        print(f"  {st}: {len(ms)} on page 1, cursor={'yes' if (r or {}).get('cursor') else 'no'}, with volume {sum(1 for v in vols if v > 0)}, "
              f"top volumes {vols[:10]}")
        if ms:
            cl = sorted(its(m.get("close_time")) or 0 for m in ms)
            print("  close range", dt.datetime.utcfromtimestamp(cl[0]), dt.datetime.utcfromtimestamp(cl[-1]))
            print("  results", collections.Counter(str(m.get("result")) for m in ms).most_common(6))
            print("  prefixes", collections.Counter(str(m.get("ticker")).split("-")[0] for m in ms).most_common(12))
            traded = [m for m in ms if bot.fnum(m.get("volume_fp") or m.get("volume"), 0) > 0]
            for m in traded[:3]:
                print("\n  --- one traded combo, every field")
                print(json.dumps(m, indent=1)[:5000])
                tk = m.get("ticker")
                tr = show(f"trades {tk}", lambda: kget("/markets/trades", {"ticker": tk, "limit": 100}))
                for t in ((tr or {}).get("trades") or [])[:8]:
                    print("   ", json.dumps(t)[:400])
                show(f"orderbook {tk}", lambda: kget(f"/markets/{tk}/orderbook"))
                legs = m.get("mve_selected_legs") or []
                for lg in legs[:4]:
                    lt = lg.get("market_ticker")
                    lm = show(f"leg {lt}", lambda: kget(f"/markets/{lt}"))
    # how many settled combo markets a day, and how many traded: one day, all pages
    for back in (1, 3):
        d0 = (now // DAY - back) * DAY
        n = tr_n = 0
        vol = 0.0
        cur = None
        pages = 0
        for _ in range(60):
            p = {"mve_filter": "only", "status": "settled", "limit": 1000, "min_close_ts": d0, "max_close_ts": d0 + DAY - 1}
            if cur:
                p["cursor"] = cur
            try:
                r = kget("/markets", p)
            except Exception as e:
                print("  day list failed", str(e)[:200])
                break
            ms = r.get("markets") or []
            pages += 1
            n += len(ms)
            for m in ms:
                v = bot.fnum(m.get("volume_fp") or m.get("volume"), 0)
                if v > 0:
                    tr_n += 1
                    vol += v
            cur = r.get("cursor")
            if not cur or not ms:
                break
        print(f"\nday -{back}: {n} settled combo markets ({pages} pages{', more left' if cur else ''}), {tr_n} traded, {vol:,.0f} contracts")
    show("fee changes", lambda: kget("/series/fee_changes"))
    show("all trades, newest (any market)", lambda: kget("/markets/trades", {"limit": 5}))
    show("communications rfqs without a key", lambda: kget("/communications/rfqs", {"limit": 5}))


# ================================================================ fetch
SPAN = int(os.environ.get("KCB_SPAN", "60"))          # seconds of the trade list per slice
PER_DAY = int(os.environ.get("KCB_PER_DAY", "12"))
MAX_PAGES = int(os.environ.get("KCB_PAGES", "12"))
MAX_COMBOS = int(os.environ.get("KCB_COMBOS", "300"))   # combos looked up per slice (a random draw of the traded ones)
WORKERS = int(os.environ.get("KCB_WORKERS", "6"))
BUDGET_MIN = float(os.environ.get("KCB_MIN", "200"))
SKIP_DAYS = 2                                           # newest days are skipped so combos have settled


def day_path(d0):
    return os.path.join(CACHE, f"day_{time.strftime('%Y%m%d', time.gmtime(d0))}.json.gz")


def slices_of(d0, n=None):
    rng = random.Random(d0 + 11)
    n = n or PER_DAY
    step = DAY // n
    return [(d0 + i * step + rng.randrange(0, step - SPAN), ) for i in range(n)]


def tape_slice(t0, t1):
    """Every trade on Kalshi in [t0, t1) (all markets, newest first); keep the combo ones.
    -> (combo rows [ts, ticker, yes price, contracts, taker bought yes], covered from, all trades seen, complete)"""
    out, cur, seen, lo, done = [], None, 0, t1, False
    for _ in range(MAX_PAGES):
        p = {"min_ts": int(t0), "max_ts": int(t1), "limit": 1000}
        if cur:
            p["cursor"] = cur
        r = kget("/markets/trades", p)
        got = r.get("trades") or []
        seen += len(got)
        for t in got:
            ts = its(t.get("created_time"))
            if ts is not None:
                lo = min(lo, ts)
            tk = str(t.get("ticker") or "")
            if not tk.startswith("KXMVE") or ts is None:
                continue
            yp = bot.fnum(t.get("yes_price_dollars"), None)
            n = bot.fnum(t.get("count_fp") or t.get("count"), 0)
            side = str(t.get("taker_side") or "")
            if yp is None or n <= 0 or side not in ("yes", "no"):
                continue
            out.append([ts, tk, yp, round(n, 2), 1 if side == "yes" else 0, 1 if t.get("is_block_trade") else 0])
        cur = r.get("cursor")
        if not cur or not got:
            done = True
            break
    return out, (t0 if done else lo + 1), seen, done


def chunks(xs, n):
    xs = list(xs)
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def markets_by_ticker(tks, per=20):
    out = {}

    def one(part):
        try:
            r = kget("/markets", {"tickers": ",".join(part), "limit": 1000})
            return r.get("markets") or []
        except Exception as e:
            return [{"_err": str(e)[:120]}]
    with ThreadPoolExecutor(WORKERS) as ex:
        for got in ex.map(one, chunks(sorted(tks), per)):
            for m in got:
                if m.get("ticker"):
                    out[m["ticker"]] = m
    return out


def slim_combo(m):
    return {"legs": [[lg.get("market_ticker"), 1 if str(lg.get("side")) == "yes" else 0] for lg in m.get("mve_selected_legs") or []],
            "res": str(m.get("result") or ""), "sv": bot.fnum(m.get("settlement_value_dollars"), None),
            "close": its(m.get("close_time")), "set": its(m.get("settlement_ts")), "open": its(m.get("open_time")),
            "col": m.get("mve_collection_ticker"), "st": m.get("status")}


def slim_leg(m):
    return {"ev": m.get("event_ticker"), "q": f"{m.get('title') or ''} | {m.get('yes_sub_title') or ''}"[:120],
            "res": str(m.get("result") or ""), "sv": bot.fnum(m.get("settlement_value_dollars"), None),
            "close": its(m.get("close_time")), "exp": its(m.get("expected_expiration_time")), "open": its(m.get("open_time")),
            "occ": its(m.get("occurrence_datetime"))}


_DBG = [0]


def candle_rows(cs):
    rows = []
    for c in cs or []:
        t, bid, ask = yesno.k_candle(c)
        rows.append([t, bid, ask, bot.fnum((c.get("price") or {}).get("close_dollars"), None)])
    return rows


def leg_minutes(tks, t0, t1):
    """{leg ticker: [[minute end, yes bid, yes ask, last trade price], ...]} around the slice (1-minute candles).
    One call per 100 legs (`/markets/candlesticks`); a leg the batch misses is asked for on its own."""
    out = {}
    span = {"start_ts": int(t0) - 240, "end_ts": int(t1) + 60, "period_interval": 1}

    def batch(part):
        try:
            r = kget("/markets/candlesticks", dict(span, market_tickers=",".join(part)))
        except Exception as e:
            if _DBG[0] < 3:
                _DBG[0] += 1
                print("   batch candles failed:", str(e)[:200], flush=True)
            return {}
        if _DBG[0] < 1:
            _DBG[0] += 1
            print("   batch candles shape:", json.dumps(shape(r, maxd=4))[:700], flush=True)
        got = {}
        for m in (r.get("markets") if isinstance(r, dict) else None) or []:
            tk = m.get("market_ticker") or m.get("ticker")
            if tk:
                got[tk] = candle_rows(m.get("candlesticks"))
        return got

    def one(tk):
        try:
            r = kget(f"/series/{tk.split('-')[0]}/markets/{tk}/candlesticks", span)
            return tk, candle_rows(r.get("candlesticks") if isinstance(r, dict) else None)
        except Exception:
            return tk, []
    with ThreadPoolExecutor(WORKERS) as ex:
        for got in ex.map(batch, chunks(sorted(tks), 100)):
            out.update(got)
        miss = [tk for tk in sorted(tks) if tk not in out]
        if miss and len(miss) <= 60:
            out.update(dict(ex.map(one, miss)))
    for tk in tks:
        out.setdefault(tk, [])
    return out


def fetch(days="14", per_day=None):
    days = int(days)
    global PER_DAY
    if per_day:
        PER_DAY = int(per_day)
    os.makedirs(CACHE, exist_ok=True)
    today = int(time.time()) // DAY * DAY
    for back in range(SKIP_DAYS, SKIP_DAYS + days):
        d0 = today - back * DAY
        path = day_path(d0)
        if rj(path):
            continue
        if time.time() - T0 > BUDGET_MIN * 60:
            print("time budget used, run again to resume")
            break
        day = {"d0": d0, "slices": []}
        for (a, ) in slices_of(d0):
            b = a + SPAN
            t0s = time.time()
            try:
                rows, cov, seen, done = tape_slice(a, b)
            except Exception as e:
                print("  slice failed", a, str(e)[:150])
                continue
            t1 = time.time()
            tks = sorted({r[1] for r in rows})
            n_all = len(tks)
            if len(tks) > MAX_COMBOS:       # a random draw by ticker: it can't depend on the result
                tks = random.Random(a).sample(tks, MAX_COMBOS)
            keep = set(tks)
            rows = [r for r in rows if r[1] in keep]
            print(f"   tape {seen} trades in {t1 - t0s:.0f}s, combos traded {n_all}, kept {len(tks)}", flush=True)
            cm = markets_by_ticker(tks)
            t2 = time.time()
            combos = {tk: slim_combo(m) for tk, m in cm.items()}
            legs = {lg[0] for c in combos.values() for lg in c["legs"] if lg[0]}
            lm = markets_by_ticker(legs)
            t3 = time.time()
            mins = leg_minutes(legs, cov, b)
            print(f"   combos {t2 - t1:.0f}s, legs {len(legs)} in {t3 - t2:.0f}s, minutes {time.time() - t3:.0f}s", flush=True)
            day["slices"].append({"a": a, "b": b, "cov": cov, "seen": seen, "done": done, "tr": rows, "n_all": n_all, "combos": combos,
                                  "legs": {tk: slim_leg(m) for tk, m in lm.items()}, "min": mins})
            print(f"  {time.strftime('%m-%d %H:%M', time.gmtime(a))} all trades {seen}{'' if done else ' (cut)'}, covered {b - cov}s, "
                  f"combo trades {len(rows)}, combos {len(tks)} (found {len(combos)}), legs {len(legs)} (found {len(lm)}), "
                  f"with minutes {sum(1 for v in mins.values() if v)}  [{(time.time() - T0) / 60:.1f} min]")
        wj(path, day)
        print(f"saved {os.path.basename(path)}: {sum(len(s['tr']) for s in day['slices'])} combo trades")


def load():
    out = []
    for f in sorted(os.listdir(CACHE)) if os.path.isdir(CACHE) else []:
        if f.startswith("day_"):
            d = rj(os.path.join(CACHE, f))
            if d:
                out.append(d)
    return out


def stat():
    days = load()
    n = sum(len(s["tr"]) for d in days for s in d["slices"])
    print(len(days), "days,", n, "combo trades")
    for d in days[:2]:
        for s in d["slices"][:2]:
            print(json.dumps({k: (v if k in ("a", "b", "cov", "seen", "done") else None) for k, v in s.items()}))
            for r in s["tr"][:6]:
                c = s["combos"].get(r[1])
                print("  ", r, json.dumps(c)[:400])
                for lg in (c or {}).get("legs", [])[:3]:
                    print("      ", lg, json.dumps(s["legs"].get(lg[0]))[:260], (s["min"].get(lg[0]) or [])[-3:])




def trial():
    global CACHE
    CACHE = "/tmp/kcb_trial"
    fetch("1", "2")
    stat()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch, "stat": stat, "trial": trial}[cmd](*sys.argv[2:])
