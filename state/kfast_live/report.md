# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4669 coin-windows from 2026-11-10T10:30 to 2026-11-19T18:45 UTC (667 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **78 of 4669** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3331 | 278 | 270 | 2 | 99.66c | $-13.63 | $-0.50 | needs ~1980 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2724 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3331 | 136 | 132 | 3 | 99.20c | $-19.82 | $-1.49 | needs ~740 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3986 | 929 | 921 | 14 | 98.90c | $-48.18 | $-0.53 | needs ~1093 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2707 | 367 | 356 | 3 | 99.67c | $-22.35 | $-0.63 | needs ~2744 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3921 | 209 | 206 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~589 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1565 | 1556 | 1548 | 108 | 92.71c | $-18.92 | $-0.13 | needs ~226 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3331 | 278 | 264 | 2 | 99.66c | $-116.53 | $-0.44 | needs ~1419 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2724 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3331 | 136 | 122 | 3 | 99.19c | $-201.13 | $-1.60 | needs ~718 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3986 | 929 | 903 | 14 | 98.93c | $-486.44 | $-0.54 | needs ~1078 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2707 | 367 | 348 | 3 | 99.68c | $-197.32 | $-0.56 | needs ~1922 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3921 | 209 | 200 | 0 | 99.62c | $+71.77 | $+0.35 | needs ~446 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1565 | 1556 | 1537 | 108 | 92.84c | $-339.45 | $-0.24 | needs ~245 more bets with no loss |

