# Earthquake markets against a counting model (quakes.py)

Generated 2026-11-13T16:46:00Z. Paper only. The holdout from 2026-11-10 is not in here.

"How many earthquakes of 6.5 or stronger this week?" and "How big will today's biggest earthquake be?" Polymarket has run these since October 2025: 860 finished markets. 62 ask something else ("another 7.0 by...") and are left out. The USGS earthquake list (46,262 quakes of 4.5+ since 2021) reproduces the result of 773 of the rest; 25 don't match, because USGS changed a magnitude after the market closed. 666 markets in 106 events have real trades; the middle one saw about $2,494.

## The idea

Big earthquakes come at a steady average pace and don't follow the news. So "what has happened so far + the usual pace (last 3 years) for the time left" gives a fair chance for every bracket, hour by hour. Is the price ever far from it?

## Who forecasts better?

Score = average squared miss, smaller is better. Model knows each quake 30 minutes late.

| share of the window gone | kind | markets | the model | Polymarket |
|---|---|---|---|---|
| before the start | how many this week | 269 | 0.0967 | 0.0985 |
| 0 to 25 in 100 | how many this week | 434 | 0.0903 | 0.0908 |
| 25 to 50 in 100 | how many this week | 445 | 0.0805 | 0.0797 |
| 50 to 75 in 100 | how many this week | 469 | 0.0701 | 0.0721 |
| 75 to 100 in 100 | how many this week | 457 | 0.0416 | 0.0427 |
| 0 to 25 in 100 | biggest of the day | 54 | 0.1472 | 0.1438 |
| 25 to 50 in 100 | biggest of the day | 123 | 0.1127 | 0.1239 |
| 50 to 75 in 100 | biggest of the day | 124 | 0.0835 | 0.0966 |
| 75 to 100 in 100 | biggest of the day | 122 | 0.0476 | 0.0708 |

About a tie early on; the model is a little better late in the window. But it reads the final USGS numbers, and live magnitudes are often revised by 0.1 in the first day, so part of that is hindsight.

## Buying where the two disagree

One $10 bet per market: the first hour where the model and the last real price are that far apart, on the side the model calls cheap, only if it is still cheap at the price paid. Fee included.

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| 10c+ apart, quakes known 30 min late, worst price of the next 15 min + 2c | 114 | 68 | +$18.53 | +$25.61 | +$11.39 |
| 20c+ apart, quakes known 30 min late, worst price of the next 15 min + 2c | 50 | 33 | +$31.93 | +$16.35 | +$47.60 |
| 30c+ apart, quakes known 30 min late, worst price of the next 15 min + 2c | 26 | 17 | +$56.95 | +$29.20 | +$84.88 |
| 10c+ apart, quakes known 30 min late, worst price of the next 2 hours + 1c | 146 | 78 | +$9.31 | +$31.53 | -$13.00 |
| 20c+ apart, quakes known 30 min late, worst price of the next 2 hours + 1c | 59 | 41 | +$61.03 | +$52.13 | +$69.66 |
| 30c+ apart, quakes known 30 min late, worst price of the next 2 hours + 1c | 27 | 17 | +$103.42 | +$72.37 | +$132.49 |
| 10c+ apart, quakes known 120 min late, worst price of the next 15 min + 2c | 116 | 62 | +$11.46 | +$24.86 | -$2.02 |
| 20c+ apart, quakes known 120 min late, worst price of the next 15 min + 2c | 64 | 37 | +$13.32 | +$3.14 | +$23.55 |
| 30c+ apart, quakes known 120 min late, worst price of the next 15 min + 2c | 35 | 15 | +$9.34 | -$7.29 | +$25.13 |
| 10c+ apart, quakes known 120 min late, worst price of the next 2 hours + 1c | 167 | 82 | +$1.17 | +$27.96 | -$25.37 |
| 20c+ apart, quakes known 120 min late, worst price of the next 2 hours + 1c | 86 | 46 | +$22.65 | +$20.34 | +$24.97 |
| 30c+ apart, quakes known 120 min late, worst price of the next 2 hours + 1c | 49 | 18 | +$14.76 | +$0.24 | +$28.79 |
| 20c+, 2 hours late, 15 min + 2c, no quake within 0.1 of a line so far | 22 | 14 | +$50.21 | -$10.23 | +$110.75 |
| 10c+, how many this week, buying Yes | 61 | 22 | +$4.09 | +$63.65 | -$53.86 |
| 10c+, how many this week, buying No | 66 | 44 | +$7.60 | +$15.00 | +$0.16 |
| 10c+, biggest of the day, buying Yes | 4 | - | - | - | - |
| 10c+, biggest of the day, buying No | 6 | - | - | - | - |
| 10c+, first third of the window | 36 | 18 | -$12.50 | +$0.46 | -$25.55 |
| 10c+, middle third | 52 | 31 | +$43.07 | +$79.50 | +$6.42 |
| 10c+, last third | 61 | 33 | +$3.72 | -$2.01 | +$9.30 |

The 20c+ rows look great and are not. The main version (20c+, quakes known 2 hours late, 15 min + 2c) made +$87.01 in total on 64 bets, and its 3 best bets made +$142.17 of that; the other 61 together made -$55.16. The best one: "Will there be exactly 1 earthquake of magnitude 6.5 or higher worldwide from June 1 - 7?", No bought at 12c while the model said that side was worth 98c. Looked at one by one, these big wins are not real chances: either the trade list shows trades on the wrong side (a market at 2c that still "trades" at 87c hours after the quake), or the price fits a quake count that USGS changed later. A live bot would not have got those prices. At 10c+ apart the first half of the year is ahead and the second half is behind, at either buy price.

## The prices alone (the comb)

No model. One $10 bet per market the first time its price is in the band, at the worst price of the next 15 minutes + 2c. Per $100 (bets).

| when | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| first third | Yes | -$69.78 (72) | -$22.87 (89) | -$4.64 (82) | +$4.53 (43) | - (5) | - (1) |
| first third | No | +$0.30 (71) | -$3.04 (88) | -$8.51 (81) | -$16.91 (43) | - (4) | - (1) |
| middle third | Yes | -$56.80 (82) | -$41.97 (108) | -$15.10 (52) | +$1.77 (59) | +$2.99 (18) | - (3) |
| middle third | No | -$0.49 (76) | +$2.68 (106) | -$4.05 (54) | -$25.22 (55) | -$36.74 (18) | - (3) |
| last third | Yes | -$81.23 (71) | -$25.92 (86) | -$41.80 (40) | -$1.96 (39) | -$3.19 (52) | +$1.60 (24) |
| last third | No | -$0.56 (62) | +$0.88 (84) | +$16.08 (39) | -$30.34 (39) | -$22.34 (51) | +$0.06 (26) |

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| "exactly N" brackets, always Yes | 225 | 26 | -$50.73 | -$50.46 | -$51.00 |
| "exactly N" brackets, always No | 211 | 185 | +$0.09 | +$0.80 | -$0.62 |
| "exactly 0", always Yes | 35 | 16 | -$7.71 | -$16.08 | +$0.20 |
| "exactly 0", always No | 35 | 19 | +$0.87 | +$8.25 | -$6.10 |
| "more than N", always Yes | 28 | 8 | -$21.37 | -$13.24 | -$29.47 |
| "more than N", always No | 28 | 20 | -$12.23 | -$16.38 | -$8.05 |
| 5.5+ counts, always Yes | 161 | 17 | -$55.66 | -$52.61 | -$58.67 |
| 5.5+ counts, always No | 154 | 136 | -$0.42 | -$2.33 | +$1.49 |
| 6.5+ counts, always Yes | 130 | 35 | -$24.94 | -$37.25 | -$12.60 |
| 6.5+ counts, always No | 124 | 90 | -$1.19 | +$0.40 | -$2.77 |
| biggest of the day, always Yes | 62 | 15 | -$18.13 | -$38.62 | +$2.32 |
| biggest of the day, always No | 60 | 45 | -$3.57 | -$2.27 | -$4.88 |
| No on long shots (Yes 3-25c), from the middle of the window on | 212 | 193 | +$1.26 | +$0.35 | +$2.17 |

Yes buyers lose a lot, most on long shots ($20-65 per $100). No buyers get about their money back, never more. Following a 10-15c price jump loses $15-20 per $100 and betting against one is about even. Nothing to build on.

## The exam

- **Earthquake markets: buy where a counting model and the price are 20c+ apart**: 64 bets in 40 separate groups, +$13.32 per $100, luck range -$12.56 to +$39.21, worst case -$41.42 per $100, verdict **Ahead, but could be luck**.
- **Earthquake markets: same, 10c+ apart**: 116 bets in 59 separate groups, +$11.46 per $100, luck range -$15.73 to +$38.66, worst case -$45.82 per $100, verdict **Ahead, but could be luck**.
- **Earthquake markets: No on long shots (Yes 3-25c), prices alone**: 212 bets in 79 separate groups, +$1.26 per $100, luck range -$1.66 to +$4.18, worst case -$6.25 per $100, verdict **Ahead, but could be luck**.

**Verdict: dropped, no track.** The model is fine, the market is about as good, and the big wins are not real. The family is also small: about 2 events a week.

## Traps found

- **The USGS list is the final version.** Magnitudes move by 0.1 in the first day (the market waits 24 hours for that). A backtest that counts from the final list knows things nobody knew live. `close_call()` marks hours where a quake sits within 0.1 of a line.
- **Wrong-side trades again, and not only crumbs.** Right after a quake the trade list mixes Yes and No prices, in trades of $50 and more. `load()` drops 35 small steps that sit at the mirror of the last price, and buys more than 15c from the last price are thrown out, but some get through. Read the biggest wins one by one before believing a total.
- **Week windows are in US Eastern time**, written in the market's description, not the question.
