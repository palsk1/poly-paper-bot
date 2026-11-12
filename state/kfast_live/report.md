# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 987 coin-windows from 2026-11-10T10:30 to 2026-11-12T05:30 UTC (141 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **8 of 987** windows. Reading the Kalshi book takes about 175 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 716 | 51 | 51 | 1 | 99.75c | $-9.24 | $-1.82 | needs ~2574 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 599 | 16 | 16 | 0 | 99.87c | $+0.05 | $+0.03 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 716 | 28 | 27 | 1 | 99.39c | $-8.40 | $-3.07 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 856 | 192 | 191 | 4 | 98.84c | $-19.96 | $-1.05 | needs ~571 more bets with no loss |
| Buy now, 60 s left (z 4+) | 591 | 71 | 71 | 0 | 99.57c | $+2.28 | $+0.32 | needs ~647 more bets with no loss |
| Buy now, 30 s left (z 4+) | 851 | 49 | 49 | 0 | 99.71c | $+0.93 | $+0.19 | needs ~1162 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 312 | 310 | 310 | 18 | 93.19c | $+17.87 | $+0.62 | needs ~75 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 716 | 51 | 51 | 1 | 99.76c | $-88.99 | $-1.75 | needs ~1750 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 599 | 16 | 16 | 0 | 99.88c | $+1.78 | $+0.11 | needs ~2048 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 716 | 28 | 25 | 1 | 99.39c | $-84.65 | $-3.26 | needs ~632 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 856 | 192 | 186 | 4 | 98.88c | $-202.24 | $-1.08 | needs ~569 more bets with no loss |
| Buy now, 60 s left (z 4+) | 591 | 71 | 69 | 0 | 99.57c | $+27.57 | $+0.40 | needs ~512 more bets with no loss |
| Buy now, 30 s left (z 4+) | 851 | 49 | 48 | 0 | 99.71c | $+12.88 | $+0.26 | needs ~824 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 312 | 310 | 309 | 18 | 93.38c | $+139.03 | $+0.48 | needs ~83 more bets with no loss |

