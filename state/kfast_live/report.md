# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8483 coin-windows from 2026-11-10T10:30 to 2026-11-28T02:00 UTC (1209 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **142 of 8483** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5969 | 438 | 425 | 2 | 99.63c | $-8.92 | $-0.21 | needs ~1606 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4882 | 82 | 80 | 0 | 99.79c | $+0.85 | $+0.11 | needs ~2077 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5969 | 228 | 219 | 3 | 99.18c | $-12.55 | $-0.57 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7221 | 1620 | 1605 | 23 | 98.83c | $-59.57 | $-0.37 | needs ~1251 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4822 | 597 | 581 | 3 | 99.71c | $-19.11 | $-0.33 | needs ~2973 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7110 | 333 | 327 | 2 | 99.01c | $+8.60 | $+0.27 | needs ~275 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2824 | 2808 | 2791 | 200 | 92.70c | $-85.22 | $-0.33 | needs ~381 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5969 | 438 | 413 | 2 | 99.64c | $-59.56 | $-0.14 | needs ~1150 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4882 | 82 | 77 | 0 | 99.80c | $+14.25 | $+0.18 | needs ~1178 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5969 | 228 | 201 | 3 | 99.17c | $-132.04 | $-0.64 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7221 | 1620 | 1566 | 23 | 98.86c | $-601.29 | $-0.38 | needs ~1218 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4822 | 597 | 570 | 3 | 99.71c | $-147.89 | $-0.26 | needs ~1931 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7110 | 333 | 319 | 2 | 99.02c | $+103.83 | $+0.32 | needs ~234 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2824 | 2808 | 2771 | 200 | 92.84c | $-1118.42 | $-0.43 | needs ~416 more bets with no loss |

