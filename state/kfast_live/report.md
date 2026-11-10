# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 105 coin-windows from 2026-11-10T10:30 to 2026-11-10T14:00 UTC (15 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 105** windows. Reading the Kalshi book takes about 152 ms (slowest 1 in 10: 205 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 74 | 5 | 5 | 0 | 99.88c | $+0.01 | $+0.02 | needs ~5000 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 60 | 3 | 3 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 74 | 1 | 1 | 0 | 99.50c | $+0.05 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 90 | 17 | 17 | 0 | 99.51c | $+0.71 | $+0.42 | needs ~534 more bets with no loss |
| Buy now, 60 s left (z 4+) | 61 | 9 | 9 | 0 | 99.79c | $+0.10 | $+0.11 | needs ~2042 more bets with no loss |
| Buy now, 30 s left (z 4+) | 91 | 6 | 6 | 0 | 99.87c | $+0.02 | $+0.03 | needs ~5000 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 34 | 34 | 34 | 2 | 93.80c | $-0.25 | $-0.08 | needs ~56 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 74 | 5 | 5 | 0 | 99.88c | $+0.54 | $+0.11 | needs ~2126 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 60 | 3 | 3 | 0 | 99.90c | $+0.27 | $+0.09 | needs ~2555 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 74 | 1 | 1 | 0 | 99.50c | $+0.50 | $+0.50 | needs ~459 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 90 | 17 | 17 | 0 | 99.56c | $+7.03 | $+0.42 | needs ~539 more bets with no loss |
| Buy now, 60 s left (z 4+) | 61 | 9 | 9 | 0 | 99.79c | $+1.73 | $+0.19 | needs ~1188 more bets with no loss |
| Buy now, 30 s left (z 4+) | 91 | 6 | 6 | 0 | 99.87c | $+0.72 | $+0.12 | needs ~1912 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 34 | 34 | 33 | 2 | 93.98c | $-7.12 | $-0.22 | needs ~58 more bets with no loss |

