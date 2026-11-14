# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2275 coin-windows from 2026-11-10T10:30 to 2026-11-14T17:45 UTC (325 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **36 of 2275** windows. Reading the Kalshi book takes about 141 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1648 | 138 | 136 | 1 | 99.78c | $-8.39 | $-0.62 | needs ~3156 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1365 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1648 | 62 | 61 | 1 | 99.43c | $-6.63 | $-1.08 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1974 | 446 | 443 | 7 | 98.93c | $-27.06 | $-0.61 | needs ~772 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1355 | 172 | 166 | 0 | 99.61c | $+4.62 | $+0.28 | needs ~656 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1951 | 111 | 109 | 0 | 99.53c | $+3.87 | $+0.36 | needs ~537 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 737 | 732 | 730 | 47 | 93.52c | $-26.84 | $-0.39 | needs ~204 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1648 | 138 | 134 | 1 | 99.79c | $-74.04 | $-0.55 | needs ~1873 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1365 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1648 | 62 | 57 | 1 | 99.43c | $-67.32 | $-1.14 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1974 | 446 | 433 | 7 | 98.97c | $-275.48 | $-0.64 | needs ~766 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1355 | 172 | 161 | 0 | 99.61c | $+58.26 | $+0.36 | needs ~474 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1951 | 111 | 104 | 0 | 99.55c | $+44.41 | $+0.42 | needs ~445 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 737 | 732 | 725 | 47 | 93.65c | $-330.12 | $-0.48 | needs ~213 more bets with no loss |

