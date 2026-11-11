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
- **Upsets have no common thread the price misses.** Roster changes, slumps, winning streaks, tiredness, rust,
  best-of-1: the price already accounts for each. The five best-looking patterns all fail at real prices (section 5).
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

## 5. What do the upsets have in common? (Jan: "4,533 matches and you can't find a red thread?")

Jan asked what the losing favorites share: upsets, roster changes, in-fighting, the start of a losing streak. We built
each team's form from bo3.gg results that ended before the match (last 5 results, rest, new team, best-of-1/3) and
roster changes from Valve's monthly player lists (a player in this month's list who wasn't in last month's).
In-fighting isn't in any data we can reach, so it isn't tested. 4,364 matches with both teams' form, 1,513 upsets.

The test for each pattern: does the price already expect it? "Price said" is how many upsets the prices implied,
"really" is how many happened. Chart prices 1h before +1c, no fee (`python3 cs2.py upsets`).

| Pattern | Matches | Upsets per 100: price said / really | Back underdog per $100 | Back favorite per $100 |
|---|---|---|---|---|
| All matches | 4,364 | 34.5 / 34.7 | -$5.70 | -$2.40 |
| Favorite won its last 5 | 234 | 30.6 / 34.6 | +$8.23 (±18) | -$7.49 |
| Favorite lost its last 2 (start of a slump) | 841 | 34.8 / 34.0 | -$10.09 | -$1.09 |
| Underdog lost its last 3 | 524 | 32.3 / 29.2 | -$17.35 | +$2.79 |
| Favorite changed a player this month | 1,229 | 34.5 / 33.8 | -$6.99 | -$0.68 |
| Underdog changed a player this month | 1,198 | 35.1 / 34.6 | -$10.13 | -$1.92 |
| Favorite is a new team (under 15 matches) | 244 | 37.9 / 41.0 | +$4.30 (±14) | -$6.81 |
| Favorite played in the last 12h (tired) | 582 | 35.2 / 34.0 | -$8.07 | -$0.04 |
| Favorite rested 14+ days (rusty) | 270 | 32.1 / 35.6 | +$3.93 (±16) | -$7.73 |
| Best-of-1 | 372 | 35.0 / 30.9 | -$17.53 | +$4.37 |
| Favorite's price fell 5c+ since a day before | 117 | 38.7 / 28.2 | -$33.08 | +$15.09 (±11) |
| Close match (favorite 50-60c) | 1,586 | 45.2 / 48.1 | +$4.20 (±4.5) | -$6.97 |
| Big favorite (75c+) | 900 | 17.5 / 14.6 | -$24.53 | +$2.36 |

(Full 20-pattern table with first/second halves: `python3 cs2.py upsets`.)

**The red thread is that there isn't one the price misses.** Roster changes, a slump, being tired or rusty: the price
already moves for all of them, and "price said" and "really" land within 1-3 upsets per 100 of each other. Looking
inside price bands made it worse: patterns flip sign from one band to the next (e.g. "favorite changed a player"
is -$17 at 60-70c and +$3 at 50-60c), which is what noise looks like.

The five best-looking patterns at prices people really paid ($25 bets, first real buy within 3h, +1c + fee):

| Rule | Chart | Real price: bets | Per $100 | Luck range | Verdict |
|---|---|---|---|---|---|
| Back the underdog in a close match (favorite 50-60c) | +$3.70 (1,914) | 1,735 | -$0.40 | -$4.61 to +$3.82 | Losing |
| Back the underdog when the favorite won its last 5 | +$7.85 (233) | 201 | +$5.17 | -$15.62 to +$25.97 | Ahead, but could be luck |
| Back the favorite after its price fell 5c+ since a day before | +$8.65 (168) | 159 | +$4.11 | -$5.44 to +$13.66 | Ahead, but could be luck |
| Favorite at 60-97c in a best-of-1 | +$3.73 (308) | 288 | +$1.29 | -$4.37 to +$6.95 | Ahead, but could be luck |
| Back the favorite when the underdog lost its last 3 | +$2.56 (529) | 489 | -$0.68 | -$5.73 to +$4.36 | Losing |

None survives. The "won 5 in a row" and "price fell" rules flip between halves (+$13 then -$3; -$5 then +$13), and
the price-fell rule loses when measured from 6h instead of 24h before (-$4). Best-of-1 is ahead in both halves but by
$1, gone at +1c worse prices. Ledger tries are now 155 for CS2 alone (34 patterns x 2 sides plus nearby versions).

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
`cs2_exam_<ids>` with rule ids like `ai1,aisweep` (no underscores). `python3 cs2.py upsets` (offline, section 5). `cs2_sources`, `cs2_peek_<team>`, `cs2_jsapi`
were the source hunt.
