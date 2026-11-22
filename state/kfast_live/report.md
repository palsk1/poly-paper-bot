# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6069 coin-windows from 2026-11-10T10:30 to 2026-11-22T12:45 UTC (867 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 6069** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4291 | 331 | 321 | 2 | 99.67c | $-12.80 | $-0.40 | needs ~2044 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3517 | 58 | 57 | 0 | 99.79c | $+0.62 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4291 | 163 | 158 | 3 | 99.24c | $-18.31 | $-1.15 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5179 | 1174 | 1162 | 16 | 98.88c | $-42.32 | $-0.37 | needs ~1046 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3493 | 452 | 438 | 3 | 99.68c | $-20.72 | $-0.47 | needs ~2710 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5110 | 254 | 251 | 0 | 99.56c | $+8.12 | $+0.32 | needs ~457 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2029 | 2017 | 2006 | 131 | 92.90c | $+27.14 | $+0.14 | needs ~180 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4291 | 331 | 314 | 2 | 99.67c | $-104.51 | $-0.33 | needs ~1435 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3517 | 58 | 54 | 0 | 99.80c | $+9.98 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4291 | 163 | 148 | 3 | 99.23c | $-186.20 | $-1.23 | needs ~731 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5179 | 1174 | 1136 | 16 | 98.91c | $-426.51 | $-0.37 | needs ~1023 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3493 | 452 | 430 | 3 | 99.69c | $-175.47 | $-0.41 | needs ~1875 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5110 | 254 | 245 | 0 | 99.58c | $+96.78 | $+0.39 | needs ~338 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2029 | 2017 | 1993 | 131 | 93.04c | $+95.23 | $+0.05 | needs ~203 more bets with no loss |

