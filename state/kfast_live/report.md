# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5250 coin-windows from 2026-11-10T10:30 to 2026-11-20T23:00 UTC (750 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **85 of 5250** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3747 | 295 | 285 | 2 | 99.66c | $-13.50 | $-0.47 | needs ~2041 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3072 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3747 | 145 | 141 | 3 | 99.22c | $-19.37 | $-1.37 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4496 | 1025 | 1017 | 16 | 98.90c | $-58.97 | $-0.58 | needs ~1238 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3051 | 395 | 382 | 3 | 99.68c | $-21.89 | $-0.57 | needs ~2762 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4429 | 227 | 224 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~596 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1729 | 1720 | 1710 | 116 | 92.69c | $+15.09 | $+0.09 | needs ~181 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3747 | 295 | 278 | 2 | 99.67c | $-113.88 | $-0.41 | needs ~1441 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3072 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3747 | 145 | 131 | 3 | 99.21c | $-196.63 | $-1.46 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4496 | 1025 | 995 | 16 | 98.93c | $-593.61 | $-0.60 | needs ~1217 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3051 | 395 | 374 | 3 | 99.69c | $-190.98 | $-0.51 | needs ~1920 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4429 | 227 | 218 | 0 | 99.63c | $+76.18 | $+0.34 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1729 | 1720 | 1697 | 116 | 92.82c | $-5.91 | $-0.00 | needs ~200 more bets with no loss |

