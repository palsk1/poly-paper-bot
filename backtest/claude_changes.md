# The `claude` sandbox: change log

Jan, 2026-11-11: "it'd be fun with one strategy that you can tweak and change, every day if you want to, just to
experiment". So `claude` is Claude's sandbox. Rules (CLAUDE.md hard rule 4): at most 1-2 small changes a day, each
checked on history first (`claudefix.py`, or the tool that fits), each with one plain line here, each reported to Jan.

Because the rules keep changing, its score never adds up to proof: it is a place to try ideas cheaply, not a
candidate for the 1 Jan money. An idea that looks good here gets its own frozen track (with Jan's OK).

| # | Date | What changed | Why | History check (per $100, real costs) | How the old version did live |
|---|---|---|---|---|---|
| 0 | 2026-11-03 | Start: boring side at 85-94c, 10-60 days left, soonest deadline first, sell at 97c, sell at 70c | Claude's first guess: "nothing happens" is often cheap | -$8.30 on 364 past bets (`backtest/claudefix.md`) | - |
| 1 | 2026-11-11 | No side at 90-97c, 30-60 days left, random pick among them, no early selling (held to the end). The 9 open bets are now held to the end too | Every simple fix of the old rules lost; random bets in the same price range did better than its "soonest deadline first" picks; boring_no (90-97c, 30+ days) tested well on real trades | -$3.99 on 359 past bets, still losing, but half the old loss (`backtest/claudefix_r2.md`) | 4 won, 0 lost, +$1.28 (luck-sized) |
