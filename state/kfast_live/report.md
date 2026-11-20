# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5124 coin-windows from 2026-11-10T10:30 to 2026-11-20T16:30 UTC (732 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **84 of 5124** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3663 | 294 | 284 | 2 | 99.66c | $-13.50 | $-0.48 | needs ~2034 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2999 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3663 | 145 | 141 | 3 | 99.22c | $-19.37 | $-1.37 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4386 | 1008 | 1000 | 16 | 98.90c | $-60.87 | $-0.61 | needs ~1260 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2980 | 392 | 379 | 3 | 99.68c | $-21.91 | $-0.58 | needs ~2748 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4318 | 226 | 223 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~593 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1693 | 1684 | 1674 | 116 | 92.68c | $-7.81 | $-0.05 | needs ~214 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3663 | 294 | 277 | 2 | 99.67c | $-113.97 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2999 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3663 | 145 | 131 | 3 | 99.21c | $-196.63 | $-1.46 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4386 | 1008 | 978 | 16 | 98.94c | $-613.07 | $-0.63 | needs ~1239 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2980 | 392 | 371 | 3 | 99.68c | $-191.41 | $-0.51 | needs ~1914 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4318 | 226 | 217 | 0 | 99.63c | $+76.09 | $+0.35 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1693 | 1684 | 1662 | 116 | 92.81c | $-233.69 | $-0.15 | needs ~233 more bets with no loss |

