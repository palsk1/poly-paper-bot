# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3185 coin-windows from 2026-11-10T10:30 to 2026-11-16T12:30 UTC (455 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 3185** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2287 | 213 | 210 | 2 | 99.63c | $-14.45 | $-0.69 | needs ~1804 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1876 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2287 | 107 | 104 | 3 | 99.15c | $-21.39 | $-2.05 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2726 | 665 | 660 | 12 | 98.96c | $-58.26 | $-0.89 | needs ~1240 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1868 | 262 | 253 | 3 | 99.62c | $-23.21 | $-0.92 | needs ~2229 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2691 | 160 | 158 | 0 | 99.60c | $+4.61 | $+0.29 | needs ~629 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1079 | 1072 | 1069 | 76 | 92.76c | $-32.57 | $-0.33 | needs ~222 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2287 | 213 | 206 | 2 | 99.63c | $-129.50 | $-0.63 | needs ~1353 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1876 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2287 | 107 | 97 | 3 | 99.14c | $-216.23 | $-2.17 | needs ~693 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2726 | 665 | 649 | 12 | 99.00c | $-585.79 | $-0.90 | needs ~1228 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1868 | 262 | 246 | 3 | 99.63c | $-214.05 | $-0.86 | needs ~1678 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2691 | 160 | 153 | 0 | 99.62c | $+55.20 | $+0.35 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1079 | 1072 | 1062 | 76 | 92.89c | $-415.99 | $-0.42 | needs ~234 more bets with no loss |

