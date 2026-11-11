# Polymarket Combos (parlays): who pays, how much (2026-11-11, `combos.py`)

Jan asked: is https://polymarket.com/combos worth exploring?

## How combos work (from Polymarket's docs)
- You pick 2-50 legs (mostly sports and esports: winners, spreads, totals, sets, maps; some politics legs are listed too).
- Your request goes to pro market makers. They have 0.4 seconds to answer with a price, you get 5-10 seconds to take it.
  There is no order book. If no maker answers, you can't buy.
- A user can **only buy (or sell back) the Yes side**, the parlay. The No side ("not all legs win") is the maker's side.
  So you can't bet against parlay gamblers as a user. Only a maker can, and that needs API keys, real money and a bot
  that answers in 0.4 seconds.
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
  makers. Not for us (hard rule 2: no keys; and it's a speed game).
- Dropped. If ever revisited: a "paper house" replay (pretend we sold every public combo buy at its price, judged on
  results from an unbiased sample of combos) would show whether makers really keep that $10 after sharp buyers.

Run: probe `cmb_peek` / `cmb_peek2` / `cmb_peek3` (API shapes, sanity checks), `cmb_run` (this table, about 10 min).
