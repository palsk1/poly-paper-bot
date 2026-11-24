#!/usr/bin/env python3
"""Bets still cheap after the answer is known (24 Nov 2026, research only, paper only). backtest/known.md.

Question: in which markets is the real-world answer already public (game over, price fixed at the reference
minute, stock market closed) while the winning side can still be BOUGHT under 97-99c, and how much of that is
there at prices people really paid?

  python3 known.py crypto            offline: Polymarket BTC/ETH price markets (bt_cache/opt) vs Binance 1-minute
  python3 known.py stocks            offline: Polymarket stock close markets (bt_cache/stk) vs Nasdaq daily closes
  python3 known.py sfetch [n]        probe kn_sfetch: Polymarket game markets, every trade from kickoff to payout +
                                     Gamma event fields (finishedTimestamp, score) -> bt_cache/kn/
  python3 known.py sports            offline: the sports test on bt_cache/kn
  python3 known.py report [log]      everything above + exam scorecards -> backtest/known.md
"""
import collections
import gzip
import json
import os
import random
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot

CACHE = os.path.join(bt.CACHE, "kn")
TRIES = 0          # versions looked at, counted as they are added (report)
HOLD = 1794268800   # 2026-11-10 00:00 UTC, the holdout start (btcheck.HOLDOUT_FROM)


def rj(p, d=None):
    try:
        with gzip.open(p, "rt") as f:
            return json.load(f)
    except Exception:
        return d


def wj(p, x):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with gzip.open(tmp, "wt") as f:
        json.dump(x, f, separators=(",", ":"))
    os.replace(tmp, p)


def usd(x):
    return ("-" if x < 0 else "+") + f"${abs(x):,.2f}"


# ================================================================ fills
def fee(px, sh, rate):
    return bot.taker_fee(sh, px, rate)


def buy(buckets, t0, yes_side, extra=0.01, window=3600, stake=25.0, rate=0.0, cap=0.995):
    """Buy the known winner at the WORST price traded in the hour after t0 (5-min or 1-min buckets in YES terms:
    [t, first, last, low, high, dollars, n]) + extra + fee. None when nothing traded. Same idea as earn.buy."""
    w = [b for b in buckets if t0 <= b[0] < t0 + window]
    if not w:
        return None
    px = max((b[4] if yes_side else 1 - b[3]) for b in w) + extra
    if px >= cap:
        return {"px": px, "skip": True}
    sh = stake / px
    return {"px": px, "sh": sh, "cost": sh * px + fee(px, sh, rate), "dollars": sum(b[5] for b in w)}


# ================================================================ crypto (offline)
def crypto_rows():
    """Every BTC/ETH price market whose answer Binance's 1-minute candles fix before payout: the reference minute
    for 'above/below/between on <day>' markets, the first touch for 'reach/dip' markets."""
    import optfair as o
    ms, *_ = o.load()
    tp = o.load_tapes()
    s1 = o.load_spot1m()

    def at(c, t):
        b = s1[c]
        i = int((t - b["t0"]) // 60)
        return b["c"][i] if 0 <= i < len(b["c"]) else None

    def touch(m):
        b = s1[m["coin"]]
        i0, i1 = max(0, int((m["start"] - b["t0"]) // 60)), min(len(b["c"]), int((m["end"] - b["t0"]) // 60))
        for i in range(i0, i1):
            h, l = b["h"][i], b["l"][i]
            if h is None:
                continue
            if (m["kind"] == "up" and h >= m["k"]) or (m["kind"] == "down" and l <= m["k"]):
                return b["t0"] + i * 60 + 60
        return None

    out = []
    for mid, m in ms.items():
        t = tp.get(mid)
        if not t:
            continue
        yes = m["final"][0] == 1.0
        if m["kind"] in ("up", "down"):
            tk = touch(m)
            if tk is None:
                guess, tk = False, m["end"] + 60
            else:
                guess = True
        else:
            c = at(m["coin"], m["end"])
            if c is None:
                continue
            k = m["k"]
            guess = c > k if m["kind"] == "above" else c < k if m["kind"] == "below" else k[0] <= c < k[1]
            tk = m["end"] + 60
            if m["kind"] == "between":
                near = min(abs(c - k[0]), abs(c - k[1])) / c
            else:
                near = abs(c - k) / c
        out.append({"id": mid, "q": m["q"], "kind": m["kind"], "known": tk, "guess": guess, "yes": yes, "b": t["b"],
                    "end": m["end"], "fee": m.get("fee") or 0.0, "ev": m.get("ev") or mid,
                    "near": None if m["kind"] in ("up", "down") else near})
    return out


def scan(rows, delay=300, lines=(0.97, 0.99)):
    """How often is the known winner still cheap after `delay` seconds, and how many dollars traded there."""
    c = collections.Counter()
    dol = collections.Counter()
    ex = []
    for r in rows:
        c["known"] += 1
        if r["guess"] != r["yes"]:
            c["source disagreed with the payout"] += 1
        b = [x for x in r["b"] if x[0] >= r["known"] + delay - 1]
        if not b:
            continue
        c["traded after"] += 1
        g = r["guess"]
        for ln in lines:
            ch = [x for x in b if (x[3] if g else 1 - x[4]) <= ln]   # someone traded the known winner at or under the line
            if ch:
                c[f"winner traded at {ln * 100:.0f}c or less"] += 1
                dol[ln] += sum(x[5] for x in ch)
                if ln == lines[0]:
                    ex.append((sum(x[5] for x in ch), r))
    return c, dol, sorted(ex, key=lambda x: -x[0])


def bets_after(rows, delay=300, extra=0.01, hi=0.97, stake=25.0):
    """The bot: `delay` after the answer is fixed, buy the side the outside source says won, if the last trade before
    that is at `hi` or less; pay the worst trade of the next hour + extra + fee; paid by the REAL result."""
    out = []
    for r in rows:
        b = r["b"]
        g = r["guess"]
        t0 = r["known"] + delay
        seen = [x for x in b if x[0] < t0 and x[0] >= r["known"] - 300]
        nxt = [x for x in b if x[0] >= t0]
        if not nxt:
            continue
        ref = (seen[-1][2] if seen else nxt[0][1])
        ref = ref if g else 1 - ref
        if ref > hi:
            continue
        f = buy(b, nxt[0][0], g, extra=extra, stake=stake, rate=r["fee"])
        if not f or f.get("skip"):
            continue
        win = r["yes"] == g
        out.append({"ev": r["ev"], "t": nxt[0][0], "cost": f["cost"], "pay": f["sh"] if win else 0.0, "px": f["px"],
                    "name": r["q"], "win": win})
    return out


def stock_rows():
    """Polymarket stock close markets (bt_cache/stk) with the answer from Nasdaq's official daily close, known a couple
    of minutes after 4 PM New York. All markets with a daily close, also the ones the close does NOT reproduce."""
    import stocks
    ms = bt.rjson(os.path.join(stocks.CACHE, "markets.json.gz"), {}) or {}
    D = bt.rjson(os.path.join(stocks.CACHE, "daily.json.gz"), {}) or {}
    _, tp, _, _, _ = stocks.load()
    out = []
    for mid, m in ms.items():
        t = tp.get(mid)
        d = D.get(m["tk"], {}).get(stocks._day(m["end"]))
        if not t or not d:
            continue
        guess = (m["lo"] is None or d[3] > m["lo"]) and (m["hi"] is None or d[3] < m["hi"])
        line = [x for x in (m["lo"], m["hi"]) if x]
        out.append({"id": mid, "q": m.get("q", ""), "kind": m.get("kind"), "known": m["end"] + 120, "guess": guess,
                    "yes": m["final"][0] == 1.0, "b": t["b"], "end": m["end"], "fee": m.get("fee") or 0.0,
                    "ev": m.get("ev") or mid, "near": min(abs(d[3] - x) / d[3] for x in line) if line else 1.0})
    return out


# ================================================================ sports fetch (probe)
LEAGUE_CAP = 160


def sfetch(n=4000):
    """Sample finished Polymarket game markets (moneyline + spreads + totals) from bt_cache/sports, at most
    LEAGUE_CAP per league; for each, every trade from kickoff to payout in 1-minute buckets (YES terms), and the
    Gamma event's own fields (finishedTimestamp, score, period, closedTime)."""
    import informed
    sp = (rj(os.path.join(bt.CACHE, "sports", "markets.json.gz"), {}) or {}).get("markets") or {}
    print(f"sports cache: {len(sp):,} markets", flush=True)
    os.makedirs(CACHE, exist_ok=True)
    MP = os.path.join(CACHE, "markets.json.gz")
    TP = os.path.join(CACHE, "tapes.json.gz")
    EP = os.path.join(CACHE, "events.json.gz")
    have_m, have_t, have_e = rj(MP, {}) or {}, rj(TP, {}) or {}, rj(EP, {}) or {}
    pool = collections.defaultdict(list)
    for m in sp.values():
        if m.get("smt") not in ("moneyline", "spreads", "totals", "child_moneyline"):
            continue
        if not (m.get("gst") and m.get("closed_t") and m.get("final") and max(m["final"]) == 1.0 and m.get("cid")):
            continue
        if (m.get("vol") or 0) < 5000 or m["closed_t"] >= HOLD or m["closed_t"] - m["gst"] > 3 * 86400:
            continue
        pool[m["slug"].split("-")[0]].append(m)
    rng = random.Random(7)
    pick = []
    for lg, v in pool.items():
        rng.shuffle(v)
        pick += v[:LEAGUE_CAP]
    rng.shuffle(pick)
    pick = [m for m in pick if m["id"] not in have_t][:n]
    print(f"{len(pool)} leagues, {len(pick)} markets to fetch", flush=True)

    def one(m):
        rows, cur = [], None
        lo = m["gst"] - 600
        for _ in range(40):
            p = {"condition_id": m["cid"], "limit": 500}
            if cur:
                p["cursor"] = cur
            try:
                r, cur, _ = informed.trades_page(p)
            except Exception:
                return m, None
            rows += r
            ts = [bot.fnum(bot.pick(x, "timestamp", "time")) for x in r]
            ts = [t / 1000 if t > 1e11 else t for t in ts if t]
            if not cur or not r or (ts and min(ts) < lo):
                break
        B = {}
        for x in rows:
            t = bot.fnum(bot.pick(x, "timestamp", "time"))
            t = t / 1000 if t > 1e11 else t
            px, sh = bot.fnum(x.get("price")), bot.fnum(x.get("size"))
            oi = x.get("outcome_index", x.get("outcomeIndex"))
            if oi not in (0, 1):
                tok = str(bot.pick(x, "token_id", "asset", default=""))
                oi = 0 if tok == m["toks"][0] else 1 if tok == m["toks"][1] else None
            if not t or t < lo or oi is None or not 0 < px < 1 or sh <= 0:
                continue
            p = round(px if oi == 0 else 1 - px, 4)
            k = int(t) // 60 * 60
            b = B.get(k)
            if b is None:
                B[k] = [k, p, p, p, p, px * sh, 1, int(t), int(t)]
            else:
                if t < b[7]:
                    b[1], b[7] = p, int(t)
                if t >= b[8]:
                    b[2], b[8] = p, int(t)
                b[3], b[4] = min(b[3], p), max(b[4], p)
                b[5] += px * sh
                b[6] += 1
        out = [[b[0], b[1], b[2], b[3], b[4], round(b[5], 1), b[6]] for b in sorted(B.values())]
        return m, {"b": out, "n": len(rows), "cut": bool(cur)}

    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(8) as ex:
        for m, res in ex.map(one, pick):
            if res is None:
                continue
            have_t[m["id"]] = res
            have_m[m["id"]] = {k: m.get(k) for k in ("id", "q", "slug", "ev", "ev_slug", "smt", "gst", "closed_t", "end", "final",
                                                    "fee", "vol", "uma", "line", "git", "outs")}
            done += 1
            if done % 250 == 0:
                print(f"  {done} tapes, {time.time() - t0:.0f} s", flush=True)
                wj(MP, have_m), wj(TP, have_t)
            if time.time() - t0 > 200 * 60:
                break
    wj(MP, have_m), wj(TP, have_t)
    # Gamma event fields
    slugs = sorted({m["ev_slug"] for m in have_m.values() if m.get("ev_slug") and m["ev_slug"] not in have_e})
    print(f"{len(slugs)} events to read from Gamma", flush=True)
    keep = ("finishedTimestamp", "ended", "score", "period", "elapsed", "live", "closedTime", "endDate", "startTime",
            "eventDate", "gameStatus", "umaResolutionStatus", "resolvedBy", "automaticallyResolved")

    def ev(s):
        try:
            r = bot.http_json(f"{bot.GAMMA}/events", {"slug": s})
            r = r[0] if isinstance(r, list) and r else r if isinstance(r, dict) else None
        except Exception:
            return s, None
        if not r:
            return s, None
        d = {k: r.get(k) for k in keep if r.get(k) is not None}
        d["keys"] = sorted(r.keys())[:80] if len(have_e) < 3 else None
        mk = {}
        for x in r.get("markets") or []:
            mk[str(x.get("id"))] = {k: x.get(k) for k in ("closedTime", "umaResolutionStatuses", "umaEndDate", "automaticallyResolved",
                                                        "resolvedBy", "gameStartTime", "endDate") if x.get(k) is not None}
        d["m"] = mk
        return s, d

    with ThreadPoolExecutor(8) as ex:
        for i, (s, d) in enumerate(ex.map(ev, slugs)):
            if d is not None:
                have_e[s] = d
                if len(have_e) <= 2:
                    print("event sample", json.dumps(d)[:2500], flush=True)
    wj(EP, have_e)
    print(f"done: {len(have_t)} tapes, {len(have_e)} events, {time.time() - t0:.0f} s", flush=True)


# ================================================================ live snapshot (probe kn_live)
def kind_of(m):
    q = str(m.get("question") or "").lower()
    if bot.is_sports(m):
        return "sports"
    if any(w in q for w in ("election", "win the", "primary", "senate", "house", "governor", "mayor", "seats", "popular vote", "prime minister", "president")):
        return "election/politics"
    if any(w in q for w in ("bitcoin", "ethereum", "solana", "xrp", "price of")):
        return "crypto"
    if any(w in q for w in ("say", "mention", "post", "tweet")):
        return "mentions/posts"
    return "other"


def live():
    """Right now: every open Polymarket market whose end date has passed (last 60 days). Leading side's listed price,
    the oracle status, and what the real order book sells under 97c and 99c."""
    import datetime as dt
    f = {"end_date_min": bot.iso(bot.now() - dt.timedelta(days=60)), "end_date_max": bot.iso(bot.now()), "liquidity_num_min": 100}
    ms = bot.scan_markets(f)
    print(f"{len(ms)} open markets past their end date (last 60 days, $100+ liquidity)", flush=True)
    rows = []
    for m in ms:
        pr = bot.binary(m)
        if not pr or m.get("closed") or m.get("acceptingOrders") is False:
            continue
        st_ = [str(x).lower() for x in bot.jlist(m.get("umaResolutionStatuses"))]
        tier = "disputed" if any("disput" in x for x in st_) else "resolved" if "resolved" in st_ else "proposed" if st_ and st_[-1] == "proposed" else "nothing proposed"
        i = 0 if pr[0] >= pr[1] else 1
        end = bot.parse_iso(m.get("endDate") or m.get("endDateIso"))
        rows.append({"q": m.get("question"), "kind": kind_of(m), "tier": tier, "lead": pr[i], "i": i, "tok": bot.market_tokens(m)[i],
                     "days": (bot.now() - end).total_seconds() / 86400 if end else None, "slug": m.get("slug"),
                     "vol": bot.fnum(bot.pick(m, "volumeNum", "volume"))})
    cand = [r for r in rows if 0.80 <= r["lead"] < 0.995]
    print(f"{len(rows)} binary, {len(cand)} with the leading side at 80c to 99.5c", flush=True)

    def bk(r):
        b = bot.book(r["tok"])
        if not b:
            return r
        asks = b["asks"] if isinstance(b, dict) else b[0]
        r["ask"] = asks[0][0] if asks else None
        r["d97"] = sum(p * s for p, s in asks if p <= 0.97)
        r["d99"] = sum(p * s for p, s in asks if p <= 0.99)
        return r
    with ThreadPoolExecutor(8) as ex:
        cand = list(ex.map(bk, cand))
    tab = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    for r in cand:
        k = (r["kind"], r["tier"])
        tab[k][0] += 1
        if r.get("ask") is not None and r["ask"] <= 0.97:
            tab[k][1] += 1
        tab[k][2] += r.get("d97") or 0
        tab[k][3] += r.get("d99") or 0
    print("| kind | oracle status | markets | ask at 97c or less | $ for sale up to 97c | $ for sale up to 99c |")
    for k, v in sorted(tab.items(), key=lambda x: -x[1][0]):
        print(f"| {k[0]} | {k[1]} | {v[0]} | {v[1]} | ${v[2]:,.0f} | ${v[3]:,.0f} |")
    cand.sort(key=lambda r: -(r.get("d97") or 0))
    print("\nbiggest under 97c:")
    for r in cand[:40]:
        print(f"  {r['kind']:<18} {r['tier']:<16} lead {r['lead']:.3f} ask {r.get('ask')} $97 {r.get('d97', 0):,.0f} $99 {r.get('d99', 0):,.0f} "
              f"{(r['days'] or 0):.1f}d past  {str(r['q'])[:90]}", flush=True)
    wj(os.path.join(CACHE, f"live_{time.strftime('%Y%m%d_%H%M', time.gmtime())}.json.gz"), cand)


# ================================================================ Kalshi tennis (offline, tennis-store)
def tennis_rows():
    """Kalshi tennis matches (minute bid / ask) joined to 365scores' finished match: start + minutes of each set gives
    an outside clock for the match end. -> rows with est_end, close, winner side and minute quotes."""
    import tennis
    gs, ks = tennis.load_365(), tennis.load_kalshi()
    tennis.join(ks, gs)
    out = []
    for k in ks:
        g = k.get("g")
        if not g or not g.get("sets") or any(x[2] is None for x in g["sets"]):
            continue
        mins = sum(x[2] for x in g["sets"])
        est = g["t0"] + mins * 60 + (len(g["sets"]) - 1) * 120
        out.append({"ev": k["ev"], "series": k["series"], "res": k["res"], "close": k["close"], "est": est, "mins": k["mins"],
                    "q": f"{k['name']} vs {k['other']}"})
    return out


def tennis_scan(rows, lags=(5, 10, 20)):
    """Kalshi closes a match market soon after the end: how long after 365scores' end, and is the winner still
    cheap in between (real ask in the minute bars)?"""
    import tennis
    gap = sorted((r["close"] - r["est"]) / 60 for r in rows)
    print(f"{len(rows)} Kalshi tennis matches with an outside end clock")
    if gap:
        print(f"Kalshi close minus 365scores end: middle {gap[len(gap) // 2]:+.0f} min, 10th-90th {gap[len(gap) // 10]:+.0f} .. {gap[len(gap) * 9 // 10]:+.0f}")
    out = {}
    for lag in lags:
        c = collections.Counter()
        for r in rows:
            t = r["est"] + lag * 60
            if t >= r["close"]:
                c["closed already"] += 1
                continue
            q = tennis.quote_at(r["mins"], t, max_gap=180, max_spread=99)
            if not q:
                c["no quote"] += 1
                continue
            ask = q[1] if r["res"] == 1 else 1 - q[0]
            c["quoted"] += 1
            if ask <= 0.97:
                c["winner ask 97c or less"] += 1
            if ask <= 0.90:
                c["winner ask 90c or less"] += 1
        out[lag] = c
        print(f"  {lag} min after the 365scores end: {dict(c)}")
    return out


# ================================================================ sports after the whistle (offline, bt_cache/kn)
CUPS = ("ucl", "uel", "uwcl", "dfb", "scop", "lib", "clf", "acle", "acl2", "fifwc", "fif", "unl")
WHISTLE = 135 * 60     # league soccer: kickoff + 2h15m = the game is over in practice (no extra time in league games)


def soccer_rows():
    """League soccer 3-way markets ('Will X win on <day>?', '... end in a draw?') from bt_cache/kn. The bot's guess is
    the side leading on the last trade before kickoff + 2h15m (no peeking at the payout); a wrong guess is a loss."""
    M, T = rj(os.path.join(CACHE, "markets.json.gz"), {}) or {}, rj(os.path.join(CACHE, "tapes.json.gz"), {}) or {}
    out = []
    for k, m in M.items():
        q = m["q"]
        if not (" win on 20" in q or "end in a draw" in q) or m["slug"].split("-")[0] in CUPS:
            continue
        t0 = m["gst"] + WHISTLE
        b = [x for x in T[k]["b"] if x[0] < m["closed_t"]]
        seen = [x for x in b if x[0] < t0]
        if not seen:
            continue
        out.append({"id": k, "q": q, "known": t0, "guess": seen[-1][2] >= 0.5, "yes": m["final"][0] == 1.0, "b": b,
                    "end": m["closed_t"], "fee": m.get("fee") or 0.05, "ev": m.get("ev_slug") or k, "near": None})
    return out


def grind(rows, lo=0.90, cap=0.9995, stake=25.0, best=False):
    """The 99c grind: right after the answer is known, buy the leader (last trade at `lo`+) at the worst (or best)
    trade of the next hour + fee, whatever the price under `cap`. Paid by the real result."""
    out = []
    for r in rows:
        nxt = [x for x in r["b"] if x[0] >= r["known"]]
        seen = [x for x in r["b"] if x[0] < r["known"]]
        if not nxt or not seen:
            continue
        g = r["guess"]
        ref = seen[-1][2] if g else 1 - seen[-1][2]
        w = [x for x in nxt if x[0] < nxt[0][0] + 3600]
        px = min((x[3] if g else 1 - x[4]) for x in w) if best else max((x[4] if g else 1 - x[3]) for x in w)
        if ref < lo or px >= cap:
            continue
        sh = stake / px
        out.append({"ev": r["ev"], "t": nxt[0][0], "cost": sh * px + fee(px, sh, r["fee"]), "pay": sh if g == r["yes"] else 0.0,
                    "px": px, "name": r["q"], "win": g == r["yes"], "hours": (r["end"] - nxt[0][0]) / 3600,
                    "room": sum(x[5] for x in w)})
    return out


def p100(b):
    c = sum(x["cost"] for x in b)
    return (sum(x["pay"] for x in b) - c) / c * 100 if c else 0.0


def report(log=False):
    import exam
    L = []
    say = lambda s="": (L.append(s), print(s, flush=True))
    tries = 14
    cr, sk, so = crypto_rows(), stock_rows(), soccer_rows()
    fams = [("Bitcoin / Ethereum price bets (answer = Binance's 1-minute price)", cr, 300),
            ("Stock close bets (answer = Nasdaq's official close)", sk, 300),
            ("League soccer, after the final whistle (kickoff + 2h15m)", so, 0)]
    say("# Bets still cheap after the answer is known")
    say()
    say(f"Generated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} by `known.py report`. Paper only, research only.")
    say()
    say("**Question (Jan, 24 Nov):** are there markets where the real answer is already public (game over, price fixed, "
        "market closed) but the winning side can still be bought under 97-99c? How often, how much, how long is the money stuck, "
        "and how often does the payout go the other way?")
    say()
    say("## 1. How often the known winner is still cheap")
    say()
    say("Every real trade, in 1- or 5-minute steps. 'Known' = the moment the outside source fixes the answer. A step counts "
        "as cheap when someone traded the known winner at that price or less (the kind count: one crumb trade is enough).")
    say()
    say("| Family | Markets | Traded after the answer was known | Winner traded at 97c or less | at 99c or less | Our source disagreed with the payout |")
    say("|---|---|---|---|---|---|")
    for nm, rows, d in fams:
        c, dol, _ = scan(rows, d)
        say(f"| {nm} | {c['known']:,} | {c['traded after']:,} | {c['winner traded at 97c or less']:,} (${dol[0.97]:,.0f} traded) | "
            f"{c['winner traded at 99c or less']:,} (${dol[0.99]:,.0f}) | {c['source disagreed with the payout']:,} |")
    say()
    say("## 2. A bot that buys the known winner when it is still under 97c")
    say()
    say("Wait 5 minutes after the answer is fixed (soccer: kickoff + 2h15m), buy the side the source says won if its last "
        "trade is 97c or less, pay the WORST trade of the next hour + 1c + fee, $25 a bet, paid by the real result.")
    say()
    say("| Family | Bets | Lost | Profit per $100 |")
    say("|---|---|---|---|")
    cheap = {}
    for nm, rows, d in fams:
        b = bets_after(rows, delay=d, hi=0.97)
        cheap[nm] = b
        say(f"| {nm} | {len(b)} | {sum(not x['win'] for x in b)} | {usd(p100(b))} |")
    say()
    say("## 3. The 99c grind: buy the known winner at whatever it costs")
    say()
    g = grind(so)
    gc = grind([dict(r, known=r["known"] + 300) for r in cr])
    gs = grind([dict(r, known=r["known"] + 300) for r in sk])
    say("| Family | Bets | Lost | Average price | Profit per $100 (worst trade of the hour) | Hours until paid | $ traded in that hour |")
    say("|---|---|---|---|---|---|---|")
    for nm, b in (("League soccer after the whistle", g), ("Crypto price bets", gc), ("Stock close bets", gs)):
        if b:
            say(f"| {nm} | {len(b)} | {sum(not x['win'] for x in b)} | {sum(x['px'] for x in b) / len(b) * 100:.2f}c | {usd(p100(b))} | "
                f"{(f"{st.median(x['hours'] for x in b):.1f}" if b is g else "under 1 (pays fast)")} | ${sum(x['room'] for x in b):,.0f} |")
    say()
    cards = []
    for nm, b, stt in (("Known answer, winner still under 97c: buy it (crypto, stocks, soccer)", sum(cheap.values(), []), "dropped"),
                       ("Soccer after the final whistle: buy the leader at 99c+ (the grind)", g, "dropped"),
                       ("Crypto / stock bets after the answer is fixed: buy the winner at 99c+", gc + gs, "dropped")):
        if b:
            cards.append((nm, exam.score(b, nm, tries=tries, src="known.py report", status=stt, log=log, quiet=True)))
    say("## 4. Exam")
    say()
    for nm, cd in cards:
        say(f"- **{nm}:** {cd.get('bets')} bets, {usd(cd['per100']) if cd.get('per100') is not None else '-'} per $100, "
            f"verdict **{cd.get('verdict')}**.")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "known_tables.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "sfetch":
        sfetch(int(sys.argv[2]) if len(sys.argv) > 2 else 4000)
    elif cmd == "report":
        report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
    elif cmd == "tennis":
        tennis_scan(tennis_rows())
    elif cmd == "live":
        live()
    elif cmd == "crypto":
        rows = crypto_rows()
        for d in (60, 300, 900):
            c, dol, ex = scan(rows, d)
            print(d, dict(c), {k: round(v) for k, v in dol.items()})
    else:
        print(__doc__)
