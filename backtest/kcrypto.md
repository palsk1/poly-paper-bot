# Kalshi 15-minute crypto: the 'late favorite maker' backtest

Generated 2026-11-09T18:53:51Z. 39820 settled windows (KXBNB15M, KXBTC15M, KXDOGE15M, KXETH15M, KXHYPE15M, KXSOL15M, KXXRP15M), closing 2026-09-10 to 2026-11-09. Paper only. Code: `kcrypto.py`.

The idea: with M minutes left, rest a buy order on the side that's winning and hold it to the close. Makers pay no fee on these series. A resting order only fills when someone sells into it, so fills are modelled from later trades (see the top of kcrypto.py). 'Won out of 100' compares all signals with the ones that actually filled: if filled orders win less often, the fills are picked off (adverse selection).

Main fill model: **fair**. P&L per $100 staked. The 90% band resamples whole days.

## In plain words (Claude, 2026-11-09)

- **Parking an order at a fixed 90-97c and waiting for a dip loses** ($0.30 to $5.30 per $100). The dips that fill you are the ones where the coin is about to flip: filled orders win 85-97 times in 100, against 98-99 for all signals. That is the adverse selection the Reddit thread kept asking about, and it's large.
- **Sitting at (or one tick in front of) the best bid is about break-even**: -$0.30 to +$0.20 per $100 in the last 1-3 minutes. Zero fees and the spread are worth about as much as the losers cost.
- **Buying at the ask (taker) is also about zero.** These markets are priced very fairly.
- **The one thing that helped: a spot check.** Only bidding when Binance spot is 2+ "typical moves until the close" past the strike made +$0.56 per $100 (band +$0.41 to +$0.73, both halves ahead, 8,663 fills). That is about half a cent on a 99c contract. One loss still eats ~80 wins.
- **Earlier is a bit better than later**: 7-10 minutes left did +$0.70 to +$1.50 per $100 at the best bid, but with fewer fills and wider bands.
- About 105 variants were tried, so a few look good by luck. The spot-check result holds across three different order types and three thresholds, which is a better sign than one lucky line. It is still only 60 days, and the size that fills at the front of the line is unknown.
- Paper tracks: `kc_maker` (the Reddit way), `kc_maker_safe` (+ spot check), `kc_maker_early` (6.5-11.5 minutes left).


## 1. Fixed price, by minutes left (fair fills)

Bid at the fixed price while the leader's mid-price is at or above it (and its ask is above it).

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| 90c, 1 min left | 20707 | 1921 (9 in 100) | 1637/284 | 98.6 vs 85.2 | 90.0c | 10.00c | 9 | -$5.32 | -$7.31 to -$3.51 | -$3.94 / -$6.69 |
| 90c, 2 min left | 26801 | 3685 (14 in 100) | 3167/518 | 98.1 vs 85.9 | 90.0c | 10.00c | 9 | -$4.51 | -$5.78 to -$3.26 | -$4.63 / -$4.38 |
| 90c, 3 min left | 24713 | 4507 (18 in 100) | 3926/581 | 97.6 vs 87.1 | 90.0c | 10.00c | 9 | -$3.21 | -$4.19 to -$2.32 | -$2.99 / -$3.43 |
| 90c, 5 min left | 17883 | 5107 (29 in 100) | 4452/655 | 96.3 vs 87.2 | 90.0c | 10.00c | 9 | -$3.14 | -$4.64 to -$1.54 | -$3.56 / -$2.72 |
| 90c, 7 min left | 11540 | 4289 (37 in 100) | 3819/470 | 95.9 vs 89.0 | 90.0c | 10.00c | 9 | -$1.06 | -$2.27 to +$0.46 | -$0.50 / -$1.63 |
| 90c, 10 min left | 3950 | 2209 (56 in 100) | 2014/195 | 95.1 vs 91.2 | 90.0c | 10.00c | 9 | +$1.30 | -$0.24 to +$3.00 | +$2.44 / +$0.17 |
| 93c, 1 min left | 19639 | 1985 (10 in 100) | 1803/182 | 99.1 vs 90.8 | 93.0c | 7.00c | 13 | -$2.33 | -$3.91 to -$0.88 | -$2.34 / -$2.33 |
| 93c, 2 min left | 24850 | 3737 (15 in 100) | 3416/321 | 98.7 vs 91.4 | 93.0c | 7.00c | 13 | -$1.71 | -$2.66 to -$0.85 | -$1.51 / -$1.91 |
| 93c, 3 min left | 22157 | 4393 (20 in 100) | 4021/372 | 98.3 vs 91.5 | 93.0c | 7.00c | 13 | -$1.58 | -$2.26 to -$0.81 | -$1.68 / -$1.48 |
| 93c, 5 min left | 14711 | 4673 (32 in 100) | 4294/379 | 97.4 vs 91.9 | 93.0c | 7.00c | 13 | -$1.19 | -$2.43 to +$0.14 | -$1.77 / -$0.62 |
| 93c, 7 min left | 8264 | 3449 (42 in 100) | 3209/240 | 97.1 vs 93.0 | 93.0c | 7.00c | 13 | +$0.04 | -$1.07 to +$1.33 | +$0.67 / -$0.58 |
| 93c, 10 min left | 1887 | 1140 (60 in 100) | 1085/55 | 97.1 vs 95.2 | 93.0c | 7.00c | 13 | +$2.34 | +$0.80 to +$3.83 | +$3.00 / +$1.68 |
| 95c, 1 min left | 18708 | 1999 (11 in 100) | 1866/133 | 99.3 vs 93.3 | 95.0c | 5.00c | 19 | -$1.74 | -$2.89 to -$0.51 | -$2.22 / -$1.26 |
| 95c, 2 min left | 23104 | 3573 (15 in 100) | 3363/210 | 99.1 vs 94.1 | 95.0c | 5.00c | 19 | -$0.92 | -$1.71 to -$0.21 | -$0.64 / -$1.21 |
| 95c, 3 min left | 19949 | 4139 (21 in 100) | 3878/261 | 98.7 vs 93.7 | 95.0c | 5.00c | 19 | -$1.37 | -$2.11 to -$0.61 | -$1.76 / -$0.99 |
| 95c, 5 min left | 12042 | 4029 (33 in 100) | 3801/228 | 98.1 vs 94.3 | 95.0c | 5.00c | 19 | -$0.69 | -$1.80 to +$0.53 | -$1.43 / +$0.04 |
| 95c, 7 min left | 5915 | 2669 (45 in 100) | 2534/135 | 97.7 vs 94.9 | 95.0c | 5.00c | 19 | -$0.06 | -$1.21 to +$1.19 | +$0.37 / -$0.49 |
| 95c, 10 min left | 923 | 589 (64 in 100) | 566/23 | 97.5 vs 96.1 | 95.0c | 5.00c | 19 | +$1.15 | -$0.82 to +$3.09 | +$1.32 / +$0.98 |
| 97c, 1 min left | 17170 | 2123 (12 in 100) | 2042/81 | 99.5 vs 96.2 | 97.0c | 3.00c | 32 | -$0.84 | -$1.83 to +$0.19 | -$1.38 / -$0.30 |
| 97c, 2 min left | 20573 | 3644 (18 in 100) | 3524/120 | 99.4 vs 96.7 | 97.0c | 3.00c | 32 | -$0.30 | -$0.82 to +$0.25 | -$0.02 / -$0.59 |
| 97c, 3 min left | 16766 | 4025 (24 in 100) | 3888/137 | 99.2 vs 96.6 | 97.0c | 3.00c | 32 | -$0.42 | -$1.03 to +$0.18 | -$0.70 / -$0.13 |
| 97c, 5 min left | 8570 | 3327 (39 in 100) | 3229/98 | 98.9 vs 97.1 | 97.0c | 3.00c | 32 | +$0.06 | -$1.03 to +$0.97 | -$0.69 / +$0.80 |
| 97c, 7 min left | 3222 | 1715 (53 in 100) | 1681/34 | 98.9 vs 98.0 | 97.0c | 3.00c | 32 | +$1.05 | +$0.16 to +$1.91 | +$2.13 / -$0.03 |
| 97c, 10 min left | 263 | 214 (81 in 100) | 210/4 | 98.5 vs 98.1 | 97.0c | 3.00c | 32 | +$1.17 | -$0.23 to +$2.58 | +$2.13 / +$0.20 |
| 98c, 1 min left | 15925 | 2168 (14 in 100) | 2116/52 | 99.7 vs 97.6 | 98.0c | 2.00c | 49 | -$0.41 | -$1.00 to +$0.35 | -$0.50 / -$0.31 |
| 98c, 2 min left | 18331 | 3925 (21 in 100) | 3851/74 | 99.6 vs 98.1 | 98.0c | 2.00c | 49 | +$0.12 | -$0.36 to +$0.55 | +$0.64 / -$0.40 |
| 98c, 3 min left | 14172 | 4143 (29 in 100) | 4066/77 | 99.5 vs 98.1 | 98.0c | 2.00c | 49 | +$0.14 | -$0.25 to +$0.55 | +$0.17 / +$0.12 |
| 98c, 5 min left | 5959 | 2916 (49 in 100) | 2867/49 | 99.2 vs 98.3 | 98.0c | 2.00c | 49 | +$0.33 | -$0.37 to +$0.95 | -$0.20 / +$0.85 |
| 98c, 7 min left | 1688 | 1034 (61 in 100) | 1014/20 | 98.8 vs 98.1 | 98.0c | 2.00c | 49 | +$0.07 | -$1.04 to +$1.05 | +$1.45 / -$1.31 |
| 98c, 10 min left | 63 | 54 (86 in 100) | 54/0 | 100.0 vs 100.0 | 98.0c | 2.00c | - | +$2.04 | +$2.04 to +$2.04 | +$2.04 / +$2.04 |
| 99c, 1 min left | 13515 | 1861 (14 in 100) | 1836/25 | 99.8 vs 98.7 | 99.0c | 1.00c | 99 | -$0.35 | -$0.85 to +$0.20 | -$0.73 / +$0.03 |
| 99c, 2 min left | 14006 | 3310 (24 in 100) | 3280/30 | 99.8 vs 99.1 | 99.0c | 1.00c | 99 | +$0.09 | -$0.31 to +$0.45 | +$0.09 / +$0.09 |
| 99c, 3 min left | 9730 | 3326 (34 in 100) | 3299/27 | 99.7 vs 99.2 | 99.0c | 1.00c | 99 | +$0.19 | -$0.08 to +$0.47 | +$0.10 / +$0.28 |
| 99c, 5 min left | 2108 | 1209 (57 in 100) | 1197/12 | 99.4 vs 99.0 | 99.0c | 1.00c | 99 | +$0.01 | -$0.66 to +$0.55 | -$0.50 / +$0.51 |
| 99c, 7 min left | 155 | 116 (75 in 100) | 113/3 | 98.1 vs 97.4 | 99.0c | 1.00c | 99 | -$1.60 | -$4.00 to +$1.01 | -$0.73 / -$2.47 |
| 99c, 10 min left | 1 | 1 (100 in 100) | 1/0 | 100.0 vs 100.0 | 99.0c | 1.00c | - | +$1.01 | +$1.01 to +$1.01 | +$0.00 / +$1.01 |

## 2. Join the best bid / step one tick in front of it (fair fills)

join = same price as the best bid, back of the line (strict fills only). improve = one tick (0.1c) above the best bid, front of the line.

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| join, leader bid 90c+, 1 min left | 20577 | 10635 (52 in 100) | 10370/265 | 98.7 vs 97.5 | 97.8c | 2.10c | 45 | -$0.31 | -$0.66 to +$0.03 | -$0.11 / -$0.51 |
| join, leader bid 90c+, 2 min left | 26716 | 18448 (69 in 100) | 17937/511 | 98.1 vs 97.2 | 97.5c | 2.38c | 40 | -$0.30 | -$0.55 to -$0.04 | -$0.16 / -$0.44 |
| join, leader bid 90c+, 3 min left | 24643 | 19127 (78 in 100) | 18553/574 | 97.7 vs 97.0 | 97.1c | 2.84c | 33 | -$0.08 | -$0.30 to +$0.14 | +$0.01 / -$0.17 |
| join, leader bid 90c+, 5 min left | 17847 | 15258 (85 in 100) | 14604/654 | 96.3 vs 95.7 | 95.9c | 4.01c | 23 | -$0.18 | -$0.67 to +$0.37 | -$0.25 / -$0.12 |
| join, leader bid 90c+, 7 min left | 11505 | 9966 (87 in 100) | 9501/465 | 96.0 vs 95.3 | 94.8c | 5.17c | 18 | +$0.61 | +$0.10 to +$1.24 | +$1.08 / +$0.14 |
| join, leader bid 90c+, 10 min left | 3934 | 3492 (89 in 100) | 3297/195 | 95.0 vs 94.4 | 93.1c | 6.86c | 13 | +$1.43 | +$0.37 to +$2.55 | +$1.86 / +$1.00 |
| join, leader bid 95c+, 1 min left | 18448 | 9072 (49 in 100) | 8946/126 | 99.3 vs 98.6 | 98.7c | 1.25c | 78 | -$0.12 | -$0.36 to +$0.14 | -$0.25 / +$0.02 |
| join, leader bid 95c+, 2 min left | 22854 | 15214 (67 in 100) | 15016/198 | 99.1 vs 98.7 | 98.6c | 1.41c | 69 | +$0.13 | -$0.06 to +$0.30 | +$0.30 / -$0.04 |
| join, leader bid 95c+, 3 min left | 19722 | 14989 (76 in 100) | 14745/244 | 98.8 vs 98.4 | 98.3c | 1.66c | 58 | +$0.06 | -$0.14 to +$0.25 | +$0.05 / +$0.06 |
| join, leader bid 95c+, 5 min left | 11865 | 10041 (85 in 100) | 9823/218 | 98.2 vs 97.8 | 97.6c | 2.36c | 41 | +$0.21 | -$0.25 to +$0.71 | -$0.11 / +$0.53 |
| join, leader bid 95c+, 7 min left | 5786 | 5053 (87 in 100) | 4923/130 | 97.8 vs 97.4 | 97.0c | 2.95c | 33 | +$0.41 | -$0.19 to +$1.07 | +$0.77 / +$0.04 |
| join, leader bid 95c+, 10 min left | 893 | 817 (91 in 100) | 794/23 | 97.4 vs 97.2 | 96.3c | 3.64c | 26 | +$0.87 | -$0.56 to +$2.26 | +$1.02 / +$0.72 |
| join, leader bid 97c+, 1 min left | 16945 | 8004 (47 in 100) | 7926/78 | 99.5 vs 99.0 | 99.1c | 0.90c | 109 | -$0.07 | -$0.27 to +$0.17 | -$0.22 / +$0.09 |
| join, leader bid 97c+, 2 min left | 20273 | 13107 (65 in 100) | 12995/112 | 99.4 vs 99.1 | 99.0c | 1.01c | 97 | +$0.17 | +$0.01 to +$0.32 | +$0.30 / +$0.03 |
| join, leader bid 97c+, 3 min left | 16500 | 12344 (75 in 100) | 12215/129 | 99.2 vs 99.0 | 98.8c | 1.18c | 83 | +$0.14 | -$0.07 to +$0.34 | +$0.10 / +$0.19 |
| join, leader bid 97c+, 5 min left | 8364 | 7039 (84 in 100) | 6948/91 | 98.9 vs 98.7 | 98.3c | 1.67c | 59 | +$0.39 | -$0.08 to +$0.80 | +$0.10 / +$0.67 |
| join, leader bid 97c+, 7 min left | 3070 | 2721 (89 in 100) | 2690/31 | 99.0 vs 98.9 | 98.0c | 2.03c | 48 | +$0.91 | +$0.41 to +$1.42 | +$1.58 / +$0.24 |
| join, leader bid 97c+, 10 min left | 248 | 235 (95 in 100) | 231/4 | 98.4 vs 98.3 | 97.6c | 2.39c | 41 | +$0.71 | -$0.65 to +$2.01 | +$1.66 / -$0.24 |
| join, leader bid 99c+, 1 min left | 13276 | 5489 (41 in 100) | 5468/21 | 99.8 vs 99.6 | 99.5c | 0.46c | 215 | +$0.08 | -$0.07 to +$0.25 | +$0.05 / +$0.11 |
| join, leader bid 99c+, 2 min left | 13613 | 8041 (59 in 100) | 8014/27 | 99.8 vs 99.7 | 99.5c | 0.50c | 200 | +$0.16 | -$0.01 to +$0.29 | +$0.17 / +$0.16 |
| join, leader bid 99c+, 3 min left | 9400 | 6620 (70 in 100) | 6596/24 | 99.7 vs 99.6 | 99.4c | 0.58c | 172 | +$0.21 | +$0.08 to +$0.35 | +$0.18 / +$0.24 |
| join, leader bid 99c+, 5 min left | 2000 | 1653 (83 in 100) | 1643/10 | 99.5 vs 99.4 | 99.3c | 0.74c | 135 | +$0.13 | -$0.31 to +$0.52 | -$0.22 / +$0.48 |
| join, leader bid 99c+, 7 min left | 145 | 130 (90 in 100) | 127/3 | 97.9 vs 97.7 | 99.2c | 0.78c | 128 | -$1.55 | -$3.92 to +$0.77 | -$0.77 / -$2.32 |
| join, leader bid 99c+, 10 min left | 1 | 1 (100 in 100) | 1/0 | 100.0 vs 100.0 | 99.5c | 0.50c | - | +$0.50 | +$0.50 to +$0.50 | +$0.00 / +$0.50 |
| improve, leader bid 90c+, 1 min left | 20577 | 12052 (59 in 100) | 11787/265 | 98.7 vs 97.8 | 97.9c | 2.01c | 47 | -$0.12 | -$0.43 to +$0.18 | +$0.04 / -$0.29 |
| improve, leader bid 90c+, 2 min left | 26716 | 20084 (75 in 100) | 19573/511 | 98.1 vs 97.5 | 97.6c | 2.29c | 41 | -$0.17 | -$0.40 to +$0.07 | -$0.04 / -$0.31 |
| improve, leader bid 90c+, 3 min left | 24643 | 20367 (83 in 100) | 19793/574 | 97.7 vs 97.2 | 97.2c | 2.75c | 34 | +$0.02 | -$0.19 to +$0.23 | +$0.08 / -$0.05 |
| improve, leader bid 90c+, 5 min left | 17847 | 15924 (89 in 100) | 15270/654 | 96.3 vs 95.9 | 96.0c | 3.94c | 24 | -$0.07 | -$0.54 to +$0.46 | -$0.11 / -$0.04 |
| improve, leader bid 90c+, 7 min left | 11505 | 10331 (90 in 100) | 9866/465 | 96.0 vs 95.5 | 94.8c | 5.12c | 18 | +$0.73 | +$0.23 to +$1.34 | +$1.19 / +$0.26 |
| improve, leader bid 90c+, 10 min left | 3934 | 3585 (91 in 100) | 3390/195 | 95.0 vs 94.6 | 93.1c | 6.81c | 14 | +$1.53 | +$0.49 to +$2.64 | +$1.97 / +$1.10 |
| improve, leader bid 95c+, 1 min left | 18448 | 10343 (56 in 100) | 10217/126 | 99.3 vs 98.8 | 98.8c | 1.18c | 82 | -$0.02 | -$0.23 to +$0.21 | -$0.15 / +$0.11 |
| improve, leader bid 95c+, 2 min left | 22854 | 16682 (73 in 100) | 16484/198 | 99.1 vs 98.8 | 98.6c | 1.35c | 72 | +$0.18 | +$0.01 to +$0.34 | +$0.34 / +$0.02 |
| improve, leader bid 95c+, 3 min left | 19722 | 16053 (81 in 100) | 15809/244 | 98.8 vs 98.5 | 98.4c | 1.60c | 61 | +$0.10 | -$0.08 to +$0.29 | +$0.09 / +$0.12 |
| improve, leader bid 95c+, 5 min left | 11865 | 10534 (89 in 100) | 10316/218 | 98.2 vs 97.9 | 97.7c | 2.30c | 42 | +$0.26 | -$0.18 to +$0.73 | -$0.03 / +$0.55 |
| improve, leader bid 95c+, 7 min left | 5786 | 5247 (91 in 100) | 5117/130 | 97.8 vs 97.5 | 97.1c | 2.90c | 33 | +$0.45 | -$0.11 to +$1.08 | +$0.81 / +$0.10 |
| improve, leader bid 95c+, 10 min left | 893 | 834 (93 in 100) | 811/23 | 97.4 vs 97.2 | 96.4c | 3.60c | 27 | +$0.88 | -$0.53 to +$2.26 | +$1.03 / +$0.73 |
| improve, leader bid 97c+, 1 min left | 16945 | 9174 (54 in 100) | 9096/78 | 99.5 vs 99.1 | 99.1c | 0.85c | 116 | +$0.00 | -$0.17 to +$0.21 | -$0.12 / +$0.12 |
| improve, leader bid 97c+, 2 min left | 20273 | 14453 (71 in 100) | 14341/112 | 99.4 vs 99.2 | 99.0c | 0.97c | 102 | +$0.20 | +$0.06 to +$0.34 | +$0.32 / +$0.08 |
| improve, leader bid 97c+, 3 min left | 16500 | 13288 (81 in 100) | 13159/129 | 99.2 vs 99.0 | 98.9c | 1.13c | 87 | +$0.17 | -$0.02 to +$0.36 | +$0.12 / +$0.22 |
| improve, leader bid 97c+, 5 min left | 8364 | 7417 (89 in 100) | 7326/91 | 98.9 vs 98.8 | 98.4c | 1.62c | 60 | +$0.41 | -$0.05 to +$0.80 | +$0.12 / +$0.69 |
| improve, leader bid 97c+, 7 min left | 3070 | 2827 (92 in 100) | 2796/31 | 99.0 vs 98.9 | 98.0c | 1.99c | 49 | +$0.91 | +$0.43 to +$1.40 | +$1.56 / +$0.26 |
| improve, leader bid 97c+, 10 min left | 248 | 237 (96 in 100) | 233/4 | 98.4 vs 98.3 | 97.6c | 2.34c | 41 | +$0.68 | -$0.66 to +$1.97 | +$1.63 / -$0.24 |
| improve, leader bid 99c+, 1 min left | 13276 | 6440 (49 in 100) | 6419/21 | 99.8 vs 99.7 | 99.6c | 0.44c | 224 | +$0.12 | -$0.01 to +$0.26 | +$0.07 / +$0.17 |
| improve, leader bid 99c+, 2 min left | 13613 | 8989 (66 in 100) | 8962/27 | 99.8 vs 99.7 | 99.5c | 0.48c | 209 | +$0.18 | +$0.03 to +$0.29 | +$0.18 / +$0.17 |
| improve, leader bid 99c+, 3 min left | 9400 | 7218 (77 in 100) | 7194/24 | 99.7 vs 99.7 | 99.5c | 0.55c | 181 | +$0.22 | +$0.09 to +$0.34 | +$0.19 / +$0.24 |
| improve, leader bid 99c+, 5 min left | 2000 | 1767 (88 in 100) | 1757/10 | 99.5 vs 99.4 | 99.3c | 0.70c | 142 | +$0.13 | -$0.27 to +$0.49 | -$0.20 / +$0.46 |
| improve, leader bid 99c+, 7 min left | 145 | 132 (91 in 100) | 129/3 | 97.9 vs 97.7 | 99.3c | 0.74c | 134 | -$1.55 | -$3.83 to +$0.73 | -$0.78 / -$2.32 |
| improve, leader bid 99c+, 10 min left | 1 | 1 (100 in 100) | 1/0 | 100.0 vs 100.0 | 99.5c | 0.50c | - | +$0.50 | +$0.50 to +$0.50 | +$0.00 / +$0.50 |

## 3. Same orders, three fill models

strict = only when a trade printed below our price; touch = any trade at our price (optimistic).

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| improve 95c, 3 min, strict | 19722 | 15704 (80 in 100) | 15460/244 | 98.8 vs 98.4 | 98.4c | 1.61c | 60 | +$0.08 | -$0.11 to +$0.27 | +$0.06 / +$0.09 |
| improve 95c, 3 min, fair | 19722 | 16053 (81 in 100) | 15809/244 | 98.8 vs 98.5 | 98.4c | 1.60c | 61 | +$0.10 | -$0.08 to +$0.29 | +$0.09 / +$0.12 |
| improve 95c, 3 min, touch | 19722 | 17729 (90 in 100) | 17485/244 | 98.8 vs 98.6 | 98.4c | 1.54c | 63 | +$0.18 | +$0.02 to +$0.35 | +$0.19 / +$0.18 |
| improve 97c, 2 min, strict | 20273 | 14007 (69 in 100) | 13895/112 | 99.4 vs 99.2 | 99.0c | 0.97c | 101 | +$0.18 | +$0.03 to +$0.32 | +$0.30 / +$0.05 |
| improve 97c, 2 min, fair | 20273 | 14453 (71 in 100) | 14341/112 | 99.4 vs 99.2 | 99.0c | 0.97c | 102 | +$0.20 | +$0.06 to +$0.34 | +$0.32 / +$0.08 |
| improve 97c, 2 min, touch | 20273 | 17580 (87 in 100) | 17468/112 | 99.4 vs 99.4 | 99.1c | 0.88c | 111 | +$0.25 | +$0.14 to +$0.36 | +$0.33 / +$0.18 |
| level 97c, 3 min, strict | 16766 | 4016 (24 in 100) | 3879/137 | 99.2 vs 96.6 | 97.0c | 3.00c | 32 | -$0.42 | -$1.04 to +$0.17 | -$0.71 / -$0.14 |
| level 97c, 3 min, fair | 16766 | 4025 (24 in 100) | 3888/137 | 99.2 vs 96.6 | 97.0c | 3.00c | 32 | -$0.42 | -$1.03 to +$0.18 | -$0.70 / -$0.13 |
| level 97c, 3 min, touch | 16766 | 4549 (27 in 100) | 4412/137 | 99.2 vs 97.0 | 97.0c | 3.00c | 32 | -$0.01 | -$0.58 to +$0.53 | -$0.22 / +$0.19 |
| level 95c, 5 min, strict | 12042 | 4026 (33 in 100) | 3798/228 | 98.1 vs 94.3 | 95.0c | 5.00c | 19 | -$0.70 | -$1.81 to +$0.52 | -$1.43 / +$0.04 |
| level 95c, 5 min, fair | 12042 | 4029 (33 in 100) | 3801/228 | 98.1 vs 94.3 | 95.0c | 5.00c | 19 | -$0.69 | -$1.80 to +$0.53 | -$1.43 / +$0.04 |
| level 95c, 5 min, touch | 12042 | 4337 (36 in 100) | 4109/228 | 98.1 vs 94.7 | 95.0c | 5.00c | 19 | -$0.27 | -$1.30 to +$0.83 | -$0.90 / +$0.36 |
| join 95c, 3 min, strict | 19722 | 14989 (76 in 100) | 14745/244 | 98.8 vs 98.4 | 98.3c | 1.66c | 58 | +$0.06 | -$0.14 to +$0.25 | +$0.05 / +$0.06 |
| join 95c, 3 min, fair | 19722 | 14989 (76 in 100) | 14745/244 | 98.8 vs 98.4 | 98.3c | 1.66c | 58 | +$0.06 | -$0.14 to +$0.25 | +$0.05 / +$0.06 |
| join 95c, 3 min, touch | 19722 | 17380 (88 in 100) | 17136/244 | 98.8 vs 98.6 | 98.4c | 1.58c | 61 | +$0.20 | +$0.04 to +$0.37 | +$0.20 / +$0.20 |
| improve 90c, 5 min, strict | 17847 | 15700 (88 in 100) | 15046/654 | 96.3 vs 95.8 | 96.0c | 3.95c | 24 | -$0.13 | -$0.59 to +$0.41 | -$0.17 / -$0.08 |
| improve 90c, 5 min, fair | 17847 | 15924 (89 in 100) | 15270/654 | 96.3 vs 95.9 | 96.0c | 3.94c | 24 | -$0.07 | -$0.54 to +$0.46 | -$0.11 / -$0.04 |
| improve 90c, 5 min, touch | 17847 | 16577 (93 in 100) | 15923/654 | 96.3 vs 96.1 | 96.0c | 3.92c | 24 | +$0.06 | -$0.39 to +$0.58 | +$0.04 / +$0.09 |

## 4. Taker comparison: buy at the ask and pay the fee

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| taker, ask 90c+, 1 min left | 21145 | 21145 (100 in 100) | 20819/326 | 98.5 vs 98.5 | 98.6c | 1.34c | 71 | -$0.14 | -$0.34 to +$0.04 | -$0.02 / -$0.27 |
| taker, ask 90c+, 3 min left | 25558 | 25558 (100 in 100) | 24895/663 | 97.4 vs 97.4 | 97.5c | 2.45c | 39 | -$0.07 | -$0.24 to +$0.11 | +$0.01 / -$0.14 |
| taker, ask 90c+, 5 min left | 18964 | 18964 (100 in 100) | 18192/772 | 95.9 vs 95.9 | 96.2c | 3.74c | 25 | -$0.25 | -$0.67 to +$0.22 | -$0.36 / -$0.13 |
| taker, ask 95c+, 1 min left | 19077 | 19077 (100 in 100) | 18930/147 | 99.2 vs 99.2 | 99.2c | 0.77c | 127 | +$0.01 | -$0.11 to +$0.14 | +$0.02 / +$0.00 |
| taker, ask 95c+, 3 min left | 20325 | 20325 (100 in 100) | 20042/283 | 98.6 vs 98.6 | 98.7c | 1.33c | 73 | -$0.05 | -$0.19 to +$0.11 | -$0.05 / -$0.05 |
| taker, ask 95c+, 5 min left | 12386 | 12386 (100 in 100) | 12146/240 | 98.1 vs 98.1 | 97.9c | 2.04c | 48 | +$0.12 | -$0.25 to +$0.54 | -$0.12 / +$0.36 |
| taker, ask 97c+, 1 min left | 17688 | 17688 (100 in 100) | 17600/88 | 99.5 vs 99.5 | 99.4c | 0.55c | 180 | +$0.06 | -$0.05 to +$0.17 | +$0.04 / +$0.07 |
| taker, ask 97c+, 3 min left | 17254 | 17254 (100 in 100) | 17100/154 | 99.1 vs 99.1 | 99.1c | 0.92c | 107 | +$0.03 | -$0.13 to +$0.18 | +$0.01 / +$0.04 |
| taker, ask 97c+, 5 min left | 8992 | 8992 (100 in 100) | 8883/109 | 98.8 vs 98.8 | 98.6c | 1.42c | 69 | +$0.21 | -$0.20 to +$0.58 | -$0.05 / +$0.47 |

## 5. Spot safety filter (Binance): only when the coin is z typical moves past the strike

Typical move = last hour's 1-minute moves scaled to the minutes left. Binance is a stand-in for CF Benchmarks' index, which settles the market.

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| improve 95c, 3 min, z any | 19722 | 16053 (81 in 100) | 15809/244 | 98.8 vs 98.5 | 98.4c | 1.60c | 61 | +$0.10 | -$0.08 to +$0.29 | +$0.09 / +$0.12 |
| improve 95c, 3 min, z 1.5 | 13707 | 10962 (80 in 100) | 10852/110 | 99.2 vs 99.0 | 98.6c | 1.34c | 73 | +$0.36 | +$0.16 to +$0.53 | +$0.19 / +$0.52 |
| improve 95c, 3 min, z 2.0 | 11000 | 8663 (79 in 100) | 8608/55 | 99.5 vs 99.4 | 98.8c | 1.18c | 82 | +$0.56 | +$0.41 to +$0.73 | +$0.53 / +$0.60 |
| improve 95c, 3 min, z 3.0 | 6197 | 4670 (75 in 100) | 4653/17 | 99.7 vs 99.6 | 99.1c | 0.93c | 105 | +$0.57 | +$0.42 to +$0.71 | +$0.45 / +$0.70 |
| level 97c, 3 min, z any | 16766 | 4025 (24 in 100) | 3888/137 | 99.2 vs 96.6 | 97.0c | 3.00c | 32 | -$0.42 | -$1.03 to +$0.18 | -$0.70 / -$0.13 |
| level 97c, 3 min, z 1.5 | 12348 | 2369 (19 in 100) | 2301/68 | 99.4 vs 97.1 | 97.0c | 3.00c | 32 | +$0.13 | -$0.55 to +$0.77 | +$0.22 / +$0.05 |
| level 97c, 3 min, z 2.0 | 10194 | 1641 (16 in 100) | 1605/36 | 99.6 vs 97.8 | 97.0c | 3.00c | 32 | +$0.83 | +$0.14 to +$1.52 | +$0.83 / +$0.83 |
| level 97c, 3 min, z 3.0 | 5923 | 678 (11 in 100) | 664/14 | 99.8 vs 97.9 | 97.0c | 3.00c | 32 | +$0.96 | -$0.09 to +$1.94 | +$0.35 / +$1.58 |
| improve 90c, 5 min, z any | 17847 | 15924 (89 in 100) | 15270/654 | 96.3 vs 95.9 | 96.0c | 3.94c | 24 | -$0.07 | -$0.54 to +$0.46 | -$0.11 / -$0.04 |
| improve 90c, 5 min, z 1.5 | 10447 | 9301 (89 in 100) | 9039/262 | 97.5 vs 97.2 | 96.9c | 3.07c | 31 | +$0.33 | -$0.09 to +$0.73 | +$0.27 / +$0.39 |
| improve 90c, 5 min, z 2.0 | 7261 | 6434 (89 in 100) | 6307/127 | 98.3 vs 98.0 | 97.3c | 2.67c | 36 | +$0.76 | +$0.38 to +$1.15 | +$0.71 / +$0.81 |
| improve 90c, 5 min, z 3.0 | 2827 | 2453 (87 in 100) | 2424/29 | 99.0 vs 98.8 | 98.0c | 2.01c | 48 | +$0.87 | +$0.47 to +$1.31 | +$0.77 / +$0.97 |

## 6. By coin (improve, leader bid 95c+, 3 min left, fair)

| Variant | Signals | Fills | Won/lost | Won out of 100: all signals vs filled | Avg price | Avg win a contract | One loss eats N wins | P&L per $100 | 90% band | Older / newer half |
|---|---|---|---|---|---|---|---|---|---|---|
| KXBNB15M | 2802 | 2034 (73 in 100) | 1998/36 | 98.7 vs 98.2 | 98.5c | 1.47c | 66 | -$0.28 | -$0.75 to +$0.10 | -$0.03 / -$0.54 |
| KXBTC15M | 2566 | 2045 (80 in 100) | 2004/41 | 98.4 vs 98.0 | 98.2c | 1.79c | 54 | -$0.20 | -$0.66 to +$0.30 | -$0.24 / -$0.16 |
| KXDOGE15M | 2837 | 2398 (85 in 100) | 2370/28 | 99.0 vs 98.8 | 98.4c | 1.58c | 61 | +$0.44 | +$0.07 to +$0.80 | +$0.66 / +$0.22 |
| KXETH15M | 2855 | 2445 (86 in 100) | 2408/37 | 98.7 vs 98.5 | 98.4c | 1.58c | 62 | +$0.08 | -$0.41 to +$0.49 | -$0.08 / +$0.25 |
| KXHYPE15M | 2945 | 2260 (77 in 100) | 2218/42 | 98.6 vs 98.1 | 98.4c | 1.56c | 62 | -$0.28 | -$0.67 to +$0.16 | -$0.61 / +$0.05 |
| KXSOL15M | 2865 | 2436 (85 in 100) | 2404/32 | 98.9 vs 98.7 | 98.4c | 1.56c | 62 | +$0.27 | -$0.10 to +$0.59 | +$0.04 / +$0.50 |
| KXXRP15M | 2852 | 2435 (85 in 100) | 2407/28 | 99.0 vs 98.9 | 98.3c | 1.68c | 58 | +$0.56 | +$0.20 to +$0.88 | +$0.77 / +$0.34 |

## 7. Worst stretch

Best maker variant with 200+ fills: `level_0.93_m10`: +$2.34 per $100 over 1140 fills, band +$0.80 to +$3.83. Staking $10 on every fill it would have made +$266.67 over 60 days; the deepest fall from a high on the way was -$73.33. With ~105 variants tried, the best one is flattered by luck: judge it by its band and halves, not its headline.
