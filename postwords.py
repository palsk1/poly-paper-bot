#!/usr/bin/env python3
"""'What will Trump / Elon post this week' markets against the words they really post (2026-11-15). Research only.

PAPER ONLY. Reads public history, never trades, never writes state/.

The outside number: every post of the account with its text (Polymarket's own counter site xtracker). For each
listed word we count in how many of the earlier weeks it really showed up, and compare that with the price.

    python3 postwords.py fetch    # probe pw_fetch: every post with its text -> bt_cache/pw/posts_<handle>.json.gz
    python3 postwords.py run      # report backtest/postwords.md (markets and trades come from mentions.py's data)
"""
import collections
import gzip
import json
import os
import sys
import time

import bisect
import calendar
import datetime
import html
import re
from zoneinfo import ZoneInfo

import bot
import tweets

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "pw")
HANDLES = ("realDonaldTrump", "elonmusk")
X = tweets.X
ET = ZoneInfo("America/New_York")


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def fetch():
    for h in HANDLES:
        path = os.path.join(CACHE, f"posts_{h}.json.gz")
        seen = rj(path, {}) or {}
        a, now, shown = tweets.ts("2025-06-01T00:00:00"), int(time.time()), 0
        if seen:
            a = max(a, max(v["t"] for v in seen.values()) - 3 * 86400)
        while a < now:
            b = min(a + 10 * 86400, now + 86400)
            f = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))
            try:
                d = json.loads(tweets.raw(f"{X}/users/{h}/posts?startDate={f(a)}&endDate={f(b)}")).get("data") or []
            except Exception as e:
                print("  posts failed", h, f(a), str(e)[:120], flush=True)
                d = []
            for p in d:
                if shown < 3:
                    shown += 1
                    print("  sample", h, json.dumps(p)[:900], flush=True)
                try:
                    seen[str(p["id"])] = {"t": tweets.ts(p["createdAt"]), "seen": tweets.ts(p["importedAt"]) if p.get("importedAt") else None,
                                          "x": {k: v for k, v in p.items() if k not in ("createdAt", "importedAt", "id", "userId", "user")}}
                except Exception as e:
                    print("  bad post", str(e)[:80], flush=True)
            a = b
        wj(path, seen)
        ts_ = sorted(v["t"] for v in seen.values())
        mon = collections.Counter(time.strftime("%Y-%m", time.gmtime(t)) for t in ts_)
        print(f"{h}: {len(seen)} posts, by month {sorted(mon.items())}", flush=True)
        keys = collections.Counter(k for v in seen.values() for k in v["x"])
        print("  fields:", keys.most_common(20), flush=True)


MON = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}

def clean(c):
    c = re.sub(r"<br\s*/?>|</p>", " ", c or "")
    c = html.unescape(re.sub(r"<[^>]+>", "", c))
    return re.sub(r"\s+", " ", c).strip()

def posts(h):
    d = rj(os.path.join(CACHE, f"posts_{h}.json.gz"), {})
    out = []
    for v in d.values():
        x = clean(v["x"].get("content"))
        rt = x.startswith("RT @") or x.startswith("RT:") or x.startswith("RT ")
        x = re.sub(r"https?://\S+", " ", x)
        out.append((v["t"], x.lower().replace("’", "'"), rt, v.get("seen") or v["t"]))
    out.sort()
    return out

def handle(m):
    return "elonmusk" if "elon" in m["title"].lower() else "realDonaldTrump"

def window(m):
    g = re.search(r"between (\w+) (\d+), (\d{4}), 12:00 AM ET and (\w+) (\d+), (\d{4}), 11:59 PM ET", m["desc"])
    if not g: return None
    a = datetime.datetime(int(g[3]), MON[g[1].lower()], int(g[2]), tzinfo=ET)
    b = datetime.datetime(int(g[6]), MON[g[4].lower()], int(g[5]), 23, 59, 59, tzinfo=ET)
    return int(a.timestamp()), int(b.timestamp())

def rx(item):
    vs = [v.strip().lower().replace("’", "'") for v in item.split(" / ") if v.strip()]
    pat = "|".join(re.escape(v).replace(r"\ ", r"[\s\-]+") for v in vs)
    return re.compile(r"(?<![a-z0-9])(?:" + pat + r")(?:s|es|'s|s')?(?![a-z0-9])")

class Said:
    """times (own posts only) at which a term showed up"""
    def __init__(self):
        self.P = {h: posts(h) for h in HANDLES}
        self.Pt = {h: [p[0] for p in self.P[h]] for h in HANDLES}
        self.c = {}
    def times(self, h, item):
        k = (h, item)
        if k not in self.c:
            r = rx(item)
            self.c[k] = [(t, seen) for t, x, rt, seen in self.P[h] if not rt and r.search(x)]
        return self.c[k]
    def first_in(self, h, item, a, b):
        for t, seen in self.times(h, item):
            if a <= t <= b: return t
        return None

WEEK = 7 * 86400
def qweek(S, h, item, w0, n=8, k0=1.0, k1=2.0):
    """share of the n weeks before w0 in which the term showed up in own posts"""
    ts = [t for t, _ in S.times(h, item)]
    P = S.Pt[h]
    k = tot = 0
    for i in range(1, n + 1):
        a, b = w0 - i * WEEK, w0 - (i - 1) * WEEK
        if bisect.bisect_left(P, b) - bisect.bisect_left(P, a) < 30:
            continue
        tot += 1
        j = bisect.bisect_left(ts, a)
        k += j < len(ts) and ts[j] < b
    return (k + k0) / (tot + k1), k, tot

def looks(S, sel, tp, hs=("realDonaldTrump", "elonmusk")):
    """every 5-minute step with trades before the term was posted (as far as our text shows) and before the week's end"""
    for m in sel:
        w = window(m); h = handle(m); r = tp.get(str(m["id"]))
        if not w or not r or h not in hs or m["final"] not in ([1.0, 0.0], [0.0, 1.0]):
            continue
        said = S.first_in(h, m["item"], *w)
        stop = min(w[1], m["closed_t"] or w[1], said or 9e18)
        qw, k, tot = qweek(S, h, m["item"], w[0])
        b = r["b"]
        for i in range(len(b) - 1):
            t = b[i][0] + 300
            if t >= stop: break
            f = min(1.0, (w[1] - t) / (w[1] - w[0]))
            q = 1 - (1 - qw) ** f
            yield m, h, w, i, t, b, q, qw, k, tot, f

def bets(S, sel, tp, gap=0.15, side=1, plo=0.0, phi=1.0, extra=0.02, hold=7200, hs=("realDonaldTrump", "elonmusk"), min_tot=4, phase=None, stake=10.0, crumb=5.0, n=8):
    out = []; done = set()
    for m, h, w, i, t, b, q, qw, k, tot, f in looks(S, sel, tp, hs):
        if m["id"] in done or tot < min_tot or b[i][5] < crumb: continue
        p = b[i][2]
        if not plo <= p <= phi: continue
        if phase == "pre" and t >= w[0]: continue
        if phase == "in" and t < w[0]: continue
        d = (p - q) if side == 1 else (q - p)
        if d < gap: continue
        nx = [y for y in b[i + 1:] if y[0] - t <= hold and y[5] >= crumb]
        if not nx: continue
        if side == 1: px = max(max(1 - y[3] for y in nx), 1 - p)
        else: px = max(max(y[4] for y in nx), p)
        c = min(0.99, px + extra)
        sh = stake / c
        fee = bot.taker_fee(sh, c, m.get("fee") or 0)
        win = (m["final"][0] == 1.0) == (side == 0)
        done.add(m["id"])
        out.append({"ev": m["ev_slug"], "t": nx[0][0], "cost": stake + fee, "pay": sh if win else 0.0, "id": m["id"], "px": c, "sig": p, "fair": q,
                    "item": m["item"], "h": h, "k": k, "tot": tot, "f": f, "w0": w[0]})
    return out

def per100(b):
    c = sum(x["cost"] for x in b)
    return (sum(x["pay"] for x in b) - c) / c * 100 if c else 0
def show(name, b):   # one table row
    b = sorted(b, key=lambda x: x["t"]); hlf = len(b) // 2
    if len(b) < 10:
        return f"| {name} | {len(b)} | - | - | - | - | - |"
    return (f"| {name} | {len(b)} | {len({x['ev'] for x in b})} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b))} | "
            f"{usd(per100(b[:hlf]))} | {usd(per100(b[hlf:]))} |")


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


HEAD = "| what | bets | weeks | won | per $100 | first half | second half |\n|---|---|---|---|---|---|---|"
TRIES = 40
RULE = dict(gap=0.15, side=1, plo=0.20, phi=0.60)


def load():
    import mentions
    ms, tp = mentions.load()
    sel = [m for m in ms.values() if "post this week" in (m.get("title") or "").lower() and window(m)]
    return sel, {str(m["id"]): tp[m["id"]] for m in sel if m["id"] in tp}


def run(score=True):
    import exam
    sel, tp = load()
    S = Said()
    L = []
    P = L.append
    P("# 'What will Trump / Elon post this week' vs the words they really post (postwords.py)\n")
    P(f"Generated {bot.iso()}. {len(sel)} finished markets in {len({m['ev_slug'] for m in sel})} weeks (Feb to Nov 2026), "
      f"{len(tp)} with real trades. Outside number: every post with its text from Polymarket's own counter site "
      f"(Trump {len(S.P['realDonaldTrump'])} posts since Jan 2026, Elon {len(S.P['elonmusk'])} since Nov 2025). Paper only.\n")
    P("## 1. Can we read the result off the post text?\n")
    c = collections.Counter()
    for m in sel:
        h = handle(m)
        c[(h, m["final"][0] == 1.0, S.first_in(h, m["item"], *window(m)) is not None)] += 1
    P("| account | Yes and we found the word | Yes but we did not | No and we found nothing | No but we found it |\n|---|---|---|---|---|")
    for h in HANDLES:
        P(f"| {h} | {c[(h, True, True)]} | {c[(h, True, False)]} | {c[(h, False, False)]} | {c[(h, False, True)]} |")
    P("\nTrump: when the text shows the word, the market always paid Yes. But 1 Yes in 4 we never see: a third of his posts "
      "are pictures or videos with no text, and words in pictures count. Elon: the counter site leaves out his replies "
      "(they count for the market) and mixes in the text of posts he quotes (it does not count), so his text is a rough guide only.\n")
    P("## 2. Is there time to buy after the word is posted?\n")
    n = cheap = 0
    usd_cheap = 0.0
    for m in sel:
        h = handle(m)
        r = tp.get(str(m["id"]))
        if h != "realDonaldTrump" or not r:
            continue
        ts = [(t, seen) for t, seen in S.times(h, m["item"]) if window(m)[0] <= t <= window(m)[1]]
        if not ts:
            continue
        n += 1
        know = max(ts[0]) + 60
        x = [b for b in r["b"] if b[0] >= know and b[4] < 0.93]
        cheap += bool(x)
        usd_cheap += sum(b[5] for b in x)
    P(f"No. In {n} Trump markets where our text shows the word, only {cheap} had any trade under 93c from a minute after the "
      f"counter site showed the post, ${usd_cheap:.0f} in total. The counter site is 2-3 minutes behind and the price is "
      "already at 95c+ by then. A speed game we don't play.\n")
    P("## 3. Does the word record beat the price?\n")
    P("Model: in how many of the 8 weeks before did the word show up in the account's own posts (pulled a little toward the "
      "middle), shrunk as the week runs out without the word. Looks only at posts from before the bet.\n")
    P("Bets: $10 each, one per market, at a 5-minute step with $5+ traded and before our text shows the word. Price paid: "
      "the worst price of the next 2 hours, never better than the price at the signal, + 2c + fee.\n")
    P(HEAD)
    B = lambda **kw: bets(S, sel, tp, **kw)
    main = B(**RULE)
    P(show("always Yes", B(gap=-9, side=0)))
    P(show("always No", B(gap=-9, side=1)))
    P(show("No where Yes is 15c+ above the record, any price", B(gap=0.15, side=1)))
    P(show("No where Yes is 15c+ above the record, Yes at 60c+", B(gap=0.15, side=1, plo=0.6)))
    P(show("**No where Yes is 15c+ above the record, Yes at 20-60c**", main))
    P(show("same price band, no word record (always No at 20-60c)", B(gap=-9, side=1, plo=0.2, phi=0.6)))
    P(show("... gap 10c+", B(gap=0.10, side=1, plo=0.2, phi=0.6)))
    P(show("... gap 20c+", B(gap=0.20, side=1, plo=0.2, phi=0.6)))
    P(show("... gap 30c+", B(gap=0.30, side=1, plo=0.2, phi=0.6)))
    P(show("... Trump only", B(hs=("realDonaldTrump",), **RULE)))
    P(show("... Elon only", B(hs=("elonmusk",), **RULE)))
    P(show("... bought before the week starts", B(phase="pre", **RULE)))
    P(show("... bought during the week", B(phase="in", **RULE)))
    P(show("... 4c extra instead of 2c", B(extra=0.04, **RULE)))
    P(show("... 6c extra", B(extra=0.06, **RULE)))
    P(show("... worst price of the next 30 minutes", B(hold=1800, **RULE)))
    P(show("... worst price of the next 6 hours", B(hold=21600, **RULE)))
    P(show("Yes where the record is 15c+ above the price", B(gap=0.15, side=0)))
    P("\nBy quarter (the bold rule):\n\n" + HEAD)
    q = collections.defaultdict(list)
    for x in main:
        g = time.gmtime(x["t"])
        q[f"{g.tm_year} Q{(g.tm_mon - 1) // 3 + 1}"].append(x)
    for k in sorted(q):
        P(show(k, q[k]))
    P("\nBiggest wins and losses by word (the bold rule): " + ", ".join(
        f"{k} {usd(v)} ({n_})" for k, n_, v in sorted(((k, len(v), sum(y['pay'] - y['cost'] for y in v)) for k, v in
        collections.defaultdict(list, {i: [x for x in main if x['item'] == i] for i in {x['item'] for x in main}}).items()),
        key=lambda z: -z[2])[:5]) + " ... " + ", ".join(
        f"{k} {usd(v)} ({n_})" for k, n_, v in sorted(((i, len([x for x in main if x['item'] == i]),
        sum(x['pay'] - x['cost'] for x in main if x['item'] == i)) for i in {x['item'] for x in main}), key=lambda z: z[2])[:5]) + ".\n")
    card = exam.score(main, "Post-word markets: No where Yes 15c+ above the text record (20-60c)", tries=TRIES, src="postwords.py",
                      status="dropped", log=score, quiet=True)
    P("## 4. The shared exam\n")
    P(f"Bold rule: **{card['verdict']}**. {card.get('plain') or ''}\n")
    P("## What it means\n")
    P("The word record helps a little: in the 20-60c band, always No loses about $4 per $100 and No only where the record "
      "disagrees makes about $6. But the band was picked after looking, Trump alone is about even, the profit is gone at "
      "6c extra cost, and the live track `word_no` already bets on these markets with a similar idea. Not enough for a new "
      "track. Dropped.\n")
    out = os.path.join(ROOT, "backtest", "postwords.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    {"fetch": fetch, "run": run, "dry": lambda: run(False)}[a]()
