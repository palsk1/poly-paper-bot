# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 763 coin-windows from 2026-11-10T10:30 to 2026-11-11T20:30 UTC (109 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **6 of 763** windows. Reading the Kalshi book takes about 167 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 545 | 33 | 33 | 1 | 99.80c | $-9.66 | $-2.93 | needs ~3793 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 455 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 545 | 20 | 20 | 1 | 99.47c | $-8.98 | $-4.51 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 662 | 145 | 144 | 4 | 98.78c | $-24.00 | $-1.68 | needs ~576 more bets with no loss |
| Buy now, 60 s left (z 4+) | 455 | 52 | 52 | 0 | 99.58c | $+1.60 | $+0.31 | needs ~695 more bets with no loss |
| Buy now, 30 s left (z 4+) | 654 | 36 | 36 | 0 | 99.76c | $+0.50 | $+0.14 | needs ~1618 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 242 | 241 | 241 | 15 | 93.11c | $+5.67 | $+0.25 | needs ~86 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 545 | 33 | 33 | 1 | 99.82c | $-94.48 | $-2.87 | needs ~2292 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 455 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 545 | 20 | 19 | 1 | 99.48c | $-90.22 | $-4.73 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 662 | 145 | 140 | 4 | 98.81c | $-241.35 | $-1.72 | needs ~570 more bets with no loss |
| Buy now, 60 s left (z 4+) | 455 | 52 | 51 | 0 | 99.58c | $+19.81 | $+0.39 | needs ~543 more bets with no loss |
| Buy now, 30 s left (z 4+) | 654 | 36 | 36 | 0 | 99.76c | $+7.78 | $+0.22 | needs ~1028 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 242 | 241 | 240 | 15 | 93.31c | $+25.30 | $+0.11 | needs ~92 more bets with no loss |

