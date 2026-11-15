# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2828 coin-windows from 2026-11-10T10:30 to 2026-11-15T20:30 UTC (404 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **48 of 2828** windows. Reading the Kalshi book takes about 148 ms (slowest 1 in 10: 247 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2019 | 177 | 174 | 2 | 99.60c | $-14.93 | $-0.86 | needs ~1654 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1653 | 38 | 37 | 0 | 99.81c | $+0.33 | $+0.09 | needs ~2527 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2019 | 91 | 89 | 3 | 99.10c | $-22.20 | $-2.48 | needs ~681 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2417 | 580 | 575 | 12 | 98.95c | $-65.43 | $-1.14 | needs ~1299 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1643 | 222 | 214 | 2 | 99.64c | $-14.75 | $-0.69 | needs ~1949 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2382 | 137 | 135 | 0 | 99.59c | $+4.03 | $+0.30 | needs ~635 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 955 | 949 | 946 | 68 | 92.73c | $-33.20 | $-0.38 | needs ~214 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 2019 | 177 | 170 | 2 | 99.60c | $-136.88 | $-0.80 | needs ~1269 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1653 | 38 | 34 | 0 | 99.82c | $+5.72 | $+0.16 | needs ~1372 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 2019 | 91 | 83 | 3 | 99.09c | $-224.08 | $-2.63 | needs ~663 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2417 | 580 | 564 | 12 | 98.99c | $-658.28 | $-1.17 | needs ~1288 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1643 | 222 | 209 | 2 | 99.65c | $-131.65 | $-0.62 | needs ~1424 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2382 | 137 | 130 | 0 | 99.61c | $+48.03 | $+0.36 | needs ~502 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 955 | 949 | 939 | 68 | 92.85c | $-413.78 | $-0.47 | needs ~224 more bets with no loss |

