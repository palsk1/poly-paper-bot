# Fast Kalshi paper bot (last 45 seconds)

Live paper test, `kfastlive.py`. 2590 coin-windows from 2026-11-10T10:30 to 2026-11-15T11:45 UTC (370 closes watched). Paper only, nothing is really bought.

Binance guessed Kalshi's result wrong on **44 of 2590** windows. Reading the Kalshi book takes about 137 ms (slowest 1 in 10: 243 ms).

P&L is after Kalshi's fee. "Full" = how often the whole order got filled. The proof line uses the repo's rule: one loss costs about a dollar a contract, so losses have to be rarer than what one bet earns, with 90% confidence.

## Orders of 10 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1868 | 158 | 155 | 1 | 99.79c | $-8.25 | $-0.53 | needs ~3305 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1541 | 31 | 30 | 0 | 99.85c | $+0.15 | $+0.05 | needs ~4568 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1868 | 76 | 75 | 1 | 99.44c | $-5.94 | $-0.79 | needs ~647 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2232 | 519 | 516 | 9 | 99.00c | $-43.24 | $-0.84 | needs ~1053 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1528 | 201 | 193 | 0 | 99.64c | $+4.85 | $+0.25 | needs ~717 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2202 | 124 | 122 | 0 | 99.57c | $+3.92 | $+0.32 | needs ~593 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 851 | 845 | 842 | 56 | 93.10c | $-14.27 | $-0.18 | needs ~182 more bets with no loss |

## Orders of 100 contracts

| Test | Chances | Bought | Full | Lost | Avg price | P&L | P&L per $100 | Proof |
|---|---|---|---|---|---|---|---|---|
| Buy now, 45 s left, Binance very sure (z 4+) (main) | 1868 | 158 | 152 | 1 | 99.79c | $-71.09 | $-0.47 | needs ~1901 more bets with no loss |
| Buy now, 45 s left, Binance extremely sure (z 6+) (main) | 1541 | 31 | 27 | 0 | 99.85c | $+3.78 | $+0.13 | needs ~1677 more bets with no loss |
| Wait at 99.5c, 45 s left (z 4+) (main) | 1868 | 76 | 70 | 1 | 99.45c | $-60.78 | $-0.85 | needs ~640 more bets with no loss |
| Wait at 99.8c, 45 s left (z 2+) (main) | 2232 | 519 | 505 | 9 | 99.03c | $-436.84 | $-0.86 | needs ~1046 more bets with no loss |
| Buy now, 60 s left (z 4+) | 1528 | 201 | 188 | 0 | 99.64c | $+62.79 | $+0.33 | needs ~497 more bets with no loss |
| Buy now, 30 s left (z 4+) | 2202 | 124 | 117 | 0 | 99.59c | $+45.95 | $+0.38 | needs ~479 more bets with no loss |
| Control: buy the favourite at 45 s, no Binance | 851 | 845 | 836 | 56 | 93.23c | $-217.87 | $-0.28 | needs ~193 more bets with no loss |

