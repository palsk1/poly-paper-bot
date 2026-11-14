# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1995 coin-windows from 2026-11-10T10:30 to 2026-11-14T07:15 UTC (285 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **30 of 1995** windows. Reading the Kalshi book takes about 153 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1447 | 115 | 113 | 1 | 99.79c | $-8.73 | $-0.77 | needs ~3359 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1204 | 23 | 23 | 0 | 99.84c | $+0.13 | $+0.06 | needs ~4050 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1447 | 52 | 51 | 1 | 99.44c | $-7.20 | $-1.40 | needs ~664 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1732 | 388 | 386 | 7 | 98.88c | $-31.07 | $-0.81 | needs ~781 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1198 | 151 | 145 | 0 | 99.60c | $+4.20 | $+0.29 | needs ~645 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1712 | 94 | 93 | 0 | 99.52c | $+3.38 | $+0.37 | needs ~538 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 639 | 634 | 632 | 39 | 93.36c | $+3.63 | $+0.06 | needs ~138 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1447 | 115 | 111 | 1 | 99.79c | $-79.09 | $-0.71 | needs ~1954 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1204 | 23 | 21 | 0 | 99.85c | $+2.91 | $+0.14 | needs ~1658 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1447 | 52 | 47 | 1 | 99.44c | $-73.02 | $-1.49 | needs ~656 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1732 | 388 | 377 | 7 | 98.92c | $-315.82 | $-0.84 | needs ~778 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1198 | 151 | 140 | 0 | 99.60c | $+52.40 | $+0.37 | needs ~474 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1712 | 94 | 89 | 0 | 99.54c | $+38.60 | $+0.42 | needs ~453 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 639 | 634 | 627 | 39 | 93.49c | $-21.53 | $-0.04 | needs ~145 more bets with no loss |

