# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4235 coin-windows from 2026-11-10T10:30 to 2026-11-18T21:00 UTC (605 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4235** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3030 | 255 | 247 | 2 | 99.65c | $-13.96 | $-0.57 | needs ~1924 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2491 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3030 | 128 | 124 | 3 | 99.20c | $-20.34 | $-1.63 | needs ~740 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3624 | 862 | 854 | 14 | 98.89c | $-54.21 | $-0.64 | needs ~1145 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2476 | 331 | 322 | 3 | 99.67c | $-22.78 | $-0.71 | needs ~2650 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3569 | 197 | 194 | 0 | 99.59c | $+5.77 | $+0.30 | needs ~576 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1415 | 1406 | 1398 | 97 | 92.84c | $-29.22 | $-0.22 | needs ~236 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3030 | 255 | 243 | 2 | 99.65c | $-121.55 | $-0.50 | needs ~1404 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2491 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3030 | 128 | 114 | 3 | 99.19c | $-206.39 | $-1.76 | needs ~717 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3624 | 862 | 836 | 14 | 98.93c | $-548.22 | $-0.66 | needs ~1133 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2476 | 331 | 314 | 3 | 99.67c | $-204.56 | $-0.65 | needs ~1893 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3569 | 197 | 188 | 0 | 99.61c | $+69.11 | $+0.36 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1415 | 1406 | 1389 | 97 | 92.97c | $-416.49 | $-0.32 | needs ~253 more bets with no loss |

