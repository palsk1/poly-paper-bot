# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5908 coin-windows from 2026-11-10T10:30 to 2026-11-22T03:30 UTC (844 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 5908** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4169 | 323 | 313 | 2 | 99.67c | $-13.03 | $-0.42 | needs ~2071 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3415 | 58 | 57 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2083 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4169 | 160 | 156 | 3 | 99.24c | $-18.56 | $-1.18 | needs ~760 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5031 | 1145 | 1134 | 16 | 98.87c | $-44.02 | $-0.39 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3400 | 434 | 421 | 3 | 99.68c | $-20.95 | $-0.50 | needs ~2683 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4963 | 252 | 249 | 0 | 99.58c | $+7.62 | $+0.31 | needs ~500 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1984 | 1971 | 1960 | 131 | 92.74c | $+26.74 | $+0.15 | needs ~176 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4169 | 323 | 306 | 2 | 99.67c | $-107.24 | $-0.35 | needs ~1450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3415 | 58 | 54 | 0 | 99.80c | $+9.93 | $+0.18 | needs ~1218 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4169 | 160 | 146 | 3 | 99.24c | $-188.49 | $-1.26 | needs ~741 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5031 | 1145 | 1109 | 16 | 98.90c | $-442.86 | $-0.40 | needs ~1029 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3400 | 434 | 413 | 3 | 99.68c | $-179.14 | $-0.43 | needs ~1870 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4963 | 252 | 243 | 0 | 99.60c | $+91.46 | $+0.37 | needs ~370 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1984 | 1971 | 1947 | 131 | 92.88c | $+91.03 | $+0.05 | needs ~199 more bets with no loss |

