# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 644 coin-windows from 2026-11-10T10:30 to 2026-11-11T14:30 UTC (92 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **4 of 644** windows. Reading the Kalshi book takes about 182 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 465 | 30 | 30 | 1 | 99.80c | $-9.69 | $-3.23 | needs ~3733 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 394 | 8 | 8 | 0 | 99.90c | $+0.00 | $+0.00 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 465 | 18 | 18 | 1 | 99.47c | $-9.08 | $-5.07 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 564 | 125 | 124 | 3 | 98.78c | $-16.19 | $-1.31 | needs ~477 more bets with no loss |
| Buy now, 60 s left (z 4+) | 395 | 49 | 49 | 0 | 99.57c | $+1.54 | $+0.32 | needs ~683 more bets with no loss |
| Buy now, 30 s left (z 4+) | 557 | 32 | 32 | 0 | 99.77c | $+0.43 | $+0.13 | needs ~1677 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 203 | 202 | 202 | 10 | 93.33c | $+26.46 | $+1.40 | needs ~42 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 465 | 30 | 30 | 1 | 99.81c | $-94.94 | $-3.17 | needs ~2274 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 394 | 8 | 8 | 0 | 99.90c | $+0.72 | $+0.09 | needs ~2550 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 465 | 18 | 17 | 1 | 99.48c | $-91.22 | $-5.34 | needs ~742 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 564 | 125 | 120 | 3 | 98.81c | $-162.55 | $-1.34 | needs ~468 more bets with no loss |
| Buy now, 60 s left (z 4+) | 395 | 49 | 48 | 0 | 99.57c | $+18.98 | $+0.39 | needs ~536 more bets with no loss |
| Buy now, 30 s left (z 4+) | 557 | 32 | 32 | 0 | 99.77c | $+6.78 | $+0.21 | needs ~1054 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 203 | 202 | 201 | 10 | 93.50c | $+242.18 | $+1.28 | needs ~46 more bets with no loss |

