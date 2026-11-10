# One model that looks at everything together (2026-11-10, `combo.py`)

**Short answer:** on the chart the model looks brilliant (+$15 to +$22 per $100 on months it never saw). At prices
people really paid it shrinks to **+$0 to +$8 per $100, and luck alone covers that range**. Verdict: "Ahead, but
could be luck". No new candidate yet.

- **The trap it fell into:** ghost prices. Dead markets show a chart price near 50c that nobody will sell at. Most
  things don't happen, so "No at 50-70c" looks like free money. For about 3 of every 4 of the model's bets, nobody
  sold anything within 3 hours.
- **The fair version** ("moving prices only": learn and bet only where the price changed since yesterday) is the
  best of the three: +$15.39 on the chart, **+$7.66 per $100 at real buys** on 259 bets, luck range -$4.23 to
  +$19.54, worst case -$14.96. Still mostly "No" bets: the old things-don't-happen lean.
- **The crowd beat the math:** over all markets the plain price guessed results a little better than the model, in
  every version. The model only "wins" on the hand-picked bets where it disagrees most, and that's where the
  ghost prices live.
- 15 versions were tried (3 models x 5 gaps); the luck bar counts them.

What would settle it: real order book history (so we know what could really be bought), or freezing the fair
version now and scoring it once on the 21 Dec holdout.

---

Research only. Every earlier test looked at one or two things at a time. This is one math model (gradient-boosted trees) that reads price, price moves, kind of market, time left, age, the rival choices in the event, weekday and fee together, and guesses the chance of Yes. It learned only from markets that ended before 10 Aug, picked its betting rule on the last 6 weeks of those, and was then judged once on 10 Aug - 9 Nov. Polymarket only (our Kalshi history is too short to learn on).

- Learned on **442,196** market-days (92,597 markets that ended before 10 Aug).
- Judged on **208,280** market-days (37,713 markets, 10 Aug - 9 Nov) it never saw.

## Does the model guess better than the price?

A score for how wrong the guesses were on the judged months (lower is better). If the price wins, the model has nothing to sell.

| Version | The market price | The model | Better guesser |
|---|---|---|---|
| with the clock | 0.2957 | 0.2982 | the price |
| no clock | 0.2957 | 0.2978 | the price |
| moving prices only, no clock | 0.3099 | 0.3180 | the price |

## The model's bets on the months it never saw

It bets $25 when its own chance is at least the 'gap' above what the bet costs (chart price + the usual extra + fee). One bet per market, held to the end.

| Version | Gap it bets on | Bets | Separate events | Per $100 | Luck range | First / second half | Worst case per $100 | Verdict |
|---|---|---|---|---|---|---|---|---|
| with the clock | 12c (tuning weeks: +$25.97 per $100 on 1309 bets) | 2,329 (257 Yes, 2,072 No) | 88 | +$20.81 | +$14.68 to +$26.95 | +$22.21 / +$16.72 | +$7.03 | Looks real |
| no clock | 12c (tuning weeks: +$22.28 per $100 on 1291 bets) | 2,347 (259 Yes, 2,088 No) | 712 | +$22.09 | +$17.02 to +$27.17 | +$19.95 / +$24.57 | +$11.47 | Looks real |
| moving prices only, no clock | 12c (tuning weeks: +$12.52 per $100 on 1008 bets) | 1,737 (338 Yes, 1,399 No) | 89 | +$15.39 | +$8.88 to +$21.89 | +$14.79 / +$16.87 | +$0.94 | Looks real |

## 'with the clock': a closer look

| Slice | Bets | Per $100 |
|---|---|---|
| No: 50-70c | 1,430 | +$29.11 |
| kind: other | 975 | +$29.65 |
| kind: crypto price | 427 | +$6.44 |
| No: 70-90c | 422 | +$11.87 |
| kind: elections | 404 | +$14.57 |
| kind: apps/tech | 173 | +$25.63 |
| No: 30-50c | 167 | +$7.52 |
| Yes: 50-70c | 104 | +$5.01 |
| kind: entertainment | 89 | +$21.50 |
| kind: mentions | 78 | +$25.98 |
| kind: stocks | 60 | +$34.03 |
| kind: economics | 59 | -$5.48 |
| Yes: 10-30c | 56 | +$6.78 |
| Yes: 30-50c | 53 | -$1.55 |

**At real buys:** 900 of its bets checked on the trade tape. 243 had a real buy within 3 hours (the rest: nobody was selling). Those came out at **+$1.53 per $100** (luck range -$16.95 to +$20.00, worst case -$39.87). Exam verdict: **Ahead, but could be luck**. (The same 900 bets at chart prices: +$21.85.)

What the model leans on most: price (588.0), lowest so far (18.6), price 1 day ago (2.9), highest so far (2.7), kind of market (2.7), age of the market (days) (2.4).

## 'no clock': a closer look

| Slice | Bets | Per $100 |
|---|---|---|
| No: 50-70c | 1,447 | +$28.69 |
| kind: other | 990 | +$28.83 |
| kind: crypto price | 441 | +$4.74 |
| No: 70-90c | 397 | +$13.23 |
| kind: elections | 370 | +$15.48 |
| kind: apps/tech | 189 | +$21.20 |
| No: 30-50c | 185 | +$12.15 |
| kind: entertainment | 92 | +$23.49 |
| Yes: 50-70c | 91 | +$14.91 |
| Yes: 30-50c | 81 | +$18.78 |
| kind: mentions | 80 | +$17.05 |
| kind: geopolitics | 67 | +$76.25 |
| kind: stocks | 58 | +$29.31 |
| No: 10-30c | 52 | -$6.81 |

**At real buys:** 900 of its bets checked on the trade tape. 233 had a real buy within 3 hours (the rest: nobody was selling). Those came out at **+$4.66 per $100** (luck range -$14.79 to +$24.12, worst case -$40.60). Exam verdict: **Ahead, but could be luck**. (The same 900 bets at chart prices: +$18.00.)

What the model leans on most: price (586.8), lowest so far (21.3), kind of market (2.9), the leader's price (2.7), price 1 day ago (2.7), age of the market (days) (2.6).

## 'moving prices only, no clock': a closer look

| Slice | Bets | Per $100 |
|---|---|---|
| No: 50-70c | 718 | +$21.94 |
| kind: other | 674 | +$18.86 |
| kind: crypto price | 411 | +$2.74 |
| No: 70-90c | 335 | +$10.58 |
| kind: elections | 283 | +$13.67 |
| No: 30-50c | 280 | +$11.70 |
| Yes: 50-70c | 148 | +$16.73 |
| kind: apps/tech | 127 | +$16.51 |
| kind: geopolitics | 78 | +$47.90 |
| Yes: 30-50c | 70 | +$37.83 |
| No: 10-30c | 59 | +$41.44 |
| Yes: 10-30c | 51 | -$27.67 |
| Yes: 70-90c | 47 | -$6.10 |
| kind: stocks | 47 | +$42.92 |

**At real buys:** 900 of its bets checked on the trade tape. 259 had a real buy within 3 hours (the rest: nobody was selling). Those came out at **+$7.66 per $100** (luck range -$4.23 to +$19.54, worst case -$14.96). Exam verdict: **Ahead, but could be luck**. (The same 900 bets at chart prices: +$12.81.)

What the model leans on most: price (589.6), lowest so far (20.5), highest so far (6.7), price 1 day ago (5.6), what the choices add up to (2.7), the leader's price (1.4).

## Limits

- Chart prices are 12-hourly, so the price the model sees can be up to 13 hours old. The real-buy check is the number to trust.
- Judged months include only markets that ended before 2026-11-10 (we need the result; later ones are the holdout).
- bt_cache has markets with $20k+ traded plus every choice of those events. Tiny markets are missing.

