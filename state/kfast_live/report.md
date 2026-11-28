# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8753 coin-windows from 2026-11-10T10:30 to 2026-11-28T10:15 UTC (1239 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **148 of 8753** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 226 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6147 | 461 | 447 | 2 | 99.64c | $-8.60 | $-0.19 | needs ~1629 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5020 | 84 | 82 | 0 | 99.79c | $+0.85 | $+0.10 | needs ~2129 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6147 | 240 | 230 | 3 | 99.19c | $-11.88 | $-0.51 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7443 | 1683 | 1667 | 24 | 98.80c | $-57.78 | $-0.35 | needs ~1210 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4951 | 616 | 600 | 3 | 99.71c | $-18.91 | $-0.32 | needs ~3006 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7327 | 345 | 338 | 2 | 99.03c | $+8.91 | $+0.27 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2933 | 2917 | 2899 | 206 | 92.67c | $-62.47 | $-0.23 | needs ~349 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6147 | 461 | 434 | 2 | 99.64c | $-54.86 | $-0.12 | needs ~1154 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5020 | 84 | 79 | 0 | 99.80c | $+14.43 | $+0.18 | needs ~1193 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6147 | 240 | 210 | 3 | 99.18c | $-126.57 | $-0.58 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7443 | 1683 | 1627 | 24 | 98.82c | $-582.99 | $-0.36 | needs ~1177 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4951 | 616 | 588 | 3 | 99.71c | $-144.75 | $-0.24 | needs ~1939 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7327 | 345 | 330 | 2 | 99.04c | $+107.17 | $+0.32 | needs ~235 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2933 | 2917 | 2877 | 206 | 92.80c | $-907.03 | $-0.34 | needs ~385 more bets with no loss |

