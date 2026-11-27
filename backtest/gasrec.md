# Gas price recorder test: does live GasBuddy beat the Kalshi gas ladder? (2026-11-27)

Research only, paper only. Tool: `python3 sources.py gasrec` (downloads the recorder's hour files once into
`bt_cache/gasrec/`, keeps only the gas lines and the KXAAAGASD books; `gasrec_nofetch` reuses them).
Background: `backtest/sources.md` section 2 (earlier trend rules lost $34-80 per $100).

**Short answer: no. Dead, as `sources.md` guessed.** At 14-18h UTC the market's middle guess misses AAA's next
number by about a quarter of a cent; the best GasBuddy guess misses by about 1 cent. Buying where they disagree
lost money on almost every setting.

## Four lines up front (rough guesses)

- **Most it could make in an average day:** $0. Nothing here is ahead.
- **Money needed in the account:** none, no track.
- **Bet size where it stops growing:** not reached; the ladder has thousands of contracts at 1c and 99c, but the
  middle rungs are thin.
- **A bad day:** about -$5 at 10 contracts a rung (one day's ladder of wrong bets).

## What was recorded

- 10-27 Nov: AAA's national number and GasBuddy's 51 state averages every 5 minutes, plus every national gas
  ladder book (17 rungs a day, half a cent apart: "above $3.5950", "above $3.6000" ...).
- 17 days with a ladder and AAA's number (11-27 Nov). The recorder skipped some hours, so at 16h UTC 13 days have
  a reading. AAA's own numbers in the recording match Kalshi's settle values exactly (checked 16-27 Nov with probe
  `src_ks_KXAAAGASD`). The rule is "strictly greater than" the rung.
- GasBuddy has no national number, so its state averages are weighted by rough state population.
- AAA posts the new number at about 08:20-08:40 UTC (sometimes the date flips first with yesterday's price for
  10-20 minutes); the Kalshi ladder for that day trades from about 13:00 UTC the day before to 04:59 UTC.

## Who guesses AAA's number better? (average miss in cents, the 10 test days, 18 Nov - 27 Nov)

Fitted on the first 7 days (11-17 Nov), scored on the later days only.

| Guess made at (UTC, day before) | 14h | 15h | 16h | 17h | 18h | 20h | 22h | 0h | 2h |
|---|---|---|---|---|---|---|---|---|---|
| **Market** (where the ladder crosses 50c) | 0.13 | 0.31 | 0.27 | 0.26 | 0.31 | 0.17 | 0.15 | 0.10 | 0.13 |
| AAA yesterday + its last change | 0.63 | 0.76 | 0.88 | 0.96 | 0.84 | 0.57 | 0.70 | 0.76 | 0.77 |
| GasBuddy "change today", fitted | - | 1.98 | 1.34 | 0.91 | 0.71 | 0.58 | 0.49 | 0.63 | 0.76 |
| GasBuddy level vs 24h ago, fitted | - | - | 1.30 | 1.11 | 1.00 | 1.26 | 0.59 | 0.71 | 0.82 |
| GasBuddy 24h change, no fit | - | - | 1.35 | 1.11 | 0.94 | 1.12 | 0.65 | 0.82 | 0.97 |

The market is 3 to 5 times sharper than anything built from GasBuddy, at every hour. It even beats the plain
"yesterday's change carries on" guess, which already beats GasBuddy. The plan's bar ("clearly beat the market's
0.3-0.5c") is missed by a mile. Why: GasBuddy's "change today" resets around 08 UTC and only shows part of the day
by 14-18h; and AAA's number is not the same mix of stations, so its day-to-day step (a steady fall of 1-3.5c a day
in this stretch) doesn't line up with GasBuddy's (e.g. 27 Nov: GasBuddy -3.1c, AAA -0.8c).

## Paper bets (test days only, 10 contracts a rung at the real ask + 1c + Kalshi fee, held to the end)

Rule: buy Yes or No on a rung where the model's chance beats the price by 5c / 10c / 15c. 81 settings tried
(3 models x 9 hours x 3 edges).

- **Headline, fixed before looking** (the model with the smallest training miss at 16h, 10c edge): 25 bets on
  7 days, cost $37.98, back $20.00: **-$47.34 per $100.** Exam: "Too early to tell" (7 separate days),
  worst case per $100: -$100.
- **14h, 16h and 18h pooled** (same 10c edge): 41 bets on 10 days, -$17.40 on $57.40: **-$30.31 per $100.**
  Exam: "Behind, but could be bad luck", worst case per $100: -$100.
- The few settings ahead (e.g. 22h, +$12-15 per $100; 18h at 15c edge, +$64 on $12) sit on 4-9 days and
  2-4 wins: luck from picking 81 settings.

Most losing bets were 3c long shots on rungs the GasBuddy guess wrongly put in reach, i.e. the model simply
missed by more than the market did.

## Backward look (all 13 days at 16h, every rung with a real price 3-97c)

What did the winners share beforehand? Only what the market already said:
- Long shots (under 25c) lost almost every time: Yes under 25c -$56 per $100 (44 bets), No under 25c -$100 (40).
- The favourites won: Yes over 75c below the market's middle +$8.39 per $100 (10 bets); No over 75c above the
  middle -$14.31 (9 bets).
- Mid-priced rungs (25-75c) split both ways, 4-5 bets each: noise.
- No weekday or direction pattern in the market's own misses (all within -0.21c to +0.33c, except 27 Nov, the
  day after Thanksgiving, +0.67c: AAA fell much less than usual).

Nothing new to test. "Favourites at 75c+" is the usual favourite lean that the backtests already showed loses
after costs.

## Verdict

Dropped, no track. The live GasBuddy reading does not beat the Kalshi gas ladder; the market already knows more.
The recorder can stop saving `gas` lines if space matters (Jan's call). Not tested: the weekly ladder
(KXAAAGASW, only 3 weeks recorded) and the state ladders (recorded only in a few early hours).

Exam cards (written to a scratch ledger, not to `backtest/ledger.json`):
- `gas_ladder_vs_live_gasbuddy_16h_10c_edge`: 25 bets, 7 groups, -$47.34 per $100, floor -$100, "Too early to tell", dropped.
- `gas_ladder_vs_live_gasbuddy_14_16_18h_pooled_10c_edge`: 41 bets, 10 groups, -$30.31 per $100, floor -$100,
  "Behind, but could be bad luck", dropped.

## Starship re-check (`backtest/dates.md`): nothing new

No Starship flight since 24 Nov. The last one is still Flight 15 (13 Nov, already in the dates.md count).
Kalshi's settled KXSPACEXSTARSHIP markets end with flight 15 ("before Nov 15", settled Yes on 14 Nov; probe
`src_ks_KXSPACEXSTARSHIP`). Flight 16 has no SpaceX date; outside reports say no earlier than 10 Dec 2026, from
Florida (LC-39A). The re-check ("No on every rung whose Yes is 2-50c") waits for that flight: run probe `dl_fetch`
and `python3 dates.py report` after it.
