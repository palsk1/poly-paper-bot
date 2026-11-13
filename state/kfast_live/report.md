# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1526 coin-windows from 2026-11-10T10:30 to 2026-11-13T09:30 UTC (218 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **20 of 1526** windows. Reading the Kalshi book takes about 164 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1099 | 87 | 87 | 1 | 99.79c | $-9.03 | $-1.04 | needs ~3417 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 908 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1099 | 38 | 37 | 1 | 99.42c | $-7.91 | $-2.12 | needs ~661 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1326 | 298 | 297 | 4 | 98.92c | $-11.08 | $-0.38 | needs ~523 more bets with no loss |
| Buy now, 60 s left (z 4+) | 898 | 115 | 111 | 0 | 99.66c | $+2.57 | $+0.23 | needs ~880 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1309 | 68 | 68 | 0 | 99.45c | $+2.93 | $+0.43 | needs ~465 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 496 | 492 | 492 | 24 | 93.64c | $+52.91 | $+1.14 | needs ~35 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1099 | 87 | 85 | 1 | 99.80c | $-84.18 | $-0.99 | needs ~2008 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 908 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1099 | 38 | 34 | 1 | 99.42c | $-79.76 | $-2.23 | needs ~652 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1326 | 298 | 291 | 4 | 98.96c | $-114.28 | $-0.39 | needs ~522 more bets with no loss |
| Buy now, 60 s left (z 4+) | 898 | 115 | 108 | 0 | 99.66c | $+33.80 | $+0.31 | needs ~628 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1309 | 68 | 65 | 0 | 99.48c | $+32.31 | $+0.48 | needs ~409 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 496 | 492 | 489 | 24 | 93.79c | $+480.04 | $+1.04 | needs ~42 more bets with no loss |

