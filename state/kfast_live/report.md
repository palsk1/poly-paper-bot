# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1057 coin-windows from 2026-11-10T10:30 to 2026-11-12T11:30 UTC (151 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **8 of 1057** windows. Reading the Kalshi book takes about 172 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 769 | 56 | 56 | 1 | 99.76c | $-9.22 | $-1.65 | needs ~2752 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 644 | 16 | 16 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 769 | 29 | 28 | 1 | 99.39c | $-8.35 | $-2.94 | needs ~644 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 921 | 205 | 204 | 4 | 98.88c | $-19.43 | $-0.96 | needs ~589 more bets with no loss |
| Buy now, 60 s left (z 4+) | 637 | 75 | 75 | 0 | 99.58c | $+2.29 | $+0.31 | needs ~680 more bets with no loss |
| Buy now, 30 s left (z 4+) | 916 | 52 | 52 | 0 | 99.72c | $+0.93 | $+0.18 | needs ~1233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 334 | 332 | 332 | 18 | 93.48c | $+22.73 | $+0.73 | needs ~70 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 769 | 56 | 56 | 1 | 99.77c | $-88.36 | $-1.58 | needs ~1814 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 644 | 16 | 16 | 0 | 99.88c | $+1.78 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 769 | 29 | 26 | 1 | 99.40c | $-84.15 | $-3.12 | needs ~635 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 921 | 205 | 199 | 4 | 98.93c | $-196.74 | $-0.99 | needs ~586 more bets with no loss |
| Buy now, 60 s left (z 4+) | 637 | 75 | 73 | 0 | 99.59c | $+28.02 | $+0.38 | needs ~531 more bets with no loss |
| Buy now, 30 s left (z 4+) | 916 | 52 | 51 | 0 | 99.72c | $+13.15 | $+0.25 | needs ~856 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 334 | 332 | 331 | 18 | 93.66c | $+188.62 | $+0.60 | needs ~78 more bets with no loss |

