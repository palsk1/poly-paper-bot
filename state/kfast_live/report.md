# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 35 coin-windows from 2026-11-10T10:30 to 2026-11-10T11:30 UTC (5 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 35** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 209 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 30 | 1 | 1 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 28 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.5c, 45 s left (z 4+) (main) | 30 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.8c, 45 s left (z 2+) (main) | 30 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Buy now, 60 s left (z 4+) | 27 | 1 | 1 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Buy now, 30 s left (z 4+) | 32 | 2 | 2 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 6 | 6 | 6 | 0 | 94.61c | $+2.98 | $+5.23 | needs ~40 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 30 | 1 | 1 | 0 | 99.90c | $+0.09 | $+0.09 | needs ~2557 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 28 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.5c, 45 s left (z 4+) (main) | 30 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Wait at 99.8c, 45 s left (z 2+) (main) | 30 | 0 | 0 | 0 | - | $0.00 | - | no bets yet |
| Buy now, 60 s left (z 4+) | 27 | 1 | 1 | 0 | 99.90c | $+0.09 | $+0.09 | needs ~2557 more bets with no loss |
| Buy now, 30 s left (z 4+) | 32 | 2 | 2 | 0 | 99.90c | $+0.18 | $+0.09 | needs ~2556 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 6 | 6 | 6 | 0 | 95.13c | $+27.31 | $+4.77 | needs ~44 more bets with no loss |

