# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3227 coin-windows from 2026-11-10T10:30 to 2026-11-16T18:00 UTC (461 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3227** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2312 | 213 | 210 | 2 | 99.63c | $-14.45 | $-0.69 | needs ~1804 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1899 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2312 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2763 | 676 | 671 | 12 | 98.96c | $-56.94 | $-0.85 | needs ~1220 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1890 | 262 | 253 | 3 | 99.62c | $-23.21 | $-0.92 | needs ~2229 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2727 | 162 | 160 | 0 | 99.60c | $+4.72 | $+0.30 | needs ~619 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1094 | 1087 | 1084 | 77 | 92.75c | $-31.62 | $-0.31 | needs ~222 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2312 | 213 | 206 | 2 | 99.63c | $-129.50 | $-0.63 | needs ~1353 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1899 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2312 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2763 | 676 | 660 | 12 | 98.99c | $-572.61 | $-0.87 | needs ~1209 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1890 | 262 | 246 | 3 | 99.63c | $-214.05 | $-0.86 | needs ~1678 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2727 | 162 | 155 | 0 | 99.61c | $+56.40 | $+0.36 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1094 | 1087 | 1077 | 77 | 92.88c | $-406.59 | $-0.40 | needs ~233 more bets with no loss |

