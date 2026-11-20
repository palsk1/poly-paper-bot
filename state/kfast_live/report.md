# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4760 coin-windows from 2026-11-10T10:30 to 2026-11-20T00:30 UTC (680 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **79 of 4760** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3401 | 285 | 276 | 2 | 99.66c | $-13.55 | $-0.49 | needs ~1995 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2780 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3401 | 140 | 136 | 3 | 99.21c | $-19.62 | $-1.43 | needs ~745 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4069 | 950 | 942 | 14 | 98.90c | $-46.62 | $-0.50 | needs ~1084 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2761 | 373 | 361 | 3 | 99.67c | $-22.19 | $-0.61 | needs ~2724 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4002 | 212 | 209 | 0 | 99.60c | $+6.05 | $+0.29 | needs ~583 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1591 | 1582 | 1573 | 108 | 92.75c | $-8.74 | $-0.06 | needs ~212 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3401 | 285 | 270 | 2 | 99.66c | $-115.19 | $-0.42 | needs ~1423 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2780 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3401 | 140 | 126 | 3 | 99.20c | $-199.13 | $-1.54 | needs ~723 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4069 | 950 | 923 | 14 | 98.94c | $-470.11 | $-0.51 | needs ~1067 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2761 | 373 | 353 | 3 | 99.68c | $-195.38 | $-0.55 | needs ~1906 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4002 | 212 | 203 | 0 | 99.62c | $+73.06 | $+0.35 | needs ~441 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1591 | 1582 | 1562 | 108 | 92.89c | $-238.26 | $-0.16 | needs ~231 more bets with no loss |

