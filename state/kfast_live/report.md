# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2660 coin-windows from 2026-11-10T10:30 to 2026-11-15T14:15 UTC (380 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **45 of 2660** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1911 | 163 | 160 | 1 | 99.79c | $-8.19 | $-0.51 | needs ~3292 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1571 | 32 | 31 | 0 | 99.84c | $+0.17 | $+0.05 | needs ~4162 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1911 | 78 | 76 | 1 | 99.44c | $-5.85 | $-0.76 | needs ~646 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2289 | 536 | 533 | 9 | 99.01c | $-42.25 | $-0.80 | needs ~1054 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1557 | 206 | 198 | 0 | 99.63c | $+5.11 | $+0.26 | needs ~688 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2258 | 127 | 125 | 0 | 99.57c | $+3.95 | $+0.32 | needs ~602 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 881 | 875 | 872 | 58 | 93.00c | $-6.90 | $-0.08 | needs ~171 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1911 | 163 | 157 | 1 | 99.79c | $-70.10 | $-0.44 | needs ~1892 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1571 | 32 | 28 | 0 | 99.84c | $+4.05 | $+0.14 | needs ~1619 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1911 | 78 | 71 | 1 | 99.45c | $-60.24 | $-0.83 | needs ~639 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2289 | 536 | 522 | 9 | 99.04c | $-426.74 | $-0.82 | needs ~1046 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1557 | 206 | 193 | 0 | 99.63c | $+65.73 | $+0.34 | needs ~478 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2258 | 127 | 120 | 0 | 99.59c | $+46.50 | $+0.38 | needs ~483 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 881 | 875 | 866 | 58 | 93.13c | $-146.52 | $-0.18 | needs ~181 more bets with no loss |

