# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4508 coin-windows from 2026-11-10T10:30 to 2026-11-19T07:45 UTC (644 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **76 of 4508** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3218 | 274 | 266 | 2 | 99.65c | $-13.64 | $-0.51 | needs ~1954 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2636 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3218 | 135 | 131 | 3 | 99.20c | $-19.87 | $-1.51 | needs ~739 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3851 | 910 | 902 | 14 | 98.89c | $-49.42 | $-0.55 | needs ~1098 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2621 | 363 | 352 | 3 | 99.67c | $-22.37 | $-0.64 | needs ~2721 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3788 | 207 | 204 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~583 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1513 | 1504 | 1496 | 105 | 92.75c | $-31.12 | $-0.22 | needs ~243 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3218 | 274 | 262 | 2 | 99.66c | $-116.85 | $-0.44 | needs ~1412 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2636 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3218 | 135 | 121 | 3 | 99.19c | $-201.63 | $-1.62 | needs ~716 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3851 | 910 | 884 | 14 | 98.92c | $-499.14 | $-0.56 | needs ~1083 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2621 | 363 | 344 | 3 | 99.68c | $-197.86 | $-0.57 | needs ~1911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3788 | 207 | 198 | 0 | 99.62c | $+71.59 | $+0.36 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1513 | 1504 | 1487 | 105 | 92.89c | $-451.88 | $-0.32 | needs ~262 more bets with no loss |

