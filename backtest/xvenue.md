# Same bet on two sites: Kalshi vs Polymarket 15-minute crypto (xvenue.py)

Research only, no track. 10 Nov 2026.

## The short version

**The idea.** Both sites list "is BTC higher at 10:15 than at 10:00". Buy UP on one site and DOWN on the other.
If the two cost less than $1.00 together, one of them pays $1.00. Reddit and GitHub are full of bots that claim this.

**The verdict: not for us.**

- A pair normally costs **$1.05** with both fees. Pays $1.00. That is a 5c loss every time, not a win.
- The recordings do show pairs under $1.00, but they are mostly a timing trick: our recorder reads Kalshi first and
  Polymarket about **20 seconds later**, and these prices move more than 1c every 5 seconds. Line the two up to the
  same second and "gaps" drop from 241 in every 1,000 reads to 7.
- Live check, both sites read in the same second for 2 hours: 46 real chances, worth **+$1.89 in total** on $10 bets
  (about 4c each). Real, but crumbs, and half vanish within 2 seconds (section 5).
- The two sites do not always agree who won: **17 windows in 1,000** end with different results (different price
  feeds). Then a pair pays $0 or $2. One $0 on a $10 bet eats about 60 small wins.

Recordings 08 Nov 22:15 to 10 Nov 15:45 UTC (36 hour files), 704 windows listed on both sites
(BNB, BTC, DOGE, ETH, HYPE, SOL, XRP, ZEC). Each bet is 10 shares on each site, both fees paid.
Polymarket price = the recorded asks. Kalshi price = the worst price a real buyer paid within a few seconds.

## 1. The recorder reads the two sites at different moments

Each book is stamped with the minute the recorder's round started, not the second it was read. Lining each site's
book up with that site's own trades shows when it was really read (smaller = closer):

| Seconds after the stamp | -10 | -5 | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kalshi: book vs its own trades, cents apart | 3.4 | 2.6 | **1.4** | 1.9 | 3.0 | 3.8 | 4.4 | 5.0 | 5.6 | 5.9 | 6.4 | 6.9 | 7.3 | 7.6 | 8.0 |
| Polymarket: book vs its own trades, cents apart | 5.9 | 5.6 | 4.8 | 4.1 | 3.4 | 2.1 | **1.4** | 3.1 | 4.0 | 4.6 | 6.0 | 6.5 | 7.7 | 8.3 | 8.1 |

Best match: Kalshi at about +0 s, Polymarket at about +20 s. Any test that compares the two books straight from one
recorder round sees gaps that were never there. **Fixed going forward:** from this PR on, every recorded book also
saves `rt`, the real second it was read.

## 2. What the pair costs

A pair pays $1.00 when the sites agree. "Under $1.00" is what a bot would call a gap.

| How the two prices are lined up | Reads | Typical cost before fees | Typical cost with fees | Under $1.00 | Under $0.99 | Under $0.97 |
|---|---|---|---|---|---|---|
| Naive: both books from the same recorder round | 6,368 | $1.010 | $1.026 | 1,533 (241 in 1,000) | 1,110 | 648 |
| Same second: Kalshi trades within 2 s of the Polymarket read | 5,958 | $1.020 | $1.039 | 432 (73 in 1,000) | 207 | 76 |
| Same second: Kalshi trades within 5 s of the Polymarket read | 6,217 | $1.029 | $1.050 | 139 (22 in 1,000) | 63 | 23 |
| Same second: Kalshi trades within 8 s of the Polymarket read | 6,238 | $1.030 | $1.057 | 43 (7 in 1,000) | 18 | 7 |

The stricter the line-up, the fewer gaps. That is what timing noise looks like, not free money.

| Minutes before the end | Reads | Typical cost with fees | Under $1.00 |
|---|---|---|---|
| 15 to 12 | 1,309 | $1.064 | 20 |
| 12 to 9 | 1,333 | $1.054 | 25 |
| 9 to 6 | 1,445 | $1.042 | 29 |
| 6 to 3 | 1,488 | $1.036 | 42 |
| 3 to 0 | 642 | $1.047 | 23 |

## 3. Buying every gap, scored on the real results

First gap per window and direction. "Paid $0 / paid $2" = bets where the two sites disagreed (both legs lost / both won).

**Read this table with care.** A pair bought under $1.00 wins by definition whenever the sites agree, so every
"gap" row is green. The real question is whether those prices could be bought at the same moment. The first three
rows could not (20 seconds apart). The rows below them shrink fast as the timing gets stricter.

| Rule | Bets | Money in | P&L | P&L per $100 | Luck range (90 of 100) | Paid $0 / paid $2 |
|---|---|---|---|---|---|---|
| Naive line-up: buy when the pair costs under $1.00 | 505 | $4,859 | +$190.90 | +$3.93 | +$3.48 to +$4.36 | 2 / 2 |
| Naive line-up: buy when the pair costs under $0.99 | 449 | $4,266 | +$224.43 | +$5.26 | +$4.73 to +$5.78 | 2 / 2 |
| Naive line-up: buy when the pair costs under $0.97 | 358 | $3,311 | +$269.15 | +$8.13 | +$7.52 to +$8.76 | 2 / 2 |
| Same second (+-5 s): buy when the pair costs under $1.00 | 114 | $1,122 | +$18.45 | +$1.65 | +$1.12 to +$2.26 | 0 / 0 |
| Same second (+-5 s): buy when the pair costs under $0.99 | 57 | $552 | +$17.74 | +$3.21 | +$2.43 to +$4.05 | 0 / 0 |
| Same second (+-5 s): buy when the pair costs under $0.97 | 21 | $198 | +$11.74 | +$5.92 | +$4.41 to +$7.28 | 0 / 0 |
| Same second, strict (+-8 s): buy when the pair costs under $1.00 | 39 | $383 | +$6.50 | +$1.70 | +$1.06 to +$2.58 | 0 / 0 |
| Same second, strict (+-8 s): buy when the pair costs under $0.99 | 17 | $164 | +$5.79 | +$3.53 | +$2.26 to +$5.25 | 0 / 0 |
| Same second, strict (+-8 s): buy when the pair costs under $0.97 | 7 | $66 | +$4.23 | +$6.43 | +$4.14 to +$9.89 | 0 / 0 |
| **Control: buy the pair at every read, gap or not** | 6,217 | $65,749 | **-$3,588.53** | **-$5.46** | -$5.66 to -$5.25 | 12 / 11 |

Even the strictest row is at most 39 bets in 40 hours across 8 coins, +$6.50 in total, and the recordings cannot
tell the second exactly (the Polymarket read time is known to about 5 s). The 57 under-$0.99 bets bunch up:
7 in the 09 Nov 19:45 window, 6 at 06:15, 4 at 06:45. Several coins in the same window = one fast market move
caught a few seconds apart, not a standing offer.

## 4. How often the two sites disagree on the result

Kalshi settles on a 60-second average of one price index, Polymarket on a single Chainlink price. When the coin
ends almost exactly where it started, they can disagree. Then a pair pays $0 or $2. Last 30 days:

| Coin | Windows on both sites | Same result | Kalshi up, Polymarket down | Kalshi down, Polymarket up | Disagree, out of 1,000 |
|---|---|---|---|---|---|
| BTC | 2,839 | 2,791 | 24 | 24 | 17 |
| ETH | 2,839 | 2,801 | 20 | 18 | 13 |
| SOL | 2,839 | 2,811 | 12 | 16 | 10 |
| XRP | 2,839 | 2,793 | 37 | 9 | 16 |
| DOGE | 2,839 | 2,798 | 22 | 19 | 14 |
| BNB | 2,839 | 2,749 | 50 | 40 | 32 |
| HYPE | 2,839 | 2,785 | 35 | 19 | 19 |
| ZEC | 2,839 | 2,804 | 14 | 21 | 12 |
| **All** | 22,712 | 22,332 | 214 | 166 | 17 |

So this is never "risk-free". The disagreements also tend to sit exactly where a gap opens: the two sites start
their window from slightly different prices, and when the coin sits between those two prices one side looks cheap
on each site, and both legs lose.

## 5. Live check: both books read in the same second

`xv_live_120`, 10 Nov 18:12 to 20:12 UTC. Every 3 seconds it read both sites' books for all 8 coins within the
same 0.3 seconds. A pair under $1.00 was read again 2 seconds later, and only counted if it was still there.

| What | Number |
|---|---|
| Pair reads | 31,700 (72 coin-windows) |
| Typical pair cost with fees | $1.041 |
| Under $1.00 at the first read | 503 (16 in 1,000) |
| Still under $1.00 2 seconds later | 229 |
| Different bets (one per window and side) | 46 |
| P&L on those 46 bets of 10 pairs, if the sites agree every time | **+$1.89 in total** (about 4c a bet, on about $10 a bet) |

So real same-second gaps exist, but they are crumbs: typically 0.2c to 0.8c a pair, mostly in the last two minutes
when one side costs 1c and the other 98c. Half of them are gone within 2 seconds. And the 4c a bet is before the
"sites disagree" risk from section 4: at 17 disagreements per 1,000 windows, 46 bets expect about one, and when it
lands on the wrong side it costs the whole $10, which is 5 hours of these wins. Too thin to prove and too thin to
live on. **Dropped.**

## Sanity checks

- `xvenue.py selftest`: in a fake fair world (both sites quote the true chance, always agree) buying pairs loses
  its costs (-$4.18 per $100) and finds 0 gaps; one planted 90c pair is found and wins. Passed.
- Control row above: buying at every read loses $5.46 per $100, which matches the typical pair cost of $1.05.
- Timing: the gap count was re-run at four line-ups. It falls every time the line-up gets stricter.
- Results come from each site's own settled result, not from prices.

## How to rerun

`xv_all_30` on the probe workflow (results + replay), `xv_live_<minutes>` for the live check, `xv_selftest`.
