# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8771 coin-windows from 2026-11-10T10:30 to 2026-11-28T10:45 UTC (1241 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **148 of 8771** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 226 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6159 | 462 | 447 | 2 | 99.64c | $-8.61 | $-0.19 | needs ~1630 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5030 | 84 | 82 | 0 | 99.79c | $+0.85 | $+0.10 | needs ~2129 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6159 | 240 | 230 | 3 | 99.19c | $-11.88 | $-0.51 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7459 | 1686 | 1670 | 24 | 98.80c | $-57.58 | $-0.35 | needs ~1209 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4961 | 618 | 602 | 3 | 99.71c | $-18.89 | $-0.31 | needs ~3010 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7343 | 345 | 338 | 2 | 99.03c | $+8.91 | $+0.27 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2940 | 2924 | 2905 | 206 | 92.68c | $-61.20 | $-0.23 | needs ~347 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6159 | 462 | 434 | 2 | 99.64c | $-54.87 | $-0.12 | needs ~1153 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5030 | 84 | 79 | 0 | 99.80c | $+14.43 | $+0.18 | needs ~1193 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6159 | 240 | 210 | 3 | 99.18c | $-126.57 | $-0.58 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7459 | 1686 | 1630 | 24 | 98.83c | $-580.89 | $-0.36 | needs ~1175 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4961 | 618 | 590 | 3 | 99.71c | $-144.39 | $-0.24 | needs ~1939 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7343 | 345 | 330 | 2 | 99.04c | $+107.17 | $+0.32 | needs ~235 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2940 | 2924 | 2883 | 206 | 92.81c | $-894.10 | $-0.33 | needs ~382 more bets with no loss |

