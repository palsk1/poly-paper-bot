# All Yes vs all No (2026-11-10, `yesno.py`)

**Short answer:** both lose, Yes loses more. $1 on every open market every day at 12:00 UTC:

| | Polymarket (3 months, about 215,000 bets a side) | Kalshi (2 months, real ask, about 600,000 markets scaled from a sample) |
|---|---|---|
| All Yes | about **-$11 to -$18 per $100** | **-$25 per $100** (-$18 if you skip silly 99c/1c prices) |
| All No | about **-$6 to -$8 per $100** | **-$20 per $100** (-$12 if you skip silly prices) |

At the "dream" price (no spread, no fee) both sites are close to fair: Yes -$1 / +$1, No -$5 / -$5. So almost all of
the loss is the cost of buying: on cheap long shots one extra cent is a big slice of the price. Long shots under 10c
lose on both sides (No under 10c, i.e. betting against something that's nearly certain, loses $65-80). Favorites at
90c+ are about even. Matches the wallet study (Yes -$8, No about even): the boring side is fair, not a gift.

Kalshi note: the 10 Aug - 10 Sep part failed (Kalshi's old-markets list refused us, "too many requests"), so Kalshi
covers 11 Sep - 9 Nov. Some days' lists were also cut short. Kalshi only gives a price in hours when something
happened, so about half the noons had no price and were skipped.

---

Research only. Jan's question: what if you put $1 on Yes in **every** open market every day, or $1 on No in every open market, at 12:00 UTC, for 3 months (2026-08-10 to 2026-11-09, 92 days)? Polymarket and Kalshi separately. Numbers are profit per $100 bet. In brackets: how many $1 bets.

## Polymarket (38,076 markets, 214,785 market-days)

### Profit per $100

Real buys = the first time a real person bought that side within 3 hours after noon, on the trade tape. That's what a slow bot would really pay.

| What you bought | Chart price (the dream) | Chart +0.3c + fee | Same, only prices under 1h old | Chart +1c + fee | Real buys (sample of 1,500 days) | Same sample at chart price |
|---|---|---|---|---|---|---|
| **All Yes** | **-$1.35** | **-$18.09** | **-$10.79** | **-$28.69** | **+$14.43** | **-$5.10** |
| Yes at under 10c | +$2.60 (107,112) | -$30.14 (107,112) | -$19.26 (7,104) | -$49.57 (107,112) | +$36.86 (94) | -$15.02 (94) |
| Yes at 10-30c | -$7.10 (33,124) | -$8.71 (33,124) | -$3.56 (2,051) | -$12.25 (33,124) | -$8.98 (61) | +$4.62 (61) |
| Yes at 30-50c | -$11.81 (16,983) | -$12.48 (16,983) | -$2.35 (1,398) | -$14.02 (16,983) | +$32.09 (38) | +$0.36 (38) |
| Yes at 50-70c | -$5.06 (27,826) | -$5.57 (27,826) | -$6.50 (2,166) | -$6.75 (27,826) | -$14.56 (31) | -$11.24 (31) |
| Yes at 70-90c | -$3.27 (10,435) | -$3.62 (10,435) | -$2.37 (625) | -$4.43 (10,435) | +$1.52 (18) | +$1.85 (18) |
| Yes at 90-97c | +$2.89 (11,339) | +$2.58 (11,339) | +$0.34 (484) | +$1.86 (11,339) | +$7.87 (11) | +$6.14 (11) |
| Yes at 97c+ | +$1.23 (7,966) | +$0.96 (7,966) | +$0.43 (1,212) | +$0.44 (7,966) | +$1.07 (11) | +$1.54 (11) |
| **All No** | **-$5.35** | **-$6.00** | **-$7.85** | **-$7.22** | **-$11.40** | **-$10.56** |
| No at under 10c | -$70.29 (19,305) | -$73.08 (19,305) | -$64.08 (1,696) | -$77.18 (19,305) | -$100.00 (23) | -$100.00 (23) |
| No at 10-30c | +$7.77 (10,252) | +$6.01 (10,252) | +$4.99 (614) | +$2.15 (10,252) | -$49.54 (16) | -$42.42 (16) |
| No at 30-50c | -$0.36 (26,200) | -$1.01 (26,200) | -$0.44 (2,035) | -$2.48 (26,200) | -$31.29 (21) | -$29.01 (21) |
| No at 50-70c | +$5.24 (18,395) | +$4.72 (18,395) | -$1.61 (1,507) | +$3.52 (18,395) | -$3.47 (39) | -$3.33 (39) |
| No at 70-90c | +$0.03 (32,839) | -$0.32 (32,839) | -$2.06 (2,041) | -$1.15 (32,839) | +$9.00 (64) | +$9.43 (64) |
| No at 90-97c | +$0.79 (40,463) | +$0.48 (40,463) | -$1.68 (2,028) | -$0.23 (40,463) | -$2.88 (53) | -$1.86 (53) |
| No at 97c+ | +$0.11 (67,331) | -$0.13 (67,331) | -$0.31 (5,119) | -$0.52 (67,331) | -$1.31 (99) | -$1.15 (99) |

- Yes: real buyers paid a median +0.3c vs the chart (264 buys).
- No: real buyers paid a median +0.3c vs the chart (315 buys).
- under 10c: real buyers paid a median +0.1c vs the chart (117 buys).
- 10-30c: real buyers paid a median +0.5c vs the chart (77 buys).
- 30-50c: real buyers paid a median +0.5c vs the chart (59 buys).
- 50-70c: real buyers paid a median +0.5c vs the chart (70 buys).
- 70-90c: real buyers paid a median +1.5c vs the chart (82 buys).
- 90-97c: real buyers paid a median +0.7c vs the chart (64 buys).
- 97c+: real buyers paid a median +0.1c vs the chart (110 buys).
- Tape misses: {'nobody bought in 3h': 2387, 'no tape': 34}

Halves (chart +0.3c): Yes first half -$10.74, Yes second half -$31.77, No first half -$4.44, No second half -$8.91

## Kalshi (sample of 22,662 of 594,848 markets, weighted back to all of them)

### Profit per $100, at the real ask + fee

Kalshi's history has the real best bid and ask each hour, so 'real ask' is what you'd really pay. Many quiet Kalshi markets show silly prices like 'buy at 99c, sell at 1c'; the last column skips those.

| What you bought | Middle of bid and ask, no fee (the dream) | Real ask + fee | Same, not scaled up | Real ask, only tight prices (bid and ask 5c apart or less) |
|---|---|---|---|---|
| **All Yes** | **+$1.35** | **-$24.73** | **-$25.97** | **-$17.68** |
| Yes at under 10c | -$2.34 (5,510) | -$43.84 (6,930) | -$47.96 (6,930) | -$43.10 (6,154) |
| Yes at 10-30c | +$0.87 (8,395) | -$27.41 (9,171) | -$29.16 (9,171) | -$13.38 (5,112) |
| Yes at 30-50c | +$3.85 (7,217) | -$14.70 (6,667) | -$15.68 (6,667) | -$4.55 (3,842) |
| Yes at 50-70c | +$0.69 (5,490) | -$13.23 (5,218) | -$14.67 (5,218) | -$6.41 (2,855) |
| Yes at 70-90c | +$3.61 (3,901) | -$15.53 (4,659) | -$15.64 (4,659) | -$1.44 (1,720) |
| Yes at 90-97c | +$2.63 (1,283) | -$24.48 (2,360) | -$21.54 (2,360) | +$2.72 (708) |
| Yes at 97c+ | +$1.35 (349) | -$30.42 (2,514) | -$27.76 (2,514) | +$0.30 (615) |
| **All No** | **-$5.11** | **-$20.12** | **-$20.70** | **-$11.89** |
| No at under 10c | -$47.42 (1,632) | -$82.52 (2,338) | -$81.86 (2,338) | -$82.04 (1,976) |
| No at 10-30c | -$17.48 (3,822) | -$42.02 (3,919) | -$43.23 (3,919) | -$23.30 (1,580) |
| No at 30-50c | -$0.44 (5,106) | -$16.03 (4,632) | -$17.15 (4,632) | -$0.19 (2,564) |
| No at 50-70c | -$3.03 (7,518) | -$16.01 (5,696) | -$13.80 (5,696) | -$8.32 (3,761) |
| No at 70-90c | +$0.38 (8,335) | -$9.75 (7,957) | -$10.34 (7,957) | -$0.95 (4,621) |
| No at 90-97c | -$0.95 (4,466) | -$12.39 (5,266) | -$11.92 (5,266) | -$2.62 (2,745) |
| No at 97c+ | +$0.55 (1,266) | -$9.84 (4,488) | -$10.21 (4,488) | -$1.39 (2,148) |

Halves: Yes first half -$18.02, Yes second half -$27.80, No first half -$23.92, No second half -$18.38

### Kalshi by kind of market (per $100)

| Kind | Yes | No |
|---|---|---|
| apps/tech | -$30.44 | -$48.36 |
| crypto price | -$62.08 | -$42.55 |
| economics | -$14.32 | -$0.19 |
| elections | -$71.96 | +$10.16 |
| entertainment | -$37.54 | -$50.70 |
| esports | -$32.00 | -$51.21 |
| mentions | -$32.61 | -$10.93 |
| other (one-off questions) | -$32.36 | -$20.33 |
| post counts | -$100.00 | +$10.02 |
| sports | -$17.46 | -$13.60 |
| stocks | -$48.23 | -$64.80 |
| weather | -$10.95 | -$41.70 |

Data notes: {'noon without a quote': 42639, 'spread over 5c (or one side empty)': 18016, 'market-days': 39863, 'Yes: nobody selling': 2344, 'spread 5c or less': 21847, 'No: nobody selling': 5567, 'markets sampled': 22662, 'markets that closed in the window (all)': 594848}

## Limits

- Only markets that ended before 2026-11-10 count (we need the result, and later ones are the holdout). So on the last days of the window only short markets are in.
- Polymarket: bt_cache only has markets that ended with $20k+ traded, plus every choice of those events. Tiny markets are missing. Chart prices are 12-hourly, so 'noon' can be up to 13 hours old.
- Kalshi: a random sample per close day, scaled up. Fee as if orders were big enough not to round up.
