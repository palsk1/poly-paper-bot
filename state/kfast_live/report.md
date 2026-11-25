# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7182 coin-windows from 2026-11-10T10:30 to 2026-11-25T05:00 UTC (1026 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7182** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5077 | 387 | 376 | 2 | 99.62c | $-9.93 | $-0.26 | needs ~1604 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4154 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5077 | 183 | 177 | 3 | 99.13c | $-15.06 | $-0.85 | needs ~617 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6127 | 1372 | 1358 | 20 | 98.86c | $-60.21 | $-0.45 | needs ~1259 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4121 | 537 | 521 | 3 | 99.70c | $-19.75 | $-0.38 | needs ~2866 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6034 | 289 | 284 | 2 | 98.97c | $+5.88 | $+0.21 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2387 | 2374 | 2361 | 168 | 92.85c | $-93.09 | $-0.42 | needs ~383 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5077 | 387 | 367 | 2 | 99.63c | $-72.47 | $-0.20 | needs ~1163 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4154 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5077 | 183 | 165 | 3 | 99.12c | $-155.00 | $-0.92 | needs ~600 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6127 | 1372 | 1326 | 20 | 98.89c | $-604.59 | $-0.45 | needs ~1227 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4121 | 537 | 512 | 3 | 99.70c | $-159.03 | $-0.31 | needs ~1909 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6034 | 289 | 278 | 2 | 98.99c | $+75.16 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2387 | 2374 | 2345 | 168 | 92.98c | $-1135.97 | $-0.52 | needs ~412 more bets with no loss |

