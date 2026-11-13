# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1477 coin-windows from 2026-11-10T10:30 to 2026-11-13T07:45 UTC (211 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **18 of 1477** windows. Reading the Kalshi book takes about 159 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1067 | 84 | 84 | 1 | 99.79c | $-9.10 | $-1.09 | needs ~3564 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 881 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1067 | 36 | 35 | 1 | 99.42c | $-8.00 | $-2.26 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1287 | 290 | 289 | 4 | 98.91c | $-11.69 | $-0.41 | needs ~526 more bets with no loss |
| Buy now, 60 s left (z 4+) | 870 | 113 | 109 | 0 | 99.65c | $+2.56 | $+0.24 | needs ~868 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1270 | 68 | 68 | 0 | 99.45c | $+2.93 | $+0.43 | needs ~465 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 476 | 473 | 473 | 23 | 93.65c | $+51.07 | $+1.15 | needs ~36 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1067 | 84 | 82 | 1 | 99.80c | $-84.99 | $-1.04 | needs ~2046 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 881 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1067 | 36 | 32 | 1 | 99.42c | $-80.72 | $-2.39 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1287 | 290 | 283 | 4 | 98.95c | $-119.96 | $-0.42 | needs ~524 more bets with no loss |
| Buy now, 60 s left (z 4+) | 870 | 113 | 106 | 0 | 99.66c | $+33.53 | $+0.31 | needs ~622 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1270 | 68 | 65 | 0 | 99.48c | $+32.31 | $+0.48 | needs ~409 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 476 | 473 | 470 | 23 | 93.80c | $+464.34 | $+1.05 | needs ~43 more bets with no loss |

