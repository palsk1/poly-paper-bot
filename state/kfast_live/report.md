# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5404 coin-windows from 2026-11-10T10:30 to 2026-11-21T04:30 UTC (772 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **89 of 5404** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3848 | 302 | 292 | 2 | 99.66c | $-13.38 | $-0.46 | needs ~2048 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3152 | 52 | 51 | 0 | 99.79c | $+0.53 | $+0.10 | needs ~2151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3848 | 150 | 146 | 3 | 99.23c | $-19.08 | $-1.30 | needs ~753 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4623 | 1050 | 1042 | 16 | 98.92c | $-58.06 | $-0.56 | needs ~1248 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3130 | 401 | 388 | 3 | 99.68c | $-21.83 | $-0.56 | needs ~2781 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4555 | 229 | 226 | 0 | 99.61c | $+6.26 | $+0.28 | needs ~602 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1784 | 1775 | 1765 | 120 | 92.71c | $+9.32 | $+0.06 | needs ~193 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3848 | 302 | 285 | 2 | 99.67c | $-112.18 | $-0.39 | needs ~1443 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3152 | 52 | 48 | 0 | 99.80c | $+8.73 | $+0.18 | needs ~1241 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3848 | 150 | 136 | 3 | 99.22c | $-193.74 | $-1.39 | needs ~732 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4623 | 1050 | 1020 | 16 | 98.95c | $-583.60 | $-0.57 | needs ~1225 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3130 | 401 | 380 | 3 | 99.69c | $-189.95 | $-0.50 | needs ~1929 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4555 | 229 | 220 | 0 | 99.63c | $+76.36 | $+0.34 | needs ~447 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1784 | 1775 | 1752 | 120 | 92.84c | $-69.27 | $-0.04 | needs ~213 more bets with no loss |

