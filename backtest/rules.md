# Fine-print hunt: does the crowd misprice markets with tricky rules?

Generated 2026-11-09T20:38:31Z. 124,260 finished binary non-sports Polymarket markets since 2026-03-01 with their rule text. 395 were disputed at UMA, 0 got a clarification added, 7,982 needed a second proposal. Paper only.

How to read: same as calib.md. Buy one side at the history price +1-5c plus the taker fee, hold to the result, profit per $100 staked, grouped by event. **<-** = 90% band at +2c above $0, 30+ events, both halves ahead. The 'vs look-alikes' tables compare flagged markets with unflagged ones in the same price band and time slot: an edge has to come from the flag, not the band.

## 1. Do the text flags predict disputes and clarifications?

Share of markets that later got disputed or clarified, flagged vs all. If a flag can't predict trouble, it can't be the reason for a mispricing.

| Flag | Markets | Disputed | Clarified | Disputed per 1,000 | vs all |
|---|---|---|---|---|---|
| rules need it to be OFFICIAL/formal, title doesn't say so | 10,076 | 260 | 0 | 25.8 | 8.1x |
| rules hinge on an announcement, title doesn't say so | 3,486 | 74 | 0 | 21.2 | 6.7x |
| rules say plans/announcements aren't enough, it must take effect | 649 | 36 | 0 | 55.5 | 17.4x |
| decided by 'consensus of credible reporting' (judgment call) | 7,860 | 252 | 0 | 32.1 | 10.1x |
| rules leave room for judgment ('ambiguity', 'discretion', 'spirit') | 5,557 | 59 | 0 | 10.6 | 3.3x |
| rules list 2+ things that DON'T count | 3,452 | 176 | 0 | 51.0 | 16.0x |
| rules name a date the title doesn't | 1,364 | 50 | 0 | 36.7 | 11.5x |
| long rules (1,500+ characters) | 3,813 | 139 | 0 | 36.5 | 11.5x |
| 3+ of the tricky flags at once | 5,062 | 192 | 0 | 37.9 | 11.9x |
| decided by one named website | 117,555 | 150 | 0 | 1.3 | 0.4x |
| has a 50-50 refund clause | 1,318 | 3 | 0 | 2.3 | 0.7x |
| none of the tricky flags (control group) | 108,095 | 43 | 0 | 0.4 | 0.1x |
| all | 124,260 | 395 | 0 | 3.2 | 1.0x |

## 2. Tricky-rule markets: buy YES or NO (Yes/No markets, 1-30 days before the end)

Idea: people read the title, the rules are stricter, so YES is too dear and NO too cheap.

### 1-3 days before the end

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| official: buy YES 10-90c | 1013 | 3157 (1392) | 43c | -$1 | -$3 | -$6 to +$0 | -$5 | -$9 | -$6 / -$0 |
| official: buy NO 10-90c | 1007 | 3132 (1743) | 57c | -$5 | -$6 | -$9 to -$4 | -$8 | -$11 | -$4 / -$9 |
| announce: buy YES 10-90c | 321 | 982 (450) | 45c | -$1 | -$3 | -$9 to +$2 | -$5 | -$9 | -$8 / +$0 |
| announce: buy NO 10-90c | 320 | 976 (527) | 55c | -$4 | -$6 | -$11 to -$1 | -$7 | -$10 | -$3 / -$9 |
| intent_not_enough: buy YES 10-90c | 59 | 207 (123) | 53c | +$11 | +$9 | -$8 to +$26 | +$7 | +$3 | -$3 / +$16 |
| intent_not_enough: buy NO 10-90c | 58 | 205 (82) | 47c | -$17 | -$19 | -$38 to +$1 | -$20 | -$23 | -$5 / -$40 |
| consensus: buy YES 10-90c | 727 | 2445 (1092) | 43c | -$1 | -$3 | -$6 to +$1 | -$5 | -$9 | -$6 / +$0 |
| consensus: buy NO 10-90c | 724 | 2427 (1336) | 56c | -$5 | -$6 | -$9 to -$4 | -$8 | -$11 | -$4 / -$9 |
| discretion: buy YES 10-90c | 671 | 2297 (859) | 37c | -$3 | -$6 | -$9 to -$2 | -$8 | -$12 | -$9 / -$3 |
| discretion: buy NO 10-90c | 671 | 2286 (1428) | 63c | -$3 | -$5 | -$7 to -$3 | -$6 | -$9 | -$3 / -$7 |
| exclusions_2plus: buy YES 10-90c | 329 | 957 (372) | 39c | -$4 | -$6 | -$16 to +$4 | -$8 | -$12 | -$20 / +$8 |
| exclusions_2plus: buy NO 10-90c | 325 | 945 (575) | 61c | -$2 | -$4 | -$10 to +$3 | -$5 | -$8 | +$7 / -$14 |
| date_gap: buy YES 10-90c **<-** | 87 | 207 (96) | 36c | +$24 | +$21 | +$7 to +$35 | +$18 | +$12 | +$11 / +$31 |
| date_gap: buy NO 10-90c | 84 | 203 (108) | 63c | -$18 | -$19 | -$28 to -$10 | -$20 | -$23 | -$13 / -$24 |
| long_rules: buy YES 10-90c | 368 | 1074 (437) | 41c | -$3 | -$6 | -$14 to +$3 | -$8 | -$12 | -$18 / +$5 |
| long_rules: buy NO 10-90c | 366 | 1064 (628) | 59c | -$2 | -$4 | -$10 to +$2 | -$5 | -$8 | +$3 / -$12 |
| tricky_3plus: buy YES 10-90c | 531 | 1762 (781) | 43c | +$0 | -$2 | -$7 to +$2 | -$4 | -$8 | -$8 / +$3 |
| tricky_3plus: buy NO 10-90c | 528 | 1750 (970) | 57c | -$5 | -$7 | -$10 to -$3 | -$8 | -$11 | -$3 / -$11 |
| named_site: buy YES 10-90c | 2316 | 7353 (2862) | 39c | -$5 | -$7 | -$9 to -$5 | -$9 | -$13 | -$8 / -$6 |
| named_site: buy NO 10-90c | 2308 | 7287 (4435) | 61c | -$3 | -$5 | -$6 to -$3 | -$6 | -$9 | -$4 / -$5 |
| fifty_fifty: buy YES 10-90c | 12 | 16 (5) | 54c | -$44 | -$45 | -$75 to -$15 | -$46 | -$48 | -$53 / -$38 |
| fifty_fifty: buy NO 10-90c | 12 | 16 (11) | 46c | +$43 | +$40 | +$11 to +$69 | +$37 | +$32 | +$43 / +$37 |
| plain: buy YES 10-90c | 1379 | 4190 (1694) | 40c | -$4 | -$6 | -$9 to -$3 | -$9 | -$13 | -$8 / -$5 |
| plain: buy NO 10-90c | 1374 | 4143 (2457) | 60c | -$4 | -$6 | -$8 to -$4 | -$7 | -$10 | -$5 / -$7 |

### 1-3 days before the end: flagged vs look-alikes (buy NO, same band 10-90c, +2c)

| Flag | Events | Flagged | Not flagged | Difference (90% band) |
|---|---|---|---|---|
| official, buy NO | 1007 | -$6.4 | -$4.7 | -$1.8 (-$4.6 to +$1.0) |
| announce, buy NO | 320 | -$5.8 | -$5.2 | -$0.6 (-$5.6 to +$4.3) |
| intent_not_enough, buy NO | 58 | -$18.6 | -$5.0 | -$13.6 (-$33.3 to +$6.1) |
| consensus, buy NO | 724 | -$6.4 | -$4.9 | -$1.5 (-$4.6 to +$1.6) |
| discretion, buy NO | 671 | -$4.7 | -$5.4 | +$0.7 (-$1.8 to +$3.3) |
| exclusions_2plus, buy NO | 325 | -$3.7 | -$5.4 | +$1.7 (-$4.9 to +$8.4) |
| date_gap, buy NO | 84 | -$19.0 | -$4.9 | -$14.1 (-$22.8 to -$5.4) |
| long_rules, buy NO | 366 | -$3.9 | -$5.4 | +$1.5 (-$4.7 to +$7.7) |
| tricky_3plus, buy NO | 528 | -$6.7 | -$4.9 | -$1.8 (-$5.5 to +$1.9) |
| named_site, buy NO | 2308 | -$4.7 | -$7.8 | +$3.1 (-$0.9 to +$7.0) |
| fifty_fifty, buy NO | 12 | +$40.3 | -$5.3 | +$45.6 (+$16.6 to +$74.6) |
| official, buy YES **<-** | 1013 | -$2.7 | -$7.3 | +$4.6 (+$0.7 to +$8.5) |
| announce, buy YES | 321 | -$3.5 | -$5.9 | +$2.5 (-$3.6 to +$8.5) |
| intent_not_enough, buy YES | 59 | +$8.7 | -$6.1 | +$14.8 (-$2.2 to +$31.8) |
| consensus, buy YES | 727 | -$2.8 | -$6.8 | +$4.0 (-$0.1 to +$8.2) |
| discretion, buy YES | 671 | -$5.6 | -$5.7 | +$0.1 (-$3.9 to +$4.0) |
| exclusions_2plus, buy YES | 329 | -$6.1 | -$5.6 | -$0.4 (-$10.7 to +$9.8) |
| date_gap, buy YES **<-** | 87 | +$20.8 | -$6.2 | +$27.0 (+$13.1 to +$40.8) |
| long_rules, buy YES | 368 | -$5.7 | -$5.7 | -$0.0 (-$8.8 to +$8.8) |
| tricky_3plus, buy YES | 531 | -$2.1 | -$6.5 | +$4.4 (-$0.5 to +$9.4) |
| named_site, buy YES | 2316 | -$7.0 | -$0.9 | -$6.1 (-$11.0 to -$1.3) |
| fifty_fifty, buy YES | 12 | -$44.9 | -$5.6 | -$39.4 (-$69.4 to -$9.4) |

### 7-30 days before the end

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| official: buy YES 10-90c | 1409 | 5809 (2377) | 41c | -$4 | -$6 | -$8 to -$3 | -$8 | -$12 | -$8 / -$4 |
| official: buy NO 10-90c | 1404 | 5759 (3387) | 59c | -$3 | -$4 | -$6 to -$2 | -$6 | -$9 | -$3 / -$6 |
| announce: buy YES 10-90c | 545 | 1833 (749) | 41c | -$5 | -$7 | -$11 to -$2 | -$9 | -$13 | -$17 / +$1 |
| announce: buy NO 10-90c | 543 | 1818 (1069) | 58c | -$2 | -$3 | -$7 to +$0 | -$5 | -$8 | +$3 / -$10 |
| intent_not_enough: buy YES 10-90c | 95 | 335 (164) | 42c | +$13 | +$10 | -$2 to +$23 | +$8 | +$3 | -$0 / +$17 |
| intent_not_enough: buy NO 10-90c | 94 | 329 (165) | 57c | -$14 | -$16 | -$26 to -$5 | -$17 | -$20 | -$7 / -$28 |
| consensus: buy YES 10-90c | 1242 | 4805 (1958) | 41c | -$3 | -$5 | -$8 to -$2 | -$7 | -$11 | -$9 / -$2 |
| consensus: buy NO 10-90c | 1236 | 4761 (2808) | 59c | -$3 | -$4 | -$6 to -$2 | -$6 | -$9 | -$2 / -$7 |
| discretion: buy YES 10-90c | 617 | 2617 (901) | 36c | -$7 | -$10 | -$14 to -$6 | -$12 | -$16 | -$18 / -$3 |
| discretion: buy NO 10-90c | 613 | 2586 (1689) | 64c | -$0 | -$2 | -$4 to +$0 | -$3 | -$6 | +$2 / -$6 |
| exclusions_2plus: buy YES 10-90c | 504 | 1780 (631) | 37c | -$7 | -$10 | -$17 to -$3 | -$12 | -$16 | -$14 / -$5 |
| exclusions_2plus: buy NO 10-90c | 499 | 1749 (1122) | 63c | +$0 | -$1 | -$5 to +$3 | -$3 | -$6 | +$2 / -$4 |
| date_gap: buy YES 10-90c | 126 | 373 (135) | 34c | +$2 | -$0 | -$12 to +$11 | -$3 | -$8 | +$0 / -$1 |
| date_gap: buy NO 10-90c | 126 | 368 (233) | 66c | -$5 | -$7 | -$13 to -$1 | -$8 | -$11 | -$7 / -$6 |
| long_rules: buy YES 10-90c | 485 | 2073 (755) | 38c | -$7 | -$9 | -$15 to -$4 | -$11 | -$16 | -$21 / +$2 |
| long_rules: buy NO 10-90c | 480 | 2040 (1289) | 62c | -$0 | -$2 | -$5 to +$2 | -$3 | -$6 | +$5 / -$8 |
| tricky_3plus: buy YES 10-90c | 831 | 3006 (1226) | 41c | -$3 | -$5 | -$9 to -$1 | -$7 | -$11 | -$11 / +$0 |
| tricky_3plus: buy NO 10-90c | 827 | 2974 (1753) | 59c | -$3 | -$4 | -$7 to -$1 | -$6 | -$9 | -$0 / -$8 |
| named_site: buy YES 10-90c | 1192 | 4650 (1635) | 37c | -$8 | -$10 | -$13 to -$8 | -$13 | -$17 | -$15 / -$6 |
| named_site: buy NO 10-90c | 1186 | 4604 (2975) | 63c | -$0 | -$2 | -$3 to +$0 | -$3 | -$6 | +$1 / -$4 |
| fifty_fifty: buy YES 10-90c | 23 | 66 (36) | 46c | +$15 | +$13 | -$14 to +$39 | +$10 | +$6 | +$17 / +$9 |
| fifty_fifty: buy NO 10-90c | 23 | 66 (30) | 54c | -$19 | -$20 | -$43 to +$3 | -$21 | -$24 | -$28 / -$16 |
| plain: buy YES 10-90c | 242 | 765 (276) | 38c | -$9 | -$11 | -$17 to -$5 | -$13 | -$17 | -$19 / -$4 |
| plain: buy NO 10-90c | 241 | 759 (485) | 62c | +$1 | -$1 | -$5 to +$3 | -$2 | -$5 | +$4 / -$5 |

### 7-30 days before the end: flagged vs look-alikes (buy NO, same band 10-90c, +2c)

| Flag | Events | Flagged | Not flagged | Difference (90% band) |
|---|---|---|---|---|
| official, buy NO | 1404 | -$4.1 | -$0.9 | -$3.3 (-$6.2 to -$0.3) |
| announce, buy NO | 543 | -$3.4 | -$3.0 | -$0.4 (-$4.1 to +$3.3) |
| intent_not_enough, buy NO | 94 | -$15.6 | -$2.6 | -$13.0 (-$23.7 to -$2.3) |
| consensus, buy NO | 1236 | -$4.4 | -$1.4 | -$3.0 (-$5.8 to -$0.2) |
| discretion, buy NO | 613 | -$1.9 | -$3.6 | +$1.7 (-$1.2 to +$4.7) |
| exclusions_2plus, buy NO | 499 | -$1.3 | -$3.5 | +$2.2 (-$2.2 to +$6.7) |
| date_gap, buy NO | 126 | -$6.8 | -$2.9 | -$4.0 (-$10.5 to +$2.5) |
| long_rules, buy NO | 480 | -$1.6 | -$3.5 | +$1.9 (-$1.9 to +$5.7) |
| tricky_3plus, buy NO | 827 | -$4.3 | -$2.4 | -$1.8 (-$5.1 to +$1.4) |
| named_site, buy NO **<-** | 1186 | -$1.6 | -$5.0 | +$3.4 (+$0.4 to +$6.4) |
| fifty_fifty, buy NO | 23 | -$20.0 | -$2.9 | -$17.1 (-$40.0 to +$5.7) |
| official, buy YES **<-** | 1409 | -$5.8 | -$11.8 | +$6.0 (+$1.1 to +$11.0) |
| announce, buy YES | 545 | -$6.8 | -$7.7 | +$0.8 (-$4.5 to +$6.1) |
| intent_not_enough, buy YES **<-** | 95 | +$10.5 | -$8.3 | +$18.7 (+$6.2 to +$31.2) |
| consensus, buy YES **<-** | 1242 | -$5.2 | -$10.8 | +$5.6 (+$1.1 to +$10.0) |
| discretion, buy YES | 617 | -$9.9 | -$6.5 | -$3.4 (-$8.3 to +$1.5) |
| exclusions_2plus, buy YES | 504 | -$9.6 | -$6.9 | -$2.7 (-$9.9 to +$4.5) |
| date_gap, buy YES | 126 | -$0.4 | -$7.8 | +$7.3 (-$4.4 to +$19.0) |
| long_rules, buy YES | 485 | -$9.2 | -$6.9 | -$2.3 (-$8.4 to +$3.7) |
| tricky_3plus, buy YES | 831 | -$5.0 | -$8.9 | +$3.9 (-$0.9 to +$8.6) |
| named_site, buy YES | 1192 | -$10.4 | -$4.2 | -$6.2 (-$10.5 to -$1.8) |
| fifty_fifty, buy YES | 23 | +$12.5 | -$7.7 | +$20.2 (-$6.8 to +$47.1) |

## 3. Tricky-rule markets: favorite vs long shot (all market shapes, 1-7 days out)

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| tricky_3plus: long shot 2-10c | 658 | 2208 (120) | 5c | -$8 | -$22 | -$40 to -$4 | -$32 | -$46 | -$34 / -$10 |
| tricky_3plus: long shot 10-25c | 495 | 1434 (305) | 17c | +$19 | +$13 | -$2 to +$27 | +$7 | -$3 | +$1 / +$24 |
| tricky_3plus: favorite 75-90c | 494 | 1434 (1122) | 83c | -$7 | -$9 | -$12 to -$5 | -$10 | -$12 | -$6 / -$11 |
| tricky_3plus: favorite 90-98c | 657 | 2210 (2088) | 95c | -$2 | -$3 | -$4 to -$1 | -$3 | -$4 | -$2 / -$3 |
| discretion: long shot 2-10c | 635 | 2298 (126) | 5c | -$13 | -$25 | -$38 to -$12 | -$34 | -$47 | -$29 / -$21 |
| discretion: long shot 10-25c | 599 | 1866 (378) | 17c | +$12 | +$6 | -$4 to +$16 | +$1 | -$9 | -$5 / +$17 |
| discretion: favorite 75-90c | 603 | 1867 (1486) | 83c | -$6 | -$7 | -$9 to -$5 | -$8 | -$10 | -$4 / -$10 |
| discretion: favorite 90-98c | 635 | 2307 (2178) | 95c | -$2 | -$2 | -$3 to -$1 | -$3 | -$4 | -$2 / -$3 |
| consensus: long shot 2-10c | 905 | 2909 (173) | 5c | -$1 | -$16 | -$31 to -$0 | -$26 | -$41 | -$21 / -$10 |
| consensus: long shot 10-25c | 694 | 1978 (371) | 17c | +$4 | -$1 | -$13 to +$10 | -$6 | -$15 | -$11 / +$9 |
| consensus: favorite 75-90c | 694 | 1973 (1594) | 83c | -$4 | -$5 | -$8 to -$3 | -$7 | -$9 | -$3 / -$8 |
| consensus: favorite 90-98c | 906 | 2914 (2739) | 95c | -$2 | -$3 | -$4 to -$2 | -$4 | -$4 | -$3 / -$3 |
| exclusions_2plus: long shot 2-10c | 460 | 1514 (70) | 5c | -$22 | -$33 | -$50 to -$17 | -$42 | -$54 | -$46 / -$21 |
| exclusions_2plus: long shot 10-25c | 338 | 854 (146) | 16c | -$2 | -$7 | -$22 to +$8 | -$12 | -$20 | -$32 / +$17 |
| exclusions_2plus: favorite 75-90c | 331 | 838 (694) | 84c | -$2 | -$4 | -$7 to -$0 | -$5 | -$7 | +$2 / -$9 |
| exclusions_2plus: favorite 90-98c | 463 | 1526 (1452) | 95c | -$1 | -$2 | -$3 to -$1 | -$2 | -$3 | -$1 / -$3 |
| date_gap: long shot 2-10c | 122 | 353 (26) | 5c | +$25 | +$7 | -$35 to +$49 | -$7 | -$26 | +$32 / -$18 |
| date_gap: long shot 10-25c | 89 | 189 (41) | 17c | +$21 | +$15 | -$18 to +$48 | +$9 | -$1 | +$0 / +$29 |
| date_gap: favorite 75-90c | 86 | 185 (144) | 83c | -$8 | -$9 | -$16 to -$1 | -$10 | -$12 | -$6 / -$11 |
| date_gap: favorite 90-98c | 121 | 356 (329) | 95c | -$4 | -$5 | -$8 to -$2 | -$5 | -$6 | -$6 / -$3 |
| plain: long shot 2-10c | 1360 | 3518 (162) | 5c | -$24 | -$35 | -$44 to -$26 | -$44 | -$55 | -$35 / -$35 |
| plain: long shot 10-25c | 1134 | 2165 (412) | 17c | +$1 | -$4 | -$11 to +$3 | -$9 | -$17 | -$1 / -$7 |
| plain: favorite 75-90c | 1127 | 2159 (1745) | 83c | -$5 | -$6 | -$7 to -$4 | -$7 | -$9 | -$6 / -$5 |
| plain: favorite 90-98c | 1358 | 3501 (3331) | 95c | -$1 | -$2 | -$3 to -$1 | -$3 | -$3 | -$2 / -$2 |

## 4. Hindsight: how wrong was the price in markets that later got disputed or clarified?

Not a rule (you only know afterwards). It shows the most a perfect trouble-spotter could have earned.

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| disputed 1-3d: long shot 2-25c **<-** | 92 | 158 (40) | 10c | +$127 | +$108 | +$52 to +$164 | +$92 | +$67 | +$123 / +$93 |
| disputed 1-3d: favorite 75-98c | 92 | 157 (118) | 90c | -$17 | -$18 | -$26 to -$11 | -$19 | -$20 | -$22 / -$15 |
| disputed 1-3d: buy NO 10-90c | 98 | 190 (108) | 60c | -$7 | -$9 | -$21 to +$4 | -$10 | -$13 | -$3 / -$14 |
| disputed 7-30d: long shot 2-25c **<-** | 109 | 217 (61) | 11c | +$128 | +$111 | +$56 to +$165 | +$96 | +$71 | +$77 / +$148 |
| disputed 7-30d: favorite 75-98c | 109 | 218 (157) | 89c | -$20 | -$21 | -$29 to -$13 | -$21 | -$23 | -$17 / -$25 |
| disputed 7-30d: buy NO 10-90c | 110 | 244 (123) | 59c | -$17 | -$18 | -$30 to -$7 | -$20 | -$22 | -$13 / -$24 |
| clarified 1-3d: long shot 2-25c | 0 | | | | | | | | |
| clarified 1-3d: favorite 75-98c | 0 | | | | | | | | |
| clarified 1-3d: buy NO 10-90c | 0 | | | | | | | | |
| clarified 7-30d: long shot 2-25c | 0 | | | | | | | | |
| clarified 7-30d: favorite 75-98c | 0 | | | | | | | | |
| clarified 7-30d: buy NO 10-90c | 0 | | | | | | | | |
| second proposal 1-3d: long shot 2-25c | 965 | 3092 (351) | 9c | +$5 | -$4 | -$14 to +$6 | -$12 | -$24 | -$2 / -$6 |
| second proposal 1-3d: favorite 75-98c | 967 | 3096 (2742) | 90c | -$3 | -$4 | -$6 to -$3 | -$5 | -$6 | -$5 / -$4 |
| second proposal 1-3d: buy NO 10-90c | 832 | 2579 (1463) | 57c | -$4 | -$6 | -$8 to -$3 | -$7 | -$10 | -$7 / -$4 |
| second proposal 7-30d: long shot 2-25c | 837 | 2904 (387) | 10c | +$16 | +$6 | -$5 to +$17 | -$2 | -$15 | +$11 / +$1 |
| second proposal 7-30d: favorite 75-98c | 839 | 2907 (2513) | 90c | -$5 | -$6 | -$7 to -$4 | -$7 | -$8 | -$7 / -$5 |
| second proposal 7-30d: buy NO 10-90c | 769 | 2633 (1499) | 59c | -$6 | -$7 | -$10 to -$5 | -$9 | -$12 | -$6 / -$9 |

## 5. Limbo: after the end date, still waiting for the result

Price 1, 3 or 7 days AFTER the end date, market not settled yet. Is the leader right?

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| 1d after end: long shot 2-10c | 364 | 502 (36) | 5c | +$22 | +$4 | -$27 to +$35 | -$9 | -$28 | -$16 / +$23 |
|   ...of them later disputed | 24 | 27 (4) | 5c | +$158 | +$119 | -$48 to +$287 | +$91 | +$51 | +$254 / +$2 |
| 1d after end: long shot 10-30c | 240 | 380 (93) | 19c | +$23 | +$17 | -$3 to +$36 | +$11 | +$2 | +$3 / +$31 |
|   ...of them later disputed | 28 | 33 (12) | 19c | +$82 | +$73 | +$9 to +$137 | +$65 | +$51 | +$29 / +$109 |
| 1d after end: leader 70-90c | 236 | 376 (284) | 81c | -$8 | -$9 | -$14 to -$4 | -$11 | -$13 | -$6 / -$13 |
|   ...of them later disputed | 28 | 33 (21) | 81c | -$23 | -$24 | -$40 to -$7 | -$25 | -$26 | -$12 / -$35 |
| 1d after end: leader 90-98c | 360 | 500 (463) | 95c | -$4 | -$5 | -$7 to -$2 | -$5 | -$6 | -$3 / -$6 |
|   ...of them later disputed | 23 | 26 (22) | 95c | -$12 | -$13 | -$25 to -$1 | -$13 | -$14 | -$21 / -$5 |
| 3d after end: long shot 2-10c | 122 | 166 (5) | 4c | -$45 | -$54 | -$88 to -$20 | -$60 | -$69 | -$64 / -$43 |
|   ...of them later disputed | 9 | 10 (1) | 4c | +$91 | +$60 | -$218 to +$338 | +$38 | +$8 | -$100 / +$233 |
| 3d after end: long shot 10-30c | 82 | 127 (33) | 19c | +$26 | +$20 | -$13 to +$52 | +$14 | +$5 | +$39 / +$1 |
|   ...of them later disputed | 13 | 15 (5) | 18c | +$74 | +$66 | -$41 to +$173 | +$58 | +$44 | +$55 / +$74 |
| 3d after end: leader 70-90c | 83 | 129 (96) | 81c | -$9 | -$10 | -$19 to -$2 | -$11 | -$13 | -$15 / -$6 |
|   ...of them later disputed | 13 | 15 (10) | 82c | -$20 | -$21 | -$47 to +$5 | -$22 | -$24 | -$17 / -$24 |
| 3d after end: leader 90-98c | 120 | 163 (158) | 96c | +$0 | -$1 | -$3 to +$2 | -$1 | -$2 | +$0 / -$1 |
|   ...of them later disputed | 9 | 10 (9) | 96c | -$7 | -$8 | -$25 to +$10 | -$8 | -$8 | +$3 / -$18 |
| 7d after end: long shot 2-10c | 63 | 84 (3) | 5c | -$38 | -$48 | -$109 to +$14 | -$54 | -$64 | -$65 / -$30 |
|   ...of them later disputed | 3 | 3 (0) | 4c | -$100 | -$100 | -$100 to -$100 | -$100 | -$100 |  /  |
| 7d after end: long shot 10-30c | 55 | 80 (19) | 20c | +$11 | +$6 | -$36 to +$48 | +$1 | -$7 | -$23 / +$35 |
|   ...of them later disputed | 6 | 8 (4) | 21c | +$122 | +$112 | -$41 to +$265 | +$104 | +$88 | +$117 / +$108 |
| 7d after end: leader 70-90c | 55 | 82 (62) | 80c | -$7 | -$8 | -$19 to +$3 | -$9 | -$11 | -$2 / -$13 |
|   ...of them later disputed | 6 | 8 (4) | 79c | -$37 | -$38 | -$79 to +$3 | -$39 | -$40 | -$38 / -$38 |
| 7d after end: leader 90-98c | 63 | 83 (80) | 95c | -$0 | -$1 | -$5 to +$3 | -$1 | -$2 | +$0 / -$2 |
|   ...of them later disputed | 3 | 3 (3) | 96c | +$3 | +$2 | +$1 to +$3 | +$1 | +$1 |  /  |

## 6. Follow-ups

### 6a. Trouble score (how many of the 7 dispute-predicting flags) vs disputes

| Flags | Markets | Disputed per 1,000 |
|---|---|---|
| 0 | 111,161 | 0.4 |
| 1 | 2,977 | 23.2 |
| 2 | 5,548 | 18.9 |
| 3 | 2,688 | 29.0 |
| 4+ | 1,886 | 51.4 |

### 6b. Long shot 10-30c, by trouble score (same topic mix is NOT controlled here; see 6c)

| Slice | Events | Bets (won) | Avg price | +1c | +2c | 90% band at +2c | +3c | +5c | 1st half / 2nd half (+2c) |
|---|---|---|---|---|---|---|---|---|---|
| 1-3d before, score 0: long shot 10-30c | 1434 | 3250 (683) | 19c | +$0 | -$5 | -$10 to +$1 | -$9 | -$16 | -$3 / -$6 |
| 1-3d before, score 1: long shot 10-30c | 211 | 419 (77) | 19c | -$9 | -$14 | -$31 to +$4 | -$18 | -$24 | +$11 / -$37 |
| 1-3d before, score 2-3: long shot 10-30c | 689 | 1632 (348) | 19c | +$3 | -$2 | -$12 to +$9 | -$6 | -$14 | -$12 / +$8 |
| 1-3d before, score 4-9: long shot 10-30c | 134 | 315 (73) | 18c | +$20 | +$14 | -$11 to +$39 | +$9 | -$1 | +$12 / +$16 |
| 7-30d before, score 0: long shot 10-30c | 368 | 1014 (173) | 17c | -$10 | -$14 | -$24 to -$5 | -$19 | -$26 | -$21 / -$8 |
| 7-30d before, score 1: long shot 10-30c | 273 | 667 (125) | 19c | -$8 | -$12 | -$26 to +$2 | -$16 | -$23 | -$14 / -$11 |
| 7-30d before, score 2-3: long shot 10-30c | 958 | 2832 (583) | 19c | +$1 | -$4 | -$12 to +$5 | -$8 | -$16 | -$11 / +$3 |
| 7-30d before, score 4-9: long shot 10-30c | 276 | 707 (131) | 18c | -$2 | -$7 | -$22 to +$8 | -$11 | -$19 | +$0 / -$14 |
| 1-3d after end (limbo), score 0: long shot 10-30c | 22 | 37 (8) | 21c | -$2 | -$6 | -$61 to +$49 | -$10 | -$17 | +$30 / -$36 |
| 1-3d after end (limbo), score 1: long shot 10-30c | 32 | 56 (12) | 19c | +$3 | -$2 | -$55 to +$52 | -$6 | -$14 | +$11 / -$15 |
| 1-3d after end (limbo), score 2-3: long shot 10-30c | 184 | 362 (90) | 18c | +$26 | +$20 | -$4 to +$43 | +$14 | +$4 | +$17 / +$22 |
| 1-3d after end (limbo), score 4-9: long shot 10-30c | 25 | 52 (16) | 20c | +$47 | +$40 | -$16 to +$96 | +$34 | +$23 | +$9 / +$69 |

### 6c. Same, flagged (score 2+) vs unflagged in the SAME topic, long shot 10-30c, +2c

| Topic / time | Events | Flagged | Not flagged | Difference (90% band) |
|---|---|---|---|---|
| mentions, 1-3d | 7 | -$14.8 | -$73.1 | +$58.4 (+$7.7 to +$109.0) |
| entertainment, 1-3d | 7 | -$2.1 | -$6.8 | +$4.6 (-$102.0 to +$111.3) |
| apps/tech, 1-3d **<-** | 42 | +$30.2 | -$56.3 | +$86.5 (+$16.0 to +$157.0) |
| other, 1-3d | 382 | -$15.5 | -$27.1 | +$11.6 (-$18.3 to +$41.4) |
| economics, 7-30d | 37 | +$62.4 | +$98.3 | -$35.8 (-$189.0 to +$117.4) |
| entertainment, 7-30d | 23 | -$27.0 | +$3.2 | -$30.2 (-$78.2 to +$17.8) |
| apps/tech, 7-30d **<-** | 75 | +$21.5 | -$41.7 | +$63.2 (+$20.1 to +$106.3) |
| other, 7-30d | 651 | -$11.3 | -$3.8 | -$7.4 (-$30.3 to +$15.4) |
| other, limbo | 71 | +$7.7 | -$36.9 | +$44.6 (-$25.9 to +$115.2) |

### 6d. The one pass: 'rules name a date the title doesn't', buy YES 1-3 days out

By topic (+2c):

| Topic | Events | Per $100 |
|---|---|---|
| apps/tech | 10 | +$54.0 |
| elections | 2 | -$23.4 |
| geopolitics | 11 | -$1.3 |
| mentions | 5 | +$43.7 |
| other | 59 | +$17.1 |

Every event (first market shown, price, won?):

- 2026-02-26 Will Trump say "Transgender" this week? (March 1) | 33c | WON | 1 bets | rule dates [('Feb', '23'), ('Mar', '1')]
- 2026-02-28 Will there be exactly 0 earthquakes of magnitude 6.5 or higher worldwide by March 1? | 80c | WON | 4 bets | rule dates [('Feb', '23'), ('Mar', '1'), ('Apr', '30')]
- 2026-03-19 Will Crude Oil (CL) hit (HIGH) $105 by March 20? | 24c | lost | 1 bets | rule dates [('Mar', '16'), ('Mar', '20')]
- 2026-03-22 Will 30-34 ships transit the Strait of Hormuz between March 17-23? | 14c | lost | 7 bets | rule dates [('Mar', '17'), ('Mar', '23'), ('Mar', '23')]
- 2026-03-26 Will there be exactly 1 earthquake of magnitude 6.5 or higher worldwide by March 29? | 60c | lost | 4 bets | rule dates [('Mar', '23'), ('Mar', '29'), ('Apr', '30')]
- 2026-03-26 Will Trump say "Minnesota" or "Minneapolis" this week? (March 29) | 66c | WON | 8 bets | rule dates [('Mar', '23'), ('Mar', '29')]
- 2026-03-28 Will Jeff Bezos be 2nd richest person on March 31? | 12c | lost | 2 bets | rule dates [('Mar', '31'), ('Mar', '31'), ('Apr', '2')]
- 2026-03-28 Will the DHS shutdown end between March 24-27, 2026? | 33c | lost | 3 bets | rule dates [('Feb', '14')]
- 2026-03-28 Will there be between 0 and 10 average daily transits of the Strait of Hormuz on March 31? | 88c | WON | 1 bets | rule dates [('Mar', '31'), ('Mar', '31'), ('Mar', '31'), ('Apr', '14')]
- 2026-03-29 Ansem mindshare all time high by March 31? | 19c | lost | 2 bets | rule dates [('Nov', '19')]
- 2026-03-30 Will the 10-year treasury yield hit 4.5% by March 31? | 20c | lost | 2 bets | rule dates [('Dec', '9'), ('Mar', '31')]
- 2026-03-30 Will Jeff Bezos be 3rd richest person on March 31? | 48c | WON | 4 bets | rule dates [('Mar', '31'), ('Mar', '31'), ('Apr', '2')]
- 2026-03-30 Will the U.S. invade Iran by March 31? | 10c | lost | 2 bets | rule dates [('Mar', '31'), ('Nov', '4')]
- 2026-03-30 Ukraine strikes another tanker in Black Sea by March 31, 2026? | 40c | WON | 2 bets | rule dates [('Dec', '10'), ('Dec', '2')]
- 2026-04-11 Will there be exactly 3 earthquakes of magnitude 5.5 or higher worldwide by April 5? | 32c | WON | 2 bets | rule dates [('Apr', '6'), ('Apr', '12'), ('May', '31')]
- 2026-04-11 Will the total number of TSA passengers for April 6 - April 12 be between 17,500,000 and 1 | 66c | WON | 2 bets | rule dates [('Apr', '6'), ('Apr', '12'), ('Dec', '1'), ('Dec', '2')]
- 2026-04-11 Will there be exactly 0 earthquakes of magnitude 6.5 or higher worldwide from April 6 - 12 | 74c | WON | 3 bets | rule dates [('Apr', '6'), ('Apr', '12'), ('May', '31')]
- 2026-04-11 Trump announces US x Iran ceasefire end by April 12, 2026? | 10c | lost | 3 bets | rule dates [('Apr', '7')]
- 2026-04-11 Will 10 ships transit the Strait of Hormuz on any day April 8–12? | 64c | WON | 2 bets | rule dates [('Apr', '8'), ('Apr', '12'), ('Apr', '12')]
- 2026-04-13 Will Trump announce that the US x Iran ceasefire has been broken by April 14, 2026? | 22c | lost | 2 bets | rule dates [('Apr', '7')]
- 2026-04-16 Will Trump say "Barack Hussein Obama" this week? (April 19) | 59c | WON | 2 bets | rule dates [('Apr', '13'), ('Apr', '19')]
- 2026-04-18 Will there be exactly 0 earthquakes of magnitude 6.5 or higher worldwide from April 13 - 1 | 78c | WON | 2 bets | rule dates [('Apr', '13'), ('Apr', '19'), ('May', '31')]
- 2026-04-18 Will there be more than 9 earthquakes of magnitude 5.5 or higher worldwide from April 13 - | 20c | WON | 2 bets | rule dates [('Apr', '13'), ('Apr', '19'), ('May', '31')]
- 2026-04-20 US x Iran ceasefire extended by April 21, 2026? | 70c | lost | 1 bets | rule dates [('Apr', '7'), ('Apr', '7')]
- 2026-04-21 US x Iran permanent peace deal by April 22, 2026? | 14c | lost | 5 bets | rule dates [('Apr', '7')]
- 2026-04-22 Will Donald Trump announce that the United States blockade of the Strait of Hormuz has bee | 18c | lost | 4 bets | rule dates [('Apr', '12')]
- 2026-04-25 Will Trump say "Crypto" or "Bitcoin" this week? (April 20 - 26) | 70c | WON | 2 bets | rule dates [('Apr', '20'), ('Apr', '26')]
- 2026-04-27 Will the Silicon Data H100 Index (SDH100RT) hit $2.75 (HIGH) by April 30, 2026? | 10c | lost | 1 bets | rule dates [('Feb', '2'), ('Apr', '30'), ('Apr', '30'), ('Apr', '30')]
- 2026-04-27 Will there be between 0 and 10 average daily transits of the Strait of Hormuz on April 30? | 86c | WON | 1 bets | rule dates [('Apr', '30'), ('May', '14'), ('Apr', '30'), ('Apr', '30')]
- 2026-04-27 Steve Bannon exonerated by April 30? | 10c | lost | 1 bets | rule dates [('Apr', '6')]
- 2026-04-29 Will the DHS shutdown end between April 29-30, 2026? | 10c | WON | 3 bets | rule dates [('Feb', '14')]
- 2026-04-29 Will a Claude Mythos model be released by June 30, 2026? | 21c | WON | 2 bets | rule dates [('Mar', '26')]
- 2026-05-02 Will there be 3 or fewer earthquakes of magnitude 5.5 or higher worldwide from April 27 -  | 29c | WON | 2 bets | rule dates [('Apr', '27'), ('May', '3'), ('May', '31')]
- 2026-05-07 Will the next US x Iran diplomatic meeting occur after May 10? | 84c | WON | 1 bets | rule dates [('May', '10'), ('May', '11')]
- 2026-05-07 Will there be more than 9 earthquakes of magnitude 5.5 or higher worldwide from May 4 - 10 | 56c | WON | 1 bets | rule dates [('May', '4'), ('May', '10'), ('May', '31')]
- 2026-05-14 Will there be exactly 0 earthquakes of magnitude 6.5 or higher worldwide from May 11 - 17? | 58c | lost | 1 bets | rule dates [('May', '11'), ('May', '17'), ('Jun', '30')]
- 2026-05-15 Iran closes its airspace by May 18? | 10c | lost | 6 bets | rule dates [('Jan', '27'), ('Jan', '25'), ('Apr', '25')]
- 2026-05-16 Will there be exactly 4 earthquakes of magnitude 5.5 or higher worldwide from May 11 - 17? | 11c | lost | 3 bets | rule dates [('May', '11'), ('May', '17'), ('May', '31')]
- 2026-05-23 Will there be more than 9 earthquakes of magnitude 5.5 or higher worldwide from May 18 - 2 | 78c | WON | 2 bets | rule dates [('May', '18'), ('May', '24'), ('Jun', '30')]
- 2026-05-28 Iran agrees to unrestricted shipping through Hormuz by May 31? | 18c | lost | 1 bets | rule dates [('May', '31'), ('Feb', '28')]
- 2026-05-29 US announces new Iran agreement/ceasefire extension by May 31? | 29c | lost | 6 bets | rule dates [('Apr', '21')]
- 2026-05-30 Will there be between 0 and 10 average daily transits of the Strait of Hormuz on May 31? | 88c | WON | 3 bets | rule dates [('May', '31'), ('Jun', '14'), ('May', '31'), ('May', '31')]
- 2026-05-30 Israel announces Lebanon ceasefire extension by May 31? | 14c | lost | 2 bets | rule dates [('Apr', '16'), ('Apr', '16'), ('Apr', '23'), ('May', '15')]
- 2026-06-01 Will both candidates advancing to the general election for Governor of California from the | 24c | lost | 4 bets | rule dates [('Jun', '2'), ('Dec', '31')]
- 2026-06-02 Will the People Power Party win 2 seats in South Korea’s June 3, 2026 parliamentary by-ele | 30c | lost | 2 bets | rule dates [('Jun', '3'), ('Jun', '3'), ('Jun', '3'), ('Dec', '31')]
- 2026-06-07 Will there be 5 or fewer earthquakes of magnitude 5.5 or higher worldwide from June 1 - 7? | 87c | lost | 2 bets | rule dates [('Jun', '1'), ('Jun', '7'), ('Jun', '30')]
- 2026-06-11 Will Iran close its airspace by June 11? | 18c | lost | 2 bets | rule dates [('Jun', '9'), ('Jan', '27'), ('Jan', '25'), ('Apr', '25')]
- 2026-06-17 Will the text of the US-Iran agreement be released by June 17? | 30c | WON | 2 bets | rule dates [('Jun', '14'), ('Jun', '19'), ('Jun', '14'), ('Jun', '14')]
- 2026-06-19 Will Claude Fable 5 be restored for US customers by June 22? | 25c | lost | 5 bets | rule dates [('Jun', '9'), ('Jun', '12'), ('Jun', '9'), ('Jun', '9')]
- 2026-06-28 Iran full airspace closure by June 30? | 13c | lost | 3 bets | rule dates [('Feb', '28'), ('Jan', '27'), ('Jan', '25'), ('Apr', '25')]
- 2026-06-28 Will Anthropic’s valuation hit (HIGH) $1.1T by June 30? | 10c | WON | 1 bets | rule dates [('Jun', '30'), ('Jul', '1'), ('Jul', '4')]
- 2026-06-29 Will there be exactly 10 earthquakes of magnitude 7.0 or higher worldwide by June 30? | 88c | WON | 3 bets | rule dates [('Dec', '4'), ('Jun', '30'), ('Jul', '7')]
- 2026-06-29 Will Claude Mythos 5 be restored for US customers by June 30? | 27c | WON | 2 bets | rule dates [('Jun', '12')]
- 2026-06-30 Will the US government rescind its ban on all foreign use of Claude Fable 5 by June 30? | 14c | WON | 2 bets | rule dates [('Jun', '12')]
- 2026-07-01 US x Iran diplomatic meeting by July 3, 2026? | 14c | lost | 1 bets | rule dates [('Jun', '22'), ('Jun', '22')]
- 2026-07-11 Will Anthropic extend Claude Fable 5 paid-plan access again by July 12? | 28c | WON | 2 bets | rule dates [('Jul', '7'), ('Jul', '12'), ('Jul', '12')]
- 2026-07-12 Israeli parliament dissolved by July 15? | 15c | lost | 1 bets | rule dates [('Jan', '27'), ('Jul', '15')]
- 2026-07-12 0 ships transit Hormuz on any date by July 14? | 10c | lost | 1 bets | rule dates [('Jun', '26')]
- 2026-07-14 Will Iran announce withdrawal from MOU negotiations by July 17? | 11c | lost | 1 bets | rule dates [('Jun', '14'), ('Jun', '14')]
- 2026-07-16 Will Anthropic extend Claude Fable 5 paid-plan access again by July 19? | 60c | WON | 1 bets | rule dates [('Jul', '12'), ('Jul', '19'), ('Jul', '19')]
- 2026-07-17 Will Anthropic remove paid plan access for Fable 5 by July 19, 2026? | 10c | lost | 1 bets | rule dates [('Jul', '12'), ('Jul', '19')]
- 2026-07-18 NYC Air Quality Index below 100 by July 21? | 88c | WON | 1 bets | rule dates [('Jul', '17')]
- 2026-07-28 Ukraine strikes another tanker in the Caspian Sea by July 31, 2026? | 23c | lost | 1 bets | rule dates [('Jul', '25')]
- 2026-07-29 US announces end of Iranian blockade by July 31, 2026? | 12c | lost | 6 bets | rule dates [('Jul', '13')]
- 2026-07-29 Will Databricks' valuation hit (HIGH) $180B by July 31? | 25c | lost | 1 bets | rule dates [('Jul', '31'), ('Aug', '1'), ('Aug', '4')]
- 2026-07-31 Israel x Hamas Ceasefire Phase II by July 31? | 34c | lost | 1 bets | rule dates [('Oct', '8'), ('Jul', '31')]
- 2026-08-03 Will 3 Sanders endorsees win August 4 primaries? | 72c | WON | 2 bets | rule dates [('Aug', '4'), ('Nov', '2')]
- 2026-08-04 Israel agrees to Board of Peace Gaza plan by August 7? | 22c | lost | 1 bets | rule dates [('Jul', '30')]
- 2026-08-12 Will Kai and Speed beat the Minecraft challenge by August 15? | 16c | WON | 1 bets | rule dates [('Aug', '7')]
- 2026-08-22 Will there be more than 13 earthquakes of magnitude 5.5 or higher worldwide from August 17 | 82c | WON | 2 bets | rule dates [('Aug', '17'), ('Aug', '23'), ('Aug', '25')]
- 2026-08-27 Will Warsh say "Bitcoin" or "Crypto" or "Cryptocurrency" during Jackson Hole speech on Aug | 18c | lost | 2 bets | rule dates [('Aug', '28'), ('Aug', '29')]
- 2026-08-30 Next Mythos-Class Model released by August 31, 2026? | 28c | lost | 5 bets | rule dates [('Jun', '9')]
- 2026-09-02 Will OpenAI’s Astra model be released by September 3, 2026? | 82c | lost | 2 bets | rule dates [('Aug', '1')]
- 2026-09-03 Lacy and Marlon beat gaming challenge by September 3, 2026, 11:59 PM ET? | 23c | lost | 7 bets | rule dates [('Sep', '1')]
- 2026-09-03 Will OpenAI's Astra model be released on September 4, 2026? | 36c | WON | 1 bets | rule dates [('Aug', '1')]
- 2026-09-21 Will the next Claude Opus model be released on September 21, 2026? | 34c | lost | 5 bets | rule dates [('Jul', '24')]
- 2026-09-27 Next Muse Spark (1.4+) released by September 30, 2026? | 10c | lost | 1 bets | rule dates [('Sep', '2')]
- 2026-09-27 Next US-Iran senior diplomatic meeting by September 30, 2026? | 20c | lost | 1 bets | rule dates [('Sep', '22')]
- 2026-09-28 Saudi Oil Pipeline (East-West) restarts by September 30? | 17c | lost | 1 bets | rule dates [('Sep', '11')]
- 2026-09-30 Will OpenAI resume US ChatGPT Pro signups by September 30, 2026? | 34c | WON | 2 bets | rule dates [('Sep', '10')]
- 2026-10-07 Will Jynxzi, Ron and Los beat the Minecraft challenge by October 7? | 12c | lost | 4 bets | rule dates [('Oct', '5')]
- 2026-10-13 Will Gemini Argon be released on October 13, 2026? | 66c | WON | 2 bets | rule dates [('Sep', '30')]
- 2026-10-18 Will OpenAI not announce that it has resumed training by October 20, 2026? | 82c | WON | 1 bets | rule dates [('Sep', '25'), ('Sep', '25'), ('Oct', '20'), ('Oct', '20')]
- 2026-10-29 Republican Senate odds hit 40% by October 31? | 11c | lost | 2 bets | rule dates [('Nov', '1'), ('Nov', '1'), ('Nov', '1')]
- 2026-10-29 Republican House odds dip to 7% by October 31? | 23c | WON | 1 bets | rule dates [('Nov', '1'), ('Nov', '1'), ('Nov', '1')]
- 2026-10-30 Jon Ossoff Democratic nomination odds leader on October 31? | 30c | lost | 5 bets | rule dates [('Oct', '31'), ('Nov', '7')]
- 2026-11-02 Turek flips Hinson for Iowa Senate by November 2? | 13c | WON | 2 bets | rule dates [('Nov', '3'), ('Nov', '3'), ('Nov', '3')]

## Samples (to check the word filters by eye)

**intent_not_enough**:

- Will Iran announce withdrawal from MOU negotiations by July 10?
- Israel x Iran ceasefire continues through July 31?
- KRG declares independence from Iraq by April 30?
- Israel military action against Lebanon on September 6?
- Will Hibachi launch a token by September 30, 2026?
- Will Donald Trump announce that the United States blockade of the Strait of Hormuz has been lifted by June 15,

**discretion**:

- Microsoft (MSFT) Up or Down on April 13?
- Will Elon Musk post 240-259 tweets from April 3 to April 10, 2026?
- Will the Freedom Movement (GS) win <25 seats in the Slovenian National Assembly in this election?
- Will Elon Musk post 320-339 tweets from July 17 to July 24, 2026?
- Will Elon Musk post 80-99 tweets from September 15 to September 22, 2026?
- Will Choo Kyung-ho win the 2026 Daegu mayoral election by less than 10%?

**date_gap**:

- Will the US next strike Iran on March 8, 2026 (ET)?
- Will Israel announce the ceasefire has been extended by May 15?
- Ethereum Up or Down on September 3?
- Ethereum Up or Down on September 10?
- Will Anthropic’s valuation hit (HIGH) $1.1T by June 30?
- Bitcoin Up or Down on June 9?

**tricky_3plus**:

- US x Iran diplomatic meeting by June 13, 2026? 
- Houthi military action against Israel by April 15, 2026?
- Will José Luna win the 2026 Peruvian presidential election?
- Will Michael Olise record the most assists in the 2025-26 UEFA Champions League?
- Will the Slovenian Democratic Party (SDS) win 30-34 seats in the Slovenian National Assembly in this election?
- Will Hanrapetutyun Party win the most seats in the 2026 Armenian National Assembly election?

**disputed**:

- Will the Iran ceasefire continue through May 25? (final [0.0, 1.0])
- Military action against Iran ends by April 17, 2026? (final [1.0, 0.0])
- Will the Fed Pause–Pause–Cut in the next three decisions (Jan–Mar–Apr)? (final [0.0, 1.0])
- Will Trump speak to Reza Pahlavi in May? (final [0.0, 1.0])
- Will Donald Trump announce that the United States blockade of the Strait of Hormuz has been lifted by May 31,  (final [0.0, 1.0])
- US x Iran Effective Ceasefire by September 4? (final [1.0, 0.0])
- Will Cristiano Ronaldo win the 2026 Ballon d'Or? (final [0.0, 1.0])
- Will Rafael Belaúnde Llosa win the 2026 Peruvian presidential election? (final [0.0, 1.0])
- Will Russell 2000 (RUT) hit 2600 (HIGH) in March? (final [0.0, 1.0])
- Will Trump praise Bryson DeChambeau in August? (final [1.0, 0.0])
- Will Iván Cepeda Castro win the 1st round of the 2026 Colombian presidential election? (final [0.0, 1.0])
- Will Trump meet with Javier Milei in September 2026? (final [1.0, 0.0])
- Iran closes its airspace by June 15? (final [1.0, 0.0])
- Over $7M committed to the P2P Protocol public sale? (final [1.0, 0.0])
- Will Trump say "Dumbocrat" during Bret Baier interview? (final [1.0, 0.0])

## Slices that passed the bar

- date_gap yes 1-3 days before the end: +$21 per $100 at +2c, band +$7 to +$35, 87 events, halves +$11 / +$31

About 204 rows were tested; at a 90% band roughly 10 pass by luck alone.
