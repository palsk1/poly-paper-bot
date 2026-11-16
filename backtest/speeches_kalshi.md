# The Trump weekly words rule on Kalshi (speeches.py kalshi)

Generated 2026-11-16T06:31:27Z. Kalshi runs the same "What will Trump say this week" markets: 1745 finished markets in 61 weeks, August 2025 to November 2026, with real hourly buy and sell quotes and every trade. A middle market trades about $23,000, four times Polymarket's. Paper only.

The rule is the one found on Polymarket, unchanged: count in how many of the 8 weeks before Trump said the word (Roll Call transcripts, only days already over), and buy Yes where that record is 15c+ above the price. Here the price is Kalshi's real sell offer at the end of an hour (offers with a gap over 15c to the best bid are skipped) + 1c + Kalshi's fee. $10 a bet, one per market. Kalshi opens these markets when the week starts, so there is no "before the week": the test buys in the first 12 hours, or at the first hour of the week that fits.

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| always Yes, first 12 hours | 1529 | 61 | 848 | -$10.56 | -$9.63 | -$11.49 |
| always No, first 12 hours | 1529 | 61 | 681 | -$23.35 | -$23.07 | -$23.64 |
| **Yes where the record is 15c+ above the offer, first 12 hours** | 123 | 46 | 66 | +$55.21 | +$36.56 | +$73.53 |
| **... the same, at the first hour of the week that fits** | 318 | 56 | 147 | +$33.80 | +$35.58 | +$32.03 |
| ... first 12 hours, gap 5c+ | 339 | 56 | 167 | +$25.46 | +$15.29 | +$35.56 |
| ... first 12 hours, gap 25c+ | 47 | 26 | 26 | +$103.29 | +$66.47 | +$138.48 |
| ... first 12 hours, 3c extra instead of 1c | 123 | 46 | 66 | +$42.97 | +$27.77 | +$57.90 |
| ... first 12 hours, 5c extra | 123 | 46 | 66 | +$33.19 | +$20.29 | +$45.87 |
| ... first 12 hours, 10c extra | 123 | 46 | 66 | +$15.02 | +$5.49 | +$24.38 |
| ... only hours 12 to 48 | 178 | 52 | 96 | +$33.23 | +$47.68 | +$18.83 |
| ... only hours 48 to 120 | 187 | 49 | 62 | +$14.18 | +$36.50 | -$7.84 |
| No where the offer is 15c+ above the record, first 12 hours | 571 | 59 | 172 | -$24.21 | -$25.04 | -$23.38 |

By quarter (first hour of the week that fits):

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| 2025 Q3 | 4 | - | - | - | - | - |
| 2025 Q4 | 91 | 13 | 42 | +$23.93 | +$25.70 | +$22.19 |
| 2026 Q1 | 66 | 13 | 39 | +$26.65 | +$25.15 | +$28.14 |
| 2026 Q2 | 69 | 14 | 31 | +$30.37 | +$18.52 | +$41.78 |
| 2026 Q3 | 71 | 11 | 26 | +$31.17 | +$4.50 | +$57.03 |
| 2026 Q4 | 17 | 4 | 5 | +$49.86 | +$121.25 | -$14.03 |

By the price paid (first hour that fits):

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| Yes at 0-20c | 86 | 38 | 22 | +$74.09 | +$87.13 | +$61.06 |
| Yes at 20-40c | 128 | 48 | 52 | +$16.58 | +$19.52 | +$13.65 |
| Yes at 40-60c | 75 | 41 | 50 | +$24.42 | +$28.79 | +$20.17 |
| Yes at 60-100c | 29 | 20 | 23 | +$12.39 | +$31.96 | -$5.86 |

## How much money fits

A bet only counts here if other people really bought Yes at our price or better in the 2 hours after the signal, and only for as many dollars as they bought.

| at most per bet | bets that found a seller | dollars bet | profit | per $100 | profit a month | losing months |
|---|---|---|---|---|---|---|
| $10 | 189 of 318 | $1,394 | +$481.43 | +$34.53 | +$30.65 | 4 of 16 |
| $25 | 189 of 318 | $2,531 | +$994.44 | +$39.30 | +$63.32 | 4 of 16 |
| $100 | 189 of 318 | $4,432 | +$2097.47 | +$47.33 | +$133.55 | 4 of 16 |

## The shared exam

First hour that fits: **Promising, needs more bets**, +$33.80 per $100, luck range +$12.70 to +$54.90, worst case per $100 -$14.67, 318 bets in 56 weeks. First 12 hours only: **Promising, needs more bets**, +$55.21 per $100, luck range +$19.29 to +$91.13.

## What it means

The rule was fixed on Polymarket and then run on Kalshi without changes, and it is ahead there too. That is the closest thing to a fresh test this idea has had. Kalshi adds about 20 bets a month to Polymarket's 10. Weak spots: the cheap offers are small (a third of the signals found no seller at all), a good part of the profit comes from long shots under 20c (22 wins in 86 tries, so long dry spells), and the later in the week the weaker it gets. Whether Jan may trade on Kalshi from Sweden is his to check. Trap found on the way: Kalshi's monthly markets looked like 29 wins of 29, because our saved quotes only cover a market's last 21 days, so a month-long market shows early hours only when it closed early, which means the word was said.

