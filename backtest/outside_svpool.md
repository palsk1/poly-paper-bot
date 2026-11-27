# Swedish-only money ideas: pool games, horse pools, lotteries, welcome bonuses (svpool, 27 Nov 2026)

Script: `outside/svpool.py` (data in the price store under `bt_cache/out_svpool/`). Money: 10.2 kronor = $1
(Riksbank, 25 Nov 2026: 10.28). Research only: no account, no bet, no key.

**Short answer for Jan:** none of the pool games or lotteries can be beaten from history. The public really does
over-pick favourites, on football and on horses, but the pools keep 35-40 öre of every krona and the mistake is
worth less than that. The only real money here is the welcome bonuses: about **$800-900 once**, never again, and it
is hand work, not a bot.

| Idea | Verdict | Best number | Can it run every day? |
|---|---|---|---|
| Stryktipset / Europatipset (13 matches) | Dropped | best system -$15 per $100 (241 rounds, Jan 2022-Nov 2026) | no, loses |
| Topptipset (8 matches) | Dropped | top rows got back 39c per $1 (2,722 rounds) | no, loses |
| ATG V75 / GS75 horse pools | Dropped | best system -$6.71 per $100 (429 rounds, Jan 2022-Nov 2026) | no, loses |
| Eurojackpot / Lotto / Vikinglotto | Dropped | never worth the ticket, even at the biggest jackpot | no |
| Welcome bonuses + Smarkets exchange | Worth doing once by hand (not a track) | about $800-900, one time | no, one-off |

## 1. Svenska Spel pool games (Stryktipset, Europatipset, Topptipset)

**How it pays (checked from the rules and the published payouts):** a row costs 1 kr. Of each krona, 65 öre go to
prizes; on Stryktipset/Europatipset that is split 13 right 40, 12 right 15, 11 right 12, 10 right 25, and 8 to a
fund. A level that would pay under 15 kr a row pays nothing and its money moves to next week's 13-right pot. No
13-right winner: the pot rolls over. One lone 13-right winner on Stryktipset is promised 10 million kr. Topptipset
(8 matches, one prize level) gives back about 70 öre per krona. So a player starts about 35 öre behind on every
krona and needs a big edge just to break even.

**Data:** Svenska Spel's public API (reachable from Actions, through the probe route) gives, per round, the
"Svenska folket" pick shares, the newspapers' tips, the opening odds, the money bet, and the real result with the
number of winners and the payout per level. Kept rounds with full data: Stryktipset 241 (Jan 2022-Nov 2026),
Europatipset 494 (Oct 2021-Nov 2026), Topptipset 2,722 (Apr 2021-Nov 2026). Sharp closing odds (Pinnacle closing,
football-data.co.uk) were matched to 2,531 Stryktipset and 3,259 Europatipset matches.

**What is true:**
- The public over-picks favourites by about 10 points. Stryktipset matches where the public put 10+ points more on a
  sign than the closing odds: closing odds said 51 in 100, the public 61 in 100, it really came in 49 times in 100
  (794 matches). The other way round (public 10 points under): closing 27, public 18, real 30 (474 matches).
  Europatipset shows the same.
- Closing odds forecast best, then opening odds, then the public (Stryktipset log loss 1.007 / 1.013 / 1.030).
- My payout model works: it guesses the number of winners per level from the public shares, and the median of real
  winners vs the model is about 1 to 1.

**Why it still loses:** a row's worth = chance it comes in x payout when it does. My model says the "value" rows
(signs the public under-picks) are worth 1.2-2.4 kr per krona. But almost all of that sits in 13-right hits that
happen about once in 100 rounds for a 144-row system. It can't be checked, and the real rounds say no:

| Stryktipset system, 241 rounds | Cost a round | Model said back per $1 | Really back per $1 | Exam |
|---|---|---|---|---|
| 144 rows, under-picked signs | 144 kr ($14) | 69c | 85c (one lucky 13-right) | Behind, but could be bad luck (-$15.05 per $100) |
| 144 rows, under-picked, no long shots | 144 kr ($14) | $1.17 | 20c | Losing (-$80 per $100) |
| 864 rows, same | 864 kr ($85) | 98c | 75c | Behind, but could be bad luck (-$24.59 per $100) |
| 144 rows, plain favourites | 144 kr ($14) | 40c | 41c | Losing (-$58.77 per $100) |

On the 130 rounds where every match had a sharp closing price the under-picked 144 rows got back only 33c per $1.
Rounds with rolled-over money ("carry in", 67 rounds) were no better. Europatipset (494 rounds, Oct 2021-Nov 2026):
best system 144 rows "under-picked, no long shots" -$3.04 per $100 (exam: Behind, but could be bad luck; first
half +$44, second -$51; more than half of what came back was a few 13-right hits), and even the model only gave it
79c per $1; plain favourites -$55 per $100, "Losing". Topptipset (2,722 rounds): its opening odds don't beat
the public at all (log loss 0.992 vs 0.993); the top 50 "value" rows came in 7 times where the odds expected 19
and the public shares expected 7, so the public was right and the old odds were wrong; real return 39c per $1.
Rounds with 250,000-500,000 kr extra money from Svenska Spel (199 rounds) gave the public 81c per $1, still a loss.

Exam (not written to the ledger, log=False): 4 systems scored, best -$15.05 per $100, worst case per $100 -$100.

**Four lines (rough guess):** best day: a loss (about -$2 a week on a $14 system); money needed $14-85 a week;
stops growing: never grows; bad day: the whole stake, -$14 to -$85 a round. **Sweden:** fine (state licence,
BankID, prizes tax free), 1 kr a row. **Verdict: dropped.**

## 2. ATG horse pools (V75, GS75; V86 / V64 not used)

**Data:** ATG's public racing API (from Actions): 510 rounds (V75 250, GS75 189, V85 71); 429 V75/GS75 rounds with
full data, Jan 2022-Nov 2026. Per horse: win-pool odds and the share of the V75 money on it; per round: money bet,
payout per level (7, 6 and 5 right, split 40/20/40, 65 öre back per krona; V75 row 50 öre, GS75 1 kr).

**What is true:** the big-game public over-bets favourites too. Horses with 10+ points more V75 money than their
win-odds chance: win odds said 37 in 100, V75 money 46 in 100, they won 36 times in 100 (645 horses). Under-bet
horses (10 points less): odds 30, money 21, real 34. The win-pool odds beat the V75 shares (log loss 1.756 vs 1.774).
The winners model is spot on (7-right winners: model median 301, real 308).

**Why it still loses:** the model itself says the best 200-600 row systems are worth 73-92 öre per krona, under
the stake even before luck. Real results (and these use the final odds and shares, which a bettor can't know when
he bets, so this is the best case):

| ATG system, 429 rounds | Model back per $1 | Really back per $1 | Exam |
|---|---|---|---|
| ~200 rows, favourites | 73c | -$11.50 per $100 | Behind, but could be bad luck |
| ~200 rows, under-bet horses | 89c | -$6.71 per $100 | Behind, but could be bad luck (first half -$50, second +$33) |
| ~600 rows, under-bet horses | 92c | -$26.35 per $100 | Losing |
| ~600 rows, like the public | 68c | -$12.60 per $100 | Behind, but could be bad luck |

The "-$6.71" one hangs on two jackpots (10,705 kr and 6,579 kr of profit). **Four lines (rough guess):** best day a
loss; money needed $10-60 a round; never grows; bad day the whole stake. **Sweden:** fine (ATG licence, tax free).
**Verdict: dropped.**

## 3. Lotteries with rollovers (math only, from the rules and jackpot history)

- **Eurojackpot:** 25 kr a row (over €2 in Sweden). Even at the €120 million cap one row is worth about 18-20 kr
  before splitting with other winners, about 18-20 kr x 0.75-0.8 after. Never worth 25 kr.
- **Vikinglotto:** 10 kr a row, about 40 öre back per krona, cap €25 million: about 6.6 kr a row at the cap. Never.
- **Lotto:** 4 kr a row, 1 in 6.7 million for the top prize. It would need a top prize of about 25-30 million kr
  after splitting; the biggest since 2019 were about 17-22 million kr (Jan 2022 was split 3 ways). Never recently.

**Verdict: dropped.** Ceiling lines: nothing to make; a bad day is the ticket.

## 4. Welcome bonuses and matched betting (the one real thing)

**Rules (spellagen 14 kap 9 §):** a licence holder may give a bonus only at a player's first game with it, so each
licence gives one bonus, once. There are about 55-66 licences for betting (counts differ by list, Oct-Nov 2026);
about two thirds offer a sports bonus, average max about 650 kr, average wagering 5.4 times, min odds about 1.8.
Several brands share one licence (one bonus for all of them). Winnings at Swedish-licensed sites are tax free.

**The exchange:** Smarkets is Sweden's only licensed betting exchange (Spelinspektionen register read 15 Nov 2026:
licence to 29 Jun 2027; one list said it lapsed in April, the newer register reading says it is live; check
before use). Commission 2 c per $1 of net winnings per market, and new players get 60 days without commission.
That makes matched betting possible: back at the bookmaker, lay the same thing on Smarkets, keep the bonus.

**What a bonus is worth (rough guess):**
- A free bet of 500 kr keeps about 375-400 kr after laying it off.
- A deposit bonus with wagering costs about 3 öre per krona wagered (bookmaker margin + commission). Example: 500 kr
  bonus, 6x on deposit+bonus = 6,000 kr wagered = about 180 kr lost, keep about 320 kr. Expekt's 1,500 kr at 15x
  the deposit (22,500 kr wagered) keeps about 800 kr.
- Examples seen in Nov 2026: bet365 1,500 kr credits (1x), Bethard 1,500 kr free bet (age 25+), Expekt 1,500,
  BetMGM 1,000, Interwetten 1,000, LeoVegas 600, ComeOn / Hajper / DBet / X3000 / Unibet / Betinia / Campobet 500
  each, Betsson 250, Betsafe / NordicBet 100, ATG and Svenska Spel 100 without wagering.
- Total over all of them: **about 8,000-9,000 kr, about $800-900, once.**

**Four lines (rough guess):** most it can make: $800-900 in total over 1-3 months (about $10-30 a day while it
lasts, then $0 forever); money needed: about $300-500 spread over the bookmaker and the exchange (the lay side
needs the liability); stops growing: each bonus has its own cap, so it simply runs out; bad day: a lay bet not
matched or a price jump before laying, about -$20 to -$50. Accounts that only take bonuses often get limited
afterwards, which doesn't matter for a one-off.
**Sweden:** BankID login and ID checks at every site (Jan does it himself, by hand); tax free on licensed sites only;
Spelpaus would block it all; some offers need age 25+. **Verdict: worth doing once by hand, interesting for later;
not a paper track** (nothing to test: the value is in the terms, and it never repeats).

## 5. Backward look: who wins Stryktipset over years, and how

- Long-term winners describe themselves as syndicates ("andelsspel"): big reduced systems (R- and M-systems) with
  thousands of rows, played mostly in jackpot and rollover rounds, and avoiding the favourites the public loves.
  One known pro claims +3.48 million kr net on andelsspel (self-reported, not checked). A 2012 Stockholm University
  thesis found no Stryktipset system that beats the stake.
- That matches the data: the only lean is "avoid the public's favourites", which this dig measured (about 10
  points), and it is worth less than the 35 öre take. What the syndicate story adds is selling shares in big systems
  for a fee, i.e. the winners are paid by their share buyers, not by the pool.
- Backward look on our rounds: the rounds that paid big were upsets where the public's favourite lost in 2-4
  matches. The model already prices those; the winners there were 1.2-1.7 times the model's guess (more people had
  the upset than independent picks predict), which makes the jackpot rows worth even less than the model says.

## Traps for the next person
- Svenska Spel's API drops the live odds after close; only opening odds remain. Join closing odds from
  football-data.co.uk by date + team names (`svpool.attach_close`, about 80 of 100 Stryktipset matches, 50 of 100
  Europatipset).
- Simulating the pool with random rows is useless: one 13-right draw dominates the average. Count the results
  exactly within 3 changes (`Round.row_ev`).
- A model that finds "value" only in near-impossible rows is not evidence. Check against the real payouts.
- ATG's odds and V75 shares in the API are final; a real bettor sees them earlier and worse.
