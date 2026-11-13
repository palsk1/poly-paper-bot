# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1596 coin-windows from 2026-11-10T10:30 to 2026-11-13T12:30 UTC (228 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **21 of 1596** windows. Reading the Kalshi book takes about 172 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1146 | 90 | 89 | 1 | 99.79c | $-9.00 | $-1.01 | needs ~3388 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 941 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1146 | 39 | 38 | 1 | 99.42c | $-7.86 | $-2.05 | needs ~662 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1384 | 307 | 306 | 4 | 98.88c | $-9.19 | $-0.30 | needs ~487 more bets with no loss |
| Buy now, 60 s left (z 4+) | 932 | 120 | 116 | 0 | 99.67c | $+2.59 | $+0.22 | needs ~911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1366 | 70 | 70 | 0 | 99.46c | $+2.95 | $+0.42 | needs ~475 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 519 | 515 | 514 | 27 | 93.46c | $+45.00 | $+0.93 | needs ~52 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1146 | 90 | 87 | 1 | 99.79c | $-83.65 | $-0.96 | needs ~1985 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 941 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1146 | 39 | 34 | 1 | 99.42c | $-79.65 | $-2.22 | needs ~651 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1384 | 307 | 300 | 4 | 98.93c | $-95.75 | $-0.32 | needs ~487 more bets with no loss |
| Buy now, 60 s left (z 4+) | 932 | 120 | 113 | 0 | 99.67c | $+34.38 | $+0.30 | needs ~644 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1366 | 70 | 67 | 0 | 99.49c | $+32.67 | $+0.48 | needs ~416 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 519 | 515 | 511 | 27 | 93.61c | $+398.23 | $+0.83 | needs ~60 more bets with no loss |

