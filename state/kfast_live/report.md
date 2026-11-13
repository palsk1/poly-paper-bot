# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1337 coin-windows from 2026-11-10T10:30 to 2026-11-13T00:45 UTC (191 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **16 of 1337** windows. Reading the Kalshi book takes about 151 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 966 | 75 | 75 | 1 | 99.78c | $-9.13 | $-1.22 | needs ~3295 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 797 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 966 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1164 | 263 | 262 | 4 | 98.88c | $-13.54 | $-0.52 | needs ~529 more bets with no loss |
| Buy now, 60 s left (z 4+) | 790 | 96 | 92 | 0 | 99.61c | $+2.50 | $+0.27 | needs ~752 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1148 | 62 | 62 | 0 | 99.65c | $+1.49 | $+0.24 | needs ~894 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 432 | 429 | 429 | 22 | 93.56c | $+38.68 | $+0.96 | needs ~54 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 966 | 75 | 75 | 1 | 99.79c | $-85.89 | $-1.15 | needs ~1992 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 797 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 966 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1164 | 263 | 256 | 4 | 98.92c | $-138.86 | $-0.54 | needs ~528 more bets with no loss |
| Buy now, 60 s left (z 4+) | 790 | 96 | 90 | 0 | 99.62c | $+31.55 | $+0.35 | needs ~567 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1148 | 62 | 60 | 0 | 99.68c | $+18.14 | $+0.29 | needs ~721 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 432 | 429 | 428 | 22 | 93.73c | $+341.83 | $+0.85 | needs ~62 more bets with no loss |

