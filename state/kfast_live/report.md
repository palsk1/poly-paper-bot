# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4935 coin-windows from 2026-11-10T10:30 to 2026-11-20T07:30 UTC (705 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **81 of 4935** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3516 | 292 | 283 | 2 | 99.66c | $-13.49 | $-0.48 | needs ~2024 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2868 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3516 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4213 | 982 | 974 | 14 | 98.90c | $-43.53 | $-0.45 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2852 | 382 | 369 | 3 | 99.68c | $-22.09 | $-0.60 | needs ~2743 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4150 | 224 | 221 | 0 | 99.61c | $+6.23 | $+0.28 | needs ~592 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1652 | 1643 | 1634 | 112 | 92.68c | $+4.38 | $+0.03 | needs ~194 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3516 | 292 | 277 | 2 | 99.67c | $-114.02 | $-0.41 | needs ~1436 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2868 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3516 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4213 | 982 | 953 | 14 | 98.94c | $-439.37 | $-0.46 | needs ~1034 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2852 | 382 | 361 | 3 | 99.68c | $-193.65 | $-0.53 | needs ~1910 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4150 | 224 | 215 | 0 | 99.62c | $+75.70 | $+0.35 | needs ~442 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1652 | 1643 | 1623 | 112 | 92.81c | $-109.75 | $-0.07 | needs ~213 more bets with no loss |

