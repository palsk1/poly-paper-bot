# What we've learned (the main page)

The one page to read first. Started 2026-11-10. **Every finished dig updates this page in the same PR**: add or
move its line, and change the candidate table if it changed. The "Live numbers" part is rewritten by
`learnings.py` every morning (after the daily run), so don't edit between the AUTO markers.

Deeper detail: every idea tried is in `backtest/ledger.md` (kept by `exam.py`), the test rules in
`backtest/PROTOCOL.md`, every live track in `state/summary.md`.

**What's running right now, and where:** see the top of `CLAUDE.md` ("Running right now"). In short: the paper bot
runs on GitHub; the combo "house" listener runs nonstop on **Jan's own AWS server in Stockholm** (paper, listen only,
since 11 Nov); a **$25 real-money bot** on that server is agreed (Jan, 12 Nov) but not built, and its strategy isn't
picked yet. 12 tracks were stopped on 12 Nov.

## The goal

- Paper money only, until **1 Jan 2027**.
- On 1 Jan, Jan either puts **$300-500 into ONE strategy**, or we say **"keep your money"**.
- A strategy only gets the money if we're about 90% sure it really makes money (Jan's line).
- "Keep your money" is a fine answer. Losing $300 on a lucky-looking fake is not.

## Where we stand (12 Nov, hand-written)

Nothing is proven with live money yet. Of about 85 ideas tried, only 2 "look real" on history, and both still need
live bets. That's normal: most ideas that look good on old data melt away once you pay real prices and fees.

Three candidates can be **settled with live bets** by 1 Jan: `kc_maker_safe` (about 125 bets a day, look about
1 Dec), the combo house on Jan's server (#13: about 180 finished parlays a day so far, so its 1,000-bet look may come around 17 Nov, well before 1 Jan) and `kalshi_patient` (1 Jan). The rest get **one fresh look** on 21 Dec (the "holdout": markets we have kept our eyes off). Passing that look
isn't proof. It just means the idea survived a test it couldn't be tuned for.

**Real-money sizes (10 Nov, `backtest/bigbets.md`):** at $100 a bet, `boring_no` and `crypto_no` cost only pennies
more (deep books, $300-500 fits easily). Soccer draws are too thin for $100 bets (half the games take $12-25).
`kc_maker_safe` can use the money (it turns over every 15 minutes) but earns only about 14-18c per $100 on the real
trade tape.

## The candidates and their check dates

Each one has a pass rule written down before the result. "Locked" means Jan OK'd it and it can't be moved.

| # | Candidate | In plain words | What we have so far | Pass rule | Check date |
|---|---|---|---|---|---|
| 1 | `kc_maker_safe` | Kalshi 15-minute crypto: bid 1c above the best bid on the side that's winning, only when Binance says the coin is far past the line. Hold to the result. One bet costs about $9.89 and pays $10.00 | Backtest: **+$0.56 per $100** on 8,663 bets. Live: see below. Warning: its two siblings lose about twice as often live as in the backtest. **On the real trade tape live is +$0.18 per $100 ($10 bids), +$0.14 at $100 bids** (`bigbets.md`) | After 2,500 live bets, **above +$0.22 per $100**. A strategy worth nothing passes this about 10 times in 100 (locked, PROTOCOL 5b, PR #64) | **about 1 Dec** |
| 2 | Fast Kalshi bot (`kfastlive`) | Same markets, but buy the sure side 45 seconds before the close, or wait at 99.5c / 99.8c | Backtest +$0.40 per $100. Live since 10 Nov | 4 fixed tests, don't change them. Each needs hundreds of bets with no loss (the "proof" column) | first look late Nov, answer by mid Dec |
| 3 | `mention_no` | Buy NO in "Will X say Y" markets that end within 7 days, at 25-90c | Backtest +$4.35 per $100 on 52 events, but anything from -$15 to +$23 is possible. About $0 at worse prices | Ahead, and the low end of its luck range above -$5 per $100 (locked, PROTOCOL 5) | **21 Dec** |
| 4 | Soccer draws | Bet on a draw in a soccer match at 15-50c, a day before kickoff | +$5.60 per $100 on 4,538 bets at prices people really paid. **Thin at real sizes:** only half the games take $25, so about +$3.50 per $100 left where it fits (`bigbets.md`) | Same as #3 (locked, PROTOCOL 5) | **21 Dec** |
| 5 | `panic_fade_10c` | Buy the boring side after a one-day 10c scare | Strict backtest -$3.11 per $100 (live is ahead, most likely luck) | Same as #3 (locked, PROTOCOL 5) | **21 Dec** |
| 6 | Boring No, far out | Buy No at 90-97c more than 30 days before the end (things like "Will Trump meet Putin in August?") | +$5.45 per $100, **100 of 101 won**. Three more losses would wipe it out. Money is stuck for a month+. Live paper track `boring_no` ($500) since 10 Nov. **$100 bets fit** (54 of 56 markets, about 8c extra a bet) | Ahead, and the low end of its luck range above -$5 per $100 (locked, PROTOCOL 5) | **21 Dec** |
| 7 | Crypto "won't get there" | Buy No at 70-90c on "Will Bitcoin reach / dip to $X this week", 3-7 days before the end | +$6.95 per $100 on 115 bets, ahead in all 9 months. Luck range touches $0. Live paper track `crypto_no` ($50) since 10 Nov. **$100 bets fit** (21 of 24 markets, about 30c extra a bet) | Same as #6 (locked, PROTOCOL 5) | **21 Dec** |
| 8 | `arb` | Buy both sides of the same question on Kalshi and Polymarket for less than the $1 payout | $77.62 in, $80.00 back on 1 Jan = +$3.07 per $100. The risk is one pair where the two sites settle differently, not luck | All 4 pairs pay what they should | **1 Jan** |
| 9 | `econ_fav` | Kalshi jobs/inflation markets: buy the 80-99c side when the free forecast agrees | Backtest +$6.73 per $100 on 141 bets (7 lost). Only 1-2 bets per data release, so maybe 10-15 by 1 Jan | **Not registered.** Can't be proven by 1 Jan | none yet |
| 10 | Everything-together model (`combo_moving`) | A math model reads price, price moves, kind of market, rival choices and more together, and bets where it disagrees with the price by 12c+. Only on markets whose price is really moving | Chart +$15.39 per $100; at prices people really paid **+$7.66 on 259 bets**, anything from -$4 to +$20. For 7 in 10 of its bets nobody was selling. The plain price guessed better overall | Frozen 10 Nov. Ahead, and the low end of its luck range above -$5 per $100 (locked, PROTOCOL 5) | **21 Dec** |
| 11 | CS2 favorite a day before (`cs2_fav_day`) | Buy the CS2 team priced 70-97c a day before the match, hold to the result | +$7.60 per $100 on 234 matches at real buys (smaller leagues +$15 on 91). Partly flattered: the matches that could be priced were the better ones. Very thin: about $7 traded near the price in 10 minutes | Ahead, and the low end of its luck range above -$5 per $100 (PROTOCOL 5, registered 11 Nov) | **21 Dec** |
| 12 | Kalshi patient buyer (`kalshi_patient`), **untested** | On Kalshi, where the likely side stands at 90-97c and the asking price is 2c+ above the best buy order, leave a $10 buy order 1c above it for an hour and wait for somebody in a hurry | +$1.42 per $100 on 971 bets in the two samples it was found in, but -$1.99 on 304 bets in a fresh third sample. All three: +$0.61 per $100 on 1,275 bets, luck range -$0.60 to +$1.82. Gone if we pay 1c more, one loss eats 15 wins. The price band was picked after looking. Every other version of the patient buyer lost. Exam: Ahead, but could be luck | Locked 12 Nov, Jan's OK (PROTOCOL 5d): 1,000+ live bets, ahead, low end of the luck range above $0 | **1 Jan** |
| 13 | Combo house (`quoter/`, on Jan's AWS server) | Be the seller of Polymarket parlays: price 2-4 leg combos (no two legs from the same game) at the legs multiplied +5%, and count the bets where that beat the pro who really won. Listen only, never quotes | History +$3.99 per $100 at risk on 1,581 buys. Live paper since 11 Nov: see the live block below. Scoreboard `state/quoter.json`, dashboard card "Combo house" | Locked 11 Nov, Jan's OK (PROTOCOL 5c): above +$1.00 per $100 at risk and both halves ahead | **1 Jan or 1,000 settled bets**; first scorecard Fri 13 Nov 09:00 |
| 14 | Post-count No (`postcount_no`), **untested** | "How many posts will Elon Musk / Trump / the White House make this week" markets: a counting model (count so far + what the same stretch of the week brought in the last 8 weeks) says how likely each count range is. Where Polymarket's Yes is 10c+ above the model, buy No (only when No costs 10c+) | **+$4.16 per $100** on 825 bets over 213 count windows at prices people really paid, exam "Promising, needs more bets". Weaker on the windows opened later (+$1.53) than on the ones it was found on (+$8.14); Elon alone +$1.57; gone if buying costs 3c more than the last trade. Always buying No makes $0, so the model adds something | Live paper track `postcount_no` ($100) since 12 Nov. Proposed bar (PROTOCOL 5e, **not locked**): 150+ bets, ahead, low end of the luck range above -$5 per $100. Too few bets by 1 Jan to prove it | **1 Jan** (first look) |
| 15 | Word-record No (`word_no`), **untested** | "Will Trump say 'Tariff'" markets: keep score of how often each speaker really said each word in earlier markets. Where a word has 3+ earlier markets and Polymarket's Yes trades 20c+ above that record, buy No (No at 10-90c, at least 6 hours before the listed end) | Since April 2026 **+$15.25 per $100** on 533 bets in 244 events, paying the worst price of the next 5 minutes + 3c, exam "Promising, needs more bets". The same rule without word knowledge makes about $0, and blind "always No" (our `mention_no`) stopped paying in April. Weak spots: no untouched test set, 2 of 8 months lost, +$7.74 at +5c and $0 at +8c (thin markets), all profit in markets 12+ hours old. **Harder price check (13 Nov, after the earnings dig):** paying the worst price of the next 2 hours instead of the next 5 minutes, the lead is +$12.16 per $100 at 1c extra and +$5.10 at 3c extra (both halves still ahead), about $0 at the worst price of 4 hours + 3c. So: weaker than first reported, and it lives or dies on how close to the listed price the bot can really buy | Live paper track `word_no` ($100) since 13 Nov (Jan said go). Proposed bar (PROTOCOL 5f, **not locked**): 150+ bets, ahead, low end of the luck range above -$5 per $100. `mention_no` (blind No) runs next to it as the yardstick | **1 Jan** |

<!-- AUTO:START (learnings.py writes this part every morning, don't edit by hand) -->

## Live numbers (updated 2026-11-13)

**49 days left** until the money decision on 1 Jan 2027.
Ideas tried so far: **101**. Dropped: 69. Still in play: 32. Looking real: **2**.

| Candidate | Finished bets | Won / lost | P&L per $100 | What it means | Check |
|---|---|---|---|---|---|
| Kalshi 15-min crypto bids, spot check (`kc_maker_safe`) | 469 | 466 / 3 | +$0.45 | Ahead, but could be luck | 1 Dec (18 days): after 2,500 bets: pass if above +$0.22 per $100 |
| NO on 'will X say Y' (`mention_no`) | 4 | 3 / 1 | +$3.70 | Too early to tell (4 finished) | 21 Dec (38 days): holdout, scored once |
| Boring side after a 10c scare (`panic_fade_10c`) | 4 | 3 / 1 | +$4.32 | Too early to tell (4 finished) | 21 Dec (38 days): holdout, scored once |
| NO at 90-97c, 30+ days out (`boring_no`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | 21 Dec (38 days): holdout, scored once |
| NO on crypto price, 70-90c, 3-7 days out (`crypto_no`) | 2 | 0 / 2 | -$100.00 | Too early to tell (2 finished) | 21 Dec (38 days): holdout, scored once |
| Economy favorites the forecast backs (`econ_fav`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | no date: not registered yet |
| Kalshi patient buyer, nearly-sure side (untested) (`kalshi_patient`) | 27 | 25 / 2 | -$1.87 | Behind, but could be bad luck | 1 Jan (49 days): 1,000+ bets, ahead, low end of the luck range above $0 |
| NO on post counts the counter says are overpriced (untested) (`postcount_no`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | 1 Jan (49 days): 150+ bets, ahead, low end of the luck range above -$5 per $100 (proposed, not locked) |
| NO on mention words priced far above the word's own record (untested) (`word_no`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | 1 Jan (49 days): 150+ bets, ahead, low end of the luck range above -$5 per $100 (proposed, not locked) |
| Same question on Kalshi and Polymarket (`arb`) | 0 | - | +$4.49 locked in | 24 sets cost $114.84 and pay $120.00 if both sites agree. Nothing to judge before then. | 1 Jan (49 days): pays out on 1 Jan |

**kc_maker_safe toward its locked test:** 475 of 2,500 bets, 3 lost, +$21.32 so far (+$0.45 per $100; the bar is +$0.22). About 131 bets a day, so the look is due about 29 Nov. This is only a peek: the number counts once, at 2,500.
**Fast Kalshi bot, last 45 seconds** (main test "Wait at 99.8c, 45 s left (z 2+) (main)", 10 contracts): 298 bought, 4 lost, -$11.08 (-$0.38 per $100). Full table: `state/kfast_live/report.md`.
**Combo house on Jan's AWS server (Stockholm)**, paper, rule `main`: 365 parlays finished, the house won 296, +$4.17 per $100 at risk (Ahead, but could be luck), 29 still waiting. Only a peek: it counts once, at 1 Jan or 1,000 finished parlays. `state/quoter.json`.

### Week by week (numbers as of the last day of each week, all bets so far)

| Week | `kc_maker_safe` | `mention_no` | `panic_fade_10c` | `boring_no` | `crypto_no` | `econ_fav` | `kalshi_patient` | `postcount_no` | `word_no` |
|---|---|---|---|---|---|---|---|---|---|
| 2026-W46 | 469 bets, +$0.45 | 4 bets, +$3.70 | 4 bets, +$4.32 | 0 bets | 2 bets, -$100.00 | 0 bets | 27 bets, -$1.87 | 0 bets | 0 bets |

Too few bets means luck. A row only matters once a track has 30+ finished bets.

<!-- AUTO:END -->

## The 1 Jan decision checklist (draft, Jan to OK)

A strategy gets real money only if **every** answer is yes:

1. **It passed its locked test** (the rule written before the result, above).
2. **Live paper bets agree** with the backtest. Not losing live, not losing much more often than the backtest said.
3. **Bigger bets still fit.** Real orders of $25-100 would fill at about the same price (the "real size" numbers).
   Checked 10 Nov (`bigbets.py`): yes for boring_no, crypto_no and kc_maker_safe; no for soccer draws and mention_no
   at $100 (fine at about $25). Re-run `big_all` once more before 1 Jan.
4. **The exam's worst case is above $0**, counting every idea we ever tried (luck gets a bigger head start the more we try).
5. **Jan may legally use that site from Sweden** (Kalshi especially). Jan checks this himself.
6. **A stop rule is set before the first dollar**, for example "if $300 turns into $250, stop and look".

- If nothing passes: **keep your money** (or keep paper testing into 2027).
- If two pass: pick the one with the better worst case, not the bigger profit.
- Start with the low end ($300). Add more only after a month of real results that match the paper.

## Calendar

| Date | What happens |
|---|---|
| 13 Nov | **Combo house first scorecard** (09:00 Stockholm), then the $25 real-bot strategy pick with Jan |
| 23 Nov | Gas-price recorder scored (who reads AAA first). Expected dead |
| late Nov | Fast Kalshi bot first look |
| about 1 Dec | **kc_maker_safe locked test** (2,500 bets). Order book shapes recheck |
| 21 Dec | **Holdout, scored once**: mention_no, soccer draws, panic_fade_10c, boring No far out, crypto No, the everything-together model, CS2 favorite a day before |
| 1 Jan 2027 | arb pays out. `kalshi_patient` and combo house locked tests (combo house earlier if it reaches 1,000 bets). **Money decision** |
| late Jan | Next GDP release (GDPNow vs Kalshi, only 19 past releases, too few to judge) |

## Big lessons so far

- **A chart price isn't always a price you can buy at.** Dead Polymarket markets sit near 50c with nobody selling. A smart model finds those first and looks like a genius (+$21 per $100) until you check real trades (10 Nov).
- **Old-data wins mostly vanish at real prices.** One extra cent plus the fee kills most "edges". Brand-new
  Polymarket markets even open with fake 1c/99c books, so the listed price lies.
- **Yes buyers pay for the thrill.** On Polymarket, buying Yes lost about $8 per $100; buying No got about your money
  back. The boring side is fair, not a gift.
- **Copying wallets doesn't work for us.** The price moves within 5 minutes of a smart bet. We arrive later and get
  nothing. "Winning wallets" are mostly luck: 32 of every 1,000 look good, and luck alone gives 28.
- **"Sure" bets hide a big loss.** At 99c, one loss eats about 100 wins. You need hundreds of bets to know.
- **Check the data for holes.** Our first data dropped losing choices in weather events, which made one idea look
  like +$121 per $100. On full data it lost $18.67.
- **Check the clock too (10 Nov).** Our recorder read Kalshi first and Polymarket about 20 seconds later. Compared as-is, that looked like +$4 per $100 of free money. Lined up to the same second it was gone. Recorded books now save the real second (`rt`).
- **A lean can stop paying (13 Nov).** Blind No in mention markets made money for seven quarters in a row, then nothing from April 2026 on. Always cut a result by quarter before trusting the total.
- **In thin markets the next trade is not your price (13 Nov).** In the earnings markets a "price drop" is often one sale to a waiting buyer, and the next trade may be another one. You can't buy there. Pricing a buy at the next 5-minute step made a dead idea look like +$18 per $100; the worst price of the next 2 hours said +$6, and 2c more said $0 (`earn.buy`).
- **We are slow (a run every 5 minutes).** Anything that needs speed belongs to the pros. Our edges must last hours.
- **A server would buy us nothing we can measure (11 Nov, `kspeed.py`).** The free GitHub machine reaches Kalshi in
  about 70 thousandths of a second, about what a cheap server gets. When Binance jumps, Kalshi's price moves in the
  same 1-3 seconds, so buying the jump lost about $5 per $100 whether we were under 1 second late or 30. The
  45-seconds-left buy made the same at 1, 2, 3 and 5 seconds late (+$0.64 to +$0.88 per $100) and only faded at 10.
  To be first you'd have to beat the paid pros by fractions of a second. Not our game. No server.
- **Downloads are slow because of the number of requests, not the size (10 Nov).** All our old prices together are
  only about 200 MB packed. The weather dig asked Kalshi for 31,446 price charts, about 2 a second, so 4 hours for
  just 5 MB. Until now each thread's download stayed on its own branch and was lost after 7 unused days, so sports
  prices were fetched twice. Now every data run saves to one shared store (`store.py`), so nothing is fetched twice.
- **Bet size is not the problem for most leads (10 Nov).** Polymarket's No books at 70-97c are deep: a $100 bet costs
  8-30c more than a $5 one. The problem is whether the lead is real, not whether it fits. Exception: soccer draws and
  mention markets, where half the books hold only $12-50.
- **Paper maker bids can look too good (10 Nov).** The bot counts a Kalshi bid as fully filled once one contract
  trades below it. On the real tape the losers fill fully and the winners only partly: `kc_maker_early` is really
  -$12 per $100, not the -$4.50 it showed. Fixed 10 Nov: the bot now counts only what was really sold.
- **Polymarket maker tracks hid their losses (11 Nov, Jan spotted it).** Money from early sales and from pairs turned
  back into $1 was counted, but never shown as finished bets, so the dashboard said "0 won / 0 lost, too early" while
  `maker_tpsl` had lost $104 of $200 and `maker_flat` $100. The cash was right; the scoreboard wasn't. Fixed: every
  sale and pair is now a finished bet. Lesson: the stop loss sells right after a fill, into a book that was just
  emptied, often 10-28c below what it paid. The maker idea stays dead.
- **Polymarket maker tracks stopped (12 Nov, Jan: "Dump them").** All five lost $416 of $1,000 in 3-4 days and earned
  $7.39 in rewards. `maker_flat` sold 42 times right after a fill and never once above cost (the price was about 4c
  lower by the next check): a bot that looks every 5 minutes only gets filled by people with fresher news. Open bets
  were closed once at the real bid; the numbers stay on the scoreboard, frozen. Review:
  `/mnt/project-files/research/maker-review-2026-11-12.md`.
- **On Kalshi, waiting for sellers mostly means being picked off (12 Nov, `khouse.py`).** We thought the patient
  side of a trade earns the gap. On 3.2 million real trades it doesn't: a buy order 1c above the best one lost about
  $5 per $100 at 50-90c and $5 to $13 during live games, where the seller has just seen the last play. Only the
  nearly-sure side (90-97c) came out a little ahead. And a trap: busy markets only keep their newest 2,000 trades,
  and which markets are "busy" depends on the result, so half-saved trade lists flatter whoever was right.
- **More ideas tried means a higher bar.** With 49 ideas, the luckiest one is bound to look good. The exam raises the
  bar for every new try.

## The 12 stopped tracks (12 Nov): what they taught us

Jan stopped these on 12 Nov and took them off the dashboard the same evening. They still sit in `state/summary.md`,
and open bets finish there. Numbers are from the evening of 12 Nov, P&L counting open bets at today's price.

| Track | Final P&L | Finished bets (won / lost) | What we learned |
|---|---|---|---|
| `fade_sure` (weather long shots at 2-10c) | +$7.88 on $25 | 55 (4 / 51) | One lucky day (12 Nov: 5 long shots in one go) turned it from -$7 to +$8. 13,000 past bets lost $18.67 per $100, lucky days included. **Bets on the same day's weather are one bet, not thirty.** |
| `wx_forecast` (free forecasts vs temperature buckets) | -$24.48 | 130 (58 / 72) | The markets know the weather better than free forecasts. Live agreed with the history test, only worse |
| `endgame_ending_soon` (93-98c, ends within a day) | -$48.87 | 114 (101 / 13) | Winning 9 times in 10 still loses when one loss costs 20 wins. Crypto "dip to", tweet counts and TV-show markets flip late |
| `endgame_97` (97-99c, every signal) | -$32.06 | 122 (115 / 7) | At 99c one loss eats about 100 wins. It also bought "past the deadline" bets before the day was over (the end-time bug, fixed 12 Nov) |
| `ladder` (two linked markets for under $1) | $0 | 0 | 6,458 pairs watched, never one cheap enough. Pros close these gaps before a 5-minute bot looks |
| `every_horse` (every answer for under $1) | +$0.54 expected | 0 (3 sets open) | 3 sets in 9 days. It would need about 69 to prove anything |
| `kc_maker_early` (Kalshi crypto bids 90c+, early) | -$70.36 | 355 (329 / 26) | Bidding early catches the windows that later flip. The kc_maker_safe spot check is what keeps the safe twin alive |
| 5 Polymarket maker tracks | -$421 of $1,000 | 117 | Rewards paid about $8 in total. A 5-minute bot gets picked off: people sell to us just before the price drops |

The two lessons for the rest: **a strategy that wins small often and loses big rarely needs hundreds of bets before
its total means anything**, and **a day of correlated wins is luck, however good it looks on the phone**.

## Tried and dropped (one line each)

Don't re-test these the same way. Only with something new (new data, a new filter).

- **Endgame, 95c+ a day before the end:** lost about $5.50 per $100 (weather, crypto and tweet-count buckets flip).
- **Endgame, 95c+ after the deadline but before a result:** lost $167 on 709 bets.
- **Favorites by rule** (screener, price bands, NO only, momentum, fade the rally): lost even with free trading.
- **The `claude` track's rules, and 4 simple fixes** (11 Nov, `claudefix.py`, `backtest/claudefix.md`): live rules lost $8.30 per $100 on 364 past bets at real costs. No 70c sell, no 97c sale, hold to the end, or 30-60 days only all lost too ($8 to $10 per $100), and random bets in the same price band did as well or better. Jan then made `claude` Claude's sandbox (change it often, log every change in `backtest/claude_changes.md`). Change 1, same day: No at 90-97c, 30-60 days, random pick, held to the end (history -$3.99 per $100, half the old loss, still losing; `backtest/claudefix_r2.md`).
- **Buy every answer of an event for under $1:** never once cheap on the real book.
- **Cheap side of "sure" weather buckets:** -$18.67 per $100 on full data (the +$121 was a data hole).
- **Crypto price model 3-30 hours out:** the markets are priced like the model.
- **Weather buckets already decided:** sit at 99.95c, nothing left.
- **Betting free weather forecasts against temperature markets (10 Nov, PR #71):** Kalshi lost $11-15 per $100 on about 17,600 bets; Polymarket lost $2-4 (and $9 at +5c). The prices know the temperature better than GFS/ECMWF/NOAA do. One shaky lead: Polymarket daily lows, +$6 to +$11, but only Sep-Nov when new cities opened. Look again on the late-December test days.
- **Same question listed twice on Polymarket:** no gaps.
- **Kalshi vs Polymarket game winners:** a pair costs about $1.04 to win $1.
- **Kalshi vs Polymarket 15-min crypto (buy UP on one site, DOWN on the other):** a pair costs about $1.05 and pays $1.00. Live, both sites read in the same second for 2 hours: 46 real gaps, worth +$1.89 in total on $10 bets, half gone within 2 seconds. And the two sites disagree on the result 17 times in 1,000 (`backtest/xvenue.md`).
- **Rejected arb pairs, one way only:** gaps only on the unsafe side.
- **Sell a full set for more than $1:** -0.05c a share at best.
- **Holding rewards:** real, but $3.25 a year per $100.
- **Quote both sides for maker rewards:** rewards 1-38c a day per $100, price moves cost far more.
- **Odd kinds of markets** (weekend, quiet, tiny, long-dated, long shots): all lose about the costs.
- **Read the settle source first** (gas, earthquakes, executive orders): -$34 to -$80 on gas.
- **Free Fed forecasts vs Kalshi economy markets:** -$4 to +$3, Kalshi knows better.
- **Ugly rule wording and disputes:** predicts disputes, but prices are already fair (-$18).
- **Idea machine, 34,000 pattern ideas:** 1 survivor (`quiet_no`), about break-even.
- **Calendar effects, "choices add up to":** 10,000 versions, 0 survivors.
- **Copy wallets that buy before the price moves:** -$4.40, the move is over in 5 minutes.
- **Learn from wallets that win:** winners don't repeat, first-half stars lost $5 per $100 later.
- **Live esports scores:** the free feed is about 100 seconds behind the price.
- **Markets that contradict each other:** no set ever under $1.
- **Sharp bookmaker (Pinnacle) price vs Polymarket sports:** Polymarket follows within 0.5c, no edge.
- **Brand-new markets:** -$0.25 to +$4 at real prices, noise.
- **Order book shapes:** about 1c, less than costs.
- **Poll averages vs approval markets:** -$6 to -$46 on Kalshi.
- **Sports totals and spreads long shots:** gone at real prices.
- **Daily stock and commodity "Up or Down", cheap side:** -$3.50.
- **$1 on Yes (or No) in every open market every day (10 Nov, `yesno.py`, just for fun):** Polymarket all Yes -$11 to -$18 per $100, all No -$6 to -$8; Kalshi at the real ask all Yes -$25, all No -$20. At the dream price both are near fair, so the loss is the cost of buying, worst on long shots. No new candidate.
- **Criss-cross of those bets (10 Nov, `yesno.py grid`):** 1,055 cuts by Yes/No, price, kind of market, time left and weekday. 124 ahead in both halves, 667 behind in both. The survivors are the two leads we already track (nearly sure things 30+ days out = `boring_no`; crypto No 3-7 days out = `crypto_no`), and they shrink at real buys. No weekday pattern. Kalshi: nothing. No new candidate.
- **One math model that looks at everything together (10 Nov, `combo.py`):** learned on markets ending before 10 Aug, judged on 10 Aug - 9 Nov. Chart says +$15 to +$22 per $100; at real buys +$0 to +$8, could be luck. It mostly found ghost prices (dead markets near 50c that nobody sells at). The plain price guessed better than the model overall. Fair version (moving prices only): +$7.66 on 259 real buys, luck range -$4 to +$20. Frozen and registered for the 21 Dec look (`combo_moving`, Jan's OK).
- **Polymarket Combos / parlays, as a buyer (11 Nov, `combos.py`):** 3,897 real combo buys vs the same legs bought one by one. A buyer pays about $100 for legs worth $86.61 (maker $10.33, fee $3.05); 5+ legs or long shots lose about $21-22 per $100. Buying combos: dropped. The house side is a lead, see open questions. `backtest/combos.md`.
- **Kalshi 15-minute crypto, every minute of the window and every speed (11 Nov, `kspeed.py`):** 39,006 rounds. Buying either side at the asking price loses $4 to $6 per $100 in every stretch (fee plus the buy/sell gap); at the middle price it's even, so the price is fair. A rule that buys when Binance says "too cheap" lost $4.75. After big Binance moves Kalshi even gives back about 1c the next minute, too little to trade. One small lean: a side already at 95c+ with 8+ minutes left made +$0.72 per $100 on 4,406 bets, also when bought a minute late: "Ahead, but could be luck", same family as `kc_maker_safe`, no track. `backtest/kspeed.md`.
- **CS2 rankings and bo3.gg's AI vs Polymarket (11 Nov, `cs2.py`, Jan's ask):** 6,495 CS2 matches. Backing the team Valve's ranking or our own rating likes when the price disagrees lost $12-17 per $100 at real buys; the price predicts better than both rankings. bo3.gg's AI picks the winner 61 times in 100, the plain favorite 66: backing every AI pick lost $4.18 per $100 at real buys (4,533 matches), and betting more when it predicts a 2-0 or sizing by price doesn't help. bo3.gg's bookmaker odds are after-the-game odds, unusable. HLTV blocks robots. One thin lean (favorite a day before) goes to the 21 Dec look. `backtest/cs2.md`. **Upsets (same day, Jan: "find the red thread"):** what losing favorites share. Roster changes, slumps, win streaks, tiredness, rust and best-of-1 are all already in the price (expected vs real upsets within 1-3 per 100); the 5 best patterns fail at real buys (best: underdog vs a favorite on 5 wins, +$5.17 per $100 on 201, flips between halves). In-fighting has no data. Dropped. **Players' recent form (same day, Jan asked):** bo3.gg player ratings for 10,367 matches; backing the team whose players are hotter than usual over the last 2-7 days lost $4-8 per $100 even at chart prices. Priced in. Dropped.
- **Kalshi patient buyer, everything except the nearly-sure side (12 Nov, `khouse.py`):** 19,385 settled Kalshi markets, 3.2 million real trades, our order filled only by contracts really sold. A buy order 1c above the best one: likely side at 50-90c -$5.35 per $100 (2,050 bets); during a live game -$5 to -$13; the unlikely side worse still. Lowball orders on the likely side: -$3 to -$19. Wide gaps (5c+) before a game looked great, +$7.97 on 266 bets, and fell to -$3.28 on 560 new games: luck. In-play "favourites are too cheap" was a data trap (cut trade lists), don't chase it. Very low buy orders on the underdog before a game: +$25.90 on 469 bets where found, -$8.51 on 318 new games (rule fixed before the download): luck. The 90-97c version lives on as `kalshi_patient`. `backtest/khouse.md`.
- **The pros' options prices as the fair price for Polymarket's Bitcoin and Ethereum markets (12 Nov, `optfair.py`): dropped.** 14,077 finished markets ("above $X on a date", "between", "reach / dip to $X"), a fair price for each from Deribit's swing index (DVOL) and Binance's price to the minute, and every real Polymarket trade in 5-minute steps. The two forecast equally well (a dead tie on 8,300 markets). Buying the cheap side where they are 5c+ apart, at the next real trade + 1c + the fee: end-price markets -$3.23 per $100 (3,122 bets), reach/dip +$1.80 (2,464 bets, "Ahead, but could be luck", halves disagree). One lead from the first 3,000 markets (reach/dip in the last hours, +$17.73 on 129 bets) was fixed as a rule and then lost on the 11,077 fresh ones (-$8.90, 433 bets). Making the swings bigger or smaller, only small gaps, only one side: nothing holds. Trap found on the way: the hourly chart shows a made-up 50c for new markets, and at chart prices this looked like +$25 to +$36 per $100. Crypto markets also carry the biggest fee (about 1.75c a share at 50c). Report `backtest/optfair.md`. Don't redo.
- **Counting model for post-count markets, every version but one (12 Nov, `tweets.py`):** 216 finished count windows (Elon Musk 152, Trump 36, White House 23), 3,267 markets, post times from Polymarket's own counter. Polymarket forecasts better than the model, most of all in the last day when people watch the account live. Betting both sides where they are 5c+ apart: -$0.89 per $100 (1,457 bets). Buying Yes where the model says it's 10c+ too cheap: -$4.08 (665 bets). Always buying No: -$0.25; always Yes: -$12.13. Trap: half of one version's profit was a single No bought at 2c, so lottery-ticket prices are out. The survivor (buy No where Yes is 10c+ too dear) is candidate #14 above. Report `backtest/tweets.md`.
- **Mention markets, the blind and the Yes versions (13 Nov, `mentions.py`):** 24,228 finished "will X say Y" markets in 1,356 events back to June 2024, 20,488 with every real trade. Polymarket's price forecasts better than a word's own record. Blind "always No" made $10-30 per $100 every quarter until March 2026, then about $0 (-$1.27 per $100 on 7,669 bets since April, when fees started on these markets): the old `mention_no` lean has faded. Buying Yes where the word's record is above the price: -$10.79 per $100. Bets within 6 hours of the listed end lose (the speech is on). The survivor (No where Yes is 20c+ above the word's record) is candidate #15 above. Report `backtest/mentions.md`.
- **Earnings markets, "will company X beat its forecast" (13 Nov, `earn.py`, `backtest/earn.md`):** 1,521 finished markets on 407 companies since September 2025, every real trade. Yes won 73 in 100 and the price knows it: fair in every price band. A company's own record of beating or missing is in the price; official vs adjusted profit, loss-making companies, cheap Yes: nothing that holds. Following a late 8c+ price jump lost $21 per $100. Betting against the jump looked like +$15 to +$18 per $100 when priced at the next trade, +$6.03 at the worst price of the next 2 hours ("Ahead, but could be luck"), $0 at 2c more, and it has lost since April. The "jump" is mostly one impatient trader paying the gap between buyers and sellers. Dropped, no track.
- **Weekend box office markets (13 Nov, `boxoffice.py`, `backtest/boxoffice.md`):** 998 finished "how much will movie X make this weekend" markets in 208 events, every real trade, plus the daily ticket sales of every movie from Box Office Mojo. A simple forecast from the public ticket numbers misses the weekend total by about 20 in 100 before the weekend and 10 in 100 even with Friday's number in hand, and the brackets are only about 10 in 100 wide, so it can't pick one. The price itself is fair. Cheap brackets (Yes under 25c) lost $48 per $100. Betting against a late jump lost $34 per $100: here a jump is real news (a ticket number came out), not a trader paying the gap. Brackets at 65c+ before the weekend were +$14.77 per $100, but on 34 bets: "Ahead, but could be luck". Dropped, no track.
- **Sweep of repeating market families (13 Nov, `families.py`, table in `backtest/boxoffice.md`):** looked for families that come back every week, trade real money and settle on a public number. Spotify, Netflix, Billboard and awards markets mostly never trade. Airdrop and token-value markets trade big money but each one is a one-off. Still untested: YouTube view counts (mostly MrBeast videos, about $2,400 traded per market, no saved history of view counts) and Rotten Tomatoes scores (93 events).

- **Review of the worst Polymarket rule tracks (12 Nov, `backtest/review_worst_poly.md`, Jan's ask):** live bets now agree with the history tests. `fade_sure` (2 won, 44 lost, -$77.84 per $100), `wx_forecast` (-$11.09 on 114), `endgame_ending_soon` (-$3.97 on 101) and `endgame_97` (-$3.33 on 112) were stopped on Jan's "Dump" the same day, with `ladder` and `every_horse` (no new bets, open ones settle). `endgame_sell98` is the one endgame variant still ahead (+$0.21 on 188, could be luck). Bug found: `bot.py` reads the end date without the time, so markets 'end' at 00:00 UTC; 133 of 161 lab 'past the deadline' buys were on the end day itself. Fixed the same day (Jan's OK): the bot now reads the full end time.
- **What "worst case per $100" means (12 Nov, Jan asked):** it is a proof bar on finished bets (one made-up total loss added, bar raised because we run ~130 tracks), not "what if every open bet loses". 90 of 130 tracks sit at the -$100 floor, mostly from too few or very swingy bets. Losses now get a luck check too: new verdict "Behind, but could be bad luck" (8 tracks today, e.g. `wx_forecast`, `kc_maker_early`, `endgame_sell98`). The dumped `fade_sure`, `endgame_ending_soon`, `endgame_97` and 4 of 5 maker tracks are still "Losing" with the check, and the history tests back the other dumps.

Still running on purpose, though the idea looks dead: the endgame lab variants `endgame_strict` and `endgame_sell98`,
`sharp_pinnacle`, `quiet_no` (Jan's pick), the 80 wallet copies. They show the drop was right.
- **`kc_maker_early`, Kalshi 15-minute crypto bids at 90c+ with 6.5-11.5 minutes left (stopped 12 Nov, Jan: "dump it"):** lost $79.62 on 341 live bets (-$2.45 per $100). The backtest said +$0.61 to +$1.43; live luck range -$5.82 to +$0.92, so it's broken, not unlucky. The 90-91c bids lost $72 of it: with 8+ minutes left, whoever sells into your bid often sees the coin turning. No new bids; history kept.
- **Why `kc_maker_safe` lost 3 of 362 bets (12 Nov, `kcrypto.py losses / basis / gapcheck`, Jan's ask):** normal, not a bug: one loss eats about 90 wins and it loses 1 in 120 live (1 in 160 in history). The fills were real. Shared pattern: Binance (USDT) runs about 0.09% above the dollar price Kalshi pays on, so on "yes" bets the cushion looks bigger than it is; on Kalshi's scale all 3 losses were under the 2-move bar. Skipping those (history, 60 days): losses 54 to 20, worst day -$22 to -$11, +$0.57 to +$0.54 per $100, 25 in 100 fewer bets, about $2.40 a day less in total. The locked rule stays; Jan said yes to a twin, `kc_maker_safe_usd`, live since 12 Nov. `backtest/kcloss.md`.
- **The `kc_maker_safe` bid on Polymarket's 15-minute crypto windows (12 Nov, `kcrypto.py pmrun`, Jan's ask): dropped.** 31 days, every real trade of the last 8 minutes of about 18,500 windows: -$1.43 per $100 with 3 minutes left (363 bets, 13 lost), about even at 2 and 4 minutes; "Behind, but could be bad luck". It loses 1 bet in 28 there against 1 in 187 on Kalshi the same days, and makes about 12 bets a day against 130. The price-gap fix doesn't rescue it. No track. `backtest/pm15.md`.

## Open questions for Jan

- **$25 real-money bot (12 Nov):** Jan said yes to a small real bot on his AWS server with his own key (the key stays
  on the server, never in the repo or chat). Which strategy? Waiting for the combo house scorecard on 13 Nov. Run it
  side by side with its paper twin, so we see if real fills match paper.
- **Be the house on Polymarket combos? (11 Nov, now candidate #13, `combos.py replay`, "Promising, needs more bets")** On 4,945 combo buys by ordinary buyers, the pros kept $31 per $100. Selling 2-4 leg combos (no legs from the same game) at the legs' price +5%, only when that beats the pros' price: +$3.99 per $100 at risk on 1,581 buys, luck range +$0.68 to +$7.29, both halves ahead. Long shots lose for us. Jan said go (11 Nov): a listen-only paper quoter (`quoter/`) runs on Jan's own server (AWS Lightsail Stockholm, the free plan allows only that region) with a fresh empty wallet, since 11 Nov 12:17 UTC. Listen-only quoters DO get the requests and trade prices, and every 30 s Polymarket reports ~2,500-2,900 requests nobody quoted. Pass rule fixed with Jan's OK (PROTOCOL.md 5c): above +$1.00 per $100 at risk and both halves ahead, at 1 Jan or 1,000 settled bets. Score: probe `cmb_qscore`.

1. **OK the 1 Jan checklist above?** Then it gets locked like the other rules.
2. ~~**Merge the open research PRs** (#66)~~ **Merged 10 Nov.**
3. ~~**every_horse and ladder**: keep, or stop?~~ **Stopped 12 Nov (Jan: "Dump").**
4. **Kalshi from Sweden:** the top candidate is a Kalshi strategy. Worth checking early.
5. ~~Kalshi paper fills are a bit too kind~~ **Fixed 10 Nov (Jan said "Fix it").** The bot now counts only contracts
   really sold to the bids. kc_maker_safe's locked test re-scores all its bets the fixed way on 1 Dec (PROTOCOL 5b).
