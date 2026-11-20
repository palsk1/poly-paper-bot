# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5180 coin-windows from 2026-11-10T10:30 to 2026-11-20T20:30 UTC (740 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **84 of 5180** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3697 | 294 | 284 | 2 | 99.66c | $-13.50 | $-0.48 | needs ~2034 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3028 | 51 | 50 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2547 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3697 | 145 | 141 | 3 | 99.22c | $-19.37 | $-1.37 | needs ~751 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4435 | 1017 | 1009 | 16 | 98.89c | $-59.18 | $-0.59 | needs ~1233 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3009 | 393 | 380 | 3 | 99.68c | $-21.89 | $-0.58 | needs ~2747 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4367 | 227 | 224 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~596 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1712 | 1703 | 1693 | 116 | 92.69c | $+3.26 | $+0.02 | needs ~198 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3697 | 294 | 277 | 2 | 99.67c | $-113.97 | $-0.41 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3028 | 51 | 47 | 0 | 99.82c | $+7.84 | $+0.16 | needs ~1359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3697 | 145 | 131 | 3 | 99.21c | $-196.63 | $-1.46 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4435 | 1017 | 987 | 16 | 98.93c | $-596.04 | $-0.60 | needs ~1212 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3009 | 393 | 372 | 3 | 99.68c | $-191.16 | $-0.51 | needs ~1914 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4367 | 227 | 218 | 0 | 99.63c | $+76.18 | $+0.34 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1712 | 1703 | 1680 | 116 | 92.82c | $-123.18 | $-0.08 | needs ~217 more bets with no loss |

