# 'What will Trump / Elon post this week' vs the words they really post (postwords.py)

Generated 2026-11-15T21:23:50Z. 861 finished markets in 53 weeks (Feb to Nov 2026), 648 with real trades. Outside number: every post with its text from Polymarket's own counter site (Trump 6857 posts since Jan 2026, Elon 14886 since Nov 2025). Paper only.

## 1. Can we read the result off the post text?

| account | Yes and we found the word | Yes but we did not | No and we found nothing | No but we found it |
|---|---|---|---|---|
| realDonaldTrump | 205 | 70 | 349 | 0 |
| elonmusk | 43 | 17 | 153 | 24 |

Trump: when the text shows the word, the market always paid Yes. But 1 Yes in 4 we never see: a third of his posts are pictures or videos with no text, and words in pictures count. Elon: the counter site leaves out his replies (they count for the market) and mixes in the text of posts he quotes (it does not count), so his text is a rough guide only.

## 2. Is there time to buy after the word is posted?

No. In 156 Trump markets where our text shows the word, only 4 had any trade under 93c from a minute after the counter site showed the post, $13 in total. The counter site is 2-3 minutes behind and the price is already at 95c+ by then. A speed game we don't play.

## 3. Does the word record beat the price?

Model: in how many of the 8 weeks before did the word show up in the account's own posts (pulled a little toward the middle), shrunk as the week runs out without the word. Looks only at posts from before the bet.

Bets: $10 each, one per market, at a 5-minute step with $5+ traded and before our text shows the word. Price paid: the worst price of the next 2 hours, never better than the price at the signal, + 2c + fee.

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| always Yes | 463 | 51 | 172 | -$43.99 | -$44.25 | -$43.74 |
| always No | 463 | 51 | 291 | -$13.00 | -$12.85 | -$13.15 |
| No where Yes is 15c+ above the record, any price | 265 | 45 | 130 | -$8.24 | -$4.08 | -$12.34 |
| No where Yes is 15c+ above the record, Yes at 60c+ | 166 | 43 | 44 | -$25.46 | -$14.37 | -$36.43 |
| **No where Yes is 15c+ above the record, Yes at 20-60c** | 148 | 41 | 107 | +$6.44 | +$9.31 | +$3.60 |
| same price band, no word record (always No at 20-60c) | 228 | 48 | 151 | -$4.03 | +$5.36 | -$13.37 |
| ... gap 10c+ | 168 | 45 | 120 | +$4.39 | +$11.42 | -$2.59 |
| ... gap 20c+ | 123 | 41 | 91 | +$9.81 | +$9.43 | +$10.18 |
| ... gap 30c+ | 77 | 31 | 55 | +$12.93 | +$18.47 | +$7.58 |
| ... Trump only | 114 | 30 | 78 | +$1.66 | +$6.93 | -$3.56 |
| ... Elon only | 34 | 11 | 29 | +$22.42 | +$19.45 | +$25.39 |
| ... bought before the week starts | 61 | 27 | 43 | +$2.82 | -$0.28 | +$5.79 |
| ... bought during the week | 100 | 37 | 70 | +$4.07 | +$16.13 | -$7.85 |
| ... 4c extra instead of 2c | 148 | 41 | 107 | +$3.34 | +$6.14 | +$0.56 |
| ... 6c extra | 148 | 41 | 107 | +$0.47 | +$3.23 | -$2.28 |
| ... worst price of the next 30 minutes | 103 | 37 | 71 | +$5.19 | +$8.27 | +$2.20 |
| ... worst price of the next 6 hours | 193 | 43 | 137 | +$2.01 | +$4.67 | -$0.60 |
| Yes where the record is 15c+ above the price | 29 | 16 | 17 | -$1.57 | -$28.74 | +$23.42 |

By quarter (the bold rule):

| what | bets | weeks | won | per $100 | first half | second half |
|---|---|---|---|---|---|---|
| 2026 Q1 | 21 | 3 | 17 | +$24.95 | +$14.41 | +$34.53 |
| 2026 Q2 | 46 | 11 | 32 | +$0.74 | +$0.47 | +$1.02 |
| 2026 Q3 | 75 | 25 | 54 | +$3.76 | +$11.77 | -$4.04 |
| 2026 Q4 | 6 | - | - | - | - | - |

Biggest wins and losses by word (the bold rule): Rigged +$27.02 (3), Sam / Altman +$22.23 (4), Uranium +$18.66 (6), Iran / Iranian +$17.51 (3), Free Tina Peters +$16.21 (2) ... Scam -$32.00 (6), President Xi -$28.66 (4), China -$23.93 (4), Russia -$19.42 (4), Border -$12.19 (4).

## 4. The shared exam

Bold rule: **Ahead, but could be luck**. 

## What it means

The word record helps a little: in the 20-60c band, always No loses about $4 per $100 and No only where the record disagrees makes about $6. But the band was picked after looking, Trump alone is about even, the profit is gone at 6c extra cost, and the live track `word_no` already bets on these markets with a similar idea. Not enough for a new track. Dropped.

