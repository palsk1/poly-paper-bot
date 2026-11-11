# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 728 coin-windows from 2026-11-10T10:30 to 2026-11-11T19:15 UTC (104 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **5 of 728** windows. Reading the Kalshi book takes about 173 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 519 | 32 | 32 | 1 | 99.80c | $-9.66 | $-3.02 | needs ~3678 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 435 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 519 | 19 | 19 | 1 | 99.47c | $-9.03 | $-4.78 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 631 | 139 | 138 | 4 | 98.74c | $-24.19 | $-1.77 | needs ~560 more bets with no loss |
| Buy now, 60 s left (z 4+) | 436 | 51 | 51 | 0 | 99.58c | $+1.57 | $+0.31 | needs ~696 more bets with no loss |
| Buy now, 30 s left (z 4+) | 624 | 36 | 36 | 0 | 99.76c | $+0.50 | $+0.14 | needs ~1618 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 234 | 233 | 233 | 14 | 93.09c | $+10.99 | $+0.50 | needs ~75 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 519 | 32 | 32 | 1 | 99.81c | $-94.57 | $-2.96 | needs ~2260 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 435 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 519 | 19 | 18 | 1 | 99.48c | $-90.72 | $-5.02 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 631 | 139 | 134 | 4 | 98.78c | $-243.40 | $-1.81 | needs ~555 more bets with no loss |
| Buy now, 60 s left (z 4+) | 436 | 51 | 50 | 0 | 99.58c | $+19.44 | $+0.39 | needs ~544 more bets with no loss |
| Buy now, 30 s left (z 4+) | 624 | 36 | 36 | 0 | 99.76c | $+7.78 | $+0.22 | needs ~1028 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 234 | 233 | 232 | 14 | 93.29c | $+78.53 | $+0.36 | needs ~81 more bets with no loss |

