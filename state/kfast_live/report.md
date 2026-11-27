# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8393 coin-windows from 2026-11-10T10:30 to 2026-11-27T22:00 UTC (1199 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **139 of 8393** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5903 | 432 | 419 | 2 | 99.63c | $-8.99 | $-0.21 | needs ~1596 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4828 | 79 | 77 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~2024 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5903 | 227 | 218 | 3 | 99.18c | $-12.61 | $-0.57 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7141 | 1602 | 1587 | 21 | 98.88c | $-50.17 | $-0.32 | needs ~1200 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4766 | 591 | 575 | 3 | 99.71c | $-19.29 | $-0.34 | needs ~3002 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7031 | 327 | 321 | 2 | 99.01c | $+7.86 | $+0.25 | needs ~285 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2796 | 2780 | 2763 | 196 | 92.73c | $-73.09 | $-0.28 | needs ~363 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5903 | 432 | 407 | 2 | 99.64c | $-60.75 | $-0.15 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4828 | 79 | 74 | 0 | 99.80c | $+13.89 | $+0.19 | needs ~1164 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5903 | 227 | 200 | 3 | 99.17c | $-132.69 | $-0.64 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7141 | 1602 | 1548 | 21 | 98.91c | $-504.83 | $-0.33 | needs ~1164 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4766 | 591 | 565 | 3 | 99.71c | $-150.09 | $-0.26 | needs ~1948 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7031 | 327 | 313 | 2 | 99.03c | $+96.05 | $+0.30 | needs ~244 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2796 | 2780 | 2743 | 196 | 92.87c | $-993.28 | $-0.39 | needs ~397 more bets with no loss |

