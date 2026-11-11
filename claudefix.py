#!/usr/bin/env python3
"""Can a simple fix save the `claude` track? (2026-11-11, Jan picked "test fixes in history first"). Research only.

PAPER ONLY. Reads bt_cache, never trades, never writes state/.

The live `claude` track buys the boring side (mostly "No, the dramatic thing won't happen") at 85-94c with
10-60 days left, sells at 97c (take profit) and at 70c (stop loss). backtest/report.md says it loses about
$5.90 per $100. This replays a few versions through the real engine (btcheck.engine), with the pessimistic
costs from backtest/PROTOCOL.md (+2c, bought 1 hour late, take-profit sold at the target), and grades each with
the shared exam (exam.py).

Versions, fixed before looking at results:
    now       97c take profit + 70c stop loss (the live rules)
    no_stop   97c take profit, no stop loss
    no_tp     70c stop loss, no take profit (held to the end otherwise)
    hold      no take profit, no stop loss: held to the end
    hold_30d  held to the end, only 30-60 days left (closer to boring_no)

Round 2 (same day, Jan said "go" to using `claude` as a sandbox Claude tweaks): `min_volume` is off in these
because the history only has each market's FINAL volume (a look-ahead). `order: random` = pick at random among
the "No" candidates instead of soonest deadline first (random bets in the same band did better in round 1).

    python3 claudefix.py round2   # -> backtest/claudefix_r2.md
    python3 claudefix.py          # needs bt_cache/markets.json.gz + hist.json.gz (store.py pull, or the release)
                                  # -> backtest/claudefix.md
"""
import os
import sys
import time

import backtest as bt
import btcheck as bc
import bot
import exam

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "backtest", "claudefix.md")

VARIANTS = {
    "now": {},
    "no_stop": {"stop_loss": None},
    "no_tp": {"take_profit": None},
    "hold": {"take_profit": None, "stop_loss": None},
    "hold_30d": {"take_profit": None, "stop_loss": None, "min_days": 30},
}
ROUND2 = {
    "now_nv": {"min_volume": 0},
    "hold_nv": {"take_profit": None, "stop_loss": None, "min_volume": 0},
    "hold30_nv": {"take_profit": None, "stop_loss": None, "min_volume": 0, "min_days": 30},
    "now_rand": {"min_volume": 0, "order": "random"},
    "hold_rand": {"take_profit": None, "stop_loss": None, "min_volume": 0, "order": "random"},
    "hold30_rand": {"take_profit": None, "stop_loss": None, "min_volume": 0, "min_days": 30, "order": "random"},
    "hold30_9097_rand": {"take_profit": None, "stop_loss": None, "min_volume": 0, "min_days": 30,
                         "min_price": 0.90, "max_price": 0.97, "order": "random"},
}
PLAIN2 = {
    "now_nv": "Live rules, no volume filter",
    "hold_nv": "Hold to the end, no volume filter",
    "hold30_nv": "Hold to the end, 30-60 days, no volume filter",
    "now_rand": "Live rules, random pick",
    "hold_rand": "Hold to the end, random pick",
    "hold30_rand": "Hold to the end, 30-60 days, random pick",
    "hold30_9097_rand": "Hold to the end, 30-60 days, 90-97c, random pick",
}
PLAIN = {
    "now": "Live rules: sell at 97c, sell at 70c",
    "no_stop": "Sell at 97c, never sell at a loss",
    "no_tp": "Sell at 70c, otherwise hold to the end",
    "hold": "Hold every bet to the end",
    "hold_30d": "Hold to the end, only 30-60 days left",
}


def add_tracks():
    names = []
    for k, over in VARIANTS.items():
        key = f"_cf_{k}"
        bot.CFG["rules"][key] = {"inherit": "claude", **over}
        bot.CFG["tracks"][key] = {"start_cash": 50, "source": "screener", "rules": key}
        names.append(key)
    return names


def bets_of(tr, chk):
    """Exam bets from the engine's finished trades, with the take-profit capped at the target (rows_cap)."""
    out = []
    caps = {round(t0): (p, s) for p, s, t0 in chk["rows_cap"]}
    for c in tr["closed"]:
        t0 = bc.pt(c["opened"])
        if round(t0) not in caps:
            continue
        p, s = caps[round(t0)]
        out.append({"ev": c.get("event_key") or c.get("event_slug") or c.get("token"), "t": t0, "cost": s, "pay": s + p})
    return out


def run():
    t_all = time.time()
    bt.Clock.real_now = bot.now()
    markets_all, hist = bc.load_cache()
    markets = bc.in_sample(markets_all)
    names = add_tracks()
    res = {}
    for label, slip, delay in (("1c", 0.01, 0), ("2c + 1h later", 0.02, 3600)):
        t0 = time.time()
        trs = bc.engine(markets, hist, slip, names, delay)
        chk = bc.recheck(trs, markets, hist, slip, delay)
        res[label] = (trs, chk)
        print(f"pass {label}: {sum(len(t['closed']) for t in trs.values())} trades in {time.time() - t0:.0f}s", flush=True)
    trs, chk = res["2c + 1h later"]
    twins = bc.random_vs_strategy(trs, markets, hist, 0.02)

    L = ["# Can a simple fix save the `claude` track?", "",
         f"Generated {bot.iso()} by `claudefix.py`. Paper only. {len(markets):,} finished Polymarket markets that ended "
         f"before {bc.HOLDOUT_FROM} (bt_cache). Each version replayed with the real picking code, 2 picks a day, no cash "
         "limit. Decision number = the pessimistic one (PROTOCOL.md): bought 1 hour late at the chart price +2c plus "
         "fee, a take-profit sold at the target. Money is per $100 bet.", "",
         "| Version | Bets (won/lost) | Per $100, +1c | Per $100, +2c 1h late | 1st / 2nd half | Random bets, same band and exits | Exam verdict | Worst case per $100 |",
         "|---|---|---|---|---|---|---|---|"]
    cards = {}
    for n in names:
        k = n[4:]
        c1 = bc.ratio_stats([(p, s) for p, s, _ in res["1c"][1][n]["rows_cap"]])
        rows = chk[n]["rows_cap"]
        c2 = bc.ratio_stats([(p, s) for p, s, _ in rows])
        a, b = bc.halves_of(rows)
        won = sum(1 for p, _, _ in rows if p > 0)
        bets = bets_of(trs[n], chk[n])
        card = exam.score(bets, f"claude track fix: {PLAIN[k]}", tries=len(VARIANTS) + (5 if VARIANTS is ROUND2 else 0), src="claudefix.py",
                          note="2c + 1h late, TP capped", quiet=True, log=(k != "now"))
        cards[k] = card
        tw = twins.get(n, {}).get("same")
        L.append(f"| {PLAIN[k]} | {len(rows)} ({won}/{len(rows) - won}) | {bc.m100(c1 and c1['per100'])} | "
                 f"{bc.m100(c2 and c2['per100'])} | {bc.m100(a and a['per100'])} / {bc.m100(b and b['per100'])} | "
                 f"{bc.m100(tw and tw['per100'])} | {card.get('verdict')} | {bc.m100(card.get('floor100'))} |")
    L += ["", "How to read it: 'Random bets' = for each bet, a random other market open at the same time with the same "
          "days left and price band, same exits and costs. If the version doesn't beat that, the picking adds nothing.",
          "", "## Exam cards", ""]
    for k, card in cards.items():
        L += [f"### {PLAIN[k]}", "", "```", exam.card_text(card), "```", ""]
    L.append(f"Run time {time.time() - t_all:.0f}s.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["round2"]:
        VARIANTS, PLAIN = ROUND2, PLAIN2
        OUT = os.path.join(ROOT, "backtest", "claudefix_r2.md")
    run()
