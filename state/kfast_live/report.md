# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4970 coin-windows from 2026-11-10T10:30 to 2026-11-20T08:45 UTC (710 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **81 of 4970** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3537 | 292 | 283 | 2 | 99.66c | $-13.49 | $-0.48 | needs ~2024 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2886 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3537 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4242 | 989 | 981 | 14 | 98.90c | $-42.36 | $-0.43 | needs ~1036 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2867 | 387 | 374 | 3 | 99.68c | $-21.97 | $-0.59 | needs ~2734 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4178 | 225 | 222 | 0 | 99.61c | $+6.23 | $+0.28 | needs ~595 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1666 | 1657 | 1648 | 113 | 92.69c | $+2.93 | $+0.02 | needs ~197 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3537 | 292 | 277 | 2 | 99.67c | $-114.02 | $-0.41 | needs ~1436 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2886 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3537 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4242 | 989 | 959 | 14 | 98.93c | $-428.13 | $-0.45 | needs ~1018 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2867 | 387 | 366 | 3 | 99.68c | $-192.40 | $-0.52 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4178 | 225 | 216 | 0 | 99.63c | $+75.79 | $+0.35 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1666 | 1657 | 1637 | 113 | 92.82c | $-125.48 | $-0.08 | needs ~216 more bets with no loss |

