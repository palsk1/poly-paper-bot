# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5439 coin-windows from 2026-11-10T10:30 to 2026-11-21T05:45 UTC (777 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **90 of 5439** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3870 | 302 | 292 | 2 | 99.66c | $-13.38 | $-0.46 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3173 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3870 | 151 | 147 | 3 | 99.23c | $-19.03 | $-1.29 | needs ~754 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4647 | 1051 | 1043 | 16 | 98.92c | $-58.04 | $-0.56 | needs ~1249 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3150 | 401 | 388 | 3 | 99.68c | $-21.83 | $-0.56 | needs ~2781 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4582 | 230 | 227 | 0 | 99.62c | $+6.26 | $+0.28 | needs ~604 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1797 | 1788 | 1778 | 122 | 92.69c | $+0.84 | $+0.01 | needs ~207 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3870 | 302 | 285 | 2 | 99.67c | $-112.18 | $-0.39 | needs ~1443 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3173 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3870 | 151 | 137 | 3 | 99.22c | $-193.24 | $-1.38 | needs ~733 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4647 | 1051 | 1021 | 16 | 98.95c | $-583.40 | $-0.57 | needs ~1226 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3150 | 401 | 380 | 3 | 99.69c | $-189.95 | $-0.50 | needs ~1929 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4582 | 230 | 221 | 0 | 99.63c | $+76.45 | $+0.34 | needs ~448 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1797 | 1788 | 1765 | 122 | 92.83c | $-155.33 | $-0.09 | needs ~227 more bets with no loss |

