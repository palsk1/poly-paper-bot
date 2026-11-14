# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1855 coin-windows from 2026-11-10T10:30 to 2026-11-14T00:30 UTC (265 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **28 of 1855** windows. Reading the Kalshi book takes about 165 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1331 | 103 | 102 | 1 | 99.79c | $-8.89 | $-0.87 | needs ~3486 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1101 | 21 | 21 | 0 | 99.87c | $+0.06 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1331 | 43 | 42 | 1 | 99.43c | $-7.67 | $-1.81 | needs ~667 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1601 | 349 | 347 | 5 | 98.90c | $-15.73 | $-0.46 | needs ~592 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1094 | 134 | 128 | 0 | 99.67c | $+2.83 | $+0.22 | needs ~909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1585 | 82 | 82 | 0 | 99.50c | $+3.19 | $+0.39 | needs ~510 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 602 | 598 | 597 | 36 | 93.27c | $+16.77 | $+0.30 | needs ~111 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1331 | 103 | 100 | 1 | 99.80c | $-81.49 | $-0.81 | needs ~2003 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1101 | 21 | 19 | 0 | 99.88c | $+2.15 | $+0.11 | needs ~2041 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1331 | 43 | 38 | 1 | 99.43c | $-77.69 | $-1.95 | needs ~656 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1601 | 349 | 339 | 5 | 98.95c | $-162.02 | $-0.48 | needs ~589 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1094 | 134 | 125 | 0 | 99.67c | $+37.75 | $+0.30 | needs ~635 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1585 | 82 | 79 | 0 | 99.52c | $+35.75 | $+0.44 | needs ~439 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 602 | 598 | 592 | 36 | 93.40c | $+111.60 | $+0.20 | needs ~118 more bets with no loss |

