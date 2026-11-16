#!/usr/bin/env python3
"""Sweep both sites for bets that repeat every week (or day) and are settled by what a person or office usually does.

  python3 habits.py scan      # probe hab_scan: Kalshi series by category / frequency, Polymarket event families that repeat
"""
import collections
import re
import sys

import backtest as bt
import bot
import yesno

G = bt.G
MONTHS = r"january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
SKIP_K = {"Sports", "Crypto", "Financials", "Climate and Weather", "Economics", "Entertainment", "Mentions"}
SKIP_P = re.compile(r"sports|crypto|nba|nfl|mlb|nhl|soccer|tennis|esports|weather|up-or-down|stocks|mention|ufc|cricket|golf|f1|temperature|games", re.I)


def fam(slug):
    s = re.sub(rf"\b({MONTHS})\b", "", str(slug).lower())
    return re.sub(r"-+", "-", re.sub(r"\d+[a-z]*", "", s)).strip("-")[:70]


def scan(since="2026-08-15", max_pages=500):
    try:
        ser = yesno.kget("/series", {}).get("series") or []
    except Exception as e:
        ser = []
        print("kalshi /series failed", str(e)[:120], flush=True)
    print("Kalshi series", len(ser), collections.Counter((s.get("category"), s.get("frequency")) for s in ser).most_common(60), flush=True)
    for s in sorted(ser, key=lambda s: (str(s.get("category")), s.get("ticker") or "")):
        if s.get("category") not in SKIP_K and s.get("frequency") in ("weekly", "daily"):
            print(f"  K | {s.get('category')} | {s.get('frequency')} | {s.get('ticker')} | {str(s.get('title'))[:100]}", flush=True)
    F = collections.defaultdict(lambda: {"n": 0, "vol": 0.0, "mk": 0, "tags": collections.Counter(), "ex": "", "ends": []})
    cur, n = None, 0
    for _ in range(max_pages):
        p = {"closed": "true", "limit": 50, "end_date_min": since + "T00:00:00Z"}
        if cur:
            p["after_cursor"] = cur
        try:
            r = bot.http_json(f"{G}/events/keyset", p)
        except Exception as e:
            print("   page failed", str(e)[:100], flush=True)
            break
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        for e in rows:
            f = F[fam(e.get("slug"))]
            f["n"] += 1
            f["vol"] += float(e.get("volume") or 0)
            f["mk"] += len(e.get("markets") or [])
            f["tags"].update(str(t.get("slug")) for t in (e.get("tags") or []) if isinstance(t, dict))
            f["ex"] = str(e.get("title"))[:90]
            f["ends"].append(str(e.get("endDate"))[:10])
        n += len(rows)
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur:
            break
    print("Polymarket closed events since", since, ":", n, "families", len(F), flush=True)
    keep = [(k, f) for k, f in F.items() if f["n"] >= 5 and not SKIP_P.search(" ".join(f["tags"]) + " " + k)]
    for k, f in sorted(keep, key=lambda kv: -kv[1]["vol"])[:400]:
        print(f"  P | {f['n']:4d} ev | {f['mk']:5d} mk | ${f['vol']:12,.0f} | {min(f['ends'])}..{max(f['ends'])} | {k} | {f['ex']} | {[t for t, _ in f['tags'].most_common(4)]}", flush=True)


if __name__ == "__main__":
    {"scan": scan}[sys.argv[1] if len(sys.argv) > 1 else "scan"]()
