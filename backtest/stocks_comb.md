# Stock price markets, second pass: patterns in the prices alone (stocks.py comb)

Generated 2026-11-13T16:10:12Z. Paper only. The holdout from 2026-11-10 is not in here. Jan's ask (13 Nov): "we have so much data downloaded, it's worth combing through it". The first pass (`stocks.md`) only compared the price with a swing model.

34,341 looks at 11,575 markets, at six moments of each market's life, only where it had traded in the 3 hours before. Every buy is $10 at the worst price anyone paid in the next 15 minutes + 2c + the fee. About 150 cuts were looked at, so the exam's luck bar is set for that.

## 1. Every price band, every moment, both sides

Per $100 (number of bets).

| moment | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| the afternoon before | buy Yes | -$33.66 (45) | -$22.81 (53) | -$0.83 (88) | -$8.27 (58) | -$16.37 (51) | -$0.38 (24) |
| the afternoon before | buy No | -$1.77 (40) | -$2.15 (53) | -$5.29 (88) | -$11.29 (58) | +$11.48 (52) | -$27.02 (26) |
| a day before the close | buy Yes | -$91.90 (26) | +$10.33 (30) | -$26.84 (35) | - (16) | -$3.82 (22) | - (18) |
| a day before the close | buy No | +$2.32 (22) | +$1.07 (29) | +$7.49 (35) | - (16) | -$12.73 (22) | - (18) |
| just after the open | buy Yes | -$43.08 (112) | -$40.22 (211) | -$12.74 (228) | -$12.23 (271) | -$5.50 (206) | -$3.69 (116) |
| just after the open | buy No | -$5.62 (95) | -$5.15 (207) | -$15.23 (227) | -$23.75 (273) | -$28.74 (209) | -$40.71 (131) |
| 4 hours before the close | buy Yes | -$75.73 (82) | -$71.73 (118) | -$27.02 (173) | -$10.51 (156) | +$0.66 (117) | +$2.18 (92) |
| 4 hours before the close | buy No | -$4.04 (73) | +$8.25 (115) | +$9.14 (172) | -$10.10 (156) | -$50.34 (120) | -$62.15 (104) |
| 2 hours before the close | buy Yes | -$54.34 (79) | -$57.33 (128) | -$28.57 (132) | -$10.14 (130) | -$6.61 (99) | +$2.18 (75) |
| 2 hours before the close | buy No | -$1.63 (66) | +$10.29 (122) | -$3.74 (131) | -$4.42 (129) | -$26.49 (99) | -$79.06 (87) |
| 1 hour before the close | buy Yes | -$25.37 (84) | -$39.14 (119) | -$8.58 (131) | -$5.61 (138) | -$9.72 (115) | +$0.74 (66) |
| 1 hour before the close | buy No | -$2.60 (68) | -$6.41 (114) | -$2.82 (130) | -$16.80 (142) | -$16.24 (120) | -$66.89 (76) |

Buying Yes loses almost everywhere, and long shots (Yes under 25c) lose most: $25 to $90 per $100. People overpay for the small chance. The other side of that, No on long shots, is the only corner that is ahead.

## 2. The one lean: No on long shots in the afternoon

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| No where Yes is 5-25c, 4 and 2 hours before the close | 339 | 308 | +$5.33 | +$4.62 | +$6.04 |
| the same, one-day markets only | 258 | 238 | +$5.93 | +$6.24 | +$5.63 |
| the same, end-of-week line markets | 44 | 41 | +$12.47 | +$17.25 | +$7.66 |
| the same, end-of-week bracket markets | 37 | 29 | -$7.32 | -$8.37 | -$6.32 |
| all kinds, at the worst price of the next 2 hours + 1c | 589 | 495 | -$5.58 | -$4.24 | -$6.91 |
| all kinds, at the worst price of the next 15 minutes + 4c | 339 | 308 | +$3.03 | +$2.38 | +$3.67 |
| just after the open instead | 276 | 228 | -$5.87 | -$8.70 | -$3.04 |
| 1 hour before the close instead | 164 | 140 | -$5.24 | -$8.79 | -$1.69 |
| a day before instead | 130 | 115 | -$0.02 | +$2.71 | -$2.76 |

Ahead with 4 and 2 hours left, behind at the open and in the last hour, and behind if the buy costs what the worst buyer of the next 2 hours paid. A thin lean that lives or dies on the price you really get.

## 3. Other cuts

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| Yes on favorites (Yes at 75-97c), last 4 hours | 564 | 489 | -$2.28 | +$0.50 | -$5.06 |
| price moved 8c+ in 3 hours, follow it, just after the open | 410 | 197 | -$24.61 | -$29.89 | -$19.34 |
| price moved 8c+ in 3 hours, bet against it, just after the open | 431 | 213 | -$7.68 | -$12.72 | -$2.66 |
| price moved 8c+ in 3 hours, follow it, 4 hours before the close | 345 | 194 | -$17.99 | -$15.82 | -$20.15 |
| price moved 8c+ in 3 hours, bet against it, 4 hours before the close | 360 | 152 | -$12.69 | -$19.13 | -$6.26 |
| price moved 8c+ in 3 hours, follow it, 2 hours before the close | 310 | 196 | -$3.57 | +$9.44 | -$16.58 |
| price moved 8c+ in 3 hours, bet against it, 2 hours before the close | 332 | 117 | -$24.04 | -$35.35 | -$12.72 |
| price moved 8c+ in 3 hours, follow it, 1 hour before the close | 310 | 194 | -$8.27 | -$7.89 | -$8.66 |
| price moved 8c+ in 3 hours, bet against it, 1 hour before the close | 353 | 110 | -$37.14 | -$40.84 | -$33.47 |

By stock, all moments, buys at 10-90c (Yes side / No side per $100):

| stock | buy Yes | buy No |
|---|---|---|
| AAPL | -$12.03 (255) | -$20.35 (251) |
| AMZN | -$10.83 (230) | -$3.03 (231) |
| GOOGL | -$28.17 (306) | -$4.10 (302) |
| META | -$17.95 (225) | -$3.76 (220) |
| MSFT | -$19.16 (172) | -$13.93 (169) |
| NVDA | -$22.08 (341) | -$0.07 (331) |
| OPEN | -$39.08 (40) | -$1.45 (40) |
| PLTR | -$33.13 (57) | +$10.35 (57) |
| SPY | -$21.45 (493) | -$6.67 (482) |
| TSLA | -$2.03 (295) | -$31.78 (283) |

No stock stands out: No beats Yes on most of them, and both lose. Following or betting against a move loses at every moment. Brackets that don't add up to $1 and lines priced out of order are too rare to bet on (under 25 cases at any moment).

## The exam

- **Stock price markets: No on long shots (Yes 5-25c), 4 and 2 hours before the close**: 339 bets in 298 separate groups, +$5.33 per $100, luck range +$1.34 to +$9.32, worst case -$3.68 per $100, verdict **Promising, needs more bets**.
- **Stock price markets: same, one-day markets only**: 258 bets in 224 separate groups, +$5.93 per $100, luck range +$2.03 to +$9.84, worst case -$2.58 per $100, verdict **Promising, needs more bets**.
- **Stock price markets: same, at the worst price of the next 2 hours**: 589 bets in 483 separate groups, -$5.58 per $100, luck range -$8.90 to -$2.26, worst case -$12.76 per $100, verdict **Losing**.
