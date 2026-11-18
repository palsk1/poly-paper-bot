# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4011 coin-windows from 2026-11-10T10:30 to 2026-11-18T09:30 UTC (573 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **65 of 4011** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2882 | 244 | 237 | 2 | 99.64c | $-14.08 | $-0.59 | needs ~1889 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2374 | 48 | 47 | 0 | 99.81c | $+0.42 | $+0.09 | needs ~2510 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2882 | 123 | 119 | 3 | 99.19c | $-20.63 | $-1.72 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3445 | 825 | 818 | 14 | 98.88c | $-57.27 | $-0.71 | needs ~1169 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2367 | 321 | 312 | 3 | 99.66c | $-22.86 | $-0.73 | needs ~2600 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3392 | 189 | 186 | 0 | 99.58c | $+5.68 | $+0.31 | needs ~564 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1330 | 1321 | 1314 | 92 | 92.84c | $-36.16 | $-0.29 | needs ~243 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2882 | 244 | 233 | 2 | 99.65c | $-123.64 | $-0.53 | needs ~1390 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2374 | 48 | 44 | 0 | 99.82c | $+7.39 | $+0.16 | needs ~1354 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2882 | 123 | 109 | 3 | 99.18c | $-209.32 | $-1.86 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3445 | 825 | 802 | 14 | 98.92c | $-578.71 | $-0.72 | needs ~1157 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2367 | 321 | 304 | 3 | 99.67c | $-206.10 | $-0.67 | needs ~1868 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3392 | 189 | 180 | 0 | 99.60c | $+67.56 | $+0.37 | needs ~438 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1330 | 1321 | 1305 | 92 | 92.97c | $-478.39 | $-0.39 | needs ~259 more bets with no loss |

