# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4137 coin-windows from 2026-11-10T10:30 to 2026-11-18T14:00 UTC (591 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4137** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2962 | 249 | 241 | 2 | 99.64c | $-14.06 | $-0.58 | needs ~1913 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2435 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2962 | 124 | 120 | 3 | 99.19c | $-20.58 | $-1.70 | needs ~738 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3543 | 846 | 839 | 14 | 98.88c | $-55.06 | $-0.66 | needs ~1146 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2426 | 328 | 319 | 3 | 99.66c | $-22.79 | $-0.72 | needs ~2629 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3487 | 191 | 188 | 0 | 99.59c | $+5.68 | $+0.30 | needs ~570 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1381 | 1372 | 1364 | 96 | 92.79c | $-35.31 | $-0.28 | needs ~242 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2962 | 249 | 237 | 2 | 99.65c | $-123.02 | $-0.52 | needs ~1400 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2435 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2962 | 124 | 110 | 3 | 99.18c | $-208.82 | $-1.84 | needs ~714 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3543 | 846 | 822 | 14 | 98.92c | $-556.88 | $-0.68 | needs ~1133 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2426 | 328 | 311 | 3 | 99.67c | $-204.92 | $-0.65 | needs ~1883 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3487 | 191 | 182 | 0 | 99.61c | $+67.74 | $+0.36 | needs ~442 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1381 | 1372 | 1355 | 96 | 92.92c | $-477.58 | $-0.38 | needs ~259 more bets with no loss |

