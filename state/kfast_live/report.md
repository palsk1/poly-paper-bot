# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5558 coin-windows from 2026-11-10T10:30 to 2026-11-21T11:45 UTC (794 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **94 of 5558** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3943 | 306 | 296 | 2 | 99.67c | $-13.33 | $-0.45 | needs ~2058 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3231 | 53 | 52 | 0 | 99.79c | $+0.55 | $+0.11 | needs ~2112 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3943 | 153 | 149 | 3 | 99.23c | $-18.93 | $-1.26 | needs ~755 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4740 | 1075 | 1067 | 16 | 98.93c | $-56.82 | $-0.54 | needs ~1250 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3216 | 409 | 396 | 3 | 99.68c | $-21.66 | $-0.55 | needs ~2773 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4679 | 235 | 232 | 0 | 99.62c | $+6.33 | $+0.27 | needs ~608 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1848 | 1838 | 1828 | 124 | 92.72c | $+10.10 | $+0.06 | needs ~196 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3943 | 306 | 289 | 2 | 99.67c | $-111.37 | $-0.38 | needs ~1447 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3231 | 53 | 49 | 0 | 99.80c | $+9.00 | $+0.18 | needs ~1227 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3943 | 153 | 139 | 3 | 99.23c | $-192.24 | $-1.35 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4740 | 1075 | 1044 | 16 | 98.96c | $-570.06 | $-0.55 | needs ~1223 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3216 | 409 | 388 | 3 | 99.69c | $-187.74 | $-0.48 | needs ~1923 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4679 | 235 | 226 | 0 | 99.63c | $+77.49 | $+0.34 | needs ~449 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1848 | 1838 | 1815 | 124 | 92.86c | $-64.69 | $-0.04 | needs ~217 more bets with no loss |

