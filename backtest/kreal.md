# How big can the Kalshi 15-minute bid get? (27 Nov 2026, `bigbets.py kreal`)

Jan, 27 Nov: "how sure are you the max bet is around 100 dollars? and if that's true it should be a lot more than 50 dollars a month if I can cover each window fully". Paper research only. Nothing on the real bot was changed.

## In short

- **Jan was right, and the old "$100 limit" was wrong.** It came from one small test on 10 Nov (124 bids, two sizes). On the real bot's own 1,008 bids there is no wall up to $400 a bid: a $4 bid's winners got 74 of every 100 contracts asked for, a $100 bid's 72, a $400 bid's 67. Sellers do not run out at these sizes.
- **So the profit grows almost in step with the bid.** On these 4.7 days: $4 bids +$1.62 a day (what really happened), $25 bids +$9.85, $50 +$18.79, $100 +$35.29, $200 +$64.10, $400 +$108.19 a day.
- **The method checks out against real money.** For the real $4 bids, the trade-list method and Kalshi agree on "bought or not" for 959 of 1,008 bids, and on the contracts: 2,981 really bought, the method says 2,969.
- **Money needed: about 7 times the bid** (up to 7 coins are open at once). $300 covers every bid up to about $40. $700 covers $100 bids.
- **The risk grows in step too.** A lost bid always fills in full and costs the whole bid. Worst 15 minutes on the paper twin: two coins lost in the same round. Worst day at $100 bids: -$126.77.
- **What this test can't see (so read the big sizes as the kind end):**
  1. Luck. 4.7 days and 4 losing bids. One win makes about 0.8c per $1, so one loss eats about 125 wins. The real bot lost 1 bought bid in 186; a few more losses and the profit is gone. The two paper twins (2 to 2.5 weeks) say about the same per $100, which helps, but nothing here is proven yet (locked test about 1 Dec).
  2. Other traders. A $4 bid is invisible. A $200 bid at the front of the line is not: others can step 1c in front of it, so the winners may fill less than the trade list says. Only real bids can show that.

## The four numbers (rough guesses, from 4.7 real days and 2 paper twins)

| | $40 a bid (fits $300) | $100 a bid | $400 a bid |
|---|---|---|---|
| Most in an average day | about +$15 (the three bid lists say $15 to $22). Count on half | about +$35 | about +$108 |
| Money needed in the account | about $280 | about $700 | about $2,800 |
| Where it stops growing | not found up to $400 a bid on the trade lists; the real limit is other traders' reaction, untested | | |
| A bad day | about -$50 (one lost bid is -$40; two coins in one round -$80) | about -$127 (one bid -$100, two -$200) | about -$525 (one bid -$400) |

## How to find the real limit

Raise the real bid in steps ($4, then $10, then $25) and compare "winners got N in 100" with the table below after a few hundred bids each. If the real number falls well under the table's, the wall is close. Bid size is Jan's setting on the server (`KALSHI_USD_PER_ORDER` and `KALSHI_MAX_OPEN_USD` in `~/.live.env`), so this is his call.

## The tables

"Bids that got anything" = bids where at least one contract was bought. "Winners got / Losers got" = of every 100 contracts asked for, how many were bought, on bids that ended on the winning / losing side. The account table skips a bid when the money is tied up in other bids; with few losing bids its cells jump around (skipping one losing bid by chance changes a cell a lot), so read the "No limit" column and the "7 times the bid" rule instead.

Each bid's real trade list is read again. A bigger bid only gets what people really sold at our price (after the line that stood there first) or below it. It can't know how other traders would have reacted to a big bid, so treat the big sizes as the kind end.

no notebook for 202612: HTTP Error 404: Not Found

### The real bot ($4 bids, cushion 2.3): 1008 bids over 4.7 days (about 213 a day), 4 on the losing side


| Bid size | Bids that got anything | Money that filled | P&L | Per $100 | A day | Winners got | Losers got | Worst day | Worst 15 minutes |
|---|---|---|---|---|---|---|---|---|---|
| $4 | 743 of 1008 | $2,945 | +$7.68 | +$0.26 | +$1.62 | 74 in 100 | 100 in 100 | -$4.77 | -$3.94 |
| $10 | 743 of 1008 | $7,349 | +$18.88 | +$0.26 | +$3.98 | 73 in 100 | 100 in 100 | -$12.03 | -$9.85 |
| $25 | 743 of 1008 | $18,288 | +$46.72 | +$0.26 | +$9.85 | 73 in 100 | 100 in 100 | -$30.20 | -$24.62 |
| $50 | 743 of 1008 | $36,367 | +$89.11 | +$0.25 | +$18.79 | 73 in 100 | 100 in 100 | -$61.59 | -$49.25 |
| $100 | 743 of 1008 | $71,919 | +$167.40 | +$0.23 | +$35.29 | 72 in 100 | 100 in 100 | -$126.77 | -$98.50 |
| $200 | 743 of 1008 | $140,853 | +$304.07 | +$0.22 | +$64.10 | 70 in 100 | 100 in 100 | -$258.39 | -$196.99 |
| $400 | 743 of 1008 | $270,116 | +$513.16 | +$0.19 | +$108.19 | 67 in 100 | 100 in 100 | -$524.50 | -$393.97 |


Most bids open at the same moment: 7. So covering every bid takes about 7 times the bid size.


What an account of a given size makes a day (a bid is skipped when the money is tied up in other bids):


| Bid size | $300 account | $500 account | $700 account | $1,000 account | $2,000 account | No limit |
|---|---|---|---|---|---|---|
| $4 | +$1.62 (1008 bids) | +$1.62 (1008 bids) | +$1.62 (1008 bids) | +$1.62 (1008 bids) | +$1.62 (1008 bids) | +$1.62 (1008 bids) |
| $10 | +$3.98 (1008 bids) | +$3.98 (1008 bids) | +$3.98 (1008 bids) | +$3.98 (1008 bids) | +$3.98 (1008 bids) | +$3.98 (1008 bids) |
| $25 | +$9.85 (1008 bids) | +$9.85 (1008 bids) | +$9.85 (1008 bids) | +$9.85 (1008 bids) | +$9.85 (1008 bids) | +$9.85 (1008 bids) |
| $50 | +$16.18 (964 bids) | +$18.79 (1008 bids) | +$18.79 (1008 bids) | +$18.79 (1008 bids) | +$18.79 (1008 bids) | +$18.79 (1008 bids) |
| $100 | +$22.37 (682 bids) | +$44.39 (896 bids) | +$35.29 (1008 bids) | +$35.29 (1008 bids) | +$35.29 (1008 bids) | +$35.29 (1008 bids) |
| $200 | +$41.08 (312 bids) | +$89.71 (520 bids) | +$39.81 (682 bids) | +$82.26 (896 bids) | +$64.10 (1008 bids) | +$64.10 (1008 bids) |
| $400 | +$0.00 (0 bids) | +$75.00 (312 bids) | +$75.00 (312 bids) | +$168.33 (520 bids) | +$146.47 (896 bids) | +$108.19 (1008 bids) |


Check of the method on the real $4 bids: the trade-list method and Kalshi agree on 'did it get bought or not' for 959 of 1008 bids. Real contracts bought: 2,981, the method says 2,969.


### Paper track kc_maker_safe_usd (only bids that got bought on paper, so 'got anything' flatters it): 1181 bids over 14.7 days (about 80 a day), 1 on the losing side


| Bid size | Bids that got anything | Money that filled | P&L | Per $100 | A day | Winners got | Losers got | Worst day | Worst 15 minutes |
|---|---|---|---|---|---|---|---|---|---|
| $4 | 1181 of 1181 | $4,683 | +$22.23 | +$0.47 | +$1.51 | 100 in 100 | 100 in 100 | -$2.63 | -$3.99 |
| $10 | 1181 of 1181 | $11,675 | +$55.36 | +$0.47 | +$3.77 | 99 in 100 | 100 in 100 | -$6.60 | -$9.97 |
| $25 | 1181 of 1181 | $29,029 | +$137.52 | +$0.47 | +$9.36 | 99 in 100 | 100 in 100 | -$16.53 | -$24.93 |
| $50 | 1181 of 1181 | $57,758 | +$273.16 | +$0.47 | +$18.58 | 98 in 100 | 100 in 100 | -$33.14 | -$49.85 |
| $100 | 1181 of 1181 | $114,543 | +$538.73 | +$0.47 | +$36.65 | 97 in 100 | 100 in 100 | -$66.59 | -$99.70 |
| $200 | 1181 of 1181 | $224,918 | +$1,044.00 | +$0.46 | +$71.02 | 95 in 100 | 100 in 100 | -$133.76 | -$199.40 |
| $400 | 1181 of 1181 | $435,775 | +$1,988.79 | +$0.46 | +$135.30 | 92 in 100 | 100 in 100 | -$271.42 | -$399.80 |


Most bids open at the same moment: 7. So covering every bid takes about 7 times the bid size.


What an account of a given size makes a day (a bid is skipped when the money is tied up in other bids):


| Bid size | $300 account | $500 account | $700 account | $1,000 account | $2,000 account | No limit |
|---|---|---|---|---|---|---|
| $4 | +$1.51 (1181 bids) | +$1.51 (1181 bids) | +$1.51 (1181 bids) | +$1.51 (1181 bids) | +$1.51 (1181 bids) | +$1.51 (1181 bids) |
| $10 | +$3.77 (1181 bids) | +$3.77 (1181 bids) | +$3.77 (1181 bids) | +$3.77 (1181 bids) | +$3.77 (1181 bids) | +$3.77 (1181 bids) |
| $25 | +$9.36 (1181 bids) | +$9.36 (1181 bids) | +$9.36 (1181 bids) | +$9.36 (1181 bids) | +$9.36 (1181 bids) | +$9.36 (1181 bids) |
| $50 | +$18.31 (1167 bids) | +$18.58 (1181 bids) | +$18.58 (1181 bids) | +$18.58 (1181 bids) | +$18.58 (1181 bids) | +$18.58 (1181 bids) |
| $100 | +$29.61 (958 bids) | +$34.99 (1133 bids) | +$36.65 (1181 bids) | +$36.65 (1181 bids) | +$36.65 (1181 bids) | +$36.65 (1181 bids) |
| $200 | +$23.95 (500 bids) | +$45.24 (785 bids) | +$57.06 (958 bids) | +$67.71 (1133 bids) | +$71.02 (1181 bids) | +$71.02 (1181 bids) |
| $400 | +$0.00 (0 bids) | +$43.23 (500 bids) | +$43.23 (500 bids) | +$85.17 (785 bids) | +$128.75 (1133 bids) | +$135.30 (1181 bids) |


### Paper track kc_maker_safe (only bids that got bought on paper, so 'got anything' flatters it): 2104 bids over 17.6 days (about 120 a day), 12 on the losing side


| Bid size | Bids that got anything | Money that filled | P&L | Per $100 | A day | Winners got | Losers got | Worst day | Worst 15 minutes |
|---|---|---|---|---|---|---|---|---|---|
| $4 | 2104 of 2104 | $8,303 | +$38.79 | +$0.47 | +$2.20 | 100 in 100 | 100 in 100 | -$2.04 | -$7.80 |
| $10 | 2104 of 2104 | $20,698 | +$96.46 | +$0.47 | +$5.48 | 99 in 100 | 100 in 100 | -$5.09 | -$19.51 |
| $25 | 2104 of 2104 | $51,475 | +$239.44 | +$0.47 | +$13.61 | 99 in 100 | 100 in 100 | -$12.70 | -$48.77 |
| $50 | 2104 of 2104 | $102,476 | +$470.69 | +$0.46 | +$26.75 | 98 in 100 | 100 in 100 | -$25.21 | -$97.55 |
| $100 | 2104 of 2104 | $203,160 | +$912.69 | +$0.45 | +$51.87 | 97 in 100 | 100 in 100 | -$53.86 | -$196.06 |
| $200 | 2104 of 2104 | $396,963 | +$1,687.64 | +$0.43 | +$95.91 | 95 in 100 | 100 in 100 | -$121.04 | -$393.12 |
| $400 | 2104 of 2104 | $761,155 | +$2,942.29 | +$0.39 | +$167.21 | 90 in 100 | 100 in 100 | -$275.24 | -$787.22 |


Most bids open at the same moment: 7. So covering every bid takes about 7 times the bid size.


What an account of a given size makes a day (a bid is skipped when the money is tied up in other bids):


| Bid size | $300 account | $500 account | $700 account | $1,000 account | $2,000 account | No limit |
|---|---|---|---|---|---|---|
| $4 | +$2.20 (2104 bids) | +$2.20 (2104 bids) | +$2.20 (2104 bids) | +$2.20 (2104 bids) | +$2.20 (2104 bids) | +$2.20 (2104 bids) |
| $10 | +$5.48 (2104 bids) | +$5.48 (2104 bids) | +$5.48 (2104 bids) | +$5.48 (2104 bids) | +$5.48 (2104 bids) | +$5.48 (2104 bids) |
| $25 | +$13.61 (2104 bids) | +$13.61 (2104 bids) | +$13.61 (2104 bids) | +$13.61 (2104 bids) | +$13.61 (2104 bids) | +$13.61 (2104 bids) |
| $50 | +$26.30 (2079 bids) | +$26.75 (2104 bids) | +$26.75 (2104 bids) | +$26.75 (2104 bids) | +$26.75 (2104 bids) | +$26.75 (2104 bids) |
| $100 | +$48.27 (1648 bids) | +$48.07 (2011 bids) | +$51.87 (2104 bids) | +$51.87 (2104 bids) | +$51.87 (2104 bids) | +$51.87 (2104 bids) |
| $200 | +$41.34 (792 bids) | +$63.50 (1295 bids) | +$89.69 (1648 bids) | +$88.30 (2011 bids) | +$95.91 (2104 bids) | +$95.91 (2104 bids) |
| $400 | +$0.00 (0 bids) | +$68.24 (792 bids) | +$68.24 (792 bids) | +$109.36 (1295 bids) | +$152.04 (2011 bids) | +$167.21 (2104 bids) |

Run: probe `big_kreal` (run 45982307713, 27 Nov 2026, 38 minutes: about 4,300 trade lists).
