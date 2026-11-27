# In-game "leader after a stage" bets in other sports (27 Nov 2026)

Tool: `stages.py`. Data: `bt_cache/stg/<sport>/` in the shared price store. Ask (coordinator, from Jan's "go crazy"
research round): tennis found a lead (the winner of set 1 at 50-80c on Kalshi is a little too cheap). Is there the
same kind of lead after a quarter, half, period, inning or map in other sports?

## Short answer

**No. Dropped, no track.** Across 13 sports and about 38,000 games, Kalshi's in-game prices right after a stage
are fair. Buying the leader loses about the fee, buying the trailer loses more.

- **The tennis rule carried over unchanged** (leader after the first stage, priced 50c to under 80c, 3 minutes
  later; maps: the moment Kalshi's map market closes), all 13 sports pooled: **9,294 bets, -$2.39 per $100**,
  both halves behind. The tennis detail that made it work there (the leader was also the pre-game favourite):
  **3,899 bets, -$3.45 per $100**, exam verdict **Losing**.
- **Backward look** (7,128 cuts: sport x stage x 1/3/10 minutes later x 6 price bands x leader or trailer x lead
  size): the average cut loses $4.28 per $100. 56 of 750 big-enough cuts are ahead in both halves, about what luck
  gives. The best one (NBA, after the 3rd quarter, the team down 1 to 6 points priced 20-35c: +$24.26 per $100 on
  173 bets) gets the exam's "Promising, needs more bets", but it is 1 of 7,403 tries, the luckiest worthless idea
  would show about +$54 per $100 on that many bets, its neighbours flip sign (down 7-10 points: -$1.50; same
  spot after the 2nd quarter: -$17), and it makes about one bet every 2-3 days. Luck. Dropped.
- Ceiling: none worth stating. At $25 a bet the pooled rule would lose about 60c a bet.

## What exists on Kalshi

| Sport | Game markets used | Stage markets on Kalshi | Bid-ask gap after stage 1 |
|---|---|---|---|
| NBA | 1,680 games (Oct 2025 - Nov 2026) | 1st / 2nd / 3rd / 4th quarter, 1st / 2nd half winner | 1c |
| WNBA | 367 | - | 1c |
| Men's college basketball | 6,240 | 1st half winner | 1c |
| Women's college basketball | 5,022 | - | 4c |
| NFL | 425 | every quarter and half | 1c |
| College football (top division only on ESPN) | 776 | quarters and halves | 1c |
| NHL | 1,866 | 1st / 2nd / 3rd period winner | 1c |
| MLB | 2,321 (2026 season) | - | 1c |
| CS2 | 6,758 matches | map winner (each map) | 3c |
| League of Legends | 2,139 | game winner (each game) | 2c |
| Dota 2 | 1,457 | map winner | 3c |
| Valorant | 1,765 | map winner | 3c |
| Call of Duty | 182 | map winner | 4c |

Clock and score: ESPN's free play-by-play (`site.api.espn.com/.../summary?event=`, readable from Actions, every
play with its wall-clock time and the score). Check: Kalshi's game market closes a median 1.7 minutes after
ESPN's last play, so ESPN's clock is right. Kalshi's own quarter markets close late (median 18-20 minutes after
the quarter), so they are no use as a clock in US sports. For esports the clock is Kalshi's map market closing
(it can only be late, never early). Prices: Kalshi's 1-minute real bid / ask; buys at the real ask + taker fee,
$25 a bet, held to the end; games where ESPN's final score and Kalshi's result disagree are dropped.

## The tennis rule, carried over (`stages.py carry`)

Per $100 bet, leader after the first stage at 50c to under 80c:

| Sport | First stage | All leaders | Leader was pre-game favourite | Leader was pre-game underdog |
|---|---|---|---|---|
| NBA | quarter 1 | 704 bets, -$3.46 | 438, -$3.81 | 266, -$2.88 |
| WNBA | quarter 1 | 151, -$7.51 | 101, -$3.56 | 50, -$15.41 |
| Men's college basketball | half 1 | 1,724, -$5.10 | 830, -$7.52 | 894, -$2.87 |
| Women's college basketball | quarter 1 | 640, -$1.08 | 370, -$0.24 | 265, -$2.29 |
| NFL | quarter 1 | 162, +$0.31 | 95, -$0.46 | 67, +$1.38 |
| College football | quarter 1 | 189, -$10.21 | 116, -$5.79 | 73, -$17.17 |
| NHL | period 1 | 794, -$4.33 | 356, -$2.25 | 438, -$6.01 |
| MLB | inning 1 | 814, -$2.53 | 413, -$4.28 | 401, -$0.74 |
| CS2 | map 1 | 2,304, -$0.67 | 665, -$3.10 | 1,627, +$0.32 |
| League of Legends | game 1 | 619, +$3.84 | 171, -$3.16 | 445, +$6.25 |
| Dota 2 | map 1 | 475, -$5.76 | 120, $0.00 | 351, -$7.83 |
| Valorant | map 1 | 662, -$0.39 | 203, +$3.66 | 457, -$2.29 |
| Call of Duty | map 1 | 56, +$7.06 | 21, +$3.80 | 34, +$6.48 |
| **All 13 pooled** | | **9,294, -$2.39** | **3,899, -$3.45 (Losing)** | **5,368, -$1.69** |

Later stages (`stages.py report <sport>`) look the same: after the half or the 3rd quarter, the 2nd period, any
inning, the leader at 50-80c sits between about -$7 and +$1 per $100 in the big samples (NBA, NHL, MLB, college
basketball), and the leader at 80-95c between -$4 and +$1. NFL after the 2nd and 3rd quarter showed +$6 to +$8 per
$100 (about 170 bets), while college football at the same spot showed -$14: two small samples pointing opposite
ways. League of Legends game 1 was +$7.49 in its first half and +$0.20 in its second.

## Why tennis and not the rest (a guess)

Tennis has a clean, slow-to-sink-in step (a set) and its lead lived in the women's main tour only. Team sports
are watched by far more money, with 1c gaps, and the leader's price already moves with every basket or run.
Esports have 2-4c gaps, which eat any small lead. Polymarket was not tested: it keeps no history of sell offers,
and the tennis replay there did worse than Kalshi.

## Traps

- Kalshi's quarter / half / period markets close 4-23 minutes after the stage really ended (median about 18):
  timing a bet from them in US sports would be slow, not dishonest.
- `/historical/markets` ignores filters on some calls: list a series by close window (`min_close_ts`), not the
  whole history, or a fetch takes an hour.
- A few League of Legends map tickers have no map number (`KXLOLMAP-T1KTR325`): skipped.
- ESPN's college football list is only the top division (`groups=80`); Kalshi lists about three times more games.

## Free re-check

NBA, after the 3rd quarter, 1 minute later: buy the team down 1 to 6 points if it costs 20c to under 35c on
Kalshi. Re-run `stages.py fetch nba` + `sweep` on games after 27 Nov 2026 at the end of the season if anyone asks;
expect about 60 bets by mid-January.
