# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3892 coin-windows from 2026-11-10T10:30 to 2026-11-18T03:15 UTC (556 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3892** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2801 | 235 | 228 | 2 | 99.64c | $-14.18 | $-0.62 | needs ~1852 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2313 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2801 | 119 | 115 | 3 | 99.18c | $-20.81 | $-1.80 | needs ~728 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3347 | 801 | 794 | 13 | 98.91c | $-51.53 | $-0.65 | needs ~1121 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2316 | 311 | 302 | 3 | 99.65c | $-22.93 | $-0.76 | needs ~2544 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3296 | 181 | 178 | 0 | 99.61c | $+4.96 | $+0.28 | needs ~646 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1284 | 1276 | 1269 | 90 | 92.81c | $-42.93 | $-0.36 | needs ~250 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2801 | 235 | 224 | 2 | 99.64c | $-125.19 | $-0.56 | needs ~1369 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2313 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2801 | 119 | 108 | 3 | 99.17c | $-210.28 | $-1.90 | needs ~710 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3347 | 801 | 779 | 13 | 98.94c | $-520.66 | $-0.67 | needs ~1110 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2316 | 311 | 294 | 3 | 99.66c | $-207.64 | $-0.70 | needs ~1843 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3296 | 181 | 173 | 0 | 99.63c | $+60.15 | $+0.34 | needs ~494 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1284 | 1276 | 1260 | 90 | 92.94c | $-540.29 | $-0.46 | needs ~265 more bets with no loss |

