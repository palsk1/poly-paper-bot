# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6979 coin-windows from 2026-11-10T10:30 to 2026-11-24T15:15 UTC (997 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **114 of 6979** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 232 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4938 | 381 | 370 | 2 | 99.62c | $-9.99 | $-0.27 | needs ~1590 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4034 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4938 | 178 | 172 | 3 | 99.12c | $-15.30 | $-0.89 | needs ~612 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5956 | 1331 | 1317 | 19 | 98.87c | $-56.16 | $-0.43 | needs ~1221 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4003 | 523 | 507 | 3 | 99.69c | $-19.98 | $-0.39 | needs ~2865 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5871 | 285 | 280 | 1 | 99.22c | $+8.83 | $+0.32 | needs ~293 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2321 | 2308 | 2295 | 159 | 92.94c | $-67.74 | $-0.32 | needs ~344 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4938 | 381 | 361 | 2 | 99.63c | $-73.56 | $-0.20 | needs ~1157 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4034 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4938 | 178 | 160 | 3 | 99.11c | $-157.46 | $-0.96 | needs ~595 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5956 | 1331 | 1285 | 19 | 98.91c | $-564.52 | $-0.44 | needs ~1191 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4003 | 523 | 498 | 3 | 99.70c | $-162.29 | $-0.32 | needs ~1913 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5871 | 285 | 274 | 1 | 99.23c | $+106.27 | $+0.38 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2321 | 2308 | 2279 | 159 | 93.07c | $-875.13 | $-0.41 | needs ~371 more bets with no loss |

