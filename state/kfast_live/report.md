# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3353 coin-windows from 2026-11-10T10:30 to 2026-11-16T22:30 UTC (479 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **53 of 3353** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2392 | 215 | 212 | 2 | 99.62c | $-14.33 | $-0.68 | needs ~1777 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1965 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2392 | 111 | 107 | 3 | 99.15c | $-21.20 | $-1.96 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2863 | 698 | 693 | 12 | 98.97c | $-55.57 | $-0.81 | needs ~1219 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1955 | 268 | 259 | 3 | 99.62c | $-23.15 | $-0.89 | needs ~2259 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2821 | 164 | 162 | 0 | 99.60c | $+4.75 | $+0.29 | needs ~621 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1141 | 1134 | 1131 | 83 | 92.68c | $-52.24 | $-0.50 | needs ~256 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2392 | 215 | 208 | 2 | 99.63c | $-128.25 | $-0.61 | needs ~1339 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1965 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2392 | 111 | 100 | 3 | 99.15c | $-214.29 | $-2.09 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2863 | 698 | 681 | 12 | 99.00c | $-559.07 | $-0.82 | needs ~1206 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1955 | 268 | 252 | 3 | 99.63c | $-212.96 | $-0.84 | needs ~1694 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2821 | 164 | 157 | 0 | 99.62c | $+56.80 | $+0.36 | needs ~486 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1141 | 1134 | 1124 | 83 | 92.81c | $-616.14 | $-0.59 | needs ~268 more bets with no loss |

