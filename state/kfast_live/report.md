# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 952 coin-windows from 2026-11-10T10:30 to 2026-11-12T04:15 UTC (136 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **7 of 952** windows. Reading the Kalshi book takes about 169 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 695 | 47 | 47 | 1 | 99.74c | $-9.27 | $-1.98 | needs ~2472 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 582 | 13 | 13 | 0 | 99.88c | $+0.02 | $+0.02 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 695 | 27 | 26 | 1 | 99.39c | $-8.45 | $-3.20 | needs ~639 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 831 | 184 | 183 | 4 | 98.82c | $-20.42 | $-1.12 | needs ~564 more bets with no loss |
| Buy now, 60 s left (z 4+) | 576 | 69 | 69 | 0 | 99.58c | $+2.10 | $+0.30 | needs ~688 more bets with no loss |
| Buy now, 30 s left (z 4+) | 825 | 47 | 47 | 0 | 99.70c | $+0.92 | $+0.20 | needs ~1127 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 296 | 294 | 294 | 16 | 93.37c | $+22.62 | $+0.82 | needs ~65 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 695 | 47 | 47 | 1 | 99.76c | $-89.58 | $-1.91 | needs ~1706 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 582 | 13 | 13 | 0 | 99.89c | $+1.28 | $+0.10 | needs ~2318 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 695 | 27 | 24 | 1 | 99.39c | $-85.15 | $-3.41 | needs ~629 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 831 | 184 | 178 | 4 | 98.86c | $-206.90 | $-1.16 | needs ~562 more bets with no loss |
| Buy now, 60 s left (z 4+) | 576 | 69 | 67 | 0 | 99.59c | $+25.92 | $+0.38 | needs ~534 more bets with no loss |
| Buy now, 30 s left (z 4+) | 825 | 47 | 46 | 0 | 99.71c | $+12.61 | $+0.27 | needs ~808 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 296 | 294 | 293 | 16 | 93.56c | $+189.48 | $+0.69 | needs ~72 more bets with no loss |

