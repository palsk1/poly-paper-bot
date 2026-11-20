# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4900 coin-windows from 2026-11-10T10:30 to 2026-11-20T06:15 UTC (700 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **81 of 4900** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3494 | 292 | 283 | 2 | 99.66c | $-13.49 | $-0.48 | needs ~2024 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2848 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3494 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4185 | 976 | 968 | 14 | 98.91c | $-44.60 | $-0.46 | needs ~1069 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2833 | 380 | 367 | 3 | 99.68c | $-22.13 | $-0.60 | needs ~2744 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4120 | 220 | 217 | 0 | 99.61c | $+6.14 | $+0.28 | needs ~593 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1639 | 1630 | 1621 | 111 | 92.72c | $-1.30 | $-0.01 | needs ~202 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3494 | 292 | 277 | 2 | 99.67c | $-114.02 | $-0.41 | needs ~1436 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2848 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3494 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4185 | 976 | 947 | 14 | 98.94c | $-449.58 | $-0.47 | needs ~1049 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2833 | 380 | 359 | 3 | 99.68c | $-194.20 | $-0.54 | needs ~1911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4120 | 220 | 211 | 0 | 99.62c | $+74.61 | $+0.35 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1639 | 1630 | 1610 | 111 | 92.86c | $-165.61 | $-0.11 | needs ~222 more bets with no loss |

