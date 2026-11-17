# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3822 coin-windows from 2026-11-10T10:30 to 2026-11-17T23:30 UTC (546 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3822** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2741 | 232 | 225 | 2 | 99.63c | $-14.18 | $-0.63 | needs ~1828 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2265 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2741 | 118 | 114 | 3 | 99.17c | $-20.86 | $-1.82 | needs ~727 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3281 | 790 | 783 | 13 | 98.91c | $-52.39 | $-0.67 | needs ~1126 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2264 | 304 | 295 | 3 | 99.65c | $-22.95 | $-0.78 | needs ~2493 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3231 | 180 | 177 | 0 | 99.61c | $+4.96 | $+0.28 | needs ~642 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1271 | 1263 | 1256 | 89 | 92.83c | $-44.24 | $-0.38 | needs ~251 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2741 | 232 | 221 | 2 | 99.64c | $-125.46 | $-0.57 | needs ~1356 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2265 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2741 | 118 | 107 | 3 | 99.17c | $-210.78 | $-1.92 | needs ~709 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3281 | 790 | 768 | 13 | 98.94c | $-529.37 | $-0.69 | needs ~1115 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2264 | 304 | 287 | 3 | 99.66c | $-208.37 | $-0.72 | needs ~1816 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3231 | 180 | 172 | 0 | 99.63c | $+60.06 | $+0.34 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1271 | 1263 | 1247 | 89 | 92.96c | $-547.60 | $-0.47 | needs ~265 more bets with no loss |

