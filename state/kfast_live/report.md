# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8169 coin-windows from 2026-11-10T10:30 to 2026-11-27T12:00 UTC (1167 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **136 of 8169** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 228 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5761 | 416 | 403 | 2 | 99.62c | $-9.30 | $-0.23 | needs ~1592 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4721 | 77 | 75 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2047 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5761 | 213 | 204 | 3 | 99.16c | $-13.36 | $-0.65 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6955 | 1549 | 1534 | 21 | 98.89c | $-55.92 | $-0.37 | needs ~1260 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4658 | 576 | 560 | 3 | 99.70c | $-19.45 | $-0.35 | needs ~2977 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6844 | 316 | 310 | 2 | 98.99c | $+7.74 | $+0.25 | needs ~278 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2706 | 2690 | 2674 | 189 | 92.74c | $-65.06 | $-0.26 | needs ~348 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5761 | 416 | 392 | 2 | 99.63c | $-64.74 | $-0.16 | needs ~1148 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4721 | 77 | 72 | 0 | 99.80c | $+13.43 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5761 | 213 | 189 | 3 | 99.15c | $-139.39 | $-0.72 | needs ~600 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6955 | 1549 | 1495 | 21 | 98.92c | $-562.64 | $-0.38 | needs ~1224 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4658 | 576 | 550 | 3 | 99.71c | $-152.86 | $-0.28 | needs ~1943 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6844 | 316 | 302 | 2 | 99.00c | $+94.12 | $+0.31 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2706 | 2690 | 2656 | 189 | 92.87c | $-897.83 | $-0.36 | needs ~380 more bets with no loss |

