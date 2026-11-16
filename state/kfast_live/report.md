# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3080 coin-windows from 2026-11-10T10:30 to 2026-11-16T08:45 UTC (440 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3080** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2208 | 208 | 205 | 2 | 99.62c | $-14.49 | $-0.71 | needs ~1776 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1807 | 45 | 44 | 0 | 99.81c | $+0.39 | $+0.09 | needs ~2532 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2208 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2633 | 644 | 639 | 12 | 98.99c | $-61.71 | $-0.97 | needs ~1310 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1800 | 250 | 242 | 3 | 99.61c | $-23.41 | $-0.97 | needs ~2205 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2600 | 157 | 155 | 0 | 99.60c | $+4.49 | $+0.29 | needs ~638 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1048 | 1041 | 1038 | 76 | 92.78c | $-55.77 | $-0.58 | needs ~257 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2208 | 208 | 201 | 2 | 99.63c | $-130.31 | $-0.65 | needs ~1338 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1807 | 45 | 41 | 0 | 99.82c | $+6.85 | $+0.16 | needs ~1367 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2208 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2633 | 644 | 628 | 12 | 99.02c | $-620.16 | $-0.99 | needs ~1297 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1800 | 250 | 235 | 3 | 99.62c | $-216.65 | $-0.91 | needs ~1663 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2600 | 157 | 150 | 0 | 99.62c | $+53.85 | $+0.35 | needs ~498 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1048 | 1041 | 1031 | 76 | 92.91c | $-645.54 | $-0.67 | needs ~269 more bets with no loss |

