# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2779 coin-windows from 2026-11-10T10:30 to 2026-11-15T18:45 UTC (397 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **46 of 2779** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 246 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1982 | 166 | 163 | 1 | 99.79c | $-8.18 | $-0.50 | needs ~3334 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1622 | 33 | 32 | 0 | 99.84c | $+0.18 | $+0.06 | needs ~4056 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1982 | 84 | 82 | 2 | 99.45c | $-15.55 | $-1.88 | needs ~912 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2376 | 564 | 559 | 11 | 99.02c | $-60.83 | $-1.09 | needs ~1328 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1614 | 218 | 210 | 2 | 99.64c | $-14.77 | $-0.70 | needs ~1921 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2342 | 132 | 130 | 0 | 99.58c | $+3.99 | $+0.31 | needs ~618 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 932 | 926 | 923 | 65 | 92.87c | $-31.39 | $-0.36 | needs ~212 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1982 | 166 | 159 | 1 | 99.79c | $-69.78 | $-0.44 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1622 | 33 | 29 | 0 | 99.84c | $+4.23 | $+0.14 | needs ~1602 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1982 | 84 | 77 | 2 | 99.45c | $-157.24 | $-1.99 | needs ~903 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2376 | 564 | 548 | 11 | 99.06c | $-612.09 | $-1.12 | needs ~1318 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1614 | 218 | 205 | 2 | 99.64c | $-132.15 | $-0.64 | needs ~1408 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2342 | 132 | 125 | 0 | 99.60c | $+47.32 | $+0.37 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 932 | 926 | 916 | 65 | 92.99c | $-394.37 | $-0.46 | needs ~222 more bets with no loss |

