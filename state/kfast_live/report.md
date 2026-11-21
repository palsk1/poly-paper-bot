# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5334 coin-windows from 2026-11-10T10:30 to 2026-11-21T02:00 UTC (762 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **88 of 5334** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3797 | 302 | 292 | 2 | 99.66c | $-13.38 | $-0.46 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3111 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3797 | 149 | 145 | 3 | 99.23c | $-19.13 | $-1.31 | needs ~752 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4563 | 1044 | 1036 | 16 | 98.91c | $-58.26 | $-0.57 | needs ~1245 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3088 | 399 | 386 | 3 | 99.68c | $-21.84 | $-0.57 | needs ~2771 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4495 | 227 | 224 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~596 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1766 | 1757 | 1747 | 120 | 92.69c | $+0.85 | $+0.01 | needs ~205 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3797 | 302 | 285 | 2 | 99.67c | $-112.18 | $-0.39 | needs ~1443 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3111 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3797 | 149 | 135 | 3 | 99.22c | $-194.24 | $-1.40 | needs ~731 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4563 | 1044 | 1014 | 16 | 98.94c | $-585.75 | $-0.58 | needs ~1223 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3088 | 399 | 378 | 3 | 99.69c | $-190.22 | $-0.50 | needs ~1925 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4495 | 227 | 218 | 0 | 99.63c | $+76.18 | $+0.34 | needs ~444 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1766 | 1757 | 1734 | 120 | 92.82c | $-153.18 | $-0.09 | needs ~225 more bets with no loss |

