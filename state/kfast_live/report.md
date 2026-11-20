# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4795 coin-windows from 2026-11-10T10:30 to 2026-11-20T01:45 UTC (685 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **79 of 4795** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3423 | 286 | 277 | 2 | 99.66c | $-13.54 | $-0.49 | needs ~1998 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2796 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3423 | 142 | 138 | 3 | 99.22c | $-19.52 | $-1.41 | needs ~748 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4097 | 959 | 951 | 14 | 98.90c | $-45.13 | $-0.48 | needs ~1062 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2780 | 377 | 364 | 3 | 99.68c | $-22.19 | $-0.61 | needs ~2745 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4030 | 217 | 214 | 0 | 99.60c | $+6.14 | $+0.29 | needs ~585 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1605 | 1596 | 1587 | 108 | 92.76c | $-1.01 | $-0.01 | needs ~201 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3423 | 286 | 271 | 2 | 99.66c | $-115.01 | $-0.42 | needs ~1425 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2796 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3423 | 142 | 128 | 3 | 99.21c | $-198.13 | $-1.51 | needs ~726 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4097 | 959 | 931 | 14 | 98.93c | $-455.37 | $-0.49 | needs ~1044 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2780 | 377 | 356 | 3 | 99.68c | $-195.03 | $-0.54 | needs ~1913 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4030 | 217 | 208 | 0 | 99.62c | $+74.34 | $+0.35 | needs ~440 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1605 | 1596 | 1576 | 108 | 92.90c | $-162.05 | $-0.11 | needs ~220 more bets with no loss |

