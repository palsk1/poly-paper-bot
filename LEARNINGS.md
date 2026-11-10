# What we've learned (the main page)

The one page to read first. Started 2026-11-10. **Every finished dig updates this page in the same PR**: add or
move its line, and change the candidate table if it changed. The "Live numbers" part is rewritten by
`learnings.py` every morning (after the daily run), so don't edit between the AUTO markers.

Deeper detail: every idea tried is in `backtest/ledger.md` (kept by `exam.py`), the test rules in
`backtest/PROTOCOL.md`, every live track in `state/summary.md`.

## The goal

- Paper money only, until **1 Jan 2027**.
- On 1 Jan, Jan either puts **$300-500 into ONE strategy**, or we say **"keep your money"**.
- A strategy only gets the money if we're about 90% sure it really makes money (Jan's line).
- "Keep your money" is a fine answer. Losing $300 on a lucky-looking fake is not.

## Where we stand (10 Nov, hand-written)

Nothing is proven yet. Of about 49 ideas tried, **0 look real**. That's normal: most ideas that look good on old
data melt away once you pay real prices and fees.

Only one candidate can be **proven with live bets** by 1 Jan: `kc_maker_safe`, because it makes about 100 bets a
day. The rest get **one fresh look** on 21 Dec (the "holdout": markets we have kept our eyes off). Passing that look
isn't proof. It just means the idea survived a test it couldn't be tuned for.

## The candidates and their check dates

Each one has a pass rule written down before the result. "Locked" means Jan OK'd it and it can't be moved.

| # | Candidate | In plain words | What we have so far | Pass rule | Check date |
|---|---|---|---|---|---|
| 1 | `kc_maker_safe` | Kalshi 15-minute crypto: bid 1c above the best bid on the side that's winning, only when Binance says the coin is far past the line. Hold to the result. One bet costs about $9.89 and pays $10.00 | Backtest: **+$0.56 per $100** on 8,663 bets. Live: see below. Warning: its two siblings lose about twice as often live as in the backtest | After 2,500 live bets, **above +$0.22 per $100**. A strategy worth nothing passes this about 10 times in 100 (locked, PROTOCOL 5b, PR #64) | **about 1 Dec** |
| 2 | Fast Kalshi bot (`kfastlive`) | Same markets, but buy the sure side 45 seconds before the close, or wait at 99.5c / 99.8c | Backtest +$0.40 per $100. Live since 10 Nov | 4 fixed tests, don't change them. Each needs hundreds of bets with no loss (the "proof" column) | first look late Nov, answer by mid Dec |
| 3 | `mention_no` | Buy NO in "Will X say Y" markets that end within 7 days, at 25-90c | Backtest +$4.35 per $100 on 52 events, but anything from -$15 to +$23 is possible. About $0 at worse prices | Ahead, and the low end of its luck range above -$5 per $100 (locked, PROTOCOL 5) | **21 Dec** |
| 4 | Soccer draws | Bet on a draw in a soccer match at 15-50c, a day before kickoff | +$5.60 per $100 on 4,538 bets at prices people really paid | Same as #3 (locked, PROTOCOL 5) | **21 Dec** |
| 5 | `panic_fade_10c` | Buy the boring side after a one-day 10c scare | Strict backtest -$3.11 per $100 (live is ahead, most likely luck) | Same as #3 (locked, PROTOCOL 5) | **21 Dec** |
| 6 | Boring No, far out | Buy No at 90-97c more than 30 days before the end (things like "Will Trump meet Putin in August?") | +$5.45 per $100, **100 of 101 won**. Three more losses would wipe it out. Money is stuck for a month+. Live paper track `boring_no` ($500) since 10 Nov | Ahead, and the low end of its luck range above -$5 per $100 (locked, PROTOCOL 5) | **21 Dec** |
| 7 | Crypto "won't get there" | Buy No at 70-90c on "Will Bitcoin reach / dip to $X this week", 3-7 days before the end | +$6.95 per $100 on 115 bets, ahead in all 9 months. Luck range touches $0. Live paper track `crypto_no` ($50) since 10 Nov | Same as #6 (locked, PROTOCOL 5) | **21 Dec** |
| 8 | `arb` | Buy both sides of the same question on Kalshi and Polymarket for less than the $1 payout | $77.62 in, $80.00 back on 1 Jan = +$3.07 per $100. The risk is one pair where the two sites settle differently, not luck | All 4 pairs pay what they should | **1 Jan** |
| 9 | `econ_fav` | Kalshi jobs/inflation markets: buy the 80-99c side when the free forecast agrees | Backtest +$6.73 per $100 on 141 bets (7 lost). Only 1-2 bets per data release, so maybe 10-15 by 1 Jan | **Not registered.** Can't be proven by 1 Jan | none yet |

<!-- AUTO:START (learnings.py writes this part every morning, don't edit by hand) -->

## Live numbers (updated 2026-11-10)

**52 days left** until the money decision on 1 Jan 2027.

| Candidate | Finished bets | Won / lost | P&L per $100 | What it means | Check |
|---|---|---|---|---|---|
| Kalshi 15-min crypto bids, spot check (`kc_maker_safe`) | 104 | 103 / 1 | +$0.07 | Ahead, but could be luck | 1 Dec (21 days): after 2,500 bets: pass if above +$0.22 per $100 |
| NO on 'will X say Y' (`mention_no`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | 21 Dec (41 days): holdout, scored once |
| Boring side after a 10c scare (`panic_fade_10c`) | 2 | 2 / 0 | +$23.52 | Too early to tell (2 finished) | 21 Dec (41 days): holdout, scored once |
| Economy favorites the forecast backs (`econ_fav`) | 0 | 0 / 0 | - | Too early to tell (0 finished) | no date: not registered yet |
| Same question on Kalshi and Polymarket (`arb`) | 0 | - | +$3.06 locked in | 16 sets cost $77.62 and pay $80.00 if both sites agree. Nothing to judge before then. | 1 Jan (52 days): pays out on 1 Jan |

**kc_maker_safe toward its locked test:** 110 of 2,500 bets, 1 lost, +$1.13 so far (+$0.10 per $100; the bar is +$0.22). About 115 bets a day, so the look is due about 1 Dec. This is only a peek: the number counts once, at 2,500.
**Fast Kalshi bot, last 45 seconds** (main test "Wait at 99.8c, 45 s left (z 2+) (main)", 10 contracts): 24 bought, 0 lost, +$1.02 (+$0.43 per $100). Full table: `state/kfast_live/report.md`.

### Week by week (numbers as of the last day of each week, all bets so far)

| Week | `kc_maker_safe` | `mention_no` | `panic_fade_10c` | `econ_fav` |
|---|---|---|---|---|
| 2026-W46 | 104 bets, +$0.07 | 0 bets | 2 bets, +$23.52 | 0 bets |

Too few bets means luck. A row only matters once a track has 30+ finished bets.

<!-- AUTO:END -->

## The 1 Jan decision checklist (draft, Jan to OK)

A strategy gets real money only if **every** answer is yes:

1. **It passed its locked test** (the rule written before the result, above).
2. **Live paper bets agree** with the backtest. Not losing live, not losing much more often than the backtest said.
3. **Bigger bets still fit.** Real orders of $25-100 would fill at about the same price (the "real size" numbers).
4. **The exam's worst case is above $0**, counting every idea we ever tried (luck gets a bigger head start the more we try).
5. **Jan may legally use that site from Sweden** (Kalshi especially). Jan checks this himself.
6. **A stop rule is set before the first dollar**, for example "if $300 turns into $250, stop and look".

- If nothing passes: **keep your money** (or keep paper testing into 2027).
- If two pass: pick the one with the better worst case, not the bigger profit.
- Start with the low end ($300). Add more only after a month of real results that match the paper.

## Calendar

| Date | What happens |
|---|---|
| 23 Nov | Gas-price recorder scored (who reads AAA first). Expected dead |
| late Nov | Fast Kalshi bot first look |
| about 1 Dec | **kc_maker_safe locked test** (2,500 bets). Order book shapes recheck |
| 21 Dec | **Holdout, scored once**: mention_no, soccer draws, panic_fade_10c, boring No far out, crypto No |
| 1 Jan 2027 | arb pays out. **Money decision** |
| late Jan | Next GDP release (GDPNow vs Kalshi, only 19 past releases, too few to judge) |

## Big lessons so far

- **Old-data wins mostly vanish at real prices.** One extra cent plus the fee kills most "edges". Brand-new
  Polymarket markets even open with fake 1c/99c books, so the listed price lies.
- **Yes buyers pay for the thrill.** On Polymarket, buying Yes lost about $8 per $100; buying No got about your money
  back. The boring side is fair, not a gift.
- **Copying wallets doesn't work for us.** The price moves within 5 minutes of a smart bet. We arrive later and get
  nothing. "Winning wallets" are mostly luck: 32 of every 1,000 look good, and luck alone gives 28.
- **"Sure" bets hide a big loss.** At 99c, one loss eats about 100 wins. You need hundreds of bets to know.
- **Check the data for holes.** Our first data dropped losing choices in weather events, which made one idea look
  like +$121 per $100. On full data it lost $18.67.
- **We are slow (a run every 5 minutes).** Anything that needs speed belongs to the pros. Our edges must last hours.
- **More ideas tried means a higher bar.** With 49 ideas, the luckiest one is bound to look good. The exam raises the
  bar for every new try.

## Tried and dropped (one line each)

Don't re-test these the same way. Only with something new (new data, a new filter).

- **Endgame, 95c+ a day before the end:** lost about $5.50 per $100 (weather, crypto and tweet-count buckets flip).
- **Endgame, 95c+ after the deadline but before a result:** lost $167 on 709 bets.
- **Favorites by rule** (screener, price bands, NO only, momentum, fade the rally): lost even with free trading.
- **Buy every answer of an event for under $1:** never once cheap on the real book.
- **Cheap side of "sure" weather buckets:** -$18.67 per $100 on full data (the +$121 was a data hole).
- **Crypto price model 3-30 hours out:** the markets are priced like the model.
- **Weather buckets already decided:** sit at 99.95c, nothing left.
- **Same question listed twice on Polymarket:** no gaps.
- **Kalshi vs Polymarket game winners:** a pair costs about $1.04 to win $1.
- **Kalshi vs Polymarket 15-min crypto:** a pair costs about $1.05.
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

Still running on purpose, though the idea looks dead: maker tracks, `wx_forecast`, the endgame lab variants,
`sharp_pinnacle`, `quiet_no` (Jan's pick), the 80 wallet copies. They show the drop was right.

## Open questions for Jan

1. **OK the 1 Jan checklist above?** Then it gets locked like the other rules.
2. **Merge the open research PRs** (#66 adds the exam, the ledger and the two new paper tracks).
3. **every_horse and ladder** have sat idle with $200 of paper since 8 Nov. Keep, or stop?
4. **Kalshi from Sweden:** the top candidate is a Kalshi strategy. Worth checking early.
