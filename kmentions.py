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
TRIES2 = 250               # cuts looked at on all markets after the fresh test (the comb and the patient side)
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


def load(trades=False):
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
                if not trades:
                    v["tr"] = []
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


def house(ms, lo_h=3, need=10):
    """The patient side. Every hour from a market's second hour until `lo_h` hours before the event's first close:
    where Yes has a buy order at 3c+, an asking price of 97c or less and a gap of 2-10c, offer Yes 1c under the asking
    price (that is: bid for No) for one hour. Filled only if people in a hurry really bought `need`+ Yes contracts at
    our price or higher in that hour. No fee for the waiting side. One bet per market (the first fill). Reads the
    shards one by one (all trades at once need too much memory). -> (No-side bets, Yes-side bets)."""
    import bisect
    first = {}
    for m in ms.values():
        first[m["ev"]] = min(first.get(m["ev"], 1e18), m["close"])
    no, yes = [], []
    for i in range(400):
        if not os.path.exists(shard_path(i)):
            continue
        for tk, v in (rj(shard_path(i), {}) or {}).items():
            m = ms.get(tk)
            if not m or m["s"].startswith("KXMVE") or not v["c"]:
                continue
            vals = [x for c in v["c"] for x in c[1:3] if x is not None]
            sc = 100 if (vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20) else 1
            T, ts, won = first[m["ev"]], [t[0] for t in v["tr"]], m["res"] == "yes"
            got_n = got_y = False
            for c in v["c"]:
                t = c[0]
                if t < m["open"] + 3600 or t > T - lo_h * 3600 or c[1] is None or c[2] is None or (got_n and got_y):
                    continue
                bid, ask = c[1] * sc, c[2] * sc
                if bid < 0.03 or ask > 0.97 or not 0.02 <= ask - bid <= 0.10:
                    continue
                tr = v["tr"][bisect.bisect_right(ts, t):bisect.bisect_right(ts, t + 3600)]
                base = {"ev": m["ev"], "t": t, "tk": tk, "w": m["w"], "k": kind(m["s"])}
                pn, py = round(ask - 0.01, 4), round(bid + 0.01, 4)
                if not got_n and sum(x[2] for x in tr if x[3] == 1 and x[1] / 1000 >= pn - 1e-9) >= need:
                    got_n = True
                    no.append(dict(base, cost=1 - pn, pay=0.0 if won else 1.0, pnl=(0.0 if won else 1.0) - (1 - pn), p=pn))
                if not got_y and sum(x[2] for x in tr if x[3] == 0 and x[1] / 1000 <= py + 1e-9) >= need:
                    got_y = True
                    yes.append(dict(base, cost=py, pay=1.0 if won else 0.0, pnl=(1.0 if won else 0.0) - py, p=py))
    return no, yes


def quarter(t):
    d = dt.datetime.fromtimestamp(t, dt.timezone.utc)
    return f"{d.year} Q{(d.month - 1) // 3 + 1}"


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


JULY = 1782864000          # 1 July 2026


def run(score=True):
    ms, tp = load()
    rows = [r for r in looks(ms, tp) if ok(r)]
    L = [f"# Kalshi \"what will X say\" markets (kmentions.py, {dt.datetime.now(dt.timezone.utc):%Y-%m-%d})", ""]
    A = L.append
    A("## Plain summary")
    A("")
    A(f"- **What:** every finished Kalshi mention market since January 2025: {len(ms):,} markets in {len({m['ev'] for m in ms.values()}):,} events "
      f"(Trump, press briefings, sports announcers, earnings calls, TV shows). {len(tp):,} of them traded 100+ contracts; for those we have "
      "the real buy and sell orders every hour and every trade.")
    SUMMARY_AT = len(L)
    A("")
    card = {}

    def sc(name, b, tries, prereg=False, status="dropped"):
        c = exam.score(b, name, tries=tries, prereg=prereg, src="kmentions.py, backtest/kmentions.md", status=status, log=score, quiet=True)
        card[name] = c
        return c

    def trow(name, b, c):
        return (f"| {name} | {len(b):,} | {c['events']:,} | {usd(c['per100'])} | {usd(c['lo100'])} to {usd(c['hi100'])} | "
                f"{usd(c['half1'])} / {usd(c['half2'])} | {c['verdict']} |")

    HEAD = "| what | bets | events | per $100 | luck range | first half / second half | exam |\n|---|---|---|---|---|---|---|"
    A("## 1. The three rules fixed before the big download (`backtest/kmentions_prereg.md`)")
    A("")
    A("Buy No at the real asking price plus Kalshi's fee, 24 hours before the event's first market closes, one bet per market.")
    A("\"First 3,500\" is where the rules were found. \"The rest\" was still downloading when they were written down.")
    A("")
    A(HEAD)
    names = {"T1": "Earnings-call markets: buy No", "T2": "Word listed only 1-2 times before (not earnings): buy No",
             "T3": "Word listed 3+ times before (not earnings): buy No"}
    for k, f in RULES.items():
        for new in (False, True):
            b = no_bets([r for r in rows if r["new"] == new and r["h"] == 24 and f(r)])
            nm = f"Kalshi mentions, {'fresh test' if new else 'first 3,500'}: {names[k]}"
            c = sc(nm, b, 3 if new else TRIES, prereg=new)
            A(trow(f"{k} {names[k]}, {'the rest' if new else 'first 3,500'}", b, c))
    A("")
    A("The two leads from the first 3,500 markets shrank to almost nothing on the rest. They were luck. Writing the rules")
    A("down first is what caught it.")
    A("")
    A("## 2. Combing all of it: buying at the asking price")
    A("")
    A("Same bet (24 hours before, real asking price plus fee), every market. \"Off\" = how many cents Yes was priced above how often it really won.")
    A("")
    A("| group | bets | Yes priced too high by | buy No, per $100 | buy Yes, per $100 | buy No since July 2026 | buy Yes since July 2026 |")
    A("|---|---|---|---|---|---|---|")
    mid = lambda r: (r["bid"] + r["ask"]) / 2
    cuts = [("all", lambda r: True)] + [(k, (lambda k: lambda r: r["k"] == k)(k)) for k in ("earnings", "sports", "trump", "other")]
    cuts += [(f"Yes at {int(a * 100)}-{int(b * 100)}c", (lambda a, b: lambda r: a <= mid(r) < b)(a, b))
             for a, b in ((.03, .15), (.15, .3), (.3, .5), (.5, .7), (.7, .85), (.85, .97))]
    cuts += [(f"word listed {a if a == b else str(a) + ('-' + str(b) if b < 999 else '+')} times before", (lambda a, b: lambda r: a <= r["n"] <= b)(a, b))
             for a, b in ((0, 0), (1, 2), (3, 9), (10, 999))]
    cuts += [("Yes 20c+ above the word's own record (3+ earlier)", lambda r: r["n"] >= 3 and r["bid"] - r["y"] / r["n"] >= .2),
             ("Yes 20c+ below the word's own record (3+ earlier)", lambda r: r["n"] >= 3 and r["y"] / r["n"] - r["ask"] >= .2)]
    for nm, f in cuts:
        R = [r for r in rows if r["h"] == 24 and f(r)]
        J = [r for r in R if r["t"] >= JULY]
        off = 100 * (sum(mid(r) for r in R) - sum(r["yes"] for r in R)) / max(1, len(R))
        A(f"| {nm} | {len(R):,} | {off:+.1f}c | {usd(per100(no_bets(R)))} | {usd(per100(yes_bets(R)))} | {usd(per100(no_bets(J)))} | {usd(per100(yes_bets(J)))} |")
    allr = [r for r in rows if r["h"] == 24]
    c_no = sc("Kalshi mentions: always buy No at the asking price, 24h before", no_bets(allr), TRIES2)
    c_yes = sc("Kalshi mentions: always buy Yes at the asking price, 24h before", yes_bets(allr), TRIES2)
    gap = [r for r in allr if r["n"] >= 3 and r["bid"] - r["y"] / r["n"] >= .2 and r["t"] >= JULY]
    c_gap = sc("Kalshi mentions: buy No where Yes is 20c+ above the word's own record, since July 2026", no_bets(gap), TRIES2)
    A("")
    A(HEAD)
    A(trow("always buy No", no_bets(allr), c_no))
    A(trow("always buy Yes", yes_bets(allr), c_yes))
    A(trow("No where Yes is 20c+ above the word's record, since July 2026", no_bets(gap), c_gap))
    A("")
    A("## 3. The waiting side: sell Yes to people in a hurry")
    A("")
    A("Each hour (until 3 hours before the event), offer Yes 1c under the asking price for one hour, which is the same as bidding for No.")
    A("Filled only when 10+ Yes contracts were really bought at our price or higher. No fee. One bet per market.")
    A("")
    no, yes = house(ms)
    A(HEAD)
    c_h = sc("Kalshi mentions, waiting side: sell Yes 1c under the asking price (all of 2025-2026)", no, TRIES2)
    A(trow("sell Yes (hold No), all of 2025-2026", no, c_h))
    nj = [b for b in no if b["t"] >= JULY]
    c_hj = sc("Kalshi mentions, waiting side since July 2026: sell Yes 1c under the asking price", nj, TRIES2)
    A(trow("sell Yes (hold No), since July 2026", nj, c_hj))
    c_hy = sc("Kalshi mentions, waiting side: buy Yes 1c above the best buy order", yes, TRIES2)
    A(trow("buy Yes 1c above the best buy order", yes, c_hy))
    A("")
    A("Quarter by quarter (sell Yes, hold No):")
    A("")
    A("| quarter | bets | per $100 | earnings | sports | Trump | other |")
    A("|---|---|---|---|---|---|---|")
    qs = collections.defaultdict(list)
    for b in no:
        qs[quarter(b["t"])].append(b)
    for q in sorted(qs):
        v = qs[q]
        cell = lambda k: (lambda x: f"{usd(per100(x))} ({len(x):,})" if len(x) >= 50 else "-")([b for b in v if b["k"] == k])
        A(f"| {q} | {len(v):,} | {usd(per100(v))} | {cell('earnings')} | {cell('sports')} | {cell('trump')} | {cell('other')} |")
    A("")
    A("This side made real money in 2025 and it shrank every quarter of 2026 to about nothing. Other people's robots do this job now.")
    A("The paper fill is also kind to us: a real order would be undercut by those robots, and with 50+ contracts needed for a fill the last two quarters are behind.")
    A("")
    A("## Traps found (for the next dig on Kalshi)")
    A("")
    A("- **A market's own close time gives away the result.** Mention markets close early once the word is said. Count time back from the first close in the whole event, never from the market's own close.")
    A("- **Kalshi's live hourly-quote endpoint returns dollars in the field that used to hold cents.** Read through `yesno.k_candle` most quotes came out 100 times too small. `kmentions.load()` scales them back (a market whose quotes never pass 1c while its trades do).")
    A("- **Final volume is not a clean filter.** Cutting by a market's total volume looked like a huge lead (+$17 per $100 under 1,000 contracts); it is only because volume depends on how the market ended.")
    A("- **A random 1 in 20 sample of markets was not enough.** Two leads of +$10 to +$14 per $100 on 100-250 bets were gone on the other 19 in 20.")
    A("- **Holdout note:** this data runs to 13 Nov 2026, so it includes Kalshi mention markets that ended on or after 10 Nov. No test registered for 21 Dec uses Kalshi mention markets, so none of them is touched.")
    s = [f"- **Buying at the asking price:** Yes is priced about {100 * (sum(mid(r) for r in allr) - sum(r['yes'] for r in allr)) / len(allr):.0f}c too high on average, so Yes buyers lose "
         f"{usd(-c_yes['per100'])[1:]} per $100 ({c_yes['verdict']}). Buying No comes out at {usd(c_no['per100'])} per $100 ({c_no['verdict']}): the fee and the gap eat the lean.",
         "- **The word's own record barely helps on Kalshi.** Words listed 10+ times before are priced right. The Polymarket idea "
         f"(No where Yes is 20c+ above the record) is {usd(c_gap['per100'])} per $100 since July ({c_gap['verdict']}), and about $0 for words with 8+ earlier markets.",
         "- **Two leads from the first 3,500 markets failed the fresh test** on the other 70,000 (section 1).",
         f"- **The waiting side was a real money-maker and is gone.** Selling Yes to people in a hurry made {usd(c_h['per100'])} per $100 on {len(no):,} bets "
         f"over two years ({c_h['verdict']}), but quarter by quarter it fell from about +$12 (late 2025) to {usd(c_hj['per100'])} since July 2026 ({c_hj['verdict']}).",
         "- **Verdict: nothing to build.** Dropped, no track. Kalshi's mention markets are fairly priced today for anyone but the Yes buyer."]
    L[SUMMARY_AT:SUMMARY_AT] = s
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    return card


# ================================================================ Kalshi's price as the outside number for Polymarket
STOP = set("what will say during the a an of on in at to and or his her their next originally scheduled for with by from this that be is before after".split())


def _toks(x):
    return {w for w in re.findall(r"[a-z0-9]+", x.lower()) if w not in STOP and len(w) > 1}


def _words(w):
    n = re.search(r"(\d+)\+", w)
    w = re.sub(r"\d+\+\s*times?", "", re.sub(r"\(.*?\)", "", w), flags=re.I)
    return frozenset(x for x in (re.sub(r"[^a-z0-9 ]", "", p.lower()).strip() for p in re.split(r"/| or ", w)) if x), int(n.group(1)) if n else 1


def twins(pm, km, overlap=0.67):
    """Polymarket mention market -> the Kalshi market on the same speech and the same word list (same count needed,
    listed ends within 36 hours, two thirds of the title words shared). -> [(polymarket id, kalshi ticker)]"""
    idx = collections.defaultdict(list)
    for m in km.values():
        if not m["s"].startswith("KXMVE"):
            ws, c = _words(m["w"])
            for w in ws:
                idx[w].append((m, ws, c, _toks(m["q"])))
    out = []
    for p in pm.values():
        try:
            pe, pc = float(p["end"]), float(p["closed_t"] or p["end"])
        except (TypeError, ValueError):
            continue
        ws, c = _words(p.get("item") or "")
        pt, best = _toks(p["title"]), None
        for w in ws:
            for m, kws, kc, kt in idx.get(w, ()):
                if kc != c or kws != ws or (abs(m["close"] - pe) > 36 * 3600 and abs(m["close"] - pc) > 36 * 3600):
                    continue
                ov = len(pt & kt) / max(1, min(len(pt), len(kt)))
                if ov >= overlap and (not best or ov > best[0]):
                    best = (ov, m["t"])
        if best:
            out.append((p["id"], best[1]))
    return out


def cross_bets(pm, ptp, km, ktp, pairs, gap, side, window=1, extra=0.02, since=0):
    """Each hour: Kalshi's real Yes bid/ask (at most 6c apart) against Polymarket's last trade (at most 2 hours old,
    $5+ steps only). side "no": Polymarket Yes is `gap`+ above Kalshi's asking price -> buy No on Polymarket.
    side "yes": `gap`+ below Kalshi's buy order -> buy Yes. Price: the worst Polymarket trade of the next `window`
    hours (never less than the signal price) + extra + fee; a buy 15c+ dearer than the signal price is thrown out. One bet per market, $10."""
    import bisect
    import mentions
    first = {}
    for m in km.values():
        first[m["ev"]] = min(first.get(m["ev"], 1e18), m["close"])
    out = []
    for pid, kt in pairs:
        p, k, kv, pv = pm[pid], km[kt], ktp.get(kt), ptp.get(pid)
        if not kv or not pv or not kv["c"] or p.get("final") not in ([0.0, 1.0], [1.0, 0.0]):
            continue
        b = [x for x in pv["b"] if x[5] >= 5]
        bt_ = [x[0] for x in b]
        stop = min(first[k["ev"]], float(p["end"])) - 3600
        for c in kv["c"]:
            t = c[0]
            if t > stop:
                break
            if t < since or c[1] is None or c[2] is None or c[1] < 0.02 or c[2] > 0.98 or c[2] - c[1] > 0.06:
                continue
            i = bisect.bisect_right(bt_, t) - 1
            if i < 0 or t - bt_[i] > 7200 or not 0.10 <= b[i][2] <= 0.90:
                continue
            pp = b[i][2]
            if not (pp - c[2] >= gap if side == "no" else c[1] - pp >= gap):
                continue
            nx = [x for x in b[i + 1:i + 200] if t < x[0] <= t + window * 3600]
            if not nx:
                continue
            raw = 1 - min(x[3] for x in nx) if side == "no" else max(x[4] for x in nx)
            sig = 1 - pp if side == "no" else pp
            if raw - sig > 0.15 or raw + extra >= 0.99:
                continue
            px = max(raw, sig) + extra        # never cheaper than the price at the signal: a move our way came after we would have bought
            sh = 10 / px
            fee_ = bot.taker_fee(sh, px, p.get("fee") or 0)
            win = (p["final"][0] == 1.0) == (side == "yes")
            out.append({"ev": p["ev_slug"], "t": t, "cost": 10 + fee_, "pay": sh if win else 0.0, "pnl": (sh if win else 0.0) - 10 - fee_,
                        "title": p["q"], "kt": kt, "same": (k["res"] == "yes") == (p["final"][0] == 1.0)})
            break
    return out


def cross(score=True):
    """Section 4 of the report: is Kalshi's price a usable outside number for Polymarket's mention markets?"""
    import mentions
    pm, ptp = mentions.load()[:2]
    km, ktp = load()
    pairs = twins(pm, km)
    agree = sum((km[k]["res"] == "yes") == (pm[p].get("final") == [1.0, 0.0]) for p, k in pairs)
    L = ["", "## 4. Kalshi's price as the outside number for Polymarket's mention markets", "",
         f"{len(pairs):,} Polymarket mention markets have a Kalshi twin (same speech, same word list). The two sites settled the same way in {agree:,} of them.",
         "Each hour, where Polymarket's last trade was 5c / 10c / 15c away from Kalshi's real orders, buy Polymarket's side that Kalshi says is cheap,",
         "at the worst Polymarket trade of the next hour + 2c + fee.", "",
         "| what | bets | events | per $100 | luck range | first half / second half | exam |", "|---|---|---|---|---|---|---|"]
    for g in (0.05, 0.10, 0.15):
        for side in ("no", "yes"):
            b = cross_bets(pm, ptp, km, ktp, pairs, g, side)
            nm = f"Polymarket mentions vs Kalshi's price: buy {side.capitalize()} where Polymarket is {int(g * 100)}c+ {'above' if side == 'no' else 'below'} Kalshi"
            c = exam.score(b, nm, tries=20, src="kmentions.py cross, backtest/kmentions.md", status="dropped", log=score and g == 0.10, quiet=True)
            L.append(f"| buy {side.capitalize()}, {int(g * 100)}c+ apart | {len(b):,} | {c['events']:,} | {usd(c['per100'])} | {usd(c['lo100'])} to {usd(c['hi100'])} | "
                     f"{usd(c['half1'])} / {usd(c['half2'])} | {c['verdict']} |")
    L += ["", "Polymarket's mention prices already follow Kalshi's. Gaps of 10c+ are rare and buying them is a coin flip. Dropped.",
          "Traps: with a looser match (\"God or Evil\" on Polymarket against \"God\" on Kalshi) this looked like +$11 per $100, because Polymarket's wider word list is a different bet.",
          "And when Polymarket's price jumps 15c+ in the hour after the signal (the word was said), a bot would already have bought at the old price: pricing those bets at the new price, or dropping them, hides the losses (it looked like +$14 per $100)."]
    with open(OUT, "a") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


def wordno_split():
    """Where does the Polymarket word_no lead (mentions.rule_bets, since April 2026) come from? Splits its bets by
    whether Kalshi listed the same word for the same speech, the same speech only, or nothing we could match."""
    import mentions
    pm, ptp = mentions.load()[:2]
    km = (rj(MK, {}) or {}).get("markets") or {}
    tw = dict(twins(pm, km))
    evs = {pm[p]["ev_slug"] for p in tw}
    b = mentions.rule_bets(pm, ptp, mentions.Hist(pm), since=mentions.NEW_ERA)
    L = ["", "## 5. The Polymarket `word_no` lead, split by whether Kalshi lists the same thing", "",
         f"The {len(b)} history bets of `word_no` since April 2026 (`mentions.rule_bets`), sorted by what Kalshi had on offer.", "",
         "| group | bets | events | won | per $100 | luck range | exam |", "|---|---|---|---|---|---|---|"]
    for nm, f in (("Kalshi lists the same word for the same speech", lambda x: x["id"] in tw),
                  ("Kalshi has the speech, not this word", lambda x: x["id"] not in tw and x["ev"] in evs),
                  ("no Kalshi match found", lambda x: x["id"] not in tw and x["ev"] not in evs)):
        v = [x for x in b if f(x)]
        c = exam.score(v, nm, tries=90, log=False, quiet=True)
        L.append(f"| {nm} | {len(v)} | {c['events']} | {sum(1 for x in v if x['pay'] > 0)} | {usd(c['per100'])} | {usd(c['lo100'])} to {usd(c['hi100'])} | {c['verdict']} |")
    L += ["", "Where Kalshi lists the same word, `word_no` has no lead: Polymarket's price is kept honest there. Its history profit sits in markets",
          "without a Kalshi twin, above all \"what will Trump / Elon post this week\" and Big Brother episodes, plus two single events (the Xi and King Charles meetings).",
          "\"No Kalshi match found\" is not the same as \"Kalshi doesn't have it\": the matcher misses Kalshi's weekly and monthly Trump markets.",
          "So this is a warning about the live track, not a new rule: watch whether its live wins also come only from the post and TV-show markets."]
    with open(OUT, "a") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode.startswith("tapes-"):
        _, a, b = mode.split("-")
        do_tapes(int(a), int(b))
    else:
        {"list": do_list, "tapes": do_tapes, "run": lambda: (run(), cross(), wordno_split()), "split": wordno_split, "cross": cross, "dry": lambda: run(False)}[mode]()
