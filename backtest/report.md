# Backtest: the strategies on past Polymarket markets

Generated 2026-11-08T19:05:15Z. Markets that ended 2026-03-01 to 2026-11-08: 125,712 finished yes/no markets (no sports, volume over $20,000). Paper only. Rerun: `probe` workflow with `btrun` (or `python3 backtest.py all`).

**How to read it.** Each rule track was replayed with its real picking code, hour by hour, seeing only prices up to that moment. Fill = the price then **plus 1c** (history has no order book) plus the market's taker fee. "Worst plausible per $100" is the same trust score the live scoreboard uses (one imaginary total loss added, 90% bar for the whole family). HOLDS UP = that worst case is above $0 after 30+ trades.

## Rule tracks, rule only (no cash limit, so every daily pick counts)

| Track | Trades (won/lost) | Profit | Per $100 bet | Worst plausible per $100 | With 0c / 2c slippage | Older / newer half | Avg days held | Verdict |
|---|---|---|---|---|---|---|---|---|
| `panic_fade_10c` | 632 (437/195) | +$56.82 | +$3.19 | -$1.80 | +$118.92 / -$2.66 | +$40.27 / +$16.54 | 8.4 | promising, not proven |
| `panic_fade_4c` | 787 (634/153) | -$1.70 | +$0.13 | -$3.32 | +$75.66 / -$65.19 | +$14.73 / -$16.43 | 9.1 | loses |
| `panic_fade` | 671 (522/149) | +$3.78 | +$0.29 | -$3.72 | +$69.69 / -$52.09 | +$7.46 / -$3.68 | 8.7 | promising, not proven |
| `endgame_97` | 4875 (4605/270) | -$1,040.42 | -$4.32 | -$5.33 | -$868.40 / -$876.97 | -$474.77 / -$565.65 | 1.3 | loses |
| `yes_fav_85_95` | 422 (386/36) | -$13.36 | -$0.70 | -$5.40 | +$6.69 / -$28.41 | -$6.56 / -$6.80 | 6.1 | loses |
| `endgame_sell98` | 6586 (5359/1227) | -$1,724.28 | -$5.40 | -$6.32 | -$1,104.94 / -$1,719.31 | -$927.32 / -$796.97 | 0.6 | loses |
| `endgame` | 5305 (4895/410) | -$1,419.00 | -$5.49 | -$6.62 | -$1,166.47 / -$1,586.41 | -$712.06 / -$706.94 | 1.4 | loses |
| `endgame_ending_soon` | 4785 (4343/442) | -$1,391.80 | -$6.03 | -$7.34 | -$1,163.46 / -$1,627.08 | -$693.79 / -$698.01 | 1.3 | loses |
| `fav_fee_free` | 509 (459/50) | -$74.62 | -$3.21 | -$7.65 | -$49.17 / -$99.21 | -$59.12 / -$15.50 | 15.0 | loses |
| `no_only_90_97` | 636 (580/56) | -$128.81 | -$4.24 | -$7.93 | -$98.59 / -$155.79 | -$25.52 / -$103.29 | 5.1 | loses |
| `fav_short_90_95` | 675 (600/75) | -$174.03 | -$5.47 | -$9.45 | -$141.80 / -$227.04 | -$54.51 / -$119.52 | 4.1 | loses |
| `fav_short_95_98` | 692 (635/57) | -$207.57 | -$6.16 | -$9.49 | -$175.70 / -$199.79 | -$86.66 / -$120.91 | 3.2 | loses |
| `claude` | 364 (270/94) | -$96.96 | -$5.88 | -$9.82 | -$61.86 / -$127.25 | -$54.23 / -$42.74 | 9.7 | loses |
| `fade_rally` | 364 (218/146) | -$30.31 | -$3.14 | -$9.88 | +$11.43 / -$72.36 | -$20.35 / -$9.96 | 3.4 | loses |
| `fav_cut_losses` | 364 (242/122) | -$116.48 | -$7.08 | -$11.01 | -$81.33 / -$144.20 | -$57.09 / -$59.39 | 5.5 | loses |
| `momentum_week` | 364 (193/171) | -$102.80 | -$7.27 | -$12.10 | -$59.90 / -$130.64 | -$40.05 / -$62.76 | 3.9 | loses |
| `screener` | 456 (383/73) | -$137.83 | -$6.72 | -$12.66 | -$115.49 / -$137.18 | -$42.28 / -$95.55 | 13.9 | loses |
| `fav_mid_80_90` | 394 (312/82) | -$151.84 | -$9.00 | -$16.25 | -$132.54 / -$176.01 | -$37.24 / -$114.60 | 11.9 | loses |
| `fav_bigvol_85_95` | 263 (215/48) | -$123.46 | -$10.29 | -$18.46 | -$110.50 / -$113.00 | -$62.31 / -$61.15 | 31.0 | loses |
| `control_random` | 419 (202/217) | -$46.79 | -$3.29 | -$20.33 | -$25.84 / -$62.39 | -$10.80 / -$35.99 | 15.8 | loses |
| `control_longshot` | 634 (42/592) | -$29.36 | -$15.31 | -$54.85 | +$3.80 / -$48.27 | -$6.17 / -$23.19 | 9.0 | loses |
| `endgame_strict` | 0 (0/0) | +$0.00 | +$0.00 | -$100.00 | +$0.00 / +$0.00 | +$0.00 / +$0.00 | - | too few trades |

Endgame by signal (trades / lost / profit): `endgame_97` ending_soon 4155/237/-$921.68, past_deadline 720/33/-$118.76; `endgame_sell98` ending_soon 5484/1071/-$1,517.36, past_deadline 1102/139/-$206.93; `endgame` ending_soon 4596/360/-$1,251.75, past_deadline 709/50/-$167.25; `endgame_ending_soon` ending_soon 4785/442/-$1,391.79

Favorite-style tracks by topic (trades / lost / profit): `endgame_97` box office 69/1/-$0.61, crypto price 1241/37/-$109.53, other 1341/48/-$152.61, post counts 222/7/-$21.24, weather 2002/177/-$756.45; `yes_fav_85_95` box office 5/0/+$1.95, crypto price 268/18/+$10.43, other 148/18/-$26.12, weather 1/0/+$0.38; `endgame_sell98` box office 83/10/-$0.42, crypto price 1897/456/-$412.45, other 1438/204/-$212.72, post counts 273/41/-$35.17, weather 2895/499/-$1,063.53; `endgame` box office 67/1/+$2.79, crypto price 1258/57/-$140.59, other 1394/65/-$158.74, post counts 228/8/-$15.29, weather 2358/279/-$1,107.17; `endgame_ending_soon` box office 60/2/+$1.32, crypto price 1271/65/-$122.69, other 1127/68/-$146.54, post counts 223/15/-$37.91, weather 2104/292/-$1,085.97; `fav_fee_free` box office 9/1/-$1.41, crypto price 1/0/+$0.22, other 457/43/-$58.39, post counts 6/0/+$1.86, weather 36/6/-$16.90; `no_only_90_97` box office 19/1/-$0.50, crypto price 327/23/-$38.01, other 136/18/-$57.99, post counts 124/12/-$30.55, weather 30/2/-$1.76; `fav_short_90_95` box office 16/1/+$0.22, crypto price 315/27/-$44.01, other 182/27/-$80.40, post counts 124/11/-$16.42, weather 38/9/-$33.44; `fav_short_95_98` box office 11/2/-$8.99, crypto price 303/18/-$57.52, other 151/13/-$47.55, post counts 114/5/-$11.69, weather 113/19/-$81.82; `claude` box office 5/2/-$2.20, other 350/89/-$87.52, post counts 3/1/-$1.50, weather 6/2/-$5.75; `fav_cut_losses` box office 11/4/-$3.09, crypto price 3/0/+$0.58, other 283/89/-$91.97, post counts 59/26/-$21.54, weather 8/3/-$0.46; `screener` box office 9/1/-$0.01, crypto price 3/0/+$1.05, other 387/66/-$129.69, post counts 52/6/-$11.83, weather 5/0/+$2.65; `fav_mid_80_90` box office 11/4/-$12.81, crypto price 2/0/+$1.23, other 313/64/-$110.97, post counts 62/13/-$27.69, weather 6/1/-$1.61; `fav_bigvol_85_95` crypto price 14/1/+$0.56, other 231/45/-$120.65, post counts 12/0/+$3.94, weather 6/2/-$7.31; `control_longshot` box office 5/5/-$2.11, crypto price 315/301/-$37.76, other 306/279/+$8.56, post counts 7/6/+$2.47, weather 1/1/-$0.52

## Rule tracks as configured (real budget and max open)

| Track | Budget | Trades (won/lost) | Profit | Most money tied up | Ran out of cash (skips) | Refills | Still open at the end |
|---|---|---|---|---|---|---|---|
| `panic_fade_10c` | $500 | 293 (211/82) | +$87.41 | $72.81 | 0 | 0 | 0 |
| `panic_fade_4c` | $500 | 306 (244/62) | +$62.50 | $81.13 | 0 | 0 | 0 |
| `panic_fade` | $50 | 120 (89/31) | +$28.03 | $31.94 | 0 | 0 | 0 |
| `endgame_97` | $500 | 2640 (2509/131) | -$481.23 | $197.75 | 3402 | 0 | 2 |
| `yes_fav_85_95` | $500 | 416 (380/36) | -$15.94 | $137.17 | 0 | 0 | 2 |
| `endgame_sell98` | $500 | 1794 (1489/305) | -$494.18 | $194.17 | 4292 | 0 | 1 |
| `endgame` | $100 | 551 (521/30) | -$76.02 | $97.56 | 5009 | 0 | 3 |
| `endgame_ending_soon` | $500 | 1721 (1556/165) | -$492.45 | $193.45 | 4112 | 0 | 1 |
| `fav_fee_free` | $500 | 452 (406/46) | -$76.36 | $188.47 | 0 | 0 | 3 |
| `no_only_90_97` | $500 | 631 (575/56) | -$130.19 | $191.10 | 0 | 0 | 0 |
| `fav_short_90_95` | $500 | 675 (600/75) | -$174.03 | $164.67 | 0 | 0 | 1 |
| `fav_short_95_98` | $500 | 692 (635/57) | -$207.57 | $136.94 | 0 | 0 | 4 |
| `claude` | $50 | 123 (105/18) | -$14.11 | $46.42 | 134 | 0 | 0 |
| `fade_rally` | $500 | 364 (218/146) | -$30.31 | $40.11 | 0 | 0 | 0 |
| `fav_cut_losses` | $500 | 364 (242/122) | -$116.48 | $86.01 | 0 | 0 | 0 |
| `momentum_week` | $500 | 364 (193/171) | -$102.80 | $59.19 | 0 | 0 | 0 |
| `screener` | $20 | 15 (10/5) | -$19.28 | $18.53 | 151 | 0 | 0 |
| `fav_mid_80_90` | $500 | 380 (299/81) | -$154.15 | $130.12 | 0 | 0 | 0 |
| `fav_bigvol_85_95` | $500 | 218 (175/43) | -$120.53 | $138.47 | 0 | 0 | 2 |
| `control_random` | $500 | 357 (165/192) | -$75.47 | $90.53 | 0 | 0 | 5 |
| `control_longshot` | $500 | 621 (39/582) | -$38.33 | $16.59 | 0 | 0 | 2 |
| `endgame_strict` | $500 | 0 (0/0) | +$0.00 | $0.00 | 0 | 0 | 0 |

## Copy tracks (the wallets' own trades, our price = theirs + 1c)

**Warning:** the 40 `w_*` wallets were chosen on 2026-11-08 *because* they made money in this same period. Their backtest is flattering by design. It mainly shows whether copying them a few minutes late still keeps their edge, not whether they will keep winning.

| Track | Trades (won/lost) | Profit | Per $100 bet | Worst plausible per $100 | Most money tied up | Verdict |
|---|---|---|---|---|---|---|
| `w_youngalphagoat` | 651 (428/223) | +$267.42 | +$21.67 | +$7.58 | $225.33 | HOLDS UP |
| `w_dominus` | 564 (389/175) | +$202.13 | +$13.61 | +$2.55 | $119.62 | HOLDS UP |
| `w_dropper` | 974 (575/399) | +$282.82 | +$17.30 | +$0.14 | $137.54 | HOLDS UP |
| `w_lava_lava` | 731 (350/381) | +$133.54 | +$24.46 | -$1.79 | $168.50 | promising, not proven |
| `w_the_joker` | 1479 (913/566) | +$123.24 | +$2.74 | -$5.08 | $215.73 | promising, not proven |
| `w_bertapotamous` | 1064 (616/448) | +$34.62 | +$9.35 | -$5.98 | $141.23 | promising, not proven |
| `w_blondbeast` | 286 (209/77) | +$51.55 | +$7.82 | -$6.81 | $79.88 | promising, not proven |
| `w_ecash` | 279 (196/83) | +$85.69 | +$7.41 | -$7.34 | $146.12 | promising, not proven |
| `w_groth` | 251 (164/87) | +$85.11 | +$9.73 | -$7.50 | $126.74 | promising, not proven |
| `w_eightpenguins` | 297 (154/143) | +$110.48 | +$23.50 | -$8.12 | $75.05 | promising, not proven |
| `w_0x448861` | 2132 (1085/1047) | -$137.46 | -$1.48 | -$8.73 | $96.13 | loses |
| `w_rabbitfoot1` | 763 (402/361) | -$2.80 | +$2.03 | -$9.94 | $44.45 | loses |
| `w_new_jeans` | 1194 (574/620) | +$97.05 | +$1.74 | -$10.14 | $190.42 | ahead, but could be luck |
| `w_albert_1953` | 1359 (729/630) | +$151.46 | +$0.17 | -$10.40 | $241.91 | ahead, but could be luck |
| `w_tunatyler` | 718 (364/354) | +$94.75 | +$3.05 | -$10.65 | $89.88 | ahead, but could be luck |
| `w_debased` | 1727 (827/900) | +$0.95 | +$0.70 | -$11.43 | $244.99 | ahead, but could be luck |
| `w_bigggggggg` | 295 (228/67) | +$14.97 | +$0.89 | -$11.45 | $334.36 | ahead, but could be luck |
| `w_rememberamalek` | 677 (367/310) | +$118.76 | +$2.61 | -$11.55 | $211.57 | ahead, but could be luck |
| `mirror_unlimited` | 100 (75/25) | +$25.17 | +$5.95 | -$11.71 | $261.47 | ahead, but could be luck |
| `w_flawfence` | 241 (134/107) | +$74.24 | +$11.98 | -$11.90 | $196.97 | ahead, but could be luck |
| `w_sbel` | 318 (222/96) | +$19.88 | +$1.03 | -$11.96 | $100.32 | ahead, but could be luck |
| `sab_big` | 31 (27/4) | +$16.78 | +$15.86 | -$12.22 | $102.78 | ahead, but could be luck |
| `w_jjo` | 432 (264/168) | +$51.60 | +$6.48 | -$12.49 | $108.90 | ahead, but could be luck |
| `w_thereturnofdarthmaul` | 279 (153/126) | +$7.38 | -$2.48 | -$14.83 | $283.37 | ahead, but could be luck |
| `w_betwick` | 447 (236/211) | +$105.00 | +$9.69 | -$15.32 | $105.63 | ahead, but could be luck |
| `w_hellyeahtrader` | 160 (104/56) | +$34.02 | +$9.66 | -$16.15 | $66.37 | ahead, but could be luck |
| `sab_hold` | 94 (73/21) | +$22.44 | +$5.47 | -$16.50 | $279.90 | ahead, but could be luck |
| `w_pako` | 215 (139/76) | -$5.42 | +$4.87 | -$18.60 | $109.77 | loses |
| `w_hauchn` | 131 (53/78) | +$53.08 | +$45.34 | -$20.12 | $47.24 | ahead, but could be luck |
| `w_vilgefortz` | 243 (139/104) | -$14.41 | -$1.92 | -$20.14 | $44.71 | loses |
| `mirror` | 45 (31/14) | +$16.36 | +$9.43 | -$20.94 | $34.59 | ahead, but could be luck |
| `w_balerinacapuchina` | 96 (63/33) | +$12.77 | +$11.96 | -$21.83 | $42.85 | ahead, but could be luck |
| `w_tokor` | 298 (165/133) | +$64.53 | +$1.19 | -$23.11 | $188.18 | ahead, but could be luck |
| `w_railcool` | 108 (53/55) | +$30.27 | +$28.09 | -$23.78 | $71.36 | ahead, but could be luck |
| `favorites` | 24 (20/4) | +$1.40 | +$1.81 | -$24.49 | $17.41 | ahead, but could be luck |
| `w_lpgb` | 114 (77/37) | -$14.18 | -$3.54 | -$25.68 | $313.44 | loses |
| `w_jsram` | 216 (109/107) | -$41.75 | -$9.48 | -$29.14 | $32.46 | loses |
| `w_wan123` | 407 (166/241) | +$22.42 | -$6.60 | -$29.77 | $139.16 | ahead, but could be luck |
| `w_anoin123` | 266 (139/127) | -$70.41 | -$16.15 | -$34.63 | $178.29 | loses |
| `w_hell0pia` | 81 (49/32) | +$29.47 | +$50.21 | -$39.14 | $37.05 | ahead, but could be luck |
| `w_cigarettes` | 92 (51/41) | -$12.21 | -$17.66 | -$43.97 | $212.29 | loses |
| `w_dromedaryy` | 87 (38/49) | +$9.40 | +$27.93 | -$49.07 | $65.89 | ahead, but could be luck |
| `w_monopoly_money` | 93 (52/41) | -$8.35 | -$0.25 | -$52.44 | $59.63 | loses |
| `w_underperformingforal` | 17 (6/11) | -$23.61 | -$44.61 | -$100.00 | $28.11 | loses |
| `w_aghy` | 15 (5/10) | +$4.24 | +$25.05 | -$100.00 | $15.98 | ahead, but could be luck |

## Not replayed

- `arb`, `every_horse`: need old order books (and Kalshi pairs). No history for those.
- `endgame_strict` and the resolved/proposed tiers: Polymarket doesn't keep when a result was proposed. Only the past-deadline and ending-soon signals are replayed for the endgame tracks.
- `consensus_2/3`: need all 40 wallets' full books at each moment; not rebuilt yet.

## What can make this look better than reality

- No order-book depth: at 5 shares that's fine; at $300-500 a trade the price would be worse.
- Volume filter uses each market's final volume (the live bot sees volume so far). Liquidity filters are off.
- Trades on the same day often share one news risk, so they aren't fully independent; the worst-case number is a bit too kind for the favorite tracks.
- Fees use each market's current fee setting.

