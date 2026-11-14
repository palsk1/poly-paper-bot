# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1925 coin-windows from 2026-11-10T10:30 to 2026-11-14T03:00 UTC (275 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **29 of 1925** windows. Reading the Kalshi book takes about 158 ms (slowest 1 in 10: 248 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1393 | 106 | 105 | 1 | 99.79c | $-8.82 | $-0.84 | needs ~3369 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1159 | 22 | 22 | 0 | 99.84c | $+0.13 | $+0.06 | needs ~3874 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1393 | 47 | 46 | 1 | 99.43c | $-7.45 | $-1.61 | needs ~663 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1668 | 363 | 361 | 6 | 98.84c | $-22.15 | $-0.62 | needs ~643 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1153 | 143 | 137 | 0 | 99.61c | $+3.75 | $+0.27 | needs ~699 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1650 | 86 | 86 | 0 | 99.49c | $+3.40 | $+0.40 | needs ~497 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 614 | 609 | 608 | 38 | 93.27c | $+3.75 | $+0.07 | needs ~135 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1393 | 106 | 103 | 1 | 99.79c | $-80.64 | $-0.78 | needs ~1968 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1159 | 22 | 20 | 0 | 99.85c | $+2.82 | $+0.14 | needs ~1631 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1393 | 47 | 42 | 1 | 99.43c | $-75.52 | $-1.72 | needs ~654 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1668 | 363 | 353 | 6 | 98.88c | $-227.30 | $-0.64 | needs ~642 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1153 | 143 | 133 | 0 | 99.62c | $+47.34 | $+0.35 | needs ~514 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1650 | 86 | 83 | 0 | 99.52c | $+37.99 | $+0.45 | needs ~428 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 614 | 609 | 603 | 38 | 93.40c | $-20.02 | $-0.04 | needs ~143 more bets with no loss |

