# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6291 coin-windows from 2026-11-10T10:30 to 2026-11-23T00:00 UTC (899 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **103 of 6291** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4446 | 351 | 341 | 2 | 99.60c | $-10.19 | $-0.30 | needs ~1500 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3635 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4446 | 169 | 164 | 3 | 99.10c | $-15.71 | $-0.96 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5367 | 1221 | 1208 | 16 | 98.87c | $-37.27 | $-0.31 | needs ~992 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3610 | 482 | 467 | 3 | 99.68c | $-20.18 | $-0.43 | needs ~2703 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5294 | 262 | 259 | 1 | 99.16c | $+8.72 | $+0.34 | needs ~275 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2110 | 2097 | 2085 | 138 | 92.96c | $-2.23 | $-0.01 | needs ~231 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4446 | 351 | 333 | 2 | 99.61c | $-77.74 | $-0.23 | needs ~1115 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3635 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4446 | 169 | 154 | 3 | 99.09c | $-160.85 | $-1.02 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5367 | 1221 | 1182 | 16 | 98.91c | $-375.32 | $-0.32 | needs ~968 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3610 | 482 | 458 | 3 | 99.69c | $-167.82 | $-0.36 | needs ~1853 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5294 | 262 | 253 | 1 | 99.18c | $+103.21 | $+0.40 | needs ~230 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2110 | 2097 | 2071 | 138 | 93.10c | $-203.01 | $-0.10 | needs ~255 more bets with no loss |

