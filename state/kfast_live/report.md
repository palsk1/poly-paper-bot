# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2030 coin-windows from 2026-11-10T10:30 to 2026-11-14T08:30 UTC (290 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **30 of 2030** windows. Reading the Kalshi book takes about 152 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1474 | 116 | 114 | 1 | 99.79c | $-8.72 | $-0.76 | needs ~3361 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1230 | 24 | 24 | 0 | 99.84c | $+0.14 | $+0.06 | needs ~3923 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1474 | 53 | 52 | 1 | 99.44c | $-7.15 | $-1.37 | needs ~664 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1764 | 395 | 393 | 7 | 98.89c | $-30.63 | $-0.78 | needs ~782 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1223 | 156 | 150 | 0 | 99.60c | $+4.21 | $+0.28 | needs ~665 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1745 | 97 | 96 | 0 | 99.53c | $+3.41 | $+0.36 | needs ~551 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 648 | 643 | 641 | 39 | 93.40c | $+6.57 | $+0.11 | needs ~134 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1474 | 116 | 112 | 1 | 99.79c | $-78.91 | $-0.70 | needs ~1954 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1230 | 24 | 22 | 0 | 99.85c | $+3.09 | $+0.14 | needs ~1634 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1474 | 53 | 48 | 1 | 99.44c | $-72.52 | $-1.45 | needs ~656 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1764 | 395 | 383 | 7 | 98.93c | $-311.48 | $-0.81 | needs ~778 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1223 | 156 | 145 | 0 | 99.61c | $+52.94 | $+0.36 | needs ~485 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1745 | 97 | 92 | 0 | 99.55c | $+39.05 | $+0.41 | needs ~462 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 648 | 643 | 636 | 39 | 93.53c | $+7.48 | $+0.01 | needs ~142 more bets with no loss |

