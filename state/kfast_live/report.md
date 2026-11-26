# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7819 coin-windows from 2026-11-10T10:30 to 2026-11-26T18:00 UTC (1117 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **127 of 7819** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5531 | 397 | 386 | 2 | 99.63c | $-9.88 | $-0.26 | needs ~1636 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4547 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5531 | 197 | 191 | 3 | 99.15c | $-14.36 | $-0.75 | needs ~627 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6665 | 1467 | 1452 | 20 | 98.88c | $-52.74 | $-0.37 | needs ~1203 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4489 | 563 | 547 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2938 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6566 | 305 | 299 | 2 | 99.00c | $+6.37 | $+0.21 | needs ~298 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2570 | 2556 | 2542 | 179 | 92.73c | $-54.18 | $-0.23 | needs ~327 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5531 | 397 | 377 | 2 | 99.64c | $-71.18 | $-0.19 | needs ~1179 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4547 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5531 | 197 | 178 | 3 | 99.15c | $-148.20 | $-0.81 | needs ~611 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6665 | 1467 | 1417 | 20 | 98.91c | $-530.24 | $-0.37 | needs ~1170 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4489 | 563 | 538 | 3 | 99.71c | $-154.76 | $-0.29 | needs ~1930 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6566 | 305 | 291 | 2 | 99.02c | $+80.75 | $+0.28 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2570 | 2556 | 2526 | 179 | 92.87c | $-767.45 | $-0.32 | needs ~357 more bets with no loss |

