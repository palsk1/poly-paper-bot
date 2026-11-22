# "How many SpaceX launches this month" bets vs the public launch list (22 Nov 2026, `spacex.py`)

## In short

- **The bets.** Kalshi's KXSPACEXCOUNT asks "more than X SpaceX launches in October?" every month: 101 finished monthly markets in 14 months (Jul 2025 to Oct 2026), $22.4 million traded, so the biggest tech family we have dug by money. Polymarket has a small copy (9 monthly lists with trades, most under $10,000). Kalshi also has Starship flight dates, all US commercial launches and Rocket Lab counts (small, not dug).
- **The outside number.** Jonathan McDowell's free launch list GCAT (planet4589.org, readable from Actions, updated within days). It reproduces Kalshi's monthly SpaceX result in 12 of 14 months (two are one launch off, near a month's edge).
- **The model loses to the price everywhere.** Model: launches so far this month + the pace of the last 60 days. The price forecasts better at every point in the month, and much better near the end (it knows the launch schedule, weather scrubs, and the 2026 slowdown). Yes where the model is 10c+ above the price: -$72.66 per $100 ("Losing").
- **Prices alone:** Yes on long shots never paid (3-25c: 2 wins in about 150 bets). No early in the month looked good at every price.
- **Backward look:** No at 10-97c with 10+ days left, +$32.37 per $100 on 79 bets, "Ahead, but could be luck", but ahead in only 6 of 14 months: four big months (Dec, Jan, Apr, Sep, when SpaceX launched fewer than expected) carry it, and the second half is behind. That is one bet on "SpaceX slows down", not a repeatable edge.
- **Verdict: dropped, no track.** Only one month at a time; answers inside a month win and lose together, so a year gives 12 real tries.

## Traps

- Kalshi closes the month's markets a day or more after the month ends: take the month from the event name (`26JAN`), not from the close time.
- GCAT times are UTC; the month is counted in New York time.

## How it was run

Probes `aim_kall-space` (Kalshi markets + hourly bid/ask + trades, `aim.SPACE_K`), `famf_spacex` (Polymarket), `spx_src` (GCAT -> `bt_cache/spx/launches.json.gz`). Then `python3 spacex.py report` (`report log` writes the ledger lines). Kalshi buys: $10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c, one bet per market at the first hour that fits. 120 cuts counted in the exam's luck bar.

## The data

- Kalshi KXSPACEXCOUNT, monthly: 101 finished 'more than X launches' markets in 14 months, 101 with hourly prices, 50537 hourly looks, $22,361,410 traded.
- Launch list: 729 SpaceX launches in GCAT since 2015.

### Who forecasts better (Brier score, lower is better)

| days left | looks | price | count + pace |
|---|---|---|---|
| 20-40 | 18661 | 0.103 | 0.168 |
| 10-20 | 16067 | 0.060 | 0.140 |
| 5-10 | 7513 | 0.035 | 0.112 |
| 2-5 | 4197 | 0.017 | 0.080 |
| 0-2 | 2656 | 0.006 | 0.073 |

### The tests

$10 at the real asking price + Kalshi's fee, buy-sell gap at most 15c, one bet per market at the first hour that fits.

| rule | bets | won | months | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|---|
| Yes where count + pace is 10c+ above the price | 64 | 11 | 13 | -$72.66 | -$72.18 / -$73.15 | -85.79 to -59.54 | -100.0 | Losing |
| No where count + pace is 10c+ below the price | 54 | 23 | 14 | +$32.84 | +$31.72 / +$33.97 | -30.69 to 96.38 | -100.0 | Ahead, but could be luck |
| Yes where count + pace is 20c+ above the price | 53 | 7 | 13 | -$79.43 | -$68.97 / -$89.49 | -93.91 to -64.94 | -100.0 | Losing |
| No where count + pace is 20c+ below the price | 42 | 15 | 13 | +$20.26 | +$71.91 / -$31.39 | -45.66 to 86.18 | -100.0 | Ahead, but could be luck |
| Same, 10c+, last 10 days only, Yes | 30 | 4 | 13 | -$81.53 | -$71.71 / -$91.34 | -97.39 to -65.67 | -100.0 | Losing |
| Same, 10c+, last 10 days only, No | 24 | 4 | 13 | -$52.46 | -$4.92 / -$100.00 | -103.31 to -1.61 | -100.0 | Losing |
| Always Yes, first look | 96 | 35 | 14 | -$54.75 | -$59.64 / -$49.86 | -69.32 to -40.18 | -89.86 | Losing |
| Always No, first look | 94 | 56 | 14 | +$25.30 | +$59.27 / -$8.67 | -17.9 to 68.51 | -72.5 | Ahead, but could be luck |

### Prices alone (per $100, bets, won)

| price | side | 10+ days left | 3-10 days | last 3 days |
|---|---|---|---|---|
| 3-10c | Yes | -$100.00 (55, 0 won) | -$100.00 (23, 0 won) | -$100.00 (11, 0 won) |
| 3-10c | No | +$5.08 (51, 51 won) | +$4.12 (20, 20 won) | +$4.35 (8, 8 won) |
| 10-25c | Yes | -$82.08 (43, 2 won) | -$100.00 (14, 0 won) | - (4) |
| 10-25c | No | +$12.06 (43, 41 won) | +$13.58 (14, 14 won) | - (4) |
| 25-50c | Yes | -$58.10 (41, 8 won) | - (6) | - (2) |
| 25-50c | No | +$25.17 (41, 33 won) | - (6) | - (2) |
| 50-75c | Yes | -$38.54 (36, 15 won) | -$6.40 (12, 8 won) | - (6) |
| 50-75c | No | +$41.63 (36, 21 won) | -$24.09 (12, 4 won) | - (6) |
| 75-90c | Yes | -$25.36 (38, 25 won) | -$0.29 (15, 13 won) | +$5.68 (12, 11 won) |
| 75-90c | No | +$55.63 (38, 13 won) | -$26.59 (15, 2 won) | -$58.33 (12, 1 won) |
| 90-97c | Yes | -$15.47 (36, 29 won) | -$0.10 (19, 18 won) | +$5.38 (14, 14 won) |
| 90-97c | No | +$78.87 (39, 7 won) | -$66.56 (23, 1 won) | -$100.00 (14, 0 won) |

### Backward look

The table above says No paid early in the month at every price. Month by month it is a coin toss:

| rule | bets | won | months | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|---|
| No at 10-97c with 10+ days left | 79 | 43 | 14 | +$32.37 | +$76.02 / -$10.20 | -17.76 to 82.5 | -79.64 | Ahead, but could be luck |

Ahead in 6 of 14 months; 25JUL -$20.00, 25AUG -$30.00, 25SEP -$15.07, 25DEC +$132.24, 26JAN +$105.80, 26FEB +$27.74, 26MARB -$34.48, 26APR +$130.25, 26MAY +$10.87, 26JUN -$37.11, 26JUL -$35.78, 26AUG -$16.44, 26SEP +$83.47, 26OCT -$45.80.

### Polymarket check

49 markets in 9 monthly lists with real trades (small: most lists trade under $10,000). $10 at the worst price of the next 2 hours + 2c + fee, a day after the list opens.

| rule | bets | won | months | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|---|
| Polymarket: always Yes, a day in | 12 | 3 | 4 | -$58.96 | -$57.00 / -$60.84 | -79.35 to -38.57 | -100.0 | Too early to tell |
| Polymarket: always No, a day in | 9 | 6 | 3 | -$23.14 | -$46.08 / -$4.97 | -50.0 to 3.71 | -100.0 | Too early to tell |
