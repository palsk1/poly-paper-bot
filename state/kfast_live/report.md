# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3731 coin-windows from 2026-11-10T10:30 to 2026-11-17T20:15 UTC (533 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **60 of 3731** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2678 | 228 | 221 | 2 | 99.63c | $-14.23 | $-0.64 | needs ~1813 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2211 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2678 | 117 | 113 | 3 | 99.17c | $-20.91 | $-1.84 | needs ~725 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3199 | 768 | 761 | 13 | 98.91c | $-54.59 | $-0.72 | needs ~1149 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2202 | 296 | 287 | 3 | 99.64c | $-22.99 | $-0.80 | needs ~2441 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3152 | 174 | 171 | 0 | 99.60c | $+4.91 | $+0.29 | needs ~628 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1244 | 1236 | 1229 | 86 | 92.80c | $-28.47 | $-0.25 | needs ~224 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2678 | 228 | 217 | 2 | 99.64c | $-126.28 | $-0.58 | needs ~1349 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2211 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2678 | 117 | 106 | 3 | 99.17c | $-211.33 | $-1.94 | needs ~707 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3199 | 768 | 747 | 13 | 98.94c | $-549.35 | $-0.74 | needs ~1134 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2202 | 296 | 280 | 3 | 99.65c | $-209.28 | $-0.74 | needs ~1793 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3152 | 174 | 166 | 0 | 99.62c | $+59.06 | $+0.35 | needs ~486 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1244 | 1236 | 1221 | 86 | 92.92c | $-385.38 | $-0.34 | needs ~237 more bets with no loss |

