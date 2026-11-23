# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6433 coin-windows from 2026-11-10T10:30 to 2026-11-23T06:45 UTC (919 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **107 of 6433** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4539 | 362 | 351 | 2 | 99.61c | $-10.13 | $-0.29 | needs ~1534 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3710 | 66 | 65 | 0 | 99.77c | $+0.80 | $+0.12 | needs ~1797 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4539 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5485 | 1250 | 1237 | 18 | 98.85c | $-51.14 | $-0.42 | needs ~1129 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3684 | 497 | 482 | 3 | 99.69c | $-20.11 | $-0.42 | needs ~2767 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5407 | 270 | 267 | 1 | 99.18c | $+8.79 | $+0.33 | needs ~282 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2166 | 2153 | 2140 | 142 | 92.96c | $-4.59 | $-0.02 | needs ~237 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4539 | 362 | 343 | 2 | 99.61c | $-76.30 | $-0.22 | needs ~1130 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3710 | 66 | 62 | 0 | 99.78c | $+12.36 | $+0.20 | needs ~1108 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4539 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5485 | 1250 | 1210 | 18 | 98.88c | $-514.18 | $-0.42 | needs ~1104 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3684 | 497 | 473 | 3 | 99.69c | $-165.82 | $-0.35 | needs ~1878 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5407 | 270 | 261 | 1 | 99.20c | $+104.57 | $+0.40 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2166 | 2153 | 2126 | 142 | 93.09c | $-226.43 | $-0.11 | needs ~261 more bets with no loss |

