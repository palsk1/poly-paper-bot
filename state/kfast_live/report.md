# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1428 coin-windows from 2026-11-10T10:30 to 2026-11-13T04:00 UTC (204 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **16 of 1428** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1043 | 78 | 78 | 1 | 99.79c | $-9.13 | $-1.17 | needs ~3427 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 870 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1043 | 33 | 32 | 1 | 99.41c | $-8.15 | $-2.52 | needs ~651 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1251 | 272 | 271 | 4 | 98.91c | $-13.34 | $-0.50 | needs ~541 more bets with no loss |
| Buy now, 60 s left (z 4+) | 860 | 102 | 98 | 0 | 99.63c | $+2.51 | $+0.26 | needs ~797 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1235 | 63 | 63 | 0 | 99.42c | $+2.90 | $+0.46 | needs ~436 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 445 | 442 | 442 | 22 | 93.58c | $+45.66 | $+1.10 | needs ~43 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1043 | 78 | 76 | 1 | 99.80c | $-85.80 | $-1.13 | needs ~2009 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 870 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1043 | 33 | 29 | 1 | 99.41c | $-82.22 | $-2.67 | needs ~643 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1251 | 272 | 265 | 4 | 98.95c | $-136.61 | $-0.52 | needs ~539 more bets with no loss |
| Buy now, 60 s left (z 4+) | 860 | 102 | 96 | 0 | 99.64c | $+32.18 | $+0.33 | needs ~591 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1235 | 63 | 61 | 0 | 99.45c | $+31.66 | $+0.51 | needs ~392 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 445 | 442 | 440 | 22 | 93.74c | $+409.82 | $+0.99 | needs ~50 more bets with no loss |

