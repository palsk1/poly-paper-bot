# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7147 coin-windows from 2026-11-10T10:30 to 2026-11-25T02:15 UTC (1021 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7147** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5054 | 387 | 376 | 2 | 99.62c | $-9.93 | $-0.26 | needs ~1604 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4133 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5054 | 182 | 176 | 3 | 99.12c | $-15.11 | $-0.85 | needs ~616 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6098 | 1364 | 1350 | 20 | 98.86c | $-60.84 | $-0.45 | needs ~1263 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4102 | 535 | 519 | 3 | 99.70c | $-19.83 | $-0.38 | needs ~2882 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6007 | 289 | 284 | 2 | 98.97c | $+5.88 | $+0.21 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2375 | 2362 | 2349 | 166 | 92.86c | $-84.75 | $-0.39 | needs ~371 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5054 | 387 | 367 | 2 | 99.63c | $-72.47 | $-0.20 | needs ~1163 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4133 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5054 | 182 | 164 | 3 | 99.12c | $-155.50 | $-0.93 | needs ~599 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6098 | 1364 | 1318 | 20 | 98.89c | $-610.74 | $-0.46 | needs ~1231 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4102 | 535 | 510 | 3 | 99.70c | $-159.95 | $-0.31 | needs ~1917 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6007 | 289 | 278 | 2 | 98.99c | $+75.16 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2375 | 2362 | 2333 | 166 | 92.99c | $-1051.72 | $-0.48 | needs ~398 more bets with no loss |

