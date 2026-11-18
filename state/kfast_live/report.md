# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4200 coin-windows from 2026-11-10T10:30 to 2026-11-18T19:45 UTC (600 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4200** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3008 | 251 | 243 | 2 | 99.64c | $-13.97 | $-0.57 | needs ~1896 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2478 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3008 | 126 | 122 | 3 | 99.19c | $-20.44 | $-1.66 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3598 | 856 | 848 | 14 | 98.89c | $-54.39 | $-0.65 | needs ~1141 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2466 | 329 | 320 | 3 | 99.66c | $-22.78 | $-0.71 | needs ~2633 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3541 | 193 | 190 | 0 | 99.59c | $+5.74 | $+0.30 | needs ~569 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1399 | 1390 | 1382 | 97 | 92.82c | $-37.77 | $-0.29 | needs ~248 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3008 | 251 | 239 | 2 | 99.65c | $-122.00 | $-0.51 | needs ~1390 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2478 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3008 | 126 | 112 | 3 | 99.18c | $-207.39 | $-1.79 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3598 | 856 | 830 | 14 | 98.92c | $-549.95 | $-0.66 | needs ~1129 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2466 | 329 | 312 | 3 | 99.67c | $-204.74 | $-0.65 | needs ~1885 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3541 | 193 | 184 | 0 | 99.61c | $+68.48 | $+0.37 | needs ~439 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1399 | 1390 | 1373 | 97 | 92.96c | $-501.89 | $-0.39 | needs ~265 more bets with no loss |

