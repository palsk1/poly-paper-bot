# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 1561 coin-windows from 2026-11-10T10:30 to 2026-11-13T11:15 UTC (223 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **20 of 1561** windows. Reading the Kalshi book takes about 167 ms (slowest 1 in 10: 250 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1125 | 89 | 88 | 1 | 99.79c | $-9.02 | $-1.02 | needs ~3421 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 924 | 19 | 19 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1125 | 38 | 37 | 1 | 99.42c | $-7.91 | $-2.12 | needs ~661 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1357 | 302 | 301 | 4 | 98.91c | $-10.54 | $-0.35 | needs ~515 more bets with no loss |
| Buy now, 60 s left (z 4+) | 917 | 120 | 116 | 0 | 99.67c | $+2.59 | $+0.22 | needs ~911 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1340 | 69 | 69 | 0 | 99.46c | $+2.94 | $+0.43 | needs ~470 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 506 | 502 | 501 | 24 | 93.64c | $+58.50 | $+1.24 | needs ~25 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1125 | 89 | 86 | 1 | 99.79c | $-83.92 | $-0.97 | needs ~1997 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 924 | 19 | 17 | 0 | 99.88c | $+1.88 | $+0.11 | needs ~2094 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1125 | 38 | 34 | 1 | 99.42c | $-79.76 | $-2.23 | needs ~652 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1357 | 302 | 295 | 4 | 98.96c | $-109.12 | $-0.37 | needs ~515 more bets with no loss |
| Buy now, 60 s left (z 4+) | 917 | 120 | 113 | 0 | 99.67c | $+34.38 | $+0.30 | needs ~644 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1340 | 69 | 66 | 0 | 99.48c | $+32.49 | $+0.48 | needs ~412 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 506 | 502 | 498 | 24 | 93.78c | $+535.55 | $+1.14 | needs ~32 more bets with no loss |

