# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1372 coin-windows from 2026-11-10T10:30 to 2026-11-13T02:00 UTC (196 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **16 of 1372** windows. Reading the Kalshi book takes about 149 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 997 | 78 | 78 | 1 | 99.79c | $-9.13 | $-1.17 | needs ~3427 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 826 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 997 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1197 | 265 | 264 | 4 | 98.89c | $-13.51 | $-0.52 | needs ~532 more bets with no loss |
| Buy now, 60 s left (z 4+) | 819 | 100 | 96 | 0 | 99.63c | $+2.51 | $+0.26 | needs ~781 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1182 | 63 | 63 | 0 | 99.42c | $+2.90 | $+0.46 | needs ~436 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 437 | 434 | 434 | 22 | 93.50c | $+44.41 | $+1.09 | needs ~44 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 997 | 78 | 76 | 1 | 99.80c | $-85.80 | $-1.13 | needs ~2009 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 826 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 997 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1197 | 265 | 258 | 4 | 98.93c | $-138.48 | $-0.54 | needs ~531 more bets with no loss |
| Buy now, 60 s left (z 4+) | 819 | 100 | 94 | 0 | 99.63c | $+32.00 | $+0.34 | needs ~582 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1182 | 63 | 61 | 0 | 99.45c | $+31.66 | $+0.51 | needs ~392 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 437 | 434 | 432 | 22 | 93.66c | $+397.18 | $+0.98 | needs ~52 more bets with no loss |

