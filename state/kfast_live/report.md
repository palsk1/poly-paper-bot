# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8618 coin-windows from 2026-11-10T10:30 to 2026-11-28T06:30 UTC (1224 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **143 of 8618** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6066 | 447 | 433 | 2 | 99.63c | $-8.74 | $-0.20 | needs ~1603 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4963 | 83 | 81 | 0 | 99.79c | $+0.85 | $+0.11 | needs ~2103 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6066 | 234 | 225 | 3 | 99.18c | $-12.19 | $-0.54 | needs ~621 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7341 | 1653 | 1638 | 23 | 98.81c | $-52.54 | $-0.32 | needs ~1161 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4898 | 607 | 591 | 3 | 99.71c | $-18.95 | $-0.32 | needs ~2974 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7225 | 341 | 335 | 2 | 99.02c | $+8.90 | $+0.27 | needs ~275 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2869 | 2853 | 2835 | 201 | 92.71c | $-68.83 | $-0.26 | needs ~358 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6066 | 447 | 421 | 2 | 99.64c | $-57.21 | $-0.13 | needs ~1145 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4963 | 83 | 78 | 0 | 99.80c | $+14.34 | $+0.18 | needs ~1185 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6066 | 234 | 206 | 3 | 99.18c | $-128.85 | $-0.60 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7341 | 1653 | 1598 | 23 | 98.84c | $-531.16 | $-0.33 | needs ~1129 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4898 | 607 | 580 | 3 | 99.71c | $-145.79 | $-0.25 | needs ~1929 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7225 | 341 | 327 | 2 | 99.04c | $+106.81 | $+0.32 | needs ~234 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2869 | 2853 | 2814 | 201 | 92.85c | $-959.98 | $-0.36 | needs ~392 more bets with no loss |

