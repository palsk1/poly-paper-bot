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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "fetch":
        fetch()
    elif cmd == "report":
        import drawsharp_report  # noqa: F401  (filled in after the fetch)
    else:
        print(__doc__)
