# Every kind of Polymarket bet (2026-11-10, `census.py`)

Research only. Live counts from probe `census_live` (2026-11-10 ~11:40 UTC). History from probe `btcensus`
(in-sample markets ending before the 2026-11-10 holdout, whole events). Real-fill check from probe `btcensustape`.

## How many, and how much money

213,113 open markets in 18,854 events. $35.8M traded in the last 24h (market level), $561M resting in order books.

| Family | Open markets | Traded last 24h | Traded Mar-Nov (our data) | Settles on | What we know |
|---|---|---|---|---|---|
| Politics & elections | 19,428 | $7.8M | $2.3B | news + UMA vote | long shots lose $40-56 per $100; rest about fair |
| Other one-offs (golf top-20s, ship counts, ...) | 9,471 | $7.4M | $3.8B | news + vote | favorites 50-85c +$4-6 per $100 on history prices, likely the thin-price trap below |
| Economics & Fed | 565 | $4.3M | $1.3B | Fed, BLS, BEA | econ.md: forecasts lose to the market |
| Sports: game winner | 57,013 | $3.3M | not in our data | league sites | sharp.md: Poly tracks Pinnacle, no edge |
| War & world politics | 332 | $2.3M | $2.1B | news + vote | about fair |
| Crypto price levels | 1,124 | $1.9M | $2.1B | Binance | day-ahead dropped; long shots lose |
| Esports single map | 1,926 | $1.3M | ~0 | hltv, dotabuff | livelag.md: free feed 100 s late, dropped |
| Sports: season futures | 12,028 | $1.1M | $5.5B | news | long shots lose |
| Courts, arrests, people | 209 | $1.1M | $159M | news + vote | few events |
| Weather: temperature buckets | 3,140 | $938k | $465M | aviationweather.gov METAR | tested many times (fade, wx_forecast, idea machine) |
| Esports match winner + lines | 1,486 | $1.2M | $3M | hltv | untested, small |
| Post/tweet counts | 562 | $839k | $672M | X / Truth Social trackers | idea machine: nothing |
| Tech, AI, apps | 3,391 | $818k | $387M | arena.ai, company news | AI-leaderboard underdogs +$28 on 64 events, too few to trust |
| Stocks & companies | 669 | $442k | $87M | Pyth, Yahoo | heavy favorites +$3 on 48 events, tiny |
| Movies, music, awards | 2,930 | $357k | $41M | the-numbers, oscars.org | about fair |
| Sports: game totals (over/under) | 57,568 | $232k | not in our data | league sites | untested; median buy/sell gap 94c (empty books) |
| Sports: spreads | 18,901 | $182k | not in our data | league sites | untested; median gap 7c |
| Soccer: draw | 2,020 | $120k | not in our data | uefa, efl | untested |
| Crypto up/down (5m/15m/1h) | 3,157 at a time | $99k (rolls over fast) | **$6.1B, the biggest** | Chainlink, automatic | speed game; favorite side loses ~$10 per $100 to fees |
| Sports: player props | 16,439 | $94k | not in our data | league sites | untested; median gap 89c |
| Stock/commodity up/down (daily) | 548 | $20k | $56M | Chainlink / Pyth | looked cheap on history, gone at real prices (below) |
| Mentions ("will X say Y") | 120 | $3k | $90M | video / transcript | mention_no track running |

Sorting is by rule (`census.classify`), so a few markets land in the wrong family (e.g. sports team "Hurricanes" as weather).
The bt_cache drops every sports market (`backtest.py` skips gameId markets), so sports lines were never priced vs results here.

## Weird things

- Half the open markets are sports side bets almost nobody trades: 57k over/unders, 19k spreads, 16k props. Most show a
  1c bid and 99c ask; under 1 in 30 traded today.
- Multi-choice events with real books (every choice's gap 5c or less) cost $1.02-1.08 to buy every choice for a $1 payout.
  No free sets (matches every_horse).
- Long shots (2-15c) lose $25-60 per $100 in nearly every family and every time before the end.
- Forex up/down markets (USD/SEK, EUR/USD...) exist with empty 1c/99c books.

## The one that looked cheap: daily stock/commodity "Up or Down"

On history prices, buying the side under 45c 23 hours before the end (the evening before) won 124 of 266 bets:
+$22 per $100 at +2c, both halves ahead (`btcensusupdown`). At the first real buy on the trade tape within 3 hours
(`btcensustape`), real buyers paid a median 8c more than the chart: 228 bets on 109 trading days,
+$0.80 per $100 at the real price, -$3.50 at +2c, 90% band -$18 to +$11. **Dropped.** Same lesson as launch.md:
on thin markets the price chart is not a price you can get.

## Sports side bets, tested (2026-11-10, Jan's "yes")

`btsports` fetched every finished sports market with $3,000+ traded, Mar 2026 to the holdout (190,380 in-sample,
183,695 with a price chart, start time and clean result; $14.9B game winners, $2.3B totals, $1.2B spreads,
$412M draws). Snapshots 24h, 6h and 1h before the game, buy 1h later but never after kickoff, held to the result.

- **Chart prices:** game winners lose $2-7 per $100 at +2c in every band (priced right, minus costs). Long shots
  (2-15c) on totals and spreads looked like +$30-50 per $100, NFL/NBA/college long shots even +$90-200. 46 slices
  flagged.
- **Real-buy check, first try was wrong:** a 1-hour window after kickoff let in in-game buys (buyers who already
  know the score). Fixed: only the first real buy of that side **before kickoff** counts.
- **Real buys before kickoff (sample of 500 per slice):** the long-shot leads shrink to noise (totals 24h +$0.80,
  spreads 1h -$14.50, NBA/college bands cross zero). Real buyers paid about the chart (+0.5c), so the chart wasn't
  the trap this time; the long-shot results just don't repeat across times and samples.
- **Soccer draws survive, barely** (`btsportsdraw`, every bet, not a sample):

| bet | when | bets | won | at the first real buy | 90% band | at +2c |
|---|---|---|---|---|---|---|
| full-time draw, 15-50c | 24h before | 3,783 | 1,146 | +$11.90 | +$7.30 to +$16.40 | +$4.00 |
| full-time draw, 15-50c | 6h before | 4,102 | 1,203 | +$8.80 | +$4.50 to +$13.10 | +$1.20 |
| full-time draw, 15-50c | 1h before | 4,094 | 1,186 | +$8.10 | +$3.70 to +$12.40 | +$0.40 |
| half-time result underdog | 6h before | 1,416 | 600 | +$13.30 | +$8.00 to +$18.50 | +$7.50 |

  So draws are about 2c cheap per bet (a 26c draw wins about 29 times in 100). That matches the old "people don't
  like betting on draws" pattern from bookmakers. But the whole edge is about 2c, so paying 2c more than the first
  real buyer wipes most of it, and we don't know how many shares sit at that price. Many slices were tested, so
  some luck is expected.
- **Verdict:** "Promising, needs more bets". No track (research mode). Pre-registered for the 21 Dec holdout:
  soccer full-time draw at 15-50c, decided 24h before kickoff, filled at the first real buy before kickoff, must be
  ahead at +1c. Check the book depth at $25 then too.


### Draw depth, live (2026-11-10 14:30 UTC, probe `census_drawdepth`)

43 open soccer draw markets kicking off within 48 hours, 23 with an ask at 15-50c.
- Books that are alive (mostly matchday): spread 1-2c, ask about 1c over the listed price. $25 fits within +1c of
  the best ask in 15 of 23; the median game has about $107 on sale within +1c and $138 within +2c.
  Big games (PSG-Bayern, Inter-Man City women) have $1,000-3,000 within +1c.
- Books a day or more out are often placeholders (5c bid / 95c ask, or $2 on the ask), so a "24h before" buy
  mostly happens on matchday anyway. The holdout rule already fills at the first real buy before kickoff.
- Verdict: $10-25 bets fit in most games, $100 only in the bigger ones. Depth is not the problem; the ~2c edge is.
