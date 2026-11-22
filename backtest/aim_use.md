# "Which AI gets used most" bets vs the public usage numbers (22 Nov 2026)

Tool: `aim.py`. Rebuild the tables below with `python3 aim.py use` (data: `bt_cache/aim/` in the price store).

## In short

**No track. One small lead to re-check for free on 21 Dec.**

- **The bets.** Kalshi lists ladders on public usage numbers: "Will OpenAI's share on OpenRouter this week be above 18.4 in 100?", "Will OpenRouter handle more than 215 trillion tokens this week?", the same every day for Vercel's AI Gateway, and monthly app downloads. 4,125 finished markets since August, in four kinds. Polymarket only has a small copy (312 markets on who is 1st / 2nd / 3rd on OpenRouter): both sides lose there, Yes -$63 and No -$14 per $100.
- **Weekly token total: the public count is right, and the price still beats it.** OpenRouter gives away each day's token count (free file, new every night). Adding up the days gives Kalshi's result in 11 of 12 weeks. But betting on "days so far + the rest like last week" loses: -$31.92 per $100 on 53 Yes bets, -$15.31 on 54 No bets. The price misses less at every point of the week. Usage can drop by a quarter over a weekend, and the people trading seem to see it first (the site shows the running day live).
- **A lab's weekly share on OpenRouter: the free file is not the number Kalshi uses.** Our count says Google has 3-7 in 100, Kalshi settles at 13-23. So there is no outside number to bet with here.
- **Vercel daily shares: thin and expensive.** The middle gap between the buy and the sell price is 25c. Everything loses (always Yes -$38.17, always No -$18.95 per $100) except No on long shots, +$2.64 per $100 on 581 bets, "Ahead, but could be luck". Vercel's free data file refuses scripts, so "last result plus the usual change" was the only model, and it lost.
- **App downloads:** both sides lose about $20-25 per $100. Only 3 months of them.
- **The one lead, found by looking (backward look).** On the first day of the week, buy Yes on the OpenRouter share ladders at 15-85c. 239 bets, 137 won, **+$40.36 per $100**, ahead in 8 of 11 weeks, exam verdict "Ahead, but could be luck". No instead of Yes loses $34.68. The lead fades day by day and is a loss from day 5.
- **Why not to trust it yet.** One week (ending 12 Oct) made $509 of the $965 total. It is 11 weeks. We found it by cutting the data about 150 ways. And we have no reason for it: it works whether the share rose or fell the week before, and the same idea on Vercel loses $43.41 per $100.

## Would it fit a small bankroll?

Yes. About 20 bets a week at $10, so about $200 out at once, back within 7 days. Kalshi's trade list shows 500 contracts at a time changing hands at these prices, so $10-25 bets are real.

## The free re-check (rule written down today, 22 Nov)

- Rule, unchanged: Kalshi OpenRouter lab share ladders (the `...SHARE` series), first hour with 144+ hours left where the asking price for Yes is 15-85c and the gap to the buy price is at most 15c. Buy Yes, $10, hold to the end.
- Fresh weeks: those ending 30 Nov, 7 Dec, 14 Dec and 21 Dec. None of them is in the data above.
- Look once, on 21 Dec, with `python3 aim.py use` after a new `aim_kall-use` probe.
- It passes if the four weeks together are ahead and at least 3 of the 4 are ahead. If it passes, it is worth a paper track. If not, drop it.

## Traps (for the next dig)

- **OpenRouter's free daily file** (`openrouter.ai/api/v1/datasets/exports/rankings-daily/<day>.json`, no key, each file holds the 30 days before it) gives the token total Kalshi uses, but not its "market share by model author".
- **Vercel's export** (`vercel.com/api/ai/leaderboard-export`) answers 403 to scripts from GitHub. We did not work around it.
- **Answers inside one week are linked** (shares add up, and all strikes of one ladder win or lose together). Count weeks, not bets.
- **Kalshi's 100-times-too-small quotes** show up on these series too. `aim.use_load()` repairs them.

---

Everything below is printed by `python3 aim.py use`.

## Kalshi usage ladders: 4125 settled markets, 456 events, 510155 hourly looks with a real two-sided quote

| kind | series | markets | events | first close | last close | middle gap between buy and sell price |
|---|---|---|---|---|---|---|
| Vercel AI Gateway daily shares | 12 | 2719 | 302 | 2026-08-28 | 2026-11-21 | 25c |
| OpenRouter weekly share of a lab | 11 | 638 | 78 | 2026-08-17 | 2026-11-16 | 4c |
| OpenRouter weekly token total | 2 | 189 | 15 | 2026-08-24 | 2026-11-16 | 14c |
| monthly app downloads | 23 | 579 | 61 | 2026-09-07 | 2026-11-08 | 1c |

### The last result plus the usual change, against the price

| kind | time left | looks | miss score, last result | miss score, the price |
|---|---|---|---|---|
| Vercel AI Gateway daily shares | last day | 26714 | 0.1778 | 0.1269 |
| Vercel AI Gateway daily shares | 1-3 days | 69492 | 0.1914 | 0.1592 |
| Vercel AI Gateway daily shares | 3+ days | 38360 | 0.2032 | 0.1771 |
| OpenRouter weekly share of a lab | last day | 2490 | 0.2164 | 0.0196 |
| OpenRouter weekly share of a lab | 1-3 days | 8076 | 0.2463 | 0.0642 |
| OpenRouter weekly share of a lab | 3+ days | 21723 | 0.2497 | 0.1409 |

### OpenRouter's public daily token totals (94 days, 2026-08-20 to 2026-11-21) against the weekly token bets

| days of the week already public | looks | miss score, the count | miss score, the price |
|---|---|---|---|
| 0 | 711 | 0.2511 | 0.1947 |
| 1 | 1859 | 0.2194 | 0.1570 |
| 2 | 2288 | 0.2438 | 0.1643 |
| 3 | 2310 | 0.2231 | 0.1305 |
| 4 | 2293 | 0.1419 | 0.0954 |
| 5 | 2081 | 0.0963 | 0.0558 |
| 6 | 1505 | 0.0449 | 0.0282 |
| 7 | 44 | 0.0227 | 0.0002 |

### The exam

Real asking price + Kalshi's fee, $10 a bet, first hour that fits, gap between buy and sell price at most 15c. Separate bets = weeks or days, because the answers inside one are linked.

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| OpenRouter weekly token total (Kalshi): Yes where the public daily count says 15c+ more than the ask | 53 | 17 | -$31.92 | -$7.65 / -$55.30 | -71.23 to 7.39 | -100.0 | Too early to tell |
| OpenRouter weekly token total (Kalshi): No where the public daily count says 15c+ less than the bid | 54 | 14 | -$15.31 | -$20.84 / -$9.78 | -85.66 to 55.04 | -100.0 | Too early to tell |
| Vercel AI Gateway daily shares: Yes where the last result says 15c+ more than the ask | 703 | 138 | -$61.06 | -$67.15 / -$54.99 | -70.14 to -51.99 | -81.76 | Losing |
| Vercel AI Gateway daily shares: No where the last result says 15c+ less than the bid | 645 | 219 | -$27.16 | -$10.88 / -$43.39 | -42.43 to -11.89 | -62.79 | Losing |
| OpenRouter weekly share of a lab: Yes where the last result says 15c+ more than the ask | 147 | 45 | +$27.47 | +$43.52 / +$11.64 | -29.63 to 84.56 | -100.0 | Too early to tell |
| OpenRouter weekly share of a lab: No where the last result says 15c+ less than the bid | 194 | 28 | -$56.35 | -$28.66 / -$84.05 | -88.68 to -24.03 | -100.0 | Too early to tell |
| Usage ladders (Kalshi), Vercel AI Gateway daily shares: always Yes at 3-97c, first look | 1727 | 722 | -$38.17 | -$48.86 / -$27.49 | -44.64 to -31.7 | -53.79 | Losing |
| Usage ladders (Kalshi), Vercel AI Gateway daily shares: always No, Yes at 3-97c, first look | 1632 | 825 | -$18.95 | -$11.35 / -$26.54 | -26.62 to -11.27 | -37.9 | Losing |
| Vercel AI Gateway daily shares: No on long shots, Yes at 3-15c | 581 | 552 | +$2.64 | +$3.88 / +$1.41 | 0.3 to 4.98 | -5.63 | Ahead, but could be luck |
| Vercel AI Gateway daily shares: Yes on near-sure things, 85-97c | 490 | 440 | -$1.91 | +$1.18 / -$5.01 | -5.21 to 1.38 | -10.98 | Behind, but could be bad luck |
| Usage ladders (Kalshi), OpenRouter weekly share of a lab: always Yes at 3-97c, first look | 576 | 294 | +$7.05 | -$8.17 / +$22.28 | -17.37 to 31.48 | -52.96 | Ahead, but could be luck |
| Usage ladders (Kalshi), OpenRouter weekly share of a lab: always No, Yes at 3-97c, first look | 573 | 264 | -$18.82 | -$19.74 / -$17.90 | -35.81 to -1.83 | -61.6 | Losing |
| OpenRouter weekly share of a lab: No on long shots, Yes at 3-15c | 304 | 254 | -$9.38 | -$3.79 / -$14.97 | -16.77 to -1.98 | -42.34 | Losing |
| OpenRouter weekly share of a lab: Yes on near-sure things, 85-97c | 300 | 274 | -$0.22 | -$1.48 / +$1.05 | -3.69 to 3.26 | -30.74 | Behind, but could be bad luck |
| Usage ladders (Kalshi), OpenRouter weekly token total: always Yes at 3-97c, first look | 180 | 88 | -$29.52 | -$17.61 / -$41.44 | -48.15 to -10.9 | -73.49 | Losing |
| Usage ladders (Kalshi), OpenRouter weekly token total: always No, Yes at 3-97c, first look | 182 | 88 | +$0.37 | -$19.94 / +$20.67 | -50.4 to 51.13 | -100.0 | Ahead, but could be luck |
| OpenRouter weekly token total: No on long shots, Yes at 3-15c | 91 | 82 | -$2.49 | -$0.65 / -$4.28 | -8.6 to 3.63 | -29.49 | Behind, but could be bad luck |
| OpenRouter weekly token total: Yes on near-sure things, 85-97c | 97 | 83 | -$7.90 | -$5.61 / -$10.14 | -21.87 to 6.07 | -47.43 | Behind, but could be bad luck |
| Usage ladders (Kalshi), monthly app downloads: always Yes at 3-97c, first look | 526 | 250 | -$25.37 | -$21.88 / -$28.86 | -34.79 to -15.95 | -100.0 | Too early to tell |
| Usage ladders (Kalshi), monthly app downloads: always No, Yes at 3-97c, first look | 535 | 261 | -$19.95 | -$5.05 / -$34.79 | -40.63 to 0.73 | -100.0 | Too early to tell |
| monthly app downloads: No on long shots, Yes at 3-15c | 269 | 246 | -$0.73 | -$4.15 / +$2.67 | -2.67 to 1.22 | -97.93 | Too early to tell |
| monthly app downloads: Yes on near-sure things, 85-97c | 262 | 241 | +$0.34 | -$2.43 / +$3.12 | -4.95 to 5.64 | -100.0 | Too early to tell |

### Backward look: the OpenRouter share bets on the first day of the week

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| OpenRouter lab share (Kalshi): Yes at 15-85c on the first day of the week | 239 | 137 | +$40.36 | +$7.16 / +$73.27 | 7.44 to 73.27 | -50.45 | Ahead, but could be luck |
| same, No instead of Yes | 233 | 87 | -$34.68 | -$24.84 / -$44.44 | -55.19 to -14.17 | -83.69 | Losing |
| same, Yes, the 4 big labs only | 194 | 118 | +$48.96 | +$35.19 / +$62.73 | 19.21 to 78.71 | -35.49 | Promising, needs more bets |
| same, Yes at 15-50c | 158 | 72 | +$56.01 | +$22.14 / +$89.87 | 10.99 to 101.03 | -56.43 | Ahead, but could be luck |
| same, Yes at 50-85c | 121 | 92 | +$11.60 | +$0.80 / +$22.23 | -3.48 to 26.68 | -47.96 | Too early to tell |
| same, strike at or below last week's result | 104 | 69 | +$35.90 | +$21.70 / +$50.10 | 14.28 to 57.52 | -40.28 | Too early to tell |
| same, strike above last week's result | 119 | 65 | +$58.89 | +$42.68 / +$74.83 | 0.71 to 117.07 | -83.22 | Too early to tell |
| Yes at 15-85c, second day | 333 | 166 | +$7.23 | -$12.86 / +$27.20 | -11.55 to 26.0 | -43.17 | Ahead, but could be luck |
| Yes at 15-85c, days 3-4 | 346 | 151 | -$5.58 | -$19.37 / +$8.20 | -27.15 to 15.99 | -58.25 | Behind, but could be bad luck |
| Yes at 15-85c, days 5-6 | 218 | 83 | -$25.73 | -$35.23 / -$16.23 | -43.95 to -7.51 | -69.6 | Losing |
| Yes at 15-85c, last day | 63 | 21 | -$46.36 | -$73.53 / -$20.04 | -73.15 to -19.57 | -100.0 | Losing |
| Vercel daily shares: Yes at 15-85c on the first day | 429 | 154 | -$43.41 | -$52.29 / -$34.58 | -53.55 to -33.27 | -71.3 | Losing |

The first-day Yes rule week by week (week's end, bets, won, dollars): 2026-08-17 15 / 7 / +60, 2026-08-24 17 / 4 / -103, 2026-09-07 27 / 17 / +158, 2026-09-21 2 / 0 / -20, 2026-09-28 46 / 22 / +6, 2026-10-05 26 / 12 / +87, 2026-10-12 34 / 24 / +509, 2026-10-19 17 / 10 / +45, 2026-10-26 29 / 23 / +168, 2026-11-02 1 / 0 / -10, 2026-11-16 25 / 18 / +65

By lab: KXANTHSHARE 41 / 26 / +201, KXBABASHARE 13 / 5 / -12, KXDEEPSHARE 55 / 28 / +115, KXGOOGSHARE 53 / 32 / +267, KXOPENSHARE 45 / 32 / +366, KXTENCENTSHARE 16 / 6 / +1, KXXIAOMISHARE 11 / 4 / -36, KXZAISHARE 5 / 4 / +61
