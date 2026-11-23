# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6657 coin-windows from 2026-11-10T10:30 to 2026-11-23T17:15 UTC (951 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **110 of 6657** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4695 | 373 | 362 | 2 | 99.62c | $-10.07 | $-0.28 | needs ~1571 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3835 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4695 | 171 | 166 | 3 | 99.10c | $-15.61 | $-0.94 | needs ~607 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5673 | 1285 | 1271 | 18 | 98.85c | $-48.48 | $-0.38 | needs ~1111 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3807 | 513 | 498 | 3 | 99.69c | $-19.99 | $-0.40 | needs ~2818 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5594 | 281 | 277 | 1 | 99.21c | $+8.84 | $+0.32 | needs ~290 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2241 | 2228 | 2215 | 150 | 92.94c | $-30.56 | $-0.15 | needs ~281 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4695 | 373 | 354 | 2 | 99.62c | $-74.83 | $-0.21 | needs ~1148 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3835 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4695 | 171 | 156 | 3 | 99.10c | $-159.85 | $-1.00 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5673 | 1285 | 1243 | 18 | 98.89c | $-486.91 | $-0.39 | needs ~1084 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3807 | 513 | 489 | 3 | 99.70c | $-163.27 | $-0.33 | needs ~1896 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5594 | 281 | 271 | 1 | 99.22c | $+106.01 | $+0.39 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2241 | 2228 | 2200 | 150 | 93.07c | $-494.16 | $-0.24 | needs ~306 more bets with no loss |

