# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2919 coin-windows from 2026-11-10T10:30 to 2026-11-16T00:15 UTC (417 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **49 of 2919** windows. Reading the Kalshi book takes about 153 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2079 | 195 | 192 | 2 | 99.61c | $-14.63 | $-0.76 | needs ~1711 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1699 | 44 | 43 | 0 | 99.80c | $+0.40 | $+0.09 | needs ~2412 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2079 | 99 | 96 | 3 | 99.12c | $-21.80 | $-2.26 | needs ~694 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2493 | 614 | 609 | 12 | 98.96c | $-62.97 | $-1.04 | needs ~1290 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1690 | 236 | 228 | 3 | 99.60c | $-23.54 | $-1.03 | needs ~2124 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2462 | 153 | 151 | 0 | 99.59c | $+4.47 | $+0.30 | needs ~625 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1003 | 996 | 993 | 69 | 92.91c | $-28.37 | $-0.31 | needs ~213 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2079 | 195 | 188 | 2 | 99.62c | $-132.71 | $-0.70 | needs ~1304 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1699 | 44 | 40 | 0 | 99.82c | $+6.85 | $+0.17 | needs ~1335 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2079 | 99 | 90 | 3 | 99.11c | $-220.23 | $-2.39 | needs ~677 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2493 | 614 | 598 | 12 | 99.00c | $-632.93 | $-1.06 | needs ~1277 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1690 | 236 | 222 | 3 | 99.61c | $-219.00 | $-0.98 | needs ~1621 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2462 | 153 | 146 | 0 | 99.61c | $+53.36 | $+0.36 | needs ~491 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1003 | 996 | 986 | 69 | 93.03c | $-366.84 | $-0.40 | needs ~224 more bets with no loss |

