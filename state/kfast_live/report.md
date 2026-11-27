# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8239 coin-windows from 2026-11-10T10:30 to 2026-11-27T14:30 UTC (1177 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **138 of 8239** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5794 | 419 | 406 | 2 | 99.62c | $-9.19 | $-0.23 | needs ~1583 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4745 | 77 | 75 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2047 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5794 | 216 | 207 | 3 | 99.16c | $-13.18 | $-0.63 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7010 | 1566 | 1551 | 21 | 98.88c | $-53.59 | $-0.35 | needs ~1232 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4683 | 580 | 564 | 3 | 99.71c | $-19.44 | $-0.34 | needs ~2995 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6899 | 320 | 314 | 2 | 99.00c | $+7.80 | $+0.25 | needs ~280 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2738 | 2722 | 2706 | 192 | 92.74c | $-74.49 | $-0.30 | needs ~364 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5794 | 419 | 394 | 2 | 99.63c | $-63.48 | $-0.16 | needs ~1141 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4745 | 77 | 72 | 0 | 99.80c | $+13.43 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5794 | 216 | 192 | 3 | 99.16c | $-137.56 | $-0.70 | needs ~601 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7010 | 1566 | 1512 | 21 | 98.91c | $-539.10 | $-0.36 | needs ~1195 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4683 | 580 | 554 | 3 | 99.71c | $-152.41 | $-0.27 | needs ~1949 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6899 | 320 | 306 | 2 | 99.01c | $+95.04 | $+0.31 | needs ~241 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2738 | 2722 | 2687 | 192 | 92.87c | $-993.67 | $-0.39 | needs ~396 more bets with no loss |

