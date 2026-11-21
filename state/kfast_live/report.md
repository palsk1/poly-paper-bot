# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5460 coin-windows from 2026-11-10T10:30 to 2026-11-21T06:30 UTC (780 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **91 of 5460** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3884 | 302 | 292 | 2 | 99.66c | $-13.38 | $-0.46 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3185 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3884 | 151 | 147 | 3 | 99.23c | $-19.03 | $-1.29 | needs ~754 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4662 | 1054 | 1046 | 16 | 98.92c | $-57.98 | $-0.56 | needs ~1251 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3164 | 404 | 391 | 3 | 99.68c | $-21.82 | $-0.56 | needs ~2799 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4597 | 230 | 227 | 0 | 99.62c | $+6.26 | $+0.28 | needs ~604 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1804 | 1795 | 1785 | 123 | 92.67c | $-0.85 | $-0.01 | needs ~209 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3884 | 302 | 285 | 2 | 99.67c | $-112.18 | $-0.39 | needs ~1443 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3185 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3884 | 151 | 137 | 3 | 99.22c | $-193.24 | $-1.38 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4662 | 1054 | 1024 | 16 | 98.95c | $-582.80 | $-0.57 | needs ~1228 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3164 | 404 | 383 | 3 | 99.69c | $-189.59 | $-0.49 | needs ~1937 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4597 | 230 | 221 | 0 | 99.63c | $+76.45 | $+0.34 | needs ~448 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1804 | 1795 | 1772 | 123 | 92.81c | $-172.76 | $-0.10 | needs ~230 more bets with no loss |

