# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6188 coin-windows from 2026-11-10T10:30 to 2026-11-22T19:30 UTC (884 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **100 of 6188** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4376 | 346 | 336 | 2 | 99.60c | $-10.30 | $-0.31 | needs ~1499 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3582 | 61 | 60 | 0 | 99.78c | $+0.73 | $+0.12 | needs ~1823 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4376 | 167 | 162 | 3 | 99.09c | $-15.83 | $-0.97 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5282 | 1205 | 1192 | 16 | 98.87c | $-38.49 | $-0.33 | needs ~1000 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3556 | 474 | 459 | 3 | 99.68c | $-20.32 | $-0.44 | needs ~2702 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5211 | 259 | 256 | 0 | 99.55c | $+8.56 | $+0.34 | needs ~429 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2075 | 2062 | 2050 | 135 | 92.95c | $+6.44 | $+0.03 | needs ~215 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4376 | 346 | 328 | 2 | 99.61c | $-79.20 | $-0.24 | needs ~1115 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3582 | 61 | 57 | 0 | 99.79c | $+11.26 | $+0.19 | needs ~1125 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4376 | 167 | 152 | 3 | 99.09c | $-162.09 | $-1.04 | needs ~590 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5282 | 1205 | 1166 | 16 | 98.90c | $-388.11 | $-0.33 | needs ~978 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3556 | 474 | 450 | 3 | 99.69c | $-169.83 | $-0.37 | needs ~1856 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5211 | 259 | 250 | 0 | 99.57c | $+101.51 | $+0.40 | needs ~317 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2075 | 2062 | 2036 | 135 | 93.09c | $-112.38 | $-0.06 | needs ~239 more bets with no loss |

