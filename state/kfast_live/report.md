# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1750 coin-windows from 2026-11-10T10:30 to 2026-11-13T20:00 UTC (250 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **25 of 1750** windows. Reading the Kalshi book takes about 175 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1258 | 97 | 96 | 1 | 99.79c | $-8.92 | $-0.93 | needs ~3376 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1035 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1258 | 41 | 40 | 1 | 99.43c | $-7.77 | $-1.93 | needs ~666 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1514 | 329 | 328 | 4 | 98.89c | $-7.27 | $-0.22 | needs ~472 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1030 | 128 | 123 | 0 | 99.66c | $+2.79 | $+0.23 | needs ~888 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1494 | 74 | 74 | 0 | 99.47c | $+3.04 | $+0.41 | needs ~485 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 566 | 562 | 561 | 32 | 93.26c | $+34.83 | $+0.66 | needs ~76 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1258 | 97 | 94 | 1 | 99.79c | $-82.28 | $-0.87 | needs ~1971 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1035 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1258 | 41 | 36 | 1 | 99.43c | $-78.69 | $-2.07 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1514 | 329 | 320 | 4 | 98.93c | $-77.55 | $-0.24 | needs ~471 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1030 | 128 | 120 | 0 | 99.67c | $+36.86 | $+0.31 | needs ~628 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1494 | 74 | 71 | 0 | 99.50c | $+33.75 | $+0.46 | needs ~423 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 566 | 562 | 557 | 32 | 93.39c | $+292.65 | $+0.56 | needs ~83 more bets with no loss |

