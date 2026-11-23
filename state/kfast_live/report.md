# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6678 coin-windows from 2026-11-10T10:30 to 2026-11-23T18:00 UTC (954 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **110 of 6678** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4713 | 373 | 362 | 2 | 99.62c | $-10.07 | $-0.28 | needs ~1571 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3851 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4713 | 172 | 167 | 3 | 99.10c | $-15.56 | $-0.93 | needs ~608 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5694 | 1289 | 1275 | 18 | 98.86c | $-48.14 | $-0.38 | needs ~1108 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3823 | 514 | 498 | 3 | 99.69c | $-20.00 | $-0.40 | needs ~2821 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5615 | 282 | 277 | 1 | 99.21c | $+8.83 | $+0.32 | needs ~289 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2244 | 2231 | 2218 | 150 | 92.94c | $-30.24 | $-0.15 | needs ~281 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4713 | 373 | 354 | 2 | 99.62c | $-74.83 | $-0.21 | needs ~1148 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3851 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4713 | 172 | 157 | 3 | 99.10c | $-159.35 | $-1.00 | needs ~594 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5694 | 1289 | 1247 | 18 | 98.89c | $-483.59 | $-0.39 | needs ~1081 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3823 | 514 | 489 | 3 | 99.70c | $-163.28 | $-0.33 | needs ~1895 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5615 | 282 | 271 | 1 | 99.22c | $+106.00 | $+0.39 | needs ~237 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2244 | 2231 | 2203 | 150 | 93.07c | $-491.03 | $-0.24 | needs ~306 more bets with no loss |

