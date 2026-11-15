# Trump's single-event markets vs the same transcripts (speeches.py events)

15 November 2026. Second test with the Roll Call transcripts: "What will Trump say during the Arizona rally / the Fox interview / the signing?" 359 events, 5,479 finished markets with real trades. Paper only.

Record: in how many of his last 20 appearances (800+ of his own words, only days before the bet) did Trump say the word. Bets only on days before the event's day, $10 each, one per market, at the worst price of the next 2 hours, never better than the price at the signal, + 2c + fee.

| what | bets | events | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| always Yes | 3,421 | 258 | 1,330 | -$35.59 | -$31.34 | -$39.79 |
| always No | 3,421 | 258 | 2,091 | +$0.69 | -$2.52 | +$3.87 |
| Yes where the record is 15c+ above the price | 450 | 134 | 95 | -$54.11 | -$39.69 | -$68.36 |
| Yes, record 25c+ above | 274 | 87 | 50 | -$59.93 | -$49.57 | -$70.17 |
| Yes, record from the same kind of appearance | 557 | 166 | 149 | -$43.04 | -$25.71 | -$60.12 |
| No where the price is 15c+ above the record | 2,554 | 251 | 1,395 | +$2.80 | -$1.26 | +$6.83 |
| **No, record from the same kind of appearance** | 2,399 | 249 | 1,332 | +$5.41 | +$2.08 | +$8.72 |
| ... 4c extra instead of 2c | 2,399 | 249 | 1,332 | +$0.76 | -$2.67 | +$4.15 |
| ... 6c extra | 2,399 | 249 | 1,332 | -$3.39 | -$6.88 | +$0.07 |
| ... worst price of the next 6 hours | 2,586 | 256 | 1,450 | -$1.03 | -$4.33 | +$2.25 |

The bold rule by quarter: 2024 Q3 -$11.28, 2024 Q4 -$1.52, 2025 Q1 +$4.50, Q2 +$16.92, Q3 +$15.32, Q4 +$14.66, 2026 Q1 +$12.00, Q2 +$33.18, Q3 -$12.10, Q4 -$4.44.

Shared exam, bold rule: **Ahead, but could be luck** (+$5.41 per $100, luck range -$0.50 to +$11.32). Since April 2026: +$5.22 on 627 bets, luck range -$7 to +$18.

## What it means

It is the opposite of the weekly markets. For one single event, people pay far too much for Yes: buying Yes loses $36 per $100, and buying it where the speech record says "he says this a lot" loses even more ($54). He says a word often over a week, but one 20-minute signing is not a week. Buying No against the record is a little ahead, but it is gone at 4-6c worse prices and it lost in the last two quarters. The live track `word_no` already bets this side. Dropped, no track.
