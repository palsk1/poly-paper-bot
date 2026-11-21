# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5789 coin-windows from 2026-11-10T10:30 to 2026-11-21T23:15 UTC (827 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **97 of 5789** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4096 | 317 | 307 | 2 | 99.67c | $-13.14 | $-0.43 | needs ~2067 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3358 | 56 | 55 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2009 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4096 | 157 | 153 | 3 | 99.24c | $-18.70 | $-1.22 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4938 | 1122 | 1112 | 16 | 98.92c | $-51.33 | $-0.46 | needs ~1179 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3340 | 424 | 411 | 3 | 99.68c | $-21.15 | $-0.51 | needs ~2688 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4870 | 242 | 239 | 0 | 99.59c | $+7.16 | $+0.30 | needs ~526 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1931 | 1920 | 1909 | 126 | 92.79c | $+33.72 | $+0.19 | needs ~163 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4096 | 317 | 300 | 2 | 99.67c | $-108.71 | $-0.36 | needs ~1449 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3358 | 56 | 52 | 0 | 99.80c | $+9.75 | $+0.18 | needs ~1196 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4096 | 157 | 143 | 3 | 99.23c | $-189.91 | $-1.30 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4938 | 1122 | 1087 | 16 | 98.95c | $-514.51 | $-0.47 | needs ~1150 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3340 | 424 | 403 | 3 | 99.68c | $-181.89 | $-0.45 | needs ~1877 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4870 | 242 | 233 | 0 | 99.61c | $+86.35 | $+0.37 | needs ~390 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1931 | 1920 | 1896 | 126 | 92.92c | $+168.07 | $+0.09 | needs ~185 more bets with no loss |

