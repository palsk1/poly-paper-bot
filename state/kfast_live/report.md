# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2625 coin-windows from 2026-11-10T10:30 to 2026-11-15T13:00 UTC (375 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **44 of 2625** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1890 | 162 | 159 | 1 | 99.79c | $-8.21 | $-0.52 | needs ~3310 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1555 | 31 | 30 | 0 | 99.85c | $+0.15 | $+0.05 | needs ~4568 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1890 | 77 | 75 | 1 | 99.44c | $-5.90 | $-0.78 | needs ~647 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2262 | 529 | 526 | 9 | 99.00c | $-42.71 | $-0.82 | needs ~1056 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1540 | 203 | 195 | 0 | 99.64c | $+4.87 | $+0.25 | needs ~721 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2231 | 125 | 123 | 0 | 99.57c | $+3.92 | $+0.32 | needs ~598 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 867 | 861 | 858 | 56 | 93.06c | $-0.79 | $-0.01 | needs ~160 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1890 | 162 | 156 | 1 | 99.79c | $-70.37 | $-0.45 | needs ~1899 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1555 | 31 | 27 | 0 | 99.85c | $+3.78 | $+0.13 | needs ~1677 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1890 | 77 | 70 | 1 | 99.45c | $-60.74 | $-0.84 | needs ~639 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2262 | 529 | 515 | 9 | 99.04c | $-431.59 | $-0.84 | needs ~1048 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1540 | 203 | 190 | 0 | 99.64c | $+63.15 | $+0.33 | needs ~498 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2231 | 125 | 118 | 0 | 99.59c | $+46.04 | $+0.38 | needs ~481 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 867 | 861 | 852 | 56 | 93.19c | $-83.25 | $-0.10 | needs ~171 more bets with no loss |

