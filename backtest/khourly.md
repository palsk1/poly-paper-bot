# The real Kalshi bot's rule on the hourly and daily crypto rounds (23 Nov 2026, Jan's ask)

Jan asked how to grow the real Kalshi bot (`kc_maker_safe_usd`, about $1-2 a day at $4 bids on the 15-minute rounds).
More bots or accounts don't help: they fight over the same few sellers. So this tests the same rule on rounds
with their own sellers: Kalshi's hourly and daily crypto rounds, and the same kind of rounds on Polymarket.
Research only, paper only. Nothing was built and no track was added.

Code: `khourly.py` (`scan`, `fetch`, `run`, `pmfetch`, `pmrun`, `queue`; probes `khr_*`). Data: `bt_cache/khr/` in the price store.

## In plain words

- **No. The rule does not carry over to the hourly rounds.** In 61 days, on 6 coins, with the real bot's 2.3
  cushion bar it found about **2 bets a day** (the 15-minute rounds give about 100), and it **lost money: 7 lost
  of 121 bets, -$16.86 at $4 bids** (-$3.76 for every $100 bet). Bars 2.0 and 2.5 lose too (-$25.94 and -$8.79).
  Bigger bids only lose more: -$188.89 at $40 bids. The exam says "Losing" at 2.0 and "Behind, but could be bad
  luck" at 2.3 and 2.5. None is ahead.
- **Why it is different there: prices move in whole cents.** On the 15-minute rounds a safe side trades at 97.3c,
  98.6c and so on, and the bot steps one tenth of a cent in front. On the hourly rounds the smallest step is 1c.
  A side as safe as our rule wants is already priced at 99c to buy and $1.00 to sell. It only shows up at
  95c-98c when the coin has just started sliding toward the line. So the few bets the rule finds are the bad
  ones. Example: 27 Sep, bitcoin, 3 minutes left, cushion 3.3: the price had sat at 99c for 10 minutes, dipped to
  98c, the rule bid, and bitcoin fell $90 in 3 minutes and settled $8 under the line.
- **The one opening left is the 99c line, and it is small and crowded.** On bitcoin about 274 markets a day sit
  at "99c bid, $1.00 ask" with a 2.3+ cushion and 3 minutes left. Only 8 of 16,666 lost. A bid there wins 1c a
  contract: 4c on a $4 bid. But you join the back of a line of other buyers at 99c. In half of those markets
  nobody sold a single contract at 99c after our bid. And the sellers who do sell under 99c are the ones who see
  the coin turning: counting only fills we can be sure of, 8 of 188 lost (-$3.29 per $100).
  - If we were magically always FIRST in line: about +$2.20 a day on bitcoin at $4 bids, +$0.54 on ether.
  - Counting only the sure fills: about -$0.38 a day on bitcoin.
  - The truth is in between, and depends on how long the line really is. History doesn't record that, so a live
    watch of the real line ran for 4 hours on 23-24 Nov: see "The live line" below.
- **Daily rounds: there aren't separate ones.** Kalshi's "daily" bitcoin bet is just the 5 PM New York hourly
  round, open longer. 61 of them, 11 signals, 6 bets. Nothing there.
- **The smaller coins are tiny.** A middle bitcoin hour trades about 1.4 million contracts. Ether 33,000, Solana
  7,600, XRP 2,000, BNB 300. (A bitcoin 15-minute round trades about 4 million.) Dogecoin's hourly list came back
  empty and was left out.
- **Polymarket: also no.** It has an hourly "up or down" round (settled on Chainlink's price since about 18 Nov,
  on Binance's hourly candle before) and a daily "above $X at noon New York" ladder (settled on Binance). Hourly:
  33 bets in 30 days at the 2.3 bar, none lost, +$1.13 at $4 bids (+$10.89 at $40). That is 1 bet a day and far
  too few to trust ("Ahead, but could be luck"; one loss would wipe out 100 wins). Daily ladder: 7 signals in
  54 days and not one fill. Nobody sells at 95-99c in the last minutes there.
- **So where can the bot grow?** Not here. The honest list: (1) the 15-minute rounds of the two coins it does
  not bid on yet (Kalshi lists NEAR and Zcash 15-minute rounds, each about as busy as BNB or HYPE: about
  5 million contracts a day), which use the same fine prices and would be a small, cheap history test; (2) a
  second look at bid size on the coins it already has. Neither was tested here.

## The numbers, straight from the run

"Tape fills" = a bet only counts with contracts that were really sold into bids after ours: everything sold
below our price, plus sales at our price when we were alone at a new price. Sales at a price we merely joined are
not counted, because the line in front of us is unknown. "Candle fills" = the older `kcrypto.py` model, for comparison.
"Bar" = the cushion needed after the Binance-vs-Kalshi gap fix (the plain Binance cushion must also be 2.0+).

Data: KXBTCD, KXETHD, KXSOLD, KXXRPD, KXBNBD, KXHYPED; 2026-09-24 01:00 to 2026-11-23 21:33 UTC (61 days)
  KXBTCD: 1425 rounds (61 open longer than 2 hours), contracts a round: middle 1,372,671, busiest 10,249,972; 23073 markets with candles, 9213 trade lists, 86636 minutes of Kalshi's number
  KXETHD: 1424 rounds (60 open longer than 2 hours), contracts a round: middle 32,677, busiest 1,225,675; 12911 markets with candles, 4829 trade lists, 86636 minutes of Kalshi's number
  KXSOLD: 1423 rounds (60 open longer than 2 hours), contracts a round: middle 7,603, busiest 158,718; 10607 markets with candles, 1744 trade lists, 86576 minutes of Kalshi's number
  KXXRPD: 1423 rounds (60 open longer than 2 hours), contracts a round: middle 1,966, busiest 69,872; 2182 markets with candles, 361 trade lists, 86576 minutes of Kalshi's number
  KXBNBD: 1423 rounds (60 open longer than 2 hours), contracts a round: middle 323, busiest 583,060; 3841 markets with candles, 539 trade lists, 86576 minutes of Kalshi's number
  KXHYPED: 1423 rounds (60 open longer than 2 hours), contracts a round: middle 1,236, busiest 107,724; 7950 markets with candles, 1188 trade lists, 86576 minutes of Kalshi's number

## A. All coins together: minutes left x cushion bar ($4 bids, tape fills)
| Min left | Bar | Signals | Bets filled | Filled in full | Lost | Per $100 | Profit | Bets a day | $ a day | Most $ out in one round |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | no check | 3008 | 1151 | 1067 | 60 | -$2.47 | -$105.85 | 18.9 | -$1.74 | $19 |
| 2 | 2.0 | 332 | 86 | 75 | 5 | -$3.91 | -$12.06 | 1.4 | -$0.20 | $12 |
| 2 | 2.3 | 206 | 59 | 52 | 4 | -$5.12 | -$10.73 | 1.0 | -$0.18 | $12 |
| 2 | 2.5 | 142 | 39 | 36 | 4 | -$8.68 | -$12.45 | 0.6 | -$0.20 | $12 |
| 3 | no check | 3878 | 1631 | 1510 | 66 | -$1.19 | -$72.20 | 26.8 | -$1.19 | $20 |
| 3 | 2.0 | 581 | 191 | 170 | 11 | -$3.69 | -$25.94 | 3.1 | -$0.43 | $13 |
| 3 | 2.3 | 349 | 121 | 108 | 7 | -$3.76 | -$16.86 | 2.0 | -$0.28 | $13 |
| 3 | 2.5 | 236 | 78 | 69 | 4 | -$3.06 | -$8.79 | 1.3 | -$0.14 | $13 |
| 5 | no check | 5444 | 2245 | 2095 | 94 | -$1.34 | -$112.43 | 36.9 | -$1.85 | $32 |
| 5 | 2.0 | 1196 | 332 | 304 | 18 | -$3.19 | -$39.44 | 5.5 | -$0.65 | $19 |
| 5 | 2.3 | 769 | 189 | 177 | 10 | -$3.01 | -$21.45 | 3.1 | -$0.35 | $19 |
| 5 | 2.5 | 550 | 124 | 114 | 6 | -$2.57 | -$11.92 | 2.0 | -$0.20 | $19 |

## B. By coin, 3 minutes left ($4 bids, tape fills)
| Coin | Bar | Signals | Bets filled | Lost | Per $100 | Profit | Bets a day | $ a day |
|---|---|---|---|---|---|---|---|---|
| KXBTCD | 2.0 | 227 | 89 | 4 | -$2.11 | -$7.27 | 1.5 | -$0.12 |
| KXBTCD | 2.3 | 137 | 57 | 3 | -$2.95 | -$6.47 | 0.9 | -$0.11 |
| KXBTCD | 2.5 | 95 | 39 | 2 | -$2.80 | -$4.23 | 0.6 | -$0.07 |
| KXETHD | 2.0 | 122 | 45 | 4 | -$7.07 | -$12.02 | 0.7 | -$0.20 |
| KXETHD | 2.3 | 74 | 33 | 2 | -$4.21 | -$5.18 | 0.5 | -$0.09 |
| KXETHD | 2.5 | 44 | 18 | 1 | -$3.88 | -$2.50 | 0.3 | -$0.04 |
| KXSOLD | 2.0 | 79 | 30 | 2 | -$4.81 | -$4.95 | 0.5 | -$0.08 |
| KXSOLD | 2.3 | 37 | 12 | 1 | -$6.56 | -$2.74 | 0.2 | -$0.05 |
| KXSOLD | 2.5 | 25 | 7 | 0 | +$3.51 | +$0.78 | 0.1 | +$0.01 |
| KXXRPD | 2.0 | 21 | 7 | 1 | -$17.82 | -$3.47 | 0.1 | -$0.06 |
| KXXRPD | 2.3 | 11 | 5 | 1 | -$24.97 | -$3.66 | 0.1 | -$0.06 |
| KXXRPD | 2.5 | 7 | 3 | 1 | -$43.05 | -$3.78 | 0.0 | -$0.06 |
| KXBNBD | 2.0 | 60 | 3 | 0 | +$3.31 | +$0.32 | 0.0 | +$0.01 |
| KXBNBD | 2.3 | 47 | 2 | 0 | +$2.74 | +$0.16 | 0.0 | +$0.00 |
| KXBNBD | 2.5 | 37 | 1 | 0 | +$2.04 | +$0.08 | 0.0 | +$0.00 |
| KXHYPED | 2.0 | 72 | 17 | 0 | +$2.56 | +$1.45 | 0.3 | +$0.02 |
| KXHYPED | 2.3 | 43 | 12 | 0 | +$2.40 | +$1.03 | 0.2 | +$0.02 |
| KXHYPED | 2.5 | 28 | 10 | 0 | +$2.38 | +$0.86 | 0.2 | +$0.01 |

## C. Bid size, 3 minutes left, all coins (tape fills: only what was really sold to us)
| Bar | Bid size | Bets with any fill | Filled in full | Lost | $ really bought | Per $100 | Profit | $ a day | Most $ out in one round | Usual $ out in a round |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 | $4 | 191 | 170 | 11 | $703 | -$3.69 | -$25.94 | -$0.43 | $13 | $4 |
| 2.0 | $10 | 191 | 160 | 11 | $1,658 | -$4.06 | -$67.34 | -$1.11 | $29 | $10 |
| 2.0 | $20 | 191 | 147 | 11 | $3,145 | -$4.42 | -$139.15 | -$2.29 | $59 | $20 |
| 2.0 | $40 | 191 | 127 | 11 | $5,824 | -$5.06 | -$294.64 | -$4.84 | $118 | $39 |
| 2.3 | $4 | 121 | 108 | 7 | $448 | -$3.76 | -$16.86 | -$0.28 | $13 | $4 |
| 2.3 | $10 | 121 | 102 | 7 | $1,057 | -$4.14 | -$43.75 | -$0.72 | $29 | $10 |
| 2.3 | $20 | 121 | 94 | 7 | $2,006 | -$4.50 | -$90.32 | -$1.48 | $59 | $20 |
| 2.3 | $40 | 121 | 81 | 7 | $3,722 | -$5.08 | -$188.89 | -$3.10 | $118 | $39 |
| 2.5 | $4 | 78 | 69 | 4 | $287 | -$3.06 | -$8.79 | -$0.14 | $13 | $4 |
| 2.5 | $10 | 78 | 66 | 4 | $683 | -$3.34 | -$22.83 | -$0.38 | $29 | $10 |
| 2.5 | $20 | 78 | 61 | 4 | $1,302 | -$3.64 | -$47.39 | -$0.78 | $59 | $20 |
| 2.5 | $40 | 78 | 51 | 4 | $2,402 | -$4.21 | -$101.10 | -$1.66 | $118 | $39 |

## D. By our price, 3 minutes left, bar 2.3 ($4 bids)
| Our price | Signals | Front of the line | Bets filled (tape) | Lost | Per $100 | Profit | Candle-model bets | Candle per $100 |
|---|---|---|---|---|---|---|---|---|
| 95c-96c | 52 | 23 | 16 | 1 | -$2.90 | -$1.64 | 16 | -$2.34 |
| 97c | 70 | 32 | 21 | 0 | +$3.09 | +$2.34 | 21 | +$3.09 |
| 98c | 227 | 63 | 84 | 6 | -$5.56 | -$17.56 | 85 | -$5.16 |
| 99c | 0 | 0 | 0 | 0 | +$0.00 | +$0.00 | 0 | +$0.00 |

## E. Other ways to cut it, 3 minutes left ($4 bids, tape fills)
| Version | Signals | Bets filled | Lost | Per $100 | Profit | $ a day |
|---|---|---|---|---|---|---|
| bar 2.3, candle fills (kcrypto 'fair' model) | 349 | 122 | 7 | -$3.39 | -$16.12 | -$0.26 |
| bar 2.3, one bet a round and coin (nearest the line) | 327 | 110 | 7 | -$4.39 | -$17.83 | -$0.29 |
| bar 2.3, only prices under 99c | 349 | 121 | 7 | -$3.76 | -$16.86 | -$0.28 |
| bar 2.3, only yes side | 238 | 82 | 5 | -$4.18 | -$12.57 | -$0.21 |
| bar 2.3, only no side | 111 | 39 | 2 | -$2.91 | -$4.29 | -$0.07 |
| Binance check only, 2.0 (kc_maker_safe) | 1575 | 641 | 25 | -$1.16 | -$27.82 | -$0.46 |
| Kalshi's own number 2.0 (kprice twin) | 1101 | 393 | 17 | -$1.92 | -$28.48 | -$0.47 |
| Kalshi's own number 3.0 | 160 | 59 | 5 | -$6.43 | -$14.56 | -$0.24 |
| bar 3.0 | 99 | 28 | 3 | -$8.81 | -$9.37 | -$0.15 |
| bar 4.0 | 23 | 5 | 0 | +$2.21 | +$0.41 | +$0.01 |
| bar 2.3, rounds open longer than 2 hours (the 'daily' ones) | 11 | 6 | 0 | +$3.09 | +$0.72 | +$0.01 |

## F. Every lost bet, 3 minutes left, bar 2.0 (tape fills)
| Round closes (UTC) | Market | Side | Our price | Cushion Binance | After the gap fix | On Kalshi's number | Sold to us |
|---|---|---|---|---|---|---|---|
| 2026-09-24 22:00 | KXXRPD-26SEP2418-T1.5399 | yes | 98c | 3.52 | 3.19 | 3.28 | 472 |
| 2026-09-27 13:00 | KXBTCD-26SEP2709-T84799.99 | yes | 98c | 4.65 | 3.30 | 3.81 | 36,005 |
| 2026-09-29 17:00 | KXSOLD-26SEP2913-T117.9999 | no | 98c | 2.43 | 2.47 | 2.26 | 260 |
| 2026-10-05 04:00 | KXETHD-26OCT0500-T2714.99 | yes | 98c | 2.62 | 2.34 | 2.20 | 2,466 |
| 2026-10-07 02:00 | KXETHD-26OCT0622-T2669.99 | yes | 98c | 3.20 | 3.02 | 4.83 | 1,366 |
| 2026-10-29 20:00 | KXSOLD-26OCT2916-T99.7499 | yes | 97c | 3.37 | 2.10 | 1.66 | 3,892 |
| 2026-11-02 16:00 | KXBTCD-26NOV0211-T77399.99 | yes | 98c | 3.31 | 2.06 | 2.09 | 75,397 |
| 2026-11-04 00:00 | KXBTCD-26NOV0319-T77399.99 | yes | 98c | 4.48 | 2.50 | 3.20 | 80,535 |
| 2026-11-04 00:00 | KXETHD-26NOV0319-T2274.99 | yes | 97c | 3.68 | 2.23 | 2.63 | 3,344 |
| 2026-11-16 12:00 | KXETHD-26NOV1607-T1804.99 | yes | 97c | 3.41 | 2.08 | 2.08 | 3,384 |
| 2026-11-23 14:00 | KXBTCD-26NOV2309-T62899.99 | no | 96c | 2.19 | 2.53 | 3.92 | 15,351 |

## H. The 99c line: markets with no seller under $1.00, 3 minutes left (a joined bid at 99c wins 1c a contract)
| Coin | Bar | Signals a day | Lost, of all signals | Sure fills (something sold under our price): bets / lost / per $100 | Best case (any sale at our price fills us): bets / lost / per $100 | Trade lists read | Contracts sold at our price after our bid: middle market | Markets with 100+ sold | with 1,000+ sold |
|---|---|---|---|---|---|---|---|---|---|
| KXBTCD | 2.0 | 277 | 8 of 16859 | 228 / 8 / -$2.53 | 4506 / 8 / +$0.83 | 6242 | 0 | 1229 | 558 |
| KXBTCD | 2.3 | 274 | 8 of 16666 | 188 / 8 / -$3.29 | 4331 / 8 / +$0.82 | 6121 | 0 | 1132 | 498 |
| KXBTCD | 2.5 | 271 | 7 of 16487 | 156 / 7 / -$3.52 | 4176 / 7 / +$0.84 | 5996 | 0 | 1032 | 436 |
| KXETHD | 2.0 | 122 | 3 of 7410 | 266 / 3 / -$0.01 | 1116 / 3 / +$0.77 | 2844 | 0 | 190 | 20 |
| KXETHD | 2.3 | 119 | 2 of 7242 | 230 / 2 / +$0.26 | 1024 / 2 / +$0.84 | 2742 | 0 | 165 | 18 |
| KXETHD | 2.5 | 116 | 2 of 7079 | 202 / 2 / +$0.14 | 936 / 2 / +$0.82 | 2635 | 0 | 141 | 12 |
| KXSOLD | 2.0 | 89 | 5 of 5388 | 329 / 5 / +$0.28 | 647 / 5 / +$0.64 | 328 | 0 | 6 | 0 |
| KXSOLD | 2.3 | 86 | 5 of 5236 | 287 / 5 / +$0.03 | 587 / 5 / +$0.53 | 275 | 0 | 4 | 0 |
| KXSOLD | 2.5 | 84 | 5 of 5112 | 259 / 5 / -$0.19 | 549 / 5 / +$0.45 | 234 | 0 | 4 | 0 |
| KXXRPD | 2.0 | 22 | 1 of 1334 | 73 / 1 / +$0.19 | 170 / 1 / +$0.66 | 80 | 0 | 3 | 0 |
| KXXRPD | 2.3 | 22 | 1 of 1311 | 70 / 1 / +$0.15 | 166 / 1 / +$0.65 | 72 | 0 | 3 | 0 |
| KXXRPD | 2.5 | 21 | 1 of 1288 | 67 / 1 / +$0.06 | 160 / 1 / +$0.61 | 63 | 0 | 3 | 0 |
| KXBNBD | 2.0 | 41 | 2 of 2474 | 73 / 2 / -$1.55 | 388 / 2 / +$0.53 | 148 | 0 | 0 | 0 |
| KXBNBD | 2.3 | 40 | 2 of 2442 | 66 / 2 / -$1.83 | 380 / 2 / +$0.52 | 137 | 0 | 0 | 0 |
| KXBNBD | 2.5 | 40 | 2 of 2420 | 62 / 2 / -$2.06 | 376 / 2 / +$0.51 | 126 | 0 | 0 | 0 |
| KXHYPED | 2.0 | 45 | 4 of 2740 | 196 / 4 / -$0.23 | 241 / 4 / +$0.00 | 259 | 0 | 0 | 0 |
| KXHYPED | 2.3 | 43 | 4 of 2610 | 168 / 4 / -$0.64 | 208 / 4 / -$0.32 | 223 | 0 | 0 | 0 |
| KXHYPED | 2.5 | 41 | 4 of 2498 | 145 / 4 / -$1.02 | 181 / 4 / -$0.62 | 198 | 0 | 0 | 0 |
| all | 2.0 | 595 | 23 of 36205 | 1165 / 23 / -$0.54 | 7068 / 23 / +$0.75 | 9901 | 0 | 1428 | 578 |
| all | 2.3 | 583 | 22 of 35507 | 1009 / 22 / -$0.77 | 6696 / 22 / +$0.74 | 9570 | 0 | 1304 | 516 |
| all | 2.5 | 573 | 21 of 34884 | 891 / 21 / -$0.95 | 6378 / 21 / +$0.74 | 9252 | 0 | 1180 | 448 |

## H2. The 99c line if we were always FIRST in it (we would not be: the best case), bar 2.3, 3 minutes left, scaled up from the rounds whose trade lists were read
| Coin | Bid size | Bids a day | Bids that get anything | Lost | $ bought a day | Wins a day, best case | Wins a day counting only sales BELOW our price (the sure ones) | Losses a day (every loser of the full 61 days fills in full) | Best case after losses | Sure fills after losses |
|---|---|---|---|---|---|---|---|---|---|---|
| KXBTCD | $4 | 279 | 72 | 8 in 61 days | $270 | +$2.72 | +$0.14 | -$0.52 | +$2.20 | -$0.38 |
| KXBTCD | $10 | 279 | 72 | 8 in 61 days | $636 | +$6.43 | +$0.36 | -$1.30 | +$5.13 | -$0.95 |
| KXBTCD | $20 | 279 | 72 | 8 in 61 days | $1,199 | +$12.11 | +$0.70 | -$2.60 | +$9.51 | -$1.91 |
| KXBTCD | $40 | 279 | 72 | 8 in 61 days | $2,211 | +$22.33 | +$1.34 | -$5.21 | +$17.13 | -$3.86 |
| KXETHD | $4 | 121 | 18 | 2 in 61 days | $65 | +$0.67 | +$0.16 | -$0.13 | +$0.54 | +$0.03 |
| KXETHD | $10 | 121 | 18 | 2 in 61 days | $150 | +$1.56 | +$0.36 | -$0.33 | +$1.23 | +$0.03 |
| KXETHD | $20 | 121 | 18 | 2 in 61 days | $271 | +$2.82 | +$0.64 | -$0.65 | +$2.17 | -$0.01 |
| KXETHD | $40 | 121 | 18 | 2 in 61 days | $473 | +$4.90 | +$1.11 | -$1.30 | +$3.60 | -$0.19 |

## I. Bidding earlier in the hour (candles only, bar 2.3, all coins)
| Min left | Bids of 95c-98c: signals / sure fills / lost / per $100 | 99c line: signals a day / lost of all / sure fills: bets, lost, per $100 / best case: bets, lost, per $100 |
|---|---|---|
| 3 | 349 / 122 / 7 / -$3.39 | 583 / 22 of 35507 / 1009 / 22 / -$0.77 / 6696 / 22 / +$0.74 |
| 5 | 769 / 199 / 10 / -$2.55 | 516 / 32 of 31402 / 1373 / 32 / -$0.98 / 6939 / 32 / +$0.62 |
| 10 | 1848 / 510 / 13 / -$0.03 | 398 / 68 of 24207 / 1908 / 68 / -$2.25 / 6817 / 68 / +$0.10 |
| 20 | 3334 / 1063 / 27 / -$0.02 | 254 / 68 of 15442 / 2576 / 68 / -$1.35 / 6211 / 68 / +$0.03 |

## G. The exam

```
=== EXAM: kc_maker_safe_usd on Kalshi hourly crypto rounds, bar 2.0 (history, 3 min, $4 bids) ===
Verdict: Losing
Bets: 191 bets on 161 events over 57 days. Counted as 161 separate bets (bets on the same event count once).
Result: -$3.69 per $100 bet (total -$25.94 on $702.94). Luck range -$6.97 to -$0.41.
Halves: first -$3.47, second -$3.88 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 285 tries. The luckiest of 285 worthless ideas would show about +$7.58 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$12.33. Below $0: not proven.

=== EXAM: kc_maker_safe_usd on Kalshi hourly crypto rounds, bar 2.3 (history, 3 min, $4 bids) ===
Verdict: Behind, but could be bad luck
Bets: 121 bets on 105 events over 46 days. Counted as 105 separate bets (bets on the same event count once).
Result: -$3.76 per $100 bet (total -$16.86 on $447.86). Luck range -$7.60 to +$0.07.
Halves: first -$6.91, second -$0.94 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 286 tries. The luckiest of 286 worthless ideas would show about +$8.35 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$12.95. Below $0: not proven.

=== EXAM: kc_maker_safe_usd on Kalshi hourly crypto rounds, bar 2.5 (history, 3 min, $4 bids) ===
Verdict: Behind, but could be bad luck
Bets: 78 bets on 68 events over 35 days. Counted as 68 separate bets (bets on the same event count once).
Result: -$3.06 per $100 bet (total -$8.79 on $286.79). Luck range -$7.61 to +$1.48.
Halves: first -$6.36, second -$0.15 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 287 tries. The luckiest of 287 worthless ideas would show about +$10.30 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$14.67. Below $0: not proven.
```

## P. Polymarket ($4 and $40 bids, filled only by later real trades)
| Rounds | Min left | Bar | Signals | Bets filled | Lost | Per $100 | Profit at $4 | Days | Bets a day | Profit at $40 bids |
|---|---|---|---|---|---|---|---|---|---|---|
| hourly up / down | 2 | no check | 159 | 52 | 2 | -$1.67 | -$3.27 | 30 | 1.7 | -$39.58 |
| hourly up / down | 2 | 2.0 | 102 | 27 | 1 | -$2.07 | -$2.16 | 30 | 0.9 | -$24.11 |
| hourly up / down | 2 | 2.3 | 75 | 21 | 1 | -$3.46 | -$2.79 | 30 | 0.7 | -$29.57 |
| hourly up / down | 2 | 2.5 | 64 | 16 | 1 | -$5.33 | -$3.26 | 30 | 0.5 | -$33.84 |
| hourly up / down | 3 | no check | 281 | 90 | 3 | -$1.70 | -$5.91 | 30 | 3.0 | -$71.06 |
| hourly up / down | 3 | 2.0 | 191 | 43 | 0 | +$0.99 | +$1.63 | 30 | 1.4 | +$15.86 |
| hourly up / down | 3 | 2.3 | 158 | 33 | 0 | +$0.90 | +$1.13 | 30 | 1.1 | +$10.89 |
| hourly up / down | 3 | 2.5 | 139 | 27 | 0 | +$0.94 | +$0.96 | 30 | 0.9 | +$9.13 |
| hourly up / down | 5 | no check | 142 | 71 | 1 | +$0.32 | +$0.88 | 29 | 2.4 | +$3.17 |
| hourly up / down | 5 | 2.0 | 84 | 40 | 0 | +$1.07 | +$1.68 | 29 | 1.4 | +$14.04 |
| hourly up / down | 5 | 2.3 | 64 | 28 | 0 | +$0.86 | +$0.94 | 29 | 1.0 | +$8.06 |
| hourly up / down | 5 | 2.5 | 52 | 21 | 0 | +$0.63 | +$0.52 | 29 | 0.7 | +$4.67 |
| daily noon ladder | 2 | no check | 6 | 2 | 0 | +$1.53 | +$0.12 | 35 | 0.1 | +$1.20 |
| daily noon ladder | 2 | 2.0 | 6 | 2 | 0 | +$1.53 | +$0.12 | 35 | 0.1 | +$1.20 |
| daily noon ladder | 2 | 2.3 | 5 | 1 | 0 | +$0.11 | +$0.00 | 35 | 0.0 | +$0.01 |
| daily noon ladder | 2 | 2.5 | 5 | 1 | 0 | +$0.11 | +$0.00 | 35 | 0.0 | +$0.01 |
| daily noon ladder | 3 | no check | 8 | 0 | 0 | +$0.00 | +$0.00 | 54 | 0.0 | +$0.00 |
| daily noon ladder | 3 | 2.0 | 8 | 0 | 0 | +$0.00 | +$0.00 | 54 | 0.0 | +$0.00 |
| daily noon ladder | 3 | 2.3 | 7 | 0 | 0 | +$0.00 | +$0.00 | 54 | 0.0 | +$0.00 |
| daily noon ladder | 3 | 2.5 | 7 | 0 | 0 | +$0.00 | +$0.00 | 54 | 0.0 | +$0.00 |
| daily noon ladder | 5 | no check | 12 | 3 | 0 | +$0.93 | +$0.11 | 51 | 0.1 | +$1.10 |
| daily noon ladder | 5 | 2.0 | 11 | 2 | 0 | +$0.70 | +$0.06 | 51 | 0.0 | +$0.56 |
| daily noon ladder | 5 | 2.3 | 11 | 2 | 0 | +$0.70 | +$0.06 | 51 | 0.0 | +$0.56 |
| daily noon ladder | 5 | 2.5 | 10 | 2 | 0 | +$0.70 | +$0.06 | 51 | 0.0 | +$0.56 |


```
=== EXAM: kc_maker_safe_usd on Polymarket hourly up / down crypto rounds, bar 2.3 (history, 3 min, $4 bids) ===
Verdict: Ahead, but could be luck
Bets: 33 bets on 31 events over 19 days. Counted as 31 separate bets (bets on the same event count once).
Result: +$0.90 per $100 bet (total +$1.13 on $125.87). Luck range +$0.66 to +$1.15. No losing bet seen yet, so that range is too kind: go by the worst case below.
Halves: first +$0.84, second +$0.96 per $100. Both ahead.
Luck bar: this is 1 of 288 tries. The luckiest of 288 worthless ideas would show about +$10.48 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$12.66. Below $0: not proven.
To prove it: can't say. It isn't ahead once one more disaster is added.

=== EXAM: kc_maker_safe_usd on Polymarket daily noon ladder crypto rounds, bar 2.3 (history, 3 min, $4 bids) ===
Verdict: Too early to tell
No bets to grade.
```

## The live line (23-24 Nov)

_To be filled in when the 4-hour watch finishes (`khourly.py queue`, probe `khr_queue_250`)._

## Two more 15-minute coins: NEAR and Zcash (the growth idea that is left)

Kalshi also runs 15-minute rounds for NEAR and Zcash. The bots don't bid on them. Each trades about as much
as BNB or HYPE, which the real bot already uses. Same rule, same 62 days, next to the 7 coins we have. Fills
here use the older, kinder candle rule (not trade lists), so read the dollars as "about", and compare coins
with each other rather than with the real bot's results.

- **NEAR at the 2.3 bar:** 763 bets, 2 lost, about +$10 in 62 days at $4 bids (17c a day).
- **Zcash at the 2.3 bar:** 707 bets, 1 lost, about +$11 (19c a day).
- Both look like the small coins the bot already bids on (BNB +19c a day, HYPE +27c a day in the same table).
  So adding both would add roughly a quarter to a third on top of today's bot. Exam verdict for both: "Ahead,
  but could be luck". No surprise: a 2-bets-lost difference decides the whole result.
- **Side finding, bitcoin:** in this same table the bitcoin 15-minute round is the only coin that is behind
  (6 lost of 552 at the 2.3 bar, about -$6). It is also the most crowded round by far. Worth a look at the
  real bot's own bitcoin results before anything is changed.
- Nothing was changed. Adding coins to the real bot or the paper tracks is Jan's call.

## N. Two more 15-minute coins: the same rule, 3 minutes left, candle fills, 2026-09-23 22:30 to 2026-11-19 16:45 UTC (57 days, $4 bids)
| Coin | Bar | Bets | Lost | 1 loss per | Per $100 | Profit at $4 bids | Bets a day | $ a day | Contracts a round (middle) |
|---|---|---|---|---|---|---|---|---|---|
| KXNEAR15M (new) | 2.0 | 939 | 3 | 313 | +$0.38 | +$14.38 | 16.5 | +$0.25 | 24,820 |
| KXNEAR15M (new) | 2.3 | 763 | 2 | 382 | +$0.34 | +$10.33 | 13.4 | +$0.18 | 24,820 |
| KXNEAR15M (new) | 2.5 | 637 | 1 | 637 | +$0.38 | +$9.82 | 11.2 | +$0.17 | 24,820 |
| KXZEC15M (new) | 2.0 | 869 | 2 | 434 | +$0.37 | +$12.76 | 15.3 | +$0.22 | 27,587 |
| KXZEC15M (new) | 2.3 | 707 | 1 | 707 | +$0.38 | +$10.71 | 12.5 | +$0.19 | 27,587 |
| KXZEC15M (new) | 2.5 | 617 | 1 | 617 | +$0.31 | +$7.70 | 10.9 | +$0.14 | 27,587 |
| KXBTC15M (the 7 we have) | 2.0 | 681 | 9 | 76 | -$0.38 | -$10.67 | 12.0 | -$0.19 | 3,119,607 |
| KXBTC15M (the 7 we have) | 2.3 | 552 | 6 | 92 | -$0.26 | -$5.82 | 9.7 | -$0.10 | 3,119,607 |
| KXBTC15M (the 7 we have) | 2.5 | 483 | 6 | 80 | -$0.46 | -$9.01 | 8.5 | -$0.16 | 3,119,607 |
| KXETH15M (the 7 we have) | 2.0 | 790 | 4 | 198 | +$0.19 | +$6.06 | 13.9 | +$0.11 | 196,945 |
| KXETH15M (the 7 we have) | 2.3 | 636 | 2 | 318 | +$0.29 | +$7.28 | 11.2 | +$0.13 | 196,945 |
| KXETH15M (the 7 we have) | 2.5 | 548 | 2 | 274 | +$0.19 | +$4.21 | 9.7 | +$0.07 | 196,945 |
| KXSOL15M (the 7 we have) | 2.0 | 911 | 2 | 456 | +$0.47 | +$17.29 | 16.0 | +$0.30 | 79,089 |
| KXSOL15M (the 7 we have) | 2.3 | 767 | 0 | 0 | +$0.61 | +$18.74 | 13.5 | +$0.33 | 79,089 |
| KXSOL15M (the 7 we have) | 2.5 | 674 | 0 | 0 | +$0.55 | +$14.82 | 11.9 | +$0.26 | 79,089 |
| KXXRP15M (the 7 we have) | 2.0 | 885 | 4 | 221 | +$0.32 | +$11.39 | 15.6 | +$0.20 | 97,680 |
| KXXRP15M (the 7 we have) | 2.3 | 750 | 2 | 375 | +$0.42 | +$12.73 | 13.2 | +$0.22 | 97,680 |
| KXXRP15M (the 7 we have) | 2.5 | 651 | 0 | 0 | +$0.63 | +$16.46 | 11.5 | +$0.29 | 97,680 |
| KXDOGE15M (the 7 we have) | 2.0 | 932 | 0 | 0 | +$0.70 | +$26.19 | 16.4 | +$0.46 | 48,082 |
| KXDOGE15M (the 7 we have) | 2.3 | 780 | 0 | 0 | +$0.60 | +$18.66 | 13.7 | +$0.33 | 48,082 |
| KXDOGE15M (the 7 we have) | 2.5 | 669 | 0 | 0 | +$0.55 | +$14.70 | 11.8 | +$0.26 | 48,082 |
| KXHYPE15M (the 7 we have) | 2.0 | 795 | 1 | 795 | +$0.56 | +$17.74 | 14.0 | +$0.31 | 31,427 |
| KXHYPE15M (the 7 we have) | 2.3 | 652 | 0 | 0 | +$0.59 | +$15.45 | 11.5 | +$0.27 | 31,427 |
| KXHYPE15M (the 7 we have) | 2.5 | 562 | 0 | 0 | +$0.54 | +$12.26 | 9.9 | +$0.22 | 31,427 |
| KXBNB15M (the 7 we have) | 2.0 | 716 | 2 | 358 | +$0.43 | +$12.49 | 12.6 | +$0.22 | 22,140 |
| KXBNB15M (the 7 we have) | 2.3 | 589 | 1 | 589 | +$0.45 | +$10.68 | 10.4 | +$0.19 | 22,140 |
| KXBNB15M (the 7 we have) | 2.5 | 496 | 1 | 496 | +$0.36 | +$7.14 | 8.7 | +$0.13 | 22,140 |

=== EXAM: kc_maker_safe_usd on KXNEAR15M, bar 2.3 (history, 3 min, candle fills) ===
Verdict: Ahead, but could be luck
Bets: 828 bets on 828 events over 62 days. Counted as 828 separate bets (bets on the same event count once).
Result: +$0.36 per $100 bet (total +$11.78 on $3292.22). Luck range +$0.07 to +$0.64.
Halves: first +$0.68, second +$0.04 per $100. Both ahead.
Luck bar: this is 1 of 236 tries. The luckiest of 236 worthless ideas would show about +$0.70 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$0.47. Below $0: not proven.
To prove it: about 6,518 more separate bets like these. At its pace (13.6 separate bets a day) that is around 2028-03-18, after 2027-01-01: too slow for the 1 Jan decision.

=== EXAM: kc_maker_safe_usd on KXZEC15M, bar 2.3 (history, 3 min, candle fills) ===
Verdict: Ahead, but could be luck
Bets: 754 bets on 754 events over 62 days. Counted as 754 separate bets (bets on the same event count once).
Result: +$0.39 per $100 bet (total +$11.67 on $3000.33). Luck range +$0.17 to +$0.61.
Halves: first +$0.57, second +$0.21 per $100. Both ahead.
Luck bar: this is 1 of 236 tries. The luckiest of 236 worthless ideas would show about +$0.63 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$0.37. Below $0: not proven.
To prove it: about 3,814 more separate bets like these. At its pace (12.4 separate bets a day) that is around 2027-09-28, after 2027-01-01: too slow for the 1 Jan decision.

## How it was tested, and what could be off

- 61 days (24 Sep-23 Nov 2026, as far back as Kalshi's normal endpoints go), every hourly "above X" round of
  bitcoin, ether, Solana, XRP, BNB and HYPE: one-minute bid / ask of every market near the line for the last 31
  minutes, Kalshi's own settle number every minute, Binance every minute, and every trade of the last 6 minutes
  of every market where the rule could bid at 95c-98c (plus every third round's 99c markets).
- The rule was written down in `khourly.py` before the first result: the 15-minute rule, unchanged, at 3 minutes
  left. The 15-minute rule reads the Binance-vs-Kalshi gap at the round's start line; an hourly round has no such
  line, so the gap is read at the last quarter hour from Kalshi's own number.
- About 60 cuts were looked at (minutes left, bars, coins, sides, prices, the 99c line). None of the 95c-98c
  cuts with more than 30 bets is ahead. Two tiny ones are (bar 4.0: 5 bets; HYPE: 12 bets); that is noise.
- The backward look (start from the losers): all 11 losers at bar 2.0 were bids at 96c-98c placed right after
  the price had dropped from 99c, 9 of 11 on the "yes" side (coin above the line and falling). The plain Binance
  cushion was 2.2 to 4.7 at those moments. A cushion measured on the last hour's calm does not see a slide that
  started a minute ago, and the market's own price does.
- Polymarket has no order-book history, so the bid there is rebuilt from the trades of the 15 seconds before we
  look (as in `backtest/pm15.md`). The hourly up/down changed its rules about 18 Nov; both versions are pooled.
- Makers pay no fee on any of these series (Kalshi `fee_type` quadratic, Polymarket taker-only), checked 23 Nov.
