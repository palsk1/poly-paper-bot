# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 882 coin-windows from 2026-11-10T10:30 to 2026-11-12T01:45 UTC (126 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **7 of 882** windows. Reading the Kalshi book takes about 155 ms (slowest 1 in 10: 240 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 645 | 42 | 42 | 1 | 99.73c | $-9.29 | $-2.22 | needs ~2273 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 542 | 12 | 12 | 0 | 99.89c | $+0.01 | $+0.01 | needs ~5000 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 645 | 25 | 25 | 1 | 99.38c | $-8.53 | $-3.43 | needs ~636 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 771 | 163 | 162 | 4 | 98.80c | $-22.32 | $-1.39 | needs ~571 more bets with no loss |
| Buy now, 60 s left (z 4+) | 533 | 56 | 56 | 0 | 99.54c | $+1.94 | $+0.35 | needs ~608 more bets with no loss |
| Buy now, 30 s left (z 4+) | 764 | 42 | 42 | 0 | 99.71c | $+0.77 | $+0.18 | needs ~1212 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 270 | 269 | 269 | 16 | 93.31c | $+8.77 | $+0.35 | needs ~86 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 645 | 42 | 42 | 1 | 99.75c | $-90.21 | $-2.15 | needs ~1625 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 542 | 12 | 12 | 0 | 99.90c | $+1.10 | $+0.09 | needs ~2490 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 645 | 25 | 24 | 1 | 99.39c | $-85.60 | $-3.56 | needs ~627 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 771 | 163 | 157 | 4 | 98.83c | $-224.32 | $-1.42 | needs ~561 more bets with no loss |
| Buy now, 60 s left (z 4+) | 533 | 56 | 55 | 0 | 99.54c | $+23.44 | $+0.43 | needs ~486 more bets with no loss |
| Buy now, 30 s left (z 4+) | 764 | 42 | 41 | 0 | 99.72c | $+10.84 | $+0.26 | needs ~847 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 270 | 269 | 268 | 16 | 93.49c | $+54.74 | $+0.22 | needs ~93 more bets with no loss |

