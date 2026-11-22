# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6153 coin-windows from 2026-11-10T10:30 to 2026-11-22T18:15 UTC (879 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **99 of 6153** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4355 | 337 | 327 | 2 | 99.60c | $-10.50 | $-0.32 | needs ~1496 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3569 | 58 | 57 | 0 | 99.79c | $+0.62 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4355 | 165 | 160 | 3 | 99.09c | $-15.99 | $-1.00 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5253 | 1191 | 1179 | 16 | 98.86c | $-39.00 | $-0.33 | needs ~999 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3546 | 470 | 455 | 3 | 99.68c | $-20.56 | $-0.45 | needs ~2758 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5181 | 257 | 254 | 0 | 99.55c | $+8.52 | $+0.34 | needs ~429 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2054 | 2042 | 2030 | 134 | 92.91c | $+11.76 | $+0.06 | needs ~205 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4355 | 337 | 320 | 2 | 99.61c | $-81.84 | $-0.25 | needs ~1117 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3569 | 58 | 54 | 0 | 99.80c | $+9.98 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4355 | 165 | 150 | 3 | 99.09c | $-163.75 | $-1.07 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5253 | 1191 | 1153 | 16 | 98.90c | $-393.94 | $-0.34 | needs ~978 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3546 | 470 | 446 | 3 | 99.69c | $-172.52 | $-0.38 | needs ~1889 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5181 | 257 | 248 | 0 | 99.57c | $+100.96 | $+0.40 | needs ~318 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2054 | 2042 | 2017 | 134 | 93.04c | $-60.43 | $-0.03 | needs ~229 more bets with no loss |

