#!/usr/bin/env python3
"""Rocket launch count bets: "How many SpaceX launches in November?" (Kalshi KXSPACEXCOUNT and friends, Polymarket tag
spacex) against the public launch record. backtest/spacex.md.

  python3 spacex.py src       (probe spx_src: Jonathan McDowell's free launch list GCAT -> bt_cache/spx/launches.json.gz)
  python3 spacex.py report [log]
"""
import collections
import datetime as dt
import os
import sys

import backtest as bt

CACHE = os.path.join(bt.CACHE, "spx")
LP = os.path.join(CACHE, "launches.json.gz")
GCAT = ("https://planet4589.org/space/gcat/tsv/launch/launch.tsv", "https://planet4589.org/space/gcat/tsv/derived/launchlog.tsv")


def src():
    """Every launch since 2015 with its day, rocket, maker and result. GCAT dates look like '2025 Nov  3 0412:30'."""
    import urllib.request
    os.makedirs(CACHE, exist_ok=True)
    rows = []
    for url in GCAT:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "poly-paper-bot research (github.com/palsk1/poly-paper-bot)"})
            raw = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
        except Exception as e:
            print(url, "failed", str(e)[:200], flush=True)
            continue
        lines = [l for l in raw.split("\n") if l.strip()]
        head = lines[0].lstrip("#").split("\t")
        print(url, len(lines), "lines; columns:", head[:30], flush=True)
        for l in lines[1:6]:
            print("   ", l[:300], flush=True)
        col = {h.strip(): i for i, h in enumerate(head)}
        for l in lines[1:]:
            if l.startswith("#"):
                continue
            f = l.split("\t")
            g = lambda k: f[col[k]].strip() if k in col and col[k] < len(f) else ""
            d = parse_day(g("Launch_Date"))
            if not d or d < "2015-01-01":
                continue
            rows.append({"tag": g("Launch_Tag"), "day": d, "t": g("Launch_Date"), "lv": g("LV_Type"), "var": g("Variant"),
                         "ag": g("Agency"), "code": g("Launch_Code"), "site": g("Launch_Site"), "mis": g("Mission")[:60],
                         "cat": g("Category")})
        if rows:
            break
    bt.wjson(LP, {"src": url if rows else None, "rows": rows, "got": dt.datetime.now(dt.timezone.utc).isoformat()})
    c = collections.Counter((r["day"][:7], r["ag"]) for r in rows if r["day"] >= "2025-10")
    print("saved", len(rows), "launches; by month and maker (since Oct 2025):", sorted(c.items())[-40:], flush=True)
    print("codes:", collections.Counter(r["code"] for r in rows).most_common(12), "makers:", collections.Counter(r["ag"] for r in rows).most_common(12))
    print("rockets:", collections.Counter(r["lv"] for r in rows if r["day"] >= "2025").most_common(15))
    print("newest:", rows and sorted(rows, key=lambda r: r["day"])[-5:])


def parse_day(s):
    p = s.split()
    if len(p) < 3:
        return None
    try:
        return dt.date(int(p[0]), dt.datetime.strptime(p[1][:3], "%b").month, int(p[2].rstrip("?"))).isoformat()
    except ValueError:
        return None


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "src":
        src()
