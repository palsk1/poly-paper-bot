#!/usr/bin/env python3
"""Kalshi "will X say Y" markets against each word's own record (2026-11-13). Research only.

PAPER ONLY. Reads public history, never trades, never writes state/.

Why: on Polymarket the one lead that used outside knowledge was "buy No where a word is priced far above how often
that speaker really said it" (mentions.py, paper track word_no). Kalshi runs far more of these markets (Trump,
press briefings, Fed, sports announcers, earnings calls) and shows a real asking price every hour, so the same
idea can be tested there at prices a buyer could really get.

    python3 kmentions.py list     # probe kmn_list: every mention series + all its settled markets -> markets.json.gz
    python3 kmentions.py tapes    # probe kmn_tapes: hourly bid/ask + every trade per market (resumes)
    python3 kmentions.py run      # report backtest/kmentions.md (data is in the price store)

Data: bt_cache/kmen/ (markets.json.gz, tapes_NNN.json.gz), saved to the shared price store.
"""
import collections
import datetime as dt
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import exam
import khouse
import yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "kmen")
MK = os.path.join(CACHE, "markets.json.gz")
OUT = os.path.join(ROOT, "backtest", "kmentions.md")
BUDGET_MIN = float(os.environ.get("KMN_MIN", "200"))
WORKERS = int(os.environ.get("KMN_WORKERS", "8"))
MIN_VOL = 100
SHARD = 500
LIFE = 21 * 86400          # quotes and trades of at most the last 21 days of a market
T0 = time.time()
kget, rj, wj, its = yesno.kget, khouse.rj, khouse.wj, khouse.its


def is_mention(s):
    t = f"{s.get('ticker') or ''} {s.get('title') or ''} {s.get('category') or ''}".lower()
    return "mention" in t or " say " in f" {t} " or "say during" in t


def all_series():
    out = []
    for p in ({"category": "Mentions"}, {}):
        try:
            r = kget("/series", p)
        except Exception as e:
            print(f"  /series {p} failed: {str(e)[:120]}")
            continue
        got = r.get("series") or []
        print(f"  /series {p}: {len(got)} series, categories {collections.Counter(str(s.get('category')) for s in got).most_common(12)}")
        out += got
    seen, keep = set(), []
    for s in out:
        tk = str(s.get("ticker") or "")
        if tk and tk not in seen and is_mention(s):
            seen.add(tk)
            keep.append(s)
    return keep


def series_markets(s):
    rows, cut = [], yesno.k_cutoff()
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(60):
            p = {"series_ticker": s, "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = kget(path, p)
            except Exception as e:
                print(f"  {s} {path} failed: {str(e)[:100]}")
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    ok, seen = {}, set()
    for m in rows:
        tk = str(m.get("ticker") or "")
        res = str(m.get("result") or "").lower()
        o, c = its(m.get("open_time")), its(m.get("close_time"))
        if not tk or tk in seen or res not in ("yes", "no") or not o or not c:
            continue
        if not str(m.get("event_ticker") or "").startswith(s):      # a filter the API ignored would hand us everything
            continue
        seen.add(tk)
        ok[tk] = {"t": tk, "s": s, "ev": str(m.get("event_ticker") or ""), "q": str(m.get("title") or "")[:160],
                  "w": str(m.get("yes_sub_title") or m.get("subtitle") or "")[:80],
                  "ck": str(m.get("custom_strike") or "")[:120],
                  "open": o, "close": c, "exp": its(m.get("expected_expiration_time")),
                  "res": res, "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0),
                  "last": bot.fnum(m.get("last_price_dollars"), None),
                  "rule": str(m.get("rules_primary") or "")[:400]}
    return s, ok, len(rows)


def do_list():
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    ser = all_series()
    print(f"mention series: {len(ser)}")
    for s in ser:
        have["series"][s["ticker"]] = {"title": str(s.get("title") or "")[:120], "cat": s.get("category"),
                                       "fee": [s.get("fee_type"), s.get("fee_multiplier")], "freq": s.get("frequency"),
                                       "tags": s.get("tags")}
    with ThreadPoolExecutor(4) as ex:
        for s, ok, n in ex.map(series_markets, sorted(have["series"])):
            have["markets"].update(ok)
            have["series"][s]["n"] = len(ok)
    wj(MK, have)
    ms = list(have["markets"].values())
    print(f"settled markets {len(ms)}, events {len({m['ev'] for m in ms})}, with {MIN_VOL}+ contracts {sum(1 for m in ms if m['vol'] >= MIN_VOL)}")
    print("fee types:", collections.Counter(str(v["fee"]) for v in have["series"].values()).most_common(8))
    by = collections.defaultdict(list)
    for m in ms:
        by[m["s"]].append(m)
    print("\n| series | title | markets | events | first | last | yes won | middle volume | total volume |")
    for s, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1]))[:80]:
        vols = sorted(m["vol"] for m in v)
        d = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
        print(f"| {s} | {have['series'][s]['title'][:60]} | {len(v)} | {len({m['ev'] for m in v})} | {d(min(m['close'] for m in v))} | "
              f"{d(max(m['close'] for m in v))} | {sum(m['res'] == 'yes' for m in v)} | {vols[len(vols) // 2]:.0f} | {sum(vols):.0f} |")
    mon = collections.Counter(dt.datetime.utcfromtimestamp(m["close"]).strftime("%Y-%m") for m in ms)
    print("\nby month:", sorted(mon.items()))
    rnd = random.Random(3)
    print("\nexamples:")
    for m in rnd.sample(ms, min(25, len(ms))):
        print(" ", {k: m[k] for k in ("t", "q", "w", "ck", "res", "vol", "last")}, "life h", round((m["close"] - m["open"]) / 3600),
              "exp-close h", None if not m["exp"] else round((m["exp"] - m["close"]) / 3600, 1))
    print("\nrule example:", ms[0]["rule"])


def tape_one(m):
    a, b = max(m["open"], m["close"] - LIFE), m["close"]
    cs = []
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = kget(path, {"start_ts": a - 3600, "end_ts": b, "period_interval": 60})
        except Exception:
            continue
        got = r.get("candlesticks") if isinstance(r, dict) else None
        if got:
            for c in got:
                t, bid, ask = yesno.k_candle(c)
                cs.append([t, bid, ask, bot.fnum(c.get("volume_fp") or c.get("volume"), 0)])
            break
    tr, done, path = khouse.trades_span(m["t"], a, b, 4)
    tr.sort()
    return m["t"], {"c": cs, "tr": tr, "full": done, "p": path}


def shard_path(i):
    return os.path.join(CACHE, f"tapes_{i:03d}.json.gz")


def do_tapes(part=0, parts=1):
    """part/parts: several probe runs can work side by side (kmn_tapes-0-4 ... kmn_tapes-3-4), each on its own shards."""
    have = rj(MK, None)
    if not have:
        print("no markets.json.gz, run list first")
        return
    order = sorted(t for t, m in have["markets"].items() if m["vol"] >= MIN_VOL)
    random.Random(1).shuffle(order)
    print(f"markets to tape: {len(order)}")
    for i in range(0, len(order), SHARD):
        if time.time() - T0 > BUDGET_MIN * 60:
            print("time budget used, run again to resume")
            break
        if (i // SHARD) % parts != part:
            continue
        sp = shard_path(i // SHARD)
        got = rj(sp, {}) or {}
        todo = [have["markets"][t] for t in order[i:i + SHARD] if t not in got]
        if not todo:
            continue
        with ThreadPoolExecutor(WORKERS) as ex:
            for tk, d in ex.map(tape_one, todo):
                got[tk] = d
        wj(sp, got)
        print(f"  shard {i // SHARD}: {len(got)} markets, {sum(len(d['tr']) for d in got.values())} trades, "
              f"{sum(1 for d in got.values() if not d['c'])} without quotes, {sum(1 for d in got.values() if not d['tr'])} without trades, "
              f"{sum(1 for d in got.values() if not d['full'])} cut short ({time.time() - T0:.0f}s)")


# ================================================================ analysis
FOUND = 7                  # shards 0-6 were looked at first; the rules in backtest/kmentions_prereg.md came from them
TRIES = 60                 # cuts looked at on the first 3,500 markets before the rules were fixed
SPORT = ("NBA", "NFL", "MLB", "NCAA", "WCMENTION", "SNF", "TNF", "MNF", "WNBA", "FIGHT", "NHL", "WOMENTION", "ATHLETE", "UFC")


def kind(s):
    if "EARNINGS" in s:
        return "earnings"
    if any(k in s for k in SPORT):
        return "sports"
    if "TRUMP" in s or "DJT" in s:
        return "trump"
    return "other"


def norm(w):
    return re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", w.lower())).strip()


def fee(p):
    return 0.07 * p * (1 - p)


def load():
    """-> markets, tapes ({ticker: {"c": hourly [end, yes bid, yes ask, volume], "tr": trades, "new": fresh-test market}}).
    Trap: Kalshi's live candle endpoint gives prices in dollars under the cents name, so most hourly quotes came
    out 100 times too small. A market whose quotes never pass 1c while its trades do is scaled back up here."""
    ms = (rj(MK, {}) or {}).get("markets") or {}
    tp, i = {}, 0
    while os.path.exists(shard_path(i)) or i < 150:
        if os.path.exists(shard_path(i)):
            for tk, v in (rj(shard_path(i), {}) or {}).items():
                vals = [x for c in v["c"] for x in c[1:3] if x is not None]
                if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
                    for c in v["c"]:
                        c[1] = None if c[1] is None else round(c[1] * 100, 4)
                        c[2] = None if c[2] is None else round(c[2] * 100, 4)
                v["new"] = i >= FOUND
                tp[tk] = v
        i += 1
    return ms, tp


class Record:
    """How often each word came up before in its series, read only up to a moment."""

    def __init__(self, ms):
        self.d = collections.defaultdict(lambda: ([], [0]))
        for m in sorted(ms.values(), key=lambda m: m["close"]):
            if m["s"].startswith("KXMVE"):
                continue
            for k in ((m["s"], norm(m["w"])), m["s"]):
                ts, cs = self.d[k]
                ts.append(m["close"])
                cs.append(cs[-1] + (m["res"] == "yes"))

    def upto(self, k, t):
        import bisect
        ts, cs = self.d.get(k) or ([], [0])
        i = bisect.bisect_left(ts, t)
        return cs[i], i


def looks(ms, tp, hours=(48, 24, 12, 6, 3, 1)):
    """One row per market and look time. The look time counts back from the FIRST close in the event, because a
    market's own close time gives the result away (markets close early once the word is said)."""
    first = {}
    for m in ms.values():
        first[m["ev"]] = min(first.get(m["ev"], 1e18), m["close"])
    rec, rows = Record(ms), []
    for tk, v in tp.items():
        m = ms.get(tk)
        if not m or m["s"].startswith("KXMVE") or not v["c"]:
            continue
        for h in hours:
            t = first[m["ev"]] - h * 3600
            if t < m["open"] + 3600:
                continue
            c = None
            for x in v["c"]:
                if x[0] > t:
                    break
                c = x
            if not c or c[1] is None or c[2] is None or t - c[0] > 3 * 3600:
                continue
            y, n = rec.upto((m["s"], norm(m["w"])), t)
            rows.append({"tk": tk, "s": m["s"], "ev": m["ev"], "h": h, "t": t, "bid": c[1], "ask": c[2], "y": y, "n": n,
                         "yes": m["res"] == "yes", "vol": m["vol"], "new": v["new"], "k": kind(m["s"]), "w": m["w"]})
    return rows


def ok(r, gap=0.10):
    return r["bid"] >= 0.03 and r["ask"] <= 0.97 and r["ask"] - r["bid"] <= gap


def no_bets(rows, extra=0.0):
    out = []
    for r in rows:
        p = 1 - r["bid"] + extra
        if p >= 0.995:
            continue
        cost = p + fee(p)
        out.append({"cost": cost, "pay": 0.0 if r["yes"] else 1.0, "pnl": (0.0 if r["yes"] else 1.0) - cost, "ev": r["ev"], "t": r["t"], "tk": r["tk"], "w": r["w"], "p": p})
    return out


def yes_bets(rows, extra=0.0):
    out = []
    for r in rows:
        p = r["ask"] + extra
        if p >= 0.995:
            continue
        cost = p + fee(p)
        out.append({"cost": cost, "pay": 1.0 if r["yes"] else 0.0, "pnl": (1.0 if r["yes"] else 0.0) - cost, "ev": r["ev"], "t": r["t"], "tk": r["tk"], "w": r["w"], "p": p})
    return out


def per100(b):
    c = sum(x["cost"] for x in b)
    return 100 * sum(x["pnl"] for x in b) / c if c else 0.0


RULES = {"T1": lambda r: r["k"] == "earnings", "T2": lambda r: r["k"] != "earnings" and 1 <= r["n"] <= 2,
         "T3": lambda r: r["k"] != "earnings" and r["n"] >= 3}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode.startswith("tapes-"):
        _, a, b = mode.split("-")
        do_tapes(int(a), int(b))
    else:
        {"list": do_list, "tapes": do_tapes}[mode]()
