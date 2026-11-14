# Kalshi mention markets: rules fixed before the big download (13 Nov 2026, 23:55 UTC)

`kmentions.py` listed 87,512 finished Kalshi "what will X say" markets. Hourly asking prices are slow to download,
so a first random 3,500 markets (shards 0-6) were looked at while the other ~70,000 were still downloading.
On those 3,500, three things stood out. They are written down here BEFORE the rest arrives, so the rest is a
fresh test and not more searching.

Every bet: one per market, 24 hours before the event's first market closes, only if Yes has a buy order at 3c+,
the Yes asking price is 97c or less and the two are at most 10c apart. Buy No at the real asking price
(1 minus the best Yes buy order) plus Kalshi's fee (7c x price x (1 - price) per contract). Hold to the result.

| # | Rule | On the first 3,500 | Expect on the rest |
|---|---|---|---|
| T1 | Earnings-call markets (series with EARNINGS in the name): buy No | +$11.60 per $100, 237 bets | ahead |
| T2 | Other markets, word listed only 1 or 2 times before in that series: buy No | +$10.10 per $100, 117 bets | ahead |
| T3 | Other markets, word listed 3+ times before: buy No (yardstick) | -$8.00 per $100, 692 bets | behind |

Second look, same rules 6 hours before instead of 24: T1 +$12.90, T2 +$13.90, T3 -$8.30.
The Polymarket idea (buy No where the price is far above the word's own record) did NOT show up here:
-$10 to -$17 per $100 on the first 3,500.
