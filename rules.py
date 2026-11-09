#!/usr/bin/env python3
"""Fine-print hunt (2026-11-09): does the crowd misprice markets whose rules say something the title doesn't?

PAPER ONLY. Reads public market data and the backtest cache (bt_cache/), never trades.

    python3 rules.py peek      # print what Gamma tells us about disputes and clarifications (a few days)
    python3 rules.py fetch     # rule text + UMA status list for every market in bt_cache/markets.json.gz
    python3 rules.py run       # write backtest/rules.md
    python3 rules.py selftest  # offline check

Ideas tested (all checked the same way as calib.py: price at a set time before the end, +1-5c and the taker fee,
held to the result, grouped by event, 90% band, both halves must be ahead, and the flagged markets must beat
look-alike markets in the same price band that have no flag):
  1. "Strict wording": the rules need an OFFICIAL announcement, a named source, or exclude things the title
     seems to include. If people trade the title, the headline outcome (usually YES) is overpriced.
  2. "Title vs rules gap": the rules name a different date/time than the title, or add conditions.
  3. Disputed / clarified markets (known only afterwards): how wrong was the price before the trouble?
     That says how much a screen could earn at best, if it could spot them in advance.
  4. Limbo: after the end date, while the result waits for UMA, is the price right?

Leakage guard: Gamma returns today's rule text, which includes clarifications added later. The screen only reads
the text BEFORE the first added note ("Update", "Clarification", "Note:", dated edits), so it sees about what a
trader saw before the end. Clarified markets are reported separately.
"""
import bisect
import datetime as dt
import json
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot

CACHE, OUT = bt.CACHE, bt.OUT
DAY = 86400
META = os.path.join(CACHE, "rules_meta.json.gz")
EXTRA_KEYS = ("umaResolutionStatuses", "umaResolutionStatus", "resolutionSource", "resolvedBy", "umaBond", "umaReward",
              "automaticallyResolved", "negRisk", "customLiveness", "hasReviewedDates", "clarification", "clarifications")


def statuses(m):
    raw = m.get("umaResolutionStatuses")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = [raw]
    return [str(x).lower() for x in (raw or [])]


def slim_rules(m):
    return {"d": str(m.get("description") or "")[:8000], "rs": str(m.get("resolutionSource") or "")[:300],
            "st": statuses(m), "q": str(m.get("question") or ""),
            "by": str(m.get("resolvedBy") or "")[:60], "bond": bot.fnum(m.get("umaBond"), None),
            "liv": m.get("customLiveness"), "auto": m.get("automaticallyResolved")}


def peek():
    rng = random.Random(1)
    today = bot.now().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = []
    for back in (5, 20, 60, 120, 200):
        rows += bt.fetch_day(today - dt.timedelta(days=back), True)
    print(f"{len(rows)} closed markets read")
    keys = Counter(k for m in rows for k in m)
    print("keys:", ", ".join(f"{k}({n})" for k, n in sorted(keys.items())))
    for k in EXTRA_KEYS:
        vals = Counter(json.dumps(m.get(k))[:80] for m in rows if k in m)
        print(f"\n{k}: {vals.most_common(12)}")
    disp = [m for m in rows if "disputed" in statuses(m)]
    print(f"\ndisputed: {len(disp)} of {len(rows)}")
    for m in disp[:8]:
        print(" -", m.get("question"), "|", m.get("umaResolutionStatuses"), "| final", m.get("outcomePrices"),
              "| end", m.get("endDate"), "closed", m.get("closedTime"))
    rx = re.compile(r"(update|clarif|note:|edit|additional context)", re.I)
    cl = [m for m in rows if rx.search(str(m.get("description") or ""))]
    print(f"\ndescriptions with update/clarification words: {len(cl)}")
    for m in rng.sample(cl, min(6, len(cl))):
        d = str(m.get("description"))
        i = rx.search(d).start()
        print(" -", m.get("question"), "\n   ...", d[max(0, i - 150):i + 350].replace("\n", " / "))
    print("\nrandom descriptions:")
    for m in rng.sample(rows, 4):
        print(" -", m.get("question"), "\n  ", str(m.get("description"))[:900].replace("\n", " / "))


def fetch():
    """Rule text for every market already in the backtest cache, read day by day like backtest.fetch_markets."""
    markets = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}).get("markets", {})
    have = bt.rjson(META, {}) or {}
    need_days = sorted({bt.utc(m["end"]).strftime("%Y-%m-%d") for k, m in markets.items() if k not in have and m.get("end")})
    print(f"rules: {len(markets)} markets in cache, {len(have)} with rules, {len(need_days)} days to read")
    t0 = time.time()

    def one(k):
        d = dt.datetime.fromisoformat(k).replace(tzinfo=bt.UTC)
        try:
            return k, bt.fetch_day(d, True)
        except Exception as e:
            print(f"  {k} failed: {e}")
            return k, []

    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for i, (k, rows) in enumerate(ex.map(one, need_days)):
            for m in rows:
                mid = str(m.get("id"))
                if mid in markets:
                    have[mid] = slim_rules(m)
            if i % 20 == 0:
                print(f"  {i + 1}/{len(need_days)} days, {len(have)} markets with rules ({time.time() - t0:.0f}s)")
    bt.wjson(META, have)
    st = Counter(s for v in have.values() for s in set(v["st"]))
    print(f"rules: {len(have)} markets with rule text. Status counts: {dict(st)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch}[cmd]()
