# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1960 coin-windows from 2026-11-10T10:30 to 2026-11-14T04:15 UTC (280 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **29 of 1960** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 248 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1417 | 107 | 106 | 1 | 99.79c | $-8.82 | $-0.83 | needs ~3401 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1179 | 22 | 22 | 0 | 99.84c | $+0.13 | $+0.06 | needs ~3874 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1417 | 47 | 46 | 1 | 99.43c | $-7.45 | $-1.61 | needs ~663 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1700 | 371 | 369 | 6 | 98.86c | $-21.80 | $-0.59 | needs ~648 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1174 | 148 | 142 | 0 | 99.62c | $+3.81 | $+0.27 | needs ~711 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1679 | 86 | 86 | 0 | 99.49c | $+3.40 | $+0.40 | needs ~497 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 624 | 619 | 618 | 38 | 93.33c | $+6.29 | $+0.11 | needs ~132 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1417 | 107 | 104 | 1 | 99.79c | $-80.55 | $-0.77 | needs ~1977 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1179 | 22 | 20 | 0 | 99.85c | $+2.82 | $+0.14 | needs ~1631 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1417 | 47 | 42 | 1 | 99.43c | $-75.52 | $-1.72 | needs ~654 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1700 | 371 | 361 | 6 | 98.90c | $-223.90 | $-0.62 | needs ~648 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1174 | 148 | 138 | 0 | 99.63c | $+48.35 | $+0.35 | needs ~519 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1679 | 86 | 83 | 0 | 99.52c | $+37.99 | $+0.45 | needs ~428 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 624 | 619 | 613 | 38 | 93.46c | $+4.99 | $+0.01 | needs ~140 more bets with no loss |

