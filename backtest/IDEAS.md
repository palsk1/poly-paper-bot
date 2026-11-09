# The idea machine: how we make new edge ideas, and how we kill them

Written 2026-11-09 (Jan: "can you create a system where you come up with a novel idea that might be hiding from
us?"). Code: `ideas.py`. Results: `backtest/ideas.md`. Rules it obeys: `backtest/PROTOCOL.md`.

## 1. Where ideas come from

An edge needs a reason why other traders get the price wrong. So every idea starts from a **bias** (a known way
people get things wrong) and a **feature** (something about a market you can see at the time). The machine crosses
them with which side we buy, the price band and how long before the end:

    idea = feature value  x  side (first answer / second answer)  x  price band (2-10c ... 90-98c)  x  time before end (1-3 / 7-14 / 30 days)

and every feature again inside each topic ("long questions about elections", "markets added late to a crypto event").
That makes tens of thousands of ideas from about 30 features. Nobody would write those by hand, which is the point:
the boring combinations are the ones nobody else checks.

Biases in the catalog and the features that test them:

| Bias | Features |
|---|---|
| Anchoring (first price sticks) | market age, opening price, change since listing, round price |
| Attention is thin | events with many markets, rank in event, planned length, repeating daily series |
| Hype after news | added late to event, move in the last 24h / 7 days, swing size |
| Disposition (people anchor to the best/worst price they saw) | below its high, above its low |
| Nothing ever happens / time decay is underpriced | share of life gone, "by <date>" wording |
| Confusing wording | negative questions, thresholds, range buckets, exact numbers, long questions, "announce/confirm" |
| Fans and haters | famous names, "most/first/highest" races |
| Position bias (first answer gets bought) | answer names (Yes/No vs Up/Down vs names) |
| Fast traders stay away | fee markets |
| **Placebo** (no bias at all) | three random coin-flip groupings per event |

To add a bias, add a feature (a few lines with `@ideas.feature(name, story)`) and rerun. Other threads (source timing,
rule wording, contradicting markets) can screen their own ideas the same way; see the top of `ideas.py`.

## 2. How ideas die

Most ideas are noise, and with this many some will look great by pure luck. So:

1. **Holdout is never read.** Only markets that ended before 2026-11-10.
2. **No peeking.** Features use prices up to the snapshot. We buy 1 hour later at the history price **+2c plus the
   fee** (the pessimistic number from PROTOCOL.md) and hold to the end. A +5c column is shown for thin markets.
3. **Beat the twins.** Each bet is compared with all other bets on the same side, same 2c price bucket, same days
   before the end. "Long shots lose" can't pass on its own; only the feature's extra effect counts.
4. **Events count once.** 20 markets about one speech are one bet.
5. **Pick on one half, prove on the other**, both ways round (halves split by end date). On the first half an idea must
   beat its twins by 2 standard errors with 30+ events. On the other half it must pass at 90% *after* dividing by the
   number of ideas that got through the first half (Bonferroni), and it must make money on its own at +2c in both halves.
6. **Placebos run through the same filter.** If coin-flip groups survive, the filter is too loose and the survivors
   are suspect.

A survivor is a lead, not proof. Next step for a survivor: a paper track (or a Claude-track tweak), judged live,
and a pre-registered line in PROTOCOL.md's holdout table if it's worth it.

## 3. First run (2026-11-09)

30,632 ideas without weather (32,498 with): **no survivor, no placebo survivor.** The only survivor with weather in
it was a data flaw: our cache drops weather buckets that lost (details and the check in `ideas.md`). Best honest near
misses, worth re-screening once the cache holds whole events: crypto price markets at their highest price so far ->
NO at 25-50c, 1-3 days out (beat its twins by about $21-26 per $100 in both halves, ~250 events); threshold questions
("above", "at least") -> NO at 25-50c, 30 days out (small, 75 events).

## 4. Ideas I'd like to add when data allows

Not testable on today's cache (it has no rule text, holder lists or order books):
- **Holder concentration**: markets where one wallet holds most of one side (a whale propping a price).
- **Creator/template effects**: markets written from the same template by the same creator, e.g. daily series.
- **Book shape**: thin asks vs thick bids before a move (needs `recorder.py` data, a few weeks more).
- **Sibling sum drift**: in multi-choice events, the side whose total drifts away from $1 (left to the
  contradicting-markets thread).
