# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4984 coin-windows from 2026-11-10T10:30 to 2026-11-20T09:15 UTC (712 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **81 of 4984** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3550 | 293 | 284 | 2 | 99.66c | $-13.49 | $-0.48 | needs ~2031 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2898 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3550 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4256 | 991 | 983 | 14 | 98.90c | $-42.18 | $-0.43 | needs ~1035 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2879 | 388 | 375 | 3 | 99.68c | $-21.95 | $-0.58 | needs ~2734 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4192 | 225 | 222 | 0 | 99.61c | $+6.23 | $+0.28 | needs ~595 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1668 | 1659 | 1650 | 113 | 92.69c | $+3.09 | $+0.02 | needs ~197 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3550 | 293 | 277 | 2 | 99.67c | $-113.96 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2898 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3550 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4256 | 991 | 961 | 14 | 98.93c | $-426.45 | $-0.44 | needs ~1016 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2879 | 388 | 367 | 3 | 99.68c | $-192.13 | $-0.52 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4192 | 225 | 216 | 0 | 99.63c | $+75.79 | $+0.35 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1668 | 1659 | 1638 | 113 | 92.83c | $-123.94 | $-0.08 | needs ~216 more bets with no loss |

