# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 70 coin-windows from 2026-11-10T10:30 to 2026-11-10T12:45 UTC (10 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 70** windows. Reading the Kalshi book takes about 153 ms (slowest 1 in 10: 212 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 47 | 3 | 3 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 39 | 2 | 2 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 47 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.8c, 45 s left (z 2+) (main) | 58 | 10 | 10 | 0 | 99.46c | $+0.46 | $+0.46 | needs ~490 more bets with no loss |
| Buy now, 60 s left (z 4+) | 42 | 6 | 6 | 0 | 99.82c | $+0.05 | $+0.09 | needs ~2702 more bets with no loss |
| Buy now, 30 s left (z 4+) | 61 | 4 | 4 | 0 | 99.88c | $+0.01 | $+0.03 | needs ~5000 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 25 | 25 | 25 | 1 | 94.35c | $+3.15 | $+1.33 | needs ~48 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 47 | 3 | 3 | 0 | 99.90c | $+0.27 | $+0.09 | needs ~2555 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 39 | 2 | 2 | 0 | 99.90c | $+0.18 | $+0.09 | needs ~2556 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 47 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.8c, 45 s left (z 2+) (main) | 58 | 10 | 10 | 0 | 99.50c | $+4.66 | $+0.47 | needs ~483 more bets with no loss |
| Buy now, 60 s left (z 4+) | 42 | 6 | 6 | 0 | 99.82c | $+1.00 | $+0.17 | needs ~1374 more bets with no loss |
| Buy now, 30 s left (z 4+) | 61 | 4 | 4 | 0 | 99.88c | $+0.45 | $+0.11 | needs ~2042 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 25 | 25 | 24 | 1 | 94.58c | $+26.74 | $+1.14 | needs ~50 more bets with no loss |

