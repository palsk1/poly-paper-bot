# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5964 coin-windows from 2026-11-10T10:30 to 2026-11-22T08:30 UTC (852 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 5964** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4211 | 324 | 314 | 2 | 99.67c | $-12.99 | $-0.41 | needs ~2062 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3456 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4211 | 160 | 155 | 3 | 99.24c | $-18.51 | $-1.19 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5084 | 1154 | 1142 | 16 | 98.87c | $-43.66 | $-0.39 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3431 | 443 | 429 | 3 | 99.68c | $-21.02 | $-0.49 | needs ~2758 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5018 | 253 | 250 | 0 | 99.56c | $+8.12 | $+0.33 | needs ~455 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1997 | 1986 | 1975 | 129 | 92.84c | $+38.07 | $+0.21 | needs ~161 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4211 | 324 | 307 | 2 | 99.67c | $-106.85 | $-0.35 | needs ~1447 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3456 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4211 | 160 | 145 | 3 | 99.23c | $-188.27 | $-1.27 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5084 | 1154 | 1117 | 16 | 98.90c | $-440.39 | $-0.39 | needs ~1031 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3431 | 443 | 421 | 3 | 99.69c | $-179.00 | $-0.42 | needs ~1902 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5018 | 253 | 244 | 0 | 99.58c | $+96.69 | $+0.39 | needs ~338 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1997 | 1986 | 1962 | 129 | 92.97c | $+206.93 | $+0.11 | needs ~183 more bets with no loss |

