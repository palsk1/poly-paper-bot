# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4165 coin-windows from 2026-11-10T10:30 to 2026-11-18T18:30 UTC (595 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4165** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2978 | 251 | 243 | 2 | 99.64c | $-13.97 | $-0.57 | needs ~1896 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2448 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2978 | 126 | 122 | 3 | 99.19c | $-20.44 | $-1.66 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3566 | 854 | 846 | 14 | 98.88c | $-54.41 | $-0.65 | needs ~1139 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2438 | 328 | 319 | 3 | 99.66c | $-22.79 | $-0.72 | needs ~2629 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3509 | 193 | 190 | 0 | 99.59c | $+5.74 | $+0.30 | needs ~569 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1394 | 1385 | 1377 | 96 | 92.82c | $-31.49 | $-0.25 | needs ~238 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2978 | 251 | 239 | 2 | 99.65c | $-122.00 | $-0.51 | needs ~1390 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2448 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2978 | 126 | 112 | 3 | 99.18c | $-207.39 | $-1.79 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3566 | 854 | 829 | 14 | 98.92c | $-550.30 | $-0.66 | needs ~1127 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2438 | 328 | 311 | 3 | 99.67c | $-204.92 | $-0.65 | needs ~1883 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3509 | 193 | 184 | 0 | 99.61c | $+68.48 | $+0.37 | needs ~439 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1394 | 1385 | 1368 | 96 | 92.96c | $-439.34 | $-0.34 | needs ~255 more bets with no loss |

