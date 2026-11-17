# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3577 coin-windows from 2026-11-10T10:30 to 2026-11-17T11:00 UTC (511 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **58 of 3577** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2558 | 222 | 217 | 2 | 99.63c | $-14.30 | $-0.66 | needs ~1807 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2111 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2558 | 113 | 109 | 3 | 99.16c | $-21.10 | $-1.92 | needs ~717 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3061 | 740 | 735 | 13 | 98.90c | $-56.73 | $-0.78 | needs ~1165 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2098 | 282 | 273 | 3 | 99.63c | $-23.04 | $-0.84 | needs ~2340 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3018 | 169 | 167 | 0 | 99.60c | $+4.86 | $+0.29 | needs ~622 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1204 | 1196 | 1191 | 85 | 92.74c | $-36.87 | $-0.33 | needs ~235 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2558 | 222 | 213 | 2 | 99.63c | $-127.37 | $-0.60 | needs ~1350 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2111 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2558 | 113 | 102 | 3 | 99.15c | $-213.29 | $-2.04 | needs ~699 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3061 | 740 | 721 | 13 | 98.93c | $-570.37 | $-0.79 | needs ~1149 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2098 | 282 | 266 | 3 | 99.64c | $-210.85 | $-0.78 | needs ~1739 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3018 | 169 | 162 | 0 | 99.62c | $+58.23 | $+0.35 | needs ~484 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1204 | 1196 | 1183 | 85 | 92.86c | $-463.77 | $-0.42 | needs ~247 more bets with no loss |

