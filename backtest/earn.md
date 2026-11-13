# Earnings markets: "Will company X beat its quarterly earnings forecast?" (earn.py)

Generated 2026-11-13T11:28:43Z. 1521 finished markets on 407 companies, September 2025 to 9 November 2026 (the holdout from 2026-11-10 is not in here), every real trade in 5-minute steps. Paper only.

**What they are.** One Yes/No market per company per quarter: does the reported profit per share beat the analysts' forecast written into the market? Yes won 1113 of 1521 (73 in 100): companies usually beat, everybody knows that, and the price knows it too. A typical market trades about $3,000 in total.

**The questions.** (1) Is the price a fair forecast? (2) Does a company's own record of beating or missing add anything? (3) Does the kind of number (official 'GAAP' profit or the company's own adjusted one, a loss, a tiny forecast) add anything? (4) When the price jumps in the last days, should you follow it or bet against it?

**Costs.** Every bet: $10, bought at the worst price anyone paid in the 2 hours after the signal, + 1c, + today's fee (charged on all bets, though half of these markets were still free). One bet per market. Why 2 hours: these markets are thin, and the gap between what buyers offer and what sellers ask is often 5-10c. A single sale makes the 'price' drop without anything being cheaper to buy.

## 1. Is the price fair?

| Yes price a day before the release | markets | Yes won | 3 days before: markets | Yes won |
|---|---|---|---|---|
| 0-20c | 65 | 15 in 100 | 41 | 10 in 100 |
| 20-40c | 128 | 33 in 100 | 123 | 36 in 100 |
| 40-60c | 180 | 54 in 100 | 175 | 54 in 100 |
| 60-70c | 139 | 70 in 100 | 159 | 60 in 100 |
| 70-80c | 215 | 76 in 100 | 260 | 79 in 100 |
| 80-90c | 362 | 85 in 100 | 366 | 87 in 100 |
| 90-100c | 419 | 92 in 100 | 346 | 91 in 100 |

Close to fair everywhere. Cheap Yes (under 40c) won a little more often than its price, on few markets. What that is worth at real buying prices:

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| buy Yes on everything, a day before | 718 | 483 | -$2.28 | -$1.80 | -$2.77 |
| buy No on everything, a day before | 753 | 231 | -$19.00 | -$19.66 | -$18.34 |
| buy Yes when it costs under 40c | 116 | 34 | -$12.07 | -$8.80 | -$15.34 |
| buy Yes at 40-80c | 344 | 231 | +$0.67 | -$4.40 | +$5.74 |
| buy No when Yes is 90c+ | 48 | 7 | -$29.77 | -$4.50 | -$55.06 |
| buy Yes on everything, 3 days before | 450 | 309 | -$5.89 | -$0.24 | -$11.53 |

## 2. The company's own record, and the kind of number

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| Yes on companies that beat every earlier time (2+ earlier markets) | 108 | 81 | +$3.34 | -$0.74 | +$7.38 |
| No on companies that beat every earlier time | 117 | 28 | -$27.26 | -$28.61 | -$25.92 |
| Yes on companies that missed last time | 133 | 71 | -$7.92 | -$16.60 | +$0.61 |
| No on companies that missed last time | 134 | 60 | -$19.75 | -$6.54 | -$33.00 |
| Yes on companies that missed 2+ times before | 60 | 33 | +$10.28 | +$24.92 | -$4.32 |
| Yes, official (GAAP) number | 298 | 169 | -$10.28 | -$12.52 | -$8.04 |
| Yes, adjusted (non-GAAP) number | 420 | 314 | +$3.41 | +$5.86 | +$0.97 |
| No, official number, Yes at 80-90c | 65 | 17 | +$38.32 | +$39.87 | +$36.81 |
| Yes, forecast is a loss | 93 | 50 | -$9.40 | +$6.74 | -$25.14 |
| No, forecast is a loss | 95 | 43 | -$8.10 | -$23.57 | +$7.05 |

A company's record on Polymarket (at most 5 earlier quarters) is already in the price. The one loud cell (official number at 80-90c) is one of many cells looked at, on about 100 markets.

## 3. The price jumped in the last days: follow it or bet against it?

Looks 48, 24 and 12 hours before the release. A jump = the Yes price moved 8c or more against three days earlier.

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| **bet against the jump** | 512 | 249 | +$6.03 | +$14.85 | -$2.78 |
| follow the jump | 505 | 255 | -$21.48 | -$27.63 | -$15.36 |
| against, price fell (buy Yes) | 296 | 177 | +$2.19 | +$13.56 | -$9.12 |
| against, price rose (buy No) | 260 | 90 | +$7.24 | +$8.87 | +$5.60 |
| against, if buying costs 3c extra, not 1c | 512 | 249 | -$0.06 | +$8.18 | -$8.30 |
| against, only the next 5 minutes' prices (too rosy, see Costs) | 110 | 48 | +$18.28 | +$40.64 | -$4.05 |
| against, worst price of the next 8 hours | 661 | 308 | -$3.86 | +$0.26 | -$7.97 |
| against, jumps of 5c+ | 646 | 309 | +$0.45 | +$9.30 | -$8.40 |
| against, jumps of 12c+ | 382 | 178 | +$6.00 | +$13.57 | -$1.56 |
| against, jump measured over 1 day | 404 | 196 | +$11.13 | +$2.29 | +$19.98 |
| against, jump measured over 7 days | 392 | 163 | -$8.07 | -$7.06 | -$9.08 |

By quarter (bet against the jump):

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| 2025 Q4 | 167 | 89 | +$12.32 | +$3.01 | +$21.52 |
| 2026 Q1 | 141 | 67 | +$21.01 | +$39.76 | +$2.58 |
| 2026 Q2 | 78 | 39 | -$1.57 | +$11.69 | -$14.80 |
| 2026 Q3 | 62 | 26 | -$18.95 | -$33.32 | -$4.63 |
| 2026 Q4 | 64 | 28 | -$9.97 | -$9.04 | -$10.90 |

Following a late jump is a clear loser: whoever chases the move overpays. Betting against it looks great if you pretend you can buy at the next trade's price, and shrinks to about nothing once you pay what sellers really ask. It also got weaker every quarter. Most of the 'jump' is one impatient trader paying the gap, not news.

## The exam

- **Earnings markets: bet against an 8c+ jump in the last 3 days (worst price of 2h +1c)**: 512 bets in 512 separate groups, +$6.03 per $100, luck range -$4.63 to +$16.70, worst case -$15.13 per $100, verdict **Ahead, but could be luck**.
- **Earnings markets: follow an 8c+ jump in the last 3 days**: 505 bets in 505 separate groups, -$21.48 per $100, luck range -$28.45 to -$14.51, worst case -$35.33 per $100, verdict **Losing**.
- **Earnings markets: buy Yes under 40c a day before the release**: 116 bets in 116 separate groups, -$12.07 per $100, luck range -$35.22 to +$11.07, worst case -$58.03 per $100, verdict **Behind, but could be bad luck**.
- **Earnings markets: buy Yes on companies that missed 2+ times before**: 60 bets in 60 separate groups, +$10.28 per $100, luck range -$15.56 to +$36.12, worst case -$41.89 per $100, verdict **Ahead, but could be luck**.
- **Earnings markets: buy No on official-number markets at 80-90c**: 65 bets in 65 separate groups, +$38.32 per $100, luck range -$13.03 to +$89.66, worst case -$63.47 per $100, verdict **Ahead, but could be luck**.

**Verdict: dropped, no track.** The price is fair, a company's record is in it, and the one pattern (bet against late jumps) is mostly the gap between buyers and sellers and has lost since April. Useful lesson for other digs: in thin markets, never price a buy at the next trade alone.

