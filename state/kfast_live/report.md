# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6993 coin-windows from 2026-11-10T10:30 to 2026-11-24T15:45 UTC (999 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **115 of 6993** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 232 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4945 | 381 | 370 | 2 | 99.62c | $-9.99 | $-0.27 | needs ~1590 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4041 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4945 | 178 | 172 | 3 | 99.12c | $-15.30 | $-0.89 | needs ~612 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5966 | 1333 | 1319 | 19 | 98.87c | $-56.03 | $-0.43 | needs ~1221 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4007 | 525 | 509 | 3 | 99.70c | $-19.98 | $-0.39 | needs ~2876 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5881 | 285 | 280 | 1 | 99.22c | $+8.83 | $+0.32 | needs ~293 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2327 | 2314 | 2301 | 160 | 92.92c | $-69.02 | $-0.32 | needs ~346 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4945 | 381 | 361 | 2 | 99.63c | $-73.56 | $-0.20 | needs ~1157 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4041 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4945 | 178 | 160 | 3 | 99.11c | $-157.46 | $-0.96 | needs ~595 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5966 | 1333 | 1287 | 19 | 98.91c | $-563.21 | $-0.44 | needs ~1190 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4007 | 525 | 500 | 3 | 99.70c | $-162.11 | $-0.32 | needs ~1917 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5881 | 285 | 274 | 1 | 99.23c | $+106.27 | $+0.38 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2327 | 2314 | 2285 | 160 | 93.05c | $-889.57 | $-0.41 | needs ~373 more bets with no loss |

