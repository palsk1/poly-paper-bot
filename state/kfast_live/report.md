# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7749 coin-windows from 2026-11-10T10:30 to 2026-11-26T15:30 UTC (1107 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **127 of 7749** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5477 | 395 | 384 | 2 | 99.63c | $-9.91 | $-0.26 | needs ~1634 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4497 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5477 | 196 | 190 | 3 | 99.15c | $-14.41 | $-0.76 | needs ~626 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6605 | 1459 | 1444 | 20 | 98.87c | $-52.99 | $-0.37 | needs ~1201 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4441 | 556 | 540 | 3 | 99.70c | $-19.65 | $-0.36 | needs ~2937 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6506 | 301 | 296 | 2 | 99.00c | $+6.17 | $+0.21 | needs ~300 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2553 | 2539 | 2525 | 177 | 92.74c | $-48.50 | $-0.21 | needs ~318 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5477 | 395 | 375 | 2 | 99.63c | $-71.63 | $-0.19 | needs ~1178 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4497 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5477 | 196 | 177 | 3 | 99.15c | $-148.70 | $-0.82 | needs ~610 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6605 | 1459 | 1409 | 20 | 98.90c | $-532.74 | $-0.38 | needs ~1168 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4441 | 556 | 531 | 3 | 99.71c | $-156.40 | $-0.29 | needs ~1933 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6506 | 301 | 289 | 2 | 99.01c | $+78.45 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2553 | 2539 | 2509 | 177 | 92.88c | $-709.65 | $-0.30 | needs ~348 more bets with no loss |

