# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2520 coin-windows from 2026-11-10T10:30 to 2026-11-15T07:30 UTC (360 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **44 of 2520** windows. Reading the Kalshi book takes about 135 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1812 | 154 | 151 | 1 | 99.78c | $-8.27 | $-0.55 | needs ~3259 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1492 | 31 | 30 | 0 | 99.85c | $+0.15 | $+0.05 | needs ~4568 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1812 | 74 | 73 | 1 | 99.44c | $-6.04 | $-0.83 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2168 | 510 | 507 | 9 | 98.99c | $-43.56 | $-0.86 | needs ~1045 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1480 | 196 | 189 | 0 | 99.63c | $+4.86 | $+0.26 | needs ~701 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2139 | 123 | 121 | 0 | 99.57c | $+3.91 | $+0.32 | needs ~590 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 833 | 827 | 824 | 56 | 93.05c | $-22.36 | $-0.29 | needs ~193 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1812 | 154 | 148 | 1 | 99.79c | $-71.63 | $-0.48 | needs ~1889 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1492 | 31 | 27 | 0 | 99.85c | $+3.78 | $+0.13 | needs ~1677 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1812 | 74 | 69 | 1 | 99.45c | $-61.36 | $-0.87 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2168 | 510 | 496 | 9 | 99.02c | $-440.33 | $-0.89 | needs ~1039 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1480 | 196 | 184 | 0 | 99.64c | $+62.44 | $+0.34 | needs ~491 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2139 | 123 | 116 | 0 | 99.58c | $+45.77 | $+0.38 | needs ~477 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 833 | 827 | 818 | 56 | 93.18c | $-299.31 | $-0.39 | needs ~204 more bets with no loss |

