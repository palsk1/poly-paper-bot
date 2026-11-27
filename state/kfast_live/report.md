# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8309 coin-windows from 2026-11-10T10:30 to 2026-11-27T19:00 UTC (1187 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **139 of 8309** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5849 | 422 | 409 | 2 | 99.62c | $-9.15 | $-0.22 | needs ~1587 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4790 | 78 | 76 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~1997 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5849 | 219 | 210 | 3 | 99.17c | $-13.03 | $-0.62 | needs ~619 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7072 | 1577 | 1562 | 21 | 98.89c | $-53.16 | $-0.34 | needs ~1233 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4728 | 583 | 567 | 3 | 99.71c | $-19.44 | $-0.34 | needs ~3011 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6963 | 323 | 317 | 2 | 99.00c | $+7.82 | $+0.25 | needs ~283 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2756 | 2740 | 2724 | 194 | 92.73c | $-79.05 | $-0.31 | needs ~371 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5849 | 422 | 397 | 2 | 99.63c | $-62.84 | $-0.16 | needs ~1142 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4790 | 78 | 73 | 0 | 99.79c | $+13.80 | $+0.19 | needs ~1157 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5849 | 219 | 195 | 3 | 99.16c | $-136.06 | $-0.68 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7072 | 1577 | 1523 | 21 | 98.92c | $-534.54 | $-0.35 | needs ~1196 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4728 | 583 | 557 | 3 | 99.71c | $-152.14 | $-0.27 | needs ~1955 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6963 | 323 | 309 | 2 | 99.02c | $+95.49 | $+0.31 | needs ~242 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2756 | 2740 | 2705 | 194 | 92.86c | $-1039.30 | $-0.41 | needs ~404 more bets with no loss |

