#!/usr/bin/env python3
"""Learn from the wallets that really win (2026-11-10, Jan: "is there any way to come up with a new strategy?").

PAPER ONLY, research only. Reads the trade lists informed.py already saved (bt_cache/inf_tapes.json.gz: every $100+
trade in ~20k finished Polymarket markets from whole events, with the wallet). Never trades, never writes state/.

Not copying (we arrive 5 minutes late, tested and dropped). The question here is WHAT KIND of bets the proven winners
make, so we can make the same kind ourselves:

  A. Every wallet sits the shared exam (exam.py). Each trade is one bet held to the result: a buy at 40c stakes 40c,
     a sell at 40c is a bet on the other side that stakes 60c. Taker fee charged on all of them (too strict for
     resting orders, on purpose). The luck bar is raised for the number of wallets tested. A shuffle (same trades,
     wallet names dealt out at random) shows how many "winners" pure luck produces.
  B. Honest check: pick the winners on the FIRST half of the calendar only, then look at their bets in the second
     half: at their own prices, and at the price a slow follower really got 5-65 minutes later (+1c + fee).
  C. What winners do differently from everyone else: topic, side, price paid, time left, bet size.
  D. Forget who made the bet: which KINDS of bet (side, price, time left, topic) paid at the price a slow follower
     really got 5-65 minutes later, same money on every bet. Those need no skill and no speed: ideas to test next.

    python3 winners.py run        # probe `win_run` (ref = any branch; reads main's bt_cache, saves nothing)
    python3 winners.py selftest   # offline: a planted winner is found, lucky wallets are not
"""
import collections
import json
import os
import random
import statistics
import sys

import exam

DAY = 86400
MIN_EV = exam.MIN_GROUPS
BANDS = ((0.10, "under 10c"), (0.30, "10-30c"), (0.50, "30-50c"), (0.70, "50-70c"), (0.90, "70-90c"), (0.97, "90-97c"),
         (9, "97c+"))
LEFT = ((0, "after the end date"), (3600, "last hour"), (6 * 3600, "1-6 hours"), (DAY, "6-24 hours"), (3 * DAY, "1-3 days"),
        (7 * DAY, "3-7 days"), (30 * DAY, "7-30 days"), (9e9, "over 30 days"))
SIZES = ((500, "$100-500"), (2000, "$500-2,000"), (10000, "$2,000-10,000"), (9e12, "over $10,000"))


def bucket(x, table):
    for lim, name in table:
        if x < lim:
            return name
    return table[-1][1]


def rows_from(tapes, topic_fn=None):
    """One row per $100+ trade, as a bet held to the result."""
    out = []
    for mid, x in tapes["m"].items():
        if x.get("cut"):
            continue
        try:
            f0 = float(x["final"][0])
        except (TypeError, ValueError, IndexError):
            continue
        rate = x.get("fee") or 0.0
        tp = topic_fn(x.get("q") or "") if topic_fn else "all"
        for t, w, oi, sd, px, sh, cp, v24 in x["tr"]:
            if not 0.005 < px < 0.995 or sh <= 0:
                continue
            fin = f0 if oi == 0 else 1 - f0
            buy = sd == "B"
            price, pay1, o = (px, fin, oi) if buy else (1 - px, 1 - fin, 1 - oi)
            fee = rate * sh * px * (1 - px)
            r = {"w": w, "ev": x.get("ev") or mid, "mid": mid, "t": t, "o": o, "buy": buy, "price": price, "sh": sh,
                 "cost": price * sh + fee, "pay": pay1 * sh, "topic": tp, "left": (x.get("end") or t) - t, "q": x.get("q") or ""}
            if buy and cp is not None and cp > 0:
                c = min(0.99, cp + 0.01)
                r["ccost"] = c * sh + rate * sh * c * (1 - c)
                r["gap"] = cp - px
                r["c"], r["rate"] = c, rate
            out.append(r)
    out.sort(key=lambda r: r["t"])
    return out


def by_wallet(rows):
    d = collections.defaultdict(list)
    for r in rows:
        d[r["w"]].append(r)
    return d


def grade_wallets(rows, min_ev=MIN_EV):
    """exam card per wallet with enough separate events. The luck bar counts every wallet graded."""
    bw = {w: rs for w, rs in by_wallet(rows).items() if len({r["ev"] for r in rs}) >= min_ev}
    n = len(bw)
    return {w: exam.score(rs, str(w), tries=n, prereg=True, log=False, quiet=True) for w, rs in bw.items()}


def shuffled(rows, seed=5):
    ws = [r["w"] for r in rows]
    random.Random(seed).shuffle(ws)
    return [dict(r, w=w) for r, w in zip(rows, ws)]


def tally(cards):
    c = collections.Counter(v["key"] for v in cards.values())
    return ", ".join(f"{c[k]} \"{exam.VERDICTS[k]}\"" for k in ("good", "promising", "maybe", "bad", "early") if c[k]) or "none"


def copies(rs):
    return [{"ev": r["ev"], "t": r["t"], "cost": r["ccost"], "pay": r["pay"], "sh": r["sh"]} for r in rs if r.get("ccost")]


def line(c):
    if not c.get("bets") or c.get("lo100") is None:
        return "too few bets"
    return (f"{exam.usd(c['per100'])} per $100 (luck range {exam.usd(c['lo100'])} to {exam.usd(c['hi100'])}, "
            f"{c['groups']} separate bets, halves {exam.usd(c['half1'], 0)} / {exam.usd(c['half2'], 0)}): {c['verdict']}")


def feats(r):
    return {"topic": r["topic"], "side": ("buys" if r["buy"] else "sells the other side to bet on") + (" the first answer (Yes)" if r["o"] == 0 else " the second answer (No)"),
            "price paid": bucket(r["price"], BANDS), "time left": bucket(r["left"], LEFT), "bet size": bucket(r["cost"], SIZES)}


def profile(win_rows, all_rows, P):
    P("\n## C. What the winners do differently\n")
    P("Share of money = how much of their betting money goes there. \"Per $100\" = result of those bets, fee included.\n")
    for f in ("topic", "side", "price paid", "time left", "bet size"):
        acc = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        for rs, i in ((win_rows, 0), (all_rows, 2)):
            for r in rs:
                a = acc[feats(r)[f]]
                a[i] += r["cost"]
                a[i + 1] += r["pay"] - r["cost"]
        tw, ta = sum(a[0] for a in acc.values()) or 1, sum(a[2] for a in acc.values()) or 1
        P(f"| {f} | Winners' money | Everyone's money | Winners per $100 | Everyone per $100 |")
        P("|---|---|---|---|---|")
        for k, a in sorted(acc.items(), key=lambda kv: -kv[1][0])[:12]:
            P(f"| {k} | {100 * a[0] / tw:.0f} of 100 | {100 * a[2] / ta:.0f} of 100 | "
              f"{exam.usd(100 * a[1] / a[0]) if a[0] else ''} | {exam.usd(100 * a[3] / a[2]) if a[2] else ''} |")
        P("")


def flat(rs, follow, stake=25.0):
    """The same bets with the same money on each ($25), so a few whales can't carry a result. follow=True prices each
    at what a slow follower got: the next real buy of that answer 5-65 minutes later, +1c, plus the taker fee."""
    out = []
    for r in rs:
        if not r.get("c"):
            continue
        p = r["c"] if follow else r["price"]
        sh = stake / p
        out.append({"ev": r["ev"], "t": r["t"], "sh": sh, "cost": stake + r["rate"] * sh * p * (1 - p), "pay": sh * r["pay"] / r["sh"]})
    return out


def kinds(rows, P, min_ev=30, top=15):
    """D. Forget who made the bet: which KINDS of bet paid, at prices a slow bot could really get?"""
    P("\n## D. Which kinds of bet paid, for anyone, at prices a slow bot could get\n")
    buys = [r for r in rows if r.get("c")]
    P(f"{len(buys):,} buys had a real follow-up buy of the same answer 5-65 minutes later. Each is counted as a $25 bet at "
      "that later price +1c + fee (so no speed needed, and whales count the same as everyone).\n")
    one = []
    for f in ("side", "price paid", "time left", "topic"):
        g = collections.defaultdict(list)
        for r in buys:
            g[(f, feats(r)[f].replace("buys the ", ""))].append(r)
        one += [(k, v) for k, v in g.items() if len({r["ev"] for r in v}) >= min_ev]
    cell = collections.defaultdict(list)
    for r in buys:
        cell[(r["topic"], "Yes / first answer" if r["o"] == 0 else "No / second answer", bucket(r["price"], BANDS), bucket(r["left"], LEFT))].append(r)
    cand = [(k, v) for k, v in cell.items() if len({r["ev"] for r in v}) >= min_ev]
    tries = len(one) + len(cand)
    P(f"Looked at {len(one)} simple splits and {len(cand)} detailed kinds (topic x side x price x time left, {min_ev}+ events each). "
      f"The luck bar is raised for all {tries}.\n")
    P("| Split | Value | Separate bets | Follower per $100 | Luck range | Halves | Worst case per $100 | Verdict |")
    P("|---|---|---|---|---|---|---|---|")
    for k, v in one:
        c = exam.score(flat(v, True), "x", tries=tries, prereg=True, log=False, quiet=True)
        P(f"| {k[0]} | {k[1]} | {c['groups']} | {exam.usd(c['per100'])} | {exam.usd(c['lo100'])} to {exam.usd(c['hi100'])} | "
          f"{exam.usd(c['half1'], 0)} / {exam.usd(c['half2'], 0)} | {exam.usd(c['floor100'])} | {c['verdict']} |")
    out = []
    for k, v in cand:
        c = exam.score(flat(v, True), " / ".join(k), tries=tries, prereg=True, log=False, quiet=True)
        own = exam.score(flat(v, False), "own", tries=tries, prereg=True, log=False, quiet=True)
        c["cell"], c["own100"], c["nbets"] = k, own["per100"], len(v)
        out.append(c)
    out.sort(key=lambda c: -(c.get("floor100") or -999))
    P("\nThe detailed kinds with the best worst case:\n")
    P("| Topic | Bet on | Price paid | Time left | Bets | Separate bets | At the price they paid | Follower per $100 | Luck range | Halves | Worst case per $100 | Verdict |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in out[:top]:
        k = c["cell"]
        P(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {c['nbets']} | {c['groups']} | {exam.usd(c['own100'])} | {exam.usd(c['per100'])} | "
          f"{exam.usd(c['lo100'])} to {exam.usd(c['hi100'])} | {exam.usd(c['half1'], 0)} / {exam.usd(c['half2'], 0)} | "
          f"{exam.usd(c['floor100'])} | {c['verdict']} |")
    ahead = sum(1 for c in out if c["per100"] > 0)
    P(f"\n{ahead} of {len(out)} detailed kinds are ahead at all for a follower. Called real: "
      f"{sum(1 for c in out if c['key'] == 'good')}. Promising: {sum(1 for c in out if c['key'] == 'promising')}. "
      "Everything here was found by looking, so even a \"real\" one still needs fresh bets before it counts.")
    return out


def analyse(rows, names=None, P=print):
    names = names or {}
    nm = lambda w: str(names.get(w, w))[:10] if not isinstance(names, list) else str(names[w])[:10]
    P("# What do the wallets that really win do? (winners.py)\n")
    P(f"Data: {len(rows):,} trades of $100 or more by {len({r['w'] for r in rows}):,} wallets in "
      f"{len({r['mid'] for r in rows}):,} finished Polymarket markets ({len({r['ev'] for r in rows}):,} events), "
      f"{exam.day(rows[0]['t'])} to {exam.day(rows[-1]['t'])}. Every trade is counted as a bet held to the result. In-sample only.\n")
    allc = exam.score(rows, "everyone", prereg=True, log=False, quiet=True)
    P(f"Everyone together: {line(allc)}\n")

    P("## A. Every wallet sits the exam\n")
    cards = grade_wallets(rows)
    luck = grade_wallets(shuffled(rows))
    P(f"Wallets with {MIN_EV}+ separate events: {len(cards):,}. Verdicts: {tally(cards)}.")
    P(f"Luck yardstick (same trades, wallet names dealt out at random): {tally(luck)}.")
    good = {w for w, c in cards.items() if c["key"] == "good"}
    prom = {w for w, c in cards.items() if c["key"] == "promising"}
    n_luck = sum(1 for c in luck.values() if c["key"] == "good")
    def share(cs, keys):
        return 1000 * sum(1 for c in cs.values() if c["key"] in keys) / max(1, len(cs))
    rw, rl = share(cards, ("good", "promising")), share(luck, ("good", "promising"))
    P(f"Passed or promising: {rw:.0f} of every 1,000 real wallets, against {rl:.0f} of every 1,000 shuffled ones. "
      + ("Clearly more than luck: real winners exist." if rw > 2 * rl and len(good) >= 5 else
         "That is about what luck alone gives: in this data, steady winners are not showing.") + "\n")
    bw = by_wallet(rows)
    P("| Wallet | Separate bets | Money bet | Per $100 | Worst case per $100 | Mostly bets on | Both sides of a market | Price 5+ min after their buys |")
    P("|---|---|---|---|---|---|---|---|")
    for w in sorted(good, key=lambda w: -cards[w]["floor100"])[:25]:
        rs, c = bw[w], cards[w]
        tp = collections.Counter()
        for r in rs:
            tp[r["topic"]] += r["cost"]
        sides = collections.defaultdict(set)
        for r in rs:
            sides[r["mid"]].add(r["o"])
        both = sum(1 for s in sides.values() if len(s) == 2) / len(sides)
        gaps = [r["gap"] for r in rs if "gap" in r]
        P(f"| {nm(w)} | {c['groups']} | ${c['staked']:,.0f} | {exam.usd(c['per100'])} | {exam.usd(c['floor100'])} | "
          f"{tp.most_common(1)[0][0]} | {100 * both:.0f} of 100 markets | "
          f"{f'{100 * statistics.median(gaps):+.1f}c' if gaps else 'n/a'} |")

    P("\n## B. Honest check: winners picked on the first half, judged on the second\n")
    T = rows[len(rows) // 2]["t"]
    h1, h2 = [r for r in rows if r["t"] < T], [r for r in rows if r["t"] >= T]
    c1 = grade_wallets(h1)
    P(f"Split day: {exam.day(T)}. First half: {len(c1):,} wallets graded: {tally(c1)}.")
    res = {}
    for label, keys in (("passed the full bar", ("good",)), ("passed or promising", ("good", "promising"))):
        pick = {w for w, c in c1.items() if c["key"] in keys}
        later = [r for r in h2 if r["w"] in pick]
        own = exam.score(later, "own", prereg=True, log=False, quiet=True)
        cp = exam.score(copies(later), "copy", prereg=True, log=False, quiet=True)
        res[label] = (len(pick), own, cp)
        P(f"- **{len(pick)} wallet(s) that {label}** in the first half, their second-half bets:")
        P(f"  - at their own prices: {line(own)}")
        P(f"  - following 5-65 min later at the real price +1c: {line(cp)}")
    rest = exam.score(h2, "all", prereg=True, log=False, quiet=True)
    P(f"- Everyone in the second half, for comparison: {line(rest)}")

    if len(good) >= 5:
        profile([r for r in rows if r["w"] in good], rows, P)
    else:
        P(f"\n## C. What the winners do differently\n\nSkipped: only {len(good)} wallet(s) passed the full bar, and the habits "
          "of one or two wallets are a story, not a pattern.")
    out = kinds(rows, P)
    return {"cards": cards, "good": good, "prom": prom, "luck_good": n_luck, "half": res, "cells": out}


def run():
    import backtest as bt
    import calib
    import informed
    tapes = bt.rjson(informed.TAPES, {}) or {}
    if not tapes.get("m"):
        print("no trade lists in bt_cache; run probe btinf_fetch on main first")
        return
    rows = rows_from(tapes, calib.topic)
    lines = []

    def P(s=""):
        print(s)
        lines.append(s)
    res = analyse(rows, tapes.get("W") or [], P)
    with open(os.path.join(exam.OUT, "winners.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    W = tapes.get("W") or []
    print("WINNER WALLETS " + json.dumps([W[w] for w in sorted(res["good"], key=lambda w: -res["cards"][w]["floor100"])[:60]]))


def selftest():
    rnd = random.Random(2)
    m, W = {}, 0
    for i in range(1500):
        yes = rnd.random() < 0.5
        topic = "mention" if i % 5 == 0 else "other"
        true_p = 0.5
        tr = []
        for j in range(12):
            w = rnd.randrange(1, 400)                       # 399 ordinary wallets betting at fair prices
            oi = rnd.randrange(2)
            tr.append([1.7e9 + i * 3600 + j, w, oi, "B" if rnd.random() < 0.8 else "S", true_p, 400, true_p, 0])
        if i % 2 == 0:                                      # wallet 0 knows the answer 72 times in 100, the price moves 5c after
            right = rnd.random() < 0.72
            oi = (0 if yes else 1) if right else (1 if yes else 0)
            tr.append([1.7e9 + i * 3600 + 20, 0, oi, "B", 0.5, 400, 0.55, 0])
        m[str(i)] = {"q": f"{topic} q{i}", "end": 1.7e9 + i * 3600 + DAY, "final": [1.0, 0.0] if yes else [0.0, 1.0], "fee": 0.0,
                     "ev": f"e{i}", "tr": tr}
    rows = rows_from({"m": m}, lambda q: q.split()[0])
    assert len(rows) == 1500 * 12 + 750
    s = [r for r in rows if not r["buy"]][0]
    assert abs(s["price"] - 0.5) < 1e-9 and s["cost"] == 200 and s["pay"] in (0.0, 400.0)
    out = []
    res = analyse(rows, None, out.append)
    print("\n".join(out[:14]))
    assert 0 in res["good"], "planted winner not found"
    assert len(res["good"]) <= 2 and res["luck_good"] <= 1, (res["good"], res["luck_good"])
    n, own, cp = res["half"]["passed the full bar"]
    assert n >= 1 and own["per100"] > 5 and cp["per100"] < own["per100"], (n, own["per100"], cp["per100"])
    assert not any(c["key"] == "good" for c in res["cells"])      # ordinary bets were fair: no kind of bet may pass
    print("\nselftest ok: planted winner found, lucky wallets not, follower gets less, no fake idea cell")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"run": run, "selftest": selftest}[cmd]()
