# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3332 coin-windows from 2026-11-10T10:30 to 2026-11-16T21:45 UTC (476 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **53 of 3332** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2377 | 215 | 212 | 2 | 99.62c | $-14.33 | $-0.68 | needs ~1777 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1951 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2377 | 110 | 106 | 3 | 99.15c | $-21.25 | $-1.99 | needs ~711 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2847 | 695 | 690 | 12 | 98.97c | $-55.64 | $-0.81 | needs ~1215 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1942 | 267 | 258 | 3 | 99.62c | $-23.16 | $-0.90 | needs ~2254 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2805 | 163 | 161 | 0 | 99.60c | $+4.74 | $+0.29 | needs ~619 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1135 | 1128 | 1125 | 83 | 92.66c | $-54.22 | $-0.52 | needs ~258 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2377 | 215 | 208 | 2 | 99.63c | $-128.25 | $-0.61 | needs ~1339 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1951 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2377 | 110 | 99 | 3 | 99.14c | $-214.79 | $-2.11 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2847 | 695 | 678 | 12 | 99.00c | $-559.84 | $-0.83 | needs ~1203 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1942 | 267 | 251 | 3 | 99.63c | $-213.14 | $-0.84 | needs ~1692 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2805 | 163 | 156 | 0 | 99.61c | $+56.67 | $+0.36 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1135 | 1128 | 1118 | 83 | 92.79c | $-635.78 | $-0.61 | needs ~270 more bets with no loss |

