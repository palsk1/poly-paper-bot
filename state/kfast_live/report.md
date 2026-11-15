# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2814 coin-windows from 2026-11-10T10:30 to 2026-11-15T20:00 UTC (402 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **47 of 2814** windows. Reading the Kalshi book takes about 147 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2006 | 177 | 174 | 2 | 99.60c | $-14.93 | $-0.86 | needs ~1654 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1640 | 38 | 37 | 0 | 99.81c | $+0.33 | $+0.09 | needs ~2527 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2006 | 91 | 89 | 3 | 99.10c | $-22.20 | $-2.48 | needs ~681 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2404 | 579 | 574 | 12 | 98.95c | $-65.45 | $-1.15 | needs ~1297 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1630 | 222 | 214 | 2 | 99.64c | $-14.75 | $-0.69 | needs ~1949 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2369 | 137 | 135 | 0 | 99.59c | $+4.03 | $+0.30 | needs ~635 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 954 | 948 | 945 | 68 | 92.73c | $-34.32 | $-0.39 | needs ~215 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2006 | 177 | 170 | 2 | 99.60c | $-136.88 | $-0.80 | needs ~1269 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1640 | 38 | 34 | 0 | 99.82c | $+5.72 | $+0.16 | needs ~1372 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2006 | 91 | 83 | 3 | 99.09c | $-224.08 | $-2.63 | needs ~663 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2404 | 579 | 563 | 12 | 98.98c | $-658.48 | $-1.17 | needs ~1286 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1630 | 222 | 209 | 2 | 99.65c | $-131.65 | $-0.62 | needs ~1424 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2369 | 137 | 130 | 0 | 99.61c | $+48.03 | $+0.36 | needs ~502 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 954 | 948 | 938 | 68 | 92.85c | $-424.58 | $-0.48 | needs ~226 more bets with no loss |

