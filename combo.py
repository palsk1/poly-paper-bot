#!/usr/bin/env python3
"""The everything-together model (2026-11-10, Jan: "let's try it"). Research only, PAPER ONLY.

Every test so far looked at one or two things at a time (price, kind of market, weekday). This is one math model
(gradient-boosted trees, scikit-learn) that looks at everything at once and guesses the chance of Yes:
price, how the price moved (1/3/7 days, highs and lows, how jumpy), kind of market, time left, age, the rival
choices in the same event (how many, what they add up to, who leads), weekday, fee.

Honest set-up (walk-forward, nothing is judged on data the model saw):
  learn    : markets that ENDED before 2026-08-10  (the model only learns from results it could have known)
  tune     : inside that, the last 6 weeks pick the betting rule (how big a gap between model and price to bet on)
  judge    : every noon 2026-08-10 .. 2026-11-09, markets ending before the holdout day (2026-11-10), events the
             model never saw. One bet per market: the first noon the rule fires. Scored ONCE.
Two versions, both judged: "with the clock" (uses time left) and "no clock" (doesn't; guards against the end date
leaking the result). Prices: chart + what real buyers paid on top (yesno.POLY_EXTRA) + fee; then the judged bets
are re-priced at real buys from the trade tape (exam.fills) and graded by the shared exam (exam.score).

Polymarket only: our Kalshi history is 2 months and has nothing to learn on.

    python3 backtest.py btcombo      # probe `btcombo` (ref=main cache), report backtest/combo.md
    python3 combo.py selftest        # offline: a fair world gives no profit, a planted pattern is found
"""
import collections
import datetime as dt
import math
import os
import random
import subprocess
import sys
import time

import bot
import backtest as bt
import yesno

DAY = 86400
T_START = yesno.tsec("2026-03-01") + 12 * 3600
T_TEST = yesno.tsec("2026-08-10") + 12 * 3600          # first judged noon
T_TUNE = yesno.tsec("2026-06-29")                      # markets ending from here to T_TEST pick the rule
T_LAST = yesno.tsec("2026-11-09") + 12 * 3600
CUT = yesno.tsec(yesno.HOLDOUT_FROM)
GRID = list(range(T_START, T_LAST + 1, DAY))
THRESHOLDS = [0.02, 0.03, 0.05, 0.08, 0.12]            # gap (in dollars a share) between model and cost
PX_LO, PX_HI = 0.05, 0.95                              # only bet where the cost is between 5c and 95c
STAKE = 25.0
FEATS = ["price", "price 1 day ago", "price 3 days ago", "price 7 days ago", "highest so far", "lowest so far",
         "how jumpy (7 days)", "age of the market (days)", "rival choices in the event", "what the choices add up to",
         "the leader's price", "weekday", "fee", "kind of market", "days left"]
CLOCK = len(FEATS) - 1
KIND = FEATS.index("kind of market")
T0 = time.time()


def need_sklearn():
    try:
        import sklearn  # noqa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-learn"], check=True)
        import importlib
        import site
        site.addsitedir(site.getusersitepackages())      # pip may have just created the user folder
        importlib.invalidate_caches()


# ================================================================ rows
def build(markets, hist):
    """One row per market per noon it was open with a fresh price. Returns dict of numpy arrays + lists."""
    import numpy as np
    import calib
    G = np.array(GRID, dtype=np.int64)
    kinds = {}
    per = []                      # (mid, mk, yi, pay_yes, kind id, idx array, p_now, pv_all)
    ev_sum, ev_cnt, ev_max = {}, {}, {}
    skipped = collections.Counter()
    for mid, mk in markets.items():
        if not mk.get("end") or mk["end"] >= CUT:
            skipped["ends in holdout"] += 1
            continue
        yi = yesno.poly_side_index(mk)
        y0 = calib.outcome0(mk) if yi is not None else None
        h = hist.get(mid)
        if yi is None or y0 is None or not h or not h[0]:
            skipped["not usable"] += 1
            continue
        T = np.array(h[0], dtype=np.int64)
        P = np.array(h[1], dtype=np.float64)
        if yi == 1:
            P = 1 - P
        k = np.searchsorted(T, G, side="right") - 1
        ok = k >= 0
        kk = np.clip(k, 0, len(T) - 1)
        last_t = T[kk]
        pv = np.where(ok & (G - last_t <= 3 * DAY), P[kk], np.nan)            # last price, up to 3 days old
        stop = min(mk["end"], mk.get("closed_t") or mk["end"])
        live = ok & (G - last_t <= 13 * 3600) & (G < stop) & (G >= (mk.get("start") or 0)) & (pv > 0) & (pv < 1)
        if not live.any():
            skipped["never open at a noon"] += 1
            continue
        ev = mk.get("ev") or mid
        tp = "sports" if mk.get("sports") else calib.topic(mk["q"])
        kid = kinds.setdefault(tp, len(kinds))
        pn = np.where(live, pv, 0.0)
        if ev not in ev_sum:
            ev_sum[ev], ev_cnt[ev], ev_max[ev] = np.zeros(len(G)), np.zeros(len(G)), np.zeros(len(G))
        ev_sum[ev] += pn
        ev_cnt[ev] += live
        ev_max[ev] = np.maximum(ev_max[ev], pn)
        per.append((mid, mk, yi, float(y0 if yi == 0 else 1 - y0), kid, live, pv, ev))
    print(f"combo: {len(per):,} markets usable, skipped {dict(skipped)} ({time.time() - T0:.0f}s)")
    X, y, t, mi, cost_meta = [], [], [], [], []
    wd = np.array([dt.datetime.fromtimestamp(g, dt.timezone.utc).weekday() for g in GRID], dtype=np.float64)
    for j, (mid, mk, yi, pay, kid, live, pv, ev) in enumerate(per):
        idx = np.nonzero(live)[0]
        n = len(pv)

        def lag(d):
            out = np.full(n, np.nan)
            out[d:] = pv[:-d]
            return out
        filled = np.where(np.isnan(pv), -np.inf, pv)
        hi = np.maximum.accumulate(filled)
        lo = np.minimum.accumulate(np.where(np.isnan(pv), np.inf, pv))
        d1 = np.abs(pv - lag(1))
        jump = np.full(n, np.nan)
        for i in idx:
            w = d1[max(0, i - 6):i + 1]
            w = w[~np.isnan(w)]
            if len(w) >= 3:
                jump[i] = w.mean()
        start = mk.get("start") or 0
        f = np.column_stack([
            pv[idx], lag(1)[idx], lag(3)[idx], lag(7)[idx], hi[idx], lo[idx], jump[idx],
            (G[idx] - start) / DAY if start else np.full(len(idx), np.nan),
            ev_cnt[ev][idx], ev_sum[ev][idx], ev_max[ev][idx], wd[idx],
            np.full(len(idx), mk.get("fee") or 0.0), np.full(len(idx), float(kid)),
            (mk["end"] - G[idx]) / DAY])
        X.append(f)
        y.append(np.full(len(idx), pay))
        t.append(G[idx])
        mi.append(np.full(len(idx), j))
    X = np.vstack(X).astype(np.float32)
    data = {"X": X, "y": np.concatenate(y), "t": np.concatenate(t), "m": np.concatenate(mi), "per": per,
            "kinds": kinds}
    print(f"combo: {len(X):,} rows, {X.shape[1]} things per row ({time.time() - T0:.0f}s)")
    return data


# ================================================================ model + bets
def fit(X, y, groups, cols):
    """Gradient-boosted trees on the chosen columns. Each event gets about the same say."""
    import numpy as np
    from sklearn.ensemble import HistGradientBoostingClassifier
    _, inv, cnt = np.unique(groups, return_inverse=True, return_counts=True)
    w = 1.0 / np.sqrt(cnt[inv])
    cat = [i for i, c in enumerate(cols) if c == KIND]
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=200,
                                       l2_regularization=1.0, categorical_features=cat or None, random_state=1)
    m.fit(X[:, cols], y, sample_weight=w)
    return m


def logloss(q, y):
    import numpy as np
    q = np.clip(q, 1e-4, 1 - 1e-4)
    return float(-(y * np.log(q) + (1 - y) * np.log(1 - q)).mean())


def make_bets(data, rows, q, thr):
    """One bet per market: the first noon where model minus cost (incl. fee) is at least thr on either side."""
    import numpy as np
    X, y, t, m, per = data["X"], data["y"], data["t"], data["m"], data["per"]
    order = rows[np.argsort(t[rows], kind="stable")]
    qmap = dict(zip(rows.tolist(), q.tolist()))
    done, bets = set(), []
    for r in order.tolist():
        j = int(m[r])
        if j in done:
            continue
        p, fee, qy = float(X[r, 0]), float(X[r, 12]), qmap[r]
        best = None
        for side, pp, qq, pay in (("Yes", p, qy, y[r]), ("No", 1 - p, 1 - qy, 1 - y[r])):
            c = min(0.999, pp + yesno.POLY_EXTRA[yesno.band(pp)])
            if not PX_LO <= c <= PX_HI:
                continue
            f = fee * c * (1 - c)
            edge = qq - c - f
            if edge >= thr and (best is None or edge > best[0]):
                best = (edge, side, c, f, float(pay), pp)
        if best is None:
            continue
        done.add(j)
        edge, side, c, f, pay, pp = best
        mid, mk, yi = per[j][0], per[j][1], per[j][2]
        sh = STAKE / (c + f)
        bets.append({"ev": per[j][7], "t": int(t[r]), "cost": STAKE, "pay": sh * pay, "sh": sh, "side": side, "px": c,
                     "edge": edge, "kind": per[j][4],
                     "sig": {"id": mid, "oi": yi if side == "Yes" else 1 - yi, "t": int(t[r]), "pay": pay,
                             "ev": per[j][7], "fee": fee, "toks": mk.get("toks"), "q": pp}})
    return bets


def quick(bets):
    """(per $100, low end of the 90% luck range by event, separate events)."""
    import exam
    if not bets:
        return None, None, 0
    g = exam._groups(bets, lambda b, i: str(b["ev"]))
    rate, se = exam._rate_se(list(g.values()))
    return 100 * rate, 100 * (rate - exam.Z90 * se) if se < float("inf") else None, len(g)


def experiment(data, log=True):
    """Tune on the last weeks of the learning period, judge once on the unseen months. Returns report lines + cards."""
    import numpy as np
    import exam
    X, y, t, m, per = data["X"], data["y"], data["t"], data["m"], data["per"]
    end = np.array([p[1]["end"] for p in per])[m]
    ev = np.array([p[7] for p in per], dtype=object)[m]
    learn_all = np.nonzero(end < T_TEST - 12 * 3600)[0]
    learn_a = np.nonzero(end < T_TUNE)[0]
    tune = np.nonzero((end >= T_TUNE) & (end < T_TEST - 12 * 3600) & (t >= T_TUNE))[0]
    seen = set(ev[learn_all].tolist())
    judge = np.nonzero((t >= T_TEST) & np.array([e not in seen for e in ev.tolist()]))[0]
    print(f"combo: learn {len(learn_all):,} rows, tune {len(tune):,}, judge {len(judge):,} ({time.time() - T0:.0f}s)")
    L, cards = [], {}
    L += [f"- Learned on **{len(learn_all):,}** market-days ({len(set(m[learn_all].tolist())):,} markets that ended before 10 Aug).",
          f"- Judged on **{len(judge):,}** market-days ({len(set(m[judge].tolist())):,} markets, 10 Aug - 9 Nov) it never saw.", ""]
    versions = [("with the clock", list(range(len(FEATS)))), ("no clock", [i for i in range(len(FEATS)) if i != CLOCK])]
    tries = len(THRESHOLDS) * len(versions)
    rows_tab, guess_tab = [], []
    for name, cols in versions:
        # 1. pick the rule on the tuning weeks
        ma = fit(X[learn_a], y[learn_a], ev[learn_a], cols)
        qt = ma.predict_proba(X[tune][:, cols])[:, 1]
        best = None
        for thr in THRESHOLDS:
            b = make_bets(data, tune, qt, thr)
            r, lo, k = quick(b)
            print(f"  {name}: tune gap {thr * 100:.0f}c -> {len(b)} bets, {k} events, per $100 {r}, low end {lo}")
            if r is not None and k >= 30 and (best is None or (lo or -1e9) > best[1]):
                best = (thr, lo or -1e9, r, len(b))
        thr = best[0] if best else THRESHOLDS[2]
        # 2. learn on everything before the judged months, judge once
        mf = fit(X[learn_all], y[learn_all], ev[learn_all], cols)
        qj = mf.predict_proba(X[judge][:, cols])[:, 1]
        pj = X[judge, 0].astype(np.float64)
        ll_m, ll_p = logloss(qj, y[judge]), logloss(pj, y[judge])
        guess_tab.append(f"| {name} | {ll_p:.4f} | {ll_m:.4f} | {'the model' if ll_m < ll_p else 'the price'} |")
        bets = make_bets(data, judge, qj, thr)
        card = exam.score(bets, f"everything-together model, {name}", tries=tries, log=False, quiet=True)
        cards[name] = (card, bets, thr, mf, cols, best)
        yes = sum(1 for b in bets if b["side"] == "Yes")
        rows_tab.append(f"| {name} | {thr * 100:.0f}c (tuning weeks: {'-' if not best else yesno.usd(best[2])} per $100 on {best[3] if best else 0} bets) | "
                        f"{card['bets']:,} ({yes:,} Yes, {card['bets'] - yes:,} No) | {card.get('groups', 0):,} | "
                        f"{'-' if card.get('per100') is None else yesno.usd(card['per100'])} | "
                        f"{'-' if card.get('lo100') is None else yesno.usd(card['lo100']) + ' to ' + yesno.usd(card['hi100'])} | "
                        f"{'-' if card.get('half1') is None else yesno.usd(card['half1']) + ' / ' + yesno.usd(card['half2'])} | "
                        f"{'-' if card.get('floor100') is None else yesno.usd(card['floor100'])} | {card['verdict']} |")
    L += ["## Does the model guess better than the price?", "",
          "A score for how wrong the guesses were on the judged months (lower is better). If the price wins, the model "
          "has nothing to sell.", "", "| Version | The market price | The model | Better guesser |", "|---|---|---|---|"] + guess_tab + [""]
    L += ["## The model's bets on the months it never saw", "",
          "It bets $25 when its own chance is at least the 'gap' above what the bet costs (chart price + the usual extra + "
          "fee). One bet per market, held to the end.", "",
          "| Version | Gap it bets on | Bets | Separate events | Per $100 | Luck range | First / second half | Worst case per $100 | Verdict |",
          "|---|---|---|---|---|---|---|---|---|"] + rows_tab + [""]
    return L, cards, tries


def importance(mf, cols, X, y, n=60000, seed=3):
    """How much worse the guesses get when one thing is scrambled (bigger = the model leans on it more)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), size=min(n, len(X)), replace=False)
    Xs, ys = X[idx][:, cols].copy(), y[idx]
    base = logloss(mf.predict_proba(Xs)[:, 1], ys)
    out = []
    for i, c in enumerate(cols):
        keep = Xs[:, i].copy()
        Xs[:, i] = rng.permutation(keep)
        out.append((logloss(mf.predict_proba(Xs)[:, 1], ys) - base, FEATS[c]))
        Xs[:, i] = keep
    return sorted(out, reverse=True)


def run():
    need_sklearn()
    import numpy as np
    import ideas
    import exam
    markets, hist, complete = ideas.load_full()
    print(f"combo: {len(markets):,} markets loaded")
    data = build(markets, hist)
    L = ["# One model that looks at everything together (2026-11-10, `combo.py`)", "",
         "Research only. Every earlier test looked at one or two things at a time. This is one math model "
         "(gradient-boosted trees) that reads price, price moves, kind of market, time left, age, the rival choices in the "
         "event, weekday and fee together, and guesses the chance of Yes. It learned only from markets that ended before "
         "10 Aug, picked its betting rule on the last 6 weeks of those, and was then judged once on 10 Aug - 9 Nov. "
         "Polymarket only (our Kalshi history is too short to learn on).", ""]
    body, cards, tries = experiment(data)
    L += body
    X, y, t, m = data["X"], data["y"], data["t"], data["m"]
    kinds = {v: k for k, v in data["kinds"].items()}
    for name, (card, bets, thr, mf, cols, best) in cards.items():
        if not bets:
            continue
        L += [f"## '{name}': a closer look", ""]
        # where the bets sit
        by = collections.defaultdict(list)
        for b in bets:
            by[(b["side"], yesno.band(b["px"]))].append(b)
            by[("kind", kinds.get(b["kind"], "?"))].append(b)
        L += ["| Slice | Bets | Per $100 |", "|---|---|---|"]
        for k in sorted(by, key=lambda k: -len(by[k]))[:14]:
            r, lo, n_ev = quick(by[k])
            L.append(f"| {k[0]}: {k[1]} | {len(by[k]):,} | {yesno.usd(r)} |")
        L.append("")
        # real buys
        rng = random.Random(9)
        pick = rng.sample(bets, min(int(os.environ.get("COMBO_TAPE_N", "900")), len(bets)))
        info = {}
        try:
            real = exam.fills([b["sig"] for b in pick], info=info)
            rc = exam.score(real, f"everything-together model, {name}, real buys", tries=tries, log=False, quiet=True)
            same_r, _, _ = quick(pick)
            L += [f"**At real buys:** {len(pick):,} of its bets checked on the trade tape. {info.get('filled')} had a real buy within "
                  f"3 hours (the rest: nobody was selling). Those came out at "
                  f"**{'-' if rc.get('per100') is None else yesno.usd(rc['per100'])} per $100** "
                  f"(luck range {'-' if rc.get('lo100') is None else yesno.usd(rc['lo100']) + ' to ' + yesno.usd(rc['hi100'])}, "
                  f"worst case {'-' if rc.get('floor100') is None else yesno.usd(rc['floor100'])}). "
                  f"Exam verdict: **{rc['verdict']}**. (The same {len(pick):,} bets at chart prices: {yesno.usd(same_r)}.)", ""]
            print(f"REAL {name}: {rc.get('per100')} per $100, {rc.get('lo100')}..{rc.get('hi100')}, {rc['verdict']}, filled {info.get('filled')}")
        except Exception as e:
            L += [f"Real-buy check failed: {str(e)[:120]}", ""]
        judge = np.nonzero(t >= T_TEST)[0]
        imp = importance(mf, cols, X[judge], y[judge])
        L += ["What the model leans on most: " + ", ".join(f"{nm} ({d * 1000:.1f})" for d, nm in imp[:6]) + ".", ""]
        print(f"CARD {name}: {card.get('per100')} per $100, {card.get('lo100')}..{card.get('hi100')}, floor {card.get('floor100')}, "
              f"{card['verdict']}, bets {card['bets']}, gap {thr}")
    L += ["## Limits", "",
          "- Chart prices are 12-hourly, so the price the model sees can be up to 13 hours old. The real-buy check is the "
          "number to trust.",
          "- Judged months include only markets that ended before 2026-11-10 (we need the result; later ones are the holdout).",
          "- bt_cache has markets with $20k+ traded plus every choice of those events. Tiny markets are missing.", ""]
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "combo.md"), "w") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


# ================================================================ selftest
def fake_world(planted, n=5000, seed=1):
    rng = random.Random(seed)
    markets, hist = {}, {}
    for k in range(n):
        end = rng.randrange(T_START + 20 * DAY, CUT - DAY)
        start = end - rng.randrange(8, 40) * DAY
        p = rng.uniform(0.08, 0.92)
        sports = planted and k % 4 == 0
        true = min(0.97, p + 0.12) if sports else p          # planted: 'sports' markets are 12c too cheap
        win = rng.random() < true
        T, P, tt = [], [], start
        while tt < end:
            T.append(tt)
            P.append(round(p, 4))          # no wobble: a wobbling price around the truth is itself beatable
            tt += 43200
        mid = str(k)
        markets[mid] = {"id": mid, "q": f"Will thing {k} happen?", "outs": ["Yes", "No"], "toks": [f"{k}y", f"{k}n"],
                        "end": end, "start": start, "closed": True, "closed_t": end + 3600,
                        "final": [1.0, 0.0] if win else [0.0, 1.0], "uma": "resolved", "vol": 50000, "fee": 0.0,
                        "sports": sports, "slug": f"m{k}", "ev": f"e{k}", "ev_slug": f"e{k}"}
        hist[mid] = [T, P]
    return markets, hist


def selftest():
    need_sklearn()
    for planted in (False, True):
        markets, hist = fake_world(planted)
        data = build(markets, hist)
        L, cards, tries = experiment(data, log=False)
        card = cards["no clock"][0]
        print(f"selftest planted={planted}: {card['bets']} bets, per $100 {card.get('per100')}, verdict {card['verdict']}")
        if planted:
            assert card["bets"] >= 50 and card["per100"] > 5, card
        else:
            assert card["bets"] < 200 or card["per100"] < 3, card
    print("combo selftest OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"selftest": selftest, "run": run}[cmd]()
