# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3297 coin-windows from 2026-11-10T10:30 to 2026-11-16T20:30 UTC (471 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **52 of 3297** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2355 | 215 | 212 | 2 | 99.62c | $-14.33 | $-0.68 | needs ~1777 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1932 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2355 | 110 | 106 | 3 | 99.15c | $-21.25 | $-1.99 | needs ~711 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2819 | 689 | 684 | 12 | 98.96c | $-56.08 | $-0.82 | needs ~1218 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1924 | 267 | 258 | 3 | 99.62c | $-23.16 | $-0.90 | needs ~2254 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2780 | 163 | 161 | 0 | 99.60c | $+4.74 | $+0.29 | needs ~619 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1122 | 1115 | 1112 | 81 | 92.68c | $-44.53 | $-0.43 | needs ~242 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2355 | 215 | 208 | 2 | 99.63c | $-128.25 | $-0.61 | needs ~1339 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1932 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2355 | 110 | 99 | 3 | 99.14c | $-214.79 | $-2.11 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2819 | 689 | 672 | 12 | 99.00c | $-564.21 | $-0.84 | needs ~1205 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1924 | 267 | 251 | 3 | 99.63c | $-213.14 | $-0.84 | needs ~1692 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2780 | 163 | 156 | 0 | 99.61c | $+56.67 | $+0.36 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1122 | 1115 | 1105 | 81 | 92.80c | $-538.03 | $-0.52 | needs ~254 more bets with no loss |

