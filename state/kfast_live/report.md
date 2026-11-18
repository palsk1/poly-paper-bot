# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3983 coin-windows from 2026-11-10T10:30 to 2026-11-18T06:30 UTC (569 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **64 of 3983** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2863 | 240 | 233 | 2 | 99.64c | $-14.17 | $-0.61 | needs ~1889 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2361 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2863 | 120 | 116 | 3 | 99.18c | $-20.76 | $-1.78 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3424 | 820 | 813 | 14 | 98.89c | $-58.41 | $-0.72 | needs ~1189 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2357 | 318 | 309 | 3 | 99.66c | $-22.88 | $-0.74 | needs ~2583 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3371 | 186 | 183 | 0 | 99.62c | $+5.02 | $+0.27 | needs ~654 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1318 | 1309 | 1302 | 92 | 92.87c | $-47.14 | $-0.39 | needs ~260 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2863 | 240 | 229 | 2 | 99.65c | $-124.65 | $-0.54 | needs ~1388 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2361 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2863 | 120 | 109 | 3 | 99.17c | $-209.78 | $-1.88 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3424 | 820 | 797 | 14 | 98.93c | $-590.14 | $-0.74 | needs ~1178 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2357 | 318 | 301 | 3 | 99.67c | $-206.55 | $-0.68 | needs ~1861 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3371 | 186 | 178 | 0 | 99.63c | $+61.15 | $+0.34 | needs ~496 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1318 | 1309 | 1293 | 92 | 93.00c | $-586.23 | $-0.48 | needs ~276 more bets with no loss |

