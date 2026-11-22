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
    python3 kcombos.py fetch [days] [moments a day] [start, days back]   # probe kcb_fetch_14_12_17: random moments of
                                       # Kalshi's public trade list, the combos traded then, their legs and results
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
SKIP_DAYS = 3                                           # newest days are skipped so most combos have finished


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


def fetch(days="14", per_day=None, start=None):
    """days = how many days; per_day = moments a day; start = how many days back to begin (default 3)."""
    days = int(days)
    global PER_DAY
    if per_day:
        PER_DAY = int(per_day)
    os.makedirs(CACHE, exist_ok=True)
    today = int(time.time()) // DAY * DAY
    first = max(SKIP_DAYS, int(start or SKIP_DAYS))
    for back in range(first, first + days):
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


# ================================================================ run
MAKER_RATE, TAKER_RATE = 0.035, 0.07       # combos: the answering side pays half the asker's fee (since 20 Aug 2026)
BANK = 300.0


def fee(rate, n, p):
    return math.ceil(rate * n * p * (1 - p) * 10000 - 1e-9) / 10000


def game_code(ev):
    parts = str(ev or "").split("-")
    return parts[1] if len(parts) > 1 else str(ev)


def kind_of(legs):
    ser = [str(lg[0]).split("-")[0] for lg in legs]
    if all(x.endswith("15M") for x in ser):
        return "crypto 15-min"
    if any(x.endswith("15M") for x in ser):
        return "mixed with crypto"
    return "sports and other"


def quote_at(rows, ts):
    """Newest finished minute at or before the trade: (yes bid, yes ask)."""
    best = None
    for r in rows or []:
        if r[0] <= ts + 59:
            best = r
        else:
            break
    if not best or best[1] is None or best[2] is None:
        return None
    return best[1], best[2]


def rows_of(days):
    """One row per combo trade. House = the answering side (it holds the opposite of the asker)."""
    out, skip = [], collections.Counter()
    for d in days:
        horizon = d["d0"] + SKIP_DAYS * DAY - DAY // 2      # every leg must have been due by then (set before the result)
        for sl in d["slices"]:
            for ts, tk, yp, n, tyes, block in sl["tr"]:
                c = sl["combos"].get(tk)
                if not c or not c["legs"]:
                    skip["combo not found"] += 1
                    continue
                legs = [sl["legs"].get(lg[0]) for lg in c["legs"]]
                if any(l is None for l in legs):
                    skip["a leg not found"] += 1
                    continue
                due = max((l.get("exp") or l.get("close") or 0) for l in legs)
                if due > horizon:
                    skip["a leg due after our cut-off (left out whatever the result)"] += 1
                    continue
                if c["res"] not in ("yes", "no") or c["sv"] is None:
                    skip["due but not settled"] += 1
                    continue
                if not 0 < yp < 1:
                    skip["price 0 or 1"] += 1
                    continue
                sv = c["sv"]
                prod_mid = prod_ask = 1.0
                full = True
                for lg, l in zip(c["legs"], legs):
                    q = quote_at(sl["min"].get(lg[0]), ts)
                    if not q:
                        full = False
                        break
                    bid, ask = q
                    mid = (bid + ask) / 2
                    prod_mid *= mid if lg[1] else 1 - mid
                    prod_ask *= ask if lg[1] else 1 - bid
                games = [game_code(l["ev"]) for l in legs]
                if tyes:      # asker bought Yes at yp; the house bought No at 1 - yp
                    cost, back = n * (1 - yp), n * (1 - sv)
                else:         # asker bought No (or sold Yes back); the house bought Yes at yp
                    cost, back = n * yp, n * sv
                out.append({"ts": ts, "tk": tk, "yp": yp, "n": n, "tyes": tyes, "sv": sv, "nlegs": len(legs),
                            "kind": kind_of(c["legs"]), "same": len(set(games)) < len(games), "slice": sl["a"],
                            "prod": prod_mid if full else None, "prod_ask": prod_ask if full else None,
                            "cost": cost, "back": back, "mfee": fee(MAKER_RATE, n, yp), "tfee": fee(TAKER_RATE, n, yp),
                            "paid": n * yp if tyes else n * (1 - yp), "lock": max(0, (c.get("set") or ts) - ts),
                            "left": (min((l.get("exp") or l.get("close") or ts) for l in legs) - ts)})
    return out, skip


def usd(x):
    return f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}"


def per100(rows, key_cost="cost"):
    c = sum(r[key_cost] for r in rows)
    return 100 * sum(r["back"] - r["cost"] - r["mfee"] for r in rows) / c if c else 0.0


def table(title, rows, keyfn, order=None, note=""):
    groups = collections.defaultdict(list)
    for r in rows:
        k = keyfn(r)
        if k is not None:
            groups[k].append(r)
    L = [f"### {title}", ""]
    if note:
        L += [note, ""]
    L += ["| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |",
          "|---|---|---|---|---|---|---|"]
    for k in (order or sorted(groups)):
        g = groups.get(k)
        if not g:
            continue
        paid = sorted(r["paid"] for r in g)
        cost = sorted(r["cost"] for r in g)
        won = sum(1 for r in g if r["back"] > r["cost"])
        net = sum(r["back"] - r["cost"] - r["mfee"] for r in g)
        L.append(f"| {k} | {len(g):,} | {usd(paid[len(paid) // 2])} | {usd(cost[len(cost) // 2])} | {won:,} of {len(g):,} | "
                 f"{usd(per100(g))} | {usd(100 * net / sum(paid))} |")
    return L + [""]


def price_band(r):
    y = r["yp"]
    for hi, name in ((0.01, "under 1c"), (0.05, "1-5c"), (0.15, "5-15c"), (0.35, "15-35c"), (0.65, "35-65c"), (0.9, "65-90c"), (1.01, "90c+")):
        if y < hi:
            return name


BANDS = ["under 1c", "1-5c", "5-15c", "15-35c", "35-65c", "65-90c", "90c+"]


def bets(rows, price=None):
    """Bet list for the exam: one row per trade from the house's chair, grouped by the minute sampled."""
    return [{"ev": f"{r['slice']}", "t": r["ts"], "cost": r["cost"], "pay": r["back"] - r["mfee"]} for r in rows]


def undercut(rows, margin, lo=2, hi=4):
    """A house that prices 'legs multiplied x (1 + margin)' and only gets the trade when that beats the real price."""
    out = []
    for r in rows:
        if not r["tyes"] or r["prod"] is None or r["same"] or not lo <= r["nlegs"] <= hi:
            continue
        q = min(0.99, r["prod"] * (1 + margin))
        if q <= 0 or q >= r["yp"]:
            continue
        n = r["n"]
        out.append(dict(r, cost=n * (1 - q), back=n * (1 - r["sv"]), mfee=fee(MAKER_RATE, n, q), paid=n * q, q=q))
    return out


def run(score="1"):
    days = load()
    rows, skip = rows_of(days)
    if not rows:
        print("no data: run fetch first")
        return
    n_sl = sum(len(d["slices"]) for d in days)
    secs = sum(sl["b"] - sl["cov"] for d in days for sl in d["slices"])
    all_tr = sum(sl["seen"] for d in days for sl in d["slices"])
    cmb_tr = sum(len(sl["tr"]) for d in days for sl in d["slices"])
    n_all = sum(sl.get("n_all") or 0 for d in days for sl in d["slices"])
    kept = sum(len(sl["combos"]) for d in days for sl in d["slices"])
    yes = [r for r in rows if r["tyes"]]
    first = time.strftime("%d %b", time.gmtime(min(d["d0"] for d in days)))
    last = time.strftime("%d %b %Y", time.gmtime(max(d["d0"] for d in days)))
    L = ["# Kalshi combos: can a small account be the house? (22 Nov 2026)", "",
         "Research only. Public data, no key, no orders. Tool `kcombos.py`, data `kcb_cache/` in the price store.", ""]
    L += ["## The sample", "",
          f"{len(days)} days ({first} to {last}), {n_sl} random moments. At each one we read every Kalshi trade of about "
          f"half a minute ({secs:,} seconds in all, {all_tr:,} trades), kept the combo trades, looked up each combo's legs, "
          f"result and what each leg cost on its own that minute.", "",
          f"- Combos traded in those seconds: {n_all:,} different ones (we kept a random {kept:,}, {cmb_tr:,} trades).",
          f"- That is about {n_all / max(1, secs) * 60:,.0f} different combos sold a minute, around the clock.",
          f"- Trades we could score (every leg due and settled): **{len(rows):,}**. Left out: "
          + "; ".join(f"{v:,} {k}" for k, v in skip.most_common()) + ".",
          f"- In {len(yes):,} of them the asker bought the combo (Yes). In {len(rows) - len(yes):,} the asker took the other side.", ""]
    paid = sorted(r["paid"] for r in yes)
    cost = sorted(r["cost"] for r in yes)
    q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))]
    L += ["## How big is one combo, and how much must the house put up?", "",
          "The house buys the No side: for every $1 a combo can pay, it puts up $1 minus the buyer's price.", "",
          "| | smallest quarter | middle | biggest quarter | biggest 1 in 20 |", "|---|---|---|---|---|",
          f"| Buyer's ticket | {usd(q(paid, .25))} | {usd(q(paid, .5))} | {usd(q(paid, .75))} | {usd(q(paid, .95))} |",
          f"| House money locked | {usd(q(cost, .25))} | {usd(q(cost, .5))} | {usd(q(cost, .75))} | {usd(q(cost, .95))} |", "",
          f"A house must answer for the whole size asked. Trades a $300 bank could carry with at most $30 locked: "
          f"{sum(1 for c in cost if c <= 30):,} of {len(cost):,}.", ""]
    L += ["## Who won: the house or the buyer?", "",
          "Every scored trade, from the house's chair, after the house's fee. \"Per $100 locked\" is what a bank earns on the "
          "money it must put up. \"Per $100 of tickets\" is the house's cut of what buyers spent.", ""]
    L += table("By kind of combo (asker bought Yes)", yes, lambda r: r["kind"])
    L += table("By the buyer's price", yes, price_band, BANDS)
    L += table("By number of legs", yes, lambda r: f"{min(r['nlegs'], 8)}{'+' if r['nlegs'] >= 8 else ''} legs")
    L += table("Legs from the same game or not (sports and other)", [r for r in yes if r["kind"] == "sports and other"],
               lambda r: "two or more legs from one game" if r["same"] else "every leg a different game")
    L += table("Small tickets only: house money locked", yes,
               lambda r: "up to $5" if r["cost"] <= 5 else "$5-30" if r["cost"] <= 30 else "$30-300" if r["cost"] <= 300 else "over $300",
               ["up to $5", "$5-30", "$30-300", "over $300"])
    L += table("When the asker took the other side (sold a combo back, or bought No)", [r for r in rows if not r["tyes"]], lambda r: r["kind"])
    # price against the legs
    pr = [r for r in yes if r["prod"] is not None and r["prod"] > 0]
    L += ["## The price against the legs", "",
          f"For {len(pr):,} Yes trades every leg had a price that minute. Legs multiplied is a fair price only when legs "
          "don't lean on each other (legs from one game do, and so do coins in the same 15 minutes).", "",
          "| | trades | buyers paid | legs multiplied were worth | combo really paid back |", "|---|---|---|---|---|"]
    for name, g in (("every leg a different game, sports", [r for r in pr if r["kind"] == "sports and other" and not r["same"]]),
                    ("same-game legs, sports", [r for r in pr if r["kind"] == "sports and other" and r["same"]]),
                    ("crypto 15-min", [r for r in pr if r["kind"] == "crypto 15-min"])):
        if g:
            p_ = sum(r["paid"] for r in g)
            L.append(f"| {name} | {len(g):,} | $100 | {usd(100 * sum(r['n'] * r['prod'] for r in g) / p_)} | "
                     f"{usd(100 * sum(r['n'] * r['sv'] for r in g) / p_)} |")
    L += [""]
    # undercut house
    L += ["## Our own house rule: legs multiplied plus a margin", "",
          "The Polymarket rule (combos.py): 2-4 legs, no two legs from one game, price = legs multiplied + 5%, and we only "
          "get the trade when that is cheaper for the buyer than what the pro really charged.", "",
          "| margin | trades we would have won | of how many asked | house profit per $100 locked | per $100 of tickets | house won |",
          "|---|---|---|---|---|---|"]
    base = [r for r in yes if r["prod"] is not None and not r["same"] and 2 <= r["nlegs"] <= 4]
    cards = []
    for mg in (0.02, 0.05, 0.10):
        g = undercut(yes, mg)
        if g:
            net = sum(r["back"] - r["cost"] - r["mfee"] for r in g)
            L.append(f"| +{mg * 100:.0f}% | {len(g):,} | {len(base):,} | {usd(per100(g))} | {usd(100 * net / sum(r['paid'] for r in g))} | "
                     f"{sum(1 for r in g if r['back'] > r['cost']):,} of {len(g):,} |")
    L += [""]
    # time locked
    L += ["## How long is the money locked?", "", "| kind | middle | longest quarter from |", "|---|---|---|"]
    for k in ("crypto 15-min", "sports and other", "mixed with crypto"):
        g = sorted(r["lock"] for r in yes if r["kind"] == k)
        if g:
            f = lambda s_: f"{s_ / 60:.0f} min" if s_ < 7200 else f"{s_ / 3600:.1f} hours"
            L.append(f"| {k} | {f(q(g, .5))} | {f(q(g, .75))} |")
    L += [""]
    if score == "1":
        L += ["## The shared exam", "", "```"]
        tries = 20
        for name, g in (("Kalshi combo house: every Yes trade the pros sold", yes),
                        ("Kalshi combo house: sports, every leg a different game", [r for r in yes if r["kind"] == "sports and other" and not r["same"]]),
                        ("Kalshi combo house: crypto 15-min combos", [r for r in yes if r["kind"] == "crypto 15-min"]),
                        ("Kalshi combo house: our rule, legs x 1.05, 2-4 legs", undercut(yes, 0.05))):
            if g:
                c = exam.score(bets(g), name, tries=tries, src="kcombos.py", note="house side of real Kalshi combo trades, after the maker fee")
                cards.append(c)
                L += [exam.card_text(c), ""]
        L += ["```", ""]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT + ".tables", "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


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




def selftest():
    """Offline: two made-up combo trades, checked by hand."""
    global CACHE
    import tempfile
    CACHE = tempfile.mkdtemp()
    d0 = 1795000000 // DAY * DAY
    leg = lambda ev, res, exp: {"ev": ev, "q": "", "res": res, "sv": 1.0 if res == "yes" else 0.0, "close": exp, "exp": exp, "open": d0, "occ": exp}
    sl = {"a": d0 + 100, "b": d0 + 160, "cov": d0 + 100, "seen": 1000, "done": True, "n_all": 2,
          "tr": [[d0 + 130, "KXMVE-A", 0.30, 10.0, 1, 0], [d0 + 131, "KXMVE-B", 0.50, 4.0, 1, 0]],
          "combos": {"KXMVE-A": {"legs": [["KXG-1-A", 1], ["KXG-2-B", 0]], "res": "no", "sv": 0.0, "close": d0 + 500, "set": d0 + 505, "open": d0, "col": "c", "st": "finalized"},
                     "KXMVE-B": {"legs": [["KXG-1-A", 1], ["KXT-1-X", 1]], "res": "yes", "sv": 1.0, "close": d0 + 900, "set": d0 + 905, "open": d0, "col": "c", "st": "finalized"}},
          "legs": {"KXG-1-A": leg("KXG-1", "yes", d0 + 800), "KXG-2-B": leg("KXG-2", "yes", d0 + 400), "KXT-1-X": leg("KXT-1", "yes", d0 + 900)},
          "min": {"KXG-1-A": [[d0 + 120, 0.59, 0.61, None]], "KXG-2-B": [[d0 + 120, 0.49, 0.51, None]], "KXT-1-X": [[d0 + 120, 0.79, 0.81, None]]}}
    wj(day_path(d0), {"d0": d0, "slices": [sl]})
    rows, skip = rows_of(load())
    assert len(rows) == 2 and not skip, (rows, skip)
    a, b = rows
    assert abs(a["cost"] - 7.0) < 1e-9 and abs(a["back"] - 10.0) < 1e-9 and abs(a["prod"] - 0.30) < 1e-9 and not a["same"]
    assert abs(b["cost"] - 2.0) < 1e-9 and b["back"] == 0 and b["same"] and abs(b["prod"] - 0.48) < 1e-9
    assert abs(a["mfee"] - 0.0735) < 1e-9
    u = undercut(rows, 0.0)
    assert not u, u            # A: 0.30 is not below 0.30; B is a same-game pair
    sl["tr"][0][2] = 0.40
    wj(day_path(d0), {"d0": d0, "slices": [sl]})
    u = undercut(rows_of(load())[0], 0.05)
    assert len(u) == 1 and abs(u[0]["q"] - 0.315) < 1e-9 and abs(u[0]["cost"] - 6.85) < 1e-9
    run("0")
    print("kcombos selftest OK")


def trial():
    global CACHE
    CACHE = "/tmp/kcb_trial"
    fetch("1", "2")
    stat()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch, "stat": stat, "trial": trial, "run": run, "selftest": selftest}[cmd](*sys.argv[2:])
