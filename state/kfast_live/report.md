# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1785 coin-windows from 2026-11-10T10:30 to 2026-11-13T21:15 UTC (255 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **25 of 1785** windows. Reading the Kalshi book takes about 172 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1277 | 101 | 100 | 1 | 99.79c | $-8.90 | $-0.89 | needs ~3450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1051 | 20 | 20 | 0 | 99.88c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1277 | 42 | 41 | 1 | 99.43c | $-7.72 | $-1.87 | needs ~667 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1542 | 341 | 340 | 4 | 98.90c | $-6.41 | $-0.19 | needs ~468 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1045 | 131 | 126 | 0 | 99.67c | $+2.81 | $+0.22 | needs ~903 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1524 | 80 | 80 | 0 | 99.50c | $+3.10 | $+0.39 | needs ~515 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 585 | 581 | 580 | 32 | 93.38c | $+40.01 | $+0.74 | needs ~69 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1277 | 101 | 98 | 1 | 99.80c | $-81.76 | $-0.83 | needs ~1994 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1051 | 20 | 18 | 0 | 99.88c | $+1.97 | $+0.11 | needs ~2113 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1277 | 42 | 37 | 1 | 99.43c | $-78.19 | $-2.01 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1542 | 341 | 332 | 4 | 98.94c | $-68.66 | $-0.21 | needs ~466 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1045 | 131 | 123 | 0 | 99.67c | $+37.31 | $+0.30 | needs ~635 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1524 | 80 | 77 | 0 | 99.52c | $+34.73 | $+0.44 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 585 | 581 | 576 | 32 | 93.51c | $+344.90 | $+0.64 | needs ~76 more bets with no loss |

