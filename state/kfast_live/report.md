# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7371 coin-windows from 2026-11-10T10:30 to 2026-11-25T16:00 UTC (1053 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7371** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5219 | 389 | 378 | 2 | 99.62c | $-9.92 | $-0.26 | needs ~1610 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4275 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5219 | 187 | 181 | 3 | 99.13c | $-14.86 | $-0.82 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6299 | 1405 | 1390 | 20 | 98.87c | $-58.48 | $-0.42 | needs ~1255 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4241 | 540 | 524 | 3 | 99.70c | $-19.74 | $-0.38 | needs ~2879 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6202 | 292 | 287 | 2 | 98.98c | $+5.89 | $+0.21 | needs ~297 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2432 | 2419 | 2406 | 170 | 92.86c | $-86.66 | $-0.39 | needs ~376 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5219 | 389 | 369 | 2 | 99.63c | $-72.26 | $-0.19 | needs ~1167 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4275 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5219 | 187 | 168 | 3 | 99.13c | $-153.20 | $-0.89 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6299 | 1405 | 1355 | 20 | 98.90c | $-587.27 | $-0.43 | needs ~1220 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4241 | 540 | 515 | 3 | 99.70c | $-158.67 | $-0.31 | needs ~1914 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6202 | 292 | 281 | 2 | 99.00c | $+75.52 | $+0.27 | needs ~258 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2432 | 2419 | 2390 | 170 | 92.99c | $-1073.47 | $-0.48 | needs ~405 more bets with no loss |

