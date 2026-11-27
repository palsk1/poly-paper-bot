# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8134 coin-windows from 2026-11-10T10:30 to 2026-11-27T08:45 UTC (1162 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **135 of 8134** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5737 | 414 | 402 | 2 | 99.62c | $-9.30 | $-0.23 | needs ~1589 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4704 | 77 | 75 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2047 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5737 | 212 | 203 | 3 | 99.16c | $-13.41 | $-0.66 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6923 | 1539 | 1524 | 21 | 98.88c | $-56.12 | $-0.37 | needs ~1256 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4639 | 573 | 557 | 3 | 99.70c | $-19.50 | $-0.35 | needs ~2978 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6815 | 316 | 310 | 2 | 98.99c | $+7.74 | $+0.25 | needs ~278 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2693 | 2677 | 2662 | 189 | 92.71c | $-66.87 | $-0.27 | needs ~350 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5737 | 414 | 391 | 2 | 99.63c | $-64.91 | $-0.16 | needs ~1148 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4704 | 77 | 72 | 0 | 99.80c | $+13.43 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5737 | 212 | 188 | 3 | 99.15c | $-139.89 | $-0.72 | needs ~600 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6923 | 1539 | 1485 | 21 | 98.91c | $-565.30 | $-0.38 | needs ~1220 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4639 | 573 | 548 | 3 | 99.71c | $-153.56 | $-0.28 | needs ~1945 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6815 | 316 | 302 | 2 | 99.00c | $+94.12 | $+0.31 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2693 | 2677 | 2644 | 189 | 92.85c | $-915.62 | $-0.37 | needs ~382 more bets with no loss |

