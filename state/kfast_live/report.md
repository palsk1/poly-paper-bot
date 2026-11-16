# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3150 coin-windows from 2026-11-10T10:30 to 2026-11-16T11:15 UTC (450 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3150** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2262 | 212 | 209 | 2 | 99.63c | $-14.46 | $-0.69 | needs ~1799 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1856 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2262 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2694 | 656 | 651 | 12 | 98.99c | $-60.44 | $-0.93 | needs ~1292 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1849 | 258 | 250 | 3 | 99.61c | $-23.20 | $-0.93 | needs ~2200 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2661 | 159 | 157 | 0 | 99.60c | $+4.50 | $+0.29 | needs ~644 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1068 | 1061 | 1058 | 76 | 92.75c | $-39.36 | $-0.40 | needs ~232 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2262 | 212 | 205 | 2 | 99.63c | $-129.68 | $-0.63 | needs ~1351 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1856 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2262 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2694 | 656 | 640 | 12 | 99.02c | $-607.47 | $-0.95 | needs ~1280 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1849 | 258 | 243 | 3 | 99.62c | $-214.31 | $-0.87 | needs ~1665 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2661 | 159 | 152 | 0 | 99.62c | $+54.12 | $+0.35 | needs ~501 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1068 | 1061 | 1051 | 76 | 92.88c | $-483.80 | $-0.49 | needs ~244 more bets with no loss |

