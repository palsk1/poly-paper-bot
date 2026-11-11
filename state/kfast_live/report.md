# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 525 coin-windows from 2026-11-10T10:30 to 2026-11-11T10:15 UTC (75 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 525** windows. Reading the Kalshi book takes about 193 ms (slowest 1 in 10: 252 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 390 | 25 | 25 | 1 | 99.81c | $-9.77 | $-3.91 | needs ~4202 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 332 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 390 | 17 | 17 | 1 | 99.47c | $-9.13 | $-5.40 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 466 | 100 | 99 | 3 | 98.96c | $-20.65 | $-2.09 | needs ~610 more bets with no loss |
| Buy now, 60 s left (z 4+) | 335 | 45 | 45 | 0 | 99.56c | $+1.49 | $+0.33 | needs ~649 more bets with no loss |
| Buy now, 30 s left (z 4+) | 457 | 23 | 23 | 0 | 99.79c | $+0.26 | $+0.11 | needs ~2005 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 155 | 154 | 154 | 10 | 93.05c | $+0.63 | $+0.04 | needs ~80 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 390 | 25 | 25 | 1 | 99.83c | $-96.05 | $-3.85 | needs ~2433 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 332 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 390 | 17 | 16 | 1 | 99.48c | $-91.77 | $-5.71 | needs ~747 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 466 | 100 | 96 | 3 | 99.00c | $-207.88 | $-2.14 | needs ~610 more bets with no loss |
| Buy now, 60 s left (z 4+) | 335 | 45 | 44 | 0 | 99.56c | $+18.17 | $+0.41 | needs ~515 more bets with no loss |
| Buy now, 30 s left (z 4+) | 457 | 23 | 23 | 0 | 99.79c | $+4.40 | $+0.19 | needs ~1179 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 155 | 154 | 153 | 10 | 93.22c | $-10.86 | $-0.08 | needs ~83 more bets with no loss |

