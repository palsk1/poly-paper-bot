# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5978 coin-windows from 2026-11-10T10:30 to 2026-11-22T09:00 UTC (854 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **101 of 5978** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4216 | 325 | 315 | 2 | 99.67c | $-12.93 | $-0.41 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3459 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4216 | 161 | 156 | 3 | 99.24c | $-18.45 | $-1.18 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5093 | 1158 | 1146 | 16 | 98.87c | $-43.36 | $-0.38 | needs ~1051 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3436 | 444 | 430 | 3 | 99.68c | $-20.93 | $-0.49 | needs ~2733 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5027 | 254 | 251 | 1 | 99.41c | $+1.95 | $+0.08 | needs ~562 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2006 | 1995 | 1984 | 130 | 92.80c | $+41.30 | $+0.22 | needs ~156 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4216 | 325 | 308 | 2 | 99.67c | $-106.20 | $-0.34 | needs ~1439 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3459 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4216 | 161 | 146 | 3 | 99.23c | $-187.62 | $-1.26 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5093 | 1158 | 1121 | 16 | 98.91c | $-437.15 | $-0.39 | needs ~1029 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3436 | 444 | 422 | 3 | 99.69c | $-178.07 | $-0.42 | needs ~1889 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5027 | 254 | 245 | 1 | 99.43c | $+31.66 | $+0.13 | needs ~482 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2006 | 1995 | 1971 | 130 | 92.94c | $+237.63 | $+0.13 | needs ~178 more bets with no loss |

