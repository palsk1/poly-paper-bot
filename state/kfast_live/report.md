# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 189 coin-windows from 2026-11-10T10:30 to 2026-11-10T19:15 UTC (27 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 189** windows. Reading the Kalshi book takes about 157 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 140 | 8 | 8 | 0 | 99.86c | $+0.03 | $+0.04 | needs ~5000 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 118 | 3 | 3 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 140 | 1 | 1 | 0 | 99.50c | $+0.05 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 168 | 29 | 29 | 0 | 99.29c | $+1.80 | $+0.62 | needs ~341 more bets with no loss |
| Buy now, 60 s left (z 4+) | 119 | 12 | 12 | 0 | 99.81c | $+0.11 | $+0.09 | needs ~2477 more bets with no loss |
| Buy now, 30 s left (z 4+) | 170 | 11 | 11 | 0 | 99.83c | $+0.08 | $+0.07 | needs ~3154 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 54 | 54 | 54 | 2 | 94.64c | $+7.07 | $+1.38 | needs ~51 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 140 | 8 | 8 | 0 | 99.86c | $+0.99 | $+0.12 | needs ~1852 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 118 | 3 | 3 | 0 | 99.90c | $+0.27 | $+0.09 | needs ~2555 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 140 | 1 | 1 | 0 | 99.50c | $+0.50 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 168 | 29 | 29 | 0 | 99.36c | $+17.16 | $+0.60 | needs ~359 more bets with no loss |
| Buy now, 60 s left (z 4+) | 119 | 12 | 11 | 0 | 99.80c | $+2.02 | $+0.18 | needs ~1273 more bets with no loss |
| Buy now, 30 s left (z 4+) | 170 | 11 | 11 | 0 | 99.83c | $+1.72 | $+0.16 | needs ~1461 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 54 | 54 | 53 | 2 | 94.79c | $+65.42 | $+1.28 | needs ~53 more bets with no loss |

