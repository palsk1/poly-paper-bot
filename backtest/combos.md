# Polymarket Combos (parlays): who pays, how much (2026-11-11, `combos.py`)

Jan asked: is https://polymarket.com/combos worth exploring?

## How combos work (from Polymarket's docs)
- You pick 2-50 legs (mostly sports and esports: winners, spreads, totals, sets, maps; some politics legs are listed too).
- Your request goes to pro market makers. They have 0.4 seconds to answer with a price, you get 5-10 seconds to take it.
  There is no order book. If no maker answers, you can't buy.
- A user can **only buy (or sell back) the Yes side**, the parlay. The No side ("not all legs win") is the maker's side.
  So you can't bet against parlay gamblers as a user. Only a maker can, and that needs an API key (on Jan's own
  server), money and a bot that answers in 0.4 seconds.
- Fee: the sports rate, 0.05 x price x (1 - price) per share (checked on a real buy: $515.74 on 44,044 shares at 37.4c).

## What we measured
Every combo buy is public (`/v2/trades?condition=<combo id>`). We took 15,655 combos held by the 130 biggest combo
wallets (combo P&L boards and biggest combo wins), shuffled them, read the buys of 2,500, and priced each leg on its own
chart at the same minute. Kept: 3,897 buys (each leg had a chart price within 30 min, no leg already decided).
About half of those 15,655 combos were held on the **No side**: many of the big combo earners are the makers.

| Kind of combo | Buys | Per $100 a buyer spends, the legs on their own are worth | Maker's extra | Fee | Typical markup |
|---|---|---|---|---|---|
| All | 3,897 | $86.61 | $10.33 | $3.05 | 5% over the legs |
| 2 legs | 1,881 | $88.22 | $8.99 | $2.79 | 3% |
| 3 legs | 857 | $86.80 | $10.03 | $3.17 | 5% |
| 4 legs | 452 | $84.63 | $12.08 | $3.29 | 7% |
| 5+ legs | 699 | $78.90 | $17.07 | $4.03 | 16% |
| Long shots (legs multiply to under 20c) | 1,444 | $77.53 | $18.36 | $4.11 | 13% |
| Legs 60c+ | 249 | $95.02 | $3.55 | $1.42 | 1% |
| Bought before any game started | 2,912 | $88.14 | $8.74 | $3.12 | 5% |
| Bought while a game was running | 985 | $81.58 | $15.56 | $2.85 | 8% |
| Same game in it (legs depend on each other) | 175 | $77.05 | $20.04 | $2.91 | 20% |

- Only 396 of 3,897 buys (1 in 10) were cheaper than the legs multiplied, and the cheapest ones are mostly same-game
  legs that work against each other (team wins + other team covers), where cheaper is the right price.
- Single game bets on Polymarket are priced about right (Pinnacle check, census). So a combo buyer starts about
  **$13 behind per $100**, against $1-3 on a single bet. More legs and longer shots = worse.
- "Money back" on these combos is **not** usable: the combos were picked from the wallets of big winners (and big
  makers), so the results are tilted. The price comparison doesn't depend on who won.

## Verdict
- **As a buyer: losing.** About -$13 per $100 on average, -$21 on 5+ legs, -$22 on long shots. No cheap corner.
- **As the house (the maker): this is where the gamblers' money goes** (about $10 per $100 of combo buys), but it
  needs a real-money market-making bot with API keys answering in 0.4 s, against pro firms who see the same requests,
  with risk of sharp parlay buyers picking them off. We can't paper-test it either: the requests only go to logged-in
  makers, so even a paper test needs Jan's own Polymarket API key on a server he controls (hard rule 2: the key never goes in this repo or to Claude). Not on today's free GitHub setup, and it's a speed game.
- Buying combos: dropped.

## Paper house replay (same day, Jan: "grade it from our circumstances")
Fairer sample: 2,062 ordinary buyers found on the big wallets' combos, 500 of them at random, then **all** their finished
Yes combos (30,341; not picked by who won). 4,945 buys on 2,924 combos kept (same chart checks as above).

**What the pros really kept:** buyers paid $348,919, the combos paid out $240,496. The house kept **$31 per $100** of
buyers' money, more than the legs said ($15). The legs these buyers pick do worse than their prices say (and some of it
is luck: results bunch by day). Long shots under 20c: house kept $45. Legs 60c+: the house *lost* $22.

**Us as the house:** quote legs x (1 + markup) and only count buys where our quote is below what the buyer really
paid (we'd be the cheapest pro). $25 of our money at risk per buy (selling a 20c combo puts up 80c a share).

| Which combos | Markup | Buys we'd win | Per $100 at risk | Luck range | Verdict |
|---|---|---|---|---|---|
| All | +0% | 4,316 | -$0.31 | -$2.56 to +$1.93 | Losing |
| All | +3% | 3,347 | +$1.51 | -$0.64 to +$3.67 | Ahead, but could be luck |
| 2-4 legs, no same-game legs | +3% | 2,111 | +$3.43 | +$0.42 to +$6.45 | Promising, needs more bets |
| 2-4 legs, no same-game legs | **+5%** | **1,581** | **+$3.99** | **+$0.68 to +$7.29** | **Promising, needs more bets** |
| 2-4 legs, no same-game legs | +10% | 959 | +$4.11 | +$0.32 to +$7.91 | Ahead, but could be luck |
| Long shots under 20c | +0% to +10% | 1,509-2,403 | -$0.61 to -$0.10 | all touch below $0 | Losing |

Exam (best of 15 versions, bar raised for 69 ideas tried): **Promising, needs more bets**. Both halves ahead (+$3.34,
+$4.83). Worst case per $100 -$2.22, so not proven. The exam's "too slow for 1 Jan" pace counts only our 500-buyer
sample; a live quoter would see every request on Polymarket, many times more.

**Why it can still be wrong:**
- We price legs on the chart minute; a live quoter needs the real book in 0.4 s.
- We assume a buyer takes our quote whenever it's cheaper than the pro's. Requests that got no trade at all are invisible here.
- Pros may decline quotes they think are sharp (Last Look); we'd be the one left with those.
- Long shots, the fattest part for the pros, lost for us: the pros must be pricing them with something better than "legs multiplied".
- Maker fees on the RFQ side are assumed zero.

**Next step if Jan says go:** a live paper quoter on Jan's own server with his own key (hard rule 2), logging every
request, our quote, and the winning trade price, scored on results. No money moves.

Run: probe `cmb_peek` / `cmb_peek2` / `cmb_peek3` (API shapes, sanity checks), `cmb_run` (this table, about 10 min).
