# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5894 coin-windows from 2026-11-10T10:30 to 2026-11-22T03:00 UTC (842 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 5894** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4160 | 323 | 313 | 2 | 99.67c | $-13.03 | $-0.42 | needs ~2071 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3409 | 58 | 57 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2083 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4160 | 160 | 156 | 3 | 99.24c | $-18.56 | $-1.18 | needs ~760 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5018 | 1141 | 1130 | 16 | 98.87c | $-44.53 | $-0.40 | needs ~1059 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3394 | 433 | 420 | 3 | 99.68c | $-20.95 | $-0.50 | needs ~2677 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4950 | 250 | 247 | 0 | 99.58c | $+7.62 | $+0.31 | needs ~496 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1979 | 1966 | 1955 | 131 | 92.75c | $+22.11 | $+0.12 | needs ~183 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4160 | 323 | 306 | 2 | 99.67c | $-107.24 | $-0.35 | needs ~1450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3409 | 58 | 54 | 0 | 99.80c | $+9.93 | $+0.18 | needs ~1218 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4160 | 160 | 146 | 3 | 99.24c | $-188.49 | $-1.26 | needs ~741 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5018 | 1141 | 1105 | 16 | 98.90c | $-448.16 | $-0.41 | needs ~1035 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3394 | 433 | 412 | 3 | 99.68c | $-179.23 | $-0.43 | needs ~1867 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4950 | 250 | 241 | 0 | 99.60c | $+91.28 | $+0.37 | needs ~368 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1979 | 1966 | 1942 | 131 | 92.88c | $+44.45 | $+0.02 | needs ~206 more bets with no loss |

