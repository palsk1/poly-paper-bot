# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4361 coin-windows from 2026-11-10T10:30 to 2026-11-19T02:00 UTC (623 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **72 of 4361** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3113 | 262 | 254 | 2 | 99.65c | $-13.81 | $-0.54 | needs ~1924 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2554 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3113 | 130 | 126 | 3 | 99.19c | $-20.16 | $-1.59 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3731 | 887 | 879 | 14 | 98.88c | $-51.02 | $-0.58 | needs ~1105 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2539 | 339 | 330 | 3 | 99.67c | $-22.76 | $-0.69 | needs ~2707 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3671 | 204 | 201 | 0 | 99.59c | $+5.94 | $+0.30 | needs ~574 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1463 | 1454 | 1446 | 101 | 92.87c | $-40.73 | $-0.30 | needs ~258 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3113 | 262 | 250 | 2 | 99.65c | $-119.50 | $-0.48 | needs ~1401 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2554 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3113 | 130 | 116 | 3 | 99.18c | $-204.56 | $-1.71 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3731 | 887 | 861 | 14 | 98.92c | $-515.57 | $-0.60 | needs ~1091 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2539 | 339 | 322 | 3 | 99.68c | $-203.66 | $-0.63 | needs ~1920 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3671 | 204 | 195 | 0 | 99.61c | $+71.32 | $+0.36 | needs ~439 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1463 | 1454 | 1437 | 101 | 93.00c | $-537.50 | $-0.40 | needs ~276 more bets with no loss |

