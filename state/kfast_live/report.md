# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2380 coin-windows from 2026-11-10T10:30 to 2026-11-14T23:30 UTC (340 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **40 of 2380** windows. Reading the Kalshi book takes about 138 ms (slowest 1 in 10: 242 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1714 | 142 | 140 | 1 | 99.78c | $-8.39 | $-0.60 | needs ~3249 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1417 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1714 | 64 | 63 | 1 | 99.43c | $-6.53 | $-1.03 | needs ~648 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2053 | 464 | 461 | 7 | 98.95c | $-26.32 | $-0.57 | needs ~782 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1403 | 181 | 174 | 0 | 99.62c | $+4.65 | $+0.27 | needs ~681 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2028 | 113 | 111 | 0 | 99.54c | $+3.87 | $+0.35 | needs ~547 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 779 | 773 | 771 | 52 | 93.16c | $-24.76 | $-0.34 | needs ~196 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1714 | 142 | 138 | 1 | 99.79c | $-73.68 | $-0.53 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1417 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1714 | 64 | 59 | 1 | 99.44c | $-66.32 | $-1.09 | needs ~641 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2053 | 464 | 451 | 7 | 98.99c | $-268.15 | $-0.59 | needs ~777 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1403 | 181 | 169 | 0 | 99.62c | $+59.33 | $+0.35 | needs ~484 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2028 | 113 | 106 | 0 | 99.56c | $+44.59 | $+0.41 | needs ~451 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 779 | 773 | 766 | 52 | 93.29c | $-316.74 | $-0.44 | needs ~206 more bets with no loss |

