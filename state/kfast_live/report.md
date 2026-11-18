# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3962 coin-windows from 2026-11-10T10:30 to 2026-11-18T05:45 UTC (566 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3962** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2851 | 238 | 231 | 2 | 99.64c | $-14.17 | $-0.61 | needs ~1873 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2352 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2851 | 120 | 116 | 3 | 99.18c | $-20.76 | $-1.78 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3409 | 817 | 810 | 13 | 98.89c | $-48.88 | $-0.61 | needs ~1079 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2350 | 317 | 308 | 3 | 99.66c | $-22.91 | $-0.74 | needs ~2586 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3356 | 185 | 182 | 0 | 99.62c | $+4.98 | $+0.27 | needs ~657 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1308 | 1299 | 1292 | 91 | 92.85c | $-41.72 | $-0.35 | needs ~250 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2851 | 238 | 227 | 2 | 99.64c | $-124.83 | $-0.55 | needs ~1379 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2352 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2851 | 120 | 109 | 3 | 99.17c | $-209.78 | $-1.88 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3409 | 817 | 794 | 13 | 98.93c | $-494.92 | $-0.62 | needs ~1069 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2350 | 317 | 300 | 3 | 99.67c | $-206.92 | $-0.68 | needs ~1863 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3356 | 185 | 177 | 0 | 99.63c | $+60.69 | $+0.34 | needs ~499 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1308 | 1299 | 1283 | 91 | 92.98c | $-531.96 | $-0.44 | needs ~266 more bets with no loss |

