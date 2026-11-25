#!/usr/bin/env python3
"""kc_maker_safe, but earlier and cheaper? (24 Nov 2026, Jan: "What about something like kalshi safe but earlier?
How far back can we push it ... maybe 85-95 cent range?" and "Test all ranges and timeliness").

PAPER ONLY. Reads cached public history and never trades.

The real Kalshi bot (kc_maker_safe_usd) bids one tick in front of the best bid on the winning side of a 15-minute
crypto window when that bid is 95c+, with 0.75-5.5 minutes left, and only when Binance (moved onto Kalshi's price)
sits 2.3+ "typical moves until the close" past the start price. This dig asks: what if it starts earlier (up to 14
minutes left) and at lower prices (80-95c)?

What is different from kc_maker_early (dumped 12 Nov, -$2.45 per $100 live): that track had NO cushion check at all
and left its bid resting until the close. Here every cell has the cushion check (several bars), and we also try two
ways to stop the bid being filled only when things turn bad: cancel after 1 minute, or cancel as soon as the cushion
falls under the bar at a minute end.

    python3 kearly.py run      # writes backtest/kearly.md (+ kearly.json)

Data (already in the shared price store, `python3 store.py pull bt_cache/kc bt_cache/ks bt_cache/kidx`):
  bt_cache/kc   78,000+ windows 17 Jul - 19 Nov 2026, the last 11 minutes of 1-minute candles (kcrypto.load_windows)
  bt_cache/ks   all 15 minutes of each window, 12 Sep - 9 Nov 2026 (kspeed.load_minutes), for 11-14 minutes left
  bt_cache/kidx Kalshi's own settle number, a value a minute (kdocs.load_kidx), for a second cushion check
Fills: our bid is one tick above the best bid (first in line), so it fills when a later trade in its lifetime prints
at or below our price (kcrypto "fair"); 'strict' needs a trade below it. Maker fee 0. Taker cells pay Kalshi's
fee rounded up to the cent on a $10 order.
"""
import datetime as dt
import json
import math
import os
import random
import sys
from collections import defaultdict

import bot
import kcrypto as kc

UTC = dt.timezone.utc
OUT = os.path.join(bot.ROOT, "backtest")
SPLIT = int(dt.datetime(2026, 10, 15, tzinfo=UTC).timestamp())   # find on windows before, check on windows after
BANDS = [(0.80, 0.85), (0.85, 0.90), (0.90, 0.93), (0.93, 0.95), (0.95, 0.97), (0.97, 0.99), (0.99, 1.0)]
BARS = [None, 1.5, 2.0, 2.3, 2.5, 3.0, 3.5, 4.0, 5.0]
LIFE = ("hold", "1m", "zcancel")
EPS = 1e-9


def fee10(p):
    """Kalshi taker fee on a $10 order at price p, per contract: ceil(0.07 x C x p x (1-p)) to the cent."""
    c = max(1, int(10 / p))
    return math.ceil(0.07 * c * p * (1 - p) * 100 - 1e-9) / 100 / c


def tick(p):
    return 0.001 if p >= 0.9 - EPS else 0.01


def prep(windows, kx, max_left):
    """Per window: {M: (side, bid, ask, zu, zk)} at each minute end with M minutes left, plus each minute's trade low
    per side. One pass so the grid is cheap."""
    rows = []
    for w in windows:
        mins = (kx.get(w["s"]) or ({}, {}))[0]
        lows = {}
        for t, r in w["c"].items():
            lows[t] = (kc.side_view(r, "yes")[2], kc.side_view(r, "no")[2])
        snap = {}
        for M in range(1, max_left + 1):
            t = w["close"] - 60 * M
            r = w["c"].get(t)
            if not r:
                continue
            side = kc.leader(r)
            if not side:
                continue
            bid, ask, _, _ = kc.side_view(r, side)
            if bid is None or ask is None:
                continue
            zu = kc.zscore_usd(w, t, M, side)
            zk = None
            if mins:
                try:
                    import kdocs
                    zk = kdocs.zk_minute(mins, w, t, M, side)
                except Exception:
                    zk = None
            # cushion for the same side at every later minute end (for zcancel)
            snap[M] = (side, bid, ask, zu, zk)
        rows.append({"tk": w["t"], "s": w["s"], "close": w["close"], "res": w["res"], "snap": snap, "lows": lows,
                     "w": w})
    return rows


def z_later(r, t, side):
    """Cushion of `side` at minute end t (minutes left from the close)."""
    M = (r["close"] - t) // 60
    if M < 1:
        return None
    return kc.zscore_usd(r["w"], t, M, side)


def calm_ok(w, t, side):
    """'Calm Kalshi' (found by looking, kearly_ta.md): this minute's contracts traded are under 1.32 times the
    window's average so far, and the winning side's bid rose less than 19c in the last 2 minutes."""
    r_now, r_old = w["c"].get(t), w["c"].get(t - 120)
    if r_now and r_old:
        a, b = kc.side_view(r_now, side)[0], kc.side_view(r_old, side)[0]
        if a is not None and b is not None and a - b >= 0.19:
            return False
    vols = [v[4] for k, v in w["c"].items() if k <= t and len(v) > 4 and v[4] is not None]
    if vols and sum(vols) > 0 and vols[-1] / (sum(vols) / len(vols)) >= 1.32:
        return False
    return True


def one_bet(r, M, band, bar, life, kind="improve", zsrc="zu", fill="fair", calm=False):
    """The bet the rule makes in window r at M minutes left, or None. Returns a dict with price, filled, won."""
    sn = r["snap"].get(M)
    if not sn:
        return None
    if calm and not calm_ok(r["w"], r["close"] - 60 * M, sn[0]):
        return None
    side, bid, ask, zu, zk = sn
    lo, hi = band
    z = zu if zsrc == "zu" else (zk if zsrc == "zk" else min(zu if zu is not None else -9, zk if zk is not None else -9))
    if bar is not None and (z is None or z < bar):
        return None
    t = r["close"] - 60 * M
    won = r["res"] == side
    if kind == "taker":
        if not (lo - EPS <= ask < hi - EPS) or ask >= 1 - EPS:
            return None
        return {"t": t, "ev": r["tk"], "s": r["s"], "price": ask, "fee": fee10(ask), "filled": True, "won": won, "M": M}
    if not (lo - EPS <= bid < hi - EPS):
        return None
    price = round(bid + tick(bid), 4)
    if price >= ask - EPS:
        return None   # no room in front: skip (joining the back of the line is a different, worse bet)
    end = r["close"] if life != "1m" else t + 60
    filled = False
    si = 0 if side == "yes" else 1
    tt = t + 60
    while tt <= end:
        lw = r["lows"].get(tt)
        if lw and lw[si] is not None and (lw[si] < price - EPS or (fill == "fair" and lw[si] <= price + EPS)):
            filled = True
            break
        if life == "zcancel" and bar is not None and tt < r["close"]:
            zz = z_later(r, tt, side)
            if zz is None or zz < bar:
                break    # cancelled at this minute end, before the next minute's trades
        tt += 60
    return {"t": t, "ev": r["tk"], "s": r["s"], "price": price, "fee": 0.0, "filled": filled, "won": won, "M": M}


def first_bet(r, Ms, band, bar, life, **kw):
    """The live bot's way: the first minute (earliest first) where the rule fits; one bid per window."""
    for M in sorted(Ms, reverse=True):
        b = one_bet(r, M, band, bar, life, **kw)
        if b:
            return b
    return None


def score(bets):
    f = [b for b in bets if b["filled"]]
    n = len(f)
    if not n:
        return {"signals": len(bets), "bets": 0}
    cost = sum(b["price"] + b["fee"] for b in f)
    pnl = [(1.0 if b["won"] else 0.0) - b["price"] - b["fee"] for b in f]
    lost = sum(1 for b in f if not b["won"])
    days = defaultdict(lambda: [0.0, 0.0])
    for b, p in zip(f, pnl):
        days[b["t"] // 86400][0] += p / (b["price"] + b["fee"]) * 10
        days[b["t"] // 86400][1] += 10
    dl = list(days.values())
    rng = random.Random(3)
    boots = []
    for _ in range(300):
        s = [dl[rng.randrange(len(dl))] for _ in dl]
        boots.append(sum(x[0] for x in s) / sum(x[1] for x in s) * 100)
    boots.sort()
    usd10 = sum(p / (b["price"] + b["fee"]) * 10 for b, p in zip(f, pnl))
    return {"signals": len(bets), "bets": n, "lost": lost, "per100": sum(pnl) / cost * 100, "usd10": usd10,
            "per_day4": usd10 * 0.4 / max(1, len(dl)), "days": len(dl), "lo": boots[15], "hi": boots[284],
            "avg_price": cost / n, "won_all": sum(1 for b in bets if b["won"]) / len(bets),
            "won_filled": 1 - lost / n}


def money(x):
    return f"{'-' if x < 0 else '+'}${abs(x):.2f}"


def cell(s):
    if not s.get("bets"):
        return "-"
    return f"{money(s['per100'])} ({s['bets']}, {s['lost']} lost)"


def split_score(bets):
    a = [b for b in bets if b["t"] < SPLIT]
    c = [b for b in bets if b["t"] >= SPLIT]
    return score(a), score(c), score(bets)


def run():
    import kdocs
    kx = kdocs.load_kidx()
    W = kc.load_windows()
    rows = prep(W, kx, 10)
    print(f"{len(rows)} windows prepared")
    res = {"grid": {}, "first": {}, "taker": {}, "zk": {}, "deep": {}}
    L = ["# kc_maker_safe, but earlier and at lower prices", "",
         f"Generated {bot.iso()}. Paper only. Code: `kearly.py`. {len(rows)} settled Kalshi 15-minute crypto windows "
         f"(7 coins), {dt.datetime.fromtimestamp(rows[0]['close'], UTC):%d %b} to "
         f"{dt.datetime.fromtimestamp(rows[-1]['close'], UTC):%d %b %Y}. Every number is P&L per $100 bid, "
         "with (bets, lost) after it. 'Find' = windows before 15 Oct, 'check' = 15 Oct to 19 Nov "
         "(only looked at after the settings were picked on 'find').", ""]

    # ---------- 1. the map: one fixed minute, every band x bar, rest to the close (fair fills), find period
    find = [r for r in rows if r["close"] < SPLIT]
    chk = [r for r in rows if r["close"] >= SPLIT]
    L += ["## 1. The map (find period): bid at one fixed minute, held to the close", "",
          "Rows = minutes left when we bid. Columns = the winning side's best bid then. Cushion bar 2.3 "
          "(the real bot's). Fills: a later trade at or below our bid.", "",
          "| Min left | " + " | ".join(f"{lo * 100:.0f}-{hi * 100:.0f}c" for lo, hi in BANDS) + " |",
          "|---|" + "---|" * len(BANDS)]
    for M in range(10, 0, -1):
        cells = []
        for band in BANDS:
            s = score([b for b in (one_bet(r, M, band, 2.3, "hold") for r in find) if b])
            res["grid"][f"m{M}_{band[0]:.2f}_z2.3_hold"] = s
            cells.append(cell(s))
        L.append(f"| {M} | " + " | ".join(cells) + " |")

    # ---------- 2. bars x bands at a few times, three bid lifetimes
    L += ["", "## 2. Does a bigger cushion or a shorter-lived bid save the early, cheaper bets? (find period)", "",
          "hold = bid rests to the close (kc_maker_early's way); 1m = cancelled after one minute; zcancel = cancelled "
          "at the first minute end where the cushion drops under the bar.", ""]
    for M in (10, 8, 6, 4):
        L += [f"### {M} minutes left", "", "| Band | Bar | hold | 1m | zcancel |", "|---|---|---|---|---|"]
        for band in BANDS[:6]:
            for bar in (None, 2.0, 2.3, 3.0, 4.0, 5.0):
                cs = []
                for life in LIFE:
                    if life == "zcancel" and bar is None:
                        cs.append("-")
                        continue
                    s = score([b for b in (one_bet(r, M, band, bar, life) for r in find) if b])
                    res["grid"][f"m{M}_{band[0]:.2f}_z{bar}_{life}"] = s
                    cs.append(cell(s))
                L.append(f"| {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {bar or 'none'} | " + " | ".join(cs) + " |")
        L.append("")

    # ---------- 3. adverse selection: won out of 100, all signals vs filled
    L += ["## 3. Why cheap early bids lose: who sells to you (find period, bar 2.3, held to the close)", "",
          "| Min left | Band | Won of 100, every signal | Won of 100, filled bids | Price paid |", "|---|---|---|---|---|"]
    for M in (10, 7, 4, 2):
        for band in BANDS[:6]:
            s = res["grid"].get(f"m{M}_{band[0]:.2f}_z2.3_hold") or score(
                [b for b in (one_bet(r, M, band, 2.3, "hold") for r in find) if b])
            if s.get("bets"):
                L.append(f"| {M} | {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {s['won_all'] * 100:.1f} | "
                         f"{s['won_filled'] * 100:.1f} | {s['avg_price'] * 100:.1f}c |")

    # ---------- 4. the live bot's way: first fitting minute in a time span
    spans = [(1, 5), (1, 7), (1, 10), (3, 7), (4, 8), (5, 10), (6, 10), (8, 10)]
    bands2 = [(0.80, 0.90), (0.85, 0.95), (0.90, 0.95), (0.90, 1.0), (0.95, 1.0)]
    L += ["", "## 4. Like the live bot: one bid per window, at the first minute in the span where it fits", "",
          "Find period, fair fills. The real bot today is roughly '1-5 min, 95-100c, bar 2.3, hold'.", "",
          "| Span (min left) | Band | Bar | hold | zcancel |", "|---|---|---|---|---|"]
    for a, b_ in spans:
        Ms = range(a, b_ + 1)
        for band in bands2:
            for bar in (2.3, 3.0, 4.0):
                cs = []
                for life in ("hold", "zcancel"):
                    s = score([x for x in (first_bet(r, Ms, band, bar, life) for r in find) if x])
                    res["first"][f"{a}-{b_}_{band[0]:.2f}-{band[1]:.2f}_z{bar}_{life}"] = s
                    cs.append(cell(s))
                L.append(f"| {a}-{b_} | {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {bar} | " + " | ".join(cs) + " |")

    # ---------- 5. taker: buy at the ask early (kspeed's 95c+ lean)
    L += ["", "## 5. Paying the asking price instead of waiting (find period, fee included)", "",
          "| Min left | Ask band | Bar | Result |", "|---|---|---|---|"]
    for M in (10, 8, 6, 4, 2):
        for band in [(0.80, 0.90), (0.90, 0.95), (0.95, 0.97), (0.97, 0.99)]:
            for bar in (None, 2.3, 3.0, 4.0):
                s = score([x for x in (one_bet(r, M, band, bar, "hold", kind="taker") for r in find) if x])
                res["taker"][f"m{M}_{band[0]:.2f}_z{bar}"] = s
                L.append(f"| {M} | {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {bar or 'none'} | {cell(s)} |")

    # ---------- 6. Kalshi's own number as the cushion (both checks)
    L += ["", "## 6. Cushion on Kalshi's own settle number too (find period, hold)", "",
          "zu = Binance moved onto Kalshi's price (live bot). zk = Kalshi's own 60-second average. both = both pass.", "",
          "| Min left | Band | Bar | zu | zk | both |", "|---|---|---|---|---|---|"]
    for M in (10, 7, 4):
        for band in [(0.85, 0.90), (0.90, 0.95), (0.95, 0.99)]:
            for bar in (2.3, 3.0):
                cs = []
                for zs in ("zu", "zk", "both"):
                    s = score([x for x in (one_bet(r, M, band, bar, "hold", zsrc=zs) for r in find) if x])
                    res["zk"][f"m{M}_{band[0]:.2f}_z{bar}_{zs}"] = s
                    cs.append(cell(s))
                L.append(f"| {M} | {band[0] * 100:.0f}-{band[1] * 100:.0f}c | {bar} | " + " | ".join(cs) + " |")

    # ---------- 7. pick on find, check on fresh windows
    cand = []
    for key, s in list(res["first"].items()) + [("grid:" + k, v) for k, v in res["grid"].items()] + \
            [("taker:" + k, v) for k, v in res["taker"].items()]:
        if s.get("bets", 0) >= 300 and s["lo"] > 0:
            cand.append((s["per_day4"], key, s))
    cand.sort(reverse=True)
    tries = len(res["grid"]) + len(res["first"]) + len(res["taker"]) + len(res["zk"])
    L += ["", f"## 7. The best settings from 'find' (300+ bets, low end of the luck range above $0), on fresh windows",
          "", f"{tries} settings were tried, so expect a few to look good by luck. 'Check' = 15 Oct-19 Nov, never used "
          "to pick. $ a day = at $4 bids like the real bot.", "",
          "| Setting | Find | Find $ a day | Check | Check $ a day |", "|---|---|---|---|---|"]
    picked = []
    for _, key, s in cand[:15]:
        bets_chk = bets_for(key, chk)
        c = score(bets_chk)
        res["deep"][key] = {"find": s, "check": c}
        picked.append((key, s, c))
        L.append(f"| {key} | {cell(s)} | {money(s['per_day4'])} | {cell(c)} | "
                 f"{money(c['per_day4']) if c.get('bets') else '-'} |")
    # the real bot's own settings as a yardstick, both periods
    base = "1-5_0.95-1.00_z2.3_hold"
    sb, cb = score(bets_for(base, find)), score(bets_for(base, chk))
    L += ["", f"Yardstick, today's rule ({base}): find {cell(sb)}, {money(sb['per_day4'])} a day; "
          f"check {cell(cb)}, {money(cb['per_day4'])} a day."]
    res["base"] = {"find": sb, "check": cb}
    os.makedirs(OUT, exist_ok=True)
    txt = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "kearly_tables.md"), "w") as fh:
        fh.write(txt)
    with open(os.path.join(OUT, "kearly.json"), "w") as fh:
        json.dump({"generated": bot.iso(), "tries": tries, "res": res}, fh, indent=0, default=str)
    print(txt)


def parse_key(key):
    """Rebuild a rule from a result key -> function(window) -> bet or None."""
    if key.startswith("grid:"):
        k = key[5:].split("_")
        M, lo, bar, life = int(k[0][1:]), float(k[1]), k[2][1:], k[3]
        bar = None if bar == "None" else float(bar)
        hi = dict(BANDS)[lo]
        return lambda r: one_bet(r, M, (lo, hi), bar, life)
    if key.startswith("taker:"):
        k = key[6:].split("_")
        M, lo, bar = int(k[0][1:]), float(k[1]), k[2][1:]
        bar = None if bar == "None" else float(bar)
        hi = {0.80: 0.90, 0.90: 0.95, 0.95: 0.97, 0.97: 0.99}[lo]
        return lambda r: one_bet(r, M, (lo, hi), bar, "hold", kind="taker")
    parts = key.split("_")
    span, band, bar, life = parts[:4]
    calm = len(parts) > 4 and parts[4] == "calm"
    a, b = (int(x) for x in span.split("-"))
    lo, hi = (float(x) for x in band.split("-"))
    return lambda r: first_bet(r, range(a, b + 1), (lo, hi), float(bar[1:]), life, calm=calm)


def bets_for(key, rows):
    fn = parse_key(key)
    return [x for x in (fn(r) for r in rows) if x]


# ================================================================ chart signals (Jan, 24 Nov: "try with real technical analysis on charts too")
def _closes(sp, t, n):
    """The last n Binance 1-minute closes up to minute end t (oldest first), or None if any is missing."""
    out = []
    for i in range(n - 1, -1, -1):
        v = sp.get(str(t - 60 * i))
        if v is None:
            return None
        out.append(v)
    return out


def _ema(xs, n):
    k = 2 / (n + 1)
    e = xs[0]
    for x in xs[1:]:
        e = x * k + e * (1 - k)
    return e


def chart(w, t, side, M):
    """Chart readings on Binance 1-minute closes at minute end t, turned toward our side (+ = agrees with us)."""
    sp = w["spot"]
    xs = _closes(sp, t, 240)
    if not xs:
        return None
    sgn = 1 if side == "yes" else -1
    px = xs[-1]
    rets = [math.log(b / a) for a, b in zip(xs[-61:-1], xs[-60:])]
    sd1 = math.sqrt(sum(r * r for r in rets) / len(rets)) or 1e-9
    rets4 = [math.log(b / a) for a, b in zip(xs[:-1], xs[1:])]
    sd4 = math.sqrt(sum(r * r for r in rets4) / len(rets4)) or 1e-9
    g = [max(0, b - a) for a, b in zip(xs[-15:-1], xs[-14:])]
    l = [max(0, a - b) for a, b in zip(xs[-15:-1], xs[-14:])]
    rsi = 100 - 100 / (1 + (sum(g) / (sum(l) or 1e-12)))
    e9, e21 = _ema(xs[-60:], 9), _ema(xs[-60:], 21)
    m20 = sum(xs[-20:]) / 20
    sd20 = math.sqrt(sum((x - m20) ** 2 for x in xs[-20:]) / 20) or 1e-9
    pb = (px - (m20 - 2 * sd20)) / (4 * sd20)
    macd_line = [_ema(xs[:i], 12) - _ema(xs[:i], 26) for i in range(len(xs) - 8, len(xs) + 1)]
    hist = macd_line[-1] - _ema(macd_line, 9)
    mom3 = math.log(px / xs[-4]) / (sd1 * math.sqrt(3))
    mom10 = math.log(px / xs[-11]) / (sd1 * math.sqrt(10))
    hi60, lo60 = max(xs[-60:]), min(xs[-60:])
    rng_pos = (px - lo60) / ((hi60 - lo60) or 1e-9)
    # Kalshi's own chart: leader bid now vs 2 minutes ago, and this minute's contracts traded vs the window's average
    r_now, r_old = w["c"].get(t), w["c"].get(t - 120)
    kmove = None
    if r_now and r_old:
        a, b = kc.side_view(r_now, side)[0], kc.side_view(r_old, side)[0]
        if a is not None and b is not None:
            kmove = a - b
    vols = [v[4] for k, v in w["c"].items() if k <= t and len(v) > 4 and v[4] is not None]
    kvol = (vols[-1] / (sum(vols) / len(vols))) if vols and sum(vols) > 0 else None
    return {"rsi": rsi if sgn > 0 else 100 - rsi,
            "ema": sgn * (e9 - e21) / (px * sd1),
            "bollinger": pb if sgn > 0 else 1 - pb,
            "macd": sgn * hist / (px * sd1),
            "mom3": sgn * mom3, "mom10": sgn * mom10,
            "range60": rng_pos if sgn > 0 else 1 - rng_pos,
            "volregime": sd1 / sd4,
            "kalshi_move": kmove, "kalshi_volume": kvol,
            "hour": (t // 3600) % 24}


def ta(Ms=range(10, 3, -1), band=(0.85, 0.97)):
    """One bid per window, at the first minute 10..4 left where the winning side's bid is 85-97c (no cushion bar),
    one tick in front, held to the close (fair fills). Then: which chart readings split winners from losers?
    Learned on 'find', checked on 'check'. Writes backtest/kearly_ta.md."""
    import kdocs
    kx = kdocs.load_kidx()
    W = kc.load_windows()
    rows = prep(W, kx, 10)
    # how many coins lead the same way at the same minute (a market-wide move?)
    lead = defaultdict(dict)
    for r in rows:
        for M, sn in r["snap"].items():
            lead[(r["close"], M)][r["s"]] = sn[0]
    sig = []
    for r in rows:
        b = first_bet(r, Ms, band, None, "hold")
        if not b or not b["filled"]:
            continue
        side = r["snap"][b["M"]][0]
        f = chart(r["w"], b["t"], side, b["M"])
        if not f:
            continue
        f["cushion"] = r["snap"][b["M"]][3]
        f["kalshi_cushion"] = r["snap"][b["M"]][4]
        others = [v for k, v in lead[(r["close"], b["M"])].items() if k != r["s"]]
        f["same_way"] = (sum(1 for v in others if v == side) / len(others)) if others else None
        b["f"] = f
        sig.append(b)
    find = [b for b in sig if b["t"] < SPLIT]
    chk = [b for b in sig if b["t"] >= SPLIT]
    L = ["# Chart signals on the earlier, cheaper bids", "",
         f"Generated {bot.iso()}. Code: `kearly.py ta`. One bid per window at the first minute with 10 to 4 minutes "
         f"left where the winning side's bid is 85-97c, one tick in front, no cushion bar, held to the close. "
         f"{len(find)} filled bids in 'find' (to 15 Oct), {len(chk)} in 'check'. Each reading is turned toward our "
         "side: high = the chart agrees with our bet. Rows = thirds of the find bids by that reading.", "",
         f"All find bids: {cell(score(find))}. All check bids: {cell(score(chk))}.", "",
         "| Reading | Low third | Middle third | High third | High third on check |", "|---|---|---|---|---|"]
    names = ["cushion", "kalshi_cushion", "rsi", "ema", "macd", "bollinger", "mom3", "mom10", "range60",
             "volregime", "kalshi_move", "kalshi_volume", "same_way", "hour"]
    cuts = {}
    for nm in names:
        xs = sorted(b["f"][nm] for b in find if b["f"].get(nm) is not None)
        if len(xs) < 30:
            continue
        q1, q2 = xs[len(xs) // 3], xs[2 * len(xs) // 3]
        cuts[nm] = (q1, q2)
        parts = [[b for b in find if b["f"].get(nm) is not None and b["f"][nm] < q1],
                 [b for b in find if b["f"].get(nm) is not None and q1 <= b["f"][nm] < q2],
                 [b for b in find if b["f"].get(nm) is not None and b["f"][nm] >= q2]]
        hc = [b for b in chk if b["f"].get(nm) is not None and b["f"][nm] >= q2]
        L.append(f"| {nm} (cuts {q1:.2f} / {q2:.2f}) | " + " | ".join(cell(score(p)) for p in parts) +
                 f" | {cell(score(hc))} |")
    # combos: cushion >= 1.5 (a soft bar) AND each reading in its best third
    L += ["", "## Soft cushion (1.5+) plus one chart reading in its top third", "",
          "| Filter | Find | Check |", "|---|---|---|"]
    soft_f = [b for b in find if (b["f"]["cushion"] or -9) >= 1.5]
    soft_c = [b for b in chk if (b["f"]["cushion"] or -9) >= 1.5]
    L.append(f"| cushion 1.5+ alone | {cell(score(soft_f))} | {cell(score(soft_c))} |")
    for nm, (q1, q2) in cuts.items():
        if nm in ("cushion", "hour"):
            continue
        a = [b for b in soft_f if b["f"].get(nm) is not None and b["f"][nm] >= q2]
        c = [b for b in soft_c if b["f"].get(nm) is not None and b["f"][nm] >= q2]
        L.append(f"| + {nm} top third | {cell(score(a))} | {cell(score(c))} |")
    # a small chart score: count of readings that agree (rsi>55, ema>0, macd>0, bollinger>0.5, mom3>0, mom10>0)
    def votes(f):
        return sum([f["rsi"] > 55, f["ema"] > 0, f["macd"] > 0, f["bollinger"] > 0.5, f["mom3"] > 0, f["mom10"] > 0])
    L += ["", "## Chart vote: how many of 6 classic readings agree with our side (RSI over 55, fast average above slow, "
          "MACD up, upper half of the Bollinger band, up over 3 min, up over 10 min)", "",
          "| Votes | Find | Check |", "|---|---|---|"]
    for v in range(7):
        L.append(f"| {v} | {cell(score([b for b in find if votes(b['f']) == v]))} | "
                 f"{cell(score([b for b in chk if votes(b['f']) == v]))} |")
    for bar in (1.0, 1.5, 2.0):
        a = [b for b in find if votes(b["f"]) >= 5 and (b["f"]["cushion"] or -9) >= bar]
        c = [b for b in chk if votes(b["f"]) >= 5 and (b["f"]["cushion"] or -9) >= bar]
        L.append(f"| 5+ votes and cushion {bar}+ | {cell(score(a))} | {cell(score(c))} |")
    txt = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "kearly_ta.md"), "w") as fh:
        fh.write(txt)
    print(txt)
    return sig


# ================================================================ real trade lists with sizes (probe ke_*)
TCACHE = os.path.join(bot.ROOT, "bt_cache", "ke")
TAPE_SEC = 11 * 60
_LOG = []


def say(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    _LOG.append(msg)


def save_log(name):
    os.makedirs(TCACHE, exist_ok=True)
    with open(os.path.join(TCACHE, name), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


def tape_one(m):
    """Every trade of the last 11 minutes of one window: [ts, yes_price, taker_yes, contracts], oldest first."""
    import kfast
    rows, cur = [], None
    t0, t1 = m["close"] - TAPE_SEC, m["close"]
    for _ in range(60):
        p = {"ticker": m["t"], "min_ts": int(t0), "max_ts": int(t1) + 1, "limit": 1000}
        if cur:
            p["cursor"] = cur
        try:
            res = kc.get("/markets/trades", p)
        except Exception as e:
            if "429" in str(e):
                import time
                time.sleep(3)
                continue
            return None
        rows += res.get("trades") or []
        cur = res.get("cursor")
        if not cur or not res.get("trades"):
            out = [r for r in (kfast.tape_row(t) for t in rows) if r and t0 - 1 <= r[0] <= t1 + 1]
            return sorted(out)
    return None


def tfetch(days=7):
    """Real trade lists (with sizes) of the last 11 minutes of every window closing in the last `days` days."""
    import time
    from concurrent.futures import ThreadPoolExecutor
    days = float(days)
    t_end = time.time()
    os.makedirs(TCACHE, exist_ok=True)
    for s in kc.SERIES:
        path = os.path.join(TCACHE, f"tape_{s}.json.gz")
        store = kc.rjson(path, {}) or {}
        ms = [m for m in kc.rjson(os.path.join(kc.CACHE, f"markets_{s}.json.gz"), [])
              if m["close"] >= t_end - days * 86400]
        todo = [m for m in ms if m["t"] not in store]
        t_s = time.time()
        say(f"{s}: {len(ms)} windows, {len(todo)} to fetch")
        for i in range(0, len(todo), 300):
            chunk = todo[i:i + 300]
            with ThreadPoolExecutor(kc.WORKERS) as ex:
                got = list(ex.map(tape_one, chunk))
            for m, g in zip(chunk, got):
                if g is not None:
                    store[m["t"]] = g
            kc.wjson(path, store)
            say(f"  {s} {i + len(chunk)}/{len(todo)} ({time.time() - t_s:.0f}s)")


def tape_fill(tape, t_place, t_end, side, price, contracts):
    """Contracts really sold to bids at or below our price after we placed it (we are one tick in front, so first
    in line at our price; anything sold below our price would have hit us first). A taker buying our side sells
    nothing to us."""
    got = 0.0
    for ts, yp, tky, n in tape:
        if ts <= t_place or ts > t_end:
            continue
        if (tky == 1) == (side == "yes"):
            continue
        px = yp if side == "yes" else 1 - yp
        if px <= price + EPS:
            got += n
            if got >= contracts:
                return float(contracts)
    return got


def sizecheck():
    """The best settings again, on windows we have real trade lists for: fills counted in real contracts at $4, $10,
    $25 and $50 bids, next to the candle model. Saved as bt_cache/ke/sizecheck.txt."""
    import kdocs
    kx = kdocs.load_kidx()
    tapes = {}
    for s in kc.SERIES:
        tapes.update(kc.rjson(os.path.join(TCACHE, f"tape_{s}.json.gz"), {}) or {})
    W = [w for w in kc.load_windows() if w["t"] in tapes]
    rows = prep(W, kx, 10)
    say(f"{len(rows)} windows with real trade lists, "
        f"{dt.datetime.fromtimestamp(rows[0]['close'], UTC):%d %b %H:%M} to "
        f"{dt.datetime.fromtimestamp(rows[-1]['close'], UTC):%d %b %H:%M} UTC")
    keys = ["1-5_0.95-1.00_z2.3_hold", "1-10_0.95-1.00_z2.3_hold", "1-10_0.90-1.00_z2.3_hold",
            "1-10_0.85-0.95_z2.3_hold", "4-8_0.90-1.00_z2.3_hold", "6-10_0.90-1.00_z2.3_hold",
            "5-10_0.85-0.95_z2.3_hold", "1-10_0.85-0.95_z3.0_hold", "1-10_0.90-1.00_z2.0_hold",
            "1-10_0.85-0.95_z2.0_hold", "4-10_0.85-0.97_z1.5_hold", "4-10_0.85-0.97_z1.5_hold_calm",
            "4-10_0.85-0.97_z2.0_hold_calm", "4-10_0.90-0.97_z2.0_hold", "1-10_0.90-1.00_z2.3_hold_calm"]
    say("| Setting | Candle model | $4 real | $10 real | $25 real | $50 real |")
    say("|---|---|---|---|---|---|")
    for key in keys:
        bets = bets_for(key, rows)
        cm = score(bets)
        cells = [cell(cm)]
        for usd in (4, 10, 25, 50):
            pnl = cost = 0.0
            n = lost = 0
            for b in bets:
                w = next(r for r in rows if r["tk"] == b["ev"])
                side = w["snap"][b["M"]][0]
                want = max(1, int(usd / b["price"]))
                got = tape_fill(tapes[b["ev"]], b["t"], w["close"], side, b["price"], want)
                if got <= 0:
                    continue
                n += 1
                lost += 0 if b["won"] else 1
                cost += got * b["price"]
                pnl += got * ((1.0 if b["won"] else 0.0) - b["price"])
            cells.append(f"{money(pnl / cost * 100) if cost else '-'} ({n}, {lost} lost, {money(pnl)})")
        say(f"| {key} | " + " | ".join(cells) + " |")
    save_log("sizecheck.txt")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "tfetch":
        tfetch(arg or 7)
    elif cmd == "sizecheck":
        sizecheck()
    elif cmd == "all":   # probe ke_all: refresh candles to today, fetch 7 days of real tapes, size check
        kc.fetch(131)
        tfetch(arg or 7)
        sizecheck()
    else:
        {"run": run, "ta": ta}[cmd]()
