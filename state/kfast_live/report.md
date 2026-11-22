# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5928 coin-windows from 2026-11-10T10:30 to 2026-11-22T07:15 UTC (847 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **98 of 5928** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4190 | 323 | 313 | 2 | 99.67c | $-13.12 | $-0.42 | needs ~2100 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3440 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4190 | 159 | 154 | 3 | 99.24c | $-18.64 | $-1.20 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5057 | 1148 | 1136 | 16 | 98.88c | $-44.67 | $-0.40 | needs ~1066 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3416 | 441 | 427 | 3 | 99.68c | $-21.04 | $-0.49 | needs ~2752 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4989 | 251 | 248 | 0 | 99.58c | $+7.65 | $+0.31 | needs ~495 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1981 | 1970 | 1959 | 129 | 92.81c | $+33.07 | $+0.18 | needs ~167 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4190 | 323 | 306 | 2 | 99.68c | $-107.99 | $-0.35 | needs ~1464 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3440 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4190 | 159 | 144 | 3 | 99.23c | $-189.41 | $-1.28 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5057 | 1148 | 1111 | 16 | 98.91c | $-449.41 | $-0.40 | needs ~1043 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3416 | 441 | 419 | 3 | 99.69c | $-179.36 | $-0.43 | needs ~1900 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4989 | 251 | 242 | 0 | 99.60c | $+91.90 | $+0.37 | needs ~365 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1981 | 1970 | 1946 | 129 | 92.94c | $+158.03 | $+0.09 | needs ~189 more bets with no loss |

