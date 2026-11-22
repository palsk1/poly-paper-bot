# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6223 coin-windows from 2026-11-10T10:30 to 2026-11-22T20:45 UTC (889 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **100 of 6223** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4397 | 347 | 337 | 2 | 99.60c | $-10.29 | $-0.31 | needs ~1502 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3597 | 61 | 60 | 0 | 99.78c | $+0.73 | $+0.12 | needs ~1823 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4397 | 167 | 162 | 3 | 99.09c | $-15.83 | $-0.97 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5310 | 1210 | 1197 | 16 | 98.87c | $-37.84 | $-0.32 | needs ~993 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3573 | 477 | 462 | 3 | 99.68c | $-20.21 | $-0.44 | needs ~2684 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5238 | 261 | 258 | 0 | 99.55c | $+8.77 | $+0.34 | needs ~416 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2087 | 2074 | 2062 | 136 | 92.96c | $+3.39 | $+0.02 | needs ~221 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4397 | 347 | 329 | 2 | 99.61c | $-79.02 | $-0.24 | needs ~1117 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3597 | 61 | 57 | 0 | 99.79c | $+11.26 | $+0.19 | needs ~1125 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4397 | 167 | 152 | 3 | 99.09c | $-162.09 | $-1.04 | needs ~590 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5310 | 1210 | 1171 | 16 | 98.90c | $-381.37 | $-0.33 | needs ~970 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3573 | 477 | 453 | 3 | 99.69c | $-168.54 | $-0.37 | needs ~1846 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5238 | 261 | 252 | 0 | 99.56c | $+103.64 | $+0.41 | needs ~308 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2087 | 2074 | 2048 | 136 | 93.09c | $-144.89 | $-0.08 | needs ~245 more bets with no loss |

