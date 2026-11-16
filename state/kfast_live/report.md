# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2919 coin-windows from 2026-11-10T10:30 to 2026-11-16T03:15 UTC (417 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **50 of 2919** windows. Reading the Kalshi book takes about 149 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2078 | 192 | 189 | 2 | 99.61c | $-14.64 | $-0.78 | needs ~1688 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1698 | 40 | 39 | 0 | 99.80c | $+0.36 | $+0.09 | needs ~2433 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2078 | 100 | 97 | 3 | 99.12c | $-21.75 | $-2.23 | needs ~696 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2487 | 606 | 601 | 12 | 98.96c | $-63.61 | $-1.06 | needs ~1294 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1693 | 233 | 225 | 3 | 99.60c | $-23.57 | $-1.05 | needs ~2106 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2456 | 151 | 149 | 0 | 99.59c | $+4.41 | $+0.30 | needs ~627 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1001 | 994 | 991 | 74 | 92.75c | $-64.99 | $-0.70 | needs ~268 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2078 | 192 | 185 | 2 | 99.61c | $-133.06 | $-0.72 | needs ~1290 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1698 | 40 | 36 | 0 | 99.82c | $+6.15 | $+0.17 | needs ~1347 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2078 | 100 | 91 | 3 | 99.12c | $-219.73 | $-2.36 | needs ~680 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2487 | 606 | 590 | 12 | 99.00c | $-639.75 | $-1.08 | needs ~1283 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1693 | 233 | 219 | 3 | 99.61c | $-219.54 | $-0.99 | needs ~1612 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2456 | 151 | 144 | 0 | 99.61c | $+52.57 | $+0.36 | needs ~494 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1001 | 994 | 984 | 74 | 92.88c | $-737.91 | $-0.80 | needs ~280 more bets with no loss |

