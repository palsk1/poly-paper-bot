# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5649 coin-windows from 2026-11-10T10:30 to 2026-11-21T17:30 UTC (807 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **95 of 5649** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4006 | 308 | 298 | 2 | 99.67c | $-13.32 | $-0.45 | needs ~2069 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3286 | 53 | 52 | 0 | 99.79c | $+0.55 | $+0.11 | needs ~2112 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4006 | 154 | 150 | 3 | 99.23c | $-18.88 | $-1.25 | needs ~756 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4816 | 1090 | 1082 | 16 | 98.91c | $-53.25 | $-0.50 | needs ~1188 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3272 | 414 | 401 | 3 | 99.68c | $-21.47 | $-0.54 | needs ~2736 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4751 | 236 | 233 | 0 | 99.62c | $+6.33 | $+0.27 | needs ~611 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1878 | 1868 | 1858 | 125 | 92.70c | $+24.32 | $+0.14 | needs ~175 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4006 | 308 | 291 | 2 | 99.67c | $-111.10 | $-0.38 | needs ~1452 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3286 | 53 | 49 | 0 | 99.80c | $+9.00 | $+0.18 | needs ~1227 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4006 | 154 | 140 | 3 | 99.23c | $-191.74 | $-1.34 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4816 | 1090 | 1058 | 16 | 98.94c | $-534.93 | $-0.50 | needs ~1163 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3272 | 414 | 393 | 3 | 99.69c | $-185.53 | $-0.47 | needs ~1902 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4751 | 236 | 227 | 0 | 99.64c | $+77.58 | $+0.34 | needs ~450 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1878 | 1868 | 1845 | 125 | 92.84c | $+74.23 | $+0.04 | needs ~196 more bets with no loss |

