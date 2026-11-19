# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4501 coin-windows from 2026-11-10T10:30 to 2026-11-19T07:30 UTC (643 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **76 of 4501** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3215 | 272 | 264 | 2 | 99.65c | $-13.67 | $-0.52 | needs ~1950 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2635 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3215 | 135 | 131 | 3 | 99.20c | $-19.87 | $-1.51 | needs ~739 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3847 | 908 | 900 | 14 | 98.89c | $-49.58 | $-0.55 | needs ~1099 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2620 | 363 | 352 | 3 | 99.67c | $-22.37 | $-0.64 | needs ~2721 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3785 | 207 | 204 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~583 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1507 | 1498 | 1490 | 105 | 92.76c | $-36.40 | $-0.26 | needs ~251 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3215 | 272 | 260 | 2 | 99.66c | $-117.31 | $-0.45 | needs ~1411 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2635 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3215 | 135 | 121 | 3 | 99.19c | $-201.63 | $-1.62 | needs ~716 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3847 | 908 | 882 | 14 | 98.92c | $-500.64 | $-0.57 | needs ~1084 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2620 | 363 | 344 | 3 | 99.68c | $-197.86 | $-0.57 | needs ~1911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3785 | 207 | 198 | 0 | 99.62c | $+71.59 | $+0.36 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1507 | 1498 | 1481 | 105 | 92.90c | $-499.60 | $-0.36 | needs ~270 more bets with no loss |

