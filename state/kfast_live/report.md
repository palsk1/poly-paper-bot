# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3927 coin-windows from 2026-11-10T10:30 to 2026-11-18T04:30 UTC (561 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3927** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2827 | 237 | 230 | 2 | 99.64c | $-14.17 | $-0.62 | needs ~1865 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2333 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2827 | 120 | 116 | 3 | 99.18c | $-20.76 | $-1.78 | needs ~730 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3378 | 809 | 802 | 13 | 98.91c | $-51.02 | $-0.64 | needs ~1120 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2332 | 314 | 305 | 3 | 99.66c | $-22.93 | $-0.75 | needs ~2569 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3326 | 183 | 180 | 0 | 99.62c | $+4.97 | $+0.28 | needs ~651 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1296 | 1287 | 1280 | 91 | 92.83c | $-47.24 | $-0.40 | needs ~257 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2827 | 237 | 226 | 2 | 99.64c | $-124.92 | $-0.55 | needs ~1375 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2333 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2827 | 120 | 109 | 3 | 99.17c | $-209.78 | $-1.88 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3378 | 809 | 786 | 13 | 98.95c | $-515.71 | $-0.66 | needs ~1107 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2332 | 314 | 297 | 3 | 99.66c | $-207.37 | $-0.69 | needs ~1855 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3326 | 183 | 175 | 0 | 99.63c | $+60.42 | $+0.34 | needs ~496 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1296 | 1287 | 1271 | 91 | 92.96c | $-586.35 | $-0.49 | needs ~273 more bets with no loss |

