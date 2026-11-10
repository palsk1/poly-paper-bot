# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 259 coin-windows from 2026-11-10T10:30 to 2026-11-10T21:45 UTC (37 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 259** windows. Reading the Kalshi book takes about 192 ms (slowest 1 in 10: 252 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 179 | 14 | 14 | 0 | 99.76c | $+0.19 | $+0.14 | needs ~1682 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 149 | 4 | 4 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 179 | 5 | 5 | 0 | 99.40c | $+0.28 | $+0.56 | needs ~406 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 227 | 51 | 50 | 0 | 98.64c | $+6.22 | $+1.24 | needs ~136 more bets with no loss |
| Buy now, 60 s left (z 4+) | 151 | 17 | 17 | 0 | 99.77c | $+0.22 | $+0.13 | needs ~1754 more bets with no loss |
| Buy now, 30 s left (z 4+) | 227 | 15 | 15 | 0 | 99.83c | $+0.10 | $+0.07 | needs ~3438 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 88 | 88 | 88 | 2 | 94.03c | $+29.31 | $+3.53 | needs ~6 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 179 | 14 | 14 | 0 | 99.78c | $+2.75 | $+0.20 | needs ~1158 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 149 | 4 | 4 | 0 | 99.90c | $+0.36 | $+0.09 | needs ~2554 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 179 | 5 | 5 | 0 | 99.45c | $+2.65 | $+0.53 | needs ~429 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 227 | 51 | 50 | 0 | 98.71c | $+60.61 | $+1.23 | needs ~139 more bets with no loss |
| Buy now, 60 s left (z 4+) | 151 | 17 | 16 | 0 | 99.77c | $+3.39 | $+0.21 | needs ~1088 more bets with no loss |
| Buy now, 30 s left (z 4+) | 227 | 15 | 15 | 0 | 99.83c | $+2.26 | $+0.15 | needs ~1513 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 88 | 88 | 87 | 2 | 94.20c | $+282.50 | $+3.41 | needs ~8 more bets with no loss |

