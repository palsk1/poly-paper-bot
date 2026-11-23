# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6328 coin-windows from 2026-11-10T10:30 to 2026-11-23T01:15 UTC (904 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **103 of 6328** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4470 | 351 | 341 | 2 | 99.60c | $-10.19 | $-0.30 | needs ~1500 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3655 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4470 | 169 | 164 | 3 | 99.10c | $-15.71 | $-0.96 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5397 | 1227 | 1214 | 18 | 98.88c | $-56.93 | $-0.47 | needs ~1218 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3630 | 485 | 470 | 3 | 99.68c | $-20.18 | $-0.43 | needs ~2720 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5323 | 264 | 261 | 1 | 99.17c | $+8.72 | $+0.34 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2123 | 2110 | 2098 | 140 | 92.96c | $-13.79 | $-0.07 | needs ~250 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4470 | 351 | 333 | 2 | 99.61c | $-77.74 | $-0.23 | needs ~1115 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3655 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4470 | 169 | 154 | 3 | 99.09c | $-160.85 | $-1.02 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5397 | 1227 | 1188 | 18 | 98.91c | $-571.69 | $-0.48 | needs ~1192 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3630 | 485 | 461 | 3 | 99.69c | $-167.55 | $-0.36 | needs ~1861 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5323 | 264 | 255 | 1 | 99.18c | $+103.39 | $+0.40 | needs ~231 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2123 | 2110 | 2084 | 140 | 93.10c | $-318.16 | $-0.16 | needs ~275 more bets with no loss |

