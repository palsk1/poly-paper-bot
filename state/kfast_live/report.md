# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7021 coin-windows from 2026-11-10T10:30 to 2026-11-24T21:45 UTC (1003 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **115 of 7021** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4970 | 382 | 371 | 2 | 99.62c | $-9.95 | $-0.27 | needs ~1586 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4059 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4970 | 179 | 173 | 3 | 99.12c | $-15.26 | $-0.88 | needs ~614 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5994 | 1337 | 1323 | 19 | 98.86c | $-53.60 | $-0.41 | needs ~1179 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4028 | 525 | 509 | 3 | 99.70c | $-19.98 | $-0.39 | needs ~2876 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5907 | 286 | 281 | 1 | 99.22c | $+8.83 | $+0.32 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2330 | 2317 | 2304 | 160 | 92.91c | $-66.61 | $-0.31 | needs ~342 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4970 | 382 | 362 | 2 | 99.63c | $-73.10 | $-0.20 | needs ~1155 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4059 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4970 | 179 | 161 | 3 | 99.11c | $-157.00 | $-0.95 | needs ~596 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5994 | 1337 | 1291 | 19 | 98.89c | $-538.69 | $-0.42 | needs ~1148 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4028 | 525 | 500 | 3 | 99.70c | $-162.11 | $-0.32 | needs ~1917 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5907 | 286 | 275 | 1 | 99.23c | $+106.36 | $+0.38 | needs ~240 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2330 | 2317 | 2288 | 160 | 93.04c | $-865.25 | $-0.40 | needs ~369 more bets with no loss |

