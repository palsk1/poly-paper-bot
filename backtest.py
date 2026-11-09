#!/usr/bin/env python3
"""Backtester: replays the bot's own strategy code on months of already-finished Polymarket markets.

PAPER ONLY. It reads public history and never trades.

    python3 backtest.py fetch    # download closed markets, price history and wallet trades into bt_cache/
    python3 backtest.py run      # replay every strategy, write backtest/report.md, results.json, trades.csv
    python3 backtest.py all      # both
    python3 backtest.py selftest # offline check on made-up markets (no network)

How it stays honest
- It calls the bot's real picking code (bot.boring_side_candidates, momentum_candidates, panic_candidates,
  endgame_candidates, buy_candidates, paper_buy/paper_close, trust) with the clock set back to each moment, so the
  backtest follows the same rules as the live tracks. Only the data feed is swapped for history.
- At each moment it only sees prices up to that moment. Markets enter the pool only if they were open then.
- New entries stop max_days before the data ends, so every market a track could have picked has had its chance to
  finish (otherwise only the quick ones would count).
- Fills: the historical price plus a slippage of 0, 1 or 2 cents (history has no order book), plus the market's own
  taker fee. 1c is the main case.

What it cannot see (said again in the report)
- No order-book depth or liquidity at the time (uses the market's final volume instead, which flatters a little).
- No UMA "proposed/resolved" history, so endgame's resolved/proposed tiers can't be replayed; only the
  past-deadline and ending-soon signals can. every_horse and arb need old order books / Kalshi pairs: not replayed.
- Copy tracks use the wallets' own trade prices plus 1c. The 40 lab wallets were picked on 2026-11-08 BECAUSE they
  were profitable over this same period, so their backtest is flattering by construction (in-sample).
"""
import bisect
import datetime as dt
import gzip
import heapq
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import bot

G, C, D = bot.GAMMA, bot.CLOB, bot.DATA
ROOT = bot.ROOT
CACHE = os.path.join(ROOT, "bt_cache")
OUT = os.path.join(ROOT, "backtest")
START = os.environ.get("BT_START", "2026-03-01")
VOL_MIN = float(os.environ.get("BT_VOL_MIN", "20000"))
WORKERS = int(os.environ.get("BT_WORKERS", "10"))
FETCH_MIN = float(os.environ.get("BT_FETCH_MIN", "150"))  # stop downloading after this, so the replay still fits in the job
FETCH_T0 = time.time()
MAIN_SLIP = 0.01
SLIPS = (0.0, 0.01, 0.02)
DAILY_HOUR = 5          # the daily job runs ~05:17 UTC
PANIC_EVERY_H = 2
STALE_H = 72            # past-deadline endgame: skip markets whose price hasn't moved for 3 days
UTC = dt.timezone.utc

RULE_SOURCES = ("screener", "random", "momentum", "panic", "endgame")
COPY_SOURCES = ("leader", "wallet")


def ts(d):
    return int(d.timestamp())


def utc(t):
    return dt.datetime.fromtimestamp(t, UTC)


def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as fh:
        json.dump(obj, fh, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def rjson(path, default=None):
    if not os.path.exists(path):
        return default
    with gzip.open(path, "rt") as fh:
        return json.load(fh)


# ================================================================ fetch

def slim_market(m):
    """The few fields the replay needs, from a Gamma market."""
    toks = bot.market_tokens(m)
    outs = bot.jlist(m.get("outcomes"))
    prices = [bot.fnum(x, None) for x in bot.jlist(m.get("outcomePrices"))]
    end = bot.parse_iso(m.get("endDate") or m.get("endDateIso"))
    start = bot.parse_iso(m.get("startDate") or m.get("createdAt"))
    closed_t = None
    if m.get("closed"):  # "2026-11-06 01:12:34.31628+00"; older markets may only have umaEndDate or the end date
        raw = str(m.get("closedTime") or m.get("umaEndDate") or "").replace(" ", "T").split("+")[0]
        closed_t = bot.parse_iso(raw + "Z") if raw else end
    ev = (m.get("events") or [{}])[0] if isinstance((m.get("events") or [{}])[0], dict) else {}
    return {"id": str(m.get("id")), "q": str(m.get("question") or ""), "outs": [str(o) for o in outs], "toks": toks,
            "end": ts(end) if end else None, "start": ts(start) if start else None,
            "closed": bool(m.get("closed")), "closed_t": ts(closed_t) if closed_t else None,
            "final": prices, "uma": m.get("umaResolutionStatus") or m.get("resolutionStatus"),
            "vol": bot.fnum(bot.pick(m, "volumeNum", "volume")), "fee": bot.fee_rate(m), "sports": bot.is_sports(m),
            "slug": str(m.get("slug") or ""), "ev": str(ev.get("id") or ev.get("slug") or m.get("slug")),
            "ev_slug": str(ev.get("slug") or "")}


def fetch_day(day, closed):
    lo, hi = day, day + dt.timedelta(days=1)
    out, cur = [], None
    for _ in range(100):
        p = {"closed": "true" if closed else "false", "limit": 500, "end_date_min": bot.iso(lo), "end_date_max": bot.iso(hi),
             "volume_num_min": VOL_MIN}
        if cur:
            p["after_cursor"] = cur
        res = bot.http_json(f"{G}/markets/keyset", p)
        rows = [m for m in bot.envelope_rows(res, "markets", "data") if isinstance(m, dict)]
        out += rows
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not cur or not rows:
            break
    return out


def fetch_markets():
    path = os.path.join(CACHE, "markets.json.gz")
    have = rjson(path, {"days": {}, "markets": {}})
    start = dt.datetime.fromisoformat(START).replace(tzinfo=UTC)
    today = bot.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days = []
    d = start
    while d <= today:
        k = d.strftime("%Y-%m-%d")
        # closed lists for days older than 40 days don't change much; recent days are re-read every run
        if k not in have["days"] or (today - d).days < 40:
            days.append(d)
        d += dt.timedelta(days=1)

    def one(d):
        rows = fetch_day(d, True) + fetch_day(d, False)
        return d, rows

    n_raw = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for d, rows in ex.map(one, days):
            n_raw += len(rows)
            kept = 0
            for m in rows:
                s = slim_market(m)
                if len(s["toks"]) != 2 or len(s["final"]) != 2 or not s["end"] or s["sports"]:
                    continue
                have["markets"][s["id"]] = s
                kept += 1
            have["days"][d.strftime("%Y-%m-%d")] = kept
            if len(rows) >= 2000:
                print(f"  {d:%Y-%m-%d}: {len(rows)} rows, may be capped")
    wjson(path, have)
    print(f"markets: read {n_raw} rows for {len(days)} days, {len(have['markets'])} binary non-sports markets cached")
    return have["markets"]


def squeeze(pts, floor_t):
    """Sorted (t, p) with repeats removed, as two compact lists."""
    pts = sorted((int(t), round(float(p), 4)) for t, p in pts if t is not None and p is not None and t >= floor_t)
    T, P = [], []
    for t, p in pts:
        if T and t == T[-1]:
            P[-1] = p
            continue
        if P and p == P[-1]:
            continue
        T.append(t)
        P.append(p)
    return [T, P]


def hist_points(res):
    out = []
    for x in bot.envelope_rows(res, "history", "data"):
        if isinstance(x, dict):
            out.append((bot.pick(x, "t", "timestamp"), bot.fnum(bot.pick(x, "p", "price"), None)))
    return out


def fetch_history(mk):
    """Price of outcome 0: twice a day over its life, hourly from 2 days before the end date to 12 days after."""
    tok = mk["toks"][0]
    floor_t = ts(dt.datetime.fromisoformat(START).replace(tzinfo=UTC)) - 10 * 86400
    pts = []
    try:
        pts += hist_points(bot.http_json(f"{C}/prices-history", {"market": tok, "interval": "max", "fidelity": 720}))
    except Exception as e:
        print(f"  12h history failed {mk['id']}: {e}")
    s = mk["end"] - 2 * 86400
    e = min(mk["closed_t"] or ts(bot.now()), mk["end"] + 12 * 86400, ts(bot.now()))
    if e > s:
        try:
            pts += hist_points(bot.http_json(f"{C}/prices-history", {"market": tok, "startTs": s, "endTs": e, "fidelity": 60}))
        except Exception as ex:
            print(f"  hourly history failed {mk['id']}: {ex}")
    return mk["id"], squeeze(pts, floor_t)


def fetch_histories(markets):
    path = os.path.join(CACHE, "hist.json.gz")
    hist = rjson(path, {})
    # re-read markets that were still open last time (their history has grown)
    todo = [m for m in markets.values() if m["id"] not in hist or not m["closed"] or m["id"] in hist and not hist[m["id"]][0]]
    print(f"history: {len(hist)} cached, {len(todo)} to fetch")
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as ex:
        for c in range(0, len(todo), 2000):
            if time.time() - FETCH_T0 > FETCH_MIN * 60:
                print(f"  time budget ({FETCH_MIN} min) used up: {len(todo) - c} histories left for the next run")
                break
            for mid, h in ex.map(fetch_history, todo[c:c + 2000]):
                hist[mid] = h
            print(f"  {min(c + 2000, len(todo))}/{len(todo)} ({time.time() - t0:.0f}s)")
            wjson(path, hist)
    wjson(path, hist)
    return hist


def wallet_trades(addr, max_pages=60):
    rows, cur = [], None
    for _ in range(max_pages):
        p = {"user": addr, "limit": 500}
        if cur:
            p["cursor"] = cur
        res = bot.http_json(f"{D}/v2/trades", p)
        rows += bot.envelope_rows(res, "data", "trades")
        cur = ((res.get("pagination") or {}) if isinstance(res, dict) else {}).get("next_cursor")
        if not cur:
            break
    out = []
    for r in rows:
        t = bot.act_time(r)
        sh, px = bot.fnum(bot.pick(r, "size", "shares")), bot.fnum(bot.pick(r, "price"))
        tok = str(bot.pick(r, "token_id", "asset", default=""))
        if not t or not tok or sh <= 0 or not 0 < px < 1:
            continue
        out.append([ts(t), tok, str(bot.pick(r, "side", default="")).upper(), round(sh, 4), round(px, 4),
                    str(bot.pick(r, "slug", default="")), str(bot.pick(r, "outcome", default="")),
                    str(bot.pick(r, "title", default=""))[:120], str(bot.pick(r, "event_slug", default=""))])
    return addr, out, bool(cur)


def fetch_wallets():
    addrs = sorted({bot.CFG["leader"]["address"].lower()} |
                   {tc["address"].lower() for tc in bot.CFG["tracks"].values() if tc.get("source") == "wallet"})
    with ThreadPoolExecutor(6) as ex:
        got = list(ex.map(wallet_trades, addrs))
    trades = {a: rows for a, rows, _ in got}
    for a, rows, more in got:
        print(f"  wallet {a[:10]}: {len(rows)} trades{' (page cap hit, older ones missing)' if more else ''}")
    slugs = sorted({r[5] for rows in trades.values() for r in rows if r[5]})
    path = os.path.join(CACHE, "copy_markets.json.gz")
    mk = rjson(path, {})
    todo = [s for s in slugs if s not in mk or not mk[s] or not mk[s].get("closed")]
    print(f"copy markets: {len(slugs)} slugs, {len(todo)} to look up")

    def look(s):
        m = bot.market_by_slug(s)
        return s, slim_market(m) if m else None

    with ThreadPoolExecutor(WORKERS) as ex:
        for s, v in ex.map(look, todo):
            mk[s] = v
    wjson(path, mk)
    wjson(os.path.join(CACHE, "wallet_trades.json.gz"), trades)
    return trades, mk


def fetch():
    t0 = time.time()
    markets = fetch_markets()
    fetch_histories(markets)
    fetch_wallets()
    print(f"fetch done in {time.time() - t0:.0f}s")


# ================================================================ replay plumbing

class Feed:
    """Historical prices of outcome 0 per market id."""

    def __init__(self, hist):
        self.h = hist

    def at(self, mid, t):
        h = self.h.get(mid)
        if not h or not h[0]:
            return None
        i = bisect.bisect_right(h[0], t) - 1
        return h[1][i] if i >= 0 else None

    def last_move(self, mid, t):
        """When the price last changed at or before t (repeats are squeezed out, so this is the last real move)."""
        h = self.h.get(mid)
        if not h or not h[0]:
            return None
        i = bisect.bisect_right(h[0], t) - 1
        return h[0][i] if i >= 0 else None

    def first_t(self, mid):
        h = self.h.get(mid)
        return h[0][0] if h and h[0] else None


def iso_t(t):
    return utc(t).strftime("%Y-%m-%dT%H:%M:%SZ")


def pseudo(mk, p0, extra=None):
    """A Gamma-shaped market as it looked at the replay moment (price p0 for outcome 0)."""
    m = {"id": mk["id"], "question": mk["q"], "outcomes": json.dumps(mk["outs"]), "clobTokenIds": json.dumps(mk["toks"]),
         "outcomePrices": json.dumps([str(p0), str(round(1 - p0, 6))]), "endDate": iso_t(mk["end"]),
         "endDateIso": iso_t(mk["end"]), "closed": False, "active": True, "acceptingOrders": True,
         "liquidityNum": 1e12,  # unknown in history: liquidity filters can't be replayed
         "volumeNum": mk["vol"], "slug": mk["slug"], "events": [{"id": mk["ev"], "slug": mk["ev_slug"]}],
         "feesEnabled": mk["fee"] > 0, "feeSchedule": {"rate": mk["fee"]}, "umaResolutionStatuses": "[]"}
    m.update(extra or {})
    return m


def payout(mk, tok_i):
    """Final payout per share for outcome tok_i, or None while unsettled (bot.resolved_payout's rules)."""
    if not mk["closed"] or tok_i >= len(mk["final"]) or mk["final"][tok_i] is None:
        return None
    p = mk["final"][tok_i]
    if p >= 0.99:
        return 1.0
    if p <= 0.01:
        return 0.0
    if mk.get("uma") == "resolved":
        return p
    return None


class Clock:
    t = 0
    real_now = None  # the true time, kept before the bot's clock is pointed at the replay


def patch_bot(slip):
    """Point the bot's clock and data calls at the replay. Nothing is written to state/ and nothing is pushed."""
    if Clock.real_now is None:
        Clock.real_now = bot.now()
    bot.now = lambda: utc(Clock.t)
    bot.print = lambda *a, **k: None  # the bot's own chatter (scan counts) would flood the log
    bot.log_event = lambda ev: None
    bot.push = lambda *a, **k: None
    bot.save = lambda *a, **k: None
    bot.load = lambda name, default: default

    def quote(token, side, shares, m=None):
        px = bot.token_price_from_market(m, token) if m else None
        if px is None:
            return None, shares, "none"
        px = min(0.999, px + slip) if side == "buy" else max(0.001, px - slip)
        return px, shares, "history"
    bot.quote = quote


def fresh_tracks(names, uncapped=False):
    tracks = {}
    for n in names:
        start = None if uncapped else bot.CFG["tracks"][n]["start_cash"]
        tracks[n] = {"unlimited": start is None, "cash": 0.0 if start is None else float(start), "start_cash": start,
                     "deposited": 0.0 if start is None else float(start), "refills": 0, "min_cash": 0.0,
                     "peak_open_cost": 0.0, "positions": {}, "closed": [], "realized": 0.0, "skipped_no_cash": 0,
                     "created": bot.iso()}
    return tracks


# ================================================================ rule tracks

def rule_names():
    return [n for n, tc in bot.CFG["tracks"].items() if tc["source"] in RULE_SOURCES]


def replay_rules(markets, feed, slip, uncapped=False, names=None):
    """Hour-by-hour replay of the rule tracks. Returns the paper tracks."""
    patch_bot(slip)
    names = names or rule_names()
    saved_rules = json.loads(json.dumps(bot.CFG["rules"]))
    saved_tracks = json.loads(json.dumps(bot.CFG["tracks"]))
    if uncapped:  # rule evidence: no cash limit, no cap on open positions, same picks per day
        for n in names:
            bot.CFG["tracks"][n]["start_cash"] = None
            bot.CFG["tracks"][n].pop("refill", None)
        for k in bot.CFG["rules"]:
            bot.CFG["rules"][k]["max_open"] = 100000
    try:
        return _replay_rules(markets, feed, names, uncapped)
    finally:
        bot.CFG["rules"] = saved_rules
        bot.CFG["tracks"] = saved_tracks


def _replay_rules(markets, feed, names, uncapped):
    mks = [m for m in markets.values() if feed.first_t(m["id"]) is not None]
    by_tok = {tok: (m, i) for m in mks for i, tok in enumerate(m["toks"])}
    by_end = sorted(mks, key=lambda m: m["end"])
    ends = [m["end"] for m in by_end]
    data_end = max((m["closed_t"] or 0) for m in mks) if mks else 0
    data_end = min(data_end, ts(Clock.real_now))
    t_start = ts(dt.datetime.fromisoformat(START).replace(tzinfo=UTC)) + 8 * 86400
    t_end = int(time.time()) if not mks else max(m["end"] for m in mks)
    t_end = min(t_end, data_end)
    tracks = fresh_tracks(names, uncapped)
    rules = {n: bot.rules_for(n) for n in names}
    last_entry = {n: data_end - (rules[n].get("max_days", 12) + 3) * 86400 for n in names}
    src = {n: bot.CFG["tracks"][n]["source"] for n in names}
    open_at = lambda m, t: m["end"] > t and (m["closed_t"] is None or m["closed_t"] > t) and \
        (m["start"] or 0) <= t and feed.first_t(m["id"]) <= t

    def universe(t, lo_days, hi_days, extra_fn=None, pre=None):
        i0 = bisect.bisect_left(ends, t + lo_days * 86400)
        i1 = bisect.bisect_right(ends, t + hi_days * 86400)
        out = []
        for m in by_end[i0:i1]:
            if not open_at(m, t):
                continue
            p0 = feed.at(m["id"], t)
            if p0 is None or not 0 < p0 < 1:
                continue
            if pre and not pre(m, p0):
                continue
            out.append(pseudo(m, p0, extra_fn(m, p0) if extra_fn else None))
        return out

    def endgame_universe(t, f):
        lo, hi = ts(bot.parse_iso(f["end_date_min"])), ts(bot.parse_iso(f["end_date_max"]))
        out = []
        for m in by_end[bisect.bisect_left(ends, lo):bisect.bisect_right(ends, hi)]:
            if (m["start"] or 0) > t or (m["closed_t"] is not None and m["closed_t"] <= t):
                continue
            p0 = feed.at(m["id"], t)
            if p0 is None or not 0.01 < max(p0, 1 - p0) < 0.999 or max(p0, 1 - p0) < 0.9:
                continue
            if m["end"] < t and t - feed.last_move(m["id"], t) > STALE_H * 3600:
                continue  # past its end date with no price move for days: trading has most likely stopped
            out.append(pseudo(m, p0))
        return out

    daily = [n for n in names if src[n] in ("screener", "random", "momentum")]
    panic = [n for n in names if src[n] == "panic"]
    endg = [n for n in names if src[n] == "endgame"]
    d_lo = min([rules[n]["min_days"] for n in daily] or [0])
    d_hi = max([rules[n]["max_days"] for n in daily] or [0])
    p_lo = min([rules[n]["min_days"] for n in panic] or [0])
    p_hi = max([rules[n]["max_days"] for n in panic] or [0])
    p_drop = min([rules[n]["min_drop"] for n in panic] or [1])

    settle_q, watched = [], {n: set() for n in names}

    def buy(n, cands, k):
        tr, r = tracks[n], rules[n]
        before = set(tr["positions"])
        bot.buy_candidates(tracks, n, cands, k)
        for tok in set(tr["positions"]) - before:
            m, _ = by_tok[tok]
            if m["closed_t"] is not None:
                heapq.heappush(settle_q, (m["closed_t"], n, tok))
            pos = tr["positions"][tok]
            if pos.get("target") or pos.get("stop") or r.get("take_profit") or r.get("stop_loss"):
                watched[n].add(tok)

    t = t_start - t_start % 3600
    steps = 0
    while t <= t_end:
        Clock.t = t
        hour = utc(t).hour
        # ---- exits first: payouts, then take-profit / stop-loss
        while settle_q and settle_q[0][0] <= t:
            ct, n, tok = heapq.heappop(settle_q)
            tr = tracks[n]
            if tok in tr["positions"]:
                m, i = by_tok[tok]
                pay = payout(m, i)
                if pay is not None:
                    rec = bot.paper_close(tr, n, tok, pay, 0.0, "resolved")
                    rec["closed_at"] = iso_t(ct)
        for n in names:
            tr, r = tracks[n], rules[n]
            for tok in list(watched[n]):
                pos = tr["positions"].get(tok)
                if not pos:
                    watched[n].discard(tok)
                    continue
                m, i = by_tok[tok]
                p0 = feed.at(m["id"], t)
                if p0 is None:
                    continue
                px = p0 if i == 0 else 1 - p0
                target = pos.get("target") or r.get("take_profit")
                stop = pos.get("stop") or r.get("stop_loss")
                why = "take profit" if target and px >= target else "stop loss" if stop and px <= stop else None
                if why:
                    fill, _, _ = bot.quote(tok, "sell", pos["shares"], pseudo(m, p0))
                    bot.paper_close(tr, n, tok, fill, bot.taker_fee(pos["shares"], fill, m["fee"]), why)
                    watched[n].discard(tok)
        # ---- daily picks
        if hour == DAILY_HOUR and daily:
            day = utc(t).strftime("%Y-%m-%d")
            week = t - 7 * 86400

            def wk(m, p0):
                p7 = feed.at(m["id"], week)
                return {"oneWeekPriceChange": None if p7 is None else round(p0 - p7, 4)}
            uni = universe(t, d_lo, d_hi, wk)
            for n in daily:
                if t > last_entry[n]:
                    continue
                r = rules[n]
                if src[n] == "momentum":
                    cands = bot.momentum_candidates([m for m in uni if m["oneWeekPriceChange"] is not None], r)
                else:
                    cands = bot.boring_side_candidates(uni, r, random.Random(f"{day}-{n}"))
                buy(n, cands, r.get("picks_per_day", 1))
        # ---- panic scans every 2 hours
        if panic and hour % PANIC_EVERY_H == 0:
            ago = t - 86400
            dc = {}

            def drop(m, p0):
                p1 = feed.at(m["id"], ago)
                if p1 is None or abs(p0 - p1) < p_drop:
                    return False
                dc[m["toks"][0]] = (p1, p0)
                dc[m["toks"][1]] = (1 - p1, 1 - p0)
                return True
            uni = universe(t, p_lo, p_hi, lambda m, p0: {"oneDayPriceChange": round(p0 - dc[m["toks"][0]][0], 4)}, drop)
            bot.day_change = lambda tok: dc.get(tok)
            for n in panic:
                if t <= last_entry[n]:
                    buy(n, bot.panic_candidates(uni, rules[n]), rules[n].get("picks_per_scan", 1))
        # ---- endgame scans (live: every 5 min; here: every hour)
        if endg:
            cache = {}

            def scan(f=None):
                k = json.dumps(f, sort_keys=True)
                if k not in cache:
                    cache[k] = endgame_universe(t, f)
                return cache[k]
            bot.scan_markets = scan
            for n in endg:
                if t <= last_entry[n]:
                    buy(n, bot.endgame_candidates(rules[n]), rules[n].get("picks_per_scan", 2))
        t += 3600
        steps += 1
    for n in names:
        tracks[n]["_window"] = [iso_t(t_start), iso_t(min(last_entry[n], t_end)), iso_t(t_end)]
    return tracks


# ================================================================ copy tracks

def copy_names():
    # backfill twins (wb_*) only differ by a one-off buy of what the wallet held on their start day: nothing to replay
    return [n for n, tc in bot.CFG["tracks"].items() if tc["source"] in COPY_SOURCES and not tc.get("backfill")]


def replay_copies(trades, cmk, slip):
    """Replays leader + wallet copy tracks from the wallets' own trade history."""
    patch_bot(slip)
    names = copy_names()
    tracks = fresh_tracks(names)
    lead = bot.CFG["leader"]
    wr = bot.rule_set("wallet_copy")
    events = []  # (t, kind, payload)
    by_addr = defaultdict(list)
    for n in names:
        tc = bot.CFG["tracks"][n]
        addr = (tc.get("address") or lead["address"]).lower()
        by_addr[addr].append(n)
    for addr, rows in trades.items():
        for r in rows:
            events.append((r[0], 0, addr, r))
    settle = {}
    for s, mk in cmk.items():
        if mk and mk.get("closed_t"):
            settle[s] = mk["closed_t"]
    data_end = max((r[0] for rows in trades.values() for r in rows), default=0)
    events.sort(key=lambda e: (e[0], e[1]))
    size = defaultdict(float)       # (addr, tok) -> shares held (from trades only)
    cost = defaultdict(float)
    appeared = {}                   # (addr, tok) -> (t first seen, [buys within 5 min])
    their_size = {}                 # (name, tok) -> their size when we copied
    day_n = defaultdict(int)        # (name, day) -> opens
    pos_mk = {}                     # tok -> (market, index)
    pending = []                    # heap-ish list of (closed_t, name, tok)

    def settle_until(t):
        for n in names:
            tr = tracks[n]
            for tok in list(tr["positions"]):
                mk, i = pos_mk[tok]
                if mk.get("closed_t") and mk["closed_t"] <= t:
                    pay = payout(mk, i)
                    if pay is not None:
                        Clock.t = mk["closed_t"]
                        rec = bot.paper_close(tr, n, tok, pay, 0.0, "resolved")
                        rec["closed_at"] = iso_t(mk["closed_t"])

    def try_copy(addr, tok, t, r):
        held, avg = size[(addr, tok)], cost[(addr, tok)] / max(size[(addr, tok)], 1e-9)
        mk = cmk.get(r[5])
        if not mk or tok not in mk["toks"] or held < 5:
            return
        i = mk["toks"].index(tok)
        if mk["end"] and mk["end"] < t or (mk.get("closed_t") and mk["closed_t"] <= t):
            return
        Clock.t = t
        px = min(0.999, avg + slip)
        fee = bot.taker_fee(bot.CFG["shares_per_trade"], px, mk["fee"])
        for n in by_addr[addr]:
            tc, tr = bot.CFG["tracks"][n], tracks[n]
            if tok in tr["positions"]:
                continue
            if tc["source"] == "leader":
                lo, hi = tc["min_price"], tc["max_price"]
                min_usd = tc.get("min_open_usd", lead["min_open_usd"])
                cap, day_cap = 10 ** 9, 10 ** 9
            else:
                lo, hi, min_usd = wr["min_price"], wr["max_price"], wr["min_open_usd"]
                cap, day_cap = wr.get("max_open", 999), wr.get("max_new_per_day", 999)
            if held * max(avg, 0.01) < min_usd or not lo <= px <= hi:
                continue
            day = utc(t).strftime("%Y-%m-%d")
            if len(tr["positions"]) >= cap or day_n[(n, day)] >= day_cap:
                continue
            meta = {"title": r[7], "outcome": mk["outs"][i] if i < len(mk["outs"]) else r[6], "slug": r[5],
                    "event_slug": r[8], "end": iso_t(mk["end"]) if mk["end"] else "", "source": n,
                    "their_avg": round(avg, 4), "their_size": held, "price_source": "their price + slippage"}
            if bot.paper_buy(tr, n, tok, bot.CFG["shares_per_trade"], px, fee, meta):
                day_n[(n, day)] += 1
                their_size[(n, tok)] = held
                pos_mk[tok] = (mk, i)

    for t, _, addr, r in events:
        settle_until(t)
        tok, side, sh, px = r[1], r[2], r[3], r[4]
        k = (addr, tok)
        before = size[k]
        if side == "BUY":
            size[k] += sh
            cost[k] += sh * px
            if before < 1:
                appeared[k] = t
            if k in appeared and t - appeared[k] <= 300:  # the bot looks every 5 minutes
                try_copy(addr, tok, appeared[k] + 300, r)
        elif side == "SELL":
            if before > 0:
                cost[k] *= max(before - sh, 0) / before
            size[k] = max(before - sh, 0.0)
            for n in by_addr[addr]:
                tr = tracks[n]
                if tok not in tr["positions"] or bot.CFG["tracks"][n].get("hold_to_end"):
                    continue
                if size[k] <= 0.2 * their_size.get((n, tok), before):
                    mk, i = pos_mk[tok]
                    Clock.t = t + 300
                    fill = max(0.001, px - slip)
                    bot.paper_close(tr, n, tok, fill, bot.taker_fee(tr["positions"][tok]["shares"], fill, mk["fee"]),
                                    "wallet exit")
            if size[k] < 1:
                appeared.pop(k, None)
    settle_until(ts(Clock.real_now))
    for n in names:
        tracks[n]["_window"] = [iso_t(min((e[0] for e in events), default=0)), iso_t(data_end), iso_t(data_end)]
    return tracks


# ================================================================ report

TOPICS = (("weather", ("temperature", "rain", "snow")), ("crypto price", ("bitcoin", "ethereum", "solana", "xrp", "btc", "eth ")),
          ("post counts", ("tweets", " posts ")), ("box office", ("box office", "opening weekend")))


def topic(title):
    t = title.lower()
    for name, words in TOPICS:
        if any(w in t for w in words):
            return name
    return "other"


def stats_for(tr, n_tracks):
    closed = tr["closed"]
    won = sum(1 for c in closed if c["pnl"] > 0)
    lost = sum(1 for c in closed if c["pnl"] <= 0)
    tru = bot.trust(tr, n_tracks)
    days = [(bot.parse_iso(c["closed_at"]) - bot.parse_iso(c["opened"])).total_seconds() / 86400 for c in closed
            if c.get("closed_at") and c.get("opened")]
    big = sorted(closed, key=lambda c: c["pnl"])[:1]
    tiers = defaultdict(lambda: [0, 0, 0.0])
    for c in closed:
        x = tiers[c.get("tier") or "-"]
        x[0] += 1
        x[1] += c["pnl"] < 0
        x[2] = round(x[2] + c["pnl"], 4)
    topics = defaultdict(lambda: [0, 0, 0.0])
    for c in closed:
        x = topics[topic(c.get("title") or "")]
        x[0] += 1
        x[1] += c["pnl"] < 0
        x[2] = round(x[2] + c["pnl"], 4)
    opened = sorted(c["opened"] for c in closed if c.get("opened"))
    mid = opened[len(opened) // 2] if opened else ""
    halves = [round(sum(c["pnl"] for c in closed if (c.get("opened") or "") < mid), 2),
              round(sum(c["pnl"] for c in closed if (c.get("opened") or "") >= mid), 2)]
    return {"finished": len(closed), "won": won, "lost": lost, "open": len(tr["positions"]),
            "profit": round(sum(c["pnl"] for c in closed), 2),
            "staked": round(sum(c["shares"] * c["entry"] + c.get("entry_fee", 0) for c in closed), 2),
            "avg_days": round(sum(days) / len(days), 1) if days else None,
            "peak_money": round(tr["peak_open_cost"], 2), "refills": tr.get("refills", 0),
            "skipped_no_cash": tr.get("skipped_no_cash", 0), "trust": tru, "tiers": dict(tiers), "topics": dict(topics), "halves": halves, "window": tr.get("_window"),
            "worst_trade": {k: big[0].get(k) for k in ("title", "outcome", "entry", "exit", "pnl")} if big else None}


def verdict(s):
    t = s["trust"]
    if s["finished"] < 10:
        return "too few trades"
    if t["proven"]:
        return "HOLDS UP"
    if s["profit"] > 0 and t["worst_per_100"] > -10:
        return "promising, not proven"
    if s["profit"] > 0:
        return "ahead, but could be luck"
    return "loses"


def money(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.2f}"


def write_report(res, meta):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump({"meta": meta, "results": res}, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    main = res["capped_1c"]
    unl = res["uncapped_1c"]
    unl0, unl2 = res["uncapped_0c"], res["uncapped_2c"]
    cop = res["copy_1c"]
    L = [f"# Backtest: the strategies on past Polymarket markets",
         "",
         f"Generated {meta['generated']}. Markets that ended {meta['start']} to {meta['data_end'][:10]}: "
         f"{meta['markets']:,} finished yes/no markets (no sports, volume over ${VOL_MIN:,.0f}). "
         f"Paper only. Rerun: `probe` workflow with `btrun` (or `python3 backtest.py all`).",
         "",
         "**How to read it.** Each rule track was replayed with its real picking code, hour by hour, seeing only "
         "prices up to that moment. Fill = the price then **plus 1c** (history has no order book) plus the market's "
         "taker fee. \"Worst plausible per $100\" is the same trust score the live scoreboard uses (one imaginary total "
         "loss added, 90% bar for the whole family). HOLDS UP = that worst case is above $0 after 30+ trades.",
         "",
         "## Rule tracks, rule only (no cash limit, so every daily pick counts)",
         "",
         "| Track | Trades (won/lost) | Profit | Per $100 bet | Worst plausible per $100 | With 0c / 2c slippage | Older / newer half | Avg days held | Verdict |",
         "|---|---|---|---|---|---|---|---|---|"]
    order = sorted(unl, key=lambda n: -unl[n]["trust"]["worst_per_100"])
    for n in order:
        s = unl[n]
        L.append(f"| `{n}` | {s['finished']} ({s['won']}/{s['lost']}) | {money(s['profit'])} | "
                 f"{money(s['trust']['avg_per_100'])} | {money(s['trust']['worst_per_100'])} | "
                 f"{money(unl0[n]['profit'])} / {money(unl2[n]['profit'])} | {money(s['halves'][0])} / {money(s['halves'][1])} | {s['avg_days'] if s['avg_days'] is not None else '-'} | "
                 f"{verdict(s)} |")
    eg = [n for n in order if bot.CFG["tracks"][n]["source"] == "endgame" and unl[n]["finished"]]
    if eg:
        L += ["", "Endgame by signal (trades / lost / profit): " + "; ".join(
            f"`{n}` " + ", ".join(f"{k} {v[0]}/{v[1]}/{money(v[2])}" for k, v in sorted(unl[n]["tiers"].items()))
            for n in eg)]
    fav = [n for n in order if bot.CFG["tracks"][n]["source"] in ("endgame", "screener") and unl[n]["finished"] >= 100]
    if fav:
        L += ["", "Favorite-style tracks by topic (trades / lost / profit): " + "; ".join(
            f"`{n}` " + ", ".join(f"{k} {v[0]}/{v[1]}/{money(v[2])}" for k, v in sorted(unl[n]["topics"].items()))
            for n in fav)]
    L += ["", "## Rule tracks as configured (real budget and max open)", "",
          "| Track | Budget | Trades (won/lost) | Profit | Most money tied up | Ran out of cash (skips) | Refills | Still open at the end |",
          "|---|---|---|---|---|---|---|---|"]
    for n in order:
        s, tc = main[n], bot.CFG["tracks"][n]
        L.append(f"| `{n}` | {'$' + str(tc['start_cash']) if tc['start_cash'] else 'none'} | {s['finished']} ({s['won']}/{s['lost']}) | "
                 f"{money(s['profit'])} | ${s['peak_money']:,.2f} | {s['skipped_no_cash']} | {s['refills']} | {s['open']} |")
    L += ["", "## Copy tracks (the wallets' own trades, our price = theirs + 1c)", "",
          "**Warning:** the 40 `w_*` wallets were chosen on 2026-11-08 *because* they made money in this same period. "
          "Their backtest is flattering by design. It mainly shows whether copying them a few minutes late still "
          "keeps their edge, not whether they will keep winning.", "",
          "| Track | Trades (won/lost) | Profit | Per $100 bet | Worst plausible per $100 | Most money tied up | Verdict |",
          "|---|---|---|---|---|---|---|"]
    for n in sorted(cop, key=lambda n: -cop[n]["trust"]["worst_per_100"]):
        s = cop[n]
        L.append(f"| `{n}` | {s['finished']} ({s['won']}/{s['lost']}) | {money(s['profit'])} | "
                 f"{money(s['trust']['avg_per_100'])} | {money(s['trust']['worst_per_100'])} | ${s['peak_money']:,.2f} | {verdict(s)} |")
    L += ["", "## Not replayed", "",
          "- `arb`, `every_horse`: need old order books (and Kalshi pairs). No history for those.",
          "- `endgame_strict` and the resolved/proposed tiers: Polymarket doesn't keep when a result was proposed. "
          "Only the past-deadline and ending-soon signals are replayed for the endgame tracks.",
          "- `consensus_2/3`: need all 40 wallets' full books at each moment; not rebuilt yet.\n- `wb_*` (filled-up twins), `maker`, `ladder`, `wx_forecast`, `crypto_late`: added after this backtest, or need order books / outside data.",
          "",
          "## What can make this look better than reality", "",
          "- No order-book depth: at 5 shares that's fine; at $300-500 a trade the price would be worse.",
          "- Volume filter uses each market's final volume (the live bot sees volume so far). Liquidity filters are off.",
          "- Trades on the same day often share one news risk, so they aren't fully independent; the worst-case "
          "number is a bit too kind for the favorite tracks.",
          "- Fees use each market's current fee setting.",
          ""]
    with open(os.path.join(OUT, "report.md"), "w") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


def write_trades(tracks_by_pass):
    import csv
    with open(os.path.join(OUT, "trades.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pass", "track", "opened", "closed_at", "title", "outcome", "entry", "exit", "fee", "pnl", "reason", "tier"])
        for pname, tracks in tracks_by_pass.items():
            for n, tr in tracks.items():
                for c in tr["closed"]:
                    w.writerow([pname, n, c.get("opened"), c.get("closed_at"), c.get("title"), c.get("outcome"),
                                c.get("entry"), c.get("exit"), round(c.get("entry_fee", 0) + c.get("exit_fee", 0), 5),
                                c.get("pnl"), c.get("reason"), c.get("tier", "")])


def run():
    markets = rjson(os.path.join(CACHE, "markets.json.gz"), {})["markets"]
    hist = rjson(os.path.join(CACHE, "hist.json.gz"), {})
    trades = rjson(os.path.join(CACHE, "wallet_trades.json.gz"), {})
    cmk = rjson(os.path.join(CACHE, "copy_markets.json.gz"), {})
    real_now = Clock.real_now or bot.now()
    Clock.real_now = real_now
    feed = Feed(hist)
    res, keep = {}, {}
    n_tracks = len(rule_names()) + len(copy_names())
    for label, slip, unc in (("uncapped_1c", 0.01, True), ("capped_1c", 0.01, False),
                             ("uncapped_0c", 0.0, True), ("uncapped_2c", 0.02, True)):
        t0 = time.time()
        bot.now = lambda: real_now
        trs = replay_rules(markets, feed, slip, unc)
        res[label] = {n: stats_for(tr, n_tracks) for n, tr in trs.items()}
        if label in ("uncapped_1c", "capped_1c"):
            keep[label] = trs
        print(f"{label}: {sum(s['finished'] for s in res[label].values())} finished trades in {time.time() - t0:.0f}s")
    bot.now = lambda: real_now
    trs = replay_copies(trades, cmk, MAIN_SLIP)
    res["copy_1c"] = {n: stats_for(tr, n_tracks) for n, tr in trs.items()}
    keep["copy_1c"] = trs
    bot.now = lambda: real_now
    data_end = max((m["closed_t"] or 0) for m in markets.values())
    meta = {"generated": bot.iso(real_now), "start": START, "data_end": iso_t(min(data_end, ts(real_now))),
            "markets": sum(1 for m in markets.values() if m["id"] in hist and hist[m["id"]][0]),
            "wallet_trades": sum(len(v) for v in trades.values()), "vol_min": VOL_MIN}
    write_report(res, meta)
    write_trades(keep)


# ================================================================ offline selftest

def selftest():
    """Made-up markets: a favorite that pays, a favorite that flips, a panic dip that recovers, an endgame."""
    global CACHE, OUT
    import tempfile
    tmp = tempfile.mkdtemp()
    CACHE, OUT = os.path.join(tmp, "c"), os.path.join(tmp, "o")
    rng = random.Random(1)
    base = ts(dt.datetime.fromisoformat(START).replace(tzinfo=UTC))
    real_now = utc(base + 200 * 86400)
    Clock.real_now = real_now
    markets, hist = {}, {}
    for k in range(400):
        start = base - 20 * 86400 + rng.randrange(150) * 86400
        end = start + rng.choice([3, 8, 20, 40, 70]) * 86400
        win_no = rng.random() < 0.9
        p_no = rng.uniform(0.8, 0.97)
        T, P = [], []
        t = start
        while t < end + 2 * 86400:
            frac = (t - start) / (end - start)
            pn = p_no + (1 - p_no) * min(frac, 1) if win_no else p_no * (1 - min(frac, 1) ** 3)
            if k % 17 == 0 and abs(frac - 0.5) < 0.04:
                pn -= 0.12  # a scare
            pn = min(max(pn + rng.uniform(-0.01, 0.01), 0.005), 0.995)
            T.append(t)
            P.append(round(1 - pn, 4))  # outcome 0 is Yes
            t += 3600 if t > end - 3 * 86400 else 43200
        mid = str(k)
        markets[mid] = {"id": mid, "q": f"Will thing {k} happen by the deadline?", "outs": ["Yes", "No"],
                        "toks": [f"{k}y", f"{k}n"], "end": end, "start": start, "closed": True,
                        "closed_t": end + 86400, "final": [0.0, 1.0] if win_no else [1.0, 0.0], "uma": "resolved",
                        "vol": 200000, "fee": 0.04 if k % 2 else 0.0, "sports": False, "slug": f"m{k}", "ev": f"e{k}",
                        "ev_slug": f"e{k}"}
        hist[mid] = [T, P]
    wjson(os.path.join(CACHE, "markets.json.gz"), {"days": {}, "markets": markets})
    wjson(os.path.join(CACHE, "hist.json.gz"), hist)
    addr = bot.CFG["leader"]["address"].lower()
    w = [[base + 5 * 86400, "3n", "BUY", 100, 0.9, "m3", "No", "Will thing 3", "e3"],
         [base + 5 * 86400 + 60, "3n", "BUY", 50, 0.9, "m3", "No", "Will thing 3", "e3"],
         [base + 6 * 86400, "3n", "SELL", 140, 0.93, "m3", "No", "Will thing 3", "e3"]]
    wjson(os.path.join(CACHE, "wallet_trades.json.gz"), {addr: w})
    m3 = dict(markets["3"], end=base + 30 * 86400)
    wjson(os.path.join(CACHE, "copy_markets.json.gz"), {"m3": m3})
    run()
    r = json.load(open(os.path.join(OUT, "results.json")))["results"]
    tot = sum(s["finished"] for s in r["uncapped_1c"].values())
    assert tot > 50, tot
    assert r["copy_1c"]["mirror_unlimited"]["finished"] == 1, r["copy_1c"]["mirror_unlimited"]
    print(f"SELFTEST OK: {tot} finished rule trades, copy exit replayed")


def diag():
    """Prints a sample of losing endgame and favorite trades with the price path around the entry, to spot data artifacts."""
    markets = rjson(os.path.join(CACHE, "markets.json.gz"), {})["markets"]
    hist = rjson(os.path.join(CACHE, "hist.json.gz"), {})
    Clock.real_now = Clock.real_now or bot.now()
    feed = Feed(hist)
    names = [n for n in ("endgame", "endgame_ending_soon", "fav_short_95_98", "control_random") if n in bot.CFG["tracks"]]
    trs = replay_rules(markets, feed, 0.0, True, names)
    by_tok = {tok: (m, i) for m in markets.values() for i, tok in enumerate(m["toks"])}
    rng = random.Random(1)
    for n in names:
        cl = trs[n]["closed"]
        lost = [c for c in cl if c.get("exit", 1) < 0.5]
        print(f"\n=== {n}: {len(cl)} closed, {len(lost)} paid 0")
        # loss rate by entry price
        buckets = {}
        for c in cl:
            b = min(int(c["entry"] * 100), 99)
            w = buckets.setdefault(b, [0, 0])
            w[0] += 1
            w[1] += c.get("exit", 1) < 0.5
        print("  entry c: trades/lost " + "  ".join(f"{b}:{v[0]}/{v[1]}" for b, v in sorted(buckets.items()) if v[0] >= 20))
        # how long the price had been at the entry level: one-point spikes are suspicious
        spikes = 0
        for c in lost:
            m, i = by_tok[c["token"]]
            t0 = ts(bot.parse_iso(c["opened"]))
            h = hist[m["id"]]
            j = bisect.bisect_right(h[0], t0) - 1
            prev = h[1][j - 1] if j >= 1 else None
            if prev is not None and (prev if i == 0 else 1 - prev) < 0.85:
                spikes += 1
        print(f"  losers whose previous price point was under 85c: {spikes}/{len(lost)}")
        for c in rng.sample(lost, min(12, len(lost))):
            m, i = by_tok[c["token"]]
            t0 = ts(bot.parse_iso(c["opened"]))
            h = hist[m["id"]]
            pts = [(utc(T).strftime("%m-%d %H"), round(P if i == 0 else 1 - P, 3)) for T, P in zip(*h) if t0 - 2 * 86400 <= T <= t0 + 2 * 86400]
            print(f"- {m['q'][:90]} | side {m['outs'][i]} | entry {c['entry']} at {c['opened']} | tier {c.get('tier', '')}")
            print(f"  end {iso_t(m['end'])} closed {iso_t(m['closed_t']) if m['closed_t'] else None} final {m['final']} uma {m.get('uma')} vol {m['vol']:.0f}")
            print(f"  path (our side): {pts[:40]}")


def fade():
    """Mirror test (2026-11-08): the endgame 'ends within a day' favorites lost money (they flipped more often than
    their price said), so what if we buy the CHEAP side of those same markets instead? Replays the ending_soon picks
    with a wide favorite band, then prices the other side at (1 - favorite price) + slippage + fee. Writes
    backtest/fade.md. A history price is not a real ask: the live `fade_sure` track checks the real books."""
    markets = rjson(os.path.join(CACHE, "markets.json.gz"), {})["markets"]
    hist = rjson(os.path.join(CACHE, "hist.json.gz"), {})
    Clock.real_now = Clock.real_now or bot.now()
    feed = Feed(hist)
    name = "endgame_ending_soon"
    saved = json.loads(json.dumps(bot.CFG["rules"]))
    bot.CFG["rules"][name].update({"min_price": 0.85, "max_price": 0.99, "picks_per_scan": 100000, "min_edge": None})
    bot.CFG["rules"]["endgame"]["min_liquidity"] = 0
    try:
        trs = replay_rules(markets, feed, 0.0, True, [name])
    finally:
        bot.CFG["rules"] = saved
    by_tok = {tok: (m, i) for m in markets.values() for i, tok in enumerate(m["toks"])}
    rows = []
    for c in trs[name]["closed"]:
        if c.get("reason") != "resolved":
            continue
        m, i = by_tok[c["token"]]
        p = c["entry"]
        t0 = ts(bot.parse_iso(c["opened"]))
        rows.append({"fav": p, "cheap": round(1 - p, 4), "pay": round(1 - c["exit"], 4), "fee": m["fee"],
                     "topic": topic(m["q"]), "h": (m["end"] - t0) / 3600, "t": t0, "q": m["q"]})
    rows.sort(key=lambda r: r["t"])
    mid_t = rows[len(rows) // 2]["t"] if rows else 0

    def agg(rs, slip):
        n = len(rs)
        won = sum(1 for r in rs if r["pay"] >= 0.5)
        cost = pnl = 0.0
        for r in rs:
            q = min(0.99, r["cheap"] + slip)
            f = bot.taker_fee(1, q, r["fee"])
            cost += q + f
            pnl += r["pay"] - q - f
        return n, won, pnl, (100 * pnl / cost if cost else 0.0)

    def line(label, rs):
        if not rs:
            return f"| {label} | 0 | | | | | |"
        n, won, _, _ = agg(rs, 0.0)
        avg = sum(r["cheap"] for r in rs) / n
        cells = []
        for s in (0.01, 0.02, 0.03):
            _, _, pnl, per = agg(rs, s)
            cells.append(f"{money(pnl * 5)} ({money(per)})")
        return f"| {label} | {n} | {won} | {avg * 100:.1f}c | " + " | ".join(cells) + " |"

    head = ["| Slice | Bets | Cheap side won | Avg cheap price | Profit at +1c (per $100) | at +2c | at +3c |",
            "|---|---|---|---|---|---|---|"]
    L = [f"# Fade test: buy the cheap side of 'sure' markets that end within a day", "",
         f"Generated {bot.iso(Clock.real_now)}. Same picks as `endgame_ending_soon` with the favorite at 85-99c, but we "
         "buy the OTHER side, 5 shares each, held to the result. Price = 1 - favorite's history price + slippage + "
         "taker fee. Profit is for 5 shares a bet; '(per $100)' is per $100 staked. Paper only.", "",
         "**Big caveat:** history has no order book. On thin bucket markets the real ask on the cheap side can be "
         "several cents above (1 - favorite price). That is why the slippage columns go to 3c, and why the live "
         "`fade_sure` track fills on the real book.", "", "## All", ""] + head + [line("all", rows)]
    L += ["", "## By topic", ""] + head
    for tp in sorted({r["topic"] for r in rows}):
        L.append(line(tp, [r for r in rows if r["topic"] == tp]))
    L += ["", "## By cheap-side price", ""] + head
    for lo, hi in ((0.0, 0.02), (0.02, 0.04), (0.04, 0.06), (0.06, 0.08), (0.08, 0.10), (0.10, 0.16)):
        L.append(line(f"{lo * 100:.0f}-{hi * 100:.0f}c", [r for r in rows if lo <= r["cheap"] < hi]))
    L += ["", "## By hours left", ""] + head
    for lo, hi in ((0, 6), (6, 12), (12, 18), (18, 25)):
        L.append(line(f"{lo}-{hi}h", [r for r in rows if lo <= r["h"] < hi]))
    L += ["", "## Older half vs newer half (does it last?)", ""] + head
    L.append(line("older", [r for r in rows if r["t"] < mid_t]))
    L.append(line("newer", [r for r in rows if r["t"] >= mid_t]))
    for tp in ("weather", "crypto price", "post counts"):
        sub = [r for r in rows if r["topic"] == tp]
        L.append(line(f"{tp} older", [r for r in sub if r["t"] < mid_t]))
        L.append(line(f"{tp} newer", [r for r in sub if r["t"] >= mid_t]))
    L += ["", "## Candidate live rule: weather + crypto price + post counts, cheap side 2-10c", ""] + head
    rule = [r for r in rows if r["topic"] in ("weather", "crypto price", "post counts") and 0.02 <= r["cheap"] <= 0.10]
    L.append(line("rule", rule))
    for tp in ("weather", "crypto price", "post counts"):
        L.append(line(f"rule, {tp}", [r for r in rule if r["topic"] == tp]))
    rng = random.Random(3)
    wins = [r for r in rule if r["pay"] >= 0.5]
    L += ["", "## Sample of cheap-side wins (sanity check)", ""]
    L += [f"- {r['q'][:100]} | cheap {r['cheap'] * 100:.1f}c | {r['h']:.0f}h left | {iso_t(r['t'])}"
          for r in rng.sample(wins, min(15, len(wins)))]
    os.makedirs(OUT, exist_ok=True)
    txt = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "fade.md"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "btideasfetch":   # whole events for the idea machine, then volbias + the screen
        __import__("ideas").fetch_events()
        __import__("ideas").volbias()
        __import__("ideas").run()
        sys.exit(0)
    if cmd == "btideasvolbias":
        __import__("ideas").volbias()
        sys.exit(0)
    if cmd.startswith("btideasdrill_"):  # idea machine drill-down (ideas.py)
        __import__("ideas").drill(cmd[len("btideasdrill_"):])
        sys.exit(0)
    if cmd.startswith("btcheck") or cmd == "btholdout":  # sanity checks of this backtester (btcheck.py)
        sys.argv[1] = {"btcheck": "run", "btcheckself": "selftest", "btholdout": "holdout"}.get(cmd, cmd)
        import runpy
        runpy.run_path(os.path.join(ROOT, "btcheck.py"), run_name="__main__")
        sys.exit(0)
    {"fetch": fetch, "run": run, "all": lambda: (fetch(), run()), "selftest": selftest,
     "btfetch": fetch, "btrun": lambda: (fetch(), run()), "btselftest": selftest, "btdiag": diag,
     "btfade": lambda: (fetch(), fade()), "fade": fade,
     "btcalib": lambda: __import__("calib").run(),
     "btideas": lambda: __import__("ideas").run(),
     "btideasself": lambda: __import__("ideas").selftest(),
     "btkc": lambda: (__import__("kcrypto").fetch(os.environ.get("KC_DAYS", 60)), __import__("kcrypto").run()),
     "btkcfetch": lambda: __import__("kcrypto").fetch(os.environ.get("KC_DAYS", 60)),
     "btkcrun": lambda: __import__("kcrypto").run(),
     "btkc2": lambda: (__import__("kcrypto").fetch(2), __import__("kcrypto").run()),
     "btrulespeek": lambda: __import__("rules").peek(),
     "btrulesfetch": lambda: __import__("rules").fetch(),
     "btrulessmall": lambda: (__import__("rules").fetch_small(), __import__("rules").run()),
     "btrulesrun": lambda: __import__("rules").run(),
     "btrules": lambda: (__import__("rules").fetch(), __import__("rules").run()),
     "btcalibsmall": lambda: (__import__("calib").fetch_small(), __import__("calib").run())}[cmd]()
