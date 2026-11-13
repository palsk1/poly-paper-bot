# Mention markets vs each word's own record (mentions.py)

Generated 2026-11-13T10:20:50Z. Markets like "Will Trump say 'Tariff' during the rally?". 24228 finished markets in 1356 events, June 2024 to 9 November 2026 (the holdout from 2026-11-10 is not in here), 20488 of them with every real trade in 5-minute steps. Paper only.

**The idea.** The same words come back again and again ("Bitcoin", "Tariff", "Biden"...). For each word we keep score: how often did this speaker really say it in earlier markets? That record (pulled toward the speaker's average when there are few earlier markets) is the model's chance. It only ever uses markets that had finished before the bet.

**The test.** Walk each market's real trades. Where the last trade and the model are far apart, buy at the next 5-minute step that has trades. One bet per market, $10 each.

## 1. Who is the better forecaster?

| looks (first look per market, 1h+ after its first trade) | model miss | Polymarket miss |
|---|---|---|
| all (17874) | 0.2372 | 0.1998 |
| since April 2026 (9052) | 0.2288 | 0.1845 |
| word has 3+ earlier markets (6010) | 0.2166 | 0.1961 |

("Miss" = average squared distance between forecast and result, smaller is better.) Polymarket's price is the better forecast. So the word record alone is no crystal ball. The question is whether it helps on one side.

How often Yes really won, by Yes price at that first look:

| Yes price | markets | Yes won (all years) | markets since April 2026 | Yes won (since April 2026) |
|---|---|---|---|---|
| 3-10c | 1127 | 7 in 100 | 641 | 7 in 100 |
| 10-20c | 1671 | 14 in 100 | 880 | 14 in 100 |
| 20-35c | 2828 | 25 in 100 | 1498 | 26 in 100 |
| 35-50c | 2940 | 38 in 100 | 1430 | 38 in 100 |
| 50-65c | 3134 | 51 in 100 | 1490 | 55 in 100 |
| 65-80c | 2950 | 61 in 100 | 1319 | 67 in 100 |
| 80-90c | 1826 | 74 in 100 | 954 | 79 in 100 |
| 90-97c | 1263 | 86 in 100 | 749 | 89 in 100 |

Yes is priced too high almost everywhere, most of all when it looks likely (at 80-90c it won 74 in 100 over all years). That is the old `mention_no` lean. Since April 2026 the gap is much smaller.

## 2. Plain "always No" (no model): it paid for two years, then stopped

First look per market, Yes at 10-90c, buying No at the next real trade + 3c + fee.

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| 2024 Q2 | 25 | 3 | 12 | -$19.22 | -$19.41 | -$19.04 |
| 2024 Q3 | 744 | 71 | 438 | +$20.77 | +$34.13 | +$7.41 |
| 2024 Q4 | 828 | 55 | 471 | +$18.68 | +$4.85 | +$32.52 |
| 2025 Q1 | 654 | 49 | 416 | +$12.39 | +$16.13 | +$8.65 |
| 2025 Q2 | 774 | 64 | 426 | +$16.48 | +$5.25 | +$27.70 |
| 2025 Q3 | 867 | 78 | 462 | +$9.87 | +$7.84 | +$11.90 |
| 2025 Q4 | 1912 | 149 | 1061 | +$20.08 | +$23.62 | +$16.55 |
| 2026 Q1 | 2049 | 166 | 1192 | +$31.15 | +$42.16 | +$20.17 |
| 2026 Q2 | 3184 | 227 | 1712 | +$0.13 | +$4.23 | -$3.94 |
| 2026 Q3 | 3536 | 350 | 1925 | -$1.73 | -$0.10 | -$3.35 |
| 2026 Q4 | 947 | 104 | 453 | -$4.19 | -$14.26 | +$6.00 |
| **all** | 15520 | 1279 | 8568 | +$9.73 | +$20.16 | -$0.53 |
| always Yes instead, all | 15520 | 1279 | 6952 | -$16.72 | -$20.47 | -$13.03 |

So blind No made about $10-30 per $100 until March 2026 and has been flat to slightly behind since April. That is also when Polymarket began charging a fee on these markets, and more people (or bots) seem to have caught on. Our live `mention_no` track runs the blind version.

## 3. No only where the word's own record says Yes is too expensive

The rule: the word has 3+ earlier markets with this speaker, Yes trades 20c or more above the word's record, buy No. Costs: the worst price anyone paid in the next 5-minute step, + 3c, + fee. No must cost 10-90c, the gap must still be 10c+ at the price paid, and the bet is made at least 6 hours before the market's listed end.

### Since April 2026 (when blind No stopped paying)

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| **the rule** | 533 | 244 | 236 | +$15.25 | +$8.29 | +$22.18 |
| the rule if buying costs 1c, not 3c | 537 | 245 | 240 | +$22.16 | +$15.48 | +$28.82 |
| the rule if buying costs 5c | 523 | 243 | 229 | +$7.74 | +$0.91 | +$14.55 |
| the rule if buying costs 8c | 511 | 238 | 223 | -$0.08 | -$6.86 | +$6.67 |
| yardstick: same rule, but every word gets 40 in 100 | 985 | 304 | 302 | -$1.63 | +$3.98 | -$7.23 |
| yardstick: same rule, speaker's average instead of the word's record | 807 | 287 | 244 | +$2.22 | +$5.41 | -$0.96 |
| gap 10c+ instead of 20c+ | 848 | 299 | 403 | +$6.44 | +$2.69 | +$10.21 |
| gap 30c+ | 322 | 188 | 134 | +$15.53 | +$14.04 | +$17.03 |
| word needs only 1 earlier market | 775 | 301 | 351 | +$13.54 | +$14.56 | +$12.52 |
| word needs 6+ earlier markets | 363 | 193 | 158 | +$18.43 | +$15.62 | +$21.23 |
| the other way round: buy Yes where the record is 20c+ above the price | 553 | 233 | 191 | -$10.79 | -$0.14 | -$21.37 |

### June 2024 to March 2026

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| **the rule** | 363 | 184 | 166 | +$16.29 | +$17.70 | +$14.88 |
| the rule if buying costs 1c, not 3c | 369 | 186 | 170 | +$23.64 | +$24.69 | +$22.60 |
| the rule if buying costs 5c | 360 | 184 | 165 | +$10.13 | +$12.57 | +$7.70 |
| the rule if buying costs 8c | 350 | 179 | 158 | +$2.08 | +$5.12 | -$0.96 |
| yardstick: same rule, but every word gets 40 in 100 | 615 | 227 | 207 | +$12.86 | +$9.19 | +$16.52 |
| yardstick: same rule, speaker's average instead of the word's record | 499 | 214 | 154 | +$15.11 | +$7.34 | +$22.84 |
| gap 10c+ instead of 20c+ | 561 | 215 | 275 | +$14.22 | +$15.46 | +$12.99 |
| gap 30c+ | 231 | 147 | 107 | +$30.51 | +$48.64 | +$12.55 |
| word needs only 1 earlier market | 716 | 258 | 329 | +$17.80 | +$19.74 | +$15.86 |
| word needs 6+ earlier markets | 201 | 128 | 91 | +$15.97 | +$27.93 | +$4.12 |
| the other way round: buy Yes where the record is 20c+ above the price | 369 | 173 | 157 | +$2.22 | -$18.11 | +$22.44 |

Read: since April the two yardsticks (no word knowledge) make nothing, the word's own record makes money. Before April everything on the No side made money, so those years can't tell the rule from blind No. Buying Yes loses, as in every dig so far.

### The rule cut up (since April 2026)

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| 2026-04 | 58 | 27 | 28 | +$41.72 | +$36.20 | +$47.14 |
| 2026-05 | 35 | 14 | 16 | +$31.24 | +$129.06 | -$61.42 |
| 2026-06 | 76 | 38 | 22 | -$38.97 | -$37.87 | -$40.07 |
| 2026-07 | 141 | 54 | 68 | +$22.37 | +$19.13 | +$25.57 |
| 2026-08 | 48 | 27 | 13 | -$19.39 | -$42.03 | +$3.30 |
| 2026-09 | 97 | 46 | 56 | +$36.99 | +$53.96 | +$20.33 |
| 2026-10 | 70 | 41 | 31 | +$29.05 | +$4.07 | +$54.52 |
| 2026-11 | 8 | - | - | - | - | - |
| No paid 10-20c | 120 | 92 | 31 | +$28.28 | +$29.20 | +$27.36 |
| No paid 20-35c | 175 | 117 | 63 | +$16.42 | -$4.27 | +$36.87 |
| No paid 35-50c | 119 | 92 | 59 | +$8.77 | +$14.39 | +$3.25 |
| No paid 50-90c | 119 | 98 | 83 | +$6.68 | +$0.93 | +$12.31 |
| market under 12h old | 272 | 157 | 110 | -$1.89 | +$1.81 | -$5.60 |
| market 12h+ old | 261 | 152 | 126 | +$33.09 | +$19.62 | +$46.42 |
| family: trump | 210 | 84 | 83 | +$18.67 | +$25.30 | +$12.05 |
| family: world-cup-mentions | 97 | 39 | 38 | +$2.96 | -$40.18 | +$45.16 |
| family: trump-weekly-mentions | 39 | 22 | 16 | -$14.56 | -$24.17 | -$5.47 |
| family: trump-post-weekly | 24 | 14 | 12 | +$29.31 | +$26.37 | +$32.21 |
| family: nfl-mentions | 24 | 12 | 15 | +$7.52 | +$31.73 | -$16.65 |
| family: trump-monthly-mentions | 23 | 6 | 11 | +$47.61 | +$13.96 | +$78.34 |
| family: mrbeast-mentions | 22 | 12 | 7 | -$45.02 | -$55.49 | -$34.59 |
| family: big-brother-mentions | 20 | 12 | 14 | +$79.27 | +$48.69 | +$109.80 |
| family: elon-tweet-mention | 19 | 8 | 15 | +$54.88 | +$17.53 | +$88.51 |
| family: rogan-mentions | 13 | 9 | 5 | -$30.41 | +$8.13 | -$63.56 |

Biggest single win: $66 of $830 in total ("Will MrBeast say "Minecraft" during his next gaming YouTube video?", No at 10c). No lottery ticket carries the result.

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| left out: bets within 6h of the listed end or after it | 147 | 83 | 52 | -$7.65 | +$2.82 | -$17.97 |

Those late bets lose: by then the speech is on and people in the room know more than a word record. The rule stays out. (This cut was found by looking, like the rest.)

**Weak spots.** (1) Everything here was found by looking at the same data, there is no untouched test set, so the live paper bets are the real test. (2) Two of eight months lost (June, August). (3) Real cost is the big unknown: these are thin markets, at +5c the lead halves and at +8c it is gone. The live track must use real asking prices. (4) All of the profit sits in markets that were already 12+ hours old; in younger ones the rule made nothing. (5) A fixed single look per market (2h, 6h, 12h after the first trade) shows nothing clear, on few bets: the money came from waiting for moments when Yes ran up.

## 4. The exam

- **Mention markets: buy No where Yes is 20c+ above the word's own record (since Apr 2026, worst price +3c)**: 533 bets in 244 separate groups, +$15.25 per $100, luck range +$1.98 to +$28.51, worst case -$12.40 per $100, verdict **Promising, needs more bets**.
- **Mention markets: same rule, June 2024 - Nov 2026**: 896 bets in 427 separate groups, +$15.66 per $100, luck range +$5.95 to +$25.37, worst case -$4.43 per $100, verdict **Promising, needs more bets**.
- **Mention markets: same rule if buying costs 5c more (since Apr 2026)**: 523 bets in 243 separate groups, +$7.74 per $100, luck range -$4.62 to +$20.11, worst case -$18.09 per $100, verdict **Ahead, but could be luck**.
- **Mention markets: always buy No, since Apr 2026 (+3c)**: 7669 bets in 667 separate groups, -$1.27 per $100, luck range -$4.73 to +$2.19, worst case -$8.38 per $100, verdict **Behind, but could be bad luck**.
- **Mention markets: buy Yes where the word's record is 20c+ above the price (since Apr 2026)**: 553 bets in 233 separate groups, -$10.79 per $100, luck range -$21.66 to +$0.08, worst case -$34.19 per $100, verdict **Behind, but could be bad luck**.

