# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8036 coin-windows from 2026-11-10T10:30 to 2026-11-27T05:00 UTC (1148 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 8036** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5668 | 409 | 398 | 2 | 99.63c | $-9.51 | $-0.24 | needs ~1613 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4647 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5668 | 209 | 201 | 3 | 99.16c | $-13.69 | $-0.68 | needs ~625 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6837 | 1518 | 1503 | 21 | 98.87c | $-57.12 | $-0.38 | needs ~1256 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4585 | 571 | 555 | 3 | 99.70c | $-19.50 | $-0.35 | needs ~2968 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6734 | 314 | 308 | 2 | 98.98c | $+7.71 | $+0.25 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2660 | 2644 | 2630 | 188 | 92.70c | $-77.03 | $-0.31 | needs ~365 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5668 | 409 | 388 | 2 | 99.63c | $-67.12 | $-0.17 | needs ~1166 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4647 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5668 | 209 | 186 | 3 | 99.16c | $-142.35 | $-0.74 | needs ~607 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6837 | 1518 | 1465 | 21 | 98.90c | $-575.45 | $-0.39 | needs ~1222 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4585 | 571 | 546 | 3 | 99.71c | $-153.74 | $-0.28 | needs ~1941 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6734 | 314 | 300 | 2 | 99.00c | $+93.66 | $+0.31 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2660 | 2644 | 2613 | 188 | 92.84c | $-1011.60 | $-0.41 | needs ~397 more bets with no loss |

