# Kalshi vs Polymarket on the same question: follow the leader? (27 Nov 2026)

Question (Jan: "go crazy"; coordinator: follow the leader, not arbitrage): when the same non-sports question is
listed on both sites and the prices differ, does one site know the winner better? And when one site moves first,
does the other follow late enough for a slow bot to buy? **Answer: no. Dropped, no track.**

## What was tested
- Every settled non-sports Kalshi market that closed 1 Mar-9 Nov 2026 (649k, listed series by series; combos,
  crypto prices and mentions left out) against every finished Polymarket market in bt_cache (126k, $20k+ traded).
- Text match + same date + same numbers + same direction gave 1,217 candidate twins. Four reviewers then read every
  pair by hand: **911 true twins** (elections 522, entertainment 149, weather 133, tech 59, politics 25, economy and
  money 23). 852 of the 911 ended the same way on both sites (weather is the odd one: the two sites read different
  weather stations).
- Prices: Kalshi's real hourly bid/ask, Polymarket's real trades. Kalshi buys pay the ask + fee. Polymarket buys
  pay the worst trade of the next hour (never less than the signal price) + 1c + fee. $10 a bet, one bet per pair,
  held to the end. The holdout (markets ending 10 Nov or later) stays out.

## Which site knows better? A tie.
Brier score = how far the price was from the result (lower is better).

| Hours before close | Pairs | Kalshi | Polymarket | 5c+ apart: Kalshi closer / Polymarket closer |
|---|---|---|---|---|
| 72 | 607 | 0.1035 | 0.1045 | 18 / 16 |
| 24 | 639 | 0.0905 | 0.0906 | 20 / 19 |
| 6 | 732 | 0.0846 | 0.0883 | 53 / 37 |
| 1 | 755 | 0.0734 | 0.0804 | 55 / 50 |

When they disagree by 5c or more, each site is the closer one about half the time.

## The eight rules (all fixed before looking, exam verdicts)
| Rule | Bets | Per $100 | Exam |
|---|---|---|---|
| Buy on Polymarket where Kalshi's price is 5c+ away (follow Kalshi) | 409 | +$5.26 | Ahead, but could be luck |
| Buy on Polymarket where Kalshi's price is 10c+ away (follow Kalshi) | 220 | -$14.82 | Behind, but could be bad luck |
| Buy on Kalshi where Polymarket's price is 5c+ away (follow Polymarket) | 488 | +$2.65 | Ahead, but could be luck |
| Buy on Kalshi where Polymarket's price is 10c+ away (follow Polymarket) | 303 | +$4.65 | Ahead, but could be luck |
| Kalshi moved 5c+ in 1h, Polymarket stood still: buy on Polymarket | 62 | +$3.69 | Ahead, but could be luck |
| Kalshi moved 5c+ in 3h, Polymarket stood still: buy on Polymarket | 66 | -$21.24 | Behind, but could be bad luck |
| Polymarket moved 5c+ in 1h, Kalshi stood still: buy on Kalshi | 179 | -$13.92 | Behind, but could be bad luck |
| Polymarket moved 5c+ in 3h, Kalshi stood still: buy on Kalshi | 177 | -$6.28 | Behind, but could be bad luck |

## Backward look and traps
- The best-looking cut, found by looking: buy on Kalshi where Polymarket is 10c+ away, elections only: +$47.67 per
  $100 on 92 bets, but one 2c long shot (Nebraska Senate) made $489 of the $449 total; without the best 5 bets it is
  -$27 per $100. First half -$30, second +$125. Luck. "Follow Kalshi 5c": the best 5 bets made $660 of $219.
- The 10c+ gaps are mostly weather (the sites settle on different stations, so they are not really the same
  question) and cheap long shots. A big gap is usually a sign the two questions differ, not that one site is asleep.
- Moves: when one site jumped 5c+ in an hour and the other stood still, buying the slow site lost (-$6 to -$21 per
  $100 in three of four versions). The slow site was usually right not to move.
- Traps for the next dig: Kalshi's `/historical/markets` ignores close-time filters (list by series); the
  candidate-name or song is often only in one site's text (a reviewer pass is needed, text scores alone let about a
  quarter of wrong pairs through).

## Ceiling (rough guess)
Nothing to size: no rule is ahead after the luck check. If one were real, about 1-2 bets a day at $10.

Run: `python3 xsite.py run` after `python3 store.py pull bt_cache/xs` (pairs with the hand review are in
`backtest/xs_pairs.json.gz`).
