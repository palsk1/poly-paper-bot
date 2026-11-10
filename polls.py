#!/usr/bin/env python3
"""Polls and poll averages vs politics markets (2026-11-10).

PAPER ONLY. Reads public data, never trades. Research tool: no live track uses it.

Question: Polymarket and Kalshi list markets that settle on a poll average (Trump approval on Silver Bulletin or
RealClearPolitics, the generic ballot, ...). The average moves slowly and its inputs (single polls) are public
before the average moves. Does a simple forecast built from the average beat the market price after costs?

    python3 polls.py reach     # which markets exist in the cache, which poll data sources answer (probe: btpolls_reach)
"""
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict

import backtest as bt
import bot

UTC = dt.timezone.utc
DAY = 86400
K = bot.KALSHI
G = bot.GAMMA
PCACHE = os.path.join(bt.CACHE, "polls")
POLL_RX = re.compile(r"approval|generic (congressional )?ballot|\bpoll|favorab|silver bulletin|realclear|\brcp\b|"
                     r"gallup|yougov|538|fivethirtyeight|net approval", re.I)


def raw(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (paper research bot)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400], None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode(), None


SOURCES = {
    "silver bulletin approval page": "https://www.natesilver.net/p/trump-approval-ratings-nate-silver-bulletin",
    "silver bulletin generic ballot": "https://www.natesilver.net/p/generic-ballot-average-2026-nate-silver-bulletin-congress-polls",
    "rcp approval page": "https://www.realclearpolling.com/polls/approval/donald-trump/approval-rating",
    "electionsusa approval api": "https://electionsusa.org/api/approval-trump-2.json",
    "electionsusa generic api": "https://electionsusa.org/api/generic-ballot-2026.json",
    "electionsusa data page": "https://electionsusa.org/data/",
    "predictionscout generic": "https://predictionscout.com/research/generic-ballot-polls-vs-prediction-markets",
    "votehub api": "https://api.votehub.com/polls?poll_type=approval&subject=Trump",
    "wikipedia approval polls (raw)": "https://en.wikipedia.org/w/index.php?title=Opinion_polling_on_the_second_Donald_Trump_presidency&action=raw",
    "538 approval polls (old)": "https://projects.fivethirtyeight.com/polls/data/president_approval_polls.csv",
    "strength in numbers": "https://www.strengthinnumbers.com/p/trump-approval-rating-tracker",
    "nyt approval": "https://www.nytimes.com/interactive/polls/donald-trump-approval-rating-polls.html",
}


def reach_sources():
    for name, url in SOURCES.items():
        st, body, ct = raw(url)
        txt = body.decode("utf-8", "replace") if body else ""
        print(f"\n== {name}: HTTP {st}, {len(body or b'')} bytes, {ct}")
        if st != 200:
            print("   ", txt[:200].replace("\n", " "))
            continue
        dw = sorted(set(re.findall(r"datawrapper\.dwcdn\.net/([A-Za-z0-9]{5})", txt)))
        if dw:
            print("   datawrapper charts:", dw)
        links = sorted(set(re.findall(r'["\'(]([^"\'()\s]+\.(?:json|csv|xlsx|zip)(?:\?[^"\'()\s]*)?)', txt)))
        if links:
            print("   data links:", links[:40])
        gs = sorted(set(re.findall(r"docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+", txt)))
        if gs:
            print("   google sheets:", gs)
        if ct and "json" in ct:
            print("   ", txt[:1500])
        else:
            for kw in ("RCP Average", "approve", "Approve", "trend", "average"):
                i = txt.find(kw)
                if i >= 0:
                    print(f"   near '{kw}':", re.sub(r"\s+", " ", txt[max(0, i - 150):i + 300]))
                    break
        if name.startswith("silver bulletin") and dw:
            for c in dw[:12]:
                for v in ("", "1/"):
                    st2, b2, _ = raw(f"https://datawrapper.dwcdn.net/{c}/{v}dataset.csv")
                    if st2 == 200:
                        t2 = b2.decode("utf-8", "replace")
                        lines = t2.splitlines()
                        print(f"   chart {c} dataset.csv: {len(lines)} lines | {' / '.join(lines[:3])[:300]} ... {lines[-1][:150]}")
                        break
                else:
                    st3, b3, _ = raw(f"https://datawrapper.dwcdn.net/{c}/")
                    t3 = b3.decode("utf-8", "replace") if b3 else ""
                    m = re.search(r"/(\d+)/", t3[:3000])
                    print(f"   chart {c}: no plain dataset.csv (HTTP {st2}); page {st3} {len(t3)} bytes, title:",
                          (re.search(r"<title>(.*?)</title>", t3) or [None, "?"])[1][:100])


def reach_markets():
    path = os.path.join(bt.CACHE, "events.json.gz")
    markets = dict(bt.rjson(os.path.join(bt.CACHE, "markets.json.gz"), {}).get("markets", {}))
    evs = bt.rjson(path, None) or {}
    for mid, mk in (evs.get("markets") or {}).items():
        markets.setdefault(mid, mk)
    print(f"\n== cache: {len(markets):,} Polymarket markets")
    hits = [m for m in markets.values() if POLL_RX.search(m["q"])]
    print(f"   poll-ish questions: {len(hits):,}")
    kinds = Counter()
    ex = defaultdict(list)
    for m in hits:
        k = re.sub(r"\d+(\.\d+)?", "#", m["q"])
        k = re.sub(r"(January|February|March|April|May|June|July|August|September|October|November|December)( #)?", "<date>", k)
        kinds[k] += 1
        if len(ex[k]) < 2:
            ex[k].append((m["q"], m.get("vol"), dt.datetime.fromtimestamp(m["end"] or 0, UTC).date().isoformat(), m.get("ev_slug")))
    vol = defaultdict(float)
    for m in hits:
        k = re.sub(r"\d+(\.\d+)?", "#", m["q"])
        k = re.sub(r"(January|February|March|April|May|June|July|August|September|October|November|December)( #)?", "<date>", k)
        vol[k] += m.get("vol") or 0
    for k, n in kinds.most_common(45):
        print(f"   {n:5d}  ${vol[k]:>12,.0f}  {k[:110]}")
        for e in ex[k]:
            print(f"            e.g. {e[0][:90]} | vol ${e[1] or 0:,.0f} | ends {e[2]} | {e[3]}")


def reach_kalshi():
    print("\n== Kalshi series about approval / polls")
    try:
        r = bot.http_json(K + "/series", {"category": "Politics"})
        ss = r.get("series") or []
    except Exception as e:
        print("   series list failed:", e)
        ss = []
    print(f"   {len(ss)} politics series")
    for s in ss:
        t = f"{s.get('ticker')} {s.get('title')}"
        if POLL_RX.search(t) or re.search(r"APR|APPROV|BALLOT|POLL", s.get("ticker") or ""):
            print(f"   {s.get('ticker'):24s} {s.get('title')[:80]} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')}")
    for tk in ("KXAPRPOTUS", "KXSBAPPROVE", "KXTRUMPAPPROVE", "KXGENERICBALLOT", "KXAPPROVE"):
        try:
            r = bot.http_json(K + "/markets", {"series_ticker": tk, "limit": 5, "status": "settled"})
            ms = r.get("markets") or []
            print(f"   {tk}: {len(ms)} settled shown", [(m.get('ticker'), m.get('yes_sub_title'), m.get('result')) for m in ms[:3]])
            if ms:
                print("     rules:", (ms[0].get("rules_primary") or "")[:300])
        except Exception as e:
            print(f"   {tk}: {e}")


def reach():
    reach_markets()
    reach_kalshi()
    reach_sources()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "reach"
    {"reach": reach}[cmd]()
