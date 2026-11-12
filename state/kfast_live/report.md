# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 917 coin-windows from 2026-11-10T10:30 to 2026-11-12T03:00 UTC (131 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **7 of 917** windows. Reading the Kalshi book takes about 162 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 670 | 42 | 42 | 1 | 99.73c | $-9.29 | $-2.22 | needs ~2273 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 563 | 12 | 12 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 670 | 26 | 26 | 1 | 99.38c | $-8.48 | $-3.28 | needs ~638 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 798 | 170 | 169 | 4 | 98.78c | $-21.24 | $-1.27 | needs ~551 more bets with no loss |
| Buy now, 60 s left (z 4+) | 553 | 62 | 62 | 0 | 99.57c | $+1.97 | $+0.32 | needs ~662 more bets with no loss |
| Buy now, 30 s left (z 4+) | 791 | 43 | 43 | 0 | 99.72c | $+0.78 | $+0.18 | needs ~1224 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 280 | 279 | 279 | 16 | 93.11c | $+20.35 | $+0.78 | needs ~66 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 670 | 42 | 42 | 1 | 99.75c | $-90.21 | $-2.15 | needs ~1625 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 563 | 12 | 12 | 0 | 99.90c | $+1.10 | $+0.09 | needs ~2490 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 670 | 26 | 24 | 1 | 99.39c | $-85.17 | $-3.42 | needs ~630 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 798 | 170 | 164 | 4 | 98.81c | $-214.14 | $-1.30 | needs ~545 more bets with no loss |
| Buy now, 60 s left (z 4+) | 553 | 62 | 60 | 0 | 99.57c | $+24.21 | $+0.40 | needs ~516 more bets with no loss |
| Buy now, 30 s left (z 4+) | 791 | 43 | 42 | 0 | 99.72c | $+11.02 | $+0.26 | needs ~852 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 280 | 279 | 278 | 16 | 93.30c | $+167.42 | $+0.64 | needs ~72 more bets with no loss |

