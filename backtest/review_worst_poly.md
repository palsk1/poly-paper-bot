# The worst Polymarket rule strategies: keep, change or dump? (2026-11-12)

Jan asked for this (12 Nov). This part covers Polymarket rule tracks only: no wallet copies, no maker tracks, no
Kalshi. The `claude` sandbox and the 21 Dec test tracks (`boring_no`, `crypto_no`, `soccer_draw`, `mention_no`,
`quiet_no`, `panic_fade_10c`) are only checked for "is it broken?".

Numbers come from `state/summary.md` and a fresh `python3 exam.py tracks` (`backtest/exam_tracks.md`) on 12 Nov
08:32 UTC. "Per $100" means: for every $100 bet, this much came back on top (or went missing). This is a review.
Nothing in the bot was changed.

**Update 12 Nov 11:46 UTC, Jan: "Dump and fix bug".** The six "dump" tracks now have `"stopped"` in config.json (no new bets, open bets settle), and the bot reads `endDate` first.

## The short answer

Three are clearly dead and should go: `fade_sure`, `wx_forecast` and `endgame_ending_soon`. A fourth,
`endgame_97`, loses for the same reason. Their live bets now say what their history tests said: they lose. Keeping
them doesn't teach us anything new.

**One bug found** (not the idea's fault): the bot reads a market's end *date* without the time, so it thinks a
market ended at midnight (Swedish 1 am) when it really ends later that day. Some endgame lab bets were labeled
"the deadline already passed" while the day was still going. Example: "Will Meta close above $630 on November 11?"
was bought at 99c at 17:17 UTC as "past the deadline". The stock market closed at 21:00 UTC, Meta closed below $630,
and the bet lost $4.95. 133 of 161 "past the deadline" buys in the lab happened on the end day itself, 12 of them in
the first hour after midnight UTC.

## Track by track (worst first)

**1. `fade_sure`: dump.** Buys the 2-10c long shot in weather buckets that end within a day. Live: 46 finished,
2 won, 44 lost. It lost $77.84 of every $100 bet ($7.49 of its $25). The full history test (PR #60) already said
-$18.67 per $100 on 13,000 bets. Not bad luck: the "sure" side is usually right.

**2. `wx_forecast` (lab): dump.** Weather forecast vs temperature buckets. Live: 114 finished, 51 won, 63 lost,
-$11.09 per $100 (-$11.32 so far, -$19.41 with open bets). The forecast test (PR #71) said Polymarket weather
markets know the temperature better than the free forecasts. Live agrees, only worse.

**3. `endgame_ending_soon` (lab): dump.** 93-98c on markets ending within a day. Live: 101 finished, 92 won,
9 lost, -$3.97 per $100 (-$30.03 so far, -$43.78 with open bets). The losses are the same kind the history test
found: "Will XRP dip to $1.10 this week" (bought at 99c, XRP dipped that evening), Elon tweet counts, a Dancing With
the Stars elimination, a strange copied earthquake market. Real flips, not a data error. History said about -$5.50
per $100. We dropped this rule from the main `endgame` on 8 Nov, and the live test has now confirmed that twice
over.

**4. `endgame_97` (lab): dump.** 97-99c, all four signals. Live: 112 finished, 105 won, 7 lost, -$3.33 per $100
(-$28.22 so far). One loss at 99c eats about 100 wins, and it had 7. Its losers are the "ending soon" kind (crypto
dips, tweets) plus 3 "past the deadline" bets bought before the day was over (the bug above). Without the bug it
would just be `endgame_ending_soon` again.

**5. `endgame_sell98` (lab): keep as it is.** Same buys at 95-97c, but sells once someone bids 98.5c. 188 finished,
179 won, 9 lost, +$0.21 per $100 so far ("Ahead, but could be luck", anything from -$0.93 to +$1.36). Selling
early dodged most flips. It's the only endgame variant still in the game, and it makes the most bets. The bug touches
it too (90 of 100 "past the deadline" buys were on the end day), but it hasn't hurt yet. It needs a lot more bets.

**6. `endgame` (main): keep as it is.** Realized +$1.01 (8 won, 0 lost). The -$4.32 on the scoreboard is 18 old
midterm-election bets still waiting for official results, valued at what someone bids right now. Those markets are
nearly dead, so bids are low and patchy. Example: "Republicans control the Texas Senate" shows 55c on a 96c buy.
That's most likely a thin book, not a real loss. We'll know when they pay out. Since 8 Nov it only buys once a result
is in, so the bug doesn't touch it.

**7. `crypto_late` (lab): keep, too early.** Last 45 minutes of hourly crypto up/down candles. 9 finished, 8 won,
1 lost: that one loss at 94c ($4.72) ate the eight wins (about 20c each). -$2.94. Nine bets is luck either way.
It's cheap, so let it run.

**8. `ladder` and `every_horse`: dump (or give their $200 a new job).** These two can't answer anything by 1 Jan.
`ladder` has watched 6,458 pairs since 8 Nov and found 0 cheap ones. `every_horse` holds 2 sets worth +$0.33 in
total and would need about 69 sets to prove anything. This is the open question from 8 Nov, so it's Jan's call.

**9. `fade_rally`, `sharp_pinnacle`, the favorite bands (`fav_*`, `no_only_90_97`, `yes_fav_85_95`), `screener`,
`favorites`, `consensus_*`, `control_*`: keep as they are.** None of them loses more than $1.74. Most have 0-1
finished bets (their bets run for weeks). Their ideas already lost in history tests, and the lab ones are kept on
purpose as evidence, so let them run. They cost nothing. `sharp_pinnacle` is +$6.01 on 6 bets: that's luck, because
the history test found no edge.

**Checked, not broken:** `boring_no` (-$3.14 is only the gap between what we paid and what someone bids today, 0
finished), `mention_no` (-$3.24, 1 won 1 lost: CoreWeave did say "Pipeline"), `soccer_draw` (+$6.13 realized, the
-$1.36 is open bets), `crypto_no`, `panic_fade`, `arb`. The date bug moves their "days left" by up to a day, which
barely matters for 3-60 day windows.

## The date bug in plain words, and the fix

Polymarket gives two end fields: a date ("2026-11-11") and a full time ("2026-11-11T21:00:00Z"). `bot.py` reads the
date first (`m.get("endDateIso") or m.get("endDate")`, in `endgame_candidates`, `base_filter` and three more places),
so every market "ends" at 00:00 UTC. The history test (`backtest.py`) reads the full time first, so live and
history don't match for the "past the deadline" signal.

Fix: read `endDate` first. It's one swap in 5 places. It would change what the frozen lab endgame tracks buy, so it
waits for Jan. The main `endgame` track no longer uses that signal, so it isn't affected.

## Table

| Strategy | Verdict | Why, in one line |
|---|---|---|
| `fade_sure` | Dump | 2 won, 44 lost, -$77.84 per $100; history said dead too |
| `wx_forecast` (lab) | Dump | -$11.09 per $100 on 114 bets; the markets know the weather better |
| `endgame_ending_soon` (lab) | Dump | -$3.97 per $100 on 101 bets, real flips, matches history |
| `endgame_97` (lab) | Dump | -$3.33 per $100 on 112 bets, the same losers plus the date bug |
| `endgame_sell98` (lab) | Keep | +$0.21 per $100 on 188 bets, selling early dodges flips; could be luck |
| `endgame` | Keep | 8 won, 0 lost; the red number is old election bets on thin books |
| `crypto_late` (lab) | Keep | 9 bets, one loss ate eight wins: too early |
| `ladder` | Dump or new job | 0 cheap pairs out of 6,458 in 4 days |
| `every_horse` | Dump or new job | 2 sets, needs about 69 to prove anything |
| other rule and lab tracks | Keep | under $2 either way, mostly 0 finished bets |
| Date bug | Fix (Jan's OK) | the bot thinks markets end at midnight UTC; read the full end time |
