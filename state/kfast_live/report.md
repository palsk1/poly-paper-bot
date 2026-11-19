# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4396 coin-windows from 2026-11-10T10:30 to 2026-11-19T03:15 UTC (628 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **74 of 4396** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3136 | 266 | 258 | 2 | 99.65c | $-13.80 | $-0.53 | needs ~1951 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2571 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3136 | 131 | 127 | 3 | 99.20c | $-20.11 | $-1.57 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3758 | 894 | 886 | 14 | 98.89c | $-50.64 | $-0.58 | needs ~1105 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2552 | 344 | 334 | 3 | 99.67c | $-22.75 | $-0.68 | needs ~2735 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3695 | 205 | 202 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~577 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1479 | 1470 | 1462 | 103 | 92.85c | $-48.17 | $-0.35 | needs ~270 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3136 | 266 | 254 | 2 | 99.66c | $-119.05 | $-0.47 | needs ~1414 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2571 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3136 | 131 | 117 | 3 | 99.19c | $-204.06 | $-1.69 | needs ~714 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3758 | 894 | 868 | 14 | 98.92c | $-511.47 | $-0.59 | needs ~1091 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2552 | 344 | 326 | 3 | 99.68c | $-203.13 | $-0.62 | needs ~1930 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3695 | 205 | 196 | 0 | 99.61c | $+71.41 | $+0.36 | needs ~440 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1479 | 1470 | 1453 | 103 | 92.99c | $-613.61 | $-0.45 | needs ~289 more bets with no loss |

