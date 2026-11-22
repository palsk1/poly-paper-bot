# Tennis in play: do prices overreact after a lost set or a break? (22 Nov 2026)

Tool: `tennis.py`. Data: `ten_cache/` in its own release `tennis-store`. Jan's ask (22 Nov): three autonomous
digs in wildly different areas; this one is live tennis. Rule from the same day: an idea must work on a pot of
at most $300, and gets a paper test before any real money.

## Short answer

1. **You can't react to the score.** By the time a free score feed shows a game is over, about three quarters of
   the price move is already done, on both sites. Same story as the esports test.
2. **Prices do not overreact. If anything they react too little.** Buying the player who just lost a set loses
   $17.16 per $100. Buying either player 2 minutes after a sudden move loses $4.62 to $8.77 per $100.
3. **A point-by-point win model adds almost nothing** over Kalshi's price (+$0.83 per $100, luck).
4. **One lead:** on Kalshi, the player who just won set 1 is a little too cheap for the next 10 to 15 minutes,
   when their price is 50c to 80c. After fees: +$2.45 per $100 on 6,469 bets in all four tours. Almost all of it
   is women's main tour (WTA): +$6.96 per $100 on 1,402 bets. Men's main tour: about $0.
   A second, stricter clock keeps the women's lead (+$5.46 per $100 on 720 bets) and kills the men's (-$0.94).
   Exam verdict: **Promising, needs more bets**. Found by looking, so it needs a live paper test.

**23 Nov: Jan said "yes build a paper track".** Two paper tracks run it live on Kalshi since then: `tennis_set_w` (women's main tour) and `tennis_set` (all four tours), $300 each, $25 a bet. They read Kalshi's own live score and look once per match, right after set 1. Proposed pass rule: PROTOCOL 5i (not locked).

## What exists (both sites)

- **Kalshi** lists every professional singles match: ATP, WTA, both challenger tours, ITF men and women
  (series `KXATPMATCH`, `KXWTAMATCH`, `KXATPCHALLENGERMATCH`, `KXWTACHALLENGERMATCH`, `KXITFMATCH`,
  `KXITFWMATCH`). A main-tour match trades around a million contracts, and the gap between buy and sell
  price is usually 1c. Taker fee: about 1.5c a share at 68c. Waiting orders pay no fee.
  It also has set-winner markets on the main tours (`KXATPSETWINNER`, `KXWTASETWINNER`).
- **Polymarket** lists the same matches (tag `tennis`, id 864), challengers included ($150,000 to $450,000 a
  match). Taker fee 0.05 x shares x p x (1-p): about 1.1c a share at 68c. Smallest order 5 shares.
- Kalshi keeps 1-minute prices with the real bid and ask for every finished match back to June 2025
  (29,076 matches used here). Polymarket's history has trades only, no asks.

## 1. The score feeds are late

Recording of 22 Nov, 4.5 hours, 34 Kalshi matches and 5 Polymarket matches (incl. the ATP Finals final):

| Feed | Price move already done when the feed shows the game |
|---|---|
| Polymarket's own sports feed (one update a game) | half done 30 s before, 3/4 done at the update |
| Kalshi's own live score (`/live_data`, read every ~10 s) | half done 30 s before, 3/4 done at the update |
| 365scores (free site) | no point by point, a few seconds behind Kalshi's |

So a bot that waits for a free score always buys after the move. Jeff Sackmann's point-by-point files, the
ATP site, Sofascore and tennis-data all refuse or are gone (404 / 403 from Actions).

Breaks of serve in the recording (152): the price moved 7c toward the breaker, then drifted 1.25c further in
the next 10 minutes (give or take 2c). No snap-back.

## 2. After a set: the model against Kalshi's price

22,317 Kalshi matches matched to 365scores (which gives the minutes each set took), 25,794 finished sets with
a two-sided quote 3 minutes after the set. "Model" = points, games, sets as a chain, tuned to the pre-match price.

| What just happened | Sets | Model | Kalshi | Really won |
|---|---|---|---|---|
| Favourite (60c+) lost set 1 | 2,026 | 41.9c | 40.1c | 37.9 in 100 |
| Favourite won set 1 | 4,623 | 88.8c | 88.3c | 90.2 in 100 |
| Even match, lost set 1 | 2,760 | 24.7c | 24.1c | 21.4 in 100 |
| Even match, won set 1 | 2,656 | 75.0c | 75.7c | 79.3 in 100 |
| Underdog lost set 1 | 4,397 | 11.0c | 11.3c | 9.0 in 100 |
| Underdog won set 1 | 2,009 | 57.5c | 59.6c | 61.4 in 100 |
| One set all, just won set 2 | 2,880 | 50.4c | 53.0c | 52.5 in 100 |

Read it like this: the set loser wins less often than both the model and Kalshi say. Nobody overreacts.
When the model and Kalshi disagree, Kalshi is right four times out of five.

Before the match Kalshi's prices are fair (within about 1c in every band). After set 1 the side priced 50-80c
wins 3 to 4 in 100 more often than its price for the first minutes, 2 more after 10 to 20 minutes.

Bets at Kalshi's real ask + fee, $25 each, held to the end:

| Rule | Bets | Per $100 | Exam verdict |
|---|---|---|---|
| Always the player who just lost the set | 26,113 | -$17.16 | Losing |
| Always the player who just won the set | 25,794 | -$0.10 | about even |
| Model says 5c+ cheap | 9,282 | +$0.83 (first half +$4.84, second -$3.21) | Ahead, but could be luck |
| Player who just fell 8c+ in 2 minutes | 89,427 | -$8.77 | Losing |
| Player who just rose 8c+ in 2 minutes | 89,427 | -$4.62 | Losing |

## 3. The lead: winner of set 1 at 50-80c

Rule: when set 1 is over, buy the player who won it on Kalshi if the ask is 50c to under 80c. Hold to the end.
Example: cost $25.21 for 39 shares at 63c plus fee, pays $39.00 if they win the match, $0 if not. About 7 in 10 win.

The first version timed the bet from the price jump and showed +$4.90 per $100. That was partly cheating: in
3 of 10 sets the jump it picked came before the set was really over. So two honest clocks:

**Clock A: 365scores' set end + 7 minutes** (all four tours, June 2025 to Nov 2026)

| Group | Bets | Per $100 | First / second half |
|---|---|---|---|
| All four tours | 6,469 | +$2.45 | +$1.92 / +$2.98 |
| Women's main tour (WTA) | 1,402 | +$6.96 | +$8.44 / +$5.47 |
| Men's main tour (ATP) | 1,455 | +$1.09 | +$0.02 / +$2.15 |
| Men's challengers | 3,006 | +$1.55 | +$0.19 / +$2.91 |
| Women's challengers | 606 | -$0.27 | +$2.97 / -$3.51 |
| Winner was not the pre-match underdog | 3,489 | +$5.67 | +$5.80 / +$5.53 |
| Winner was the pre-match underdog | 2,980 | -$1.30 | -$1.87 / -$0.73 |

Waiting 4 / 10 / 15 / 20 minutes instead of 7: +$3.43 / +$2.28 / +$1.08 / +$0.59. Paying 1c more a share:
+$0.98. Paying 2c more: -$0.45. So it is thin: it lives on a 1c gap.

**Clock B: Kalshi's own set-1 market has closed** (main tours only; it closes about 9 minutes after the set
ends, so this bet can't know anything early)

| Minutes after it closes | Women (WTA) | Men (ATP) |
|---|---|---|
| 1 | +$2.33 (727 bets) | -$0.96 (1,082) |
| 3 | +$5.46 (720) | -$0.94 (1,075) |
| 5 | +$5.55 (700) | +$0.21 (1,043) |
| 10 | +$4.10 (647) | +$0.47 (982) |

Exam (`exam.score`, bar raised for 130 cuts in this dig and every idea in the ledger):

- All four tours, clock A: **Promising, needs more bets**. Luck range +$1.08 to +$3.81. Worst case -$0.37.
- WTA only, clock A: "Looks real" on paper (worst case +$0.98), but WTA was picked from four tours after looking.
- WTA only, clock B: **Promising, needs more bets**. Luck range +$1.38 to +$9.55. Worst case -$3.23.
- ATP only, clock B: Behind, but could be bad luck.

Honest reading: men's tennis, nothing. Women's main tour, something that survived two clocks and both halves,
worth about $2 to $6 per $100 if real. It was found by looking, with no untouched test set (365scores does not
list ITF matches, so those 40,000 Kalshi matches can't be timed).

### Backward look (start from the upsets)

Who came back after losing set 1? Nothing you could have bought: comebacks happen less often than the price
says in every group (favourites 37.9 vs 40.1c, even 21.4 vs 24.1c, underdogs 9.0 vs 11.3c), after narrow sets
(24.1 vs 27.5c) and after bad ones (14.6 vs 15.3c). The only thing the winners of the lead share: the set
winner was not the pre-match underdog. An underdog who steals set 1 is priced right.

### Fit for a $300 pot

About 12 bets a day over the whole time, 17 a day in the last 60 days (WTA alone: about 4 a day in season).
A match ends about 69 minutes after the bet, 9 in 10 within 2 hours. With $25 bets the most money out at once
in the last 60 days was $177, the worst dip $236. With $10 bets: $71 out at once, worst dip $94. Smallest
possible bet: one share, about 68c. So it fits $300, and it fits $100 with $10 bets.

## 4. Polymarket

Polymarket keeps no ask history, so the test re-buys the same set-1 moments at the worst price anyone paid in the next 3 minutes + 1c + fee (`tennis.py pmreport`).

First check, 7 days of matches (Polymarket's list stops handing out older ones in one go): 76 bets, -$12.25 per $100. The same matches on Kalshi: -$6.07 on 67 bets. A bad week on both sites, and far too few bets to say anything. A wider download (`ten_pm_150`, in 4-day pieces) was still running when the tracks were built; the paper tracks are Kalshi only.

What is known: same matches, a slightly lower fee (about 1.1c a share at 68c against 1.5c on Kalshi), and its own score feed is just as late.

## Traps found

- **A release holds at most 1,000 files.** This dig's first download filled `price-store` (other threads'
  uploads failed for a few hours). Tennis now has its own release `tennis-store` (`STORE_TAG`), and the store
  itself was changed on main to spread over several releases.
- Kalshi's live candle endpoint answers 404 for matches older than about two months. The `/historical`
  endpoint has them, with fields named `close` / `low` / `high` (no `_dollars`).
- Timing a set end from the price jump peeks ahead (the jump is often a break late in the set). Use a clock
  that is known to be late.
- Kalshi's set-winner markets close about 9 minutes after the set ends, not at once.
- Polymarket's set-winner markets close about 30 minutes late: useless as a clock.
- 365scores has no ITF matches and no doubles prices. Its day list gives the minutes of each set.
- A cancelled Actions run gets 5 minutes for its save steps, then is killed.

## How to run it again

    probe ten_fetch_520_KXATPMATCH_KXWTAMATCH     # 365scores set times + Kalshi minute prices (resumable)
    probe ten_setclock                            # Kalshi set-winner markets (the second clock)
    probe ten_live_275                            # live recording + feed-delay report
    probe ten_pm_120                              # Polymarket match-winner trades, 120 days
    STORE_TAG=tennis-store python3 store.py pull ten_cache    # in Actions; from the workspace download the release files
    python3 tennis.py sets | jumps | lead | pmreport
