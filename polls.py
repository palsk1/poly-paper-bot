#!/usr/bin/env python3
"""Polls and poll averages vs politics markets (2026-11-10).

PAPER ONLY. Reads public data, never trades. Research tool: no live track uses it.

Question: Polymarket and Kalshi list markets that settle on a poll average (Trump approval on Silver Bulletin or
RealClearPolitics, the generic ballot, ...). The average moves slowly and its inputs (single polls) are public
before the average moves. Does a simple forecast built from the average beat the market price after costs?

    python3 polls.py reach     # which markets exist in the cache, which poll data sources answer (probe: btpolls_reach)
    python3 polls.py fetch     # settled Kalshi approval/ballot markets + hourly bid/ask, Polymarket approval events
                               # + hourly prices, VoteHub polls, Silver Bulletin daily average (probe: btpolls_fetch)
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


# ================================================================ fetch

from concurrent.futures import ThreadPoolExecutor   # noqa: E402

import econ   # noqa: E402  (Kalshi market list, hourly candles, fee, strike matching)

HOLDOUT_TS = econ.HOLDOUT_TS
KSERIES = {   # series -> (settle source, step of the reported number)
    "KXTRUMPAPPROVE": ("rcp", 0.1), "KXAPRPOTUS": ("rcp", 0.1), "APRPOTUS": ("rcp", 0.1), "KXAPRPOTUSD": ("rcp", 0.1),
    "KXTRUMPPOLLDAILY": ("rcp?", 0.1), "KXTRUMPVH": ("votehub", 0.1), "KXVHAPRPOTUS": ("votehub", 0.1),
    "KXVOTEHUBTRUMPUPDOWN": ("votehub", 0.1), "KXGENERICBALLOTVOTEHUB": ("votehub_gb", 0.1),
    "KXGENERICBALLOT": ("gb?", 0.1), "KXSILVERAPPROVE": ("silver", 0.1), "KXTRUMPFAV": ("fav?", 0.1),
    "KX538APPROVE": ("538", 0.1), "538APPROVE": ("538", 0.1),
}
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december")


def psave(name, obj):
    os.makedirs(PCACHE, exist_ok=True)
    with gzip.open(os.path.join(PCACHE, name + ".json.gz"), "wt") as f:
        json.dump(obj, f)


def pload(name, default=None):
    try:
        with gzip.open(os.path.join(PCACHE, name + ".json.gz"), "rt") as f:
            return json.load(f)
    except Exception:
        return default


def kfull(m, series):
    d = econ.kslim(m, series)
    d["rules"] = (m.get("rules_primary") or "")[:500]
    return d


def fetch_kalshi():
    mk = pload("kmarkets") or {}
    for s in KSERIES:
        if s in mk:
            continue
        ms = [m for m in econ.kalshi_markets(s) if m["close"] < HOLDOUT_TS]
        mk[s] = ms
        evs = sorted({m["e"] for m in ms})
        print(f"  {s}: {len(ms)} settled markets, {len(evs)} events"
              + (f", {dt.datetime.fromtimestamp(min(m['close'] for m in ms), UTC).date()} to "
                 f"{dt.datetime.fromtimestamp(max(m['close'] for m in ms), UTC).date()}" if ms else ""))
        if ms:
            print("     e.g.", ms[0]["t"], ms[0]["st"], ms[0]["lo"], ms[0]["hi"], ms[0]["sub"], "|", ms[0]["rules"][:200])
    psave("kmarkets", mk)
    cd = pload("kcandles") or {}
    todo = [m for ms in mk.values() for m in ms if m["t"] not in cd]
    print(f"  Kalshi candles to fetch: {len(todo)}")
    t0 = time.time()
    with ThreadPoolExecutor(econ.WORKERS) as ex:
        for i, (m, c) in enumerate(zip(todo, ex.map(econ.kalshi_candles, todo))):
            cd[m["t"]] = c
            if i % 1000 == 999:
                print(f"    {i + 1}/{len(todo)} ({time.time() - t0:.0f}s)")
                psave("kcandles", cd)
    psave("kcandles", cd)
    print(f"  candles: {sum(1 for v in cd.values() if v)} of {len(cd)} markets have history")


def gamma_event(slug):
    try:
        r = bot.http_json(G + "/events", {"slug": slug})
    except Exception:
        return None
    rows = r if isinstance(r, list) else bot.envelope_rows(r, "events", "data")
    return rows[0] if rows else None


def fetch_poly():
    evs = pload("pevents") or {}
    start = dt.date(2025, 3, 1)
    slugs = []
    d = start
    while d < dt.date(2026, 11, 10):
        base = f"{MONTHS[d.month - 1]}-{d.day}"
        for pat in ("trump-approval-rating-on-{b}", "trump-approval-rating-on-{b}-{y}",
                    "trump-approval-rating-at-least-on-{b}", "trump-approval-rating-at-least-on-{b}-{y}",
                    "trump-approval-rating-up-or-down-on-{b}", "trump-net-approval-on-{b}",
                    "generic-ballot-on-{b}", "generic-ballot-on-{b}-{y}"):
            slugs.append(pat.format(b=base, y=d.year))
        d += dt.timedelta(days=1)
    todo = [s for s in slugs if s not in evs]
    print(f"  Polymarket slugs to try: {len(todo)}")
    with ThreadPoolExecutor(8) as ex:
        for s, e in zip(todo, ex.map(gamma_event, todo)):
            if not e:
                evs[s] = None
                continue
            ms = [bt.slim_market(m) for m in e.get("markets") or []]
            for m, rm in zip(ms, e.get("markets") or []):
                m["rules"] = str(rm.get("description") or "")[:600]
            evs[s] = {"slug": s, "title": e.get("title"), "end": ms[0]["end"] if ms else None, "markets": ms}
    found = {k: v for k, v in evs.items() if v}
    print(f"  Polymarket poll events found: {len(found)}")
    for k in sorted(found)[:6] + sorted(found)[-3:]:
        v = found[k]
        print(f"    {k}: {len(v['markets'])} markets, vol ${sum(m['vol'] or 0 for m in v['markets']):,.0f} | "
              f"{v['markets'][0]['q'][:70] if v['markets'] else ''} | {v['markets'][0].get('rules', '')[:160] if v['markets'] else ''}")
    psave("pevents", evs)
    ph = pload("phist") or {}
    mlist = [m for v in found.values() for m in v["markets"] if m["id"] not in ph and m.get("toks") and m.get("end")]
    print(f"  Polymarket histories to fetch: {len(mlist)}")

    def one(m):
        tok = m["toks"][0]
        s, e = m["end"] - 9 * DAY, min(m["closed_t"] or m["end"] + DAY, m["end"] + 2 * DAY)
        try:
            return m["id"], bt.hist_points(bot.http_json(f"{bt.C}/prices-history",
                                                         {"market": tok, "startTs": s, "endTs": e, "fidelity": 60}))
        except Exception as ex:
            return m["id"], []
    with ThreadPoolExecutor(8) as ex:
        for mid, pts in ex.map(one, mlist):
            ph[mid] = pts
    psave("phist", ph)
    print(f"  Polymarket histories: {sum(1 for v in ph.values() if v)} of {len(ph)}")


def dw_latest(chart):
    """Latest published dataset of a Datawrapper chart (the bare URL can serve an old version)."""
    st, b, _ = raw(f"https://datawrapper.dwcdn.net/{chart}/")
    txt = b.decode("utf-8", "replace") if b else ""
    vs = [int(x) for x in re.findall(rf"{chart}/(\d+)/", txt)]
    m = re.search(r'http-equiv="REFRESH"[^>]*url=([^"]+)', txt, re.I)
    if m:
        vs += [int(x) for x in re.findall(r"/(\d+)/", m.group(1))]
    best = None
    for v in sorted(set(vs), reverse=True)[:3] or [None]:
        url = f"https://datawrapper.dwcdn.net/{chart}/{v}/dataset.csv" if v else f"https://datawrapper.dwcdn.net/{chart}/dataset.csv"
        st2, b2, _ = raw(url)
        if st2 == 200:
            best = (v, b2.decode("utf-8", "replace"))
            break
    return best


def fetch_sources():
    out = pload("sources") or {}
    for chart in ("rfiFi", "sEHv2", "kSCt4"):
        r = dw_latest(chart)
        if r:
            out["dw_" + chart] = r[1]
            ls = r[1].splitlines()
            print(f"  Silver Bulletin chart {chart} v{r[0]}: {len(ls)} lines, first {ls[1][:80] if len(ls) > 1 else ''} | last {ls[-1][:80]}")
        else:
            print(f"  Silver Bulletin chart {chart}: no dataset")
    # find every datawrapper chart on the SB approval page, in case the daily average moved to another chart
    st, b, _ = raw(SOURCES["silver bulletin approval page"])
    for c in sorted(set(re.findall(r"datawrapper\.dwcdn\.net/([A-Za-z0-9]{5})", b.decode("utf-8", "replace") if b else ""))):
        if "dw_" + c not in out:
            r = dw_latest(c)
            if r:
                out["dw_" + c] = r[1]
                print(f"  SB page chart {c}: {len(r[1].splitlines())} lines")
    for name, url in (("votehub", SOURCES["votehub api"]),
                      ("votehub_gb", "https://api.votehub.com/polls?poll_type=generic-ballot"),
                      ("eusa_approval", SOURCES["electionsusa approval api"]),
                      ("eusa_generic", SOURCES["electionsusa generic api"]),
                      ("eusa_polls", "https://electionsusa.org/data/polls.csv")):
        st, b, ct = raw(url, timeout=90)
        if st == 200:
            out[name] = b.decode("utf-8", "replace")
            print(f"  {name}: {len(b):,} bytes")
            if name.startswith("votehub"):
                try:
                    j = json.loads(out[name])
                    print("    first row:", json.dumps(j[0] if isinstance(j, list) else j)[:500])
                except Exception as e:
                    print("    not json:", e)
        else:
            print(f"  {name}: HTTP {st}")
    psave("sources", out)


def fetch():
    t0 = time.time()
    fetch_sources()
    print(f"sources done ({time.time() - t0:.0f}s)")
    fetch_poly()
    print(f"polymarket done ({time.time() - t0:.0f}s)")
    fetch_kalshi()
    print(f"kalshi done ({time.time() - t0:.0f}s)")


def reach():
    reach_markets()
    reach_kalshi()
    reach_sources()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "reach"
    {"reach": reach, "fetch": fetch}[cmd]()
