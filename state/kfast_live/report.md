# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 3857 coin-windows from 2026-11-10T10:30 to 2026-11-18T02:00 UTC (551 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **63 of 3857** windows. Reading the Kalshi book takes about 144 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2770 | 233 | 226 | 2 | 99.63c | $-14.18 | $-0.63 | needs ~1836 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2288 | 46 | 45 | 0 | 99.81c | $+0.41 | $+0.09 | needs ~2462 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2770 | 118 | 114 | 3 | 99.17c | $-20.86 | $-1.82 | needs ~727 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3315 | 798 | 791 | 13 | 98.91c | $-51.84 | $-0.66 | needs ~1124 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2289 | 306 | 297 | 3 | 99.65c | $-22.95 | $-0.77 | needs ~2510 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3264 | 181 | 178 | 0 | 99.61c | $+4.96 | $+0.28 | needs ~646 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1278 | 1270 | 1263 | 89 | 92.87c | $-43.58 | $-0.37 | needs ~252 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2770 | 233 | 222 | 2 | 99.64c | $-125.37 | $-0.56 | needs ~1361 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2288 | 46 | 42 | 0 | 99.82c | $+7.12 | $+0.17 | needs ~1345 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2770 | 118 | 107 | 3 | 99.17c | $-210.78 | $-1.92 | needs ~709 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3315 | 798 | 776 | 13 | 98.94c | $-523.59 | $-0.67 | needs ~1113 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2289 | 306 | 289 | 3 | 99.66c | $-208.19 | $-0.71 | needs ~1824 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3264 | 181 | 173 | 0 | 99.63c | $+60.15 | $+0.34 | needs ~494 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1278 | 1270 | 1254 | 89 | 92.99c | $-540.79 | $-0.46 | needs ~266 more bets with no loss |

