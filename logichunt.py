#!/usr/bin/env python3
"""Logic hunt (research only, 2026-11-09): markets whose prices break simple logic, the kinds the
`ladder` and `every_horse` tracks do NOT already cover. Saves nothing, pushes nothing.
Run through the probe workflow: what = lh_all | lh_nested | lh_groups | lh_cross | lh_kalshi | lh_watch_<minutes>.

Reuses bot.py for everything that touches money: the market scan, the order books, walk(), the fees,
and bot.ladder_pairs() itself for the cross-event ladders.

  nested   Polymarket, across events. Two one-winner lists about the same names where one can only
           happen if the other does ("wins the NBA Finals" -> "wins the West"; "wins the presidency" ->
           "is the nominee"). NO on the stricter + YES on the looser pays at least $1. The direction is
           read from the crowd (the stricter list is lower for nearly every name) and then checked by eye.
  groups   Polymarket, one event of plain yes/no markets (NOT a linked one-winner list) whose prices add
           up to about $1, so the outcomes look like they exclude each other. Nothing links them, so
           nothing forces the sum to stay at $1. All-NO pays at least n-1 when at most one can win.
  cross    Polymarket, the ladder detector run across events: the same question and rules text in two
           different events, differing only by strike or deadline. Pairs inside one event are skipped
           (the ladder track already watches those).
  kalshi   Kalshi, inside one event: strike ladders ("above 4,000" vs "above 4,100") and mutually exclusive
           sets (all-YES vs $1, all-NO vs n-1). Kalshi's book lists bids only; asks come from the other side.
  watch    Runs nested + groups + cross + kalshi once, then re-prices every candidate on the real books
           every 3 minutes for <minutes> and reports how long each gap lasted.
"""
import datetime as dt
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import bot
from bot import fnum, jlist, now, parse_iso

SHARES = 5
OUT = "logichunt_out"
GENERIC = {"other", "others", "yes", "no", "none", "field", "any other", "someone else", "tie", "draw", "no one"}


def mid(m):
    b, a = fnum(m.get("bestBid"), None), fnum(m.get("bestAsk"), None)
    return None if b is None or a is None else (a + b) / 2


def ev_of(m):
    evs = m.get("events") or []
    return evs[0] if evs and isinstance(evs[0], dict) else {}


def is_negrisk(m):
    e = ev_of(m)
    return bool(e.get("negRisk") or e.get("enableNegRisk") or m.get("negRisk"))


def end_of(m):
    return parse_iso(m.get("endDateIso") or m.get("endDate"))


def norm_name(s):
    s = re.sub(r"[^a-z0-9 ]+", " ", str(s or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def scan_poly():
    ms = bot._scan_markets({"end_date_min": bot.iso(now()), "end_date_max": bot.iso(now() + dt.timedelta(days=800)),
                            "liquidity_num_min": 100})
    out = [m for m in ms if not m.get("closed") and m.get("acceptingOrders") is not False and bot.yes_no_tokens(m)
           and mid(m) is not None]
    print(f"poly: {len(out)} open yes/no markets with prices")
    return out


_books = {}


def pbook(tok):
    if tok not in _books:
        _books[tok] = bot.book(tok)
    return _books[tok]


def legs_cost(legs, shares=SHARES):
    """legs = [(token, fee_rate)] bought on Polymarket's real books. Returns (cost per share, min depth) or None."""
    with ThreadPoolExecutor(8) as ex:
        bks = list(ex.map(pbook, [t for t, _ in legs]))
    if any(not b for b in bks):
        return None
    n = max([shares] + [b["min_size"] for b in bks])
    total = 0.0
    for (t, rate), b in zip(legs, bks):
        p = bot.walk(b["asks"], n)
        if p is None:
            return None
        total += n * p + bot.taker_fee(n, p, rate)
    return total / n


def annual(edge, cost, end):
    days = max(1.0, ((end or now()) - now()).total_seconds() / 86400) + 3
    return edge / max(cost, 0.01) * 365 / days, days


# ------------------------------------------------------------------ nested lists across events

LEAGUE = [("football", r"\b(nfl|pro football|super bowl|afc|nfc)\b"), ("basketball", r"\b(nba|pro basketball)\b"),
          ("hockey", r"\b(nhl|pro hockey|stanley cup)\b"), ("baseball", r"\b(mlb|pro baseball|world series)\b"),
          ("wnba", r"\bwnba\b")]
CONF = r"\b(afc|nfc|eastern|western|east|west|american league|national league|al|nl)\b"
SKIP_T = r"\b(mvp|player|coach|rookie|trophy|award|division|cup winner|nba cup|record|leader|seed|draft|next team|2nd|3rd|worst|fewest)\b" \
         r"|\b(afc|nfc|al|nl|american league|national league) (north|south|east|west|central)\b" \
         r"|\b(atlantic|metropolitan|pacific|central|southeast|northwest|southwest)\b"


def level(title):
    """(league, level) for sports futures lists: 3 = league champion, 2 = conference champion, 1 = makes the playoffs.
    A team at level 3 must also be at levels 2 and 1, so P(3) <= P(2) <= P(1)."""
    t = str(title or "").lower()
    lg = next((k for k, rx in LEAGUE if re.search(rx, t)), None)
    if not lg or re.search(SKIP_T, t):
        return None
    if re.search(r"make (the )?playoffs|playoff teams|qualify for (the )?playoffs|reach (the )?playoffs", t):
        return lg, 1
    if re.search(r"champion|winner", t):
        return lg, (2 if re.search(CONF, t) else 3)
    return None


def hunt_nested(ms):
    """Polymarket, across events: league champion -> conference champion -> makes the playoffs, team by team."""
    lists = {}
    for m in ms:
        e = ev_of(m)
        lv = level(e.get("title"))
        name = norm_name(m.get("groupItemTitle"))
        if not lv or not name or name in GENERIC:
            continue
        k = str(e.get("id") or "")
        lists.setdefault(k, {"title": e.get("title"), "lv": lv, "end": end_of(m), "m": {}})["m"][name] = m
    by_lg = defaultdict(list)
    for L in lists.values():
        by_lg[L["lv"][0]].append(L)
    rows, npairs = [], 0
    for lg, Ls in by_lg.items():
        for s in Ls:
            for l in Ls:
                if s["lv"][1] <= l["lv"][1]:
                    continue
                if abs(((s["end"] or now()) - (l["end"] or now())).days) > 200:
                    continue  # different seasons
                if s["lv"][1] == 3 and l["lv"][1] == 2 and len(set(s["m"]) & set(l["m"])) < 3:
                    continue
                names = set(s["m"]) & set(l["m"])
                if not names:
                    continue
                npairs += 1
                bad = sum(mid(s["m"][x]) > mid(l["m"][x]) + 0.005 for x in names)
                print(f"  PAIR {lg}: {s['title']!r} -> {l['title']!r}: {len(names)} teams, {bad} priced the wrong way round")
                for x in names:
                    a, b = s["m"][x], l["m"][x]
                    listed = 1 - ((1 - fnum(a["bestBid"])) + fnum(b["bestAsk"]))
                    if listed > -0.01:
                        rows.append({"kind": "nested", "name": x, "stricter": s["title"], "looser": l["title"],
                                     "s_slug": a.get("slug"), "l_slug": b.get("slug"), "listed": round(listed, 4),
                                     "legs": [(bot.yes_no_tokens(a)[1], bot.fee_rate(a)), (bot.yes_no_tokens(b)[0], bot.fee_rate(b))],
                                     "payout": 1.0, "end": max(end_of(a) or now(), end_of(b) or now())})
    print(f"nested: {len(lists)} sports futures lists, {npairs} champion/conference/playoff pairs, {len(rows)} near or under $1 listed")
    return rows


# ------------------------------------------------------------------ yes/no groups that add up to about $1

def hunt_groups(ms):
    by_ev = defaultdict(list)
    for m in ms:
        if is_negrisk(m):
            continue
        k = str(ev_of(m).get("id") or "")
        if k:
            by_ev[k].append(m)
    rows, n_groups, sums = [], 0, Counter()
    for k, g in by_ev.items():
        if len(g) < 3:
            continue
        titles = [norm_name(m.get("groupItemTitle")) for m in g]
        if not all(titles) or len(set(titles)) != len(titles):
            continue
        if len({(end_of(m) or now()).date() for m in g}) > 1:
            continue  # different deadlines = a ladder, not one-of-many
        tot = sum(mid(m) for m in g)
        sums[round(tot, 1)] += 1
        if not 0.85 <= tot <= 1.15:
            continue
        n_groups += 1
        ev = ev_of(g[0])
        end = max(end_of(m) or now() for m in g)
        no_listed = (len(g) - 1) - sum(1 - fnum(m["bestBid"]) for m in g)
        yes_listed = 1 - sum(fnum(m["bestAsk"]) for m in g)
        print(f"  GROUP {ev.get('title')!r} n={len(g)} sum={tot:.3f} all-NO listed {no_listed:+.3f} all-YES listed {yes_listed:+.3f}"
              f" names={titles[:8]}")
        if no_listed > -0.01 * len(g):
            rows.append({"kind": "group_no", "event": ev.get("title"), "slug": ev.get("slug"), "n": len(g),
                         "listed": round(no_listed / (len(g) - 1), 4), "payout": len(g) - 1.0, "end": end,
                         "legs": [(bot.yes_no_tokens(m)[1], bot.fee_rate(m)) for m in g]})
        if yes_listed > -0.01 * len(g):
            rows.append({"kind": "group_yes", "event": ev.get("title"), "slug": ev.get("slug"), "n": len(g),
                         "listed": round(yes_listed, 4), "payout": 1.0, "end": end, "needs": "list must be complete",
                         "legs": [(bot.yes_no_tokens(m)[0], bot.fee_rate(m)) for m in g]})
    print(f"groups: {n_groups} plain yes/no groups adding up to $0.85-1.15; sum histogram {sorted(sums.items())[:30]}")
    return rows


# ------------------------------------------------------------------ the ladder detector across events

def hunt_cross(ms):
    r = dict(bot.ladder_rules()[1])
    fake = []
    for m in ms:
        if is_negrisk(m):
            continue
        tq, _, _ = bot.ladder_template(m.get("question"))
        m2 = dict(m)
        m2["_real_ev"] = str(ev_of(m).get("id") or "")
        m2["events"] = [{"id": "T|" + tq}]
        fake.append(m2)
    pairs, stats = bot.ladder_pairs(fake, r)
    cross = [(a, b, k) for a, b, k in pairs if a["_real_ev"] != b["_real_ev"]]
    print(f"cross: {len(pairs)} ladder pairs by question text, {len(cross)} of them across two events; {dict(stats)}")
    rows = []
    for a, b, kind in cross:
        listed = 1 - ((1 - fnum(a["bestBid"])) + fnum(b["bestAsk"]))
        if listed > -0.003:
            rows.append({"kind": "cross_" + kind, "stricter": a.get("question"), "looser": b.get("question"),
                         "s_slug": a.get("slug"), "l_slug": b.get("slug"), "listed": round(listed, 4), "payout": 1.0,
                         "legs": [(bot.yes_no_tokens(a)[1], bot.fee_rate(a)), (bot.yes_no_tokens(b)[0], bot.fee_rate(b))],
                         "end": max(end_of(a) or now(), end_of(b) or now())})
    for x in cross[:15]:
        print(f"  CROSS {x[2]}: {x[0].get('question')!r} -> {x[1].get('question')!r}")
    return rows


# ------------------------------------------------------------------ Kalshi: ladders and exclusive sets in one event

def kalshi_events():
    out, cursor = [], None
    for page in range(300):
        p = {"status": "open", "with_nested_markets": "true", "limit": 200}
        if cursor:
            p["cursor"] = cursor
        try:
            res = bot.kalshi_get("/events", p)
        except Exception as e:
            print(f"kalshi events page {page}: {e}")
            break
        out += res.get("events") or []
        cursor = res.get("cursor")
        if not cursor:
            break
    print(f"kalshi: {len(out)} open events")
    return out


def k_complete(ms):
    """True when the markets tile the whole number line: one '< low', buckets with no gaps, one '> high'."""
    lo = [m for m in ms if m.get("strike_type") in ("less", "less_or_equal")]
    hi = [m for m in ms if m.get("strike_type") in ("greater", "greater_or_equal")]
    mid_ = sorted((m for m in ms if m.get("strike_type") == "between"), key=lambda m: fnum(m.get("floor_strike")))
    if len(lo) != 1 or len(hi) != 1 or len(mid_) + 2 != len(ms):
        return False
    edges = [fnum(lo[0].get("cap_strike"))] + [x for m in mid_ for x in (fnum(m.get("floor_strike")), fnum(m.get("cap_strike")))] \
        + [fnum(hi[0].get("floor_strike"))]
    ints = all(float(x).is_integer() for x in edges)
    for i in range(0, len(edges) - 1, 2):
        gap = edges[i + 1] - edges[i]
        if gap < -1e-9 or gap > (1.0 if ints else 0.011):
            return False
    return True


def kq(m, side):
    return bot.kpx(m, f"{side}_ask")


def hunt_kalshi():
    evs = kalshi_events()
    rows, st = [], Counter()
    for e in evs:
        ms = [m for m in (e.get("markets") or []) if str(m.get("status") or "").lower() in ("active", "open")]
        ms = [m for m in ms if kq(m, "yes") and kq(m, "no") and 0 < kq(m, "yes") < 1 and 0 < kq(m, "no") < 1]
        if len(ms) < 2:
            continue
        end = max(parse_iso(m.get("close_time")) or now() for m in ms)
        # strike ladders
        for typ, up in (("greater", True), ("greater_or_equal", True), ("less", False), ("less_or_equal", False)):
            lad = [m for m in ms if m.get("strike_type") == typ and m.get("floor_strike" if up else "cap_strike") is not None]
            if len(lad) < 2:
                continue
            st["ladders"] += 1
            key = "floor_strike" if up else "cap_strike"
            lad.sort(key=lambda m: fnum(m.get(key)))
            subj = lambda m: (re.sub(r"-?[\d.]+$", "", str(m.get("ticker"))),
                              re.sub(r"[\d.,]+", "#", str(m.get("yes_sub_title") or m.get("subtitle") or "")))
            for i, lo in enumerate(lad):
                for hi in lad[i + 1:]:
                    if fnum(hi.get(key)) == fnum(lo.get(key)) or subj(hi) != subj(lo):
                        continue
                    if lo.get("close_time") != hi.get("close_time"):
                        continue
                    a, b = (hi, lo) if up else (lo, hi)  # a = stricter
                    listed = 1 - (kq(a, "no") + kq(b, "yes"))
                    st["ladder pairs"] += 1
                    if listed > -0.003:
                        rows.append({"kind": "k_ladder", "event": e.get("event_ticker"), "title": e.get("title"),
                                     "stricter": a.get("ticker"), "looser": b.get("ticker"), "listed": round(listed, 4),
                                     "payout": 1.0, "end": end, "klegs": [(a.get("ticker"), "no"), (b.get("ticker"), "yes")]})
        # mutually exclusive sets
        if e.get("mutually_exclusive") and len(ms) >= 2:
            st["exclusive sets"] += 1
            n = len(ms)
            no_listed = (n - 1) - sum(kq(m, "no") for m in ms)
            yes_listed = 1 - sum(kq(m, "yes") for m in ms)
            if no_listed > -0.003 * n:
                rows.append({"kind": "k_all_no", "event": e.get("event_ticker"), "title": e.get("title"), "n": n,
                             "listed": round(no_listed / max(n - 1, 1), 4), "payout": n - 1.0, "end": end,
                             "klegs": [(m.get("ticker"), "no") for m in ms]})
            if yes_listed > -0.003 * n and k_complete(ms):
                rows.append({"kind": "k_all_yes", "event": e.get("event_ticker"), "title": e.get("title"), "n": n,
                             "listed": round(yes_listed, 4), "payout": 1.0, "end": end, "needs": "list must be complete",
                             "klegs": [(m.get("ticker"), "yes") for m in ms]})
    print(f"kalshi: {dict(st)}; {len(rows)} look cheap or near on listed prices")
    return rows


_kb = {}


def kbook(t):
    if t not in _kb:
        _kb[t] = bot.kalshi_asks(t)
    return _kb[t]


def klegs_cost(legs, shares=SHARES):
    with ThreadPoolExecutor(6) as ex:
        bks = list(ex.map(kbook, [t for t, _ in legs]))
    total = 0.0
    for (t, side), b in zip(legs, bks):
        if not b:
            return None
        p = bot.walk(b[0] if side == "yes" else b[1], shares)
        if p is None:
            return None
        total += shares * p + bot.kalshi_fee(shares, p)
    return total / shares


# ------------------------------------------------------------------ pricing on real books

def price(rows, limit=120):
    rows = sorted(rows, key=lambda r: -r["listed"])[:limit]
    out = []
    for r in rows:
        c = klegs_cost(r["klegs"]) if "klegs" in r else legs_cost(r["legs"])
        if c is None:
            r["book"] = "too thin"
            continue
        r["cost"] = round(c, 4)
        r["edge"] = round(r["payout"] - c, 4)  # per share of the set
        r["annual"], r["days"] = annual(r["edge"], c, r["end"])
        out.append(r)
    out.sort(key=lambda r: -r["edge"])
    return out


def show(rows, title):
    good = [r for r in rows if r["edge"] >= 0.01]
    print(f"\n=== {title}: {len(rows)} priced on real books; edge >= 0: {sum(r['edge'] >= 0 for r in rows)}, "
          f">= 1c: {len(good)}, >= 2c: {sum(r['edge'] >= 0.02 for r in rows)}, "
          f">= 2c and >= 15%/yr: {sum(r['edge'] >= 0.02 and r['annual'] >= 0.15 for r in rows)}")
    for r in rows[:25]:
        d = {k: v for k, v in r.items() if k not in ("legs", "klegs")}
        d["end"] = bot.iso(r["end"]) if isinstance(r["end"], dt.datetime) else r["end"]
        d["annual"] = round(r["annual"], 3)
        print(json.dumps(d, default=str))


def run_all(which):
    rows = []
    ms = scan_poly() if which & {"nested", "groups", "cross"} else []
    if "nested" in which:
        rows += hunt_nested(ms)
    if "groups" in which:
        rows += hunt_groups(ms)
    if "cross" in which:
        rows += hunt_cross(ms)
    if "kalshi" in which:
        rows += hunt_kalshi()
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r["kind"]].append(r)
    print("\nlisted-price candidates by kind:", {k: len(v) for k, v in by_kind.items()},
          "listed >= 1c:", dict(Counter(r["kind"] for r in rows if r["listed"] >= 0.01)))
    priced = []
    for k, v in by_kind.items():
        p = price(v)
        show(p, k)
        priced += p
    return priced


def watch(minutes):
    priced = run_all({"nested", "groups", "cross", "kalshi"})
    cands = [r for r in priced if r["edge"] >= -0.01][:150]
    print(f"\nwatch: re-pricing {len(cands)} candidates every 3 min for {minutes} min")
    hist = defaultdict(list)
    t0 = time.time()
    while time.time() - t0 < minutes * 60:
        _books.clear()
        _kb.clear()
        for i, r in enumerate(cands):
            c = klegs_cost(r["klegs"]) if "klegs" in r else legs_cost(r["legs"])
            hist[i].append(None if c is None else round(r["payout"] - c, 4))
        print(f"  {round((time.time() - t0) / 60)} min: {sum(1 for h in hist.values() if h[-1] is not None and h[-1] >= 0.01)} at >= 1c")
        time.sleep(180)
    print("\nwatch result (edge per share over time; one value per 3 min):")
    rows = []
    for i, r in enumerate(cands):
        h = [x for x in hist[i] if x is not None]
        if not h:
            continue
        rows.append((sum(x >= 0.01 for x in h), r, hist[i]))
    rows.sort(key=lambda x: -x[0])
    for n, r, h in rows[:40]:
        name = r.get("name") or r.get("event") or r.get("stricter")
        print(f"  {r['kind']:10s} {n:3d}/{len(h)} checks >= 1c  {str(name)[:70]!r}  {h}")
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/watch.json", "w") as f:
        json.dump([{"kind": r["kind"], "row": {k: v for k, v in r.items() if k not in ("legs", "klegs", "end")},
                    "hist": h} for n, r, h in rows], f, default=str)


if __name__ == "__main__":
    what = (sys.argv[1] if len(sys.argv) > 1 else "all").replace("lh_", "")
    if what.startswith("kevent_"):
        ev = bot.kalshi_get(f"/events/{what[7:]}", {"with_nested_markets": "true"})
        for m in (ev.get("event") or {}).get("markets") or ev.get("markets") or []:
            print(json.dumps({k: m.get(k) for k in ("ticker", "status", "strike_type", "floor_strike", "cap_strike", "yes_sub_title",
                  "yes_bid_dollars", "yes_ask_dollars", "no_ask_dollars", "last_price_dollars", "volume", "rules_primary")}))
            print("  book:", kbook(m["ticker"]))
    elif what.startswith("watch"):
        watch(int(what.split("_")[1]) if "_" in what else 60)
    else:
        run_all({"nested", "groups", "cross", "kalshi"} if what == "all" else {what})
