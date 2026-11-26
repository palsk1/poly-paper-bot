# What kc_maker's losing bets have in common (26 Nov 2026)

Generated 2026-11-26T19:23:24Z. Paper only. Code: `kcflip.py`. History: every Kalshi 15-minute crypto window of the 7 coins, 16 Jul to 24 Nov 2026. kc_maker's rule the live way: the first minute end from 5 to 1 minutes left where the winning side's best bid is 95c+, bid 1 tick above it, filled when a later trade prints at or below our bid, held to the result. $10 a bid. 'Find' = before 15 Oct (rules picked here), 'check' = 15 Oct to 24 Nov (looked at only after).

All filled bets: 41,705, lost 872 (1 in 47).

**Short answer (26 Nov):** the flips have one thing in common: the coin sat close to its start price when we bid (a small cushion). Once you know the cushion, everything else adds little or nothing: how fast the coin moved, how jumpy it was, the hour, the gap, how busy Kalshi was, other coins. Skipping bids with a cushion under 1.5 (the live bot uses 2.3, kc_maker uses none) keeps about 2 in 3 bets and drops about 3 in 4 flips. On the paper track's own 16 days (never used to pick it): +$122 instead of +$105, worst day -$3.45 instead of -$10.17, 9 days with no loss instead of 1. History check months (15 Oct - 24 Nov): +$4.73 a day, worst day -$38.61, against plain +$2.32 / -$69.64, cushion 2.0 +$4.59 / -$21.24 and the live bot's 2.3 +$2.70 / -$26.23 (all at $10 bids). So 1.5 to 2.0 is the sweet spot; 2.3 gives away money. Exam: Promising, needs more bets. Caveat: the real bot checks every 15 s, so it bids the moment a coin first clears the bar, which is riskier than the paper bot's every-5-minutes look.

## 1. What the flips look like (find months only)

### zu

| zu | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -99 to 0 | 45 | 5 | 9 | -$0.84 |
| 0 to 1 | 2,492 | 97 | 25 | -$0.08 |
| 1 to 1.5 | 6,597 | 191 | 34 | +$0.02 |
| 1.5 to 2 | 7,541 | 157 | 48 | +$0.05 |
| 2 to 2.3 | 3,047 | 43 | 70 | +$0.08 |
| 2.3 to 3 | 3,772 | 31 | 121 | +$0.09 |
| 3 to 4 | 1,878 | 7 | 268 | +$0.09 |
| 4 to 6 | 634 | 1 | 634 | +$0.08 |
| 6 to 99 | 73 | 0 | - | +$0.07 |

### zk

| zk | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -99 to 0 | 34 | 1 | 34 | +$0.00 |
| 0 to 1 | 3,567 | 131 | 27 | -$0.06 |
| 1 to 1.5 | 7,786 | 231 | 33 | -$0.01 |
| 1.5 to 2 | 7,807 | 159 | 49 | +$0.06 |
| 2 to 2.3 | 3,175 | 39 | 81 | +$0.10 |
| 2.3 to 3 | 3,983 | 32 | 124 | +$0.11 |
| 3 to 4 | 2,165 | 11 | 196 | +$0.08 |
| 4 to 6 | 705 | 2 | 352 | +$0.07 |
| 6 to 99 | 72 | 0 | - | +$0.06 |

### M

| M | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 1 to 2 | 5,013 | 92 | 54 | -$0.00 |
| 2 to 3 | 5,566 | 135 | 41 | -$0.02 |
| 3 to 4 | 5,544 | 120 | 46 | +$0.04 |
| 4 to 5 | 5,791 | 116 | 49 | +$0.07 |
| 5 to 6 | 7,870 | 157 | 50 | +$0.07 |

### bid

| bid | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0.95 to 0.96 | 4,891 | 204 | 23 | +$0.03 |
| 0.96 to 0.97 | 5,677 | 173 | 32 | +$0.05 |
| 0.97 to 0.98 | 6,870 | 136 | 50 | +$0.05 |
| 0.98 to 0.99 | 7,314 | 92 | 79 | +$0.03 |
| 0.99 to 1 | 5,032 | 15 | 335 | +$0.03 |

### spread

| spread | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0 to 0.011 | 27,824 | 546 | 50 | +$0.04 |
| 0.011 to 0.021 | 1,622 | 62 | 26 | -$0.02 |
| 0.021 to 0.04 | 331 | 12 | 27 | +$0.07 |
| 0.04 to 1 | 7 | 0 | - | +$0.51 |

### volr

| volr | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0 to 0.5 | 1,168 | 30 | 38 | -$0.00 |
| 0.5 to 0.8 | 6,764 | 147 | 46 | +$0.04 |
| 0.8 to 1.2 | 11,863 | 248 | 47 | +$0.04 |
| 1.2 to 1.6 | 5,002 | 94 | 53 | +$0.05 |
| 1.6 to 2.5 | 1,301 | 14 | 92 | +$0.11 |

### mom1

| mom1 | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -99 to -2 | 177 | 3 | 59 | +$0.07 |
| -2 to -1 | 1,089 | 18 | 60 | +$0.07 |
| -1 to -0.3 | 3,516 | 69 | 50 | +$0.06 |
| -0.3 to 0.3 | 7,778 | 190 | 40 | +$0.01 |
| 0.3 to 1 | 7,659 | 161 | 47 | +$0.03 |
| 1 to 2 | 4,446 | 75 | 59 | +$0.06 |
| 2 to 99 | 1,433 | 17 | 84 | +$0.09 |

### mom3

| mom3 | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -99 to -2 | 55 | 1 | 55 | +$0.09 |
| -2 to -1 | 656 | 11 | 59 | +$0.11 |
| -1 to -0.3 | 2,828 | 81 | 34 | -$0.02 |
| -0.3 to 0.3 | 6,687 | 145 | 46 | +$0.04 |
| 0.3 to 1 | 8,517 | 161 | 52 | +$0.06 |
| 1 to 2 | 5,781 | 108 | 53 | +$0.04 |
| 2 to 99 | 1,574 | 26 | 60 | +$0.04 |

### bid_rise

| bid_rise | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -1 to 0 | 1,114 | 22 | 50 | +$0.11 |
| 0 to 0.02 | 4,184 | 50 | 83 | +$0.07 |
| 0.02 to 0.05 | 5,251 | 104 | 50 | +$0.04 |
| 0.05 to 0.1 | 6,069 | 106 | 57 | +$0.07 |
| 0.1 to 0.2 | 6,526 | 161 | 40 | +$0.02 |
| 0.2 to 1 | 6,640 | 177 | 37 | -$0.01 |

### kvr

| kvr | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0 to 0.5 | 1,711 | 35 | 48 | +$0.04 |
| 0.5 to 1 | 6,423 | 135 | 47 | +$0.05 |
| 1 to 1.5 | 7,913 | 160 | 49 | +$0.06 |
| 1.5 to 2.5 | 9,658 | 204 | 47 | +$0.02 |
| 2.5 to 999 | 4,079 | 86 | 47 | +$0.01 |

### led

| led | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0 to 0.5 | 2,065 | 52 | 39 | -$0.00 |
| 0.5 to 0.8 | 4,357 | 129 | 33 | -$0.04 |
| 0.8 to 0.99 | 3,917 | 87 | 45 | +$0.02 |
| 0.99 to 1.01 | 19,445 | 352 | 55 | +$0.06 |

### n_same

| n_same | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| 0 to 1 | 1,053 | 29 | 36 | -$0.02 |
| 1 to 3 | 3,157 | 78 | 40 | +$0.01 |
| 3 to 5 | 7,534 | 195 | 38 | -$0.00 |
| 5 to 7 | 18,040 | 318 | 56 | +$0.06 |

### oth_minz

| oth_minz | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| -99 to -1 | 20 | 0 | - | +$0.20 |
| -1 to 0 | 3,821 | 97 | 39 | +$0.01 |
| 0 to 1 | 16,766 | 404 | 41 | +$0.02 |
| 1 to 2 | 5,830 | 95 | 61 | +$0.08 |
| 2 to 99 | 3,341 | 23 | 145 | +$0.12 |

### coin

| Coin | Bets | Lost | 1 loss in | $ per bet |
|---|---|---|---|---|
| BNB | 4,485 | 91 | 49 | +$0.04 |
| BTC | 1,885 | 33 | 57 | +$0.06 |
| DOGE | 4,700 | 101 | 46 | +$0.03 |
| ETH | 4,276 | 102 | 41 | +$0.00 |
| HYPE | 4,893 | 113 | 43 | +$0.01 |
| SOL | 4,749 | 88 | 53 | +$0.06 |
| XRP | 4,796 | 92 | 52 | +$0.07 |

### hour (UTC) of the bid

| Hour | Bets | Lost | 1 loss in |
|---|---|---|---|
| 00 | 1,323 | 30 | 44 |
| 01 | 1,372 | 28 | 49 |
| 02 | 1,311 | 33 | 39 |
| 03 | 1,323 | 37 | 35 |
| 04 | 1,304 | 18 | 72 |
| 05 | 1,361 | 27 | 50 |
| 06 | 1,267 | 15 | 84 |
| 07 | 1,042 | 16 | 65 |
| 08 | 1,023 | 17 | 60 |
| 09 | 1,066 | 20 | 53 |
| 10 | 1,028 | 27 | 38 |
| 11 | 1,120 | 28 | 40 |
| 12 | 1,177 | 30 | 39 |
| 13 | 1,258 | 30 | 41 |
| 14 | 1,297 | 22 | 58 |
| 15 | 1,226 | 19 | 64 |
| 16 | 1,264 | 31 | 40 |
| 17 | 1,234 | 31 | 39 |
| 18 | 1,268 | 28 | 45 |
| 19 | 1,266 | 34 | 37 |
| 20 | 1,308 | 19 | 68 |
| 21 | 1,336 | 23 | 58 |
| 22 | 1,323 | 20 | 66 |
| 23 | 1,287 | 37 | 34 |

## 2. Skip rules on the find months, best $ a day first

$10 bids, 91 days.

| Skip rule | Bets | Lost | $ a day | Luck range | Worst day | Days not in the red |
|---|---|---|---|---|---|---|
| none (plain kc_maker) | 29,784 (100 in 100 kept) | 620 | +$12.39 | +$7.17 to +$17.27 | -$64.76 | 63 of 91 |
| Kalshi's own cushion under 1.5 | 17,907 (60 in 100 kept) | 243 | +$15.66 | +$12.12 to +$19.11 | -$43.86 | 75 of 91 |
| Kalshi's own cushion under 1.0 | 25,693 (86 in 100 kept) | 474 | +$15.21 | +$10.59 to +$19.72 | -$65.56 | 63 of 91 |
| cushion under 1.0 unless bid 99c+ | 24,211 (81 in 100 kept) | 434 | +$14.63 | +$10.22 to +$18.86 | -$63.75 | 67 of 91 |
| cushion under 1.0 | 23,542 (79 in 100 kept) | 430 | +$14.61 | +$10.18 to +$18.87 | -$63.88 | 68 of 91 |
| led under 80% of the window | 23,362 (78 in 100 kept) | 439 | +$14.61 | +$10.30 to +$18.87 | -$64.37 | 68 of 91 |
| lower of both cushions under 1.0 | 21,860 (73 in 100 kept) | 382 | +$14.50 | +$10.20 to +$18.64 | -$60.76 | 68 of 91 |
| cushion under 1.0 OR coin 2x jumpier | 23,338 (78 in 100 kept) | 429 | +$14.28 | +$9.82 to +$18.54 | -$64.65 | 67 of 91 |
| cushion under 1.0 OR last minute 1+ against | 22,346 (75 in 100 kept) | 411 | +$13.64 | +$9.55 to +$17.72 | -$67.11 | 67 of 91 |
| cushion under 1.5 unless bid 99c+ | 18,068 (61 in 100 kept) | 245 | +$13.60 | +$10.49 to +$16.74 | -$39.06 | 74 of 91 |
| cushion under 1.5 | 16,945 (57 in 100 kept) | 239 | +$13.47 | +$10.27 to +$16.55 | -$39.88 | 74 of 91 |
| cushion under 1.5 OR coin 2x jumpier | 16,752 (56 in 100 kept) | 238 | +$13.18 | +$10.01 to +$16.30 | -$40.00 | 73 of 91 |
| bid jumped 20c+ in 2 min | 23,144 (78 in 100 kept) | 443 | +$13.02 | +$8.68 to +$17.24 | -$63.09 | 65 of 91 |
| lower of both cushions under 1.5 | 14,045 (47 in 100 kept) | 170 | +$12.82 | +$9.90 to +$15.72 | -$31.67 | 73 of 91 |
| cushion under 1.5 OR last minute 1+ against | 15,952 (54 in 100 kept) | 225 | +$12.64 | +$9.55 to +$15.56 | -$35.83 | 73 of 91 |
| coin 2.5x jumpier than its last hour | 29,784 (100 in 100 kept) | 620 | +$12.39 | +$7.17 to +$17.27 | -$64.76 | 63 of 91 |
| gap 4c+ wide | 29,777 (100 in 100 kept) | 620 | +$12.35 | +$7.14 to +$17.21 | -$64.76 | 63 of 91 |
| gap 2c+ wide | 29,446 (99 in 100 kept) | 608 | +$12.10 | +$7.13 to +$16.87 | -$65.28 | 64 of 91 |
| coin 2x jumpier than its last hour | 29,579 (99 in 100 kept) | 619 | +$12.05 | +$6.83 to +$16.94 | -$65.53 | 63 of 91 |
| busy minute (2.5x usual trading) | 25,705 (86 in 100 kept) | 534 | +$12.02 | +$7.44 to +$16.37 | -$64.63 | 66 of 91 |
| bid jumped 10c+ in 2 min | 16,618 (56 in 100 kept) | 282 | +$11.90 | +$8.24 to +$15.29 | -$81.34 | 72 of 91 |
| cushion under 1.0 OR coin 1.5x jumpier | 21,542 (72 in 100 kept) | 411 | +$11.87 | +$7.56 to +$15.89 | -$69.35 | 68 of 91 |
| last minute moved 1.5+ typical minutes against us | 29,323 (98 in 100 kept) | 614 | +$11.84 | +$6.82 to +$16.66 | -$65.75 | 63 of 91 |
| cushion under 1.0 OR last minute 0.5+ against | 20,523 (69 in 100 kept) | 385 | +$11.56 | +$7.69 to +$15.25 | -$63.70 | 65 of 91 |
| last minute moved 1+ typical minutes against us | 28,518 (96 in 100 kept) | 599 | +$11.39 | +$6.37 to +$16.13 | -$68.00 | 65 of 91 |
| cushion under 1.5 OR coin 1.5x jumpier | 15,090 (51 in 100 kept) | 220 | +$11.29 | +$8.26 to +$14.22 | -$45.31 | 70 of 91 |
| Kalshi's own cushion under 2.0 | 10,100 (34 in 100 kept) | 84 | +$10.72 | +$8.53 to +$12.93 | -$43.31 | 77 of 91 |
| cushion under 1.5 OR last minute 0.5+ against | 14,615 (49 in 100 kept) | 213 | +$10.72 | +$7.75 to +$13.54 | -$40.36 | 69 of 91 |
| coin 1.5x jumpier than its last hour | 27,750 (93 in 100 kept) | 598 | +$9.86 | +$4.78 to +$14.70 | -$70.24 | 61 of 91 |
| last minute moved 0.5+ typical minutes against us | 26,504 (89 in 100 kept) | 564 | +$9.64 | +$4.84 to +$14.07 | -$66.83 | 59 of 91 |
| cushion under 2.0 unless bid 99c+ | 11,365 (38 in 100 kept) | 90 | +$9.50 | +$7.65 to +$11.22 | -$15.55 | 73 of 91 |
| cushion under 2.0 | 9,404 (32 in 100 kept) | 82 | +$9.00 | +$7.24 to +$10.58 | -$17.04 | 74 of 91 |
| cushion under 2.0 OR coin 2x jumpier | 9,225 (31 in 100 kept) | 82 | +$8.64 | +$6.89 to +$10.19 | -$17.23 | 73 of 91 |
| cushion under 2.0 OR last minute 1+ against | 8,719 (29 in 100 kept) | 76 | +$8.23 | +$6.59 to +$9.70 | -$17.86 | 73 of 91 |
| cushion under 1.5, but under 2.5 when 4-5 min left | 10,607 (36 in 100 kept) | 110 | +$8.06 | +$5.88 to +$10.11 | -$32.53 | 70 of 91 |
| bid under 97c | 19,216 (65 in 100 kept) | 243 | +$7.73 | +$4.44 to +$10.85 | -$55.58 | 60 of 91 |
| cushion under 2.0 OR coin 1.5x jumpier | 7,903 (27 in 100 kept) | 66 | +$7.66 | +$6.17 to +$9.05 | -$17.54 | 74 of 91 |
| cushion under 2.0 OR last minute 0.5+ against | 7,971 (27 in 100 kept) | 72 | +$7.21 | +$5.71 to +$8.62 | -$17.86 | 74 of 91 |
| lower of both cushions under 2.0 | 7,209 (24 in 100 kept) | 53 | +$7.17 | +$5.57 to +$8.70 | -$21.27 | 76 of 91 |
| cushion under 2.3 | 6,357 (21 in 100 kept) | 39 | +$6.43 | +$5.25 to +$7.53 | -$22.39 | 73 of 91 |
| cushion under 2.5 | 4,846 (16 in 100 kept) | 22 | +$5.08 | +$4.23 to +$5.87 | -$14.47 | 76 of 91 |
| cushion under 2.0, but under 3 when 4-5 min left | 5,619 (19 in 100 kept) | 38 | +$4.23 | +$3.23 to +$5.19 | -$14.07 | 70 of 91 |
| cushion under 3.0 | 2,585 (9 in 100 kept) | 8 | +$2.51 | +$1.90 to +$3.06 | -$17.46 | 84 of 91 |
| 4-5 minutes left | 16,123 (54 in 100 kept) | 347 | +$1.22 | -$2.68 to +$4.95 | -$55.49 | 50 of 91 |

## 3. The 6 best from the find months, scored on the check months (never seen)

41 days.

| Skip rule | Bets | Lost | $ a day | Luck range | Worst day | Days not in the red |
|---|---|---|---|---|---|---|
| none (plain kc_maker) | 11,921 (100 in 100 kept) | 252 | +$2.32 | -$5.76 to +$9.96 | -$69.64 | 23 of 41 |
| Kalshi's own cushion under 1.5 | 6,141 (52 in 100 kept) | 83 | +$5.31 | +$0.72 to +$9.69 | -$30.58 | 30 of 41 |
| Kalshi's own cushion under 1.0 | 9,099 (76 in 100 kept) | 177 | +$2.54 | -$3.64 to +$8.53 | -$68.32 | 23 of 41 |
| cushion under 1.0 unless bid 99c+ | 10,833 (91 in 100 kept) | 206 | +$4.93 | -$2.72 to +$11.98 | -$69.01 | 24 of 41 |
| cushion under 1.0 | 10,749 (90 in 100 kept) | 206 | +$4.80 | -$2.84 to +$11.85 | -$69.06 | 24 of 41 |
| led under 80% of the window | 9,354 (78 in 100 kept) | 182 | +$4.44 | -$2.61 to +$11.21 | -$73.49 | 21 of 41 |
| lower of both cushions under 1.0 | 9,998 (84 in 100 kept) | 192 | +$3.09 | -$4.23 to +$9.81 | -$69.06 | 24 of 41 |
| cushion under 1.5 (the pick) | 7,298 (61 in 100 kept) | 106 | +$4.73 | -$0.75 to +$9.90 | -$38.61 | 28 of 41 |
| cushion under 2.0 (like kc_maker_safe) | 3,728 (31 in 100 kept) | 24 | +$4.59 | +$2.40 to +$6.54 | -$21.24 | 31 of 41 |
| cushion under 2.3 (like the live bot) | 2,480 (21 in 100 kept) | 12 | +$2.70 | +$0.80 to +$4.22 | -$26.23 | 31 of 41 |

## 4. Fresh test: the live paper track `kc_maker`'s own bets

3,251 of its 3,894 finished bets fall inside the cached history (2026-11-09 to 2026-11-24); real fills from Kalshi's trade list, its real $10 bids. Each bet's cushion is worked out from Binance at the minute it was placed. None of these bets were used to pick anything.

| Skip when cushion is under | Bets kept | Lost | Total | $ a day | Worst day | Days with 0 losses |
|---|---|---|---|---|---|---|
| nothing (plain kc_maker) | 3,251 | 38 | +$105.45 | +$6.59 | -$10.17 | 1 of 16 |
| 1.0 | 2,884 | 30 | +$81.93 | +$5.12 | -$12.30 | 2 of 16 |
| 1.5 | 2,138 | 9 | +$122.47 | +$7.65 | -$3.45 | 9 of 16 |
| 2.0 | 1,358 | 4 | +$51.18 | +$3.20 | -$6.30 | 12 of 16 |
| 2.3 | 963 | 1 | +$42.72 | +$2.67 | -$6.71 | 15 of 16 |

## 5. Exam

- kc_maker skip cushion under 1.5, check months: 7,298 bets, Promising, needs more bets

