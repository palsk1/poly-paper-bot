# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8663 coin-windows from 2026-11-10T10:30 to 2026-11-28T07:45 UTC (1229 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **144 of 8663** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 226 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6088 | 453 | 439 | 2 | 99.63c | $-8.66 | $-0.20 | needs ~1610 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4976 | 83 | 81 | 0 | 99.79c | $+0.85 | $+0.11 | needs ~2103 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6088 | 236 | 227 | 3 | 99.19c | $-12.08 | $-0.53 | needs ~621 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7371 | 1665 | 1650 | 23 | 98.81c | $-52.16 | $-0.32 | needs ~1163 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4910 | 612 | 596 | 3 | 99.71c | $-18.93 | $-0.32 | needs ~2993 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7256 | 344 | 337 | 2 | 99.03c | $+8.91 | $+0.27 | needs ~276 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2896 | 2880 | 2862 | 203 | 92.68c | $-60.76 | $-0.23 | needs ~345 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6088 | 453 | 427 | 2 | 99.64c | $-55.93 | $-0.13 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4976 | 83 | 78 | 0 | 99.80c | $+14.34 | $+0.18 | needs ~1185 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6088 | 236 | 207 | 3 | 99.18c | $-128.12 | $-0.60 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7371 | 1665 | 1610 | 23 | 98.84c | $-527.01 | $-0.33 | needs ~1131 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4910 | 612 | 585 | 3 | 99.71c | $-145.20 | $-0.25 | needs ~1936 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7256 | 344 | 329 | 2 | 99.04c | $+107.08 | $+0.32 | needs ~234 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2896 | 2880 | 2841 | 203 | 92.81c | $-881.74 | $-0.33 | needs ~380 more bets with no loss |

