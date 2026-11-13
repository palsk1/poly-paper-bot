# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1820 coin-windows from 2026-11-10T10:30 to 2026-11-13T22:30 UTC (260 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **25 of 1820** windows. Reading the Kalshi book takes about 168 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1309 | 101 | 100 | 1 | 99.79c | $-8.90 | $-0.89 | needs ~3450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1081 | 20 | 20 | 0 | 99.88c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1309 | 42 | 41 | 1 | 99.43c | $-7.72 | $-1.87 | needs ~667 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1575 | 342 | 341 | 4 | 98.90c | $-6.39 | $-0.19 | needs ~469 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1075 | 131 | 126 | 0 | 99.67c | $+2.81 | $+0.22 | needs ~903 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1557 | 80 | 80 | 0 | 99.50c | $+3.10 | $+0.39 | needs ~515 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 588 | 584 | 583 | 32 | 93.41c | $+40.42 | $+0.74 | needs ~68 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1309 | 101 | 98 | 1 | 99.80c | $-81.76 | $-0.83 | needs ~1994 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1081 | 20 | 18 | 0 | 99.88c | $+1.97 | $+0.11 | needs ~2113 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1309 | 42 | 37 | 1 | 99.43c | $-78.19 | $-2.01 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1575 | 342 | 333 | 4 | 98.95c | $-68.46 | $-0.21 | needs ~467 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1075 | 131 | 123 | 0 | 99.67c | $+37.31 | $+0.30 | needs ~635 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1557 | 80 | 77 | 0 | 99.52c | $+34.73 | $+0.44 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 588 | 584 | 578 | 32 | 93.54c | $+349.06 | $+0.64 | needs ~75 more bets with no loss |

