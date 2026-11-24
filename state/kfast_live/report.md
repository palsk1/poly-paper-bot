# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6713 coin-windows from 2026-11-10T10:30 to 2026-11-24T01:15 UTC (959 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **111 of 6713** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4736 | 377 | 366 | 2 | 99.62c | $-10.05 | $-0.27 | needs ~1584 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3867 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4736 | 173 | 167 | 3 | 99.11c | $-15.55 | $-0.93 | needs ~608 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5722 | 1297 | 1283 | 18 | 98.86c | $-47.73 | $-0.37 | needs ~1107 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3841 | 517 | 501 | 3 | 99.69c | $-19.99 | $-0.40 | needs ~2834 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5641 | 282 | 277 | 1 | 99.21c | $+8.83 | $+0.32 | needs ~289 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2260 | 2247 | 2234 | 151 | 92.95c | $-30.56 | $-0.15 | needs ~283 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4736 | 377 | 358 | 2 | 99.62c | $-74.29 | $-0.21 | needs ~1154 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3867 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4736 | 173 | 157 | 3 | 99.10c | $-159.33 | $-0.99 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5722 | 1297 | 1254 | 18 | 98.89c | $-479.42 | $-0.38 | needs ~1079 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3841 | 517 | 492 | 3 | 99.70c | $-162.92 | $-0.33 | needs ~1901 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5641 | 282 | 271 | 1 | 99.22c | $+106.00 | $+0.39 | needs ~237 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2260 | 2247 | 2219 | 151 | 93.08c | $-496.88 | $-0.24 | needs ~308 more bets with no loss |

