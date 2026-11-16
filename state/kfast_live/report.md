# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2975 coin-windows from 2026-11-10T10:30 to 2026-11-16T04:30 UTC (425 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 2975** windows. Reading the Kalshi book takes about 148 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2118 | 199 | 196 | 2 | 99.61c | $-14.53 | $-0.74 | needs ~1711 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1729 | 42 | 41 | 0 | 99.80c | $+0.39 | $+0.10 | needs ~2359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2118 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2536 | 629 | 624 | 12 | 98.98c | $-62.42 | $-1.01 | needs ~1303 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1723 | 240 | 232 | 3 | 99.60c | $-23.48 | $-1.01 | needs ~2139 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2505 | 156 | 154 | 0 | 99.60c | $+4.49 | $+0.29 | needs ~634 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1024 | 1017 | 1014 | 75 | 92.77c | $-61.46 | $-0.65 | needs ~264 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2118 | 199 | 192 | 2 | 99.62c | $-131.43 | $-0.68 | needs ~1303 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1729 | 42 | 38 | 0 | 99.81c | $+6.58 | $+0.17 | needs ~1323 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2118 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2536 | 629 | 613 | 12 | 99.01c | $-627.20 | $-1.02 | needs ~1290 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1723 | 240 | 226 | 3 | 99.61c | $-218.13 | $-0.95 | needs ~1630 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2505 | 156 | 149 | 0 | 99.62c | $+53.76 | $+0.35 | needs ~496 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1024 | 1017 | 1007 | 75 | 92.90c | $-702.48 | $-0.75 | needs ~276 more bets with no loss |

