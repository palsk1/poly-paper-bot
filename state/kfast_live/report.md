# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1211 coin-windows from 2026-11-10T10:30 to 2026-11-12T20:00 UTC (173 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **9 of 1211** windows. Reading the Kalshi book takes about 158 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 886 | 65 | 65 | 1 | 99.77c | $-9.17 | $-1.41 | needs ~2997 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 735 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 886 | 31 | 30 | 1 | 99.40c | $-8.25 | $-2.72 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1061 | 234 | 233 | 4 | 98.92c | $-17.29 | $-0.75 | needs ~587 more bets with no loss |
| Buy now, 60 s left (z 4+) | 725 | 86 | 83 | 0 | 99.60c | $+2.35 | $+0.28 | needs ~727 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1050 | 54 | 54 | 0 | 99.71c | $+1.01 | $+0.19 | needs ~1175 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 379 | 377 | 377 | 20 | 93.69c | $+22.90 | $+0.65 | needs ~77 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 886 | 65 | 65 | 1 | 99.78c | $-87.15 | $-1.34 | needs ~1902 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 735 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 886 | 31 | 27 | 1 | 99.40c | $-83.22 | $-2.89 | needs ~639 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1061 | 234 | 227 | 4 | 98.96c | $-175.80 | $-0.77 | needs ~584 more bets with no loss |
| Buy now, 60 s left (z 4+) | 725 | 86 | 81 | 0 | 99.61c | $+29.46 | $+0.36 | needs ~554 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1050 | 54 | 53 | 0 | 99.71c | $+14.07 | $+0.26 | needs ~827 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 379 | 377 | 376 | 20 | 93.86c | $+186.87 | $+0.53 | needs ~86 more bets with no loss |

