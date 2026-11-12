# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1267 coin-windows from 2026-11-10T10:30 to 2026-11-12T22:00 UTC (181 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **13 of 1267** windows. Reading the Kalshi book takes about 156 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 917 | 68 | 68 | 1 | 99.78c | $-9.16 | $-1.35 | needs ~3097 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 759 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 917 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1105 | 248 | 247 | 4 | 98.90c | $-15.47 | $-0.63 | needs ~557 more bets with no loss |
| Buy now, 60 s left (z 4+) | 749 | 89 | 86 | 0 | 99.61c | $+2.35 | $+0.27 | needs ~754 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1090 | 58 | 58 | 0 | 99.71c | $+1.09 | $+0.19 | needs ~1165 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 405 | 403 | 403 | 21 | 93.69c | $+27.90 | $+0.74 | needs ~71 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 917 | 68 | 68 | 1 | 99.79c | $-86.79 | $-1.28 | needs ~1934 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 759 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 917 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1105 | 248 | 241 | 4 | 98.94c | $-157.92 | $-0.65 | needs ~556 more bets with no loss |
| Buy now, 60 s left (z 4+) | 749 | 89 | 84 | 0 | 99.62c | $+29.73 | $+0.35 | needs ~568 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1090 | 58 | 56 | 0 | 99.71c | $+15.15 | $+0.26 | needs ~818 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 405 | 403 | 402 | 21 | 93.87c | $+235.36 | $+0.62 | needs ~80 more bets with no loss |

