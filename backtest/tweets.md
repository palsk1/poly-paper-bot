# A counting model vs Polymarket's post-count markets (tweets.py)

Generated 2026-11-12T22:13:26Z. Markets like "Will Elon Musk post 90-114 tweets from 5 to 7 November?". 216 finished count windows (ended before 2026-11-10) with 3267 markets: elonmusk 152, realDonaldTrump 36, WhiteHouse 23, cz_binance 3, tedcruz 1, ZelenskyyUa 1. Post times come from Polymarket's own counter (xtracker), the site the markets are settled on: when each post was made and when the counter first showed it.

**The model.** Count so far (only posts the counter was already showing) + what the same stretch of the week brought in the last 8 weeks, with a wide spread. Version 2 uses 4 weeks, leans half-way toward the pace of the last 3 days and spreads 1.5x wider.

**The test.** Every 30 minutes: the model's chance for each count range vs the last real trade of the past 30 minutes. If they are far enough apart, buy the cheap side at the first real trade of the next 30 minutes, + 1c + the fee. One bet per market, $10 each. The first 86 windows (fixed shuffled order) were used to look around, the other 130 were opened later.

## 1. Who is closer?

| looks | model miss | model v2 miss | Polymarket miss |
|---|---|---|---|
| one random look per market, any time (1798) | 0.0867 | 0.0905 | 0.0800 |
| last 3 days only (1194) | 0.1267 | 0.1277 | 0.1057 |
| last day only (740) | 0.1599 | 0.1656 | 0.1242 |

("Miss" = average squared distance between the forecast and what happened; smaller is better. Polymarket is the better forecaster, most of all near the end, when people watch the account live.)

## 2. Buying where the model disagrees

### Windows used to look around (86)

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| model, both sides, 5c+ apart | 572 | 86 | 334 | -$8.27 | -$23.93 | +$7.47 |
| model, both sides, 10c+ apart | 425 | 86 | 254 | +$5.69 | -$4.08 | +$15.46 |
| model v2, both sides, 5c+ apart | 581 | 86 | 335 | +$2.43 | +$2.43 | +$2.42 |
| model says Yes is too cheap, 10c+ (buy Yes) | 272 | 85 | 61 | -$9.98 | -$5.14 | -$14.85 |
| **model says Yes is too dear, 10c+ (buy No)** | 329 | 86 | 249 | +$7.80 | +$9.05 | +$6.56 |
| same, 5c+ | 469 | 86 | 383 | +$5.10 | +$8.41 | +$1.80 |
| same, model v2, 10c+ | 365 | 86 | 281 | +$5.85 | +$8.86 | +$2.84 |
| same, before the window starts | 109 | 59 | 79 | -$0.44 | -$3.62 | +$2.68 |
| same, inside the window | 296 | 86 | 216 | +$7.63 | +$12.07 | +$3.18 |
| yardstick: always buy No | 698 | 86 | 612 | +$0.03 | +$0.00 | +$0.06 |
| yardstick: always buy Yes | 698 | 86 | 86 | -$4.89 | -$2.39 | -$7.39 |

### Windows opened later (130)

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| model, both sides, 5c+ apart | 885 | 128 | 537 | +$3.88 | -$1.98 | +$9.72 |
| model, both sides, 10c+ apart | 647 | 128 | 380 | +$5.35 | +$0.09 | +$10.59 |
| model v2, both sides, 5c+ apart | 883 | 128 | 545 | +$7.86 | +$15.73 | +$0.03 |
| model says Yes is too cheap, 10c+ (buy Yes) | 393 | 127 | 88 | +$0.00 | -$21.56 | +$21.48 |
| **model says Yes is too dear, 10c+ (buy No)** | 499 | 128 | 379 | +$6.79 | +$1.86 | +$11.68 |
| same, 5c+ | 708 | 128 | 585 | +$1.67 | +$0.67 | +$2.68 |
| same, model v2, 10c+ | 528 | 128 | 408 | +$4.11 | +$2.87 | +$5.35 |
| same, before the window starts | 193 | 95 | 155 | +$6.51 | +$7.46 | +$5.58 |
| same, inside the window | 441 | 128 | 323 | +$7.03 | +$3.26 | +$10.77 |
| yardstick: always buy No | 1100 | 128 | 973 | -$0.42 | -$0.21 | -$0.64 |
| yardstick: always buy Yes | 1100 | 128 | 127 | -$16.72 | -$14.76 | -$18.67 |

### All (216)

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| model, both sides, 5c+ apart | 1457 | 214 | 871 | -$0.89 | -$11.12 | +$9.34 |
| model, both sides, 10c+ apart | 1072 | 214 | 634 | +$5.49 | -$2.67 | +$13.65 |
| model v2, both sides, 5c+ apart | 1464 | 214 | 880 | +$5.70 | +$10.07 | +$1.33 |
| model says Yes is too cheap, 10c+ (buy Yes) | 665 | 212 | 149 | -$4.08 | -$17.12 | +$8.96 |
| **model says Yes is too dear, 10c+ (buy No)** | 828 | 214 | 628 | +$7.19 | +$5.26 | +$9.12 |
| same, 5c+ | 1177 | 214 | 968 | +$3.04 | +$3.40 | +$2.68 |
| same, model v2, 10c+ | 893 | 214 | 689 | +$4.82 | +$5.95 | +$3.70 |
| same, before the window starts | 302 | 154 | 234 | +$4.00 | +$4.92 | +$3.09 |
| same, inside the window | 737 | 214 | 539 | +$7.27 | +$6.45 | +$8.08 |
| yardstick: always buy No | 1798 | 214 | 1585 | -$0.25 | -$0.20 | -$0.30 |
| yardstick: always buy Yes | 1798 | 214 | 213 | -$12.13 | -$9.12 | -$15.14 |

### The "buy No" rule, cut up (all windows)

Careful: of the $603 the plain rule made, $293 came from ONE bet (No at 2c in "Will Elon Musk post 65-89 tweets from August 17 to August 19, 2026?", a lottery ticket). So the rule we keep only buys No at 10c or more (Yes at 90c or less). Everything below is that rule.

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| **the rule: buy No, model 10c+ under the price, No costs 10c+** | 825 | 213 | 627 | +$4.16 | +$5.79 | +$2.54 |
| &nbsp;&nbsp;windows used to look around | 328 | 86 | 249 | +$8.14 | +$9.05 | +$7.23 |
| &nbsp;&nbsp;windows opened later | 497 | 127 | 378 | +$1.53 | +$2.28 | +$0.78 |
| elonmusk | 577 | 152 | 436 | +$1.57 | +$1.53 | +$1.62 |
| realDonaldTrump | 161 | 36 | 126 | +$7.86 | +$6.69 | +$9.02 |
| WhiteHouse | 78 | 22 | 56 | +$2.00 | +$7.99 | -$3.93 |
| paid under 50c | 83 | 70 | 39 | +$21.32 | +$39.43 | +$3.61 |
| paid 50-85c | 549 | 204 | 417 | +$3.91 | +$3.00 | +$4.81 |
| paid 85c+ | 193 | 97 | 171 | -$2.69 | -$5.03 | -$0.37 |
| 3+ days left | 527 | 194 | 424 | +$6.10 | +$6.43 | +$5.77 |
| under 3 days left | 298 | 159 | 203 | +$0.74 | +$2.92 | -$1.44 |
| 2026-03 | 53 | 18 | 40 | -$2.19 | -$8.10 | +$3.48 |
| 2026-04 | 173 | 45 | 134 | +$8.97 | +$9.63 | +$8.32 |
| 2026-05 | 117 | 29 | 93 | +$1.93 | +$0.87 | +$2.97 |
| 2026-06 | 79 | 27 | 55 | +$4.63 | +$14.41 | -$4.90 |
| 2026-07 | 94 | 27 | 72 | +$5.05 | -$0.27 | +$10.38 |
| 2026-08 | 90 | 30 | 68 | +$6.84 | +$9.99 | +$3.68 |
| 2026-09 | 74 | 27 | 50 | -$5.74 | -$6.39 | -$5.08 |
| 2026-10 | 136 | 31 | 108 | +$5.28 | +$12.36 | -$1.86 |
| 2026-11 | 9 | - | - | - | - | - |
| if buying costs 2c more than the trade price (not 1c) | 825 | 213 | 627 | +$2.67 | +$4.25 | +$1.09 |
| if buying costs 3c more than the trade price (not 1c) | 825 | 213 | 627 | +$1.23 | +$2.78 | -$0.31 |
| if buying costs 5c more than the trade price (not 1c) | 825 | 213 | 627 | -$1.49 | +$0.00 | -$2.97 |

## 3. The exam

- **Post-count markets: buy No (10c+) where the counting model says Yes is 10c+ too dear**: 825 bets in 213 separate groups, +$4.16 per $100, worst case -$2.07 per $100, verdict **Promising, needs more bets**.
- **Post-count markets: counting model, both sides, 5c+ apart**: 1457 bets in 214 separate groups, -$0.89 per $100, worst case -$17.89 per $100, verdict **Behind, but could be bad luck**.
- **Post-count markets: counting model says Yes is 10c+ too cheap (buy Yes)**: 665 bets in 212 separate groups, -$4.08 per $100, worst case -$30.23 per $100, verdict **Behind, but could be bad luck**.
- **Post-count markets: always buy No (yardstick)**: 1798 bets in 207 separate groups, -$0.25 per $100, worst case -$2.81 per $100, verdict **Behind, but could be bad luck**.

