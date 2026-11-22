# "Which app is #1 in the App Store" bets: the price vs the chart's own record (22 Nov 2026, `appstore.py`)

## In short

- **The bets.** "Will ChatGPT be the #1 free app in the US App Store on Friday?" Polymarket lists the #1 and #2 of the free and the paid chart about once a week (3,603 finished markets, Oct 2025 to Nov 2026, tag `app-store`). Kalshi listed the free #1 and #2 every day from Nov 2024 to Nov 2025 (`KXAPPRANKFREE`, `KXAPPRANKFREE2`, 2,646 markets), then stopped. Kalshi reads the chart at 10:00 New York time, Polymarket at 12:00.
- **The outside number.** Apple's live chart has no free history, but the finished bets themselves tell us which app was on top each day: 349 days of the free #1, 262 of the free #2, 63 of the paid #1. The "record": how often the app on top at the last reading is still there (free #1 the next day: 86 in 100; a week later: 58 in 100; paid #1 a week later: 79 in 100; free #2 a week later: only 17 in 100).
- **The record loses to the price everywhere.** At every distance from the reading the price forecasts better, and betting where they disagree by 10c+ loses on Yes on both sites (-$21.81 and -$12.01 per $100). The No side looks better on Kalshi (+$14.18 on 391 bets) but "could be luck".
- **Prices alone:** buying Yes on apps other than the holder loses badly (-$52.62 Polymarket, -$14.02 Kalshi per $100). Yes on any favourite a day or two ahead loses ($18.69 per $100 on Kalshi).
- **Backward look, one lead:** the app priced at 50-97c a day or two before the reading lost more often than its price said. On Kalshi's #2 spot: No on that favourite made +$37.76 per $100 on 181 bets, both halves ahead, exam "Promising, needs more bets". But: one app (Threads, 92 bets, +$74 per $100) carries it, the 10 best bets made more than the whole profit, it swung from -$54 to +$165 per $100 month to month, Kalshi no longer lists these bets, and Polymarket's #2 lists gave only 17 check bets (+$27.58, second half behind). The same No on the favourite at 6-24 hours before loses on both sites.
- **Verdict: dropped, no track.** Too thin to bet: Polymarket has 2-4 such lists a week, about $10 a bet, money back within a week. Not worth re-checking: a year of Polymarket lists would give about 50 #2 bets.

## Traps

- Polymarket's listed end of these markets is midnight UTC, but the chart is read at 12:00 New York time that day: take the day from the question and the time from the rule (`appstore.read_time`), or the last 12-17 hours of trading (when the live chart is public) look like "before the end".
- App names change ("Sora by OpenAI", "Threads, an Instagram app"): match on `appstore.norm`.
- "Other" is an outcome on Polymarket and wins sometimes (9 free #1 days).
- Kalshi's two series stopped in Nov 2025, so the daily record ends there; after it, the "last reading" is a week old.

## How it was run

- Polymarket: probe `famf_app-store` (`families.py fetch`, markets + every real trade -> `bt_cache/fam_app_store/`). Kalshi: probe `aim_kall-app` (`aim.py` pick `APP_K`, settled markets + hourly bid/ask + trades -> `bt_cache/aim/ktapes_KXAPPRANK*.json.gz`). Then `python3 appstore.py report` (`report log` writes the ledger lines).
- Polymarket buys: $10 at the worst price anyone paid in the next hour (never better than the price seen) + 2c + the market's fee. Kalshi buys: $10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c. One bet per market, first look that fits. Every cut looked at (170) counts in the exam's luck bar.

## The data

- Polymarket: 3603 finished app markets in 206 lists (free and paid chart, #1 and #2), 1392 with real trades, 2025-10-17 to 2026-11-06, usually one list a week.
- Kalshi: 2646 finished markets (#1 and #2 of the free chart, daily), 1294 with hourly prices, 2024-11-15 to 2025-11-14.
- Known chart results: free #1 349 days, free #2 262 days, free #3 1 days, paid #1 63 days, paid #2 15 days; the sites disagree on 0 days.

### How often the app on top at the last reading is still there

| chart | next reading | pairs | still there |
|---|---|---|---|
| free #1 | 2-4 days later | 33 | 18 (55 in 100) |
| free #1 | 5-8 days later | 43 | 25 (58 in 100) |
| free #1 | next day | 271 | 234 (86 in 100) |
| free #2 | 2-4 days later | 38 | 16 (42 in 100) |
| free #2 | 5-8 days later | 35 | 6 (17 in 100) |
| free #2 | next day | 185 | 135 (73 in 100) |
| paid #1 | 2-4 days later | 22 | 15 (68 in 100) |
| paid #1 | 5-8 days later | 39 | 31 (79 in 100) |
| paid #2 | 5-8 days later | 13 | 11 (85 in 100) |

- most days at free #1: chatgpt 234, googlegemini 20, sora 17, loveislandusa 10, other 9, deepseek 8, teadatingadvic 6,  6
- most days at free #2: threads 76, chatgpt 70, teadatingadvic 24, claude 17, loveislandusa 12, googlegemini 10, other 6, sora 5
- most days at paid #1: shadowrocket 52, hotschedules 7, other 3, dualshotrecord 1
- most days at paid #2: hotschedules 13, shadowrocket 1, chromagraphcam 1

### Who forecasts better: the price or the record (the app holding the spot at the last reading)

Brier score, lower is better.

| site | hours before the reading | looks | price | record | held on |
|---|---|---|---|---|---|
| Polymarket | 72- | 291 | 0.167 | 0.218 | 184 |
| Polymarket | 24-72 | 286 | 0.125 | 0.222 | 188 |
| Polymarket | 6-24 | 303 | 0.054 | 0.226 | 195 |
| Polymarket | 0-6 | 306 | 0.018 | 0.224 | 195 |
| Kalshi | 24-72 | 7970 | 0.195 | 0.228 | 5307 |
| Kalshi | 6-24 | 6941 | 0.133 | 0.202 | 4972 |
| Kalshi | 0-6 | 752 | 0.077 | 0.242 | 476 |

### The tests

Polymarket: $10 at the worst price anyone paid in the next hour (never better than the price seen) + 2c + fee. Kalshi: $10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c. One bet per market, first look that fits.

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| Polymarket: Yes on the holder where the record is 10c+ above the price | 39 | 14 | -$21.81 | +$18.24 / -$59.56 | -54.42 to 10.81 | -90.77 | Behind, but could be bad luck |
| Polymarket: No on the holder where the record is 10c+ below the price | 44 | 10 | +$4.99 | -$26.16 / +$35.62 | -61.55 to 71.53 | -100.0 | Ahead, but could be luck |
| Polymarket: always Yes on the holder, first look | 51 | 32 | -$14.61 | -$12.26 / -$16.88 | -35.62 to 6.39 | -59.83 | Behind, but could be bad luck |
| Polymarket: always No on the holder, first look | 50 | 18 | +$24.99 | +$27.82 / +$22.20 | -36.25 to 86.23 | -100.0 | Ahead, but could be luck |
| Polymarket: always Yes on any other app, first look | 107 | 16 | -$52.62 | -$68.78 / -$36.99 | -83.11 to -22.13 | -100.0 | Losing |
| Polymarket: always No on any other app, first look | 62 | 46 | +$8.48 | +$7.45 / +$9.50 | -25.52 to 42.47 | -63.72 | Ahead, but could be luck |
| Kalshi: Yes on the holder where the record is 10c+ above the price | 256 | 83 | -$12.01 | -$36.27 / +$12.25 | -28.95 to 4.93 | -48.05 | Behind, but could be bad luck |
| Kalshi: No on the holder where the record is 10c+ below the price | 391 | 81 | +$14.18 | +$18.82 / +$9.56 | -7.84 to 36.19 | -32.23 | Ahead, but could be luck |
| Kalshi: always Yes on the holder, first look | 562 | 353 | -$7.85 | -$17.66 / +$1.96 | -15.27 to -0.43 | -23.93 | Losing |
| Kalshi: always No on the holder, first look | 572 | 194 | -$0.33 | +$3.23 / -$3.88 | -14.35 to 13.69 | -29.91 | Behind, but could be bad luck |
| Kalshi: always Yes on any other app, first look | 904 | 168 | -$14.02 | -$49.66 / +$21.61 | -26.86 to -1.18 | -41.37 | Losing |
| Kalshi: always No on any other app, first look | 642 | 481 | +$1.29 | -$0.08 / +$2.65 | -3.56 to 6.14 | -9.24 | Ahead, but could be luck |

### Prices alone (per $100, bets, won)


**Polymarket, the holder**

| price | side | 24h+ before | 6-24h | under 6h |
|---|---|---|---|---|
| 3-10c | Yes | - (3) | - (5) | -$100.00 (14, 0 won) |
| 3-10c | No | - (3) | - (3) | - (6) |
| 10-25c | Yes | - (7) | - (10) | - (8) |
| 10-25c | No | - (7) | - (9) | - (6) |
| 25-50c | Yes | - (11) | - (7) | - (8) |
| 25-50c | No | - (11) | - (7) | - (7) |
| 50-75c | Yes | -$37.65 (17, 7 won) | - (8) | - (2) |
| 50-75c | No | +$54.91 (17, 10 won) | - (9) | - (2) |
| 75-90c | Yes | -$16.53 (30, 22 won) | - (8) | - (2) |
| 75-90c | No | +$12.37 (30, 8 won) | - (8) | - (4) |
| 90-97c | Yes | -$12.72 (31, 26 won) | -$5.25 (22, 20 won) | - (11) |
| 90-97c | No | +$86.29 (33, 5 won) | -$22.74 (25, 2 won) | -$95.95 (25, 1 won) |

**Polymarket, other apps**

| price | side | 24h+ before | 6-24h | under 6h |
|---|---|---|---|---|
| 3-10c | Yes | -$92.47 (63, 1 won) | -$100.00 (20, 0 won) | -$89.08 (28, 3 won) |
| 3-10c | No | -$1.12 (30, 29 won) | - (10) | - (9) |
| 10-25c | Yes | +$13.44 (39, 8 won) | - (10) | - (10) |
| 10-25c | No | -$14.91 (36, 28 won) | - (8) | - (6) |
| 25-50c | Yes | -$72.53 (27, 4 won) | +$5.79 (14, 7 won) | - (8) |
| 25-50c | No | +$13.18 (20, 16 won) | -$38.68 (14, 7 won) | - (6) |
| 50-75c | Yes | -$17.26 (15, 8 won) | - (10) | - (8) |
| 50-75c | No | -$1.98 (15, 7 won) | - (10) | - (10) |
| 75-90c | Yes | -$11.84 (12, 9 won) | - (10) | - (6) |
| 75-90c | No | - (11) | - (10) | - (8) |
| 90-97c | Yes | - (2) | - (8) | - (10) |
| 90-97c | No | - (2) | - (10) | -$100.00 (19, 0 won) |

**Kalshi, the holder**

| price | side | 24h+ before | 6-24h | under 6h |
|---|---|---|---|---|
| 3-10c | Yes | -$3.83 (49, 5 won) | -$40.97 (59, 4 won) | -$100.00 (46, 0 won) |
| 3-10c | No | -$3.67 (29, 27 won) | -$1.31 (41, 39 won) | - (8) |
| 10-25c | Yes | -$10.69 (69, 15 won) | -$40.90 (63, 8 won) | - (3) |
| 10-25c | No | -$11.59 (69, 54 won) | -$1.42 (63, 55 won) | - (3) |
| 25-50c | Yes | -$5.38 (89, 36 won) | -$17.84 (81, 30 won) | - (1) |
| 25-50c | No | -$16.14 (89, 53 won) | -$12.35 (81, 51 won) | - (1) |
| 50-75c | Yes | -$23.65 (118, 63 won) | -$13.42 (116, 70 won) | - (3) |
| 50-75c | No | +$8.64 (118, 55 won) | -$5.22 (116, 46 won) | - (3) |
| 75-90c | Yes | -$14.09 (214, 163 won) | -$8.45 (223, 181 won) | +$9.26 (24, 24 won) |
| 75-90c | No | +$16.63 (214, 51 won) | -$14.40 (223, 42 won) | -$100.00 (24, 0 won) |
| 90-97c | Yes | -$6.87 (144, 129 won) | -$8.47 (214, 188 won) | +$1.25 (49, 48 won) |
| 90-97c | No | +$2.54 (175, 21 won) | +$3.60 (259, 29 won) | -$80.39 (102, 1 won) |

**Kalshi, other apps**

| price | side | 24h+ before | 6-24h | under 6h |
|---|---|---|---|---|
| 3-10c | Yes | -$5.41 (414, 38 won) | -$39.34 (452, 31 won) | -$80.18 (193, 3 won) |
| 3-10c | No | -$8.88 (185, 163 won) | -$8.11 (231, 205 won) | -$1.33 (22, 21 won) |
| 10-25c | Yes | -$1.22 (233, 45 won) | -$22.27 (224, 37 won) | -$100.00 (14, 0 won) |
| 10-25c | No | -$10.94 (233, 188 won) | -$6.33 (224, 187 won) | +$9.65 (14, 14 won) |
| 25-50c | Yes | -$25.90 (154, 45 won) | -$26.44 (129, 42 won) | - (4) |
| 25-50c | No | -$2.18 (154, 109 won) | -$4.32 (129, 87 won) | - (4) |
| 50-75c | Yes | -$40.84 (93, 39 won) | -$17.59 (79, 44 won) | - (1) |
| 50-75c | No | +$33.90 (93, 54 won) | -$3.46 (79, 35 won) | - (1) |
| 75-90c | Yes | -$22.65 (62, 42 won) | -$12.87 (70, 54 won) | - (5) |
| 75-90c | No | +$25.70 (62, 20 won) | +$9.16 (70, 16 won) | - (5) |
| 90-97c | Yes | -$12.24 (12, 10 won) | -$8.85 (31, 27 won) | +$3.01 (12, 12 won) |
| 90-97c | No | +$29.10 (13, 2 won) | -$3.86 (33, 4 won) | -$100.00 (23, 0 won) |

### Backward look: what came before the upsets

On Kalshi the app priced at 50-97c a day or two before the reading lost more often than its price said, most of all on the #2 spot. Found by looking at the tables above. The fresh check is Polymarket's own #1 and #2 lists (Oct 2025 to Nov 2026), which the Kalshi rule never saw, but whose price tables were already on screen.

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| Kalshi: No on the favourite (50-97c) 24h+ before | 457 | 138 | +$10.27 | +$1.31 / +$19.19 | -5.43 to 25.97 | -22.91 | Ahead, but could be luck |
| Kalshi: No on the favourite 24h+ before, #1 spot | 276 | 66 | -$7.76 | -$17.26 / +$1.74 | -26.7 to 11.18 | -47.79 | Behind, but could be bad luck |
| Kalshi: No on the favourite 24h+ before, #2 spot | 181 | 72 | +$37.76 | +$42.65 / +$32.92 | 10.79 to 64.73 | -19.45 | Promising, needs more bets |
| Kalshi: No on the favourite 6-24h before | 470 | 109 | -$4.80 | +$5.68 / -$15.29 | -21.4 to 11.8 | -39.85 | Behind, but could be bad luck |
| Kalshi: Yes on the favourite 24h+ before | 433 | 299 | -$18.69 | -$16.03 / -$21.33 | -22.76 to -14.61 | -27.69 | Losing |
| Polymarket check: No on the favourite 24h+ before | 58 | 19 | +$27.51 | +$44.00 / +$11.21 | -27.43 to 82.45 | -88.56 | Ahead, but could be luck |
| Polymarket check: No on the favourite 24h+ before, #2 spot | 17 | 9 | +$27.58 | +$79.20 / -$18.19 | -20.93 to 76.08 | -79.25 | Ahead, but could be luck |
| Polymarket check: No on the favourite 6-24h before | 55 | 10 | -$38.18 | -$77.77 / -$0.37 | -80.36 to 4.01 | -100.0 | Behind, but could be bad luck |

- Kalshi: No on the favourite (50-97c) 24h+ before: profit $469 in all, the 10 best bets made $839 (more than all of it: long-shot No bets at 5-15c that came in).
- Polymarket check: No on the favourite 24h+ before: profit $161 in all, the 10 best bets made $452 (more than all of it: long-shot No bets at 5-15c that came in).
