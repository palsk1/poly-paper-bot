# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 385 coin-windows from 2026-11-10T10:30 to 2026-11-11T02:15 UTC (55 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 385** windows. Reading the Kalshi book takes about 186 ms (slowest 1 in 10: 258 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 271 | 19 | 19 | 0 | 99.80c | $+0.19 | $+0.10 | needs ~2283 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 234 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 271 | 12 | 12 | 0 | 99.46c | $+0.63 | $+0.53 | needs ~426 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 338 | 83 | 82 | 1 | 98.84c | $-1.34 | $-0.16 | needs ~287 more bets with no loss |
| Buy now, 60 s left (z 4+) | 235 | 30 | 30 | 0 | 99.44c | $+1.33 | $+0.45 | needs ~488 more bets with no loss |
| Buy now, 30 s left (z 4+) | 332 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 128 | 127 | 127 | 6 | 93.62c | $+16.09 | $+1.35 | needs ~47 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 271 | 19 | 19 | 0 | 99.81c | $+3.20 | $+0.17 | needs ~1348 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 234 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 271 | 12 | 12 | 0 | 99.48c | $+6.15 | $+0.52 | needs ~437 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 338 | 83 | 80 | 1 | 98.88c | $-14.86 | $-0.18 | needs ~287 more bets with no loss |
| Buy now, 60 s left (z 4+) | 235 | 30 | 29 | 0 | 99.43c | $+15.51 | $+0.53 | needs ~404 more bets with no loss |
| Buy now, 30 s left (z 4+) | 332 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 128 | 127 | 126 | 6 | 93.81c | $+144.08 | $+1.21 | needs ~51 more bets with no loss |

