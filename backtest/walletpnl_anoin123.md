# Did wallet anoin123 really lose $4.8 million? (22 Nov 2026, `walletpnl.py`)

Jan doubted the dashboard note. Checked with the wallet's whole public money trail: 252,251 rows from
`/v2/activity` (29 Dec 2025 to 22 Nov 2026), every buy, sell, redeem, merge, conversion, reward and rebate,
plus what its 989 open positions are worth now. Probe `wpnl_fetch_0x96489abcb9f583d6835c8ef95ffc923d05a86825`.

## Yes, the loss is real

| Way of counting | Result |
|---|---|
| Money trail: got back $70.25M (sold $8.55M, redeemed $40.53M, merged $20.83M, conversions $0.20M, rewards $0.10M, rebates $0.03M) minus paid $76.85M, plus open bets worth $2.13M now | **-$4.48 million** |
| The API's per-position numbers added up (what the 11 Nov note used) | -$4.56 million |
| Polymarket's own leaderboard, all-time | -$4.69 million |
| Polymarket's leaderboard, last month / last week | +$455,000 / +$38,000 |

Three separate counts agree within $0.2 million, so merges and redeems are not missing. The 8 Nov config label
("all-time $283,464") was wrong.

## Where the loss is

- "US / Israel strikes Iran by <date>" markets: 87 markets, $20.0M bought (almost all No), **-$4.42 million**.
  Biggest: "US strikes Iran by February 28, 2026?" -$1.60M. The strikes happened.
- Everything else: 1,555 markets, $56.9M bought, -$0.19 million (about even).
- By the month a market was first bought: Jan -$2.92M, Feb -$1.40M, Mar -$0.82M, Apr-Jun -$0.35M,
  Jul-Nov **+$0.74M**. Since August it has been winning.

## What it really does

- About 500 buys a day (233,556 buys, median $12, up to $141,000), around the clock, busiest 16:00-03:00 UTC.
  It almost never sells (10,516 sells).
- It bought **both sides** in 651 of 1,642 markets (63 in 100 of its dollars). It gets out by **merging** a
  Yes + No pair back into $1: $20.8 million of merges, 6,274 times.
- It earns liquidity rewards ($104,419) and maker rebates ($25,899), so many buys are waiting orders.
- The pairs are not cheap on average: Yes + No it paid adds to 102.9c a merged pair. So it's not a clean
  "buy both for under $1" arb. It's a part market maker with big opinions on world news, and one big opinion
  (no Iran strike) cost it $4.4 million.

## What it means for us

The copy tracks `w_anoin123` / `wb_anoin123` copy its buys 5 minutes late. Many of its buys are one leg of a
pair it later merges, so a copier gets half of a hedge. Lab is frozen to 1 Jan, so the tracks keep running as
they are. Not a model to follow with money.
