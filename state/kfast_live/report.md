# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6279 coin-windows from 2026-11-10T10:30 to 2026-11-22T22:45 UTC (897 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **105 of 6279** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4435 | 352 | 342 | 2 | 99.60c | $-10.19 | $-0.30 | needs ~1505 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3625 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4435 | 169 | 164 | 3 | 99.10c | $-15.71 | $-0.96 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5358 | 1223 | 1210 | 18 | 98.86c | $-55.61 | $-0.46 | needs ~1188 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3600 | 480 | 465 | 3 | 99.68c | $-20.19 | $-0.43 | needs ~2695 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5283 | 263 | 260 | 1 | 99.17c | $+8.73 | $+0.34 | needs ~276 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2108 | 2095 | 2083 | 141 | 92.94c | $-28.06 | $-0.14 | needs ~271 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4435 | 352 | 334 | 2 | 99.61c | $-77.65 | $-0.23 | needs ~1117 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3625 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4435 | 169 | 154 | 3 | 99.09c | $-160.85 | $-1.02 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5358 | 1223 | 1184 | 18 | 98.89c | $-560.14 | $-0.47 | needs ~1165 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3600 | 480 | 456 | 3 | 99.69c | $-168.09 | $-0.37 | needs ~1850 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5283 | 263 | 254 | 1 | 99.18c | $+103.39 | $+0.40 | needs ~230 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2108 | 2095 | 2069 | 141 | 93.07c | $-461.29 | $-0.24 | needs ~296 more bets with no loss |

