# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6552 coin-windows from 2026-11-10T10:30 to 2026-11-23T13:30 UTC (936 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **108 of 6552** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4615 | 372 | 361 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1568 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3768 | 71 | 70 | 0 | 99.78c | $+0.80 | $+0.11 | needs ~1936 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4615 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5582 | 1272 | 1258 | 18 | 98.86c | $-50.15 | $-0.40 | needs ~1130 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3742 | 511 | 496 | 3 | 99.69c | $-20.02 | $-0.40 | needs ~2817 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5505 | 278 | 275 | 1 | 99.20c | $+8.80 | $+0.32 | needs ~290 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2217 | 2204 | 2191 | 145 | 92.98c | $-5.02 | $-0.02 | needs ~240 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4615 | 372 | 353 | 2 | 99.62c | $-75.01 | $-0.21 | needs ~1147 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3768 | 71 | 67 | 0 | 99.79c | $+12.81 | $+0.19 | needs ~1151 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4615 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5582 | 1272 | 1230 | 18 | 98.89c | $-503.70 | $-0.41 | needs ~1103 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3742 | 511 | 487 | 3 | 99.70c | $-163.73 | $-0.33 | needs ~1896 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5505 | 278 | 269 | 1 | 99.22c | $+105.38 | $+0.39 | needs ~239 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2217 | 2204 | 2177 | 145 | 93.11c | $-235.64 | $-0.12 | needs ~266 more bets with no loss |

