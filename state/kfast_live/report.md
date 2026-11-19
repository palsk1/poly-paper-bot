# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4634 coin-windows from 2026-11-10T10:30 to 2026-11-19T17:30 UTC (662 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **78 of 4634** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3309 | 276 | 268 | 2 | 99.65c | $-13.64 | $-0.51 | needs ~1969 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2709 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3309 | 136 | 132 | 3 | 99.20c | $-19.82 | $-1.49 | needs ~740 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3958 | 923 | 915 | 14 | 98.90c | $-48.87 | $-0.54 | needs ~1101 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2692 | 367 | 356 | 3 | 99.67c | $-22.35 | $-0.63 | needs ~2744 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3892 | 207 | 204 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~583 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1550 | 1541 | 1533 | 108 | 92.73c | $-32.34 | $-0.23 | needs ~246 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3309 | 276 | 263 | 2 | 99.66c | $-116.76 | $-0.44 | needs ~1416 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2709 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3309 | 136 | 122 | 3 | 99.19c | $-201.13 | $-1.60 | needs ~718 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3958 | 923 | 897 | 14 | 98.93c | $-493.52 | $-0.55 | needs ~1087 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2692 | 367 | 348 | 3 | 99.68c | $-197.32 | $-0.56 | needs ~1922 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3892 | 207 | 198 | 0 | 99.62c | $+71.59 | $+0.36 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1550 | 1541 | 1523 | 108 | 92.87c | $-468.38 | $-0.33 | needs ~266 more bets with no loss |

