# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5684 coin-windows from 2026-11-10T10:30 to 2026-11-21T18:45 UTC (812 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **96 of 5684** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4030 | 312 | 302 | 2 | 99.67c | $-13.19 | $-0.44 | needs ~2050 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3302 | 54 | 53 | 0 | 99.79c | $+0.58 | $+0.11 | needs ~2039 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4030 | 155 | 151 | 3 | 99.23c | $-18.80 | $-1.24 | needs ~755 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4848 | 1100 | 1092 | 16 | 98.90c | $-52.15 | $-0.48 | needs ~1176 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3287 | 419 | 406 | 3 | 99.67c | $-21.21 | $-0.52 | needs ~2676 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4784 | 239 | 236 | 0 | 99.59c | $+7.13 | $+0.30 | needs ~522 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1892 | 1882 | 1872 | 126 | 92.73c | $+19.63 | $+0.11 | needs ~183 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4030 | 312 | 295 | 2 | 99.67c | $-109.62 | $-0.37 | needs ~1442 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3302 | 54 | 50 | 0 | 99.80c | $+9.29 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4030 | 155 | 141 | 3 | 99.23c | $-190.91 | $-1.32 | needs ~735 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4848 | 1100 | 1068 | 16 | 98.94c | $-523.59 | $-0.49 | needs ~1150 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3287 | 419 | 398 | 3 | 99.68c | $-182.89 | $-0.46 | needs ~1873 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4784 | 239 | 230 | 0 | 99.60c | $+85.80 | $+0.37 | needs ~389 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1892 | 1882 | 1859 | 126 | 92.86c | $+27.79 | $+0.02 | needs ~205 more bets with no loss |

