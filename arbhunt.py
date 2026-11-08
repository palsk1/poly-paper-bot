#!/usr/bin/env python3
"""Arb hunt (research only): looks for NEW kinds of safe pairs and measures how often they pay.
Saves nothing, pushes nothing. Run through the probe workflow: what = hunt | hunt_ladders | hunt_rejected | hunt_sports.

Pair kinds measured:
  ladders   Inside Polymarket. Markets in one event that differ only by a strike or a deadline, where one
            market's YES can only happen if the other's does ("BTC above 120k" -> "above 110k";
            "ceasefire by Dec 31" -> "by Mar 31"). Buying NO on the stricter one + YES on the looser one pays
            at least $1 whatever happens (and $2 if only the looser one comes true).
  dupes     Inside Polymarket. The same question listed twice (different events).
  rejected  Kalshi x Polymarket pairs the review rejected. Many differ in a one-way way (Kalshi needs MORE
            than Polymarket), so one direction is still safe. Prints both directions' real book cost.
  sports    Kalshi game winner vs Polymarket moneyline, next few days. Measures overlap and gaps.
"""
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import bot
from bot import fnum, jlist, now, parse_iso

SHARES = 5
_MON = "january|february|march|april|may|june|july|august|september|october|november|december|" \
       "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
DATE_RE = re.compile(rf"\b({_MON})\.?\s+\d{{1,2}}(st|nd|rd|th)?(,?\s+\d{{4}})?\b|\b\d{{1,2}}(st|nd|rd|th)?\s+(of\s+)?({_MON})\b"
                     rf"|\b({_MON})\s+\d{{4}}\b|\bq[1-4]\s+\d{{4}}\b|\b(end of|in)\s+\d{{4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b")
NUM_RE = re.compile(r"[$€£]?\d[\d,]*(?:\.\d+)?\s*(?:k|m|b|bn|million|billion|trillion|%|bps|c)?\b", re.I)
UP = re.compile(r"\b(above|over|more than|at least|reach|reaches|hit|hits|exceed|exceeds|or more|or higher|greater than|"
                r"surpass|top|tops)\b|\+|↑|>")
DOWN = re.compile(r"\b(below|under|less than|at most|dip|dips|fall to|falls to|drop to|drops to|or lower|or less|"
                  r"fewer than)\b|↓|<")
CUMUL = re.compile(r"\b(by|before|until|prior to|no later than)\b")


def num_value(s):
    s = s.lower().replace(",", "").strip()
    m = re.match(r"[$€£]?(\d+(?:\.\d+)?)\s*(.*)$", s)
    if not m:
        return None
    mult = {"k": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9, "trillion": 1e12}
    return float(m.group(1)) * mult.get(m.group(2).strip(), 1)


def strip_dates(t):
    return DATE_RE.sub(" <D> ", t)


def template(text):
    """Text with dates -> <D> and numbers -> <N>; returns (template, [numbers])."""
    t = strip_dates(str(text or "").lower())
    nums = []

    def rep(m):
        v = num_value(m.group(0))
        if v is None or (1990 <= v <= 2100 and "." not in m.group(0) and "$" not in m.group(0)):
            return m.group(0)  # years stay part of the text
        nums.append(v)
        return " <N> "
    t = NUM_RE.sub(rep, t)
    return re.sub(r"\s+", " ", t).strip(), nums


def yes_no(m):
    toks, outs = bot.market_tokens(m), [str(o).lower() for o in jlist(m.get("outcomes"))]
    if len(toks) != 2 or outs != ["yes", "no"]:
        return None
    return toks[0], toks[1]


def end_of(m):
    return parse_iso(m.get("endDateIso") or m.get("endDate"))


def ev_key(m):
    evs = m.get("events") or []
    e = evs[0] if evs and isinstance(evs[0], dict) else {}
    return str(e.get("id") or e.get("slug") or ""), str(e.get("slug") or "")


def book_cost(no_tok, yes_tok, rate_a, rate_b):
    """Real cost to buy SHARES of NO(a) + YES(b) on the live books, fees included. None if too thin."""
    with ThreadPoolExecutor(2) as ex:
        ba, bb = list(ex.map(bot.book, [no_tok, yes_tok]))
    if not ba or not bb:
        return None
    n = max(SHARES, ba["min_size"], bb["min_size"])
    pa, pb = bot.walk(ba["asks"], n), bot.walk(bb["asks"], n)
    if pa is None or pb is None:
        return None
    fees = bot.taker_fee(n, pa, rate_a) + bot.taker_fee(n, pb, rate_b)
    cost = n * (pa + pb) + fees
    return {"shares": n, "p_no_a": round(pa, 4), "p_yes_b": round(pb, 4), "fees": round(fees, 4),
            "cost_per_share": round(cost / n, 4), "edge": round(1 - cost / n, 4),
            "depth_no_a": round(sum(s for p, s in ba["asks"] if p <= pa + 0.01)),
            "depth_yes_b": round(sum(s for p, s in bb["asks"] if p <= pb + 0.01))}


def scan_poly(max_days=400):
    ms = bot._scan_markets({"end_date_min": bot.iso(now()), "end_date_max": bot.iso(now() + dt.timedelta(days=max_days)),
                            "liquidity_num_min": 200})
    out = []
    for m in ms:
        if m.get("closed") or m.get("acceptingOrders") is False or not yes_no(m):
            continue
        if fnum(m.get("bestBid"), None) is None or fnum(m.get("bestAsk"), None) is None:
            continue
        out.append(m)
    return out


# ------------------------------------------------------------------ ladders (inside Polymarket)

def ladder_pairs(ms):
    """Same detector the ladder track uses (bot.ladder_pairs), so this probe measures exactly what it would trade."""
    return bot.ladder_pairs(ms, bot.ladder_rules()[1])


def hunt_ladders(ms=None):
    ms = ms if ms is not None else scan_poly()
    pairs, stats = ladder_pairs(ms)
    print(f"ladders: {len(ms)} yes/no markets, stats {dict(stats)}, implied pairs {len(pairs)}")
    ids = sorted({str(m.get("id")) for a, b, _ in pairs[:150] for m in (a, b)})
    fresh = bot.gamma_markets_by_id(ids)
    print(f"batch price fetch: asked {len(ids)} markets, got {len(fresh)}")
    by_kind = Counter(k for _, _, k in pairs)
    print("implied pairs by kind:", dict(by_kind))
    # listed check first: NO ask(A) ~ 1 - bestBid(A); YES ask(B) = bestAsk(B)
    near = []
    gaps = Counter()
    for a, b, kind in pairs:
        listed = 1 - (1 - fnum(a.get("bestBid")) + fnum(b.get("bestAsk")))
        gaps["listed >= 0c" if listed >= 0 else "listed < 0c"] += 1
        if listed >= 0.02:
            gaps["listed >= 2c"] += 1
        if listed > -0.005:
            near.append((listed, a, b, kind))
    print("listed price check:", dict(gaps))
    near.sort(key=lambda x: -x[0])
    rows = []
    for listed, a, b, kind in near[:60]:
        ya, yb = yes_no(a), yes_no(b)
        c = book_cost(ya[1], yb[0], bot.fee_rate(a), bot.fee_rate(b))
        if not c:
            continue
        end = max(end_of(a) or now(), end_of(b) or now())
        days = max(1.0, (end - now()).total_seconds() / 86400) + 3
        c["annual"] = round(c["edge"] / max(c["cost_per_share"], 0.01) * 365 / days, 3)
        c.update({"kind": kind, "listed": round(listed, 4), "days": round(days), "stricter": a.get("question"),
                  "looser": b.get("question"), "slug_a": a.get("slug"), "slug_b": b.get("slug"),
                  "event": ev_key(a)[1], "fee_a": bot.fee_rate(a), "fee_b": bot.fee_rate(b),
                  "p_yes_a": fnum(a.get("bestAsk")), "p_yes_b_mid": fnum(b.get("bestBid"))})
        rows.append(c)
    rows.sort(key=lambda r: -r["edge"])
    ok = [r for r in rows if r["edge"] >= 0.02 and r["annual"] >= 0.15]
    print(f"ladders on real books ({len(rows)} checked): edge>=0: {sum(r['edge'] >= 0 for r in rows)}, "
          f">=1c: {sum(r['edge'] >= 0.01 for r in rows)}, >=2c: {sum(r['edge'] >= 0.02 for r in rows)}, "
          f">=2c and >=15%/yr: {len(ok)}")
    for r in rows[:25]:
        print(json.dumps(r))
    return rows


# ------------------------------------------------------------------ duplicates (inside Polymarket)

def hunt_dupes(ms=None):
    ms = ms if ms is not None else scan_poly()
    by_q = defaultdict(list)
    for m in ms:
        q = re.sub(r"[^a-z0-9$%. ]+", " ", str(m.get("question") or "").lower())
        by_q[(re.sub(r"\s+", " ", q).strip(), (end_of(m) or now()).date())].append(m)
    dup = [(q, g) for q, g in by_q.items() if len({ev_key(m)[0] for m in g}) > 1]
    print(f"dupes: {len(dup)} questions listed in 2+ events with the same end date")
    for (q, d), g in dup[:20]:
        print(" ", q[:100], d, [(m.get("slug"), m.get("bestBid"), m.get("bestAsk")) for m in g][:4])


# ------------------------------------------------------------------ rejected cross-site pairs, both directions

def hunt_rejected():
    pairs = bot.load_pairs()
    rows = []
    for p in pairs["rejected"]:
        kt, slug = p["id"].split("|", 1)
        km, pm = bot.kalshi_market(kt), bot.market_by_slug(slug)
        if not km or not pm or pm.get("closed") or str(km.get("status") or "").lower() not in ("active", "open"):
            continue
        toks, outs = bot.market_tokens(pm), [str(o) for o in jlist(pm.get("outcomes"))]
        kb = bot.kalshi_asks(kt)
        if len(toks) != 2 or not kb:
            continue
        pb = [bot.book(toks[0]), bot.book(toks[1])]
        if not pb[0] or not pb[1]:
            continue
        rate = bot.fee_rate(pm)
        res = {}
        # 'k_yes+p_<out>' = Kalshi YES + Polymarket outcome
        for k_side, lv in (("yes", kb[0]), ("no", kb[1])):
            for j in (0, 1):
                pk, pp = bot.walk(lv, SHARES), bot.walk(pb[j]["asks"], SHARES)
                if pk is None or pp is None:
                    continue
                cost = SHARES * (pk + pp) + bot.kalshi_fee(SHARES, pk) + bot.taker_fee(SHARES, pp, rate)
                res[f"k_{k_side}+p_{outs[j]}"] = round(1 - cost / SHARES, 4)
        if res:
            best = max(res.items(), key=lambda x: x[1])
            rows.append({"id": p["id"], "best": best, "all": res, "reason": p.get("reason", "")[:160],
                         "kalshi_close": km.get("close_time"), "poly_end": pm.get("endDateIso")})
    rows.sort(key=lambda r: -r["best"][1])
    print(f"rejected pairs still open and priced: {len(rows)}; best leg >= 2c: {sum(r['best'][1] >= 0.02 for r in rows)}")
    for r in rows[:30]:
        print(json.dumps(r))


# ------------------------------------------------------------------ sports: Kalshi game winner vs Polymarket moneyline

K_SPORTS = ["KXNFLGAME", "KXNBAGAME", "KXNHLGAME", "KXNCAAFGAME", "KXNCAAMBGAME", "KXMLBGAME", "KXEPLGAME",
            "KXUCLGAME", "KXLALIGAGAME", "KXSERIEAGAME", "KXBUNDESLIGAGAME", "KXLIGUE1GAME", "KXMLSGAME",
            "KXWNBAGAME", "KXATPMATCH", "KXWTAMATCH", "KXUFCFIGHT"]


def hunt_sports():
    K = []
    for s in K_SPORTS:
        try:
            res = bot.kalshi_get("/markets", {"series_ticker": s, "status": "open", "limit": 1000})
        except Exception as e:
            print(f"kalshi {s}: {e}")
            continue
        ms = res.get("markets") or []
        close = [parse_iso(m.get("close_time")) for m in ms]
        soon = [m for m, c in zip(ms, close) if c and (c - now()).days <= 4]
        print(f"kalshi {s}: {len(ms)} open, {len(soon)} closing within 4 days")
        K += soon
    if K:
        print("kalshi sample rules:", json.dumps({k: K[0].get(k) for k in ("ticker", "event_ticker", "title",
              "yes_sub_title", "rules_primary", "rules_secondary", "close_time", "expected_expiration_time")})[:1800])
    ms = bot._scan_markets({"end_date_min": bot.iso(now() - dt.timedelta(days=1)),
                            "end_date_max": bot.iso(now() + dt.timedelta(days=5))})
    P = [m for m in ms if bot.is_sports(m) and not m.get("closed") and str(m.get("sportsMarketType") or "") == "moneyline"]
    print(f"poly sports moneyline markets in the next 5 days: {len(P)} (of {sum(bot.is_sports(m) for m in ms)} sports)")
    if P:
        print("poly sample:", json.dumps({k: P[0].get(k) for k in ("question", "slug", "outcomes", "sportsMarketType",
              "gameStartTime", "endDate", "feeSchedule", "feesEnabled", "description")})[:1800])
    # match: Kalshi yes_sub_title (team) + date vs Polymarket outcomes names + game date
    idx = defaultdict(list)
    for m in P:
        for o in jlist(m.get("outcomes")):
            for w in bot.text_tokens(o):
                if len(w) > 3:
                    idx[w].append(m)
    matched, gaps = [], []
    for k in K:
        team = str(k.get("yes_sub_title") or "")
        kd = parse_iso(k.get("expected_expiration_time") or k.get("close_time"))
        cands = Counter()
        for w in bot.text_tokens(team):
            for m in idx.get(w, ()):
                cands[m.get("slug")] += 1
        best = None
        for slug, _ in cands.most_common(5):
            m = next(x for x in P if x.get("slug") == slug)
            gs = parse_iso(m.get("gameStartTime") or m.get("endDate"))
            if gs and kd and abs((gs - kd).total_seconds()) > 2 * 86400:
                continue
            others = [str(o) for o in jlist(m.get("outcomes"))]
            if not any(bot.text_tokens(team) & bot.text_tokens(o) for o in others):
                continue
            # the Kalshi title should mention the other team too
            if not all(bot.text_tokens(o) & bot.text_tokens(k.get("title")) for o in others):
                continue
            best = m
            break
        if not best:
            continue
        outs = [str(o) for o in jlist(best.get("outcomes"))]
        j = max(range(2), key=lambda i: len(bot.text_tokens(team) & bot.text_tokens(outs[i])))
        matched.append((k, best, j))
    print(f"sports matched (Kalshi team market <-> Polymarket moneyline): {len(matched)}")
    for k, m, j in matched[:80]:
        toks = bot.market_tokens(m)
        kb = bot.kalshi_asks(k.get("ticker"))
        pb = [bot.book(toks[0]), bot.book(toks[1])]
        if not kb or not pb[0] or not pb[1]:
            continue
        rate = bot.fee_rate(m)
        best = None
        for k_side, lv, pj in (("yes", kb[0], 1 - j), ("no", kb[1], j)):
            pk, pp = bot.walk(lv, SHARES), bot.walk(pb[pj]["asks"], SHARES)
            if pk is None or pp is None:
                continue
            cost = SHARES * (pk + pp) + bot.kalshi_fee(SHARES, pk) + bot.taker_fee(SHARES, pp, rate)
            e = 1 - cost / SHARES
            if best is None or e > best[0]:
                best = (round(e, 4), k_side, round(pk, 3), round(pp, 3))
        if best:
            gaps.append((best, k.get("ticker"), m.get("slug"), rate))
    gaps.sort(key=lambda g: -g[0][0])
    print(f"sports on real books: {len(gaps)} checked; edge>=0: {sum(g[0][0] >= 0 for g in gaps)}, "
          f">=1c: {sum(g[0][0] >= 0.01 for g in gaps)}, >=2c: {sum(g[0][0] >= 0.02 for g in gaps)}")
    for g in gaps[:20]:
        print(" ", g)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "hunt"
    ms = scan_poly() if what in ("hunt", "hunt_ladders", "hunt_dupes") else None
    if what in ("hunt", "hunt_ladders"):
        hunt_ladders(ms)
    if what in ("hunt", "hunt_dupes"):
        hunt_dupes(ms)
    if what in ("hunt", "hunt_rejected"):
        hunt_rejected()
    if what in ("hunt", "hunt_sports"):
        hunt_sports()


# ------------------------------------------------------------------ sports v2: match by league + date + team codes

LEAGUES = {"nfl": "KXNFLGAME", "nba": "KXNBAGAME", "nhl": "KXNHLGAME", "cbb": "KXNCAAMBGAME", "cfb": "KXNCAAFGAME",
           "epl": "KXEPLGAME", "lal": "KXLALIGAGAME", "sea": "KXSERIEAGAME", "bun": "KXBUNDESLIGAGAME",
           "fl1": "KXLIGUE1GAME"}
SLUG_RE = re.compile(r"^([a-z0-9]+)-([a-z0-9]+)-([a-z0-9]+)-(\d{4})-(\d{2})-(\d{2})$")
KEV_RE = re.compile(r"^(KX[A-Z0-9]+GAME)-(\d{2})([A-Z]{3})(\d{2})([A-Z0-9]+)$")
_MONS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def kalshi_games(series):
    out = []
    try:
        res = bot.kalshi_get("/markets", {"series_ticker": series, "status": "open", "limit": 1000})
    except Exception as e:
        print(f"kalshi {series}: {e}")
        return out
    for m in res.get("markets") or []:
        mm = KEV_RE.match(str(m.get("event_ticker") or ""))
        if not mm:
            continue
        d = dt.date(2000 + int(mm.group(2)), _MONS.index(mm.group(3)) + 1, int(mm.group(4)))
        team = str(m.get("ticker") or "").rsplit("-", 1)[-1]
        out.append({"m": m, "date": d, "codes": mm.group(5), "team": team})
    return out


def hunt_sports2():
    ms = bot._scan_markets({"end_date_min": bot.iso(now() - dt.timedelta(days=1)),
                            "end_date_max": bot.iso(now() + dt.timedelta(days=5))})
    P = {}
    for m in ms:
        if not bot.is_sports(m) or m.get("closed") or str(m.get("sportsMarketType") or "") != "moneyline":
            continue
        mm = SLUG_RE.match(str(m.get("slug") or ""))
        if mm and mm.group(1) in LEAGUES and len(jlist(m.get("outcomes"))) == 2:
            P[(mm.group(1), mm.group(2).upper(), mm.group(3).upper(), mm.group(4) + mm.group(5) + mm.group(6))] = m
    print(f"poly moneyline games in supported leagues: {len(P)}; leagues {Counter(k[0] for k in P)}")
    rows, unmatched = [], Counter()
    descs = {}
    for lg, series in LEAGUES.items():
        K = kalshi_games(series)
        by_ev = defaultdict(list)
        for k in K:
            by_ev[(k["date"], k["codes"])].append(k)
        n_match = 0
        for (d, codes), ks in by_ev.items():
            hit = None
            for dd in (d, d - dt.timedelta(days=1), d + dt.timedelta(days=1)):
                for (l2, a, b, ds), m in P.items():
                    if l2 == lg and ds == dd.strftime("%Y%m%d") and codes in (a + b, b + a):
                        hit = (a, b, m)
                        break
                if hit:
                    break
            if not hit:
                unmatched[lg] += 1
                continue
            n_match += 1
            a, b, m = hit
            descs.setdefault(lg, (str(m.get("description") or "")[:900], str(ks[0]["m"].get("rules_secondary") or "")[:500]))
            outs = [str(o) for o in jlist(m.get("outcomes"))]
            toks = bot.market_tokens(m)
            pb = [bot.book(toks[0]), bot.book(toks[1])]
            if not pb[0] or not pb[1]:
                continue
            rate = bot.fee_rate(m)
            for k in ks:
                if k["team"] not in (a, b):
                    continue
                j = 0 if k["team"] == a else 1  # ASSUMPTION checked below by price: slug order == outcomes order
                kb = bot.kalshi_asks(k["m"].get("ticker"))
                if not kb:
                    continue
                k_mid = (bot.kpx(k["m"], "yes_ask") + bot.kpx(k["m"], "yes_bid")) / 2 if bot.kpx(k["m"], "yes_bid") is not None else None
                p_mid = (pb[j]["asks"][0][0] + pb[j]["bids"][0][0]) / 2 if pb[j]["asks"] and pb[j]["bids"] else None
                best = None
                for k_side, lv, pj in (("yes", kb[0], 1 - j), ("no", kb[1], j)):
                    pk, pp = bot.walk(lv, SHARES), bot.walk(pb[pj]["asks"], SHARES)
                    if pk is None or pp is None:
                        continue
                    cost = SHARES * (pk + pp) + bot.kalshi_fee(SHARES, pk) + bot.taker_fee(SHARES, pp, rate)
                    e = 1 - cost / SHARES
                    if best is None or e > best["edge"]:
                        best = {"edge": round(e, 4), "k_side": k_side, "pk": round(pk, 3), "pp": round(pp, 3),
                                "p_out": outs[pj]}
                if best:
                    best.update({"kalshi": k["m"].get("ticker"), "k_team": k["m"].get("yes_sub_title"), "poly": m.get("slug"),
                                 "poly_team_j": outs[j], "k_mid": k_mid and round(k_mid, 3), "p_mid": p_mid and round(p_mid, 3),
                                 "start": m.get("gameStartTime"), "fee": rate})
                    rows.append(best)
        print(f"{lg}: kalshi games {len(by_ev)}, matched {n_match}")
    print("unmatched kalshi games by league:", dict(unmatched))
    for lg, (pd, kd) in descs.items():
        print(f"--- {lg} rules\n POLY: {pd}\n KALSHI: {kd}")
    bad = [r for r in rows if r["k_mid"] is not None and r["p_mid"] is not None and abs(r["k_mid"] - r["p_mid"]) > 0.15]
    print(f"sports2 rows {len(rows)}; price-disagree >15c (likely wrong team order): {len(bad)}")
    good = [r for r in rows if r not in bad]
    good.sort(key=lambda r: -r["edge"])
    print(f"edge>=0: {sum(r['edge'] >= 0 for r in good)}, >=1c: {sum(r['edge'] >= 0.01 for r in good)}, "
          f">=2c: {sum(r['edge'] >= 0.02 for r in good)}; median edge "
          f"{sorted(r['edge'] for r in good)[len(good) // 2] if good else None}")
    for r in good[:25]:
        print(json.dumps(r))
    for r in bad[:5]:
        print("DISAGREE", json.dumps(r))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "hunt_sports2":
    hunt_sports2()
