# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1141 coin-windows from 2026-11-10T10:30 to 2026-11-12T17:30 UTC (163 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **9 of 1141** windows. Reading the Kalshi book takes about 161 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 831 | 61 | 61 | 1 | 99.77c | $-9.22 | $-1.51 | needs ~2998 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 693 | 17 | 17 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 831 | 30 | 29 | 1 | 99.40c | $-8.30 | $-2.82 | needs ~646 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 996 | 219 | 218 | 4 | 98.90c | $-18.34 | $-0.85 | needs ~586 more bets with no loss |
| Buy now, 60 s left (z 4+) | 685 | 77 | 77 | 0 | 99.59c | $+2.29 | $+0.30 | needs ~698 more bets with no loss |
| Buy now, 30 s left (z 4+) | 988 | 53 | 53 | 0 | 99.72c | $+0.94 | $+0.18 | needs ~1243 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 361 | 359 | 359 | 18 | 93.57c | $+36.29 | $+1.08 | needs ~49 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 831 | 61 | 61 | 1 | 99.78c | $-87.91 | $-1.44 | needs ~1900 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 693 | 17 | 17 | 0 | 99.88c | $+1.87 | $+0.11 | needs ~2071 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 831 | 30 | 27 | 1 | 99.40c | $-83.65 | $-3.00 | needs ~637 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 996 | 219 | 212 | 4 | 98.94c | $-186.53 | $-0.88 | needs ~584 more bets with no loss |
| Buy now, 60 s left (z 4+) | 685 | 77 | 75 | 0 | 99.60c | $+28.20 | $+0.37 | needs ~542 more bets with no loss |
| Buy now, 30 s left (z 4+) | 988 | 53 | 52 | 0 | 99.72c | $+13.33 | $+0.25 | needs ~860 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 361 | 359 | 358 | 18 | 93.75c | $+322.09 | $+0.95 | needs ~57 more bets with no loss |

