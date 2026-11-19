# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4431 coin-windows from 2026-11-10T10:30 to 2026-11-19T04:30 UTC (633 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **74 of 4431** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3163 | 268 | 260 | 2 | 99.65c | $-13.71 | $-0.53 | needs ~1934 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2594 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3163 | 132 | 128 | 3 | 99.19c | $-20.02 | $-1.55 | needs ~735 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3787 | 896 | 888 | 14 | 98.89c | $-50.54 | $-0.57 | needs ~1105 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2578 | 349 | 339 | 3 | 99.67c | $-22.55 | $-0.67 | needs ~2692 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3727 | 205 | 202 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~577 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1489 | 1480 | 1472 | 103 | 92.83c | $-38.89 | $-0.28 | needs ~256 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3163 | 268 | 256 | 2 | 99.66c | $-118.03 | $-0.46 | needs ~1404 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2594 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3163 | 132 | 118 | 3 | 99.18c | $-203.13 | $-1.67 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3787 | 896 | 870 | 14 | 98.92c | $-510.36 | $-0.59 | needs ~1091 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2578 | 349 | 331 | 3 | 99.68c | $-200.73 | $-0.60 | needs ~1904 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3727 | 205 | 196 | 0 | 99.61c | $+71.41 | $+0.36 | needs ~440 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1489 | 1480 | 1463 | 103 | 92.97c | $-521.40 | $-0.38 | needs ~274 more bets with no loss |

