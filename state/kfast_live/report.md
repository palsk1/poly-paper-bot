# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2114 coin-windows from 2026-11-10T10:30 to 2026-11-14T11:30 UTC (302 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **34 of 2114** windows. Reading the Kalshi book takes about 147 ms (slowest 1 in 10: 245 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1542 | 123 | 121 | 1 | 99.78c | $-8.54 | $-0.70 | needs ~3110 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1288 | 26 | 26 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~3715 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1542 | 58 | 57 | 1 | 99.43c | $-6.87 | $-1.20 | needs ~657 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1837 | 406 | 404 | 7 | 98.91c | $-30.19 | $-0.75 | needs ~790 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1279 | 162 | 156 | 0 | 99.61c | $+4.29 | $+0.28 | needs ~676 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1819 | 100 | 99 | 0 | 99.51c | $+3.71 | $+0.38 | needs ~514 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 671 | 666 | 664 | 42 | 93.38c | $-7.86 | $-0.13 | needs ~161 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1542 | 123 | 119 | 1 | 99.79c | $-76.78 | $-0.64 | needs ~1874 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1288 | 26 | 24 | 0 | 99.84c | $+3.45 | $+0.14 | needs ~1592 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1542 | 58 | 53 | 1 | 99.44c | $-69.80 | $-1.27 | needs ~652 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1837 | 406 | 394 | 7 | 98.95c | $-306.89 | $-0.78 | needs ~786 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1279 | 162 | 151 | 0 | 99.62c | $+54.21 | $+0.35 | needs ~489 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1819 | 100 | 95 | 0 | 99.53c | $+42.05 | $+0.43 | needs ~435 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 671 | 666 | 659 | 42 | 93.51c | $-138.52 | $-0.22 | needs ~170 more bets with no loss |

