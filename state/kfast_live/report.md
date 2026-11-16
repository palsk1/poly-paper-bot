# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3045 coin-windows from 2026-11-10T10:30 to 2026-11-16T07:00 UTC (435 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3045** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2179 | 205 | 202 | 2 | 99.62c | $-14.52 | $-0.72 | needs ~1760 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1781 | 44 | 43 | 0 | 99.81c | $+0.39 | $+0.09 | needs ~2475 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2179 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2601 | 639 | 634 | 12 | 98.98c | $-61.87 | $-0.98 | needs ~1305 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1774 | 248 | 240 | 3 | 99.61c | $-23.42 | $-0.98 | needs ~2190 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2569 | 157 | 155 | 0 | 99.60c | $+4.49 | $+0.29 | needs ~638 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1039 | 1032 | 1029 | 75 | 92.78c | $-51.75 | $-0.54 | needs ~250 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2179 | 205 | 198 | 2 | 99.63c | $-130.80 | $-0.66 | needs ~1329 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1781 | 44 | 40 | 0 | 99.82c | $+6.76 | $+0.17 | needs ~1353 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2179 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2601 | 639 | 623 | 12 | 99.02c | $-621.90 | $-1.00 | needs ~1293 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1774 | 248 | 233 | 3 | 99.62c | $-216.92 | $-0.92 | needs ~1655 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2569 | 157 | 150 | 0 | 99.62c | $+53.85 | $+0.35 | needs ~498 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1039 | 1032 | 1022 | 75 | 92.91c | $-605.73 | $-0.63 | needs ~262 more bets with no loss |

