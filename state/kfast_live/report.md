# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2450 coin-windows from 2026-11-10T10:30 to 2026-11-15T02:00 UTC (350 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **41 of 2450** windows. Reading the Kalshi book takes about 135 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1770 | 142 | 140 | 1 | 99.78c | $-8.39 | $-0.60 | needs ~3249 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1467 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1770 | 67 | 66 | 1 | 99.43c | $-6.38 | $-0.96 | needs ~647 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2114 | 477 | 474 | 7 | 98.97c | $-25.78 | $-0.55 | needs ~789 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1451 | 187 | 180 | 0 | 99.63c | $+4.65 | $+0.26 | needs ~705 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2089 | 115 | 113 | 0 | 99.54c | $+3.88 | $+0.34 | needs ~555 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 793 | 787 | 785 | 54 | 93.11c | $-32.44 | $-0.44 | needs ~209 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1770 | 142 | 138 | 1 | 99.79c | $-73.68 | $-0.53 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1467 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1770 | 67 | 61 | 1 | 99.44c | $-65.05 | $-1.03 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2114 | 477 | 462 | 7 | 99.00c | $-263.33 | $-0.57 | needs ~783 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1451 | 187 | 175 | 0 | 99.63c | $+59.87 | $+0.34 | needs ~495 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2089 | 115 | 108 | 0 | 99.56c | $+44.86 | $+0.40 | needs ~456 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 793 | 787 | 780 | 54 | 93.24c | $-395.49 | $-0.54 | needs ~219 more bets with no loss |

