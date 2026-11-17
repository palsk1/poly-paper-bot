# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3612 coin-windows from 2026-11-10T10:30 to 2026-11-17T12:15 UTC (516 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **58 of 3612** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2590 | 224 | 219 | 2 | 99.63c | $-14.26 | $-0.65 | needs ~1809 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2140 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2590 | 113 | 109 | 3 | 99.16c | $-21.10 | $-1.92 | needs ~717 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3094 | 742 | 737 | 13 | 98.90c | $-56.69 | $-0.77 | needs ~1167 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2126 | 285 | 276 | 3 | 99.63c | $-23.02 | $-0.83 | needs ~2358 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3051 | 170 | 167 | 0 | 99.60c | $+4.85 | $+0.29 | needs ~623 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1209 | 1201 | 1196 | 85 | 92.76c | $-36.01 | $-0.32 | needs ~235 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2590 | 224 | 215 | 2 | 99.64c | $-126.90 | $-0.59 | needs ~1352 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2140 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2590 | 113 | 102 | 3 | 99.15c | $-213.29 | $-2.04 | needs ~699 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3094 | 742 | 723 | 13 | 98.93c | $-569.90 | $-0.79 | needs ~1151 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2126 | 285 | 269 | 3 | 99.64c | $-210.40 | $-0.77 | needs ~1748 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3051 | 170 | 162 | 0 | 99.62c | $+58.22 | $+0.35 | needs ~483 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1209 | 1201 | 1188 | 85 | 92.88c | $-455.36 | $-0.41 | needs ~247 more bets with no loss |

