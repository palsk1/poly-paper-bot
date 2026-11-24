# Fed decision and CPI bets vs what the big-money markets say (fed.py, 2026-11-24)

## The short version

- **Question:** Kalshi and Polymarket sell "what will the Fed do at its next meeting" and "what will inflation (CPI)
  be" bets. Banks bet on the same thing in futures and options on the CME. Do the CME prices know better, so we can
  buy where the betting sites disagree? The 9 Nov dig (`econ.py`, `backtest/econ.md`) already tested CPI against the
  Cleveland Fed's forecast (it lost to Kalshi) and could not test the Fed: no free history of futures odds.
- **New source found:** the Atlanta Fed publishes, free, the chance of every Fed rate range as read from CME SOFR
  options, every trading day since 29 Mar 2023 (`mpt_histdata.xlsx`, 7 MB). CME's own FedWatch, Yahoo futures,
  stooq, Barchart, investing.com and rateprobability.com all block scripts from GitHub. For CPI there is no free
  futures or inflation-swap history at all, so CPI was tested against the other betting site instead.
- **Answer: no lead worth a track.**
  1. **Fed vs the options:** only 8 meetings per site can be read cleanly (the March, June, September and December
     meetings, which sit on the first day of an options quarter). Buying where the options said 10c+ more:
     -$8.43 per $100 on 26 bets in 8 meetings, "Too early to tell", luck range -$110 to +$93. Kalshi alone -$27.88,
     Polymarket alone +$11.02. Kalshi's own price guessed about as well as the options (score 0.014 vs 0.009, 8
     meetings; lower is better), and the options view goes dark in the last ~5 days (the options expire before the
     quarter starts).
  2. **Fed, Kalshi vs Polymarket:** 47 Polymarket markets in 14 meetings with a Kalshi twin. The two sites never
     sat 5c+ apart at real prices more than once (1 bet, lost). They move together. Nothing to buy.
  3. **CPI, Kalshi vs Polymarket:** 185 Polymarket CPI brackets in 24 months against the same bracket built from
     Kalshi's "above X" ladder. Buying on Polymarket 3c+ under Kalshi -$14.97 per $100 (94 bets, 19 months), 5c+
     -$4.66 (64 bets), 10c+ **+$47.87 (23 bets, 13 months, "Ahead, but could be luck")**. Buying on Kalshi where
     it was cheaper lost every way (-$19 to -$64). The 10c+ win is a lone survivor of three gaps (the two smaller
     gaps lose), found by looking, and sits in thin markets: in 12 of the 23 bets under $100 changed hands in the two
     hours we would buy, and two long-shot Yes wins (bought at 19c and 29c) make about two thirds of the profit. Not a track. Free re-check: the same rule on the Dec 2026 - Feb 2027 CPI months.
  4. **Backward look (what winners had in common, every meeting, both sites):** Kalshi's Fed prices are honest:
     90-98c sides won 35 of 35 looks, 2-10c sides 0 of 46. Buying the favourite at 85-97c: +$5.96 per $100 a day
     before (11 bets), -$0.65 a week before (16 bets), +$8.63 four weeks before (11 bets); No on 3-15c long shots
     +$5.91 / -$1.28 / +$6.29. All "Too early to tell" or "could be luck", 7-10 meetings each, and one surprise
     (like the Sept 2024 half-point cut or the Sept 2026 hike) wipes out a year of these.
- **Ceiling (rough guess):** the Fed meets 8 times a year, so even a real edge gives 2-3 bets a meeting. At $25 a
  bet and +$6 per $100, about **$1.50 a bet, about $30 a year**. Money needed: $50-75, out for up to 4 weeks. Size
  is not the limit (Kalshi trades $20-100 million per meeting); the calendar is. Bad day: a surprise meeting loses
  the whole stake, about -$25 to -$75. CPI 10c gap on Polymarket: about 1 bet a month, $25 a bet (sellers run out
  above that), at most about $10-15 a month even if it were real; bad day -$25.

## Data

- Atlanta Fed Market Probability Tracker history (`bt_cache/fed/mpt_histdata.xlsx`, store `price-store`):
  919 days, 29 Mar 2023 to 20 Nov 2026; for each day and each 3-month quarter, the chance of each 25bp range
  (chances under 2 in 100 left out, so the rest is scaled to 1). We only use a day's file from the next day on.
- US Treasury daily bill rates 2021-2026 (`bills.json.gz`, home.treasury.gov CSV): fetched, not used (bill rates
  move a few hundredths each day for reasons other than the Fed, which is 20c of chance on a 25bp step).
- Kalshi: KXFEDDECISION (16 meetings, Dec 2024 - Oct 2026, $2-100 million per meeting), KXFED (7 meetings),
  KXCPI / KXCPIYOY / KXCPICORE (every strike), hourly bid/ask + trades (`tapes_*.json.gz`). The 100-times-too-small
  quote trap (see `dates.load`) is repaired.
- Polymarket: tags `fed-rates` (734 markets, 21 decision events May 2024 - Oct 2026) and `cpi` (603 markets),
  every real trade in 5-minute steps (`bt_cache/fam_fed_rates/`, `bt_cache/fam_cpi/`). Sept 2025, March 2026 and
  April 2026 Fed events came back without trades.

## How the tests price a bet

- Looks at 1, 2, 4, 7, 14, 21 and 28 days before the decision at 15:00 UTC (Fed); every 6 hours over the last 28
  days (cross-site).
- Kalshi: buy Yes at the hourly ask, No at 1 minus the bid (quote at most 12 hours old), plus Kalshi's taker fee.
  Polymarket: the worst price anyone paid over the next 2 hours, plus its fee. One bet per market and side (the
  earliest look that fits), $25 a bet, held to the result. Bets on one meeting / one CPI month count as one.
- Options odds for a meeting = the quarter starting on the meeting day (December: up to 8 days later). The next
  meeting, about 6 weeks into that quarter, blurs the number a little: in a run of cuts (2024, late 2025) it makes
  the options lean further toward "cut" than the meeting itself deserves.

## Traps

- SOFR quarterly options stop trading before their quarter starts, so the options view has no number for the last
  ~5 days before a March / June / September / December meeting.
- Non-quarter meetings (January, April/May, July, October/November) can't be read from quarterly options at all.
- Kalshi's hourly quotes on KXFED / KXFEDDECISION come 100 times too small through `yesno.k_candle` (first run
  showed +$1,203 per $100). `fed.k_tapes()` repairs them.

## Full run output

See the run log of `python3 fed.py all` (probe `fed_all`). The tables below are copied from it.

### Who guesses better: options vs market (lower is better)

| Site | Days before | Points | Meetings | Options score | Market score |
|---|---|---|---|---|---|
| kalshi | 7 | 50 | 8 | 0.0087 | 0.0136 |
| kalshi | 14 | 53 | 8 | 0.0112 | 0.0144 |
| kalshi | 21 | 55 | 8 | 0.0269 | 0.0368 |
| kalshi | 28 | 61 | 8 | 0.0265 | 0.0358 |
| poly | 7 | 32 | 8 | 0.0096 | 0.0663 |
| poly | 14 | 27 | 7 | 0.0240 | 0.0512 |
| poly | 21 | 29 | 7 | 0.0498 | 0.0876 |
| poly | 28 | 32 | 8 | 0.0484 | 0.0829 |

The options look better on paper, but 8 meetings is nothing: most of the gap is the Sept 2024 half-point cut and the
Sept 2026 hike, where the blur from the next meeting happened to point the right way. Betting on it lost money on
Kalshi (bets above).

### Backward look: how often each Fed price band won (all meetings, 1-28 days before)

| Site | Price band | Looks | Average price | Share that won | Meetings |
|---|---|---|---|---|---|
| kalshi | 2-10c | 46 | 0.04 | 0.00 | 14 |
| kalshi | 10-30c | 19 | 0.19 | 0.05 | 9 |
| kalshi | 30-70c | 11 | 0.51 | 0.55 | 4 |
| kalshi | 70-90c | 19 | 0.81 | 0.95 | 10 |
| kalshi | 90-98c | 35 | 0.95 | 1.00 | 15 |
| poly | 2-10c | 45 | 0.05 | 0.02 | 15 |
| poly | 10-30c | 17 | 0.20 | 0.12 | 10 |
| poly | 30-70c | 18 | 0.51 | 0.56 | 5 |
| poly | 70-90c | 13 | 0.79 | 0.85 | 7 |
| poly | 90-98c | 36 | 0.95 | 0.97 | 15 |

### The 23 CPI bets (Polymarket 10c+ under Kalshi), one by one

Mostly "No on a bracket" 2-4 weeks before the release. 16 won, 7 lost. In 12 of 23 the two hours we would buy saw
under $100 change hands. Two long-shot Yes wins (the December "2.8% or less" at 19c, +$107, and March "0.8% or
more" at 29c, +$61) make about two thirds of the +$239. The smaller gaps (3c, 5c) on the same markets lose, which
says "thin-market noise" more than "Kalshi knows". The list is printed by `python3 fed.py cross` (lines "CPI BET").
