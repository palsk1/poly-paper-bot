# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 854 coin-windows from 2026-11-10T10:30 to 2026-11-11T23:45 UTC (122 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **7 of 854** windows. Reading the Kalshi book takes about 150 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 621 | 39 | 39 | 1 | 99.73c | $-9.33 | $-2.40 | needs ~2240 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 522 | 11 | 11 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 621 | 24 | 24 | 1 | 99.38c | $-8.57 | $-3.59 | needs ~628 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 745 | 160 | 159 | 4 | 98.79c | $-22.48 | $-1.42 | needs ~567 more bets with no loss |
| Buy now, 60 s left (z 4+) | 518 | 55 | 55 | 0 | 99.53c | $+1.93 | $+0.35 | needs ~600 more bets with no loss |
| Buy now, 30 s left (z 4+) | 737 | 40 | 40 | 0 | 99.73c | $+0.65 | $+0.16 | needs ~1374 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 263 | 262 | 262 | 16 | 93.21c | $+6.78 | $+0.28 | needs ~88 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 621 | 39 | 39 | 1 | 99.74c | $-90.85 | $-2.33 | needs ~1618 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 522 | 11 | 11 | 0 | 99.90c | $+1.01 | $+0.09 | needs ~2486 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 621 | 24 | 23 | 1 | 99.38c | $-86.06 | $-3.74 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 745 | 160 | 154 | 4 | 98.82c | $-226.00 | $-1.46 | needs ~558 more bets with no loss |
| Buy now, 60 s left (z 4+) | 518 | 55 | 54 | 0 | 99.54c | $+23.26 | $+0.43 | needs ~482 more bets with no loss |
| Buy now, 30 s left (z 4+) | 737 | 40 | 40 | 0 | 99.74c | $+9.55 | $+0.24 | needs ~923 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 263 | 262 | 261 | 16 | 93.40c | $+34.98 | $+0.14 | needs ~95 more bets with no loss |

