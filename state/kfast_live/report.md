# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2499 coin-windows from 2026-11-10T10:30 to 2026-11-15T03:45 UTC (357 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **41 of 2499** windows. Reading the Kalshi book takes about 133 ms (slowest 1 in 10: 241 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1812 | 145 | 143 | 1 | 99.78c | $-8.34 | $-0.58 | needs ~3214 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1503 | 29 | 29 | 0 | 99.84c | $+0.16 | $+0.06 | needs ~4144 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1812 | 69 | 68 | 1 | 99.44c | $-6.29 | $-0.92 | needs ~649 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2161 | 488 | 485 | 7 | 98.98c | $-25.33 | $-0.52 | needs ~794 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1486 | 192 | 185 | 0 | 99.63c | $+4.69 | $+0.25 | needs ~717 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2136 | 116 | 114 | 0 | 99.55c | $+3.88 | $+0.34 | needs ~560 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 803 | 797 | 795 | 54 | 93.16c | $-29.78 | $-0.40 | needs ~207 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1812 | 145 | 141 | 1 | 99.79c | $-72.95 | $-0.52 | needs ~1886 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1503 | 29 | 27 | 0 | 99.85c | $+3.72 | $+0.14 | needs ~1657 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1812 | 69 | 63 | 1 | 99.44c | $-64.09 | $-0.98 | needs ~642 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2161 | 488 | 472 | 7 | 99.02c | $-258.61 | $-0.55 | needs ~786 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1486 | 192 | 180 | 0 | 99.64c | $+60.69 | $+0.33 | needs ~500 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2136 | 116 | 109 | 0 | 99.57c | $+44.95 | $+0.40 | needs ~459 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 803 | 797 | 790 | 54 | 93.30c | $-371.98 | $-0.50 | needs ~218 more bets with no loss |

