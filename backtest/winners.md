# Can we learn a strategy from the wallets that win? (2026-11-10, `winners.py`)

Research only. Jan's question: the exam checks ideas, but can anything help us *find* one? Idea: Polymarket shows
every wallet's trades, so study the proven winners and do what they do (not copy them: we arrive too late).

Data: 523,408 trades of $100 or more by 64,084 wallets in 16,028 finished Polymarket markets (2,559 events),
ending before 2026-11-10 (in-sample). Every trade counts as a bet held to the result, taker fee charged.
Runs: probe `win_run` and `win_drill` on 2026-11-10.

## 1. Steady winners don't show up

- 2,742 wallets had 10+ separate events. The exam's verdicts: 1 "Looks real", 88 "Promising", 1,442 "Ahead, but
  could be luck", 1,211 "Losing".
- Luck yardstick (the same trades with the wallet names dealt out at random): **28 of every 1,000 wallets look
  good by luck. Among the real wallets it's 32 of every 1,000.** About the same.
- Honest check: the 31 wallets that looked best in the first half (before 2026-05-27) then **lost $5.13 per $100**
  in the second half (404 events). Following them 5-65 minutes later lost $5.82. Everyone together lost $0.71.
- The one wallet that passed the full bar (0xaa7575ba, 56 events, +$6.38 per $100) had only 9 events in the second
  half. Not a pattern.

So "find the winners and learn their trick" is mostly a mirage in this data. It also explains why the 80 copy
tracks go nowhere. Limits: only $100+ trades, a sample of events, and a wallet with a small steady edge can hide
behind the luck bar. Fast bots that win a little on thousands of tiny trades are invisible here.

## 2. But the same data shows which kinds of bet paid, for anybody

Forget who made the bet. 300,494 buys had a real follow-up buy of the same answer 5-65 minutes later. Each is
counted as a $25 bet at that later price +1c + fee: what a slow bot could really get.

| What was bought | Separate events | Per $100 | Luck range | Verdict |
|---|---|---|---|---|
| Yes (first answer) | 2,352 | -$8.10 | -$11.58 to -$4.62 | Losing |
| No (second answer) | 2,446 | +$0.28 | -$1.81 to +$2.38 | Ahead, but could be luck |
| Under 10c | 700 | -$25.91 | -$50.66 to -$1.16 | Losing |
| 10-30c | 1,337 | -$13.10 | -$24.44 to -$1.75 | Losing |
| 30-50c | 1,505 | -$9.39 | -$14.55 to -$4.23 | Losing |
| 50-70c | 1,739 | -$1.58 | -$5.01 to +$1.85 | Losing |
| 70-90c | 2,206 | -$1.44 | -$3.47 to +$0.59 | Losing |
| 90-97c | 2,282 | -$0.75 | -$1.65 to +$0.15 | Losing |
| 97c+ | 2,251 | -$0.40 | -$0.77 to -$0.02 | Losing |

Every time-left band and every topic lost too (weather -$3.11, elections -$6.56, crypto price -$2.45).
**People who buy Yes pay about $8 per $100 for the thrill. People who buy No get about their money back.**

Then 256 detailed kinds (topic x Yes/No x price x time left, 30+ events each). 101 were ahead at all. With the luck
bar raised for all 282 looks, 5 passed, all of them No bets:

| Topic | Bet | Price | Time left | Bets | Events | Follower per $100 | Luck range | Worst case per $100 |
|---|---|---|---|---|---|---|---|---|
| crypto price | No | 70-90c | 3-7 days | 1,593 | 99 | +$11.95 | +$7.61 to +$16.30 | +$1.04 |
| other | No | 90-97c | over 30 days | 3,343 | 136 | +$3.76 | +$2.81 to +$4.70 | +$0.87 |
| other | No | 97c+ | over 30 days | 7,835 | 106 | +$0.98 | +$0.85 to +$1.12 | +$0.53 |
| other | No | 97c+ | 3-7 days | 4,805 | 124 | +$0.95 | +$0.86 to +$1.05 | +$0.43 |
| crypto price | No | 90-97c | 3-7 days | 1,625 | 98 | +$3.49 | +$2.25 to +$4.73 | +$0.25 |

These follow somebody's $100+ buy, and busy events count many times. So the next step replays them as plain rules.

## 3. The leads replayed as rules a bot could follow by itself

One bet per market: the first time the price is in the band with the right time left, wait 5 minutes, take the
next real $100+ buy of that answer within 6 hours, +1c + fee, $25 a bet. No bet if that price is more than 2c
outside the band. Luck bar: 282 tries.

| Rule | Bets | Won / lost | Typical cost | Per $100 | Luck range | Halves | Months ahead | Worst case per $100 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **"other" topics: No at 90-97c, over 30 days left** | 101 (64 events) | 100 / 1 | 93c, pays $1 | **+$5.45** | +$3.63 to +$7.28 | +$4.48 / +$6.49 | 11 of 11 | -$0.75 | Promising, needs more bets |
| **Crypto price: No at 70-90c, 3-7 days left** | 115 | 102 / 13 | about 80c, pays $1 | **+$6.95** | +$0.42 to +$13.48 | +$8.97 / +$4.89 | 9 of 9 | -$9.67 | Ahead, but could be luck |
| Crypto price: No at 90-97c, 3-7 days left | 195 (94 events) | 186 / 9 | 95c | +$0.53 | -$2.26 to +$3.31 | -$1.99 / +$2.60 | 6 of 10 | -$6.03 | Ahead, but could be luck |
| Control, the mirror: crypto price Yes at 70-90c | 74 (53 events) | 57 / 17 | 81c | -$5.38 | -$18.05 to +$7.29 | -$14.77 / +$5.04 | 7 of 10 | -$39.25 | Losing |

(The 97c+ kinds can't be replayed this way: one extra cent on a 99c bet eats the whole win.)

What the two leads are:
- **Boring No, far out.** Things like "Will Trump meet Putin in August?", "Will Montenegro be top 10 at
  Eurovision?", "Karoline Leavitt out by March 31?", bought at No 90-97c more than a month before the end. 100 of
  101 won. The price said about 7 should lose. It's sabsabinxz's "nothing ever happens" style, but **further from
  the end than any of our tracks look** (they stop at about 12 days).
- **Crypto "won't get there".** "Will Bitcoin reach / dip to / be above $X this week", No at 70-90c with 3-7 days
  left. Ahead in all 9 months, in "dip" and "reach" questions alike, so it isn't just crypto drifting one way.
  The mirror bet (Yes) loses.

## 4. Why this is a lead and not a strategy

- Found by looking at 282 kinds. Neither clears the full luck bar as a rule (worst case -$0.75 and -$9.67).
- The boring-No lead has 1 loss in 101. Three more losses would wipe it out. Its money is locked for a month or more.
- Only 1 signal in 12 had a $100+ buy near the band within 6 hours. A bot would buy from the order book, which
  this data can't show.
- Counting each calendar week once, the crypto lead's luck range touches $0 (-$0.28 to +$14.18, 32 weeks).
- Neither can be proven with live bets by 1 Jan: about 0.2 separate bets a day.

## 5. Suggested next step (Jan decides)

Register both rules now, exactly as written in section 3, and score them once on markets ending 2026-11-10 or
later (the holdout), together with the others on 21 Dec. That costs nothing and can't be bent afterwards. No live
track is added.
