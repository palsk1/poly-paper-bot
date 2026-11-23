# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6363 coin-windows from 2026-11-10T10:30 to 2026-11-23T02:30 UTC (909 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **103 of 6363** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4491 | 355 | 345 | 2 | 99.60c | $-10.17 | $-0.29 | needs ~1514 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3671 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4491 | 169 | 164 | 3 | 99.10c | $-15.71 | $-0.96 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5425 | 1236 | 1223 | 18 | 98.88c | $-55.88 | $-0.46 | needs ~1206 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3645 | 489 | 474 | 3 | 99.68c | $-20.12 | $-0.42 | needs ~2724 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5351 | 266 | 263 | 1 | 99.17c | $+8.75 | $+0.34 | needs ~279 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2140 | 2127 | 2115 | 140 | 92.97c | $-3.38 | $-0.02 | needs ~235 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4491 | 355 | 337 | 2 | 99.61c | $-77.20 | $-0.23 | needs ~1122 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3671 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4491 | 169 | 154 | 3 | 99.09c | $-160.85 | $-1.02 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5425 | 1236 | 1197 | 18 | 98.91c | $-560.98 | $-0.47 | needs ~1180 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3645 | 489 | 465 | 3 | 99.69c | $-166.63 | $-0.36 | needs ~1861 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5351 | 266 | 257 | 1 | 99.19c | $+103.84 | $+0.40 | needs ~232 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2140 | 2127 | 2101 | 140 | 93.10c | $-213.84 | $-0.11 | needs ~259 more bets with no loss |

