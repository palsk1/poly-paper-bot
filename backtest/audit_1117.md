# Deep data check, 17 Nov 2026 (probe `audit_full`, Jan: "just do the rerun")

The 9 Nov audit (`probe audit`) checked a sample. This one checks **every** Polymarket paper buy from 9 Nov to 17 Nov 14:00 UTC, on 112 tracks. Kalshi tracks and maker tracks aren't included, because their fills come from the real trade list by design.

## Buys: did a real seller exist at our price?

Each buy was compared with Polymarket's real trade list for that market (`/v2/trades?condition_id=`, paged back by cursor).

| | buys |
|---|---|
| All buys | 3,028 |
| Trade list reaches back far enough to check | 2,799 |
| Someone really traded at our price (+1c) or cheaper within an hour | 2,212 |
| Quiet market: nobody traded within an hour | 562 |
| ... of those, the next real trade (whenever it came) was at our price +1c or cheaper | 466 of 534 that traded later |
| People traded within an hour, but **only dearer** than our price +1c | **25** (about 1 in 110) |

- The 25 "dearer" buys are mostly 1-3c off, spread over many tracks. The worst was one stopped `wx_forecast` bet: we paid 15c and the cheapest trade near it was 38c.
- Quiet markets are where paper is least proven. `boring_no` (65 of 102 buys) and `soccer_draw` (64 of 77) live mostly there. The book showed a seller, but nobody bought within the hour to prove it. The live scout on Jan's box (planned) would watch those offers second by second.
- Copy tracks (`w_*`, `wb_*`) are almost all backed by a real trade within the hour.

## Payouts and stuck bets
- 0 of 1,337 resolved closes differ from the market's final price today.
- 0 open bets stuck on a closed market.
- The light check (`state/integrity.json`) flags one thing: `kc_maker_safe_usd` has 532 finished trades and not one loss (Kalshi; not covered by this check).

Rerun: probe `audit_full` (or `audit_full_<YYYY-MM-DD>` for another start date). It takes about 3 minutes.

## kc_maker_safe_usd: 534 wins, 0 losses (checked the same day, Jan: "do it")
- Fills are real-tape fills (`bot.kmaker_fill`: only contracts really sold at our price after the queue ahead of us, or below it). 528 of its 534 fills are the exact same bets at the same price as its twin `kc_maker_safe`, whose fills were checked against the tape before (`backtest/kreplay.md`).
- Why no losses: the twin lost 4 times since the twin was added (12 Nov 16:42 UTC), and 5 times counting the morning of 12 Nov. All 5 were Yes bets that the price-gap check (Binance moved onto Kalshi's price) filtered out. That's exactly what it was built for (`backtest/kcloss.md`). The 4 later losses came after the rule was written, so this is a small but fair sign it works.
- Since launch: `_usd` +$31.61 on $5,290 of bids (+$0.60 per $100); twin +$23.76. One loss costs about $10, so the lead is a few losses wide. Too early to tell; the fills aren't fake.
