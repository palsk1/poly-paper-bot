#!/usr/bin/env python3
"""The exam: one shared test that every idea sits, graded the same way (2026-11-10). Research only.

PAPER ONLY. Reads data, never trades, never writes state/.

Why: every dig graded itself its own way (own costs, own luck range, own idea of "enough bets"), most leads died
at the same late step ("at real prices it's gone"), and nobody counted how many ideas we tried. With hundreds of
tries a few lucky fakes are certain. So: one bet list in, one scorecard out, one line in the list of everything tried.

Use it from a dig (3 lines):

    import exam
    bets = exam.fills(signals)                 # optional: re-price chart signals at what people REALLY paid
    exam.score(bets, "soccer draws 22-32c", tries=14, src="digs.py dig_draws")

A bet is a dict:  ev (event / game / window: bets in one ev count as ONE), t (unix time of the buy),
                  cost ($ paid, fee included), pay ($ back at the end).  Optional: sh (shares), q (chart price).
A signal is a dict: cid (Polymarket condition id), oi (0/1 outcome bought), t (decision time), pay (what that
                  outcome paid per share, 0 or 1), ev, optional q (chart price), fee (rate), toks, end (hard stop,
                  e.g. kickoff), id (Gamma id when there's no cid).
`tries` = how many versions this dig looked at before it picked this one. Be honest: it sets the luck bar.

What the scorecard says (plain words, same for every idea):
  - profit per $100 bet, and the luck range around it
  - how many bets are really separate (same event, or same day when losses come in bunches, count once)
  - first half vs second half
  - the worst case per $100 after one more made-up disaster and a bar raised for every idea we ever tried
  - how many more separate bets it needs, and when that is at its pace
  - one verdict, the dashboard's words: Looks real / Promising, needs more bets / Ahead, but could be luck /
    Losing / Too early to tell

    python3 exam.py selftest          # offline checks (fair world, planted edge, bunched losses, fake trade tape)
    python3 exam.py tracks            # the same exam for every live paper track -> backtest/exam_tracks.md
    python3 exam.py ledger            # rebuild backtest/ledger.md from backtest/ledger.json
    python3 exam.py file bets.json "name" [tries]     # grade any saved bet list
    python3 exam.py tapetest          # probe `exam_tapetest`: live check that real-price fills work
"""
import collections
import datetime as dt
import json
import math
import os
import random
import re
import statistics
import sys
from statistics import NormalDist

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "backtest")
LEDGER = os.path.join(OUT, "ledger.json")
DAY = 86400
Z90 = 1.645                 # the luck range shown is the usual 90% one
FAMILY = 0.10               # chance we accept that ANY dud among all tries gets called real
MIN_GROUPS = 10             # under this: "Too early to tell" (same as the dashboard's 10 finished bets)
MIN_REAL = 30               # "Looks real" needs at least this many separate bets
STAKE = 25.0                # dollars per bet when the exam prices a signal itself (the ranking's real-size number)
DEADLINE = "2027-01-01"     # Jan's decision day

VERDICTS = {"good": "Looks real", "promising": "Promising, needs more bets", "maybe": "Ahead, but could be luck",
            "bad": "Losing", "early": "Too early to tell"}


# ================================================================ small helpers
def ts(x):
    """unix seconds from a number or an ISO time."""
    if isinstance(x, (int, float)):
        return float(x) / 1000 if x > 1e11 else float(x)
    if not x:
        return 0.0
    s = str(x).replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(s)
    except ValueError:
        d = dt.datetime.fromisoformat(s[:10])
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.timestamp()


def day(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")


def usd(x, nd=2):
    return f"{'+' if x >= 0 else '-'}${abs(x):.{nd}f}"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")[:60]


def _groups(bets, key):
    """{group: [profit, stake, first time]}"""
    g = {}
    for i, b in enumerate(bets):
        k = key(b, i)
        e = g.setdefault(k, [0.0, 0.0, b.get("t") or 0.0])
        e[0] += b["pay"] - b["cost"]
        e[1] += b["cost"]
        e[2] = min(e[2], b.get("t") or 0.0)
    return g


def _rate_se(rows):
    """profit per $1 staked and its standard error, treating each row (profit, stake) as one separate bet."""
    P, S, k = sum(r[0] for r in rows), sum(r[1] for r in rows), len(rows)
    if S <= 0 or k < 2:
        return (P / S if S > 0 else 0.0), float("inf")
    rate = P / S
    var = sum((r[0] - rate * r[1]) ** 2 for r in rows) / (S * S) * (k / (k - 1))
    return rate, math.sqrt(var)


def luck_z(n):
    return NormalDist().inv_cdf(1 - FAMILY / max(1, n))


# ================================================================ the ledger: everything we ever tried
def ledger_load(path=None):
    try:
        with open(path or LEDGER) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"rows": []}


def ledger_count(path=None, skip=None):
    return sum(1 for r in ledger_load(path)["rows"] if r.get("id") != skip)


def ledger_add(row, path=None):
    """Add or update one line (same id = same idea: updated, not counted twice). `tries` only ever goes up."""
    L = ledger_load(path)
    for r in L["rows"]:
        if r.get("id") == row["id"]:
            row = dict(row, tries=max(int(r.get("tries") or 1), int(row.get("tries") or 1)),
                       date=r.get("date") or row.get("date"))
            r.clear()
            r.update(row)
            break
    else:
        L["rows"].append(row)
    with open(path or LEDGER, "w") as f:
        json.dump(L, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return L


def ledger_md(path=None, out=None):
    L = ledger_load(path)
    rows = sorted(L["rows"], key=lambda r: (r.get("date") or "", r.get("id") or ""))
    by = collections.Counter("dropped" if str(r.get("status") or "").startswith("dropped") else "still being tested or waiting"
                             for r in rows)
    tries = sum(int(r.get("tries") or 1) for r in rows)
    real = [r for r in rows if r.get("verdict") == VERDICTS["good"]]
    n = len(rows)
    md = ["# Everything we've tried so far (the ledger)\n",
          "Kept by `exam.py`. One line per idea. A new line is added every time an idea sits the exam "
          "(`exam.score`). Rebuild this page with `python3 exam.py ledger`.\n",
          f"**{n} ideas examined, in about {tries:,} versions.** "
          + ", ".join(f"{v} {k}" for k, v in sorted(by.items(), key=lambda kv: -kv[1])) + ". "
          f"**Looks real: {len(real)}.**\n",
          f"Why count: if you test {n} ideas that are all worthless, the luckiest one still looks good. "
          f"With {n} tries, a result has to beat about {luck_z(n):.1f} \"luck steps\" instead of the usual 1.6 before "
          "the exam calls it real. Every new try raises that bar a little for everyone.\n",
          "| Date | Idea | Versions tried | Separate bets | Per $100 | Verdict | Now | Where |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p = r.get("per100")
        md.append(f"| {r.get('date', '')} | {r.get('what') or r.get('id')} | {int(r.get('tries') or 1):,} | "
                  f"{r.get('groups') if r.get('groups') is not None else ''} | {usd(p) if isinstance(p, (int, float)) else (p or '')} | "
                  f"{r.get('verdict', '')} | {r.get('status', '')} | {r.get('src', '')} |")
    md.append("\n\"Per $100\" is the strictest number the dig reported (real or pessimistic prices). Lines from before "
              "2026-11-10 were filled in by hand from the reports: their verdicts are the dig's own words put into the exam's "
              "five verdicts, and their version counts are estimates.")
    text = "\n".join(md) + "\n"
    with open(out or os.path.join(OUT, "ledger.md"), "w") as f:
        f.write(text)
    return text


# ================================================================ the scorecard
def score(bets, name, tries=1, prereg=False, src="", note="", status=None, log=True, ledger=None, quiet=False,
          deadline=DEADLINE, now=None):
    """Grade a bet list. Returns the scorecard (dict) and prints it in plain words.
    tries  = versions this dig looked at to find this one.
    prereg = True for a test whose rule was fixed BEFORE the data existed (holdout, live track): then only `tries`
             (the number of such fixed tests) sets the luck bar. Otherwise every idea in the ledger counts too."""
    bets = [b for b in bets if b.get("cost", 0) > 0]
    n = len(bets)
    ident = slug(name)
    N = max(1, int(tries)) + (0 if prereg else ledger_count(ledger, skip=ident))
    card = {"id": ident, "name": name, "bets": n, "tries": int(tries), "luck_tries": N, "src": src, "note": note}
    if n == 0:
        card.update(groups=0, events=0, days=0, per100=None, key="early", verdict=VERDICTS["early"])
        return _finish(card, status, log, ledger, quiet, now)
    by_ev = _groups(bets, lambda b, i: str(b.get("ev") if b.get("ev") is not None else f"#{i}"))
    by_day = _groups(bets, lambda b, i: day(b.get("t") or 0))
    have_t = any(b.get("t") for b in bets)
    r_ev, se_ev = _rate_se(list(by_ev.values()))
    r_day, se_day = _rate_se(list(by_day.values())) if have_t and len(by_day) >= MIN_GROUPS else (r_ev, 0.0)
    bunched = se_day > se_ev * 1.25 and len(by_day) < len(by_ev)
    g = by_day if bunched else by_ev          # the grouping with the wider luck range is the honest one
    rows = sorted(g.values(), key=lambda r: r[2])
    k = len(rows)
    rate, se = _rate_se(rows)
    # one more made-up disaster: a separate bet that loses everything, as big as the worst loss seen (or a normal bet)
    typical = statistics.median(r[1] for r in rows)
    worst_seen = max([-r[0] for r in rows if r[0] < 0] or [0.0])
    ph = max(typical, worst_seen)
    rate_ph, se_ph = _rate_se(rows + [[-ph, ph, 0]])
    zN = luck_z(N)
    floor = max(-1.0, rate_ph - zN * se_ph) if se_ph < float("inf") else -1.0
    soft = rate_ph - Z90 * se_ph if se_ph < float("inf") else -1.0     # same, without the many-tries bar
    no_loss = not any(r[0] < 0 for r in rows)
    half = k // 2
    h1 = _rate_se(rows[:half])[0] if half else 0.0
    h2 = _rate_se(rows[half:])[0] if half else 0.0
    lo, hi = rate - Z90 * se, rate + Z90 * se
    t0, t1 = min(r[2] for r in rows), max(b.get("t") or 0 for b in bets)
    span = max(1.0, (t1 - t0) / DAY) if have_t else None
    pace = k / span if span else None
    # how many separate bets until the worst case clears $0, if things keep going exactly like this
    need = more = eta = None
    if rate_ph > 0 and 0 < se_ph < float("inf"):
        need = int(math.ceil((k + 1) * (zN * se_ph / rate_ph) ** 2))
        more = max(0, need - k, MIN_REAL - k)
        if pace:
            base = now or (dt.datetime.now(dt.timezone.utc).timestamp() if prereg else t1)
            eta = base + min(more / pace, 36500) * DAY      # capped at 100 years: a date that far out just means "never"
    if k < MIN_GROUPS:
        key = "early"
    elif rate < 0:
        key = "bad"
    elif floor > 0 and k >= MIN_REAL and h1 > 0 and h2 > 0:
        key = "good"
    elif lo > 0 and soft > 0 and h1 >= 0 and h2 >= 0:
        key = "promising"
    else:
        key = "maybe"
    stress = {}
    if all(b.get("sh") for b in bets):
        for c in (0.01, 0.02):
            stress[c] = sum(b["pay"] - b["cost"] - b["sh"] * c for b in bets) / sum(b["cost"] + b["sh"] * c for b in bets)
    gaps = [b["px"] - b["q"] for b in bets if b.get("q") is not None and b.get("px") is not None]
    card.update(groups=k, events=len(by_ev), days=len(by_day) if have_t else None, bunched=bunched,
                staked=round(sum(b["cost"] for b in bets), 2), profit=round(sum(b["pay"] - b["cost"] for b in bets), 2),
                per100=round(100 * rate, 2), lo100=round(100 * lo, 2) if se < float("inf") else None,
                hi100=round(100 * hi, 2) if se < float("inf") else None,
                floor100=round(100 * floor, 2), no_loss=no_loss, half1=round(100 * h1, 2), half2=round(100 * h2, 2),
                luck_show=round(100 * zN * se_ph, 2) if se_ph < float("inf") else None,
                need=need, more=more, pace=round(pace, 2) if pace else None,
                eta=day(eta) if eta else None, in_time=(day(eta) <= deadline) if eta else None,
                stress={f"+{int(c * 100)}c": round(100 * v, 2) for c, v in stress.items()},
                chart_gap_c=round(100 * statistics.median(gaps), 1) if gaps else None,
                key=key, verdict=VERDICTS[key])
    return _finish(card, status, log, ledger, quiet, now)


def _finish(card, status, log, ledger, quiet, now):
    if not quiet:
        print(card_text(card))
    if log:
        row = {"id": card["id"], "date": day(now or dt.datetime.now(dt.timezone.utc).timestamp()), "what": card["name"],
               "tries": card["tries"], "bets": card["bets"], "groups": card.get("groups"), "per100": card.get("per100"),
               "floor100": card.get("floor100"), "verdict": card["verdict"],
               "status": status or ("dropped" if card["key"] in ("bad", "maybe") else "open"), "src": card.get("src", "")}
        try:
            ledger_add(row, ledger)
        except OSError as e:
            print("ledger not saved:", e)
        if not quiet:
            print("LEDGER ROW " + json.dumps(row, ensure_ascii=False))   # so a probe log can be pasted into the ledger
    return card


def card_text(c):
    L = [f"\n=== EXAM: {c['name']} ===", f"Verdict: {c['verdict']}"]
    if not c.get("bets"):
        return "\n".join(L + ["No bets to grade."])
    sep = f"{c['groups']} separate bets"
    how = (f"{c['bets']} bets on {c['events']} events over {c['days']} day{'s' if c['days'] != 1 else ''}" if c.get("days")
           else f"{c['bets']} bets on {c['events']} events")
    L.append(f"Bets: {how}. Counted as {sep}"
             + (" (losses came in bunches on the same days, so one day counts once)." if c.get("bunched")
                else " (bets on the same event count once)."))
    if c.get("lo100") is not None:
        L.append(f"Result: {usd(c['per100'])} per $100 bet (total {usd(c['profit'])} on ${c['staked']:.2f}). "
                 f"Luck range {usd(c['lo100'])} to {usd(c['hi100'])}."
                 + (" No losing bet seen yet, so that range is too kind: go by the worst case below." if c.get("no_loss") else ""))
    else:
        L.append(f"Result: {usd(c['per100'])} per $100 bet. Too few bets for a luck range.")
    L.append(f"Halves: first {usd(c['half1'])}, second {usd(c['half2'])} per $100"
             + (". Both ahead." if c["half1"] > 0 and c["half2"] > 0 else ". Not ahead in both: could be one good stretch."))
    if c.get("stress"):
        L.append("If every price were worse: " + ", ".join(f"{k} {usd(v)}" for k, v in c["stress"].items()) + " per $100.")
    if c.get("chart_gap_c") is not None:
        L.append(f"Real price paid vs the chart price: {c['chart_gap_c']:+.1f}c (typical bet).")
    if c.get("luck_show") is not None:
        L.append(f"Luck bar: this is 1 of {c['luck_tries']:,} tries. The luckiest of {c['luck_tries']:,} worthless ideas "
                 f"would show about {usd(c['luck_show'])} per $100 on this many bets.")
        L.append(f"Worst case per $100 (one more disaster added, bar raised for all tries): {usd(c['floor100'])}. "
                 + ("Above $0: good." if c["floor100"] > 0 else "Below $0: not proven."))
    if c["key"] in ("promising", "maybe", "early") and (c.get("more") or 0) > 100000:
        L.append("To prove it: it would take more bets than anyone will ever make. The lead is too thin to prove.")
    elif c["key"] in ("promising", "maybe", "early") and c.get("more") is not None:
        when = ""
        if c.get("eta"):
            when = (f" At its pace ({c['pace']:.1f} separate bets a day) that is around {c['eta']}"
                    + ("." if c.get("in_time") else f", after {DEADLINE}: too slow for the 1 Jan decision."))
        L.append(f"To prove it: about {c['more']:,} more separate bets like these.{when}")
    elif c["key"] in ("promising", "maybe", "early"):
        L.append("To prove it: can't say. It isn't ahead once one more disaster is added.")
    return "\n".join(L)


# ================================================================ can a planned test even give an answer?
def bar_protocol(card):
    """backtest/PROTOCOL.md section 5: ahead, and the low end of the luck range above -$5 per $100."""
    return card["per100"] is not None and card["per100"] > 0 and (card.get("lo100") or -999) > -5


def bar_real(card):
    return card["key"] == "good"


def power(bets, n_more, bar=bar_protocol, sims=400, seed=7, tries=1):
    """How often would a fresh test of `n_more` separate bets pass `bar`, (a) if what we saw is real, (b) if there's
    no edge at all (same bets, profit shifted to $0)? Returns (pass_if_real, pass_if_dud) out of 100.
    A test that passes about as often either way can't tell us anything: don't wait for it."""
    g = list(_groups(bets, lambda b, i: str(b.get("ev") if b.get("ev") is not None else f"#{i}")).items())
    if len(g) < 2 or n_more < 2:
        return None
    rate = sum(v[0] for _, v in g) / sum(v[1] for _, v in g)
    rnd = random.Random(seed)
    out = []
    for shift in (0.0, rate):
        ok = 0
        for _ in range(sims):
            pick = [g[rnd.randrange(len(g))][1] for _ in range(n_more)]
            fake = [{"ev": i, "t": 0, "cost": s, "pay": s + p - shift * s} for i, (p, s, _) in enumerate(pick)]
            ok += bool(bar(score(fake, "sim", tries=tries, prereg=True, log=False, quiet=True)))
        out.append(round(100 * ok / sims))
    return tuple(out)


# ================================================================ real prices: what people actually paid
def fills(signals, window=3 * 3600, extra=0.01, stake=STAKE, tape_fn=None, max_pages=40, workers=8, info=None):
    """Turn chart signals into bets at REAL prices: the first real BUY of that outcome on the Polymarket trade tape
    within `window` seconds after the decision time (and before `end`, if given), plus `extra` and the taker fee.
    A signal nobody could have bought (no real buy in the window) is left out and counted in info['no_buy'].
    Each bet stakes `stake` dollars. Also notes how many dollars really traded near that price (info['room'])."""
    import bot
    if tape_fn is None:
        import informed
        need = [str(s["id"]) for s in signals if not s.get("cid") and s.get("id")]
        cids = informed.cids_for(need) if need else {}

        def tape_fn(sg):
            cid = sg.get("cid") or cids.get(str(sg.get("id")))
            return informed.tape(cid, max_pages)[0] if cid else None

    def one(sg):
        try:
            tr = tape_fn(sg)
        except Exception:
            return sg, None
        if tr is None:
            return sg, None
        end = min(sg["t"] + window, sg["end"]) if sg.get("end") else sg["t"] + window
        buys = []
        for r in tr:
            t = bot.fnum(bot.pick(r, "timestamp", "time"))
            t = t / 1000 if t > 1e11 else t
            o = r.get("outcome_index", r.get("outcomeIndex"))
            if o not in (0, 1) and sg.get("toks"):
                tok = str(bot.pick(r, "token_id", "asset", default=""))
                o = 0 if tok == sg["toks"][0] else 1 if tok == sg["toks"][1] else None
            px = bot.fnum(r.get("price"))
            if o == sg["oi"] and str(r.get("side") or "").upper().startswith("B") and sg["t"] <= t < end and 0 < px < 1:
                buys.append((t, px, bot.fnum(r.get("size"))))
        buys.sort()
        return sg, buys

    if workers > 1 and len(signals) > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(workers) as ex:
            res = list(ex.map(one, signals))
    else:
        res = [one(s) for s in signals]
    bets, no_tape, no_buy, room = [], 0, 0, []
    for sg, buys in res:
        if buys is None:
            no_tape += 1
            continue
        if not buys:
            no_buy += 1
            continue
        t0, p0, _ = buys[0]
        c = min(0.99, p0 + extra)
        sh = stake / c
        fee = bot.taker_fee(sh, c, sg.get("fee") or 0)
        room.append(sum(p * s for t, p, s in buys if t <= t0 + 600 and p <= p0 + 0.01))
        bets.append({"ev": sg.get("ev") if sg.get("ev") is not None else sg.get("cid") or sg.get("id"), "t": t0,
                     "cost": stake + fee, "pay": sh * sg["pay"], "sh": sh, "px": p0, "q": sg.get("q")})
    stats = {"signals": len(signals), "filled": len(bets), "no_buy": no_buy, "no_tape": no_tape,
             "room": round(statistics.median(room), 2) if room else None,
             "fits": sum(1 for x in room if x >= stake)}
    if info is not None:
        info.update(stats)
    print(f"Real prices: {len(signals)} signals, {len(bets)} had a real buy in the window, {no_buy} had none "
          f"(nobody could buy there), {no_tape} tapes unreadable."
          + (f" Typical money traded near that price in 10 min: ${stats['room']:.0f}; ${stake:.0f} would have fit in "
             f"{stats['fits']} of {len(bets)}." if room else ""))
    return bets


# ================================================================ the same exam for the live paper tracks
def track_bets(tr, size="25"):
    """Finished bets of one live track as exam bets. Real-size numbers when the trade has them (like the trust
    ranking), else the paper numbers. Bets in one event, or one Kalshi 15-minute window, share an `ev`."""
    out = []
    for c in tr.get("closed") or []:
        rs = (c.get("rs_pnl") or {}).get(size)
        if rs:
            cost, pnl = rs[0], rs[1]
            if cost <= 1e-9:
                continue
        else:
            cost = c.get("cost") or (c.get("shares", 0) * c.get("entry", 0) + c.get("entry_fee", 0.0))
            pnl = c.get("pnl", 0.0)
        if not cost or cost <= 0:
            continue
        ev = c.get("event_key") or c.get("event_slug") or (("k15:" + str(c["close"])) if c.get("close") else None) \
            or c.get("ticker") or c.get("slug") or c.get("token")
        out.append({"ev": ev, "t": ts(c.get("opened") or c.get("placed") or c.get("closed_at")), "cost": cost, "pay": cost + pnl})
    return out


def tracks(path=None, out=None, now=None):
    with open(path or os.path.join(ROOT, "state", "tracks.json")) as f:
        T = json.load(f)
    now = now or dt.datetime.now(dt.timezone.utc).timestamp()
    left = max(0.0, (ts(DEADLINE) - now) / DAY)
    n_tr = len(T)
    cards = []
    for name, tr in T.items():
        bets = track_bets(tr)
        c = score(bets, name, tries=n_tr, prereg=True, log=False, quiet=True, now=now)
        c["by_deadline"] = None
        if c.get("pace") and c["groups"] >= MIN_GROUPS and c["key"] != "bad":
            fresh = int(c["groups"] + c["pace"] * left)
            c["fresh"] = fresh
            if fresh >= MIN_REAL:
                c["by_deadline"] = power(bets, min(fresh, 4000), bar=bar_real, sims=200, tries=n_tr)
        cards.append(c)
    order = {"good": 0, "promising": 1, "maybe": 2, "early": 3, "bad": 4}
    cards.sort(key=lambda c: (order[c["key"]], -(c.get("floor100") if c.get("floor100") is not None else -999), c["name"]))
    graded = [c for c in cards if c["bets"]]
    cnt = collections.Counter(c["verdict"] for c in graded)
    md = [f"# The exam for every live paper track ({day(now)})\n",
          "Made by `python3 exam.py tracks` from `state/tracks.json`. Research only: this page changes nothing in the bot, "
          "the dashboard or the ranking. It asks one question the scoreboard doesn't: **can this track be proven by "
          f"{DEADLINE}, or are we waiting for nothing?**\n",
          f"{len(T)} tracks, {len(graded)} with finished bets: " + ", ".join(f"{v} \"{k}\"" for k, v in cnt.most_common()) + ".\n",
          "How to read it:",
          "- **Separate bets**: bets on the same event (or in the same 15 minutes of crypto) count once. If losses come "
          "in bunches on the same days, a whole day counts once. That's the real amount of evidence.",
          "- **Worst case per $100**: the result after adding one more made-up disaster and raising the bar because we run "
          f"{len(T)} tracks at once. Above $0 with 30+ separate bets and both halves ahead = \"Looks real\".",
          f"- **Answer by**: when the worst case would clear $0 if the track keeps going exactly as now. After {DEADLINE} = too slow.",
          "- **Pass chance by 1 Jan**: out of 100 replays of the bets it will have by then. First number: if what we see "
          "is real. Second: if it's really worth $0. A good test has a high first and a low second number.\n",
          "| Track | Verdict | Finished bets | Separate bets | Per $100 | Luck range | Worst case per $100 | Answer by | Pass chance by 1 Jan (real / worthless) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c in [c for c in graded if c["key"] != "early"]:
        rng = f"{usd(c['lo100'])} to {usd(c['hi100'])}" if c.get("lo100") is not None else "too few"
        ans = "" if c["key"] in ("bad", "good") else (c.get("eta") or "can't say") + ("" if c.get("in_time") or not c.get("eta") else " (too slow)")
        pw = f"{c['by_deadline'][0]} / {c['by_deadline'][1]}" if c.get("by_deadline") else ""
        md.append(f"| {c['name']} | {c['verdict']} | {c['bets']} | {c['groups']}{' (by day)' if c.get('bunched') else ''} | "
                  f"{usd(c['per100'])} | {rng} | {usd(c['floor100']) if c.get('floor100') is not None else ''} | {ans} | {pw} |")
    early = [c for c in graded if c["key"] == "early"]
    md.append(f"\nToo early to tell, under {MIN_GROUPS} separate bets ({len(early)}): "
              + ", ".join(f"{c['name']} ({c['groups']}, {usd(c['per100'], 0)})" for c in sorted(early, key=lambda c: -c["groups"]))
              + ". The number is separate bets, the dollars are per $100 so far: mostly luck at this size.")
    idle = sorted(c["name"] for c in cards if not c["bets"])
    md.append(f"\nNo finished bets yet ({len(idle)}): " + ", ".join(idle) + ".")
    text = "\n".join(md) + "\n"
    with open(out or os.path.join(OUT, "exam_tracks.md"), "w") as f:
        f.write(text)
    print(text)
    return cards


# ================================================================ live plumbing check (probe exam_tapetest)
def tapetest(n=40):
    """Not a strategy test: proves the real-price step works on live data. Takes recently finished Polymarket markets,
    'decides' to buy the first answer 24h before the end, fills at the first real buy, and grades it (not logged)."""
    import bot
    rows = bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"closed": "true", "limit": 200, "order": "closedTime",
                                                                     "ascending": "false", "volume_num_min": 20000}), "data", "markets")
    sig = []
    for m in rows:
        try:
            px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            toks = json.loads(m.get("clobTokenIds") or "[]")
        except ValueError:
            continue
        end = ts(m.get("closedTime") or m.get("endDate"))
        if len(px) != 2 or len(toks) != 2 or max(px) < 0.99 or not m.get("conditionId") or not end:
            continue
        sig.append({"cid": m["conditionId"], "toks": toks, "oi": 0, "t": end - DAY, "pay": 1.0 if px[0] > 0.5 else 0.0,
                    "ev": str((m.get("events") or [{}])[0].get("id") or m.get("id")), "end": end, "fee": 0})
        if len(sig) >= n:
            break
    print(f"tapetest: {len(sig)} finished markets from Gamma")
    info = {}
    bets = fills(sig, window=6 * 3600, info=info)
    print("fill stats", json.dumps(info))
    for b in bets[:5]:
        print("  sample bet", json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in b.items()}))
    score(bets, "tapetest: buy the first answer a day before the end (plumbing check, not an idea)", log=False)
    return bets


# ================================================================ offline checks
def selftest():
    import tempfile
    rnd = random.Random(3)
    tmp = os.path.join(tempfile.mkdtemp(), "ledger.json")

    def world(n, p_true, price, edge_free=True, days=60, ev_size=1):
        out = []
        for i in range(n):
            win = rnd.random() < p_true
            out.append({"ev": i // ev_size, "t": 1.76e9 + (i * days * DAY) // n, "cost": 25.0, "sh": 25 / price,
                        "pay": 25 / price if win else 0.0})
        return out

    # 1. fair world: 300 worthless ideas, 200 bets each at the true price. None may be called real.
    calls = collections.Counter(score(world(200, 0.5, 0.5), f"dud{i}", tries=300, prereg=True, log=False, quiet=True)["key"]
                                for i in range(300))
    print("1. 300 worthless ideas:", dict(calls))
    assert calls["good"] == 0, calls
    assert calls["promising"] <= 30, calls            # about 5 in 100 land above the plain luck range by chance
    # the same duds WITHOUT counting the tries: this is the trap the ledger closes
    naive = sum(score(world(200, 0.5, 0.5), "x", tries=1, prereg=True, log=False, quiet=True)["floor100"] > 0 for _ in range(300))
    print(f"   same 300 duds graded as if each were the only try: {naive} have a worst case above $0")
    # 2. planted edge: 54 wins in 100 at 50c (+$8 per $100), 3,000 bets -> must be called real even among 300 tries
    c = score(world(3000, 0.54, 0.5), "planted edge", tries=300, prereg=True, log=False, quiet=True)
    print("2. planted edge:", c["verdict"], c["per100"], c["floor100"])
    assert c["key"] == "good", c
    # 3. small sure wins, rare big loss, no loss seen yet: 40 wins at 97c must NOT be called real
    c = score([{"ev": i, "t": 1.76e9 + i * DAY, "cost": 24.25, "pay": 25.0} for i in range(40)], "no loss yet",
              prereg=True, log=False, quiet=True)
    print("3. 40 wins at 97c, no loss yet:", c["verdict"], "worst case", c["floor100"])
    assert c["key"] == "maybe" and c["floor100"] < 0, c
    # 4. bunched losses: 600 bets at 99c over 30 days, 8 losses all on 2 days vs spread out
    def favs(loss_days):
        out, losses = [], 0
        for i in range(600):
            d = i // 20
            lose = d in loss_days and (i % 20) < 8 // len(loss_days)
            out.append({"ev": i, "t": 1.76e9 + d * DAY + i, "cost": 9.9, "pay": 0.0 if lose else 10.0})
        return out
    a = score(favs({3, 17}), "bunched", prereg=True, log=False, quiet=True)
    b = score(favs({1, 5, 9, 13, 17, 21, 25, 29}), "spread", prereg=True, log=False, quiet=True)
    print("4. bunched:", a["groups"], "separate bets, range", a["lo100"], a["hi100"], "| spread:", b["groups"], b["lo100"], b["hi100"])
    assert a["bunched"] and a["groups"] == 30 and not b["bunched"] and b["groups"] == 600
    assert a["hi100"] - a["lo100"] > b["hi100"] - b["lo100"]
    # 5. same event counts once
    c = score(world(300, 0.5, 0.5, ev_size=10), "ten per event", prereg=True, log=False, quiet=True)
    assert c["groups"] == 30 and c["events"] == 30, c
    # 6. real-price fills from a fake tape
    B = 1760000000
    tape = [{"timestamp": B + 1000, "price": 0.30, "size": 50, "side": "BUY", "outcomeIndex": 0},      # before the decision
            {"timestamp": B + 2100, "price": 0.41, "size": 10, "side": "SELL", "outcomeIndex": 0},     # a sell: ignore
            {"timestamp": B + 2200, "price": 0.60, "size": 99, "side": "BUY", "outcomeIndex": 1},      # other answer: ignore
            {"timestamp": (B + 2300) * 1000, "price": 0.44, "size": 100, "side": "BUY", "asset": "tokA"},    # ms time + token id
            {"timestamp": B + 2400, "price": 0.45, "size": 40, "side": "BUY", "outcomeIndex": 0},
            {"timestamp": B + 9000, "price": 0.20, "size": 40, "side": "BUY", "outcomeIndex": 0}]      # after the window
    sig = [{"cid": "a", "toks": ["tokA", "tokB"], "oi": 0, "t": B + 2000, "pay": 1.0, "ev": "E", "q": 0.38, "fee": 0.0},
           {"cid": "b", "toks": ["tokA", "tokB"], "oi": 0, "t": B + 2000, "pay": 1.0, "ev": "E", "end": B + 2250},   # stop before any buy
           {"cid": "c", "oi": 0, "t": B + 2000, "pay": 0.0, "ev": "F"}]
    info = {}
    got = fills(sig, window=3600, tape_fn=lambda s: None if s["cid"] == "c" else tape, workers=1, info=info)
    assert info == {"signals": 3, "filled": 1, "no_buy": 1, "no_tape": 1, "room": 62.0, "fits": 1}, info
    g = got[0]
    assert g["px"] == 0.44 and abs(g["sh"] - 25 / 0.45) < 1e-9 and abs(g["pay"] - 25 / 0.45) < 1e-9 and g["t"] == B + 2300, g
    print("6. fake tape: first real buy 44c (chart said 38c), 1 signal nobody could buy, 1 unreadable: ok")
    # 7. ledger: same idea twice = one line, tries only go up, and other ideas raise the luck bar
    for i in range(20):
        ledger_add({"id": f"old{i}", "tries": 1}, tmp)
    c1 = score(world(200, 0.5, 0.5), "My Idea", tries=5, ledger=tmp, quiet=True)
    c2 = score(world(200, 0.5, 0.5), "my idea", tries=2, ledger=tmp, quiet=True)
    L = ledger_load(tmp)
    mine = [r for r in L["rows"] if r["id"] == "my_idea"]
    assert len(L["rows"]) == 21 and len(mine) == 1 and mine[0]["tries"] == 5, mine
    assert c1["luck_tries"] == 25 and c2["luck_tries"] == 22
    assert "21 ideas examined" in ledger_md(tmp, tmp + ".md")
    # 8. power: a worthless test should rarely pass the "looks real" bar, a strong one usually
    strong = power(world(3000, 0.54, 0.5), 3000, bar=bar_real, sims=40)
    weak = power(world(60, 0.54, 0.5), 60, bar=bar_real, sims=40)
    print("8. pass chance (real / worthless): 3,000 bets", strong, "| 60 bets", weak)
    assert strong[0] >= 80 and strong[1] <= 10 and weak[0] <= 40, (strong, weak)
    # 8b. a hopeless pace must not crash the date (found on real wallets: year 36759)
    c = score([{"ev": i, "t": 1.76e9 + i, "cost": 10.0, "pay": 10.0001 if i else 9.0} for i in range(40)], "slow", tries=5000,
              prereg=True, log=False, quiet=True)
    assert c["eta"] is None or c["eta"] < "2200", c["eta"]
    # 9. the printed card runs for every verdict
    for bl in (world(5, 0.5, 0.5), world(200, 0.4, 0.5), world(200, 0.56, 0.5), world(3000, 0.54, 0.5), []):
        assert "Verdict:" in card_text(score(bl, "print check", prereg=True, log=False, quiet=True))
    print(card_text(score(world(400, 0.55, 0.5), "example: 55 wins in 100 at 50c, 400 bets", tries=10, ledger=tmp, log=False, quiet=True)))
    print("\nselftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest":
        selftest()
    elif cmd == "tracks":
        tracks()
    elif cmd == "ledger":
        print(ledger_md())
    elif cmd == "tapetest":
        tapetest(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == "file":
        with open(sys.argv[2]) as f:
            data = json.load(f)
        score(data["bets"] if isinstance(data, dict) else data, sys.argv[3] if len(sys.argv) > 3 else os.path.basename(sys.argv[2]),
              tries=int(sys.argv[4]) if len(sys.argv) > 4 else 1)
    else:
        sys.exit(f"unknown command {cmd}")
