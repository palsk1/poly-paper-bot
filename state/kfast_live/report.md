# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8438 coin-windows from 2026-11-10T10:30 to 2026-11-28T00:45 UTC (1204 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **142 of 8438** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5935 | 434 | 421 | 2 | 99.63c | $-8.93 | $-0.21 | needs ~1593 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4854 | 79 | 77 | 0 | 99.79c | $+0.84 | $+0.11 | needs ~2024 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5935 | 228 | 219 | 3 | 99.18c | $-12.55 | $-0.57 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7182 | 1612 | 1597 | 23 | 98.82c | $-59.82 | $-0.38 | needs ~1249 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4795 | 592 | 576 | 3 | 99.71c | $-19.20 | $-0.33 | needs ~2977 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7070 | 331 | 325 | 2 | 99.00c | $+8.58 | $+0.27 | needs ~273 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2810 | 2794 | 2777 | 198 | 92.70c | $-74.38 | $-0.29 | needs ~364 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5935 | 434 | 409 | 2 | 99.64c | $-60.01 | $-0.14 | needs ~1144 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4854 | 79 | 74 | 0 | 99.80c | $+13.89 | $+0.19 | needs ~1164 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5935 | 228 | 201 | 3 | 99.17c | $-132.04 | $-0.64 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7182 | 1612 | 1558 | 23 | 98.85c | $-603.68 | $-0.39 | needs ~1216 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4795 | 592 | 566 | 3 | 99.71c | $-149.16 | $-0.26 | needs ~1936 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7070 | 331 | 317 | 2 | 99.02c | $+103.47 | $+0.32 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2810 | 2794 | 2757 | 198 | 92.83c | $-1008.56 | $-0.39 | needs ~399 more bets with no loss |

