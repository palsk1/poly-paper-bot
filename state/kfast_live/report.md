# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 224 coin-windows from 2026-11-10T10:30 to 2026-11-10T20:30 UTC (32 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **0 of 224** windows. Reading the Kalshi book takes about 175 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 158 | 9 | 9 | 0 | 99.77c | $+0.12 | $+0.13 | needs ~1717 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 134 | 3 | 3 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 158 | 2 | 2 | 0 | 99.25c | $+0.14 | $+0.70 | needs ~326 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 197 | 40 | 40 | 0 | 99.15c | $+3.00 | $+0.76 | needs ~267 more bets with no loss |
| Buy now, 60 s left (z 4+) | 136 | 14 | 14 | 0 | 99.79c | $+0.15 | $+0.11 | needs ~2120 more bets with no loss |
| Buy now, 30 s left (z 4+) | 198 | 13 | 13 | 0 | 99.83c | $+0.09 | $+0.07 | needs ~3312 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 70 | 70 | 70 | 2 | 94.25c | $+17.71 | $+2.67 | needs ~28 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 158 | 9 | 9 | 0 | 99.79c | $+1.68 | $+0.19 | needs ~1223 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 134 | 3 | 3 | 0 | 99.90c | $+0.27 | $+0.09 | needs ~2555 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 158 | 2 | 2 | 0 | 99.37c | $+1.19 | $+0.60 | needs ~384 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 197 | 40 | 40 | 0 | 99.23c | $+28.52 | $+0.72 | needs ~282 more bets with no loss |
| Buy now, 60 s left (z 4+) | 136 | 14 | 13 | 0 | 99.79c | $+2.54 | $+0.19 | needs ~1187 more bets with no loss |
| Buy now, 30 s left (z 4+) | 198 | 13 | 13 | 0 | 99.83c | $+1.99 | $+0.15 | needs ~1491 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 70 | 70 | 69 | 2 | 94.40c | $+170.54 | $+2.58 | needs ~29 more bets with no loss |

