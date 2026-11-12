# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1106 coin-windows from 2026-11-10T10:30 to 2026-11-12T13:15 UTC (158 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **9 of 1106** windows. Reading the Kalshi book takes about 165 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 800 | 58 | 58 | 1 | 99.76c | $-9.22 | $-1.59 | needs ~2851 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 667 | 16 | 16 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 800 | 29 | 28 | 1 | 99.39c | $-8.35 | $-2.94 | needs ~644 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 963 | 213 | 212 | 4 | 98.89c | $-18.76 | $-0.89 | needs ~586 more bets with no loss |
| Buy now, 60 s left (z 4+) | 658 | 75 | 75 | 0 | 99.58c | $+2.29 | $+0.31 | needs ~680 more bets with no loss |
| Buy now, 30 s left (z 4+) | 956 | 53 | 53 | 0 | 99.72c | $+0.94 | $+0.18 | needs ~1243 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 354 | 352 | 352 | 18 | 93.62c | $+30.21 | $+0.91 | needs ~60 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 800 | 58 | 58 | 1 | 99.78c | $-88.18 | $-1.52 | needs ~1849 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 667 | 16 | 16 | 0 | 99.88c | $+1.78 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 800 | 29 | 26 | 1 | 99.40c | $-84.15 | $-3.12 | needs ~635 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 963 | 213 | 206 | 4 | 98.93c | $-190.26 | $-0.92 | needs ~581 more bets with no loss |
| Buy now, 60 s left (z 4+) | 658 | 75 | 73 | 0 | 99.59c | $+28.02 | $+0.38 | needs ~531 more bets with no loss |
| Buy now, 30 s left (z 4+) | 956 | 53 | 52 | 0 | 99.72c | $+13.33 | $+0.25 | needs ~860 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 354 | 352 | 351 | 18 | 93.80c | $+262.16 | $+0.79 | needs ~67 more bets with no loss |

