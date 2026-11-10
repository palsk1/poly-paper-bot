# Poll averages vs approval and generic-ballot markets (polls.py)

**Verdict (2026-11-10): no strategy here. Dropped, no track.**

- Kalshi approval markets (RealClearPolitics, 2021-2026, ~4,100 strikes with real hourly bid/ask) guess the final number
  much better than a "the average barely moves" model. Betting the model loses $6 to $46 per $100.
- Polymarket weekly Silver Bulletin buckets (about 45 events, Oct 2025 - Oct 2026) look ahead on paper: +$7 to +$22 per $100,
  wrong-dates control loses. But the luck range includes zero at every horizon, the market still guesses better overall
  (score 0.10-0.12 vs the model's 0.12-0.16), and only 3-13 of every ~40 bets would have found a real seller near our
  price within 2 hours. The paper profit comes from a few cheap buckets that hit.
- Silver Bulletin revises its past numbers (0.14 points on average, 120 of 584 days by 0.25+). The first run used today's
  chart and looked better (+$68 per $100 at 3h); with the numbers as first published (old chart versions) most of that went away.
- VoteHub approval and generic-ballot markets list one strike a week, so the settle number can't be read from the results;
  too few events (22-38) to test anyway.
- Race markets vs polls/models: not re-tested. Kalshi's own study of the 2026 midterms (393 races) found its prices beat
  every polling average and model (Silver Bulletin, Split Ticket, Economist, DDHQ...). Elections are over until 2027-28.

Written by `python3 polls.py run` on 2026-11-10. Markets that closed before 2026-11-10 only (PROTOCOL.md holdout).

Model: the poll average the market settles on (RealClearPolitics, Silver Bulletin or VoteHub) can only move so far in a few days. We take its last value a bot could have known (the previous settled market's number, or Silver Bulletin's chart for the day before, counted as known at 12:00 UTC the next day) and spread it by how much it moved over the same number of days in the past (only past data). That gives a chance for every strike.

Bets: Kalshi at the real hourly ask (YES) or 1 minus the bid (NO) plus the taker fee; Polymarket at the history price + 2c + fee. One bet per event and time (the strike with the biggest gap), held to the result. 'Coin-flip side' = same markets, random side: what costs alone do. 'Wrong dates' = the model is given the average from 3 weeks earlier: a real edge must vanish there.

## Data checks

- KXTRUMPAPPROVE (rcp): 55 events with one settle value, 14 without (dropped)
- KXAPRPOTUS (rcp): 175 events with one settle value, 88 without (dropped)
- APRPOTUS (rcp): 0 events with one settle value, 0 without (dropped)
- KXAPRPOTUSD (rcp): 9 events with one settle value, 1 without (dropped)
- KXTRUMPPOLLDAILY (rcp?): 0 events with one settle value, 1 without (dropped)
- KXTRUMPVH (votehub): 0 events with one settle value, 22 without (dropped)
- KXVHAPRPOTUS (votehub): 0 events with one settle value, 0 without (dropped)
- KXVOTEHUBTRUMPUPDOWN (votehub): 0 events with one settle value, 38 without (dropped)
- KXGENERICBALLOTVOTEHUB (votehub_gb): 0 events with one settle value, 31 without (dropped)
- KXGENERICBALLOT (gb?): 0 events with one settle value, 1 without (dropped)
- KXSILVERAPPROVE (silver): 1 events with one settle value, 0 without (dropped)
- KXTRUMPFAV (fav?): 2 events with one settle value, 0 without (dropped)
- KX538APPROVE (538): 106 events with one settle value, 37 without (dropped)
- 538APPROVE (538): 0 events with one settle value, 0 without (dropped)
- Silver Bulletin revisions: first-published vs today's chart differ by 0.14 points on average, 120 of 584 days by 0.25+
- Silver Bulletin values used: first-published (chart versions), 586 days
- Polymarket: 52 events with one settle value, 27 without
- Silver Bulletin chart vs Polymarket results: 41 agree, 5 disagree
- known values: rcp 195, fav? 2, 538 33, silver 586
- strike x time rows: 5582 (wrong-dates: 5748)

## Who guesses better? (lower is better; every strike row)

| Family | Hours before | Rows | Model score | Market score |
|---|---|---|---|---|
| KX538APPROVE | 3 | 84 | 0.1061 | 0.0567 |
| KX538APPROVE | 12 | 86 | 0.1251 | 0.1299 |
| KX538APPROVE | 24 | 88 | 0.1229 | 0.1145 |
| KX538APPROVE | 48 | 91 | 0.1188 | 0.1037 |
| KX538APPROVE | 96 | 79 | 0.1213 | 0.1095 |
| KXAPRPOTUS | 3 | 491 | 0.0953 | 0.0717 |
| KXAPRPOTUS | 12 | 599 | 0.1006 | 0.0574 |
| KXAPRPOTUS | 24 | 597 | 0.1061 | 0.0724 |
| KXAPRPOTUS | 48 | 628 | 0.1023 | 0.0934 |
| KXAPRPOTUS | 96 | 573 | 0.0959 | 0.0943 |
| KXTRUMPAPPROVE | 3 | 352 | 0.0979 | 0.0529 |
| KXTRUMPAPPROVE | 12 | 352 | 0.0979 | 0.0703 |
| KXTRUMPAPPROVE | 24 | 352 | 0.0979 | 0.0815 |
| poly_rcp | 12 | 27 | 0.0149 | 0.0135 |
| poly_rcp | 24 | 30 | 0.0389 | 0.0268 |
| poly_rcp | 48 | 34 | 0.0337 | 0.0507 |
| poly_rcp | 96 | 36 | 0.0948 | 0.0583 |
| poly_silver | 3 | 176 | 0.1609 | 0.1002 |
| poly_silver | 12 | 209 | 0.1588 | 0.1131 |
| poly_silver | 24 | 217 | 0.1441 | 0.1151 |
| poly_silver | 48 | 235 | 0.1491 | 0.1196 |
| poly_silver | 96 | 242 | 0.1206 | 0.1245 |

## Betting the model (all families together)

### 3 hours before the close
- model beats price by 3c+: 135 bets on 135 releases, won 41, staked $48.11, P&L -$7.11 = -$14.78 per $100 (luck range -$29.86 to +$0.78); coin-flip side on the same markets -$10.39 per $100
  - first half -$21.15 per $100 (67 bets), second half -$8.39 (68 bets); 1c worse prices -$19.11 per $100
  - wrong dates: 138 bets on 138 releases, won 29, staked $46.18, P&L -$17.18 = -$37.20 per $100 (luck range -$53.63 to -$20.28); coin-flip side on the same markets -$11.49 per $100
- model beats price by 5c+: 129 bets on 129 releases, won 37, staked $44.47, P&L -$7.47 = -$16.80 per $100 (luck range -$33.58 to -$0.46); coin-flip side on the same markets -$9.35 per $100
  - first half -$26.44 per $100 (64 bets), second half -$7.58 (65 bets); 1c worse prices -$21.85 per $100
  - wrong dates: 135 bets on 135 releases, won 27, staked $44.15, P&L -$17.15 = -$38.84 per $100 (luck range -$55.19 to -$22.61); coin-flip side on the same markets -$10.86 per $100
- model beats price by 10c+: 113 bets on 113 releases, won 31, staked $36.27, P&L -$5.27 = -$14.54 per $100 (luck range -$33.32 to +$4.05); coin-flip side on the same markets -$8.51 per $100
  - first half -$15.80 per $100 (56 bets), second half -$13.31 (57 bets); 1c worse prices -$16.50 per $100
  - wrong dates: 125 bets on 125 releases, won 25, staked $38.35, P&L -$13.35 = -$34.80 per $100 (luck range -$52.08 to -$16.65); coin-flip side on the same markets -$10.02 per $100

### 12 hours before the close
- model beats price by 3c+: 171 bets on 171 releases, won 58, staked $71.05, P&L -$13.05 = -$18.37 per $100 (luck range -$29.52 to -$6.63); coin-flip side on the same markets -$9.60 per $100
  - first half -$30.48 per $100 (85 bets), second half -$6.93 (86 bets); 1c worse prices -$22.92 per $100
  - wrong dates: 182 bets on 182 releases, won 46, staked $66.30, P&L -$20.30 = -$30.62 per $100 (luck range -$44.81 to -$16.89); coin-flip side on the same markets -$9.60 per $100
- model beats price by 5c+: 165 bets on 165 releases, won 54, staked $67.22, P&L -$13.22 = -$19.67 per $100 (luck range -$32.48 to -$7.40); coin-flip side on the same markets -$9.80 per $100
  - first half -$33.02 per $100 (82 bets), second half -$6.91 (83 bets); 1c worse prices -$23.24 per $100
  - wrong dates: 181 bets on 181 releases, won 45, staked $66.12, P&L -$21.12 = -$31.95 per $100 (luck range -$45.61 to -$19.19); coin-flip side on the same markets -$9.59 per $100
- model beats price by 10c+: 138 bets on 138 releases, won 38, staked $53.43, P&L -$15.43 = -$28.87 per $100 (luck range -$42.31 to -$14.97); coin-flip side on the same markets -$9.24 per $100
  - first half -$41.60 per $100 (69 bets), second half -$15.47 (69 bets); 1c worse prices -$30.49 per $100
  - wrong dates: 171 bets on 171 releases, won 42, staked $60.84, P&L -$18.84 = -$30.96 per $100 (luck range -$43.76 to -$17.34); coin-flip side on the same markets -$9.14 per $100

### 24 hours before the close
- model beats price by 3c+: 182 bets on 182 releases, won 78, staked $87.84, P&L -$9.84 = -$11.20 per $100 (luck range -$21.81 to -$0.56); coin-flip side on the same markets -$7.24 per $100
  - first half -$25.10 per $100 (91 bets), second half +$3.65 (91 bets); 1c worse prices -$11.55 per $100
  - wrong dates: 192 bets on 192 releases, won 52, staked $69.71, P&L -$17.71 = -$25.40 per $100 (luck range -$37.51 to -$13.13); coin-flip side on the same markets -$6.12 per $100
- model beats price by 5c+: 172 bets on 172 releases, won 72, staked $81.81, P&L -$9.81 = -$11.99 per $100 (luck range -$23.10 to -$0.85); coin-flip side on the same markets -$7.36 per $100
  - first half -$24.99 per $100 (86 bets), second half +$2.19 (86 bets); 1c worse prices -$14.33 per $100
  - wrong dates: 187 bets on 187 releases, won 49, staked $66.75, P&L -$17.75 = -$26.60 per $100 (luck range -$39.32 to -$14.49); coin-flip side on the same markets -$6.08 per $100
- model beats price by 10c+: 142 bets on 142 releases, won 54, staked $64.39, P&L -$10.39 = -$16.13 per $100 (luck range -$29.40 to -$2.46); coin-flip side on the same markets -$6.91 per $100
  - first half -$32.10 per $100 (71 bets), second half +$3.30 (71 bets); 1c worse prices -$20.14 per $100
  - wrong dates: 181 bets on 181 releases, won 47, staked $63.81, P&L -$16.81 = -$26.35 per $100 (luck range -$38.44 to -$11.90); coin-flip side on the same markets -$6.10 per $100

### 48 hours before the close
- model beats price by 3c+: 146 bets on 146 releases, won 77, staked $75.39, P&L +$1.61 = +$2.14 per $100 (luck range -$9.21 to +$13.49); coin-flip side on the same markets -$6.13 per $100
  - first half -$10.43 per $100 (73 bets), second half +$17.37 (73 bets); 1c worse prices +$3.20 per $100
  - wrong dates: 154 bets on 154 releases, won 68, staked $64.95, P&L +$3.05 = +$4.70 per $100 (luck range -$7.27 to +$15.98); coin-flip side on the same markets -$5.45 per $100
- model beats price by 5c+: 137 bets on 137 releases, won 71, staked $70.40, P&L +$0.60 = +$0.85 per $100 (luck range -$11.14 to +$12.96); coin-flip side on the same markets -$6.01 per $100
  - first half -$9.45 per $100 (68 bets), second half +$13.38 (69 bets); 1c worse prices -$0.41 per $100
  - wrong dates: 148 bets on 148 releases, won 66, staked $62.52, P&L +$3.48 = +$5.57 per $100 (luck range -$6.32 to +$17.13); coin-flip side on the same markets -$5.40 per $100
- model beats price by 10c+: 119 bets on 119 releases, won 61, staked $61.11, P&L -$0.11 = -$0.18 per $100 (luck range -$12.97 to +$12.92); coin-flip side on the same markets -$5.86 per $100
  - first half -$11.49 per $100 (59 bets), second half +$13.90 (60 bets); 1c worse prices -$2.45 per $100
  - wrong dates: 132 bets on 132 releases, won 58, staked $55.96, P&L +$2.04 = +$3.65 per $100 (luck range -$10.03 to +$17.28); coin-flip side on the same markets -$5.40 per $100

### 96 hours before the close
- model beats price by 3c+: 137 bets on 137 releases, won 74, staked $73.20, P&L +$0.80 = +$1.10 per $100 (luck range -$8.38 to +$10.48); coin-flip side on the same markets -$5.15 per $100
  - first half -$0.64 per $100 (68 bets), second half +$2.71 (69 bets); 1c worse prices -$1.21 per $100
  - wrong dates: 145 bets on 145 releases, won 62, staked $59.72, P&L +$2.28 = +$3.82 per $100 (luck range -$6.77 to +$13.81); coin-flip side on the same markets -$4.70 per $100
- model beats price by 5c+: 128 bets on 128 releases, won 69, staked $68.32, P&L +$0.68 = +$1.00 per $100 (luck range -$9.73 to +$11.08); coin-flip side on the same markets -$5.19 per $100
  - first half -$0.98 per $100 (64 bets), second half +$2.88 (64 bets); 1c worse prices -$1.23 per $100
  - wrong dates: 136 bets on 136 releases, won 58, staked $55.33, P&L +$2.67 = +$4.83 per $100 (luck range -$6.70 to +$15.11); coin-flip side on the same markets -$4.73 per $100
- model beats price by 10c+: 81 bets on 81 releases, won 41, staked $40.64, P&L +$0.36 = +$0.89 per $100 (luck range -$14.29 to +$14.55); coin-flip side on the same markets -$5.49 per $100
  - first half -$7.25 per $100 (40 bets), second half +$9.16 (41 bets); 1c worse prices +$2.64 per $100
  - wrong dates: 121 bets on 121 releases, won 52, staked $49.51, P&L +$2.49 = +$5.03 per $100 (luck range -$5.98 to +$15.35); coin-flip side on the same markets -$4.80 per $100

## By family (5c+ gap)

- KX538APPROVE, 3h: 4 bets on 4 releases, won 0, staked $2.18, P&L -$2.18 = -$100.00 per $100; coin-flip side on the same markets -$32.01 per $100; first half -$100.00 per $100 (2 bets), second half -$100.00 (2 bets)
- KX538APPROVE, 12h: 10 bets on 10 releases, won 5, staked $4.99, P&L +$0.01 = +$0.20 per $100 (luck range -$49.64 to +$48.21); coin-flip side on the same markets -$11.31 per $100; first half -$2.68 per $100 (5 bets), second half +$4.85 (5 bets)
- KX538APPROVE, 24h: 11 bets on 11 releases, won 4, staked $4.52, P&L -$0.52 = -$11.60 per $100 (luck range -$60.88 to +$41.63); coin-flip side on the same markets -$4.96 per $100; first half -$20.54 per $100 (5 bets), second half -$8.16 (6 bets)
- KX538APPROVE, 48h: 12 bets on 12 releases, won 5, staked $5.15, P&L -$0.15 = -$2.95 per $100 (luck range -$52.36 to +$47.68); coin-flip side on the same markets -$5.07 per $100; first half -$4.72 per $100 (6 bets), second half -$1.74 (6 bets)
- KX538APPROVE, 96h: 12 bets on 12 releases, won 4, staked $4.53, P&L -$0.53 = -$11.68 per $100 (luck range -$46.20 to +$6.83); coin-flip side on the same markets -$4.60 per $100; first half -$29.18 per $100 (6 bets), second half -$3.75 (6 bets)
- KXAPRPOTUS, 3h: 41 bets on 41 releases, won 10, staked $14.61, P&L -$4.61 = -$31.53 per $100 (luck range -$59.05 to -$2.35); coin-flip side on the same markets -$14.38 per $100; first half -$47.24 per $100 (20 bets), second half -$14.58 (21 bets)
- KXAPRPOTUS, 12h: 69 bets on 69 releases, won 15, staked $28.03, P&L -$13.03 = -$46.48 per $100 (luck range -$65.49 to -$28.68); coin-flip side on the same markets -$15.34 per $100; first half -$55.02 per $100 (34 bets), second half -$35.84 (35 bets)
- KXAPRPOTUS, 24h: 80 bets on 80 releases, won 27, staked $41.11, P&L -$14.11 = -$34.32 per $100 (luck range -$50.02 to -$17.25); coin-flip side on the same markets -$10.21 per $100; first half -$32.18 per $100 (40 bets), second half -$36.81 (40 bets)
- KXAPRPOTUS, 48h: 77 bets on 77 releases, won 41, staked $43.69, P&L -$2.69 = -$6.15 per $100 (luck range -$20.46 to +$8.46); coin-flip side on the same markets -$7.01 per $100; first half -$16.05 per $100 (38 bets), second half +$5.71 (39 bets)
- KXAPRPOTUS, 96h: 75 bets on 75 releases, won 42, staked $41.07, P&L +$0.93 = +$2.27 per $100 (luck range -$12.07 to +$14.99); coin-flip side on the same markets -$5.59 per $100; first half +$0.78 per $100 (37 bets), second half +$3.53 (38 bets)
- KXTRUMPAPPROVE, 3h: 42 bets on 42 releases, won 12, staked $14.51, P&L -$2.51 = -$17.28 per $100 (luck range -$46.87 to +$11.76); coin-flip side on the same markets -$5.73 per $100; first half +$6.03 per $100 (21 bets), second half -$36.75 (21 bets)
- KXTRUMPAPPROVE, 12h: 41 bets on 41 releases, won 17, staked $19.37, P&L -$2.37 = -$12.24 per $100 (luck range -$31.33 to +$4.85); coin-flip side on the same markets -$4.75 per $100; first half +$1.63 per $100 (20 bets), second half -$23.91 (21 bets)
- KXTRUMPAPPROVE, 24h: 36 bets on 36 releases, won 17, staked $16.57, P&L +$0.43 = +$2.60 per $100 (luck range -$18.26 to +$25.52); coin-flip side on the same markets -$4.96 per $100; first half +$13.74 per $100 (18 bets), second half -$9.99 (18 bets)
- poly_rcp, 12h: 2 bets on 2 releases, won 0, staked $0.16, P&L -$0.16 = -$100.00 per $100; coin-flip side on the same markets -$3.85 per $100; 
- poly_rcp, 24h: 4 bets on 4 releases, won 3, staked $2.42, P&L +$0.58 = +$23.78 per $100; coin-flip side on the same markets -$4.26 per $100; first half -$100.00 per $100 (1 bets), second half +$41.93 (3 bets)
- poly_rcp, 48h: 6 bets on 6 releases, won 5, staked $3.44, P&L +$1.56 = +$45.41 per $100 (luck range +$17.50 to +$72.94); coin-flip side on the same markets -$4.43 per $100; first half +$18.34 per $100 (2 bets), second half +$54.23 (4 bets)
- poly_rcp, 96h: 6 bets on 6 releases, won 1, staked $2.11, P&L -$1.11 = -$52.68 per $100 (luck range -$100.00 to -$5.21); coin-flip side on the same markets -$4.23 per $100; first half -$100.00 per $100 (2 bets), second half -$36.64 (4 bets)
- poly_silver, 3h: 42 bets on 42 releases, won 15, staked $13.18, P&L +$1.82 = +$13.84 per $100 (luck range -$15.12 to +$45.15); coin-flip side on the same markets -$4.50 per $100; first half +$25.84 per $100 (21 bets), second half +$7.03 (21 bets)
- poly_silver, 12h: 43 bets on 43 releases, won 17, staked $14.67, P&L +$2.33 = +$15.86 per $100 (luck range -$18.61 to +$52.61); coin-flip side on the same markets -$4.49 per $100; first half +$31.73 per $100 (21 bets), second half +$4.66 (22 bets)
- poly_silver, 24h: 41 bets on 41 releases, won 21, staked $17.18, P&L +$3.82 = +$22.21 per $100 (luck range -$4.09 to +$47.53); coin-flip side on the same markets -$4.52 per $100; first half +$21.40 per $100 (20 bets), second half +$22.83 (21 bets)
- poly_silver, 48h: 42 bets on 42 releases, won 20, staked $18.13, P&L +$1.87 = +$10.34 per $100 (luck range -$16.47 to +$33.01); coin-flip side on the same markets -$4.63 per $100; first half +$17.48 per $100 (21 bets), second half +$1.13 (21 bets)
- poly_silver, 96h: 35 bets on 35 releases, won 22, staked $20.61, P&L +$1.39 = +$6.76 per $100 (luck range -$13.06 to +$26.88); coin-flip side on the same markets -$4.71 per $100; first half -$22.57 per $100 (17 bets), second half +$29.68 (18 bets)

## Polymarket real-fill check (5c+ gap): only bets where a real buyer paid near our price within 2 hours

- poly_rcp, 12h: 1 of 2 bets fill; filled: 1 bets on 1 releases, won 0, staked $0.05, P&L -$0.05 = -$100.00 per $100; coin-flip side on the same markets -$3.85 per $100
- poly_rcp, 24h: 1 of 4 bets fill; filled: 1 bets on 1 releases, won 1, staked $0.68, P&L +$0.32 = +$47.31 per $100; coin-flip side on the same markets -$5.47 per $100
- poly_rcp, 48h: 2 of 6 bets fill; filled: 2 bets on 2 releases, won 2, staked $0.91, P&L +$1.09 = +$119.78 per $100; coin-flip side on the same markets -$3.85 per $100
- poly_rcp, 96h: 0 of 6 bets fill; filled: none
- poly_silver, 3h: 11 of 42 bets fill; filled: 11 bets on 11 releases, won 2, staked $1.73, P&L +$0.27 = +$15.61 per $100 (luck range -$100.00 to +$238.79); coin-flip side on the same markets -$4.16 per $100
- poly_silver, 12h: 13 of 43 bets fill; filled: 13 bets on 13 releases, won 6, staked $4.75, P&L +$1.25 = +$26.35 per $100 (luck range -$32.20 to +$108.47); coin-flip side on the same markets -$4.17 per $100
- poly_silver, 24h: 6 of 41 bets fill; filled: 6 bets on 6 releases, won 4, staked $2.72, P&L +$1.28 = +$47.06 per $100 (luck range +$0.00 to +$83.83); coin-flip side on the same markets -$4.15 per $100
- poly_silver, 48h: 3 of 42 bets fill; filled: 3 bets on 3 releases, won 1, staked $1.35, P&L -$0.35 = -$25.91 per $100; coin-flip side on the same markets -$4.44 per $100
- poly_silver, 96h: 5 of 35 bets fill; filled: 5 bets on 5 releases, won 5, staked $3.14, P&L +$1.86 = +$59.41 per $100 (luck range +$30.00 to +$121.38); coin-flip side on the same markets -$4.47 per $100

## By price paid (all hours, 5c+ gap)

- paid 0-20c: 194 bets on 117 releases, won 15, staked $19.80, P&L -$4.80 = -$24.25 per $100 (luck range -$61.22 to +$13.10); coin-flip side on the same markets -$3.78 per $100
- paid 20-50c: 179 bets on 108 releases, won 51, staked $64.22, P&L -$13.22 = -$20.58 per $100 (luck range -$37.03 to -$2.10); coin-flip side on the same markets -$8.07 per $100
- paid 50-80c: 288 bets on 161 releases, won 173, staked $187.80, P&L -$14.80 = -$7.88 per $100 (luck range -$17.51 to +$0.64); coin-flip side on the same markets -$9.40 per $100
- paid 80-100c: 70 bets on 55 releases, won 64, staked $60.40, P&L +$3.60 = +$5.95 per $100 (luck range -$0.55 to +$11.89); coin-flip side on the same markets -$9.62 per $100


