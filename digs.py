#!/usr/bin/env python3
"""Edge digs, 2026-11-10 (one long research thread). PAPER ONLY, reads data, never trades, changes no track.

Four digs, each reusing an existing tool where one fits (TOOLS.md):

  draws     Soccer draws, deeper (census.py sports cache): by league, price, hours before kickoff, how even the
            match is, the other two legs of the same 3-way game, and other sports that have a draw.
            Real-buy check on the trade tape (census.tape_check, buys before kickoff only).
            probe: dig_draws  (needs bt_cache/sports from `btsportsfetch` on main)
  kfetch    Kalshi family census download: settled Kalshi markets (every series), hourly bid/ask candles over the
            last 3 days before close. Own cache dig_cache/kfam/.   probe: dig_kfetch
  kfam      Kalshi family census: buy at the REAL ask (YES ask, or 1 - YES bid for NO) 72h/24h/6h/1h before close,
            Kalshi taker fee, held to the result; by category and by series; halves, +1c, placebo families.
            probe: dig_kfam (or dig_kall = fetch + run)
  ideas     Calendar effects (month end, US holidays, start-of-month deposits, weekend endings) and "the set adds up
            to more/less than $1" inside one event, as idea-machine features (ideas.py), screened with ONLY these
            features + the placebos, so the many-ideas correction is small.   probe: dig_ideas
  selftest  offline checks of the Kalshi scorer and placebo logic.

Reports: backtest/digs_draws.md, backtest/kfamily.md, backtest/digs_ideas.md (the probe prints them too).
"""
import bisect
import collections
import datetime as dt
import hashlib
import math
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "backtest")
DIG = os.path.join(ROOT, "dig_cache")
DAY = 86400
T0 = time.time()


def m100(x):
    return "" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def write(name, lines):
    os.makedirs(OUT, exist_ok=True)
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(txt)
    print(txt)


def cluster_score(items):
    """items = [(event, profit, stake)]. Profit per $100 staked and a 90% band, clustered by event."""
    by = collections.defaultdict(lambda: [0.0, 0.0])
    for ev, p, s in items:
        by[ev][0] += p
        by[ev][1] += s
    P = sum(v[0] for v in by.values())
    S = sum(v[1] for v in by.values())
    n = len(by)
    if S <= 0 or n < 2:
        return None
    r = P / S
    se = math.sqrt(sum((v[0] - r * v[1]) ** 2 for v in by.values()) / (S * S) * (n / (n - 1)))
    return {"per100": 100 * r, "lo": 100 * (r - 1.645 * se), "hi": 100 * (r + 1.645 * se), "events": n,
            "bets": len(items)}


# ================================================================ dig 1: soccer draws, deeper

DRAW_BANDS = ((0.15, 0.22), (0.22, 0.27), (0.27, 0.32), (0.32, 0.50))


def draws():
    import backtest as bt
    import census
    ms, hist, rows, kinds = census.sports_rows()
    print(f"sports rows {len(rows):,}; kinds {kinds.most_common(12)}")
    L = ["# Soccer draws, deeper (digs.py draws)", "",
         f"Generated {bot.iso(dt.datetime.now(dt.timezone.utc))}. In-sample games only (ended before "
         f"2026-11-10; the 21 Dec holdout is untouched). Chart price 1h after the snapshot, never after kickoff, "
         "+2c + fee, held to the result. 'Per $100' = profit per $100 staked, grouped by game.", ""]
    # every event: its moneyline legs (team A, draw, team B)
    by_ev = collections.defaultdict(list)
    for mk in ms.values():
        if hist.get(mk["id"]) and mk.get("gst"):
            by_ev[mk.get("ev") or mk["id"]].append(mk)

    def px(mk, t):
        h = hist.get(mk["id"])
        if not h or not h[0]:
            return None
        k = bisect.bisect_right(h[0], t) - 1
        return h[1][k] if k >= 0 and t - h[0][k] <= 12 * 3600 else None

    # which sports have a draw leg at all
    dsport = collections.Counter(r["sport"] for r in rows if r["kind"] == "draw" and r["h"] == "24h before start")
    L += ["## Which leagues have draw bets (24h-before snapshots)", "",
          ", ".join(f"{k} {n}" for k, n in dsport.most_common(40)), ""]
    drows = [r for r in rows if r["kind"] == "draw"]
    for r in drows:
        legs = [m for m in by_ev[r["ev"]] if m["id"] != r["mk"]["id"] and census.sports_kind(m) == "game winner"]
        ps = [p for p in (px(m, r["t"]) for m in legs) if p is not None]
        r["fav"] = max(ps) if len(ps) == 2 else None
        r["setsum"] = (r["p"] + sum(ps)) if len(ps) == 2 else None
    def tab(title, sel, keyf, slips=(0.0, 0.02, 0.04)):
        g = collections.defaultdict(list)
        for r in sel:
            k = keyf(r)
            if k is not None:
                g[k].append(r)
        out = [f"### {title}", "", "| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |",
               "|---|---|---|---|---|---|---|---|---|---|"]
        for k in sorted(g, key=str):
            rs = g[k]
            sc = {}
            for s in slips:
                items = []
                for r in rs:
                    c = min(0.99, r["p"] + s)
                    f = bot.taker_fee(1, c, r["fee"])
                    items.append((r["ev"], r["y"] - c - f, c + f))
                sc[s] = cluster_score(items)
            if not sc[0.02] or sc[0.02]["events"] < 25:
                continue
            ts = sorted(r["t"] for r in rs)
            mid = ts[len(ts) // 2]
            hv = []
            for part in ([r for r in rs if r["t"] < mid], [r for r in rs if r["t"] >= mid]):
                items = []
                for r in part:
                    c = min(0.99, r["p"] + 0.02)
                    f = bot.taker_fee(1, c, r["fee"])
                    items.append((r["ev"], r["y"] - c - f, c + f))
                s_ = cluster_score(items)
                hv.append(m100(s_["per100"]) if s_ else "")
            won = sum(1 for r in rs if r["y"] >= 0.5)
            out.append(f"| {k} | {sc[0.02]['events']} | {len(rs)} | {won} | {100 * sum(r['p'] for r in rs) / len(rs):.0f}c | "
                       f"{m100(sc[0.0]['per100'])} | {m100(sc[0.02]['per100'])} | {m100(sc[0.02]['lo'])} to {m100(sc[0.02]['hi'])} | "
                       f"{m100(sc[0.04]['per100'])} | {hv[0]} / {hv[1]} |")
        return out + [""]

    base = [r for r in drows if 0.15 <= r["p"] < 0.50]
    L += ["## Full-time draws at 15-50c, sliced", ""]
    L += tab("By hours before kickoff", base, lambda r: r["h"])
    d24 = [r for r in base if r["h"] == "24h before start"]
    L += tab("By draw price (24h before)", d24, lambda r: next((f"{a * 100:.0f}-{b * 100:.0f}c" for a, b in DRAW_BANDS if a <= r["p"] < b), None))
    L += tab("By league (24h before, leagues with 25+ games)", d24, lambda r: r["sport"])
    L += tab("By how even the match is: favorite's win price (24h before)", d24,
             lambda r: None if r["fav"] is None else "fav <45c (even)" if r["fav"] < 0.45 else "fav 45-60c" if r["fav"] < 0.60
             else "fav 60-75c" if r["fav"] < 0.75 else "fav 75c+ (lopsided)")
    L += tab("By what the 3 legs add up to (24h before)", d24,
             lambda r: None if r["setsum"] is None else "sum <99c" if r["setsum"] < 0.99 else "sum 99-101c" if r["setsum"] <= 1.01
             else "sum 101-104c" if r["setsum"] <= 1.04 else "sum 104c+")
    L += tab("By month (24h before)", d24, lambda r: dt.datetime.fromtimestamp(r["t"], dt.timezone.utc).strftime("%Y-%m"))
    L += tab("By kickoff weekday (24h before)", d24, lambda r: dt.datetime.fromtimestamp(r["mk"]["gst"], dt.timezone.utc).strftime("%a"))

    # the other two legs: if the draw is cheap, are the team legs dear? NO on the favorite = draw or upset
    legrows = []
    soccer_evs = {r["ev"] for r in drows}
    for r in rows:
        if r["kind"] != "game winner" or r["ev"] not in soccer_evs:
            continue
        sibs = [m for m in by_ev[r["ev"]] if m["id"] != r["mk"]["id"] and census.sports_kind(m) == "game winner"]
        op = px(sibs[0], r["t"]) if len(sibs) == 1 else None
        if op is None:
            continue
        r["role"] = "favorite" if r["p"] > op else "underdog"
        legrows.append(r)
    L += ["## The team legs of the same soccer games", "",
          "If draws are cheap, the two 'team X wins' legs should be a bit dear. Buying NO on a team = draw or the "
          "other team wins.", ""]
    for side_name, flip in (("YES on the team", False), ("NO on the team", True)):
        sel = []
        for r in legrows:
            q = 1 - r["p"] if flip else r["p"]
            y = 1 - r["y"] if flip else r["y"]
            if 0.10 <= q <= 0.90:
                rr = dict(r)
                rr["p"], rr["y"] = q, y
                sel.append(rr)
        L += tab(f"{side_name}, by role and hours before kickoff", sel, lambda r: f"{r['role']} | {r['h']}")

    # real buys for the best-looking slices
    L += ["## Real first buy before kickoff (trade tape)", "",
          "Decide at the snapshot, then fill at the first real buy of that side after it and before kickoff, "
          "+0c and +2c, fee included. 400-game sample per slice.", ""]
    print("\n".join(L))
    checks = [("draw 24h, league epl/lal/sea/bun/fl1/ucl (big leagues)", [r for r in d24 if r["sport"] in ("epl", "lal", "sea", "bun", "fl1", "ucl", "uel")]),
              ("draw 24h, other leagues", [r for r in d24 if r["sport"] not in ("epl", "lal", "sea", "bun", "fl1", "ucl", "uel")]),
              ("draw 24h, favorite 60c+", [r for r in d24 if (r["fav"] or 0) >= 0.60]),
              ("draw 24h, favorite under 60c", [r for r in d24 if r["fav"] is not None and r["fav"] < 0.60]),
              ("NO on favorite, 24h", [dict(r, p=1 - r["p"], y=1 - r["y"]) for r in legrows if r["role"] == "favorite" and r["h"] == "24h before start" and 0.10 <= 1 - r["p"] <= 0.90])]
    import io
    import contextlib
    for name, sel in checks:
        if len(sel) < 30:
            continue
        sig = [(r["mk"], 0 if not name.startswith("NO") else 1, r["p"], r["t"] - census.ENTRY_LAG, r["y"], r["mk"]["gst"]) for r in sel]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            census.tape_check(sig, 24 * 3600, int(os.environ.get("DIG_TAPE_CAP", "400")))
        L += [f"- **{name}** ({len(sel)} bets on the chart)", "", "```", buf.getvalue().rstrip(), "```", ""]
        print(L[-4], buf.getvalue())
    write("digs_draws.md", L)


# ================================================================ dig 2: Kalshi family census

KDIR = os.path.join(DIG, "kfam")
K_MK = os.path.join(KDIR, "markets.json.gz")
K_H = os.path.join(KDIR, "hist.json.gz")
K_START = os.environ.get("DIG_K_START", "2026-09-11")
K_END = "2026-11-10"                       # holdout day: nothing closing on/after it
K_EV_PER_SERIES_DAY = int(os.environ.get("DIG_K_EV", "2"))
K_MIN_VOL = float(os.environ.get("DIG_K_MINVOL", "50"))
K_BUDGET = float(os.environ.get("DIG_K_MIN", "230"))
K_HZ = (("72h", 72), ("24h", 24), ("6h", 6), ("1h", 1))
K_BANDS = ((0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98))
DONE_RX = re.compile(r"15M|CPI|PAYROLL|JOBLESS|CLAIMS|UNEMP|GDP|HIGH|LOWT|AAAGAS|GAS|APPROV|RCP|BTCD|ETHD", re.I)


def _rj(p, d=None):
    import backtest as bt
    return bt.rjson(p, d)


def _wj(p, o):
    import backtest as bt
    bt.wjson(p, o)


def _ts(x):
    d = bot.parse_iso(x) if isinstance(x, str) else None
    return int(d.timestamp()) if d else None


def kday(d):
    t0 = int(d.timestamp())
    rows, cur = [], None
    for _ in range(400):
        p = {"status": "settled", "min_close_ts": t0, "max_close_ts": t0 + DAY, "limit": 1000, "mve_filter": "exclude"}
        if cur:
            p["cursor"] = cur
        try:
            r = bot.http_json(f"{bot.KALSHI}/markets", p)
        except Exception as e:
            print(f"  kalshi {d:%Y-%m-%d} failed: {e}")
            break
        got = r.get("markets") or []
        rows += got
        cur = r.get("cursor")
        if not cur or not got:
            break
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for m in rows:
        tk = str(m.get("ticker") or "")
        res = str(m.get("result") or "").lower()
        if tk.startswith("KXMVE") or res not in ("yes", "no"):
            continue
        vol = bot.fnum(m.get("volume_fp") or m.get("volume"), 0)
        o, c = _ts(m.get("open_time")), _ts(m.get("close_time"))
        if not o or not c or c - o < 6 * 3600 or vol < K_MIN_VOL:
            continue
        ser = str(m.get("event_ticker") or "").split("-")[0]
        by[ser][m.get("event_ticker")].append({
            "t": tk, "s": ser, "ev": m.get("event_ticker"), "q": f"{m.get('title') or ''} | {m.get('yes_sub_title') or ''}"[:160],
            "open": o, "close": c, "res": res, "vol": vol})
    rng = random.Random(t0)
    out = []
    for ser, evs in by.items():
        keys = sorted(evs)
        rng.shuffle(keys)
        for ek in keys[:K_EV_PER_SERIES_DAY]:
            out.append(rng.choice(evs[ek]))
    return d, len(rows), len(by), out


def kcandles(m):
    a = max(m["open"], m["close"] - 80 * 3600)
    try:
        r = bot.http_json(f"{bot.KALSHI}/series/{m['s']}/markets/{m['t']}/candlesticks",
                          {"start_ts": a, "end_ts": m["close"], "period_interval": 60})
    except Exception:
        return m["t"], None
    out = []
    for c in r.get("candlesticks") or []:
        def px(block):
            v = (c.get(block) or {}).get("close_dollars")
            if v in (None, ""):
                v = (c.get(block) or {}).get("close")
                v = None if v in (None, "") else float(v) / 100
            return None if v is None else round(float(v), 4)
        out.append([int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask"), round(bot.fnum(c.get("volume_fp") or c.get("volume"), 0), 1)])
    return m["t"], out


def kfetch():
    os.makedirs(KDIR, exist_ok=True)
    have = _rj(K_MK, {"days": {}, "markets": {}}) or {"days": {}, "markets": {}}
    d = dt.datetime.fromisoformat(K_START).replace(tzinfo=dt.timezone.utc)
    end = dt.datetime.fromisoformat(K_END).replace(tzinfo=dt.timezone.utc)
    days = []
    while d < end:
        if d.strftime("%Y-%m-%d") not in have["days"]:
            days.append(d)
        d += dt.timedelta(days=1)
    print(f"kalshi family census: {len(days)} days to list, {len(have['markets'])} markets cached")
    with ThreadPoolExecutor(3) as ex:
        for d, n, nser, ms in ex.map(kday, days):
            have["days"][d.strftime("%Y-%m-%d")] = n
            for m in ms:
                have["markets"][m["t"]] = m
            print(f"  {d:%Y-%m-%d}: {n} settled, {nser} series with volume, kept {len(ms)} ({time.time() - T0:.0f}s)")
    _wj(K_MK, have)
    hist = _rj(K_H, {}) or {}
    todo = [m for m in have["markets"].values() if m["t"] not in hist]
    print(f"candles: {len(hist)} cached, {len(todo)} to fetch")
    with ThreadPoolExecutor(int(os.environ.get("DIG_K_THREADS", "6"))) as ex:
        for c in range(0, len(todo), 1500):
            if time.time() - T0 > K_BUDGET * 60:
                print("  time budget used up (run dig_kfetch again)")
                break
            for t, h in ex.map(kcandles, todo[c:c + 1500]):
                if h is not None:
                    hist[t] = h
            _wj(K_H, hist)
            print(f"  {min(c + 1500, len(todo))}/{len(todo)} ({time.time() - T0:.0f}s)")
    _wj(K_H, hist)


def kfee(price, n=10):
    return bot.kalshi_fee(n, price) / n


def krows(mk, hist):
    """One row per (market, horizon, side) at the real ask."""
    import launch
    rows = []
    for tk, m in mk.items():
        C = hist.get(tk)
        if not C:
            continue
        Ct = [c[0] for c in C]
        pay0 = 1.0 if m["res"] == "yes" else 0.0
        cat = launch.kcategory(m["s"], m["q"])
        for hn, hh in K_HZ:
            t = m["close"] - hh * 3600
            if t < m["open"] + 3600:
                continue
            k = bisect.bisect_right(Ct, t) - 1
            if k < 0 or t - Ct[k] > 3 * 3600:
                continue
            b, a = C[k][1], C[k][2]
            if b is None or a is None or not (0 < b < a < 1):
                continue
            spread = a - b
            vol = C[k][3] if len(C[k]) > 3 else None
            for side in (0, 1):
                q = a if side == 0 else 1 - b
                if not 0.02 <= q <= 0.98:
                    continue
                rows.append({"s": m["s"], "cat": cat, "ev": m["ev"], "h": hn, "side": side, "q": q,
                             "pay": pay0 if side == 0 else 1 - pay0, "t": t, "spread": spread, "close": m["close"],
                             "done": bool(DONE_RX.search(m["s"])), "title": m["q"],
                             "vol": vol, "age": t - Ct[k], "tk": tk})
    return rows


def kscore(rs, extra=0.0):
    items = []
    for r in rs:
        c = min(0.99, r["q"] + extra)
        f = kfee(c)
        items.append((r["ev"], r["pay"] - c - f, c + f))
    return cluster_score(items)


def kslices(rows, keyname, min_ev=40):
    """Every (group, horizon, side, band) slice: score at the ask, +1c, halves, vs twins (same horizon/side/band, all
    other groups)."""
    cell = collections.defaultdict(list)
    for r in rows:
        bi = next((i for i, (a, b) in enumerate(K_BANDS) if a <= r["q"] < b), None)
        if bi is None:
            continue
        cell[(r[keyname], r["h"], r["side"], bi)].append(r)
    base = collections.defaultdict(list)
    for (g, h, s, bi), rs in cell.items():
        base[(h, s, bi)] += rs
    ts = sorted(r["t"] for r in rows)
    mid = ts[len(ts) // 2] if ts else 0
    out = []
    for key, rs in cell.items():
        sc = kscore(rs)
        if not sc or sc["events"] < min_ev:
            continue
        sc1 = kscore(rs, 0.01)
        a = kscore([r for r in rs if r["t"] < mid])
        b = kscore([r for r in rs if r["t"] >= mid])
        others = [r for r in base[key[1:]] if r[keyname] != key[0]]
        tw = kscore(others) if len(others) > 30 else None
        flag = sc["lo"] > 0 and sc1 and sc1["per100"] > 0 and a and b and a["per100"] > 0 and b["per100"] > 0
        out.append({"key": key, "n": sc["events"], "bets": len(rs), "won": sum(1 for r in rs if r["pay"] >= 0.5),
                    "avgq": sum(r["q"] for r in rs) / len(rs), "sc": sc, "sc1": sc1, "a": a, "b": b, "tw": tw,
                    "spread": sum(r["spread"] for r in rs) / len(rs), "flag": bool(flag), "rows": rs})
    return out


def placebo_rows(rows, salt):
    """Same rows, but each event dropped into one of 40 fake 'series' at random (same size spread as real ones)."""
    out = []
    for r in rows:
        h = int(hashlib.md5((salt + r["ev"]).encode()).hexdigest()[:6], 16)
        rr = dict(r)
        rr["s"] = f"FAKE{h % 40}"
        out.append(rr)
    return out


def btts():
    """Cross-check of the Kalshi Argentina 'both teams to score' flag on Polymarket's own BTTS markets: YES and NO,
    by league and hours before kickoff, chart +2c + fee, held."""
    import census
    ms, hist, rows, kinds = census.sports_rows()
    rs = [r for r in rows if r["kind"] == "both teams score"]
    print(f"both-teams-score rows {len(rs):,}")
    L = ["# Both teams to score, Polymarket cross-check (digs.py btts)", "",
         "Kalshi's Argentina 'both teams to score' YES at 25-50c, 1h before close, won 28 of 42 (+$53 per $100). Does the "
         "same bet win on Polymarket? Chart price +2c + fee, held, in-sample games only.", "",
         "| group | side | games | won | avg price | per $100 at +2c | 90% band |", "|---|---|---|---|---|---|---|"]
    g = collections.defaultdict(list)
    for r in rs:
        for side in (0, 1):
            p_ = r["p"] if side == 0 else 1 - r["p"]
            y_ = r["y"] if side == 0 else 1 - r["y"]
            if not 0.25 <= p_ < 0.75:
                continue
            for key in ("all", r["sport"]):
                g[(key, r["h"], side)].append((r["ev"], p_, y_, r["fee"]))
    for k in sorted(g, key=lambda k: (k[0] != "all", k[0] != "arg", k)):
        it = g[k]
        if len(it) < 30:
            continue
        items = []
        for ev, p_, y_, fee in it:
            c = min(0.99, p_ + 0.02)
            f = bot.taker_fee(1, c, fee)
            items.append((ev, y_ - c - f, c + f))
        sc = cluster_score(items)
        won = sum(1 for x in it if x[2] >= 0.5)
        avg = sum(x[1] for x in it) / len(it)
        L.append(f"| {k[0]} {k[1]} | {'YES' if k[2] == 0 else 'NO'} | {sc['events']} | {won} | {avg * 100:.0f}c | "
                 f"{m100(sc['per100'])} | {m100(sc['lo'])} to {m100(sc['hi'])} |")
    txt = "\n".join(L) + "\n"
    os.makedirs("backtest", exist_ok=True)
    open("backtest/digs_btts.md", "w").write(txt)
    print(txt)


def ksane():
    """Is the Kalshi census data clean? Score at the MIDDLE of bid and ask (no fee): a fair, clean market should be
    near $0 there. Split by bid-ask gap, by whether anyone traded in that hour, and by how old the quote is."""
    mk = (_rj(K_MK, {}) or {}).get("markets", {})
    hist = _rj(K_H, {}) or {}
    rows = krows(mk, hist)

    def mid_score(rs):
        items = []
        for r in rs:
            m = (r["q"] + (r["q"] - r["spread"])) / 2  # mid seen from that side
            items.append((r["ev"], r["pay"] - m, m))
        return cluster_score(items)

    L = ["# Kalshi census sanity check (digs.py ksane)", "",
         "A clean, fair market loses about $0 per $100 at the middle of bid and ask. Big losses at the middle mean the "
         "quotes were stale or one-sided, not real prices.", "",
         "| group | events | bets | per $100 at the ask (+fee) | per $100 at the middle (no fee) |", "|---|---|---|---|---|"]

    def line(name, rs):
        a, m_ = kscore(rs), mid_score(rs)
        if a and m_:
            L.append(f"| {name} | {a['events']} | {len(rs)} | {m100(a['per100'])} | {m100(m_['per100'])} |")
    line("all", rows)
    for lo, hi in ((0, 0.021), (0.021, 0.051), (0.051, 0.15), (0.15, 1)):
        line(f"gap {lo * 100:.0f}-{hi * 100:.0f}c", [r for r in rows if lo <= r["spread"] < hi])
    line("someone traded that hour", [r for r in rows if (r.get("vol") or 0) > 0])
    line("nobody traded that hour", [r for r in rows if not (r.get("vol") or 0) > 0])
    line("traded that hour AND gap 0-2c", [r for r in rows if (r.get("vol") or 0) > 0 and r["spread"] < 0.021])
    for hn, _ in K_HZ:
        line(f"traded + gap 0-2c, {hn}", [r for r in rows if r["h"] == hn and (r.get("vol") or 0) > 0 and r["spread"] < 0.021])
    for bi, (a, b) in enumerate(K_BANDS):
        for side in (0, 1):
            line(f"traded + gap 0-2c, {a * 100:.0f}-{b * 100:.0f}c {'YES' if side == 0 else 'NO'}",
                 [r for r in rows if a <= r["q"] < b and r["side"] == side and (r.get("vol") or 0) > 0 and r["spread"] < 0.021])
    # examples: favorites 90-98c that lost
    bad = [r for r in rows if 0.90 <= r["q"] < 0.98 and r["pay"] == 0][:12]
    L += ["", "Examples: 90-98c buys that lost (quote age, gap, traded that hour, prices after)", ""]
    for r in bad:
        C = hist[r["tk"]]
        after = [f"{c[1]}/{c[2]}" for c in C if c[0] > r["t"]][:4]
        L.append(f"- {r['tk']} {r['h']} {'YES' if r['side'] == 0 else 'NO'} paid {r['q'] * 100:.0f}c, gap {r['spread'] * 100:.0f}c, "
                 f"age {r['age'] / 60:.0f} min, vol {r.get('vol')}, next bid/ask {after} | {r['title'][:70]}")
    txt = "\n".join(L) + "\n"
    os.makedirs("backtest", exist_ok=True)
    open("backtest/kfamily_sanity.md", "w").write(txt)
    print(txt)


def kfam():
    mk = (_rj(K_MK, {}) or {}).get("markets", {})
    hist = _rj(K_H, {}) or {}
    rows = krows(mk, hist)
    print(f"kalshi markets {len(mk):,}, with candles {sum(1 for t in mk if hist.get(t)):,}, rows {len(rows):,}")
    nser = len({r["s"] for r in rows})
    L = ["# Kalshi family census (digs.py kfam)", "",
         f"Generated {bot.iso(dt.datetime.now(dt.timezone.utc))}. Settled Kalshi markets closing {K_START} to 2026-11-09 "
         f"(volume {K_MIN_VOL:.0f}+ contracts; up to {K_EV_PER_SERIES_DAY} events per series per day, one market each). "
         f"{len(mk):,} markets, {nser:,} series, {len(rows):,} priced bets. Every bet is bought at the REAL top-of-book ask "
         "at that hour (YES ask, or 1 - YES bid for NO), plus Kalshi's taker fee (10 contracts), held to the result. "
         "'Per $100' = profit per $100 staked, grouped by event. Size at the ask is unknown, so '+1c' is the "
         "stress column. Families marked 'done' were already tested by other threads (crypto 15-min, econ data, "
         "weather highs, gas, approval polls).", ""]
    # overview by category
    L += ["## By kind of market (all bands, both sides)", "", "| kind | events | bets | per $100 at ask | 90% band | +1c |", "|---|---|---|---|---|---|"]
    bycat = collections.defaultdict(list)
    for r in rows:
        bycat[r["cat"]].append(r)
    for c, rs in sorted(bycat.items(), key=lambda kv: -len(kv[1])):
        s, s1 = kscore(rs), kscore(rs, 0.01)
        if s:
            L.append(f"| {c} | {s['events']} | {len(rs)} | {m100(s['per100'])} | {m100(s['lo'])} to {m100(s['hi'])} | {m100(s1['per100'])} |")
    L += ["", "## Long shots vs favorites (all Kalshi, at the ask)", "", "| price | hours before close | YES or NO | events | per $100 | 90% band |", "|---|---|---|---|---|---|"]
    for bi, (a, b) in enumerate(K_BANDS):
        for hn, _ in K_HZ:
            for side in (0, 1):
                rs = [r for r in rows if a <= r["q"] < b and r["h"] == hn and r["side"] == side]
                s = kscore(rs)
                if s and s["events"] >= 40:
                    L.append(f"| {a * 100:.0f}-{b * 100:.0f}c | {hn} | {'YES' if side == 0 else 'NO'} | {s['events']} | {m100(s['per100'])} | {m100(s['lo'])} to {m100(s['hi'])} |")
    # calendar on Kalshi
    L += ["", "## Calendar checks (all Kalshi, 24h before close, both sides, 10-90c)", "",
          "| group | events | per $100 | 90% band |", "|---|---|---|---|"]
    mid_rows = [r for r in rows if r["h"] == "24h" and 0.10 <= r["q"] < 0.90]
    for lab, f in (("closes on a weekend", lambda r: dt.datetime.fromtimestamp(r["close"], dt.timezone.utc).weekday() >= 5),
                   ("closes on a weekday", lambda r: dt.datetime.fromtimestamp(r["close"], dt.timezone.utc).weekday() < 5),
                   ("closes in the last 3 days of a month", lambda r: (dt.datetime.fromtimestamp(r["close"], dt.timezone.utc) + dt.timedelta(days=3)).month != dt.datetime.fromtimestamp(r["close"], dt.timezone.utc).month),
                   ("closes days 1-7 of a month", lambda r: dt.datetime.fromtimestamp(r["close"], dt.timezone.utc).day <= 7)):
        for side in (0, 1):
            s = kscore([r for r in mid_rows if f(r) and r["side"] == side])
            if s:
                L.append(f"| {lab}, {'YES' if side == 0 else 'NO'} | {s['events']} | {m100(s['per100'])} | {m100(s['lo'])} to {m100(s['hi'])} |")
    # slices
    res = {}
    for keyname, label in (("cat", "kind"), ("s", "series")):
        sl = kslices(rows, keyname)
        res[keyname] = sl
        flags = sorted([x for x in sl if x["flag"]], key=lambda x: -x["sc"]["lo"])
        L += ["", f"## Slices by {label}: {len(sl)} tested (40+ events each), {len(flags)} flagged", "",
              "Flag = 90% band above $0 at the ask, still ahead at +1c, and ahead in both halves (by time).", "",
              f"| {label} | hours before | side | price | events | bets (won) | avg price | avg gap bid-ask | per $100 at ask | 90% band | +1c | halves | other {label}s same price |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in flags[:40]:
            g, h, s, bi = x["key"]
            done = " (done)" if keyname == "s" and DONE_RX.search(g) else ""
            L.append(f"| {g}{done} | {h} | {'YES' if s == 0 else 'NO'} | {K_BANDS[bi][0] * 100:.0f}-{K_BANDS[bi][1] * 100:.0f}c | {x['n']} | "
                     f"{x['bets']} ({x['won']}) | {100 * x['avgq']:.0f}c | {100 * x['spread']:.1f}c | {m100(x['sc']['per100'])} | "
                     f"{m100(x['sc']['lo'])} to {m100(x['sc']['hi'])} | {m100(x['sc1']['per100'])} | {m100(x['a']['per100'])} / {m100(x['b']['per100'])} | "
                     f"{m100(x['tw']['per100']) if x['tw'] else ''} |")
        if keyname == "s":
            for x in flags[:12]:
                L += ["", f"Examples, {x['key'][0]} {x['key'][1]} {'YES' if x['key'][2] == 0 else 'NO'}:"]
                for r in random.Random(4).sample(x["rows"], min(4, len(x["rows"]))):
                    L.append(f"- {r['title'][:110]} | paid {100 * r['q']:.0f}c | {'won' if r['pay'] >= 0.5 else 'lost'}")
    # placebo: how many flags does pure chance give?
    pf = []
    for salt in ("a", "b", "c"):
        sl = kslices(placebo_rows(rows, salt), "s")
        pf.append((len(sl), sum(1 for x in sl if x["flag"])))
    real = res["s"]
    L += ["", "## Luck check", "",
          f"Real series slices: {len(real)} tested, {sum(1 for x in real if x['flag'])} flagged. "
          f"Same bets dropped into 40 random fake series, 3 times: " + ", ".join(f"{n} tested / {k} flagged" for n, k in pf) +
          ". Fake series are bigger than real ones, so compare the SHARE flagged.", ""]
    write("kfamily.md", L)


# ================================================================ dig 3+4: calendar + set-sum features on the idea machine

HOLIDAYS = ["2026-04-03", "2026-04-05", "2026-05-25", "2026-06-19", "2026-07-03", "2026-07-04", "2026-09-07",
            "2026-10-12", "2026-03-17"]
MINE = []


def _register():
    import ideas
    hol = [int(dt.datetime.fromisoformat(d).replace(tzinfo=dt.timezone.utc).timestamp()) for d in HOLIDAYS]

    def reg(name, story):
        MINE.append(name)
        return ideas.feature(name, story)

    @reg("calendar: ends at month end", "'by the end of the month' deadlines: people hold YES too long into the last days")
    def _(c):
        d = dt.datetime.fromtimestamp(c.mk["end"], dt.timezone.utc)
        return "last 3 days of a month" if (d + dt.timedelta(days=3)).month != d.month else "other days"

    @reg("calendar: holiday nearby", "around public holidays fewer people watch, so prices go stale")
    def _(c):
        near = any(abs(c.t - h) <= 2 * DAY for h in hol) or any(c.t <= h <= c.mk["end"] for h in hol)
        return "holiday before the end" if near else "no holiday"

    @reg("calendar: part of month", "new deposits at the start of a month chase long shots")
    def _(c):
        d = dt.datetime.fromtimestamp(c.t, dt.timezone.utc).day
        return "days 1-7" if d <= 7 else "days 8-23" if d <= 23 else "days 24-31"

    @reg("calendar: ends on a weekend", "markets ending on a Saturday/Sunday get checked by fewer people at the end")
    def _(c):
        return "ends Sat/Sun" if dt.datetime.fromtimestamp(c.mk["end"], dt.timezone.utc).weekday() >= 5 else "ends Mon-Fri"

    @reg("set sum: choices add up to", "when every choice in one event adds up to well over $1, each YES is overpriced")
    def _(c):
        sp = c.sib_prices()
        if len(sp) < 3:
            return None
        s = sum(p for _, p in sp)
        return "under 95c" if s < 0.95 else "95-105c" if s <= 1.05 else "105-120c" if s <= 1.20 else "over 120c"

    @reg("set sum: my share", "a choice whose price is far above its share of the set is the one people overbought")
    def _(c):
        sp = c.sib_prices()
        if len(sp) < 3:
            return None
        s = sum(p for _, p in sp)
        if s < 1.03:
            return None
        return "set over $1.03"


def run_ideas():
    import ideas
    _register()
    keep = set(MINE)
    ideas.FEATURES[:] = [f for f in ideas.FEATURES if f[0] in keep or f[0].startswith("PLACEBO")]
    print("features:", [f[0] for f in ideas.FEATURES])
    ideas.run(out_name="digs_ideas.md")


# ================================================================ selftest

def selftest():
    bad = 0
    # a fair world: price = true chance, scorer should show about -fee
    rng = random.Random(1)
    rows = []
    for i in range(4000):
        p = rng.uniform(0.1, 0.9)
        y = 1.0 if rng.random() < p else 0.0
        rows.append({"s": f"S{i % 20}", "cat": "x", "ev": f"e{i}", "h": "24h", "side": 0, "q": p, "pay": y, "t": i,
                     "spread": 0.01, "close": i, "done": False, "title": "t"})
    s = kscore(rows)
    ok = -6 < s["per100"] < 1
    bad += not ok
    print("fair world per $100", round(s["per100"], 2), "ok" if ok else "BAD")
    # planted edge in one series: S3 wins 15c more often
    for r in rows:
        if r["s"] == "S3":
            r["pay"] = 1.0 if rng.random() < min(1, r["q"] + 0.3) else 0.0
    sl = kslices(rows, "s", min_ev=30)
    fl = {x["key"][0] for x in sl if x["flag"]}
    ok = "S3" in fl and len(fl) <= 6   # ~1 in 15 fair slices flags by luck: that is why the report has a placebo count
    bad += not ok
    print("planted edge found:", sorted(fl), "ok" if ok else "BAD")
    pl = kslices(placebo_rows([dict(r, pay=(1.0 if rng.random() < r["q"] else 0.0)) for r in rows], "z"), "s", min_ev=30)
    nf = sum(1 for x in pl if x["flag"])
    print(f"placebo flags {nf}/{len(pl)}", "ok" if nf <= max(2, len(pl) // 10) else "BAD")
    bad += nf > max(2, len(pl) // 10)
    print("kfee 50c", kfee(0.5), "94c", kfee(0.94))
    print("selftest", "passed" if not bad else f"FAILED ({bad})")
    return not bad


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"draws": draws, "kfetch": kfetch, "kfam": kfam, "ksane": ksane, "btts": btts, "kall": lambda: (kfetch(), kfam()), "ideas": run_ideas,
     "selftest": selftest}[cmd]()
