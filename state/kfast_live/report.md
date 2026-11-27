# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8204 coin-windows from 2026-11-10T10:30 to 2026-11-27T13:15 UTC (1172 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **137 of 8204** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5776 | 417 | 404 | 2 | 99.62c | $-9.22 | $-0.23 | needs ~1581 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4732 | 77 | 75 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2047 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5776 | 214 | 205 | 3 | 99.16c | $-13.28 | $-0.64 | needs ~617 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6983 | 1559 | 1544 | 21 | 98.88c | $-54.58 | $-0.36 | needs ~1244 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4669 | 579 | 563 | 3 | 99.71c | $-19.44 | $-0.35 | needs ~2990 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6872 | 319 | 313 | 2 | 98.99c | $+7.80 | $+0.25 | needs ~279 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2723 | 2707 | 2691 | 191 | 92.75c | $-76.14 | $-0.30 | needs ~366 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5776 | 417 | 393 | 2 | 99.63c | $-63.91 | $-0.16 | needs ~1141 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4732 | 77 | 72 | 0 | 99.80c | $+13.43 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5776 | 214 | 190 | 3 | 99.15c | $-138.56 | $-0.71 | needs ~599 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6983 | 1559 | 1505 | 21 | 98.91c | $-548.98 | $-0.36 | needs ~1207 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4669 | 579 | 553 | 3 | 99.71c | $-152.50 | $-0.27 | needs ~1947 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6872 | 319 | 305 | 2 | 99.01c | $+94.95 | $+0.31 | needs ~240 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2723 | 2707 | 2673 | 191 | 92.88c | $-1008.75 | $-0.40 | needs ~399 more bets with no loss |

