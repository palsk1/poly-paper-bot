# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7945 coin-windows from 2026-11-10T10:30 to 2026-11-27T01:45 UTC (1135 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 7945** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5603 | 405 | 394 | 2 | 99.63c | $-9.56 | $-0.24 | needs ~1607 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4602 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5603 | 204 | 197 | 3 | 99.16c | $-13.88 | $-0.70 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6757 | 1495 | 1480 | 21 | 98.87c | $-59.62 | $-0.41 | needs ~1282 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4538 | 566 | 550 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2954 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6658 | 309 | 303 | 2 | 99.01c | $+6.47 | $+0.22 | needs ~300 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2631 | 2616 | 2602 | 187 | 92.73c | $-93.30 | $-0.38 | needs ~389 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5603 | 405 | 385 | 2 | 99.63c | $-67.77 | $-0.17 | needs ~1162 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4602 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5603 | 204 | 183 | 3 | 99.15c | $-144.19 | $-0.77 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6757 | 1495 | 1443 | 21 | 98.90c | $-599.60 | $-0.41 | needs ~1248 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4538 | 566 | 541 | 3 | 99.71c | $-154.49 | $-0.28 | needs ~1936 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6658 | 309 | 295 | 2 | 99.02c | $+81.91 | $+0.28 | needs ~257 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2631 | 2616 | 2586 | 187 | 92.87c | $-1164.92 | $-0.48 | needs ~421 more bets with no loss |

