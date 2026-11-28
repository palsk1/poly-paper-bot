# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8600 coin-windows from 2026-11-10T10:30 to 2026-11-28T05:15 UTC (1222 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **143 of 8600** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 226 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6057 | 447 | 433 | 2 | 99.63c | $-8.75 | $-0.20 | needs ~1604 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4956 | 84 | 82 | 0 | 99.79c | $+0.85 | $+0.10 | needs ~2129 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6057 | 236 | 227 | 3 | 99.19c | $-12.09 | $-0.53 | needs ~622 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7328 | 1650 | 1635 | 23 | 98.82c | $-55.32 | $-0.34 | needs ~1203 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4891 | 608 | 592 | 3 | 99.71c | $-18.95 | $-0.32 | needs ~2979 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7214 | 337 | 331 | 2 | 99.01c | $+8.81 | $+0.27 | needs ~274 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2860 | 2844 | 2826 | 201 | 92.75c | $-84.60 | $-0.32 | needs ~383 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6057 | 447 | 421 | 2 | 99.64c | $-57.31 | $-0.13 | needs ~1146 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4956 | 84 | 79 | 0 | 99.80c | $+14.43 | $+0.18 | needs ~1193 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6057 | 236 | 208 | 3 | 99.18c | $-127.91 | $-0.60 | needs ~604 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7328 | 1650 | 1594 | 23 | 98.85c | $-558.69 | $-0.35 | needs ~1171 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4891 | 608 | 581 | 3 | 99.71c | $-145.76 | $-0.25 | needs ~1932 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7214 | 337 | 323 | 2 | 99.03c | $+105.86 | $+0.33 | needs ~233 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2860 | 2844 | 2805 | 201 | 92.88c | $-1113.78 | $-0.42 | needs ~417 more bets with no loss |

