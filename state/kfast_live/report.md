# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6398 coin-windows from 2026-11-10T10:30 to 2026-11-23T05:30 UTC (914 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **106 of 6398** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4512 | 358 | 347 | 2 | 99.61c | $-10.16 | $-0.29 | needs ~1522 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3688 | 64 | 63 | 0 | 99.77c | $+0.80 | $+0.13 | needs ~1742 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4512 | 169 | 164 | 3 | 99.10c | $-15.71 | $-0.96 | needs ~605 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5454 | 1246 | 1233 | 18 | 98.84c | $-51.26 | $-0.42 | needs ~1128 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3662 | 493 | 478 | 3 | 99.69c | $-20.12 | $-0.42 | needs ~2747 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5377 | 270 | 267 | 1 | 99.18c | $+8.79 | $+0.33 | needs ~282 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2155 | 2142 | 2129 | 141 | 92.95c | $-0.20 | $-0.00 | needs ~229 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4512 | 358 | 339 | 2 | 99.61c | $-76.94 | $-0.23 | needs ~1124 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3688 | 64 | 60 | 0 | 99.78c | $+12.18 | $+0.20 | needs ~1089 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4512 | 169 | 154 | 3 | 99.09c | $-160.85 | $-1.02 | needs ~591 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5454 | 1246 | 1206 | 18 | 98.88c | $-515.45 | $-0.43 | needs ~1103 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3662 | 493 | 469 | 3 | 99.69c | $-166.27 | $-0.35 | needs ~1870 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5377 | 270 | 261 | 1 | 99.20c | $+104.57 | $+0.40 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2155 | 2142 | 2115 | 141 | 93.08c | $-183.13 | $-0.09 | needs ~253 more bets with no loss |

