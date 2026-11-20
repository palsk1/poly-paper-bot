# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5019 coin-windows from 2026-11-10T10:30 to 2026-11-20T12:45 UTC (717 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **82 of 5019** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3580 | 293 | 284 | 2 | 99.66c | $-13.49 | $-0.48 | needs ~2031 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2927 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3580 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4288 | 992 | 984 | 14 | 98.90c | $-42.11 | $-0.43 | needs ~1034 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2906 | 391 | 378 | 3 | 99.68c | $-21.91 | $-0.58 | needs ~2740 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4224 | 225 | 222 | 0 | 99.61c | $+6.23 | $+0.28 | needs ~595 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1672 | 1663 | 1654 | 113 | 92.68c | $+8.53 | $+0.06 | needs ~188 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3580 | 293 | 277 | 2 | 99.67c | $-113.96 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2927 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3580 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4288 | 992 | 962 | 14 | 98.93c | $-425.98 | $-0.44 | needs ~1016 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2906 | 391 | 370 | 3 | 99.68c | $-191.50 | $-0.51 | needs ~1911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4224 | 225 | 216 | 0 | 99.63c | $+75.79 | $+0.35 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1672 | 1663 | 1642 | 113 | 92.81c | $-70.70 | $-0.05 | needs ~208 more bets with no loss |

