# Chart signals on the earlier, cheaper bids

Generated 2026-11-24T21:01:23Z. Code: `kearly.py ta`. One bid per window at the first minute with 10 to 4 minutes left where the winning side's bid is 85-97c, one tick in front, no cushion bar, held to the close. 23391 filled bids in 'find' (to 15 Oct), 9402 in 'check'. Each reading is turned toward our side: high = the chart agrees with our bet. Rows = thirds of the find bids by that reading.

All find bids: +$0.96 (23391, 1790 lost). All check bids: -$0.19 (9402, 774 lost).

| Reading | Low third | Middle third | High third | High third on check |
|---|---|---|---|---|
| cushion (cuts 1.09 / 1.43) | +$0.23 (7787, 791 lost) | +$0.91 (7788, 608 lost) | +$1.71 (7788, 389 lost) | +$0.94 (2735, 138 lost) |
| kalshi_cushion (cuts 0.99 / 1.33) | -$0.03 (7754, 784 lost) | +$0.98 (7754, 602 lost) | +$1.84 (7754, 398 lost) | +$0.92 (2934, 158 lost) |
| rsi (cuts 61.54 / 70.97) | +$0.67 (7797, 675 lost) | +$1.00 (7797, 586 lost) | +$1.21 (7797, 529 lost) | -$0.56 (2944, 234 lost) |
| ema (cuts 0.40 / 1.03) | +$0.80 (7797, 649 lost) | +$0.75 (7797, 616 lost) | +$1.33 (7797, 525 lost) | -$0.26 (3203, 248 lost) |
| macd (cuts 0.24 / 0.42) | +$0.67 (7797, 672 lost) | +$0.57 (7797, 634 lost) | +$1.65 (7797, 484 lost) | +$0.42 (3034, 207 lost) |
| bollinger (cuts 0.85 / 1.00) | +$0.92 (7797, 658 lost) | +$1.23 (7797, 583 lost) | +$0.74 (7797, 549 lost) | +$0.68 (2714, 177 lost) |
| mom3 (cuts 0.58 / 1.29) | +$1.06 (7797, 639 lost) | +$1.45 (7797, 569 lost) | +$0.38 (7797, 582 lost) | -$0.43 (2828, 219 lost) |
| mom10 (cuts 0.81 / 1.24) | +$0.24 (7797, 734 lost) | +$0.79 (7797, 606 lost) | +$1.84 (7797, 450 lost) | +$0.28 (3029, 204 lost) |
| range60 (cuts 0.66 / 0.97) | +$0.60 (7797, 658 lost) | +$1.05 (7797, 598 lost) | +$1.23 (7797, 534 lost) | +$0.44 (2916, 209 lost) |
| volregime (cuts 0.86 / 1.06) | +$0.39 (7797, 646 lost) | +$1.40 (7797, 566 lost) | +$1.09 (7797, 578 lost) | +$0.45 (3080, 230 lost) |
| kalshi_move (cuts 0.10 / 0.19) | +$1.55 (6404, 456 lost) | +$1.01 (6445, 478 lost) | -$0.06 (6425, 552 lost) | -$1.11 (2319, 212 lost) |
| kalshi_volume (cuts 0.95 / 1.32) | +$1.82 (7797, 564 lost) | +$1.14 (7797, 579 lost) | -$0.07 (7797, 647 lost) | -$0.51 (3387, 273 lost) |
| same_way (cuts 0.83 / 1.00) | +$0.89 (4953, 420 lost) | +$0.60 (3318, 271 lost) | +$1.07 (15120, 1099 lost) | -$0.37 (6889, 561 lost) |
| hour (cuts 7.00 / 16.00) | +$0.12 (7182, 613 lost) | +$1.10 (8200, 603 lost) | +$1.57 (8009, 574 lost) | -$0.33 (3131, 263 lost) |

## Soft cushion (1.5+) plus one chart reading in its top third

| Filter | Find | Check |
|---|---|---|
| cushion 1.5+ alone | +$1.77 (6524, 309 lost) | +$1.11 (2181, 101 lost) |
| + kalshi_cushion top third | +$2.13 (5131, 216 lost) | +$1.32 (1662, 70 lost) |
| + rsi top third | +$2.09 (3396, 150 lost) | +$0.84 (1086, 53 lost) |
| + ema top third | +$2.14 (3746, 166 lost) | +$1.37 (1286, 58 lost) |
| + macd top third | +$1.94 (3958, 181 lost) | +$1.33 (1286, 56 lost) |
| + bollinger top third | +$1.42 (3546, 176 lost) | +$1.83 (1056, 41 lost) |
| + mom3 top third | +$1.34 (3744, 190 lost) | +$0.85 (1182, 58 lost) |
| + mom10 top third | +$2.20 (4778, 206 lost) | +$1.68 (1582, 64 lost) |
| + range60 top third | +$2.29 (3504, 152 lost) | +$1.30 (1100, 51 lost) |
| + volregime top third | +$2.70 (1801, 63 lost) | +$1.82 (610, 23 lost) |
| + kalshi_move top third | +$0.95 (1490, 81 lost) | -$0.40 (463, 28 lost) |
| + kalshi_volume top third | +$0.91 (2036, 106 lost) | -$0.38 (791, 45 lost) |
| + same_way top third | +$1.87 (4729, 212 lost) | +$1.31 (1814, 79 lost) |

## Chart vote: how many of 6 classic readings agree with our side (RSI over 55, fast average above slow, MACD up, upper half of the Bollinger band, up over 3 min, up over 10 min)

| Votes | Find | Check |
|---|---|---|
| 0 | -$11.15 (5, 1 lost) | - |
| 1 | +$4.38 (28, 2 lost) | -$2.17 (8, 1 lost) |
| 2 | +$4.01 (154, 11 lost) | +$0.46 (48, 5 lost) |
| 3 | -$0.71 (450, 49 lost) | +$3.01 (147, 11 lost) |
| 4 | +$0.86 (2153, 189 lost) | -$0.49 (877, 86 lost) |
| 5 | +$0.74 (5273, 441 lost) | -$0.80 (2236, 206 lost) |
| 6 | +$1.07 (15328, 1097 lost) | -$0.00 (6086, 465 lost) |
| 5+ votes and cushion 1.0+ | +$1.18 (16248, 1087 lost) | -$0.06 (6422, 463 lost) |
| 5+ votes and cushion 1.5+ | +$1.78 (6303, 297 lost) | +$1.12 (2106, 97 lost) |
| 5+ votes and cushion 2.0+ | +$2.32 (1680, 55 lost) | +$2.66 (373, 9 lost) |
