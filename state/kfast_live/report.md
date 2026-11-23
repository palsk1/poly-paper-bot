# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6622 coin-windows from 2026-11-10T10:30 to 2026-11-23T16:00 UTC (946 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **108 of 6622** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4672 | 372 | 361 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1568 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3818 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4672 | 171 | 166 | 3 | 99.10c | $-15.61 | $-0.94 | needs ~607 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5647 | 1281 | 1267 | 18 | 98.85c | $-48.71 | $-0.39 | needs ~1111 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3789 | 512 | 497 | 3 | 99.69c | $-19.99 | $-0.40 | needs ~2812 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5568 | 281 | 277 | 1 | 99.21c | $+8.84 | $+0.32 | needs ~290 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2228 | 2215 | 2202 | 148 | 92.97c | $-26.15 | $-0.13 | needs ~274 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4672 | 372 | 353 | 2 | 99.62c | $-75.01 | $-0.21 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3818 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4672 | 171 | 156 | 3 | 99.10c | $-159.85 | $-1.00 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5647 | 1281 | 1239 | 18 | 98.88c | $-489.26 | $-0.39 | needs ~1085 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3789 | 512 | 488 | 3 | 99.70c | $-163.36 | $-0.33 | needs ~1894 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5568 | 281 | 271 | 1 | 99.22c | $+106.01 | $+0.39 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2228 | 2215 | 2188 | 148 | 93.10c | $-449.60 | $-0.22 | needs ~300 more bets with no loss |

