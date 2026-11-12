#!/usr/bin/env python3
"""Post-count markets ("Will Elon Musk post 90-114 tweets from ... to ...?"): a counting model vs Polymarket's price.

  python3 tweets.py peek     what the counter site (xtracker, the settle source) gives us
  python3 tweets.py run      the test -> backtest/tweets.md
  python3 tweets.py fetch    counter windows, post times and real trades -> bt_cache/tw/
"""
import bisect
import calendar
import collections
import concurrent.futures as cf
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.request

import backtest as bt
import bot
import btcheck

X = "https://xtracker.polymarket.com/api"


def raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def peek():
    urls = [f"{X}/users", f"{X}/users/elonmusk", f"{X}/users/elonmusk?platform=X", f"{X}/trackings", f"{X}/trackings?activeOnly=false",
            f"{X}/users/elonmusk/trackings", f"{X}/users/elonmusk/posts?startDate=2026-11-01&endDate=2026-11-03",
            f"{X}/users/elonmusk/posts?startDate=2026-03-01T00:00:00.000Z&endDate=2026-03-02T00:00:00.000Z",
            f"{X}/users/elonmusk/posts", f"{X}/metrics/elonmusk?type=daily&startDate=2026-03-01&endDate=2026-03-10",
            f"{X}/posts?handle=elonmusk&startDate=2026-11-01&endDate=2026-11-02", "https://xtracker.polymarket.com/"]
    seen = {}
    for u in urls:
        try:
            t = raw(u)
            print(f"\n== {u}\n   {len(t)} chars: {t[:1500]}", flush=True)
            seen[u] = t
        except Exception as e:
            print(f"\n== {u}\n   FAILED {str(e)[:200]}", flush=True)
    # follow ids found in the answers
    try:
        d = json.loads(seen.get(f"{X}/users/elonmusk") or "{}")
        d = d.get("data", d)
        uid = d.get("id")
        tr = d.get("trackings") or []
        print("\nuser id", uid, "trackings", len(tr), json.dumps(tr[:3])[:800])
        for u in ([f"{X}/metrics/{uid}?type=daily&startDate=2026-03-01&endDate=2026-03-10",
                   f"{X}/metrics/{uid}?type=hourly&startDate=2026-03-01&endDate=2026-03-03"] if uid else []) + \
                 [f"{X}/trackings/{t.get('id')}?includeStats=true" for t in tr[:2]]:
            try:
                t = raw(u)
                print(f"\n== {u}\n   {len(t)} chars: {t[:2500]}", flush=True)
            except Exception as e:
                print(f"\n== {u}\n   FAILED {str(e)[:200]}", flush=True)
    except Exception as e:
        print("follow failed", e)



# ================================================================ data
CACHE = os.path.join(bt.CACHE, "tw")
T0 = time.time()
BUDGET_MIN = float(os.environ.get("TW_MIN", "200"))
WORKERS = int(os.environ.get("TW_WORKERS", "8"))
NUM = r"(\d[\d,]*)"
UNIT = r"(?:Truth Social )?(?:tweets|posts|times)"


def bucket(q):
    """The count range in a market's title: (low, high) both included; high = 10**9 for "240+"."""
    n = lambda x: int(x.replace(",", ""))
    g = re.search(rf"(?:post|tweet|have) (?:between )?{NUM}\s*(?:-|–|to|and)\s*{NUM} {UNIT}", q)
    if g:
        return n(g.group(1)), n(g.group(2))
    g = re.search(rf"(?:post|tweet) (?:<|less than |fewer than |under ){NUM}", q)
    if g:
        return 0, n(g.group(1)) - 1
    g = re.search(rf"(?:post|tweet) {NUM}(?:\+| or more| or greater)", q)
    if g:
        return n(g.group(1)), 10 ** 9
    g = re.search(rf"(?:post|tweet) (?:more than |over |>){NUM}", q)
    if g:
        return n(g.group(1)) + 1, 10 ** 9
    return None


def pick_markets(markets):
    out = {}
    for m in markets.values():
        q = m.get("q") or ""
        if not re.search(r"^Will .+ (post|tweet|have) ", q) or not re.search(r"\b(tweets?|posts?|times)\b", q, re.I):
            continue
        b = bucket(q)
        if not b or not m.get("toks") or not m.get("ev_slug"):
            continue
        out[m["id"]] = dict(m, lo=b[0], hi=b[1])
    return out


def ts(iso):
    return int(calendar.timegm(time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")))


def order_key(ev):
    return hashlib.md5(("tw" + str(ev)).encode()).hexdigest()


def fetch():
    """Counter windows (trackings), every post's time (when posted, when the counter saw it; no text) and trade lists."""
    import ideas, informed, optfair
    os.makedirs(CACHE, exist_ok=True)
    tr = json.loads(raw(f"{X}/trackings?activeOnly=false"))["data"]
    rows, handles = [], {}
    for t in tr:
        u = t.get("user") or {}
        slug = (t.get("marketLink") or "").rstrip("/").split("/")[-1]
        if not slug or not u.get("handle"):
            continue
        rows.append({"id": t["id"], "handle": u["handle"], "platform": u.get("platform"), "title": t.get("title"),
                     "start": ts(t["startDate"]), "end": ts(t["endDate"]), "slug": slug})
        handles[u["handle"]] = u.get("platform")
    bt.wjson(os.path.join(CACHE, "trackings.json.gz"), rows)
    print(f"counter windows: {len(rows)}, accounts: {handles}", flush=True)
    posts = {}
    for h in handles:
        seen = {}
        day0, now = ts("2025-11-01T00:00:00"), int(time.time())
        a = day0
        while a < now:
            b = min(a + 20 * 86400, now + 86400)
            u = f"{X}/users/{h}/posts?startDate={time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(a))}&endDate={time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(b))}"
            try:
                d = json.loads(raw(u)).get("data") or []
            except Exception as e:
                print("  posts failed", h, str(e)[:100], flush=True)
                d = []
            for p in d:
                try:
                    seen[p["id"]] = [ts(p["createdAt"]), ts(p["importedAt"]) if p.get("importedAt") else ts(p["createdAt"])]
                except Exception:
                    pass
            a = b
        posts[h] = sorted(seen.values())
        v = posts[h]
        print(f"  {h}: {len(v)} posts, first {time.strftime('%Y-%m-%d', time.gmtime(v[0][0])) if v else '-'}, "
              f"last {time.strftime('%Y-%m-%d', time.gmtime(v[-1][0])) if v else '-'}", flush=True)
    bt.wjson(os.path.join(CACHE, "posts.json.gz"), posts)
    markets, _, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m.get("final")}
    slugs = {r["slug"] for r in rows}
    print(f"markets: {len(ms)}, events: {len({m['ev_slug'] for m in ms.values()})}, "
          f"with a counter window: {len({m['ev_slug'] for m in ms.values() if m['ev_slug'] in slugs})}", flush=True)
    path = os.path.join(CACHE, "tapes.json.gz")
    have = bt.rjson(path, {}) or {}
    todo = [k for k in ms if k not in have]
    for i in range(0, len(todo), 400):
        chunk = todo[i:i + 400]
        cids = informed.cids_for(chunk)
        jobs = [(ms[k], cids[k]) for k in chunk if cids.get(k)]
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for mid, r in ex.map(optfair.fetch_tape, jobs):
                if r is not None:
                    have[mid] = r
        bt.wjson(path, have)
        print(f"  tapes {len(have)}/{len(ms)} ({(time.time() - T0) / 60:.0f} min), cut short {sum(1 for r in have.values() if r['cut'])}", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break
    print(f"tapes saved: {len(have)}")



# ================================================================ the counting model
def nb_cdf(m, v, n_max):
    """Running total of a spread-out count curve (negative binomial) with average m and variance v, for 0..n_max."""
    if m <= 0:
        return [1.0] * (n_max + 1)
    v = max(v, m * 1.02)
    r = m * m / (v - m)
    p = r / (r + m)
    out, acc = [], 0.0
    lp, l1 = math.log(p), math.log(1 - p)
    for k in range(n_max + 1):
        acc += math.exp(math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1) + r * lp + k * l1)
        out.append(min(1.0, acc))
    return out


class Counter:
    """One account's posts: when posted (c) and when the counter showed them (i)."""
    def __init__(self, rows):
        self.c = [r[0] for r in rows]
        self.rows = rows

    def between(self, a, b):
        return bisect.bisect_right(self.c, b) - bisect.bisect_left(self.c, a)

    def seen(self, a, t):
        """Posts made since a that the counter was already showing at t."""
        i, j = bisect.bisect_left(self.c, a), bisect.bisect_right(self.c, t)
        return sum(1 for k in range(i, j) if self.rows[k][1] <= t)


def forecast(cn, start, end, t, weeks=8, widen=1.0, recent=0.0):
    """Count so far (as the counter showed it at t) and the average / variance of what is still to come, from what the
    same stretch of the week brought in the last `weeks` weeks that are fully in the past."""
    a = max(t, start)
    n0 = cn.seen(start, t) if t > start else 0
    xs, k = [], 1
    while len(xs) < weeks and k < 60:
        if end - 7 * 86400 * k <= t:
            if a - 7 * 86400 * k < cn.c[0]:
                break
            xs.append(cn.between(a - 7 * 86400 * k, end - 7 * 86400 * k))
        k += 1
    if len(xs) < 3:
        return None
    m = sum(xs) / len(xs)
    if recent:
        # lean toward the pace of the last 3 days compared with the same 3 days in those weeks
        r3 = cn.between(t - 3 * 86400, t)
        b3 = [cn.between(t - 3 * 86400 - 7 * 86400 * j, t - 7 * 86400 * j) for j in range(1, len(xs) + 1)]
        base = sum(b3) / len(b3)
        if base > 5:
            m *= (1 - recent) + recent * min(3.0, max(0.33, r3 / base))
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1) * (1 + 1 / len(xs)) * widen
    return n0, m, max(v, m)


def load():
    import ideas
    markets, _, _ = ideas.load_full()
    ms = pick_markets(markets)
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut and m.get("final") and m["final"][0] in (0.0, 1.0)}
    tr = {r["slug"]: r for r in bt.rjson(os.path.join(CACHE, "trackings.json.gz"), []) or []}
    posts = {h: Counter(v) for h, v in (bt.rjson(os.path.join(CACHE, "posts.json.gz"), {}) or {}).items() if v}
    tp = bt.rjson(os.path.join(CACHE, "tapes.json.gz"), {}) or {}
    evs = collections.defaultdict(list)
    for m in ms.values():
        if m["ev_slug"] in tr and m["id"] in tp and tr[m["ev_slug"]]["handle"] in posts:
            evs[m["ev_slug"]].append(m)
    return evs, tr, posts, tp


STEP = 1800


def tbets(evs, tr, posts, tp, gap=0.05, lo=0.03, hi=0.97, min_left=3600, max_left=30 * 86400, sides=(0, 1), extra=0.01,
          stake=10.0, weeks=8, widen=1.0, recent=0.0, handles=None, looks=None, first_only=True, started=None, always=None):
    """Every 30 minutes: the model's chance for each bucket vs the last real trade of the past 30 minutes. 5c+ apart ->
    buy the cheap side at the first real trade of the next 30 minutes, + `extra` + fee. One bet per market."""
    out = []
    for slug, mk in evs.items():
        r = tr[slug]
        if handles and r["handle"] not in handles:
            continue
        cn = posts[r["handle"]]
        start, end = r["start"], r["end"]
        B = {m["id"]: tp[m["id"]]["b"] for m in mk}
        ptr = {k: 0 for k in B}
        done = set()
        t = min((b[0][0] for b in B.values() if b), default=end) // STEP * STEP + STEP
        while t <= end - min_left:
            left = end - t
            if left > max_left or (started is not None and (t >= start) != started):
                t += STEP
                continue
            f = forecast(cn, start, end, t, weeks, widen, recent)
            if f is None:
                t += STEP
                continue
            n0, m_, v_ = f
            top = int(m_ + 8 * math.sqrt(v_) + 10)
            cdf = None
            for m in mk:
                mid = m["id"]
                if mid in done:
                    continue
                b = B[mid]
                i = ptr[mid]
                while i < len(b) and b[i][0] + 300 <= t:
                    i += 1
                ptr[mid] = i
                if i == 0 or b[i - 1][0] < t - STEP or i >= len(b) or b[i][0] >= t + STEP or b[i][0] >= end:
                    continue
                p = b[i - 1][2]
                if not lo <= p <= hi:
                    continue
                if cdf is None:
                    cdf = nb_cdf(m_, v_, top)
                F = lambda x: 0.0 if x < 0 else cdf[min(x, top)]
                q = F(m["hi"] - n0) - F(m["lo"] - n0 - 1)
                if looks is not None:
                    looks.append((slug, mid, t, q, p, m["final"][0], left))
                side = 0 if q - p >= gap else 1 if p - q >= gap else None
                if always is not None:
                    side = always            # a yardstick: always buy this side, whatever the model says
                if side is None or side not in sides:
                    continue
                y = b[i]
                px = y[1] if side == 0 else 1 - y[1]
                c = min(0.99, px + extra)
                if c <= 0.01:
                    continue
                sh = stake / c
                fee = bot.taker_fee(sh, c, m.get("fee") or 0)
                win = (m["final"][0] == 1.0) == (side == 0)
                out.append({"ev": slug, "t": y[0], "cost": stake + fee, "pay": sh if win else 0.0, "sh": sh, "id": mid,
                            "side": side, "left": left, "q": p if side == 0 else 1 - p, "fair": q if side == 0 else 1 - q,
                            "px": px, "handle": r["handle"], "title": m["q"], "pre": t < start, "n0": n0, "m": m_})
                if first_only:
                    done.add(mid)
            t += STEP
    return out



# ================================================================ report
OUT = os.path.join(bt.OUT, "tweets.md") if hasattr(bt, "OUT") else "backtest/tweets.md"
LOOK = 0.4          # share of the events (fixed shuffled order) used to look around; the rest were opened later
TRIES = 55          # versions looked at in this dig
V2 = dict(weeks=4, recent=0.5, widen=1.5)


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def per100(b):
    c = sum(x["cost"] for x in b)
    return None if not c else (sum(x["pay"] for x in b) - c) / c * 100


def line(name, b):
    if len(b) < 10:
        return f"| {name} | {len(b)} | - | - | - | - | - |"
    bs = sorted(b, key=lambda x: x["t"])
    h = len(bs) // 2
    return (f"| {name} | {len(b)} | {len({x['ev'] for x in b})} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b))} | "
            f"{usd(per100(bs[:h]))} | {usd(per100(bs[h:]))} |")


HEAD = "| what | bets | weeks | won | per $100 | first half | second half |\n|---|---|---|---|---|---|---|"


def run():
    import exam, random
    evs, tr, posts, tp = load()
    order = sorted(evs, key=order_key)
    nA = int(len(order) * LOOK)
    A = {s: evs[s] for s in order[:nA]}
    F = {s: evs[s] for s in order[nA:]}
    L = []
    P = L.append
    who = collections.Counter(tr[s]["handle"] for s in evs)
    P("# A counting model vs Polymarket's post-count markets (tweets.py)\n")
    P(f"Generated {bot.iso()}. Markets like \"Will Elon Musk post 90-114 tweets from 5 to 7 November?\". {len(evs)} finished "
      f"count windows (ended before {btcheck.HOLDOUT_FROM}) with {sum(len(v) for v in evs.values())} markets: "
      + ", ".join(f"{h} {n}" for h, n in who.most_common()) + ". Post times come from Polymarket's own counter (xtracker), "
      "the site the markets are settled on: when each post was made and when the counter first showed it.\n")
    P("**The model.** Count so far (only posts the counter was already showing) + what the same stretch of the week brought "
      "in the last 8 weeks, with a wide spread. Version 2 uses 4 weeks, leans half-way toward the pace of the last 3 days and "
      "spreads 1.5x wider.\n")
    P("**The test.** Every 30 minutes: the model's chance for each count range vs the last real trade of the past 30 minutes. "
      "If they are far enough apart, buy the cheap side at the first real trade of the next 30 minutes, + 1c + the fee. "
      f"One bet per market, $10 each. The first {len(A)} windows (fixed shuffled order) were used to look around, the other "
      f"{len(F)} were opened later.\n")
    P("## 1. Who is closer?\n")
    P("| looks | model miss | model v2 miss | Polymarket miss |")
    P("|---|---|---|---|")
    for nm, kw in (("one random look per market, any time", {}), ("last 3 days only", dict(max_left=3 * 86400)), ("last day only", dict(max_left=86400))):
        row = []
        for mk in ({}, V2):
            looks = []
            tbets(evs, tr, posts, tp, gap=9, looks=looks, first_only=False, **dict(kw, **mk))
            by = collections.defaultdict(list)
            for r in looks:
                by[r[1]].append(r)
            rng = random.Random(5)
            rows = [rng.choice(v) for _, v in sorted(by.items())]
            br = lambda f: sum((f(r) - r[5]) ** 2 for r in rows) / max(1, len(rows))
            row.append((br(lambda r: r[3]), br(lambda r: r[4]), len(rows)))
        P(f"| {nm} ({row[0][2]}) | {row[0][0]:.4f} | {row[1][0]:.4f} | {row[0][1]:.4f} |")
    P("\n(\"Miss\" = average squared distance between the forecast and what happened; smaller is better. Polymarket is the "
      "better forecaster, most of all near the end, when people watch the account live.)\n")
    P("## 2. Buying where the model disagrees\n")
    for title, S in ((f"Windows used to look around ({len(A)})", A), (f"Windows opened later ({len(F)})", F), (f"All ({len(evs)})", evs)):
        P(f"### {title}\n")
        P(HEAD)
        for nm, kw in (("model, both sides, 5c+ apart", dict(gap=0.05)), ("model, both sides, 10c+ apart", dict(gap=0.10)),
                       ("model v2, both sides, 5c+ apart", dict(gap=0.05, **V2)),
                       ("model says Yes is too cheap, 10c+ (buy Yes)", dict(gap=0.10, sides=(0,))),
                       ("**model says Yes is too dear, 10c+ (buy No)**", dict(gap=0.10, sides=(1,))),
                       ("same, 5c+", dict(gap=0.05, sides=(1,))),
                       ("same, model v2, 10c+", dict(gap=0.10, sides=(1,), **V2)),
                       ("same, before the window starts", dict(gap=0.10, sides=(1,), started=False)),
                       ("same, inside the window", dict(gap=0.10, sides=(1,), started=True)),
                       ("yardstick: always buy No", dict(always=1)), ("yardstick: always buy Yes", dict(always=0))):
            P(line(nm, tbets(S, tr, posts, tp, **kw)))
        P("")
    main = dict(gap=0.10, sides=(1,), hi=0.90)      # No must cost 10c or more: no lottery tickets
    b = tbets(evs, tr, posts, tp, **main)
    P("### The \"buy No\" rule, cut up (all windows)\n")
    raw_b = tbets(evs, tr, posts, tp, gap=0.10, sides=(1,))
    best = max(raw_b, key=lambda x: x["pay"] - x["cost"])
    P(f"Careful: of the ${sum(x['pay'] - x['cost'] for x in raw_b):.0f} the plain rule made, ${best['pay'] - best['cost']:.0f} came from ONE bet "
      f"(No at {best['px'] * 100:.0f}c in \"{best['title']}\", a lottery ticket). So the rule we keep only buys No at 10c or more "
      f"(Yes at 90c or less). Everything below is that rule.\n")
    P(HEAD)
    P(line("**the rule: buy No, model 10c+ under the price, No costs 10c+**", b))
    P(line("&nbsp;&nbsp;windows used to look around", [x for x in b if x["ev"] in A]))
    P(line("&nbsp;&nbsp;windows opened later", [x for x in b if x["ev"] in F]))
    for h, _ in who.most_common(3):
        P(line(h, [x for x in b if x["handle"] == h]))
    for nm, f in (("paid under 50c", lambda x: x["px"] < .5), ("paid 50-85c", lambda x: .5 <= x["px"] < .85), ("paid 85c+", lambda x: x["px"] >= .85),
                  ("3+ days left", lambda x: x["left"] >= 3 * 86400), ("under 3 days left", lambda x: x["left"] < 3 * 86400)):
        P(line(nm, [x for x in b if f(x)]))
    bym = collections.defaultdict(list)
    for x in b:
        bym[time.strftime("%Y-%m", time.gmtime(x["t"]))].append(x)
    for k in sorted(bym):
        P(line(k, bym[k]))
    for ex in (0.02, 0.03, 0.05):
        P(line(f"if buying costs {ex * 100:.0f}c more than the trade price (not 1c)", tbets(evs, tr, posts, tp, extra=ex, **main)))
    P("")
    P("## 3. The exam\n")
    tests = [("Post-count markets: buy No (10c+) where the counting model says Yes is 10c+ too dear", main, "lead: wants a live paper test"),
             ("Post-count markets: counting model, both sides, 5c+ apart", dict(gap=0.05), "dropped"),
             ("Post-count markets: counting model says Yes is 10c+ too cheap (buy Yes)", dict(gap=0.10, sides=(0,)), "dropped"),
             ("Post-count markets: always buy No (yardstick)", dict(always=1), "dropped")]
    cards = []
    for name, kw, status in tests:
        bb = tbets(evs, tr, posts, tp, **kw)
        card = exam.score(bb, name, tries=TRIES, src="tweets.py, backtest/tweets.md", status=status, quiet=True)
        cards.append(card)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {usd(card.get('per100'))} per $100, "
          f"worst case {usd(card.get('floor100'))} per $100, verdict **{card.get('verdict')}**.")
    P("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return cards


def selftest():
    assert bucket("Will Donald Trump post 100-119 Truth Social posts from April 10 to April 17, 2026?") == (100, 119)
    assert bucket("Will Elon Musk post <40 tweets from November 5 to November 7, 2026?") == (0, 39)
    assert bucket("Will Elon Musk post 240+ tweets from November 5 to November 7, 2026?") == (240, 10 ** 9)
    c = nb_cdf(50, 200, 400)
    assert abs(c[-1] - 1) < 1e-6 and 0.4 < c[50] < 0.65 and c[10] < 0.01
    mean = sum(k * (c[k] - (c[k - 1] if k else 0)) for k in range(401))
    assert abs(mean - 50) < 0.5, mean
    week = 7 * 86400
    rows = [[t, t + 120] for w in range(12) for t in range(w * week, w * week + week, 3600)]      # one post an hour
    cn = Counter(rows)
    t = 10 * week + 2 * 86400
    n0, m, v = forecast(cn, 10 * week, 11 * week, t)
    assert n0 == 48 and abs(m - 120) < 2, (n0, m)
    assert cn.seen(10 * week, 10 * week + 60) == 0 and cn.seen(10 * week, 10 * week + 121) == 1
    print("tweets selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch, "run": run, "selftest": selftest}.get(cmd, lambda: sys.exit(f"unknown command {cmd}"))()
