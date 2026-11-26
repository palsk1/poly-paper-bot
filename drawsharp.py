#!/usr/bin/env python3
"""Soccer draws vs the sharp bookies (26 Nov 2026, Jan: "research this").

Question: does the soccer_draw rule (Polymarket draw at 15-50c, a day before kickoff) win more when the sharp
bookies also say the draw is cheap on Polymarket? If yes, the rule could be made pickier.

Pinnacle keeps no free history. football-data.co.uk (free CSVs, readable from GitHub Actions, not from Claude's
workspace) has, per match: bookmaker odds collected before the weekend ("pre-closing", Friday for weekend games,
Tuesday for midweek ones, so roughly 1-3 days before kickoff) and at kickoff ("closing"). Main 22 European
divisions have both; the "extra" leagues (Argentina, Brazil, USA, Mexico, Japan, Norway, ...) only closing.

Commands:
  fetch      (probe `dsh_fetch`) download every 2025-26 / 2026-27 main division + extra league CSV into
             bt_cache/dsh/fd.json.gz, print which odds columns each file has
  report     (local, after `python3 store.py pull bt_cache/dsh bt_cache/sports`) match Polymarket draw markets
             (in-sample games only, before 10 Nov) to football-data rows, test the filters, write
             backtest/drawsharp.md
"""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import math
import os
import sys

import bot

DIR = "bt_cache/dsh"
FD = os.path.join(DIR, "fd.json.gz")
MAIN = ("E0 E1 E2 E3 EC SC0 SC1 SC2 SC3 D1 D2 I1 I2 SP1 SP2 F1 F2 N1 B1 P1 T1 G1").split()
EXTRA = ("ARG AUT BRA CHN DNK FIN IRL JPN MEX NOR POL ROU RUS SWE SWZ USA").split()
SEASONS = ("2526", "2627")
OUT = "backtest/drawsharp.md"


def fetch():
    import sharp
    os.makedirs(DIR, exist_ok=True)
    rows, heads = [], {}
    urls = [(f"{s}/{d}", f"https://www.football-data.co.uk/mmz4281/{s}/{d}.csv") for s in SEASONS for d in MAIN]
    urls += [(f"new/{d}", f"https://www.football-data.co.uk/new/{d}.csv") for d in EXTRA]
    for key, url in urls:
        st, body = sharp.raw(url)
        if st != 200:
            print(f"{key}: HTTP {st}")
            continue
        rd = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig", "replace"))))
        keep = 0
        for r in rd:
            ds = r.get("Date") or ""
            d = None
            for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                try:
                    d = dt.datetime.strptime(ds, fmt).date()
                    break
                except ValueError:
                    pass
            if not d or d < dt.date(2026, 1, 1):
                continue
            r = {k: v for k, v in r.items() if k and v not in (None, "")}
            r["_file"] = key
            r["_date"] = d.isoformat()
            rows.append(r)
            keep += 1
        cols = list(rd[0].keys()) if rd else []
        heads[key] = cols
        odds = [c for c in cols if c and c.endswith("D") and len(c) <= 7]
        print(f"{key}: {len(rd)} rows, {keep} from 2026; draw-odds columns: {' '.join(odds)}")
    with gzip.open(FD, "wt") as f:
        json.dump({"rows": rows, "heads": heads, "at": bot.iso(dt.datetime.now(dt.timezone.utc))}, f)
    print(f"saved {len(rows)} rows to {FD}")
    # quick fill-rate of the odds columns we care about, 2026 rows only
    cnt = collections.Counter()
    for r in rows:
        for c in ("PSD", "PSCD", "BFED", "BFECD", "AvgD", "AvgCD", "MaxD", "MaxCD", "B365D", "B365CD", "BFD", "BFCD"):
            if c in r:
                cnt[(r["_file"].split("/")[0] == "new", c)] += 1
    for (ex, c), n in sorted(cnt.items()):
        print(f"  {'extra' if ex else 'main '} {c}: {n}")


# ================================================================ report

LIVE_FEE = 0.05       # Polymarket sports taker rate today (old history markets often show 0)
SLIP = 0.02           # pay 2c over the chart, as in digs_draws.md


def _f(r, k):
    try:
        v = float(r[k])
        return v if v > 1.0 else None
    except (KeyError, ValueError, TypeError):
        return None


def book_fair(r, kind):
    """Fair draw chance from one football-data row, margin removed (multiplicative). kind 'pre' or 'close'.
    Sharpest source first: Pinnacle, then Betfair Exchange, then the market average. Returns (fair, source)."""
    import sharp
    srcs = (("PS", "Pinnacle"), ("BFE", "Betfair"), ("Avg", "average")) if kind == "pre" else \
           (("PSC", "Pinnacle"), ("BFEC", "Betfair"), ("AvgC", "average"))
    for pre, name in srcs:
        o = [_f(r, pre + x) for x in "HDA"]
        if None in o:
            # the extra-league files name closing columns PSCH / AvgCH / BFECH the same way; also try "C" variants
            continue
        fair = sharp.devig([1 / x for x in o])
        return fair[1][0], name, sum(1 / x for x in o) - 1
    return None, None, None


def _teams(q):
    import re
    m = re.match(r"Will (.+?) vs\.? (.+?) end in a draw", q or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def match_rows(drows, fd):
    import sharp
    by_date = collections.defaultdict(list)
    for r in fd:
        by_date[r["_date"]].append(r)
    out, miss = [], 0
    for d in drows:
        a, b = _teams(d["q"])
        if not a:
            miss += 1
            continue
        g = dt.datetime.fromtimestamp(d["mk"]["gst"], dt.timezone.utc).date()
        best, bs = None, 0.0
        for dd in (g, g - dt.timedelta(days=1), g + dt.timedelta(days=1)):
            for r in by_date.get(dd.isoformat(), []):
                h, w = r.get("HomeTeam") or r.get("Home"), r.get("AwayTeam") or r.get("Away")
                if not h or not w:
                    continue
                sc = min(sharp.name_score(a, h), sharp.name_score(b, w))
                if dd != g:
                    sc -= 0.05
                if sc > bs:
                    best, bs = r, sc
        if best is not None and bs >= 0.6:
            out.append((d, best, bs))
        else:
            miss += 1
    return out, miss


def report():
    import census
    import exam
    fd = json.load(gzip.open(FD, "rt"))["rows"]
    ms, hist, rows, kinds = census.sports_rows()          # in-sample only (games before 10 Nov)
    L = ["# Soccer draws vs the sharp bookies (drawsharp.py)", "",
         f"Generated {bot.iso(dt.datetime.now(dt.timezone.utc))}. Polymarket games before 10 Nov only (the games the "
         "draw rule was found on; the 21 Dec holdout from 10 Nov is not touched). Bookmaker odds from football-data.co.uk.", ""]
    res = {}
    for hn in ("24h before start", "1h before start"):
        drows = [r for r in rows if r["kind"] == "draw" and r["h"] == hn and 0.15 <= r["p"] < 0.50]
        m, miss = match_rows(drows, fd)
        res[hn] = (drows, m, miss)
        print(f"{hn}: {len(drows)} draw bets, matched {len(m)}, not matched {miss}")
    return L, res


def bets_of(m):
    """One dict per matched draw bet: Polymarket chart price, the books' fair draw chance before and at kickoff."""
    out = []
    for d, r, sc in m:
        fp, sp, op = book_fair(r, "pre")
        fc, scl, oc = book_fair(r, "close")
        c = min(0.99, d["p"] + SLIP)
        cost = c + bot.taker_fee(1, c, LIVE_FEE)
        out.append({"ev": d["ev"], "t": d["t"], "p": d["p"], "y": d["y"], "cost": cost, "pay": d["y"],
                    "pre": fp, "pre_src": sp, "close": fc, "close_src": scl, "sport": d["sport"],
                    "file": r["_file"], "q": d["q"]})
    return out


def per100(bs):
    c = sum(b["cost"] for b in bs)
    return 100 * (sum(b["pay"] for b in bs) - c) / c if c else None


# leagues (Polymarket slug prefix) where football-data has the bookmaker odds; found by matching (report)
COVERED = set("arg bra mls chi es2 mex itsb tur elc bl2 por nor ere den rou1 fr2 jap fl1 lal sea rus swe epl scop "
              "bun aut pol fin irl swz bel gre e2 e3".split())
BIG = set("epl lal sea bun fl1 ucl uel".split())


def live():
    """One live look, no trades: Pinnacle's fair draw chance vs Polymarket's listed draw ask, for every soccer game
    in the next 36h that matches. Saved to bt_cache/dsh/live_<time>.json.gz so the results can be scored later."""
    import statistics as stx
    import sharp
    board = sharp.pinnacle_board([s for s, nm in sharp.PIN_SPORTS.items() if nm == "soccer"])
    games = sharp.poly_games(36)
    rows = []
    for g in games:
        b, amap = sharp.match_game(g, board)
        if not b or "draw" not in b["prob"]:
            continue
        for m, i, label, ask, fair in sharp.offers(g, b, amap):
            if label != "draw: Yes":
                continue
            mlt, pw = b["prob"]["draw"]
            slug = str(g["event"].get("slug") or "")
            rows.append({"slug": slug, "lg": slug.split("-")[0], "title": g["event"].get("title"), "ask": ask,
                         "bid": bot.fnum(m.get("bestBid"), None), "fair_mult": mlt, "fair_pow": pw,
                         "limit": b["limit"], "over": b["overround"], "pin_league": b["league"],
                         "hrs": (g["start"] - bot.now()).total_seconds() / 3600, "start": bot.iso(g["start"]),
                         "cid": m.get("conditionId"), "at": bot.iso(bot.now())})
    print(f"Pinnacle soccer games {len(board)}, Polymarket games in 36h {len(games)}, matched with a draw {len(rows)}")
    os.makedirs(DIR, exist_ok=True)
    fn = os.path.join(DIR, f"live_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M')}.json.gz")
    with gzip.open(fn, "wt") as f:
        json.dump(rows, f)
    print("saved", fn)

    def show(name, rr):
        if not rr:
            print(f"  {name}: none")
            return
        gaps = [r["fair_mult"] - r["ask"] for r in rr]
        print(f"  {name:38s} n={len(rr):3d}  Pinnacle fair minus Polymarket ask: median {100 * stx.median(gaps):+.1f}c, "
              f"2c+ under fair {sum(x >= 0.02 for x in gaps)}, 3c+ {sum(x >= 0.03 for x in gaps)}, "
              f"Polymarket dearer {sum(x < 0 for x in gaps)}")
    rule = [r for r in rows if 0.15 <= r["ask"] <= 0.50]
    show("every matched draw at 15-50c", rule)
    show("  ...20-28h before (the rule's window)", [r for r in rule if 20 <= r["hrs"] <= 28])
    show("  ...big leagues", [r for r in rule if r["lg"] in BIG])
    show("  ...other leagues with free odds history", [r for r in rule if r["lg"] in COVERED and r["lg"] not in BIG])
    show("  ...leagues with NO free odds history", [r for r in rule if r["lg"] not in COVERED and r["lg"] not in BIG])
    for r in sorted(rule, key=lambda r: r["ask"] - r["fair_mult"])[:40]:
        print(f"    {100 * (r['fair_mult'] - r['ask']):+5.1f}c ask {100 * r['ask']:4.1f} fair {100 * r['fair_mult']:4.1f} "
              f"in {r['hrs']:4.1f}h lim {r['limit']:.0f} | {r['lg']} {r['title'][:50]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "fetch":
        fetch()
    elif cmd == "live":
        live()
    elif cmd == "report":
        report()
    else:
        print(__doc__)
