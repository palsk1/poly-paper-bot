# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 455 coin-windows from 2026-11-10T10:30 to 2026-11-11T07:45 UTC (65 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 455** windows. Reading the Kalshi book takes about 193 ms (slowest 1 in 10: 253 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 334 | 20 | 20 | 0 | 99.81c | $+0.19 | $+0.10 | needs ~2403 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 286 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 334 | 14 | 14 | 0 | 99.46c | $+0.73 | $+0.52 | needs ~427 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 403 | 90 | 89 | 1 | 98.91c | $-1.19 | $-0.13 | needs ~305 more bets with no loss |
| Buy now, 60 s left (z 4+) | 289 | 43 | 43 | 0 | 99.54c | $+1.47 | $+0.34 | needs ~629 more bets with no loss |
| Buy now, 30 s left (z 4+) | 398 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 136 | 135 | 135 | 7 | 93.12c | $+17.37 | $+1.38 | needs ~45 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 334 | 20 | 20 | 0 | 99.82c | $+3.29 | $+0.16 | needs ~1379 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 286 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 334 | 14 | 14 | 0 | 99.48c | $+7.15 | $+0.51 | needs ~436 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 403 | 90 | 86 | 1 | 98.95c | $-13.31 | $-0.15 | needs ~304 more bets with no loss |
| Buy now, 60 s left (z 4+) | 289 | 43 | 42 | 0 | 99.54c | $+17.81 | $+0.42 | needs ~503 more bets with no loss |
| Buy now, 30 s left (z 4+) | 398 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 136 | 135 | 134 | 7 | 93.30c | $+156.80 | $+1.24 | needs ~48 more bets with no loss |

