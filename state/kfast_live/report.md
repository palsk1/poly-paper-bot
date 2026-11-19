# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 4326 coin-windows from 2026-11-10T10:30 to 2026-11-19T00:45 UTC (618 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **69 of 4326** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 239 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3094 | 258 | 250 | 2 | 99.64c | $-13.81 | $-0.55 | needs ~1894 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2543 | 49 | 48 | 0 | 99.81c | $+0.44 | $+0.09 | needs ~2445 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3094 | 130 | 126 | 3 | 99.19c | $-20.16 | $-1.59 | needs ~736 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3704 | 879 | 871 | 14 | 98.88c | $-51.90 | $-0.60 | needs ~1114 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2527 | 337 | 328 | 3 | 99.67c | $-22.76 | $-0.69 | needs ~2691 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3644 | 202 | 199 | 0 | 99.59c | $+5.88 | $+0.30 | needs ~577 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1443 | 1434 | 1426 | 100 | 92.86c | $-43.73 | $-0.33 | needs ~261 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 3094 | 258 | 246 | 2 | 99.65c | $-119.86 | $-0.49 | needs ~1385 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 2543 | 49 | 45 | 0 | 99.82c | $+7.66 | $+0.17 | needs ~1334 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 3094 | 130 | 116 | 3 | 99.18c | $-204.56 | $-1.71 | needs ~712 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 3704 | 879 | 853 | 14 | 98.92c | $-524.77 | $-0.61 | needs ~1101 more bets with no loss |
| Buy now, 60 s left (z 4+) | 2527 | 337 | 320 | 3 | 99.68c | $-203.84 | $-0.63 | needs ~1912 more bets with no loss |
| Buy now, 30 s left (z 4+) | 3644 | 202 | 193 | 0 | 99.61c | $+70.58 | $+0.36 | needs ~441 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1443 | 1434 | 1417 | 100 | 93.00c | $-566.96 | $-0.43 | needs ~279 more bets with no loss |

