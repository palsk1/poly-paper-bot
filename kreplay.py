#!/usr/bin/env python3
"""Replay the Kalshi 15-minute crypto maker tracks on the RECORDED order books and trade tape (2026-11-10).

PAPER ONLY, research only: reads public data, never trades, never touches state/ (except reading it).

Why: live, all three kc_maker tracks lost about twice as often as the kcrypto.py backtest said. Is the backtest's
fill model (1-minute candles, "fair") too kind, or were the first live days just unlucky? Three looks:

  A. The backtest itself (kcrypto candles + Kalshi results) on the days we recorded and on the live days only.
     If the backtest also loses there, the live losses are the market, not the fill model.
  B. The same signals re-filled from the recorder's real books + full trade tape (recorder.py releases), with the
     live bot's own fill rule (bot.kmaker_fill: traded through our price = full fill, else only sells at our price
     after the queue ahead of us). Cross-tab: candle fill vs tape fill, and who wins.
  C. The live tracks' own orders (state/events.jsonl) re-scored with the candle model: does the backtest fill the
     orders that lost live, and does it skip orders live filled?

    python3 kreplay.py run [days]     # fetch recent kcrypto windows (default 3 days) + recordings, write backtest/kreplay.md
    From GitHub: probe workflow, what = btkreplay (keeps bt_cache).
"""
import datetime as dt
import gzip
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict

import bot
import kcrypto as kc

ROOT = bot.ROOT
REC = os.path.join(ROOT, "bt_cache", "rec")
OUT = os.path.join(ROOT, "backtest")
REPO = "palsk1/poly-paper-bot"
SERIES = tuple(kc.SERIES)
EPS = 1e-9
# the three live tracks, as backtest variants: (name, kind, level, minutes left at placement, min z)
VARIANTS = [("kc_maker_safe", "improve", 0.95, 3, 2.0), ("kc_maker", "improve", 0.95, 3, None),
            ("kc_maker_early", "improve", 0.90, 8, None)]


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh_json(url):
    h = {"User-Agent": "paper-research", "Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        h["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
        return json.loads(r.read().decode())


def fetch_recordings():
    """Download every recorder hour file (releases data-YYYYMMDD) into bt_cache/rec/ (skips files already there)."""
    os.makedirs(REC, exist_ok=True)
    try:
        rels = gh_json(f"https://api.github.com/repos/{REPO}/releases?per_page=100")
    except Exception as e:   # API rate limit on a shared runner IP: guess the file names instead (404s are skipped)
        print(f"release list failed ({e}); guessing hour files")
        rels, now_ = [], dt.datetime.now(dt.timezone.utc)
        for h in range(24 * 10):
            x = now_ - dt.timedelta(hours=h)
            name = f"rec-{x:%Y%m%d-%H}.jsonl.gz"
            rels.append({"tag_name": f"data-{x:%Y%m%d}", "assets": [{"name": name, "size": -1,
                         "browser_download_url": f"https://github.com/{REPO}/releases/download/data-{x:%Y%m%d}/{name}"}]})
    n = 0
    for rel in rels:
        if not str(rel.get("tag_name", "")).startswith("data-"):
            continue
        for a in rel.get("assets") or []:
            p = os.path.join(REC, a["name"])
            if os.path.exists(p) and os.path.getsize(p) == a["size"]:
                continue
            if a["size"] == -1 and os.path.exists(p):
                continue
            for i in range(3):
                try:
                    urllib.request.urlretrieve(a["browser_download_url"], p)
                    n += 1
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        break
                    print(f"download {a['name']} failed: {e}")
                except Exception as e:
                    print(f"download {a['name']} failed: {e}")
    print(f"recordings: {n} new files, {len(os.listdir(REC))} in total")


def load_recordings():
    """books[ticker] = [(t, yes_bids, no_bids)], tape[ticker] = [trade rows], spot_minutes = set of minute stamps."""
    books, tape, seen, minutes = defaultdict(list), defaultdict(list), set(), set()
    for f in sorted(os.listdir(REC)):
        if not f.endswith(".jsonl.gz"):
            continue
        try:
            fh = gzip.open(os.path.join(REC, f), "rt")
            for line in fh:
                if '"k":"kbook"' not in line[:12] and '"k":"ktrade"' not in line[:13] and '"k":"spot"' not in line[:11]:
                    continue
                if '15M-' not in line and '"k":"spot"' not in line[:11]:
                    continue
                d = json.loads(line)
                k = d["k"]
                if k == "spot":
                    minutes.add(d["t"] // 60)
                elif k == "kbook":
                    tk = d.get("tk", "")
                    if tk.split("-")[0] in SERIES:
                        books[tk].append((d["t"], [tuple(x) for x in d.get("yb") or []], [tuple(x) for x in d.get("nb") or []]))
                else:
                    tk = d.get("ticker", "")
                    tid = str(d.get("trade_id"))[:18]
                    if tk.split("-")[0] in SERIES and tid not in seen:
                        seen.add(tid)
                        ts_ = dt.datetime.fromisoformat(d["created_time"].replace("Z", "+00:00")).timestamp()
                        tape[tk].append((ts_, float(d.get("yes_price_dollars") or 0), str(d.get("taker_side")),
                                         float(d.get("count_fp") or d.get("count") or 0)))
        except (EOFError, OSError) as e:   # a file cut short by a recorder crash: keep what was read
            print(f"{f}: {e}")
    for v in books.values():
        v.sort(key=lambda x: x[0])
    print(f"recorded: {len(books)} tickers with books, {sum(map(len, tape.values()))} trades, {len(minutes)} spot minutes")
    return books, tape, minutes


def book_at(rows, t, max_age=600):
    """Latest recorded book at or before t (recorder writes a book only when it changed)."""
    best = None
    for r in rows:
        if r[0] > t:
            break
        best = r
    if not best or t - best[0] > max_age:
        return None
    return best


def price_for(kind, level, bid, ask):
    if bid < level - EPS:
        return None
    tick = 0.001 if bid >= 0.9 - EPS else 0.01
    p = round(bid + tick, 4)
    return (p, True) if p < ask - EPS else (bid, False)


def tape_fill(trades, t_place, side, price, queue, shares):
    """Same rule as bot.kmaker_fill (the live tracks), on compact tape rows (ts, yes_price, taker_side, count)."""
    sold_at = 0.0
    for ts_, yp, taker, cnt in sorted(trades):
        if ts_ <= t_place:
            continue
        px = yp if side == "yes" else round(1 - yp, 6)
        if px < price - 1e-6:
            return float(shares), True
        if abs(px - price) < 1e-6 and taker != side:
            sold_at += cnt
    return max(0.0, min(float(shares), sold_at - queue)), False


def summarize(rows, key):
    """rows have price, won, and a boolean fill flag under `key`. Per-$100 P&L of the filled ones."""
    f = [r for r in rows if r[key]]
    if not f:
        return {"n": len(rows), "fills": 0}
    cost = sum(r["price"] for r in f)
    pnl = sum((1.0 if r["won"] else 0.0) - r["price"] for r in f)
    lost = sum(1 for r in f if not r["won"])
    return {"n": len(rows), "fills": len(f), "lost": lost, "won_all": sum(1 for r in rows if r["won"]),
            "per100": pnl / cost * 100, "avg": cost / len(f),
            "breakeven_loss_per100": (1 - cost / len(f)) * 100}


def fmt(s):
    if not s.get("fills"):
        return f"{s['n']} signals, 0 fills"
    return (f"{s['n']} signals, {s['fills']} filled, lost {s['lost']} ({s['lost'] / s['fills'] * 100:.1f} in 100; "
            f"break-even {s['breakeven_loss_per100']:.1f} in 100), avg price {s['avg'] * 100:.1f}c, "
            f"{'+' if s['per100'] >= 0 else '-'}${abs(s['per100']):.2f} per $100; all signals won "
            f"{s['won_all'] / s['n'] * 100:.1f} in 100")


def run(days=3):
    days = int(days)
    kc.fetch(days)
    fetch_recordings()
    wins = [w for w in kc.load_windows() if w["close"] >= int(dt.datetime.now(dt.timezone.utc).timestamp()) - days * 86400]
    books, tape, minutes = load_recordings()
    rec_t0 = min((r[0] for v in books.values() for r in v), default=0)
    rec_t1 = max((r[0] for v in books.values() for r in v), default=0)
    live_t0 = int(dt.datetime(2026, 11, 9, 19, 0, tzinfo=dt.timezone.utc).timestamp())
    L = ["# Kalshi 15-min crypto: backtest vs recorded books vs live (kreplay.py)", "",
         f"Generated {iso(int(dt.datetime.now(dt.timezone.utc).timestamp()))}. Paper research only. "
         f"{len(wins)} settled windows in the last {days} days (kcrypto candles + Kalshi results). "
         f"Recordings {iso(rec_t0)} to {iso(rec_t1)}. Live tracks started {iso(live_t0)}.", ""]

    # ---------- A. the backtest itself, by period ----------
    L += ["## A. The backtest's own model (candles, 'fair' fill) on recent days", ""]
    by_day_lines = []
    for name, kind, lvl, m, z in VARIANTS:
        rows = kc.variant_trades(kc.signals(wins, m), kind, lvl, z)
        for label, lo, hi in (("all recent days", 0, 10 ** 12), ("recorded hours", rec_t0, rec_t1),
                              ("live hours", live_t0, 10 ** 12)):
            sub = [{"price": r["price"], "won": r["won"], "fair": r["fills"][1], "t": r["t"]} for r in rows if lo <= r["t"] <= hi]
            L.append(f"- **{name}** ({m} min left, {'z ' + str(z) if z else 'no spot check'}), {label}: {fmt(summarize(sub, 'fair'))}")
        days_ = defaultdict(list)
        for r in rows:
            days_[iso(r["t"])[:10]].append({"price": r["price"], "won": r["won"], "fair": r["fills"][1]})
        by_day_lines += [f"- {name} {d}: {fmt(summarize(v, 'fair'))}" for d, v in sorted(days_.items())]
    L += ["", "By day:", ""] + by_day_lines + [""]

    # ---------- B. same signals, recorded books + tape ----------
    L += ["## B. Same windows, filled from the recorded book and full trade tape (live fill rule)", ""]
    wmap = {w["t"]: w for w in wins}
    for name, kind, lvl, m, z in VARIANTS:
        rows, skipped = [], defaultdict(int)
        for w in wins:
            t = w["close"] - 60 * m
            if not (rec_t0 <= t and w["close"] <= rec_t1):
                continue
            if any((t // 60 + i) not in minutes for i in range(0, m + 1)):
                skipped["recording gap"] += 1
                continue
            bk = book_at(books.get(w["t"], []), t)
            if not bk or not bk[1] or not bk[2]:
                skipped["no recorded book"] += 1
                continue
            yb, ya = max(p for p, _ in bk[1]), round(1 - max(p for p, _ in bk[2]), 4)
            if not (0 < yb < ya < 1):
                skipped["crossed book"] += 1
                continue
            side = "yes" if (yb + ya) / 2 >= 0.5 else "no"
            bid, ask = (yb, ya) if side == "yes" else (round(1 - ya, 4), round(1 - yb, 4))
            got = price_for(kind, lvl, bid, ask)
            if not got:
                continue
            price, front = got
            if z is not None:
                zz = kc.zscore(w, t, m, side)
                if zz is None or zz < z:
                    continue
            sideb = bk[1] if side == "yes" else bk[2]
            queue = 0.0 if front else sum(s for p, s in sideb if abs(p - price) < 1e-6)
            shares = max(1, int(10 / price))
            trades = tape.get(w["t"], [])
            filled, through = tape_fill(trades, t, side, price, queue, shares)
            # candle model for the same placement and price
            strict, fair, touch = kc.fill_after(w, t, side, price, front)
            rows.append({"tk": w["t"], "t": t, "price": price, "won": w["res"] == side, "tape": filled > EPS,
                         "full": filled >= shares - EPS, "through": through, "fair": fair, "strict": strict,
                         "front": front, "ntr": len(trades)})
        L.append(f"**{name}**: {len(rows)} signals in recorded hours (skipped: {dict(skipped) or 'none'})")
        L.append(f"- recorded tape, live rule: {fmt(summarize(rows, 'tape'))}")
        L.append(f"- candle model, same signals: {fmt(summarize(rows, 'fair'))}")
        L.append(f"- strict (traded through only): {fmt(summarize(rows, 'strict'))}")
        both = sum(1 for r in rows if r["tape"] and r["fair"])
        only_t = [r for r in rows if r["tape"] and not r["fair"]]
        only_c = [r for r in rows if r["fair"] and not r["tape"]]
        L.append(f"- cross-tab: both filled {both}; tape only {len(only_t)} (lost {sum(1 for r in only_t if not r['won'])}); "
                 f"candles only {len(only_c)} (lost {sum(1 for r in only_c if not r['won'])}); "
                 f"windows with no recorded trades {sum(1 for r in rows if not r['ntr'])}")
        for r in rows:
            if not r["won"]:
                L.append(f"  - loser {r['tk']} at {r['price'] * 100:.1f}c: tape {'filled' if r['tape'] else 'no fill'}"
                         f"{' (through)' if r['through'] else ''}, candles {'filled' if r['fair'] else 'no fill'}")
        L.append("")

    # ---------- C. the live orders, re-scored by the candle model ----------
    L += ["## C. The live tracks' own orders, re-scored by the backtest's fill model", ""]
    t_state = json.load(open(os.path.join(ROOT, "state", "tracks.json")))
    orders = defaultdict(dict)
    for line in open(os.path.join(ROOT, "state", "events.jsonl")):
        if '"kmaker_order"' in line:
            e = json.loads(line)
            orders[e["track"]][e["ticker"]] = e
    for name, *_ in VARIANTS:
        tr = t_state.get(name, {})
        live_fill = {c["ticker"]: c for c in tr.get("closed", [])}
        unfilled = {u["ticker"] for u in tr.get("unfilled_log", [])}
        rows = []
        for tk, e in orders[name].items():
            w = wmap.get(tk)
            if not w or (tk not in live_fill and tk not in unfilled):
                continue
            tp = int(dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00")).timestamp())
            t_min = tp - tp % 60   # candles end on minutes; placement inside a minute -> use that minute's end
            row = w["c"].get(t_min + 60) or w["c"].get(t_min)
            front = True
            if row:
                b, a, _, _ = kc.side_view(row, e["side"])
                front = b is None or e["price"] > b + EPS
            fair = kc.fill_after(w, t_min, e["side"], e["price"], front)[1]
            rows.append({"price": e["price"], "won": w["res"] == e["side"], "live": tk in live_fill, "fair": fair})
        L.append(f"**{name}**: {len(rows)} live orders matched to settled windows")
        L.append(f"- live fills: {fmt(summarize(rows, 'live'))}")
        L.append(f"- backtest model on the same orders: {fmt(summarize(rows, 'fair'))}")
        lo = [r for r in rows if r["live"] and not r["won"]]
        L.append(f"- live losers the backtest would also have filled: {sum(1 for r in lo if r['fair'])} of {len(lo)}; "
                 f"live fills the backtest skips: {sum(1 for r in rows if r['live'] and not r['fair'])}; "
                 f"backtest fills live missed: {sum(1 for r in rows if r['fair'] and not r['live'])}")
        L.append("")
    txt = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "kreplay.md"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        run(*(sys.argv[2:3] or [os.environ.get("KR_DAYS", 3)]))
    elif cmd == "rec":
        fetch_recordings()
        load_recordings()
