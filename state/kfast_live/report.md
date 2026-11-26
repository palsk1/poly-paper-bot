# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7532 coin-windows from 2026-11-10T10:30 to 2026-11-26T01:15 UTC (1076 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **123 of 7532** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5324 | 390 | 379 | 2 | 99.62c | $-9.92 | $-0.26 | needs ~1614 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4367 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5324 | 189 | 183 | 3 | 99.14c | $-14.76 | $-0.80 | needs ~621 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6423 | 1422 | 1407 | 20 | 98.87c | $-57.05 | $-0.41 | needs ~1244 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4327 | 544 | 528 | 3 | 99.70c | $-19.70 | $-0.37 | needs ~2888 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6327 | 296 | 291 | 2 | 98.98c | $+6.16 | $+0.21 | needs ~295 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2487 | 2473 | 2460 | 172 | 92.77c | $-48.11 | $-0.21 | needs ~316 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5324 | 390 | 370 | 2 | 99.63c | $-72.17 | $-0.19 | needs ~1169 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4367 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5324 | 189 | 170 | 3 | 99.13c | $-152.20 | $-0.87 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6423 | 1422 | 1372 | 20 | 98.90c | $-573.07 | $-0.42 | needs ~1209 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4327 | 544 | 519 | 3 | 99.70c | $-157.94 | $-0.30 | needs ~1916 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6327 | 296 | 285 | 2 | 99.00c | $+77.99 | $+0.27 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2487 | 2473 | 2444 | 172 | 92.90c | $-700.44 | $-0.31 | needs ~345 more bets with no loss |

