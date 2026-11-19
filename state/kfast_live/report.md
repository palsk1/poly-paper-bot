# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4445 coin-windows from 2026-11-10T10:30 to 2026-11-19T05:00 UTC (635 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **75 of 4445** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 238 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3174 | 270 | 262 | 2 | 99.65c | $-13.69 | $-0.52 | needs ~1942 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2603 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3174 | 133 | 129 | 3 | 99.20c | $-19.97 | $-1.54 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3799 | 898 | 890 | 14 | 98.89c | $-50.43 | $-0.57 | needs ~1105 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2588 | 350 | 340 | 3 | 99.67c | $-22.45 | $-0.66 | needs ~2660 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3739 | 205 | 202 | 0 | 99.60c | $+5.94 | $+0.29 | needs ~577 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1494 | 1485 | 1477 | 103 | 92.84c | $-36.26 | $-0.26 | needs ~252 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3174 | 270 | 258 | 2 | 99.66c | $-117.72 | $-0.45 | needs ~1408 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2603 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3174 | 133 | 119 | 3 | 99.19c | $-202.63 | $-1.65 | needs ~713 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3799 | 898 | 872 | 14 | 98.92c | $-509.20 | $-0.58 | needs ~1091 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2588 | 350 | 332 | 3 | 99.68c | $-199.84 | $-0.60 | needs ~1889 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3739 | 205 | 196 | 0 | 99.61c | $+71.41 | $+0.36 | needs ~440 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1494 | 1485 | 1468 | 103 | 92.97c | $-494.81 | $-0.36 | needs ~270 more bets with no loss |

