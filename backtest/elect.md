# Foreign elections vs local polls (24 Nov 2026, `elect.py`)

Jan asked for 5 deep digs in different areas. This one: national elections outside the US on Polymarket and
Kalshi (who wins, who comes 2nd or 3rd, who makes the runoff, a party's share of the vote). The idea: most
traders are American and may not follow the local polls, so foreign races could be mispriced. We compared the
price with the local poll average from Wikipedia's poll tables. The old polls dig (`backtest/polls.md`) was about
US approval only.

## The ceiling first (rough guess)

- **Most it could make in an average day:** about 15 cents (about $4 a month). The "follow the polls" rule finds
  about 5 bets a month at $25. Without the one big election that made all the profit (Brazil 2026) it made about
  $3 per $100. In a lucky year one upset the polls saw coming can pay $500+, but that is one event, not a habit.
- **Money needed:** $150-250. Bets sit 1-60 days until the vote, and 5-10 are open at once.
- **Bet size where it stops growing:** about $100-500 a bet for the big races (they trade millions of dollars in
  the last week); $25 or less for small-party vote-share brackets.
- **A bad day:** election night. 5-8 bets on the same election win or lose together: about -$125 to -$200 at $25.

## What we did

- `elect.py scan`: Polymarket tags `world-elections`, `global-elections`, `politics` and 40 country tags: 1,028
  finished foreign-politics events, about $4 billion traded (182 events over $1 million). Kalshi: 852 foreign
  series in Elections / Politics / World (biggest: Brazil president, Canada PM, Peru, Romania, Honduras).
- `elect.py fetch`: every market of 440 Polymarket election events (6,640 markets, 3,619 with every real trade
  in 5-minute steps) and 80 Kalshi election series (hourly real bid / ask + every trade).
- `elect.py wiki`: the "Opinion polling for the ..." page of 70 elections (and the election article when there is
  no poll page). Our own table reader (the pages are messy: logos instead of party names, year-less dates, event
  rows across the table) found usable polls for about 55 of them.
- **The poll model:** average of the polls that ended 2+ days before the look, from the last 14 days (45 if fewer
  than 3). Each candidate's real result = poll average + a usual poll miss (bigger for big parties, bigger further
  out), 4,000 random elections, then the chance of each answer (1st, 2nd, 3rd, top two, share bracket). For a
  two-round vote, the overall winner uses only head-to-head runoff polls. Seat questions in first-past-the-post
  countries (Canada, UK, Australia, France, BC, Ontario) are left out: national shares don't give the seat order
  (Canada's Bloc wins more seats than the bigger NDP).
- Looks at 60, 30, 14, 7, 3 and 1 days before the vote (vote days written in by hand, `FIX_DAYS`).
- **Prices:** Polymarket = the worst price anyone paid in the hour after the look + 1c + the market's fee, $25 a
  bet. Kalshi = the real asking price + Kalshi's fee, only when the buyer-seller gap is 10c or less. One bet per
  market. All markets of one election count as one bet in the luck range (they win and lose together).

## Result 1: the price forecasts better than the polls

Lower score = better forecast (0 = perfect; a coin flip on a 50-50 question scores 0.25).

| poll-miss size | looks | price score | poll score |
|---|---|---|---|
| x1.0 | 1855 | 0.1036 | 0.1275 |
| x1.5 | 1855 | 0.1036 | 0.1183 |
| x2.0 (used below) | 1855 | 0.1036 | 0.1149 |
| x3.0 | 1855 | 0.1036 | 0.1146 |

| days before the vote | Polymarket looks | price score | poll score | Kalshi looks | price score | poll score |
|---|---|---|---|---|---|---|
| 60 | 97 | 0.1176 | 0.1458 | 29 | 0.2456 | 0.2309 |
| 30 | 150 | 0.1119 | 0.1133 | 38 | 0.2173 | 0.1763 |
| 14 | 299 | 0.1078 | 0.1263 | 63 | 0.1557 | 0.1787 |
| 7 | 391 | 0.1074 | 0.1102 | 70 | 0.1527 | 0.1620 |
| 3 | 437 | 0.0972 | 0.1130 | 71 | 0.1393 | 0.1724 |
| 1 | 481 | 0.0984 | 0.1077 | 59 | 0.1733 | 0.2053 |

Polymarket: 111 events in 36 elections. Kalshi: 30 events in 18 elections (few, and Brazil, Colombia and Peru
2026 make most of them; those three had big upsets, which is why Kalshi's scores are bad for both).
On Polymarket the price beats the polls at every distance, most of all in the last 3 days. The traders do read
the local polls, and they know things the polls miss: seat maps, tactical voting, a fading candidate.

## Result 2: betting where the polls and the price disagree

| site | rule | bets | elections | won | per $100 | first half / second half | luck range per $100 | exam verdict | without the best election |
|---|---|---|---|---|---|---|---|---|---|
| Polymarket | follow the polls, 10c+ apart | 145 | 29 | 69 | +$26.71 | +$4.73 / +$48.31 | -20.9 to 74.33 | Ahead, but could be luck | +$3.29 (without Brazil 2026) |
| Kalshi | follow the polls, 10c+ apart | 50 | 14 | 24 | +$3.00 | +$7.35 / -$1.70 | -36.74 to 42.75 | Ahead, but could be luck | -$13.67 (without Brazil 2026) |
| Polymarket | follow the polls, 20c+ apart | 56 | 20 | 24 | +$42.24 | -$3.08 / +$87.36 | -48.52 to 133.0 | Ahead, but could be luck | -$9.69 (without Brazil 2026) |
| Kalshi | follow the polls, 20c+ apart | 25 | 8 | 9 | -$15.73 | +$2.67 / -$31.15 | -67.08 to 35.62 | Too early to tell | -$29.08 (without Ecuador 2025) |
| Polymarket | follow the polls, Yes only | 68 | 24 | 23 | +$37.97 | +$1.45 / +$74.30 | -26.56 to 102.51 | Ahead, but could be luck | +$7.40 (without Brazil 2026) |
| Kalshi | follow the polls, Yes only | 24 | 12 | 8 | -$10.21 | -$20.95 / +$3.90 | -64.35 to 43.93 | Behind, but could be bad luck | -$35.48 (without Brazil 2026) |
| Polymarket | follow the polls, No only | 78 | 26 | 47 | +$17.39 | +$8.98 / +$25.77 | -16.74 to 51.51 | Ahead, but could be luck | +$0.78 (without Brazil 2026) |
| Kalshi | follow the polls, No only | 30 | 13 | 18 | +$13.14 | +$27.48 / +$1.69 | -18.44 to 44.72 | Ahead, but could be luck | +$2.60 (without Brazil 2026) |
| Polymarket | against the polls, 10c+ apart | 145 | 29 | 76 | -$7.63 | -$5.53 / -$9.69 | -26.07 to 10.82 | Behind, but could be bad luck | -$12.04 (without Bolivia 2025) |
| Kalshi | against the polls, 10c+ apart | 47 | 13 | 24 | -$11.60 | -$15.06 / -$8.45 | -43.78 to 20.58 | Behind, but could be bad luck | -$22.54 (without Colombia 2026) |

**Read the big wins one by one.** The Polymarket rule made $970 on $3,632 bet. Brazil 2026 alone made $863 of it:
Flávio Bolsonaro won the first round, the price then gave Lula only 12c to win the runoff while the runoff polls
still had him close, and Lula won (5 linked bets: Lula 2nd in round 1 at 5c, Lula to win at 12c, No on Flávio at
12c, ...). Next: Saxony-Anhalt (BSW 5-7% at 7c), Chile (Parisi 3rd at 7c), Venezuela 2024 (polls said González;
Polymarket paid González because credible reporting showed he won, not the official count). Without Brazil the rule
is about +$3 per $100 on Polymarket and loses on Kalshi. That's one upset, not a habit. **Dropped, no track.**

## Result 3: the backward look (prices alone, and the upsets)

Every foreign election market on Polymarket with a known vote day (2,509 markets, 56 elections), bought at real
prices 30, 7 and 1 days before the vote, by the Yes price:

| days before | Yes price | markets | elections | Yes won | buy Yes per $100 | buy No per $100 |
|---|---|---|---|---|---|---|
| 30 | 2-10c | 18 | 14 | 4 | +$264.22 | -$17.68 |
| 30 | 10-25c | 13 | 11 | 3 | +$1.43 | -$10.98 |
| 30 | 25-50c | 19 | 13 | 6 | -$22.12 | +$9.27 |
| 30 | 50-75c | 17 | 12 | 13 | +$20.61 | -$45.62 |
| 30 | 75-90c | 12 | 12 | 8 | -$22.00 | +$76.50 |
| 30 | 90-98c | 4 | 4 | 3 | -$20.67 | +$107.83 |
| 7 | 2-10c | 85 | 21 | 4 | -$18.19 | -$0.82 |
| 7 | 10-25c | 67 | 22 | 16 | +$24.59 | -$10.55 |
| 7 | 25-50c | 68 | 21 | 18 | -$24.07 | +$12.98 |
| 7 | 50-75c | 30 | 19 | 17 | -$8.63 | +$4.19 |
| 7 | 75-90c | 23 | 17 | 18 | -$5.42 | +$2.38 |
| 7 | 90-98c | 19 | 13 | 18 | -$0.49 | -$62.41 |
| 1 | 2-10c | 175 | 33 | 12 | +$13.51 | -$3.43 |
| 1 | 10-25c | 170 | 36 | 33 | -$4.17 | -$5.15 |
| 1 | 25-50c | 157 | 32 | 58 | +$5.24 | -$5.15 |
| 1 | 50-75c | 65 | 30 | 34 | -$15.62 | +$17.63 |
| 1 | 75-90c | 45 | 28 | 35 | -$7.34 | -$3.93 |
| 1 | 90-98c | 30 | 22 | 26 | -$9.16 | +$68.33 |

No band is ahead at all three distances; the big numbers are 4-30 markets where one upset decides. By region, a
week before: Latin American favourites (50-98c) lost $14.12 per $100 on 26 bets (Brazil, Colombia, Peru upsets),
Europe -$1.36 on 37, Asia +$2.75 on 9.

**The upsets.** Winner questions with a favourite at 60c+ a week before: 64, won 49 (77 in 100) at an average price
of 85c. So favourites were a bit too dear. Betting No on them:

| backward look: No on the favourite (winner questions) | bets | elections | No won | per $100 | luck range | exam verdict | without the best election |
|---|---|---|---|---|---|---|---|
| 30 days before, favourite at 60-98c | 18 | 18 | 5 | +$36.59 | -63.62 to 136.79 | Ahead, but could be luck | -$4.32 (without Argentina 2025) |
| 7 days before, favourite at 60-98c | 31 | 25 | 8 | +$13.07 | -46.24 to 72.39 | Ahead, but could be luck | -$6.95 (without Belgium 2024) |
| 1 days before, favourite at 60-98c | 43 | 35 | 12 | +$53.16 | -38.33 to 144.65 | Ahead, but could be luck | +$9.25 (without Belgium 2024) |

What the 15 upsets had in common: in 7 of the 9 with a poll table, **the polls had the same favourite** (Simion,
Trzaskowski, PVV, Cepeda, Lula round 1, Thailand's People's Party, Belgium's VB). The polls were wrong, so the
polls can't warn you. A pattern found by looking, too small to bet: in Europe four far-right favourites lost
(Simion, PVV, Belgium's VB, France's RN in 2024); Austria's FPÖ won. Each needs many more elections than exist.
Found by looking, one election moves each line by $50+ per $100. **Dropped, no track.**

## Traps (for the next dig)

- **Wikipedia poll tables often have no year in the date** (the year is a section heading). Read naively, a 2024
  table looks like 2025 polls. Fix: if a year-less table puts polls after the vote, move the whole table back a
  year (`poll_avg`), and inside a table, rows go newest first.
- **Party names are often logos**: read the link title or the image's alt text (`_cell_name`).
- **Pick the table by freshness**: a page has many tables (first round, runoff pairs, old years, regions, preferred
  PM). Use the one with fresh polls covering the market's candidates; a head-to-head table can't answer a
  first-round or vote-share question.
- **Polymarket's event end date is often not the vote day** (e.g. "31 Dec 2025" for the German election): write the
  vote days in by hand.
- **Surnames aren't enough** ('F. Bolsonaro' is not Michelle Bolsonaro) and pairs ('Jara & Matthei') have no column.
- **Seats are not votes** in first-past-the-post countries.
- Wikipedia's API answers 429 when rushed; `wiki` saves what it got and a rerun fills the gaps.

## Not dug

Seat-count brackets, margin-of-victory brackets and turnout (need a seat model or turnout history), Israel (polls
are in seats), "next PM / coalition" questions (government talks, not votes), leader-exit markets ("Starmer out by"),
and the 2026 elections still to come. The data is saved (`bt_cache/el/`, `bt_cache/elw/` in the price store), so a
seat-model dig can start from it.
