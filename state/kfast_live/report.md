# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1841 coin-windows from 2026-11-10T10:30 to 2026-11-13T23:15 UTC (263 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **25 of 1841** windows. Reading the Kalshi book takes about 166 ms (slowest 1 in 10: 249 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1329 | 102 | 101 | 1 | 99.78c | $-8.82 | $-0.87 | needs ~3241 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1098 | 21 | 21 | 0 | 99.84c | $+0.13 | $+0.06 | needs ~3698 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1329 | 43 | 42 | 1 | 99.42c | $-7.64 | $-1.81 | needs ~658 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1595 | 344 | 343 | 4 | 98.91c | $-6.29 | $-0.18 | needs ~469 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1090 | 133 | 128 | 0 | 99.65c | $+3.03 | $+0.24 | needs ~840 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1577 | 80 | 80 | 0 | 99.50c | $+3.10 | $+0.39 | needs ~515 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 590 | 586 | 585 | 33 | 93.38c | $+33.35 | $+0.61 | needs ~81 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1329 | 102 | 99 | 1 | 99.79c | $-81.00 | $-0.82 | needs ~1929 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1098 | 21 | 19 | 0 | 99.84c | $+2.73 | $+0.14 | needs ~1599 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1329 | 43 | 38 | 1 | 99.42c | $-77.43 | $-1.94 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1595 | 344 | 335 | 4 | 98.95c | $-67.49 | $-0.20 | needs ~468 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1090 | 133 | 125 | 0 | 99.66c | $+39.50 | $+0.31 | needs ~602 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1577 | 80 | 77 | 0 | 99.52c | $+34.73 | $+0.44 | needs ~443 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 590 | 586 | 580 | 33 | 93.51c | $+278.36 | $+0.51 | needs ~88 more bets with no loss |

