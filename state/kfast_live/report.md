# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1092 coin-windows from 2026-11-10T10:30 to 2026-11-12T12:45 UTC (156 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **9 of 1092** windows. Reading the Kalshi book takes about 167 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 791 | 56 | 56 | 1 | 99.76c | $-9.22 | $-1.65 | needs ~2752 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 664 | 16 | 16 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 791 | 29 | 28 | 1 | 99.39c | $-8.35 | $-2.94 | needs ~644 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 951 | 211 | 210 | 4 | 98.89c | $-19.00 | $-0.91 | needs ~589 more bets with no loss |
| Buy now, 60 s left (z 4+) | 656 | 75 | 75 | 0 | 99.58c | $+2.29 | $+0.31 | needs ~680 more bets with no loss |
| Buy now, 30 s left (z 4+) | 945 | 53 | 53 | 0 | 99.72c | $+0.94 | $+0.18 | needs ~1243 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 347 | 345 | 345 | 18 | 93.56c | $+28.01 | $+0.86 | needs ~63 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 791 | 56 | 56 | 1 | 99.77c | $-88.36 | $-1.58 | needs ~1814 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 664 | 16 | 16 | 0 | 99.88c | $+1.78 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 791 | 29 | 26 | 1 | 99.40c | $-84.15 | $-3.12 | needs ~635 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 951 | 211 | 205 | 4 | 98.94c | $-192.62 | $-0.94 | needs ~587 more bets with no loss |
| Buy now, 60 s left (z 4+) | 656 | 75 | 73 | 0 | 99.59c | $+28.02 | $+0.38 | needs ~531 more bets with no loss |
| Buy now, 30 s left (z 4+) | 945 | 53 | 52 | 0 | 99.72c | $+13.33 | $+0.25 | needs ~860 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 347 | 345 | 344 | 18 | 93.74c | $+240.63 | $+0.74 | needs ~70 more bets with no loss |

