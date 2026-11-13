# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1631 coin-windows from 2026-11-10T10:30 to 2026-11-13T13:45 UTC (233 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **23 of 1631** windows. Reading the Kalshi book takes about 175 ms (slowest 1 in 10: 251 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1170 | 91 | 90 | 1 | 99.79c | $-9.00 | $-1.00 | needs ~3426 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 960 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1170 | 39 | 38 | 1 | 99.42c | $-7.86 | $-2.05 | needs ~662 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1411 | 310 | 309 | 4 | 98.88c | $-8.80 | $-0.29 | needs ~482 more bets with no loss |
| Buy now, 60 s left (z 4+) | 949 | 122 | 118 | 0 | 99.67c | $+2.60 | $+0.22 | needs ~923 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1393 | 71 | 71 | 0 | 99.46c | $+3.02 | $+0.43 | needs ~469 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 531 | 527 | 526 | 28 | 93.37c | $+47.01 | $+0.95 | needs ~50 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1170 | 91 | 88 | 1 | 99.79c | $-83.56 | $-0.95 | needs ~1996 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 960 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1170 | 39 | 34 | 1 | 99.42c | $-79.65 | $-2.22 | needs ~651 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1411 | 310 | 301 | 4 | 98.92c | $-91.94 | $-0.31 | needs ~478 more bets with no loss |
| Buy now, 60 s left (z 4+) | 949 | 122 | 115 | 0 | 99.68c | $+34.65 | $+0.30 | needs ~649 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1393 | 71 | 68 | 0 | 99.49c | $+33.34 | $+0.48 | needs ~412 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 531 | 527 | 523 | 28 | 93.51c | $+416.90 | $+0.85 | needs ~58 more bets with no loss |

