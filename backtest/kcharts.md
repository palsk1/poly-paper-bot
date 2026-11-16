# Weekly chart bets (Netflix, Billboard, YouTube) on Kalshi and Polymarket

16 Nov 2026, `kcharts.py`. Jan's ask: something outside Twitter, and check both sites.

**Short answer: nothing to build. Both sites price these bets better than any free chart we can read.**

## What trades

- Kalshi runs about 190 repeating entertainment series. The big live ones are Netflix's weekly #1 show and #1 movie (US and global, plus the #2 spots), Billboard's #1 song and album, YouTube daily views and album sales. Kalshi's Spotify chart bets stopped in July 2026.
- Polymarket runs the same eight Netflix bets every week. They do trade: about $500,000 to $1 million a month in 2026 (the 13 Nov sweep said "mostly never trade" because most single titles get $0; the weeks as a whole get about $21,000 each). Billboard and Spotify weeks are smaller.

## Test 1: prices alone (Kalshi, all Netflix series, real asking prices + fee)

| when | always Yes | always No | Yes on the favourite | Yes on the others |
|---|---|---|---|---|
| 5 days before the close | -$9.27 (450) | -$4.32 (450) | -$6.02 (188) | -$18.73 (262) |
| 3 days before the close | -$4.45 (524) | -$5.39 (524) | -$2.61 (256) | -$13.42 (268) |
| 1 days before the close | -$3.75 (399) | -$5.43 (399) | +$0.66 (209) | -$35.95 (190) |

Per $100 staked, number of bets in brackets. Everything sits a few dollars under zero, which is the fee plus the gap between buyers and sellers. Last week's winner, new titles and price bands show nothing either. Polymarket's own price tables (`families.comb`) look the same or worse: Yes on long shots lost $25-75 per $100.
Billboard, YouTube views and album sales on Kalshi: same picture, and few hours with a tight enough price to bet at all.

## Test 2: Netflix's daily top 10 against the price

Netflix shows a daily top 10. whats-on-netflix.com keeps every day's US list back to 2020 (608 days from Jan 2025 downloaded, a few gaps). The weekly #1 is the title with the most views Monday to Sunday, so the daily lists should tell us who is ahead before the weekly list comes out.

- Even with all seven daily lists in hand, the title with the most days at #1 was the weekly winner in only 58 of 75 weeks for shows and about 50 of 78 for movies. The daily list ranks titles but hides how far apart they are.
- Kalshi's favourite one day before the close won about 8 times in 10. Miss score (lower is better): our daily-list chance 0.066, Kalshi's price 0.029. The price is more than twice as sharp.
- Betting where the two disagree by 10c or more, on Kalshi at the real asking price: -$4.71 per $100 on 398 bets. Exam: Behind, but could be bad luck.
- Same on Polymarket (worst price of the next hour + 2c): -$29.40 per $100 on 121 bets. Exam: Behind, but could be bad luck.

## Test 3: one site against the other

The same title in the same week on both sites, 507 pairs. Buying the cheap side where the prices are 10c+ apart: -$9.75 per $100 on 70 bets on Kalshi, +$7.01 on 23 bets on Polymarket. Together: Ahead, but could be luck. The gaps are rare and mostly stale last trades.

## Traps for next time

- Kalshi sometimes lists a title twice and pulls one copy days early: use the close time most markets of the event share (`kcharts.ev_close`), not the first close.
- Kalshi lists each season of a show as its own bet ("From: Season 1", "Season 2"), the daily list only says "From". Those are skipped.
- An event named 9 Nov is the list published 10 Nov for the week 2-8 Nov.
- whats-on-netflix.com answers `?dateselect=MM/DD/YYYY`; some days have no country lists. FlixPatrol blocks robots. Netflix's own weekly files (`/tudum/top10/data/all-weeks-countries.tsv`) cut off mid-download now and then, so retry.
- Too many probe runs at once use up GitHub's hourly allowance for the price store (each run fetches about 600 files), and then a run can't save its download.

Don't redo. A lead here would need real viewing numbers per day, which nobody publishes for free.
