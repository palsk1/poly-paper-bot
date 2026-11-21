# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5488 coin-windows from 2026-11-10T10:30 to 2026-11-21T09:15 UTC (784 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **91 of 5488** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3899 | 303 | 293 | 2 | 99.67c | $-13.38 | $-0.46 | needs ~2055 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3197 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3899 | 151 | 147 | 3 | 99.23c | $-19.03 | $-1.29 | needs ~754 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4684 | 1060 | 1052 | 16 | 98.92c | $-57.83 | $-0.55 | needs ~1255 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3177 | 405 | 392 | 3 | 99.68c | $-21.82 | $-0.56 | needs ~2806 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4621 | 231 | 228 | 0 | 99.62c | $+6.27 | $+0.28 | needs ~606 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1818 | 1809 | 1799 | 123 | 92.71c | $+2.08 | $+0.01 | needs ~206 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3899 | 303 | 286 | 2 | 99.67c | $-112.09 | $-0.39 | needs ~1446 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3197 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3899 | 151 | 137 | 3 | 99.22c | $-193.24 | $-1.38 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4684 | 1060 | 1029 | 16 | 98.95c | $-581.07 | $-0.56 | needs ~1230 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3177 | 405 | 384 | 3 | 99.69c | $-189.50 | $-0.49 | needs ~1940 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4621 | 231 | 222 | 0 | 99.63c | $+76.63 | $+0.34 | needs ~448 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1818 | 1809 | 1786 | 123 | 92.85c | $-143.02 | $-0.09 | needs ~227 more bets with no loss |

