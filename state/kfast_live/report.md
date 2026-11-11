# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 490 coin-windows from 2026-11-10T10:30 to 2026-11-11T09:00 UTC (70 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 490** windows. Reading the Kalshi book takes about 194 ms (slowest 1 in 10: 251 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 364 | 24 | 24 | 0 | 99.80c | $+0.23 | $+0.10 | needs ~2378 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 311 | 7 | 7 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 364 | 16 | 16 | 0 | 99.47c | $+0.82 | $+0.52 | needs ~433 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 434 | 93 | 92 | 1 | 98.93c | $-1.07 | $-0.12 | needs ~309 more bets with no loss |
| Buy now, 60 s left (z 4+) | 314 | 43 | 43 | 0 | 99.54c | $+1.47 | $+0.34 | needs ~629 more bets with no loss |
| Buy now, 30 s left (z 4+) | 428 | 22 | 22 | 0 | 99.78c | $+0.26 | $+0.12 | needs ~1918 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 145 | 144 | 144 | 8 | 92.98c | $+14.97 | $+1.11 | needs ~51 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 364 | 24 | 24 | 0 | 99.82c | $+3.86 | $+0.16 | needs ~1405 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 311 | 7 | 7 | 0 | 99.90c | $+0.63 | $+0.09 | needs ~2551 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 364 | 16 | 15 | 0 | 99.48c | $+7.73 | $+0.51 | needs ~435 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 434 | 93 | 89 | 1 | 98.97c | $-12.16 | $-0.13 | needs ~310 more bets with no loss |
| Buy now, 60 s left (z 4+) | 314 | 43 | 42 | 0 | 99.54c | $+17.81 | $+0.42 | needs ~503 more bets with no loss |
| Buy now, 30 s left (z 4+) | 428 | 22 | 22 | 0 | 99.78c | $+4.31 | $+0.20 | needs ~1152 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 145 | 144 | 143 | 8 | 93.16c | $+133.18 | $+0.99 | needs ~54 more bets with no loss |

