# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2849 coin-windows from 2026-11-10T10:30 to 2026-11-15T21:45 UTC (407 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **47 of 2849** windows. Reading the Kalshi book takes about 149 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2034 | 185 | 182 | 2 | 99.60c | $-14.77 | $-0.81 | needs ~1671 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1661 | 40 | 39 | 0 | 99.80c | $+0.36 | $+0.09 | needs ~2433 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2034 | 95 | 92 | 3 | 99.10c | $-22.00 | $-2.38 | needs ~684 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2433 | 590 | 585 | 12 | 98.96c | $-65.07 | $-1.12 | needs ~1309 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1652 | 226 | 218 | 2 | 99.65c | $-14.71 | $-0.68 | needs ~1969 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2401 | 143 | 141 | 0 | 99.59c | $+4.22 | $+0.30 | needs ~627 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 968 | 962 | 959 | 68 | 92.81c | $-31.95 | $-0.36 | needs ~214 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2034 | 185 | 178 | 2 | 99.61c | $-134.88 | $-0.75 | needs ~1282 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1661 | 40 | 36 | 0 | 99.82c | $+6.15 | $+0.17 | needs ~1347 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2034 | 95 | 86 | 3 | 99.10c | $-222.23 | $-2.52 | needs ~667 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2433 | 590 | 574 | 12 | 99.00c | $-654.54 | $-1.14 | needs ~1298 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1652 | 226 | 213 | 2 | 99.65c | $-130.92 | $-0.61 | needs ~1433 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2401 | 143 | 136 | 0 | 99.61c | $+50.17 | $+0.36 | needs ~496 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 968 | 962 | 952 | 68 | 92.93c | $-402.20 | $-0.45 | needs ~225 more bets with no loss |

