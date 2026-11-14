# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2079 coin-windows from 2026-11-10T10:30 to 2026-11-14T10:15 UTC (297 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **31 of 2079** windows. Reading the Kalshi book takes about 149 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1517 | 118 | 116 | 1 | 99.78c | $-8.62 | $-0.74 | needs ~3163 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1269 | 24 | 24 | 0 | 99.84c | $+0.14 | $+0.06 | needs ~3923 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1517 | 55 | 54 | 1 | 99.43c | $-7.03 | $-1.30 | needs ~659 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1808 | 399 | 397 | 7 | 98.90c | $-30.46 | $-0.77 | needs ~785 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1261 | 157 | 151 | 0 | 99.60c | $+4.26 | $+0.28 | needs ~660 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1789 | 98 | 97 | 0 | 99.53c | $+3.45 | $+0.36 | needs ~549 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 656 | 651 | 649 | 40 | 93.41c | $+1.19 | $+0.02 | needs ~144 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1517 | 118 | 114 | 1 | 99.79c | $-77.88 | $-0.68 | needs ~1890 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1269 | 24 | 22 | 0 | 99.85c | $+3.09 | $+0.14 | needs ~1634 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1517 | 55 | 50 | 1 | 99.44c | $-71.36 | $-1.38 | needs ~652 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1808 | 399 | 387 | 7 | 98.94c | $-309.69 | $-0.80 | needs ~781 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1261 | 157 | 146 | 0 | 99.61c | $+53.49 | $+0.36 | needs ~482 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1789 | 98 | 93 | 0 | 99.55c | $+39.51 | $+0.41 | needs ~460 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 656 | 651 | 644 | 40 | 93.54c | $-47.35 | $-0.08 | needs ~152 more bets with no loss |

