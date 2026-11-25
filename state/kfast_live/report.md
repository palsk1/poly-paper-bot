# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7301 coin-windows from 2026-11-10T10:30 to 2026-11-25T09:15 UTC (1043 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7301** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5160 | 389 | 378 | 2 | 99.62c | $-9.92 | $-0.26 | needs ~1610 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4223 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5160 | 186 | 180 | 3 | 99.13c | $-14.91 | $-0.82 | needs ~619 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6233 | 1398 | 1384 | 20 | 98.87c | $-58.59 | $-0.43 | needs ~1252 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4191 | 538 | 522 | 3 | 99.70c | $-19.74 | $-0.38 | needs ~2868 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6136 | 292 | 287 | 2 | 98.98c | $+5.89 | $+0.21 | needs ~297 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2422 | 2409 | 2396 | 170 | 92.85c | $-90.79 | $-0.41 | needs ~382 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5160 | 389 | 369 | 2 | 99.63c | $-72.26 | $-0.19 | needs ~1167 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4223 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5160 | 186 | 167 | 3 | 99.13c | $-153.70 | $-0.90 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6233 | 1398 | 1350 | 20 | 98.90c | $-588.66 | $-0.44 | needs ~1219 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4191 | 538 | 513 | 3 | 99.70c | $-158.85 | $-0.31 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6136 | 292 | 281 | 2 | 99.00c | $+75.52 | $+0.27 | needs ~258 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2422 | 2409 | 2380 | 170 | 92.98c | $-1114.93 | $-0.50 | needs ~410 more bets with no loss |

