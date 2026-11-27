# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 8099 coin-windows from 2026-11-10T10:30 to 2026-11-27T07:30 UTC (1157 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **132 of 8099** windows. Reading the Kalshi book takes about 142 ms (slowest 1 in 10: 229 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5710 | 411 | 400 | 2 | 99.62c | $-9.30 | $-0.23 | needs ~1581 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4681 | 75 | 74 | 0 | 99.79c | $+0.81 | $+0.11 | needs ~2020 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5710 | 211 | 203 | 3 | 99.16c | $-13.43 | $-0.66 | needs ~618 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6893 | 1533 | 1518 | 21 | 98.88c | $-56.32 | $-0.37 | needs ~1254 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4617 | 572 | 556 | 3 | 99.70c | $-19.50 | $-0.35 | needs ~2973 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6787 | 315 | 309 | 2 | 98.98c | $+7.74 | $+0.25 | needs ~277 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2682 | 2666 | 2652 | 189 | 92.71c | $-73.11 | $-0.30 | needs ~360 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 5710 | 411 | 389 | 2 | 99.63c | $-65.17 | $-0.17 | needs ~1146 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 4681 | 75 | 71 | 0 | 99.80c | $+13.26 | $+0.18 | needs ~1175 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 5710 | 211 | 188 | 3 | 99.15c | $-139.91 | $-0.72 | needs ~601 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 6893 | 1533 | 1479 | 21 | 98.91c | $-567.40 | $-0.38 | needs ~1219 more bets with no loss |
| Buy now, 60 s left (z 4+) | 4617 | 572 | 547 | 3 | 99.71c | $-153.65 | $-0.28 | needs ~1943 more bets with no loss |
| Buy now, 30 s left (z 4+) | 6787 | 315 | 301 | 2 | 99.00c | $+94.03 | $+0.31 | needs ~238 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 2682 | 2666 | 2634 | 189 | 92.84c | $-976.82 | $-0.40 | needs ~392 more bets with no loss |

