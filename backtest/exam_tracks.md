# The exam for every live paper track (2026-11-12)

Made by `python3 exam.py tracks` from `state/tracks.json`. Research only: this page changes nothing in the bot, the dashboard or the ranking. It asks one question the scoreboard doesn't: **can this track be proven by 2027-01-01, or are we waiting for nothing?**

130 tracks, 76 with finished bets: 57 "Too early to tell", 15 "Losing", 4 "Ahead, but could be luck".

How to read it:
- **Separate bets**: bets on the same event (or in the same 15 minutes of crypto) count once. If losses come in bunches on the same days, a whole day counts once. That's the real amount of evidence.
- **Worst case per $100**: the result after adding one more made-up disaster and raising the bar because we run 130 tracks at once. Above $0 with 30+ separate bets and both halves ahead = "Looks real".
- **Answer by**: when the worst case would clear $0 if the track keeps going exactly as now. After 2027-01-01 = too slow.
- **Pass chance by 1 Jan**: out of 100 replays of the bets it will have by then. First number: if what we see is real. Second: if it's really worth $0. A good test has a high first and a low second number.

| Track | Verdict | Finished bets | Separate bets | Per $100 | Luck range | Worst case per $100 | Answer by | Pass chance by 1 Jan (real / worthless) |
|---|---|---|---|---|---|---|---|---|
| kc_maker_safe | Ahead, but could be luck | 329 | 117 | +$0.50 | -$0.23 to +$1.24 | -$2.52 | can't say | 88 / 0 |
| endgame_sell98 | Ahead, but could be luck | 188 | 127 | +$0.21 | -$0.93 to +$1.36 | -$3.12 | can't say | 6 / 0 |
| kc_maker | Ahead, but could be luck | 643 | 192 | +$0.10 | -$1.16 to +$1.36 | -$3.64 | can't say | 2 / 0 |
| panic_fade | Ahead, but could be luck | 12 | 12 | +$6.31 | +$3.29 to +$9.33 | -$11.96 | 2027-08-14 (too slow) | 99 / 0 |
| kc_maker_early | Losing | 341 | 106 | -$2.43 | -$5.79 to +$0.94 | -$10.94 |  |  |
| endgame_97 | Losing | 112 | 108 | -$3.33 | -$6.80 to +$0.13 | -$11.99 |  |  |
| endgame_ending_soon | Losing | 101 | 95 | -$3.97 | -$8.32 to +$0.39 | -$14.08 |  |  |
| w_bigggggggg | Losing | 26 | 13 | -$6.80 | -$11.76 to -$1.85 | -$25.85 |  |  |
| wb_bigggggggg | Losing | 31 | 16 | -$10.54 | -$18.34 to -$2.74 | -$33.95 |  |  |
| wx_forecast | Losing | 114 | 114 | -$11.09 | -$27.24 to +$5.07 | -$42.93 |  |  |
| wb_tokor | Losing | 16 | 13 | -$9.71 | -$29.37 to +$9.94 | -$55.37 |  |  |
| w_tokor | Losing | 14 | 11 | -$6.51 | -$26.60 to +$13.58 | -$56.11 |  |  |
| wb_hellyeahtrader | Losing | 51 | 37 | -$38.20 | -$52.25 to -$24.15 | -$67.80 |  |  |
| wb_cigarettes | Losing | 19 | 17 | -$34.21 | -$54.03 to -$14.39 | -$75.41 |  |  |
| w_hellyeahtrader | Losing | 32 | 25 | -$44.80 | -$63.94 to -$25.66 | -$84.73 |  |  |
| fade_sure | Losing | 46 | 46 | -$77.84 | -$104.25 to -$51.42 | -$100.00 |  |  |
| w_cigarettes | Losing | 17 | 14 | -$59.13 | -$83.86 to -$34.40 | -$100.00 |  |  |
| w_sbel | Losing | 16 | 13 | -$21.92 | -$68.61 to +$24.77 | -$100.00 |  |  |
| wb_sbel | Losing | 22 | 17 | -$37.78 | -$71.72 to -$3.85 | -$100.00 |  |  |

Too early to tell, under 10 separate bets (57): crypto_late (9, -$7), endgame (8, +$2), panic_fade_4c (8, +$5), maker (8, -$16), soccer_draw (7, +$60), wb_groth (6, +$18), wb_jjo (6, -$8), sharp_pinnacle (6, +$65), w_jjo (5, -$8), wb_blondbeast (5, +$9), maker_flat (4, -$10), maker_tp (4, -$4), wb_underperformingforal (4, -$10), w_anoin123 (4, -$4), wb_anoin123 (4, -$4), w_underperformingforal (4, -$8), claude (4, +$3), wb_lpgb (4, -$24), maker_tpsl (4, -$16), maker_short (4, -$13), wb_hauchn (4, +$3), wb_youngalphagoat (4, -$51), w_0x448861 (3, +$98), wb_0x448861 (3, +$98), wb_hell0pia (3, +$40), momentum_week (3, +$5), wb_rememberamalek (3, +$18), wb_dominus (3, -$17), wb_ecash (3, -$26), mention_no (2, -$45), panic_fade_10c (2, +$23), w_blondbeast (2, +$79), w_groth (2, +$34), w_lpgb (2, +$2), w_rememberamalek (2, +$22), wb_debased (2, +$29), wb_new_jeans (2, -$11), consensus_3 (1, +$8), endgame_strict (1, +$0), fade_rally (1, -$37), screener (1, +$22), w_betwick (1, -$11), w_debased (1, +$6), w_dominus (1, -$3), w_hauchn (1, +$22), w_hell0pia (1, +$62), w_lava_lava (1, +$68), w_pako (1, +$14), w_wan123 (1, -$100), wb_bertapotamous (1, -$4), wb_betwick (1, -$11), wb_dropper (1, -$74), wb_lava_lava (1, +$68), wb_pako (1, +$14), wb_rabbitfoot1 (1, -$100), wb_the_joker (1, -$74), wb_wan123 (1, -$100). The number is separate bets, the dollars are per $100 so far: mostly luck at this size.

No finished bets yet (54): arb, boring_no, consensus_2, control_longshot, control_random, crypto_no, econ_fav, every_horse, fav_bigvol_85_95, fav_cut_losses, fav_fee_free, fav_mid_80_90, fav_short_90_95, fav_short_95_98, favorites, ladder, mirror, mirror_unlimited, no_only_90_97, quiet_no, sab_big, sab_hold, w_aghy, w_albert_1953, w_balerinacapuchina, w_bertapotamous, w_dromedaryy, w_dropper, w_ecash, w_eightpenguins, w_flawfence, w_jsram, w_monopoly_money, w_new_jeans, w_rabbitfoot1, w_railcool, w_the_joker, w_thereturnofdarthmaul, w_tunatyler, w_vilgefortz, w_youngalphagoat, wb_aghy, wb_albert_1953, wb_balerinacapuchina, wb_dromedaryy, wb_eightpenguins, wb_flawfence, wb_jsram, wb_monopoly_money, wb_railcool, wb_thereturnofdarthmaul, wb_tunatyler, wb_vilgefortz, yes_fav_85_95.
