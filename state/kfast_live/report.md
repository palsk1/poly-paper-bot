# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6118 coin-windows from 2026-11-10T10:30 to 2026-11-22T14:30 UTC (874 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 6118** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4328 | 334 | 324 | 2 | 99.67c | $-12.78 | $-0.39 | needs ~2056 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3546 | 58 | 57 | 0 | 99.79c | $+0.62 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4328 | 163 | 158 | 3 | 99.24c | $-18.31 | $-1.15 | needs ~750 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5221 | 1183 | 1171 | 16 | 98.88c | $-41.83 | $-0.36 | needs ~1045 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3523 | 463 | 448 | 3 | 99.68c | $-20.63 | $-0.46 | needs ~2740 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5149 | 255 | 252 | 0 | 99.57c | $+8.13 | $+0.32 | needs ~458 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2044 | 2032 | 2021 | 133 | 92.92c | $+14.85 | $+0.08 | needs ~201 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4328 | 334 | 317 | 2 | 99.68c | $-104.06 | $-0.33 | needs ~1441 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3546 | 58 | 54 | 0 | 99.80c | $+9.98 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4328 | 163 | 148 | 3 | 99.23c | $-186.20 | $-1.23 | needs ~731 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5221 | 1183 | 1145 | 16 | 98.91c | $-421.38 | $-0.37 | needs ~1021 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3523 | 463 | 440 | 3 | 99.69c | $-173.72 | $-0.39 | needs ~1885 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5149 | 255 | 246 | 0 | 99.58c | $+96.96 | $+0.39 | needs ~339 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2044 | 2032 | 2008 | 133 | 93.05c | $-28.83 | $-0.02 | needs ~224 more bets with no loss |

