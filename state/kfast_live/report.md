# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1715 coin-windows from 2026-11-10T10:30 to 2026-11-13T18:45 UTC (245 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **24 of 1715** windows. Reading the Kalshi book takes about 177 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1235 | 94 | 93 | 1 | 99.79c | $-8.99 | $-0.96 | needs ~3504 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1019 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1235 | 39 | 38 | 1 | 99.42c | $-7.86 | $-2.05 | needs ~662 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1485 | 320 | 319 | 4 | 98.88c | $-7.93 | $-0.25 | needs ~475 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1010 | 124 | 120 | 0 | 99.67c | $+2.66 | $+0.22 | needs ~915 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1466 | 72 | 72 | 0 | 99.46c | $+3.03 | $+0.42 | needs ~474 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 551 | 547 | 546 | 31 | 93.24c | $+36.42 | $+0.71 | needs ~71 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1235 | 94 | 91 | 1 | 99.80c | $-83.20 | $-0.91 | needs ~2018 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1019 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1235 | 39 | 34 | 1 | 99.42c | $-79.65 | $-2.22 | needs ~651 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1485 | 320 | 311 | 4 | 98.93c | $-83.59 | $-0.27 | needs ~473 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1010 | 124 | 117 | 0 | 99.67c | $+35.39 | $+0.30 | needs ~644 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1466 | 72 | 69 | 0 | 99.49c | $+33.52 | $+0.47 | needs ~415 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 551 | 547 | 542 | 31 | 93.37c | $+310.02 | $+0.61 | needs ~78 more bets with no loss |

