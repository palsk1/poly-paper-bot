# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3647 coin-windows from 2026-11-10T10:30 to 2026-11-17T13:30 UTC (521 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **59 of 3647** windows. Reading the Kalshi book takes about 138 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2611 | 225 | 220 | 2 | 99.63c | $-14.25 | $-0.65 | needs ~1814 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2157 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2611 | 113 | 109 | 3 | 99.16c | $-21.10 | $-1.92 | needs ~717 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3121 | 750 | 745 | 13 | 98.90c | $-55.95 | $-0.76 | needs ~1161 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2144 | 289 | 280 | 3 | 99.64c | $-22.99 | $-0.82 | needs ~2381 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3077 | 172 | 169 | 0 | 99.60c | $+4.88 | $+0.29 | needs ~626 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1224 | 1216 | 1211 | 86 | 92.77c | $-36.90 | $-0.33 | needs ~237 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2611 | 225 | 216 | 2 | 99.64c | $-126.72 | $-0.58 | needs ~1354 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2157 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2611 | 113 | 102 | 3 | 99.15c | $-213.29 | $-2.04 | needs ~699 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3121 | 750 | 731 | 13 | 98.94c | $-562.70 | $-0.77 | needs ~1145 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2144 | 289 | 273 | 3 | 99.65c | $-209.91 | $-0.76 | needs ~1762 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3077 | 172 | 164 | 0 | 99.62c | $+58.62 | $+0.35 | needs ~485 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1224 | 1216 | 1203 | 86 | 92.89c | $-467.53 | $-0.42 | needs ~250 more bets with no loss |

