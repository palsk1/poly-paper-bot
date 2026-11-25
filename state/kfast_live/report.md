# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7441 coin-windows from 2026-11-10T10:30 to 2026-11-25T18:30 UTC (1063 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **120 of 7441** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5262 | 389 | 378 | 2 | 99.62c | $-9.92 | $-0.26 | needs ~1610 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4313 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5262 | 187 | 181 | 3 | 99.13c | $-14.86 | $-0.82 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6353 | 1412 | 1397 | 20 | 98.87c | $-57.91 | $-0.42 | needs ~1251 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4275 | 541 | 525 | 3 | 99.70c | $-19.74 | $-0.38 | needs ~2885 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6253 | 292 | 287 | 2 | 98.98c | $+5.89 | $+0.21 | needs ~297 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2457 | 2444 | 2431 | 171 | 92.84c | $-73.91 | $-0.33 | needs ~357 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5262 | 389 | 369 | 2 | 99.63c | $-72.26 | $-0.19 | needs ~1167 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4313 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5262 | 187 | 168 | 3 | 99.13c | $-153.20 | $-0.89 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6353 | 1412 | 1362 | 20 | 98.90c | $-581.80 | $-0.43 | needs ~1216 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4275 | 541 | 516 | 3 | 99.70c | $-158.58 | $-0.31 | needs ~1916 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6253 | 292 | 281 | 2 | 99.00c | $+75.52 | $+0.27 | needs ~258 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2457 | 2444 | 2415 | 171 | 92.97c | $-951.39 | $-0.42 | needs ~385 more bets with no loss |

