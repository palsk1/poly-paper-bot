# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2219 coin-windows from 2026-11-10T10:30 to 2026-11-14T15:15 UTC (317 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **36 of 2219** windows. Reading the Kalshi book takes about 143 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1612 | 133 | 131 | 1 | 99.78c | $-8.39 | $-0.64 | needs ~3040 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1339 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1612 | 61 | 60 | 1 | 99.43c | $-6.68 | $-1.11 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1928 | 432 | 429 | 7 | 98.90c | $-27.48 | $-0.64 | needs ~760 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1330 | 172 | 166 | 0 | 99.61c | $+4.62 | $+0.28 | needs ~656 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1907 | 106 | 104 | 0 | 99.52c | $+3.84 | $+0.37 | needs ~518 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 712 | 707 | 705 | 42 | 93.55c | $+6.40 | $+0.10 | needs ~142 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1612 | 133 | 129 | 1 | 99.78c | $-74.49 | $-0.58 | needs ~1837 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1339 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1612 | 61 | 56 | 1 | 99.43c | $-67.82 | $-1.17 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1928 | 432 | 419 | 7 | 98.94c | $-280.01 | $-0.67 | needs ~754 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1330 | 172 | 161 | 0 | 99.61c | $+58.26 | $+0.36 | needs ~474 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1907 | 106 | 99 | 0 | 99.54c | $+43.68 | $+0.43 | needs ~433 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 712 | 707 | 700 | 42 | 93.67c | $+3.53 | $+0.01 | needs ~151 more bets with no loss |

