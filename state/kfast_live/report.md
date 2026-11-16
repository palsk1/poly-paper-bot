# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2968 coin-windows from 2026-11-10T10:30 to 2026-11-16T02:00 UTC (424 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **49 of 2968** windows. Reading the Kalshi book takes about 156 ms (slowest 1 in 10: 248 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2115 | 199 | 196 | 2 | 99.61c | $-14.52 | $-0.74 | needs ~1708 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1730 | 45 | 44 | 0 | 99.81c | $+0.40 | $+0.09 | needs ~2468 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2115 | 102 | 99 | 3 | 99.13c | $-21.59 | $-2.17 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2536 | 626 | 621 | 12 | 98.97c | $-62.20 | $-1.01 | needs ~1289 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1717 | 240 | 232 | 3 | 99.60c | $-23.46 | $-1.01 | needs ~2131 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2506 | 158 | 156 | 0 | 99.60c | $+4.57 | $+0.29 | needs ~628 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1019 | 1012 | 1009 | 70 | 92.93c | $-30.24 | $-0.32 | needs ~218 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2115 | 199 | 192 | 2 | 99.62c | $-131.38 | $-0.68 | needs ~1301 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1730 | 45 | 41 | 0 | 99.82c | $+6.94 | $+0.17 | needs ~1349 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2115 | 102 | 93 | 3 | 99.12c | $-218.16 | $-2.30 | needs ~679 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2536 | 626 | 610 | 12 | 99.00c | $-625.60 | $-1.03 | needs ~1278 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1717 | 240 | 226 | 3 | 99.61c | $-217.97 | $-0.95 | needs ~1627 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2506 | 158 | 151 | 0 | 99.62c | $+54.67 | $+0.36 | needs ~492 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1019 | 1012 | 1002 | 70 | 93.06c | $-386.63 | $-0.41 | needs ~229 more bets with no loss |

