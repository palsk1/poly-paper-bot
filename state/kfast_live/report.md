# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5719 coin-windows from 2026-11-10T10:30 to 2026-11-21T20:00 UTC (817 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **96 of 5719** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4052 | 312 | 302 | 2 | 99.67c | $-13.19 | $-0.44 | needs ~2050 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3322 | 54 | 53 | 0 | 99.79c | $+0.58 | $+0.11 | needs ~2039 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4052 | 156 | 152 | 3 | 99.24c | $-18.75 | $-1.23 | needs ~756 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4878 | 1105 | 1096 | 16 | 98.91c | $-52.10 | $-0.48 | needs ~1179 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3307 | 421 | 408 | 3 | 99.68c | $-21.21 | $-0.52 | needs ~2690 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4812 | 239 | 236 | 0 | 99.59c | $+7.13 | $+0.30 | needs ~522 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1901 | 1891 | 1880 | 126 | 92.73c | $+24.04 | $+0.14 | needs ~176 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4052 | 312 | 295 | 2 | 99.67c | $-109.62 | $-0.37 | needs ~1442 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3322 | 54 | 50 | 0 | 99.80c | $+9.29 | $+0.18 | needs ~1211 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4052 | 156 | 142 | 3 | 99.23c | $-190.41 | $-1.31 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4878 | 1105 | 1072 | 16 | 98.94c | $-522.84 | $-0.49 | needs ~1152 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3307 | 421 | 400 | 3 | 99.68c | $-182.71 | $-0.45 | needs ~1879 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4812 | 239 | 230 | 0 | 99.60c | $+85.80 | $+0.37 | needs ~389 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1901 | 1891 | 1867 | 126 | 92.86c | $+72.12 | $+0.04 | needs ~197 more bets with no loss |

