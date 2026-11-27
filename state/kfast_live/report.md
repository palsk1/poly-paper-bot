# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7980 coin-windows from 2026-11-10T10:30 to 2026-11-27T03:00 UTC (1140 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 7980** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5629 | 405 | 394 | 2 | 99.63c | $-9.56 | $-0.24 | needs ~1607 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4617 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5629 | 205 | 198 | 3 | 99.16c | $-13.83 | $-0.69 | needs ~624 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6788 | 1503 | 1488 | 21 | 98.87c | $-58.58 | $-0.40 | needs ~1270 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4553 | 566 | 550 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2954 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6688 | 312 | 306 | 2 | 99.02c | $+6.49 | $+0.21 | needs ~302 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2641 | 2625 | 2611 | 187 | 92.72c | $-84.72 | $-0.35 | needs ~376 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5629 | 405 | 385 | 2 | 99.63c | $-67.77 | $-0.17 | needs ~1162 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4617 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5629 | 205 | 184 | 3 | 99.15c | $-143.69 | $-0.76 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6788 | 1503 | 1451 | 21 | 98.90c | $-589.32 | $-0.41 | needs ~1236 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4553 | 566 | 541 | 3 | 99.71c | $-154.49 | $-0.28 | needs ~1936 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6688 | 312 | 298 | 2 | 99.03c | $+82.37 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2641 | 2625 | 2595 | 187 | 92.86c | $-1083.82 | $-0.45 | needs ~409 more bets with no loss |

