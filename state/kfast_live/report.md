# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7714 coin-windows from 2026-11-10T10:30 to 2026-11-26T07:45 UTC (1102 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **127 of 7714** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5451 | 395 | 384 | 2 | 99.63c | $-9.91 | $-0.26 | needs ~1634 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4475 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5451 | 195 | 189 | 3 | 99.15c | $-14.46 | $-0.76 | needs ~625 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6576 | 1457 | 1442 | 20 | 98.87c | $-53.03 | $-0.37 | needs ~1200 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4422 | 556 | 540 | 3 | 99.70c | $-19.65 | $-0.36 | needs ~2937 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6477 | 301 | 296 | 2 | 99.00c | $+6.17 | $+0.21 | needs ~300 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2546 | 2532 | 2518 | 177 | 92.78c | $-61.41 | $-0.26 | needs ~338 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5451 | 395 | 375 | 2 | 99.63c | $-71.63 | $-0.19 | needs ~1178 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4475 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5451 | 195 | 176 | 3 | 99.14c | $-149.20 | $-0.83 | needs ~609 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6576 | 1457 | 1407 | 20 | 98.90c | $-533.14 | $-0.38 | needs ~1167 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4422 | 556 | 531 | 3 | 99.71c | $-156.40 | $-0.29 | needs ~1933 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6477 | 301 | 289 | 2 | 99.01c | $+78.45 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2546 | 2532 | 2502 | 177 | 92.91c | $-837.75 | $-0.36 | needs ~368 more bets with no loss |

