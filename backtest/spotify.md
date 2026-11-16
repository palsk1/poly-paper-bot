# Spotify's weekly #1 song: do the public daily play counts beat the price? (16 Nov 2026)

Tool: `spotw.py`. Short answer: **no. Everybody reads the same numbers. Dropped, no track.**

## The bets

- **Polymarket** runs "#1 song on US Spotify this week" and the same for the global list (plus #2 versions). 43 finished US events since December 2025, about $40,000 traded per event.
- **Kalshi** ran "Top song on Weekly Top Songs USA" (KXSPOTIFYW): 72 weekly events, February 2025 to 3 July 2026, about 4.9 million contracts. **Kalshi stopped all Spotify bets in July 2026** after someone pushed a song ("Earrings") to #1 on the daily list with bought fake plays and a $3.3 million bet paid out before Spotify removed them. Polymarket carried on.
- Spotify's week runs Friday to Thursday. The weekly list comes out on Friday.

## The outside number

Spotify publishes, every day, how many times each song in its top 200 was played. So by Wednesday anyone can add up Friday to Tuesday and see who is ahead.

- US daily top 50 with play counts, every day from 2019 to 17 Sep 2026: a public GitHub copy of Spotify's own charts.
- The newest month: kworb.net's song pages (they only show a song's last ~31 chart days).
- 406 full weeks. The rule of thumb is strong: the song ahead on the count wins the week in 306 of 406 after one day, 366 after three days, 399 after six.
- The winner of every Kalshi market we could check was the song with the most plays (57 of 57).

## Test 1: the count against the price

For each bet, at the hour a new day's count is surely public, a chance from the count (plays so far, the last day repeated for the days left, how far ahead of the best other song, new song or not; learned only from earlier weeks back to 2019).

| | Kalshi (42 weeks, 1,151 looks) | Polymarket US (30 weeks, 831 looks) |
|---|---|---|
| Miss score, our count (lower is better) | 0.0165 | 0.0228 |
| Miss score, the price | 0.0165 | 0.0160 |
| Bets where the two are 10c+ apart | 17 | 12 |
| Result per $100 | +$3.01, "Ahead, but could be luck" (first half +$31, second half -$28) | -$58.89, "Losing" |

The count and the price say the same thing almost always. In 72 + 43 weeks there were fewer than 30 real disagreements, and the price won them.

## Test 2: prices alone (Kalshi)

- Yes on long shots at 3-20c: 156 bets, 0 wins.
- No against those long shots (No at 80-97c): 21 bets, 21 wins, +$7.70 per $100. Too few bets, and Kalshi no longer lists these.
- Nothing else stands out.

## Test 3: the backward look (start from the upsets)

Winners that had been priced under 35c: 4 on Kalshi, 3 on Polymarket. All the same story: **a big new release leads after the Friday, fades day by day, and the steady old song passes it late in the week.** The price already expects that (new-song leaders are priced lower than their lead suggests). Three or four cases a year, nothing to build on.

## Bought plays

Since 2025 the leader after five days lost the week three times. One of them (week of 5 June 2026) was won by about 1,000 plays out of 12 million after the winner's last day jumped by 225,000 plays. That was the same month as the "Earrings" case. A plan built on "the count tells us who wins" loses exactly these weeks.

## Traps for the next dig

- kworb's song pages hold only the last ~31 chart days per song. Old days need another source.
- The sum of the seven daily counts is not always the official weekly winner in a close race (week of 24 April 2026: our sum said one song, Spotify's weekly list and both sites said the other, 2 in 100 apart).
- Global list: no free day-by-day archive found for 2025-26, so the global bets were not tested. Same public numbers, same traders, so no reason to expect a different answer.
- Polymarket's Christmas-week event and events with an "Other" answer don't line up with a plain Friday-Thursday week.
