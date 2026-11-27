# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7910 coin-windows from 2026-11-10T10:30 to 2026-11-27T00:30 UTC (1130 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **130 of 7910** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5582 | 404 | 393 | 2 | 99.62c | $-9.56 | $-0.24 | needs ~1603 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4583 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5582 | 202 | 195 | 3 | 99.15c | $-13.98 | $-0.71 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6731 | 1488 | 1473 | 21 | 98.87c | $-59.79 | $-0.41 | needs ~1279 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4519 | 566 | 550 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2954 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6632 | 309 | 303 | 2 | 99.01c | $+6.47 | $+0.22 | needs ~300 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2618 | 2603 | 2589 | 185 | 92.73c | $-82.21 | $-0.34 | needs ~372 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5582 | 404 | 384 | 2 | 99.63c | $-67.86 | $-0.18 | needs ~1160 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4583 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5582 | 202 | 181 | 3 | 99.15c | $-145.19 | $-0.78 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6731 | 1488 | 1436 | 21 | 98.90c | $-601.41 | $-0.42 | needs ~1245 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4519 | 566 | 541 | 3 | 99.71c | $-154.49 | $-0.28 | needs ~1936 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6632 | 309 | 295 | 2 | 99.02c | $+81.91 | $+0.28 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2618 | 2603 | 2573 | 185 | 92.86c | $-1049.42 | $-0.44 | needs ~403 more bets with no loss |

