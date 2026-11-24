# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6874 coin-windows from 2026-11-10T10:30 to 2026-11-24T11:30 UTC (982 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **112 of 6874** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 232 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4863 | 379 | 368 | 2 | 99.62c | $-10.04 | $-0.27 | needs ~1591 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3972 | 72 | 71 | 0 | 99.79c | $+0.80 | $+0.11 | needs ~1963 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4863 | 176 | 170 | 3 | 99.11c | $-15.40 | $-0.90 | needs ~610 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5866 | 1313 | 1299 | 18 | 98.86c | $-46.80 | $-0.36 | needs ~1104 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3945 | 522 | 506 | 3 | 99.69c | $-19.98 | $-0.39 | needs ~2859 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5783 | 284 | 279 | 1 | 99.21c | $+8.83 | $+0.32 | needs ~292 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2291 | 2278 | 2265 | 154 | 92.92c | $-34.15 | $-0.16 | needs ~289 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4863 | 379 | 360 | 2 | 99.63c | $-74.02 | $-0.20 | needs ~1157 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3972 | 72 | 68 | 0 | 99.79c | $+12.90 | $+0.19 | needs ~1160 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4863 | 176 | 159 | 3 | 99.10c | $-158.28 | $-0.98 | needs ~594 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5866 | 1313 | 1269 | 18 | 98.90c | $-470.59 | $-0.37 | needs ~1076 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3945 | 522 | 497 | 3 | 99.70c | $-162.38 | $-0.32 | needs ~1910 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5783 | 284 | 273 | 1 | 99.22c | $+106.18 | $+0.39 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2291 | 2278 | 2250 | 154 | 93.05c | $-535.06 | $-0.25 | needs ~315 more bets with no loss |

