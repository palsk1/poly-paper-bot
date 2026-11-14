# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2149 coin-windows from 2026-11-10T10:30 to 2026-11-14T12:45 UTC (307 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **35 of 2149** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1561 | 126 | 124 | 1 | 99.77c | $-8.45 | $-0.68 | needs ~2994 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1305 | 28 | 28 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4001 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1561 | 59 | 58 | 1 | 99.43c | $-6.78 | $-1.16 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1861 | 413 | 411 | 7 | 98.91c | $-29.60 | $-0.73 | needs ~786 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1294 | 166 | 160 | 0 | 99.60c | $+4.55 | $+0.28 | needs ~644 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1844 | 102 | 101 | 0 | 99.52c | $+3.76 | $+0.37 | needs ~516 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 690 | 685 | 683 | 42 | 93.43c | $+0.85 | $+0.01 | needs ~148 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1561 | 126 | 122 | 1 | 99.78c | $-75.67 | $-0.62 | needs ~1828 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1305 | 28 | 26 | 0 | 99.85c | $+3.63 | $+0.14 | needs ~1637 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1561 | 59 | 54 | 1 | 99.43c | $-68.87 | $-1.23 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1861 | 413 | 401 | 7 | 98.95c | $-300.69 | $-0.75 | needs ~782 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1294 | 166 | 155 | 0 | 99.61c | $+57.08 | $+0.36 | needs ~469 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1844 | 102 | 97 | 0 | 99.54c | $+42.63 | $+0.43 | needs ~437 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 690 | 685 | 678 | 42 | 93.55c | $-51.60 | $-0.08 | needs ~157 more bets with no loss |

