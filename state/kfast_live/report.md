# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2380 coin-windows from 2026-11-10T10:30 to 2026-11-14T21:30 UTC (340 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **39 of 2380** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1715 | 141 | 139 | 1 | 99.78c | $-8.35 | $-0.60 | needs ~3144 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1416 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1715 | 65 | 64 | 1 | 99.43c | $-6.49 | $-1.01 | needs ~650 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2056 | 467 | 464 | 7 | 98.96c | $-26.36 | $-0.57 | needs ~788 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1402 | 181 | 174 | 0 | 99.62c | $+4.66 | $+0.27 | needs ~679 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2031 | 114 | 112 | 0 | 99.54c | $+3.87 | $+0.35 | needs ~552 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 778 | 771 | 769 | 52 | 93.32c | $-38.25 | $-0.53 | needs ~223 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1715 | 141 | 137 | 1 | 99.79c | $-73.45 | $-0.54 | needs ~1869 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1416 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1715 | 65 | 59 | 1 | 99.44c | $-66.09 | $-1.08 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2056 | 467 | 452 | 7 | 98.99c | $-268.39 | $-0.59 | needs ~779 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1402 | 181 | 169 | 0 | 99.62c | $+59.42 | $+0.35 | needs ~483 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2031 | 114 | 107 | 0 | 99.56c | $+44.68 | $+0.41 | needs ~454 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 778 | 771 | 764 | 52 | 93.44c | $-445.22 | $-0.62 | needs ~232 more bets with no loss |

