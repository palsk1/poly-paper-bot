# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2401 coin-windows from 2026-11-10T10:30 to 2026-11-14T22:15 UTC (343 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **39 of 2401** windows. Reading the Kalshi book takes about 138 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1734 | 141 | 139 | 1 | 99.78c | $-8.35 | $-0.60 | needs ~3144 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1434 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1734 | 65 | 64 | 1 | 99.43c | $-6.49 | $-1.01 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2077 | 475 | 472 | 7 | 98.97c | $-26.21 | $-0.56 | needs ~798 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1419 | 184 | 176 | 0 | 99.62c | $+4.65 | $+0.26 | needs ~688 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2052 | 114 | 112 | 0 | 99.54c | $+3.87 | $+0.35 | needs ~552 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 779 | 772 | 770 | 52 | 93.33c | $-38.24 | $-0.53 | needs ~223 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1734 | 141 | 137 | 1 | 99.79c | $-73.45 | $-0.54 | needs ~1869 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1434 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1734 | 65 | 59 | 1 | 99.44c | $-66.09 | $-1.08 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2077 | 475 | 460 | 7 | 99.01c | $-266.81 | $-0.58 | needs ~789 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1419 | 184 | 171 | 0 | 99.63c | $+59.59 | $+0.34 | needs ~486 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2052 | 114 | 107 | 0 | 99.56c | $+44.68 | $+0.41 | needs ~454 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 779 | 772 | 765 | 52 | 93.45c | $-445.04 | $-0.62 | needs ~232 more bets with no loss |

