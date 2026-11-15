# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2709 coin-windows from 2026-11-10T10:30 to 2026-11-15T16:15 UTC (387 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **45 of 2709** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1941 | 164 | 161 | 1 | 99.79c | $-8.19 | $-0.51 | needs ~3313 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1592 | 32 | 31 | 0 | 99.84c | $+0.17 | $+0.05 | needs ~4162 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1941 | 78 | 76 | 1 | 99.44c | $-5.85 | $-0.76 | needs ~646 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2327 | 544 | 540 | 9 | 99.01c | $-41.83 | $-0.78 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1581 | 206 | 198 | 0 | 99.63c | $+5.11 | $+0.26 | needs ~688 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2294 | 129 | 127 | 0 | 99.58c | $+3.95 | $+0.31 | needs ~612 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 901 | 895 | 892 | 59 | 93.01c | $-4.54 | $-0.05 | needs ~169 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1941 | 164 | 157 | 1 | 99.79c | $-70.05 | $-0.44 | needs ~1895 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1592 | 32 | 28 | 0 | 99.84c | $+4.05 | $+0.14 | needs ~1619 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1941 | 78 | 71 | 1 | 99.45c | $-60.24 | $-0.83 | needs ~639 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2327 | 544 | 529 | 9 | 99.05c | $-422.13 | $-0.80 | needs ~1044 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1581 | 206 | 193 | 0 | 99.63c | $+65.73 | $+0.34 | needs ~478 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2294 | 129 | 122 | 0 | 99.60c | $+46.68 | $+0.37 | needs ~489 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 901 | 895 | 885 | 59 | 93.14c | $-123.81 | $-0.15 | needs ~179 more bets with no loss |

