# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4564 coin-windows from 2026-11-10T10:30 to 2026-11-19T15:00 UTC (652 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **77 of 4564** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3252 | 275 | 267 | 2 | 99.65c | $-13.64 | $-0.51 | needs ~1961 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2663 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3252 | 135 | 131 | 3 | 99.20c | $-19.87 | $-1.51 | needs ~739 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3895 | 918 | 910 | 14 | 98.89c | $-49.06 | $-0.54 | needs ~1099 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2649 | 364 | 353 | 3 | 99.67c | $-22.37 | $-0.63 | needs ~2728 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3829 | 207 | 204 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~583 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1536 | 1527 | 1519 | 106 | 92.74c | $-23.94 | $-0.17 | needs ~233 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3252 | 275 | 262 | 2 | 99.66c | $-116.85 | $-0.44 | needs ~1412 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2663 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3252 | 135 | 121 | 3 | 99.19c | $-201.63 | $-1.62 | needs ~716 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3895 | 918 | 892 | 14 | 98.93c | $-495.58 | $-0.56 | needs ~1085 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2649 | 364 | 345 | 3 | 99.68c | $-197.77 | $-0.57 | needs ~1915 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3829 | 207 | 198 | 0 | 99.62c | $+71.59 | $+0.36 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1536 | 1527 | 1509 | 106 | 92.88c | $-384.29 | $-0.27 | needs ~252 more bets with no loss |

