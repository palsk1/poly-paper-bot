# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6034 coin-windows from 2026-11-10T10:30 to 2026-11-22T11:30 UTC (862 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 6034** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4261 | 330 | 320 | 2 | 99.67c | $-12.82 | $-0.40 | needs ~2044 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3491 | 58 | 57 | 0 | 99.79c | $+0.62 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4261 | 162 | 157 | 3 | 99.23c | $-18.36 | $-1.16 | needs ~749 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5146 | 1170 | 1158 | 16 | 98.88c | $-42.88 | $-0.37 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3467 | 448 | 434 | 3 | 99.68c | $-20.84 | $-0.48 | needs ~2727 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5077 | 253 | 250 | 0 | 99.56c | $+8.12 | $+0.33 | needs ~455 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2022 | 2011 | 2000 | 131 | 92.89c | $+25.87 | $+0.14 | needs ~182 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4261 | 330 | 313 | 2 | 99.67c | $-104.78 | $-0.33 | needs ~1436 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3491 | 58 | 54 | 0 | 99.80c | $+9.98 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4261 | 162 | 147 | 3 | 99.23c | $-186.70 | $-1.24 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5146 | 1170 | 1132 | 16 | 98.91c | $-432.14 | $-0.38 | needs ~1030 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3467 | 448 | 426 | 3 | 99.69c | $-176.88 | $-0.41 | needs ~1884 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5077 | 253 | 244 | 0 | 99.58c | $+96.69 | $+0.39 | needs ~338 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2022 | 2011 | 1987 | 131 | 93.02c | $+82.99 | $+0.04 | needs ~205 more bets with no loss |

