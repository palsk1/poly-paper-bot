# CS2 match bets vs team rankings and bo3.gg's AI (cs2.py)

Research only, no track. 11 Nov 2026. Jan: "can we find something between cs2 and hltv? People are dumb, would be
nice to just go against gamblers, not the elite quants." Then: "check bo3.gg's prediction bot: if we just used it,
would we have made money? Maybe with different bet sizes too."

## The short version

- **Rankings don't beat the price.** Betting on the team a ranking likes, when the Polymarket price disagrees by 10c+,
  lost **$12.84 per $100** (our own rating) and **$17.47 per $100** (Valve's official ranking) at prices people really
  paid, on about 1,400-1,600 matches each. The price already knows the rankings, and then some.
- **bo3.gg's AI picks don't beat the price either.** It picks the winner 61 times in 100. The plain Polymarket favorite
  is right 66 times in 100. Backing every AI pick an hour before the match lost **$4.18 per $100** on 4,533 matches at real prices. Betting more when it is "surer"
  (it predicts 2-0) or sizing by price doesn't fix it (table 3).
- **bo3.gg's bookmaker odds can't be used.** They are the last odds seen, often from during or after the match, so
  they "predict" the winner far too well. Any test with them would be cheating.
- **One lean: the favorite a day before.** Buying the team priced 70-97c a day before the match made **+$7.60 per
  $100** on 234 matches at real prices ("Promising, needs more bets"), and **+$15.27 on 91** in smaller leagues
  (bo3.gg tier B, the exam says "Looks real"). But: only 4 in 10 of these could be priced at all, the ones that could
  were the better ones (a hidden tip-off, section 4), and only about **$7 traded near that price in 10 minutes**, so a
  $25 bet fits in 1 of 4. Registered for the 21 Dec fresh-data look (PROTOCOL 5). No track.

Where the data comes from: every finished CS2 match-winner market on Polymarket (sports cache, March to 9 Nov 2026,
6,495 matches, median $30,000 traded), 18,000 finished matches from bo3.gg's public API (results, tournament tier,
AI pick), and Valve's official monthly team standings (GitHub repo `ValveSoftware/counter-strike_regional_standings`).
**HLTV itself blocks robots** (Cloudflare "Just a moment..." page, also from GitHub's servers), so it stands in as
Valve's ranking plus our own rating built from bo3.gg results. Games from 10 Nov on are left out (holdout).

## 1. Who predicts better: the price or the rankings?

"Average surprise" (log loss): lower is better. A coin flip scores 0.693.

| Games | Polymarket price 1h before | Our rating (Elo from bo3.gg results) | Valve's ranking points | Price + a dash of rating |
|---|---|---|---|---|
| 3,717 with our rating | **0.607** | 0.653 | | 0.608 |
| 3,616 with Valve points | **0.608** | | 0.650 | 0.609 |

Both rankings are clearly worse than the price, and adding them to the price makes it slightly worse, not better.
Our rating only counts matches that ended before the game started and teams with 15+ past matches.

## 2. Rules at prices people really paid

Each bet $25, bought at the first real buy of that team within 3 hours after the decision time (and before the
match starts), +1c + fee. "Nobody could buy" = no real buy in that window, left out.

| Rule | Chart price | Real price: bets | Per $100 | Luck range | Verdict |
|---|---|---|---|---|---|
| Back the team **our rating** likes, 10c+ over the price, 1h before | -$7.10 (1,663) | 1,559 | **-$12.84** | -$18.57 to -$7.12 | Losing |
| Back the team **Valve's ranking** likes, 10c+ over the price, 1h before | -$10.48 (1,469) | 1,355 | **-$17.47** | -$23.66 to -$11.28 | Losing |
| Favorite at 70-97c **an hour before** | +$2.30 (1,800) | 1,671 | +$0.96 | -$1.00 to +$2.91 | Ahead, but could be luck |
| Favorite at 70-97c **a day before** | +$7.91 (577) | 234 | **+$7.60** | +$3.10 to +$12.10 | Promising, needs more bets |
| Same, smaller leagues only (bo3.gg tier B) | +$11.90 (229) | 91 | **+$15.27** | +$9.64 to +$20.91 | Looks real (but see section 4) |
| Back **bo3.gg's AI pick**, 1h before | -$0.98 (4,930) | 4,533 | **-$4.18** | -$6.29 to -$2.07 | Losing |
| Back the AI pick only when it predicts a 2-0, 1h before | +$1.76 (2,498) | 2,288 | -$1.29 | -$4.07 to +$1.50 | Losing |
| Back the AI pick a day before | +$3.87 (1,690) | 555 | -$0.04 | -$5.63 to +$5.56 | Losing |

Ledger tries for this dig: 65 versions (rating gaps, price bands, tiers, timing, price drift, months and 14 ways to
bet or size the AI pick), so the exam's luck bar counts them all, plus everything tried before (107 ideas).

## 3. bo3.gg's AI pick, flat and sized (chart prices +1c, no fee)

bo3.gg shows an "AI prediction" on every match: a predicted map score (2-0, 2-1 ...). It gives no chance, so "surer"
can only mean "predicts a sweep". 4,930 Polymarket matches have one. It agrees with the Polymarket favorite 73 times
in 100. We can't see when bo3.gg made each pick; if it was ever updated after the start, this flatters the AI.

| How to bet the AI pick | Bets | Per $100 | Luck range | First half / second half |
|---|---|---|---|---|
| Every pick, same size, 1h before | 4,930 | -$0.98 | -$3.06 to +$1.10 | +$1.01 / -$2.97 |
| Every pick, a day before | 1,524 | +$3.60 | -$0.16 to +$7.36 | +$3.99 / +$3.22 |
| Only when the AI picks the underdog (under 50c) | 1,318 | -$0.92 | -$6.64 to +$4.80 | +$4.40 / -$6.23 |
| Only when the AI picks a big underdog (under 40c) | 598 | -$9.60 | -$19.31 to +$0.11 | -$0.49 / -$18.71 |
| Only when the AI agrees with the favorite | 3,612 | -$1.01 | -$2.94 to +$0.92 | -$0.39 / -$1.62 |
| Only when the AI predicts a 2-0 | 2,498 | +$1.76 | -$0.97 to +$4.49 | +$2.24 / +$1.28 |
| Only when the AI predicts a close one | 2,432 | -$3.80 | -$6.96 to -$0.64 | -$0.48 / -$7.11 |
| Double the bet when it predicts a 2-0 | 4,930 | -$0.06 | -$2.17 to +$2.05 | +$1.60 / -$1.65 |
| Bet more on favorites (size = price / (1 - price)) | 4,930 | +$0.49 | -$0.94 to +$1.92 | +$1.44 / -$0.45 |
| Bet more on underdogs (size = 1 / price) | 4,930 | -$3.04 | -$6.50 to +$0.42 | +$0.41 / -$6.43 |

The "a day before" line is mostly the favorite-a-day-before lean again (the AI mostly picks the favorite). The 2-0
line is the same story: a predicted sweep is usually a big favorite. Nothing here beats just buying the favorite.

## 4. The day-before lean: is "someone else bought too" a tip-off?

The real-price step only prices a bet if somebody really bought that team in the 3 hours after the decision. If those
buyers know something, the priced bets look better than the rule really is. Chart results, split:

| Rule | Priced (someone bought) | Nobody bought |
|---|---|---|
| Favorite a day before | +$10.19 per $100 (234) | +$6.36 (343) |
| Same, smaller leagues | +$17.79 (91) | +$8.02 (138) |
| Favorite an hour before (control) | +$2.27 (1,671) | +$2.60 (129) |

So yes, partly. For the day-before rules the priced ones did clearly better; an hour before there's no difference.
The unpriced ones are still ahead on the chart, but a chart price nobody traded at is not a price you can buy. Honest
guess: the real lean is smaller than the real-price card says, maybe +$5 per $100, and it lives in thin markets
($7 traded near the price in 10 minutes, a $25 bet fits in about 1 of 4). That's why it goes to the 21 Dec look
instead of a track, and why it couldn't take real money at any size even if it passes.

## Sanity checks

- Result check: bo3.gg's winner matches Polymarket's result in 5,886 of 5,902 matched games (16 left out).
- Rating check: our rating and Valve's points both beat a coin flip (0.65 vs 0.69), so they are real ratings; they
  are just worse than the price.
- Look-ahead: our rating only uses matches that ended before the start; Valve's list is the last one published before
  the match; the tier is bo3.gg's tournament tier, known in advance. Final traded volume (known only afterwards) is
  NOT used as a filter, though on the chart "low volume favorites" looked great (+$8.80): that would be cheating.
- bo3.gg bookmaker odds: average surprise 0.33 vs the price's 0.60, impossible for pre-match odds. Left out.

## How to rerun

`cs2_fetch` (Valve standings + bo3.gg results into the price store), `cs2_ai` (bo3.gg AI picks + odds),
`python3 cs2.py chart` (offline, tables 1-2 on chart prices), probe `cs2_exam` (all rules at real prices) or
`cs2_exam_<ids>` with rule ids like `ai1,aisweep` (no underscores). `cs2_sources`, `cs2_peek_<team>`, `cs2_jsapi`
were the source hunt.
