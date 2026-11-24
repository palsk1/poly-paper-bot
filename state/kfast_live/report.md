# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6944 coin-windows from 2026-11-10T10:30 to 2026-11-24T14:00 UTC (992 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **113 of 6944** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 232 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4913 | 381 | 370 | 2 | 99.62c | $-9.99 | $-0.27 | needs ~1590 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4015 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4913 | 177 | 171 | 3 | 99.11c | $-15.35 | $-0.89 | needs ~611 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5925 | 1324 | 1310 | 19 | 98.87c | $-56.28 | $-0.43 | needs ~1217 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3986 | 523 | 507 | 3 | 99.69c | $-19.98 | $-0.39 | needs ~2865 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5842 | 285 | 280 | 1 | 99.22c | $+8.83 | $+0.32 | needs ~293 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2312 | 2299 | 2286 | 157 | 92.92c | $-50.40 | $-0.24 | needs ~316 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4913 | 381 | 361 | 2 | 99.63c | $-73.56 | $-0.20 | needs ~1157 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4015 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4913 | 177 | 159 | 3 | 99.11c | $-157.96 | $-0.97 | needs ~594 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5925 | 1324 | 1280 | 19 | 98.90c | $-565.80 | $-0.44 | needs ~1188 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3986 | 523 | 498 | 3 | 99.70c | $-162.29 | $-0.32 | needs ~1913 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5842 | 285 | 274 | 1 | 99.23c | $+106.27 | $+0.38 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2312 | 2299 | 2270 | 157 | 93.05c | $-701.43 | $-0.33 | needs ~342 more bets with no loss |

