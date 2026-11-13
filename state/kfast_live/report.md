# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1442 coin-windows from 2026-11-10T10:30 to 2026-11-13T06:30 UTC (206 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **18 of 1442** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1041 | 83 | 83 | 1 | 99.79c | $-9.10 | $-1.10 | needs ~3522 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 858 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1041 | 36 | 35 | 1 | 99.42c | $-8.00 | $-2.26 | needs ~655 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1254 | 282 | 281 | 4 | 98.91c | $-12.37 | $-0.44 | needs ~531 more bets with no loss |
| Buy now, 60 s left (z 4+) | 848 | 108 | 104 | 0 | 99.64c | $+2.55 | $+0.25 | needs ~831 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1238 | 65 | 65 | 0 | 99.43c | $+2.92 | $+0.45 | needs ~447 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 466 | 463 | 463 | 23 | 93.59c | $+47.71 | $+1.10 | needs ~41 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1041 | 83 | 81 | 1 | 99.80c | $-85.08 | $-1.05 | needs ~2034 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 858 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1041 | 36 | 32 | 1 | 99.42c | $-80.72 | $-2.39 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1254 | 282 | 275 | 4 | 98.95c | $-126.50 | $-0.46 | needs ~528 more bets with no loss |
| Buy now, 60 s left (z 4+) | 848 | 108 | 101 | 0 | 99.65c | $+32.99 | $+0.32 | needs ~605 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1238 | 65 | 63 | 0 | 99.47c | $+32.02 | $+0.50 | needs ~400 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 466 | 463 | 461 | 23 | 93.75c | $+430.80 | $+0.99 | needs ~49 more bets with no loss |

