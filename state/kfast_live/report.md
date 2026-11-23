# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6517 coin-windows from 2026-11-10T10:30 to 2026-11-23T09:45 UTC (931 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **107 of 6517** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4592 | 372 | 361 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1568 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3750 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4592 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5556 | 1270 | 1256 | 18 | 98.86c | $-50.23 | $-0.40 | needs ~1129 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3726 | 510 | 495 | 3 | 99.69c | $-20.03 | $-0.40 | needs ~2814 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5479 | 277 | 274 | 1 | 99.20c | $+8.80 | $+0.32 | needs ~289 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2206 | 2193 | 2180 | 145 | 93.01c | $-19.05 | $-0.09 | needs ~263 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4592 | 372 | 353 | 2 | 99.62c | $-75.01 | $-0.21 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3750 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4592 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5556 | 1270 | 1228 | 18 | 98.89c | $-504.38 | $-0.41 | needs ~1102 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3726 | 510 | 486 | 3 | 99.70c | $-163.91 | $-0.34 | needs ~1896 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5479 | 277 | 268 | 1 | 99.21c | $+105.29 | $+0.39 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2206 | 2193 | 2166 | 145 | 93.14c | $-371.90 | $-0.18 | needs ~288 more bets with no loss |

