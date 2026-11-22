# AI leaderboard bets vs the public leaderboard (22 Nov 2026)

Tool: `aim.py`. Rebuild the tables below with `python3 aim.py report` (data: `bt_cache/aim/` and `bt_cache/fam_ai/` in the price store).

## In short

**Dropped, no track.** Nothing here is worth a paper track yet.

- **The bets.** Both sites take bets on who is on top of the Arena (LMArena) leaderboard for AI models: "Will Google have the best AI model at the end of November?", "Which model is #1 on Friday?", and the same for 2nd and 3rd place, coding, math and Chinese models. Polymarket: 3,648 finished markets in 163 events. Kalshi: 1,473 finished markets in 5 series, about $49 million traded on the biggest one.
- **The outside number.** Arena publishes its whole leaderboard history for free (259 dated boards since 2023). From it we can see who held each place on any day, and how often a place changed hands in the past.
- **Does the public board beat the price? No.** The price forecasts better than the boards' own record at every distance from the end. Buying where the two disagree by 10c or more: +$16.39 per $100 on 81 Yes bets, but the first half lost $44.84 and the second half won $75.31, so that is luck. No bets: +$0.60 on 131. Nothing.
- **One lead, found by looking: the "late holder".** In the last 3 days, buy Yes on the name that already holds the place, at 50-97c. On Polymarket: 39 bets, 37 won, +$4.31 per $100 ("Ahead, but could be luck"). Stretch it to 5 days and it reads +$11.12 on 52 bets ("Promising"). Stretch it to 7 days and it is behind (-$2.15). A result that flips when you move the window two days is a warning sign.
- **The fresh check on Kalshi killed it.** The rule was written down before the Kalshi prices were opened. At Kalshi's real asking prices plus its fee: 102 bets, 94 won, **-$2.29 per $100** ("Behind, but could be bad luck"); the 5-day version -$5.06 on 145 bets ("Losing"). Example: you pay $9.40 to win $10.00, so one loss eats about 15 wins, and the holder lost 8 times in 102.
- **Why the holder loses.** Every loss was a new model landing on the board in the last days (Opus 5, Fable 5.1, Gemini 4, GPT-5.6) or two versions of the same model swapping places by a point or two. Nobody can see that coming from the board itself. People who know a release is near can.
- **Release-day bets** ("will GPT-6 come out on 14 October?"): No on the 10-50c days made +$1.92 per $100 on 40 bets and -$0.35 at 4c more cost. Could be luck. Dropped.
- **Everything else in the AI tag** on Polymarket: Yes on long shots loses heavily, No is about even. Same as every other family.

## Would it fit a small bankroll?

Yes, which is the sad part: $10-25 a bet, 3 to 6 bets a month, money stuck for 3 to 5 days, about $50 out at once. It fits $300 fine. It just does not make money.

## Traps (for the next dig)

- **The board's date is not the day it went public.** A board can be dated 1-2 days before anyone could see it (launch boards are prepared early: Gemini 3 Pro's first board is dated 16 Nov 2025, public on 18 Nov). `aim.py` only uses a board 3 days after its date (`LAG`). With a 1-day wait the Polymarket lead looked better (+$7 instead of +$4 per $100).
- **Old boards don't reproduce results.** Before July 2025 the dataset's boards don't match how markets ended (Arena changed its default view in May 2025). `FIRST_END` skips them. After that our reading of the rules matches the result in 98-100 of 100 markets on both sites (`aim.py check`, `aim.py kcheck`).
- **Kalshi's hourly quotes come 100 times too small** on some series (the known candle trap). `aim.k_load()` repairs them.
- **Two versions of one model** ("thinking" and plain) sit 1-5 points apart and swap places often. Model bets are much less safe than company bets: on Kalshi the model series alone lost $32 with this rule, while the other four series together made $9.
- **Not dug:** Kalshi's other AI families (which model has the biggest share on OpenRouter / Vercel, release-date ladders KXGPT / KXCLAUDE / KXGEMINI / KXGROK, graphics-card prices, first-score ladders for new models). `aim.py kscan` lists them with sizes.

---

Everything below is printed by `python3 aim.py report`. Prices: Polymarket bets pay the worst price anyone paid in the next 2 hours, never better than the price at the signal, plus 2c and the market's fee. Kalshi bets pay the real asking price of that hour plus Kalshi's fee. $10 a bet, one bet per market. "Tries" for the luck bar: 150 cuts on the leaderboard bets, 260 on the release bets; the Kalshi fresh check counts as a test fixed in advance.

## Polymarket: 3648 leaderboard markets, 163 events, 151821 looks


### all leaderboard markets: 1987 markets with a price and a board


Its name HOLDS the place on the newest board

| time left | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| last day | Yes | - (0) | - (0) | - (1) | - (1) | +$11.89 (12, 12 won) | +$4.39 (21, 21 won) |
| last day | No | - (0) | - (0) | - (1) | - (1) | -$100.00 (13, 0 won) | -$100.00 (23, 0 won) |
| 1-3 days | Yes | - (3) | - (0) | - (6) | - (10) | +$13.54 (21, 21 won) | +$1.02 (31, 30 won) |
| 1-3 days | No | - (1) | - (0) | - (6) | - (10) | -$100.00 (21, 0 won) | -$66.04 (36, 1 won) |
| 3-7 days | Yes | - (9) | - (6) | -$16.82 (13, 5 won) | -$11.77 (23, 15 won) | -$3.69 (37, 31 won) | -$2.92 (41, 38 won) |
| 3-7 days | No | - (7) | - (6) | -$10.70 (13, 8 won) | -$21.64 (23, 8 won) | -$31.57 (37, 6 won) | -$49.32 (45, 3 won) |
| 1-2 weeks | Yes | - (5) | - (9) | +$10.75 (18, 9 won) | +$11.49 (33, 26 won) | -$11.34 (48, 37 won) | -$0.17 (35, 33 won) |
| 1-2 weeks | No | - (4) | - (9) | -$25.77 (18, 9 won) | -$53.60 (33, 7 won) | -$3.02 (48, 11 won) | -$51.64 (38, 2 won) |
| 2+ weeks | Yes | +$16.23 (18, 3 won) | +$10.51 (38, 11 won) | +$14.22 (46, 23 won) | -$8.25 (47, 28 won) | -$8.81 (45, 34 won) | -$0.46 (28, 26 won) |
| 2+ weeks | No | -$7.32 (17, 15 won) | -$17.51 (38, 27 won) | -$32.57 (45, 22 won) | -$15.15 (47, 19 won) | -$8.62 (45, 11 won) | -$49.97 (28, 2 won) |

Its name does NOT hold the place

| time left | side | Yes at 3-10c | Yes at 10-25c | Yes at 25-50c | Yes at 50-75c | Yes at 75-90c | Yes at 90-97c |
|---|---|---|---|---|---|---|---|
| last day | Yes | -$100.00 (15, 0 won) | - (6) | - (0) | - (2) | - (0) | - (0) |
| last day | No | - (11) | - (6) | - (0) | - (2) | - (0) | - (1) |
| 1-3 days | Yes | -$100.00 (25, 0 won) | -$100.00 (13, 0 won) | - (7) | - (4) | - (4) | - (2) |
| 1-3 days | No | +$3.32 (13, 13 won) | - (11) | - (7) | - (4) | - (4) | - (3) |
| 3-7 days | Yes | -$96.33 (41, 1 won) | -$66.13 (27, 2 won) | -$8.92 (14, 5 won) | -$15.20 (12, 7 won) | - (9) | - (6) |
| 3-7 days | No | -$0.17 (30, 29 won) | +$5.62 (27, 25 won) | -$13.03 (14, 9 won) | -$24.38 (12, 5 won) | - (9) | - (8) |
| 1-2 weeks | Yes | -$86.26 (83, 2 won) | -$34.51 (47, 8 won) | -$18.16 (33, 12 won) | -$26.78 (18, 9 won) | -$4.28 (12, 10 won) | - (4) |
| 1-2 weeks | No | +$0.01 (61, 59 won) | -$7.55 (47, 39 won) | -$15.44 (33, 21 won) | +$3.44 (18, 9 won) | -$40.62 (12, 2 won) | - (4) |
| 2+ weeks | Yes | -$60.31 (314, 11 won) | -$54.05 (117, 13 won) | -$39.84 (84, 20 won) | -$38.13 (43, 18 won) | - (11) | - (1) |
| 2+ weeks | No | -$0.01 (224, 217 won) | -$0.90 (109, 97 won) | -$1.72 (76, 57 won) | +$9.15 (43, 25 won) | - (11) | - (1) |

### The boards' own record against the price: 140262 looks at 1869 markets

| time left | looks | miss score, the record | miss score, the price | (lower is better) |
|---|---|---|---|---|
| last day | 2101 | 0.0219 | 0.0022 | price |
| 1-3 days | 4995 | 0.0297 | 0.0056 | price |
| 3-7 days | 10264 | 0.0414 | 0.0167 | price |
| 1-2 weeks | 17322 | 0.0467 | 0.0298 | price |
| 2+ weeks | 105580 | 0.0562 | 0.0450 | price |

| rule | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| Yes where the record is 10c+ above the price | 81 | 30 | +$16.39 | -$44.84 | +$75.31 |
| No where the record is 10c+ below the price | 131 | 96 | +$0.60 | +$6.88 | -$5.54 |
| Yes, 10c+, its name holds the place | 64 | 29 | +$9.41 | -$10.10 | +$28.61 |
| Yes, 10c+, its name does not hold the place | 40 | 4 | -$8.50 | -$100.00 | +$80.26 |
| No, 10c+, its name holds the place | 54 | 20 | -$4.51 | -$0.27 | -$8.69 |
| No, 10c+, its name does not hold the place | 120 | 94 | -$3.41 | -$2.51 | -$4.30 |
| Yes where the record is 20c+ above the price | 69 | 34 | +$56.20 | -$5.36 | +$114.84 |
| No where the record is 20c+ below the price | 110 | 68 | +$4.72 | +$4.07 | +$5.38 |

### The exam

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| Arena leaderboard bets (Polymarket): Yes where the boards' own change record is 10c+ above the price | 81 | 30 | +$16.39 | -$44.84 / +$75.31 | -27.13 to 59.92 | -75.8 | Ahead, but could be luck |
| Arena leaderboard bets (Polymarket): No where the boards' own change record is 10c+ below the price | 131 | 96 | +$0.60 | +$6.88 / -$5.54 | -8.12 to 9.32 | -18.33 | Ahead, but could be luck |
| late holder, 50-90c, last 3 days | 23 | 22 | +$10.37 | +$19.29 / +$2.18 | 1.24 to 19.5 | -18.33 | Ahead, but could be luck |
| Arena leaderboard bets (Polymarket): Yes on the name already holding the place, 50-97c, last 3 days | 39 | 37 | +$4.31 | +$4.58 / +$4.05 | -2.74 to 11.36 | -15.18 | Ahead, but could be luck |
| late holder, 50-97c, last 3 days, 4c extra | 39 | 37 | +$2.29 | +$2.69 / +$1.91 | -4.58 to 9.16 | -16.75 | Ahead, but could be luck |
| late holder, 50-97c, last 3 days, 6c extra | 39 | 37 | +$0.83 | +$1.36 / +$0.33 | -5.87 to 7.53 | -17.81 | Ahead, but could be luck |
| late holder, 50-97c, last 5 days | 52 | 50 | +$11.12 | +$8.43 / +$13.82 | 4.44 to 17.8 | -6.36 | Promising, needs more bets |
| late holder, 50-97c, last 7 days | 64 | 54 | -$2.15 | +$3.06 / -$7.35 | -11.16 to 6.87 | -22.76 | Behind, but could be bad luck |
| holder, 50-97c, days 3 to 7 only | 56 | 46 | -$5.05 | +$0.05 / -$10.15 | -15.46 to 5.36 | -28.71 | Behind, but could be bad luck |
| blind: any name at 50-97c, last 3 days | 46 | 39 | -$7.11 | -$9.25 / -$4.97 | -16.77 to 2.55 | -35.66 | Behind, but could be bad luck |
| a favourite that does NOT hold the place, last 3 days | 10 | 5 | -$47.18 | -$100.00 / +$6.31 | -76.37 to -18.0 | -100.0 | Losing |
| Arena leaderboard bets (Polymarket): Yes on the holder priced 3-50c with 2+ weeks left | 56 | 21 | +$5.60 | +$4.79 / +$6.41 | -35.35 to 46.56 | -80.94 | Ahead, but could be luck |

The 5-day rule by kind of bet (bets, won):
- unit: company 34 / 32, lab 7 / 7, model 11 / 11
- pos: 1 31 / 30, 2 14 / 13, 3 7 / 7
- sub: text 37 / 35, text_style_control 13 / 13, webdev 2 / 2

### Backward look: every time the holder lost inside the last 7 days

- 2026-04-23, 162 hours left, paid 73c: Will Alibaba have the best AI model at the end of April 2026? -> ended ['claude-opus-4-6-thinking', 'claude-opus-4-6', 'claude-opus-4-7-thinking']
- 2026-04-24, 138 hours left, paid 56c: Will Anthropic have the third best AI model at the end of April 2026? -> ended ['claude-opus-4-6-thinking', 'claude-opus-4-6', 'claude-opus-4-7-thinking']
- 2026-05-25, 144 hours left, paid 53c: Will Google have the third best AI model at the end of May 2026? -> ended ['claude-opus-4-6-thinking', 'claude-opus-4-6', 'claude-opus-4-7-thinking']
- 2026-07-25, 168 hours left, paid 69c: Will Moonshot have the best Code Arena | WebDev AI at the end of July 2026? -> ended ['claude-opus-5-max', 'kimi-k3-max', 'claude-opus-5-high']
- 2026-08-25, 166 hours left, paid 51c: Will Moonshot be the third-best Chinese AI company at the end of August 2026? -> ended ['claude-opus-5-max', 'claude-opus-5-high', 'claude-opus-4-6-high']
- 2026-09-01, 168 hours left, paid 65c: Will claude-opus-5-max be the best AI model on September 7, 2026? -> ended ['claude-fable-5.1-max', 'claude-opus-5-high', 'claude-opus-5-max']
- 2026-09-23, 166 hours left, paid 70c: Will OpenAI have the best Code Arena | WebDev AI at the end of September 2026? -> ended ['claude-opus-5.5-max', 'gpt-6-astra-max', 'gpt-6.1-sol-max']
- 2026-09-23, 166 hours left, paid 91c: Will Alibaba have the best Chinese AI model at the end of September 2026? -> ended ['gemini-4-argon-high', 'claude-opus-5.5-high', 'claude-fable-5.1-max']
- 2026-10-24, 166 hours left, paid 77c: Will Meta be the third-best Code Arena | WebDev AI lab at the end of October 2026? -> ended ['Claude Opus 5.5 (Max)', 'GPT-6 Astra (Max)', 'Claude Sonnet 5.5 (xHigh']
- 2026-10-25, 160 hours left, paid 56c: Will Meta be the third-best Math AI lab at the end of October 2026? -> ended ['Gemini 4 Argon (High)', 'Gemini 4 Carbon (High)', 'Claude Fable 5.1 (Max)']

## Kalshi, the fresh check: 1473 settled markets (KXCHINAAI, KXLLM1, KXMATHAI, KXTECHRANKLISTAICODE, KXTOPMODEL), 233653 hourly looks with a real two-sided quote

Bought at the real asking price + Kalshi's fee, $10 a bet, first hour that fits, buy-sell gap at most 15c.

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| Arena leaderboard bets (Kalshi, fresh check): Yes on the name already holding first place, ask 50-97c, last 3 days | 102 | 94 | -$2.29 | -$4.15 / -$0.42 | -6.95 to 2.38 | -8.11 | Behind, but could be bad luck |
| Kalshi: same, last 5 days | 145 | 127 | -$5.06 | +$2.44 / -$12.46 | -9.95 to -0.17 | -10.67 | Losing |
| Kalshi: same, ask 50-90c, last 3 days | 28 | 24 | -$1.10 | -$2.33 / +$0.13 | -13.58 to 11.38 | -31.95 | Behind, but could be bad luck |
| Kalshi: same, last day only | 48 | 46 | +$0.59 | -$2.35 / +$3.52 | -4.33 to 5.5 | -13.61 | Ahead, but could be luck |
| Kalshi: any name at 50-97c, last 3 days | 107 | 99 | -$1.65 | -$3.23 / -$0.09 | -5.89 to 2.59 | -11.79 | Behind, but could be bad luck |
| Kalshi: holder priced 3-50c, last 7 days | 32 | 5 | -$59.20 | -$42.68 / -$75.73 | -89.57 to -28.84 | -100.0 | Losing |
| Kalshi: always Yes, 3-97c, first look | 793 | 156 | -$48.94 | -$58.88 / -$39.02 | -60.64 to -37.24 | -73.69 | Losing |
| Kalshi: always No, Yes at 3-97c, first look | 483 | 323 | +$4.00 | -$8.17 / +$16.12 | -13.95 to 21.95 | -34.27 | Ahead, but could be luck |
| Kalshi: No on a name that does not hold the place, Yes 3-50c, last 3 days | 81 | 77 | -$0.34 | -$3.09 / +$2.34 | -4.48 to 3.79 | -11.01 | Behind, but could be bad luck |

The 3-day rule by Kalshi series (bets, won, dollars): KXCHINAAI 15 / 15 / +12.44, KXLLM1 26 / 25 / -1.51, KXMATHAI 3 / 3 / +1.04, KXTECHRANKLISTAICODE 18 / 17 / -3.07, KXTOPMODEL 40 / 34 / -32.22

Its losses:
- KXLLM1-26FEB07-GOOG, paid 97c, 72 hours left, lead then 27.8 points -> ended ['claude-opus-4-6-thinking', 'gemini-3.1-pro-preview', 'claude-opus-4-6']
- KXTOPMODEL-26FEB07-GEMI, paid 94c, 72 hours left, lead then 17.4 points -> ended ['claude-opus-4-6-thinking', 'gemini-3.1-pro-preview', 'claude-opus-4-6']
- KXTOPMODEL-26FEB21-CLAUT, paid 88c, 72 hours left, lead then 3.7 points -> ended ['claude-opus-4-6', 'claude-opus-4-6-thinking', 'gemini-3.1-pro-preview']
- KXTOPMODEL-26MAR21-CLAU, paid 88c, 72 hours left, lead then 1.5 points -> ended ['claude-opus-4-6-thinking', 'claude-opus-4-6', 'gemini-3.1-pro-preview']
- KXTECHRANKLISTAICODE-26JUL13-CLAU, paid 94c, 72 hours left, lead then 68.4 points -> ended ['gpt-5.6-sol-xhigh (codex', 'claude-fable-5', 'glm-5.2 (max)']
- KXTOPMODEL-26JUL27-CLAUT, paid 95c, 72 hours left, lead then 5.4 points -> ended ['claude-opus-5-max', 'claude-opus-5-high', 'claude-opus-4-6-thinking']
- KXTOPMODEL-26SEP28-CLF51M, paid 75c, 72 hours left, lead then 2.6 points -> ended ['claude-opus-5.5-high', 'claude-fable-5.1-max', 'claude-opus-5-max']
- KXTOPMODEL-26OCT31-GEMI, paid 92c, 72 hours left, lead then 9.6 points -> ended ['Gemini 4 Carbon (High)', 'Gemini 4 Argon (High)', 'Claude Opus 5.5 (High)']

## Polymarket release-day bets: 904 markets in 57 events

| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |
|---|---|---|---|---|---|---|---|
| AI release-day bets (Polymarket): No where Yes is 10-50c after the first third of the market's life | 40 | 35 | +$1.92 | +$1.82 / +$2.02 | -6.89 to 10.74 | -21.01 | Ahead, but could be luck |
| release-day No, same, 4c extra | 40 | 35 | -$0.35 | -$0.54 / -$0.17 | -8.97 to 8.26 | -22.76 | Behind, but could be bad luck |
| release-day No, Yes 3-10c, any time | 102 | 101 | +$2.13 | +$1.22 / +$3.03 | 0.44 to 3.81 | -7.6 | Ahead, but could be luck |
