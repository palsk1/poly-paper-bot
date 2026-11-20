# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5054 coin-windows from 2026-11-10T10:30 to 2026-11-20T14:00 UTC (722 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **84 of 5054** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3601 | 294 | 284 | 2 | 99.66c | $-13.50 | $-0.48 | needs ~2034 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2942 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3601 | 144 | 140 | 3 | 99.22c | $-19.42 | $-1.38 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4320 | 1002 | 994 | 16 | 98.90c | $-61.17 | $-0.62 | needs ~1259 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2923 | 392 | 379 | 3 | 99.68c | $-21.91 | $-0.58 | needs ~2748 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4253 | 226 | 223 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~593 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1685 | 1676 | 1666 | 115 | 92.68c | $-3.87 | $-0.02 | needs ~207 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3601 | 294 | 277 | 2 | 99.67c | $-113.97 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2942 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3601 | 144 | 130 | 3 | 99.21c | $-197.13 | $-1.48 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4320 | 1002 | 972 | 16 | 98.93c | $-616.25 | $-0.63 | needs ~1239 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2923 | 392 | 371 | 3 | 99.68c | $-191.41 | $-0.51 | needs ~1914 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4253 | 226 | 217 | 0 | 99.63c | $+76.09 | $+0.35 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1685 | 1676 | 1654 | 115 | 92.82c | $-194.67 | $-0.13 | needs ~227 more bets with no loss |

