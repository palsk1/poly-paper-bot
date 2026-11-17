# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3801 coin-windows from 2026-11-10T10:30 to 2026-11-17T22:45 UTC (543 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3801** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2725 | 231 | 224 | 2 | 99.63c | $-14.18 | $-0.63 | needs ~1820 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2251 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2725 | 118 | 114 | 3 | 99.17c | $-20.86 | $-1.82 | needs ~727 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3262 | 786 | 779 | 13 | 98.90c | $-52.68 | $-0.68 | needs ~1128 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2250 | 304 | 295 | 3 | 99.65c | $-22.95 | $-0.78 | needs ~2493 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3212 | 179 | 176 | 0 | 99.61c | $+4.93 | $+0.28 | needs ~643 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1265 | 1257 | 1250 | 89 | 92.81c | $-45.53 | $-0.39 | needs ~252 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2725 | 231 | 220 | 2 | 99.64c | $-125.55 | $-0.57 | needs ~1352 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2251 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2725 | 118 | 107 | 3 | 99.17c | $-210.78 | $-1.92 | needs ~709 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3262 | 786 | 764 | 13 | 98.94c | $-531.74 | $-0.70 | needs ~1115 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2250 | 304 | 287 | 3 | 99.66c | $-208.37 | $-0.72 | needs ~1816 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3212 | 179 | 171 | 0 | 99.63c | $+59.69 | $+0.34 | needs ~493 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1265 | 1257 | 1241 | 89 | 92.94c | $-559.47 | $-0.48 | needs ~266 more bets with no loss |

