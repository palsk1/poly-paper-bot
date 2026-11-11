# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 833 coin-windows from 2026-11-10T10:30 to 2026-11-11T23:00 UTC (119 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **6 of 833** windows. Reading the Kalshi book takes about 153 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 602 | 37 | 37 | 1 | 99.72c | $-9.34 | $-2.53 | needs ~2158 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 505 | 10 | 10 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 602 | 23 | 23 | 1 | 99.37c | $-8.62 | $-3.77 | needs ~624 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 725 | 156 | 155 | 4 | 98.76c | $-22.59 | $-1.47 | needs ~557 more bets with no loss |
| Buy now, 60 s left (z 4+) | 503 | 54 | 54 | 0 | 99.53c | $+1.93 | $+0.36 | needs ~589 more bets with no loss |
| Buy now, 30 s left (z 4+) | 717 | 39 | 39 | 0 | 99.73c | $+0.65 | $+0.17 | needs ~1340 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 259 | 258 | 258 | 16 | 93.23c | $+3.86 | $+0.16 | needs ~93 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 602 | 37 | 37 | 1 | 99.74c | $-91.12 | $-2.47 | needs ~1582 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 505 | 10 | 10 | 0 | 99.90c | $+0.92 | $+0.09 | needs ~2481 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 602 | 23 | 22 | 1 | 99.38c | $-86.56 | $-3.93 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 725 | 156 | 150 | 4 | 98.79c | $-227.01 | $-1.51 | needs ~547 more bets with no loss |
| Buy now, 60 s left (z 4+) | 503 | 54 | 53 | 0 | 99.53c | $+23.17 | $+0.44 | needs ~475 more bets with no loss |
| Buy now, 30 s left (z 4+) | 717 | 39 | 39 | 0 | 99.73c | $+9.46 | $+0.24 | needs ~909 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 259 | 258 | 257 | 16 | 93.41c | $+7.37 | $+0.03 | needs ~99 more bets with no loss |

