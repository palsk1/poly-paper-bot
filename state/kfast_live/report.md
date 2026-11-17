# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3388 coin-windows from 2026-11-10T10:30 to 2026-11-17T02:00 UTC (484 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **53 of 3388** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2416 | 215 | 212 | 2 | 99.62c | $-14.33 | $-0.68 | needs ~1777 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1986 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2416 | 111 | 107 | 3 | 99.15c | $-21.20 | $-1.96 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2894 | 709 | 704 | 12 | 98.96c | $-53.93 | $-0.77 | needs ~1190 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1971 | 273 | 264 | 3 | 99.63c | $-23.15 | $-0.88 | needs ~2303 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2852 | 166 | 164 | 0 | 99.60c | $+4.82 | $+0.29 | needs ~618 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1152 | 1145 | 1142 | 83 | 92.70c | $-46.27 | $-0.43 | needs ~247 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2416 | 215 | 208 | 2 | 99.63c | $-128.25 | $-0.61 | needs ~1339 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1986 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2416 | 111 | 100 | 3 | 99.15c | $-214.29 | $-2.09 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2894 | 709 | 692 | 12 | 99.00c | $-542.97 | $-0.79 | needs ~1178 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1971 | 273 | 257 | 3 | 99.64c | $-212.51 | $-0.82 | needs ~1717 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2852 | 166 | 159 | 0 | 99.61c | $+57.59 | $+0.36 | needs ~483 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1152 | 1145 | 1134 | 83 | 92.82c | $-557.22 | $-0.53 | needs ~260 more bets with no loss |

