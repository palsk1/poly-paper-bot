# Weekly "habit" bets: does the record of earlier weeks beat the price? (16 Nov 2026)

Tool: `habits.py`. Short answer: **no, not across the board. Two small leans, both "could be luck". Dropped, no track.**

## Why this dig

Public counts are priced (Spotify, Netflix, post counts). The one lead that held up was a habit record: Trump's words of the last 8 weeks against the weekly word bets. So: do other weekly bets about what a person or office usually does have the same gap?

## What is out there

- **Kalshi** has a whole shelf of them (137 Politics series listed, 4,220 settled markets). The busy ones: executive orders this week (KXEOWEEK, 55 weeks, the biggest), "at least N presidential actions this week" (KXTRUMPACT, 39 weeks), Truth Social posts per week and per day, Trump endorsements per week, nominations sent to the Senate, Trump photos, Mamdani's executive orders, top ActBlue fundraiser, plus ship traffic through Hormuz / Suez / Panama.
- **Polymarket** ran daily and weekly "will Trump sign an executive order" bets from January to July 2025 and then stopped. Today it has nothing of this kind that repeats weekly (checked the tags executive-orders, trump-presidency, white-house, truth-social: 1,039 finished events, the weekly families all end in 2025). So this dig is Kalshi only, because that is where the bets are.

## The test

Same rule as the Trump words: for each answer ("at least 5 actions", "more than 1 order"), in how many of the last 8 finished rounds of the same bet did it come true. Buy Yes where that record is 15c+ above the real asking price, No where it is 15c+ below the real bid. Looks at 2, 12, 24, 48 and 72 hours after the bet opens, first fit only, Kalshi's fee included. 16 series with prices, 1,761 markets with a record.

| | bets | per $100 | verdict |
|---|---|---|---|
| All 16 series together | 656 in 256 rounds | -$0.31 (first half +$11, second half -$17) | Behind, but could be bad luck |
| Only "presidential actions this week" | 108 in 30 weeks | +$26.68 | Ahead, but could be luck |
| Only "executive orders this week" | 45 in 25 weeks | +$24.65 (+$16 at 2c worse, +$6 at 5c worse) | Ahead, but could be luck |

The price forecasts better than the record (miss score 0.123 against 0.152). Series by series it is a coin toss: 8 ahead, 8 behind. The two that are ahead were picked after looking at 16, and the "presidential actions" one flips to a loss when the record uses 4 weeks instead of 8. That is what luck looks like.

## Prices alone, and the backward look

- Buying Yes loses in every price band (-$6 to -$23 per $100).
- Backward look, starting from the upsets: the big surprises are weeks where "at least 2 / 3 / 4 actions" sat at 85-90c on Monday and then nothing got signed. Buying No at 3-20c on everything: +$11.64 per $100 on 252 bets, first half +$17, second half +$5, "Ahead, but could be luck" (range -$21 to +$44). Small bets: these markets trade a few hundred dollars at those prices.

## Why the Trump words lead is different

There the record comes from outside (his real speeches) and the bets are many separate words. Here the record is just the bet's own past results, which every trader sees on the same screen.

## Traps

- Kalshi's order bets stay open 2-3 weeks after the week ends (the Federal Register is slow), so "the last 8 rounds" must only count rounds already closed when the new one opens.
- A market's own close time leaks the result, so looks are counted from the open.
- The answers inside one week ("at least 3", "at least 4", ...) win and lose together: count weeks, not bets.
