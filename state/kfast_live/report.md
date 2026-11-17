# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3661 coin-windows from 2026-11-10T10:30 to 2026-11-17T14:00 UTC (523 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **59 of 3661** windows. Reading the Kalshi book takes about 137 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2624 | 225 | 220 | 2 | 99.63c | $-14.25 | $-0.65 | needs ~1814 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2170 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2624 | 114 | 110 | 3 | 99.16c | $-21.05 | $-1.90 | needs ~719 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3135 | 752 | 747 | 13 | 98.90c | $-55.88 | $-0.75 | needs ~1162 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2157 | 290 | 281 | 3 | 99.64c | $-22.99 | $-0.82 | needs ~2389 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3091 | 172 | 169 | 0 | 99.60c | $+4.88 | $+0.29 | needs ~626 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1225 | 1217 | 1212 | 86 | 92.77c | $-36.85 | $-0.33 | needs ~237 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2624 | 225 | 216 | 2 | 99.64c | $-126.72 | $-0.58 | needs ~1354 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2170 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2624 | 114 | 103 | 3 | 99.16c | $-212.79 | $-2.01 | needs ~701 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3135 | 752 | 733 | 13 | 98.94c | $-561.98 | $-0.77 | needs ~1146 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2157 | 290 | 274 | 3 | 99.65c | $-209.82 | $-0.76 | needs ~1767 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3091 | 172 | 164 | 0 | 99.62c | $+58.62 | $+0.35 | needs ~485 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1225 | 1217 | 1204 | 86 | 92.90c | $-467.02 | $-0.41 | needs ~250 more bets with no loss |

