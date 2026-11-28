# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8573 coin-windows from 2026-11-10T10:30 to 2026-11-28T04:30 UTC (1219 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **142 of 8573** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 227 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6035 | 444 | 430 | 2 | 99.63c | $-8.77 | $-0.20 | needs ~1597 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4937 | 83 | 81 | 0 | 99.79c | $+0.85 | $+0.11 | needs ~2103 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6035 | 232 | 223 | 3 | 99.18c | $-12.29 | $-0.55 | needs ~620 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7303 | 1642 | 1627 | 23 | 98.82c | $-55.67 | $-0.35 | needs ~1203 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4873 | 605 | 589 | 3 | 99.71c | $-18.98 | $-0.32 | needs ~2974 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7189 | 336 | 330 | 2 | 99.01c | $+8.81 | $+0.27 | needs ~273 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2852 | 2836 | 2818 | 201 | 92.73c | $-85.62 | $-0.33 | needs ~383 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6035 | 444 | 418 | 2 | 99.64c | $-57.76 | $-0.14 | needs ~1143 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4937 | 83 | 78 | 0 | 99.80c | $+14.34 | $+0.18 | needs ~1185 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6035 | 232 | 205 | 3 | 99.18c | $-129.49 | $-0.61 | needs ~603 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7303 | 1642 | 1587 | 23 | 98.85c | $-562.41 | $-0.35 | needs ~1171 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4873 | 605 | 578 | 3 | 99.71c | $-146.25 | $-0.25 | needs ~1930 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7189 | 336 | 322 | 2 | 99.03c | $+105.77 | $+0.33 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2852 | 2836 | 2797 | 201 | 92.87c | $-1123.47 | $-0.43 | needs ~418 more bets with no loss |

