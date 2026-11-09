# Live esports lag test (2026-11-09)

Jan's question: can a bot watch live esports (CS2 rounds, LoL/Dota fights) and buy on Polymarket before the odds move?

**Answer: not with free data. The price moves first.** Run `probe lag_<minutes>` (livelag.py) to repeat.

What was measured (75 min, 11:55-13:10 UTC, 6 live tier-2 Dota 2 matches, 17 match/game winner markets;
CS2 games were live on the score feed but Polymarket had no markets for them that day):

- Polymarket's own free score feed (sports websocket) updates in chunks, a median **101 seconds** apart, and for
  most Dota games it doesn't even send kill counts (`000-000`), only maps won.
- When the feed did change mid-game, the price had usually already moved: in 29 of 42 cases the price made its
  big step first, a median **~6 seconds before** the feed. For 3c+ steps: 14 of 19, again ~6 s early.
- Most big jumps (197 moves of 4c+ within 3 seconds) had **no score update anywhere near them**. Example: Power
  Rangers vs Nemiga, 12:25:44-12:26:25, the match price ran 67c -> 86c and back to 76c with up to 18,000 shares
  traded in 5 seconds; the free feed updated ~100 s later. Someone trades on a much faster feed.
- Our websocket itself is fast: messages reach a GitHub runner ~50 ms after Polymarket stamps them.
- Map ends: by the time the feed said "finished", the winner was already priced at 99.6c.

Context from research: Twitch is 30-60 s behind the game; official feeds (GRID, PandaScore) arrive in under a
second and cost from about €500 a month per game (GRID: quote only, its cheap media plan is banned for betting);
GRID is Polymarket's own esports data partner; some Polymarket sports markets hold taker orders ~1 s before
matching to stop snipers. The "TeemuTeemuTeemu $900 -> $208k" story (Dec 2025) is from a tweet, unverified,
and predates the delays and the GRID deal.

Verdict: dropped. To compete you'd need a paid official feed, an always-on server, and to beat pro bots on the
same feed through a 1 s order hold. Not a fit for a $300-500 trial. Limits of this test: one session, tier-2
Dota only, no CS2/LoL markets live that day.

## Raw report

Messages: 1598 esports score updates, 1560229 market updates, 17 markets on 6 live games.
Delivery lag of the market websocket to us (our clock - Polymarket's timestamp): median 50 ms, 90th pct 53 ms (n=1560229).

## Score changes vs price moves
lead = when the price made its biggest step minus when Polymarket's score feed told us. Negative = the price moved first.

- 12:09:29 dota2: Power Rangers vs Nemiga Gaming: 000-000|0-1|Bo3 2/3 -> 000-000|1-1|Bo3 3/3 (running)
- 12:13:30 dota2: Froglings vs Team Synapse: 000-000|1-0|Bo3 2/3 -> 000-000|2-0|Bo3 2/3 (finished)
- 12:15:51 dota2: PlayTime vs potn9ki: 000-000|0-1|Bo3 2/3 -> 000-000|1-1|Bo3 3/3 (running)
- 12:49:49 dota2: Xipto Esports vs HULIGANI: 000-000|1-1|Bo3 3/3 -> 000-000|2-1|Bo3 3/3 (finished)
- 13:08:18 dota2: Spirit Academy vs Zero Tenacity: 000-000|1-0|Bo3 2/3 -> 000-000|2-0|Bo3 2/3 (finished)
    Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy]: moved +4.9c, biggest step +2.0c at lead -53.6s | mid -30s:99.6 -10s:99.6 -3s:99.6 +0s:99.6 +3s:99.6 +10s:99.6 +30s:99.6
- 13:08:38 dota2: PlayTime vs potn9ki: 000-000|1-1|Bo3 3/3 -> 000-000|2-1|Bo3 3/3 (finished)
- 13:09:18 dota2: Xipto Esports vs Team Synapse: 000-000|0-0|Bo3 0/3 -> 000-000|0-0|Bo3 1/3 (running)

Map/game ends: n=1, median lead -53.6s, price first in 1, feed first in 0.

Kills/rounds inside a game (window +-15s, moves of 1c+): n=42, lead 10th pct -13.5s, median -5.7s, 90th pct +10.7s; price first in 29, feed first in 13. Big ones (3c+ step):
    n=19, median lead -5.8s, price first in 14

Score feed: 143 changes, median gap between updates 101s.

## Big jumps (4c+ within 3s) and the nearest score change
- 11:55:46 Dota 2: Froglings vs Team Synapse - Game 2 Winner [Froglings] 86.5 -> 82.5c, trades +-5s: 0 shares, nearest score change +115.2s after the jump
- 11:56:06 Dota 2: PlayTime vs potn9ki - Game 2 Winner [PlayTime] 78.0 -> 82.5c, trades +-5s: 1436 shares, nearest score change +1185.6s after the jump
- 11:56:17 Dota 2: PlayTime vs potn9ki - Game 2 Winner [PlayTime] 85.5 -> 81.5c, trades +-5s: 21 shares, nearest score change +1174.2s after the jump
- 11:57:35 Dota 2: Froglings vs Team Synapse - Game 2 Winner [Froglings] 84.0 -> 88.0c, trades +-5s: 797 shares, nearest score change +5.8s after the jump
- 11:57:37 Dota 2: Froglings vs Team Synapse - Game 2 Winner [Froglings] 88.0 -> 92.0c, trades +-5s: 809 shares, nearest score change +3.3s after the jump
- 12:00:54 Dota 2: PlayTime vs potn9ki - Game 2 Winner [PlayTime] 75.5 -> 80.0c, trades +-5s: 10 shares, nearest score change +897.1s after the jump
- 12:01:26 Dota 2: PlayTime vs potn9ki - Game 2 Winner [PlayTime] 76.0 -> 80.0c, trades +-5s: 0 shares, nearest score change +865.7s after the jump
- 12:02:21 Dota 2: PlayTime vs potn9ki - Game 2 Winner [PlayTime] 86.5 -> 91.5c, trades +-5s: 307 shares, nearest score change +809.8s after the jump
- 12:08:41 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 45.5 -> 50.0c, trades +-5s: 9911 shares, nearest score change +2467.6s after the jump
- 12:10:45 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 56.0 -> 60.5c, trades +-5s: 2536 shares, nearest score change +2344.4s after the jump
- 12:10:55 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 59.0 -> 63.5c, trades +-5s: 3441 shares, nearest score change +2334.0s after the jump
- 12:10:57 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 63.5 -> 57.5c, trades +-5s: 1931 shares, nearest score change +2332.0s after the jump
- 12:13:05 Dota 2: PlayTime vs potn9ki (BO3) - DreamLeague Division 2 Group A [PlayTime] 84.5 -> 80.0c, trades +-5s: 0 shares, nearest score change +166.4s after the jump
- 12:14:24 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 53.0 -> 57.5c, trades +-5s: 2759 shares, nearest score change +3234.0s after the jump
- 12:14:25 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 57.5 -> 52.5c, trades +-5s: 2759 shares, nearest score change +3233.2s after the jump
- 12:20:03 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 69.5 -> 73.5c, trades +-5s: 924 shares, nearest score change +1786.2s after the jump
- 12:20:05 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 52.0 -> 56.5c, trades +-5s: 3194 shares, nearest score change +2893.2s after the jump
- 12:20:06 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 56.5 -> 60.5c, trades +-5s: 3192 shares, nearest score change +2891.7s after the jump
- 12:20:07 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 73.0 -> 77.0c, trades +-5s: 924 shares, nearest score change +1781.8s after the jump
- 12:20:08 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 60.5 -> 56.0c, trades +-5s: 730 shares, nearest score change +2889.6s after the jump
- 12:20:09 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 56.0 -> 60.5c, trades +-5s: 730 shares, nearest score change +2889.3s after the jump
- 12:20:13 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 60.0 -> 55.5c, trades +-5s: 151 shares, nearest score change +2885.0s after the jump
- 12:21:00 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 53.0 -> 58.0c, trades +-5s: 819 shares, nearest score change +2837.9s after the jump
- 12:21:19 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 58.0 -> 52.5c, trades +-5s: 98 shares, nearest score change +2819.0s after the jump
- 12:25:44 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 67.5 -> 72.5c, trades +-5s: 18284 shares, nearest score change +112.9s after the jump
- 12:25:49 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 72.0 -> 77.0c, trades +-5s: 15270 shares, nearest score change +108.5s after the jump
- 12:25:50 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 77.0 -> 71.5c, trades +-5s: 14521 shares, nearest score change +107.1s after the jump
- 12:25:51 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 71.5 -> 75.5c, trades +-5s: 14521 shares, nearest score change +106.8s after the jump
- 12:25:54 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 75.5 -> 80.0c, trades +-5s: 2634 shares, nearest score change +102.9s after the jump
- 12:25:57 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 80.0 -> 76.0c, trades +-5s: 822 shares, nearest score change +100.1s after the jump
- 12:26:03 Dota 2: Xipto Esports vs HULIGANI (BO3) - 1win Essence Play-in Group B [Xipto Esports] 76.5 -> 80.5c, trades +-5s: 771 shares, nearest score change +1426.4s after the jump
- 12:26:09 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 76.0 -> 81.0c, trades +-5s: 11964 shares, nearest score change +88.5s after the jump
- 12:26:15 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 78.0 -> 82.5c, trades +-5s: 3085 shares, nearest score change +82.7s after the jump
- 12:26:15 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 82.5 -> 86.5c, trades +-5s: 3085 shares, nearest score change +82.2s after the jump
- 12:26:18 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 86.5 -> 82.5c, trades +-5s: 4460 shares, nearest score change +79.2s after the jump
- 12:26:20 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 82.5 -> 78.0c, trades +-5s: 2031 shares, nearest score change +77.7s after the jump
- 12:26:25 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 75.5 -> 80.0c, trades +-5s: 2557 shares, nearest score change +72.6s after the jump
- 12:27:29 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 40.5 -> 36.5c, trades +-5s: 0 shares, nearest score change +2448.9s after the jump
- 12:30:33 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 39.5 -> 44.0c, trades +-5s: 1029 shares, nearest score change +2265.2s after the jump
- 12:32:05 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 46.0 -> 42.0c, trades +-5s: 11 shares, nearest score change +2172.7s after the jump
- 12:33:31 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 44.5 -> 49.0c, trades +-5s: 11 shares, nearest score change +2087.0s after the jump
- 12:33:32 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 63.0 -> 67.0c, trades +-5s: 17 shares, nearest score change +2085.9s after the jump
- 12:33:36 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 49.0 -> 44.5c, trades +-5s: 0 shares, nearest score change +2081.4s after the jump
- 12:33:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 65.0 -> 61.0c, trades +-5s: 809 shares, nearest score change +8.3s after the jump
- 12:34:27 Dota 2: PlayTime vs potn9ki (BO3) - DreamLeague Division 2 Group A [PlayTime] 76.5 -> 82.4c, trades +-5s: 2240 shares, nearest score change -1115.6s after the jump
- 12:35:23 Dota 2: PlayTime vs potn9ki (BO3) - DreamLeague Division 2 Group A [PlayTime] 86.0 -> 81.5c, trades +-5s: 0 shares, nearest score change -1172.2s after the jump
- 12:36:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 65.5 -> 61.5c, trades +-5s: 0 shares, nearest score change +77.4s after the jump
- 12:37:27 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 56.0 -> 60.5c, trades +-5s: 223 shares, nearest score change -5.0s after the jump
- 12:37:54 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 65.0 -> 69.5c, trades +-5s: 0 shares, nearest score change +1823.9s after the jump
- 12:38:05 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 47.5 -> 43.0c, trades +-5s: 76 shares, nearest score change +1812.6s after the jump
- 12:40:29 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 44.0 -> 48.5c, trades +-5s: 1403 shares, nearest score change +15.7s after the jump
- 12:40:30 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 48.5 -> 53.0c, trades +-5s: 1403 shares, nearest score change +13.9s after the jump
- 12:40:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 53.5 -> 58.5c, trades +-5s: 7 shares, nearest score change -7.2s after the jump
- 12:41:05 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 64.0 -> 68.0c, trades +-5s: 0 shares, nearest score change +1633.2s after the jump
- 12:41:28 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 46.0 -> 50.5c, trades +-5s: 856 shares, nearest score change +1610.2s after the jump
- 12:41:30 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 50.5 -> 55.0c, trades +-5s: 864 shares, nearest score change +1608.1s after the jump
- 12:41:30 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 55.0 -> 64.0c, trades +-5s: 864 shares, nearest score change +1607.8s after the jump
- 12:41:30 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 64.0 -> 60.0c, trades +-5s: 864 shares, nearest score change +1607.8s after the jump
- 12:41:30 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 60.0 -> 64.0c, trades +-5s: 864 shares, nearest score change +1607.7s after the jump
- 12:41:30 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 64.0 -> 56.5c, trades +-5s: 864 shares, nearest score change +1607.6s after the jump
- 12:41:36 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 58.0 -> 62.0c, trades +-5s: 8 shares, nearest score change +1602.2s after the jump
- 12:41:36 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 67.0 -> 71.5c, trades +-5s: 20 shares, nearest score change +1601.3s after the jump
- 12:41:38 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 62.0 -> 66.0c, trades +-5s: 8 shares, nearest score change +1600.3s after the jump
- 12:41:54 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 73.5 -> 78.5c, trades +-5s: 10 shares, nearest score change +1583.7s after the jump
- 12:42:34 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 48.0 -> 41.5c, trades +-5s: 366 shares, nearest score change +11.4s after the jump
- 12:42:42 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 41.0 -> 36.5c, trades +-5s: 1357 shares, nearest score change +3.6s after the jump
- 12:42:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 36.5 -> 40.5c, trades +-5s: 1082 shares, nearest score change +0.4s after the jump
- 12:44:39 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 46.5 -> 51.0c, trades +-5s: 2604 shares, nearest score change +7.1s after the jump
- 12:44:39 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 51.0 -> 55.5c, trades +-5s: 2604 shares, nearest score change +7.1s after the jump
- 12:44:46 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 59.0 -> 63.0c, trades +-5s: 3232 shares, nearest score change +0.9s after the jump
- 12:45:25 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 52.5 -> 48.5c, trades +-5s: 1000 shares, nearest score change +2.0s after the jump
- 12:46:36 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 53.5 -> 49.5c, trades +-5s: 0 shares, nearest score change +1301.9s after the jump
- 12:46:54 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 46.5 -> 51.5c, trades +-5s: 293 shares, nearest score change +1283.8s after the jump
- 12:46:57 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 51.5 -> 55.5c, trades +-5s: 293 shares, nearest score change +1281.2s after the jump
- 12:47:48 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 62.5 -> 67.5c, trades +-5s: 468 shares, nearest score change +1229.9s after the jump
- 12:47:49 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 67.5 -> 72.0c, trades +-5s: 468 shares, nearest score change +1228.6s after the jump
- 12:47:50 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 74.0 -> 78.0c, trades +-5s: 183 shares, nearest score change +1227.3s after the jump
- 12:47:55 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 82.0 -> 77.5c, trades +-5s: 25 shares, nearest score change +1222.8s after the jump
- 12:48:01 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 78.0 -> 82.5c, trades +-5s: 0 shares, nearest score change +1216.4s after the jump
- 12:48:02 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 70.0 -> 74.0c, trades +-5s: 0 shares, nearest score change +1216.1s after the jump
- 12:48:09 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 72.0 -> 76.0c, trades +-5s: 0 shares, nearest score change +1209.3s after the jump
- 12:51:51 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 57.0 -> 61.0c, trades +-5s: 1430 shares, nearest score change -0.6s after the jump
- 12:52:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 63.5 -> 70.5c, trades +-5s: 2581 shares, nearest score change +6.0s after the jump
- 12:52:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 70.5 -> 66.0c, trades +-5s: 2581 shares, nearest score change +5.9s after the jump
- 12:52:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 66.0 -> 70.5c, trades +-5s: 2581 shares, nearest score change +5.6s after the jump
- 12:52:06 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 70.5 -> 74.5c, trades +-5s: 3038 shares, nearest score change +4.5s after the jump
- 12:52:06 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 74.5 -> 69.0c, trades +-5s: 3038 shares, nearest score change +4.1s after the jump
- 12:52:10 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 69.5 -> 73.5c, trades +-5s: 1653 shares, nearest score change +0.2s after the jump
- 12:52:26 Dota 2: PlayTime vs potn9ki (BO3) - DreamLeague Division 2 Group A [PlayTime] 95.9 -> 91.8c, trades +-5s: 130 shares, nearest score change +972.1s after the jump
- 12:52:36 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 76.5 -> 72.5c, trades +-5s: 88 shares, nearest score change -25.7s after the jump
- 12:52:53 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 65.0 -> 61.0c, trades +-5s: 0 shares, nearest score change +924.3s after the jump
- 12:53:05 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 60.0 -> 64.0c, trades +-5s: 631 shares, nearest score change +912.9s after the jump
- 12:53:13 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 62.5 -> 66.5c, trades +-5s: 0 shares, nearest score change +905.2s after the jump
- 12:53:14 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 66.5 -> 62.5c, trades +-5s: 0 shares, nearest score change +904.0s after the jump
- 12:53:18 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 63.5 -> 68.5c, trades +-5s: 0 shares, nearest score change +899.4s after the jump
- 12:53:21 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 68.5 -> 73.0c, trades +-5s: 0 shares, nearest score change +897.0s after the jump
- 12:53:46 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 66.0 -> 70.5c, trades +-5s: 0 shares, nearest score change +871.7s after the jump
- 12:54:21 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 69.0 -> 73.0c, trades +-5s: 1 shares, nearest score change +836.6s after the jump
- 12:56:07 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 77.5 -> 82.0c, trades +-5s: 128 shares, nearest score change +731.1s after the jump
- 12:56:26 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 80.5 -> 86.0c, trades +-5s: 317 shares, nearest score change +711.6s after the jump
- 12:56:29 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 86.0 -> 90.0c, trades +-5s: 322 shares, nearest score change +709.1s after the jump
- 12:57:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 68.0 -> 64.0c, trades +-5s: 30 shares, nearest score change +289.7s after the jump
- 12:57:10 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 62.5 -> 66.5c, trades +-5s: 30 shares, nearest score change +284.6s after the jump
- 12:57:49 Dota 2: Spirit Academy vs Zero Tenacity - Game 2 Winner [Spirit Academy] 97.0 -> 93.0c, trades +-5s: 0 shares, nearest score change +629.1s after the jump
- 12:59:32 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 65.5 -> 70.0c, trades +-5s: 1249 shares, nearest score change +142.7s after the jump
- 13:01:14 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 64.0 -> 60.0c, trades +-5s: 210 shares, nearest score change +41.4s after the jump
- 13:01:48 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 65.0 -> 70.0c, trades +-5s: 2267 shares, nearest score change +6.7s after the jump
- 13:01:49 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 70.0 -> 74.0c, trades +-5s: 2267 shares, nearest score change +6.3s after the jump
- 13:01:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 74.0 -> 68.5c, trades +-5s: 3403 shares, nearest score change +3.3s after the jump
- 13:01:53 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 68.5 -> 73.5c, trades +-5s: 2473 shares, nearest score change +2.2s after the jump
- 13:01:54 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 73.5 -> 79.5c, trades +-5s: 1293 shares, nearest score change +0.4s after the jump
- 13:01:56 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 79.5 -> 85.5c, trades +-5s: 1279 shares, nearest score change -1.1s after the jump
- 13:01:59 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 88.0 -> 82.5c, trades +-5s: 1185 shares, nearest score change -4.6s after the jump
- 13:02:02 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 82.5 -> 86.5c, trades +-5s: 2357 shares, nearest score change -7.1s after the jump
- 13:02:09 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 88.0 -> 81.5c, trades +-5s: 2822 shares, nearest score change -14.3s after the jump
- 13:03:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 75.5 -> 69.5c, trades +-5s: 993 shares, nearest score change +4.2s after the jump
- 13:03:53 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 69.5 -> 62.5c, trades +-5s: 997 shares, nearest score change +2.5s after the jump
- 13:03:55 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 62.5 -> 58.5c, trades +-5s: 997 shares, nearest score change +0.5s after the jump
- 13:04:26 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 60.5 -> 56.5c, trades +-5s: 486 shares, nearest score change -30.0s after the jump
- 13:05:42 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 49.5 -> 45.0c, trades +-5s: 1180 shares, nearest score change -5.3s after the jump
- 13:05:43 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 45.0 -> 41.0c, trades +-5s: 1230 shares, nearest score change -5.8s after the jump
- 13:05:44 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 41.0 -> 36.5c, trades +-5s: 1230 shares, nearest score change -7.1s after the jump
- 13:05:44 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 36.5 -> 29.0c, trades +-5s: 1230 shares, nearest score change -7.6s after the jump
- 13:05:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 29.0 -> 33.0c, trades +-5s: 1230 shares, nearest score change -8.0s after the jump
- 13:05:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 33.0 -> 27.5c, trades +-5s: 1230 shares, nearest score change -8.1s after the jump
- 13:05:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.5 -> 23.5c, trades +-5s: 1230 shares, nearest score change -8.3s after the jump
- 13:05:46 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 23.5 -> 36.0c, trades +-5s: 1230 shares, nearest score change -9.5s after the jump
- 13:05:46 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 36.0 -> 26.5c, trades +-5s: 1230 shares, nearest score change -9.7s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 26.5 -> 31.5c, trades +-5s: 1230 shares, nearest score change -9.8s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 31.5 -> 27.0c, trades +-5s: 1674 shares, nearest score change +10.0s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.0 -> 31.5c, trades +-5s: 1674 shares, nearest score change +9.9s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 31.5 -> 26.5c, trades +-5s: 1674 shares, nearest score change +9.9s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 26.5 -> 31.5c, trades +-5s: 1674 shares, nearest score change +9.7s after the jump
- 13:05:47 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 31.5 -> 27.0c, trades +-5s: 1674 shares, nearest score change +9.6s after the jump
- 13:05:49 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.0 -> 22.0c, trades +-5s: 1712 shares, nearest score change +8.4s after the jump
- 13:05:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 23.0 -> 18.5c, trades +-5s: 531 shares, nearest score change +5.3s after the jump
- 13:05:52 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.5 -> 30.5c, trades +-5s: 531 shares, nearest score change +5.2s after the jump
- 13:05:53 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 30.5 -> 25.5c, trades +-5s: 481 shares, nearest score change +4.1s after the jump
- 13:05:54 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 25.5 -> 20.5c, trades +-5s: 481 shares, nearest score change +3.2s after the jump
- 13:06:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 20.5 -> 15.5c, trades +-5s: 71 shares, nearest score change -6.9s after the jump
- 13:06:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 15.5 -> 20.5c, trades +-5s: 71 shares, nearest score change -7.0s after the jump
- 13:06:07 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.5 -> 22.5c, trades +-5s: 167 shares, nearest score change +9.9s after the jump
- 13:06:09 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 22.5 -> 18.5c, trades +-5s: 326 shares, nearest score change +8.1s after the jump
- 13:06:10 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.5 -> 14.5c, trades +-5s: 326 shares, nearest score change +7.0s after the jump
- 13:06:13 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 14.5 -> 9.0c, trades +-5s: 355 shares, nearest score change +4.2s after the jump
- 13:06:14 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 9.0 -> 13.0c, trades +-5s: 355 shares, nearest score change +3.5s after the jump
- 13:06:14 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 13.0 -> 9.0c, trades +-5s: 388 shares, nearest score change +2.8s after the jump
- 13:06:18 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 7.5 -> 2.5c, trades +-5s: 1143 shares, nearest score change -1.1s after the jump
- 13:06:20 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 2.5 -> 9.5c, trades +-5s: 987 shares, nearest score change -2.9s after the jump
- 13:06:21 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 9.5 -> 5.5c, trades +-5s: 969 shares, nearest score change -4.2s after the jump
- 13:07:21 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 5.5 -> 9.5c, trades +-5s: 2867 shares, nearest score change +16.8s after the jump
- 13:07:24 Dota 2: Spirit Academy vs Zero Tenacity (BO3) - Asgard Championship Group A [Spirit Academy] 94.7 -> 99.5c, trades +-5s: 178 shares, nearest score change +53.6s after the jump
- 13:07:25 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 9.5 -> 15.5c, trades +-5s: 4336 shares, nearest score change +12.8s after the jump
- 13:07:27 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 15.5 -> 22.5c, trades +-5s: 3423 shares, nearest score change +10.7s after the jump
- 13:07:31 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 25.0 -> 21.0c, trades +-5s: 2835 shares, nearest score change +6.4s after the jump
- 13:07:33 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 21.0 -> 16.5c, trades +-5s: 1761 shares, nearest score change +4.5s after the jump
- 13:07:36 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 16.5 -> 21.0c, trades +-5s: 1849 shares, nearest score change +1.6s after the jump
- 13:07:40 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 21.5 -> 27.0c, trades +-5s: 2588 shares, nearest score change -2.1s after the jump
- 13:07:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.0 -> 31.5c, trades +-5s: 870 shares, nearest score change -7.6s after the jump
- 13:07:49 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 31.0 -> 26.0c, trades +-5s: 2491 shares, nearest score change +8.5s after the jump
- 13:07:53 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 26.5 -> 32.0c, trades +-5s: 3567 shares, nearest score change +4.9s after the jump
- 13:07:53 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 32.0 -> 27.5c, trades +-5s: 3567 shares, nearest score change +4.7s after the jump
- 13:07:55 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.5 -> 23.5c, trades +-5s: 4176 shares, nearest score change +2.6s after the jump
- 13:07:57 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 23.5 -> 29.0c, trades +-5s: 1895 shares, nearest score change +0.4s after the jump
- 13:07:58 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 29.0 -> 33.0c, trades +-5s: 1895 shares, nearest score change +0.0s after the jump
- 13:07:59 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 33.0 -> 37.5c, trades +-5s: 1895 shares, nearest score change -0.9s after the jump
- 13:07:59 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 37.5 -> 49.5c, trades +-5s: 1895 shares, nearest score change -1.6s after the jump
- 13:08:02 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 49.5 -> 41.5c, trades +-5s: 739 shares, nearest score change -4.1s after the jump
- 13:08:02 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 41.5 -> 47.0c, trades +-5s: 739 shares, nearest score change -4.1s after the jump
- 13:08:03 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 47.0 -> 41.5c, trades +-5s: 714 shares, nearest score change -5.2s after the jump
- 13:08:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 41.5 -> 45.5c, trades +-5s: 714 shares, nearest score change -5.8s after the jump
- 13:08:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 45.5 -> 37.5c, trades +-5s: 714 shares, nearest score change -6.4s after the jump
- 13:08:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 37.5 -> 42.5c, trades +-5s: 714 shares, nearest score change -6.4s after the jump
- 13:08:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 42.5 -> 35.5c, trades +-5s: 894 shares, nearest score change -7.5s after the jump
- 13:08:05 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 35.5 -> 40.0c, trades +-5s: 894 shares, nearest score change -7.6s after the jump
- 13:08:06 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 40.0 -> 32.5c, trades +-5s: 821 shares, nearest score change -8.7s after the jump
- 13:08:07 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 32.5 -> 37.5c, trades +-5s: 821 shares, nearest score change -8.8s after the jump
- 13:08:10 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 37.5 -> 32.5c, trades +-5s: 846 shares, nearest score change +8.2s after the jump
- 13:08:38 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 38.0 -> 42.5c, trades +-5s: 5 shares, nearest score change -19.8s after the jump
- 13:08:54 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 41.0 -> 46.5c, trades +-5s: 691 shares, nearest score change +24.3s after the jump
- 13:09:14 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 46.0 -> 37.5c, trades +-5s: 15 shares, nearest score change +3.8s after the jump
- 13:09:16 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 37.5 -> 32.5c, trades +-5s: 15 shares, nearest score change +2.4s after the jump
- 13:09:16 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 32.5 -> 28.0c, trades +-5s: 15 shares, nearest score change +2.3s after the jump
- 13:09:16 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 28.0 -> 23.5c, trades +-5s: 15 shares, nearest score change +2.2s after the jump
- 13:09:16 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 23.5 -> 18.5c, trades +-5s: 15 shares, nearest score change +1.9s after the jump
- 13:09:17 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.5 -> 14.5c, trades +-5s: 15 shares, nearest score change +1.3s after the jump
- 13:09:22 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 13.0 -> 19.5c, trades +-5s: 1313 shares, nearest score change -3.8s after the jump
- 13:09:24 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 19.5 -> 24.0c, trades +-5s: 1461 shares, nearest score change -5.6s after the jump
- 13:09:29 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 23.5 -> 18.0c, trades +-5s: 1440 shares, nearest score change +9.1s after the jump
- 13:09:32 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.0 -> 13.5c, trades +-5s: 2368 shares, nearest score change +6.7s after the jump
- 13:09:36 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 16.0 -> 12.0c, trades +-5s: 2688 shares, nearest score change +2.6s after the jump
- 13:09:39 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 12.0 -> 16.0c, trades +-5s: 1857 shares, nearest score change -0.2s after the jump
- 13:09:45 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 15.0 -> 20.0c, trades +-5s: 338 shares, nearest score change -6.1s after the jump
- 13:09:49 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 18.0 -> 22.0c, trades +-5s: 269 shares, nearest score change -11.0s after the jump
- 13:10:01 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 21.5 -> 25.5c, trades +-5s: 395 shares, nearest score change -22.2s after the jump
- 13:10:04 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 27.5 -> 22.5c, trades +-5s: 395 shares, nearest score change -25.7s after the jump
- 13:10:13 Dota 2: Power Rangers vs Nemiga Gaming (BO3) - DreamLeague Division 2 Group A [Power Rangers] 20.0 -> 25.5c, trades +-5s: 3116 shares, nearest score change -34.9s after the jump

197 big jumps, 143 score changes.
