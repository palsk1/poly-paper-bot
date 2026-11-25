# kc_maker_safe, but earlier and cheaper? (24 Nov 2026)

Jan: "What about something like kalshi safe but earlier? How far back can we push it to earn more and find winners?
Like maybe 85-95 cent range?", then "test all ranges and timeliness", "try with real technical analysis on charts
too", "try them all" and "always test both Polymarket and Kalshi". Research only, no track. Code `kearly.py`.

## The short answer

- **You can't really buy the "safe" side at 85-95c.** When Binance says the coin is safely past the line (the
  real bot's 2.3 cushion), Kalshi already prices it at 95c+. Over 4 months, 7 coins, a bid at 85-95c with the 2.3
  cushion came up about 5 times a day in total. The market and the cushion agree almost always.
- **Starting earlier does help a little, at the same 90c+ prices.** Letting the bot bid from 10 minutes left
  instead of 5.5 (90c and up, cushion 2.3) made **+$0.68 per $100 on the fresh month** vs **+$0.50** for today's
  rule. At $4 bids that is about **$2.60 a day instead of $1.75** on the candle model. Exam: "Promising, needs more
  bets".
- **Cheaper and earlier with a softer cushion looked good on the check month and then failed.** 85-97c, 4-10 minutes
  left, cushion 2.0: +$1.81 per $100 on the check month (620 bets), then **-$2.79** on the fresh week. Dropped.
- **Before 10 minutes left there is almost nothing**: prices are rarely 85c+ that early (a handful of bids a day).
- **Chart signals (RSI, moving averages, MACD, Bollinger, momentum, volume, other coins) add nothing the cushion
  doesn't already know.** Six classic readings all agreeing: $0.00 per $100 on the fresh month. Losers looked the same
  as winners on every chart reading. Flips are news-like jumps; charts don't see them coming.
- **Polymarket: no.** The same bids on Polymarket's 15-minute rounds lose at 85-95c at every time (-$3 to -$7 per
  $100 without a cushion, about $0 with one) and find under $1 a day.
- **Real-size check on a fresh week (17-24 Nov, every trade with its size):** the 10-minute, 90c+, cushion 2.3 version
  made +$0.85 per $100 vs +$0.59 for today's rule (about $2.55 vs $1.60 a day at $4 bids), and fills held up to $50
  bids. **Every cheaper or softer-bar version lost that week** (-$0.83 to -$6.04 per $100).

What is different from `kc_maker_early` (dumped 12 Nov, -$2.45 per $100 live): it bid 90c+ with 6.5-11.5 minutes
left and **no cushion check at all**. Without a cushion, early cheap bids lose about 1 in 10 and come out
between -$1 and +$1 per $100 on the fresh month. Every version here has the cushion.

## Data and method

- 78,304 settled Kalshi 15-minute windows (BTC, ETH, SOL, XRP, DOGE, HYPE, BNB), 17 Jul-19 Nov 2026, the last 11
  minutes of 1-minute candles (`bt_cache/kc`), all 15 minutes for 12 Sep-9 Nov (`bt_cache/ks`), Binance 1-minute
  prices, Kalshi's own settle number a minute (`bt_cache/kidx`).
- **Find** = windows before 15 Oct (settings picked here). **Check** = 15 Oct-19 Nov, only scored after picking.
- Bid one tick (0.1c) above the best bid on the winning side (first in line); filled when a later trade prints at
  or below our bid. Maker fee 0. "Paying the ask" cells pay Kalshi's taker fee, rounded up per $10 order.
- Cushion = the real bot's: Binance moved onto Kalshi's price, distance to the line in "typical moves until the
  close". "zk" = the same on Kalshi's own settle number.
- Bid lifetimes: held to the close (the live bot's way), cancelled after 1 minute, or cancelled as soon as the
  cushion falls under the bar. They come out about the same: cancelling doesn't save the early bids.
- Full tables: `backtest/kearly_tables.md` (time x price x cushion, lifetimes, paying the ask, Kalshi's own number,
  the live-bot way, picks on fresh windows) and `backtest/kearly_ta.md` (chart signals). Polymarket:
  `backtest/kearly_pm.txt`.

## 1. Time x price, cushion 2.3 (find period, held to the close)

Bets at 85-95c with the 2.3 cushion are rare at every time (1-84 bets in 3 months per cell). They do win
(+$1 to +$9 per $100), but there are too few to matter. 95-99c is where the bets are, and it pays more the earlier
you bid: +$2-4 per $100 at 7-10 minutes left vs +$0.3-1.3 at 1-3 minutes.

## 2. The live-bot way (first minute that fits), find vs fresh check

P&L per $100, (bets, lost), $ a day at $4 bids:

| Setting | Find (17 Jul-15 Oct) | Check (15 Oct-19 Nov) |
|---|---|---|
| Today's rule: 1-5.5 min, 95c+, cushion 2.3 | +$0.70 (10,028, 59 lost), $3.15 a day | +$0.50 (3,222, 11 lost), **$1.76 a day** |
| 1-10 min, 90c+, cushion 2.3 | +$0.98 (10,816, 86 lost), $4.80 a day | +$0.68 (3,517, 18 lost), **$2.63 a day** |
| 4-10 min, 85-97c, cushion 2.0 | +$2.38 (3,377, 92 lost), $3.59 a day | +$1.81 (620, 18 lost), **$1.26 a day** |
| 4-10 min, 85-97c, cushion 1.5 | +$1.77 (9,930, 426 lost), $7.90 a day | +$0.62 (3,082, 148 lost), $2.19 a day |
| 4-10 min, 85-97c, cushion 1.5 + "calm Kalshi" | +$2.02 (7,081, 286 lost) | +$1.06 (1,946, 87 lost), $2.36 a day |

"Calm Kalshi" (found by looking): this minute's trading is not unusually busy and the price did not jump 19c+ in
the last 2 minutes. It was the only filter beyond the cushion that held up on the fresh month, but only a little.

Every setting earns less on the fresh month than where it was found. That is the usual shrink.

## 3. Paying the asking price early

At 6-10 minutes left, buying 90-97c at the ask with cushion 2.3 made +$1.4 to +$3.6 per $100 on the find period,
on a few hundred bets. Without a cushion it is about $0 at 8-10 minutes and loses from 4 minutes left. Waiting with a
bid is the better way, as before.

## 4. Chart signals (Jan's ask)

On 23,391 early bids (85-97c, 4-10 min, no cushion), each reading split in thirds (`kearly_ta.md`):
- the cushion itself (on Binance or on Kalshi's own number) is the only strong one: top third +$1.71 per $100 vs
  low third +$0.23 (find), and it holds on the fresh month (+$0.94);
- RSI, fast vs slow average, MACD, Bollinger, 3- and 10-minute momentum, place in the last hour's range: the top
  thirds look better on find (+$1.2 to +$1.8) and fall to -$0.56 to +$0.68 on the fresh month;
- the 6-reading "chart vote": all six agree = $0.00 per $100 on the fresh month (6,086 bets);
- busy Kalshi minutes and a 19c+ jump in the last 2 minutes are bad signs (-$0.5 to -$1.1 per $100 fresh);
- other coins moving the same way: no help.
- Backward look: lost bets vs won bets have almost the same average on every reading (RSI 70 vs 72, cushion 1.8 vs
  1.9). Nothing on the chart marks the flips beforehand. Worst hours 08-12 UTC, HYPE the worst coin, BTC the best.

## 5. Polymarket (Jan: "always test both")

Same bids on Polymarket's 15-minute rounds, 31 days of real trades (last 8 minutes of each window, `bt_cache/pm15`):
85-95c lose at every time from 2 to 7 minutes left (-$2.58 to -$6.84 per $100 without a cushion; with a cushion
about -$5 to +$2 on 9-150 bets). 95c+ at 7 minutes left: +$2.10 on 310 bets, under $1 a day. Polymarket trades
too little in these rounds (alts 10-40 trades in the last 8 minutes) and disagrees with Kalshi's result in about 17
windows in 1,000. Dropped.

## 6. Real sizes (real trade lists with contract counts, last 7 days)

7 fresh days that no setting was picked on (17-24 Nov, 4,213 windows), every trade with its size from Kalshi
(probe `ke_all_7`, `bt_cache/ke/`). A bid gets only contracts that sellers really sold at or below our price after
we placed it, capped at the bid size. P&L per $100 (bets, lost, total $):

| Setting | $4 bids | $50 bids |
|---|---|---|
| Today's rule: 1-5.5 min, 95c+, cushion 2.3 | +$0.59 (492, 1 lost, +$11.33 in 7 days) | +$0.58 (+$134.63) |
| **1-10 min, 90c+, cushion 2.3** | **+$0.85 (534, 2 lost, +$17.82)** | +$0.86 (+$219.51) |
| 1-10 min, 90c+, cushion 2.3, calm Kalshi | +$1.01 (301, 1 lost, +$11.86) | +$1.02 (+$146.19) |
| 6-10 min only, 90c+, cushion 2.3 | +$1.50 (177, 1 lost, +$10.39) | +$1.51 (+$130.82) |
| 1-10 min, 85-95c, cushion 2.3 | +$6.46 (14, 0 lost, +$3.40) | +$6.46 (+$44.84) |
| 1-10 min, 90c+, cushion **2.0** | **-$0.12** (813, 14 lost, -$3.84) | -$0.17 (-$65.75) |
| 4-10 min, 85-97c, cushion 2.0 | **-$2.79** (113, 8 lost, -$12.03) | -$2.95 (-$160.80) |
| 4-10 min, 85-97c, cushion 1.5 | **-$0.83** (602, 37 lost, -$18.94) | -$0.98 (-$283.43) |
| 4-10 min, 85-97c, cushion 1.5, calm Kalshi | **-$1.48** (384, 26 lost, -$21.48) | -$1.56 (-$291.04) |

What it says:
- Real contract counts match the candle model almost to the cent, even at $50 bids. Early bids do fill on the good
  ones too, not only before a flip.
- **The cheaper, softer-bar versions all lost on the fresh week.** The +$1.81 per $100 "85-97c, cushion 2.0" lead from
  the check month became -$2.79. Below 95c you need the full 2.3 cushion, and then bets are rare (14 in 7 days).
- **The longer window with the same 2.3 bar held up a third time:** +$0.85 vs +$0.59 for today's rule, about
  **$2.55 a day vs $1.60 at $4 bids**. That is three separate stretches (find, check month, fresh week) ahead of
  today's rule, by about $0.20-0.30 per $100 each time. Only 2 lost bets in the week, so luck still matters.


## Ceilings (rough guesses)

| Version | Most in an average day | Money needed | Where it stops growing | Bad day |
|---|---|---|---|---|
| Today's rule (1-5.5 min, 95c+) | about $1.75 at $4 bids, about $15 at its best size | about $700 | about $100 a bid | about -$100 |
| Window to 10 min, 90c+ | about $2.55 at $4 bids, about $30 a day at $50 bids on the fresh week | about $700 at $50 bids (about 7-10 bids out at once) | fills still full at $50; untested above | about -$50 at $50 bids (one loss = one bid) |

## Verdict

No new track. The earlier, cheaper idea mostly runs into the fact that Kalshi already prices a safe coin at 95c+.
The one practical change, letting the real bot start at 10 minutes left and take 90c+ bids with the same 2.3
cushion, beat today's rule in all three stretches (about +$0.90 a day at $4 bids, real fills on the fresh week). It is
a rule change on a real-money bot, so it is Jan's call. **25 Nov: Jan picked "Paper twin first"**: paper track `kc_maker_safe_usd_10m` runs it next to `kc_maker_safe_usd`; compare after 1-2 weeks. Exam
rows added to `backtest/ledger.md`. Don't redo the chart-signal cuts on these rounds.
