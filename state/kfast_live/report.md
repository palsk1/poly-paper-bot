# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 329 coin-windows from 2026-11-10T10:30 to 2026-11-11T01:00 UTC (47 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 329** windows. Reading the Kalshi book takes about 192 ms (slowest 1 in 10: 259 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 227 | 19 | 19 | 0 | 99.80c | $+0.19 | $+0.10 | needs ~2283 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 193 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 227 | 9 | 9 | 0 | 99.44c | $+0.48 | $+0.54 | needs ~422 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 286 | 71 | 70 | 1 | 98.79c | $-2.30 | $-0.33 | needs ~285 more bets with no loss |
| Buy now, 60 s left (z 4+) | 193 | 26 | 26 | 0 | 99.37c | $+1.31 | $+0.51 | needs ~430 more bets with no loss |
| Buy now, 30 s left (z 4+) | 281 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 115 | 115 | 115 | 6 | 93.72c | $+7.75 | $+0.72 | needs ~62 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 227 | 19 | 19 | 0 | 99.81c | $+3.20 | $+0.17 | needs ~1348 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 193 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 227 | 9 | 9 | 0 | 99.47c | $+4.65 | $+0.52 | needs ~436 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 286 | 71 | 69 | 1 | 98.85c | $-24.67 | $-0.36 | needs ~287 more bets with no loss |
| Buy now, 60 s left (z 4+) | 193 | 26 | 25 | 0 | 99.36c | $+14.97 | $+0.60 | needs ~362 more bets with no loss |
| Buy now, 30 s left (z 4+) | 281 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 115 | 115 | 114 | 6 | 93.91c | $+63.03 | $+0.58 | needs ~66 more bets with no loss |

