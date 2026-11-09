# Idea machine: hundreds of edge ideas, screened hard

Generated 2026-11-09T21:48:14Z by `ideas.py` (probe `btideas`). Paper only. 172,329 finished markets that ended before 2026-11-10 (the holdout is never read; data: whole events only (622,412 complete events)), 65,243 price snapshots, 29 features (3 of them placebo coin flips). Halves split at 2026-06-30.

How to read: each idea buys one side 1 hour after a snapshot at the history price + 2c + fee and holds to the end. 'vs twins' = how much better than all other bets at the same price and time before the end (so a plain long-shot effect can't pass). Money per $100 staked, events weighted equally.

- Ideas made: 33,823 (feature value x side x price band x time before end)
- With enough events to judge (30+ in a half): 7,604 in half A, 9,058 in half B
- Through discovery (beat twins by 2 standard errors): 221 picked on A, 182 picked on B
- Confirm bar on the other half: 90% after correcting for that many ideas, AND making money at +2c in both halves

**Survivors: 1 real ideas, 0 placebos.** Placebos are 4,881 of the 33,823 ideas, so pure luck would let through about 0.0 real-looking ideas (placebo survivors scaled up). No placebo passed, so the filter is strict enough.

Every number below includes one made-up total loss per idea (so a short lucky run can't pass).

## Survivors

| Idea | Why it might work | Events A / B | Bets | vs twins A / B | +2c A / B | +5c (all) | Passed | Note |
|---|---|---|---|---|---|---|---|---|
| swing size last 7 days = <2c | buy second answer (No) at 50-75c | 1-3 days before the end | after a wild week the price is noisier than it should be | 97 / 56 | 409 | +$13.23 / +$24.73 | +$24.86 / +$35.23 | +$22.76 | picked on A, confirmed on B |  |

Sample questions behind each survivor (check the feature caught what its name says):

- **swing size last 7 days = <2c | buy second answer (No) at 50-75c | 1-3 days before the end**
  - Will Zach Bauchou finish in the Top 10 at the 2026 Cognizant Classic in The Palm Beaches? (52c, won)
  - Will TISZA – Respect and Freedom Party (TISZA) finish with the second-most seats in the next Hungarian parliam
  - Will the Patek Index hit $108,000 (HIGH) by April 30? (73c, won)
  - Will Rayo Vallecano win the 2025-26 UEFA Europa Conference League? (66c, won)
  - Will Chris Gotterup win the 2026 John Deere Classic? (50c, lost)
  - Will Elon Musk post 65-89 tweets from August 27 to August 29, 2026? (68c, won)

## Near misses (beat their twins in both halves, but not by enough)

| Idea | Why it might work | Events A / B | Bets | vs twins A / B | +2c A / B | +5c (all) | Passed | Note |
|---|---|---|---|---|---|---|---|---|
| words: famous name = no | buy first answer (Yes) at 25-50c | 1-3 days before the end | fans and haters overpay for famous names (attention bias) | 1284 / 934 | 6795 | +$9.91 / +$7.41 | -$13.69 / -$9.49 | -$18.56 |  |  |
| PLACEBO coin 1 = group D | buy first answer (Yes) at 25-50c | 1-3 days before the end | none: random groups, should never pass | 368 / 277 | 1978 | +$11.37 / +$15.93 | -$11.71 / -$1.27 | -$14.13 |  |  |
| words: superlative = no | buy first answer (Yes) at 25-50c | 30 days before the end | 'most/highest/first' races: fans overpay for their pick | 216 / 393 | 1288 | +$15.48 / +$13.36 | -$11.71 / -$13.30 | -$19.29 |  |  |
| topic other & fee market = no fees | buy first answer (Yes) at 75-90c | 1-3 days before the end | markets with taker fees scare away the quick traders who fix prices | 37 / 33 | 195 | +$11.50 / +$13.26 | +$8.39 / +$12.33 | +$6.47 |  |  |
| words: superlative = yes | buy first answer (Yes) at 25-50c | 1-3 days before the end | 'most/highest/first' races: fans overpay for their pick | 376 / 70 | 1453 | +$11.07 / +$37.48 | -$9.64 / +$21.10 | -$12.45 |  |  |
| markets in event = 5-14 | buy first answer (Yes) at 25-50c | 1-3 days before the end | big multi-choice events spread attention thin over the outsiders | 1130 / 775 | 5641 | +$8.95 / +$7.16 | -$14.77 / -$10.09 | -$19.43 |  |  |
| topic crypto price & below its high = at its high | buy second answer (No) at 10-25c | 1-3 days before the end | people anchor to the best price they saw (disposition effect) | 137 / 126 | 308 | +$36.71 / +$38.91 | +$24.32 / +$8.36 | +$0.19 |  |  |
| move last 24h = drop 3-10c | buy first answer (Yes) at 10-25c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 644 / 499 | 1666 | +$17.52 / +$17.58 | -$12.82 / -$0.61 | -$21.18 |  | panic fade family (already live) |
| markets in event = 2-4 | buy first answer (Yes) at 25-50c | 30 days before the end | big multi-choice events spread attention thin over the outsiders | 69 / 149 | 264 | +$32.38 / +$19.85 | +$5.83 / -$6.57 | -$10.02 |  |  |
| opening price = opened over 80c | buy first answer (Yes) at 50-75c | 1-3 days before the end | markets that open at a coin flip stay too close to it | 98 / 51 | 231 | +$13.43 / +$19.41 | +$6.08 / +$15.67 | +$4.78 |  |  |
| PLACEBO coin 3 = group A | buy first answer (Yes) at 25-50c | 1-3 days before the end | none: random groups, should never pass | 334 / 281 | 2024 | +$10.60 / +$11.90 | -$12.97 / -$4.79 | -$16.09 |  |  |
| topic crypto price & below its high = 10-30c below | buy first answer (Yes) at 50-75c | 1-3 days before the end | people anchor to the best price they saw (disposition effect) | 168 / 139 | 383 | +$10.03 / +$13.61 | +$1.65 / +$5.69 | -$0.99 |  |  |
| share of life gone = last quarter | buy first answer (Yes) at 25-50c | 7-14 days before the end | people forget a deadline is getting close (time decay is underpriced) | 190 / 311 | 886 | +$14.26 / +$14.32 | -$17.72 / +$3.48 | -$11.80 |  |  |
| swing size last 7 days = 10-25c | buy first answer (Yes) at 25-50c | 30 days before the end | after a wild week the price is noisier than it should be | 124 / 228 | 526 | +$23.78 / +$13.88 | -$3.66 / -$13.17 | -$16.53 |  |  |
| since listing = flat | buy first answer (Yes) at 10-25c | 7-14 days before the end | the opening price sticks longer than it should (anchoring) | 180 / 266 | 861 | +$30.71 / +$21.09 | +$2.69 / +$1.49 | -$13.09 |  |  |
| topic other & move last 7 days = rise 15c+ | buy first answer (Yes) at 75-90c | 1-3 days before the end | slow drift keeps going (underreaction) or snaps back (overreaction) | 35 / 55 | 158 | +$15.30 / +$7.77 | +$12.10 / +$6.70 | +$5.13 |  |  |
| below its high = 10-30c below | buy first answer (Yes) at 25-50c | 30 days before the end | people anchor to the best price they saw (disposition effect) | 139 / 266 | 605 | +$20.96 / +$12.96 | -$6.05 / -$11.86 | -$16.74 |  |  |
| topic crypto price & move last 24h = drop 10c+ | buy first answer (Yes) at 50-75c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 115 / 79 | 210 | +$17.08 / +$14.60 | +$11.21 / +$6.72 | +$4.62 |  | panic fade family (already live) |
| words: famous name = no | buy first answer (Yes) at 25-50c | 30 days before the end | fans and haters overpay for famous names (attention bias) | 224 / 431 | 1275 | +$12.89 / +$10.59 | -$14.11 / -$16.03 | -$21.70 |  |  |
| topic elections & move last 24h = flat | buy second answer (No) at 90-98c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 114 / 425 | 1512 | +$1.95 / +$1.47 | +$0.95 / -$0.50 | -$1.33 |  |  |
| topic crypto price & move last 24h = drop 3-10c | buy first answer (Yes) at 25-50c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 122 / 133 | 305 | +$24.17 / +$19.26 | +$1.64 / +$2.30 | -$6.05 |  | panic fade family (already live) |
| topic elections & share of life gone = middle | buy first answer (Yes) at 10-25c | 7-14 days before the end | people forget a deadline is getting close (time decay is underpriced) | 47 / 119 | 310 | +$63.33 / +$29.73 | +$34.73 / +$10.46 | +$0.34 |  |  |
| words: announce = no | buy first answer (Yes) at 25-50c | 30 days before the end | 'announce/confirm' needs an official act, which is rarer than people think | 244 / 448 | 1400 | +$11.63 / +$11.73 | -$15.31 / -$15.00 | -$21.43 |  |  |
| answer names = yes/no | buy first answer (Yes) at 25-50c | 30 days before the end | the first answer listed gets bought more (position bias), most of all when it isn't Yes/No | 251 / 450 | 1435 | +$11.40 / +$11.19 | -$15.63 / -$15.36 | -$21.76 |  |  |
| words: exact number = yes | buy first answer (Yes) at 25-50c | 30 days before the end | exact counts and prices look precise but are coin flips | 220 / 412 | 1292 | +$12.10 / +$14.34 | -$15.19 / -$11.89 | -$19.53 |  |  |

Best placebo in this list scores 2.1 standard errors in its weaker half: anything near or below that is noise.

## The catalog (features and their stories)

- **market age**: new listings are priced by few people and anchored to the opening price
- **share of life gone**: people forget a deadline is getting close (time decay is underpriced)
- **planned length**: short-lived markets get less attention per question
- **markets in event**: big multi-choice events spread attention thin over the outsiders
- **rank in event**: people overpay for the second favorite and ignore the field
- **added late to event**: a choice added after news is bought on hype
- **move last 24h**: people overreact to fresh news (or underreact and it keeps going)
- **move last 7 days**: slow drift keeps going (underreaction) or snaps back (overreaction)
- **swing size last 7 days**: after a wild week the price is noisier than it should be
- **below its high**: people anchor to the best price they saw (disposition effect)
- **above its low**: people anchor to the worst price they saw
- **since listing**: the opening price sticks longer than it should (anchoring)
- **opening price**: markets that open at a coin flip stay too close to it
- **round price**: people like round prices, so they cluster on them
- **words: threshold**: thresholds ('above', 'at least', '+') are hard to judge, people guess the round number
- **words: range bucket**: one bucket out of many: people overpay for the bucket near today's number
- **words: deadline**: 'by <date>' questions: nothing ever happens, YES drifts down slower than it should
- **words: announce**: 'announce/confirm' needs an official act, which is rarer than people think
- **words: negative**: questions phrased in the negative confuse people, so they buy the wrong side
- **words: superlative**: 'most/highest/first' races: fans overpay for their pick
- **words: famous name**: fans and haters overpay for famous names (attention bias)
- **words: exact number**: exact counts and prices look precise but are coin flips
- **question length**: long, complicated questions put people off, so they stay mispriced
- **answer names**: the first answer listed gets bought more (position bias), most of all when it isn't Yes/No
- **repeating daily series**: the same question every day: people price today like yesterday
- **fee market**: markets with taker fees scare away the quick traders who fix prices
- **PLACEBO coin 1**: none: random groups, should never pass
- **PLACEBO coin 2**: none: random groups, should never pass
- **PLACEBO coin 3**: none: random groups, should never pass

## The data hole, and how whole events fix it (volbias, probe `btideasvolbias`)

The first run on the old cache had one survivor, "buy YES at 25-50c on most/highest/first questions", which was
really weather buckets. Cause: bt_cache keeps only markets whose **final** volume passed $20k, and the bucket that
wins draws trading late, so losing buckets were missing. `ideas.fetch_events()` (probe `btideasfetch`, 2026-11-09)
downloaded every closed event since March with all its choices and filled in the price history of ~52,000 missing
choices. Check, per market, 1 day before the end: YES prices added up vs how many YES won.

| topic | old cache (>$20k) won / expected | whole events won / expected |
|---|---|---|
| weather | 1.27 (6,203 markets) | **0.97** (15,839 markets) |
| other | 1.06 | 0.95 |
| apps/tech | 1.14 | 1.04 |
| crypto price | 1.01 | 1.00 |
| elections | 1.02 | 0.98 |
| mentions | 0.77 (131 markets) | 0.81 (1,173 markets) |

So whole events remove the hole. The screen above uses complete events only (every choice that traded $500+ is in
the data). Use `ideas.load_full()` / `ideas.load_screen_set()` for any multi-choice backtest.

**mention_no check** (NO at 25-90c the first time a market is within 7 days of its end, +2c + fee, averaged per
event): old cache +$1.50 per $100 on 51 events, whole events **+$8.33 per $100 on 66 events** (YES in mention markets
won 0.81 of what its price said). The hole did not flatter mention_no; with all the words in, it looks a bit better.
This is in-sample (markets ending before 2026-11-10) and doesn't replace the pre-registered holdout test.

## Follow-up on the one survivor: "quiet week, buy NO" (2026-11-09, probes `btideasdrill_quiet_no`, `btcheckquiet`)

Split by month on whole events, the screen's version looked steady (ahead in 7 of 9 months, both halves). But the
screen buys at three fixed moments (exactly 1, 2 and 3 days before the end) and averages them. A real bot would buy
the **first** hour the rule fits. Replayed that way (`btcheck.quiet_bets`, hourly from 3 days to 1 day out, 1 hour
late, +2c + fee, one bet per event, whole events, markets ending before 2026-11-10):

| Cost | Events | Per $100 | 90% band | 1st half / 2nd half |
|---|---|---|---|---|
| +2c | 215 | +$0.32 | -$7.53 to +$8.16 | +$7.04 / -$6.54 |
| +5c | 215 | -$3.96 | -$11.47 to +$3.55 | +$2.53 / -$10.58 |

So the profit came from the exact moment of buying (mostly 2 days out, 50-55c), not from a rule a bot can follow.
**Verdict: dropped, no paper track.** The machine's filter passed something that shows up only at one timing. Next
version of the screen should test each idea the way a bot would enter it (first qualifying hour), not at fixed
snapshots.
