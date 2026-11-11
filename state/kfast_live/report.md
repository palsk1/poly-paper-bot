# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 609 coin-windows from 2026-11-10T10:30 to 2026-11-11T13:15 UTC (87 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 609** windows. Reading the Kalshi book takes about 186 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 438 | 30 | 30 | 1 | 99.80c | $-9.69 | $-3.23 | needs ~3733 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 371 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 438 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 531 | 121 | 120 | 3 | 98.75c | $-16.28 | $-1.37 | needs ~465 more bets with no loss |
| Buy now, 60 s left (z 4+) | 372 | 47 | 47 | 0 | 99.57c | $+1.51 | $+0.32 | needs ~669 more bets with no loss |
| Buy now, 30 s left (z 4+) | 523 | 31 | 31 | 0 | 99.76c | $+0.43 | $+0.14 | needs ~1625 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 196 | 195 | 195 | 10 | 93.12c | $+26.03 | $+1.43 | needs ~41 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 438 | 30 | 30 | 1 | 99.81c | $-94.94 | $-3.17 | needs ~2274 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 371 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 438 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 531 | 121 | 116 | 3 | 98.78c | $-163.73 | $-1.40 | needs ~458 more bets with no loss |
| Buy now, 60 s left (z 4+) | 372 | 47 | 46 | 0 | 99.57c | $+18.53 | $+0.40 | needs ~527 more bets with no loss |
| Buy now, 30 s left (z 4+) | 523 | 31 | 31 | 0 | 99.76c | $+6.69 | $+0.22 | needs ~1035 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 196 | 195 | 194 | 10 | 93.29c | $+237.57 | $+1.30 | needs ~45 more bets with no loss |

