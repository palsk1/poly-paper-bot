# Box office markets, and a sweep of repeating market families (boxoffice.py, families.py)

Generated 2026-11-13T13:29:31Z. Paper only. The holdout from 2026-11-10 is not in here.

## 1. The sweep: which families repeat, trade real money and settle on a public number?

Looked up by Polymarket tag (`python3 families.py peek <tags>`, probe `fam_<tags>`), 13 Nov 2026.

| family (Polymarket tag) | finished events / markets | traded per market (middle one) | settles on | verdict |
|---|---|---|---|---|
| Box office (`box-office`, id 51) | 305 / 1,593 | $14,500 | the-numbers.com, boxofficemojo.com | **tested here** |
| Earnings beats (`earnings`, id 1013) | 1,602 / 1,606 | $5,200 | company reports | tested 13 Nov (`earn.md`): fair |
| Mentions (`mention-markets`, id 100343) | 1,356 / 24,228 | small | video / transcript | tested 13 Nov (`mentions.md`): track `word_no` |
| YouTube (`youtube`, id 146) | 412 / 3,725 | $2,400 | youtube.com view counts | mostly MrBeast video views (about 170 events) and podcast mentions; **untested**, views need a counter we don't have history for |
| Rotten Tomatoes (`rotten-tomatoes`, id 101453) | 93 / 576 | $1,500 | rottentomatoes.com | untested, few events |
| Billboard (`billboard`, id 103077) | 101 / 1,478 | $330 | billboard.com | untested, thin |
| Spotify (`spotify`, id 102851) | 175 / 3,099 | $0 | Spotify charts | most markets never trade |
| Netflix (`netflix`, id 100407) | 431 / 7,657 | $0 | Netflix top 10 | most markets never trade |
| Awards (`awards`, id 18) | 756 / 14,898 | $0 | award shows | most markets never trade; census said about fair |
| Airdrops / token value (`airdrops`, `fdv`) | 50 / 260 and 109 / 800 | $109,000 and $42,500 | token prices | big money, one-off events, no repeating number to keep score of |
| AI (`ai`, id 439) / OpenAI (`openai`) | 785 / 8,372 and 315 / 2,477 | $1,500 / $1,300 | leaderboards, company news | mixed bag, a dig of its own (census: leaderboard underdogs, 64 events) |
| Google Search (`google-search`) | 15 / 566 | $0 | Google Trends | too few |

Box office was the best fit: every weekend, real money, and it settles on daily ticket numbers anyone can read.

## 2. Box office: can the public ticket numbers out-forecast the market?

Daily ticket sales of every movie from Box Office Mojo (1298 days saved). A simple forecast of a movie's 2nd or later weekend, built on weekends before October 2025 and checked on the ones after:

| what the forecast knows | half the time it misses by less than | 9 times in 10 by less than | weekends checked |
|---|---|---|---|
| last weekend + Monday-Wednesday + theater count (known Thursday) | 21 in 100 | 61 in 100 | 304 |
| the same + Thursday's number (known Friday) | 19 in 100 | 51 in 100 | 304 |
| Friday's number (known Saturday) | 10 in 100 | 28 in 100 | 304 |

Polymarket's brackets are about 10 in 100 wide ("between 20m and 23m"). A forecast that is usually off by 15-20 in 100 before the weekend can't pick a bracket, and even with Friday's number in hand it is off by about a bracket. The people trading these read the same numbers hours earlier from the trade press. No model bet was run: it would only be noise.

## 3. Is the price itself fair? (998 weekend markets in 208 events)

Markets close Monday 12:00 UTC after a Friday-Sunday weekend. How often Yes won, by price, at four moments:

| Yes price | Thursday noon, before the weekend | Saturday 00:00, previews known | Saturday 20:00, Friday known | Sunday 20:00, estimate out |
|---|---|---|---|---|
| 2-10c | 4 in 100 (153) | 5 in 100 (186) | 3 in 100 (144) | 0 in 100 (77) |
| 10-25c | 15 in 100 (181) | 13 in 100 (150) | 13 in 100 (102) | 18 in 100 (50) |
| 25-45c | 31 in 100 (122) | 31 in 100 (103) | 35 in 100 (84) | 33 in 100 (33) |
| 45-65c | 51 in 100 (35) | 46 in 100 (68) | 61 in 100 (54) | 43 in 100 (21) |
| 65-85c | 89 in 100 (27) | 86 in 100 (50) | 79 in 100 (43) | 78 in 100 (40) |
| 85-98c | 91 in 100 (22) | 97 in 100 (33) | 95 in 100 (42) | 100 in 100 (58) |

Fair, give or take. The one soft spot: brackets priced 65-85c before the weekend won more often than their price, on a few dozen markets. Bets, $10 each, bought at the worst price of the next 2 hours + 1c + today's fee:

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| Yes at 65c+ before the weekend | 34 | 30 | +$14.77 | +$21.15 | +$8.42 |
| Yes under 25c before the weekend | 111 | 13 | -$48.18 | -$47.77 | -$48.57 |
| No where Yes is under 25c | 95 | 82 | +$2.25 | +$0.95 | +$3.53 |
| Yes at 25-65c before the weekend | 94 | 37 | -$11.05 | +$2.22 | -$24.31 |
| Yes at 65c+ on Saturday evening (Friday known) | 48 | 39 | -$1.02 | +$1.94 | -$3.99 |
| bet against an 8c+ jump within a day | 290 | 104 | -$34.02 | -$39.96 | -$28.07 |
| follow an 8c+ jump within a day | 272 | 163 | -$4.66 | +$6.29 | -$15.59 |

Unlike the earnings markets, a late jump here is usually real news (a ticket number came out): betting against it loses badly, and following it is too late.

## The exam

- **Box office: buy Yes on brackets at 65c+ before the weekend**: 34 bets in 34 separate groups, +$14.77 per $100, luck range +$1.09 to +$28.46, worst case -$16.69 per $100, verdict **Ahead, but could be luck**.
- **Box office: buy Yes on brackets under 25c before the weekend**: 111 bets in 72 separate groups, -$48.18 per $100, luck range -$72.16 to -$24.20, worst case -$95.50 per $100, verdict **Losing**.
- **Box office: buy No where Yes is under 25c before the weekend**: 95 bets in 65 separate groups, +$2.25 per $100, luck range -$4.26 to +$8.77, worst case -$11.91 per $100, verdict **Ahead, but could be luck**.
- **Box office: bet against an 8c+ jump within a day**: 290 bets in 141 separate groups, -$34.02 per $100, luck range -$45.25 to -$22.78, worst case -$56.55 per $100, verdict **Losing**.
- **Box office: follow an 8c+ jump within a day**: 272 bets in 138 separate groups, -$4.66 per $100, luck range -$12.76 to +$3.45, worst case -$21.71 per $100, verdict **Behind, but could be bad luck**.

**Verdict: dropped, no track.** The market reads the ticket numbers better and sooner than a simple model, and the prices are fair. The favorite-bracket lean rests on too few bets to act on.

