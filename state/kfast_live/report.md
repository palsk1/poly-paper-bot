# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8274 coin-windows from 2026-11-10T10:30 to 2026-11-27T17:45 UTC (1182 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **138 of 8274** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5820 | 421 | 408 | 2 | 99.62c | $-9.16 | $-0.22 | needs ~1585 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4768 | 78 | 76 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~1997 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5820 | 217 | 208 | 3 | 99.16c | $-13.13 | $-0.63 | needs ~619 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7040 | 1572 | 1557 | 21 | 98.88c | $-53.31 | $-0.35 | needs ~1232 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4705 | 581 | 565 | 3 | 99.71c | $-19.44 | $-0.34 | needs ~3001 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6931 | 322 | 316 | 2 | 99.00c | $+7.81 | $+0.25 | needs ~282 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2749 | 2733 | 2717 | 194 | 92.72c | $-83.01 | $-0.33 | needs ~377 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5820 | 421 | 396 | 2 | 99.63c | $-63.02 | $-0.16 | needs ~1141 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4768 | 78 | 73 | 0 | 99.79c | $+13.80 | $+0.19 | needs ~1157 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5820 | 217 | 193 | 3 | 99.16c | $-137.06 | $-0.69 | needs ~601 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7040 | 1572 | 1518 | 21 | 98.91c | $-536.03 | $-0.35 | needs ~1195 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4705 | 581 | 555 | 3 | 99.71c | $-152.32 | $-0.27 | needs ~1951 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6931 | 322 | 308 | 2 | 99.02c | $+95.31 | $+0.31 | needs ~242 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2749 | 2733 | 2698 | 194 | 92.86c | $-1078.44 | $-0.43 | needs ~409 more bets with no loss |

