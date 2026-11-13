# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1407 coin-windows from 2026-11-10T10:30 to 2026-11-13T05:15 UTC (201 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **16 of 1407** windows. Reading the Kalshi book takes about 152 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1016 | 81 | 81 | 1 | 99.79c | $-9.13 | $-1.13 | needs ~3559 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 839 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1016 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1225 | 276 | 275 | 4 | 98.92c | $-13.17 | $-0.48 | needs ~544 more bets with no loss |
| Buy now, 60 s left (z 4+) | 829 | 104 | 100 | 0 | 99.63c | $+2.53 | $+0.25 | needs ~806 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1210 | 63 | 63 | 0 | 99.42c | $+2.90 | $+0.46 | needs ~436 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 456 | 453 | 453 | 23 | 93.57c | $+42.62 | $+1.00 | needs ~50 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1016 | 81 | 79 | 1 | 99.80c | $-85.53 | $-1.08 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 839 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1016 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1225 | 276 | 269 | 4 | 98.96c | $-134.72 | $-0.50 | needs ~541 more bets with no loss |
| Buy now, 60 s left (z 4+) | 829 | 104 | 97 | 0 | 99.64c | $+32.45 | $+0.33 | needs ~592 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1210 | 63 | 61 | 0 | 99.45c | $+31.66 | $+0.51 | needs ~392 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 456 | 453 | 451 | 23 | 93.73c | $+380.28 | $+0.89 | needs ~57 more bets with no loss |

