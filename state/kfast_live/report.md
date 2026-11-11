# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 420 coin-windows from 2026-11-10T10:30 to 2026-11-11T03:30 UTC (60 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 420** windows. Reading the Kalshi book takes about 170 ms (slowest 1 in 10: 254 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 298 | 20 | 20 | 0 | 99.81c | $+0.19 | $+0.10 | needs ~2403 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 260 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 298 | 12 | 12 | 0 | 99.46c | $+0.63 | $+0.53 | needs ~426 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 368 | 85 | 84 | 1 | 98.85c | $-1.22 | $-0.15 | needs ~289 more bets with no loss |
| Buy now, 60 s left (z 4+) | 261 | 32 | 32 | 0 | 99.45c | $+1.37 | $+0.43 | needs ~505 more bets with no loss |
| Buy now, 30 s left (z 4+) | 361 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 136 | 135 | 135 | 6 | 93.28c | $+25.19 | $+1.99 | needs ~30 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 298 | 20 | 20 | 0 | 99.82c | $+3.29 | $+0.16 | needs ~1379 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 260 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 298 | 12 | 12 | 0 | 99.48c | $+6.15 | $+0.52 | needs ~437 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 368 | 85 | 82 | 1 | 98.89c | $-13.64 | $-0.17 | needs ~289 more bets with no loss |
| Buy now, 60 s left (z 4+) | 261 | 32 | 31 | 0 | 99.45c | $+16.06 | $+0.52 | needs ~416 more bets with no loss |
| Buy now, 30 s left (z 4+) | 361 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 136 | 135 | 134 | 6 | 93.47c | $+234.78 | $+1.86 | needs ~33 more bets with no loss |

