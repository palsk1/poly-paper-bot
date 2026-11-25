# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7126 coin-windows from 2026-11-10T10:30 to 2026-11-25T01:30 UTC (1018 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **119 of 7126** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5039 | 386 | 375 | 2 | 99.62c | $-9.93 | $-0.27 | needs ~1599 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4121 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5039 | 181 | 175 | 3 | 99.12c | $-15.16 | $-0.86 | needs ~615 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6082 | 1361 | 1347 | 20 | 98.86c | $-60.90 | $-0.46 | needs ~1261 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4089 | 535 | 519 | 3 | 99.70c | $-19.83 | $-0.38 | needs ~2882 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5991 | 289 | 284 | 2 | 98.97c | $+5.88 | $+0.21 | needs ~294 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2368 | 2355 | 2342 | 164 | 92.89c | $-76.48 | $-0.35 | needs ~358 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5039 | 386 | 366 | 2 | 99.63c | $-72.56 | $-0.20 | needs ~1161 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4121 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5039 | 181 | 163 | 3 | 99.11c | $-156.00 | $-0.94 | needs ~598 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6082 | 1361 | 1315 | 20 | 98.89c | $-611.34 | $-0.46 | needs ~1230 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4089 | 535 | 510 | 3 | 99.70c | $-159.95 | $-0.31 | needs ~1917 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5991 | 289 | 278 | 2 | 98.99c | $+75.16 | $+0.27 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2368 | 2355 | 2326 | 164 | 93.02c | $-965.76 | $-0.44 | needs ~386 more bets with no loss |

