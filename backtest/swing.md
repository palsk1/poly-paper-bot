# Buy and sell inside one crypto window (26 Nov 2026)

Jan: "What about a bot that buys and sells inside the 15 or 5 minute windows?" and "this one you will have to do loads of different tests for".

Paper research only. Nothing live was changed.

## Short answer

- **Buying a share and selling it again before the window ends loses money, on both sites, in every version tried.** 41,756 rule versions in all; 19,740 of them really sell inside the window (not counting the speed family below). 115 were ahead on the days they were picked from, and 6 of those were still ahead on days they had never seen. That is what luck alone gives.
- **Why:** a buy-then-sell on Polymarket costs about 5c a share at middle prices (1.4c gap between buyers and sellers + 3.5c in two fees). Kalshi is about the same (1.3c gap + 3.5c fees). The price would have to snap back by more than that, and it does not: after a jump, about a twentieth of it comes back in the next 30-60 seconds (a 10c jump gives back half a cent).
- **Selling early is the costly part.** For the same buys, getting out before the end (after a set time, at a take-profit, at a stop-loss, or with a waiting sell offer) did worse than just holding to the end in almost every rule, by $2 to $6 per $100. See "Selling early against holding".
- **Waiting offers on both legs do not rescue it.** Waiting bids get filled exactly when the price is falling through them. Of 9,432 waiting-bid versions, 4 were ahead on both halves of the days with sure fills and 5 even if we were always first in line; all of those are two days of SOL, and are late bids on the likely side held to the end, so not a swing at all.
- **The one family that is ahead on paper is the speed bot we already have** (the coin jumped, the share has not moved yet). It is a race: half a second late it shows +$10.56 per $100 on fresh days, one second late +$6.88, two seconds late -$1.55. Adding a sale inside the window makes it worse, not better: one second late, holding made +$6.88 per $100 and selling after 60 seconds +$2.43.
- **A stop-loss on the real Kalshi bot's kind of bet does not pay either.** By the minute it looks almost free, but second by second the price dips and comes back, and the stop sells at the bottom.
- **Side-find that matters for the real speed bot:** the box is nearly blind for the first 11 seconds of every 5-minute window (its price feed reconnects there). All 8 real orders that were killed although the offer "stayed" were sent in those seconds. Details at the end.

## The four numbers (rough guesses)

| | Buy cheap, sell back (any version) | Speed buy + sell after 60 s | Speed buy, hold to the end (what the real bot does) |
|---|---|---|---|
| Most it makes in an average day | Nothing. A $5 bet loses about 47 cents on Polymarket and about 50 cents on Kalshi, every time | Paper: about +$14.22 a day at 10 shares a bet, if every order filled one second late | Paper: about +$40.31 a day at 10 shares a bet, same if |
| Money needed in the account | $5-10 a bet, back within a minute | About $5 a bet, back in a minute: $10-15 is plenty | About $5 a bet, back within 5 minutes: $15-25 out at once |
| Bet size where it stops growing | Does not apply | About $25 a bet. The offer we would buy holds 150 shares in the middle case, but under 54 shares one time in four | Same |
| A bad day | 50 bets a day would lose about $24 | Paper worst day -$47.44; ahead on 5 of 10 days | Paper worst day -$7.54; ahead on 7 of 10 days. Real money so far: 4 orders filled of 38, -$2.64 |

Paper means: the test assumes our order gets the offer it saw one second earlier. The real bot's orders mostly did not (34 of 38 killed on 26 Nov). So the right-hand columns are a ceiling, not a forecast.

## What a buy-then-sell costs, and how prices move (Bitcoin 5-minute, Polymarket)

```
Bitcoin: 2,616 windows, 20261117 to 20261126

A round trip (buy now, sell right away) costs, per share, by price of the share:
  0.05-0.20: gap 1.18c + fees 1.48c = 2.66c   (with a waiting sell order on the way out: 1.95c)
  0.20-0.40: gap 1.37c + fees 2.91c = 4.28c   (with a waiting sell order on the way out: 2.84c)
  0.40-0.60: gap 1.38c + fees 3.45c = 4.83c   (with a waiting sell order on the way out: 3.11c)
  0.60-0.80: gap 1.38c + fees 2.93c = 4.31c   (with a waiting sell order on the way out: 2.83c)
  0.80-0.95: gap 1.19c + fees 1.48c = 2.67c   (with a waiting sell order on the way out: 1.90c)

How far the middle price moves (average size of the move, cents):
  over     1 s: 1.45c   moves of 5c+: 5.3 in 100
  over     5 s: 4.42c   moves of 5c+: 24.4 in 100
  over    15 s: 8.34c   moves of 5c+: 42.0 in 100
  over    30 s: 12.08c   moves of 5c+: 50.9 in 100
  over    60 s: 17.30c   moves of 5c+: 56.8 in 100
  over   120 s: 25.04c   moves of 5c+: 55.0 in 100

Does a move keep going or bounce back? (next move as a share of the last move; + = keeps going, - = bounces)
     1 s then    1 s: all moves +0.097, moves of 5c+ +0.072  (413282 looks)
     3 s then    3 s: all moves +0.042, moves of 5c+ +0.036  (1278212 looks)
     5 s then    5 s: all moves +0.021, moves of 5c+ +0.019  (1860320 looks)
    15 s then   15 s: all moves -0.013, moves of 5c+ -0.014  (2956538 looks)
    30 s then   30 s: all moves -0.048, moves of 5c+ -0.049  (3100418 looks)
    60 s then   60 s: all moves -0.054, moves of 5c+ -0.054  (2334190 looks)

When the share is X cents under the Binance fair price, how much of the gap closes? (middle price, no costs)
  gap 3-6c,   1 s later: +0.05c toward fair (855485 looks);  gap 6-10c,   1 s later: +0.11c toward fair (974867 looks);  gap 10-30c,   1 s later: +0.29c toward fair (1721275 looks);
  gap 3-6c,   5 s later: +0.10c toward fair (855189 looks);  gap 6-10c,   5 s later: +0.20c toward fair (974456 looks);  gap 10-30c,   5 s later: +0.56c toward fair (1720012 looks);
  gap 3-6c,  15 s later: +0.06c toward fair (850921 looks);  gap 6-10c,  15 s later: +0.23c toward fair (969299 looks);  gap 10-30c,  15 s later: +0.75c toward fair (1699259 looks);
  gap 3-6c,  30 s later: +0.09c toward fair (833462 looks);  gap 6-10c,  30 s later: +0.32c toward fair (948711 looks);  gap 10-30c,  30 s later: +0.98c toward fair (1634048 looks);
  gap 3-6c,  60 s later: +0.27c toward fair (771086 looks);  gap 6-10c,  60 s later: +0.66c toward fair (871524 looks);  gap 10-30c,  60 s later: +1.34c toward fair (1433434 looks);
```

Read it like this: prices swing a lot (4c in 5 seconds on average), which is why the idea looks tempting. But the swings do not come back. A move is followed by a tiny bit more of the same in the next 1-5 seconds (that is the speed race) and a tiny bounce after 30-60 seconds, both far smaller than the 5c it costs to get in and out.

## Every family of rule, picked on the first days and checked on fresh days

How to read the tables: a rule is "looked at" on the first days and then checked on the later days it never saw. "Sure fills only" = our waiting order counts as filled only when a real trade went through its price. "Always first in line" is the hopeful end: filled the moment anyone trades at our price.

### Polymarket Bitcoin 5-minute, 17-26 Nov (10 looks a second)

2,616 windows, 8,378 rule versions. Rules were looked at on the first 5 day(s) and checked on the other 5.

| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |
|---|---|---|---|---|---|
| buy the dip (buy at the offer) | 640 | 0 | 0 | -$10.47 | -$5.13 then -$5.35 (fell 5c+ in 15s; hold to the end) |
| buy the dip, coin calm (buy at the offer) | 640 | 14 | 1 | -$9.93 | +$9.74 then -$4.66 (fell 20c+ in 15s, fair price fell under a third of that; hold to the end) |
| cheap vs Binance (buy at the offer) | 160 | 0 | 0 | -$7.36 | -$3.40 then +$4.04 (ask 20c+ under the Binance fair price; sell after 15s) |
| cheap vs Chainlink (buy at the offer) | 160 | 0 | 0 | -$10.71 | -$7.63 then -$4.73 (ask 3c+ under the Chainlink fair price; hold to the end) |
| coin moved, share did not (buy at the offer) | 352 | 184 | 182 | +$2.17 | +$21.01 then +$29.94 (fair +15c in 2s, share under half of that; sell after 15s) |
| follow the move (buy at the offer) | 640 | 0 | 0 | -$7.51 | -$1.69 then -$3.16 (rose 20c+ in 60s; hold to the end) |
| time and price (buy at the offer) | 672 | 20 | 6 | -$10.32 | +$12.85 then -$5.47 (at 3min, ask 30c-45c; stop -30c / else hold) |
| bid after a fall (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$7.09 | -$3.10 then -$3.46 (join the best bid after a 5c+ fall in 5s; hold to the end) |
| bid after a rise (waiting bid, always first in line (hopeful)) | 216 | 2 | 0 | -$4.26 | +$0.09 then -$0.14 (join the best bid after a 10c+ rise in 15s; hold to the end) |
| bid under Binance fair (waiting bid, always first in line (hopeful)) | 144 | 0 | 0 | -$5.64 | -$2.84 then -$0.71 (bid 8c under the Binance fair price (never above the best bid); hold to the end) |
| bid under the price (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$5.51 | -$1.28 then -$2.82 (bid 8c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, always first in line (hopeful)) | 504 | 0 | 0 | -$15.07 | -$8.37 then -$10.22 (bid 20c on both sides, first 4min; stop -20c / else hold) |
| join the bid by price (waiting bid, always first in line (hopeful)) | 180 | 1 | 0 | -$6.55 | +$1.22 then -$1.25 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, always first in line (hopeful)) | 108 | 0 | 0 | -$5.24 | -$1.64 then -$1.95 (join the best bid, 0s-90s; hold to the end) |
| late favourite bid (waiting bid, always first in line (hopeful)) | 144 | 0 | 0 | -$2.31 | -$0.04 then +$1.52 (join the best bid at 88c-97c in the last 2min; offer at +10c / else hold) |
| bid after a fall (waiting bid, sure fills only) | 216 | 0 | 0 | -$9.82 | -$5.03 then -$5.21 (join the best bid after a 5c+ fall in 5s; hold to the end) |
| bid after a rise (waiting bid, sure fills only) | 216 | 0 | 0 | -$7.50 | -$2.55 then -$3.58 (join the best bid after a 10c+ rise in 30s; hold to the end) |
| bid under Binance fair (waiting bid, sure fills only) | 144 | 0 | 0 | -$9.10 | -$5.66 then -$3.66 (bid 3c under the Binance fair price (never above the best bid); hold to the end) |
| bid under the price (waiting bid, sure fills only) | 216 | 0 | 0 | -$8.00 | -$3.34 then -$3.87 (bid 5c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, sure fills only) | 504 | 0 | 0 | -$18.02 | -$12.16 then -$15.21 (bid 20c on both sides, first 4min; stop -20c / else hold) |
| join the bid by price (waiting bid, sure fills only) | 180 | 0 | 0 | -$9.64 | -$1.15 then -$3.47 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, sure fills only) | 108 | 0 | 0 | -$8.19 | -$4.09 then -$4.24 (join the best bid, 90s-3min; hold to the end) |
| late favourite bid (waiting bid, sure fills only) | 144 | 0 | 0 | -$4.38 | -$1.87 then +$0.02 (join the best bid at 88c-97c in the last 2min; hold to the end) |

Without the speed family and the hopeful fills: 4,640 versions, 34 ahead on the first days, 7 of those still ahead on the fresh days, 33 ahead on the fresh days at all.

### Polymarket ETH 5-minute, 25-26 Nov

313 windows, 8,148 rule versions. Rules were looked at on the first 1 day(s) and checked on the other 1.

| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |
|---|---|---|---|---|---|
| buy the dip (buy at the offer) | 608 | 4 | 0 | -$8.68 | +$4.77 then -$11.64 (fell 12c+ in 1s; sell at +20c / else hold) |
| buy the dip, coin calm (buy at the offer) | 576 | 7 | 0 | -$8.99 | +$7.17 then -$12.50 (fell 12c+ in 1s, fair price fell under a third of that; sell after 60s) |
| cheap vs Binance (buy at the offer) | 160 | 0 | 0 | -$7.95 | -$4.88 then -$7.22 (ask 8c+ under the Binance fair price; offer at +10c / stop -5c) |
| coin moved, share did not (buy at the offer) | 128 | 11 | 3 | -$6.29 | +$10.77 then +$0.81 (fair +4c in 1s, share under half of that; hold to the end) |
| follow the move (buy at the offer) | 608 | 15 | 0 | -$7.32 | +$8.91 then -$5.04 (rose 20c+ in 5s; sell at +20c / else hold) |
| bid after a fall (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$7.33 | -$3.48 then -$7.90 (join the best bid after a 10c+ fall in 30s; stop -10c / else hold) |
| bid after a rise (waiting bid, always first in line (hopeful)) | 216 | 3 | 0 | -$5.71 | +$0.96 then -$1.91 (join the best bid after a 10c+ rise in 15s; hold to the end) |
| bid under Binance fair (waiting bid, always first in line (hopeful)) | 144 | 2 | 0 | -$5.67 | +$1.18 then -$4.01 (bid 8c under the Binance fair price (never above the best bid); stop -20c / else hold) |
| bid under the price (waiting bid, always first in line (hopeful)) | 216 | 4 | 0 | -$5.88 | +$2.66 then -$6.10 (bid 0c under the best bid; stop -20c / else hold) |
| fixed bids on both sides (waiting bid, always first in line (hopeful)) | 432 | 0 | 0 | -$16.50 | -$9.11 then -$6.89 (bid 20c on both sides, first 4min; sell at +5c / else hold) |
| join the bid by price (waiting bid, always first in line (hopeful)) | 180 | 9 | 0 | -$6.86 | +$4.02 then -$3.49 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, always first in line (hopeful)) | 108 | 4 | 0 | -$6.03 | +$2.66 then -$6.10 (join the best bid, 0s-90s; stop -20c / else hold) |
| late favourite bid (waiting bid, always first in line (hopeful)) | 72 | 1 | 0 | -$1.94 | +$0.76 then -$1.37 (join the best bid at 80c-90c in the last 2min; offer at +5c / out after 60s) |
| bid after a fall (waiting bid, sure fills only) | 216 | 0 | 0 | -$7.67 | -$3.44 then -$8.33 (join the best bid after a 10c+ fall in 30s; stop -10c / else hold) |
| bid after a rise (waiting bid, sure fills only) | 216 | 1 | 0 | -$6.14 | +$0.52 then -$1.88 (join the best bid after a 10c+ rise in 15s; hold to the end) |
| bid under Binance fair (waiting bid, sure fills only) | 144 | 2 | 0 | -$6.58 | +$0.75 then -$4.80 (bid 8c under the Binance fair price (never above the best bid); stop -20c / else hold) |
| bid under the price (waiting bid, sure fills only) | 216 | 4 | 0 | -$6.28 | +$2.52 then -$6.84 (bid 0c under the best bid; stop -20c / else hold) |
| fixed bids on both sides (waiting bid, sure fills only) | 432 | 0 | 0 | -$16.65 | -$9.90 then -$8.26 (bid 20c on both sides, first 4min; sell at +5c / else hold) |
| join the bid by price (waiting bid, sure fills only) | 180 | 8 | 0 | -$7.32 | +$3.26 then -$3.78 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, sure fills only) | 108 | 4 | 0 | -$6.36 | +$2.52 then -$6.84 (join the best bid, 0s-90s; stop -20c / else hold) |
| late favourite bid (waiting bid, sure fills only) | 72 | 1 | 0 | -$2.32 | +$0.14 then -$1.88 (join the best bid at 80c-90c in the last 2min; offer at +5c / out after 60s) |

Without the speed family and the hopeful fills: 3,536 versions, 46 ahead on the first days, 0 of those still ahead on the fresh days, 12 ahead on the fresh days at all.

### Polymarket SOL 5-minute, 25-26 Nov

313 windows, 8,148 rule versions. Rules were looked at on the first 1 day(s) and checked on the other 1.

| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |
|---|---|---|---|---|---|
| buy the dip (buy at the offer) | 608 | 4 | 0 | -$10.13 | +$4.40 then -$3.25 (fell 20c+ in 5s; sell after 60s) |
| buy the dip, coin calm (buy at the offer) | 608 | 24 | 0 | -$10.47 | +$13.39 then -$5.60 (fell 20c+ in 5s, fair price fell under a third of that; sell after 60s) |
| cheap vs Binance (buy at the offer) | 160 | 7 | 0 | -$10.55 | +$8.27 then -$10.93 (ask 20c+ under the Binance fair price; stop -20c / else hold) |
| coin moved, share did not (buy at the offer) | 192 | 5 | 0 | -$8.66 | +$11.66 then -$11.02 (fair +6c in 5s, share under half of that; stop -20c / else hold) |
| follow the move (buy at the offer) | 608 | 17 | 0 | -$7.56 | +$5.27 then -$12.22 (rose 12c+ in 1s; stop -30c / else hold) |
| bid after a fall (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$9.27 | -$0.22 then -$6.19 (join the best bid after a 5c+ fall in 5s; stop -30c / else hold) |
| bid after a rise (waiting bid, always first in line (hopeful)) | 216 | 2 | 1 | -$6.34 | +$1.36 then -$4.65 (join the best bid after a 10c+ rise in 15s; stop -30c / else hold) |
| bid under Binance fair (waiting bid, always first in line (hopeful)) | 144 | 0 | 0 | -$8.58 | -$0.87 then -$8.54 (bid 5c under the Binance fair price (never above the best bid); stop -20c / else hold) |
| bid under the price (waiting bid, always first in line (hopeful)) | 216 | 4 | 0 | -$7.21 | +$0.62 then -$6.55 (bid 5c under the best bid; stop -30c / else hold) |
| fixed bids on both sides (waiting bid, always first in line (hopeful)) | 396 | 0 | 0 | -$20.41 | -$5.58 then -$17.44 (bid 35c on both sides, first 4min; stop -10c / else hold) |
| join the bid by price (waiting bid, always first in line (hopeful)) | 180 | 4 | 0 | -$8.73 | +$2.38 then -$2.44 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, always first in line (hopeful)) | 108 | 2 | 0 | -$6.94 | +$0.53 then -$6.48 (join the best bid, 0s-90s; stop -20c / else hold) |
| late favourite bid (waiting bid, always first in line (hopeful)) | 72 | 15 | 4 | -$2.73 | +$5.39 then -$1.04 (join the best bid at 80c-90c in the last 2min; hold to the end) |
| bid after a fall (waiting bid, sure fills only) | 216 | 0 | 0 | -$9.41 | -$0.23 then -$6.39 (join the best bid after a 5c+ fall in 5s; stop -30c / else hold) |
| bid after a rise (waiting bid, sure fills only) | 216 | 2 | 1 | -$6.63 | +$1.13 then -$4.70 (join the best bid after a 10c+ rise in 15s; stop -30c / else hold) |
| bid under Binance fair (waiting bid, sure fills only) | 144 | 0 | 0 | -$9.01 | -$1.03 then -$11.33 (bid 8c under the Binance fair price (never above the best bid); stop -20c / else hold) |
| bid under the price (waiting bid, sure fills only) | 216 | 2 | 0 | -$7.50 | +$0.20 then -$7.23 (bid 5c under the best bid; stop -30c / else hold) |
| fixed bids on both sides (waiting bid, sure fills only) | 396 | 0 | 0 | -$20.60 | -$5.60 then -$14.44 (bid 30c on both sides, first 4min; stop -5c / else hold) |
| join the bid by price (waiting bid, sure fills only) | 180 | 4 | 0 | -$9.12 | +$2.27 then -$2.59 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, sure fills only) | 108 | 1 | 0 | -$7.18 | +$0.12 then -$6.54 (join the best bid, 0s-90s; stop -20c / else hold) |
| late favourite bid (waiting bid, sure fills only) | 72 | 13 | 3 | -$3.00 | +$5.39 then -$1.16 (join the best bid at 80c-90c in the last 2min; hold to the end) |

Without the speed family and the hopeful fills: 3,532 versions, 74 ahead on the first days, 4 of those still ahead on the fresh days, 4 ahead on the fresh days at all.

### Kalshi 15-minute, 7 coins, 25-26 Nov (a look every 1-10 s)

662 windows, 5,790 rule versions. Rules were looked at on the first 1 day(s) and checked on the other 1.

| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |
|---|---|---|---|---|---|
| buy the dip (buy at the offer) | 512 | 4 | 0 | -$8.88 | +$15.46 then -$6.61 (fell 20c+ in 10s; hold to the end) |
| follow the move (buy at the offer) | 512 | 1 | 0 | -$8.60 | +$0.17 then -$4.70 (rose 20c+ in 2min; hold to the end) |
| time and price (buy at the offer) | 416 | 28 | 5 | -$8.57 | +$12.86 then -$1.77 (at 3min, ask 8c-30c; sell at +20c / stop -10c) |
| bid after a fall (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$10.08 | -$3.23 then -$7.41 (join the best bid after a 10c+ fall in 60s; stop -20c / else hold) |
| bid after a rise (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$9.85 | -$4.02 then -$5.82 (join the best bid after a 10c+ rise in 60s; hold to the end) |
| bid under the price (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$9.54 | -$4.78 then -$5.00 (bid 5c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, always first in line (hopeful)) | 468 | 0 | 0 | -$12.17 | -$6.53 then -$5.53 (bid 30c on both sides, first 13min; sell at +5c / else hold) |
| join the bid by price (waiting bid, always first in line (hopeful)) | 180 | 0 | 0 | -$9.72 | -$1.31 then -$6.18 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, always first in line (hopeful)) | 108 | 0 | 0 | -$9.46 | -$4.05 then -$3.57 (join the best bid, 9min-13min; hold to the end) |
| late favourite bid (waiting bid, always first in line (hopeful)) | 144 | 0 | 0 | -$3.10 | -$1.40 then +$1.52 (join the best bid at 88c-97c in the last 2min; hold to the end) |
| bid after a fall (waiting bid, sure fills only) | 216 | 0 | 0 | -$10.70 | -$3.87 then -$12.36 (join the best bid after a 5c+ fall in 60s; sell at +5c / else hold) |
| bid after a rise (waiting bid, sure fills only) | 216 | 0 | 0 | -$10.18 | -$4.05 then -$6.38 (join the best bid after a 10c+ rise in 60s; hold to the end) |
| bid under the price (waiting bid, sure fills only) | 216 | 0 | 0 | -$9.86 | -$4.99 then -$4.03 (bid 8c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, sure fills only) | 468 | 0 | 0 | -$13.02 | -$6.85 then -$6.69 (bid 30c on both sides, first 13min; sell at +20c / else hold) |
| join the bid by price (waiting bid, sure fills only) | 180 | 0 | 0 | -$10.24 | -$1.47 then -$6.40 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, sure fills only) | 108 | 0 | 0 | -$9.97 | -$4.18 then -$3.79 (join the best bid, 9min-13min; hold to the end) |
| late favourite bid (waiting bid, sure fills only) | 144 | 0 | 0 | -$3.24 | -$1.40 then +$1.39 (join the best bid at 88c-97c in the last 2min; hold to the end) |

Without the speed family and the hopeful fills: 2,988 versions, 33 ahead on the first days, 5 of those still ahead on the fresh days, 51 ahead on the fresh days at all.

### Kalshi 15-minute, 7 coins, 12 Sep - 9 Nov (a look a minute)

39,006 windows, 11,292 rule versions. Rules were looked at on the first 29 day(s) and checked on the other 30.

| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |
|---|---|---|---|---|---|
| buy the dip (buy at the offer) | 1024 | 0 | 0 | -$10.09 | -$5.22 then -$4.38 (fell 5c+ in 60s; hold to the end) |
| follow the move (buy at the offer) | 1024 | 0 | 0 | -$6.68 | -$1.52 then -$3.77 (rose 20c+ in 3min; hold to the end) |
| time and price (buy at the offer) | 1600 | 0 | 0 | -$9.17 | -$0.68 then -$2.59 (at 3min, ask 70c-92c; hold to the end) |
| bid after a fall (waiting bid, always first in line (hopeful)) | 432 | 0 | 0 | -$10.79 | -$1.80 then -$0.51 (join the best bid after a 5c+ fall in 2min; hold to the end) |
| bid after a rise (waiting bid, always first in line (hopeful)) | 432 | 8 | 0 | -$6.76 | +$0.09 then -$1.21 (join the best bid after a 10c+ rise in 3min; hold to the end) |
| bid under the price (waiting bid, always first in line (hopeful)) | 432 | 0 | 0 | -$7.32 | -$0.98 then -$1.16 (bid 0c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, always first in line (hopeful)) | 1008 | 11 | 0 | -$15.55 | +$3.63 then -$1.49 (bid 20c on both sides, first 90s; stop -10c / else hold) |
| join the bid by price (waiting bid, always first in line (hopeful)) | 360 | 2 | 0 | -$7.80 | +$0.06 then -$0.57 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, always first in line (hopeful)) | 216 | 0 | 0 | -$7.89 | -$0.83 then -$0.88 (join the best bid, 4min-9min; hold to the end) |
| late favourite bid (waiting bid, always first in line (hopeful)) | 144 | 30 | 0 | -$1.53 | +$0.72 then -$0.33 (join the best bid at 80c-90c in the last 7min; hold to the end) |
| bid after a fall (waiting bid, sure fills only) | 432 | 0 | 0 | -$14.33 | -$5.17 then -$4.29 (join the best bid after a 5c+ fall in 2min; hold to the end) |
| bid after a rise (waiting bid, sure fills only) | 432 | 0 | 0 | -$8.95 | -$2.20 then -$3.43 (join the best bid after a 10c+ rise in 3min; hold to the end) |
| bid under the price (waiting bid, sure fills only) | 432 | 0 | 0 | -$9.54 | -$3.68 then -$4.02 (bid 0c under the best bid; hold to the end) |
| fixed bids on both sides (waiting bid, sure fills only) | 1008 | 0 | 0 | -$18.33 | -$0.83 then -$5.43 (bid 20c on both sides, first 90s; stop -10c / else hold) |
| join the bid by price (waiting bid, sure fills only) | 360 | 0 | 0 | -$10.76 | -$1.83 then -$2.36 (join the best bid while it is 70c-90c; hold to the end) |
| join the bid by time (waiting bid, sure fills only) | 216 | 0 | 0 | -$10.40 | -$3.45 then -$3.71 (join the best bid, 4min-9min; hold to the end) |
| late favourite bid (waiting bid, sure fills only) | 144 | 0 | 0 | -$2.85 | -$0.21 then -$0.96 (join the best bid at 88c-97c in the last 7min; hold to the end) |

Without the speed family and the hopeful fills: 6,672 versions, 0 ahead on the first days, 0 of those still ahead on the fresh days, 1 ahead on the fresh days at all.

## Selling early against holding to the end

Same buys, different ways out. A minus means the way out did worse than simply holding the share to the end of the window.

| Data | Way out | Rules | Against just holding to the end, per $100 (middle rule) | Better than holding in |
|---|---|---|---|---|
| Polymarket BTC | sell after a set time (5 s to 5 min) | 460 | -$3.79 | 15 of 460 |
| Polymarket BTC | stop-loss only (sell if it falls 5-30c) | 556 | -$1.99 | 55 of 556 |
| Polymarket BTC | take profit + stop-loss, selling at the bid | 546 | -$4.12 | 10 of 546 |
| Polymarket BTC | take profit only, selling at the bid | 417 | -$3.89 | 5 of 417 |
| Polymarket BTC | waiting sell offer 1-10c higher, hopeful fills (always first in line) | 1274 | -$3.25 | 28 of 1274 |
| Polymarket BTC | waiting sell offer 1-10c higher, sure fills only | 2522 | -$3.99 | 68 of 2522 |
| Polymarket ETH | sell after a set time (5 s to 5 min) | 330 | -$3.65 | 30 of 330 |
| Polymarket ETH | stop-loss only (sell if it falls 5-30c) | 416 | -$2.01 | 100 of 416 |
| Polymarket ETH | take profit + stop-loss, selling at the bid | 366 | -$3.38 | 30 of 366 |
| Polymarket ETH | take profit only, selling at the bid | 312 | -$3.15 | 32 of 312 |
| Polymarket ETH | waiting sell offer 1-10c higher, hopeful fills (always first in line) | 854 | -$2.79 | 87 of 854 |
| Polymarket ETH | waiting sell offer 1-10c higher, sure fills only | 1972 | -$3.40 | 199 of 1972 |
| Polymarket SOL | sell after a set time (5 s to 5 min) | 334 | -$3.83 | 13 of 334 |
| Polymarket SOL | stop-loss only (sell if it falls 5-30c) | 420 | -$1.68 | 67 of 420 |
| Polymarket SOL | take profit + stop-loss, selling at the bid | 372 | -$3.90 | 4 of 372 |
| Polymarket SOL | take profit only, selling at the bid | 315 | -$4.79 | 10 of 315 |
| Polymarket SOL | waiting sell offer 1-10c higher, hopeful fills (always first in line) | 868 | -$3.57 | 22 of 868 |
| Polymarket SOL | waiting sell offer 1-10c higher, sure fills only | 1986 | -$3.77 | 56 of 1986 |
| Kalshi, by the second | sell after a set time (5 s to 5 min) | 258 | -$4.20 | 19 of 258 |
| Kalshi, by the second | stop-loss only (sell if it falls 5-30c) | 344 | -$2.02 | 59 of 344 |
| Kalshi, by the second | take profit + stop-loss, selling at the bid | 258 | -$4.01 | 32 of 258 |
| Kalshi, by the second | take profit only, selling at the bid | 258 | -$3.76 | 9 of 258 |
| Kalshi, by the second | waiting sell offer 1-10c higher, hopeful fills (always first in line) | 602 | -$4.40 | 72 of 602 |
| Kalshi, by the second | waiting sell offer 1-10c higher, sure fills only | 1720 | -$4.75 | 71 of 1720 |
| Kalshi, by the minute | sell after a set time (5 s to 5 min) | 624 | -$3.31 | 0 of 624 |
| Kalshi, by the minute | stop-loss only (sell if it falls 5-30c) | 792 | -$1.54 | 9 of 792 |
| Kalshi, by the minute | take profit + stop-loss, selling at the bid | 684 | -$3.46 | 0 of 684 |
| Kalshi, by the minute | take profit only, selling at the bid | 594 | -$2.46 | 1 of 594 |
| Kalshi, by the minute | waiting sell offer 1-10c higher, hopeful fills (always first in line) | 1596 | -$2.63 | 16 of 1596 |
| Kalshi, by the minute | waiting sell offer 1-10c higher, sure fills only | 3780 | -$6.32 | 0 of 3780 |

Why holding wins: selling costs a second fee and a second trip across the gap, and there is no bounce to collect. A waiting sell offer saves the fee, but it only fills when the price is running up through it, so it sells the winners cheap and keeps the losers.

## The one family ahead: the coin jumped and the share has not moved yet

This is the speed bot's own signal, tested here with ways out. Not in the first 12 seconds of a window (see the recording flaw below).

| How late we buy | Which offers | Way out | Bets a day | Per $100, first days | Per $100, fresh days | A day at 10 shares, fresh days | Worst day | Days ahead |
|---|---|---|---|---|---|---|---|---|
| 0.5 s late | any offer still there | hold to the end | 270 | +$9.38 | +$11.89 | +$169.00 | +$42.32 | 10 of 10 |
| 0.5 s late | any offer still there | sell after 60s | 270 | +$6.83 | +$9.76 | +$138.70 | +$10.41 | 10 of 10 |
| 0.5 s late | any offer still there | sell after 15s | 270 | +$5.07 | +$7.37 | +$104.77 | +$20.30 | 10 of 10 |
| 0.5 s late | book fresh and 20+ shares on offer | hold to the end | 208 | +$9.19 | +$10.56 | +$115.76 | -$5.60 | 9 of 10 |
| 0.5 s late | book fresh and 20+ shares on offer | sell after 60s | 208 | +$6.18 | +$6.99 | +$76.59 | -$6.09 | 9 of 10 |
| 0.5 s late | book fresh and 20+ shares on offer | sell after 15s | 208 | +$4.70 | +$6.04 | +$66.21 | +$20.38 | 10 of 10 |
| 1 s late | any offer still there | hold to the end | 167 | +$6.59 | +$11.47 | +$98.82 | -$14.53 | 9 of 10 |
| 1 s late | any offer still there | sell after 60s | 167 | +$3.66 | +$7.44 | +$64.04 | -$7.58 | 9 of 10 |
| 1 s late | any offer still there | sell after 15s | 167 | +$2.52 | +$6.21 | +$53.51 | -$18.50 | 9 of 10 |
| 1 s late | book fresh and 20+ shares on offer | hold to the end | 117 | +$7.64 | +$6.88 | +$40.31 | -$7.54 | 7 of 10 |
| 1 s late | book fresh and 20+ shares on offer | sell after 60s | 117 | +$1.41 | +$2.43 | +$14.22 | -$47.44 | 5 of 10 |
| 1 s late | book fresh and 20+ shares on offer | sell after 15s | 117 | -$1.46 | +$2.43 | +$14.25 | -$38.17 | 4 of 10 |
| 2 s late | any offer still there | hold to the end | 96 | +$1.51 | -$1.82 | -$8.29 | -$35.41 | 4 of 10 |
| 2 s late | any offer still there | sell after 60s | 96 | -$4.45 | -$4.18 | -$19.05 | -$50.65 | 1 of 10 |
| 2 s late | any offer still there | sell after 15s | 96 | -$5.49 | -$1.32 | -$6.01 | -$51.56 | 2 of 10 |
| 2 s late | book fresh and 20+ shares on offer | hold to the end | 80 | +$5.34 | -$1.55 | -$5.67 | -$37.44 | 6 of 10 |
| 2 s late | book fresh and 20+ shares on offer | sell after 60s | 80 | -$1.93 | -$5.83 | -$21.33 | -$44.71 | 2 of 10 |
| 2 s late | book fresh and 20+ shares on offer | sell after 15s | 80 | -$5.14 | -$3.77 | -$13.78 | -$46.94 | 1 of 10 |
| 5 s late | any offer still there | hold to the end | 137 | -$3.15 | -$5.76 | -$37.88 | -$106.28 | 4 of 10 |
| 5 s late | any offer still there | sell after 60s | 137 | -$9.24 | -$9.80 | -$64.45 | -$125.59 | 0 of 10 |
| 5 s late | any offer still there | sell after 15s | 137 | -$10.17 | -$8.89 | -$58.51 | -$80.73 | 0 of 10 |
| 5 s late | book fresh and 20+ shares on offer | hold to the end | 114 | -$0.35 | -$5.92 | -$31.87 | -$119.02 | 4 of 10 |
| 5 s late | book fresh and 20+ shares on offer | sell after 60s | 114 | -$8.93 | -$9.74 | -$52.40 | -$105.76 | 0 of 10 |
| 5 s late | book fresh and 20+ shares on offer | sell after 15s | 114 | -$10.03 | -$10.31 | -$55.44 | -$84.54 | 0 of 10 |

Shares on offer at the price we would pay (1 s late, fresh book, 20+): middle 150, one in four under 54, one in four over 698. Middle price paid 46c.

So it is a race that is over inside two seconds, and the money is in holding, not in selling. The real bot's answer times were 0.3 to 1.7 seconds on 26 Nov.

## A stop-loss for late bids on the likely side (the real Kalshi bot's kind of bet)

Bid on the side priced 88-97c late in the window, as the real bot does (without its Binance cushion check, so these lose a little where the real rule wins a little). Question: does selling when the price falls help?

| Data | Bet | Way out | Bets | Per $100 | Worst day at 10 shares a bet |
|---|---|---|---|---|---|
| Kalshi, by the minute | join the best bid at 88c-97c in the last 7min | hold to the end | 22,811 | -$0.58 | -$217.54 |
| Kalshi, by the minute | join the best bid at 88c-97c in the last 7min | stop -30c / else hold | 22,811 | -$0.63 | -$138.35 |
| Kalshi, by the minute | join the best bid at 88c-97c in the last 7min | stop -10c / else hold | 22,811 | -$0.65 | -$133.30 |
| Kalshi, by the minute | join the best bid at 88c-97c in the last 7min | stop -20c / else hold | 22,811 | -$0.70 | -$144.75 |
| Kalshi, by the minute | join the best bid at 88c-97c in the last 7min | stop -5c / else hold | 22,811 | -$0.75 | -$140.86 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 2min | hold to the end | 408 | +$0.71 | -$12.76 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 2min | stop -10c / else hold | 408 | -$2.05 | -$52.03 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 2min | stop -5c / else hold | 408 | -$2.57 | -$72.64 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 2min | stop -20c / else hold | 408 | -$3.04 | -$67.06 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 2min | stop -30c / else hold | 408 | -$3.39 | -$73.05 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 7min | hold to the end | 662 | -$0.19 | -$29.44 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 7min | stop -10c / else hold | 662 | -$1.53 | -$52.27 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 7min | stop -20c / else hold | 662 | -$1.77 | -$69.72 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 7min | stop -30c / else hold | 662 | -$2.10 | -$66.15 |
| Kalshi, by the second | join the best bid at 88c-97c in the last 7min | stop -5c / else hold | 662 | -$2.14 | -$88.20 |
| Polymarket BTC | join the best bid at 88c-97c in the last 2min | hold to the end | 2,179 | -$0.89 | -$82.45 |
| Polymarket BTC | join the best bid at 88c-97c in the last 2min | stop -30c / else hold | 2,179 | -$1.56 | -$57.58 |
| Polymarket BTC | join the best bid at 88c-97c in the last 2min | stop -20c / else hold | 2,179 | -$1.68 | -$63.38 |
| Polymarket BTC | join the best bid at 88c-97c in the last 2min | stop -10c / else hold | 2,179 | -$2.23 | -$67.75 |
| Polymarket BTC | join the best bid at 88c-97c in the last 2min | stop -5c / else hold | 2,179 | -$2.65 | -$70.13 |
| Polymarket BTC | join the best bid at 88c-97c in the last 59s | hold to the end | 792 | -$2.01 | -$42.45 |
| Polymarket BTC | join the best bid at 88c-97c in the last 59s | stop -30c / else hold | 792 | -$3.13 | -$46.31 |
| Polymarket BTC | join the best bid at 88c-97c in the last 59s | stop -10c / else hold | 792 | -$3.38 | -$42.04 |
| Polymarket BTC | join the best bid at 88c-97c in the last 59s | stop -20c / else hold | 792 | -$3.46 | -$42.02 |
| Polymarket BTC | join the best bid at 88c-97c in the last 59s | stop -5c / else hold | 792 | -$3.94 | -$46.21 |

By the minute (59 days) a stop costs only a few cents per $100 and trims the worst day. Second by second (only 2 days, but the truer picture) it costs $2-3 per $100, because the price often dips 10c and comes back, and the stop has sold at the dip. Not worth adding to the real bot.

## The shared exam

| Test | Bets | Per $100 | Luck range | Verdict |
|---|---|---|---|---|
| Buy and sell inside the window, btc: best of 4359 rules on the first days, graded on fresh days (buy at the offer; at 4min, ask 8c-30c; sell after 15s) | 174 | -$14.52 | -$32.79 to +$3.75 | Behind, but could be bad luck |
| Buy and sell inside the window, ksec: best of 2846 rules on the first days, graded on fresh days (buy at the offer; at 3min, ask 8c-30c; sell at +20c / stop -10c) | 112 | -$1.77 | -$20.69 to +$17.15 | Behind, but could be bad luck |
| Buy and sell inside the window, kmin: best of 5806 rules on the first days, graded on fresh days (waiting bid; join the best bid at 88c-97c in the last 7min; sell at +5c / else hold) | 11,227 | -$1.20 | -$1.84 to -$0.57 | Losing |
| Speed buy on BTC 5-min 1 s late (not in the first 12 s), sell after 60s, fresh days, PAPER fills | 902 | +$7.44 | +$4.64 to +$10.23 | Promising, needs more bets |
| Speed buy on BTC 5-min 1 s late (not in the first 12 s), hold to the end, fresh days, PAPER fills | 902 | +$11.47 | +$7.55 to +$15.40 | Looks real |

The two speed lines are paper fills. The exam cannot know that real orders mostly get killed.

## How the test works

- **Polymarket:** the speed box's log (release `speed-data`): the best buy and sell price of the Up share with sizes, every real trade, and Binance / Chainlink prices, all on our box's clock. Laid on a grid of 10 looks a second. Buying pays the best sell offer, selling gets the best buy order; the Down share is the mirror. An order decided at one look trades at the prices 1 second later (0.5-5 s in the speed table), and only if the price is not worse than the one it saw.
- **Fees:** Polymarket 0.07 x shares x price x (1 - price) on every hurried buy and sell (what we measured on real fills). Kalshi 0.07 x contracts x price x (1 - price), rounded up to a cent an order. Waiting orders pay nothing.
- **Waiting orders:** counted as filled only when a later real trade printed through their price ("sure"), or at their price ("hopeful", shown apart). The truth is in between; no version was ahead even at the hopeful end.
- **Kalshi:** two sources. 25-26 Nov from the speed box (book every 10 s, every second in the last 7 minutes, every trade), and 12 Sep - 9 Nov by the minute (`kspeed`'s candles: bid and ask at each minute's end, lowest and highest trade in the minute).
- **Learn days and fresh days:** Bitcoin 17-21 Nov against 22-26 Nov; ETH, SOL and Kalshi-by-the-second 25 Nov against 26 Nov; Kalshi-by-the-minute the first 29 days against the last 30.
- **Checks done:** two rules were re-counted with a slow, plain loop and matched the fast replay to the cent (3,002 waiting-bid fills; 600 random windows of a buy / take-profit / stop rule). A share bought at a random moment and held loses about the gap plus the fee, as it should.

## Traps found (for the next dig)

- **The speed box is nearly blind in seconds 1-11 of every 5-minute window.** On 24 Nov it logged about 24 book updates in second 0, none in second 1, about 4-6 a second in seconds 2-10, then 25-30 a second. The code drops and reopens the price feed when a window ends and again when the next one is listed about 10 s later (`market()` in `quoter/speedcheck.py` and `live/pspeed_live.py`). In those seconds the recorded book is stale, so a replay "buys" offers that were not there. Before this was cut out, the speed family looked good even 2 and 5 seconds late; after, it is gone at 2 seconds. `swing.FIRST` skips the first 12 s. `backtest/speedcheck.md` and `backtest/maker5m.md` did not skip them.
- **The real bot has the same blind spot.** Of 34 real orders killed on 26 Nov, 8 had the offer at or under our limit at every book update until the exchange answered, with 16 to 247 shares showing, and nobody else bought it. All 8 were sent 0.2-6 s after a window started. The 4 orders that filled were sent 37-101 s in.
- **A waiting order's fill is bad news.** It fills when the price falls through it. On minute data a waiting sell offer looks much worse than it is (the price has run far past it by the minute's end), so read the "hopeful" line too.
- **Minute data hides the dip-and-recover.** Stops look nearly free by the minute and cost $2-3 per $100 by the second.
- **Buying the other side later is the same trade as selling.** It pays the same fee and locks the money to the end, so it was not tested apart.

## Verdict

Dropped as a strategy: no track. The useful outcomes are (1) keep holding to the end in every bot we have, (2) the 12-second blind spot at each window start, which is a concrete thing to fix or avoid in the real speed bot.
