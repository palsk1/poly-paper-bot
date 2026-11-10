#!/usr/bin/env python3
"""Census of every kind of Polymarket bet (2026-11-10, Jan's "check all types of bets" ask). Research only.

PAPER ONLY. Reads Gamma (live) and the backtest cache (history). Never trades, never writes state/.

    python3 census.py live       # probe `census_live`: every open event, sorted into families and formats
    python3 backtest.py btcensus # probe `btcensus` (ref=main): same families on finished markets, priced vs result
    python3 census.py selftest   # offline check of the sorter

What it answers per family (sports moneyline, spreads, totals, player props, esports, up/down crypto windows,
crypto strike ladders, weather buckets, mention markets, post counts, economics, elections, ...):
  - how many open events/markets, money traded in 24h and in total, money waiting in the books
  - how they settle (the website in the rules, or "UMA vote on news")
  - spreads, markets with no trade today, fees on/off, reward pools, and for multi-choice events how far the
    sum of the asks sits from $1
  - history (in-sample only, ends before the 2026-11-10 holdout): buy the cheap side or the dear side at
    6h / 1d / 3d / 7d before the end, 1 hour late, +2c + taker fee, held to the result. Grouped by event.
    Sports are included here for the first time (calib.py and ideas.py leave them out).
"""
import bisect
import collections
import datetime as dt
import math
import re
import statistics
import sys
import time

import bot

DAY = 86400
ENTRY_LAG = 3600

SPORT_SLUG = re.compile(r"^(nfl|nba|wnba|mlb|nhl|cfb|cbb|ncaab|ncaaf|epl|ucl|uel|lal|laliga|bun|bundesliga|sea|seriea|"
                        r"fl1|ligue1|mls|lib|bra|arg|mex|ere|por|tur|sau|jap|kor|chi|aus|uef|fif|wc|atp|wta|ufc|mma|"
                        r"box|pga|f1|nascar|ipl|cric|crint|t20|odi|test|afl|nrl|rug|kbo|npb|euro|copa|ahl|khl|shl|"
                        r"cs2|csgo|lol|dota2|dota|val|valorant|ow|r6|rl|cod|sc2|mlbb|hok|pubg|fifa|esp)-")
ESPORT_SLUG = re.compile(r"^(cs2|csgo|lol|dota2|dota|val|valorant|ow|r6|rl|cod|sc2|mlbb|hok|pubg)-")
ESPORT_WORDS = re.compile(r"counter-strike|\bcs2\b|league of legends|\blol:|dota|valorant|overwatch|rainbow six|"
                          r"rocket league|call of duty|starcraft|mobile legends|honor of kings|\besports?\b|\(bo[135]\)")
FUTURES = re.compile(r"win the 20\d\d|champion|\bmvp\b|super bowl|world series|stanley cup|nba finals|ballon d'or|"
                     r"make the playoffs|win the (afc|nfc|east|west|league|cup|premier league|title|division|conference|"
                     r"pennant|world cup|tournament|masters|open)|relegat|top scorer|golden boot|rookie of the year|"
                     r"cy young|heisman|win the (us|french|australian) open|wimbledon|grand slam|award")
PROP = re.compile(r"\b(points|rebounds|assists|yards|touchdowns?|receptions|strikeouts|home runs?|hits|saves|"
                  r"goals? scored|anytime|first goal|to score|shots|aces|kills|sacks|3-pointers|threes)\b")


def classify(q, slug="", ev_title="", outs=None, sports=False, smt=None, n_sib=1, tags=()):
    """(family, format) for one market. family = what it's about; format = the shape of the bet."""
    t = (q or "").lower()
    et = (ev_title or "").lower()
    s = (slug or "").lower()
    outs = [str(o).lower() for o in (outs or [])]
    smt = (smt or "").lower()
    both = t + " | " + et
    tg = {str(x).lower() for x in (tags or ())}
    # ---- format first (shape of the bet)
    if "up or down" in both or outs == ["up", "down"]:
        fmt = "up/down window"
    elif smt in ("totals", "total") or "o/u" in t or "over/under" in t or outs == ["over", "under"]:
        fmt = "over/under line"
    elif smt in ("spreads", "spread") or t.startswith("spread") or re.search(r"\([+-]\d+(\.5)?\)", t):
        fmt = "handicap line"
    elif re.search(r"\bbetween\b.*\band\b|\d+\s*-\s*\d+\s*(°|f\b|c\b|%|tweets|posts|k\b|m\b|bps)|or (higher|more|above)\b"
                   r"|or (lower|less|below)\b|\b\d+-\d+\b", t) and n_sib >= 3:
        fmt = "range buckets"
    elif re.search(r"\b(above|below|greater than|less than|at least|more than|fewer than|over|under|reach|hit|"
                   r"dip to|exceed)\b[^?]*\$?\d", t):
        fmt = "strike ladder" if n_sib >= 2 else "price/number line"
    elif re.search(r"\bby (january|february|march|april|may|june|july|august|september|october|november|december|"
                   r"end of|\d)|\bbefore (20\d\d|january|february|march|april|may|june|july|august|september|"
                   r"october|november|december)", t):
        fmt = "deadline (by date X)"
    elif n_sib >= 3:
        fmt = "pick one of many"
    elif len(outs) == 2 and outs != ["yes", "no"]:
        fmt = "head to head"
    else:
        fmt = "single yes/no"
    # ---- family (what it's about)
    is_sport = (sports or bool(smt) or bool(SPORT_SLUG.match(s)) or bool(ESPORT_WORDS.search(both))
                or bool(tg & {"sports", "esports"}))
    if "mentions" in tg and not is_sport:
        return "mentions (will X say Y)", fmt
    if tg & {"daily temperature", "weather"} and not is_sport and re.search(r"temperature|°|ºc", both):
        return "weather: temperature", fmt
    if ESPORT_SLUG.match(s) or ESPORT_WORDS.search(both) or "esports" in tg:
        if re.search(r"(game|map) \d", t):
            fam = "esports: single map/game"
        elif fmt in ("over/under line", "handicap line"):
            fam = "esports: lines (maps, kills)"
        else:
            fam = "esports: match winner"
    elif FUTURES.search(both) and (is_sport or re.search(r"nfl|nba|nhl|mlb|premier league|uefa|fifa|\bf1\b|ufc|super bowl|stanley cup|world series|"
                                                             r"ballon|heisman|cy young|wimbledon|grand slam|playoffs|relegat", both)):
        fam = "sports: season futures/awards"
    elif is_sport:
        if fmt == "handicap line":
            fam = "sports: spreads"
        elif fmt == "over/under line" and not PROP.search(t):
            fam = "sports: game totals"
        elif PROP.search(t) or smt.startswith("player") or "prop" in smt:
            fam = "sports: player props"
        elif "draw" in t:
            fam = "sports: draw (soccer)"
        else:
            fam = "sports: game winner"
    elif fmt == "up/down window":
        fam = ("up/down: crypto" if re.search(r"bitcoin|ethereum|solana|xrp|\bbtc\b|\beth\b|\bsol\b|doge|bnb|hype", both)
               else "up/down: stocks/other")
    else:
        tp = _topic(both)
        fam = {"crypto price": "crypto price levels", "weather": "weather", "mentions": "mentions (will X say Y)",
               "post counts": "post/tweet counts", "economics": "economics & Fed", "stocks": "stocks & companies",
               "elections": "elections & politics", "geopolitics": "war & world politics",
               "people/legal": "courts, arrests, people", "entertainment": "movies, music, TV, awards",
               "apps/tech": "tech, AI, apps", "other": "other"}.get(tp, tp)
        if fam == "weather" and re.search(r"temperature|°", both):
            fam = "weather: temperature"
        elif fam == "weather":
            fam = "weather: rain/snow/storms"
        if fam == "other" and re.search(r"trump|biden|vance|harris|musk|white house|congress|senate|president|"
                                        r"government|democrat|republican|tariff", both):
            fam = "elections & politics"
    return fam, fmt


_TOPIC = None


def _topic(text):
    global _TOPIC
    if _TOPIC is None:
        import calib
        _TOPIC = calib.topic
    return _TOPIC(text)


def f(x, d=0.0):
    try:
        v = float(x)
        return v if math.isfinite(v) else d
    except (TypeError, ValueError):
        return d


def money(x):
    if x >= 1e9:
        return f"${x / 1e9:.1f}B"
    if x >= 1e6:
        return f"${x / 1e6:.1f}M"
    if x >= 1e3:
        return f"${x / 1e3:.0f}k"
    return f"${x:.0f}"


def settle_source(e, ms):
    import sources
    text = " ".join([str(e.get("resolutionSource") or ""), str(e.get("description") or "")]
                    + [str(m.get("resolutionSource") or "") + " " + str(m.get("description") or "") for m in ms[:2]])
    ds = sources.domains(text)
    if ds:
        return collections.Counter(ds).most_common(1)[0][0]
    low = text.lower()
    if "chainlink" in low:
        return "chainlink (automatic)"
    if "official" in low or "consensus of credible reporting" in low or "credible report" in low:
        return "news / UMA vote"
    return "(none named) / UMA vote"


# ================================================================ live census

def live(pages=400):
    import sources
    t0 = time.time()
    evs = sources.poly_events(pages)
    now = bot.now()
    print(f"open events read: {len(evs)} ({time.time() - t0:.0f}s)")
    if evs:
        print("event keys:", sorted(evs[0].keys())[:80])
        ms0 = evs[0].get("markets") or [{}]
        print("market keys:", sorted(ms0[0].keys())[:120])
    fam = collections.defaultdict(lambda: {"ev": set(), "mk": 0, "v24": 0.0, "vol": 0.0, "liq": 0.0, "spr": [],
                                           "dead": 0, "fee": 0, "rew": 0, "soon": 0, "src": collections.Counter(),
                                           "fmt": collections.Counter(), "ex": [], "over": [], "tags": collections.Counter(),
                                           "rec": collections.Counter(), "mid": [], "end": []})
    fmts = collections.defaultdict(lambda: {"ev": set(), "mk": 0, "v24": 0.0, "vol": 0.0})
    tags_all = collections.Counter()
    tag_money = collections.Counter()
    n_mk = 0
    for e in evs:
        ms = [m for m in (e.get("markets") or []) if isinstance(m, dict) and not m.get("closed")]
        if not ms:
            continue
        tags = [str(t.get("label") or t.get("slug")) for t in (e.get("tags") or []) if isinstance(t, dict)]
        for tg in tags:
            tags_all[tg] += 1
            tag_money[tg] += f(e.get("volume24hr"))
        rec = ""
        ser = e.get("series") or []
        if isinstance(ser, list) and ser and isinstance(ser[0], dict):
            rec = str(ser[0].get("recurrence") or "")
        src = settle_source(e, ms)
        n_sib = len(ms)
        seen_fam = set()
        asks = []
        for m in ms:
            n_mk += 1
            outs = bot.jlist(m.get("outcomes"))
            fa, fo = classify(m.get("question"), m.get("slug") or e.get("slug"), e.get("title"), outs,
                              bot.is_sports(m), m.get("sportsMarketType"), n_sib, tags)
            a = fam[fa]
            a["ev"].add(e.get("id"))
            a["mk"] += 1
            a["v24"] += f(m.get("volume24hr"))
            a["vol"] += f(m.get("volumeNum") or m.get("volume"))
            a["liq"] += f(m.get("liquidityNum") or m.get("liquidity"))
            bb, ba = f(m.get("bestBid"), None), f(m.get("bestAsk"), None)
            if bb is not None and ba is not None and 0 < bb < ba <= 1:
                a["spr"].append(ba - bb)
                a["mid"].append((ba + bb) / 2)
            if f(m.get("volume24hr")) <= 0:
                a["dead"] += 1
            if bot.fee_rate(m) > 0 and m.get("feesEnabled") is not False and (m.get("feeSchedule") or m.get("feesEnabled")):
                a["fee"] += 1
            if m.get("clobRewards") or f(m.get("rewardsMinSize")) > 0:
                a["rew"] += 1
            end = bot.parse_iso(m.get("endDate") or m.get("endDateIso"))
            if end:
                d = (end - now).total_seconds() / DAY
                a["end"].append(d)
                if d < 3:
                    a["soon"] += 1
            a["fmt"][fo] += 1
            fm = fmts[fo]
            fm["ev"].add(e.get("id"))
            fm["mk"] += 1
            fm["v24"] += f(m.get("volume24hr"))
            fm["vol"] += f(m.get("volumeNum") or m.get("volume"))
            asks.append(ba)
            if fa not in seen_fam:
                seen_fam.add(fa)
                a["src"][src] += 1
                for tg in tags[:4]:
                    a["tags"][tg] += 1
                if rec:
                    a["rec"][rec] += 1
                if len(a["ex"]) < 4 and f(e.get("volume24hr")) > 0:
                    a["ex"].append(str(m.get("question") or e.get("title"))[:70])
        if (e.get("negRisk") or e.get("enableNegRisk")) and n_sib >= 3 and all(x is not None and x > 0 for x in asks):
            fa0 = classify(ms[0].get("question"), ms[0].get("slug"), e.get("title"), bot.jlist(ms[0].get("outcomes")),
                           bot.is_sports(ms[0]), ms[0].get("sportsMarketType"), n_sib, tags)[0]
            # only events where every choice has a real two-sided book (empty books ask 99c and mean nothing)
            sprs = [f(m.get("bestAsk")) - f(m.get("bestBid")) for m in ms]
            if max(sprs) <= 0.05:
                fam[fa0]["over"].append(sum(asks) - 1.0)
    tot24 = sum(a["v24"] for a in fam.values()) or 1
    totliq = sum(a["liq"] for a in fam.values()) or 1
    print(f"\nopen markets: {n_mk}, money traded in the last 24h: {money(tot24)}, money resting in books: {money(totliq)}")
    print("\n== FAMILIES (sorted by money traded in 24h)")
    print("family | events | markets | traded 24h | traded total | in books | median spread | no trade today | "
          "fees on | reward pool | ends <3d | median days left | multi-choice: asks sum minus $1 (median) | top formats | "
          "settles on | tags | repeats | examples")
    for k, a in sorted(fam.items(), key=lambda kv: -kv[1]["v24"]):
        spr = f"{100 * statistics.median(a['spr']):.1f}c" if a["spr"] else "-"
        ov = f"{100 * statistics.median(a['over']):+.1f}c ({len(a['over'])} ev)" if a["over"] else "-"
        dl = f"{statistics.median(a['end']):.1f}" if a["end"] else "-"
        topf = ", ".join(f"{x} {n}" for x, n in a["fmt"].most_common(3))
        src = ", ".join(f"{x} {n}" for x, n in a["src"].most_common(3))
        tg = ", ".join(x for x, _ in a["tags"].most_common(4))
        rc = ", ".join(f"{x} {n}" for x, n in a["rec"].most_common(2))
        print(f"{k} | {len(a['ev'])} | {a['mk']} | {money(a['v24'])} | {money(a['vol'])} | {money(a['liq'])} | {spr} | "
              f"{a['dead']} | {a['fee']} | {a['rew']} | {a['soon']} | {dl} | {ov} | {topf} | {src} | {tg} | {rc} | "
              f"{' / '.join(a['ex'])}")
    print("\n== FORMATS (shape of the bet)")
    print("format | events | markets | traded 24h | traded total")
    for k, a in sorted(fmts.items(), key=lambda kv: -kv[1]["v24"]):
        print(f"{k} | {len(a['ev'])} | {a['mk']} | {money(a['v24'])} | {money(a['vol'])}")
    print("\n== Polymarket's own tags, top 60 by events (24h money of events carrying the tag)")
    for tg, n in tags_all.most_common(60):
        print(f"{tg} | {n} | {money(tag_money[tg])}")
    print(f"\ndone in {time.time() - t0:.0f}s")


# ================================================================ history (in-sample)

HZ = (("6h", 0.25), ("1d", 1), ("3d", 3), ("7d", 7))
BANDS = (("long shot 2-15c", 0.02, 0.15), ("underdog 15-50c", 0.15, 0.50), ("favorite 50-85c", 0.50, 0.85),
         ("heavy favorite 85-98c", 0.85, 0.98))


def history():
    import backtest as bt
    import calib
    import ideas
    markets, hist, complete = ideas.load_full()
    ms = ideas.in_sample(markets)
    by_ev = collections.defaultdict(list)
    for mk in ms.values():
        by_ev[mk.get("ev") or mk["id"]].append(mk)
    print(f"in-sample finished markets: {len(ms):,} in {len(by_ev):,} events; complete events known: "
          f"{'none' if complete is None else f'{len(complete):,}'}")
    fam_n = collections.defaultdict(lambda: {"mk": 0, "ev": set(), "vol": 0.0, "fmt": collections.Counter(),
                                             "inc": 0})
    rows = []
    for ev, sibs in by_ev.items():
        n_sib = len(sibs)
        for mk in sibs:
            fa, fo = classify(mk["q"], mk.get("slug"), "", mk.get("outs"), mk.get("sports"), None, n_sib)
            a = fam_n[fa]
            a["mk"] += 1
            a["ev"].add(ev)
            a["vol"] += mk.get("vol") or 0
            a["fmt"][fo] += 1
            # multi-choice non-sports events must be complete (else the losing choices are missing, see TOOLS.md)
            whole = complete is None or ev in complete or (n_sib <= 2)
            if not whole:
                a["inc"] += 1
                continue
            y = calib.outcome0(mk)
            h = hist.get(mk["id"])
            if y is None or not h or not h[0] or not mk.get("end"):
                continue
            T, P = h
            for hn, hd in HZ:
                t = mk["end"] - hd * DAY
                if t < T[0] + (DAY if hd >= 1 else 6 * 3600) or (mk.get("start") and t < mk["start"]):
                    continue
                if mk.get("closed_t") and t + ENTRY_LAG >= mk["closed_t"]:
                    continue
                i = bisect.bisect_right(T, t) - 1
                if i < 0 or t - T[i] > (3 * DAY if hd >= 1 else 6 * 3600):
                    continue
                k = bisect.bisect_right(T, t + ENTRY_LAG) - 1
                pe = P[k]
                if not 0.02 <= pe <= 0.98:
                    continue
                rows.append({"fam": fa, "fmt": fo, "ev": ev, "h": hn, "p": pe, "y": y, "fee": mk.get("fee", 0),
                             "t": t, "q": mk["q"]})
    print("\n== HOW MANY (finished markets, Mar-Nov 2026, main cache = final volume over $20k + whole-event fill-ins)")
    print("family | markets | events | money traded | skipped (incomplete event) | top formats")
    for k, a in sorted(fam_n.items(), key=lambda kv: -kv[1]["vol"]):
        print(f"{k} | {a['mk']:,} | {len(a['ev']):,} | {money(a['vol'])} | {a['inc']:,} | "
              f"{', '.join(f'{x} {n}' for x, n in a['fmt'].most_common(3))}")
    print(f"\nprice snapshots: {len(rows):,}")
    flags = []
    for group in ("fam", "fmt"):
        keys = sorted({r[group] for r in rows})
        print(f"\n== PRICED vs RESULT by {'family' if group == 'fam' else 'format'}: buy at the price 1h after the "
              f"snapshot, +2c + taker fee, held to the end. Profit per $100, 90% band, events, halves")
        print("slice | when | band | events | bets (won) | avg price | win rate | +1c | +2c | 90% band +2c | "
              "+5c | 1st/2nd half +2c")
        for key in keys:
            rk = [r for r in rows if r[group] == key]
            for hn, _ in HZ:
                rh = [r for r in rk if r["h"] == hn]
                if len(rh) < 30:
                    continue
                for bn, lo, hi in BANDS:
                    tr = []
                    for r in rh:
                        for q, pay in ((r["p"], r["y"]), (1 - r["p"], 1 - r["y"])):
                            if lo <= q < hi:
                                tr.append((r, q, pay))
                    s1, s2, s5 = (calib.score(tr, x) for x in (0.01, 0.02, 0.05))
                    if not s2 or s2["events"] < 20:
                        continue
                    a, b = calib.halves(tr, 0.02)
                    wr = s2["wins"] / s2["bets"]
                    flag = s2["lo"] > 0 and s2["events"] >= 30 and (a or 0) > 0 and (b or 0) > 0
                    mark = " <-" if flag else ""
                    print(f"{key} | {hn} | {bn} | {s2['events']} | {s2['bets']} ({s2['wins']}) | "
                          f"{100 * s2['avgq']:.0f}c | {100 * wr:.0f}c | {calib.m(s1['per100'])} | "
                          f"{calib.m(s2['per100'])} | {calib.m(s2['lo'])} to {calib.m(s2['hi'])} | "
                          f"{calib.m(s5['per100'])} | {calib.m(a)} / {calib.m(b)}{mark}")
                    if flag:
                        flags.append((key, hn, bn, s2, a, b, tr))
    print(f"\n== FLAGGED (band above $0 at +2c, 30+ events, both halves ahead): {len(flags)}. Many slices were "
          f"tested, so expect a few false alarms.")
    import random
    rng = random.Random(7)
    for key, hn, bn, s2, a, b, tr in flags:
        print(f"\n-- {key} | {hn} | {bn}: {calib.m(s2['per100'])} per $100, band {calib.m(s2['lo'])} to "
              f"{calib.m(s2['hi'])}, {s2['events']} events, halves {calib.m(a)} / {calib.m(b)}")
        for r, q, pay in rng.sample(tr, min(6, len(tr))):
            print(f"     {'WON ' if pay >= 0.5 else 'lost'} {100 * q:.0f}c  {r['q'][:90]}")


# ================================================================ drill: daily stock/commodity up/down (flagged 2026-11-10)

def updown_hist():
    """Every finished daily (not 5m/15m/hourly) stock/commodity Up-or-Down market: price 1 day before the end
    (the previous close, before the window opens) and later, the result, how many price points, the fee."""
    import calib
    import ideas
    markets, hist, _ = ideas.load_full()
    ms = ideas.in_sample(markets)
    rows = []
    for mk in ms.values():
        fa, fo = classify(mk["q"], mk.get("slug"), "", mk.get("outs"), mk.get("sports"), None, 1)
        if fa != "up/down: stocks/other" or re.search(r"\d{1,2}(:\d\d)?\s*(am|pm)", mk["q"].lower()):
            continue
        y = calib.outcome0(mk)
        h = hist.get(mk["id"])
        if y is None or not h or not h[0] or not mk.get("end"):
            continue
        T, P = h

        def px(hours):
            t = mk["end"] - hours * 3600
            i = bisect.bisect_right(T, t) - 1
            return (P[i], t - T[i]) if i >= 0 else (None, None)
        p24, age24 = px(24 - 1)
        p12, _ = px(12)
        p6, _ = px(6)
        n_before = sum(1 for t in T if t < mk["end"] - 23 * 3600)
        rows.append((mk, y, p24, age24, p12, p6, n_before))
    print(f"daily stock/commodity up/down markets with history: {len(rows)}")
    by_asset = collections.defaultdict(list)
    for r in rows:
        a = re.sub(r" (opens )?up or down.*", "", r[0]["q"].lower())
        by_asset[a].append(r)
    print("asset | markets | median price 23h before end | share priced under 45c or over 55c then | fee")
    for a, rs in sorted(by_asset.items(), key=lambda kv: -len(kv[1])):
        ps = [r[2] for r in rs if r[2] is not None]
        off = sum(1 for x in ps if x < 0.45 or x > 0.55)
        if not ps:
            continue
        print(f"{a} | {len(rs)} | {100 * statistics.median(ps):.0f}c | {off}/{len(ps)} | {rs[0][0].get('fee')}")
    print("\nbuy the side under 45c, 23h before the end (fill = that price + 1c/2c/5c + fee), held to the result")
    for slip in (0.01, 0.02, 0.05):
        pnl = cost = 0.0
        n = w = 0
        for mk, y, p24, age, *_ in rows:
            if p24 is None:
                continue
            for q, pay in ((p24, y), (1 - p24, 1 - y)):
                if 0.15 <= q < 0.45:
                    c = min(0.99, q + slip)
                    fe = bot.taker_fee(1, c, mk.get("fee", 0))
                    pnl += pay - c - fe
                    cost += c + fe
                    n += 1
                    w += pay >= 0.5
        if cost:
            print(f"  +{100 * slip:.0f}c: {n} bets, won {w}, {'+' if pnl >= 0 else '-'}${abs(100 * pnl / cost):.0f} per $100")
    print("\nsample: question | price 23h / 12h / 6h before end (outcome 0) | age of that price | points before | result")
    import random
    for mk, y, p24, age, p12, p6, nb in random.Random(5).sample(rows, min(40, len(rows))):
        fmt = lambda x: "-" if x is None else f"{100 * x:.0f}c"
        print(f"  {mk['q'][:60]} | {fmt(p24)} / {fmt(p12)} / {fmt(p6)} | {(age or 0) / 3600:.0f}h | {nb} | "
              f"{mk['outs'][0] if y == 1 else mk['outs'][1]}")


def updown_tape():
    """Real-fill check for the daily stock/commodity up/down lead: the same signal (side under 45c on the price
    history 23h before the end), but filled at the first real BUY of that side on the trade tape in the next 3 hours.
    Results grouped by trading day, since SPX/SPY/'opens' markets on one day are really one bet."""
    import calib
    import ideas
    import informed
    markets, hist, _ = ideas.load_full()
    ms = ideas.in_sample(markets)
    sig = []
    for mk in ms.values():
        fa, _ = classify(mk["q"], mk.get("slug"), "", mk.get("outs"), mk.get("sports"), None, 1)
        if fa != "up/down: stocks/other" or re.search(r"\d{1,2}(:\d\d)?\s*(am|pm)", mk["q"].lower()):
            continue
        y = calib.outcome0(mk)
        h = hist.get(mk["id"])
        if y is None or not h or not h[0] or not mk.get("end"):
            continue
        T, P = h
        t = mk["end"] - 23 * 3600
        i = bisect.bisect_right(T, t) - 1
        if i < 0 or t - T[i] > 6 * 3600:
            continue
        for oi, q in ((0, P[i]), (1, 1 - P[i])):
            if 0.15 <= q < 0.45:
                sig.append((mk, oi, q, t, y if oi == 0 else 1 - y))
    print(f"signals: {len(sig)}")
    cids = informed.cids_for([s[0]["id"] for s in sig])
    print(f"condition ids found: {len(cids)}")
    rows = []
    from concurrent.futures import ThreadPoolExecutor

    def one(sg):
        mk, oi, q, t, pay = sg
        cid = cids.get(mk["id"])
        if not cid:
            return None
        tr, _ = informed.tape(cid, 40)
        buys = []
        for r in tr:
            ts = bot.fnum(bot.pick(r, "timestamp", "time"))
            ts = ts / 1000 if ts > 1e11 else ts
            o = r.get("outcome_index", r.get("outcomeIndex"))
            if o not in (0, 1):
                tok = str(bot.pick(r, "token_id", "asset", default=""))
                o = 0 if tok == mk["toks"][0] else 1 if tok == mk["toks"][1] else None
            if o == oi and str(r.get("side") or "").upper().startswith("B") and t <= ts <= t + 3 * 3600:
                buys.append((ts, bot.fnum(r.get("price")), bot.fnum(r.get("size"))))
        buys.sort()
        return (mk, oi, q, t, pay, buys, len(tr))
    with ThreadPoolExecutor(8) as ex:
        for x in ex.map(one, sig):
            if x:
                rows.append(x)
    filled = [r for r in rows if r[5]]
    print(f"tapes read: {len(rows)}, with a real buy of that side within 3h: {len(filled)}")
    gap = [r[5][0][1] - r[2] for r in filled]
    if gap:
        print(f"real first buy minus history price: median {100 * statistics.median(gap):+.1f}c, "
              f"mean {100 * statistics.mean(gap):+.1f}c")
    for extra in (0.0, 0.01, 0.02):
        by_day = collections.defaultdict(lambda: [0.0, 0.0])
        n = w = 0
        for mk, oi, q, t, pay, buys, _ in filled:
            c = min(0.99, buys[0][1] + extra)
            fe = bot.taker_fee(1, c, mk.get("fee", 0))
            d = bot.iso(dt.datetime.fromtimestamp(mk["end"], dt.timezone.utc))[:10]
            by_day[d][0] += pay - c - fe
            by_day[d][1] += c + fe
            n += 1
            w += pay >= 0.5
        P_ = sum(v[0] for v in by_day.values())
        S_ = sum(v[1] for v in by_day.values())
        if S_ <= 0:
            continue
        rate = P_ / S_
        k = len(by_day)
        var = sum((v[0] - rate * v[1]) ** 2 for v in by_day.values()) / (S_ * S_) * (k / max(1, k - 1))
        se = math.sqrt(var)
        days = sorted(by_day)
        mid = days[len(days) // 2]
        h1 = [v for d, v in by_day.items() if d < mid]
        h2 = [v for d, v in by_day.items() if d >= mid]
        r1 = 100 * sum(v[0] for v in h1) / max(1e-9, sum(v[1] for v in h1))
        r2 = 100 * sum(v[0] for v in h2) / max(1e-9, sum(v[1] for v in h2))
        print(f"  real first buy +{100 * extra:.0f}c + fee: {n} bets on {k} trading days, won {w}, "
              f"{100 * rate:+.1f} per $100, 90% band {100 * (rate - 1.645 * se):+.1f} to {100 * (rate + 1.645 * se):+.1f}, "
              f"halves {r1:+.1f} / {r2:+.1f}")
    print("\nsample: question | side | history price | first real buy (time after signal, shares) | result")
    import random
    for mk, oi, q, t, pay, buys, ntr in random.Random(3).sample(filled, min(30, len(filled))):
        b = buys[0]
        print(f"  {mk['q'][:55]} | {mk['outs'][oi]} | {100 * q:.0f}c | {100 * b[1]:.0f}c ({(b[0] - t) / 60:.0f} min, "
              f"{b[2]:.0f} sh) | {'WON' if pay >= 0.5 else 'lost'}")


def updown_live():
    """Open daily stock/commodity up/down markets right now: real best bid/ask, depth on the ask, hours left."""
    import sources
    evs = sources.poly_events(400)
    now = bot.now()
    out = []
    for e in evs:
        tags = {str(t.get("label") or "").lower() for t in (e.get("tags") or []) if isinstance(t, dict)}
        for m in e.get("markets") or []:
            if not isinstance(m, dict) or m.get("closed"):
                continue
            fa, _ = classify(m.get("question"), m.get("slug"), e.get("title"), bot.jlist(m.get("outcomes")),
                             bot.is_sports(m), m.get("sportsMarketType"), 1, tags)
            q = str(m.get("question") or "")
            if fa != "up/down: stocks/other" or re.search(r"\d{1,2}(:\d\d)?\s*(am|pm)", q.lower()):
                continue
            end = bot.parse_iso(m.get("endDate"))
            out.append(((end - now).total_seconds() / 3600 if end else None, q, m))
    print(f"open daily stock/commodity up/down markets: {len(out)}")
    for hrs, q, m in sorted(out, key=lambda x: x[0] or 1e9)[:60]:
        toks = bot.market_tokens(m)
        book = ""
        try:
            b = bot.http_json(f"{bot.CLOB}/book", {"token_id": toks[0]}) if toks else {}
            asks = sorted(((f(a.get("price")), f(a.get("size"))) for a in b.get("asks") or []))[:3]
            bids = sorted(((f(a.get("price")), f(a.get("size"))) for a in b.get("bids") or []), reverse=True)[:3]
            book = f"bids {bids} asks {asks}"
        except Exception as ex:
            book = f"book failed {ex}"
        print(f"  {hrs:5.1f}h | {q[:55]} | bid {m.get('bestBid')} ask {m.get('bestAsk')} last {m.get('lastTradePrice')} "
              f"| 24h ${f(m.get('volume24hr')):.0f} | fee {bot.fee_rate(m)} | {book}")


# ================================================================ selftest

def selftest():
    cases = [
        ("Bitcoin Up or Down - November 10, 3:15PM-3:30PM ET", "btc-updown-15m-1", ["Up", "Down"], False, None, 1,
         "up/down: crypto", "up/down window"),
        ("Spread: Bills (-3.5)", "nfl-buf-mia-2026-11-09-spread", ["Bills", "Dolphins"], True, "spreads", 1,
         "sports: spreads", "handicap line"),
        ("Bills vs. Dolphins: O/U 47.5", "nfl-buf-mia-2026-11-09-total", ["Over", "Under"], True, "totals", 1,
         "sports: game totals", "over/under line"),
        ("Counter-Strike: NAVI vs FaZe - Map 1 Winner", "cs2-navi-faze-1", ["NAVI", "FaZe"], False, None, 1,
         "esports: single map/game", "head to head"),
        ("Will the highest temperature in London be between 12-13°C on November 11?", "london-temp", ["Yes", "No"],
         False, None, 9, "weather: temperature", "range buckets"),
        ("Will Trump say \"crypto\" during his speech?", "trump-say", ["Yes", "No"], False, None, 12,
         "mentions (will X say Y)", "pick one of many"),
        ("Will Bitcoin reach $150,000 by December 31?", "btc-150k", ["Yes", "No"], False, None, 8,
         "crypto price levels", "strike ladder"),
        ("Will the Chiefs win Super Bowl 2027?", "super-bowl-2027-chiefs", ["Yes", "No"], False, None, 32,
         "sports: season futures/awards", "pick one of many"),
        ("Will Elon Musk post 200-219 tweets from November 7 to November 14?", "elon-tweets", ["Yes", "No"], False,
         None, 20, "post/tweet counts", "range buckets"),
    ]
    bad = 0
    for q, slug, outs, sp, smt, n, want_f, want_fmt in cases:
        got = classify(q, slug, "", outs, sp, smt, n)
        ok = got == (want_f, want_fmt)
        bad += not ok
        print("ok " if ok else "BAD", got, "<-", q)
    print("selftest", "passed" if not bad else f"FAILED ({bad})")
    return bad == 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "live"
    {"live": live, "history": history, "selftest": selftest, "updown": updown_live, "updownhist": updown_hist, "updowntape": updown_tape}[cmd]()
