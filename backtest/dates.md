# "Will it happen before <date>?" ladders on Kalshi (24 Nov 2026, `dates.py`)

Jan: "Go next". The two areas nobody had dug: Starship flight-date ladders and AI model release-date ladders
(KXGPT, KXCLAUDE, KXGEMINI). Both are "date ladders": one question, a row of deadlines ("Before May 1", "Before
June 1", ...), and each rung pays $1 if the thing happens before its date. So the dig took every such ladder on
Kalshi, not just those two.

## The ceiling first (rough guess)

- **Most it could make in an average day:** about $0.30. The one clean pattern (Starship) has about 1.6 bets a month.
  At $25 a bet and +$25 per $100, that's about $10 a month. The wide version (all ladders, ~18 bets a month) would be
  about $1 a day at $25 a bet if it were real, and it isn't (see below).
- **Money needed:** $100-300. Money is stuck for weeks to months, because a "No" only pays at the deadline.
- **Bet size where it stops growing:** about $25-50 a rung. In the 24 hours after a look, the middle rung saw nobody
  else buy No at our price or less; the busy ones saw hundreds of contracts.
- **A bad day:** one surprise early launch or release takes all the No bets on that ladder at once, e.g. 3 rungs
  x $25 = -$75.

## What we did

- `dates.py scan`: all 16,814 Kalshi series, 1,549 with a date-ish title, kept the 120 whose settled answers are
  mostly deadlines and that traded 20,000+ contracts. Biggest: Strait of Hormuz back to normal (40 million contracts),
  DHS funding, Anthropic / SpaceX IPO dates, Starship, FAA ground stop, ChatGPT / Claude / Gemini release dates,
  "X out as ..." ladders, album release dates.
- `dates.py fetch`: 1,291 settled rungs in 209 ladders (2024-2026), hourly real bid/ask for the last 120 days of each
  rung, every trade.
- One look a week at each ladder, counted from the day it opened (never from a close: a rung that closes early is a
  Yes, so counting from closes peeks at the answer). Buy at the real asking price + Kalshi's fee, only when the
  buyer-seller gap is 10c or less. One bet per rung (the first look that fits). Rungs of one ladder count as one bet
  in the luck range.

## What we found

Tables: `backtest/dates_tables.md` (made by `python3 dates.py report`).

1. **Yes loses everywhere, as on the rest of Kalshi.** Long shots worst: Yes at 2-10c lost $49.72 per $100, 10-25c
   lost $40.86. Even Yes at 75-90c lost $13.31.
2. **No at 25-90c looks ahead, but a few ladders carry it.** +$7.87 per $100 on 455 rungs in 137 ladders, both halves
   ahead, exam verdict "Ahead, but could be luck", +$3.50 at 2c more a share. Take away the best 5 ladders (FISA
   extension, Hormuz, DHS funding, Gemini 3.5 Pro, the Avengers trailer) and it is **-$2.04**. And it loses where
   the thing does happen: "someone leaves office" ladders -$25.47. Old ladders (120+ days open) -$12.54.
3. **"It will slip" (No on the nearest deadline only): +$1.06 per $100** on 170 bets, second half -$7.06. Kalshi
   already prices delays.
4. **AI model release dates (KXGPT, KXCLAUDE, KXGEMINI): No at 25-90c +$17.70 per $100** on 54 rungs but only 12
   ladders, luck range -$24 to +$60, "Ahead, but could be luck". Too few launches to tell anything.
5. **Starship flight dates: SpaceX has never been early.** On 10 flights (Flight 7 to 15) and the "Starship from
   Florida" ladder, no rung whose Yes cost 2-50c ever won: No there won 34 of 34, +$24.82 per $100 (+$20.10 at 4c
   more a share). The exam says "Promising, needs more bets", but that luck range treats 10 flights as plenty; they
   aren't. Most of these bets are No at 80-99c (tiny wins); the profit comes from about a dozen No's at 54-66c.
   Found by looking (the band was picked after the first table). About 1.6 bets a month.

## Verdict

Dropped, no track. The wide "No on date ladders" is a handful of lucky ladders. The Starship pattern is real
history but tiny (about $10 a month at $25 a bet) and rests on 10 flights.

**Free re-check (no track, nothing to build):** the next Starship flights (16, 17, ...). Rule written down now: at
each weekly look, No on every Starship rung whose Yes is 2-50c, real ask + fee. If a rung like that ever wins, the
pattern is broken. Run probe `dl_fetch` after a flight, then `python3 dates.py report`.

## Traps

- A rung's close time leaks the answer (Yes rungs close early). Count looks from the ladder's first opening.
- Rung order inside a ladder: use the price (nearer deadline = cheaper Yes), not the close time.
- Some candle quotes come 100 times too small (same trap as `aim.k_load()`); `dates.load()` repairs them.
- "Someone leaves" ladders behave the other way round: people do go, and No loses there.
