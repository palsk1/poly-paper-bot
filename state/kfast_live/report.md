# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2240 coin-windows from 2026-11-10T10:30 to 2026-11-14T16:00 UTC (320 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **36 of 2240** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1626 | 135 | 133 | 1 | 99.78c | $-8.39 | $-0.63 | needs ~3086 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1350 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1626 | 62 | 61 | 1 | 99.43c | $-6.63 | $-1.08 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1947 | 438 | 435 | 7 | 98.92c | $-27.37 | $-0.63 | needs ~767 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1341 | 172 | 166 | 0 | 99.61c | $+4.62 | $+0.28 | needs ~656 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1924 | 108 | 106 | 0 | 99.52c | $+3.87 | $+0.37 | needs ~523 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 721 | 716 | 714 | 43 | 93.57c | $+0.07 | $+0.00 | needs ~155 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1626 | 135 | 131 | 1 | 99.78c | $-74.31 | $-0.57 | needs ~1852 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1350 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1626 | 62 | 57 | 1 | 99.43c | $-67.32 | $-1.14 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1947 | 438 | 425 | 7 | 98.95c | $-278.62 | $-0.65 | needs ~761 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1341 | 172 | 161 | 0 | 99.61c | $+58.26 | $+0.36 | needs ~474 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1924 | 108 | 101 | 0 | 99.54c | $+44.14 | $+0.42 | needs ~436 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 721 | 716 | 709 | 43 | 93.70c | $-59.61 | $-0.09 | needs ~163 more bets with no loss |

