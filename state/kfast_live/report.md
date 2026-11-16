# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3262 coin-windows from 2026-11-10T10:30 to 2026-11-16T19:15 UTC (466 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3262** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2335 | 214 | 211 | 2 | 99.63c | $-14.42 | $-0.68 | needs ~1800 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1915 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2335 | 109 | 105 | 3 | 99.15c | $-21.34 | $-2.01 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2791 | 682 | 677 | 12 | 98.97c | $-56.78 | $-0.84 | needs ~1226 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1907 | 265 | 256 | 3 | 99.62c | $-23.20 | $-0.91 | needs ~2252 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2754 | 162 | 160 | 0 | 99.60c | $+4.72 | $+0.30 | needs ~619 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1107 | 1100 | 1097 | 77 | 92.76c | $-23.78 | $-0.23 | needs ~211 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2335 | 214 | 207 | 2 | 99.63c | $-129.18 | $-0.62 | needs ~1353 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1915 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2335 | 109 | 98 | 3 | 99.14c | $-215.72 | $-2.14 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2791 | 682 | 665 | 12 | 99.00c | $-571.07 | $-0.86 | needs ~1213 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1907 | 265 | 249 | 3 | 99.63c | $-213.69 | $-0.85 | needs ~1691 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2754 | 162 | 155 | 0 | 99.61c | $+56.40 | $+0.36 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1107 | 1100 | 1090 | 77 | 92.89c | $-329.13 | $-0.32 | needs ~222 more bets with no loss |

