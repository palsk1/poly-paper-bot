# More coins for the real Kalshi bot? (27 Nov 2026)

Tool: `khourly.py scan15 / fetch15 / grow15` (probe `khr_all15`). Printout: `bt_cache/khr/grow15.txt` in the price store. Rows: `bt_cache/khr/kc15/grow_rows.json.gz`.

## The short answer

- **Kalshi has only two 15-minute coins the real bot skips that really trade: NEAR and Zcash.** The others in the list (Cardano, Bitcoin Cash, TON, "Crypto Comparison") had no rounds at all in the last 2 days. "Coin Race" trades a little but has no single coin price to check against, so the rule can't run there.
- **NEAR and Zcash would add a little:** about +$0.72 a day at $4 bids, +$4.28 a day at $25, +$6.66 a day at $40, over 64 days. They make the same cents per $1 as the 7 coins the bot already has. Exam: "Promising, needs more bets", right at the luck bar. So: real, but small, and not proven.
- **Coins do lose together.** Rounds where 2 or more coins lost at once: 7 in 64 days. If losses were unrelated it would be about 0.4. A big crypto move breaks several coins in the same 15 minutes. Adding NEAR and Zcash added one such round; the 3 worst rounds stay the same (about -$118 at $40 bids, 3 coins at once).
- **Surprise: Bitcoin is the bot's weakest coin.** Over 64 days it made $0.00 at $4 bids and -$4.87 at $40, with 13 lost bids (the others have 3-7). The worst single day of any coin was Bitcoin's: -$99.83 at $40. The other 6 coins all made money. Not what we were asked, but worth knowing. Dropping it is Jan's call, and 13 losses is still a small number.

## How it was tested

The real bot's rule (kc_maker_safe_usd with the 2.3 cushion, `KALSHI_MIN_Z_USD`): from 5 to 1 minutes left, the leading side at 95c+, Binance at least 2.3 "steps" away from the line after moving Binance onto Kalshi's own price. Bid one tick in front of the best bid (or join it if there is no room), one bid a window, hold to the result.

Fills come from Kalshi's real trade list for each window (the method from `bigbets.kalshi_fill`): we get contracts sold at our price only if we stood in front of the line, plus everything sold below our price; trades where the buyer took our side don't count. 64 days, 24 Sep to 27 Nov, 9 coins, 17,427 bids.

The replay looks once a minute; the real bot looks every 15 seconds. So the replay finds fewer bids. Check against the real bot since 22 Nov: real 1,062 bids and 3,157 contracts bought, replay 841 bids and 2,174 contracts at $4 (+$7.55; the real bot shows about +$7.81). So the replay counts about two thirds of what the bot really buys. Treat these numbers as a floor.

## Every coin

| Coin | Bot has it? | Bids | Got anything ($4) | Lost (filled) | $4: P&L / a day / per $100 | $25: P&L / a day / per $100 | $40: P&L / a day / per $100 | Worst day at $40 |
|---|---|---|---|---|---|---|---|---|
| KXNEAR15M | NO | 2240 | 1553 | 5 | +$27.12 / +$0.42 / +$0.44 | +$161.32 / +$2.52 / +$0.43 | +$253.01 / +$3.95 / +$0.43 | -$36.44 |
| KXZEC15M | NO | 2002 | 1353 | 5 | +$18.87 / +$0.29 / +$0.35 | +$112.39 / +$1.76 / +$0.34 | +$173.43 / +$2.71 / +$0.34 | -$35.70 |
| KXBNB15M | yes | 1836 | 1280 | 4 | +$26.08 / +$0.41 / +$0.52 | +$156.99 / +$2.45 / +$0.51 | +$243.19 / +$3.80 / +$0.51 | -$35.35 |
| KXBTC15M | yes | 1663 | 1075 | 13 | +$0.08 / +$0.00 / +$0.00 | -$2.49 / -$0.04 / -$0.01 | -$4.87 / -$0.08 / -$0.01 | -$99.83 |
| KXDOGE15M | yes | 2030 | 1477 | 3 | +$36.49 / +$0.57 / +$0.62 | +$222.10 / +$3.47 / +$0.62 | +$351.76 / +$5.50 / +$0.61 | -$35.20 |
| KXETH15M | yes | 1734 | 1178 | 7 | +$13.26 / +$0.21 / +$0.28 | +$81.47 / +$1.27 / +$0.28 | +$128.75 / +$2.01 / +$0.28 | -$38.12 |
| KXHYPE15M | yes | 2018 | 1310 | 5 | +$21.41 / +$0.33 / +$0.42 | +$128.52 / +$2.01 / +$0.41 | +$199.44 / +$3.12 / +$0.40 | -$35.31 |
| KXSOL15M | yes | 1938 | 1397 | 4 | +$29.52 / +$0.46 / +$0.53 | +$181.01 / +$2.83 / +$0.53 | +$287.14 / +$4.49 / +$0.53 | -$55.93 |
| KXXRP15M | yes | 1966 | 1433 | 6 | +$25.73 / +$0.40 / +$0.45 | +$157.70 / +$2.46 / +$0.45 | +$250.26 / +$3.91 / +$0.45 | -$65.27 |
| **The 7 the bot has** | | 13185 | 9150 | 42 | +$152.56 / +$2.38 / +$0.42 | +$925.29 / +$14.46 / +$0.42 | +$1,455.66 / +$22.75 / +$0.41 | |
| **The new ones** | | 4242 | 2906 | 10 | +$45.98 / +$0.72 / +$0.40 | +$273.71 / +$4.28 / +$0.39 | +$426.44 / +$6.66 / +$0.39 | |
| **All together** | | 17427 | 12056 | 52 | +$198.55 / +$3.10 / +$0.42 | +$1,199.01 / +$18.74 / +$0.41 | +$1,882.10 / +$29.41 / +$0.41 | |

"Got anything" = bids that got at least one contract at $4. Every losing bid got its whole order (when you're wrong, sellers line up), winners got about 62-71 of 100 contracts asked for.

## Losing at the same moment

- The 7 the bot has: 42 lost bids in 34 rounds; rounds with 1 / 2 / 3+ coins losing: 28 / 4 / 2. Worst 3 rounds at $40: 2026-11-17 16:00 -$118.36 (ETH, SOL, XRP); 2026-09-28 05:45 -$117.32 (BTC, ETH, XRP); 2026-10-05 23:15 -$79.34 (BTC, ETH)
- All together: 52 lost bids in 43 rounds; rounds with 1 / 2 / 3+ coins losing: 36 / 5 / 2. Worst 3 rounds at $40: 2026-11-17 16:00 -$118.36 (ETH, SOL, XRP); 2026-09-28 05:45 -$117.04 (BTC, ETH, XRP); 2026-10-05 23:15 -$79.26 (BTC, ETH)
- If losses had nothing to do with each other (1 filled bid in 232 loses), rounds with 2+ coins losing would happen about 0.4 times in these 4026 rounds.

The 52 losing bids one by one (`grow_rows.json.gz`): spread over the whole 64 days, no data holes, every one fully filled. The shared rounds are big market moves: 28 Sep 05:45 (BTC, ETH, XRP), 5 Oct 23:15 (BTC, ETH), 17 Nov 16:00 (ETH, SOL, XRP). 9 of Bitcoin's 13 losses fell between 28 Sep and 17 Oct. Bitcoin also buys at a lower price on average (98.98c vs 99.2-99.3c for the rest), so its winners pay more but a busier crowd lets more bad windows through.

## Exam

=== EXAM: kc_maker_safe_usd on the 15-minute coins the real bot lacks (real trade lists, $25 bids) ===
Verdict: Promising, needs more bets
Bets: 2906 bets on 2326 events over 65 days. Counted as 2326 separate bets (bets on the same event count once).
Result: +$0.39 per $100 bet (total +$273.71 on $70020.25). Luck range +$0.21 to +$0.58.
Halves: first +$0.64, second +$0.15 per $100. Both ahead.
Luck bar: this is 1 of 278 tries. The luckiest of 278 worthless ideas would show about +$0.40 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$0.04. Below $0: not proven.
To prove it: about 618 more separate bets like these. At its pace (36.4 separate bets a day) that is around 2026-12-14.

=== EXAM: kc_maker_safe_usd replay on its own 7 coins (yardstick, real trade lists, $25 bids) ===
Verdict: Looks real
Bets: 9150 bets on 3405 events over 65 days. Counted as 3405 separate bets (bets on the same event count once).
Result: +$0.42 per $100 bet (total +$925.29 on $222625.19). Luck range +$0.27 to +$0.56.
Halves: first +$0.35, second +$0.48 per $100. Both ahead.
Luck bar: this is 1 of 278 tries. The luckiest of 278 worthless ideas would show about +$0.32 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): +$0.06. Above $0: good.


## Ceiling (rough guess)

| Setup | Most in an average day | Money needed | Where it stops growing | Bad day |
|---|---|---|---|---|
| NEAR + Zcash alone | +$0.72 at $4, +$4.28 at $25, +$6.66 at $40 | about 2 bids open at once on top of the bot's 7 | no wall seen up to $40 (same fill shares at every size) | one lost bid = the whole bid; worst day per coin about -$36 at $40 |
| All 9 coins | +$3.10 at $4, +$18.74 at $25, +$29.41 at $40 (replay; the real bot buys more) | up to 9 bids open at once: about $360 at $40 bids | not found up to $400 a bid in `backtest/kreal.md` | worst round about -$118 at $40 (3 coins in one round), worst day about -$100 |

## What it means

- Adding NEAR and Zcash is a small plus (a few dollars a day at $25-40 bids), not a big one. It also adds one more coin to lose in a bad round.
- The more useful find is that Bitcoin has been flat. Without it, the other 6 coins made +$1,460 at $40 bids in 64 days in this replay.
- Both changes are server settings, Jan's call. **27 Nov, Jan: "Paper test first then merge"**: paper tracks `kc_maker_safe_usd_new` (NEAR + Zcash) and `kc_maker_safe_usd_nobtc` (6 coins, no Bitcoin) run the real bot's exact rule (z 2.0, 2.3 on Kalshi's scale) at $10 bids. Compare with the real bot for 1-2 weeks.
- Don't redo: every 15-minute coin Kalshi lists has now been checked (27 Nov). New coins only if Kalshi lists more.
