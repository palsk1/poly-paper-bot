# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 5894 coin-windows from 2026-11-10T10:30 to 2026-11-22T06:00 UTC (842 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **98 of 5894** windows. Reading the Kalshi book takes about 145 ms (slowest 1 in 10: 234 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4175 | 321 | 311 | 2 | 99.67c | $-13.13 | $-0.42 | needs ~2090 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3429 | 57 | 56 | 0 | 99.79c | $+0.61 | $+0.11 | needs ~2046 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4175 | 159 | 154 | 3 | 99.24c | $-18.64 | $-1.20 | needs ~757 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5029 | 1136 | 1124 | 16 | 98.87c | $-45.38 | $-0.41 | needs ~1069 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3405 | 436 | 422 | 3 | 99.68c | $-21.06 | $-0.50 | needs ~2727 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4962 | 248 | 245 | 0 | 99.58c | $+7.60 | $+0.31 | needs ~494 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1961 | 1950 | 1939 | 129 | 92.76c | $+29.80 | $+0.16 | needs ~171 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 4175 | 321 | 304 | 2 | 99.68c | $-108.26 | $-0.35 | needs ~1460 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 3429 | 57 | 53 | 0 | 99.80c | $+9.84 | $+0.18 | needs ~1207 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 4175 | 159 | 144 | 3 | 99.23c | $-189.41 | $-1.28 | needs ~737 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 5029 | 1136 | 1099 | 16 | 98.90c | $-456.86 | $-0.42 | needs ~1045 more bets with no loss |
| Buy now, 60 s left (z 4+) | 3405 | 436 | 414 | 3 | 99.69c | $-179.99 | $-0.43 | needs ~1890 more bets with no loss |
| Buy now, 30 s left (z 4+) | 4962 | 248 | 239 | 0 | 99.59c | $+91.17 | $+0.38 | needs ~366 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 1961 | 1950 | 1926 | 129 | 92.89c | $+124.61 | $+0.07 | needs ~193 more bets with no loss |

