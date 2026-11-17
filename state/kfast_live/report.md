# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3766 coin-windows from 2026-11-10T10:30 to 2026-11-17T21:30 UTC (538 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3766** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2700 | 229 | 222 | 2 | 99.63c | $-14.23 | $-0.64 | needs ~1821 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2231 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2700 | 117 | 113 | 3 | 99.17c | $-20.91 | $-1.84 | needs ~725 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3230 | 779 | 772 | 13 | 98.90c | $-53.28 | $-0.69 | needs ~1132 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2224 | 298 | 289 | 3 | 99.65c | $-22.97 | $-0.80 | needs ~2450 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3181 | 177 | 174 | 0 | 99.61c | $+4.93 | $+0.28 | needs ~636 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1256 | 1248 | 1241 | 88 | 92.79c | $-39.76 | $-0.34 | needs ~242 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2700 | 229 | 218 | 2 | 99.64c | $-126.19 | $-0.58 | needs ~1353 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2231 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2700 | 117 | 106 | 3 | 99.17c | $-211.33 | $-1.94 | needs ~707 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3230 | 779 | 757 | 13 | 98.94c | $-537.62 | $-0.71 | needs ~1120 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2224 | 298 | 282 | 3 | 99.65c | $-208.92 | $-0.73 | needs ~1797 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3181 | 177 | 169 | 0 | 99.62c | $+59.51 | $+0.35 | needs ~489 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1256 | 1248 | 1232 | 88 | 92.92c | $-501.56 | $-0.43 | needs ~256 more bets with no loss |

