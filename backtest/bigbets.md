# Do the leads still pay at real-money sizes? (bigbets.py, 2026-11-10)

Paper only, research only. The paper tracks buy about $1-5 a bet. Jan's real money would be $25-100 a bet.
Code: `bigbets.py`, run with probe `big_all` (or `big_live`, `big_kalshi`, `big_hist`). Numbers below are from
probe runs 42897607039 (Kalshi, old trades) and 42898921990 (today's books), both 10 Nov about 20:45-20:55 UTC.
One evening snapshot for the books: worth one re-run on a weekday afternoon before 1 Jan.

## Plain summary

| Lead | Profit per $100 at paper size | Left at $100 a bet | Chances | Can $300-500 be used? |
|---|---|---|---|---|
| `boring_no` (No at 90-97c, 30+ days out) | +$5.45 (backtest) | **+$5.37**: a $100 bet costs about 8c more | 56 on sale tonight, 54 take $100 | **Yes, easily.** But each bet is stuck 1+ months, and one loss costs about $94 |
| `crypto_no` (No at 70-90c, 3-7 days out) | +$6.95 (backtest) | **+$6.67**: a $100 bet costs about 30c more | 24 on sale tonight, 21 take $100. New ones every week | **Yes.** $2,210 fits right now at $100 a bet, money back in 3-7 days |
| `soccer_draw` (draws 15-50c, a day before kickoff) | +$5.60 (backtest) | **+$3.40 to +$3.70** where it fits | 4 buyable tonight, only 2 take even $25 | **Barely.** All 4 games together take $224. Half the games have only about $12 on sale |
| `kc_maker_safe` (Kalshi 15-min crypto bids) | +$0.56 (backtest), **+$0.18 live** (real tape, $10 bids) | **+$0.14** (real tape, $100 bids) | about 120 a day | **Yes, money comes back every 15 min.** But the profit is tiny: about $10 a day on $300, and one loss costs about $50-100 |
| `mention_no` (bonus) | +$4.35 (backtest) | about +$4.00 | 2 on sale tonight, 0 take $100 | **No.** $106 fits in total |

What it means:
- **Size is not the problem for boring_no and crypto_no.** Their books are deep. Paying for $100 instead of $5
  costs pennies. If they pass on 21 Dec, $300-500 fits.
- **Soccer draws are too thin for $100 bets.** The lead is only about 2c a bet, and it's gone at 4c. Where a game
  takes $100 the extra cost is small (about half a cent a share), but half the games only take $12-25. At $25 a bet
  it can work; at $100 it mostly can't.
- **kc_maker_safe can use the money but barely earns.** At real tape fills it makes 14-18c per $100 bet live, under
  its own pass bar (+$0.22). Bigger bids get slightly worse, because losing bets fill completely and winning bets
  sometimes only partly.
- **A bot fill-model problem found on the way (Kalshi):** the bot counts a resting bid as fully filled as soon as one
  contract trades below it. For a paper bid that isn't really in the book, that's too kind: the seller would only
  have hit us for what they sold. On the real tape: `kc_maker_safe` +$0.18 per $100 (bot says +$0.21), `kc_maker`
  -$0.51 (bot says -$0.45), `kc_maker_early` **-$12.05 (bot says -$4.53)**. Not changed: kc_maker_safe's pass test
  is locked, so this is Jan's call.

## Today's order books (Polymarket)

Every market each track's rules match right now (not only the ones it bought), its real book walked at the paper
size and at $25/$50/$100, with the bot's own price limit (never more than listed price + the track's
`max_over_listed`, never above the band's top + 1c). 'Extra' = how much more a share costs than at paper size.
'Profit left' = the backtest's profit per $100 minus that extra price and fee.

| Track | Stake | Markets where it all fits | Extra per share | Profit per $100 left | Money that fits, all markets |
|---|---|---|---|---|---|
| soccer_draw (4) | $25 | 2 of 4 | +0.54c | +$3.66 | $74 |
| | $50 | 2 of 4 | +0.55c | +$3.60 | $124 |
| | $100 | 2 of 4 | +0.59c | +$3.42 | $224 |
| boring_no (56) | $25 | 56 of 56 | +0.02c | +$5.43 | $1,400 |
| | $50 | 55 of 56 | +0.05c | +$5.40 | $2,778 |
| | $100 | 54 of 56 | +0.08c | +$5.37 | $5,518 |
| crypto_no (24) | $25 | 23 of 24 | +0.10c | +$6.83 | $598 |
| | $50 | 22 of 24 | +0.16c | +$6.76 | $1,160 |
| | $100 | 21 of 24 | +0.24c | +$6.67 | $2,210 |
| mention_no (2) | $25 | 1 of 2 | +0.00c | +$4.35 | $45 |
| | $50 | 1 of 2 | +0.11c | +$4.21 | $70 |
| | $100 | 0 of 2 | +0.27c | +$4.01 | $106 |

Soccer: 312 games scanned, 15 draw markets 20-28h before kickoff, 10 in the price band, 4 with a real ask inside the
limit. Thinnest: Real Cundinamarca vs Real Cartagena and Torreense vs Sparta Prague ($12-13 of $100 fits). The
window rolls about 3 times a day, so roughly 10 buyable games a day, half of them thin.

The "bought in the last 24 hours" counts read only the newest 500 trades per market, so they are rough: typical $501
for boring_no answers, $4 for crypto_no, $165 for mention_no, $0 for draws. Deep books with few buyers means market
makers fill the books; that's good for us.

## Kalshi 15-minute crypto: bigger resting bids on the real trade tapes

Every finished order of the live paper tracks (about 1 day, 9-10 Nov), its real trade tape read again. A bid of $S at
price P gets what people really sold at P after the queue that was there first, plus everything sold below P.

| Track | Bid size | Fully filled | Money that filled | P&L | Per $100 | Bot's own record |
|---|---|---|---|---|---|---|
| kc_maker_safe (124 orders, 1 lost) | $10 | 123 of 124 | $1,239 | +$2.26 | +$0.18 | +$0.21 |
| | $25 | 122 of 124 | $3,068 | +$5.45 | +$0.18 | +$0.21 |
| | $50 | 120 of 124 | $6,075 | +$10.06 | +$0.17 | +$0.21 |
| | $100 | 114 of 124 | $11,930 | +$16.29 | +$0.14 | +$0.21 |
| kc_maker (259, 5 lost) | $10 | 253 of 259 | $2,539 | -$12.95 | -$0.51 | -$0.45 |
| | $100 | 233 of 259 | $24,343 | -$147.70 | -$0.61 | -$0.46 |
| kc_maker_early (164, 16 lost) | $10 | 95 of 164 | $959 | -$115.53 | -$12.05 | -$4.53 |
| | $100 | 91 of 164 | $9,279 | -$1,175.14 | -$12.66 | -$4.56 |

At $100 bids, kc_maker_safe's winning bets got 96 of every 100 contracts they asked for and the losing bet got all
100. kc_maker_early's winners got only 52 of 100. That's the classic market-maker trap: you get all of the bad bets
and only part of the good ones.

How much of $300-500 is used (kc_maker_safe's live orders, each open up to 5.5 min, at most 6 at once):
- $25 or $50 bids: every order fits in $300. About $3,000 (at $25) or $6,000 (at $50) goes through a day.
- $100 bids: $300 takes 89 of 125 orders a day (3 at a time), $500 takes 118.
- At the live rate (+$0.17 per $100) that's about $10 a day with $50 bids. One loss is about -$50.

## Old trades (boring_no, crypto_no)

Same bets as the backtest (`backtest/winners.md`), each spending $25/$50/$100 at what the next real $100+ buyers
paid, in order, never above the band's top + 2c. Our trade lists only hold buys of $100 or more, so a single $100 bet
fits by design; the useful part is how much more was bought soon after.

- crypto_no: 115 bets in 36 weeks of our sample (about 3 a week; the live scan finds far more, the sample is
  only 19,625 markets). First real buy after a signal: typically $264. In the next 6 hours people bought a typical
  $818 inside the band (a quarter under $270).
- boring_no: 101 bets in 44 weeks (about 2 a week in the sample). First real buy typically $194; $723 bought in the
  next 6 hours (a quarter under $185).
- So even in history there was usually several hundred dollars on sale at the backtest price within hours.
