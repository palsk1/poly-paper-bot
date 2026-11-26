# Soccer draws vs the sharp bookies (drawsharp.py)

Generated 2026-11-26T22:02:54Z. Polymarket games before 10 Nov only (the games the draw rule was found on; the 21 Dec holdout from 10 Nov on is not touched). Bookmaker odds: football-data.co.uk. Every bet: Polymarket chart price 24h before kickoff +2c + today's sports fee (0.05), held to the result, like `digs_draws.md`. 'Per $100' = profit per $100 staked.

## Plain summary (26 Nov 2026)

- **Question (Jan):** does soccer_draw win more when the sharp bookie (Pinnacle) also says the draw is cheap on Polymarket? Then we could make the rule pickier.
- **Pinnacle keeps no free history**, so the past test uses Betfair Exchange, the other sharp price (football-data.co.uk, 10,320 games in 2026). The sharp bookies price draws right: 2,659 draws happened, they said 2,639.
- **Where a bookie price exists, Polymarket's draw sits right on it** (about 0.2c apart) and soccer_draw loses: -$1.90 per $100 on 1,877 bets. All of the rule's profit came from leagues with no free bookie history (Colombia, Brazil's 2nd league, Korea, Egypt, World Cup qualifiers, Libertadores...): +$10.95 per $100 on 2,370 bets.
- **The pickier rule (bookie says the draw is worth 1c+ more than Polymarket's price):** looked great at first (+$12.53 per $100, 116 bets), but most of that came from games where the bookie odds were taken after our bet. Done fairly: +$4.22 per $100 on 98 bets, one half losing, exam 'Ahead, but could be luck'. Not a real filter.
- **Live, right now (75 draws on Pinnacle and Polymarket):** Polymarket's draw ask sat about 0.7c ABOVE Pinnacle's fair price, dearer in 69 of 75, and 0 draws were 2c+ cheap. Same in the leagues that made the money. So a 'Pinnacle says cheap' rule would buy almost nothing.
- **What it means:** Pinnacle can't make soccer_draw pickier. If the draw lead is real, the sharp bookies miss it too, in the smaller leagues. The 21 Dec check (PROTOCOL 5) stays as written; this dig adds one secondary check written down now, before those games are looked at: `soccer_draw_nofree` (only leagues with no free bookie history, list `drawsharp.COVERED` + `BIG`).
- **Pinnacle note on live paper bets (built 26 Nov, Jan: 'Do it and merge'):** every paper soccer_draw bet now records Pinnacle's fair draw chance (`pin_fair`), records only. Score it with the 21 Dec check.
- **Ceiling (rough guess):** as it is, about 540 bets a month in history; at $2 a bet about +$50 a month on paper, worst drop -$158, 18 losses in a row. No-free-odds leagues only: about 280 a month, +$60 a month at $2, worst drop -$93. Half the games take only $12-25 (bigbets.md), so $5 bets would not all fit.

## 1. Do the sharp bookies price draws right?

Every 2026 game in the football-data files before 10 Nov: the bookie's draw chance (margin removed) added up, against the draws that really happened.

| odds | games | draws happened | bookie said | source mix |
|---|---|---|---|---|
| before the weekend (main divisions) | 6,316 | 1,611 | 1,622 | Betfair 5,672, average 482, Pinnacle 162 |
| at kickoff (all files) | 10,320 | 2,659 | 2,639 | Betfair 9,199, average 962, Pinnacle 159 |

Pinnacle's own columns are blank in 2026 (its feed closed July 2025), so this is mostly Betfair Exchange, the other sharp price.

## 2. The soccer_draw bets, split by league kind

4,538 draw bets (15-50c, 24h before). 1,877 matched a football-data game.

| group | bets | draws happened | Polymarket said | bookie said | per $100 |
|---|---|---|---|---|---|
| every bet | 4538 | 1374 | 1174 |  | +4.86 |
| big leagues (epl lal sea bun fl1 ucl uel) | 302 | 74 | 73 |  | -9.80 |
| other leagues with free bookie odds | 1866 | 535 | 483 |  | -0.70 |
| leagues with NO free bookie odds | 2370 | 765 | 618 |  | +10.95 |
| matched to a bookie price (kickoff odds) | 1877 | 530 | 484 | 488 | -1.90 |

Where a bookie price exists, Polymarket's draw price sits on it (median gap +0.16c at kickoff odds) and the rule loses after the 2c + fee. All of the profit is in leagues where no free bookie history exists.

## 3. The pickier rule: bookie fair draw at least X above Polymarket

'Before the weekend' odds are taken on Friday (weekend games) or Tuesday (midweek games). For Friday and Tuesday games that can be AFTER our bet, so those odds peek ahead. The honest row drops them. Kickoff odds always peek ahead (shown only to see the size of the peek).

| odds used | gap | bets | draws happened | Polymarket said | bookie said | per $100 | first half | second half |
|---|---|---|---|---|---|---|---|---|
| before the weekend, all days | any | 847 | 252 | 218 | 219 | +3.70 | +6.80 | +0.69 |
| before the weekend, all days | +0.0c+ | 480 | 140 | 119 | 124 | +4.73 | +5.25 | +4.16 |
| before the weekend, all days | +1.0c+ | 116 | 36 | 29 | 31 | +12.53 | +17.01 | +8.38 |
| before the weekend, all days | +1.5c+ | 55 | 21 | 14 | 16 | +37.18 | +46.87 | +30.71 |
| before the weekend, all days | +2.0c+ | 35 | 13 | 9 | 11 | +30.95 | +36.90 | +27.48 |
| before the weekend, no Fri/Tue games (honest) | any | 697 | 200 | 179 | 180 | +0.09 | +2.24 | -1.93 |
| before the weekend, no Fri/Tue games (honest) | +0.0c+ | 395 | 110 | 98 | 102 | +0.29 | +0.53 | +0.02 |
| before the weekend, no Fri/Tue games (honest) | +1.0c+ | 98 | 28 | 24 | 27 | +4.22 | -1.48 | +9.73 |
| before the weekend, no Fri/Tue games (honest) | +1.5c+ | 46 | 15 | 11 | 13 | +17.45 | +18.83 | +16.54 |
| before the weekend, no Fri/Tue games (honest) | +2.0c+ | 29 | 9 | 7 | 9 | +9.55 | +17.71 | +3.79 |
| at kickoff (peeks ahead) | any | 1877 | 530 | 484 | 488 | -1.90 | -6.46 | +3.13 |
| at kickoff (peeks ahead) | +0.0c+ | 1053 | 301 | 269 | 282 | +0.26 | -4.02 | +5.30 |
| at kickoff (peeks ahead) | +1.0c+ | 500 | 150 | 125 | 136 | +7.12 | -5.04 | +21.93 |
| at kickoff (peeks ahead) | +1.5c+ | 304 | 97 | 75 | 83 | +14.93 | +10.14 | +20.74 |
| at kickoff (peeks ahead) | +2.0c+ | 181 | 62 | 45 | 51 | +23.53 | +29.72 | +15.38 |

Exam (honest row, gap 1c+, 15 versions tried): **Ahead, but could be luck**, 98 bets, +4.22 per $100.

## 4. Live: Pinnacle's fair draw vs Polymarket's draw ask right now

| look | draws 15-50c | in the rule's 20-28h window | median Pinnacle minus ask | ask 2c+ under Pinnacle | ask above Pinnacle | no-free-odds leagues: median |
|---|---|---|---|---|---|---|
| 20261126T2113 UTC | 75 | 37 | -0.7c | 0 | 69 | -0.8c (47) |

## 5. Size on a $100-300 bank (history, chart price +2c + fee, no check that $2-5 really fits)

| version | bets a month | bet | profit a month | worst drop | longest run of losses |
|---|---|---|---|---|---|
| soccer_draw as it is | 536 | $2 | +49 | -$158 | 18 |
| soccer_draw as it is | 536 | $5 | +122 | -$396 | 18 |
| only leagues with no free bookie odds | 280 | $2 | +60 | -$93 | 15 |
| only leagues with no free bookie odds | 280 | $5 | +150 | -$233 | 15 |

