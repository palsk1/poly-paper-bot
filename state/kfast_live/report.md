# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7854 coin-windows from 2026-11-10T10:30 to 2026-11-26T19:15 UTC (1122 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **129 of 7854** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5553 | 399 | 388 | 2 | 99.62c | $-9.67 | $-0.25 | needs ~1603 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4564 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5553 | 198 | 192 | 3 | 99.15c | $-14.16 | $-0.73 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6692 | 1473 | 1458 | 21 | 98.87c | $-61.01 | $-0.42 | needs ~1289 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4506 | 564 | 548 | 3 | 99.70c | $-19.54 | $-0.36 | needs ~2943 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6591 | 306 | 300 | 2 | 99.00c | $+6.39 | $+0.21 | needs ~298 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2586 | 2571 | 2557 | 181 | 92.71c | $-59.47 | $-0.25 | needs ~335 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5553 | 399 | 379 | 2 | 99.63c | $-69.09 | $-0.18 | needs ~1160 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4564 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5553 | 198 | 179 | 3 | 99.14c | $-146.29 | $-0.80 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6692 | 1473 | 1423 | 21 | 98.90c | $-613.69 | $-0.43 | needs ~1256 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4506 | 564 | 539 | 3 | 99.71c | $-154.67 | $-0.29 | needs ~1932 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6591 | 306 | 292 | 2 | 99.02c | $+81.02 | $+0.28 | needs ~256 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2586 | 2571 | 2541 | 181 | 92.85c | $-821.47 | $-0.35 | needs ~365 more bets with no loss |

