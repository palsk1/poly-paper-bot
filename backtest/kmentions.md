# Kalshi "what will X say" markets (kmentions.py, 2026-11-14)

## Plain summary

- **What:** every finished Kalshi mention market since January 2025: 87,512 markets in 4,362 events (Trump, press briefings, sports announcers, earnings calls, TV shows). 73,099 of them traded 100+ contracts; for those we have the real buy and sell orders every hour and every trade.
- **Buying at the asking price:** Yes is priced about 3c too high on average, so Yes buyers lose $11.31 per $100 (Losing). Buying No comes out at -$0.12 per $100 (Behind, but could be bad luck): the fee and the gap eat the lean.
- **The word's own record barely helps on Kalshi.** Words listed 10+ times before are priced right. The Polymarket idea (No where Yes is 20c+ above the record) is +$2.83 per $100 since July (Ahead, but could be luck), and about $0 for words with 8+ earlier markets.
- **Two leads from the first 3,500 markets failed the fresh test** on the other 70,000 (section 1).
- **The waiting side was a real money-maker and is gone.** Selling Yes to people in a hurry made +$4.98 per $100 on 53,370 bets over two years (Looks real), but quarter by quarter it fell from about +$12 (late 2025) to +$0.67 since July 2026 (Ahead, but could be luck).
- **Verdict: nothing to build.** Dropped, no track. Kalshi's mention markets are fairly priced today for anyone but the Yes buyer.

## 1. The three rules fixed before the big download (`backtest/kmentions_prereg.md`)

Buy No at the real asking price plus Kalshi's fee, 24 hours before the event's first market closes, one bet per market.
"First 3,500" is where the rules were found. "The rest" was still downloading when they were written down.

| what | bets | events | per $100 | luck range | first half / second half | exam |
|---|---|---|---|---|---|---|
| T1 Earnings-call markets: buy No, first 3,500 | 255 | 191 | +$10.24 | +$0.91 to +$19.56 | +$11.56 / +$9.18 | Ahead, but could be luck |
| T1 Earnings-call markets: buy No, the rest | 5,112 | 485 | +$0.91 | -$1.23 to +$3.05 | +$3.66 / -$0.98 | Ahead, but could be luck |
| T2 Word listed only 1-2 times before (not earnings): buy No, first 3,500 | 109 | 96 | +$14.49 | +$2.26 to +$26.71 | +$11.32 / +$17.25 | Promising, needs more bets |
| T2 Word listed only 1-2 times before (not earnings): buy No, the rest | 2,465 | 804 | +$3.35 | +$0.25 to +$6.44 | +$7.88 / -$3.48 | Ahead, but could be luck |
| T3 Word listed 3+ times before (not earnings): buy No, first 3,500 | 844 | 586 | -$6.83 | -$11.54 to -$2.12 | -$6.10 / -$7.40 | Losing |
| T3 Word listed 3+ times before (not earnings): buy No, the rest | 15,964 | 1,495 | -$2.12 | -$3.44 to -$0.80 | -$1.55 / -$2.54 | Losing |

The two leads from the first 3,500 markets shrank to almost nothing on the rest. They were luck. Writing the rules
down first is what caught it.

## 2. Combing all of it: buying at the asking price

Same bet (24 hours before, real asking price plus fee), every market. "Off" = how many cents Yes was priced above how often it really won.

| group | bets | Yes priced too high by | buy No, per $100 | buy Yes, per $100 | buy No since July 2026 | buy Yes since July 2026 |
|---|---|---|---|---|---|---|
| all | 29,213 | +3.1c | -$0.12 | -$11.31 | -$2.09 | -$8.69 |
| earnings | 5,367 | +3.7c | +$1.33 | -$11.53 | -$0.81 | -$9.38 |
| sports | 11,789 | +1.6c | -$2.91 | -$8.14 | -$4.44 | -$5.81 |
| trump | 3,939 | +1.0c | -$3.76 | -$7.39 | -$1.88 | -$7.47 |
| other | 8,118 | +5.9c | +$4.41 | -$18.05 | -$1.81 | -$11.20 |
| Yes at 3-15c | 3,104 | +3.0c | +$0.80 | -$45.42 | +$0.62 | -$41.04 |
| Yes at 15-30c | 4,976 | +4.4c | +$1.64 | -$30.16 | -$1.25 | -$18.22 |
| Yes at 30-50c | 5,605 | +4.8c | +$1.79 | -$19.82 | -$1.38 | -$13.66 |
| Yes at 50-70c | 6,139 | +4.7c | +$2.43 | -$13.06 | -$2.44 | -$8.83 |
| Yes at 70-85c | 5,033 | +1.2c | -$8.40 | -$5.43 | -$9.93 | -$4.20 |
| Yes at 85-97c | 4,356 | -0.7c | -$25.57 | -$1.41 | -$13.49 | -$2.51 |
| word listed 0 times before | 6,926 | +4.6c | +$2.19 | -$14.58 | -$5.28 | -$5.83 |
| word listed 1-2 times before | 4,764 | +5.1c | +$3.75 | -$14.82 | -$1.30 | -$10.07 |
| word listed 3-9 times before | 4,634 | +3.6c | +$1.13 | -$12.56 | +$1.74 | -$12.67 |
| word listed 10+ times before | 12,889 | +1.3c | -$3.30 | -$7.83 | -$2.57 | -$7.89 |
| Yes 20c+ above the word's own record (3+ earlier) | 2,304 | +4.1c | +$4.53 | -$9.14 | +$2.83 | -$7.46 |
| Yes 20c+ below the word's own record (3+ earlier) | 1,328 | +2.6c | -$0.26 | -$15.78 | -$0.88 | -$13.90 |

| what | bets | events | per $100 | luck range | first half / second half | exam |
|---|---|---|---|---|---|---|
| always buy No | 29,213 | 2,299 | -$0.12 | -$1.16 to +$0.91 | +$1.88 / -$1.83 | Behind, but could be bad luck |
| always buy Yes | 29,213 | 2,299 | -$11.31 | -$12.30 to -$10.32 | -$13.25 / -$9.36 | Losing |
| No where Yes is 20c+ above the word's record, since July 2026 | 871 | 232 | +$2.83 | -$6.22 to +$11.88 | +$0.88 / +$4.78 | Ahead, but could be luck |

## 3. The waiting side: sell Yes to people in a hurry

Each hour (until 3 hours before the event), offer Yes 1c under the asking price for one hour, which is the same as bidding for No.
Filled only when 10+ Yes contracts were really bought at our price or higher. No fee. One bet per market.

| what | bets | events | per $100 | luck range | first half / second half | exam |
|---|---|---|---|---|---|---|
| sell Yes (hold No), all of 2025-2026 | 53,370 | 3,785 | +$4.98 | +$4.08 to +$5.87 | +$7.95 / +$2.22 | Looks real |
| sell Yes (hold No), since July 2026 | 13,834 | 990 | +$0.67 | -$0.96 to +$2.30 | +$1.26 / +$0.07 | Ahead, but could be luck |
| buy Yes 1c above the best buy order | 46,634 | 3,712 | -$10.00 | -$10.90 to -$9.10 | -$10.72 / -$9.19 | Losing |

Quarter by quarter (sell Yes, hold No):

| quarter | bets | per $100 | earnings | sports | Trump | other |
|---|---|---|---|---|---|---|
| 2025 Q1 | 705 | +$20.92 | +$7.97 (78) | - | +$16.72 (259) | +$26.14 (368) |
| 2025 Q2 | 1,267 | +$6.09 | +$7.18 (250) | - | +$7.55 (441) | +$4.64 (576) |
| 2025 Q3 | 1,970 | +$8.50 | +$10.86 (275) | +$2.30 (70) | +$0.10 (628) | +$13.56 (997) |
| 2025 Q4 | 7,642 | +$12.06 | +$14.86 (749) | +$8.75 (2,280) | +$7.71 (1,898) | +$16.62 (2,715) |
| 2026 Q1 | 12,759 | +$5.76 | +$8.05 (979) | +$3.31 (5,740) | +$3.95 (1,561) | +$8.96 (4,479) |
| 2026 Q2 | 15,193 | +$3.63 | +$9.92 (1,113) | +$0.39 (6,535) | +$1.01 (1,992) | +$7.25 (5,553) |
| 2026 Q3 | 9,433 | +$0.92 | -$5.52 (1,772) | -$1.74 (1,755) | +$4.35 (2,308) | +$3.00 (3,598) |
| 2026 Q4 | 4,401 | +$0.14 | +$1.05 (1,179) | - | -$3.29 (1,232) | +$1.73 (1,990) |

This side made real money in 2025 and it shrank every quarter of 2026 to about nothing. Other people's robots do this job now.
The paper fill is also kind to us: a real order would be undercut by those robots, and with 50+ contracts needed for a fill the last two quarters are behind.

## Traps found (for the next dig on Kalshi)

- **A market's own close time gives away the result.** Mention markets close early once the word is said. Count time back from the first close in the whole event, never from the market's own close.
- **Kalshi's live hourly-quote endpoint returns dollars in the field that used to hold cents.** Read through `yesno.k_candle` most quotes came out 100 times too small. `kmentions.load()` scales them back (a market whose quotes never pass 1c while its trades do).
- **Final volume is not a clean filter.** Cutting by a market's total volume looked like a huge lead (+$17 per $100 under 1,000 contracts); it is only because volume depends on how the market ended.
- **A random 1 in 20 sample of markets was not enough.** Two leads of +$10 to +$14 per $100 on 100-250 bets were gone on the other 19 in 20.
- **Holdout note:** this data runs to 13 Nov 2026, so it includes Kalshi mention markets that ended on or after 10 Nov. No test registered for 21 Dec uses Kalshi mention markets, so none of them is touched.

## 4. Kalshi's price as the outside number for Polymarket's mention markets

3,056 Polymarket mention markets have a Kalshi twin (same speech, same word list). The two sites settled the same way in 2,999 of them.
Each hour, where Polymarket's last trade was 5c / 10c / 15c away from Kalshi's real orders, buy Polymarket's side that Kalshi says is cheap,
at the worst Polymarket trade of the next hour + 2c + fee.

| what | bets | events | per $100 | luck range | first half / second half | exam |
|---|---|---|---|---|---|---|
| buy No, 5c+ apart | 522 | 202 | +$1.98 | -$6.62 to +$10.57 | +$9.83 / -$6.30 | Ahead, but could be luck |
| buy Yes, 5c+ apart | 332 | 164 | -$10.63 | -$19.62 to -$1.64 | -$10.31 / -$10.95 | Losing |
| buy No, 10c+ apart | 204 | 118 | +$0.63 | -$13.63 to +$14.89 | +$6.31 / -$5.95 | Ahead, but could be luck |
| buy Yes, 10c+ apart | 107 | 71 | -$5.78 | -$23.61 to +$12.05 | +$13.65 / -$22.67 | Behind, but could be bad luck |
| buy No, 15c+ apart | 91 | 71 | +$3.98 | -$17.08 to +$25.03 | +$7.91 / +$0.34 | Ahead, but could be luck |
| buy Yes, 15c+ apart | 45 | 34 | +$12.18 | -$24.22 to +$48.58 | +$35.17 / -$4.44 | Ahead, but could be luck |

Polymarket's mention prices already follow Kalshi's. Gaps of 10c+ are rare and buying them is a coin flip. Dropped.
Traps: with a looser match ("God or Evil" on Polymarket against "God" on Kalshi) this looked like +$11 per $100, because Polymarket's wider word list is a different bet.
And when Polymarket's price jumps 15c+ in the hour after the signal (the word was said), a bot would already have bought at the old price: pricing those bets at the new price, or dropping them, hides the losses (it looked like +$14 per $100).

## 5. The Polymarket `word_no` lead, split by whether Kalshi lists the same thing

The 533 history bets of `word_no` since April 2026 (`mentions.rule_bets`), sorted by what Kalshi had on offer.

| group | bets | events | won | per $100 | luck range | exam |
|---|---|---|---|---|---|---|
| Kalshi lists the same word for the same speech | 143 | 85 | 46 | -$7.44 | -$33.32 to +$18.44 | Behind, but could be bad luck |
| Kalshi has the speech, not this word | 137 | 75 | 56 | +$4.34 | -$17.28 to +$25.96 | Ahead, but could be luck |
| no Kalshi match found | 253 | 128 | 134 | +$34.01 | +$14.28 to +$53.74 | Promising, needs more bets |

Where Kalshi lists the same word, `word_no` has no lead: Polymarket's price is kept honest there. Its history profit sits in markets
without a Kalshi twin, above all "what will Trump / Elon post this week" and Big Brother episodes, plus two single events (the Xi and King Charles meetings).
"No Kalshi match found" is not the same as "Kalshi doesn't have it": the matcher misses Kalshi's weekly and monthly Trump markets.
So this is a warning about the live track, not a new rule: watch whether its live wins also come only from the post and TV-show markets.
