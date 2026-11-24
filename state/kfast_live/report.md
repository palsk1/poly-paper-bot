# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6909 coin-windows from 2026-11-10T10:30 to 2026-11-24T12:45 UTC (987 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **113 of 6909** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 232 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4890 | 381 | 370 | 2 | 99.62c | $-9.99 | $-0.27 | needs ~1590 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3996 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4890 | 177 | 171 | 3 | 99.11c | $-15.35 | $-0.89 | needs ~611 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5895 | 1317 | 1303 | 19 | 98.87c | $-56.66 | $-0.44 | needs ~1217 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3969 | 522 | 506 | 3 | 99.69c | $-19.98 | $-0.39 | needs ~2859 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5813 | 284 | 279 | 1 | 99.21c | $+8.83 | $+0.32 | needs ~292 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2301 | 2288 | 2275 | 156 | 92.93c | $-48.61 | $-0.23 | needs ~312 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4890 | 381 | 361 | 2 | 99.63c | $-73.56 | $-0.20 | needs ~1157 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3996 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4890 | 177 | 159 | 3 | 99.11c | $-157.96 | $-0.97 | needs ~594 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5895 | 1317 | 1273 | 19 | 98.90c | $-569.16 | $-0.45 | needs ~1188 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3969 | 522 | 497 | 3 | 99.70c | $-162.38 | $-0.32 | needs ~1910 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5813 | 284 | 273 | 1 | 99.22c | $+106.18 | $+0.39 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2301 | 2288 | 2259 | 156 | 93.06c | $-679.88 | $-0.32 | needs ~338 more bets with no loss |

