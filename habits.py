#!/usr/bin/env python3
"""Sweep both sites for bets that repeat every week (or day) and are settled by what a person or office usually does.

  python3 habits.py scan      # probe hab_scan: Kalshi series by category / frequency, Polymarket event families that repeat
"""
import collections
import datetime as dt
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import yesno
import khouse
import kmentions as km

rj, wj = khouse.rj, khouse.wj

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


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "hab")
MK = os.path.join(CACHE, "markets.json.gz")
HAB = re.compile(r"TRUMP|POTUS|FULLLID|EOWEEK|MAMDANI|BILLSCOUNT|TRUTHSOCIAL|KEVCOUNT|LEAVITT|VANCE|MUSK|PRESS|GOLF|VISIT|PARDON|VETO|WHITEHOUSE|^KXWH|BRIEFING|SIGN|CALL|MEET|TRAVEL|RALLY")
NOT = re.compile(r"APPROVE|FAV|TRUMPVH|VOTEHUB|TRUMPSAY|MENTION|APRPOTUS|NOBEL|TRUMPOUT|IMPEACH")


def do_list(pick=None):
    """probe hab_list[-regex]: every settled market of Kalshi's Politics series about what a person or office does -> bt_cache/hab/markets.json.gz"""
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    allser = yesno.kget("/series", {}).get("series") or []
    ser = [x for x in allser if x.get("ticker") and (re.search(pick, x["ticker"]) if pick else
           (x.get("category") == "Politics" and not NOT.search(x["ticker"]) and
            (x.get("frequency") in ("weekly", "daily") or (x.get("frequency") in ("custom", "monthly") and HAB.search(x["ticker"])))))]
    print("series to list:", len(ser), collections.Counter(x.get("frequency") for x in ser), flush=True)
    for x in ser:
        have["series"][x["ticker"]] = {"title": str(x.get("title") or "")[:120], "cat": x.get("category"), "freq": x.get("frequency"),
                                       "fee": [x.get("fee_type"), x.get("fee_multiplier")],
                                       "src": [y.get("url") for y in (x.get("settlement_sources") or []) if isinstance(y, dict)][:3]}
    with ThreadPoolExecutor(4) as ex:
        for t, ok, n in ex.map(km.series_markets, sorted(x["ticker"] for x in ser)):
            have["markets"].update(ok)
            have["series"][t]["n"] = len(ok)
    wj(MK, have)
    by = collections.defaultdict(list)
    for m in have["markets"].values():
        by[m["s"]].append(m)
    d = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
    print(f"settled markets {len(have['markets'])}", flush=True)
    print("| series | title | freq | markets | events | first | last | yes won | middle volume | total volume | middle life days |")
    for t, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1])):
        vols = sorted(m["vol"] for m in v)
        life = sorted((m["close"] - m["open"]) / 86400 for m in v)
        i = have["series"][t]
        if len({m["ev"] for m in v}) < 8:
            continue
        print(f"| {t} | {i['title'][:60]} | {i['freq']} | {len(v)} | {len({m['ev'] for m in v})} | {d(min(m['close'] for m in v))} | "
              f"{d(max(m['close'] for m in v))} | {sum(m['res'] == 'yes' for m in v)} | {vols[len(vols) // 2]:.0f} | {sum(vols):.0f} | {life[len(life) // 2]:.1f} |", flush=True)
        m = max(v, key=lambda m: m["vol"])
        print("   EX", {k: m[k] for k in ("t", "q", "w", "res", "vol")}, "| RULE", m["rule"][:260], flush=True)


def do_tapes(pick=None, min_events=15):
    """probe hab_tapes[-regex]: hourly bid/ask + every trade -> bt_cache/hab/tapes_<series>.json.gz"""
    have = (rj(MK, {}) or {}).get("markets") or {}
    by = collections.defaultdict(list)
    for m in have.values():
        if (not pick or re.search(pick, m["s"])) and m["vol"] >= 50:
            by[m["s"]].append(m)
    t0 = time.time()
    for t, ms in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1])):
        if len({m["ev"] for m in ms}) < min_events or time.time() - t0 > 3 * 3600:
            continue
        path = os.path.join(CACHE, f"tapes_{t}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in ms if m["t"] not in got]
        for i in range(0, len(todo), 300):
            with ThreadPoolExecutor(8) as ex:
                for tk, dd in ex.map(km.tape_one, todo[i:i + 300]):
                    got[tk] = dd
            wj(path, got)
        print(f"{t}: {len(got)} of {len(ms)} markets, {sum(len(x['tr']) for x in got.values())} trades ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "scan"
    mode, _, arg = a.partition("-")
    {"scan": scan, "list": do_list, "tapes": do_tapes}[mode](*([arg] if arg else []))
