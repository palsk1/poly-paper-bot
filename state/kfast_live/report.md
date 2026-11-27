# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8064 coin-windows from 2026-11-10T10:30 to 2026-11-27T06:15 UTC (1152 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 8064** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5684 | 411 | 400 | 2 | 99.62c | $-9.30 | $-0.23 | needs ~1581 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4659 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5684 | 211 | 203 | 3 | 99.16c | $-13.43 | $-0.66 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6859 | 1524 | 1509 | 21 | 98.88c | $-56.80 | $-0.38 | needs ~1256 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4595 | 571 | 555 | 3 | 99.70c | $-19.50 | $-0.35 | needs ~2968 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6756 | 314 | 308 | 2 | 98.98c | $+7.71 | $+0.25 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2673 | 2657 | 2643 | 189 | 92.70c | $-76.50 | $-0.31 | needs ~364 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5684 | 411 | 389 | 2 | 99.63c | $-65.17 | $-0.17 | needs ~1146 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4659 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5684 | 211 | 188 | 3 | 99.15c | $-139.91 | $-0.72 | needs ~601 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6859 | 1524 | 1470 | 21 | 98.91c | $-572.51 | $-0.39 | needs ~1220 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4595 | 571 | 546 | 3 | 99.71c | $-153.74 | $-0.28 | needs ~1941 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6756 | 314 | 300 | 2 | 99.00c | $+93.66 | $+0.31 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2673 | 2657 | 2625 | 189 | 92.83c | $-1009.69 | $-0.41 | needs ~396 more bets with no loss |

