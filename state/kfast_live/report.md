# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2345 coin-windows from 2026-11-10T10:30 to 2026-11-14T20:15 UTC (335 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **39 of 2345** windows. Reading the Kalshi book takes about 139 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1690 | 140 | 138 | 1 | 99.78c | $-8.39 | $-0.61 | needs ~3202 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1398 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1690 | 64 | 63 | 1 | 99.43c | $-6.53 | $-1.03 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2025 | 459 | 456 | 7 | 98.95c | $-26.67 | $-0.59 | needs ~784 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1387 | 178 | 171 | 0 | 99.61c | $+4.65 | $+0.27 | needs ~669 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2001 | 113 | 111 | 0 | 99.54c | $+3.87 | $+0.35 | needs ~547 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 766 | 760 | 758 | 50 | 93.31c | $-24.55 | $-0.35 | needs ~198 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1690 | 140 | 136 | 1 | 99.79c | $-73.86 | $-0.54 | needs ~1887 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1398 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1690 | 64 | 59 | 1 | 99.44c | $-66.32 | $-1.09 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2025 | 459 | 446 | 7 | 98.99c | $-271.48 | $-0.61 | needs ~778 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1387 | 178 | 166 | 0 | 99.62c | $+59.06 | $+0.35 | needs ~478 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2001 | 113 | 106 | 0 | 99.56c | $+44.59 | $+0.41 | needs ~451 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 766 | 760 | 753 | 50 | 93.44c | $-308.17 | $-0.43 | needs ~207 more bets with no loss |

