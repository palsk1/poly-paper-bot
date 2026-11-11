# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 798 coin-windows from 2026-11-10T10:30 to 2026-11-11T21:45 UTC (114 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **6 of 798** windows. Reading the Kalshi book takes about 159 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 569 | 35 | 35 | 1 | 99.80c | $-9.65 | $-2.76 | needs ~3906 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 476 | 10 | 10 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 569 | 21 | 21 | 1 | 99.47c | $-8.93 | $-4.27 | needs ~741 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 691 | 153 | 152 | 4 | 98.76c | $-22.92 | $-1.52 | needs ~560 more bets with no loss |
| Buy now, 60 s left (z 4+) | 474 | 54 | 54 | 0 | 99.53c | $+1.93 | $+0.36 | needs ~589 more bets with no loss |
| Buy now, 30 s left (z 4+) | 683 | 39 | 39 | 0 | 99.73c | $+0.65 | $+0.17 | needs ~1340 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 255 | 254 | 254 | 16 | 93.23c | $+1.19 | $+0.05 | needs ~97 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 569 | 35 | 35 | 1 | 99.82c | $-94.28 | $-2.70 | needs ~2343 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 476 | 10 | 10 | 0 | 99.90c | $+0.92 | $+0.09 | needs ~2481 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 569 | 21 | 20 | 1 | 99.48c | $-89.72 | $-4.47 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 691 | 153 | 147 | 4 | 98.79c | $-230.37 | $-1.56 | needs ~550 more bets with no loss |
| Buy now, 60 s left (z 4+) | 474 | 54 | 53 | 0 | 99.53c | $+23.17 | $+0.44 | needs ~475 more bets with no loss |
| Buy now, 30 s left (z 4+) | 683 | 39 | 39 | 0 | 99.73c | $+9.46 | $+0.24 | needs ~909 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 255 | 254 | 253 | 16 | 93.42c | $-18.83 | $-0.08 | needs ~104 more bets with no loss |

