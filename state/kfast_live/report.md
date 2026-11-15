# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2485 coin-windows from 2026-11-10T10:30 to 2026-11-15T06:15 UTC (355 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **44 of 2485** windows. Reading the Kalshi book takes about 135 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1786 | 152 | 149 | 1 | 99.78c | $-8.29 | $-0.56 | needs ~3255 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1474 | 31 | 30 | 0 | 99.85c | $+0.15 | $+0.05 | needs ~4568 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1786 | 71 | 70 | 1 | 99.44c | $-6.19 | $-0.88 | needs ~649 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2137 | 496 | 493 | 9 | 98.97c | $-43.99 | $-0.90 | needs ~1031 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1461 | 191 | 184 | 0 | 99.63c | $+4.82 | $+0.26 | needs ~689 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2112 | 122 | 120 | 0 | 99.56c | $+3.91 | $+0.33 | needs ~585 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 822 | 816 | 813 | 56 | 93.09c | $-32.39 | $-0.43 | needs ~210 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1786 | 152 | 146 | 1 | 99.79c | $-71.99 | $-0.49 | needs ~1889 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1474 | 31 | 27 | 0 | 99.85c | $+3.78 | $+0.13 | needs ~1677 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1786 | 71 | 66 | 1 | 99.44c | $-62.86 | $-0.93 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2137 | 496 | 482 | 9 | 99.00c | $-444.97 | $-0.92 | needs ~1025 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1461 | 191 | 179 | 0 | 99.63c | $+61.71 | $+0.34 | needs ~485 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2112 | 122 | 115 | 0 | 99.58c | $+45.68 | $+0.39 | needs ~474 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 822 | 816 | 807 | 56 | 93.22c | $-397.83 | $-0.52 | needs ~220 more bets with no loss |

