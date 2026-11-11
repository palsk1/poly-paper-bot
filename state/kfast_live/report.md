# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 455 coin-windows from 2026-11-10T10:30 to 2026-11-11T04:45 UTC (65 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **3 of 455** windows. Reading the Kalshi book takes about 158 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 324 | 24 | 24 | 0 | 99.80c | $+0.25 | $+0.10 | needs ~2186 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 278 | 8 | 8 | 0 | 99.88c | $+0.02 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 324 | 15 | 15 | 0 | 99.47c | $+0.78 | $+0.52 | needs ~427 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 401 | 98 | 97 | 1 | 98.93c | $-0.61 | $-0.06 | needs ~305 more bets with no loss |
| Buy now, 60 s left (z 4+) | 279 | 39 | 39 | 0 | 99.49c | $+1.55 | $+0.40 | needs ~539 more bets with no loss |
| Buy now, 30 s left (z 4+) | 394 | 25 | 25 | 0 | 99.78c | $+0.30 | $+0.12 | needs ~1887 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 149 | 148 | 148 | 6 | 93.79c | $+26.24 | $+1.88 | needs ~31 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 324 | 24 | 24 | 0 | 99.81c | $+4.19 | $+0.17 | needs ~1294 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 278 | 8 | 8 | 0 | 99.88c | $+0.90 | $+0.11 | needs ~2038 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 324 | 15 | 14 | 0 | 99.48c | $+7.36 | $+0.51 | needs ~435 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 401 | 98 | 94 | 1 | 98.96c | $-7.29 | $-0.08 | needs ~301 more bets with no loss |
| Buy now, 60 s left (z 4+) | 279 | 39 | 37 | 0 | 99.48c | $+18.32 | $+0.49 | needs ~437 more bets with no loss |
| Buy now, 30 s left (z 4+) | 394 | 25 | 25 | 0 | 99.78c | $+4.94 | $+0.20 | needs ~1139 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 149 | 148 | 147 | 6 | 93.96c | $+245.80 | $+1.76 | needs ~34 more bets with no loss |

