# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8528 coin-windows from 2026-11-10T10:30 to 2026-11-28T03:15 UTC (1214 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **142 of 8528** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5998 | 441 | 427 | 2 | 99.63c | $-8.86 | $-0.21 | needs ~1602 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4905 | 82 | 80 | 0 | 99.79c | $+0.85 | $+0.11 | needs ~2077 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5998 | 229 | 220 | 3 | 99.18c | $-12.48 | $-0.56 | needs ~621 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7259 | 1632 | 1617 | 23 | 98.83c | $-58.29 | $-0.36 | needs ~1239 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4843 | 599 | 583 | 3 | 99.71c | $-19.09 | $-0.33 | needs ~2976 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7148 | 334 | 328 | 2 | 99.01c | $+8.67 | $+0.27 | needs ~274 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2842 | 2826 | 2808 | 200 | 92.72c | $-79.48 | $-0.30 | needs ~373 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5998 | 441 | 415 | 2 | 99.64c | $-58.80 | $-0.14 | needs ~1146 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4905 | 82 | 77 | 0 | 99.80c | $+14.25 | $+0.18 | needs ~1178 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5998 | 229 | 202 | 3 | 99.17c | $-131.36 | $-0.63 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7259 | 1632 | 1578 | 23 | 98.86c | $-588.42 | $-0.37 | needs ~1206 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4843 | 599 | 572 | 3 | 99.71c | $-147.53 | $-0.26 | needs ~1931 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7148 | 334 | 320 | 2 | 99.02c | $+104.57 | $+0.32 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2842 | 2826 | 2787 | 200 | 92.86c | $-1061.27 | $-0.41 | needs ~407 more bets with no loss |

