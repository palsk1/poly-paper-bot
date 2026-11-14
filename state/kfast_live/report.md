# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2184 coin-windows from 2026-11-10T10:30 to 2026-11-14T14:00 UTC (312 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **35 of 2184** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 244 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1589 | 130 | 128 | 1 | 99.77c | $-8.39 | $-0.65 | needs ~2971 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1326 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1589 | 60 | 59 | 1 | 99.43c | $-6.73 | $-1.14 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1896 | 423 | 420 | 7 | 98.91c | $-28.45 | $-0.68 | needs ~771 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1316 | 171 | 165 | 0 | 99.61c | $+4.61 | $+0.28 | needs ~654 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1878 | 105 | 104 | 0 | 99.52c | $+3.85 | $+0.37 | needs ~517 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 699 | 694 | 692 | 42 | 93.50c | $+1.87 | $+0.03 | needs ~148 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1589 | 130 | 126 | 1 | 99.78c | $-74.76 | $-0.59 | needs ~1815 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1326 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1589 | 60 | 55 | 1 | 99.43c | $-68.32 | $-1.20 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 1896 | 423 | 410 | 7 | 98.94c | $-289.46 | $-0.70 | needs ~765 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1316 | 171 | 160 | 0 | 99.61c | $+58.08 | $+0.36 | needs ~473 more bets with no loss |
| Buy now, 30 s left (z 4+) | 1878 | 105 | 99 | 0 | 99.54c | $+43.69 | $+0.43 | needs ~434 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 699 | 694 | 687 | 42 | 93.62c | $-40.94 | $-0.06 | needs ~157 more bets with no loss |

