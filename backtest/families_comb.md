# Three more families, prices alone: YouTube views, Rotten Tomatoes scores, flu numbers (families.py)

Generated 2026-11-13T17:13:21Z. Paper only. The holdout from 2026-11-10 is not in here.

The families left over from the sweep in `boxoffice.md`. No model here, only the comb Jan asked for: every price band, at four moments of a market's life, both sides. One $10 bet per market the first time it fits, at the worst price anyone paid in the next hour + 2c + the fee. Small trades at the mirror of the last price are dropped and a buy more than 15c from the last price is thrown out (the wrong-side trades found in `quakes.md`). About 200 cuts looked at. Per $100 (bets).

### YouTube (video views, subscriber counts; the "will he say X" markets are left to `mentions.md`): 2231 finished markets, 1814 with real trades, 327 events

| when | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| first third of its life | Yes | -$36.81 (334) | -$15.66 (387) | -$24.67 (266) | -$16.62 (160) | -$10.08 (97) | -$8.88 (46) |
| first third of its life | No | -$4.27 (288) | -$3.37 (381) | -$1.24 (267) | +$0.18 (152) | +$4.96 (93) | -$8.81 (58) |
| middle third | Yes | -$61.34 (86) | +$9.22 (110) | +$7.12 (82) | -$8.47 (61) | -$10.20 (46) | -$6.13 (27) |
| middle third | No | -$1.69 (75) | -$10.94 (111) | -$14.14 (80) | -$13.98 (58) | +$18.76 (46) | +$0.56 (27) |
| last third | Yes | -$17.11 (43) | +$8.81 (42) | -$7.03 (35) | +$1.55 (30) | +$9.54 (28) | +$5.06 (19) |
| last third | No | -$3.51 (42) | -$10.77 (45) | -$21.54 (37) | -$26.04 (28) | -$63.29 (28) | -$100.00 (20) |
| last day | Yes | -$56.72 (151) | -$46.23 (157) | -$22.07 (113) | -$18.32 (80) | -$9.49 (72) | -$3.20 (42) |
| last day | No | -$2.13 (101) | -$6.78 (162) | -$13.45 (110) | -$12.09 (76) | -$28.64 (61) | -$77.46 (52) |

Yes buyers lose in almost every box and No buyers don't win it back: the gap between buyers and sellers eats both. "Will the channel hit N billion views by a date" looks good for Yes at 25-75c (+$53.62 per $100) on 13 bets, which is nothing.

### Rotten Tomatoes ("will the film score at least N"): 576 finished markets, 532 with real trades, 87 events

| when | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| first third of its life | Yes | - (10) | -$49.73 (30) | -$26.04 (47) | -$25.33 (61) | -$6.89 (37) | +$0.52 (20) |
| first third of its life | No | - (10) | +$4.65 (31) | +$0.25 (53) | +$23.08 (63) | +$11.13 (34) | -$62.87 (20) |
| middle third | Yes | -$58.21 (21) | -$4.26 (27) | -$6.87 (24) | -$0.85 (21) | +$9.08 (17) | -$2.76 (15) |
| middle third | No | +$0.26 (17) | -$8.15 (28) | -$6.83 (25) | -$26.87 (20) | -$74.09 (17) | -$70.89 (15) |
| last third | Yes | - (10) | - (14) | - (13) | - (9) | +$9.06 (15) | - (14) |
| last third | No | - (9) | - (14) | - (14) | - (9) | - (14) | - (14) |
| last day | Yes | - (3) | - (2) | - (1) | - (2) | - (4) | - (3) |
| last day | No | - (3) | - (2) | - (1) | - (2) | - (4) | - (4) |

One lean: early in a market's life, lines priced as "probably yes" (Yes at 50-75c) are too dear. A film's score tends to slide as more critics post, and early buyers don't price that in.

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| No where Yes is 50-75c, first third of the market's life | 63 | 33 | +$23.08 | +$12.54 | +$33.29 |
| the same, buying Yes instead | 61 | 30 | -$25.33 | -$19.43 | -$31.03 |
| No, at the worst price of the next 2 hours + 1c | 80 | 39 | +$17.28 | +$29.05 | +$5.51 |
| No, 4c extra instead of 2c | 63 | 33 | +$17.27 | +$6.91 | +$27.31 |
| No where Yes is 40-80c, first third | 86 | 44 | +$16.97 | +$20.44 | +$13.50 |
| No where Yes is 50-75c, middle third | 20 | 6 | -$26.87 | -$58.77 | +$4.94 |
| No where Yes is 50-75c, 24-72 hours before the end | 14 | 5 | -$20.34 | -$0.28 | -$40.42 |
| No where Yes is 50-75c, 72-120 hours before the end | 33 | 18 | +$28.18 | +$16.60 | +$39.07 |
| No where Yes is 50-75c, 120-240 hours before the end | 26 | 9 | -$16.03 | -$33.50 | +$1.47 |
| No where Yes is 50-75c, 240-more hours before the end | 22 | 12 | +$33.69 | +$22.59 | +$44.81 |

Ahead in both halves and at harsher prices, but it is 63 bets on 45 films, it flips sign in the middle third, and cut by hours left instead it jumps between +$30 and -$20. A lean, not a find.

### Flu hospital numbers: 171 finished markets, 149 with real trades, 30 events

| when | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| first third of its life | Yes | - (11) | - (2) | - (2) | - (1) | - (6) | - (5) |
| first third of its life | No | - (6) | - (2) | - (2) | - (1) | - (6) | - (5) |
| middle third | Yes | - (2) | - (0) | - (3) | - (1) | - (6) | - (4) |
| middle third | No | - (2) | - (0) | - (3) | - (1) | - (6) | - (4) |
| last third | Yes | - (1) | - (1) | - (1) | - (2) | - (2) | - (5) |
| last third | No | - (0) | - (1) | - (1) | - (2) | - (1) | - (5) |
| last day | Yes | - (1) | - (1) | - (1) | - (1) | - (1) | - (1) |
| last day | No | - (1) | - (1) | - (1) | - (1) | - (1) | - (2) |

30 events in a year and hardly any trades in each box. Too small to test or to trade.

## The exam

- **Rotten Tomatoes: No where Yes is 50-75c, early in the market's life**: 63 bets in 45 separate groups, +$23.08 per $100, luck range -$3.29 to +$49.44, worst case -$37.84 per $100, verdict **Ahead, but could be luck**.
- **Rotten Tomatoes: same, Yes at 40-80c**: 86 bets in 50 separate groups, +$16.97 per $100, luck range -$6.10 to +$40.04, worst case -$35.17 per $100, verdict **Ahead, but could be luck**.
- **YouTube view counts: always No, prices alone**: 922 bets in 231 separate groups, -$6.28 per $100, luck range -$9.46 to -$3.10, worst case -$13.62 per $100, verdict **Losing**.

**Verdict:** YouTube and flu dropped. Rotten Tomatoes keeps one lean that is too small to call (about 20 films a month since August, so a live test would need months). No track.
