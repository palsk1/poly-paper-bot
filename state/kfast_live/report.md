# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6412 coin-windows from 2026-11-10T10:30 to 2026-11-23T04:15 UTC (916 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **106 of 6412** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4524 | 356 | 346 | 2 | 99.60c | $-10.13 | $-0.29 | needs ~1511 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3701 | 63 | 62 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1714 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4524 | 171 | 166 | 3 | 99.10c | $-15.62 | $-0.94 | needs ~608 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5466 | 1249 | 1236 | 18 | 98.87c | $-54.30 | $-0.44 | needs ~1188 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3675 | 492 | 477 | 3 | 99.68c | $-20.11 | $-0.42 | needs ~2738 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5388 | 268 | 265 | 1 | 99.18c | $+8.76 | $+0.33 | needs ~281 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2158 | 2144 | 2132 | 142 | 92.89c | $+3.99 | $+0.02 | needs ~222 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4524 | 356 | 338 | 2 | 99.61c | $-76.74 | $-0.23 | needs ~1119 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3701 | 63 | 59 | 0 | 99.78c | $+12.09 | $+0.20 | needs ~1080 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4524 | 171 | 156 | 3 | 99.10c | $-159.89 | $-1.00 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5466 | 1249 | 1210 | 18 | 98.90c | $-545.00 | $-0.45 | needs ~1162 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3675 | 492 | 468 | 3 | 99.69c | $-166.27 | $-0.35 | needs ~1866 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5388 | 268 | 259 | 1 | 99.19c | $+104.11 | $+0.40 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2158 | 2144 | 2118 | 142 | 93.02c | $-142.25 | $-0.07 | needs ~246 more bets with no loss |

