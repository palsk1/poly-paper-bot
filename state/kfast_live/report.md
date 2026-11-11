# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 693 coin-windows from 2026-11-10T10:30 to 2026-11-11T16:15 UTC (99 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **5 of 693** windows. Reading the Kalshi book takes about 177 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 493 | 31 | 31 | 1 | 99.80c | $-9.69 | $-3.13 | needs ~3858 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 415 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 493 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 601 | 135 | 134 | 3 | 98.81c | $-15.55 | $-1.17 | needs ~486 more bets with no loss |
| Buy now, 60 s left (z 4+) | 416 | 49 | 49 | 0 | 99.57c | $+1.54 | $+0.32 | needs ~683 more bets with no loss |
| Buy now, 30 s left (z 4+) | 594 | 35 | 35 | 0 | 99.77c | $+0.47 | $+0.13 | needs ~1675 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 225 | 224 | 224 | 12 | 93.20c | $+23.01 | $+1.10 | needs ~52 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 493 | 31 | 31 | 1 | 99.82c | $-94.85 | $-3.06 | needs ~2308 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 415 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 493 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 601 | 135 | 130 | 3 | 98.84c | $-155.91 | $-1.19 | needs ~477 more bets with no loss |
| Buy now, 60 s left (z 4+) | 416 | 49 | 48 | 0 | 99.57c | $+18.98 | $+0.39 | needs ~536 more bets with no loss |
| Buy now, 30 s left (z 4+) | 594 | 35 | 35 | 0 | 99.77c | $+7.41 | $+0.21 | needs ~1051 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 225 | 224 | 223 | 12 | 93.39c | $+201.22 | $+0.96 | needs ~58 more bets with no loss |

