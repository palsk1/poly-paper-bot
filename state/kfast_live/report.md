# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2415 coin-windows from 2026-11-10T10:30 to 2026-11-15T00:45 UTC (345 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **40 of 2415** windows. Reading the Kalshi book takes about 136 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1739 | 142 | 140 | 1 | 99.78c | $-8.39 | $-0.60 | needs ~3249 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1439 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1739 | 65 | 64 | 1 | 99.43c | $-6.48 | $-1.01 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2080 | 468 | 465 | 7 | 98.95c | $-25.94 | $-0.56 | needs ~778 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1423 | 183 | 176 | 0 | 99.62c | $+4.65 | $+0.26 | needs ~689 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2056 | 115 | 113 | 0 | 99.54c | $+3.88 | $+0.34 | needs ~555 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 789 | 783 | 781 | 53 | 93.08c | $-22.92 | $-0.31 | needs ~192 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1739 | 142 | 138 | 1 | 99.79c | $-73.68 | $-0.53 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1439 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1739 | 65 | 60 | 1 | 99.44c | $-65.82 | $-1.06 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2080 | 468 | 454 | 7 | 98.99c | $-264.96 | $-0.58 | needs ~774 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1423 | 183 | 171 | 0 | 99.63c | $+59.51 | $+0.34 | needs ~488 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2056 | 115 | 108 | 0 | 99.56c | $+44.86 | $+0.40 | needs ~456 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 789 | 783 | 776 | 53 | 93.22c | $-300.60 | $-0.41 | needs ~202 more bets with no loss |

