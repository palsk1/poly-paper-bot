# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1666 coin-windows from 2026-11-10T10:30 to 2026-11-13T15:00 UTC (238 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **24 of 1666** windows. Reading the Kalshi book takes about 177 ms (slowest 1 in 10: 251 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1194 | 91 | 90 | 1 | 99.79c | $-9.00 | $-1.00 | needs ~3426 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 981 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1194 | 39 | 38 | 1 | 99.42c | $-7.86 | $-2.05 | needs ~662 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1440 | 315 | 314 | 4 | 98.87c | $-8.05 | $-0.26 | needs ~471 more bets with no loss |
| Buy now, 60 s left (z 4+) | 971 | 123 | 119 | 0 | 99.67c | $+2.60 | $+0.22 | needs ~931 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1421 | 72 | 72 | 0 | 99.46c | $+3.03 | $+0.42 | needs ~474 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 542 | 538 | 537 | 29 | 93.34c | $+45.34 | $+0.90 | needs ~54 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1194 | 91 | 88 | 1 | 99.79c | $-83.56 | $-0.95 | needs ~1996 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 981 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1194 | 39 | 34 | 1 | 99.42c | $-79.65 | $-2.22 | needs ~651 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1440 | 315 | 306 | 4 | 98.91c | $-84.92 | $-0.28 | needs ~468 more bets with no loss |
| Buy now, 60 s left (z 4+) | 971 | 123 | 116 | 0 | 99.68c | $+34.74 | $+0.30 | needs ~653 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1421 | 72 | 69 | 0 | 99.49c | $+33.52 | $+0.47 | needs ~415 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 542 | 538 | 534 | 29 | 93.49c | $+399.09 | $+0.79 | needs ~62 more bets with no loss |

