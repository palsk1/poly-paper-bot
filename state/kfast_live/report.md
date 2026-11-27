# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8344 coin-windows from 2026-11-10T10:30 to 2026-11-27T20:15 UTC (1192 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **139 of 8344** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5879 | 424 | 411 | 2 | 99.62c | $-9.06 | $-0.22 | needs ~1578 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4817 | 78 | 76 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~1997 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5879 | 222 | 213 | 3 | 99.17c | $-12.85 | $-0.60 | needs ~619 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7105 | 1584 | 1569 | 21 | 98.89c | $-52.88 | $-0.34 | needs ~1234 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4755 | 587 | 571 | 3 | 99.71c | $-19.39 | $-0.34 | needs ~3014 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6996 | 326 | 320 | 2 | 99.01c | $+7.86 | $+0.25 | needs ~284 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2763 | 2747 | 2731 | 194 | 92.73c | $-74.64 | $-0.29 | needs ~365 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5879 | 424 | 399 | 2 | 99.63c | $-62.11 | $-0.15 | needs ~1139 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4817 | 78 | 73 | 0 | 99.79c | $+13.80 | $+0.19 | needs ~1157 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5879 | 222 | 197 | 3 | 99.17c | $-134.59 | $-0.66 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7105 | 1584 | 1530 | 21 | 98.92c | $-532.08 | $-0.35 | needs ~1197 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4755 | 587 | 561 | 3 | 99.71c | $-151.34 | $-0.27 | needs ~1955 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6996 | 326 | 312 | 2 | 99.03c | $+95.96 | $+0.31 | needs ~244 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2763 | 2747 | 2712 | 194 | 92.86c | $-998.02 | $-0.39 | needs ~398 more bets with no loss |

