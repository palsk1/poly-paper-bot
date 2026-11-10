# Who trades before the price moves? (informed-trader hunt)

**Verdict (2026-11-09): dropped, no new track.** In plain words:

- When someone places a big bet, the price does move their way, about 1.4c on average. But it happens within
  the first 5 minutes. After our bot's 5-minute delay the move is already gone (about -0.1c).
- Copying every $100+ bet would lose about $4.40 per $100 (costs eat it).
- Being "early" barely repeats. Wallets that were early before mid-May were only slightly early after it
  (rank match 0.05, where 0 means no link at all).
- The best wallet picks beat random wallets by about $2-4 per $100, in both directions of the split test, but they
  still only end around +$0 to +$3 per $100, the range always includes losing, and at 3c costs they'd lose.
- "New wallet, one big bet, quiet market" (the classic insider look) is noise: one half wins, the other loses,
  and the brand-new wallets are only 17 bets.

Run: probe `btinf_all` on ref=main (run 42709511719). Full numbers below.

Data: full trade lists of 19625 finished Polymarket markets from 2566 whole events (sports and 5/15-minute crypto left out, every choice of an event kept so cheap losers aren't missing: yes), markets ending 2026-03-01 to 2026-11-09 (holdout untouched). 355548 first buys of $100+ by 82834 wallets. Prices are real trades (5-minute steps). A copy pays the next real buy price 5-65 minutes later (our bot is ~5 min behind) + 1c + taker fee, held to the result. No later buy within an hour = no copy (no made-up fills).

## 1. Baseline: copying everyone

- All $100+ first buys: 95484 copies in 2416 events, won 62807: $-4.40 per $100 (90% band $-6.31 to $-2.66)
- Same at +3c: 85541 copies in 2372 events, won 53020: $-9.51 per $100 (90% band $-11.44 to $-7.52)
- Buys $100-1,000: 87746 copies in 2399 events, won 57241: $-4.52 per $100 (90% band $-6.27 to $-2.17)
- Buys $1,000-10,000: 7104 copies in 997 events, won 5293: $-1.95 per $100 (90% band $-4.25 to $+0.01)
- Buys $10,000-1,000,000,000,000: 173 copies in 95 events, won 129: $-4.18 per $100 (90% band $-14.94 to $+7.56)

Average move in the buyer's direction (cents), from just before the trade / after our 5-min delay:

- 1h: +1.41c / -0.05c
- 6h: +1.38c / -0.08c
- 24h: +1.38c / -0.08c

## 2. Wallets that are early again and again (split-half test)

Split at 2026-05-13T08:59:04Z (middle trade). Picks use only moves seen 24h after the trade and before the split.

**Does 'early' repeat?** 777 wallets have 5+ markets in both halves. Rank correlation of their 24h-after-delay move between halves: 0.054 (0 = no memory, 1 = perfect).

- Top tenth in half A (77 wallets): half A avg +15.62c, half B avg +1.21c
- Bottom tenth in half A: half A -14.00c, half B -0.81c
- Everyone in both halves: half B +0.84c

| Pick rule | direction | wallets | copies in the other half | same-size random wallets (median, 20 draws) |
|---|---|---|---|---|
| S1 5+ markets, avg +3c, t>=2 | pick A, test B | 282 | 1639 copies in 557 events, won 1184: $+2.19 per $100 (90% band $-2.07 to $+7.58); niche markets (<$250k): 963 copies in 482 events, won 735: $+3.78 per $100 (90% band $-1.46 to $+9.67) | $-0.02 per $100 |
| S1 5+ markets, avg +3c, t>=2 | pick B, test A | 362 | 942 copies in 369 events, won 713: $-0.52 per $100 (90% band $-5.36 to $+4.28); niche markets (<$250k): 498 copies in 284 events, won 399: $-3.01 per $100 (90% band $-7.26 to $+1.56) | $-3.68 per $100 |
| S2 10+ markets, t>=3 | pick A, test B | 37 | 230 copies in 136 events, won 158: $+1.15 per $100 (90% band $-13.31 to $+19.60); niche markets (<$250k): 137 copies in 99 events, won 101: $+10.01 per $100 (90% band $-7.80 to $+34.30) | $-2.81 per $100 |
| S2 10+ markets, t>=3 | pick B, test A | 46 | 268 copies in 151 events, won 211: $-0.88 per $100 (90% band $-8.21 to $+7.36); niche markets (<$250k): 224 copies in 128 events, won 173: $-1.48 per $100 (90% band $-8.04 to $+6.17) | $-4.17 per $100 |
| S3 3+ markets, avg +10c | pick A, test B | 511 | 1378 copies in 468 events, won 858: $-1.93 per $100 (90% band $-8.55 to $+4.73); niche markets (<$250k): 765 copies in 383 events, won 508: $-0.12 per $100 (90% band $-8.27 to $+9.24) | $-3.23 per $100 |
| S3 3+ markets, avg +10c | pick B, test A | 685 | 931 copies in 317 events, won 602: $-4.71 per $100 (90% band $-11.68 to $+2.71); niche markets (<$250k): 428 copies in 233 events, won 308: $-3.55 per $100 (90% band $-13.42 to $+8.43) | $-1.49 per $100 |
| S4 5+ markets, avg +5c, t>=2.5 | pick A, test B | 152 | 930 copies in 405 events, won 698: $+1.83 per $100 (90% band $-4.23 to $+8.95); niche markets (<$250k): 547 copies in 336 events, won 441: $+7.38 per $100 (90% band $-0.64 to $+17.20) | $+0.76 per $100 |
| S4 5+ markets, avg +5c, t>=2.5 | pick B, test A | 223 | 579 copies in 271 events, won 467: $+2.78 per $100 (90% band $-1.89 to $+8.08); niche markets (<$250k): 327 copies in 203 events, won 282: $+2.05 per $100 (90% band $-2.57 to $+6.54) | $-2.05 per $100 |
| P1 copy profit: 5+ markets, +$5 per $100, t>=2 | pick A, test B | 179 | 1165 copies in 472 events, won 942: $-2.63 per $100 (90% band $-5.24 to $+0.31); niche markets (<$250k): 732 copies in 406 events, won 610: $+0.05 per $100 (90% band $-2.85 to $+3.47) | $-1.20 per $100 |
| P1 copy profit: 5+ markets, +$5 per $100, t>=2 | pick B, test A | 239 | 553 copies in 267 events, won 471: $+2.15 per $100 (90% band $-1.54 to $+6.20); niche markets (<$250k): 283 copies in 192 events, won 246: $-3.11 per $100 (90% band $-6.64 to $+0.08) | $-2.41 per $100 |
| P2 copy profit: 10+ markets, t>=2 | pick A, test B | 39 | 318 copies in 162 events, won 242: $-5.89 per $100 (90% band $-10.89 to $-0.68); niche markets (<$250k): 172 copies in 118 events, won 134: $-0.62 per $100 (90% band $-8.66 to $+7.11) | $-1.35 per $100 |
| P2 copy profit: 10+ markets, t>=2 | pick B, test A | 50 | 228 copies in 142 events, won 208: $+1.02 per $100 (90% band $-2.63 to $+4.53); niche markets (<$250k): 148 copies in 114 events, won 136: $-0.11 per $100 (90% band $-3.61 to $+4.19) | $-1.50 per $100 |

- Pass S1 5+ markets, avg +3c, t>=2 in both halves: 18 wallets
- Pass S2 10+ markets, t>=3 in both halves: 1 wallets
- Pass S3 3+ markets, avg +10c in both halves: 19 wallets
- Pass S4 5+ markets, avg +5c, t>=2.5 in both halves: 8 wallets
- Pass P1 copy profit: 5+ markets, +$5 per $100, t>=2 in both halves: 13 wallets
- Pass P2 copy profit: 10+ markets, t>=2 in both halves: 1 wallets

Top wallets picked on half A (S1), and what they did in half B:

| wallet | A markets | A avg | A t | B markets | B avg | B copies |
|---|---|---|---|---|---|---|
| `0xd30d0fe99693bae7893ee5659c9b2d0b8517fd5d` | 5 | +5.5c | 21.4 | 0 | +0.0c | - |
| `0xca5f6a17056a5ffcfa034848cba18cf8511e1e74` | 8 | +4.9c | 12.3 | 0 | +0.0c | - |
| `0xa20aa87bc8e6938739e57e80638cfeaa23abd92d` | 6 | +59.7c | 11.1 | 1 | -3.0c | 1 copies in 1 events, won 1: $+5.26 per $100 (90% band $+5.26 to $+5.26) |
| `0x88b4d65905d8b0178c6fb8f6ea3785b2090acf0b` | 5 | +8.3c | 10.0 | 4 | -2.6c | 5 copies in 4 events, won 4: $-14.66 per $100 (90% band $-31.81 to $+9.63) |
| `0xe502185d8bff53c20cf531e638546c5b4601fba0` | 5 | +17.5c | 9.1 | 18 | -9.9c | 28 copies in 13 events, won 11: $-8.10 per $100 (90% band $-33.45 to $+34.02) |
| `0x348cacfab1b7d75c0edeee43f9e880d77703c35a` | 7 | +5.8c | 9.1 | 1 | +5.0c | 2 copies in 2 events, won 2: $+5.59 per $100 (90% band $+5.23 to $+5.96) |
| `0x924f89ecfdb1cd6dd39cdf538380e7100640f5ae` | 6 | +9.6c | 9.0 | 1 | -92.8c | 1 copies in 1 events, won 0: $-100.30 per $100 (90% band $-100.30 to $-100.30) |
| `0x6d1ad4d9bf79ab1184472fc302dd060d2bd2837e` | 7 | +4.7c | 8.8 | 1 | -3.0c | - |
| `0x309c96ca3c4977058f35d8e59ca7548d029809b5` | 7 | +5.8c | 8.8 | 0 | +0.0c | - |
| `0x306e06d4457dc86d88671a788c77b17e8c213a7c` | 5 | +9.9c | 8.7 | 1 | +10.0c | 1 copies in 1 events, won 1: $+6.08 per $100 (90% band $+6.08 to $+6.08) |
| `0xbe601e361ea42a04ad0e761ecb3cd514986e377c` | 6 | +11.1c | 8.3 | 5 | +7.5c | 6 copies in 6 events, won 6: $+7.83 per $100 (90% band $+5.20 to $+11.36) |
| `0xec6c626f970be3fc433e4db854bdf72799526ea0` | 23 | +8.7c | 8.2 | 0 | +0.0c | - |
| `0xfe578df75e3c9ae0ba3182bf4bc1b3385bec4406` | 12 | +6.2c | 8.1 | 2 | +7.2c | 2 copies in 2 events, won 2: $+7.76 per $100 (90% band $+6.08 to $+9.44) |
| `0x2c77c848cbe94c196ce981027daa19be6b0bbde7` | 12 | +13.6c | 7.8 | 4 | -19.6c | 5 copies in 4 events, won 3: $-23.12 per $100 (90% band $-59.73 to $+22.33) |
| `0xbfa09746cdac8268a0bbd9a3d9da0ad0e0491a65` | 8 | +5.9c | 7.5 | 8 | -17.9c | 11 copies in 10 events, won 8: $-24.17 per $100 (90% band $-58.06 to $+4.22) |

## 3. Pattern: new wallet, one big bet, quiet market

Known at the time of the trade, no wallet history needed from us. 'Quiet' = the bet is bigger than everything traded in that market in the 24 hours before. 'New in our data' = first market we see this wallet in.

| Pattern | half A | half B | all |
|---|---|---|---|
| big ($1k+) | 2077 copies in 314 events, won 1442: $-1.65 per $100 (90% band $-6.33 to $+3.43) | 2930 copies in 523 events, won 1858: $-3.53 per $100 (90% band $-7.29 to $-0.31) | 5007 copies in 802 events, won 3300: $-2.75 per $100 (90% band $-5.46 to $+0.28) |
| big + quiet | 298 copies in 181 events, won 205: $-3.15 per $100 (90% band $-9.29 to $+4.54) | 547 copies in 309 events, won 376: $+4.16 per $100 (90% band $-3.05 to $+12.42) | 845 copies in 469 events, won 581: $+1.58 per $100 (90% band $-3.91 to $+7.87) |
| big + new in our data | 799 copies in 183 events, won 528: $-5.36 per $100 (90% band $-11.82 to $+0.90) | 480 copies in 154 events, won 275: $-7.96 per $100 (90% band $-19.26 to $+3.56) | 1279 copies in 325 events, won 803: $-6.34 per $100 (90% band $-11.95 to $+0.78) |
| big + quiet + new | 103 copies in 75 events, won 59: $-12.17 per $100 (90% band $-25.89 to $+3.43) | 72 copies in 51 events, won 49: $+15.53 per $100 (90% band $-11.40 to $+46.74) | 175 copies in 121 events, won 108: $-0.77 per $100 (90% band $-14.58 to $+15.50) |
| $5k+ + quiet + new | 30 copies in 22 events, won 15: $-25.69 per $100 (90% band $-47.91 to $-2.70) | 21 copies in 18 events, won 18: $+14.53 per $100 (90% band $-9.23 to $+33.17) | 51 copies in 40 events, won 33: $-9.13 per $100 (90% band $-26.83 to $+9.29) |
| big + quiet + new, cheap side (3-30c) | 6 copies in 6 events, won 1: $-47.29 per $100 (90% band $-102.12 to $+60.96) | 9 copies in 9 events, won 3: $+102.96 per $100 (90% band $-63.75 to $+311.57) | 15 copies in 14 events, won 4: $+42.86 per $100 (90% band $-57.41 to $+162.75) |

Same price band, big buys that are NOT the pattern (are we just seeing the price band?):

- 3-30c: pattern 15 copies in 14 events, won 4: $+42.86 per $100 (90% band $-57.41 to $+162.75); others 500 copies in 207 events, won 84: $-31.95 per $100 (90% band $-53.78 to $-9.59)
- 30-60c: pattern 46 copies in 36 events, won 17: $-18.19 per $100 (90% band $-43.57 to $+9.50); others 1246 copies in 363 events, won 605: $-0.73 per $100 (90% band $-8.00 to $+6.09)
- 60-90c: pattern 114 copies in 83 events, won 87: $+0.51 per $100 (90% band $-9.13 to $+11.65); others 3086 copies in 650 events, won 2503: $+1.06 per $100 (90% band $-2.11 to $+3.99)

Real wallet age from the Polymarket API (trades the wallet made before this bet):

- big + quiet, brand new (0 earlier trades): 17 copies in 14 events, won 6: $+13.56 per $100 (90% band $-69.45 to $+152.03); half A 11 copies in 8 events, won 2: $-62.40 per $100 (90% band $-100.63 to $-33.48); half B 6 copies in 6 events, won 4: $+152.81 per $100 (90% band $-55.60 to $+478.09)
- big + quiet, 1-5 earlier: 21 copies in 18 events, won 11: $-18.09 per $100 (90% band $-49.26 to $+12.03); half A 11 copies in 10 events, won 8: $+10.93 per $100 (90% band $-25.50 to $+46.60); half B 10 copies in 8 events, won 3: $-50.02 per $100 (90% band $-102.13 to $-15.20)
- big + quiet, 6-3000 earlier: 356 copies in 221 events, won 240: $-1.70 per $100 (90% band $-9.66 to $+5.81); half A 155 copies in 101 events, won 109: $+0.03 per $100 (90% band $-9.45 to $+10.15); half B 201 copies in 125 events, won 131: $-3.03 per $100 (90% band $-13.12 to $+9.17)
- big + quiet, 3000+ earlier: 186 copies in 153 events, won 132: $+1.84 per $100 (90% band $-9.94 to $+13.58); half A 39 copies in 35 events, won 32: $+2.39 per $100 (90% band $-11.70 to $+14.78); half B 147 copies in 119 events, won 100: $+1.69 per $100 (90% band $-11.29 to $+15.29)
- big + quiet, unknown: 193 copies in 145 events, won 142: $+6.63 per $100 (90% band $-3.93 to $+18.85); half A 67 copies in 56 events, won 42: $-9.02 per $100 (90% band $-25.20 to $+9.13); half B 126 copies in 92 events, won 100: $+14.95 per $100 (90% band $+1.80 to $+27.73)

Fresh + big + quiet by topic: other: 24 copies in 19 events, won 11: $+10.87 per $100 (90% band $-47.93 to $+99.56); elections: 5 copies in 4 events, won 2: $-23.73 per $100 (90% band $-100.74 to $+19.04); apps/tech: 6 copies in 5 events, won 4: $+1.83 per $100 (90% band $-72.70 to $+50.25); geopolitics: 2 copies in 2 events, won 0: $-101.33 per $100 (90% band $-102.65 to $-100.00); crypto price: 1 copies in 1 events, won 0: $-100.00 per $100 (90% band $-100.00 to $-100.00)

Examples (fresh wallet, big bet, quiet market):

- 2026-02-27T03:28 $17,745 at 55c (24h before: $4,026 traded) -> won, copy +79 per $100 | Will Anthropic have the best AI model at the end of March 2026?
- 2026-09-26T02:17 $13,000 at 86c (24h before: $1 traded) -> lost, copy - | Pakistan military action against Afghanistan by October 15, 2026?
- 2026-03-02T01:19 $12,135 at 31c (24h before: $382 traded) -> lost, copy -100 per $100 | Will the price of Bitcoin be between $66,000 and $68,000 on March 3?
- 2026-10-05T13:40 $12,000 at 80c (24h before: $6,864 traded) -> lost, copy - | Will Ukraine target Moscow on October 10, 2026?
- 2026-10-06T12:33 $11,686 at 89c (24h before: $0 traded) -> lost, copy - | Will Ukraine target Moscow on October 16, 2026?
- 2026-10-06T13:17 $11,037 at 80c (24h before: $0 traded) -> lost, copy - | Will Ukraine target Moscow on October 14, 2026?
- 2026-06-28T01:10 $10,513 at 73c (24h before: $4,573 traded) -> won, copy +35 per $100 | Will Brazil reach the Round of 16 at the 2026 FIFA World Cup?
- 2026-03-19T15:53 $10,000 at 88c (24h before: $37 traded) -> won, copy +39 per $100 | Will Google reach $320 in March?
- 2026-04-21T01:05 $9,968 at 82c (24h before: $7,602 traded) -> won, copy +32 per $100 | Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award?
- 2026-03-06T12:22 $9,587 at 43c (24h before: $622 traded) -> lost, copy -100 per $100 | Will USD reach 1.8M Iranian rials by March 31?
- 2026-03-06T11:39 $8,959 at 37c (24h before: $2,259 traded) -> won, copy +144 per $100 | Will USD reach 1.7M Iranian rials by March 31?
- 2026-10-11T05:16 $8,490 at 88c (24h before: $0 traded) -> won, copy - | Will Ukraine target Moscow on October 21, 2026?
- 2026-09-24T11:39 $7,560 at 72c (24h before: $0 traded) -> won, copy - | Shipping targeted in Hormuz on September 25, 2026?
- 2026-04-08T09:04 $7,104 at 67c (24h before: $5,830 traded) -> lost, copy -100 per $100 | Will 80 ships transit the Strait of Hormuz on any day by April 30?
- 2026-10-05T13:07 $6,535 at 81c (24h before: $0 traded) -> lost, copy - | Will Ukraine target Moscow on October 6, 2026?
- 2026-07-17T15:34 $6,230 at 89c (24h before: $15 traded) -> won, copy - | Will Jorginho Mello win the Governor of Santa Catarina election?
- 2025-10-30T03:45 $6,004 at 76c (24h before: $2,829 traded) -> won, copy - | Will a new Cabinet of the Netherlands be sworn in by December 31, 2025?
- 2026-05-25T15:19 $5,906 at 90c (24h before: $0 traded) -> lost, copy - | Will the Milwaukee Brewers win 100 or more games during the 2026 MLB Regular Sea
- 2026-10-05T13:17 $5,818 at 82c (24h before: $0 traded) -> won, copy - | Will Ukraine target Moscow on October 7, 2026?
- 2026-10-05T13:27 $5,661 at 80c (24h before: $0 traded) -> lost, copy -100 per $100 | Will Ukraine target Moscow on October 10, 2026?


