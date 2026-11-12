# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1176 coin-windows from 2026-11-10T10:30 to 2026-11-12T18:45 UTC (168 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **9 of 1176** windows. Reading the Kalshi book takes about 159 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 859 | 62 | 62 | 1 | 99.77c | $-9.22 | $-1.49 | needs ~3047 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 715 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 859 | 30 | 29 | 1 | 99.40c | $-8.30 | $-2.82 | needs ~646 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1029 | 224 | 223 | 4 | 98.90c | $-17.86 | $-0.81 | needs ~582 more bets with no loss |
| Buy now, 60 s left (z 4+) | 707 | 82 | 79 | 0 | 99.60c | $+2.26 | $+0.29 | needs ~725 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1019 | 53 | 53 | 0 | 99.72c | $+0.94 | $+0.18 | needs ~1243 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 368 | 366 | 366 | 19 | 93.62c | $+28.54 | $+0.83 | needs ~65 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 859 | 62 | 62 | 1 | 99.78c | $-87.82 | $-1.42 | needs ~1917 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 715 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 859 | 30 | 27 | 1 | 99.40c | $-83.65 | $-3.00 | needs ~637 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1029 | 224 | 217 | 4 | 98.94c | $-181.79 | $-0.84 | needs ~580 more bets with no loss |
| Buy now, 60 s left (z 4+) | 707 | 82 | 77 | 0 | 99.60c | $+28.35 | $+0.37 | needs ~550 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1019 | 53 | 52 | 0 | 99.72c | $+13.33 | $+0.25 | needs ~860 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 368 | 366 | 365 | 19 | 93.80c | $+244.20 | $+0.71 | needs ~73 more bets with no loss |

