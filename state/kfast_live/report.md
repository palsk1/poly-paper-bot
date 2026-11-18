# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4081 coin-windows from 2026-11-10T10:30 to 2026-11-18T12:00 UTC (583 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **68 of 4081** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2923 | 247 | 240 | 2 | 99.64c | $-14.05 | $-0.59 | needs ~1902 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2405 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2923 | 124 | 120 | 3 | 99.19c | $-20.58 | $-1.70 | needs ~738 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3499 | 840 | 833 | 14 | 98.89c | $-56.19 | $-0.68 | needs ~1164 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2397 | 324 | 315 | 3 | 99.66c | $-22.82 | $-0.73 | needs ~2608 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3445 | 191 | 188 | 0 | 99.59c | $+5.68 | $+0.30 | needs ~570 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1362 | 1353 | 1346 | 95 | 92.84c | $-44.76 | $-0.36 | needs ~258 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2923 | 247 | 236 | 2 | 99.65c | $-123.11 | $-0.52 | needs ~1397 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2405 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2923 | 124 | 110 | 3 | 99.18c | $-208.82 | $-1.84 | needs ~714 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3499 | 840 | 817 | 14 | 98.92c | $-567.69 | $-0.70 | needs ~1152 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2397 | 324 | 307 | 3 | 99.67c | $-205.55 | $-0.66 | needs ~1874 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3445 | 191 | 182 | 0 | 99.61c | $+67.74 | $+0.36 | needs ~442 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1362 | 1353 | 1337 | 95 | 92.97c | $-565.39 | $-0.45 | needs ~274 more bets with no loss |

