# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 539 coin-windows from 2026-11-10T10:30 to 2026-11-11T10:45 UTC (77 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 539** windows. Reading the Kalshi book takes about 193 ms (slowest 1 in 10: 251 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 400 | 27 | 27 | 1 | 99.80c | $-9.72 | $-3.60 | needs ~3723 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 340 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 400 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 478 | 103 | 102 | 3 | 98.97c | $-20.55 | $-2.02 | needs ~621 more bets with no loss |
| Buy now, 60 s left (z 4+) | 342 | 45 | 45 | 0 | 99.56c | $+1.49 | $+0.33 | needs ~649 more bets with no loss |
| Buy now, 30 s left (z 4+) | 468 | 24 | 24 | 0 | 99.79c | $+0.26 | $+0.11 | needs ~2093 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 161 | 160 | 160 | 10 | 93.17c | $+2.63 | $+0.18 | needs ~78 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 400 | 27 | 27 | 1 | 99.81c | $-95.41 | $-3.54 | needs ~2258 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 340 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 400 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 478 | 103 | 99 | 3 | 99.02c | $-206.76 | $-2.06 | needs ~620 more bets with no loss |
| Buy now, 60 s left (z 4+) | 342 | 45 | 44 | 0 | 99.56c | $+18.17 | $+0.41 | needs ~515 more bets with no loss |
| Buy now, 30 s left (z 4+) | 468 | 24 | 24 | 0 | 99.79c | $+4.49 | $+0.19 | needs ~1205 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 161 | 160 | 159 | 10 | 93.35c | $+8.04 | $+0.05 | needs ~82 more bets with no loss |

