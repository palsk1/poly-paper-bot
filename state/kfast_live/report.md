# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 7602 coin-windows from 2026-11-10T10:30 to 2026-11-26T03:45 UTC (1086 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **124 of 7602** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 230 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5367 | 394 | 383 | 2 | 99.63c | $-9.91 | $-0.26 | needs ~1630 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4402 | 74 | 73 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~1993 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5367 | 191 | 185 | 3 | 99.14c | $-14.66 | $-0.79 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6478 | 1437 | 1422 | 20 | 98.88c | $-55.58 | $-0.39 | needs ~1230 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4359 | 551 | 535 | 3 | 99.70c | $-19.65 | $-0.37 | needs ~2910 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6382 | 300 | 295 | 2 | 99.00c | $+6.16 | $+0.21 | needs ~299 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2517 | 2503 | 2489 | 174 | 92.75c | $-45.27 | $-0.20 | needs ~311 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5367 | 394 | 374 | 2 | 99.63c | $-71.72 | $-0.19 | needs ~1176 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4402 | 74 | 70 | 0 | 99.80c | $+13.17 | $+0.19 | needs ~1167 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5367 | 191 | 172 | 3 | 99.14c | $-151.20 | $-0.86 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6478 | 1437 | 1387 | 20 | 98.90c | $-557.96 | $-0.40 | needs ~1195 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4359 | 551 | 526 | 3 | 99.71c | $-156.85 | $-0.30 | needs ~1923 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6382 | 300 | 288 | 2 | 99.01c | $+78.27 | $+0.27 | needs ~258 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2517 | 2503 | 2473 | 174 | 92.89c | $-674.76 | $-0.29 | needs ~341 more bets with no loss |

