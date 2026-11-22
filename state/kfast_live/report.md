# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5859 coin-windows from 2026-11-10T10:30 to 2026-11-22T01:45 UTC (837 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **97 of 5859** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4138 | 323 | 313 | 2 | 99.67c | $-13.03 | $-0.42 | needs ~2071 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3390 | 58 | 57 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2083 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4138 | 160 | 156 | 3 | 99.24c | $-18.56 | $-1.18 | needs ~760 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4992 | 1137 | 1126 | 16 | 98.86c | $-44.59 | $-0.40 | needs ~1057 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3374 | 431 | 418 | 3 | 99.68c | $-20.98 | $-0.50 | needs ~2674 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4923 | 248 | 245 | 0 | 99.58c | $+7.61 | $+0.31 | needs ~493 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1966 | 1953 | 1942 | 129 | 92.77c | $+29.48 | $+0.16 | needs ~171 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4138 | 323 | 306 | 2 | 99.67c | $-107.24 | $-0.35 | needs ~1450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3390 | 58 | 54 | 0 | 99.80c | $+9.93 | $+0.18 | needs ~1218 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4138 | 160 | 146 | 3 | 99.24c | $-188.49 | $-1.26 | needs ~741 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4992 | 1137 | 1101 | 16 | 98.90c | $-448.92 | $-0.41 | needs ~1033 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3374 | 431 | 410 | 3 | 99.68c | $-179.68 | $-0.44 | needs ~1867 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4923 | 248 | 239 | 0 | 99.59c | $+91.01 | $+0.38 | needs ~367 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1966 | 1953 | 1929 | 129 | 92.90c | $+121.94 | $+0.07 | needs ~193 more bets with no loss |

