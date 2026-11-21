# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5775 coin-windows from 2026-11-10T10:30 to 2026-11-21T22:00 UTC (825 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **98 of 5775** windows. Reading the Kalshi book takes about 146 ms (slowest 1 in 10: 235 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4082 | 316 | 306 | 2 | 99.67c | $-13.15 | $-0.43 | needs ~2064 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3342 | 56 | 55 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2009 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4082 | 157 | 153 | 3 | 99.24c | $-18.70 | $-1.22 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4924 | 1122 | 1113 | 17 | 98.91c | $-60.38 | $-0.55 | needs ~1278 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3326 | 427 | 414 | 3 | 99.66c | $-20.34 | $-0.49 | needs ~2445 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4857 | 244 | 241 | 0 | 99.58c | $+7.50 | $+0.31 | needs ~495 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1930 | 1919 | 1908 | 128 | 92.75c | $+19.63 | $+0.11 | needs ~185 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4082 | 316 | 299 | 2 | 99.67c | $-108.89 | $-0.36 | needs ~1448 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3342 | 56 | 52 | 0 | 99.80c | $+9.75 | $+0.18 | needs ~1196 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4082 | 157 | 143 | 3 | 99.23c | $-189.91 | $-1.30 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 4924 | 1122 | 1088 | 17 | 98.94c | $-605.12 | $-0.56 | needs ~1249 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3326 | 427 | 406 | 3 | 99.66c | $-173.58 | $-0.42 | needs ~1738 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4857 | 244 | 235 | 0 | 99.59c | $+89.56 | $+0.38 | needs ~371 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1930 | 1919 | 1895 | 128 | 92.88c | $+27.31 | $+0.02 | needs ~206 more bets with no loss |

