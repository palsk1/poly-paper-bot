# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5859 coin-windows from 2026-11-10T10:30 to 2026-11-22T04:45 UTC (837 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **97 of 5859** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4145 | 320 | 310 | 2 | 99.67c | $-13.13 | $-0.42 | needs ~2084 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3402 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4145 | 158 | 153 | 3 | 99.24c | $-18.69 | $-1.22 | needs ~756 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4997 | 1133 | 1121 | 16 | 98.87c | $-45.59 | $-0.41 | needs ~1070 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3378 | 433 | 419 | 3 | 99.68c | $-21.07 | $-0.50 | needs ~2711 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4929 | 246 | 243 | 0 | 99.58c | $+7.60 | $+0.31 | needs ~490 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1955 | 1944 | 1933 | 128 | 92.75c | $+36.50 | $+0.20 | needs ~160 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4145 | 320 | 303 | 2 | 99.68c | $-108.35 | $-0.36 | needs ~1456 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3402 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4145 | 158 | 143 | 3 | 99.23c | $-189.91 | $-1.30 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4997 | 1133 | 1096 | 16 | 98.90c | $-458.93 | $-0.42 | needs ~1046 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3378 | 433 | 411 | 3 | 99.69c | $-180.35 | $-0.44 | needs ~1883 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4929 | 246 | 237 | 0 | 99.59c | $+90.99 | $+0.38 | needs ~364 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1955 | 1944 | 1920 | 128 | 92.88c | $+192.06 | $+0.11 | needs ~182 more bets with no loss |

