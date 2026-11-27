# Platform reward programs: real cash for us? (27 Nov 2026)

Short answer: no. Every program that pays real money either shuts out non-US
accounts (Jan trades from Sweden) or starts at a trading size we will never reach.

Sources: Kalshi help center (Liquidity Incentive Program, APY on Kalshi,
Referral FAQ, Where to find rewards), Kalshi's CFTC filings (Liquidity Incentive
Program updates 15 Jul / 30 Jul / 14 Oct 2026, Volume Incentive Program
termination 28 Sep 2026), Kalshi's public `GET /trade-api/v2/incentive_programs`
(no key), Polymarket docs (Maker Rebates, Fee and rebate changes 20 Nov 2026,
Referral Program), Polymarket US refer-a-friend FAQ.

## Kalshi

| Program | What it pays | Can Jan get it? |
|---|---|---|
| Liquidity incentive (waiting orders) | $1-$1,000 a market a day, split by size and nearness to the top of the book, snapshot every second, ends 1 Jan 2027 | **No.** Help page: "International, non-U.S. users (ineligible for rewards)" |
| Volume incentive | share of a pool by traded volume | **No.** Terminated 13 Oct 2026 |
| Interest (APY) | 3.5 a year on cash + positions, $250 average balance | **No.** US and territories only |
| Referral / sign-up bonus | varies | **No.** US users only |

**Would the real bot qualify if it were a US account?** Still about $0:
- A snapshot only counts if 100+ (up to 20,000) contracts wait on *both* sides
  (the "target size"), and the pool is shared by everyone in that depth.
- Our bid is $4 (about 4 contracts at 95c) up to $40 (about 42). With a common
  target of 300 contracts and a $20 pool, our share is roughly 4/300 to 42/300
  of $20 = about 25c to $2.80 per program, and **any program paying under $1
  is not paid** (the $1 floor is per program, not per day).
- In 4,308 programs from Kalshi's public list (3 Sep - 14 Oct 2026) none was on
  KXBTC15M / KXETH15M / KXSOL15M or the other coin windows the bot uses (only
  `KXCRYPTOLEAD15M` and a few metals 15-minute series). The current rewards page
  shows the big pools on long-dated markets (NVIDIA CEO $18,000, GTA VI score
  $17,730, gas prices $8,625), not crypto windows.
- So: $0 a month at $4 bids, $0 at $40 bids. Rough guess, but the eligibility
  line alone settles it.

## Polymarket (changed 20 Nov 2026, 23:59 UTC)

| Program | What it pays | Can Jan get it? |
|---|---|---|
| Maker (seller) rebate, new tiers | 3-15 in 100 of the fees your filled waiting orders generate | **No.** Starts at $200,000 of 30-day maker "weighted volume" (shares x p x (1-p)). A $2 bet at 50c adds 50c of it, so about 400,000 such bets a month. Our real bots are mostly instant buyers anyway |
| Taker (buyer) rebate | 10-60 in 100 of your fees back | **No.** Same $200,000 floor; the old small Bronze/Silver tiers were removed |
| One-time level-up bonuses | $10-$25,000 | **Gone** since 20 Nov |
| Referral | 10 in 100 of a friend's net fees for their first 30 days | Needs $10,000 lifetime trading first; the friend gets nothing. Not a money source |
| Polymarket US $25 credit | $25 trading credit on a $10 deposit | **No.** US exchange only |
| Liquidity rewards (quote near the middle) | daily pools | Already measured 8-12 Nov: about $8 in total on the 5 maker tracks, eaten by pick-off losses |
| Holding rewards | $3.25 a year per $100 | Already known; only long-dated markets. On the ~$60 bank: under $2 a year |

## Ceiling (rough guess)
- Most it can make a day: $0 (Kalshi, not eligible), a few cents (Polymarket holding rewards).
- Money needed: n/a.
- Where it stops growing: n/a.
- Bad day: n/a.

Dropped. Re-check only if Kalshi opens its liquidity rewards or interest to
non-US accounts (watch its help page / notices), or Polymarket brings back a
small-account tier.
