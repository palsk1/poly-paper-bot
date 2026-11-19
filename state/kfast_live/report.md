# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4466 coin-windows from 2026-11-10T10:30 to 2026-11-19T06:15 UTC (638 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **76 of 4466** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3187 | 271 | 263 | 2 | 99.65c | $-13.67 | $-0.52 | needs ~1942 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2610 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3187 | 135 | 131 | 3 | 99.20c | $-19.87 | $-1.51 | needs ~739 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3816 | 905 | 897 | 14 | 98.89c | $-49.75 | $-0.56 | needs ~1099 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2595 | 356 | 345 | 3 | 99.67c | $-22.49 | $-0.65 | needs ~2715 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3754 | 206 | 203 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~580 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1501 | 1492 | 1484 | 104 | 92.79c | $-34.48 | $-0.25 | needs ~248 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3187 | 271 | 259 | 2 | 99.66c | $-117.40 | $-0.45 | needs ~1407 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2610 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3187 | 135 | 121 | 3 | 99.19c | $-201.63 | $-1.62 | needs ~716 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3816 | 905 | 879 | 14 | 98.92c | $-502.17 | $-0.57 | needs ~1084 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2595 | 356 | 337 | 3 | 99.68c | $-199.56 | $-0.59 | needs ~1910 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3754 | 206 | 197 | 0 | 99.61c | $+71.50 | $+0.36 | needs ~442 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1501 | 1492 | 1475 | 104 | 92.93c | $-479.87 | $-0.35 | needs ~267 more bets with no loss |

