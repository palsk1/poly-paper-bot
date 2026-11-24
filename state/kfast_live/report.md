# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6748 coin-windows from 2026-11-10T10:30 to 2026-11-24T02:30 UTC (964 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **111 of 6748** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4763 | 377 | 366 | 2 | 99.62c | $-10.05 | $-0.27 | needs ~1584 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3892 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4763 | 173 | 167 | 3 | 99.11c | $-15.55 | $-0.93 | needs ~608 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5753 | 1299 | 1285 | 18 | 98.86c | $-47.54 | $-0.37 | needs ~1106 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3864 | 519 | 503 | 3 | 99.69c | $-19.99 | $-0.40 | needs ~2846 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5672 | 282 | 277 | 1 | 99.21c | $+8.83 | $+0.32 | needs ~289 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2267 | 2254 | 2241 | 152 | 92.92c | $-30.40 | $-0.15 | needs ~282 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4763 | 377 | 358 | 2 | 99.62c | $-74.29 | $-0.21 | needs ~1154 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3892 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4763 | 173 | 157 | 3 | 99.10c | $-159.33 | $-0.99 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5753 | 1299 | 1256 | 18 | 98.89c | $-477.93 | $-0.38 | needs ~1078 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3864 | 519 | 494 | 3 | 99.70c | $-162.74 | $-0.33 | needs ~1905 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5672 | 282 | 271 | 1 | 99.22c | $+106.00 | $+0.39 | needs ~237 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2267 | 2254 | 2226 | 152 | 93.05c | $-495.85 | $-0.24 | needs ~308 more bets with no loss |

