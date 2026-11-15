# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2450 coin-windows from 2026-11-10T10:30 to 2026-11-15T05:00 UTC (350 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **43 of 2450** windows. Reading the Kalshi book takes about 135 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1760 | 146 | 143 | 1 | 99.78c | $-8.34 | $-0.58 | needs ~3223 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1456 | 30 | 29 | 0 | 99.84c | $+0.15 | $+0.05 | needs ~4416 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1760 | 69 | 68 | 1 | 99.44c | $-6.29 | $-0.92 | needs ~649 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2109 | 483 | 480 | 9 | 98.95c | $-44.34 | $-0.93 | needs ~1015 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1442 | 187 | 180 | 0 | 99.62c | $+4.72 | $+0.26 | needs ~692 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2082 | 119 | 117 | 0 | 99.56c | $+3.90 | $+0.33 | needs ~572 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 807 | 801 | 798 | 56 | 93.03c | $-37.94 | $-0.51 | needs ~217 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1760 | 146 | 141 | 1 | 99.79c | $-72.96 | $-0.52 | needs ~1885 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1456 | 30 | 27 | 0 | 99.85c | $+3.71 | $+0.14 | needs ~1661 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1760 | 69 | 64 | 1 | 99.44c | $-63.86 | $-0.97 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2109 | 483 | 469 | 9 | 98.99c | $-448.80 | $-0.95 | needs ~1010 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1442 | 187 | 175 | 0 | 99.63c | $+60.43 | $+0.34 | needs ~489 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2082 | 119 | 112 | 0 | 99.57c | $+45.32 | $+0.39 | needs ~467 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 807 | 801 | 793 | 56 | 93.16c | $-453.42 | $-0.61 | needs ~227 more bets with no loss |

