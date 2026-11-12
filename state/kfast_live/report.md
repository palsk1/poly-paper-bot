# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1302 coin-windows from 2026-11-10T10:30 to 2026-11-12T23:30 UTC (186 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **16 of 1302** windows. Reading the Kalshi book takes about 154 ms (slowest 1 in 10: 237 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 940 | 73 | 73 | 1 | 99.78c | $-9.13 | $-1.25 | needs ~3207 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 775 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 940 | 32 | 31 | 1 | 99.40c | $-8.20 | $-2.61 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1134 | 258 | 257 | 4 | 98.87c | $-13.83 | $-0.54 | needs ~527 more bets with no loss |
| Buy now, 60 s left (z 4+) | 766 | 93 | 90 | 0 | 99.61c | $+2.51 | $+0.28 | needs ~733 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1118 | 60 | 60 | 0 | 99.65c | $+1.49 | $+0.25 | needs ~865 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 421 | 419 | 419 | 22 | 93.67c | $+28.19 | $+0.72 | needs ~73 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 940 | 73 | 73 | 1 | 99.79c | $-86.07 | $-1.18 | needs ~1965 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 775 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 940 | 32 | 28 | 1 | 99.41c | $-82.72 | $-2.78 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1134 | 258 | 251 | 4 | 98.91c | $-141.77 | $-0.56 | needs ~526 more bets with no loss |
| Buy now, 60 s left (z 4+) | 766 | 93 | 88 | 0 | 99.62c | $+31.38 | $+0.35 | needs ~559 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1118 | 60 | 58 | 0 | 99.67c | $+17.96 | $+0.30 | needs ~705 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 421 | 419 | 418 | 22 | 93.84c | $+237.58 | $+0.60 | needs ~82 more bets with no loss |

