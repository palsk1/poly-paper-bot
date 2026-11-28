# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8708 coin-windows from 2026-11-10T10:30 to 2026-11-28T09:00 UTC (1234 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **146 of 8708** windows. Reading the Kalshi book takes about 140 ms (slowest 1 in 10: 226 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6120 | 457 | 443 | 2 | 99.63c | $-8.60 | $-0.19 | needs ~1614 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5003 | 84 | 82 | 0 | 99.79c | $+0.85 | $+0.10 | needs ~2129 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6120 | 240 | 230 | 3 | 99.19c | $-11.88 | $-0.51 | needs ~623 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7408 | 1674 | 1659 | 24 | 98.80c | $-59.02 | $-0.36 | needs ~1224 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4935 | 613 | 597 | 3 | 99.71c | $-18.91 | $-0.32 | needs ~2991 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7294 | 345 | 338 | 2 | 99.03c | $+8.91 | $+0.27 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2912 | 2896 | 2878 | 204 | 92.67c | $-58.07 | $-0.22 | needs ~342 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 6120 | 457 | 431 | 2 | 99.64c | $-55.16 | $-0.13 | needs ~1149 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 5003 | 84 | 79 | 0 | 99.80c | $+14.43 | $+0.18 | needs ~1193 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 6120 | 240 | 210 | 3 | 99.18c | $-126.57 | $-0.58 | needs ~602 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 7408 | 1674 | 1619 | 24 | 98.83c | $-595.55 | $-0.37 | needs ~1191 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4935 | 613 | 586 | 3 | 99.71c | $-144.93 | $-0.25 | needs ~1935 more bets with no loss |
| Buy now, 30 s left (z 4+) | 7294 | 345 | 330 | 2 | 99.04c | $+107.17 | $+0.32 | needs ~235 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2912 | 2896 | 2857 | 204 | 92.81c | $-856.93 | $-0.32 | needs ~377 more bets with no loss |

