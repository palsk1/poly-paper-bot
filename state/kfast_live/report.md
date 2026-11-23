# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 6468 coin-windows from 2026-11-10T10:30 to 2026-11-23T08:00 UTC (924 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **107 of 6468** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4560 | 370 | 359 | 2 | 99.61c | $-10.08 | $-0.28 | needs ~1559 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3721 | 69 | 68 | 0 | 99.78c | $+0.80 | $+0.12 | needs ~1880 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4560 | 170 | 165 | 3 | 99.10c | $-15.66 | $-0.95 | needs ~606 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5515 | 1263 | 1250 | 18 | 98.86c | $-50.77 | $-0.41 | needs ~1134 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3701 | 505 | 490 | 3 | 99.69c | $-20.06 | $-0.41 | needs ~2796 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5437 | 274 | 271 | 1 | 99.19c | $+8.80 | $+0.33 | needs ~286 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2187 | 2174 | 2161 | 144 | 93.00c | $-19.58 | $-0.10 | needs ~263 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4560 | 370 | 351 | 2 | 99.62c | $-75.19 | $-0.21 | needs ~1142 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3721 | 69 | 65 | 0 | 99.79c | $+12.63 | $+0.19 | needs ~1134 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4560 | 170 | 155 | 3 | 99.09c | $-160.35 | $-1.01 | needs ~592 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5515 | 1263 | 1222 | 18 | 98.89c | $-509.98 | $-0.42 | needs ~1108 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3701 | 505 | 481 | 3 | 99.70c | $-164.64 | $-0.34 | needs ~1889 more bets with no loss |
| Buy now, 30 s left (z 4+) | 5437 | 274 | 265 | 1 | 99.21c | $+105.02 | $+0.39 | needs ~236 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2187 | 2174 | 2147 | 144 | 93.13c | $-376.82 | $-0.19 | needs ~287 more bets with no loss |

