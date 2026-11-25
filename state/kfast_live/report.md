# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7091 coin-windows from 2026-11-10T10:30 to 2026-11-25T00:15 UTC (1013 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **118 of 7091** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5020 | 384 | 373 | 2 | 99.62c | $-9.95 | $-0.27 | needs ~1595 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4104 | 73 | 72 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1991 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5020 | 180 | 174 | 3 | 99.12c | $-15.21 | $-0.87 | needs ~614 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6055 | 1351 | 1337 | 20 | 98.85c | $-61.63 | $-0.46 | needs ~1266 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4075 | 533 | 517 | 3 | 99.70c | $-19.84 | $-0.38 | needs ~2874 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5966 | 289 | 284 | 2 | 98.97c | $+5.88 | $+0.21 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2350 | 2337 | 2324 | 164 | 92.90c | $-91.20 | $-0.42 | needs ~381 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5020 | 384 | 364 | 2 | 99.63c | $-72.92 | $-0.20 | needs ~1159 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4104 | 73 | 69 | 0 | 99.80c | $+12.99 | $+0.19 | needs ~1168 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5020 | 180 | 162 | 3 | 99.11c | $-156.50 | $-0.94 | needs ~597 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6055 | 1351 | 1305 | 20 | 98.89c | $-619.08 | $-0.47 | needs ~1235 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4075 | 533 | 508 | 3 | 99.70c | $-160.17 | $-0.31 | needs ~1913 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5966 | 289 | 278 | 2 | 98.99c | $+75.16 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2350 | 2337 | 2308 | 164 | 93.03c | $-1112.16 | $-0.51 | needs ~409 more bets with no loss |

