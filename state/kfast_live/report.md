# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3493 coin-windows from 2026-11-10T10:30 to 2026-11-17T05:45 UTC (499 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **55 of 3493** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2495 | 220 | 216 | 2 | 99.63c | $-14.29 | $-0.66 | needs ~1795 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2056 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2495 | 113 | 109 | 3 | 99.16c | $-21.10 | $-1.92 | needs ~717 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2987 | 732 | 727 | 13 | 98.89c | $-56.93 | $-0.79 | needs ~1158 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2041 | 281 | 272 | 3 | 99.63c | $-23.05 | $-0.85 | needs ~2335 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2945 | 169 | 167 | 0 | 99.60c | $+4.86 | $+0.29 | needs ~622 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1184 | 1176 | 1172 | 83 | 92.76c | $-32.57 | $-0.30 | needs ~228 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2495 | 220 | 212 | 2 | 99.63c | $-127.45 | $-0.60 | needs ~1346 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2056 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2495 | 113 | 102 | 3 | 99.15c | $-213.29 | $-2.04 | needs ~699 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2987 | 732 | 714 | 13 | 98.92c | $-572.38 | $-0.80 | needs ~1144 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2041 | 281 | 265 | 3 | 99.64c | $-210.97 | $-0.79 | needs ~1735 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2945 | 169 | 162 | 0 | 99.62c | $+58.23 | $+0.35 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1184 | 1176 | 1164 | 83 | 92.88c | $-421.10 | $-0.39 | needs ~241 more bets with no loss |

