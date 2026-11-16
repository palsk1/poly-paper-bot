# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2954 coin-windows from 2026-11-10T10:30 to 2026-11-16T01:30 UTC (422 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **49 of 2954** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 248 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2109 | 197 | 194 | 2 | 99.61c | $-14.52 | $-0.75 | needs ~1691 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1725 | 44 | 43 | 0 | 99.80c | $+0.40 | $+0.09 | needs ~2412 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2109 | 102 | 99 | 3 | 99.13c | $-21.59 | $-2.17 | needs ~695 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2526 | 620 | 615 | 12 | 98.97c | $-62.63 | $-1.02 | needs ~1291 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1711 | 239 | 231 | 3 | 99.60c | $-23.51 | $-1.02 | needs ~2140 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2496 | 156 | 154 | 0 | 99.59c | $+4.57 | $+0.30 | needs ~620 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1010 | 1003 | 1000 | 70 | 92.91c | $-34.00 | $-0.36 | needs ~223 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2109 | 197 | 190 | 2 | 99.62c | $-131.56 | $-0.69 | needs ~1292 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1725 | 44 | 40 | 0 | 99.82c | $+6.85 | $+0.17 | needs ~1335 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2109 | 102 | 93 | 3 | 99.12c | $-218.16 | $-2.30 | needs ~679 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2526 | 620 | 604 | 12 | 99.00c | $-629.50 | $-1.04 | needs ~1278 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1711 | 239 | 225 | 3 | 99.61c | $-218.52 | $-0.96 | needs ~1632 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2496 | 156 | 149 | 0 | 99.61c | $+54.49 | $+0.36 | needs ~487 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1010 | 1003 | 993 | 70 | 93.03c | $-423.36 | $-0.45 | needs ~234 more bets with no loss |

