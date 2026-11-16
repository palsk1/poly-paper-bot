# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3115 coin-windows from 2026-11-10T10:30 to 2026-11-16T10:00 UTC (445 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3115** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2236 | 209 | 206 | 2 | 99.62c | $-14.49 | $-0.70 | needs ~1784 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1833 | 45 | 44 | 0 | 99.81c | $+0.39 | $+0.09 | needs ~2532 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2236 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2664 | 649 | 644 | 12 | 98.99c | $-61.55 | $-0.96 | needs ~1315 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1826 | 255 | 247 | 3 | 99.62c | $-23.31 | $-0.94 | needs ~2213 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2632 | 158 | 156 | 0 | 99.60c | $+4.49 | $+0.29 | needs ~642 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1056 | 1049 | 1046 | 76 | 92.79c | $-51.13 | $-0.52 | needs ~251 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2236 | 209 | 202 | 2 | 99.63c | $-130.22 | $-0.64 | needs ~1343 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1833 | 45 | 41 | 0 | 99.82c | $+6.85 | $+0.16 | needs ~1367 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2236 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2664 | 649 | 633 | 12 | 99.03c | $-618.57 | $-0.98 | needs ~1302 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1826 | 255 | 240 | 3 | 99.62c | $-215.51 | $-0.89 | needs ~1672 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2632 | 158 | 151 | 0 | 99.62c | $+53.94 | $+0.35 | needs ~500 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1056 | 1049 | 1039 | 76 | 92.91c | $-599.96 | $-0.62 | needs ~263 more bets with no loss |

