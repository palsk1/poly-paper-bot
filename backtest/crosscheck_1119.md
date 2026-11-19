# Cross-data review, 19 Nov 2026 (`crosscheck.py`)

Jan: "Check if you find any new findings based on all data we have so far" and "will you do crosschecks, as
information in one strat or bot can maybe help another? Be thorough."

What was read: every finished paper bet in `state/tracks.json` (7,946 bets on 137 tracks; 1,860 different
Polymarket bets once copies of the same bet are counted once), the fast Kalshi day files (4,529 windows), and from
Jan's AWS server: the combo-house logs of 17-19 Nov (release `quoter-data`) and the speed-check logs of 17-18 Nov
(release `speed-data`). Not redone here: the Kalshi own-settle-price re-test, the combo house $5 question and the
Bitcoin 5-minute speed score (other threads).

Run it again: `python3 crosscheck.py tracks`, `python3 crosscheck.py legs quoter-*.jsonl.gz`,
`python3 crosscheck.py gap speed-*.jsonl.gz` (download the files from the two releases first).

## 1. Soccer draws are the best live Polymarket result, well above their history test

`soccer_draw`: 152 finished bets, 49 draws won. The prices we paid said about 40. Paper P&L +$36.12 on $209
(+$17.29 per $100 at $5 bets). Priced at $25 on the real book: **+$11.00 per $100**, exam verdict "Ahead, but could be
luck" (the history test said +$5.60). Data is clean: all 152 buys were re-priced later and the price held; 131 of
152 would have filled a full $25 bet. No day carried it (best day +$16, worst -$10). Its one fixed look stays 21 Dec.

## 2. The Pinnacle track is winning in the same corner, and the two tracks can talk to each other

`sharp_pinnacle`: 22 finished bets, 16 won. Polymarket's prices said 11, Pinnacle's fair prices said 13. At $25:
**+$59.92 per $100**, exam "Promising, needs more bets", but 22 bets is far too few. Its old history test (top 5
European leagues, 15 minutes before kickoff) found nothing; live it bets small leagues and NBA/NCAA games hours
before the start, a different place.

The link: both tracks win in small leagues, a day or hours before kickoff, where Polymarket's price is slow to
follow the sharp bookmaker. And they already bet the same games: 5 games overlap, and in one (Benfica vs Austria
Wien, 10 Nov) they bet **opposite sides**: `soccer_draw` bought the draw at 36c, and 30 minutes later
`sharp_pinnacle` bet against it because Pinnacle's fair draw price was only 33c. No draw: Pinnacle was right. `soccer_draw` never looks at
Pinnacle. Pinnacle prices the draw too (`sharp.py` already reads it), so every soccer draw bet could carry
Pinnacle's fair draw price. We can't test this on history (no old Pinnacle prices are saved). **Best candidate:**
record Pinnacle's fair draw price on each new `soccer_draw` bet (records only, the rule stays the same). By 21 Dec
that shows whether "the draw is cheaper on Polymarket than on Pinnacle" picks out the winners.

## 3. Kalshi patient buyer: the sports half matches its history, the price half loses

`kalshi_patient`, 410 finished bets, +$0.51 per $100:

| kind | bets | lost | per $100 |
|---|---|---|---|
| sports | 229 | 8 | +$2.48 |
| weather | 75 | 3 | +$1.47 |
| other | 41 | 2 | -$0.56 |
| crypto, stock index, oil/gold/gas prices | 65 | 8 | -$7.11 |

The history test said +$2.50 for sports before the game at 90-97c: live says +$2.48. The price markets hold 8 of the
21 losses: a patient bid there gets filled by people who just saw the price move (like `kc_maker_early`). Also: bets
whose market closes 2-24 hours after the order +$3.29 per $100 (277 bets); under 2 hours -$3.98; over a day -$6.57.
Found by looking at cuts, so it's a lean, not proof. The rule is locked for 1 Jan (PROTOCOL 5d): nothing changes, but
we know where to look on 1 Jan.

## 4. Kalshi 15-minute crypto: the Yes side held every loss, and Jan's server confirms the fix

`kc_maker_safe`: all 8 losses were Yes bets; its 327 No bets lost 0. The twin with the price-gap check,
`kc_maker_safe_usd`, is 664 won, 0 lost (+$0.58 per $100). That's what the 12 Nov dig predicted (Binance runs high, so
Yes looked safer than it was).

Jan's speed-check box records Binance, Coinbase and Chainlink every second. Binance sat **0.10-0.15% above**
Coinbase all day (middle 0.12%), and the gap moves: about 0.11% in the morning (UTC), 0.15% at 21-22 UTC. Chainlink
is almost the same as Coinbase. So a fixed correction would be wrong part of the day. The twin measures the gap fresh
for every window, which is the right way. No change needed.

## 5. Combo house x single markets: parlay buyers don't make single prices wrong (dropped)

From the server logs: 1,921 parlay legs with a known result (17-19 Nov). The single-market price at the request
said 997 should win; 990 did. Right in every price band and every bet type, and also for the legs parlay buyers
ask for most (100+ requests: price said 46, got 54, a few too many wins, likely luck). So there's no "bet against the
crowd's favorite parlay legs" trick. Dropped.

## 6. Crypto price markets lose for almost every slow Polymarket track

Across all Polymarket tracks, the 437 different bets on crypto price markets lost $138 (-$7.10 per $100). Most is
the frozen lab track `endgame_sell98` (its whole loss, -$50 of -$51, is crypto; elsewhere it's about even) and the
copied wallet tokor (-$118 for both copies). Weather lost about the same (-$7.70, mostly stopped tracks). Same lesson
as before: markets that follow a live price feed are where a 5-minute bot gets picked off. Nothing to change (lab is
frozen), but it backs up the "no crypto for slow bots" lesson.

## 7. Data checks

- Every live track's P&L adds up bet by bet (shares x price difference minus fees). Only the stopped Polymarket
  maker tracks don't split out their sell fees (their cash was right).
- The speed box's Polymarket feed reconnects 7-17 times a day ("slow consumer"), but the order books never went
  quiet for more than 20 seconds, so no holes in its data.
- Fast Kalshi days: too few flips (2 in 1,532 bets at z 4+) to say anything about time of day.
- No time-of-day or weekday pattern holds across tracks once copies are counted once.
