# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7875 coin-windows from 2026-11-10T10:30 to 2026-11-26T20:00 UTC (1125 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **129 of 7875** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5565 | 399 | 388 | 2 | 99.62c | $-9.67 | $-0.25 | needs ~1603 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4573 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5565 | 198 | 192 | 3 | 99.15c | $-14.16 | $-0.73 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6709 | 1477 | 1462 | 21 | 98.87c | $-60.19 | $-0.41 | needs ~1277 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4512 | 564 | 548 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2943 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6608 | 307 | 301 | 2 | 99.01c | $+6.39 | $+0.21 | needs ~299 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2595 | 2580 | 2566 | 181 | 92.73c | $-56.48 | $-0.24 | needs ~331 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5565 | 399 | 379 | 2 | 99.63c | $-69.09 | $-0.18 | needs ~1160 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4573 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5565 | 198 | 179 | 3 | 99.14c | $-146.29 | $-0.80 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6709 | 1477 | 1427 | 21 | 98.90c | $-605.44 | $-0.42 | needs ~1245 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4512 | 564 | 539 | 3 | 99.71c | $-154.67 | $-0.29 | needs ~1932 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6608 | 307 | 293 | 2 | 99.02c | $+81.11 | $+0.27 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2595 | 2580 | 2550 | 181 | 92.86c | $-791.54 | $-0.33 | needs ~361 more bets with no loss |

