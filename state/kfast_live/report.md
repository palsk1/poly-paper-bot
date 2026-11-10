# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 315 coin-windows from 2026-11-10T10:30 to 2026-11-10T23:45 UTC (45 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 315** windows. Reading the Kalshi book takes about 205 ms (slowest 1 in 10: 273 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 223 | 15 | 15 | 0 | 99.77c | $+0.19 | $+0.13 | needs ~1802 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 191 | 5 | 5 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 223 | 7 | 7 | 0 | 99.43c | $+0.38 | $+0.55 | needs ~417 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 280 | 63 | 62 | 0 | 98.69c | $+7.36 | $+1.19 | needs ~132 more bets with no loss |
| Buy now, 60 s left (z 4+) | 192 | 22 | 22 | 0 | 99.80c | $+0.23 | $+0.11 | needs ~2170 more bets with no loss |
| Buy now, 30 s left (z 4+) | 277 | 18 | 18 | 0 | 99.83c | $+0.12 | $+0.07 | needs ~3435 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 102 | 101 | 101 | 2 | 94.14c | $+35.45 | $+3.71 | **PROVEN** |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 223 | 15 | 15 | 0 | 99.79c | $+2.84 | $+0.19 | needs ~1201 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 191 | 5 | 5 | 0 | 99.90c | $+0.45 | $+0.09 | needs ~2553 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 223 | 7 | 7 | 0 | 99.46c | $+3.65 | $+0.52 | needs ~434 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 280 | 63 | 62 | 0 | 98.76c | $+72.16 | $+1.18 | needs ~134 more bets with no loss |
| Buy now, 60 s left (z 4+) | 192 | 22 | 21 | 0 | 99.80c | $+3.93 | $+0.18 | needs ~1225 more bets with no loss |
| Buy now, 30 s left (z 4+) | 277 | 18 | 18 | 0 | 99.83c | $+2.71 | $+0.15 | needs ~1511 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 102 | 101 | 100 | 2 | 94.31c | $+344.00 | $+3.61 | **PROVEN** |

