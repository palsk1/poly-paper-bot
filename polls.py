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


# ================================================================ test

import math     # noqa: E402
import random   # noqa: E402

HOURS = (3, 12, 24, 48, 96)
THRESH = (0.03, 0.05, 0.10)
GRID = [round(20 + i * 0.1, 1) for i in range(500)]   # 20.0 .. 69.9


def settle_value(ms, step=0.1):
    """The reported number that reproduces every strike result of one event (None if none or ambiguous range > 1)."""
    ok = [v for v in GRID if all(econ.sat(v, m) in (None, m["res"] == "yes") for m in ms)
          and any(econ.sat(v, m) is not None for m in ms)]
    if not ok or ok[-1] - ok[0] > 1.0001:
        return None
    return round((ok[0] + ok[-1]) / 2, 2), round(ok[-1] - ok[0], 2)


POLY_RX = (("between", re.compile(r"between (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?)", re.I)),
           ("less", re.compile(r"(?:less than|below) (\d+(?:\.\d+)?)", re.I)),
           ("greater_or_equal", re.compile(r"(?:at least|or (?:more|higher)) (\d+(?:\.\d+)?)", re.I)),
           ("greater_or_equal", re.compile(r"(\d+(?:\.\d+)?)%? or (?:more|higher|above)", re.I)))


def poly_strike(q):
    for st, rx in POLY_RX:
        mt = rx.search(q)
        if mt:
            if st == "between":
                return {"st": "between", "lo": float(mt.group(1)), "hi": float(mt.group(2))}
            if st == "less":
                return {"st": "less", "lo": None, "hi": float(mt.group(1))}
            return {"st": st, "lo": float(mt.group(1)), "hi": None}
    return None


def poly_source(rules):
    r = (rules or "").lower()
    if "silver bulletin" in r:
        return "silver"
    if "realclear" in r:
        return "rcp"
    if "votehub" in r:
        return "votehub"
    return "?"


def sb_series(src):
    """Silver Bulletin daily approve average from the Datawrapper datasets: {date: value}."""
    best = {}
    for k, txt in src.items():
        if k != "dw_kSCt4":   # the approval chart on the SB approval page (rfiFi is the generic ballot)
            continue
        lines = [ln for ln in txt.splitlines() if ln.strip()]
        if not lines:
            continue
        sep = "\t" if "\t" in lines[0] else ","
        head = [h.strip().lower() for h in lines[0].split(sep)]
        if "modeldate" not in head or "approve" not in head:
            continue
        di, ai = head.index("modeldate"), head.index("approve")
        gi = head.index("group") if "group" in head else None
        ser = {}
        for ln in lines[1:]:
            c = ln.split(sep)
            if gi is not None and c[gi].strip().lower() not in ("all", "all polls"):
                continue
            try:
                mo, da, yr = [int(x) for x in c[di].strip().split("/")]
                yr += 2000 if yr < 100 else 0
                ser[dt.date(yr, mo, da).isoformat()] = float(c[ai])
            except Exception:
                continue
        if len(ser) > len(best):
            best = ser
            print(f"  Silver Bulletin daily series from {k}: {len(ser)} days, {min(ser)} to {max(ser)}")
    return best


class Families:
    """Every event we can test: settle source, close time, strike markets with results and hourly quotes."""

    def __init__(self):
        self.events = []      # {"fam", "src", "e", "close", "value", "markets": [m...]}
        self.known = defaultdict(dict)   # src -> {known_from_ts: value}
        src = pload("sources") or {}
        kmk, kcd = pload("kmarkets") or {}, pload("kcandles") or {}
        self.checks = []
        for s, ms in kmk.items():
            source = KSERIES.get(s, ("?", 0.1))[0]
            by = defaultdict(list)
            for m in ms:
                by[m["e"]].append(m)
            ok = bad = 0
            for e, group in by.items():
                sv = settle_value(group)
                if sv is None:
                    bad += 1
                    continue
                ok += 1
                close = max(m["close"] for m in group)
                for m in group:
                    m["quotes"] = kcd.get(m["t"]) or []
                    m["venue"] = "kalshi"
                self.events.append({"fam": s, "src": source, "e": e, "close": close, "value": sv[0], "width": sv[1],
                                    "markets": group})
                if sv[1] <= 0.2001:
                    self.known[source][close] = sv[0]
            self.checks.append(f"{s} ({source}): {ok} events with one settle value, {bad} without (dropped)")
        sb = sb_series(src)
        for d, v in sb.items():   # a day's value counts as known at 12:00 UTC the next day (cautious)
            t = int(dt.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp()) + DAY + 12 * 3600
            self.known["silver"][t] = v
        pev, ph = pload("pevents") or {}, pload("phist") or {}
        pok = pbad = 0
        for slug, ev in pev.items():
            if not ev or not ev["markets"]:
                continue
            group = []
            for m in ev["markets"]:
                sk = poly_strike(m["q"])
                if not sk or not m.get("final") or m["final"][0] is None or not m.get("closed") or (m.get("end") or 0) >= HOLDOUT_TS:
                    continue
                if m["final"][0] not in (0.0, 1.0) and not (m["final"][0] > 0.98 or m["final"][0] < 0.02):
                    continue
                q = dict(m, **sk, res="yes" if m["final"][0] > 0.5 else "no", sub="", venue="poly",
                         hist=ph.get(m["id"]) or [], close=m["end"])
                group.append(q)
            if not group:
                continue
            source = poly_source(group[0].get("rules"))
            sv = settle_value(group)
            if sv is None:
                pbad += 1
                continue
            pok += 1
            self.events.append({"fam": "poly_" + source, "src": source, "e": slug, "close": max(m["close"] for m in group),
                                "value": sv[0], "width": sv[1], "markets": group})
        self.checks.append(f"Polymarket: {pok} events with one settle value, {pbad} without")
        # Silver Bulletin cross-check: does the chart's value for the day match the Polymarket result?
        agree = dis = 0
        for ev in self.events:
            if ev["src"] != "silver" or ev["fam"] == "KXSILVERAPPROVE":
                continue
            mt = re.search(r"on-([a-z]+)-(\d+)", ev["e"])
            if not mt or mt.group(1) not in MONTHS:
                continue
            d = dt.datetime.fromtimestamp(ev["close"] - 12 * 3600, UTC).date()
            v = sb.get(d.isoformat())
            if v is None:
                continue
            if abs(round(v, 1) - ev["value"]) <= ev["width"] / 2 + 0.051:
                agree += 1
            else:
                dis += 1
        self.checks.append(f"Silver Bulletin chart vs Polymarket results: {agree} agree, {dis} disagree")
        for k in self.known:
            self.known[k] = dict(sorted(self.known[k].items()))
        self.ktimes = {k: list(v) for k, v in self.known.items()}

    def last_known(self, src, t, lag=0):
        ts_ = self.ktimes.get(src) or []
        import bisect
        i = bisect.bisect_right(ts_, t - lag) - 1
        if i < 0:
            return None
        return ts_[i], self.known[src][ts_[i]]

    def changes(self, src, t, gap_days):
        """Past changes of the settle number over about gap_days, using only pairs finished before t."""
        ts_ = [x for x in self.ktimes.get(src) or [] if x < t]
        vals = self.known[src]
        out = []
        j = 0
        for i, a in enumerate(ts_):
            target = a + gap_days * DAY
            while j < len(ts_) and ts_[j] < target - 0.5 * DAY:
                j += 1
            if j < len(ts_) and abs(ts_[j] - target) <= 0.5 * DAY:
                out.append(round(vals[ts_[j]] - vals[a], 2))
        return out


def model_p(fams, ev, m, t, placebo_shift=0):
    """Chance the market settles YES, from the last known value + past changes over the same gap."""
    lk = fams.last_known(ev["src"], t - placebo_shift)
    if not lk:
        return None
    t0, v0 = lk
    gap = (ev["close"] - (t0 + placebo_shift)) / DAY
    if gap < 0.3 or gap > 12:
        return None
    ch = fams.changes(ev["src"], t, max(1, round(gap)))
    if len(ch) < 20:
        return None
    sd = max(0.15, (sum(c * c for c in ch) / len(ch)) ** 0.5)
    pe = sum(1 for c in ch if econ.sat(round(v0 + c, 1), m)) / len(ch)
    pn = econ.prob(v0, sd, 0.1, m)
    return 0.8 * pe + 0.2 * pn, v0, gap


def quote_at(m, t):
    if m["venue"] == "kalshi":
        return econ.quote(m["quotes"], t)
    h = [x for x in m["hist"] if x[0] is not None and x[1] is not None and t - 6 * 3600 <= x[0] <= t]
    if not h:
        return None
    p = h[-1][1]
    if not 0.01 <= p <= 0.99:
        return None
    return p - 0.02, p + 0.02   # Polymarket history is a price, not a book: buy 2c worse (PROTOCOL.md)


def fee(m, price):
    if m["venue"] == "kalshi":
        return econ.kfee(price)
    return (m.get("fee") or 0) * price * (1 - price)


def build(fams, placebo_shift=0):
    pts = []
    for ev in fams.events:
        if ev["close"] >= HOLDOUT_TS:
            continue
        for m in ev["markets"]:
            if m.get("res") not in ("yes", "no"):
                continue
            for h in HOURS:
                t = ev["close"] - h * 3600
                q = quote_at(m, t)
                if not q:
                    continue
                r = model_p(fams, ev, m, t, placebo_shift)
                if not r:
                    continue
                pts.append({"fam": ev["fam"], "src": ev["src"], "e": ev["e"], "close": ev["close"], "h": h, "p": r[0],
                            "v0": r[1], "gap": r[2], "value": ev["value"], "bid": q[0], "ask": q[1], "venue": m["venue"],
                            "fee": m.get("fee") or 0, "y": 1 if m["res"] == "yes" else 0, "t": m.get("t") or m.get("id")})
    return pts


def pick(pts, thr, slip=0.0, one_per_event=True):
    """Bet the side the model likes when it's worth thr more than the price + fee. One bet per event and horizon
    (the biggest gap), so 15 strikes of one day count once."""
    cand = []
    for r in pts:
        m = {"venue": r["venue"], "fee": r["fee"]}
        cy, cn = r["ask"] + slip, 1 - r["bid"] + slip
        if not (0 < cy < 1 and 0 < cn < 1):
            continue
        ey = r["p"] - cy - fee(m, cy)
        en = (1 - r["p"]) - cn - fee(m, cn)
        side, cost, edge = (1, cy + fee(m, cy), ey) if ey >= en else (0, cn + fee(m, cn), en)
        if edge < thr:
            continue
        twin = 0.5 * ((r["y"] - cy - fee(m, cy)) + ((1 - r["y"]) - cn - fee(m, cn)))
        cand.append(dict(r, side=side, cost=cost, edge=edge, won=r["y"] == side, pnl=(1.0 if r["y"] == side else 0.0) - cost,
                         twin_pnl=twin, twin_cost=0.5 * (cy + fee(m, cy) + cn + fee(m, cn))))
    if not one_per_event:
        return cand
    best = {}
    for b in cand:
        k = (b["e"], b["h"])
        if k not in best or b["edge"] > best[k]["edge"]:
            best[k] = b
    return list(best.values())


def run():
    fams = Families()
    pts = build(fams)
    placebo = build(fams, placebo_shift=21 * DAY)
    L = ["# Poll averages vs approval and generic-ballot markets (polls.py)", "",
         f"Written by `python3 polls.py run` on {dt.date.today().isoformat()}. Markets that closed before 2026-11-10 only "
         "(PROTOCOL.md holdout).", "",
         "Model: the poll average the market settles on (RealClearPolitics, Silver Bulletin or VoteHub) can only move "
         "so far in a few days. We take its last value a bot could have known (the previous settled market's number, "
         "or Silver Bulletin's chart for the day before, counted as known at 12:00 UTC the next day) and spread it by "
         "how much it moved over the same number of days in the past (only past data). That gives a chance for every strike.", "",
         "Bets: Kalshi at the real hourly ask (YES) or 1 minus the bid (NO) plus the taker fee; Polymarket at the "
         "history price + 2c + fee. One bet per event and time (the strike with the biggest gap), held to the result. "
         "'Coin-flip side' = same markets, random side: what costs alone do. 'Wrong dates' = the model is given the "
         "average from 3 weeks earlier: a real edge must vanish there.", "", "## Data checks", ""]
    L += [f"- {c}" for c in fams.checks]
    L += [f"- known values: " + ", ".join(f"{k} {len(v)}" for k, v in fams.known.items())]
    L += [f"- strike x time rows: {len(pts)} (wrong-dates: {len(placebo)})", ""]
    L += ["## Who guesses better? (lower is better; every strike row)", "",
          "| Family | Hours before | Rows | Model score | Market score |", "|---|---|---|---|---|"]
    fam_names = sorted({r["fam"] for r in pts})
    for f in fam_names:
        for h in HOURS:
            sub = [r for r in pts if r["fam"] == f and r["h"] == h]
            if len(sub) < 20:
                continue
            bm = sum((r["p"] - r["y"]) ** 2 for r in sub) / len(sub)
            bk = sum(((r["bid"] + r["ask"]) / 2 - r["y"]) ** 2 for r in sub) / len(sub)
            L.append(f"| {f} | {h} | {len(sub)} | {bm:.4f} | {bk:.4f} |")
    L += ["", "## Betting the model (all families together)", ""]
    for h in HOURS:
        L.append(f"### {h} hours before the close")
        for thr in THRESH:
            bs = pick([r for r in pts if r["h"] == h], thr)
            L.append(f"- model beats price by {int(thr * 100)}c+: {econ.line(bs)}")
            if bs:
                L.append(f"  - {econ.halves(bs)}; 1c worse prices {econ.money(econ.per100(pick([r for r in pts if r['h'] == h], thr, 0.01)))} per $100")
                L.append(f"  - wrong dates: {econ.line(pick([r for r in placebo if r['h'] == h], thr))}")
        L.append("")
    L += ["## By family (5c+ gap)", ""]
    for f in fam_names:
        for h in HOURS:
            bs = pick([r for r in pts if r["fam"] == f and r["h"] == h], 0.05)
            if bs:
                L.append(f"- {f}, {h}h: {econ.line(bs)}; {econ.halves(bs)}")
    L += ["", "## By price paid (all hours, 5c+ gap)", ""]
    allb = pick(pts, 0.05)
    for lo, hi in ((0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.01)):
        bs = [b for b in allb if lo <= b["cost"] < hi]
        L.append(f"- paid {int(lo * 100)}-{min(100, int(hi * 100))}c: {econ.line(bs)}")
    txt = "\n".join(L) + "\n"
    os.makedirs(bt.OUT, exist_ok=True)
    with open(os.path.join(bt.OUT, "polls.md"), "w") as f:
        f.write(txt)
    print(txt)
    rng = random.Random(1)
    print("\n== sample rows")
    for r in rng.sample(pts, min(20, len(pts))):
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


def selftest():
    """Offline: in a fake world where the market price is the true chance, betting the model must lose about the
    costs (no fake edge). In a world where the market ignores the average entirely, the model must win."""
    import tempfile
    global PCACHE
    old = PCACHE
    steps = [-0.3, -0.2, -0.1, 0.1, 0.2, 0.3]
    for world in ("fair", "blind"):
        PCACHE = tempfile.mkdtemp()
        rng = random.Random(5)
        v, t0 = 42.0, 1767225600
        km, kc = [], {}
        for d in range(300):
            close = t0 + d * DAY + 18 * 3600
            prev = v
            if rng.random() < 0.4:
                v = round(v + rng.choice(steps), 1)
            e = f"FAKE-{d}"
            for k in range(-4, 5):
                x = round(prev + k * 0.1 + 0.05, 2)
                m = {"t": f"{e}-{k}", "e": e, "s": "KXTRUMPAPPROVE", "close": close, "st": "greater", "lo": x, "hi": None,
                     "sub": "", "res": "yes" if v > x else "no", "vol": 1, "rules": ""}
                km.append(m)
                true = 0.6 * (prev > x) + 0.4 * sum(1 for c in steps if prev + c > x) / len(steps)
                p = true if world == "fair" else 0.5
                p = min(0.97, max(0.03, p))
                kc[m["t"]] = [[close - h * 3600, round(p - 0.01, 3), round(p + 0.01, 3), 1] for h in range(0, 100, 3)]
        psave("kmarkets", {"KXTRUMPAPPROVE": km})
        psave("kcandles", kc)
        for n in ("sources", "pevents", "phist"):
            psave(n, {})
        pts = build(Families())
        bs = pick([r for r in pts if r["h"] == 12], 0.03)
        r = econ.per100(bs) if bs else 0.0
        print(f"  {world} world: {len(bs)} bets, {econ.money(r)} per $100; costs alone {econ.money(econ.per100(bs, 'twin_pnl', 'twin_cost')) if bs else 0}")
        if world == "fair":
            assert len(bs) < 30 or r < 3, "fake edge in a fair world"
        else:
            assert bs and r > 10, "model can't beat a blind market"
    PCACHE = old
    print("selftest OK")


def reach():
    reach_markets()
    reach_kalshi()
    reach_sources()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "reach"
    {"reach": reach, "fetch": fetch, "run": run, "selftest": selftest, "all": lambda: (fetch(), run())}[cmd]()
