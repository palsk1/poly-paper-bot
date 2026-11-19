# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4725 coin-windows from 2026-11-10T10:30 to 2026-11-19T23:15 UTC (675 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **78 of 4725** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3375 | 281 | 272 | 2 | 99.66c | $-13.62 | $-0.50 | needs ~1990 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2761 | 50 | 49 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2496 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3375 | 138 | 134 | 3 | 99.21c | $-19.72 | $-1.46 | needs ~743 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4039 | 942 | 934 | 14 | 98.90c | $-47.50 | $-0.51 | needs ~1093 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2746 | 369 | 358 | 3 | 99.68c | $-22.34 | $-0.62 | needs ~2755 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3972 | 209 | 206 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~589 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1579 | 1570 | 1561 | 108 | 92.74c | $-15.26 | $-0.10 | needs ~221 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3375 | 281 | 266 | 2 | 99.66c | $-116.18 | $-0.43 | needs ~1422 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2761 | 50 | 46 | 0 | 99.82c | $+7.75 | $+0.17 | needs ~1347 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3375 | 138 | 124 | 3 | 99.20c | $-200.13 | $-1.57 | needs ~721 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4039 | 942 | 915 | 14 | 98.94c | $-479.11 | $-0.52 | needs ~1078 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2746 | 369 | 350 | 3 | 99.68c | $-197.05 | $-0.56 | needs ~1927 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3972 | 209 | 200 | 0 | 99.62c | $+71.77 | $+0.35 | needs ~446 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1579 | 1570 | 1550 | 108 | 92.88c | $-303.23 | $-0.21 | needs ~240 more bets with no loss |

