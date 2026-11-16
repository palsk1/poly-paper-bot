# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3010 coin-windows from 2026-11-10T10:30 to 2026-11-16T05:45 UTC (430 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3010** windows. Reading the Kalshi book takes about 147 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2148 | 201 | 198 | 2 | 99.61c | $-14.52 | $-0.73 | needs ~1725 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1755 | 42 | 41 | 0 | 99.80c | $+0.39 | $+0.10 | needs ~2359 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2148 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2569 | 636 | 631 | 12 | 98.98c | $-62.12 | $-0.99 | needs ~1307 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1748 | 242 | 234 | 3 | 99.61c | $-23.48 | $-1.00 | needs ~2157 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2537 | 157 | 155 | 0 | 99.60c | $+4.49 | $+0.29 | needs ~638 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1031 | 1024 | 1021 | 75 | 92.76c | $-55.19 | $-0.58 | needs ~255 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2148 | 201 | 194 | 2 | 99.62c | $-131.16 | $-0.67 | needs ~1310 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1755 | 42 | 38 | 0 | 99.81c | $+6.58 | $+0.17 | needs ~1323 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2148 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2569 | 636 | 620 | 12 | 99.02c | $-624.20 | $-1.01 | needs ~1294 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1748 | 242 | 227 | 3 | 99.61c | $-218.00 | $-0.95 | needs ~1637 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2537 | 157 | 150 | 0 | 99.62c | $+53.85 | $+0.35 | needs ~498 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1031 | 1024 | 1014 | 75 | 92.89c | $-639.69 | $-0.67 | needs ~266 more bets with no loss |

