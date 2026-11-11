# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 679 coin-windows from 2026-11-10T10:30 to 2026-11-11T15:45 UTC (97 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 679** windows. Reading the Kalshi book takes about 178 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 488 | 31 | 31 | 1 | 99.80c | $-9.69 | $-3.13 | needs ~3858 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 411 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 488 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 595 | 134 | 133 | 3 | 98.81c | $-15.64 | $-1.18 | needs ~486 more bets with no loss |
| Buy now, 60 s left (z 4+) | 412 | 49 | 49 | 0 | 99.57c | $+1.54 | $+0.32 | needs ~683 more bets with no loss |
| Buy now, 30 s left (z 4+) | 588 | 34 | 34 | 0 | 99.76c | $+0.47 | $+0.14 | needs ~1628 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 216 | 215 | 215 | 11 | 93.53c | $+20.57 | $+1.02 | needs ~56 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 488 | 31 | 31 | 1 | 99.82c | $-94.85 | $-3.06 | needs ~2308 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 411 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 488 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 595 | 134 | 129 | 3 | 98.84c | $-156.75 | $-1.21 | needs ~477 more bets with no loss |
| Buy now, 60 s left (z 4+) | 412 | 49 | 48 | 0 | 99.57c | $+18.98 | $+0.39 | needs ~536 more bets with no loss |
| Buy now, 30 s left (z 4+) | 588 | 34 | 34 | 0 | 99.76c | $+7.32 | $+0.22 | needs ~1034 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 216 | 215 | 214 | 11 | 93.70c | $+181.81 | $+0.90 | needs ~61 more bets with no loss |

