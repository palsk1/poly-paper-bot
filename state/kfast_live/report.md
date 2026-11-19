# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4690 coin-windows from 2026-11-10T10:30 to 2026-11-19T19:30 UTC (670 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **78 of 4690** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3347 | 278 | 270 | 2 | 99.66c | $-13.63 | $-0.50 | needs ~1980 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2738 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3347 | 136 | 132 | 3 | 99.20c | $-19.82 | $-1.49 | needs ~740 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4007 | 934 | 926 | 14 | 98.90c | $-47.82 | $-0.52 | needs ~1091 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2725 | 368 | 357 | 3 | 99.68c | $-22.34 | $-0.63 | needs ~2747 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3941 | 209 | 206 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~589 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1569 | 1560 | 1552 | 108 | 92.72c | $-18.60 | $-0.13 | needs ~226 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3347 | 278 | 264 | 2 | 99.66c | $-116.53 | $-0.44 | needs ~1419 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2738 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3347 | 136 | 122 | 3 | 99.19c | $-201.13 | $-1.60 | needs ~718 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4007 | 934 | 908 | 14 | 98.93c | $-482.65 | $-0.53 | needs ~1076 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2725 | 368 | 349 | 3 | 99.68c | $-197.14 | $-0.56 | needs ~1923 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3941 | 209 | 200 | 0 | 99.62c | $+71.77 | $+0.35 | needs ~446 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1569 | 1560 | 1541 | 108 | 92.86c | $-335.98 | $-0.23 | needs ~245 more bets with no loss |

