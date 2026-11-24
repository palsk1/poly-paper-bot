# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7056 coin-windows from 2026-11-10T10:30 to 2026-11-24T23:00 UTC (1008 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **116 of 7056** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 231 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4997 | 384 | 373 | 2 | 99.62c | $-9.95 | $-0.27 | needs ~1595 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4082 | 73 | 72 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1991 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4997 | 179 | 173 | 3 | 99.12c | $-15.26 | $-0.88 | needs ~614 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6027 | 1344 | 1330 | 19 | 98.85c | $-52.15 | $-0.40 | needs ~1158 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4053 | 532 | 516 | 3 | 99.70c | $-19.86 | $-0.38 | needs ~2875 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5939 | 288 | 283 | 1 | 99.22c | $+8.94 | $+0.32 | needs ~292 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2338 | 2325 | 2312 | 161 | 92.92c | $-72.30 | $-0.33 | needs ~351 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4997 | 384 | 364 | 2 | 99.63c | $-72.92 | $-0.20 | needs ~1159 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4082 | 73 | 69 | 0 | 99.80c | $+12.99 | $+0.19 | needs ~1168 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4997 | 179 | 161 | 3 | 99.11c | $-157.00 | $-0.95 | needs ~596 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6027 | 1344 | 1298 | 19 | 98.88c | $-524.30 | $-0.40 | needs ~1129 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4053 | 532 | 507 | 3 | 99.70c | $-160.44 | $-0.31 | needs ~1914 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5939 | 288 | 277 | 1 | 99.23c | $+107.41 | $+0.38 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2338 | 2325 | 2296 | 161 | 93.05c | $-922.65 | $-0.43 | needs ~379 more bets with no loss |

