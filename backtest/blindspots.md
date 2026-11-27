# Blind spots: the kinds of edge we never tried (27 Nov 2026)

Jan asked (27 Nov): "have some of them look outside areas I have maybe missed entirely". This page is a fresh-eyes
pass over the ~274 ideas in `backtest/ledger.md`, plus what papers and serious traders say works, then tests of the
three best gaps our data can answer. Code: `blindspots.py` (`chart` offline, `real` = probe `bs_real`). Paper only.

Skipped on purpose (other threads have them): in-game sports, OpenRouter shares, more Kalshi coins, Kalshi vs
Polymarket price gaps, re-scoring at the new fees, new market families, other sites, reward programs.

## What the outside world says (short)

Read by two research helpers: about 15 papers (2008-2026) and about 20 trader write-ups. Sources are in the PR.

- **Most of it we already did.** Longshots lose, takers lose to waiting orders, near-sure bets are cheap because the
  money is locked up, copying "smart wallets" fails, arbitrage gets taken by fast bots. Every one of these is in the
  ledger already, with the same answer the papers give.
- **Insider trading is real but can't be followed.** One study flags $143 million of insider-looking wins on
  Polymarket (Google Year in Search, the Nobel Peace Prize, Iran strikes), but it spots them after the fact.
- **The genuinely new angles were few:** (1) sort questions by "what happens if nothing changes" instead of by price
  or topic (LessWrong, 16 Nov 2026); (2) follow late jumps before a fixed announcement (the insider leak idea);
  (3) on the day, the 75-95c weather bucket is too dear (Qiu & Qiu 2026, +50c per $1 on 184 bets); plus smaller
  ones listed under "Not tested".

## The gap list, ranked

| # | Kind of edge we never tried | Why it might work | Data we have? | Done here |
|---|---|---|---|---|
| 1 | Question type: "No if nothing changes" | People overrate change; one study says Yes is 1.5x too dear | yes, 126k Polymarket markets | tested |
| 2 | Late jumps before a fixed announcement (awards, Nobel, picks) | Insiders leak in the last hours | yes, hourly prices in the last 2 days | tested |
| 3 | Weather favourite too dear on the day | One paper's backtest | yes, hourly weather prices | tested |
| 4 | Settle-source lag on weather: the low is nearly set by 8am | The answer is mostly known hours before the end | prices yes, live readings no | found while testing 3 |
| 5 | Kalshi waiting orders by category (media, world events) | Papers: maker profit is 7x bigger there than in finance | partly (khouse tapes) | not tested: it re-cuts a dropped idea |
| 6 | NASA monthly temperature markets vs daily satellite data | One trader's biggest win; NASA publishes ~10 days late | no, needs new downloads | not tested: ~12 markets a year |
| 7 | Kalshi Rotten Tomatoes with the review count | Score barely moves after 200 reviews | no review history | not tested: ~20 films a month |
| 8 | US debt ladders vs the Treasury's daily number | Official daily feed | not checked that Kalshi lists them | not tested |
| 9 | Late money in horse racing | Old papers: late movers win | not our kind of market | not tested |

## Results

All at chart prices first (+1-2c), then the survivors at real prices (`exam.fills`).

**1. "No if nothing changes" (2,483 markets labelled from the question text).** Buying No at Yes 30-70c a day in:
+$10.70 per $100 on 316 events, both halves ahead. Sounds good, but the yardstick kills it: the same rule on
every *other* worded market made +$20.06, and on number markets +$18.90. So sorting by question type adds nothing:
it's our old "things don't happen" lean, which shrinks a lot at real prices (yesno grid, 10 Nov). Real-price check
below.

**2. Late jumps before announcements.** A candidate up 10c+ in 12 hours, in the last 2.5 days, bought an hour later:
-$8 to -$28 per $100 on 43-186 bets (awards, picks, Nobel and the like), and -$13 to -$18 on 5,500-16,000 bets
everywhere else. Following a jump loses everywhere, insider markets included. Dropped.

**3. Weather favourite too dear on the day.** Buying No on the 75-95c bucket 0-8 hours into the local day:
-$12 to -$23 per $100 (daily highs, 218-301 bets). The paper's result does not show up in our data: the favourite
is about fairly priced (buying it: -$0.64 to -$2.21). Dropped.

**4. Weather lows, found by looking (64 cuts).** Buying Yes on the 60-75c favourite for the daily LOW, 8 hours into
the local day: +$18.04 per $100 on 149 bets (91 days), both halves ahead. Likely reason: the low usually comes
around sunrise, so by 8am it is mostly set, and the market is slow to price that in. The 2026-11-10 weather dig
already saw a shaky "daily lows" lead (+$6 to +$11). Real-price check below.

## At real prices (probe `bs_real`, 27 Nov): all dead

The first real buy within 3 hours + 1c + fee, from Polymarket's trade list (`exam.fills`).

| Test | Signals | Could really buy | Separate bets | Per $100 | Exam verdict |
|---|---|---|---|---|---|
| "No if nothing changes", buy No, Yes 30-70c a day in | 576 | 210 | 128 | -$5.29 | Behind, but could be bad luck |
| Yardstick: No on every other worded market (900 picked at random) | 900 | 91 | 81 | +$16.31 | Ahead, but could be luck |
| Weather lows, Yes on the 60-75c favourite, 8 h in | 149 | 111 | 83 | -$5.47 | Behind, but could be bad luck |
| Weather lows, Yes on the 75-95c favourite, 8 h in | 394 | 311 | 131 | -$1.45 | Behind, but could be bad luck |
| Weather lows, Yes on the 60-75c favourite, 6 h in | 243 | 214 | 117 | -$2.78 | Behind, but could be bad luck |

- **Question type:** at real prices the "nothing changes" pick loses $5.29 per $100. The yardstick stays ahead, but
  only 1 signal in 10 could be bought at all (nobody sold No there), so it is the same thin "things don't happen"
  lean we already know (`boring_no`, `quiet_no`, the 10 Nov yesno grid). Nothing new to build.
- **Weather lows:** the real price paid was about **20c above the chart** at 60-75c. The chart was stale: by the time
  anyone traded, the price already knew the low. The +$18 was a chart illusion. Same lesson as `known.py`: once the
  answer is mostly in, the people with live readings get there first.

**Bottom line:** none of the 9 blind spots gives a new candidate. The three the outside world rated best, plus the
one we found while looking, all fail at prices you could really pay.

## Not tested, and why

- **Kalshi waiting orders by category:** a fresh cut of an idea we dropped (Kalshi patient buyer); splitting a dead
  idea into 10 categories finds a lucky one by chance.
- **NASA temperature, Rotten Tomatoes, debt ladders:** small (12-250 markets a year) and need new data. Worth a look
  only if nothing bigger turns up.
- **Horse-racing late money:** a betting-pool effect, no match on our sites.
