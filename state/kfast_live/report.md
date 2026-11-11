# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 469 coin-windows from 2026-11-10T10:30 to 2026-11-11T05:15 UTC (67 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 469** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 334 | 24 | 24 | 0 | 99.80c | $+0.25 | $+0.10 | needs ~2186 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 287 | 8 | 8 | 0 | 99.88c | $+0.02 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 334 | 15 | 15 | 0 | 99.47c | $+0.78 | $+0.52 | needs ~427 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 413 | 100 | 99 | 1 | 98.94c | $-0.49 | $-0.05 | needs ~306 more bets with no loss |
| Buy now, 60 s left (z 4+) | 288 | 40 | 40 | 0 | 99.48c | $+1.60 | $+0.40 | needs ~535 more bets with no loss |
| Buy now, 30 s left (z 4+) | 405 | 25 | 25 | 0 | 99.78c | $+0.30 | $+0.12 | needs ~1887 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 154 | 152 | 152 | 6 | 93.91c | $+26.78 | $+1.87 | needs ~31 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 334 | 24 | 24 | 0 | 99.81c | $+4.19 | $+0.17 | needs ~1294 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 287 | 8 | 8 | 0 | 99.88c | $+0.90 | $+0.11 | needs ~2038 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 334 | 15 | 14 | 0 | 99.48c | $+7.36 | $+0.51 | needs ~435 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 413 | 100 | 96 | 1 | 98.97c | $-5.99 | $-0.06 | needs ~302 more bets with no loss |
| Buy now, 60 s left (z 4+) | 288 | 40 | 38 | 0 | 99.48c | $+18.86 | $+0.49 | needs ~434 more bets with no loss |
| Buy now, 30 s left (z 4+) | 405 | 25 | 25 | 0 | 99.78c | $+4.94 | $+0.20 | needs ~1139 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 154 | 152 | 151 | 6 | 94.08c | $+251.21 | $+1.75 | needs ~34 more bets with no loss |

