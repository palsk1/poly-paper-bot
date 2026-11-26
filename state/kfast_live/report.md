# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7497 coin-windows from 2026-11-10T10:30 to 2026-11-26T00:00 UTC (1071 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **122 of 7497** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5301 | 389 | 378 | 2 | 99.62c | $-9.92 | $-0.26 | needs ~1610 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4345 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5301 | 187 | 181 | 3 | 99.13c | $-14.86 | $-0.82 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6399 | 1419 | 1404 | 20 | 98.87c | $-57.25 | $-0.41 | needs ~1245 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4305 | 544 | 528 | 3 | 99.70c | $-19.70 | $-0.37 | needs ~2888 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6300 | 294 | 289 | 2 | 98.98c | $+6.10 | $+0.21 | needs ~295 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2474 | 2460 | 2447 | 171 | 92.82c | $-59.19 | $-0.26 | needs ~334 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5301 | 389 | 369 | 2 | 99.63c | $-72.26 | $-0.19 | needs ~1167 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4345 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5301 | 187 | 168 | 3 | 99.13c | $-153.20 | $-0.89 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6399 | 1419 | 1369 | 20 | 98.90c | $-575.14 | $-0.42 | needs ~1210 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4305 | 544 | 519 | 3 | 99.70c | $-157.94 | $-0.30 | needs ~1916 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6300 | 294 | 283 | 2 | 99.00c | $+77.26 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2474 | 2460 | 2431 | 171 | 92.95c | $-807.05 | $-0.35 | needs ~363 more bets with no loss |

