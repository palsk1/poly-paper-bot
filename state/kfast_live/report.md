# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1246 coin-windows from 2026-11-10T10:30 to 2026-11-12T21:15 UTC (178 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **12 of 1246** windows. Reading the Kalshi book takes about 157 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 902 | 67 | 67 | 1 | 99.77c | $-9.16 | $-1.37 | needs ~3052 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 746 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 902 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1087 | 244 | 243 | 4 | 98.90c | $-15.84 | $-0.66 | needs ~560 more bets with no loss |
| Buy now, 60 s left (z 4+) | 736 | 87 | 84 | 0 | 99.61c | $+2.35 | $+0.28 | needs ~736 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1073 | 57 | 57 | 0 | 99.71c | $+1.08 | $+0.19 | needs ~1156 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 398 | 396 | 396 | 20 | 93.68c | $+34.18 | $+0.92 | needs ~58 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 902 | 67 | 67 | 1 | 99.79c | $-86.88 | $-1.30 | needs ~1919 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 746 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 902 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1087 | 244 | 237 | 4 | 98.94c | $-161.63 | $-0.68 | needs ~559 more bets with no loss |
| Buy now, 60 s left (z 4+) | 736 | 87 | 82 | 0 | 99.61c | $+29.55 | $+0.36 | needs ~558 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1073 | 57 | 55 | 0 | 99.71c | $+14.97 | $+0.26 | needs ~814 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 398 | 396 | 395 | 20 | 93.86c | $+298.40 | $+0.80 | needs ~67 more bets with no loss |

