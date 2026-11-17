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
