# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6503 coin-windows from 2026-11-10T10:30 to 2026-11-23T09:15 UTC (929 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **107 of 6503** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4582 | 372 | 361 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1568 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3740 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4582 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5543 | 1267 | 1253 | 18 | 98.86c | $-50.65 | $-0.41 | needs ~1134 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3716 | 510 | 495 | 3 | 99.69c | $-20.03 | $-0.40 | needs ~2814 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5466 | 276 | 273 | 1 | 99.20c | $+8.80 | $+0.32 | needs ~288 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2202 | 2189 | 2176 | 144 | 93.01c | $-11.93 | $-0.06 | needs ~251 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4582 | 372 | 353 | 2 | 99.62c | $-75.01 | $-0.21 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3740 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4582 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5543 | 1267 | 1225 | 18 | 98.89c | $-508.59 | $-0.41 | needs ~1107 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3716 | 510 | 486 | 3 | 99.70c | $-163.91 | $-0.34 | needs ~1896 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5466 | 276 | 267 | 1 | 99.21c | $+105.20 | $+0.39 | needs ~237 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2202 | 2189 | 2162 | 144 | 93.14c | $-300.75 | $-0.15 | needs ~276 more bets with no loss |

