# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5285 coin-windows from 2026-11-10T10:30 to 2026-11-21T00:15 UTC (755 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **85 of 5285** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 236 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3770 | 299 | 289 | 2 | 99.66c | $-13.41 | $-0.46 | needs ~2037 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3090 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3770 | 147 | 143 | 3 | 99.22c | $-19.23 | $-1.34 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4526 | 1032 | 1024 | 16 | 98.90c | $-58.73 | $-0.58 | needs ~1241 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3069 | 397 | 384 | 3 | 99.68c | $-21.85 | $-0.57 | needs ~2760 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4459 | 227 | 224 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~596 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1743 | 1734 | 1724 | 117 | 92.70c | $+12.01 | $+0.07 | needs ~187 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3770 | 299 | 282 | 2 | 99.67c | $-112.72 | $-0.40 | needs ~1438 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3090 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3770 | 147 | 133 | 3 | 99.22c | $-195.24 | $-1.43 | needs ~729 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4526 | 1032 | 1002 | 16 | 98.94c | $-591.02 | $-0.59 | needs ~1220 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3069 | 397 | 376 | 3 | 99.69c | $-190.49 | $-0.50 | needs ~1920 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4459 | 227 | 218 | 0 | 99.63c | $+76.18 | $+0.34 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1743 | 1734 | 1711 | 117 | 92.84c | $-36.07 | $-0.02 | needs ~206 more bets with no loss |

