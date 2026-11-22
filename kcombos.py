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
# Sampling: random 5-minute windows of CLOSE time on each day; in each, a random draw of the combo markets that
# settled and had any trade. The draw is by ticker, so it can't depend on who won. (Reading Kalshi's whole trade
# list by time was tried first: far too slow.)
SPAN = int(os.environ.get("KCB_SPAN", "300"))
PER_DAY = int(os.environ.get("KCB_PER_DAY", "8"))
MAX_PAGES = int(os.environ.get("KCB_PAGES", "6"))
MAX_COMBOS = int(os.environ.get("KCB_COMBOS", "120"))
WORKERS = int(os.environ.get("KCB_WORKERS", "5"))
BUDGET_MIN = float(os.environ.get("KCB_MIN", "200"))
SKIP_DAYS = 1


def day_path(d0):
    return os.path.join(CACHE, f"day_{time.strftime('%Y%m%d', time.gmtime(d0))}.json.gz")


def slices_of(d0, n=None):
    rng = random.Random(d0 + 11)
    n = n or PER_DAY
    step = DAY // n
    return [d0 + i * step + rng.randrange(0, step - SPAN) for i in range(n)]


def list_window(a, b):
    """Settled combo markets whose close time is in [a, b). -> (markets, complete)"""
    out, cur = [], None
    for _ in range(MAX_PAGES):
        p = {"mve_filter": "only", "status": "settled", "limit": 1000, "min_close_ts": int(a), "max_close_ts": int(b) - 1}
        if cur:
            p["cursor"] = cur
        r = kget("/markets", p)
        got = r.get("markets") or []
        out += got
        cur = r.get("cursor")
        if not cur or not got:
            return out, True
    return out, False


def chunks(xs, n):
    xs = list(xs)
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def pmap(fn, xs):
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(fn, xs))


def markets_by_ticker(tks, per=20):
    def one(part):
        try:
            return kget("/markets", {"tickers": ",".join(part), "limit": 1000}).get("markets") or []
        except Exception:
            return []
    out = {}
    for got in pmap(one, chunks(sorted(tks), per)):
        for m in got:
            if m.get("ticker"):
                out[m["ticker"]] = m
    return out


def combo_trades(tk):
    try:
        r = kget("/markets/trades", {"ticker": tk, "limit": 1000})
    except Exception:
        return tk, None
    rows = []
    for t in r.get("trades") or []:
        ts = its(t.get("created_time"))
        yp = bot.fnum(t.get("yes_price_dollars"), None)
        n = bot.fnum(t.get("count_fp") or t.get("count"), 0)
        side = str(t.get("taker_side") or "")
        if ts is None or yp is None or n <= 0 or side not in ("yes", "no"):
            continue
        rows.append([ts, yp, round(n, 2), 1 if side == "yes" else 0, 1 if t.get("is_block_trade") else 0])
    return tk, rows


def slim_combo(m):
    return {"legs": [[lg.get("market_ticker"), 1 if str(lg.get("side")) == "yes" else 0] for lg in m.get("mve_selected_legs") or []],
            "res": str(m.get("result") or ""), "sv": bot.fnum(m.get("settlement_value_dollars"), None),
            "close": its(m.get("close_time")), "set": its(m.get("settlement_ts")), "open": its(m.get("open_time")),
            "col": m.get("mve_collection_ticker"), "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0)}


def slim_leg(m):
    return {"ev": m.get("event_ticker"), "q": f"{m.get('title') or ''} | {m.get('yes_sub_title') or ''}"[:120],
            "res": str(m.get("result") or ""), "sv": bot.fnum(m.get("settlement_value_dollars"), None),
            "close": its(m.get("close_time")), "exp": its(m.get("expected_expiration_time")), "open": its(m.get("open_time")),
            "occ": its(m.get("occurrence_datetime"))}


def leg_quotes(need):
    """need = {leg ticker: sorted trade times}. -> {leg: {trade time: [yes bid, yes ask, last price]}} from 1-minute
    candles: the newest finished minute at or before the trade (a quote the maker could have seen)."""
    def one(item):
        tk, times = item
        s = tk.split("-")[0]
        lo, hi = min(times), max(times)
        rows = []
        a = lo - 600
        while a < hi + 60:
            b = min(hi + 60, a + 4000 * 60)
            try:
                r = kget(f"/series/{s}/markets/{tk}/candlesticks", {"start_ts": int(a), "end_ts": int(b), "period_interval": 1})
            except Exception:
                r = None
            for c in (r.get("candlesticks") if isinstance(r, dict) else None) or []:
                t, bid, ask = yesno.k_candle(c)
                rows.append([t, bid, ask, bot.fnum((c.get("price") or {}).get("close_dollars"), None)])
            a = b
            if hi - lo > 3 * DAY:       # very long span: only fetch around each trade
                break
        rows.sort()
        out = {}
        for ts in times:
            best = None
            for row in rows:
                if row[0] <= ts:
                    best = row
                else:
                    break
            if best and ts - best[0] <= 900:
                out[str(ts)] = best[1:]
        return tk, out
    return dict(pmap(one, sorted(need.items())))


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
        for a in slices_of(d0):
            b = a + SPAN
            t0 = time.time()
            try:
                ms, done = list_window(a, b)
            except Exception as e:
                print("  window failed", a, str(e)[:150], flush=True)
                continue
            traded = sorted(m["ticker"] for m in ms if bot.fnum(m.get("volume_fp") or m.get("volume"), 0) > 0)
            vol_all = sum(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ms)
            pick = set(random.Random(a).sample(traded, MAX_COMBOS) if len(traded) > MAX_COMBOS else traded)
            combos = {m["ticker"]: slim_combo(m) for m in ms if m["ticker"] in pick}
            t1 = time.time()
            for tk, rows in pmap(combo_trades, sorted(pick)):
                combos[tk]["tr"] = rows
            t2 = time.time()
            need = collections.defaultdict(set)
            for c in combos.values():
                for lg in c["legs"]:
                    for r in c.get("tr") or []:
                        need[lg[0]].add(r[0])
            need = {k: sorted(v) for k, v in need.items() if k}
            lm = markets_by_ticker(need)
            t3 = time.time()
            q = leg_quotes(need)
            day["slices"].append({"a": a, "b": b, "listed": len(ms), "done": done, "traded": len(traded), "vol": vol_all,
                                  "combos": combos, "legs": {tk: slim_leg(m) for tk, m in lm.items()}, "q": q})
            print(f"  {time.strftime('%m-%d %H:%M', time.gmtime(a))} listed {len(ms)}{'' if done else '+'} traded {len(traded)} "
                  f"kept {len(pick)} trades {sum(len(c.get('tr') or []) for c in combos.values())} legs {len(need)} "
                  f"(found {len(lm)}, quoted {sum(1 for v in q.values() if v)}) | list {t1 - t0:.0f}s trades {t2 - t1:.0f}s "
                  f"legs {t3 - t2:.0f}s quotes {time.time() - t3:.0f}s [{(time.time() - T0) / 60:.1f} min]", flush=True)
        wj(path, day)
        print(f"saved {os.path.basename(path)}", flush=True)


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
    n = sum(len(c.get("tr") or []) for d in days for sl in d["slices"] for c in sl["combos"].values())
    print(len(days), "days,", n, "combo trades")
    for d in days[:2]:
        for sl in d["slices"][:2]:
            print({k: sl[k] for k in ("a", "b", "listed", "done", "traded", "vol")})
            for tk, c in list(sl["combos"].items())[:6]:
                print("  ", tk, json.dumps({k: v for k, v in c.items() if k != "legs"})[:300])
                for lg in c["legs"][:4]:
                    qq = sl["q"].get(lg[0]) or {}
                    print("      ", lg, json.dumps(sl["legs"].get(lg[0]))[:230], list(qq.items())[:2])


def trial():
    global CACHE
    CACHE = "/tmp/kcb_trial"
    fetch("1", "2")
    stat()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch, "stat": stat, "trial": trial}[cmd](*sys.argv[2:])
