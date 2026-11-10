# kc_maker_safe: checked the way a trading firm would (kcdepth, 2026-11-10)

## In plain words (Claude, 2026-11-10)

- **A filled bid is not a warning sign here.** Filled bets won 99.4 times in 100, all signals 99.5. A minute after
  we bid, the price had still moved our way (+0.16c). Plain market makers lose because the bids that fill are the
  ones about to go wrong. With the spot check, that effect is tiny.
- **Losses come in small bunches, not big ones.** 54 losses sat in 47 windows (at most 3 coins lost together).
  With $10 bets: 12 losing days out of 61, worst day -$22.14, a typical day +$9.32.
- **A fair yes/no is possible by about 1 Dec.** The live track makes ~115 bets a day. Proposed pass bar, written
  now, before the results: **after 2,500 live bets (around 1 Dec), pass if the live P&L is above +$0.22 per $100.**
  A track with no real edge passes that only 1 time in 10. If the backtest is right, it passes 96 times in 100.
  Earlier check: 1,500 bets (around 22 Nov), bar +$0.29 (passes 86 in 100 if the backtest is right).
- **Live so far:** 83 bets, 1 lost, -$0.06 per $100. Far too early. At the live average price (98.9c) one loss eats
  about 86 wins; the backtest had 1 loss in 160 bets.
- **A $300 pot with $10 bets, if the backtest is right**, never fell below $250 in 4,000 tries over 30 or 60 days.
  That is a big "if": it is what the live test is for.
- Not answered: whether $25-$100 orders fill the same, and whether Kalshi accepts a Swedish account.

Research only, paper only. Data: 39833 Kalshi 15-minute crypto windows, 2026-09-11 to 2026-11-10. Rule: improve, leader bid 95c+, 3 min left, Binance spot z >= 2.0, 'fair' fills (same as backtest/kcrypto.md). Code: `kcrypto.py depth`, probe `btkcdepth` (run 42823059046).

Backtest: 8632 filled bets over 61 days, 54 lost, average price 98.8c, +$0.57 per $100.

## A. Does a filled bid mean trouble? (price 1 and 2 minutes after we bid)

If the bets that get filled are the ones about to go wrong, the price drops after they fill and filled bets win less often than all signals. That is how market makers lose money.

| Group | Bets | Won out of 100 | Price after 1 min vs our bid | After 2 min |
|---|---|---|---|---|
| All signals | 10995 | 99.5 | +0.27c | +0.55c |
| Filled | 8632 | 99.4 | +0.16c | +0.47c |
| Not filled | 2363 | 100.0 | +0.69c | +0.84c |

## B. Do losses come in bunches?

- 8632 bets sit in 3258 different 15-minute windows (up to 7 coins share a window).
- The 54 losses happened in 47 windows: 41 windows with 1 loss, 5 windows with 2 losses, 1 window with 3 losses.
- Losing days with $10 bets: 12 of 61. Worst day -$22.14, best day +$29.55, typical day +$9.32.
- So the real number of independent chances is closer to the number of losing *windows* than the number of bets. Every test below resamples whole windows or whole days, never single bets.

## C. The pass bar for the live track (written before the live results)

Two made-up worlds, both built from the real 60 days by drawing whole 15-minute windows: 'no edge' (the same bets with the average profit removed, so it breaks even) and 'backtest is right'. The bar is the live P&L per $100 that the no-edge world beats only 1 time in 10. That is our 90% test.

| Live bets | Pass if live P&L per $100 is above | Chance a truly break-even track passes | Chance the backtest's track passes |
|---|---|---|---|
| 300 | +$0.62 | 10 in 100 | 51 in 100 |
| 600 | +$0.46 | 10 in 100 | 66 in 100 |
| 1000 | +$0.36 | 10 in 100 | 79 in 100 |
| 1500 | +$0.29 | 10 in 100 | 86 in 100 |
| 2500 | +$0.22 | 10 in 100 | 96 in 100 |
| 4000 | +$0.17 | 10 in 100 | 100 in 100 |

Live so far: 83 bets, 1 lost, average price 98.9c, -$0.06 per $100, about 115 bets a day.
Average live price vs backtest: 98.9c vs 98.8c (a higher price means a smaller win per bet).
- At the live average price one loss eats about 86 wins, so break-even is about 1 loss in 87 bets. The backtest had 1 loss in 160.
- 1000 live bets reached around day 9 after the start (9 Nov 19:00 UTC).
- 1500 live bets reached around day 13 after the start (9 Nov 19:00 UTC).
- 2500 live bets reached around day 22 after the start (9 Nov 19:00 UTC).

Use one bar, not all of them: looking at every row and stopping at the first pass would make a lucky pass more likely than 1 in 10.

## D. A $300 pot with $10 bets, played out on real days

Each run strings together whole days drawn from the 60 (so bad days and bad windows stay intact). 4000 runs each.

| Days | Typical end | Worst 1 in 20 | Ends below $300 | Drops below $250 at some point | Drops below $200 |
|---|---|---|---|---|---|
| 30 | $543 | $452 | 0 in 100 | 0 in 100 | 0 in 100 |
| 60 | $787 | $658 | 0 in 100 | 0 in 100 | 0 in 100 |

Limits: 60 days only; Binance stands in for the index Kalshi settles on; size that fills at $25-$100 is unknown; the live bot bids anywhere from 0.75 to 5.5 minutes left, the backtest at exactly 3.
