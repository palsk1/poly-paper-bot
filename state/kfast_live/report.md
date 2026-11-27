# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8274 coin-windows from 2026-11-10T10:30 to 2026-11-27T15:45 UTC (1182 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **139 of 8274** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5822 | 419 | 406 | 2 | 99.62c | $-9.19 | $-0.23 | needs ~1583 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4770 | 77 | 75 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2047 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5822 | 216 | 207 | 3 | 99.16c | $-13.18 | $-0.63 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7040 | 1567 | 1552 | 21 | 98.88c | $-53.58 | $-0.35 | needs ~1233 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4709 | 580 | 564 | 3 | 99.71c | $-19.44 | $-0.34 | needs ~2995 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6931 | 322 | 316 | 2 | 99.00c | $+7.80 | $+0.25 | needs ~282 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2745 | 2729 | 2713 | 193 | 92.72c | $-75.58 | $-0.30 | needs ~365 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5822 | 419 | 394 | 2 | 99.63c | $-63.48 | $-0.16 | needs ~1141 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4770 | 77 | 72 | 0 | 99.80c | $+13.43 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5822 | 216 | 192 | 3 | 99.16c | $-137.56 | $-0.70 | needs ~601 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7040 | 1567 | 1513 | 21 | 98.91c | $-538.92 | $-0.36 | needs ~1196 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4709 | 580 | 554 | 3 | 99.71c | $-152.41 | $-0.27 | needs ~1949 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6931 | 322 | 308 | 2 | 99.02c | $+95.22 | $+0.31 | needs ~242 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2745 | 2729 | 2694 | 193 | 92.86c | $-1004.54 | $-0.40 | needs ~398 more bets with no loss |

