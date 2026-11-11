# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 420 coin-windows from 2026-11-10T10:30 to 2026-11-11T06:30 UTC (60 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 420** windows. Reading the Kalshi book takes about 191 ms (slowest 1 in 10: 254 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 304 | 20 | 20 | 0 | 99.81c | $+0.19 | $+0.10 | needs ~2403 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 259 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 304 | 12 | 12 | 0 | 99.46c | $+0.63 | $+0.53 | needs ~426 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 372 | 87 | 86 | 1 | 98.88c | $-1.26 | $-0.15 | needs ~297 more bets with no loss |
| Buy now, 60 s left (z 4+) | 263 | 37 | 37 | 0 | 99.49c | $+1.44 | $+0.39 | needs ~554 more bets with no loss |
| Buy now, 30 s left (z 4+) | 366 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 131 | 130 | 130 | 6 | 93.76c | $+16.18 | $+1.32 | needs ~48 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 304 | 20 | 20 | 0 | 99.82c | $+3.29 | $+0.16 | needs ~1379 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 259 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 304 | 12 | 12 | 0 | 99.48c | $+6.15 | $+0.52 | needs ~437 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 372 | 87 | 83 | 1 | 98.93c | $-14.08 | $-0.17 | needs ~297 more bets with no loss |
| Buy now, 60 s left (z 4+) | 263 | 37 | 36 | 0 | 99.49c | $+17.04 | $+0.47 | needs ~453 more bets with no loss |
| Buy now, 30 s left (z 4+) | 366 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 131 | 130 | 129 | 6 | 93.95c | $+144.92 | $+1.18 | needs ~52 more bets with no loss |

