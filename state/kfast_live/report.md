# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3696 coin-windows from 2026-11-10T10:30 to 2026-11-17T19:00 UTC (528 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **59 of 3696** windows. Reading the Kalshi book takes about 138 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2653 | 226 | 220 | 2 | 99.63c | $-14.26 | $-0.65 | needs ~1816 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2193 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2653 | 115 | 111 | 3 | 99.17c | $-21.00 | $-1.88 | needs ~721 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3168 | 758 | 753 | 13 | 98.91c | $-55.49 | $-0.74 | needs ~1161 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2182 | 293 | 284 | 3 | 99.64c | $-22.99 | $-0.81 | needs ~2415 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3123 | 173 | 170 | 0 | 99.60c | $+4.89 | $+0.29 | needs ~628 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1232 | 1224 | 1218 | 86 | 92.80c | $-35.92 | $-0.32 | needs ~236 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2653 | 226 | 216 | 2 | 99.64c | $-126.73 | $-0.58 | needs ~1354 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2193 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2653 | 115 | 104 | 3 | 99.16c | $-212.29 | $-1.99 | needs ~703 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3168 | 758 | 739 | 13 | 98.94c | $-558.06 | $-0.76 | needs ~1146 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2182 | 293 | 277 | 3 | 99.65c | $-209.55 | $-0.75 | needs ~1780 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3123 | 173 | 165 | 0 | 99.62c | $+58.80 | $+0.35 | needs ~486 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1232 | 1224 | 1210 | 86 | 92.92c | $-457.58 | $-0.40 | needs ~249 more bets with no loss |

