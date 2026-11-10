# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 294 coin-windows from 2026-11-10T10:30 to 2026-11-10T23:00 UTC (42 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 294** windows. Reading the Kalshi book takes about 203 ms (slowest 1 in 10: 267 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 209 | 15 | 15 | 0 | 99.77c | $+0.19 | $+0.13 | needs ~1802 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 178 | 5 | 5 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 209 | 7 | 7 | 0 | 99.43c | $+0.38 | $+0.55 | needs ~417 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 261 | 58 | 57 | 0 | 98.74c | $+6.52 | $+1.14 | needs ~145 more bets with no loss |
| Buy now, 60 s left (z 4+) | 179 | 21 | 21 | 0 | 99.79c | $+0.23 | $+0.11 | needs ~2072 more bets with no loss |
| Buy now, 30 s left (z 4+) | 260 | 18 | 18 | 0 | 99.83c | $+0.12 | $+0.07 | needs ~3435 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 94 | 94 | 94 | 2 | 94.29c | $+30.31 | $+3.41 | needs ~4 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 209 | 15 | 15 | 0 | 99.79c | $+2.84 | $+0.19 | needs ~1201 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 178 | 5 | 5 | 0 | 99.90c | $+0.45 | $+0.09 | needs ~2553 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 209 | 7 | 7 | 0 | 99.46c | $+3.65 | $+0.52 | needs ~434 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 261 | 58 | 57 | 0 | 98.81c | $+63.66 | $+1.13 | needs ~148 more bets with no loss |
| Buy now, 60 s left (z 4+) | 179 | 21 | 20 | 0 | 99.79c | $+3.84 | $+0.19 | needs ~1195 more bets with no loss |
| Buy now, 30 s left (z 4+) | 260 | 18 | 18 | 0 | 99.83c | $+2.71 | $+0.15 | needs ~1511 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 94 | 94 | 93 | 2 | 94.46c | $+292.56 | $+3.29 | needs ~6 more bets with no loss |

