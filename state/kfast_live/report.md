# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2555 coin-windows from 2026-11-10T10:30 to 2026-11-15T08:45 UTC (365 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **44 of 2555** windows. Reading the Kalshi book takes about 134 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1839 | 156 | 153 | 1 | 99.78c | $-8.26 | $-0.54 | needs ~3282 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1515 | 31 | 30 | 0 | 99.85c | $+0.15 | $+0.05 | needs ~4568 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1839 | 74 | 73 | 1 | 99.44c | $-6.04 | $-0.83 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2199 | 515 | 512 | 9 | 98.99c | $-43.47 | $-0.85 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1499 | 197 | 190 | 0 | 99.63c | $+4.86 | $+0.26 | needs ~705 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2171 | 125 | 123 | 0 | 99.57c | $+3.92 | $+0.32 | needs ~598 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 843 | 837 | 834 | 56 | 93.07c | $-17.67 | $-0.23 | needs ~187 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1839 | 156 | 150 | 1 | 99.79c | $-71.36 | $-0.47 | needs ~1895 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1515 | 31 | 27 | 0 | 99.85c | $+3.78 | $+0.13 | needs ~1677 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1839 | 74 | 69 | 1 | 99.45c | $-61.36 | $-0.87 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2199 | 515 | 500 | 9 | 99.03c | $-439.22 | $-0.88 | needs ~1043 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1499 | 197 | 185 | 0 | 99.64c | $+62.53 | $+0.33 | needs ~493 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2171 | 125 | 118 | 0 | 99.59c | $+46.04 | $+0.38 | needs ~481 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 843 | 837 | 828 | 56 | 93.20c | $-252.27 | $-0.32 | needs ~197 more bets with no loss |

