# Weather forecasts vs weather markets (wxcast.py)

Written by `python3 wxcast.py run` on 2026-11-10. Research only, no track. Days 2025-12-28 to 2026-11-10 (the holdout from PROTOCOL.md is left out).

**Question:** do free professional forecasts (NOAA's GFS, Europe's ECMWF, NOAA's National Blend where it exists, all as Open-Meteo stored them *when they were made*) know tomorrow's high or low temperature better than Kalshi and Polymarket prices, by enough to pay the costs?

**How:** for every finished daily high/low market, at three moments (10am two days before, 10am the day before, 6pm the day before), take the forecast that was public then (a run counts 8 hours after it started), correct it by how far it missed at that station over the last 60 finished days (only days already settled at the time), and turn it into a chance per bucket with the spread of those past misses. Then buy the one bucket+side per market where the forecast beats the cost by the most, if by at least the threshold. Kalshi: the real hourly ask (YES) or bid (NO buys at 1 - bid), plus the taker fee for 10 contracts. Polymarket: history has no order book, so the listed price **+2c** plus the fee (PROTOCOL.md pessimistic case), and +5c as a stress test. Held to the result.

Kalshi settle check: 68382 strikes agree with the settled temperature, 0 don't (should be about 0; non-zero means a strike-reading bug).

## Who knows the temperature better? (lower is better)

Average miss in degrees (Kalshi in °F, Polymarket in °C) of each forecast after the bias fix. For comparison, 1°F is about half a bucket on Kalshi, 1°C is one bucket on Polymarket.

| Market | When | Model | Days | Average miss |
|---|---|---|---|---|
| kalshi | 1 day ahead (10am the day before) | blend | 10645 | 2.32° |
| kalshi | 1 day ahead (10am the day before) | ecmwf_ifs025 | 10645 | 2.68° |
| kalshi | 1 day ahead (10am the day before) | gfs_seamless | 10645 | 2.70° |
| kalshi | 1 day ahead (10am the day before) | ncep_nbm_conus | 10645 | 2.42° |
| kalshi | 2 days ahead (10am two days before) | blend | 10598 | 2.54° |
| kalshi | 2 days ahead (10am two days before) | ecmwf_ifs025 | 10598 | 2.89° |
| kalshi | 2 days ahead (10am two days before) | gfs_seamless | 10598 | 3.05° |
| kalshi | 2 days ahead (10am two days before) | ncep_nbm_conus | 10598 | 2.63° |
| kalshi | evening before (6pm the day before) | blend | 10645 | 2.27° |
| kalshi | evening before (6pm the day before) | ecmwf_ifs025 | 10645 | 2.62° |
| kalshi | evening before (6pm the day before) | gfs_seamless | 10645 | 2.63° |
| kalshi | evening before (6pm the day before) | ncep_nbm_conus | 10645 | 2.36° |
| poly | 1 day ahead (10am the day before) | blend | 8435 | 1.24° |
| poly | 1 day ahead (10am the day before) | ecmwf_ifs025 | 8435 | 1.37° |
| poly | 1 day ahead (10am the day before) | gfs_seamless | 8435 | 1.47° |
| poly | 1 day ahead (10am the day before) | ncep_nbm_conus | 2159 | 1.54° |
| poly | 2 days ahead (10am two days before) | blend | 8339 | 1.35° |
| poly | 2 days ahead (10am two days before) | ecmwf_ifs025 | 8339 | 1.48° |
| poly | 2 days ahead (10am two days before) | gfs_seamless | 8339 | 1.61° |
| poly | 2 days ahead (10am two days before) | ncep_nbm_conus | 2136 | 1.61° |
| poly | evening before (6pm the day before) | blend | 8435 | 1.24° |
| poly | evening before (6pm the day before) | ecmwf_ifs025 | 8435 | 1.36° |
| poly | evening before (6pm the day before) | gfs_seamless | 8435 | 1.47° |
| poly | evening before (6pm the day before) | ncep_nbm_conus | 2159 | 1.53° |

Score per bucket (Brier: 0 = perfect, lower is better). 'Half and half' averages the two.

| Market | When | Buckets | Forecast | Market price | Half and half |
|---|---|---|---|---|---|
| kalshi | 1 day ahead (10am the day before) | 58527 | 0.1256 | 0.1093 | 0.1134 |
| kalshi | evening before (6pm the day before) | 60743 | 0.1258 | 0.1051 | 0.1108 |
| poly | 2 days ahead (10am two days before) | 31248 | 0.0813 | 0.0781 | 0.0771 |
| poly | 1 day ahead (10am the day before) | 61455 | 0.0989 | 0.0895 | 0.0913 |
| poly | evening before (6pm the day before) | 58272 | 0.1053 | 0.0936 | 0.0960 |

When the forecast and the price disagree, who was right? (average forecast chance, average price, how often the bucket really won)

| Market | Forecast vs price | Buckets | Forecast said | Price said | Really won |
|---|---|---|---|---|---|
| kalshi | forecast 15c+ lower | 12603 | 18c | 42c | 43 in 100 |
| kalshi | 5-15c lower | 20035 | 19c | 28c | 29 in 100 |
| kalshi | within 5c | 55195 | 10c | 11c | 9 in 100 |
| kalshi | 5-15c higher | 21438 | 21c | 12c | 11 in 100 |
| kalshi | forecast 15c+ higher | 9999 | 37c | 12c | 12 in 100 |
| poly | forecast 15c+ lower | 16641 | 15c | 39c | 33 in 100 |
| poly | 5-15c lower | 24743 | 16c | 26c | 25 in 100 |
| poly | within 5c | 76494 | 8c | 8c | 7 in 100 |
| poly | 5-15c higher | 26557 | 17c | 8c | 7 in 100 |
| poly | forecast 15c+ higher | 6540 | 29c | 8c | 8 in 100 |

## Betting the forecast: Kalshi (real asks and bids, fee for 10 contracts)

| Rule | Bets | Won | Avg cost | P&L per $100 | Luck range (90%) | Older / newer half | Coin-flip side | Same price, other market |
|---|---|---|---|---|---|---|---|---|
| forecast beats cost by 3c+, all moments | 18897 | 6247 | 37c | -$10.85 | -$12.59 to -$9.20 | -$8.50 / -$12.42 | -$5.59 | -$11.65 |
| forecast beats cost by 5c+, all moments | 17618 | 5704 | 37c | -$11.64 | -$13.44 to -$9.74 | -$9.71 / -$12.91 | -$5.52 | -$11.41 |
| forecast beats cost by 10c+, all moments | 13395 | 4198 | 36c | -$12.18 | -$14.30 to -$9.89 | -$10.28 / -$13.30 | -$5.40 | -$11.99 |
| forecast beats cost by 15c+, all moments | 9330 | 2721 | 34c | -$14.59 | -$17.37 to -$11.99 | -$11.93 / -$15.99 | -$5.27 | -$12.40 |
| 5c+, 2 days ahead (10am two days before) | 0 | | | | | | | |
| 5c+, 1 day ahead (10am the day before) | 8348 | 2665 | 36c | -$10.89 | -$13.15 to -$8.65 | -$7.99 / -$12.65 | -$5.76 | -$12.85 |
| 5c+, evening before (6pm the day before) | 9270 | 3039 | 37c | -$12.30 | -$14.32 to -$10.34 | -$11.09 / -$13.13 | -$5.30 | -$11.06 |
| 5c+, cost under 25c | 14092 | 995 | 10c | -$28.89 | -$33.17 to -$24.46 | -$22.72 / -$32.96 | -$3.67 | -$37.11 |
| 5c+, cost 25-75c | 14275 | 7205 | 56c | -$10.55 | -$12.17 to -$8.92 | -$9.48 / -$11.26 | -$6.72 | -$8.45 |
| 5c+, cost over 75c | 5577 | 4369 | 82c | -$4.47 | -$5.67 to -$2.98 | -$2.50 / -$6.30 | -$5.94 | -$3.82 |
| 5c+, daily highs only | 9813 | 3309 | 38c | -$12.20 | -$14.46 to -$10.00 | -$11.08 / -$13.05 | -$4.46 | -$11.53 |
| 5c+, daily lows only | 7805 | 2395 | 34c | -$10.86 | -$13.32 to -$8.15 | -$6.86 / -$13.07 | -$6.81 | -$11.86 |
| 5c+, buckets that traded $5k+ | 11593 | 4667 | 46c | -$11.73 | -$13.93 to -$9.68 | -$11.13 / -$12.24 | -$4.87 | -$9.98 |
| PLACEBO: a week-old forecast for the wrong day, 5c+ | 20023 | 4085 | 24c | -$15.60 | -$17.87 to -$13.37 | -$18.32 / -$14.02 | -$5.46 | -$15.30 |

## Betting the forecast: Polymarket (listed price +2c, plus fee)

| Rule | Bets | Won | Avg cost | P&L per $100 | Luck range (90%) | Older / newer half | Coin-flip side | Same price, other market |
|---|---|---|---|---|---|---|---|---|
| forecast beats cost by 3c+, all moments | 18824 | 9268 | 51c | -$3.59 | -$5.07 to -$2.12 | -$5.95 / -$0.83 | -$5.59 | -$4.15 |
| forecast beats cost by 5c+, all moments | 17789 | 8778 | 51c | -$3.57 | -$5.14 to -$2.07 | -$5.79 / -$1.16 | -$5.60 | -$4.40 |
| forecast beats cost by 10c+, all moments | 13691 | 6786 | 51c | -$3.00 | -$4.84 to -$1.16 | -$5.91 / -$0.42 | -$5.68 | -$4.44 |
| forecast beats cost by 15c+, all moments | 9082 | 4522 | 51c | -$1.63 | -$3.98 to +$0.54 | -$4.96 / +$0.63 | -$5.85 | -$4.74 |
| 5c+, 2 days ahead (10am two days before) | 2960 | 1608 | 53c | +$1.77 | -$1.25 to +$4.74 | -$4.35 / +$7.95 | -$5.56 | -$1.74 |
| 5c+, 1 day ahead (10am the day before) | 7271 | 3519 | 51c | -$4.72 | -$6.36 to -$2.92 | -$6.13 / -$3.28 | -$5.49 | -$5.11 |
| 5c+, evening before (6pm the day before) | 7558 | 3651 | 51c | -$4.66 | -$6.33 to -$3.11 | -$6.69 / -$2.47 | -$5.73 | -$4.87 |
| 5c+, cost under 25c | 13909 | 863 | 9c | -$29.97 | -$35.53 to -$25.13 | -$25.50 / -$35.38 | -$5.15 | -$39.24 |
| 5c+, cost 25-75c | 15089 | 8828 | 61c | -$4.35 | -$5.91 to -$2.72 | -$7.14 / -$1.55 | -$5.84 | -$3.02 |
| 5c+, cost over 75c | 7282 | 5959 | 82c | +$0.38 | -$1.14 to +$1.82 | -$1.36 / +$2.24 | -$5.18 | -$0.84 |
| 5c+, daily highs only | 15353 | 7391 | 51c | -$5.91 | -$7.28 to -$4.44 | -$5.95 / -$5.87 | -$5.52 | -$4.19 |
| 5c+, daily lows only | 2436 | 1387 | 51c | +$11.22 | +$6.17 to +$15.42 | -$3.54 / +$24.29 | -$6.16 | -$4.86 |
| 5c+, buckets that traded $5k+ | 14149 | 6627 | 52c | -$10.18 | -$11.84 to -$8.69 | -$10.30 / -$10.04 | -$5.40 | -$4.17 |
| PLACEBO: a week-old forecast for the wrong day, 5c+ | 18113 | 7792 | 46c | -$7.18 | -$8.83 to -$5.48 | -$9.37 / -$4.38 | -$6.16 | -$5.01 |
| 5c+, stress: listed price +5c | 15456 | 7658 | 54c | -$8.61 | -$10.33 to -$6.98 | -$11.26 / -$6.04 | -$11.14 | -$9.91 |

## Walk-forward (pick the threshold on one half, score it on the other)

| Market | Direction | Picked | On the picking half | On the other half |
|---|---|---|---|---|
| kalshi | pick on older, score newer | 3c | -$8.50 | 11297 bets, -$12.42 |
| kalshi | pick on newer, score older | 3c | -$12.42 | 7600 bets, -$8.50 |
| poly | pick on older, score newer | 15c | -$5.37 | 5057 bets, +$0.96 |
| poly | pick on newer, score older | 15c | +$0.96 | 4025 bets, -$5.37 |

## By station (5c+ rule, all moments)

| Market | Station | Bets | P&L per $100 |
|---|---|---|---|
| kalshi | KAUS | 1042 | -$14.14 |
| kalshi | KLAX | 1030 | -$11.13 |
| kalshi | KDEN | 984 | -$4.61 |
| kalshi | KMDW | 955 | -$9.70 |
| kalshi | KMSP | 955 | -$13.07 |
| kalshi | KNYC | 940 | -$13.11 |
| kalshi | KPHL | 911 | -$11.08 |
| kalshi | KSFO | 863 | -$8.86 |
| kalshi | KMIA | 806 | -$8.25 |
| kalshi | KSEA | 802 | -$6.19 |
| kalshi | KDFW | 787 | -$12.26 |
| kalshi | KDCA | 785 | -$16.44 |
| kalshi | KATL | 781 | -$11.34 |
| kalshi | KMSY | 781 | -$13.11 |
| kalshi | KSAT | 781 | -$19.21 |
| kalshi | KLAS | 777 | -$23.61 |
| kalshi | KHOU | 752 | -$10.22 |
| kalshi | KOKC | 752 | -$6.96 |
| kalshi | KPHX | 743 | -$8.33 |
| kalshi | KBOS | 722 | -$9.08 |
| kalshi | KSAN | 198 | -$30.42 |
| kalshi | KSDF | 167 | -$5.12 |
| kalshi | KTTN | 166 | -$21.29 |
| kalshi | KEWR | 138 | -$10.33 |
| poly | EGLC | 817 | -$0.21 |
| poly | KLGA | 677 | -$7.32 |
| poly | LFPB | 671 | -$2.47 |
| poly | KMIA | 620 | +$7.11 |
| poly | RKSI | 584 | -$4.64 |
| poly | ZSPD | 552 | -$4.19 |
| poly | RJTT | 537 | -$15.28 |
| poly | LTAC | 487 | -$11.68 |
| poly | EDDM | 475 | -$14.08 |
| poly | CYYZ | 453 | -$1.00 |
| poly | RCSS | 451 | +$18.69 |
| poly | LEMD | 445 | -$13.50 |
| poly | SAEZ | 434 | -$12.89 |
| poly | LIMC | 434 | -$9.47 |
| poly | EPWA | 419 | +$0.69 |
| poly | KDAL | 417 | -$2.32 |
| poly | EFHK | 402 | -$1.82 |
| poly | SBGR | 401 | -$14.12 |
| poly | KATL | 399 | -$4.37 |
| poly | KORD | 395 | -$5.48 |
| poly | EHAM | 393 | -$2.89 |
| poly | KSEA | 389 | +$4.79 |
| poly | FACT | 389 | -$1.64 |
| poly | KLAX | 371 | -$14.47 |
| poly | KSFO | 345 | -$4.53 |

## Drill: Polymarket daily lows (found after looking, so a lead, not proof)

| Rule | Bets | Won | Avg cost | P&L per $100 | Luck range (90%) | Older / newer half | Coin-flip side | Same price, other market |
|---|---|---|---|---|---|---|---|---|
| lows, 5c+, listed price +2c | 2436 | 1387 | 51c | +$11.22 | +$6.17 to +$15.42 | -$3.54 / +$24.29 | -$6.16 | +$0.90 |
| lows, YES (this bucket) bets only | 610 | 86 | 14c | +$3.10 | -$17.21 to +$25.26 | +$0.97 / +$5.92 | -$4.88 | -$45.36 |
| lows, NO (not this bucket) bets only | 1826 | 1301 | 64c | +$11.80 | +$6.81 to +$15.98 | -$4.49 / +$25.32 | -$6.55 | +$4.12 |
| lows, cost under 25c | 517 | 55 | 10c | +$2.35 | -$23.90 to +$29.29 | -$0.30 / +$6.28 | -$4.74 | -$52.34 |
| lows, cost 25-75c | 1652 | 1082 | 59c | +$10.92 | +$4.99 to +$15.84 | -$8.18 / +$26.12 | -$6.70 | +$3.20 |
| lows, cost over 75c | 268 | 251 | 82c | +$14.83 | +$10.55 to +$18.23 | +$12.70 / +$16.71 | -$5.26 | +$3.14 |
| lows, 2 days ahead (10am two days before) | 405 | 288 | 57c | +$24.57 | +$18.21 to +$30.21 | +$13.12 / +$32.25 | -$5.68 | +$6.93 |
| lows, 1 day ahead (10am the day before) | 1002 | 534 | 50c | +$6.99 | +$0.89 to +$12.31 | -$10.13 / +$21.41 | -$5.87 | -$0.53 |
| lows, evening before (6pm the day before) | 1029 | 565 | 50c | +$9.33 | +$3.93 to +$14.41 | -$6.47 / +$23.43 | -$6.63 | -$0.44 |

| Month | Bets | P&L per $100 |
|---|---|---|
| 2026-05 | 354 | +$5.71 |
| 2026-06 | 457 | -$13.59 |
| 2026-07 | 448 | -$4.26 |
| 2026-08 | 326 | +$2.13 |
| 2026-09 | 72 | +$52.29 |
| 2026-10 | 221 | +$32.35 |
| 2026-11 | 558 | +$27.63 |

| Station | Bets | P&L per $100 |
|---|---|---|
| LFPB | 343 | +$9.49 |
| EGLC | 336 | +$9.75 |
| ZSPD | 251 | -$1.96 |
| KMIA | 251 | +$6.62 |
| RKSI | 244 | -$6.60 |
| KLGA | 241 | +$9.21 |
| RJTT | 236 | -$22.43 |
| RCSS | 128 | +$56.07 |
| ZSJN | 24 | +$77.11 |
| LTAC | 14 | -$13.32 |
| EDDM | 14 | -$0.08 |
| LIMC | 14 | +$26.55 |
| LEMD | 14 | -$2.67 |
| EPWA | 14 | +$22.45 |
| EHAM | 14 | +$48.70 |
| EFHK | 14 | +$32.97 |
| OEJN | 14 | +$50.89 |
| FACT | 14 | +$28.70 |
| OPKC | 12 | +$34.65 |
| NZWN | 12 | +$33.62 |
| KDAL | 11 | +$19.54 |
| KATL | 11 | +$45.74 |
| KORD | 11 | +$43.93 |
| KAUS | 11 | +$18.91 |
| KHOU | 11 | +$48.34 |
| KSEA | 11 | +$38.03 |
| KLAX | 11 | +$46.38 |
| KSFO | 11 | +$50.04 |
| SBGR | 11 | +$7.72 |
| SAEZ | 11 | -$29.97 |
| CYYZ | 11 | +$17.24 |
| MMMX | 11 | +$33.36 |
| ZUCK | 10 | +$39.84 |
| ZBAA | 10 | +$41.68 |
| ZHHH | 10 | +$19.27 |
| ZUUU | 10 | +$24.98 |
| ZGSZ | 10 | -$2.43 |
| RKPK | 10 | +$24.74 |
| ZGGG | 10 | +$33.70 |
| ZSQD | 10 | +$29.29 |
| LLBG | 5 | +$46.55 |
| UUWW | 5 | +$69.71 |
| LTFM | 5 | +$37.28 |
| KDEN | 5 | +$45.71 |

| Rule | Bets | Won | Avg cost | P&L per $100 | Luck range (90%) | Older / newer half | Coin-flip side | Same price, other market |
|---|---|---|---|---|---|---|---|---|
| lows, 5c+, listed price +5c | 2187 | 1274 | 55c | +$5.90 | +$0.58 to +$10.02 | -$9.90 / +$18.70 | -$11.76 | -$4.93 |
| check: highs since the first lows market (2026-04-15), 5c+ | 13769 | 6645 | 51c | -$6.12 | -$7.70 to -$4.65 | -$7.01 / -$4.34 | -$5.60 | -$5.56 |
