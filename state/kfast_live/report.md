# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8379 coin-windows from 2026-11-10T10:30 to 2026-11-27T21:30 UTC (1197 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **139 of 8379** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5895 | 429 | 416 | 2 | 99.63c | $-9.00 | $-0.22 | needs ~1587 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4825 | 78 | 76 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~1997 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5895 | 226 | 217 | 3 | 99.18c | $-12.66 | $-0.58 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7129 | 1596 | 1581 | 21 | 98.89c | $-52.25 | $-0.33 | needs ~1232 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4764 | 590 | 574 | 3 | 99.71c | $-19.30 | $-0.34 | needs ~3000 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7021 | 327 | 321 | 2 | 99.01c | $+7.86 | $+0.25 | needs ~285 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2787 | 2771 | 2754 | 195 | 92.73c | $-70.07 | $-0.27 | needs ~358 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5895 | 429 | 404 | 2 | 99.63c | $-61.11 | $-0.15 | needs ~1142 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4825 | 78 | 73 | 0 | 99.79c | $+13.80 | $+0.19 | needs ~1157 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5895 | 226 | 200 | 3 | 99.17c | $-132.95 | $-0.64 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7129 | 1596 | 1542 | 21 | 98.92c | $-525.88 | $-0.34 | needs ~1196 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4764 | 590 | 564 | 3 | 99.71c | $-150.27 | $-0.26 | needs ~1947 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7021 | 327 | 313 | 2 | 99.03c | $+96.05 | $+0.30 | needs ~244 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2787 | 2771 | 2735 | 195 | 92.87c | $-962.03 | $-0.38 | needs ~392 more bets with no loss |

