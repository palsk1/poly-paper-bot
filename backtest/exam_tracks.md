# The exam for every live paper track (2026-11-10)

Made by `python3 exam.py tracks` from `state/tracks.json`. Research only: this page changes nothing in the bot, the dashboard or the ranking. It asks one question the scoreboard doesn't: **can this track be proven by 2027-01-01, or are we waiting for nothing?**

127 tracks, 55 with finished bets: 45 "Too early to tell", 9 "Losing", 1 "Ahead, but could be luck".

How to read it:
- **Separate bets**: bets on the same event (or in the same 15 minutes of crypto) count once. If losses come in bunches on the same days, a whole day counts once. That's the real amount of evidence.
- **Worst case per $100**: the result after adding one more made-up disaster and raising the bar because we run 127 tracks at once. Above $0 with 30+ separate bets and both halves ahead = "Looks real".
- **Answer by**: when the worst case would clear $0 if the track keeps going exactly as now. After 2027-01-01 = too slow.
- **Pass chance by 1 Jan**: out of 100 replays of the bets it will have by then. First number: if what we see is real. Second: if it's really worth $0. A good test has a high first and a low second number.

| Track | Verdict | Finished bets | Separate bets | Per $100 | Luck range | Worst case per $100 | Answer by | Pass chance by 1 Jan (real / worthless) |
|---|---|---|---|---|---|---|---|---|
| kc_maker_safe | Ahead, but could be luck | 110 | 39 | +$0.10 | -$1.45 to +$1.66 | -$8.19 | can't say | 3 / 0 |
| endgame_sell98 | Losing | 94 | 60 | -$0.50 | -$2.50 to +$1.49 | -$6.74 |  |  |
| kc_maker | Losing | 240 | 68 | -$0.60 | -$3.47 to +$2.27 | -$9.72 |  |  |
| endgame_ending_soon | Losing | 54 | 51 | -$1.36 | -$5.53 to +$2.82 | -$14.18 |  |  |
| endgame_97 | Losing | 57 | 54 | -$2.68 | -$6.88 to +$1.52 | -$15.73 |  |  |
| kc_maker_early | Losing | 144 | 45 | -$4.77 | -$11.23 to +$1.69 | -$21.89 |  |  |
| wb_bigggggggg | Losing | 20 | 12 | -$14.45 | -$25.74 to -$3.17 | -$47.68 |  |  |
| wb_hellyeahtrader | Losing | 34 | 26 | -$26.90 | -$43.03 to -$10.78 | -$63.18 |  |  |
| wx_forecast | Losing | 50 | 50 | -$14.67 | -$39.64 to +$10.29 | -$63.93 |  |  |
| w_hellyeahtrader | Losing | 15 | 14 | -$20.25 | -$47.15 to +$6.66 | -$79.06 |  |  |

Too early to tell, under 10 separate bets (45): w_bigggggggg (9, -$9), wb_tokor (9, +$4), crypto_late (9, -$7), wb_cigarettes (9, -$19), wb_sbel (9, -$72), w_cigarettes (8, -$37), w_tokor (7, +$14), fade_sure (7, -$100), panic_fade (6, +$10), endgame (6, +$3), w_sbel (5, -$58), wb_jjo (4, +$4), wb_lpgb (4, -$24), sharp_pinnacle (4, -$8), wb_youngalphagoat (4, -$51), w_underperformingforal (3, -$9), w_jjo (3, +$5), wb_dominus (3, -$17), wb_underperformingforal (3, -$11), wb_groth (3, +$6), claude (3, +$2), momentum_week (3, +$13), panic_fade_4c (3, +$5), panic_fade_10c (2, +$23), w_anoin123 (2, -$5), w_lpgb (2, +$2), wb_anoin123 (2, -$5), wb_blondbeast (2, -$42), wb_ecash (2, +$6), consensus_3 (1, +$8), fade_rally (1, -$37), maker_short (1, -$75), screener (1, +$22), w_dominus (1, -$3), w_groth (1, +$22), w_pako (1, -$5), w_rememberamalek (1, +$36), w_wan123 (1, -$100), wb_bertapotamous (1, -$4), wb_hauchn (1, +$42), wb_new_jeans (1, +$3), wb_pako (1, -$5), wb_rabbitfoot1 (1, -$100), wb_rememberamalek (1, +$36), wb_wan123 (1, -$100). The number is separate bets, the dollars are per $100 so far: mostly luck at this size.

No finished bets yet (72): arb, consensus_2, control_longshot, control_random, econ_fav, endgame_strict, every_horse, fav_bigvol_85_95, fav_cut_losses, fav_fee_free, fav_mid_80_90, fav_short_90_95, fav_short_95_98, favorites, ladder, maker, maker_flat, maker_tp, maker_tpsl, mention_no, mirror, mirror_unlimited, no_only_90_97, quiet_no, sab_big, sab_hold, w_0x448861, w_aghy, w_albert_1953, w_balerinacapuchina, w_bertapotamous, w_betwick, w_blondbeast, w_debased, w_dromedaryy, w_dropper, w_ecash, w_eightpenguins, w_flawfence, w_hauchn, w_hell0pia, w_jsram, w_lava_lava, w_monopoly_money, w_new_jeans, w_rabbitfoot1, w_railcool, w_the_joker, w_thereturnofdarthmaul, w_tunatyler, w_vilgefortz, w_youngalphagoat, wb_0x448861, wb_aghy, wb_albert_1953, wb_balerinacapuchina, wb_betwick, wb_debased, wb_dromedaryy, wb_dropper, wb_eightpenguins, wb_flawfence, wb_hell0pia, wb_jsram, wb_lava_lava, wb_monopoly_money, wb_railcool, wb_the_joker, wb_thereturnofdarthmaul, wb_tunatyler, wb_vilgefortz, yes_fav_85_95.
