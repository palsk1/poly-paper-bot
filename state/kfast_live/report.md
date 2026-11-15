# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2485 coin-windows from 2026-11-10T10:30 to 2026-11-15T03:15 UTC (355 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **41 of 2485** windows. Reading the Kalshi book takes about 134 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1804 | 144 | 142 | 1 | 99.78c | $-8.34 | $-0.59 | needs ~3191 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1497 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1804 | 69 | 68 | 1 | 99.44c | $-6.29 | $-0.92 | needs ~649 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2149 | 482 | 479 | 7 | 98.98c | $-25.68 | $-0.54 | needs ~794 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1480 | 189 | 182 | 0 | 99.63c | $+4.65 | $+0.26 | needs ~713 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2124 | 115 | 113 | 0 | 99.54c | $+3.88 | $+0.34 | needs ~555 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 796 | 790 | 788 | 54 | 93.14c | $-32.38 | $-0.44 | needs ~210 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1804 | 144 | 140 | 1 | 99.79c | $-73.04 | $-0.52 | needs ~1879 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1497 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1804 | 69 | 63 | 1 | 99.44c | $-64.09 | $-0.98 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2149 | 482 | 466 | 7 | 99.01c | $-262.25 | $-0.56 | needs ~786 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1480 | 189 | 177 | 0 | 99.64c | $+60.05 | $+0.34 | needs ~499 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2124 | 115 | 108 | 0 | 99.56c | $+44.86 | $+0.40 | needs ~456 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 796 | 790 | 783 | 54 | 93.27c | $-394.73 | $-0.54 | needs ~220 more bets with no loss |

