# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7658 coin-windows from 2026-11-10T10:30 to 2026-11-26T05:45 UTC (1094 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **126 of 7658** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5407 | 394 | 383 | 2 | 99.63c | $-9.91 | $-0.26 | needs ~1630 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4437 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5407 | 192 | 186 | 3 | 99.14c | $-14.61 | $-0.78 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6525 | 1447 | 1432 | 20 | 98.87c | $-53.68 | $-0.38 | needs ~1203 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4391 | 554 | 538 | 3 | 99.70c | $-19.65 | $-0.37 | needs ~2926 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6427 | 301 | 296 | 2 | 99.00c | $+6.17 | $+0.21 | needs ~300 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2533 | 2519 | 2505 | 175 | 92.76c | $-47.00 | $-0.20 | needs ~315 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5407 | 394 | 374 | 2 | 99.63c | $-71.72 | $-0.19 | needs ~1176 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4437 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5407 | 192 | 173 | 3 | 99.14c | $-150.70 | $-0.85 | needs ~607 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6525 | 1447 | 1397 | 20 | 98.90c | $-539.71 | $-0.39 | needs ~1170 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4391 | 554 | 529 | 3 | 99.71c | $-156.58 | $-0.29 | needs ~1929 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6427 | 301 | 289 | 2 | 99.01c | $+78.45 | $+0.27 | needs ~259 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2533 | 2519 | 2489 | 175 | 92.90c | $-692.88 | $-0.30 | needs ~345 more bets with no loss |

