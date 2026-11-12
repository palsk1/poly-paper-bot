# Kalshi: be the patient buyer (khouse.py)

**In short.** The idea: on Kalshi, don't pay the asking price. Leave a buy order 1c above the best one and wait an hour for somebody in a hurry to sell to us. Tested on two months of real trades, with our order filled only by contracts that were really sold.

- **It loses almost everywhere.** At 50-90c it lost $5.35 per $100. During a live game it lost $5 to $13. The people who sell to a waiting order usually know something.
- **Lowball orders on the likely side lose too** ($3 to $19 per $100).
- **A lead on wide gaps before a game was luck:** +$7.97 per $100 where we found it, -$3.28 on new games.
- **One version is left: the nearly-sure side at 90-97c.** +$1.42 per $100 on 971 bets in the two samples it was found in, but -$1.99 on 304 bets in a third, fresh sample. All together +$0.61 per $100 on 1275 bets (1199 won), luck range -$0.60 to +$1.82. Exam: **Ahead, but could be luck**. It runs as the paper track `kalshi_patient`, labelled untested; its live bets decide.
- **Lowball on the unlikely side before a game:** +$25.90 per $100 where we found it, -$8.51 on 318 new games. It did not repeat. Dropped.

Generated 2026-11-12T18:59:41Z. Settled Kalshi markets that closed 2026-09-11 to 2026-11-09 with 100+ contracts traded (no 15-minute crypto, no combos), one market per event. Sample 1: up to 70 sports and 110 other events a day, 10535 markets, 1,436,801 real trades from their last 7 days. Sample 2 (downloaded later, to re-check a sports lead): 8850 other sports events, 1,810,165 trades. Markets that closed from 2026-11-10 on are untouched.

A trap we fell into first: for very busy markets the download kept only the newest 2,000 trades. Which markets have such a cut list depends on how the game went, and it made favourites look underpriced. Those stretches are thrown away here.

## 1. Who earned on the real trades (sample 1)

Every trade has a side in a hurry (it took the price on offer) and a patient side (its order was waiting). This is the patient side's profit per $100 it put in, held to the result, before any fee. Trades over 500 contracts count as 500.

| kind | patient side per $100 | luck range | contracts | events |
|---|---|---|---|---|
| all | +$0.66 | -$1.33 to +$2.65 | 69,373,825 | 10281 |
| sports before the game | +$5.98 | -$3.86 to +$15.81 | 8,157,728 | 2007 |
| sports, game on | -$0.96 | -$3.03 to +$1.11 | 38,997,762 | 3981 |
| crypto price | +$0.82 | -$0.50 to +$2.14 | 7,049,108 | 2337 |
| stocks | +$22.79 | -$10.50 to +$56.09 | 397,109 | 146 |
| weather | -$0.89 | -$2.42 to +$0.65 | 4,213,633 | 1504 |
| slow questions | +$1.70 | -$0.76 to +$4.17 | 10,558,485 | 2191 |

By the price the patient side paid:

| kind | 0-10c | 10-30c | 30-50c | 50-70c | 70-80c | 80-90c | 90-97c | 97-100c |
|---|---|---|---|---|---|---|---|---|
| all | -$26.57 (9202) | -$17.16 (6802) | -$5.24 (5076) | +$3.16 (5144) | +$1.56 (4705) | +$6.35 (5036) | +$2.92 (5016) | +$1.16 (5067) |
| sports before the game | -$45.94 (354) | +$68.86 (619) | +$5.36 (815) | +$12.33 (808) | -$11.60 (412) | +$13.41 (330) | -$5.13 (262) | +$2.20 (81) |
| sports, game on | -$32.09 (3619) | -$31.33 (2882) | -$10.64 (2280) | +$1.93 (2330) | +$4.38 (1949) | +$5.76 (1931) | +$3.53 (1762) | +$1.43 (2155) |
| crypto price | -$62.77 (2015) | -$30.33 (1548) | -$8.36 (1080) | +$2.28 (1094) | +$7.02 (1162) | +$4.52 (1351) | +$5.74 (1457) | +$1.66 (1187) |
| stocks | +$423.35 (128) | +$169.16 (110) | -$2.33 (88) | +$2.63 (89) | +$8.23 (82) | +$3.24 (80) | -$1.35 (73) | +$0.29 (53) |
| weather | +$52.92 (1426) | +$10.96 (923) | -$2.93 (599) | -$8.16 (588) | -$2.08 (648) | -$2.29 (818) | -$2.07 (943) | -$0.34 (983) |
| slow questions | -$22.92 (1915) | -$18.45 (1197) | +$5.25 (890) | -$5.69 (885) | +$4.11 (749) | +$8.94 (782) | +$3.81 (724) | +$0.97 (662) |

(In brackets: events. Cells with under 25 events are left out.)

## 2. The bot rule: a $10 buy order 1c above the best one, refreshed once an hour (sample 1)

Filled only by contracts really sold at our price or lower in the next hour (after a 60-second wait). One bet per market, held to the result, Kalshi's fee for waiting orders included where a series has one. 'Price after' = the middle price at the next hour mark compared with what we paid (minus = we were sold to just before it fell).

62 versions with 40+ bets (side x price x gap x kind of market).

| side | best buy order at | gap at least | kind | bets | won | per $100 | luck range | first half | second half | price after |
|---|---|---|---|---|---|---|---|---|---|---|
| the likely side | 50-70c | 2c | sports before the game | 533 | 309 | -$3.89 | -$10.85 to +$3.07 | -$1.29 | -$6.31 | +0.4c |
| the likely side | 50-70c | 5c | sports before the game | 201 | 124 | +$3.39 | -$7.87 to +$14.65 | +$4.69 | +$2.24 | +1.5c |
| the likely side | 70-80c | 2c | sports before the game | 273 | 215 | +$3.77 | -$2.54 to +$10.08 | +$6.07 | +$1.50 | +0.2c |
| the likely side | 70-80c | 5c | sports before the game | 103 | 87 | +$16.05 | +$7.59 to +$24.51 | +$8.23 | +$23.66 | +2.0c |
| the likely side | 80-90c | 2c | sports before the game | 220 | 190 | +$1.93 | -$2.83 to +$6.69 | +$5.80 | -$2.47 | +0.6c |
| the likely side | 80-90c | 5c | sports before the game | 84 | 76 | +$7.62 | +$1.29 to +$13.96 | +$9.54 | +$5.47 | +1.8c |
| the likely side | 90-97c | 2c | sports before the game | 156 | 148 | +$2.50 | -$0.22 to +$5.23 | -$0.05 | +$5.05 | +0.3c |
| the likely side | 50-70c | 2c | sports, game on | 798 | 438 | -$12.70 | -$17.77 to -$7.63 | -$7.99 | -$17.46 | -2.0c |
| the likely side | 50-70c | 5c | sports, game on | 487 | 267 | -$12.26 | -$18.85 to -$5.67 | -$1.13 | -$23.93 | -2.3c |
| the likely side | 70-80c | 2c | sports, game on | 386 | 278 | -$5.84 | -$11.15 to -$0.53 | -$5.75 | -$5.93 | -1.0c |
| the likely side | 70-80c | 5c | sports, game on | 210 | 145 | -$10.04 | -$17.58 to -$2.51 | -$5.18 | -$15.01 | -0.4c |
| the likely side | 80-90c | 2c | sports, game on | 304 | 239 | -$8.13 | -$12.79 to -$3.48 | -$3.73 | -$12.69 | -3.2c |
| the likely side | 80-90c | 5c | sports, game on | 126 | 101 | -$7.38 | -$14.58 to -$0.17 | +$1.25 | -$16.10 | -2.9c |
| the likely side | 90-97c | 2c | sports, game on | 197 | 176 | -$5.29 | -$9.34 to -$1.25 | -$6.64 | -$3.90 | -3.4c |
| the likely side | 80-90c | 2c | crypto price | 45 | 35 | -$7.40 | -$19.62 to +$4.81 | -$25.99 | +$13.76 | -1.1c |
| the likely side | 50-70c | 2c | stocks | 49 | 21 | -$31.84 | -$53.53 to -$10.16 | -$15.85 | -$49.81 | -7.2c |
| the likely side | 50-70c | 5c | stocks | 43 | 17 | -$44.21 | -$66.13 to -$22.30 | -$23.68 | -$62.68 | -5.9c |
| the likely side | 70-80c | 2c | stocks | 41 | 24 | -$19.37 | -$38.86 to +$0.12 | -$11.12 | -$28.04 | +3.7c |
| the likely side | 50-70c | 2c | weather | 206 | 120 | -$4.32 | -$15.15 to +$6.51 | +$1.70 | -$10.89 | -1.2c |
| the likely side | 50-70c | 5c | weather | 177 | 101 | -$9.93 | -$21.73 to +$1.87 | -$4.97 | -$15.40 | -0.6c |
| the likely side | 70-80c | 2c | weather | 177 | 124 | -$10.97 | -$19.66 to -$2.28 | -$8.76 | -$13.31 | +0.5c |
| the likely side | 70-80c | 5c | weather | 127 | 89 | -$10.39 | -$20.99 to +$0.20 | -$7.46 | -$13.22 | +1.4c |
| the likely side | 80-90c | 2c | weather | 177 | 143 | -$6.36 | -$12.59 to -$0.12 | -$9.47 | -$3.26 | -0.8c |
| the likely side | 80-90c | 5c | weather | 117 | 95 | -$6.83 | -$14.88 to +$1.21 | -$8.08 | -$5.52 | +1.7c |
| the likely side | 90-97c | 2c | weather | 185 | 177 | +$2.71 | +$0.15 to +$5.26 | +$2.59 | +$2.82 | -0.6c |
| the likely side | 90-97c | 5c | weather | 70 | 66 | -$0.07 | -$6.55 to +$6.41 | -$4.22 | +$3.90 | +0.8c |
| the likely side | 50-70c | 2c | slow questions | 412 | 235 | -$8.96 | -$16.32 to -$1.60 | -$17.18 | -$1.21 | -0.9c |
| the likely side | 50-70c | 5c | slow questions | 277 | 152 | -$12.39 | -$21.48 to -$3.30 | -$21.50 | -$3.26 | -1.0c |
| the likely side | 70-80c | 2c | slow questions | 245 | 180 | -$4.89 | -$11.77 to +$2.00 | -$8.25 | -$1.62 | -0.6c |
| the likely side | 70-80c | 5c | slow questions | 171 | 128 | -$4.05 | -$12.27 to +$4.16 | -$9.13 | +$0.60 | +1.3c |
| the likely side | 80-90c | 2c | slow questions | 248 | 212 | -$0.64 | -$5.37 to +$4.08 | -$1.90 | +$0.69 | -0.6c |
| the likely side | 80-90c | 5c | slow questions | 164 | 144 | +$1.75 | -$3.75 to +$7.25 | -$2.35 | +$6.02 | +0.8c |
| the likely side | 90-97c | 2c | slow questions | 234 | 222 | +$0.51 | -$2.24 to +$3.25 | -$3.19 | +$4.26 | -0.6c |
| the likely side | 90-97c | 5c | slow questions | 74 | 73 | +$6.46 | +$3.82 to +$9.10 | +$5.10 | +$7.76 | +1.0c |
| the unlikely side | 3-10c | 2c | sports before the game | 163 | 13 | -$63.22 | -$95.69 to -$30.75 | -$67.73 | -$57.49 | +0.8c |
| the unlikely side | 3-10c | 5c | sports before the game | 88 | 7 | -$49.37 | -$106.97 to +$8.23 | -$81.40 | +$4.39 | +2.0c |
| the unlikely side | 10-30c | 2c | sports before the game | 363 | 86 | -$7.77 | -$31.58 to +$16.04 | -$2.56 | -$13.31 | +0.3c |
| the unlikely side | 10-30c | 5c | sports before the game | 172 | 46 | -$41.46 | -$63.32 to -$19.59 | -$28.97 | -$50.98 | +0.8c |
| the unlikely side | 30-50c | 2c | sports before the game | 524 | 217 | +$2.26 | -$8.44 to +$12.96 | -$3.12 | +$7.33 | +0.4c |
| the unlikely side | 30-50c | 5c | sports before the game | 181 | 75 | -$1.09 | -$19.95 to +$17.76 | -$7.78 | +$5.54 | +2.0c |
| the unlikely side | 3-10c | 2c | sports, game on | 574 | 31 | -$57.78 | -$74.76 to -$40.81 | -$66.29 | -$48.54 | +1.1c |
| the unlikely side | 3-10c | 5c | sports, game on | 379 | 20 | -$70.83 | -$87.67 to -$53.99 | -$93.19 | -$46.98 | +2.1c |
| the unlikely side | 10-30c | 2c | sports, game on | 968 | 138 | -$49.30 | -$57.71 to -$40.90 | -$63.80 | -$34.18 | -1.4c |
| the unlikely side | 10-30c | 5c | sports, game on | 615 | 88 | -$50.57 | -$60.98 to -$40.16 | -$71.09 | -$29.97 | -1.1c |
| the unlikely side | 30-50c | 2c | sports, game on | 685 | 219 | -$22.47 | -$30.37 to -$14.57 | -$23.91 | -$21.00 | -2.8c |
| the unlikely side | 30-50c | 5c | sports, game on | 380 | 116 | -$27.20 | -$37.77 to -$16.63 | -$38.96 | -$14.71 | -2.9c |
| the unlikely side | 10-30c | 2c | crypto price | 52 | 16 | +$22.08 | -$43.95 to +$88.11 | +$25.91 | +$18.13 | +0.4c |
| the unlikely side | 3-10c | 2c | stocks | 49 | 7 | +$148.14 | -$18.62 to +$314.89 | +$175.10 | +$123.97 | +0.4c |
| the unlikely side | 10-30c | 2c | stocks | 65 | 15 | -$13.42 | -$67.05 to +$40.20 | -$29.20 | +$1.66 | -3.0c |
| the unlikely side | 10-30c | 5c | stocks | 55 | 13 | -$18.98 | -$71.20 to +$33.25 | -$7.13 | -$31.38 | -2.4c |
| the unlikely side | 3-10c | 2c | weather | 269 | 16 | -$44.95 | -$89.11 to -$0.79 | -$17.61 | -$76.27 | +0.4c |
| the unlikely side | 3-10c | 5c | weather | 177 | 13 | -$56.09 | -$94.32 to -$17.86 | -$62.78 | -$49.10 | +1.1c |
| the unlikely side | 10-30c | 2c | weather | 276 | 62 | -$8.75 | -$32.35 to +$14.84 | +$7.27 | -$26.74 | +0.7c |
| the unlikely side | 10-30c | 5c | weather | 211 | 52 | -$13.76 | -$38.08 to +$10.57 | -$6.10 | -$20.87 | +1.5c |
| the unlikely side | 30-50c | 2c | weather | 175 | 63 | -$19.43 | -$38.03 to -$0.84 | -$37.67 | -$0.46 | -1.3c |
| the unlikely side | 30-50c | 5c | weather | 135 | 54 | -$0.37 | -$23.02 to +$22.27 | -$17.33 | +$16.88 | +1.3c |
| the unlikely side | 3-10c | 2c | slow questions | 492 | 33 | -$45.44 | -$71.59 to -$19.28 | -$28.60 | -$66.32 | +0.3c |
| the unlikely side | 3-10c | 5c | slow questions | 344 | 26 | -$59.68 | -$84.86 to -$34.49 | -$40.60 | -$83.81 | +1.1c |
| the unlikely side | 10-30c | 2c | slow questions | 531 | 89 | -$35.01 | -$48.75 to -$21.27 | -$34.79 | -$35.25 | -0.4c |
| the unlikely side | 10-30c | 5c | slow questions | 407 | 76 | -$29.11 | -$46.03 to -$12.19 | -$32.00 | -$25.81 | +0.7c |
| the unlikely side | 30-50c | 2c | slow questions | 280 | 82 | -$33.64 | -$46.33 to -$20.94 | -$26.60 | -$40.60 | -2.4c |
| the unlikely side | 30-50c | 5c | slow questions | 165 | 47 | -$33.45 | -$50.66 to -$16.24 | -$23.53 | -$44.30 | -2.0c |

Ahead in both halves with the low end of the luck range above $0: **4 of 62**. Luck alone would give about 2-3.

- likely side 70-80c, gap 5c+, sports before the game: +$16.05 on 103 bets
- likely side 80-90c, gap 5c+, sports before the game: +$7.62 on 84 bets
- likely side 90-97c, gap 2c+, weather: +$2.71 on 185 bets
- likely side 90-97c, gap 5c+, slow questions: +$6.46 on 74 bets

## 3. The first lead did not repeat: wide gaps before a game

The best-looking cell in sample 1 was sports before the game, likely side at 60-95c, gap 5c or more. So we downloaded sample 2 (other games, same weeks) and ran the same rule once.

| what | bets | won | per $100 | luck range | first half | second half |
|---|---|---|---|---|---|---|
| sample 1 (where it was found) | 266 | 215 | +$7.97 | +$2.21 to +$13.74 | +$7.04 | +$8.89 |
| sample 2 (new games) | 560 | 416 | -$3.28 | -$8.08 to +$1.53 | +$2.90 | -$8.92 |

It was luck. Dropped.

## 4. Lowball orders lose too

A buy order far under the going price, filled only when somebody dumps below it. Both samples together.

| what | bets | won | per $100 | luck range | first half | second half |
|---|---|---|---|---|---|---|
| likely side 50-97c, 5c under, before a game | 534 | 317 | -$3.39 | -$10.05 to +$3.26 | -$3.23 | -$3.54 |
| likely side 50-97c, 10c under, before a game | 370 | 207 | -$5.83 | -$14.64 to +$2.97 | -$3.05 | -$8.36 |
| likely side 50-97c, 10c under, game on | 6162 | 3052 | -$19.15 | -$21.18 to -$17.13 | -$16.02 | -$22.29 |
| likely side 50-97c, 5c under, everything but sports | 1169 | 647 | -$14.24 | -$19.33 to -$9.15 | -$15.90 | -$12.48 |
| unlikely side 10-50c, 5c under, before a game | 469 | 149 | +$25.90 | +$4.80 to +$47.00 | +$25.62 | +$26.13 |

On the likely side, whoever dumps below the going price usually knows why: dropped. The last row is the odd one out: lowball orders on the UNLIKELY side before a game came out well ahead in both samples. It was version number 90-something, it lives on a handful of long-shot wins, and nobody had asked the question beforehand, so it got its own re-test on new games (below).

### 4b. Re-test of the unlikely-side lowball on new games (rule fixed before the download)

Rule, written into the commit before sample 3 was downloaded: sports before the game, the unlikely side (middle price 10-50c), a buy order 5c under the middle price and at least 2c under the best buy order, refreshed hourly, filled only by contracts sold below our price. Passes if sample 3 alone is ahead with the low end of its luck range above $0.

Sample 3: 8723 new sports events, 1,838,070 trades.

| what | bets | won | per $100 | luck range | first half | second half |
|---|---|---|---|---|---|---|
| samples 1+2 (where it was found) | 469 | 149 | +$25.90 | +$4.80 to +$47.00 | +$25.62 | +$26.13 |
| **sample 3 (new games), the test** | 318 | 94 | -$8.51 | -$25.21 to +$8.20 | -$10.34 | -$6.53 |
| sample 3, if every contract had cost 1c more | 318 | 94 | -$12.60 | -$28.62 to +$3.41 | -$14.11 | -$10.99 |
| sample 3, second look: middle price 30-50c only | 234 | 80 | -$6.66 | -$23.35 to +$10.04 | -$17.33 | +$4.68 |

**Did not pass.**

## 5. The one that is left: the nearly-sure side

Rule: the likely side's best buy order stands at 90-97c, the gap to the sell price is 2c or more, we bid 1c above the best buy order for an hour. Never on a sports game that has started. All kinds of markets, both samples.

| what | bets | won | per $100 | luck range | first half | second half |
|---|---|---|---|---|---|---|
| sample 1 | 645 | 612 | +$1.49 | -$0.05 to +$3.03 | -$0.15 | +$3.14 |
| sample 2 (sports before the game only) | 326 | 306 | +$1.28 | -$1.03 to +$3.59 | +$1.21 | +$1.35 |
| **both** | 971 | 918 | +$1.42 | +$0.14 to +$2.70 | +$0.34 | +$2.50 |
| **sample 3 (new games, downloaded after the rule was fixed and the track was built)** | 304 | 281 | -$1.99 | -$4.98 to +$0.99 | -$3.34 | -$0.65 |
| **all three** | 1275 | 1199 | +$0.61 | -$0.60 to +$1.82 | -$0.36 | +$1.58 |
| both, if every contract had cost 1c more | 971 | 918 | +$0.35 | -$0.92 to +$1.62 | -$0.72 | +$1.42 |
| both, if every contract had cost 2c more | 971 | 918 | -$0.70 | -$1.96 to +$0.56 | -$1.76 | +$0.36 |
| both: sports before the game | 482 | 454 | +$1.68 | -$0.11 to +$3.48 | +$0.80 | +$2.55 |
| both: crypto price | 39 | 38 | +$3.48 | -$1.39 to +$8.34 | +$6.69 | +$0.19 |
| both: stocks | 31 | 27 | -$4.77 | -$15.14 to +$5.61 | -$11.23 | +$0.24 |
| both: weather | 185 | 177 | +$2.71 | +$0.15 to +$5.26 | +$2.59 | +$2.82 |
| both: slow questions | 234 | 222 | +$0.51 | -$2.24 to +$3.25 | -$3.19 | +$4.26 |
| both: nothing traded in the hour before | 603 | 573 | +$2.27 | +$0.76 to +$3.78 | +$1.48 | +$3.05 |
| both: traded in the hour before | 368 | 345 | +$0.11 | -$2.18 to +$2.39 | -$1.42 | +$1.64 |
| sample 1 at $25 an order | 645 | 612 | +$1.34 | -$0.37 to +$3.04 | -$0.11 | +$2.78 |
| sample 1 at $100 an order | 645 | 612 | +$1.17 | -$0.80 to +$3.14 | -$0.09 | +$2.46 |

Average bet $7.89. A win makes about 5c a contract, a loss costs about 94c, so one loss eats about 15 wins.

Sample 3 was downloaded for the lowball re-test, but it is also the first data this rule had never seen. There it was behind: -$1.99 per $100 on 304 bets. With all three samples the lead shrinks to +$0.61 per $100. The live paper track is now the tie-breaker.

Honest notes: (1) this band was picked after seeing both samples, so sample 2 is not a clean re-test of it. (2) The split by 'traded in the hour before' was also looked at afterwards. (3) Paper can't see other robots stepping in front of our order. (4) It dies if we pay 2c more.

## 6. The exam

Versions looked at in this dig: about 93 (the luck bar counts them, plus every idea in the ledger).

```

=== EXAM: Kalshi patient buyer: nearly-sure side (best buy order 90-97c, gap 2c+), bid 1c above it, no live sports ===
Verdict: Ahead, but could be luck
Bets: 1275 bets on 1271 events over 64 days. Counted as 1271 separate bets (bets on the same event count once).
Result: +$0.61 per $100 bet (total +$61.48 on $10047.13). Luck range -$0.60 to +$1.82.
Halves: first -$0.34, second +$1.56 per $100. Not ahead in both: could be one good stretch.
If every price were worse: +1c -$0.45, +2c -$1.49 per $100.
Luck bar: this is 1 of 181 tries. The luckiest of 181 worthless ideas would show about +$2.42 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$1.90. Below $0: not proven.
To prove it: about 26,794 more separate bets like these. At its pace (19.9 separate bets a day) that is around 2030-07-15, after 2027-01-01: too slow for the 1 Jan decision.
```

```

=== EXAM: Kalshi patient buyer: likely side at 50-90c, bid 1c above the best buy order, no live sports ===
Verdict: Losing
Bets: 2050 bets on 2036 events over 64 days. Counted as 2036 separate bets (bets on the same event count once).
Result: -$5.35 per $100 bet (total -$770.79 on $14410.23). Luck range -$8.20 to -$2.50.
Halves: first -$6.14, second -$4.60 per $100. Not ahead in both: could be one good stretch.
If every price were worse: +1c -$6.72, +2c -$8.05 per $100.
Luck bar: this is 1 of 181 tries. The luckiest of 181 worthless ideas would show about +$5.66 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$11.14. Below $0: not proven.
```

```

=== EXAM: Kalshi patient buyer: sports before the game, likely side 60-95c, gap 5c+ (lead from sample 1, re-run on new games) ===
Verdict: Behind, but could be bad luck
Bets: 560 bets on 559 events over 64 days. Counted as 559 separate bets (bets on the same event count once).
Result: -$3.28 per $100 bet (total -$120.92 on $3692.14). Luck range -$8.08 to +$1.53.
Halves: first +$3.47, second -$9.38 per $100. Not ahead in both: could be one good stretch.
If every price were worse: +1c -$4.56, +2c -$5.81 per $100.
Luck bar: this is 1 of 181 tries. The luckiest of 181 worthless ideas would show about +$9.55 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$13.09. Below $0: not proven.
```

```

=== EXAM: Kalshi lowball orders: likely side, 10c under the going price, before a game ===
Verdict: Behind, but could be bad luck
Bets: 370 bets on 369 events over 62 days. Counted as 369 separate bets (bets on the same event count once).
Result: -$5.83 per $100 bet (total -$144.27 on $2473.73). Luck range -$14.65 to +$2.98.
Halves: first -$3.61, second -$7.84 per $100. Not ahead in both: could be one good stretch.
If every price were worse: +1c -$7.69, +2c -$9.47 per $100.
Luck bar: this is 1 of 181 tries. The luckiest of 181 worthless ideas would show about +$17.46 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$23.67. Below $0: not proven.
```

```

=== EXAM: Kalshi lowball on the unlikely side before a game (10-50c, 5c under): re-test on new games ===
Verdict: Behind, but could be bad luck
Bets: 318 bets on 318 events over 60 days. Counted as 318 separate bets (bets on the same event count once).
Result: -$8.51 per $100 bet (total -$178.88 on $2102.92). Luck range -$25.24 to +$8.23.
Halves: first -$10.34, second -$6.53 per $100. Not ahead in both: could be one good stretch.
If every price were worse: +1c -$12.60, +2c -$16.35 per $100.
Luck bar: this is 1 of 2 tries. The luckiest of 2 worthless ideas would show about +$16.67 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$25.61. Below $0: not proven.
```

