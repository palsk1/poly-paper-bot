# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 574 coin-windows from 2026-11-10T10:30 to 2026-11-11T12:00 UTC (82 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 574** windows. Reading the Kalshi book takes about 191 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 418 | 29 | 29 | 1 | 99.80c | $-9.70 | $-3.35 | needs ~3730 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 354 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 418 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 502 | 112 | 111 | 3 | 99.00c | $-19.97 | $-1.81 | needs ~630 more bets with no loss |
| Buy now, 60 s left (z 4+) | 356 | 47 | 47 | 0 | 99.57c | $+1.51 | $+0.32 | needs ~669 more bets with no loss |
| Buy now, 30 s left (z 4+) | 493 | 28 | 28 | 0 | 99.75c | $+0.41 | $+0.15 | needs ~1540 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 180 | 179 | 179 | 10 | 93.21c | $+14.22 | $+0.85 | needs ~60 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 418 | 29 | 29 | 1 | 99.81c | $-95.12 | $-3.29 | needs ~2280 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 354 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 418 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 502 | 112 | 107 | 3 | 99.03c | $-200.90 | $-1.85 | needs ~624 more bets with no loss |
| Buy now, 60 s left (z 4+) | 356 | 47 | 46 | 0 | 99.57c | $+18.53 | $+0.40 | needs ~527 more bets with no loss |
| Buy now, 30 s left (z 4+) | 493 | 28 | 28 | 0 | 99.76c | $+6.24 | $+0.22 | needs ~1004 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 180 | 179 | 178 | 10 | 93.38c | $+121.19 | $+0.72 | needs ~64 more bets with no loss |

