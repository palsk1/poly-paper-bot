# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7784 coin-windows from 2026-11-10T10:30 to 2026-11-26T16:45 UTC (1112 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **127 of 7784** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5510 | 396 | 385 | 2 | 99.63c | $-9.90 | $-0.26 | needs ~1636 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4528 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5510 | 197 | 191 | 3 | 99.15c | $-14.36 | $-0.75 | needs ~627 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6638 | 1461 | 1446 | 20 | 98.87c | $-52.96 | $-0.37 | needs ~1202 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4471 | 558 | 542 | 3 | 99.70c | $-19.61 | $-0.36 | needs ~2934 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6539 | 302 | 297 | 2 | 99.00c | $+6.20 | $+0.21 | needs ~301 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2556 | 2542 | 2528 | 179 | 92.74c | $-66.18 | $-0.28 | needs ~345 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5510 | 396 | 376 | 2 | 99.63c | $-71.45 | $-0.19 | needs ~1179 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4528 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5510 | 197 | 178 | 3 | 99.15c | $-148.20 | $-0.81 | needs ~611 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6638 | 1461 | 1411 | 20 | 98.90c | $-532.36 | $-0.38 | needs ~1169 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4471 | 558 | 533 | 3 | 99.71c | $-155.85 | $-0.29 | needs ~1931 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6539 | 302 | 290 | 2 | 99.02c | $+78.82 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2556 | 2542 | 2512 | 179 | 92.88c | $-886.48 | $-0.38 | needs ~375 more bets with no loss |

