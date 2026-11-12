# Options price vs Polymarket's Bitcoin and Ethereum markets (optfair.py)

Generated 2026-11-12T21:22:34Z. 14072 finished Polymarket markets on Bitcoin / Ethereum prices with an hourly chart (ended before 2026-11-10): 5184 above, 2969 up, 2919 down, 2698 between, 302 below.

## 1. Who forecasts better, the options market or Polymarket?

One look per market, 1-3 days before the end (or at the start for shorter ones).

| kind | options said | markets | options (avg) | Polymarket (avg) | it happened |
|---|---|---|---|---|---|
| touch | 0-10 in 100 | 919 | 4 | 5 | 6 |
| touch | 10-20 in 100 | 363 | 14 | 11 | 11 |
| touch | 20-30 in 100 | 224 | 25 | 18 | 21 |
| touch | 30-40 in 100 | 185 | 35 | 26 | 22 |
| touch | 40-50 in 100 | 149 | 45 | 32 | 34 |
| touch | 50-60 in 100 | 160 | 55 | 43 | 46 |
| touch | 60-70 in 100 | 100 | 65 | 53 | 59 |
| touch | 70-80 in 100 | 69 | 75 | 66 | 62 |
| touch | 80-90 in 100 | 36 | 84 | 79 | 78 |
| touch | all | 2214 | 23 | 19 | 20 |
| end price | 0-10 in 100 | 1230 | 4 | 5 | 3 |
| end price | 10-20 in 100 | 707 | 15 | 12 | 11 |
| end price | 20-30 in 100 | 704 | 25 | 26 | 28 |
| end price | 30-40 in 100 | 332 | 34 | 36 | 33 |
| end price | 40-50 in 100 | 160 | 45 | 46 | 38 |
| end price | 50-60 in 100 | 135 | 55 | 57 | 61 |
| end price | 60-70 in 100 | 148 | 65 | 69 | 62 |
| end price | 70-80 in 100 | 168 | 75 | 80 | 85 |
| end price | 80-90 in 100 | 236 | 85 | 89 | 93 |
| end price | 90-100 in 100 | 507 | 96 | 96 | 96 |
| end price | all | 4327 | 35 | 35 | 35 |

## 2. The trap: hourly chart prices

New Polymarket markets open with a made-up price near 50c and the chart keeps showing it until real trades come in. Buying "where the two disagree" at chart prices looks like a money machine, and is not real:

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| touch (reach / dip), gap 5c+, any hour of the chart | 3079 | 2009 | +$25.21 | +$30.33 | +$20.08 |
| touch (reach / dip), gap 5c+, skipping the first 6 hours | 1854 | 848 | +$2.23 | -$8.99 | +$13.50 |
| end price (above / below / between), gap 5c+, any hour of the chart | 6152 | 4642 | +$36.40 | +$29.45 | +$43.37 |
| end price (above / below / between), gap 5c+, skipping the first 6 hours | 4901 | 3168 | +$20.95 | +$9.17 | +$32.78 |

## 3. The real test: prices people really paid

Every real trade of the markets, in 5-minute steps, in a fixed shuffled order that has nothing to do with the results. The first 3000 markets were used to look around; the other 11077 were only opened once, for the rules marked "fixed before". Rule: every 5 minutes with a real trade, Polymarket's price = the last trade, the coin = Binance's last finished minute, swing size = Deribit's DVOL. If they disagree by the gap, buy the cheap side at the first real trade of a later 5 minutes (within 30 min), + 1c + the fee. One bet per market, $10 each.

### Who is closer, on real trades (one random look per market)

| kind | markets | options miss | Polymarket miss | half-half miss | when 5c+ apart: markets | options miss | Polymarket miss |
|---|---|---|---|---|---|---|---|
| end price | 5277 | 0.0844 | 0.0836 | 0.0829 | 1110 | 0.1118 | 0.1113 |
| touch | 3042 | 0.1080 | 0.1080 | 0.1056 | 1409 | 0.1338 | 0.1333 |

("Miss" = average squared distance between the forecast and what happened; smaller is better.)

### Markets used to look around: 3000

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| end price, 6h+ left, gap 3c+ | 851 | 333 | -$8.14 | -$13.89 | -$2.40 |
| end price, 6h+ left, gap 5c+ | 697 | 277 | -$7.99 | -$22.67 | +$6.68 |
| &nbsp;&nbsp;buy Yes | 299 | 95 | -$9.59 | -$35.03 | +$15.69 |
| &nbsp;&nbsp;buy No | 398 | 182 | -$6.78 | -$15.42 | +$1.91 |
| &nbsp;&nbsp;price did not run away (2c or less) | 376 | 143 | +$0.60 | -$13.73 | +$14.98 |
| end price, 6h+ left, gap 10c+ | 264 | 127 | +$1.65 | -$7.45 | +$10.76 |
| end price, last 30 min to 6 hours, gap 5c+ | 299 | 169 | +$1.14 | -$10.92 | +$13.25 |
| end price, 6h+ left, gap 5c+, swing size x0.8 | 720 | 473 | +$0.41 | +$1.30 | -$0.47 |
| end price, 6h+ left, gap 5c+, swing size x1.2 | 855 | 275 | -$8.83 | -$20.64 | +$3.00 |
| touch, 6h+ left, gap 3c+ | 587 | 309 | +$2.27 | -$10.42 | +$14.99 |
| touch, 6h+ left, gap 5c+ | 517 | 255 | -$0.20 | -$11.75 | +$11.35 |
| &nbsp;&nbsp;buy Yes | 366 | 140 | +$1.98 | -$14.68 | +$18.72 |
| &nbsp;&nbsp;buy No | 151 | 115 | -$5.62 | -$2.46 | -$8.74 |
| &nbsp;&nbsp;price did not run away (2c or less) | 301 | 133 | -$8.25 | -$12.42 | -$4.10 |
| touch, 6h+ left, gap 10c+ | 360 | 170 | +$5.04 | -$6.58 | +$16.65 |
| touch, last 30 min to 6 hours, gap 5c+ | 129 | 66 | +$17.73 | +$9.41 | +$25.91 |
| touch, 6h+ left, gap 5c+, swing size x0.8 | 551 | 374 | +$4.65 | +$3.16 | +$6.14 |
| touch, 6h+ left, gap 5c+, swing size x1.2 | 565 | 220 | +$0.84 | -$19.47 | +$21.24 |

### Fresh markets (rules fixed before): 11077

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| end price, 6h+ left, gap 3c+ | 3051 | 1195 | -$3.74 | -$4.65 | -$2.83 |
| end price, 6h+ left, gap 5c+ | 2425 | 972 | -$1.87 | -$4.90 | +$1.18 |
| &nbsp;&nbsp;buy Yes | 1034 | 322 | +$1.05 | -$16.84 | +$19.01 |
| &nbsp;&nbsp;buy No | 1391 | 650 | -$4.06 | +$2.11 | -$10.23 |
| &nbsp;&nbsp;price did not run away (2c or less) | 1306 | 485 | +$1.38 | -$8.62 | +$11.43 |
| end price, 6h+ left, gap 10c+ | 934 | 386 | -$3.59 | -$6.81 | -$0.37 |
| end price, last 30 min to 6 hours, gap 5c+ | 1011 | 611 | +$5.53 | -$3.09 | +$14.18 |
| end price, 6h+ left, gap 5c+, swing size x0.8 | 2474 | 1607 | -$1.49 | -$3.65 | +$0.67 |
| end price, 6h+ left, gap 5c+, swing size x1.2 | 2992 | 912 | -$2.91 | +$0.10 | -$5.93 |
| touch, 6h+ left, gap 3c+ | 2174 | 1080 | +$1.58 | -$5.09 | +$8.29 |
| touch, 6h+ left, gap 5c+ | 1947 | 948 | +$2.33 | -$2.68 | +$7.37 |
| &nbsp;&nbsp;buy Yes | 1290 | 430 | +$1.25 | -$4.78 | +$7.32 |
| &nbsp;&nbsp;buy No | 657 | 518 | +$4.53 | +$3.56 | +$5.49 |
| &nbsp;&nbsp;price did not run away (2c or less) | 1163 | 507 | +$7.14 | +$5.74 | +$8.55 |
| touch, 6h+ left, gap 10c+ | 1313 | 592 | -$0.24 | -$7.40 | +$6.96 |
| touch, last 30 min to 6 hours, gap 5c+ | 433 | 225 | -$8.90 | +$2.12 | -$19.94 |
| touch, 6h+ left, gap 5c+, swing size x0.8 | 2079 | 1454 | +$4.66 | +$3.98 | +$5.34 |
| touch, 6h+ left, gap 5c+, swing size x1.2 | 2096 | 736 | -$0.76 | -$8.50 | +$7.03 |

## 4. The exam

- **Options price vs Polymarket: BTC/ETH end-price markets, 5c+ apart, real trades**: 3122 bets, -$3.23 per $100, verdict **Behind, but could be bad luck**.
- **Options price vs Polymarket: BTC/ETH reach/dip markets, 5c+ apart, real trades**: 2464 bets, +$1.80 per $100, verdict **Ahead, but could be luck**.
- **Options price vs Polymarket: reach/dip, last 30 min to 6 hours (fresh markets only)**: 433 bets, -$8.90 per $100, verdict **Behind, but could be bad luck**.

