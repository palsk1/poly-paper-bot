# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5215 coin-windows from 2026-11-10T10:30 to 2026-11-20T21:45 UTC (745 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **85 of 5215** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3723 | 294 | 284 | 2 | 99.66c | $-13.50 | $-0.48 | needs ~2034 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3052 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3723 | 145 | 141 | 3 | 99.22c | $-19.37 | $-1.37 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4467 | 1022 | 1014 | 16 | 98.90c | $-59.07 | $-0.59 | needs ~1237 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3032 | 394 | 381 | 3 | 99.68c | $-21.89 | $-0.57 | needs ~2754 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4400 | 227 | 224 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~596 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1719 | 1710 | 1700 | 116 | 92.69c | $+7.88 | $+0.05 | needs ~191 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3723 | 294 | 277 | 2 | 99.67c | $-113.97 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3052 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3723 | 145 | 131 | 3 | 99.21c | $-196.63 | $-1.46 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4467 | 1022 | 992 | 16 | 98.93c | $-594.80 | $-0.60 | needs ~1216 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3032 | 394 | 373 | 3 | 99.68c | $-191.07 | $-0.51 | needs ~1917 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4400 | 227 | 218 | 0 | 99.63c | $+76.18 | $+0.34 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1719 | 1710 | 1687 | 116 | 92.82c | $-77.87 | $-0.05 | needs ~211 more bets with no loss |

