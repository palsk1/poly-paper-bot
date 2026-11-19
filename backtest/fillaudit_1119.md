# Are the Kalshi 15-minute paper fills real? (19 Nov 2026)

Jan asked: "Does kc maker actually check if there were sellers at that point? They all seem unreal."

Tool: `kcrypto.py fillaudit [track]` (probe `kc_fillaudit_<track>`). It re-reads Kalshi's real trade list for every
lost bet plus 80 random won bets and walks our paper bid again, separately from the bot's own code.

## What counts as a fill (bot.kmaker_fill)

- Only trades **after** the moment we placed the bid, and **before** the close.
- Only real **sellers** of our side (a trade where someone bought our side is skipped).
- A sale **at** our price only counts after everyone who was already waiting at that price (the queue we saw in the
  book) has been served. People who cancel ahead of us are not credited to us (harsh on us).
- A sale **below** our price counts in full: a seller who sold lower would have hit our higher bid first.
- Fill size is capped at our 10 dollars' worth. No sellers means no bet (the "unfilled" pile).

## What the real tape said

| | kc_maker_safe_usd | kc_maker_safe |
|---|---|---|
| bets re-checked | 80 (all won) | 88 (8 lost + 80 won) |
| re-check gives the same fill | 80 of 80 | 88 of 88 |
| still full if only sales BELOW our price count | 68 of 80 | 82 of 88 |
| still full if twice our size must be sold | 79 of 80 | 87 of 88 |
| filled in the last 10 s / 30 s | 0 / 0 | 0 / 0 |
| typical time the fill came | 2.7 min before the close | 3 min before the close |
| contracts sold to bids after our bid (middle bet) | about 25,000 | about 25,000 |

Lost bets: all 8 were filled in full, early (2.5-5 min before the close), with 25,000 to 1,000,000 contracts dumped
below our price on the way to 0.1c. Unfilled bets: 0 of 537 (both tracks) would have lost. So the paper rule does
not dodge losers: when a coin flips, the bid fills, exactly like a real one would.

## Verdict

The fills are real. There were real sellers, at or below our price, after our bid, in sizes 100+ times ours.

What is still rosy:
1. **Luck, by far the biggest.** A win pays about 6c on a $9.94 bet (kc_maker_safe_usd); one loss costs about $9.94,
   so one loss eats about 170 wins. 0 losses in ~680 happens about 1 time in 8 if the true rate is 1 in 324 (history).
   The $39 profit is about 4 losses away from $0.
2. Real orders take time to reach Kalshi; paper takes the queue we saw at the read. Small at these sizes.
3. A real bot needs Kalshi access from Sweden, which is not checked yet.

No change to any live track or to the locked 1 Dec test.
