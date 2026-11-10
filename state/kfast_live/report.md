# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 154 coin-windows from 2026-11-10T10:30 to 2026-11-10T15:45 UTC (22 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 154** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 203 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 113 | 7 | 7 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 93 | 3 | 3 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 113 | 1 | 1 | 0 | 99.50c | $+0.05 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 135 | 24 | 24 | 0 | 99.50c | $+1.02 | $+0.43 | needs ~517 more bets with no loss |
| Buy now, 60 s left (z 4+) | 94 | 9 | 9 | 0 | 99.79c | $+0.10 | $+0.11 | needs ~2042 more bets with no loss |
| Buy now, 30 s left (z 4+) | 137 | 9 | 9 | 0 | 99.86c | $+0.04 | $+0.04 | needs ~5000 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 46 | 46 | 46 | 2 | 94.77c | $+2.50 | $+0.57 | needs ~62 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 113 | 7 | 7 | 0 | 99.89c | $+0.72 | $+0.10 | needs ~2231 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 93 | 3 | 3 | 0 | 99.90c | $+0.27 | $+0.09 | needs ~2555 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 113 | 1 | 1 | 0 | 99.50c | $+0.50 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 135 | 24 | 24 | 0 | 99.55c | $+9.96 | $+0.42 | needs ~530 more bets with no loss |
| Buy now, 60 s left (z 4+) | 94 | 9 | 9 | 0 | 99.79c | $+1.73 | $+0.19 | needs ~1188 more bets with no loss |
| Buy now, 30 s left (z 4+) | 137 | 9 | 9 | 0 | 99.86c | $+1.17 | $+0.13 | needs ~1762 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 46 | 46 | 45 | 2 | 94.91c | $+20.52 | $+0.47 | needs ~63 more bets with no loss |

