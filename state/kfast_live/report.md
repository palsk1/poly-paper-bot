# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3458 coin-windows from 2026-11-10T10:30 to 2026-11-17T04:30 UTC (494 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **55 of 3458** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2460 | 218 | 214 | 2 | 99.63c | $-14.32 | $-0.67 | needs ~1789 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2025 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2460 | 112 | 108 | 3 | 99.16c | $-21.15 | $-1.94 | needs ~715 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2952 | 725 | 720 | 13 | 98.88c | $-57.08 | $-0.80 | needs ~1151 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2008 | 278 | 269 | 3 | 99.63c | $-23.06 | $-0.86 | needs ~2313 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2910 | 169 | 167 | 0 | 99.60c | $+4.86 | $+0.29 | needs ~622 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1182 | 1174 | 1170 | 83 | 92.75c | $-32.60 | $-0.30 | needs ~228 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2460 | 218 | 210 | 2 | 99.63c | $-127.90 | $-0.61 | needs ~1343 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2025 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2460 | 112 | 101 | 3 | 99.15c | $-213.79 | $-2.06 | needs ~697 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2952 | 725 | 708 | 13 | 98.92c | $-573.87 | $-0.81 | needs ~1137 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2008 | 278 | 262 | 3 | 99.64c | $-211.33 | $-0.80 | needs ~1724 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2910 | 169 | 162 | 0 | 99.62c | $+58.23 | $+0.35 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1182 | 1174 | 1162 | 83 | 92.87c | $-421.55 | $-0.39 | needs ~241 more bets with no loss |

