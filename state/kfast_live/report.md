# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7567 coin-windows from 2026-11-10T10:30 to 2026-11-26T02:30 UTC (1081 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **124 of 7567** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5345 | 391 | 380 | 2 | 99.62c | $-9.91 | $-0.26 | needs ~1617 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4384 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5345 | 190 | 184 | 3 | 99.14c | $-14.71 | $-0.80 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6451 | 1430 | 1415 | 20 | 98.87c | $-56.18 | $-0.40 | needs ~1235 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4342 | 548 | 532 | 3 | 99.70c | $-19.69 | $-0.37 | needs ~2907 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6354 | 298 | 293 | 2 | 98.99c | $+6.16 | $+0.21 | needs ~297 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2501 | 2487 | 2473 | 172 | 92.75c | $-35.70 | $-0.15 | needs ~296 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5345 | 391 | 371 | 2 | 99.63c | $-71.99 | $-0.19 | needs ~1170 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4384 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5345 | 190 | 171 | 3 | 99.13c | $-151.70 | $-0.87 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6451 | 1430 | 1380 | 20 | 98.90c | $-564.04 | $-0.41 | needs ~1200 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4342 | 548 | 523 | 3 | 99.70c | $-157.49 | $-0.30 | needs ~1923 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6354 | 298 | 286 | 2 | 99.01c | $+78.09 | $+0.27 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2501 | 2487 | 2457 | 172 | 92.88c | $-576.82 | $-0.25 | needs ~325 more bets with no loss |

