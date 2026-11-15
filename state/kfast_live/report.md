# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2744 coin-windows from 2026-11-10T10:30 to 2026-11-15T17:30 UTC (392 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **45 of 2744** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1962 | 165 | 162 | 1 | 99.79c | $-8.19 | $-0.51 | needs ~3333 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1607 | 32 | 31 | 0 | 99.84c | $+0.17 | $+0.05 | needs ~4162 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1962 | 83 | 81 | 2 | 99.45c | $-15.60 | $-1.90 | needs ~912 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2351 | 555 | 551 | 11 | 99.02c | $-61.10 | $-1.11 | needs ~1321 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1597 | 213 | 205 | 2 | 99.64c | $-14.83 | $-0.72 | needs ~1899 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2317 | 131 | 129 | 0 | 99.58c | $+3.99 | $+0.31 | needs ~614 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 916 | 910 | 907 | 64 | 92.95c | $-39.08 | $-0.46 | needs ~225 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1962 | 165 | 158 | 1 | 99.79c | $-69.96 | $-0.44 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1607 | 32 | 28 | 0 | 99.84c | $+4.05 | $+0.14 | needs ~1619 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1962 | 83 | 76 | 2 | 99.45c | $-157.74 | $-2.02 | needs ~903 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2351 | 555 | 540 | 11 | 99.05c | $-615.01 | $-1.14 | needs ~1311 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1597 | 213 | 200 | 2 | 99.64c | $-133.15 | $-0.66 | needs ~1398 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2317 | 131 | 124 | 0 | 99.60c | $+47.23 | $+0.37 | needs ~489 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 916 | 910 | 900 | 64 | 93.07c | $-469.95 | $-0.56 | needs ~236 more bets with no loss |

