# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5824 coin-windows from 2026-11-10T10:30 to 2026-11-22T00:30 UTC (832 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **97 of 5824** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4114 | 319 | 309 | 2 | 99.67c | $-13.14 | $-0.43 | needs ~2080 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3372 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4114 | 157 | 153 | 3 | 99.24c | $-18.70 | $-1.22 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4965 | 1131 | 1120 | 16 | 98.87c | $-45.59 | $-0.41 | needs ~1070 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3356 | 429 | 416 | 3 | 99.68c | $-21.07 | $-0.51 | needs ~2693 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4895 | 245 | 242 | 0 | 99.58c | $+7.55 | $+0.31 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1950 | 1939 | 1928 | 127 | 92.77c | $+39.90 | $+0.22 | needs ~155 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4114 | 319 | 302 | 2 | 99.68c | $-108.53 | $-0.36 | needs ~1455 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3372 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4114 | 157 | 143 | 3 | 99.23c | $-189.91 | $-1.30 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4965 | 1131 | 1095 | 16 | 98.90c | $-459.10 | $-0.42 | needs ~1047 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3356 | 429 | 408 | 3 | 99.68c | $-180.70 | $-0.44 | needs ~1877 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4895 | 245 | 236 | 0 | 99.59c | $+90.44 | $+0.38 | needs ~366 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1950 | 1939 | 1915 | 127 | 92.90c | $+226.16 | $+0.13 | needs ~176 more bets with no loss |

