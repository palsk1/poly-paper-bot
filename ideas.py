#!/usr/bin/env python3
"""Idea machine (2026-11-09): make hundreds of edge ideas on purpose, then try hard to kill them.

PAPER ONLY. Reads the backtest cache (bt_cache/, filled by `backtest.py fetch`), never trades.
A thin layer on calib.py (snapshots, topic tagger, payouts) and btcheck.py (holdout cut). Method: backtest/IDEAS.md.

    python3 ideas.py run        # screen every idea on the cache, write backtest/ideas.md   (probe: btideas)
    python3 ideas.py list       # print the idea list without looking at any results
    python3 ideas.py selftest   # offline: a planted edge must be found, pure noise must not pass

How an idea is born
  idea = (a FEATURE of the market known at the time) x (which side we buy) x (price band) x (time before the end)
  Features come from a catalog of things a trader could see (wording, how old the market is, its siblings in the
  event, the shape of its price path, ...). Each one carries a "story": the human bias that would make it work.
  Every feature is also crossed with every topic, so "long questions about elections" is its own idea.

How an idea dies (backtest/PROTOCOL.md rules, made stricter for many ideas at once)
  - Only markets that ended before the holdout day (btcheck.HOLDOUT_FROM). The holdout is never read.
  - Features use prices up to the snapshot only. We buy 1 hour later, at the history price + 2c + the taker fee.
  - Twins: every bet is compared with the average of ALL bets on the same side, same 2c price bucket, same days
    before the end. An idea must beat its twins, so "long shots lose" alone can never pass.
  - Events count once (20 markets about one speech are one bet), averaged inside the event.
  - Two halves by end date. Ideas are picked on one half (discovery) and must pass on the other (confirm), both
    ways round. The confirm bar is corrected for how many ideas got through discovery (Bonferroni, 90%).
  - It must also make money on its own at +2c in both halves, not just lose less than its twins.
  - Placebo features (random coin flips per event) go through the same machine. How many placebos survive tells
    us how much to trust the real survivors.

Plugging in your own ideas (other threads): import ideas, add a feature with the decorator, call ideas.run().

    import ideas
    @ideas.feature("my_rule_quirk", "people misread X")
    def _(c):          # c = Ctx (see below). Return a short label string, or None when it doesn't apply.
        return "quirky" if "x" in c.q else None
    ideas.run(out_name="ideas_mine.md")
"""
import bisect
import datetime as dt
import hashlib
import math
import os
import re
import sys
import time
from collections import defaultdict

import backtest as bt
import bot
import btcheck
import calib

DAY = 86400
HOLDOUT_FROM = btcheck.HOLDOUT_FROM   # markets ending on/after this day are never read here
HORIZONS = (1, 2, 3, 7, 14, 30)
HGROUP = {1: "1-3 days", 2: "1-3 days", 3: "1-3 days", 7: "7-14 days", 14: "7-14 days", 30: "30 days"}
BANDS = ((0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98))
SLIP = 0.02           # decision cost (PROTOCOL.md): history price + 2c + fee
SLIP_HARD = 0.05      # thin-market stress column
ENTRY_LAG = 3600      # buy 1 hour after the snapshot
MIN_EV_DISC = 30      # events needed in the discovery half
MIN_EV_CONF = 30      # events needed in the confirm half
DISC_T = 2.0          # discovery bar: beats its twins by 2 standard errors
ALPHA = 0.10          # 90% confidence, split over the ideas that reached the confirm half
TOPIC_CROSS = True
# Data flaw found by this machine (volbias, 2026-11-09): the cache keeps only markets whose FINAL volume passed $20k.
# In weather events the winning bucket draws volume late, so losing buckets are missing: weather choices we have won
# 1.3-1.5 times as often as their prices said (other topics about 1.0). Weather is left out until the data is fixed.
EXCLUDE_TOPICS = {"weather"}   # only used while the whole-event data (fetch_events) is missing
DATA_NOTE = ["old cache"]

FEATURES = []         # (name, story, fn, cross)
LAB = {}              # label text -> small int (rows keep ints, so 500k rows x 60 labels fit in memory)


def feature(name, story, cross=True):
    """Register a feature. fn(ctx) -> label (str) or None. cross=False: don't cross it with topics."""
    def deco(fn):
        FEATURES[:] = [f for f in FEATURES if f[0] != name]
        FEATURES.append((name, story, fn, cross))
        return fn
    return deco


class Ctx:
    """What a trader could know at snapshot time t. Prices are outcome 0 (usually "Yes")."""
    __slots__ = ("mk", "q", "ql", "t", "p", "T", "P", "i", "sibs", "ev_first_start", "hz", "topic", "_cache", "hi", "lo")

    def __init__(self, mk, T, P, i, t, hz, sibs, ev_first_start, tp, hi=None, lo=None):
        self.hi, self.lo = (hi[i] if hi else max(P[:i + 1])), (lo[i] if lo else min(P[:i + 1]))  # life high/low so far
        self.mk, self.q, self.ql = mk, mk["q"], mk["q"].lower()
        self.T, self.P, self.i, self.t, self.p, self.hz = T, P, i, t, P[i], hz
        self.sibs, self.ev_first_start, self.topic = sibs, ev_first_start, tp
        self._cache = {}

    def price_ago(self, secs):
        k = bisect.bisect_right(self.T, self.t - secs) - 1
        return self.P[k] if k >= 0 and self.t - secs - self.T[k] <= 3 * DAY else None

    def window(self, secs):
        k = bisect.bisect_left(self.T, self.t - secs)
        return self.P[k:self.i + 1]

    def sib_prices(self):
        """Outcome-0 prices at t of the event's markets that were listed by then (incl. this one)."""
        if "sp" not in self._cache:
            out = []
            for m, h in self.sibs:
                if m.get("start") and m["start"] > self.t:
                    continue
                k = bisect.bisect_right(h[0], self.t) - 1
                if k >= 0 and self.t - h[0][k] <= 3 * DAY:
                    out.append((m["id"], h[1][k]))
            self._cache["sp"] = out
        return self._cache["sp"]


def mv(x, small=0.03, big=0.10, up="rise", down="drop"):
    if x is None:
        return None
    if x <= -big:
        return f"{down} {big * 100:.0f}c+"
    if x <= -small:
        return f"{down} {small * 100:.0f}-{big * 100:.0f}c"
    if x < small:
        return "flat"
    if x < big:
        return f"{up} {small * 100:.0f}-{big * 100:.0f}c"
    return f"{up} {big * 100:.0f}c+"


def has(rx):
    r = re.compile(rx)
    return lambda c: "yes" if r.search(c.ql) else "no"


# ================================================================ the feature catalog
# Story = the bias that would make it pay. Already TESTED & DROPPED in memory (weekend, quiet/busy, tiny markets,
# final volume, topic x long shot alone) are left out on purpose.

@feature("market age", "new listings are priced by few people and anchored to the opening price")
def _(c):
    s = c.mk.get("start")
    if not s:
        return None
    a = (c.t - s) / DAY
    return "<1 day" if a < 1 else "1-3 days" if a < 3 else "3-14 days" if a < 14 else "14-60 days" if a < 60 else "60+ days"


@feature("share of life gone", "people forget a deadline is getting close (time decay is underpriced)")
def _(c):
    s = c.mk.get("start")
    if not s or c.mk["end"] <= s:
        return None
    f = (c.t - s) / (c.mk["end"] - s)
    return "first quarter" if f < 0.25 else "middle" if f < 0.75 else "last quarter" if f < 0.95 else "last 5 parts in 100"


@feature("planned length", "short-lived markets get less attention per question")
def _(c):
    s = c.mk.get("start")
    if not s:
        return None
    L = (c.mk["end"] - s) / DAY
    return "<3 days" if L < 3 else "3-14 days" if L < 14 else "14-60 days" if L < 60 else "60+ days"


@feature("markets in event", "big multi-choice events spread attention thin over the outsiders")
def _(c):
    n = len(c.sib_prices())
    return "single" if n <= 1 else "2-4" if n <= 4 else "5-14" if n <= 14 else "15+"


@feature("rank in event", "people overpay for the second favorite and ignore the field")
def _(c):
    sp = c.sib_prices()
    if len(sp) < 3:
        return None
    r = 1 + sum(1 for mid, p in sp if p > c.p + 1e-9 and mid != c.mk["id"])
    return "favorite" if r == 1 else "2nd" if r == 2 else "3rd-5th" if r <= 5 else "6th or lower"


@feature("added late to event", "a choice added after news is bought on hype")
def _(c):
    if len(c.sibs) < 2 or not c.mk.get("start") or not c.ev_first_start:
        return None
    return "added 2+ days later" if c.mk["start"] - c.ev_first_start > 2 * DAY else "listed with the event"


@feature("move last 24h", "people overreact to fresh news (or underreact and it keeps going)")
def _(c):
    a = c.price_ago(DAY)
    return mv(None if a is None else c.p - a)


@feature("move last 7 days", "slow drift keeps going (underreaction) or snaps back (overreaction)")
def _(c):
    a = c.price_ago(7 * DAY)
    return mv(None if a is None else c.p - a, 0.05, 0.15)


@feature("swing size last 7 days", "after a wild week the price is noisier than it should be")
def _(c):
    w = c.window(7 * DAY)
    if len(w) < 2:
        return "no moves"
    r = max(w) - min(w)
    return "<2c" if r < 0.02 else "2-10c" if r < 0.10 else "10-25c" if r < 0.25 else "25c+"


@feature("below its high", "people anchor to the best price they saw (disposition effect)")
def _(c):
    d = c.hi - c.p
    return "at its high" if d < 0.01 else "1-10c below" if d < 0.10 else "10-30c below" if d < 0.30 else "30c+ below"


@feature("above its low", "people anchor to the worst price they saw")
def _(c):
    d = c.p - c.lo
    return "at its low" if d < 0.01 else "1-10c above" if d < 0.10 else "10-30c above" if d < 0.30 else "30c+ above"


@feature("since listing", "the opening price sticks longer than it should (anchoring)")
def _(c):
    return mv(c.p - c.P[0], 0.05, 0.20, "up", "down")


@feature("opening price", "markets that open at a coin flip stay too close to it")
def _(c):
    f = c.P[0]
    return "opened 45-55c" if 0.45 <= f <= 0.55 else "opened under 20c" if f < 0.20 else "opened over 80c" if f > 0.80 else "opened 20-45c or 55-80c"


@feature("round price", "people like round prices, so they cluster on them")
def _(c):
    x = c.p * 100
    if abs(x - round(x / 10) * 10) < 0.25:
        return "on a 10c mark"
    if abs(x - round(x / 5) * 5) < 0.25:
        return "on a 5c mark"
    return "off-round"


feature("words: threshold", "thresholds ('above', 'at least', '+') are hard to judge, people guess the round number")(
    has(r"\babove\b|\bbelow\b|\bmore than\b|\bless than\b|\bat least\b|\bor more\b|\bover\b|\bunder\b|\d\+|\breach\b|\bhit\b"))
feature("words: range bucket", "one bucket out of many: people overpay for the bucket near today's number")(
    has(r"\bbetween\b|\d\s*-\s*\d|\d\s*–\s*\d|\bto\b \$?\d"))
feature("words: deadline", "'by <date>' questions: nothing ever happens, YES drifts down slower than it should")(
    has(r"\bby\b|\bbefore\b|\bin 20\d\d\b|\bthis (week|month|year)\b"))
feature("words: announce", "'announce/confirm' needs an official act, which is rarer than people think")(
    has(r"announc|confirm|official|publicly"))
feature("words: negative", "questions phrased in the negative confuse people, so they buy the wrong side")(
    has(r"\bnot\b|\bno\b|n't\b|\bfail|\bwithout\b|\bnever\b"))
feature("words: superlative", "'most/highest/first' races: fans overpay for their pick")(
    has(r"\bmost\b|\bhighest\b|\blowest\b|\bfirst\b|\btop\b|\bbest\b|\blargest\b|\bbiggest\b|#1"))
feature("words: famous name", "fans and haters overpay for famous names (attention bias)")(
    has(r"trump|musk|elon|taylor swift|kanye|\bye\b|mrbeast|drake|kim kardashian|zelensky|putin|netanyahu|vance|newsom"))
feature("words: exact number", "exact counts and prices look precise but are coin flips")(
    has(r"\d"))


@feature("question length", "long, complicated questions put people off, so they stay mispriced")
def _(c):
    n = len(c.q)
    return "short (<50 letters)" if n < 50 else "medium" if n < 100 else "long (100+ letters)"


@feature("answer names", "the first answer listed gets bought more (position bias), most of all when it isn't Yes/No")
def _(c):
    o = [x.lower() for x in c.mk.get("outs") or []]
    if o[:2] == ["yes", "no"]:
        return "yes/no"
    if o[:2] in (["up", "down"], ["over", "under"], ["higher", "lower"]):
        return "up/down or over/under"
    return "names"


MONTHS = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
_DATED = re.compile(MONTHS + r" \d{1,2}\b")


@feature("repeating daily series", "the same question every day: people price today like yesterday")
def _(c):
    s = c.mk.get("ev_slug") or ""
    return "dated series" if _DATED.search(c.ql) or re.search(MONTHS + r"-\d{1,2}(-|$)", s) else "one-off"


@feature("fee market", "markets with taker fees scare away the quick traders who fix prices")
def _(c):
    return "has fees" if (c.mk.get("fee") or 0) > 0 else "no fees"


def _placebo(salt):
    def fn(c):
        h = hashlib.md5((salt + (c.mk.get("ev") or c.mk["id"])).encode()).digest()[0]
        return "group " + "ABCD"[h % 4]
    return fn


feature("PLACEBO coin 1", "none: random groups, should never pass")(_placebo("p1"))
feature("PLACEBO coin 2", "none: random groups, should never pass")(_placebo("p2"))
feature("PLACEBO coin 3", "none: random groups, should never pass")(_placebo("p3"))


# ================================================================ rows

def in_sample(markets):
    cut = int(dt.datetime.fromisoformat(HOLDOUT_FROM).replace(tzinfo=dt.timezone.utc).timestamp())
    return {k: m for k, m in markets.items() if m.get("end") and m["end"] < cut}


def build_rows(markets, hist, horizons=HORIZONS):
    """One row per (market, horizon): entry price 1h after the snapshot, outcome, and every feature label."""
    by_ev = defaultdict(list)
    for mk in markets.values():
        h = hist.get(mk["id"])
        if h and h[0]:
            by_ev[mk.get("ev") or mk["id"]].append((mk, h))
    rows = []
    t0 = time.time()
    for n_ev, (ev, sibs) in enumerate(by_ev.items()):
        starts = [m["start"] for m, _ in sibs if m.get("start")]
        first = min(starts) if starts else None
        for mk, h in sibs:
            y = calib.outcome0(mk)
            if y is None:
                continue
            T, P = h
            tp = calib.topic(mk["q"])
            hi, lo, a, b = [], [], -1.0, 2.0
            for x in P:
                a, b = max(a, x), min(b, x)
                hi.append(a)
                lo.append(b)
            for hz in horizons:
                t = mk["end"] - hz * DAY
                if t < T[0] + DAY or (mk.get("start") and t < mk["start"]):
                    continue
                if mk.get("closed_t") and t + ENTRY_LAG >= mk["closed_t"]:
                    continue
                i = bisect.bisect_right(T, t) - 1
                if i < 0 or t - T[i] > 3 * DAY:
                    continue
                k = bisect.bisect_right(T, t + ENTRY_LAG) - 1
                pe = P[k]
                if not 0.02 <= pe <= 0.98:
                    continue
                c = Ctx(mk, T, P, i, t, hz, sibs, first, tp, hi, lo)
                labels = []
                for name, _, fn, cross in FEATURES:
                    try:
                        lab = fn(c)
                    except Exception:
                        lab = None
                    if lab is None:
                        continue
                    labels.append(LAB.setdefault(f"{name} = {lab}", len(LAB)))
                    if TOPIC_CROSS and cross:
                        labels.append(LAB.setdefault(f"topic {tp} & {name} = {lab}", len(LAB)))
                rows.append({"ev": ev, "end": mk["end"], "h": hz, "pe": pe, "y": y, "fee": mk.get("fee", 0),
                             "labels": tuple(labels), "q": mk["q"]})
        if n_ev % 20000 == 0 and n_ev:
            print(f"  rows: {n_ev}/{len(by_ev)} events, {len(rows)} rows ({time.time() - t0:.0f}s)")
    return rows


# ================================================================ whole events (fixes the $20k final-volume hole)
# bt_cache keeps only markets whose FINAL volume passed $20k. fetch_events() reads every closed event (with all its
# markets, any volume) day by day, then downloads price history for the choices the cache is missing, in events
# that have at least one cached market. load_full() merges it all and says which events are COMPLETE: every choice
# that traded at least MIN_VOL_COMPLETE is in the data with a price history. Screen on complete events only.

EV_PATH = os.path.join(bt.CACHE, "events.json.gz")
FILL_HIST = os.path.join(bt.CACHE, "fill_hist.json.gz")
MIN_VOL_COMPLETE = 500.0


def fetch_events():
    from concurrent.futures import ThreadPoolExecutor
    have = bt.rjson(EV_PATH, {"days": {}, "events": {}, "markets": {}}) or {"days": {}, "events": {}, "markets": {}}
    main = bt.rjson(os.path.join(bt.CACHE, "markets.json.gz"), {}).get("markets", {})
    start = dt.datetime.fromisoformat(bt.START).replace(tzinfo=dt.timezone.utc)
    end = bot.now() - dt.timedelta(days=2)
    days, d = [], start
    while d < end:
        if bot.iso(d)[:10] not in have["days"]:
            days.append(d)
        d += dt.timedelta(days=1)
    print(f"events: {len(have['days'])} days cached, {len(days)} to read")

    def one_day(d):
        out, cur = [], None
        for _ in range(200):
            p = {"closed": "true", "limit": 100, "end_date_min": bot.iso(d), "end_date_max": bot.iso(d + dt.timedelta(days=1))}
            if cur:
                p["after_cursor"] = cur
            try:
                res = bot.http_json(f"{bt.G}/events/keyset", p)
            except Exception as e:
                print(f"  {d:%Y-%m-%d} failed: {e}")
                return d, None
            rows = [e for e in bot.envelope_rows(res, "events", "data") if isinstance(e, dict)]
            out += rows
            cur = res.get("next_cursor") if isinstance(res, dict) else None
            if not cur or not rows:
                break
        return d, out

    t0 = time.time()
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for d, evs in ex.map(one_day, days):
            if evs is None:
                continue
            nm = 0
            for e in evs:
                eid = str(e.get("id") or e.get("slug"))
                mids = []
                for m in e.get("markets") or []:
                    if not isinstance(m, dict):
                        continue
                    m = dict(m)
                    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
                    sm = bt.slim_market(m)
                    if len(sm["toks"]) != 2 or not sm["end"]:
                        continue
                    mids.append([sm["id"], sm["vol"] or 0.0])
                    if sm["id"] not in main:
                        have["markets"][sm["id"]] = sm
                        nm += 1
                have["events"][eid] = {"neg": bool(e.get("negRisk") or e.get("enableNegRisk")), "mids": mids}
            have["days"][bot.iso(d)[:10]] = len(evs)
            print(f"  {d:%Y-%m-%d}: {len(evs)} events, {nm} markets not in the main cache ({time.time() - t0:.0f}s)")
    # history for the missing choices, only in events that have at least one main-cache market.
    # Everything else is dropped (the full list is ~1M events / 4.5M markets, a 600MB cache nobody needs).
    in_main = defaultdict(int)
    for m in main.values():
        in_main[m.get("ev") or m["id"]] += 1
    have["events"] = {k: v for k, v in have["events"].items() if in_main.get(k)}
    keep = {mid for e in have["events"].values() for mid, _ in e["mids"]}
    have["markets"] = {k: v for k, v in have["markets"].items() if k in keep}
    bt.wjson(EV_PATH, have)
    print(f"events: {len(have['events'])} events with a main-cache market, {len(have['markets'])} extra markets kept")
    hist = bt.rjson(FILL_HIST, {}) or {}
    todo = []
    for eid, e in have["events"].items():
        if not in_main.get(eid):
            continue
        for mid, vol in e["mids"]:
            if mid in have["markets"] and mid not in hist and vol >= MIN_VOL_COMPLETE:
                mk = have["markets"][mid]
                if mk.get("closed") and not mk.get("sports"):
                    todo.append(mk)
    print(f"fill history: {len(hist)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for c in range(0, len(todo), 2000):
            if time.time() - bt.FETCH_T0 > bt.FETCH_MIN * 60:
                print(f"  time budget used up: {len(todo) - c} left for the next run (run btideasfetch again)")
                break
            for mid, h in ex.map(bt.fetch_history, todo[c:c + 2000]):
                hist[mid] = h
            print(f"  {min(c + 2000, len(todo))}/{len(todo)} ({time.time() - t0:.0f}s)")
            bt.wjson(FILL_HIST, hist)
    bt.wjson(FILL_HIST, hist)


def load_full():
    """markets, hist, complete_events. Main cache + filled-in choices. complete_events = event ids where every
    choice that traded at least MIN_VOL_COMPLETE is present with a history. None if fetch_events() never ran."""
    markets = dict(bt.rjson(os.path.join(bt.CACHE, "markets.json.gz"), {}).get("markets", {}))
    hist = dict(bt.rjson(os.path.join(bt.CACHE, "hist.json.gz"), {}))
    evs = bt.rjson(EV_PATH, None)
    if not evs:
        return markets, hist, None
    fh = bt.rjson(FILL_HIST, {}) or {}
    for mid, mk in evs["markets"].items():
        if mid in fh and fh[mid] and fh[mid][0]:
            markets.setdefault(mid, mk)
            hist.setdefault(mid, fh[mid])
    complete = set()
    for eid, e in evs["events"].items():
        if e["mids"] and all(mid in hist and hist[mid] and hist[mid][0] for mid, vol in e["mids"]
                             if vol >= MIN_VOL_COMPLETE and (markets.get(mid) or {}).get("closed", True)):
            complete.add(eid)
    return markets, hist, complete


def load_screen_set(exclude_topics=None):
    """What the screen uses: in-sample, non-sports, complete events when known (else the old cache minus
    EXCLUDE_TOPICS). Importable by other threads."""
    markets, hist, complete = load_full()
    ms = in_sample(markets)
    if complete is not None:
        out = {k: m for k, m in ms.items() if not m.get("sports") and (m.get("ev") or m["id"]) in complete}
        note = f"whole events only ({len(complete):,} complete events)"
    else:
        ex = EXCLUDE_TOPICS if exclude_topics is None else exclude_topics
        out = {k: m for k, m in ms.items() if not m.get("sports") and calib.topic(m["q"]) not in ex}
        note = f"old cache without {sorted(ex)} (run btideasfetch for whole events)"
    return out, hist, note


# ================================================================ screening

def roi(q, pay, fee, slip):
    c = min(0.99, q + slip)
    f = bot.taker_fee(1, c, fee)
    return (pay - c - f) / (c + f)


def band_of(q):
    for b in BANDS:
        if b[0] <= q < b[1]:
            return b
    return None


def bname(b):
    return f"{b[0] * 100:.0f}-{b[1] * 100:.0f}c"


def split_events(rows):
    """Half A / B by the event's last end date, split so each half has about the same number of rows."""
    ev_end = {}
    for r in rows:
        ev_end[r["ev"]] = max(ev_end.get(r["ev"], 0), r["end"])
    ends = sorted(ev_end[r["ev"]] for r in rows)
    cut = ends[len(ends) // 2] if ends else 0
    return {e: ("A" if t < cut else "B") for e, t in ev_end.items()}, cut


def twins(rows, half_of):
    """Average return of ALL bets with the same side, 2c price bucket, days before end and half."""
    acc = defaultdict(lambda: [0.0, 0])
    for r in rows:
        hf = half_of[r["ev"]]
        for side, q, pay in ((0, r["pe"], r["y"]), (1, 1 - r["pe"], 1 - r["y"])):
            a = acc[(hf, side, int(q * 50), r["h"])]
            a[0] += roi(q, pay, r["fee"], SLIP)
            a[1] += 1
    return {k: s / n for k, (s, n) in acc.items()}


def screen(rows):
    """Accumulate, per half and idea, the per-event average of: return at +2c, at +5c, and return minus twins."""
    half_of, cut = split_events(rows)
    base = twins(rows, half_of)
    acc = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0, 0])  # events, sum x, sum x^2, sum r2, sum r5, bets
    rows = sorted(rows, key=lambda r: r["ev"])
    k = 0
    t0 = time.time()
    while k < len(rows):
        ev = rows[k]["ev"]
        j = k
        tmp = defaultdict(lambda: [0.0, 0.0, 0.0, 0])
        while j < len(rows) and rows[j]["ev"] == ev:
            r = rows[j]
            hf = half_of[ev]
            for side, q, pay in ((0, r["pe"], r["y"]), (1, 1 - r["pe"], 1 - r["y"])):
                b = band_of(q)
                if b is None:
                    continue
                r2 = roi(q, pay, r["fee"], SLIP)
                x = r2 - base[(hf, side, int(q * 50), r["h"])]
                r5 = roi(q, pay, r["fee"], SLIP_HARD)
                hg = HGROUP[r["h"]]
                for lab in r["labels"]:
                    a = tmp[(lab, side, b, hg)]
                    a[0] += x
                    a[1] += r2
                    a[2] += r5
                    a[3] += 1
            j += 1
        hf = half_of[ev]
        for key, (sx, s2, s5, n) in tmp.items():
            a = acc[(hf,) + key]
            xm = sx / n
            a[0] += 1
            a[1] += xm
            a[2] += xm * xm
            a[3] += s2 / n
            a[4] += s5 / n
            a[5] += n
        k = j
    names = {v: k for k, v in LAB.items()}
    acc = {(k[0], names[k[1]]) + k[2:]: v for k, v in acc.items()}
    print(f"  screened {len(rows)} rows into {len(acc)} idea-halves ({time.time() - t0:.0f}s)")
    return acc, cut


PHANTOM = True       # add one made-up event that lost its whole stake (like the live trust score's phantom loss)


def stat(a, phantom=None):
    """events, mean excess, its t, return +2c, return +5c, bets. With the phantom loss, an idea with 30 wins at 95c and
    no loss yet can't look sure: the normal-curve t is far too kind to bets that win small and lose big, rarely."""
    if not a or a[0] < 2:
        return None
    n, sx, sx2, s2, s5, bets = a
    if PHANTOM if phantom is None else phantom:
        n, sx, sx2, s2, s5 = n + 1, sx - 1, sx2 + 1, s2 - 1, s5 - 1
    m = sx / n
    var = max(0.0, (sx2 - n * m * m) / (n - 1))
    se = math.sqrt(var / n) if var > 0 else 1e-9
    return {"n": n, "x": m, "t": m / se, "r2": s2 / n, "r5": s5 / n, "bets": bets}


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def select(acc):
    """Discovery on one half, confirm on the other, both ways round. Returns survivors and bookkeeping."""
    ideas = {k[1:] for k in acc}
    out, info = {}, {"ideas": len(ideas)}
    for disc, conf in (("A", "B"), ("B", "A")):
        cand = []
        for key in ideas:
            s = stat(acc.get((disc,) + key))
            if s and s["n"] >= MIN_EV_DISC and s["t"] >= DISC_T:
                cand.append(key)
        K = max(1, len(cand))
        info[f"tested_{disc}"] = sum(1 for key in ideas if (stat(acc.get((disc,) + key)) or {}).get("n", 0) >= MIN_EV_DISC)
        info[f"cand_{disc}"] = len(cand)
        for key in cand:
            s = stat(acc.get((conf,) + key))
            if not s or s["n"] < MIN_EV_CONF:
                continue
            p = norm_sf(s["t"])
            sd = stat(acc.get((disc,) + key))
            ok = p < ALPHA / K and s["r2"] > 0 and sd["r2"] > 0
            if ok:
                out.setdefault(key, []).append((disc, conf, p * K))
    return out, info


def is_placebo(key):
    return "PLACEBO" in key[0]


def known(key):
    lab = key[0]
    if "mentions" in lab:
        return "mention markets (already a live track, holdout-locked)"
    if "topic weather" in lab:
        return "weather (fade_sure already trades this)"
    if lab.startswith("move last 24h = drop") or "move last 24h = drop" in lab:
        return "panic fade family (already live)"
    return ""


def describe(key):
    lab, side, b, hg = key
    side_s = "first answer (Yes)" if side == 0 else "second answer (No)"
    return f"{lab} | buy {side_s} at {bname(b)} | {hg} before the end"


def m100(x):
    return f"{'+' if x >= 0 else '-'}${abs(x) * 100:.2f}"


def examples(rows, key, k=6):
    lab, side, b, hg = key
    lid = LAB.get(lab)
    seen, out = set(), []
    for r in rows:
        q = r["pe"] if side == 0 else 1 - r["pe"]
        if lid in r["labels"] and HGROUP[r["h"]] == hg and band_of(q) == b and r["ev"] not in seen:
            seen.add(r["ev"])
            out.append(f"{r['q']} ({q * 100:.0f}c, {'won' if (r['y'] if side == 0 else 1 - r['y']) else 'lost'})")
    step = max(1, len(out) // k)
    return out[::step][:k]


def report(acc, cut, rows, survivors, info, n_markets):
    stories = {n: s for n, s, _, _ in FEATURES}
    L = ["# Idea machine: hundreds of edge ideas, screened hard", "",
         f"Generated {bot.iso(bot.now())} by `ideas.py` (probe `btideas`). Paper only. {n_markets:,} finished markets "
         f"that ended before {HOLDOUT_FROM} (the holdout is never read; data: {DATA_NOTE[0]}), {len(rows):,} price snapshots, "
         f"{len(FEATURES)} features ({sum(1 for f in FEATURES if 'PLACEBO' in f[0])} of them placebo coin flips). "
         f"Halves split at {bt.iso_t(cut)[:10]}.", "",
         "How to read: each idea buys one side 1 hour after a snapshot at the history price + 2c + fee and holds to the "
         "end. 'vs twins' = how much better than all other bets at the same price and time before the end (so a "
         "plain long-shot effect can't pass). Money per $100 staked, events weighted equally.", "",
         f"- Ideas made: {info['ideas']:,} (feature value x side x price band x time before end)",
         f"- With enough events to judge (30+ in a half): {info['tested_A']:,} in half A, {info['tested_B']:,} in half B",
         f"- Through discovery (beat twins by 2 standard errors): {info['cand_A']:,} picked on A, {info['cand_B']:,} picked on B",
         f"- Confirm bar on the other half: 90% after correcting for that many ideas, AND making money at +2c in both halves", ""]
    real = {k: v for k, v in survivors.items() if not is_placebo(k)}
    plac = {k: v for k, v in survivors.items() if is_placebo(k)}
    n_pl = sum(1 for k in {k[1:] for k in acc} if is_placebo(k))
    n_re = info["ideas"] - n_pl
    luck = len(plac) * n_re / max(1, n_pl)
    L += [f"**Survivors: {len(real)} real ideas, {len(plac)} placebos.** Placebos are {n_pl:,} of the {info['ideas']:,} "
          f"ideas, so pure luck would let through about {luck:.1f} real-looking ideas (placebo survivors scaled up). "
          + ("No placebo passed, so the filter is strict enough." if not plac else
             "Placebos passed too, so treat survivors with extra doubt.")]
    L += ["", "Every number below includes one made-up total loss per idea (so a short lucky run can't pass)."]
    L += ["", "## Survivors", ""]
    hdr = ["| Idea | Why it might work | Events A / B | Bets | vs twins A / B | +2c A / B | +5c (all) | Passed | Note |",
           "|---|---|---|---|---|---|---|---|---|"]
    L += hdr

    def rowtxt(key, passed):
        a, b = stat(acc.get(("A",) + key)), stat(acc.get(("B",) + key))
        name = key[0].split(" = ")[0].split("& ")[-1]
        nA, nB = (a or {}).get("n", 0), (b or {}).get("n", 0)
        r5 = ((a["r5"] * a["n"] if a else 0) + (b["r5"] * b["n"] if b else 0)) / max(1, nA + nB)
        bets = (a or {}).get("bets", 0) + (b or {}).get("bets", 0)
        ps = ", ".join(f"picked on {d}, confirmed on {c}" for d, c, _ in passed) if passed else ""
        return (f"| {describe(key)} | {stories.get(name, '')} | {nA} / {nB} | {bets} | "
                f"{m100(a['x']) if a else '-'} / {m100(b['x']) if b else '-'} | "
                f"{m100(a['r2']) if a else '-'} / {m100(b['r2']) if b else '-'} | {m100(r5)} | {ps} | {known(key)} |")

    def strength(key):
        a, b = stat(acc.get(("A",) + key)), stat(acc.get(("B",) + key))
        return min(a["t"] if a else 0, b["t"] if b else 0)

    for key in sorted(real, key=strength, reverse=True):
        L.append(rowtxt(key, real[key]))
    if not real:
        L.append("| none | | | | | | | | |")
    if real:
        L += ["", "Sample questions behind each survivor (check the feature caught what its name says):", ""]
        for key in sorted(real, key=strength, reverse=True):
            L += [f"- **{describe(key)}**"] + [f"  - {q[:110]}" for q in examples(rows, key)]
    if plac:
        L += ["", "### Placebos that passed (should be none)", ""] + hdr + [rowtxt(k, v) for k, v in plac.items()]

    # near misses: strongest ideas in both halves, so the next run has somewhere to look
    both = []
    for key in {k[1:] for k in acc}:
        a, b = stat(acc.get(("A",) + key)), stat(acc.get(("B",) + key))
        if not a or not b or a["n"] < MIN_EV_CONF or b["n"] < MIN_EV_CONF or key in survivors:
            continue
        both.append((min(a["t"], b["t"]), key))
    both.sort(reverse=True)
    L += ["", "## Near misses (beat their twins in both halves, but not by enough)", ""] + hdr
    L += [rowtxt(k, []) for _, k in both[:25]]
    pl_best = [t for t, k in both if is_placebo(k)][:1]
    L += ["", f"Best placebo in this list scores {pl_best[0]:.1f} standard errors in its weaker half: anything near or "
          "below that is noise." if pl_best else ""]
    L += ["", "## The catalog (features and their stories)", ""]
    L += [f"- **{n}**: {s}" for n, s, _, _ in FEATURES]
    return "\n".join(L) + "\n"


def run(out_name="ideas.md"):
    markets, hist, note = load_screen_set()
    DATA_NOTE[0] = note
    print(f"markets {len(markets)} in-sample non-sports, {note} (end before {HOLDOUT_FROM})")
    t0 = time.time()
    rows = build_rows(markets, hist)
    print(f"rows {len(rows)} ({time.time() - t0:.0f}s)")
    acc, cut = screen(rows)
    survivors, info = select(acc)
    txt = report(acc, cut, rows, survivors, info, len(markets))
    os.makedirs(bt.OUT, exist_ok=True)
    with open(os.path.join(bt.OUT, out_name), "w") as fh:
        fh.write(txt)
    print(txt)
    return survivors


# ================================================================ drill-down of one survivor

DRILLS = {  # name: (question regex, side, band, horizons)
    "quiet_no": (r".", 1, (0.50, 0.75), (1, 2, 3), "swing size last 7 days = <2c"),
    "quiet_no_wide": (r".", 1, (0.40, 0.90), (1, 2, 3, 7), "swing size last 7 days = <2c"),
    "wx": (r"temperature", 0, (0.25, 0.50), (1, 2, 3)),
    "wx_all": (r"temperature", 0, (0.02, 0.98), (1, 2, 3)),
    "superl_nowx": (r"^(?!.*temperature).*(\bmost\b|\bhighest\b|\blowest\b|\bfirst\b|\btop\b|\bbest\b|\blargest\b|\bbiggest\b|#1)", 0, (0.25, 0.50), (1, 2, 3)),
}


def drill(name):
    """Split one idea every way we can think of: by month, days before the end, price, and its twins."""
    rx_s, side, band, hzs, *lab = DRILLS[name]
    rx = re.compile(rx_s, re.I)
    markets, hist, note = load_screen_set()
    print(f"drill data: {note}")
    keep = [f for f in FEATURES if lab and f[0] == lab[0].split(" = ")[0]]
    FEATURES[:] = keep          # only the feature the drill filters on
    rows = build_rows(markets, hist, horizons=hzs)
    half_of, cut = split_events(rows)
    base = twins(rows, half_of)
    lid = LAB.get(lab[0]) if lab else None
    sel = []
    for r in rows:
        q = r["pe"] if side == 0 else 1 - r["pe"]
        pay = r["y"] if side == 0 else 1 - r["y"]
        if rx.search(r["q"]) and band[0] <= q < band[1] and (lid is None or lid in r["labels"]):
            sel.append((r, q, pay))
    print(f"drill {name}: {len(sel)} bets")

    def tab(title, keyf):
        groups = defaultdict(lambda: defaultdict(list))
        for r, q, pay in sel:
            g = keyf(r, q)
            groups[g][r["ev"]].append((roi(q, pay, r["fee"], SLIP), roi(q, pay, r["fee"], SLIP_HARD),
                                       roi(q, pay, r["fee"], SLIP) - base[(half_of[r["ev"]], side, int(q * 50), r["h"])], pay))
        print(f"\n{title}\n| group | events | bets | won | +2c | +5c | vs twins |\n|---|---|---|---|---|---|---|")
        for g in sorted(groups):
            evs = groups[g]
            em = [[sum(x[i] for x in v) / len(v) for i in range(4)] for v in evs.values()]
            n = len(em)
            print(f"| {g} | {n} | {sum(len(v) for v in evs.values())} | {sum(1 for v in evs.values() for x in v if x[3] >= 0.5)} | "
                  f"{m100(sum(e[0] for e in em) / n)} | {m100(sum(e[1] for e in em) / n)} | {m100(sum(e[2] for e in em) / n)} |")

    tab("by month (end date)", lambda r, q: bt.iso_t(r["end"])[:7])
    tab("by half", lambda r, q: half_of[r["ev"]])
    tab("by days before the end", lambda r, q: r["h"])
    tab("by price", lambda r, q: f"{int(q * 20) * 5:02d}-{int(q * 20) * 5 + 5}c")
    tab("by topic", lambda r, q: calib.topic(r["q"]))
    tab("by city / first words", lambda r, q: " ".join(re.sub(r"[^a-z ]", " ", r["q"].lower()).split()[:7])[-28:])
    tab("all", lambda r, q: "all")
    rng = __import__("random").Random(4)
    print("\nsample questions:")
    for r, q, pay in rng.sample(sel, min(25, len(sel))):
        print(f"- {r['q'][:100]} | {q * 100:.0f}c | {'won' if pay >= 0.5 else 'lost'} | {bt.iso_t(r['end'])[:10]}")


def volbias():
    """Selection-bias detector. The cache only keeps markets with FINAL volume over $20k, and the market that wins
    tends to draw volume late. In an event with many choices (weather buckets, 'most seats'), that drops losing
    choices and keeps winners. Test: 1 day before the end, add up the YES prices of the choices we have. With no
    bias, the number of choices that win should match that sum on average. More wins than the sum = biased data."""
    markets_all, hist, complete = load_full()
    markets = {k: m for k, m in in_sample(markets_all).items() if not m.get("sports")}
    by_ev = defaultdict(list)
    for m in markets.values():
        if hist.get(m["id"]) and hist[m["id"]][0] and calib.outcome0(m) is not None:
            by_ev[m.get("ev") or m["id"]].append(m)
    g = defaultdict(lambda: [0, 0.0, 0, 0])   # events, sum of prices, wins, markets
    for ev, ms in by_ev.items():
        t = min(m["end"] for m in ms) - DAY
        ps, wins = 0.0, 0
        for m in ms:
            T, P = hist[m["id"]]
            k = bisect.bisect_right(T, t) - 1
            if k < 0 or t - T[k] > 3 * DAY or (m.get("closed_t") and t >= m["closed_t"]):
                break
            ps += P[k]
            wins += calib.outcome0(m)
        else:
            n = len(ms)
            key = (calib.topic(ms[0]["q"]), ("1" if n == 1 else "2-4" if n <= 4 else "5+") +
                   ("" if complete is None else " whole event" if ev in complete else " partial"))
            a = g[key]
            a[0] += 1
            a[1] += ps
            a[2] += wins
            a[3] += n
    # Part 2, for any kind of market (also not-one-winner events like "will X say Y"): per market, YES price 1 day
    # before the end vs how often YES won, in the main cache (final volume > $20k) and in the small sample below it.
    # If the cut bends results, the two rows of a topic differ. Also NO's return at +2c, per event, as mention_no buys.
    main_ids = set(bt.rjson(os.path.join(bt.CACHE, "markets.json.gz"), {}).get("markets", {}))
    small = bt.rjson(os.path.join(bt.CACHE, "small_markets.json.gz"), {}) or {}
    shist = bt.rjson(os.path.join(bt.CACHE, "small_hist.json.gz"), {}) or {}
    small = {k: m for k, m in in_sample(small).items() if k not in markets_all and not m.get("sports")}
    srcs = [("main cache (>$20k)", {k: m for k, m in markets.items() if k in main_ids}, hist)]
    if complete is not None:
        srcs.append(("whole events", {k: m for k, m in markets.items() if (m.get("ev") or m["id"]) in complete}, hist))
    if small:
        srcs.append(("small sample ($1k-20k)", small, shist))
    print("| topic | data | markets | events | YES prices added up (1 day out) | YES won | won / expected | "
          "NO 25-90c first time within 7 days, +2c, per $100 (events) |")
    print("|---|---|---|---|---|---|---|---|")

    def px(T, P, m, t):
        k = bisect.bisect_right(T, t) - 1
        if k < 0 or t - T[k] > 3 * DAY or (m.get("closed_t") and t >= m["closed_t"]) or not 0.02 <= P[k] <= 0.98:
            return None
        return P[k]

    for src, mks, hh in srcs:
        agg = defaultdict(lambda: [0, set(), 0.0, 0, defaultdict(list)])
        for m in mks.values():
            y = calib.outcome0(m)
            h = hh.get(m["id"])
            if y is None or not h or not h[0]:
                continue
            T, P = h
            a = agg[calib.topic(m["q"])]
            p1 = px(T, P, m, m["end"] - DAY)
            if p1 is not None:
                a[0] += 1
                a[1].add(m.get("ev") or m["id"])
                a[2] += p1
                a[3] += y
            for hz in (7, 3, 1):   # first time inside the 7-day window, like mention_no
                p = px(T, P, m, m["end"] - hz * DAY)
                if p is not None:
                    if 0.25 <= 1 - p < 0.90:
                        a[4][m.get("ev") or m["id"]].append(roi(1 - p, 1 - y, m.get("fee", 0), SLIP))
                    break
        for tp in sorted(agg):
            n, evs, ps, w, no = agg[tp]
            if n < 30:
                continue
            em = [sum(v) / len(v) for v in no.values()]
            nr = f"{m100(sum(em) / len(em))} ({len(em)})" if em else "-"
            print(f"| {tp} | {src} | {n} | {len(evs)} | {ps:.0f} | {w} | {w / max(ps, 1e-9):.2f} | {nr} |")
    print()
    print("| topic | markets we have per event | events | avg markets | YES prices added up (expected wins) | real wins | wins / expected |")
    print("|---|---|---|---|---|---|---|")
    for key in sorted(g):
        n, ps, w, nm = g[key]
        if n >= 20:
            print(f"| {key[0]} | {key[1]} | {n} | {nm / n:.1f} | {ps:.0f} | {w} | {w / max(ps, 1e-9):.2f} |")


def list_ideas():
    for n, s, _, cross in FEATURES:
        print(f"- {n}{' (x topics)' if cross and TOPIC_CROSS else ''}: {s}")
    print(f"{len(FEATURES)} features x their values x {len(calib.TOPICS) + 2} topic crosses x 2 sides x {len(BANDS)} "
          f"bands x {len(set(HGROUP.values()))} horizon groups")


# ================================================================ selftest

def selftest():
    """Fake fair markets plus one planted edge: questions with 'zebra' in them resolve YES 15 points more often
    than their price says. The machine must find zebra and must not pass any placebo."""
    import random
    rng = random.Random(11)
    markets, hist = {}, {}
    t0 = int(dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc).timestamp())
    for i in range(16000):
        end = t0 + (i % 200) * DAY + 3600 * (i % 7)
        zebra = i % 8 == 0
        p = rng.choice([0.3, 0.4, 0.5, 0.6])
        prob = min(0.98, p + 0.15) if zebra else p
        y = 1 if rng.random() < prob else 0
        q = f"Will the zebra number {i} happen?" if zebra else f"Will event number {i} happen?"
        mk = {"id": str(i), "q": q, "outs": ["Yes", "No"], "toks": [f"a{i}", f"b{i}"], "end": end, "start": end - 40 * DAY,
              "closed": True, "closed_t": end + 3600, "final": [float(y), float(1 - y)], "uma": "resolved", "vol": 30000,
              "fee": 0.0, "sports": False, "slug": f"m{i}", "ev": f"e{i}", "ev_slug": ""}
        markets[mk["id"]] = mk
        hist[mk["id"]] = [[end - 39 * DAY + k * 12 * 3600 for k in range(80)], [p] * 80]
    feature("words: zebra", "planted test edge", cross=False)(has(r"zebra"))
    try:
        rows = build_rows(markets, hist, horizons=(1, 7))
        acc, cut = screen(rows)
        surv, info = select(acc)
        found = [k for k in surv if "zebra = yes" in k[0] and k[1] == 0]
        plac = [k for k in surv if is_placebo(k)]
        assert found, ("planted edge not found", info)
        assert not plac, ("placebo passed", plac)
        report(acc, cut, rows, surv, info, len(markets))
        print(f"ideas selftest ok: planted edge found in {len(found)} cells, {len(surv)} survivors, 0 placebos, "
              f"{info['ideas']} ideas")
    finally:
        FEATURES[:] = [f for f in FEATURES if f[0] != "words: zebra"]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "volbias":
        volbias()
    elif cmd.startswith("drill_"):
        drill(cmd[len("drill_"):])
    else:
        {"run": run, "list": list_ideas, "selftest": selftest}[cmd]()
