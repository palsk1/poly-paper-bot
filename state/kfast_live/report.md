# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7252 coin-windows from 2026-11-10T10:30 to 2026-11-25T07:30 UTC (1036 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7252** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5125 | 388 | 377 | 2 | 99.62c | $-9.93 | $-0.26 | needs ~1608 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4194 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5125 | 186 | 180 | 3 | 99.13c | $-14.91 | $-0.82 | needs ~619 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6189 | 1389 | 1375 | 20 | 98.87c | $-59.27 | $-0.43 | needs ~1257 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4164 | 538 | 522 | 3 | 99.70c | $-19.74 | $-0.38 | needs ~2868 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6094 | 291 | 286 | 2 | 98.98c | $+5.88 | $+0.21 | needs ~296 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2408 | 2395 | 2382 | 170 | 92.83c | $-96.03 | $-0.43 | needs ~389 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5125 | 388 | 368 | 2 | 99.63c | $-72.38 | $-0.19 | needs ~1165 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4194 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5125 | 186 | 167 | 3 | 99.13c | $-153.70 | $-0.90 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6189 | 1389 | 1342 | 20 | 98.90c | $-595.19 | $-0.44 | needs ~1224 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4164 | 538 | 513 | 3 | 99.70c | $-158.85 | $-0.31 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6094 | 291 | 280 | 2 | 98.99c | $+75.34 | $+0.27 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2408 | 2395 | 2366 | 170 | 92.96c | $-1167.03 | $-0.53 | needs ~417 more bets with no loss |

