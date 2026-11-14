# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1960 coin-windows from 2026-11-10T10:30 to 2026-11-14T06:00 UTC (280 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **29 of 1960** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 248 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1418 | 112 | 110 | 1 | 99.79c | $-8.77 | $-0.80 | needs ~3380 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1178 | 23 | 23 | 0 | 99.84c | $+0.13 | $+0.06 | needs ~4050 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1418 | 51 | 50 | 1 | 99.43c | $-7.25 | $-1.44 | needs ~664 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1701 | 382 | 380 | 7 | 98.87c | $-31.19 | $-0.83 | needs ~773 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1171 | 145 | 139 | 0 | 99.62c | $+3.75 | $+0.27 | needs ~710 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1681 | 92 | 91 | 0 | 99.51c | $+3.38 | $+0.37 | needs ~526 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 630 | 625 | 623 | 39 | 93.33c | $-0.22 | $-0.00 | needs ~143 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1418 | 112 | 108 | 1 | 99.79c | $-79.67 | $-0.74 | needs ~1959 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1178 | 23 | 21 | 0 | 99.85c | $+2.91 | $+0.14 | needs ~1658 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1418 | 51 | 46 | 1 | 99.44c | $-73.52 | $-1.54 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1701 | 382 | 371 | 7 | 98.91c | $-317.26 | $-0.85 | needs ~770 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1171 | 145 | 135 | 0 | 99.62c | $+47.52 | $+0.35 | needs ~519 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1681 | 92 | 87 | 0 | 99.54c | $+38.42 | $+0.43 | needs ~446 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 630 | 625 | 618 | 39 | 93.46c | $-58.79 | $-0.10 | needs ~151 more bets with no loss |

