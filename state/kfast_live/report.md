# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5614 coin-windows from 2026-11-10T10:30 to 2026-11-21T13:45 UTC (802 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **94 of 5614** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3989 | 307 | 297 | 2 | 99.67c | $-13.33 | $-0.45 | needs ~2065 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3272 | 53 | 52 | 0 | 99.79c | $+0.55 | $+0.11 | needs ~2112 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3989 | 154 | 150 | 3 | 99.23c | $-18.88 | $-1.25 | needs ~756 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4790 | 1080 | 1072 | 16 | 98.92c | $-56.13 | $-0.53 | needs ~1240 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3257 | 410 | 397 | 3 | 99.68c | $-21.54 | $-0.54 | needs ~2734 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4728 | 236 | 233 | 0 | 99.62c | $+6.33 | $+0.27 | needs ~611 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1859 | 1849 | 1839 | 124 | 92.74c | $+14.67 | $+0.09 | needs ~189 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3989 | 307 | 290 | 2 | 99.67c | $-111.28 | $-0.38 | needs ~1450 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3272 | 53 | 49 | 0 | 99.80c | $+9.00 | $+0.18 | needs ~1227 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3989 | 154 | 140 | 3 | 99.23c | $-191.74 | $-1.34 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4790 | 1080 | 1048 | 16 | 98.96c | $-563.33 | $-0.54 | needs ~1213 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3257 | 410 | 389 | 3 | 99.69c | $-186.53 | $-0.48 | needs ~1903 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4728 | 236 | 227 | 0 | 99.64c | $+77.58 | $+0.34 | needs ~450 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1859 | 1849 | 1826 | 124 | 92.87c | $-20.34 | $-0.01 | needs ~211 more bets with no loss |

