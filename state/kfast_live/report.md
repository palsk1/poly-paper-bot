# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2884 coin-windows from 2026-11-10T10:30 to 2026-11-15T23:00 UTC (412 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **49 of 2884** windows. Reading the Kalshi book takes about 151 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2055 | 190 | 187 | 2 | 99.61c | $-14.67 | $-0.79 | needs ~1681 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1677 | 40 | 39 | 0 | 99.80c | $+0.36 | $+0.09 | needs ~2433 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2055 | 99 | 96 | 3 | 99.12c | $-21.80 | $-2.26 | needs ~694 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2462 | 602 | 597 | 12 | 98.96c | $-63.73 | $-1.07 | needs ~1290 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1671 | 232 | 224 | 3 | 99.60c | $-23.57 | $-1.05 | needs ~2097 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2430 | 149 | 147 | 0 | 99.59c | $+4.38 | $+0.30 | needs ~624 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 987 | 980 | 977 | 69 | 92.85c | $-33.52 | $-0.37 | needs ~219 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2055 | 190 | 183 | 2 | 99.61c | $-133.51 | $-0.73 | needs ~1287 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1677 | 40 | 36 | 0 | 99.82c | $+6.15 | $+0.17 | needs ~1347 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2055 | 99 | 90 | 3 | 99.11c | $-220.23 | $-2.39 | needs ~677 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2462 | 602 | 586 | 12 | 98.99c | $-641.10 | $-1.09 | needs ~1278 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1671 | 232 | 218 | 3 | 99.61c | $-219.63 | $-1.00 | needs ~1607 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2430 | 149 | 142 | 0 | 99.61c | $+52.17 | $+0.36 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 987 | 980 | 970 | 69 | 92.97c | $-418.55 | $-0.46 | needs ~230 more bets with no loss |

