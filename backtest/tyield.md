# Treasury yield "how high / how low" bets vs a simple model (27 Nov 2026)

`tyield.py`, data in `bt_cache/nf/ty/` (shared price store). Paper research only.

**Verdict: dropped.** The free yield history plus a simple "how far can it wander" model does not beat the price
in a way you can buy. Every rule that looked ahead rests on one month (September 2026, when yields jumped) and
falls apart without it.

## What these bets are

"Will the 10-year Treasury yield hit 4.82% in September?" Polymarket lists a ladder of levels per month (2, 5,
10, 30 year; how high and how low), plus to-year-end ladders ("before 2027") and, in 2025, a few one-day "above
4.5% on Friday?" bets. Kalshi has the same thing: monthly and weekly ladders (KX10YRDIRHM / LM / HW / LW, the 2,
5 and 30 year too), and day bets "above X% on Nov 25?" (KXUST10AD, KXUST10A, KXUST2A).

**Both sites settle on Treasury.gov's Daily Par Yield Curve** (one number a day, set near the close), not on the
yield's moves during the day. So a model on daily closes is exactly the right yardstick: no intraday trap here.
Treasury.gov's CSV is readable from Actions; FRED timed out from Actions on this run.

## What was there

| | Polymarket | Kalshi |
|---|---|---|
| Rungs with trades and a readable rule | 316 (54 events, Apr 2025-Nov 2026) | 2,066 (152 events, Jul-Nov 2026) |
| Finished (whole span over, every rung answered) | 188 rungs: 7 ladder spans + 15 one-day bets | 1,940 rungs, but only Jul-Nov 2026 |
| Money traded | ~$11.8 million; $5.9 million of it on the 2025 "how high" ladder | KXUST10AD ~$2.2 million in contracts, ladders ~$50-170 thousand each |
| Fee | 1c per $1 rate (tiny) on the new ones, 0 on older ones | Kalshi's usual fee |

The new Sep-Nov 2026 Polymarket families: September and October monthly ladders are finished (16 ladders);
November ends 30 Nov and the "before 2027" ladders are open. Careful: the rungs already settled in an open
ladder are only the ones that were hit (Yes). Counting them alone makes "buy Yes" look great (+$87.74 per $100
in a first pass). Only finished spans are scored below.

## The test

Every day at 02:00 UTC (US market closed, the day's Treasury number published): the chance the yield touches
the level before the span ends, from yesterday's close, the business days left, and the typical daily move over
the last 60 days (no drift; the reflection rule, with and without the usual fix for "only daily closes count").
One-day bets use the plain bell curve. Buy the side the model likes when it is 10c+ away from the last real
price, once per rung, $10 a bet, at the worst real price of the next 2 hours + 1c + fee (Kalshi: the real
sell offer + fee). Rungs of one month move together, so the exam counts one month (or one day for day bets) as
one bet.

**Who guesses better** (finished spans, daily looks; lower miss is better):

- Ladders: the plain model is a bit sharper than the price on both sites (Polymarket miss 0.095 vs 0.100,
  Kalshi 0.137 vs 0.149). With the daily-close fix it is a tie.
- One-day bets: the price is clearly sharper (it already knows the overnight move).

**Rules (exam verdicts):**

| Rule | Bets (separate) | P&L per $100 | Verdict |
|---|---|---|---|
| Polymarket, both sides, 10c gap | 100 (22) | +$12.94 | Ahead, but could be luck; without its best 3 months -$28.71 |
| Polymarket, ladders only, plain model | 83 (7) | +$50.05 | Too early to tell; September 2026 made $375 of $417, without the best 3 -$57.92 |
| Polymarket, one-day bets only | 15 (15) | +$26.52 | Ahead, but could be luck; first half -$9.72 |
| Kalshi, both sides, 10c gap | 864 (74) | -$6.20 | Behind, but could be bad luck |
| Kalshi, ladders only, plain model | 338 (4) | -$5.65 | Too early to tell; Sept +$207, Oct -$440 |
| Kalshi, one-day bets only | 542 (70) | -$9.91 | Behind, but could be bad luck |

Also tried (counted in `tries`): Yes only, No only, 20c gap, +2c price, the daily-close fix on or off. Kalshi
Yes-only +$5.80 on 547 bets, No-only -$20.90: that is just yields falling in Oct-Nov, not skill.

**Biggest wins read one by one:** they are all "yield jumped in September 2026, cheap Yes on a high rung paid"
(Polymarket 10-year September ladder, Kalshi 30-year September ladder, a 2-year Friday bet at 5c). Real buys at
real prices, but one market move, not a repeatable edge.

**Backward look** (first look of every finished rung): rungs more than 2 daily swings away paid 1 of 18
(Polymarket) and 0 of 34 (Kalshi) and were priced at 10-25c, so far rungs look a bit dear. But that is 52
rungs from a handful of months, picked after looking, and on Kalshi those far rungs barely trade. "Low" rungs
paid more than "high" ones on Kalshi because yields fell after September. Nothing to build.

## Ceiling (rough guess)

- Most it could make in an average day at its best size: about $0 (no edge found); even if the ladder lean were
  real, about $1-2 a day.
- Money needed: $100-300.
- Bet size where it stops growing: about $25-50 a rung; a monthly Polymarket ladder trades only $20-40 thousand
  in a whole month, Kalshi ladders less.
- A bad day: about -$50 to -$100 at $10 a rung on a normal ladder day, because every rung of a month loses together when yields move
  the other way (Kalshi October 2026: -$440 on $2,429 of bets, 237 rungs, in one month).

## Traps

- Open ladders: settled rungs are only the hit ones (all Yes). Score finished spans only.
- Group by month (all tenors and both directions move together), not by rung or event.
- Kalshi says "above" (strictly), Polymarket "reaches or is higher" for highs; both say "lower than" for lows.
- A day's Treasury number is out around 21:00-23:00 UTC; look after that or the model peeks ahead.
- FRED timed out from Actions; use the Treasury.gov CSV (`ust_par.json.gz`, 2024-2026).

Re-check for free: with the November 2026 ladders and the "before 2027" ladders finished (early January), rerun
`python3 tyield.py run` and `run kalshi` after `python3 tyield.py fetch` / `kfetch dir`. That adds 2 months.
