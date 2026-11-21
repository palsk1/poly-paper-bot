# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5754 coin-windows from 2026-11-10T10:30 to 2026-11-21T21:15 UTC (822 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **97 of 5754** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4071 | 315 | 305 | 2 | 99.67c | $-13.15 | $-0.43 | needs ~2057 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3336 | 55 | 54 | 0 | 99.78c | $+0.61 | $+0.11 | needs ~1973 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4071 | 157 | 153 | 3 | 99.24c | $-18.70 | $-1.22 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4907 | 1115 | 1106 | 16 | 98.91c | $-51.40 | $-0.47 | needs ~1175 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3318 | 422 | 409 | 3 | 99.68c | $-21.20 | $-0.52 | needs ~2693 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4839 | 242 | 239 | 0 | 99.59c | $+7.16 | $+0.30 | needs ~526 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1919 | 1908 | 1897 | 126 | 92.76c | $+31.27 | $+0.18 | needs ~166 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4071 | 315 | 298 | 2 | 99.67c | $-108.98 | $-0.36 | needs ~1445 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3336 | 55 | 51 | 0 | 99.80c | $+9.66 | $+0.19 | needs ~1185 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4071 | 157 | 143 | 3 | 99.23c | $-189.91 | $-1.30 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4907 | 1115 | 1081 | 16 | 98.94c | $-515.77 | $-0.48 | needs ~1148 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3318 | 422 | 401 | 3 | 99.68c | $-182.53 | $-0.45 | needs ~1880 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4839 | 242 | 233 | 0 | 99.61c | $+86.35 | $+0.37 | needs ~390 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1919 | 1908 | 1884 | 126 | 92.89c | $+144.19 | $+0.08 | needs ~187 more bets with no loss |

