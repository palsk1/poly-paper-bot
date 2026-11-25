# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7217 coin-windows from 2026-11-10T10:30 to 2026-11-25T06:15 UTC (1031 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7217** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5101 | 387 | 376 | 2 | 99.62c | $-9.93 | $-0.26 | needs ~1604 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4171 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5101 | 185 | 179 | 3 | 99.13c | $-14.96 | $-0.83 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6158 | 1382 | 1368 | 20 | 98.86c | $-59.47 | $-0.44 | needs ~1254 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4140 | 538 | 522 | 3 | 99.70c | $-19.74 | $-0.38 | needs ~2868 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6064 | 289 | 284 | 2 | 98.97c | $+5.88 | $+0.21 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2397 | 2384 | 2371 | 169 | 92.83c | $-92.79 | $-0.42 | needs ~383 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5101 | 387 | 367 | 2 | 99.63c | $-72.47 | $-0.20 | needs ~1163 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4171 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5101 | 185 | 167 | 3 | 99.12c | $-154.00 | $-0.90 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6158 | 1382 | 1336 | 20 | 98.89c | $-597.41 | $-0.45 | needs ~1223 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4140 | 538 | 513 | 3 | 99.70c | $-158.85 | $-0.31 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6064 | 289 | 278 | 2 | 98.99c | $+75.16 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2397 | 2384 | 2355 | 169 | 92.96c | $-1135.18 | $-0.51 | needs ~411 more bets with no loss |

