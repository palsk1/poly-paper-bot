# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3423 coin-windows from 2026-11-10T10:30 to 2026-11-17T03:15 UTC (489 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **53 of 3423** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2435 | 217 | 213 | 2 | 99.63c | $-14.33 | $-0.67 | needs ~1784 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2002 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2435 | 111 | 107 | 3 | 99.15c | $-21.20 | $-1.96 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2922 | 719 | 714 | 13 | 98.89c | $-58.17 | $-0.82 | needs ~1169 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1987 | 275 | 266 | 3 | 99.63c | $-23.15 | $-0.87 | needs ~2321 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2881 | 167 | 165 | 0 | 99.60c | $+4.82 | $+0.29 | needs ~621 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1170 | 1163 | 1159 | 83 | 92.72c | $-37.29 | $-0.35 | needs ~234 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2435 | 217 | 209 | 2 | 99.63c | $-128.08 | $-0.61 | needs ~1340 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2002 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2435 | 111 | 100 | 3 | 99.15c | $-214.29 | $-2.09 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2922 | 719 | 702 | 13 | 98.92c | $-585.05 | $-0.83 | needs ~1156 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1987 | 275 | 259 | 3 | 99.64c | $-212.33 | $-0.81 | needs ~1726 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2881 | 167 | 160 | 0 | 99.62c | $+57.68 | $+0.35 | needs ~485 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1170 | 1163 | 1151 | 83 | 92.85c | $-467.29 | $-0.43 | needs ~246 more bets with no loss |

