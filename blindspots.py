#!/usr/bin/env python3
"""Blind spots in our research (2026-11-27, Jan: "look outside areas I have maybe missed"). RESEARCH ONLY, PAPER ONLY.

A fresh-eyes list of the kinds of edge we never tried (report: backtest/blindspots.md), and tests of the three that
the papers and trader write-ups rated best and that our data can answer:

  1. "Nothing ever happens", by question type (LessWrong 16 Nov 2026): one-off "will X happen by <date>" questions,
     where nothing changing means No. Buy No at Yes 30-70c a day / a week after the first trade. Yardstick: the same
     rule on every other worded (non-number) market, so we see if the question type adds anything.
  2. Late jumps before a fixed announcement (awards, Nobel, picks, "named"): insiders leak, so follow a candidate
     that rose 10c+ in 12 hours in the last 2.5 days before the result. Yardstick: the same on every other market.
  3. Weather favourites too dear on the day (Qiu & Qiu 2026, arXiv 2610.13593): buy No on the Polymarket
     temperature bucket priced 75-95c, 0-8 hours after the local day starts (7-15 hours before the usual peak).

    python3 blindspots.py chart     # all three at chart prices (+1-2c), offline (bt_cache + wx_cache)
    python3 blindspots.py real      # test 1 at REAL prices (exam.fills, needs the trade tape) + exam lines
  From GitHub: probe what = bs_chart / bs_real.
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import random
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
DAY = 86400

# ---------------------------------------------------------------- data
_D = {}


def poly():
    if "m" not in _D:
        import ideas
        m, h, _ = ideas.load_full()
        _D["m"], _D["h"] = m, h
    return _D["m"], _D["h"]


def rj(p):
    with gzip.open(os.path.join(ROOT, p)) as f:
        return json.load(f)


def final_ok(m):
    return (not m.get("sports")) and m.get("closed") and m.get("final") and m["final"][0] in (0.0, 1.0)


def summ(b, label):
    """quick chart-price line: bets, events, per $100, event-mean +- 90% range, halves."""
    if not b:
        print(f"{label}: none")
        return
    c = sum(x["cost"] for x in b)
    p = sum(x["pay"] for x in b)
    g = collections.defaultdict(lambda: [0.0, 0.0])
    for x in b:
        g[x["ev"]][0] += x["cost"]
        g[x["ev"]][1] += x["pay"]
    r = [(pp - cc) / cc * 100 for cc, pp in g.values()]
    se = statistics.pstdev(r) / math.sqrt(len(r)) if len(r) > 1 else 0
    s = sorted(b, key=lambda x: x["t"])
    k = len(s) // 2
    hv = [100 * (sum(x["pay"] for x in q) - sum(x["cost"] for x in q)) / max(1e-9, sum(x["cost"] for x in q)) for q in (s[:k], s[k:])]
    print(f"{label}: bets {len(b)} groups {len(g)} won {sum(1 for x in b if x['pay'] > 0)} avg price "
          f"{statistics.mean(x['q'] for x in b):.2f} | per $100 {100 * (p - c) / c:+.2f} | group mean {statistics.mean(r):+.2f}"
          f" +-{1.645 * se:.2f} | halves {hv[0]:+.1f} / {hv[1]:+.1f}")


def bet(m, side, q, t, ev):
    """$25 at chart price q (+ slip already in q) on outcome `side` (0 = Yes, 1 = No)."""
    fee = (m.get("fee") or 0) * q * (1 - q)
    sh = 25 / (q + fee)
    return dict(ev=ev, t=t, cost=25.0, pay=sh * (m["final"][side] == 1.0), q=q, mid=m["id"], qq=m.get("q", ""),
                side=side, toks=m.get("toks"), fee=m.get("fee") or 0)


# ---------------------------------------------------------------- 1. nothing ever happens, by question type
CHG = re.compile(r"\b(by|before|in 202\d|this year|this month|this week)\b", re.I)
ACT = re.compile(r"\b(happen|announce|launch|release|resign|out as|leave|ceasefire|strike|invade|meet|sign|pass|approve|ban|"
                 r"arrest|indict|acquire|ipo|visit|declare|recogni|join|withdraw|impeach|fire|nominate|confirm|deal|agree|"
                 r"test|attack|capture|end the|win the|become|reach|hit|elected|win|cut|raise|hike|close|open|return|split|"
                 r"divorce|marry|die|pardon|sanction|tariff|lawsuit|sue|charged|convicted|sentenced|shutdown|default)\w*", re.I)
SQ = re.compile(r"\b(remain|stay|still|continue|keep|retain|not |no longer|hold on|survive)\w*", re.I)
NUM = re.compile(r"(\$|above|below|between|less than|more than|greater|at least|or more|or less|°|temperature|price|bitcoin|"
                 r"btc|eth|solana|xrp|nasdaq|s&p|tweets|posts|views|up or down|close at|ranked|#\d|top \d| o/u|spread|vs\.?)", re.I)


def label(q):
    """'no' = No if nothing changes, 'yes' = Yes if nothing changes, 'num' = number market, None = other worded."""
    if NUM.search(q):
        return "num"
    if SQ.search(q):
        return "yes"
    if CHG.search(q) and ACT.search(q):
        return "no"
    return None


def nothing(want="no", day=1, lo=0.30, hi=0.70, slip=0.02, minleft=3):
    m_all, h = poly()
    out = []
    for mid, m in m_all.items():
        if not final_ok(m) or (m.get("outs") or ["Yes"])[0] != "Yes" or label(m.get("q", "")) != want:
            continue
        hh = h.get(mid)
        if not hh or not hh[0]:
            continue
        T, P = hh
        for t, p in zip(T, P):
            if t < T[0] + day * DAY:
                continue
            if t > m["end"] - minleft * DAY:
                break
            if lo <= p <= hi:
                side = 0 if want == "yes" else 1      # bet on "nothing changes" (for the yardsticks: No)
                q = (p if side == 0 else 1 - p) + slip
                out.append(bet(m, side, q, t, m.get("ev") or mid))
            break
    return out


# ---------------------------------------------------------------- 2. late jumps before announcements
ANN = re.compile(r"(oscar|academy award|grammy|emmy|golden globe|sag award|actor award|bafta|nobel|ballon|heisman|cy young|"
                 r"rookie of the year|\bmvp\b|person of the year|word of the year|year in search|most searched|nominat|announce|"
                 r"\bpick\b|named |be chosen|selected|eurovision|pope|cabinet|secretary of|chair|vp pick|running mate|wrapped|"
                 r"time 100|coach of the year|player of the year|best picture|winner of the)", re.I)
SPORTY = re.compile(r"( vs\.? | o/u |spread|total|points|goals)", re.I)


def jumps(kind="ann", rise=0.10, lo=0.15, hi=0.80, win=12, lag=1, slip=0.01, lastdays=2.5):
    m_all, h = poly()
    out = []
    for mid, m in m_all.items():
        if not final_ok(m):
            continue
        txt = (m.get("q", "") + " " + (m.get("ev_slug") or "")).replace("-", " ")
        a = bool(ANN.search(txt)) and not SPORTY.search(txt)
        if (kind == "ann") != a:
            continue
        hh = h.get(mid)
        if not hh or not hh[0]:
            continue
        T, P = hh
        ct = m.get("closed_t") or m["end"]
        for i in range(len(T) - 1 - lag):
            t, p = T[i], P[i]
            if t < ct - lastdays * DAY or not (lo <= p <= hi):
                continue
            j = i
            while j > 0 and T[j] > t - win * 3600:
                j -= 1
            if not (win * 1800 <= t - T[j] <= win * 3600 * 1.6) or p - P[j] < rise:
                continue
            if T[i + lag] - t > 3 * 3600:
                continue
            q = P[i + lag] + slip          # bought at the NEXT hourly price, not the one that showed the jump
            if q < 0.99:
                out.append(bet(m, 0, q, T[i + lag], m.get("ev") or mid))
            break
    return out


# ---------------------------------------------------------------- 3. weather favourites on the day
def weather(kind="high", hr=3, lo=0.75, hi=0.95, slip=0.01, side=1):
    ev = rj("wx_cache/poly_events_v2.json.gz")
    ph = rj("wx_cache/poly_hist.json.gz")
    HB = 62                                     # wxcast.HOURS_BEFORE: the hourly grid starts 62 h before the local day
    out = []
    for e in ev.values():
        if e["kind"] != kind:
            continue
        best = None
        for m in e["ms"]:
            g = ph.get(m["id"])
            k = HB + hr
            if g and k < len(g) and g[k] is not None and lo <= g[k] <= hi and (best is None or g[k] > best[0]):
                best = (g[k], m)
        if not best:
            continue
        p, m = best
        q = (1 - p if side == 1 else p) + slip
        mm = dict(id=m["id"], fee=m.get("fee"), final=[float(m["y"] == 1), float(m["y"] == 0)], toks=[m.get("tok"), None])
        out.append(bet(mm, side, q, e["s"] + hr * 3600, e["day"]))     # one group per day: same-day weather is linked
    return out


# ---------------------------------------------------------------- commands
def chart():
    print("== 1. Nothing ever happens, by question type (chart price + 2c, hold to the end)")
    cnt = collections.Counter(label(m.get("q", "")) for m in poly()[0].values() if not m.get("sports"))
    print("labels:", dict(cnt))
    for day in (1, 7, 30):
        for lo, hi in ((0.30, 0.70), (0.10, 0.30), (0.70, 0.90)):
            summ(nothing("no", day, lo, hi), f"No if nothing changes, day {day}, Yes {lo}-{hi}")
    for want, nm in ((None, "other worded markets"), ("num", "number markets")):
        for day in (1, 7):
            summ(nothing(want, day), f"YARDSTICK {nm}, buy No, day {day}, Yes 0.3-0.7")
    for day in (1, 7):
        summ(nothing("yes", day), f"Yes if nothing changes, buy Yes, day {day}, Yes 0.3-0.7")
    print("\n== 2. Late jumps before an announcement (next hourly price + 1c)")
    for kind in ("ann", "other"):
        for rise in (0.08, 0.10, 0.15, 0.25):
            for lag in (1, 2):
                summ(jumps(kind, rise, lag=lag), f"{kind}: rose {rise:.2f} in 12h, bought {lag}h later")
    print("\n== 3. Weather favourites on the day (Polymarket temperature buckets, chart price + 1c)")
    for kind in ("high", "low"):
        for hr in (0, 3, 6, 8):
            for lo, hi in ((0.60, 0.75), (0.75, 0.95)):
                for side, nm in ((1, "buy No"), (0, "buy Yes")):
                    summ(weather(kind, hr, lo, hi, side=side), f"{kind}, {hr}h into the day, fav {lo}-{hi}, {nm}")


def real():
    """Re-price the leads at REAL prices: first real buy within 3 h + 1c + fee (exam.fills). Prints exam cards and
    the bets (BETS_JSON lines) so the ledger can be filled offline from the log."""
    import exam
    random.seed(7)
    jobs = [("nothing_no", "'Nothing ever happens' by question type: buy No, Yes 30-70c a day in", nothing("no", 1), 15),
            ("nothing_yard", "Yardstick: buy No on every other worded market, Yes 30-70c a day in", nothing(None, 1), 15),
            ("wx_low8", "Weather lows: buy Yes on the 60-75c favourite 8 h into the local day (found by looking)",
             weather("low", 8, 0.60, 0.75, side=0), 64),
            ("wx_low8b", "Weather lows: buy Yes on the 75-95c favourite 8 h into the local day (found by looking)",
             weather("low", 8, 0.75, 0.95, side=0), 64),
            ("wx_low6", "Weather lows: buy Yes on the 60-75c favourite 6 h into the local day (found by looking)",
             weather("low", 6, 0.60, 0.75, side=0), 64)]
    for key, name, sig, tries in jobs:
        if len(sig) > 900:
            sig = random.sample(sig, 900)
        slip = 0.02 if key.startswith("nothing") else 0.01
        signals = [dict(id=b["mid"], oi=b["side"], t=b["t"], pay=1.0 if b["pay"] > 0 else 0.0, ev=b["ev"], q=round(b["q"] - slip, 4),
                        fee=b["fee"], toks=b["toks"] if b["toks"] and b["toks"][-1] else None) for b in sig]
        print(f"\n== {name}: {len(signals)} signals")
        info = {}
        bets = exam.fills(signals, extra=0.01, info=info)
        exam.score(bets, name + ", real prices", tries=tries, src="blindspots.py real", note=json.dumps(info), log=False)
        print("BETS_JSON", json.dumps({"key": key, "name": name, "tries": tries, "info": info, "bets": bets}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "chart"
    {"chart": chart, "real": real}[cmd]()
