# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6587 coin-windows from 2026-11-10T10:30 to 2026-11-23T14:45 UTC (941 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **108 of 6587** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 233 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4643 | 372 | 361 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1568 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3793 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4643 | 171 | 166 | 3 | 99.10c | $-15.61 | $-0.94 | needs ~607 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5614 | 1277 | 1263 | 18 | 98.85c | $-49.05 | $-0.39 | needs ~1114 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3766 | 512 | 497 | 3 | 99.69c | $-19.99 | $-0.40 | needs ~2812 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5535 | 280 | 277 | 1 | 99.21c | $+8.85 | $+0.32 | needs ~291 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2224 | 2211 | 2198 | 147 | 92.97c | $-18.55 | $-0.09 | needs ~262 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4643 | 372 | 353 | 2 | 99.62c | $-75.01 | $-0.21 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3793 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4643 | 171 | 156 | 3 | 99.10c | $-159.85 | $-1.00 | needs ~593 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5614 | 1277 | 1235 | 18 | 98.88c | $-492.82 | $-0.40 | needs ~1087 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3766 | 512 | 488 | 3 | 99.70c | $-163.36 | $-0.33 | needs ~1894 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5535 | 280 | 271 | 1 | 99.22c | $+106.02 | $+0.39 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2224 | 2211 | 2184 | 147 | 93.10c | $-373.16 | $-0.18 | needs ~288 more bets with no loss |

