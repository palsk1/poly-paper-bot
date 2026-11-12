# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1022 coin-windows from 2026-11-10T10:30 to 2026-11-12T10:15 UTC (146 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **8 of 1022** windows. Reading the Kalshi book takes about 176 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 739 | 54 | 54 | 1 | 99.75c | $-9.22 | $-1.71 | needs ~2654 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 616 | 16 | 16 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 739 | 29 | 28 | 1 | 99.39c | $-8.35 | $-2.94 | needs ~644 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 889 | 203 | 202 | 4 | 98.87c | $-19.45 | $-0.97 | needs ~584 more bets with no loss |
| Buy now, 60 s left (z 4+) | 608 | 72 | 72 | 0 | 99.57c | $+2.28 | $+0.32 | needs ~656 more bets with no loss |
| Buy now, 30 s left (z 4+) | 883 | 51 | 51 | 0 | 99.72c | $+0.93 | $+0.18 | needs ~1210 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 327 | 325 | 325 | 18 | 93.41c | $+20.73 | $+0.68 | needs ~73 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 739 | 54 | 54 | 1 | 99.77c | $-88.54 | $-1.64 | needs ~1778 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 616 | 16 | 16 | 0 | 99.88c | $+1.78 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 739 | 29 | 26 | 1 | 99.40c | $-84.15 | $-3.12 | needs ~635 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 889 | 203 | 197 | 4 | 98.92c | $-197.10 | $-1.00 | needs ~582 more bets with no loss |
| Buy now, 60 s left (z 4+) | 608 | 72 | 70 | 0 | 99.58c | $+27.66 | $+0.39 | needs ~517 more bets with no loss |
| Buy now, 30 s left (z 4+) | 883 | 51 | 50 | 0 | 99.72c | $+13.06 | $+0.26 | needs ~845 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 327 | 325 | 324 | 18 | 93.59c | $+168.17 | $+0.55 | needs ~81 more bets with no loss |

