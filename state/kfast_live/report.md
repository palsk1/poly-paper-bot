# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4116 coin-windows from 2026-11-10T10:30 to 2026-11-18T13:15 UTC (588 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4116** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2948 | 248 | 241 | 2 | 99.64c | $-14.05 | $-0.58 | needs ~1910 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2423 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2948 | 124 | 120 | 3 | 99.19c | $-20.58 | $-1.70 | needs ~738 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3528 | 845 | 838 | 14 | 98.88c | $-55.19 | $-0.66 | needs ~1147 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2414 | 325 | 316 | 3 | 99.66c | $-22.80 | $-0.72 | needs ~2608 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3472 | 191 | 188 | 0 | 99.59c | $+5.68 | $+0.30 | needs ~570 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1373 | 1364 | 1357 | 96 | 92.81c | $-43.40 | $-0.34 | needs ~256 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2948 | 248 | 237 | 2 | 99.65c | $-123.02 | $-0.52 | needs ~1401 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2423 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2948 | 124 | 110 | 3 | 99.18c | $-208.82 | $-1.84 | needs ~714 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3528 | 845 | 821 | 14 | 98.92c | $-558.16 | $-0.68 | needs ~1135 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2414 | 325 | 308 | 3 | 99.67c | $-205.28 | $-0.66 | needs ~1874 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3472 | 191 | 182 | 0 | 99.61c | $+67.74 | $+0.36 | needs ~442 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1373 | 1364 | 1348 | 96 | 92.95c | $-555.92 | $-0.44 | needs ~273 more bets with no loss |

