#!/usr/bin/env python3
"""Calibration hunt (2026-11-09): are some KINDS of Polymarket markets priced wrong in a steady way?

PAPER ONLY. Reads the backtest cache (bt_cache/, filled by `backtest.py fetch`) plus an optional sample of tiny
markets, and never trades.

    python3 calib.py fetch_small   # sample of small markets ($1k-$20k volume), not in the main cache
    python3 calib.py run           # write backtest/calib.md
    python3 calib.py selftest      # offline check on made-up markets

The idea ("three lenses" list): edges survive where nobody looks or where people are bored or confused.
Each is checked the same way: take the price at a fixed time before the scheduled end, pretend we bought that side
for 1-5c worse than the history price plus the taker fee, hold to the result. Slices tested:
  - horizon: 1 day to 4 months before the end (do traders get bored and sell long-dated markets cheap?)
  - topic, incl. "will X say Y" mention markets, economics data, entertainment scores, elections
  - market size ($1k-$20k tiny markets vs big ones)
  - weekend vs weekday prices (supermarket closing time)

How it stays honest
- Only prices up to the snapshot moment; the market had to be open then (not closed early).
- Results are grouped by EVENT, because 20 "will Trump say X" markets about one speech are one bet, not 20.
  The range is a 90% band from event-clustered errors.
- Many slices are tested at once, so a few will look good by luck. A slice only counts if its 90% band is above 0
  at +2c, both halves of the period are ahead, and it has 30+ events.
- History has no order book. Tiny markets can have asks many cents above the history price: see the +5c column.
"""
import bisect
import datetime as dt
import math
import os
import random
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot

CACHE, OUT = bt.CACHE, bt.OUT
DAY = 86400
HORIZONS = (1, 3, 7, 14, 30, 60, 120)
BANDS = ((0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98))
SLIPS = (0.01, 0.02, 0.03, 0.05)

TOPICS = (
    ("mentions", (r"\bsay\b", r"\bsays\b", r"\bmention", r"\bsaid\b", r"\bsay \"", r"\bwill .* post\b")),
    ("weather", (r"temperature", r"\brain\b", r"\bsnow", r"hurricane", r"\bstorm\b")),
    ("crypto price", (r"bitcoin", r"ethereum", r"solana", r"\bxrp\b", r"\bbtc\b", r"\beth\b", r"dogecoin")),
    ("post counts", (r"tweets", r" posts ", r"# of ")),
    ("economics", (r"\bcpi\b", r"inflation", r"\bfed\b", r"interest rate", r"unemployment", r"jobs report", r"\bgdp\b",
                   r"payroll", r"rate cut", r"bps", r"recession", r"jobless")),
    ("entertainment", (r"box office", r"opening weekend", r"rotten tomatoes", r"spotify", r"billboard", r"\boscar",
                       r"grammy", r"emmy", r"netflix", r"top song", r"#1 song", r"album", r"\bmovie\b", r"imdb")),
    ("apps/tech", (r"app store", r"\bapp\b", r"openai", r"\bgpt", r"gemini", r"\bai model", r"apple", r"google",
                   r"tesla", r"nvidia", r"launch", r"release")),
    ("stocks", (r"\bs&p\b", r"nasdaq", r"\bspx\b", r"\bdow\b", r"close above", r"stock", r"\bshares\b", r"market cap",
                r"earnings")),
    ("elections", (r"election", r"\bwin the\b.*(primary|seat|race|mayor|governor|senate|president)", r"nominee",
                   r"\bvote", r"\bpoll", r"\bparty\b", r"prime minister", r"\bmayor\b")),
    ("geopolitics", (r"ceasefire", r"invade", r"\bwar\b", r"strike", r"\bnato\b", r"sanction", r"\btroops", r"missile",
                     r"\bpeace\b", r"military", r"\bnuclear")),
    ("people/legal", (r"indicted", r"arrest", r"convicted", r"sentenced", r"\btrial\b", r"supreme court", r"\bcourt\b",
                      r"pardon", r"resign", r"fired", r"out as", r"leave office")),
)
_TOPIC_RE = [(name, re.compile("|".join(words))) for name, words in TOPICS]


def topic(q):
    t = q.lower()
    for name, rx in _TOPIC_RE:
        if rx.search(t):
            return name
    return "other"


def size_tier(vol):
    for lim, name in ((20e3, "tiny ($1k-20k)"), (50e3, "small ($20k-50k)"), (250e3, "mid ($50k-250k)"),
                      (1e6, "big ($250k-1M)")):
        if vol < lim:
            return name
    return "huge (>$1M)"


def outcome0(mk):
    """1 or 0 for outcome 0, or None when not cleanly settled."""
    p = bt.payout(mk, 0)
    if p is None or 0.01 < p < 0.99:
        return None
    return 1 if p >= 0.5 else 0


# ================================================================ small-market sample

def fetch_small(days_step=3, per_day=150, vmin=1000, vmax=20000):
    """A sample of finished tiny markets (the main cache only keeps volume > $20k). History is 12-hourly only."""
    path_m = os.path.join(CACHE, "small_markets.json.gz")
    path_h = os.path.join(CACHE, "small_hist.json.gz")
    have = bt.rjson(path_m, {}) or {}
    hist = bt.rjson(path_h, {}) or {}
    start = dt.datetime.fromisoformat(bt.START).replace(tzinfo=bt.UTC)
    end = bot.now() - dt.timedelta(days=2)
    rng = random.Random(7)
    days, d = [], start
    while d < end:
        days.append(d)
        d += dt.timedelta(days=days_step)

    def one_day(d):
        out, cur = [], None
        for _ in range(20):
            p = {"closed": "true", "limit": 500, "end_date_min": bot.iso(d), "end_date_max": bot.iso(d + dt.timedelta(days=1)),
                 "volume_num_min": vmin, "volume_num_max": vmax}
            if cur:
                p["after_cursor"] = cur
            try:
                res = bot.http_json(f"{bt.G}/markets/keyset", p)
            except Exception as e:
                print(f"  {d:%Y-%m-%d} failed: {e}")
                break
            rows = [m for m in bot.envelope_rows(res, "markets", "data") if isinstance(m, dict)]
            out += rows
            cur = res.get("next_cursor") if isinstance(res, dict) else None
            if not cur or not rows:
                break
        keep = []
        for m in out:
            s = bt.slim_market(m)
            if len(s["toks"]) == 2 and len(s["final"]) == 2 and s["end"] and not s["sports"] and vmin <= s["vol"] < vmax:
                keep.append(s)
        rng2 = random.Random(d.toordinal())
        return d, (rng2.sample(keep, per_day) if len(keep) > per_day else keep), len(out)

    t0 = time.time()
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for d, rows, n in ex.map(one_day, days):
            for s in rows:
                have[s["id"]] = s
            print(f"  {d:%Y-%m-%d}: {n} rows read, {len(rows)} kept")
    vals = [v for v in have.values() if v.get("vmax_check", True)]
    # out-of-range volumes would mean the API ignored volume_num_max: say so loudly
    big = sum(1 for v in vals if v["vol"] >= vmax)
    print(f"small markets: {len(have)} cached ({big} with volume >= ${vmax:,.0f}, should be 0) in {time.time() - t0:.0f}s")
    bt.wjson(path_m, have)

    def hist_one(mk):
        try:
            res = bot.http_json(f"{bt.C}/prices-history", {"market": mk["toks"][0], "interval": "max", "fidelity": 720})
            pts = bt.hist_points(res)
        except Exception as e:
            return mk["id"], None
        return mk["id"], bt.squeeze(pts, 0)

    todo = [m for m in have.values() if m["id"] not in hist]
    print(f"small history: {len(todo)} to fetch")
    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for c in range(0, len(todo), 2000):
            for mid, h in ex.map(hist_one, todo[c:c + 2000]):
                if h is not None:
                    hist[mid] = h
            print(f"  {min(c + 2000, len(todo))}/{len(todo)} ({time.time() - t0:.0f}s)")
            bt.wjson(path_h, hist)
    bt.wjson(path_h, hist)
    rng.random()


# ================================================================ snapshots

def snapshots(markets, hist, horizons=HORIZONS):
    """One row per (market, horizon): the outcome-0 price at end - h days, if the market was open then."""
    rows = []
    for mk in markets.values():
        y = outcome0(mk)
        h = hist.get(mk["id"])
        if y is None or not h or not h[0] or not mk.get("end"):
            continue
        T, P = h
        first = T[0]
        for hz in horizons:
            t = mk["end"] - hz * DAY
            if t < first + DAY or (mk.get("start") and t < mk["start"]):
                continue
            if mk.get("closed_t") and t > mk["closed_t"] - 6 * 3600:
                continue  # already settled (or about to): that is endgame, tested elsewhere
            i = bisect.bisect_right(T, t) - 1
            if i < 0 or t - T[i] > 3 * DAY:
                continue  # no recent price point: no trading, can't trust the number
            p = P[i]
            if not 0.02 <= p <= 0.98:
                continue
            rows.append({"mid": mk["id"], "ev": mk.get("ev") or mk["id"], "h": hz, "p": p, "y": y, "fee": mk.get("fee", 0),
                         "topic": topic(mk["q"]), "size": size_tier(mk.get("vol") or 0), "t": t, "q": mk["q"],
                         "wkend": bt.utc(t).weekday() >= 5})
    return rows


def weekpoints(markets, hist, max_days=60):
    """Every 12-hourly history point in the last max_days of a market's life (open at the time), with its weekday."""
    rows = []
    for mk in markets.values():
        y = outcome0(mk)
        h = hist.get(mk["id"])
        if y is None or not h or not h[0] or not mk.get("end"):
            continue
        last_t = min(mk["end"], mk.get("closed_t") or mk["end"]) - DAY
        lo = mk["end"] - max_days * DAY
        T, P = h
        k = 0
        t = max(T[0] + DAY, lo)
        t -= t % (12 * 3600)
        while t < last_t:
            i = bisect.bisect_right(T, t) - 1
            if i >= 0 and t - T[i] <= 3 * DAY and 0.02 <= P[i] <= 0.98:
                rows.append({"mid": mk["id"], "ev": mk.get("ev") or mk["id"], "p": P[i], "y": y, "fee": mk.get("fee", 0),
                             "t": t, "wkend": bt.utc(t).weekday() >= 5, "topic": topic(mk["q"]),
                             "size": size_tier(mk.get("vol") or 0)})
            t += 12 * 3600
            k += 1
    return rows


# ================================================================ scoring

def side_rows(rows, band, side):
    """Rows where we buy `side` ('yes' = outcome 0, 'no' = outcome 1, 'cheap', 'dear') and its price is in band."""
    lo, hi = band
    out = []
    for r in rows:
        for s, q, pay in (("yes", r["p"], r["y"]), ("no", 1 - r["p"], 1 - r["y"])):
            if side in ("cheap", "dear"):
                if (side == "cheap") != (q < 0.5):
                    continue
            elif s != side:
                continue
            if lo <= q < hi:
                out.append((r, q, pay))
    return out


def score(trades, slip):
    """Profit per $100 staked, its 90% band (clustered by event), events, bets, wins."""
    if not trades:
        return None
    by_ev = defaultdict(lambda: [0.0, 0.0])
    wins = 0
    for r, q, pay in trades:
        c = min(0.99, q + slip)
        f = bot.taker_fee(1, c, r["fee"])
        e = by_ev[r["ev"]]
        e[0] += pay - c - f
        e[1] += c + f
        wins += pay >= 0.5
    P = sum(v[0] for v in by_ev.values())
    S = sum(v[1] for v in by_ev.values())
    if S <= 0:
        return None
    rate = P / S
    n = len(by_ev)
    var = sum((v[0] - rate * v[1]) ** 2 for v in by_ev.values()) / (S * S) * (n / max(1, n - 1))
    se = math.sqrt(var)
    return {"per100": 100 * rate, "lo": 100 * (rate - 1.645 * se), "hi": 100 * (rate + 1.645 * se), "events": n,
            "bets": len(trades), "wins": wins, "avgq": sum(q for _, q, _ in trades) / len(trades)}


def halves(trades, slip):
    if len(trades) < 4:
        return None, None
    ts_sorted = sorted(r["t"] for r, _, _ in trades)
    mid = ts_sorted[len(ts_sorted) // 2]
    a = score([x for x in trades if x[0]["t"] < mid], slip)
    b = score([x for x in trades if x[0]["t"] >= mid], slip)
    return (a or {}).get("per100"), (b or {}).get("per100")


def m(x):
    return "" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.0f}"


HEAD = ["| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |",
        "|---|---|---|---|---|---|---|---|---|---|"]
FLAGS = []


def line(label, trades, flag_name=None):
    s = {sl: score(trades, sl) for sl in SLIPS}
    if not s[0.02]:
        return f"| {label} | 0 | | | | | | | | |"
    a, b = halves(trades, 0.02)
    s2 = s[0.02]
    good = s2["lo"] > 0 and s2["events"] >= 30 and (a or 0) > 0 and (b or 0) > 0
    if good and flag_name:
        FLAGS.append(f"{flag_name}: {m(s2['per100'])} per $100 at +2c, band {m(s2['lo'])} to {m(s2['hi'])}, "
                     f"{s2['events']} events, halves {m(a)} / {m(b)}")
    star = " **<-**" if good else ""
    return (f"| {label}{star} | {s2['events']} | {s2['bets']} ({s2['wins']}) | {s2['avgq'] * 100:.0f}c | {m(s[0.01]['per100'])} | "
            f"{m(s2['per100'])} | {m(s2['lo'])} to {m(s2['hi'])} | {m(s[0.03]['per100'])} | {m(s[0.05]['per100'])} | {m(a)} / {m(b)} |")


def bandname(b):
    return f"{b[0] * 100:.0f}-{b[1] * 100:.0f}c"


def report(rows, wrows, n_markets, n_small):
    FLAGS.clear()
    L = ["# Calibration hunt: are some kinds of markets priced wrong?", "",
         f"Generated {bot.iso(bot.now())}. {n_markets:,} finished binary non-sports Polymarket markets since {bt.START} "
         f"(of them {n_small:,} tiny ones from a sample), {len(rows):,} price snapshots. Paper only.", "",
         "How to read: each row buys one side at the history price plus 1-5c (no order book in history) plus the taker "
         "fee, holds to the result. Profit is per $100 staked. Events = separate events (markets of one event count as "
         "one). The 90% band is how far luck could move it. **<-** marks a slice whose band at +2c is above $0, with "
         "30+ events and both halves ahead. Dozens of slices are tested, so expect one or two false alarms.", ""]

    L += ["## 1. Price x time before end (all markets)", "", "Which side is bought: the side whose price is in the band.", ""]
    for hz in HORIZONS:
        L += [f"### {hz} day{'s' if hz > 1 else ''} before the end", ""] + HEAD
        sub = [r for r in rows if r["h"] == hz]
        for b in BANDS:
            L.append(line(bandname(b), side_rows(sub, b, "any_side") if False else
                          side_rows(sub, b, "cheap" if b[1] <= 0.5 else "dear"), f"all, {hz}d, {bandname(b)}"))
        L.append("")

    long_rows = [r for r in rows if r["h"] >= 30]
    short_rows = [r for r in rows if r["h"] <= 7]
    for title, sub, tag in (("## 2. Topics, long-dated (30+ days before the end)", long_rows, "30d+"),
                            ("## 3. Topics, short-dated (1-7 days before the end)", short_rows, "1-7d")):
        L += [title, ""]
        for b in ((0.02, 0.10), (0.10, 0.25), (0.75, 0.90), (0.90, 0.98)):
            side = "cheap" if b[1] <= 0.5 else "dear"
            L += [f"### Buying the {'long shot' if side == 'cheap' else 'favorite'} at {bandname(b)}", ""] + HEAD
            for tp in [n for n, _ in TOPICS] + ["other"]:
                L.append(line(tp, side_rows([r for r in sub if r["topic"] == tp], b, side), f"{tp}, {tag}, {bandname(b)}"))
            L.append("")

    L += ["## 4. Market size (all horizons)", ""]
    sizes = ["tiny ($1k-20k)", "small ($20k-50k)", "mid ($50k-250k)", "big ($250k-1M)", "huge (>$1M)"]
    for b in ((0.02, 0.10), (0.10, 0.25), (0.75, 0.90), (0.90, 0.98)):
        side = "cheap" if b[1] <= 0.5 else "dear"
        L += [f"### Buying the {'long shot' if side == 'cheap' else 'favorite'} at {bandname(b)}", ""] + HEAD
        for sz in sizes:
            L.append(line(sz, side_rows([r for r in rows if r["size"] == sz], b, side), f"{sz}, {bandname(b)}"))
        L.append("")

    L += ["## 5. Weekend vs weekday (every 12h point in the last 60 days of each market)", "",
          "Same market, same rule, only the day of the week differs. If weekend prices were sloppier, the weekend rows "
          "would beat the weekday rows.", ""]
    for b in BANDS:
        side = "cheap" if b[1] <= 0.5 else "dear"
        L += [f"### {'Long shot' if side == 'cheap' else 'Favorite'} at {bandname(b)}", ""] + HEAD
        for lab, wk in (("weekday", False), ("weekend", True)):
            L.append(line(lab, side_rows([r for r in wrows if r["wkend"] == wk], b, side), f"{lab}, {bandname(b)}"))
        L.append("")

    L += ["## 6. 'Will X say Y' mention markets, every horizon", ""]
    men = [r for r in rows if r["topic"] == "mentions"]
    L += HEAD
    for b in BANDS:
        side = "cheap" if b[1] <= 0.5 else "dear"
        L.append(line(f"{'long shot' if side == 'cheap' else 'favorite'} {bandname(b)}", side_rows(men, b, side),
                      f"mentions all horizons, {bandname(b)}"))
        L.append(line(f"  ...buy YES {bandname(b)}", side_rows(men, b, "yes"), f"mentions YES, {bandname(b)}"))
        L.append(line(f"  ...buy NO {bandname(b)}", side_rows(men, b, "no"), f"mentions NO, {bandname(b)}"))
    rng = random.Random(5)
    L += ["", "Sample of mention questions (to check the word filter):", ""]
    qs = sorted({r["q"] for r in men})
    L += [f"- {q[:110]}" for q in rng.sample(qs, min(12, len(qs)))]

    L += ["", "## Slices that passed the bar", ""]
    L += [f"- {f}" for f in FLAGS] or ["- none"]
    n_cells = sum(1 for x in L if x.startswith("| ") and not x.startswith("| Slice") and not x.startswith("|---"))
    L += ["", f"{n_cells} slices were tested. At a 90% band, about {n_cells // 20} could pass by luck alone (one side "
          "of the band), so a pass is a lead to paper-test, not proof."]
    return "\n".join(L) + "\n"


def run():
    markets = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}).get("markets", {})
    hist = bt.rjson(os.path.join(CACHE, "hist.json.gz"), {})
    small = bt.rjson(os.path.join(CACHE, "small_markets.json.gz"), {}) or {}
    shist = bt.rjson(os.path.join(CACHE, "small_hist.json.gz"), {}) or {}
    small = {k: v for k, v in small.items() if k not in markets}
    allm = dict(markets)
    allm.update(small)
    allh = dict(hist)
    allh.update(shist)
    print(f"markets {len(markets)}, small {len(small)}")
    rows = snapshots(allm, allh)
    wrows = weekpoints(allm, allh)
    print(f"snapshots {len(rows)}, week points {len(wrows)}")
    txt = report(rows, wrows, len(allm), len(small))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "calib.md"), "w") as fh:
        fh.write(txt)
    print(txt)


def selftest():
    """Made-up markets where long shots at 5c win 20% of the time: the 2-10c long-shot rows must show a profit."""
    rng = random.Random(1)
    markets, hist = {}, {}
    t_end0 = bot.parse_iso("2026-06-01T00:00:00Z").timestamp()
    for i in range(3000):
        end = int(t_end0 + i * 3600)
        p = 0.05 if i % 2 else 0.4
        y = 1 if rng.random() < (0.20 if p == 0.05 else 0.4) else 0
        mk = {"id": str(i), "q": "Will Trump say \"tariff\" this week?" if i % 3 == 0 else "Will it rain?",
              "outs": ["Yes", "No"], "toks": [f"a{i}", f"b{i}"], "end": end, "start": end - 200 * DAY, "closed": True,
              "closed_t": end + 3600, "final": [float(y), float(1 - y)], "uma": "resolved", "vol": 30000 if i % 4 else 5000,
              "fee": 0.0, "sports": False, "slug": f"m{i}", "ev": f"e{i}", "ev_slug": ""}
        markets[mk["id"]] = mk
        hist[mk["id"]] = [[end - 190 * DAY + k * 12 * 3600 for k in range(380)], [p] * 380]
    rows = snapshots(markets, hist)
    tr = side_rows(rows, (0.02, 0.10), "cheap")
    s = score(tr, 0.01)
    assert s and s["per100"] > 100, s
    tr2 = side_rows(rows, (0.25, 0.50), "cheap")
    s2 = score(tr2, 0.0)
    assert s2 and abs(s2["per100"]) < 15, s2
    assert topic("Will Trump say \"crypto\" during the rally?") == "mentions"
    assert topic("Highest temperature in NYC on June 3?") == "weather"
    txt = report(rows, weekpoints(markets, hist), len(markets), 0)
    assert "**<-**" in txt
    print("calib selftest ok:", round(s["per100"]), "per $100 on 5c long shots that win 20%")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"fetch_small": fetch_small, "run": run, "selftest": selftest}[cmd]()
