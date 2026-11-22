# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5999 coin-windows from 2026-11-10T10:30 to 2026-11-22T10:15 UTC (857 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 5999** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4245 | 326 | 316 | 2 | 99.67c | $-12.98 | $-0.41 | needs ~2072 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3484 | 58 | 57 | 0 | 99.79c | $+0.62 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4245 | 160 | 155 | 3 | 99.24c | $-18.51 | $-1.19 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5118 | 1157 | 1145 | 16 | 98.87c | $-43.61 | $-0.38 | needs ~1055 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3461 | 447 | 433 | 3 | 99.68c | $-20.84 | $-0.48 | needs ~2720 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5052 | 253 | 250 | 0 | 99.56c | $+8.12 | $+0.33 | needs ~455 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2000 | 1989 | 1978 | 129 | 92.85c | $+38.53 | $+0.21 | needs ~160 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4245 | 326 | 309 | 2 | 99.68c | $-106.62 | $-0.34 | needs ~1452 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3484 | 58 | 54 | 0 | 99.80c | $+9.98 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4245 | 160 | 145 | 3 | 99.23c | $-188.27 | $-1.27 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5118 | 1157 | 1119 | 16 | 98.91c | $-439.88 | $-0.39 | needs ~1032 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3461 | 447 | 425 | 3 | 99.69c | $-176.97 | $-0.41 | needs ~1881 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5052 | 253 | 244 | 0 | 99.58c | $+96.69 | $+0.39 | needs ~338 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2000 | 1989 | 1965 | 129 | 92.98c | $+210.73 | $+0.11 | needs ~183 more bets with no loss |

