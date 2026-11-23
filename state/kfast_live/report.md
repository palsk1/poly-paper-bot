# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6398 coin-windows from 2026-11-10T10:30 to 2026-11-23T03:45 UTC (914 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **105 of 6398** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4519 | 355 | 345 | 2 | 99.60c | $-10.17 | $-0.29 | needs ~1514 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3698 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4519 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5456 | 1243 | 1230 | 18 | 98.88c | $-55.29 | $-0.45 | needs ~1202 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3671 | 491 | 476 | 3 | 99.68c | $-20.12 | $-0.42 | needs ~2735 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5380 | 266 | 263 | 1 | 99.17c | $+8.75 | $+0.34 | needs ~279 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2147 | 2134 | 2122 | 141 | 92.91c | $+2.65 | $+0.01 | needs ~224 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4519 | 355 | 337 | 2 | 99.61c | $-77.20 | $-0.23 | needs ~1122 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3698 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4519 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5456 | 1243 | 1204 | 18 | 98.91c | $-554.94 | $-0.46 | needs ~1175 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3671 | 491 | 467 | 3 | 99.69c | $-166.45 | $-0.35 | needs ~1865 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5380 | 266 | 257 | 1 | 99.19c | $+103.84 | $+0.40 | needs ~232 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2147 | 2134 | 2108 | 141 | 93.04c | $-155.73 | $-0.08 | needs ~249 more bets with no loss |

