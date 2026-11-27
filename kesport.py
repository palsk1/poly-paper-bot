#!/usr/bin/env python3
"""Kalshi's new round-the-clock families (27 Nov 2026): table tennis (Liga Pro, TT Elite, TT Star), eBasketball,
eSoccer, eFootball. Research only, PAPER ONLY: reads public history, never trades, never writes state/.

Question: these leagues are new, niche and run all day. Does anything beat Kalshi's own pre-game price?
  a) Elo rating per player (or per eBasketball "team (player)") from Kalshi's own settled results, walk-forward.
  b) price-only cuts (price band, hour of day, matches already played that day, eSoccer ties).
  c) backward look from the upsets.

    python3 kesport.py peek            # probe nfx_kesport_peek: one market / milestone / candle sample per series
    python3 kesport.py fetch [series]  # probe nfx_kesport_fetch: settled markets + start times + 1-minute candles
    python3 kesport.py report          # offline: backtest/kesport.md (after `store.py pull bt_cache/nf`)

Data: bt_cache/nf/kes/ (shared store folder bt_cache/nf).
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import exam
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "nf", "kes")
OUT = os.path.join(ROOT, "backtest", "kesport.md")
SERIES = ["KXLIGAPROMATCH", "KXTTELITEMATCH", "KXTTSTARMATCH", "KXEBASKETBALLGAME", "KXESOCCERGAME", "KXEFOOTBALLGAME"]
kget = yesno.kget
T0 = time.time()
PRE = 180          # minutes of 1-minute candles before the start


def its(x):
    if not x:
        return 0
    try:
        return int(bot.parse_iso(x).timestamp())
    except Exception:
        return 0


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def short(x, n=1500):
    s = json.dumps(x, default=str)
    return s[:n]


# ================================================================ peek
def peek():
    try:
        print("CUTOFF", short(kget("/historical/cutoff")))
    except Exception as e:
        print("cutoff failed", e)
    for s in SERIES:
        print("=" * 30, s)
        try:
            print("SERIES", short(kget(f"/series/{s}"), 1200))
        except Exception as e:
            print("series failed", str(e)[:200])
        try:
            r = kget("/markets", {"series_ticker": s, "status": "settled", "limit": 6})
        except Exception as e:
            print("markets failed", str(e)[:200])
            continue
        ms = r.get("markets") or []
        if not ms:
            continue
        m = ms[0]
        print("MARKET", short(m, 3000))
        for x in ms[1:]:
            print("  other", x.get("ticker"), x.get("yes_sub_title"), x.get("result"), x.get("open_time"), x.get("close_time"),
                  x.get("expected_expiration_time"), x.get("volume_fp") or x.get("volume"))
        ev = m.get("event_ticker")
        try:
            print("EVENT", short(kget(f"/events/{ev}"), 1500))
        except Exception as e:
            print("event failed", str(e)[:200])
        for p in ({"limit": 5, "related_event_ticker": ev}, {"limit": 5, "event_ticker": ev}):
            try:
                print("MILESTONE", p, short(kget("/milestones", p), 1500))
            except Exception as e:
                print("milestone failed", p, str(e)[:200])
        o, c = its(m.get("open_time")), its(m.get("close_time"))
        try:
            r = kget("/markets/candlesticks", {"market_tickers": ",".join(x["ticker"] for x in ms[:4]), "start_ts": o, "end_ts": c, "period_interval": 1})
            for mm in r.get("markets") or []:
                cs = mm.get("candlesticks") or []
                print("CANDLES", mm.get("market_ticker"), len(cs), "first", short(cs[:1], 700), "last", short(cs[-1:], 700))
                act = [x for x in cs if bot.fnum(x.get("volume_fp") or x.get("volume"), 0) > 0]
                print("  minutes with trades", len(act), "first trade minute", (act[0].get("end_period_ts") - o) / 60 if act else None,
                      "close-open min", (c - o) / 60)
        except Exception as e:
            print("candles failed", str(e)[:200])
        try:
            r = kget("/markets/trades", {"ticker": m["ticker"], "limit": 1000})
            tr = r.get("trades") or []
            print("TRADES", len(tr), short(tr[:2], 800))
            if tr:
                ts = sorted(its(t.get("created_time")) for t in tr)
                print("  trade span min from open", (ts[0] - o) / 60, (ts[-1] - o) / 60, "close", (c - o) / 60)
        except Exception as e:
            print("trades failed", str(e)[:200])
    # milestones with these competitions: what kinds exist
    try:
        r = kget("/milestones", {"limit": 500, "minimum_start_date": bot.iso(dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=6))})
        rows = r.get("milestones") or []
        kinds = collections.Counter((x.get("category"), x.get("type")) for x in rows)
        print("MILESTONE KINDS", kinds.most_common(30))
        for x in rows:
            evs = " ".join((x.get("related_event_tickers") or []) + (x.get("primary_event_tickers") or []))
            if any(s in evs for s in SERIES):
                print("MS HIT", short(x, 800))
                break
    except Exception as e:
        print("milestones list failed", str(e)[:200])


# ================================================================ fetch
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}


def sched(ev):
    """Scheduled start (unix) from the event ticker: KXLIGAPROMATCH-26NOV271100STRORL = 27 Nov 2026 11:00 New York time.
    Never the close time (that leaks the result)."""
    import re
    from zoneinfo import ZoneInfo
    m = re.search(r"-(\d\d)([A-Z]{3})(\d\d)(\d\d)(\d\d)", ev or "")
    if not m or m.group(2) not in MON:
        return 0
    y, mo, d, h, mi = 2000 + int(m.group(1)), MON[m.group(2)], int(m.group(3)), int(m.group(4)), int(m.group(5))
    try:
        return int(dt.datetime(y, mo, d, h, mi, tzinfo=ZoneInfo("America/New_York")).timestamp())
    except Exception:
        return 0


def list_series(s):
    rows = []
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(400):
            p = {"series_ticker": s, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  {s} {path} failed: {str(e)[:100]}", flush=True)
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    out, seen = {}, set()
    for m in rows:
        tk = str(m.get("ticker") or "")
        if not tk or tk in seen or not str(m.get("event_ticker") or "").startswith(s):
            continue
        seen.add(tk)
        out[tk] = {"t": tk, "ev": m.get("event_ticker"), "name": m.get("yes_sub_title"), "res": m.get("result"),
                   "sv": m.get("settlement_value_dollars"), "open": its(m.get("open_time")), "close": its(m.get("close_time")),
                   "start": sched(m.get("event_ticker")), "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0),
                   "rule": str(m.get("rules_primary") or "")[:300], "strike": m.get("custom_strike")}
    return out


def crow(c):
    def px(b, k="close"):
        d = c.get(b) or {}
        v = d.get(k + "_dollars")
        if v in (None, ""):
            v = d.get(k)
            if v in (None, ""):
                return None
            v = float(v) / 100
        return round(float(v) * 100, 2)
    pr = c.get("price") or {}
    last = pr.get("close_dollars") or pr.get("close")
    return [int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask"), round(bot.fnum(c.get("volume_fp") or c.get("volume"), 0), 2),
            None if last in (None, "") else round(float(last) * 100, 2), px("yes_ask", "low"), px("yes_bid", "high")]


def fetch(only=None):
    for s in SERIES:
        if only and s not in only:
            continue
        mp = os.path.join(CACHE, f"mk_{s}.json.gz")
        have = rj(mp, {}) or {}
        new = list_series(s)
        have.update(new)
        wj(mp, have)
        res = collections.Counter(m["res"] for m in have.values())
        print(f"{s}: {len(have)} markets, {len({m['ev'] for m in have.values()})} events, results {dict(res)}, "
              f"no start {sum(1 for m in have.values() if not m['start'])} ({time.time() - T0:.0f}s)", flush=True)
        cp = os.path.join(CACHE, f"c_{s}.json.gz")
        cs = rj(cp, {}) or {}
        todo = sorted([m for m in have.values() if m["t"] not in cs and m["res"] in ("yes", "no") and m["start"] and m["open"]],
                      key=lambda m: m["start"])
        groups = [todo[i:i + 20] for i in range(0, len(todo), 20)]

        def one(g):
            a = max(min(max(m["open"] - 60, m["start"] - PRE * 60) for m in g), 0)
            b = max(m["start"] for m in g) + 120
            for _ in range(3):
                try:
                    r = kget("/markets/candlesticks", {"market_tickers": ",".join(m["t"] for m in g), "start_ts": a, "end_ts": b, "period_interval": 1})
                    out = {}
                    for x in r.get("markets") or []:
                        out[x.get("market_ticker")] = [crow(c) for c in x.get("candlesticks") or []]
                    return g, out
                except Exception as e:
                    err = e
                    time.sleep(3)
            return g, err
        bad = 0
        with ThreadPoolExecutor(6) as ex:
            for i, (g, out) in enumerate(ex.map(one, groups)):
                if isinstance(out, Exception):
                    bad += 1
                    if bad < 4:
                        print("   candles failed", str(out)[:200], flush=True)
                    continue
                for m in g:
                    st = m["start"]
                    cs[m["t"]] = [r for r in out.get(m["t"]) or [] if st - PRE * 60 - 3600 <= r[0] <= st + 120]
                if i and i % 200 == 0:
                    wj(cp, cs)
                    print(f"   {s} candles {i}/{len(groups)} ({time.time() - T0:.0f}s)", flush=True)
                if time.time() - T0 > 110 * 60:
                    break
        wj(cp, cs)
        print(f"  {s}: candles for {sum(1 for v in cs.values() if v)} of {len(cs)} markets, {bad} failed calls ({time.time() - T0:.0f}s)", flush=True)
        if time.time() - T0 > 110 * 60:
            print("out of time, run again", flush=True)
            return


def hist(only=None):
    """Second pass: markets the batch call missed (older than Kalshi's history cutoff, or a failed group): one call per
    market on the per-market endpoints (live, then /historical). For a two-player game one side is enough (mirror)."""
    for s in SERIES:
        if only and s not in only:
            continue
        mk = rj(os.path.join(CACHE, f"mk_{s}.json.gz"), {}) or {}
        cp = os.path.join(CACHE, f"c_{s}.json.gz")
        cs = rj(cp, {}) or {}
        evs = collections.defaultdict(list)
        for m in mk.values():
            if m["res"] in ("yes", "no") and m["start"] and m["open"]:
                evs[m["ev"]].append(m)
        todo = []
        for ev, ms in evs.items():
            miss = [m for m in ms if not cs.get(m["t"])]
            if not miss:
                continue
            if s != "KXESOCCERGAME" and len(ms) == 2 and len(miss) == 1:
                continue
            todo += miss[:1] if s != "KXESOCCERGAME" and len(ms) == 2 else miss
        print(f"{s}: {len(todo)} markets to fetch one by one ({time.time() - T0:.0f}s)", flush=True)

        def one(m):
            a, b = max(m["open"] - 60, m["start"] - PRE * 60), m["start"] + 120
            for path in (f"/series/{s}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
                try:
                    r = kget(path, {"start_ts": a, "end_ts": b, "period_interval": 1})
                except Exception:
                    continue
                rows = [crow(c) for c in r.get("candlesticks") or []]
                if rows:
                    return m["t"], rows
            return m["t"], []
        with ThreadPoolExecutor(8) as ex:
            for i, (tk, rows) in enumerate(ex.map(one, todo)):
                cs[tk] = rows
                if i and i % 1000 == 0:
                    wj(cp, cs)
                    print(f"   {s} {i}/{len(todo)} ({time.time() - T0:.0f}s)", flush=True)
                if time.time() - T0 > 100 * 60:
                    break
        wj(cp, cs)
        print(f"  {s}: now {sum(1 for v in cs.values() if v)} markets with candles ({time.time() - T0:.0f}s)", flush=True)
        if time.time() - T0 > 100 * 60:
            print("out of time, run again", flush=True)
            return


# ================================================================ analysis (offline)
FAM = {"KXLIGAPROMATCH": "Liga Pro table tennis", "KXTTELITEMATCH": "TT Elite table tennis", "KXTTSTARMATCH": "TT Star table tennis",
       "KXEBASKETBALLGAME": "eBasketball", "KXESOCCERGAME": "eSoccer", "KXEFOOTBALLGAME": "eFootball"}
STAKE = 10.0
MAXSPREAD = 10      # cents, on the market we buy from
TRIES = collections.Counter()


def player(name, s):
    import re
    n = str(name or "").strip()
    if s.startswith("KXTT") or s.startswith("KXLIGA"):
        return n.lower()
    m = re.search(r"\(([^)]+)\)\s*$", n)
    return (m.group(1) if m else n).strip().lower()


def fixq(rows):
    vals = [x for r in rows for x in (r[1], r[2]) if x is not None]
    if vals and any(0 < x < 0.99 for x in vals) and max(vals) <= 1.01:
        for r in rows:
            for i in (1, 2, 4, 5, 6):
                if r[i] is not None:
                    r[i] = round(r[i] * 100, 2)


def at(rows, T):
    """bid, ask (cents) of the last candle ending at or before T; contracts traded up to T."""
    q, vol = None, 0.0
    for r in rows:
        if r[0] > T:
            break
        if r[1] is not None or r[2] is not None:
            q = (r[1] or 0.0, r[2] if r[2] is not None else 100.0)
        vol += r[3] or 0
    return q, vol


def kfee(C, p):
    return math.ceil(0.07 * C * p * (1 - p) * 100 - 1e-9) / 100


def bet(ev, t, price_c, won, stake=STAKE, **kw):
    p = price_c / 100
    C = max(1, int(stake / p))
    cost = C * p + kfee(C, p)
    return dict(ev=ev, t=t, cost=round(cost, 4), pay=float(C if won else 0), sh=C, px=p, **kw)


def load_games(s, lag=2):
    mk = rj(os.path.join(CACHE, f"mk_{s}.json.gz"), {}) or {}
    cs = rj(os.path.join(CACHE, f"c_{s}.json.gz"), {}) or {}
    evs = collections.defaultdict(list)
    for m in mk.values():
        evs[m["ev"]].append(m)
    games, skip = [], collections.Counter()
    for ev, ms in evs.items():
        ms = [m for m in ms if m["res"] in ("yes", "no")]
        tie = [m for m in ms if str(m["t"]).endswith("-TIE")]
        sides = [m for m in ms if not str(m["t"]).endswith("-TIE")]
        if len(sides) != 2 or sum(m["res"] == "yes" for m in ms) != 1 or len(tie) > 1:
            skip["shape"] += 1
            continue
        st = sides[0]["start"]
        if not st:
            skip["nostart"] += 1
            continue
        T = st - lag * 60
        g = {"ev": ev, "s": s, "start": st, "T": T, "close": max(m["close"] for m in ms), "side": [], "tie": None}
        ok = True
        if not tie and len(sides) == 2:
            for X, Y in ((0, 1), (1, 0)):
                if not cs.get(sides[X]["t"]) and cs.get(sides[Y]["t"]):
                    src = [list(r) for r in cs[sides[Y]["t"]]]
                    fixq(src)
                    cs[sides[X]["t"]] = [[r[0], None if r[2] is None else 100 - r[2], None if r[1] is None else 100 - r[1], r[3], None, None, None]
                                         for r in src]
        for m in sides + tie:
            rows = cs.get(m["t"])
            if rows is None:
                ok = False
                break
            fixq(rows)
            q, vol = at(rows, T)
            q30, _ = at(rows, T - 20 * 60)
            d = {"t": m["t"], "name": m["name"], "p": player(m["name"], s), "won": m["res"] == "yes", "q": q, "q20": q30, "vol": vol,
                 "open": m["open"], "allvol": m["vol"]}
            if str(m["t"]).endswith("-TIE"):
                g["tie"] = d
            else:
                g["side"].append(d)
        if not ok:
            skip["nocandles"] += 1
            continue
        if any(d["q"] is None for d in g["side"]):
            skip["noquote"] += 1
            continue
        games.append(g)
    games.sort(key=lambda g: g["start"])
    # best real buy price of each side and the fair (middle) chance
    for g in games:
        A, B = g["side"]
        if g["tie"] is None:
            for X, Y in ((A, B), (B, A)):
                opts = [(X["q"][1], X["q"][1] - X["q"][0])]
                if Y["q"][0] > 0:
                    opts.append((100 - Y["q"][0], Y["q"][1] - Y["q"][0]))
                X["buy"], X["spr"] = min(opts)
            mA, mB = sum(A["q"]) / 2, sum(B["q"]) / 2
            A["fair"] = mA / (mA + mB) if mA + mB > 0 else 0.5
            B["fair"] = 1 - A["fair"]
        else:
            Tm = g["tie"]
            mids = []
            for X in (A, B, Tm):
                if X["q"] is None:
                    X["buy"], X["spr"], mids = None, 99, None
                    break
                X["buy"], X["spr"] = X["q"][1], X["q"][1] - X["q"][0]
                X["nobuy"] = 100 - X["q"][0]
                mids.append(sum(X["q"]) / 2)
            if mids and sum(mids) > 0:
                for X, mm in zip((A, B, Tm), mids):
                    X["fair"] = mm / sum(mids)
            else:
                for X in (A, B, Tm):
                    X["fair"] = None
        g["ok"] = all(X.get("buy") is not None and X.get("fair") is not None and X["spr"] <= MAXSPREAD and 0 < X["buy"] < 100
                      for X in g["side"])
    return games, skip


def add_elo(games, K=32, base=1500.0):
    """walk-forward Elo: a game's rating uses only games that closed before its decision time."""
    R, N = collections.defaultdict(lambda: base), collections.Counter()
    last = collections.defaultdict(list)            # player -> [(close, won)]
    pend = sorted(games, key=lambda g: g["close"])
    j = 0
    for g in games:
        while j < len(pend) and pend[j]["close"] < g["T"]:
            h = pend[j]
            j += 1
            A, B = h["side"]
            win = 1.0 if A["won"] else (0.0 if B["won"] else 0.5)
            e = 1 / (1 + 10 ** ((R[B["p"]] - R[A["p"]]) / 400))
            R[A["p"]] += K * (win - e)
            R[B["p"]] -= K * (win - e)
            N[A["p"]] += 1
            N[B["p"]] += 1
            last[A["p"]].append((h["close"], h["start"], win == 1.0))
            last[B["p"]].append((h["close"], h["start"], win == 0.0))
        A, B = g["side"]
        g["elo"] = 1 / (1 + 10 ** ((R[B["p"]] - R[A["p"]]) / 400))
        g["n"] = (N[A["p"]], N[B["p"]])
        for X in (A, B):
            hist = last[X["p"]]
            X["prev"] = hist[-1][2] if hist else None
            X["prev_gap"] = (g["T"] - hist[-1][0]) / 60 if hist else None
            day0 = g["start"] - 6 * 3600
            X["today"] = sum(1 for c, s0, w in hist if s0 >= day0)
            X["form5"] = sum(w for c, s0, w in hist[-5:]) if len(hist) >= 5 else None
    return games


def logloss(ps, ys):
    e = 1e-6
    return -sum(y * math.log(max(e, p)) + (1 - y) * math.log(max(e, 1 - p)) for p, y in zip(ps, ys)) / max(1, len(ys))


def lg(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def fit2(xs, ys, iters=300):
    """logistic y ~ a*x1 + b*x2 (no intercept), Newton steps."""
    a = b = 0.0
    for _ in range(iters):
        ga = gb = haa = hab = hbb = 0.0
        for (x1, x2), y in zip(xs, ys):
            p = 1 / (1 + math.exp(-(a * x1 + b * x2)))
            ga += (y - p) * x1
            gb += (y - p) * x2
            w = p * (1 - p)
            haa += w * x1 * x1
            hab += w * x1 * x2
            hbb += w * x2 * x2
        det = haa * hbb - hab * hab
        if abs(det) < 1e-12:
            break
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        a += da
        b += db
        if abs(da) + abs(db) < 1e-7:
            break
    return a, b


def pelo(g, X):
    """Elo's chance that side X wins; with a tie market, the price's tie chance is taken off first."""
    pe = g["elo"] if X is g["side"][0] else 1 - g["elo"]
    if g.get("tie") is not None and g["tie"].get("fair") is not None:
        pe *= 1 - g["tie"]["fair"]
    return pe


def p100(bets):
    c = sum(b["cost"] for b in bets)
    return 100 * sum(b["pay"] - b["cost"] for b in bets) / c if c else 0.0


def line(name, bets, mid):
    h1 = [b for b in bets if b["t"] < mid]
    h2 = [b for b in bets if b["t"] >= mid]
    return f"| {name} | {len(h1)} | {p100(h1):+.2f} | {len(h2)} | {p100(h2):+.2f} | {len(bets)} | {p100(bets):+.2f} |"


HEAD = "| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |\n|---|---|---|---|---|---|---|"


def cut_bets(games, pick, key="buy"):
    out = []
    for g in games:
        if not g["ok"]:
            continue
        for X in g["side"] + ([g["tie"]] if g["tie"] else []):
            if X.get("buy") is None:
                continue
            r = pick(g, X)
            if r:
                out.append(bet(g["ev"], g["T"], X["buy"], X["won"], name=X["name"], fair=X.get("fair")))
                break        # one bet per game
    return out


def report(log=True):
    L = ["# Kalshi's new all-day families: table tennis and e-sports (27 Nov 2026)", "",
         "Research only, paper only. `kesport.py`, data `bt_cache/nf/kes/` (shared store folder `bt_cache/nf`).", "",
         "Every bet is bought at the real asking price 2 minutes before the scheduled start (start time from the event name, "
         "never from the close), plus Kalshi's fee, $10 a bet, one bet per game. 'First half' = the older half of each family's "
         "games, where rules were picked; 'fresh half' = the newer half, the check.", ""]
    allcards = []
    summary = []
    for s in SERIES:
        games, skip = load_games(s)
        ok = [g for g in games if g["ok"]]
        if len(ok) < 100:
            L += [f"## {FAM[s]} (`{s}`)", "", f"Only {len(ok)} games with a usable pre-game price (skipped: {dict(skip)}). Not tested.", ""]
            summary.append((s, len(ok), None))
            continue
        mid = ok[len(ok) // 2]["start"] - 2 * 60
        h1 = [g for g in ok if g["T"] < mid]
        # Elo: pick K on the first half by log loss
        bestK, bestL = 32, 9
        for K in (8, 16, 24, 32, 48, 64):
            add_elo(games, K)
            sel = [g for g in h1 if min(g["n"]) >= 5]
            ll = logloss([g["elo"] for g in sel], [1.0 if g["side"][0]["won"] else 0.0 for g in sel])
            TRIES[s] += 1
            if ll < bestL:
                bestK, bestL = K, ll
        add_elo(games, bestK)
        vol = sorted(sum(X["vol"] for X in g["side"]) for g in ok)
        allv = sorted(sum(X["allvol"] for X in g["side"]) for g in ok)
        days = max(1.0, (ok[-1]["start"] - ok[0]["start"]) / 86400)
        L += [f"## {FAM[s]} (`{s}`)", "",
              f"{len(ok)} games with a usable price ({len(games)} settled with a quote, skipped {dict(skip)}), "
              f"{time.strftime('%d %b', time.gmtime(ok[0]['start']))} to {time.strftime('%d %b', time.gmtime(ok[-1]['start']))}, "
              f"about {len(ok) / days:.0f} a day. Contracts traded before the start, typical game: {vol[len(vol) // 2]:.0f} "
              f"(busiest tenth {vol[int(len(vol) * .9)]:.0f}); whole game incl. live: {allv[len(allv) // 2]:.0f}.", ""]
        # forecast quality
        rated = [g for g in ok if min(g["n"]) >= 5]
        for nm, part in (("first half", [g for g in rated if g["T"] < mid]), ("fresh half", [g for g in rated if g["T"] >= mid])):
            ys = [1.0 if g["side"][0]["won"] else 0.0 for g in part]
            if g["tie"] is not None if part else False:
                pass
            L.append(f"- Forecast check, {nm} ({len(part)} games, both players 5+ earlier games): price miss score "
                     f"{logloss([g['side'][0]['fair'] for g in part], ys):.4f}, Elo (K={bestK}) {logloss([pelo(g, g['side'][0]) for g in part], ys):.4f} "
                     f"(lower is better; a coin flip is 0.6931).")
        # combined model, fit on first half
        r1 = [g for g in rated if g["T"] < mid]
        r2 = [g for g in rated if g["T"] >= mid]
        xs1 = [(lg(g["side"][0]["fair"]), lg(pelo(g, g["side"][0]))) for g in r1]
        ys1 = [1.0 if g["side"][0]["won"] else 0.0 for g in r1]
        a, b = fit2(xs1, ys1) if r1 else (1.0, 0.0)
        TRIES[s] += 1
        def comb(g):
            return 1 / (1 + math.exp(-(a * lg(g["side"][0]["fair"]) + b * lg(pelo(g, g["side"][0])))))
        ys2 = [1.0 if g["side"][0]["won"] else 0.0 for g in r2]
        L.append(f"- Price + Elo together (weights fit on the first half: price {a:.2f}, Elo {b:.2f}): fresh-half miss score "
                 f"{logloss([comb(g) for g in r2], ys2):.4f} vs price alone {logloss([g['side'][0]['fair'] for g in r2], ys2):.4f}.")
        L += ["", HEAD]
        rules = []
        for gap in (0.05, 0.10, 0.15):
            def pk(g, X, gap=gap):
                if min(g["n"]) < 5:
                    return False
                if X is g.get("tie"):
                    return False
                pe = pelo(g, X)
                return pe - (X["buy"] / 100 + 0.02) >= gap
            rules.append((f"Elo {int(gap * 100)}c+ above the real ask", pk))
        def pkc(g, X):
            if min(g["n"]) < 5 or X is g.get("tie"):
                return False
            pc = comb(g) if X is g["side"][0] else (1 - comb(g) - (g["tie"]["fair"] if g.get("tie") else 0))
            return pc - (X["buy"] / 100 + 0.02) >= 0.03
        rules.append(("Price+Elo 3c+ above the real ask", pkc))
        bands = [(3, 15), (15, 30), (30, 45), (45, 55), (55, 70), (70, 85), (85, 97)]
        for lo, hi in bands:
            rules.append((f"Buy any side priced {lo}-{hi}c", (lambda g, X, lo=lo, hi=hi: X is not g.get("tie") and lo <= X["buy"] < hi)))
        for h0 in range(0, 24, 6):
            rules.append((f"Favourite, start {h0:02d}-{h0 + 6:02d} New York time",
                          (lambda g, X, h0=h0: X is not g.get("tie") and X["fair"] > 0.5 and h0 <= (time.gmtime(g["start"] - 5 * 3600).tm_hour) < h0 + 6)))
            rules.append((f"Underdog, start {h0:02d}-{h0 + 6:02d} New York time",
                          (lambda g, X, h0=h0: X is not g.get("tie") and X["fair"] < 0.5 and h0 <= (time.gmtime(g["start"] - 5 * 3600).tm_hour) < h0 + 6)))
        def other(g, X):
            return g["side"][1] if X is g["side"][0] else g["side"][0]
        rules += [
            ("Side whose rival played 2+ more games today", lambda g, X: X is not g.get("tie") and (other(g, X)["today"] - X["today"]) >= 2),
            ("Side that lost its last game, other won", lambda g, X: X is not g.get("tie") and X["prev"] is False and other(g, X)["prev"] is True),
            ("Side that won its last game, other lost", lambda g, X: X is not g.get("tie") and X["prev"] is True and other(g, X)["prev"] is False),
            ("Side with 4-5 of last 5 won, rival 0-1", lambda g, X: X is not g.get("tie") and (X["form5"] or 0) >= 4 and other(g, X)["form5"] is not None and other(g, X)["form5"] <= 1),
            ("Follow a 5c+ move in the last 20 min", lambda g, X: X is not g.get("tie") and X["q20"] and (sum(X["q"]) - sum(X["q20"])) / 2 >= 5),
            ("Fade a 5c+ move in the last 20 min", lambda g, X: X is not g.get("tie") and X["q20"] and (sum(X["q20"]) - sum(X["q"])) / 2 >= 5),
            ("Busy book (top third pre-game volume), favourite", lambda g, X: X is not g.get("tie") and X["fair"] > 0.5 and sum(Y["vol"] for Y in g["side"]) >= vol[len(vol) * 2 // 3]),
            ("Quiet book (bottom third), favourite", lambda g, X: X is not g.get("tie") and X["fair"] > 0.5 and sum(Y["vol"] for Y in g["side"]) <= vol[len(vol) // 3]),
            ("Quiet book (bottom third), underdog", lambda g, X: X is not g.get("tie") and X["fair"] < 0.5 and sum(Y["vol"] for Y in g["side"]) <= vol[len(vol) // 3]),
            ("Player new to Kalshi (under 5 games) vs veteran (30+): veteran", lambda g, X: X is not g.get("tie") and g["n"][g["side"].index(X)] >= 30 and g["n"][1 - g["side"].index(X)] < 5),
        ]
        if any(g["tie"] for g in ok):
            def tie_yes(lo, hi):
                def f(g, X):
                    return X is g.get("tie") and X["spr"] <= MAXSPREAD and lo <= X["buy"] < hi
                return f
            for lo, hi in ((3, 15), (15, 25), (25, 40)):
                rules.append((f"eSoccer: buy Tie at {lo}-{hi}c", tie_yes(lo, hi)))
        res = []
        for nm, pk in rules:
            bs = cut_bets(ok, pk)
            TRIES[s] += 1
            res.append((nm, bs))
            L.append(line(nm, bs, mid))
        if any(g["tie"] for g in ok):
            # Tie No: buy "no tie" at 100 - tie bid
            bs = []
            for g in ok:
                X = g["tie"]
                if X and X.get("nobuy") and X["spr"] <= MAXSPREAD and 60 <= X["nobuy"] < 97:
                    bs.append(bet(g["ev"], g["T"], X["nobuy"], not X["won"]))
            TRIES[s] += 1
            res.append(("eSoccer: bet against the Tie (No at 60-97c)", bs))
            L.append(line("eSoccer: bet against the Tie (No at 60-97c)", bs, mid))
        # backward look: the upsets
        dogs = []
        for g in ok:
            for X in g["side"]:
                if X["fair"] < 0.35:
                    dogs.append((g, X))
        up = [(g, X) for g, X in dogs if X["won"]]
        L += ["", f"**Backward look.** {len(up)} upsets (winner priced under 35c) out of {len(dogs)} such underdogs "
              f"(price said {sum(X['fair'] for g, X in dogs):.0f} wins). What the underdogs had beforehand, and what buying them earned:", "",
              "| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |", "|---|---|---|---|---|---|"]
        feats = [
            ("all", lambda g, X: True),
            ("won its last game", lambda g, X: X["prev"] is True),
            ("lost its last game", lambda g, X: X["prev"] is False),
            ("Elo likes it (Elo 10c+ above price)", lambda g, X: min(g["n"]) >= 5 and (pelo(g, X) - X["fair"]) >= 0.10),
            ("price fell 5c+ in the last 20 min", lambda g, X: X["q20"] and (sum(X["q20"]) - sum(X["q"])) / 2 >= 5),
            ("price rose 5c+ in the last 20 min", lambda g, X: X["q20"] and (sum(X["q"]) - sum(X["q20"])) / 2 >= 5),
            ("rival played 3+ games today", lambda g, X: other(g, X)["today"] >= 3),
            ("its 1st game today", lambda g, X: X["today"] == 0),
            ("night in New York (0-6)", lambda g, X: time.gmtime(g["start"] - 5 * 3600).tm_hour < 6),
            ("rival on a 4-5 of 5 run", lambda g, X: (other(g, X)["form5"] or 0) >= 4),
        ]
        for nm, f in feats:
            sel = [(g, X) for g, X in dogs if f(g, X)]
            TRIES[s] += 1
            bs = [bet(g["ev"], g["T"], X["buy"], X["won"]) for g, X in sel if X["spr"] <= MAXSPREAD]
            L.append(f"| {nm} | {len(sel)} | {sum(X['won'] for g, X in sel)} | {sum(X['fair'] for g, X in sel):.0f} | "
                     f"{p100([b for b in bs if b['t'] >= mid]):+.2f} | {p100(bs):+.2f} |")
            res.append(("Upset look: underdog, " + nm, bs))
        # pick on the first half: the best rule ahead there with 50+ bets, check on the fresh half
        cand = [(nm, bs) for nm, bs in res if len([b for b in bs if b["t"] < mid]) >= 50]
        cand.sort(key=lambda x: -p100([b for b in x[1] if b["t"] < mid]))
        L += [""]
        picks = cand[:2]
        for nm, bs in picks:
            fresh = [b for b in bs if b["t"] >= mid]
            card = exam.score(fresh, f"kesport {s}: {nm} (fresh half)", tries=TRIES[s], src="kesport.py", log=log, quiet=True)
            allcards.append((s, nm, card, bs, mid))
            L.append(f"- Best on the first half: **{nm}**, {p100([b for b in bs if b['t'] < mid]):+.2f} per $100 there; "
                     f"fresh half {len(fresh)} bets, {p100(fresh):+.2f} per $100, exam: **{card['verdict']}** "
                     f"(luck range {card.get('lo100')} to {card.get('hi100')}, {TRIES[s]} cuts tried on this family).")
        # Elo rule always graded
        eb = dict(res)["Elo 10c+ above the real ask"]
        card = exam.score(eb, f"kesport {s}: Elo 10c+ above the real ask", tries=TRIES[s], src="kesport.py", log=log, quiet=True)
        allcards.append((s, "Elo 10c+ above the real ask", card, eb, mid))
        L.append(f"- The planned test, Elo 10c+ above the ask: {len(eb)} bets, {p100(eb):+.2f} per $100, exam: **{card['verdict']}**.")
        L.append("")
        summary.append((s, len(ok), (vol[len(vol) // 2], len(ok) / days)))
    return L, allcards, summary


def big_wins(bets, n=8):
    return sorted(bets, key=lambda b: -(b["pay"] - b["cost"]))[:n]


def run():
    L, cards, summary = report()
    L += ["## Biggest wins, read one by one", ""]
    for s, nm, card, bs, mid in cards:
        if card.get("per100") is not None and card["per100"] > 0:
            L.append(f"*{FAM[s]}: {nm}*")
            for b in big_wins(bs, 5):
                L.append(f"- {time.strftime('%d %b %H:%M', time.gmtime(b['t']))} UTC {b['ev']} {b.get('name') or ''}: "
                         f"paid ${b['cost']:.2f} for {b['sh']} at {b['px'] * 100:.0f}c, got ${b['pay']:.2f}")
            L.append("")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    if cmd == "peek":
        peek()
    elif cmd == "fetch":
        fetch(sys.argv[2:] or None)
    elif cmd == "hist":
        hist(sys.argv[2:] or None)
    elif cmd == "report":
        run()
