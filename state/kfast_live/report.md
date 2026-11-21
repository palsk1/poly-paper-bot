# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5523 coin-windows from 2026-11-10T10:30 to 2026-11-21T10:30 UTC (789 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **92 of 5523** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3922 | 304 | 294 | 2 | 99.67c | $-13.36 | $-0.45 | needs ~2055 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3214 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3922 | 152 | 148 | 3 | 99.23c | $-18.98 | $-1.28 | needs ~755 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4713 | 1067 | 1059 | 16 | 98.93c | $-57.40 | $-0.55 | needs ~1253 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3197 | 406 | 393 | 3 | 99.68c | $-21.82 | $-0.55 | needs ~2813 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4651 | 233 | 230 | 0 | 99.62c | $+6.30 | $+0.27 | needs ~607 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1832 | 1822 | 1812 | 123 | 92.71c | $+12.15 | $+0.07 | needs ~191 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3922 | 304 | 287 | 2 | 99.67c | $-111.82 | $-0.39 | needs ~1446 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3214 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3922 | 152 | 138 | 3 | 99.23c | $-192.74 | $-1.36 | needs ~734 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4713 | 1067 | 1036 | 16 | 98.96c | $-576.44 | $-0.56 | needs ~1228 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3197 | 406 | 385 | 3 | 99.69c | $-189.41 | $-0.49 | needs ~1943 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4651 | 233 | 224 | 0 | 99.63c | $+77.09 | $+0.34 | needs ~448 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1832 | 1822 | 1799 | 123 | 92.84c | $-44.57 | $-0.03 | needs ~212 more bets with no loss |

