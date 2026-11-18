# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4291 coin-windows from 2026-11-10T10:30 to 2026-11-18T23:00 UTC (613 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4291** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3064 | 257 | 249 | 2 | 99.64c | $-13.83 | $-0.56 | needs ~1893 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2516 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3064 | 130 | 126 | 3 | 99.19c | $-20.16 | $-1.59 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3671 | 876 | 868 | 14 | 98.88c | $-52.34 | $-0.61 | needs ~1121 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2500 | 335 | 326 | 3 | 99.67c | $-22.76 | $-0.70 | needs ~2674 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3613 | 202 | 199 | 0 | 99.59c | $+5.88 | $+0.30 | needs ~577 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1438 | 1429 | 1421 | 100 | 92.86c | $-46.22 | $-0.35 | needs ~265 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3064 | 257 | 245 | 2 | 99.65c | $-120.13 | $-0.49 | needs ~1385 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2516 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3064 | 130 | 116 | 3 | 99.18c | $-204.56 | $-1.71 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3671 | 876 | 850 | 14 | 98.92c | $-529.32 | $-0.62 | needs ~1108 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2500 | 335 | 318 | 3 | 99.68c | $-204.02 | $-0.64 | needs ~1904 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3613 | 202 | 193 | 0 | 99.61c | $+70.58 | $+0.36 | needs ~441 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1438 | 1429 | 1412 | 100 | 92.99c | $-591.09 | $-0.45 | needs ~283 more bets with no loss |

