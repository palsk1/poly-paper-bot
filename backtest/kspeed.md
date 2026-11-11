# Kalshi 15-minute crypto: what speed buys, and the whole 15 minutes

Generated 2026-11-11T06:24:10Z. Paper only. Code: `kspeed.py`. Windows closing 2026-09-12 to 2026-11-09 (39006 windows of 7 coins, 529995 window-minutes with a real two-sided quote). Nothing from 10 Nov on (holdout).

Every number is profit per $100 put in, after Kalshi's fee, bought at the real asking price. In brackets: the luck range (9 times in 10 the true number sits inside) and the number of bets. Bets in the same 15 minutes count as one for the luck range, since the coins move together.

## 1. The whole 15 minutes

### a) Is the price right, minute by minute?

Buy a side at its asking price, by how far into the 15 minutes we are (rows) and what the side costs (columns). If some stretch of the timeline were mispriced, a cell here would be clearly above $0.

| Stretch | 5-20c | 20-40c | 40-60c | 60-80c | 80-95c | 95-99.5c | all |
|---|---|---|---|---|---|---|---|
| minutes 1-4 | -$17.46 (-$23.62 to -$11.64, 18574) | -$6.00 (-$8.65 to -$3.98, 73655) | -$4.56 (-$4.85 to -$4.25, 114674) | -$3.80 (-$4.76 to -$2.84, 81436) | -$0.76 (-$1.78 to +$0.36, 22683) | +$1.58 (+$0.37 to +$2.65, 590) | -$5.18 (-$5.74 to -$4.64, 311612) |
| minutes 5-7 | -$17.38 (-$22.78 to -$12.11, 36967) | -$6.77 (-$9.02 to -$4.38, 47620) | -$4.98 (-$5.35 to -$4.59, 46908) | -$3.25 (-$4.20 to -$2.42, 48596) | -$0.78 (-$1.56 to -$0.05, 40610) | +$0.74 (+$0.20 to +$1.19, 7116) | -$6.07 (-$6.92 to -$5.19, 227817) |
| minutes 8-10 | -$16.15 (-$20.31 to -$11.72, 40771) | -$7.66 (-$9.76 to -$5.51, 34012) | -$5.06 (-$5.45 to -$4.57, 30401) | -$3.01 (-$3.93 to -$2.00, 34100) | -$0.68 (-$1.27 to -$0.14, 42515) | +$0.17 (-$0.13 to +$0.45, 25769) | -$5.78 (-$6.62 to -$4.93, 207568) |
| minutes 11-12 | -$10.96 (-$15.71 to -$5.83, 21576) | -$7.20 (-$9.69 to -$4.42, 14925) | -$5.54 (-$6.30 to -$4.93, 12595) | -$3.69 (-$4.75 to -$2.55, 14764) | -$1.49 (-$2.15 to -$0.83, 22031) | +$0.03 (-$0.21 to +$0.26, 25154) | -$4.51 (-$5.40 to -$3.58, 111045) |
| minutes 13-14 | -$9.97 (-$15.57 to -$3.63, 11592) | -$8.51 (-$11.49 to -$5.45, 7008) | -$4.85 (-$5.91 to -$3.77, 5843) | -$4.25 (-$5.54 to -$2.77, 6734) | -$2.00 (-$2.71 to -$1.36, 11423) | -$0.04 (-$0.23 to +$0.18, 17950) | -$4.22 (-$5.29 to -$3.25, 60550) |

The same at the middle price with no fee (what a perfect waiting order would get; you can't just buy this, it shows if the price itself leans):

| Stretch | 5-20c | 20-40c | 40-60c | 60-80c | 80-95c | 95-99.5c | all |
|---|---|---|---|---|---|---|---|
| minutes 1-4 | -$8.20 (-$14.41 to -$0.58, 19886) | +$0.85 (-$1.54 to +$3.22, 77707) | +$0.14 (+$0.01 to +$0.29, 114890) | -$0.57 (-$1.56 to +$0.46, 78529) | +$0.96 (-$0.04 to +$1.97, 20050) | +$2.54 (+$1.52 to +$3.60, 496) | -$0.34 (-$0.89 to +$0.29, 311558) |
| minutes 5-7 | -$8.50 (-$14.06 to -$3.18, 38110) | +$0.36 (-$1.99 to +$2.99, 48448) | -$0.11 (-$0.30 to +$0.06, 47088) | -$0.22 (-$1.24 to +$0.75, 48775) | +$0.83 (+$0.03 to +$1.60, 38285) | +$1.03 (+$0.45 to +$1.59, 6674) | -$1.25 (-$2.26 to -$0.29, 227380) |
| minutes 8-10 | -$6.92 (-$11.89 to -$1.62, 41157) | -$0.78 (-$3.26 to +$1.53, 34324) | +$0.09 (-$0.11 to +$0.33, 30487) | +$0.20 (-$0.80 to +$1.09, 34487) | +$0.73 (+$0.05 to +$1.31, 41260) | +$0.52 (+$0.21 to +$0.82, 25560) | -$1.24 (-$2.29 to -$0.21, 207275) |
| minutes 11-12 | -$0.74 (-$6.17 to +$4.58, 21598) | +$0.65 (-$2.41 to +$3.02, 14995) | -$0.17 (-$0.45 to +$0.16, 12561) | -$0.17 (-$1.32 to +$0.92, 15034) | -$0.06 (-$0.75 to +$0.57, 21656) | +$0.41 (+$0.19 to +$0.62, 27499) | -$0.01 (-$1.05 to +$0.95, 113343) |
| minutes 13-14 | +$2.87 (-$3.42 to +$8.72, 11455) | +$0.71 (-$3.32 to +$4.36, 6960) | +$0.39 (-$0.16 to +$0.85, 5814) | -$0.28 (-$1.61 to +$1.09, 6989) | -$0.25 (-$0.84 to +$0.46, 11469) | +$0.38 (+$0.22 to +$0.57, 20545) | +$0.68 (-$0.26 to +$1.75, 63232) |

### b) Does Binance know more than Kalshi's price?

Learned on one half of the days: how often YES wins for each stretch and each distance of the Binance price from the line. On the other half: buy when that chance beats the asking price by the gap, at most one bet a window. 'Same minute' pretends we buy at the quote of the very minute we looked. 'One minute late' buys at the next minute's quote.

| Learned on | Gap | Stretch | Same minute | One minute late |
|---|---|---|---|---|
| older half | 3c | whole window | -$5.05 (-$7.14 to -$2.51, 19243) | -$6.42 (-$8.73 to -$3.79, 19238) |
| older half | 3c | minutes 1-7 | -$5.33 (-$7.47 to -$2.86, 18990) | -$6.58 (-$8.96 to -$3.97, 18990) |
| older half | 3c | minutes 8-14 | -$3.44 (-$7.82 to +$0.69, 15588) | -$6.90 (-$11.27 to -$2.84, 15516) |
| older half | 6c | whole window | -$4.99 (-$7.49 to -$2.39, 17577) | -$6.18 (-$8.79 to -$3.54, 17518) |
| older half | 6c | minutes 1-7 | -$5.69 (-$8.24 to -$2.96, 15957) | -$6.39 (-$9.12 to -$3.50, 15957) |
| older half | 6c | minutes 8-14 | -$2.62 (-$6.50 to +$1.86, 12659) | -$3.85 (-$8.71 to +$1.85, 12424) |
| older half | 10c | whole window | -$4.70 (-$8.09 to -$1.86, 13149) | -$4.28 (-$8.33 to -$0.24, 12881) |
| older half | 10c | minutes 1-7 | -$4.87 (-$8.66 to -$1.30, 9670) | -$4.93 (-$8.66 to -$1.37, 9670) |
| older half | 10c | minutes 8-14 | -$1.00 (-$5.87 to +$3.98, 9232) | -$0.16 (-$6.84 to +$7.19, 8797) |
| newer half | 3c | whole window | -$4.36 (-$6.49 to -$2.30, 18156) | -$5.62 (-$7.83 to -$3.46, 18155) |
| newer half | 3c | minutes 1-7 | -$4.63 (-$6.75 to -$2.59, 17991) | -$6.11 (-$8.26 to -$3.73, 17991) |
| newer half | 3c | minutes 8-14 | -$4.32 (-$7.40 to -$0.68, 14664) | -$3.13 (-$7.64 to +$1.85, 14614) |
| newer half | 6c | whole window | -$3.53 (-$6.04 to -$1.07, 16638) | -$4.74 (-$7.43 to -$1.73, 16592) |
| newer half | 6c | minutes 1-7 | -$4.32 (-$6.76 to -$1.63, 15341) | -$5.96 (-$8.46 to -$3.08, 15341) |
| newer half | 6c | minutes 8-14 | -$4.43 (-$7.95 to -$0.65, 11463) | -$5.29 (-$10.74 to +$0.04, 11269) |
| newer half | 10c | whole window | -$4.00 (-$6.80 to -$1.14, 11925) | -$4.77 (-$9.17 to -$1.09, 11654) |
| newer half | 10c | minutes 1-7 | -$4.87 (-$8.06 to -$1.57, 8812) | -$6.14 (-$9.81 to -$2.75, 8812) |
| newer half | 10c | minutes 8-14 | -$6.16 (-$10.24 to -$1.90, 8279) | -$8.84 (-$14.50 to -$3.06, 7853) |

### c) After a big Binance minute, does Kalshi keep drifting?

Minutes where Binance moved a lot, while Kalshi was at 10-90c. 'Same minute' = how far Kalshi's price had already moved by the end of that minute. 'Minute after' = what was left to move. A slow market would leave cents in the last column.

| Binance move in one minute | Cases | Kalshi, same minute | Kalshi, minute after |
|---|---|---|---|
| 1 typical move or more | 95971 | +18.3c | -0.03c |
| 2 or more | 18772 | +25.2c | -0.50c |
| 3 or more | 3691 | +28.9c | -0.87c |

### d) The one cell that is ahead: a side already at 95c+ early in the window

In table a) the only cells above $0 are sides that cost 95c or more while 8+ minutes are still left. As one rule: the first time that happens in a window, buy that side at the asking price.

| Version | Result | Lost bets | By coin |
|---|---|---|---|
| Buy the same minute | +$0.62 (+$0.06 to +$1.23, 4407) | 126 | BTC +$1.77, ETH +$1.19, SOL +$0.78, XRP +$0.62, DOGE +$0.87, HYPE -$0.21, BNB +$0.04 |
| Buy one minute late | +$0.69 (+$0.09 to +$1.28, 4406) | 126 | BTC +$1.71, ETH +$1.54, SOL +$0.71, XRP +$0.94, DOGE +$0.85, HYPE -$0.16, BNB -$0.00 |

## 2. The delay curve, second by second

2805 windows with every trade of their last 5 minutes (2026-10-28 to 2026-11-09) and Binance prices every second.

### a) When Binance jumps, how fast does Kalshi follow?

A jump = Binance moved the odds a lot within 3 seconds while Kalshi was still at 15-85c (293 jumps). The line shows how many cents Kalshi's last traded price had moved our way, counted from 6 seconds before it. The jump itself runs from -3 to 0, so a number that is already big at -2 or -1 means Kalshi moved while Binance was still moving.

| Seconds after the jump | -3 | -2 | -1 | 0 | 1 | 2 | 3 | 5 | 10 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kalshi has moved | +5.2c | +11.0c | +22.6c | +24.1c | +24.4c | +24.5c | +24.7c | +25.1c | +25.0c | +25.0c | +24.9c |

Buying the jump's side at the next real trade (the dearest one in that second), held to the result:

| We are this late | Bets | Avg price paid | P&L per $100 (luck range) |
|---|---|---|---|
| under 1 s | 281 | 76.7c | -$5.93 (-$13.04 to +$0.06) |
| 1 s | 275 | 75.8c | -$4.79 (-$11.26 to +$2.81) |
| 2 s | 272 | 75.9c | -$5.81 (-$12.77 to +$2.24) |
| 3 s | 263 | 75.4c | -$5.89 (-$13.40 to +$1.77) |
| 5 s | 253 | 75.0c | -$5.76 (-$14.39 to +$3.55) |
| 10 s | 239 | 72.8c | -$6.70 (-$17.34 to +$4.72) |
| 30 s | 172 | 63.9c | -$3.84 (-$24.80 to +$20.40) |

### b) The 45-seconds-left buy (the live paper bot's main test), by delay

Binance very sure (z 4+) with 45 s left; buy that side at the next real trade.

| We are this late | Bets | Avg price paid | Lost | P&L per $100 (luck range) |
|---|---|---|---|---|
| under 1 s | 317 | 98.71c | 2 | +$0.88 (-$0.43 to +$2.88) |
| 1 s | 284 | 98.62c | 2 | +$0.70 (-$0.61 to +$2.39) |
| 2 s | 264 | 98.64c | 2 | +$0.64 (-$0.93 to +$2.19) |
| 3 s | 242 | 98.54c | 2 | +$0.66 (-$0.80 to +$2.67) |
| 5 s | 206 | 98.30c | 2 | +$0.79 (-$1.14 to +$3.30) |
| 10 s | 162 | 98.14c | 2 | +$0.08 (-$1.94 to +$1.73) |

## 3. How fast are we really?

Measured 2026-11-11T04:51:38Z from a GitHub machine (a rented data-centre computer in the US, much like a cheap server), on a connection kept open:

| What | Network round trip | Typical answer | Slow answer (1 in 10) |
|---|---|---|---|
| Kalshi order book | 75 ms | 70 ms | 72 ms |
| Kalshi trades | 68 ms | 69 ms | 71 ms |
| Binance price (1-second bars) | 137 ms | 101 ms | 101 ms |

The live paper bot's own log (294 coin-windows): reading the Kalshi order book takes 198 ms (slow: 251 ms); getting fresh Binance seconds takes 824 ms (slow: 1011 ms).

## The exam

- **Binance vs Kalshi price, whole window, 6c gap, one minute late**: 17518 bets, -$4.75 per $100, luck range -$7.37 to -$2.13, halves -$5.47 / -$4.09. Verdict: **Losing**.
- **Side at 95c+ with 8+ minutes left, bought one minute late**: 4406 bets, +$0.72 per $100, luck range +$0.14 to +$1.31, halves +$0.63 / +$0.80. Verdict: **Ahead, but could be luck**.
- **Buy the Binance jump, 1 s late**: 275 bets, -$4.58 per $100, luck range -$9.82 to +$0.66, halves -$9.50 / -$0.88. Verdict: **Losing**.
- **45 s left, Binance very sure, 1 s late**: 284 bets, +$0.69 per $100, luck range +$0.18 to +$1.20, halves +$0.96 / +$0.44. Verdict: **Ahead, but could be luck**.

Versions looked at in this dig: 84.
