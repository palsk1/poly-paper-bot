# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4865 coin-windows from 2026-11-10T10:30 to 2026-11-20T05:00 UTC (695 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **79 of 4865** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3474 | 291 | 282 | 2 | 99.66c | $-13.50 | $-0.48 | needs ~2020 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2835 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3474 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4158 | 970 | 962 | 14 | 98.90c | $-44.71 | $-0.47 | needs ~1065 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2819 | 380 | 367 | 3 | 99.68c | $-22.13 | $-0.60 | needs ~2744 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4092 | 219 | 216 | 0 | 99.61c | $+6.14 | $+0.29 | needs ~590 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1624 | 1615 | 1606 | 109 | 92.78c | $-0.92 | $-0.01 | needs ~202 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3474 | 291 | 276 | 2 | 99.67c | $-114.20 | $-0.41 | needs ~1435 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2835 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3474 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4158 | 970 | 941 | 14 | 98.94c | $-451.06 | $-0.48 | needs ~1046 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2819 | 380 | 359 | 3 | 99.68c | $-194.20 | $-0.54 | needs ~1911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4092 | 219 | 210 | 0 | 99.62c | $+74.52 | $+0.35 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1624 | 1615 | 1595 | 109 | 92.92c | $-162.14 | $-0.11 | needs ~222 more bets with no loss |

