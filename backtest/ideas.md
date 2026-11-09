# Idea machine: hundreds of edge ideas, screened hard

Generated 2026-11-09T20:44:07Z by `ideas.py` (probe `btideas`). Paper only. 118,707 finished markets that ended before 2026-11-10 (the holdout is never read; weather left out, see volbias), 40,238 price snapshots, 29 features (3 of them placebo coin flips). Halves split at 2026-07-12.

How to read: each idea buys one side 1 hour after a snapshot at the history price + 2c + fee and holds to the end. 'vs twins' = how much better than all other bets at the same price and time before the end (so a plain long-shot effect can't pass). Money per $100 staked, events weighted equally.

- Ideas made: 30,632 (feature value x side x price band x time before end)
- With enough events to judge (30+ in a half): 7,185 in half A, 7,575 in half B
- Through discovery (beat twins by 2 standard errors): 122 picked on A, 174 picked on B
- Confirm bar on the other half: 90% after correcting for that many ideas, AND making money at +2c in both halves

**Survivors: 0 real ideas, 0 placebos.** Placebos are 4,477 of the 30,632 ideas, so pure luck would let through about 0.0 real-looking ideas (placebo survivors scaled up). No placebo passed, so the filter is strict enough.

Every number below includes one made-up total loss per idea (so a short lucky run can't pass).

## Survivors

| Idea | Why it might work | Events A / B | Bets | vs twins A / B | +2c A / B | +5c (all) | Passed | Note |
|---|---|---|---|---|---|---|---|---|
| none | | | | | | | | |

## Near misses (beat their twins in both halves, but not by enough)

| Idea | Why it might work | Events A / B | Bets | vs twins A / B | +2c A / B | +5c (all) | Passed | Note |
|---|---|---|---|---|---|---|---|---|
| topic other & planned length = 3-14 days | buy first answer (Yes) at 2-10c | 1-3 days before the end | short-lived markets get less attention per question | 102 / 84 | 637 | +$115.94 / +$124.50 | +$81.85 / +$109.63 | +$36.12 |  |  |
| topic crypto price & below its high = at its high | buy second answer (No) at 25-50c | 1-3 days before the end | people anchor to the best price they saw (disposition effect) | 99 / 157 | 297 | +$25.81 / +$21.12 | +$18.23 / +$15.29 | +$8.26 |  |  |
| topic elections & share of life gone = middle | buy first answer (Yes) at 10-25c | 7-14 days before the end | people forget a deadline is getting close (time decay is underpriced) | 42 / 64 | 160 | +$65.44 / +$86.21 | +$53.69 / +$84.82 | +$47.59 |  |  |
| since listing = flat | buy first answer (Yes) at 10-25c | 7-14 days before the end | the opening price sticks longer than it should (anchoring) | 186 / 202 | 643 | +$35.03 / +$31.31 | +$28.70 / +$27.34 | +$8.86 |  |  |
| topic crypto price & below its high = at its high | buy second answer (No) at 10-25c | 1-3 days before the end | people anchor to the best price they saw (disposition effect) | 95 / 112 | 242 | +$47.18 / +$40.95 | +$35.03 / +$18.67 | +$8.18 |  |  |
| topic other & market age = 3-14 days | buy first answer (Yes) at 2-10c | 1-3 days before the end | new listings are priced by few people and anchored to the opening price | 108 / 84 | 547 | +$119.20 / +$98.49 | +$84.84 / +$83.22 | +$28.48 |  |  |
| words: threshold = yes | buy second answer (No) at 25-50c | 30 days before the end | thresholds ('above', 'at least', '+') are hard to judge, people guess the round number | 42 / 33 | 104 | +$50.83 / +$38.12 | +$45.30 / +$41.36 | +$32.98 |  |  |
| topic crypto price & move last 24h = rise 3-10c | buy second answer (No) at 25-50c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 63 / 72 | 149 | +$33.50 / +$26.86 | +$25.87 / +$16.53 | +$12.39 |  |  |
| move last 24h = drop 3-10c | buy first answer (Yes) at 10-25c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 365 / 331 | 865 | +$20.73 / +$23.75 | +$11.98 / +$20.83 | -$1.06 |  | panic fade family (already live) |
| market age = 3-14 days | buy first answer (Yes) at 2-10c | 7-14 days before the end | new listings are priced by few people and anchored to the opening price | 173 / 172 | 872 | +$36.77 / +$45.86 | -$1.56 / +$10.98 | -$26.25 |  |  |
| markets in event = single | buy first answer (Yes) at 25-50c | 1-3 days before the end | big multi-choice events spread attention thin over the outsiders | 189 / 148 | 545 | +$15.76 / +$19.54 | +$2.51 / +$14.22 | -$0.14 |  |  |
| question length = medium | buy first answer (Yes) at 10-25c | 7-14 days before the end | long, complicated questions put people off, so they stay mispriced | 410 / 454 | 1720 | +$16.62 / +$17.24 | +$10.06 / +$14.02 | -$4.17 |  |  |
| topic crypto price & move last 24h = rise 10c+ | buy second answer (No) at 10-25c | 1-3 days before the end | people overreact to fresh news (or underreact and it keeps going) | 104 / 107 | 235 | +$36.73 / +$37.54 | +$27.67 / +$17.31 | +$5.30 |  |  |
| move last 7 days = drop 5-15c | buy second answer (No) at 25-50c | 1-3 days before the end | slow drift keeps going (underreaction) or snaps back (overreaction) | 51 / 62 | 158 | +$30.01 / +$28.39 | +$23.54 / +$20.56 | +$13.05 |  |  |
| rank in event = 6th or lower | buy second answer (No) at 50-75c | 1-3 days before the end | people overpay for the second favorite and ignore the field | 131 / 97 | 484 | +$13.64 / +$11.29 | +$17.47 / +$6.21 | +$7.79 |  |  |
| PLACEBO coin 1 = group D | buy first answer (Yes) at 25-50c | 1-3 days before the end | none: random groups, should never pass | 250 / 220 | 1087 | +$11.44 / +$14.64 | -$1.16 / +$10.03 | -$3.61 |  |  |
| swing size last 7 days = 10-25c | buy first answer (Yes) at 2-10c | 1-3 days before the end | after a wild week the price is noisier than it should be | 646 / 493 | 2233 | +$18.74 / +$29.41 | -$17.62 / +$11.24 | -$33.42 |  |  |
| round price = on a 5c mark | buy second answer (No) at 75-90c | 7-14 days before the end | people like round prices, so they cluster on them | 51 / 39 | 92 | +$8.81 / +$9.40 | +$4.12 / +$5.02 | +$1.01 |  |  |
| words: deadline = yes | buy first answer (Yes) at 25-50c | 1-3 days before the end | 'by <date>' questions: nothing ever happens, YES drifts down slower than it should | 96 / 88 | 397 | +$35.92 / +$22.43 | +$23.05 / +$21.97 | +$13.06 |  |  |
| topic other & PLACEBO coin 3 = group A | buy first answer (Yes) at 50-75c | 7-14 days before the end | none: random groups, should never pass | 44 / 30 | 114 | +$17.18 / +$18.28 | +$11.58 / +$12.70 | +$7.11 |  |  |
| topic other & rank in event = 3rd-5th | buy first answer (Yes) at 2-10c | 30 days before the end | people overpay for the second favorite and ignore the field | 87 / 62 | 230 | +$68.00 / +$74.53 | +$43.46 / +$41.98 | +$2.49 |  |  |
| topic other & share of life gone = middle | buy first answer (Yes) at 2-10c | 1-3 days before the end | people forget a deadline is getting close (time decay is underpriced) | 76 / 56 | 348 | +$82.79 / +$88.62 | +$44.01 / +$72.51 | +$8.97 |  |  |
| market age = 3-14 days | buy second answer (No) at 10-25c | 30 days before the end | new listings are priced by few people and anchored to the opening price | 42 / 32 | 90 | +$54.29 / +$91.59 | +$70.33 / +$87.58 | +$52.76 |  |  |
| topic elections & repeating daily series = one-off | buy first answer (Yes) at 10-25c | 7-14 days before the end | the same question every day: people price today like yesterday | 91 / 185 | 466 | +$33.13 / +$24.11 | +$25.54 / +$21.48 | +$5.34 |  |  |
| topic other & PLACEBO coin 3 = group C | buy first answer (Yes) at 50-75c | 1-3 days before the end | none: random groups, should never pass | 49 / 40 | 153 | +$15.07 / +$14.52 | +$6.96 / +$10.19 | +$3.78 |  |  |

Best placebo in this list scores 1.6 standard errors in its weaker half: anything near or below that is noise.

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


## Data flaw found on the first run (volbias, probe `btideasvolbias`)

The first run (with weather) had one survivor: "buy YES at 25-50c, 1-3 days before the end, on questions with
most/highest/first". The sample questions were mostly weather buckets ("highest temperature in Tokyo..."). Drilling
in (probe `btideasdrill_wx_all`): buying YES on EVERY weather bucket under 50c made +$71 per $100, which is impossible
if prices were fair and complete. Reason: the cache only keeps markets whose **final** volume passed $20k, and the
bucket that wins draws trading late, so losing buckets are missing from our data.

Check: one day before the end, add up the YES prices of the choices we have in each event. With no bias, the number
that win should match. Weather choices win 1.3-1.5 times as often as their prices say; most other topics are close
to 1.0 ("other" with 5+ choices 1.16 is the next worst).

| topic | choices we have per event | events | YES prices added up (expected wins) | real wins | wins / expected |
|---|---|---|---|---|---|
| weather | 1 | 1491 | 368 | 546 | 1.48 |
| weather | 2-4 | 1204 | 701 | 939 | 1.34 |
| weather | 5+ | 436 | 411 | 428 | 1.04 |
| crypto price | 1 | 7184 | 3534 | 3545 | 1.00 |
| crypto price | 5+ | 547 | 1933 | 1942 | 1.00 |
| elections | 2-4 | 493 | 472 | 477 | 1.01 |
| other | 1 | 963 | 318 | 347 | 1.09 |
| other | 5+ | 92 | 133 | 154 | 1.16 |

Consequences: weather is left out of the screen (above). Earlier weather backtests that used this cache
(`backtest/fade.md` cheap-side weather +$121 per $100, calib.md weather long shots) are too rosy for the same
reason. Cheap-YES near misses in "other" may carry a smaller dose of the same bias. Fix: refetch whole events (every
choice, whatever its volume) before trusting any multi-choice result.
