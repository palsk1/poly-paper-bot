# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8015 coin-windows from 2026-11-10T10:30 to 2026-11-27T04:15 UTC (1145 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 8015** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5653 | 408 | 397 | 2 | 99.63c | $-9.51 | $-0.24 | needs ~1609 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4635 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5653 | 208 | 200 | 3 | 99.16c | $-13.74 | $-0.68 | needs ~624 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6817 | 1513 | 1498 | 21 | 98.88c | $-58.24 | $-0.39 | needs ~1273 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4572 | 568 | 552 | 3 | 99.70c | $-19.53 | $-0.35 | needs ~2962 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6715 | 312 | 306 | 2 | 99.02c | $+6.49 | $+0.21 | needs ~302 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2654 | 2638 | 2624 | 188 | 92.70c | $-80.29 | $-0.33 | needs ~369 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5653 | 408 | 387 | 2 | 99.63c | $-67.21 | $-0.17 | needs ~1164 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4635 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5653 | 208 | 185 | 3 | 99.15c | $-142.85 | $-0.75 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6817 | 1513 | 1460 | 21 | 98.91c | $-586.27 | $-0.40 | needs ~1238 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4572 | 568 | 543 | 3 | 99.71c | $-154.22 | $-0.28 | needs ~1939 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6715 | 312 | 298 | 2 | 99.03c | $+82.37 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2654 | 2638 | 2607 | 188 | 92.84c | $-1043.94 | $-0.43 | needs ~402 more bets with no loss |

