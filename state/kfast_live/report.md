# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4046 coin-windows from 2026-11-10T10:30 to 2026-11-18T10:45 UTC (578 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **65 of 4046** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2903 | 245 | 238 | 2 | 99.64c | $-14.06 | $-0.59 | needs ~1890 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2390 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2903 | 124 | 120 | 3 | 99.19c | $-20.58 | $-1.70 | needs ~738 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3471 | 832 | 825 | 14 | 98.89c | $-57.03 | $-0.70 | needs ~1173 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2381 | 323 | 314 | 3 | 99.66c | $-22.82 | $-0.73 | needs ~2600 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3418 | 190 | 187 | 0 | 99.59c | $+5.68 | $+0.30 | needs ~567 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1345 | 1336 | 1329 | 93 | 92.86c | $-38.80 | $-0.31 | needs ~248 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2903 | 245 | 234 | 2 | 99.65c | $-123.38 | $-0.53 | needs ~1390 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2390 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2903 | 124 | 110 | 3 | 99.18c | $-208.82 | $-1.84 | needs ~714 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3471 | 832 | 809 | 14 | 98.92c | $-576.09 | $-0.71 | needs ~1161 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2381 | 323 | 306 | 3 | 99.67c | $-205.64 | $-0.67 | needs ~1870 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3418 | 190 | 181 | 0 | 99.60c | $+67.65 | $+0.37 | needs ~440 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1345 | 1336 | 1320 | 93 | 92.99c | $-505.38 | $-0.41 | needs ~264 more bets with no loss |

