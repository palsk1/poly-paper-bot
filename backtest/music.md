# Music chart bets vs outside chart data (24 Nov 2026, `music.py`)

Paper research only. Jan asked for deep digs in new areas; the earlier music digs used prices only (`families_comb2.md`) or Spotify's weekly #1 (`spotify.md`). This one tries outside knowledge: Spotify's daily US plays for the Billboard Hot 100 #1, and HITS Daily Double's weekly album numbers and midweek forecast for the album-sales bets.

## Ceiling first (rough guess, only for the one lead)

1. **Most in an average day:** about $2 (about $13 a week), only on Saturdays.
2. **Money needed:** about $125 (up to 5 bets of $25 on one Saturday, back on Sunday).
3. **Where it stops growing:** about $25-50 a bet. Half the bets had only $35 or less sold at our price in the next 2 hours.
4. **Bad day:** about -$50 (two albums missing on the same Saturday; the worst album in history lost $27 at $25 a bet).

## What exists

| Bet | Site | History | Traded | Settles on |
|---|---|---|---|---|
| Album first-week units ladder ("FRESH above 63,000 units?", `KXALBUMEQUIV`) | Kalshi | 99 albums, May-Nov 2026 | $7.9 million | Luminate (Billboard's number), Sunday |
| Pure album sales ladder (`KXPUREALBUMS`) | Kalshi | 84 albums | $1.9 million | Luminate |
| Billboard Hot 100 #1 (`KXTOPSONG`) | Kalshi | 108 weeks | $4.5 million | Billboard |
| Billboard 200 #1 (`KXTOPALBUM`) | Kalshi | 100 weeks | $2.9 million | Billboard |
| Hot 100 #2, top 10, #1 this month, Billboard position | Kalshi | 2025-2026 | $1-6 million each | Billboard |
| Daily / weekly Spotify charts (`KXSPOTIFYD` $21.8 million and others) | Kalshi | to July 2026 | stopped after the faked-plays case | Spotify |
| Hot 100 #1 song of the week | Polymarket | 2026 | $1.3 million | Billboard |
| First-week album sales brackets (Drake "Iceman" $2.1 million, Ye "BULLY", Ariana "Petal", ~20 albums) | Polymarket | 2026 | about $3 million | **HITS Daily Double "Activity" column** |

Outside sources that GitHub Actions can read: HITS Daily Double (`/charts/hits-top-50/<Thursday>` = final weekly numbers, `/charts/midweek-20/<Thursday>` = the forecast, both kept for every week since Jan 2026), Billboard chart pages, kworb (Spotify, iTunes, radio), Apple Music's top lists, Wayback copies of HITS. Data: `bt_cache/mus/hits.json.gz` (price store, `price-store-2`).

Timing (from Wayback copies): HITS's midweek forecast for a week ending Thursday was up by Thursday ~23:00 UTC to Friday 03:00 UTC. The final HITS number came Saturday afternoon in one week and after Saturday 20:00 UTC in another. Kalshi's album ladders close Sunday 15:00 UTC.

## 1. Hot 100 #1 vs Spotify's daily US plays: the price knows more. Dropped.

Buy Yes on the song with the most US Spotify plays in the tracking week (only days already published at the look time). The Spotify leader is the Hot 100 #1 only about 6 weeks in 10, because radio counts too (country hits like "Choosin' Texas" win with fewer Spotify plays). The price already has the winner at 90-99c by Thursday most weeks.

| Look | Bets | Per $100 |
|---|---|---|
| 110 hours before close | 35 | -$26.70 (exam: "Losing") |
| 60 hours | 17 | -$39.72 |
| 30 hours | 11 | -$39.39 |
| 12 hours | 7 | -$100 |

## 2. Album ladders vs HITS's midweek forecast: the price knows more. Dropped.

HITS's midweek forecast is good: within 3% of HITS's own final number for 538 of 861 albums (typical miss about 9%). Luminate's number runs about 4% above HITS's. A model "HITS midweek x the Luminate/HITS ratio of the other albums" against Kalshi's price at Friday 06:00 UTC:

- Miss score (lower is better), 281 rungs: model 0.079, Kalshi's price 0.044. A day earlier the price was already better (0.039) than the model.
- Buying 10c+ disagreements: +$10.76 per $100 on 64 bets in 27 albums, first half -$21.80, second half +$49.71, exam "Ahead, but could be luck". Most "No" bets at 3-7c lost because the market was right.
- Polymarket's first-week brackets (they settle on HITS itself): model 0.062 vs price 0.039 on 111 brackets; only 3 bets found.

So the traders already have HITS's forecast and more (Billboard's own early numbers).

## 3. Backward look: the lead (no track)

Starting from the results: on Kalshi's album-units ladders, a rung priced in the middle (10-90c) the night before Saturday came true more often than its price said.

**Rule:** 36 hours before the ladder closes (Saturday about 02:00 UTC, Friday night in New York), buy Yes on every rung whose price is 10-90c (bid-ask gap 15c or less, ask 97c or less), at the hourly ask + Kalshi fee, only where someone really traded at or under that price in the next 2 hours.

| Look | Bets | Albums | Per $100 | Halves |
|---|---|---|---|---|
| 96 h | 57 | 37 | +$22.71 | -$2.62 / +$44.15 |
| 72 h | 56 | 39 | +$8.85 | +$16.76 / $0.00 |
| 60 h | 46 | 35 | +$6.19 | -$20.61 / +$35.63 |
| 48 h | 48 | 35 | +$19.47 | +$10.12 / +$29.70 |
| 42 h | 48 | 37 | +$22.50 | +$28.62 / +$16.12 |
| **36 h** | **49** | **36** | **+$36.51** | **+$36.01 / +$37.21** |
| 30 h | 14 | 12 | +$7.47 | +$28.42 / -$15.51 |
| 24 h | 9 | 8 | -$28.38 | |
| 12 h | 9 | 8 | -$44.40 | |

Exam (36 h): **+$36.51 per $100 on 49 bets in 36 albums, "Promising, needs more bets"**, luck range +$20 to +$53, worst case per $100 -$1.05, about 4 more albums to clear the bar. Tries counted: 70.

Checks, one by one:
- Without the best 5 wins: +$21; without the best 10: +$11.
- Paying 2c / 4c / 6c more a share: +$30 / +$25 / +$21.
- One bet per album (the rung nearest 50c): +$43.90 on 37 bets.
- Favourites (50c+) won 27 of 28 (+$24); long shots under 50c won 11 of 24 (+$70).
- Rungs 0-8% above HITS's midweek number won 20 of 25. That fits a story: Luminate's number runs about 4% above HITS's, and late on Friday the price still leans on HITS. But a rule built only on that story is not steady across hours (-$17.50 at 60 h, +$27.70 at 36 h), so treat the story as a guess.
- Between 36 h and 30 h most middle rungs jump to near 0c or 100c: the real answer seems to get out early Saturday (UTC). Our 36 h look is just before that.

Weak spots: found by looking (70 versions), only 6 months and 36 albums, thin (median $35 sold at our price in 2 hours), the hourly price is an hourly snapshot (fills checked against real trades, but not our place in line).

**Free re-check (no track, Jan decides):** every Saturday from 28 Nov to 26 Dec, the same rule unchanged on the new album ladders (probe `kch_list` then `kch_tapes-KXALBUMEQUIV`, then `python3 music.py run`). About 8-10 more albums. If they are ahead too, ask Jan about a small paper track.

## How to run

    python3 music.py peek | hddpeek   # probes mus_peek, mus_hddpeek: which sources answer from Actions
    python3 music.py hits             # probe mus_hits: HITS final + midweek numbers for every week -> bt_cache/mus/hits.json.gz
    python3 music.py run              # the tables above
    python3 music.py report           # exam lines
