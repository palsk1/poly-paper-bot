# Backtest sanity checks

## What it means (written 2026-11-09)

- **The engine is honest.** On fake fair markets every strategy loses just its costs, a planted stop-loss bug is caught, and a separate second simulator agrees with the engine on all 8,646 real trades.
- **One real flaw, found and priced:** price history is 12-hourly, so a take-profit is often first seen far above its target and was booked there. The live bot (every 5 minutes) would sell near the target. That alone was worth about $67 of panic_fade_10c's backtest profit. Sold at the target, `panic_fade_10c` goes from +$2.57 to -$0.46 per $100, and to -$3.11 at +2c with a 1-hour-late entry. **No strategy is ahead on the pessimistic numbers.**
- **The panic signal is real but too small:** panic entries beat random entries with the same exits by about $3-7 per $100, but not by enough to pay the costs. The sweep's best setting (15c drop) wins one half (+$1.32) and loses the other (-$0.84): a coin flip, not an edge.
- **The favorite rules are worse than random:** screener, fav_mid, fav_bigvol, fav_short and no_only lose $3-9 per $100 more than random bets in the same price band.
- **mention_no, rebuilt from scratch (one bet per event):** +$4.35 per $100 at +2c on 52 events, but the 90% band runs from -$15 to +$23, the second half is slightly negative and it's about $0 at +5c. Weaker than calib.md's +$15. Buying YES in the same markets loses $14, so "fans overrate the word" still points the right way; it's just not proven. The holdout (markets ending 2026-11-10 on, scored once from 2026-12-21) decides.

Generated 2026-11-09T19:21:51Z by `btcheck.py` (probe `btcheck`). Paper only. 126,352 finished markets that ended before 2026-11-10; later ones are the holdout (backtest/PROTOCOL.md). Money is per $100 staked.

## 1. Fair-coin world (fake markets where every price is exactly right)

Every strategy, run through the real backtest engine at +1c. With the costs added back, each should land near $0. A track outside its band would mean the engine invents or loses money by itself.

| Track | Trades | Profit per $100 | Same, costs added back (should be ~$0) | 99% band | OK? |
|---|---|---|---|---|---|
| `panic_fade_4c` | 907 | -$2.24 | +$0.78 | -$1.46 to +$3.02 | yes |
| `panic_fade` | 648 | -$2.39 | +$0.79 | -$2.16 to +$3.74 | yes |
| `control_longshot` | 496 | -$19.75 | -$4.67 | -$41.03 to +$31.69 | yes |
| `screener` | 477 | +$1.16 | +$2.47 | -$1.36 to +$6.31 | yes |
| `fav_short_90_95` | 472 | +$0.50 | +$1.69 | -$1.24 to +$4.62 | yes |
| `panic_fade_10c` | 469 | -$0.93 | +$2.88 | -$1.16 to +$6.93 | yes |
| `no_only_90_97` | 458 | +$0.67 | +$1.83 | -$0.80 to +$4.46 | yes |
| `fav_fee_free` | 453 | +$1.00 | +$2.08 | -$1.03 to +$5.18 | yes |
| `fav_short_95_98` | 449 | -$0.11 | +$0.96 | -$0.97 to +$2.89 | yes |
| `fav_cut_losses` | 342 | -$1.45 | +$1.12 | -$0.91 to +$3.14 | yes |
| `claude` | 341 | -$1.80 | +$0.50 | -$1.77 to +$2.78 | yes |
| `momentum_week` | 336 | -$2.34 | +$1.44 | -$1.93 to +$4.81 | yes |
| `fav_mid_80_90` | 333 | +$2.96 | +$4.37 | -$0.64 to +$9.38 | yes |
| `fade_rally` | 333 | -$1.51 | +$3.42 | -$1.07 to +$7.91 | yes |
| `yes_fav_85_95` | 319 | -$2.98 | -$1.73 | -$6.61 to +$3.16 | yes |
| `control_random` | 318 | -$0.71 | +$2.02 | -$10.35 to +$14.39 | yes |

Result: all inside their band.

Planted bug (stop-loss booked at the stop price even when the price had gapped past it, the Reddit poster's bug). The check must flag it:

| Track | Trades | Profit per $100 | Same, costs added back (should be ~$0) | 99% band | OK? |
|---|---|---|---|---|---|
| `panic_fade` | 648 | +$0.62 | +$3.80 | +$1.51 to +$6.10 | **NO** |
| `panic_fade_10c` | 469 | +$3.48 | +$7.30 | +$4.15 to +$10.45 | **NO** |
| `fav_cut_losses` | 342 | +$0.54 | +$3.11 | +$1.60 to +$4.61 | **NO** |
| `claude` | 341 | +$0.09 | +$2.40 | +$0.74 to +$4.05 | **NO** |

Result: caught: panic_fade, panic_fade_10c, fav_cut_losses, claude. (27s)

## 2. Second simulator vs the backtest engine (real data, +1c)

A separate, small simulator re-walked every trade from the raw price history.

| Track | Trades | Entry off | Exit off | Profit off | Biggest gap | Take-profits (seen above target) | Extra profit from those | Stops gapped through |
|---|---|---|---|---|---|---|---|---|
| `panic_fade_4c` | 787 | 0 | 0 | 0 | $0.0000 | 613 (515) | +$67.96 | 147 (146) |
| `fav_short_95_98` | 692 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `fav_short_90_95` | 675 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `panic_fade` | 671 | 0 | 0 | 0 | $0.0000 | 504 (432) | +$57.20 | 143 (140) |
| `no_only_90_97` | 636 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `control_longshot` | 634 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `panic_fade_10c` | 632 | 0 | 0 | 0 | $0.0000 | 421 (375) | +$66.95 | 189 (182) |
| `fav_fee_free` | 509 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `screener` | 456 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `yes_fav_85_95` | 422 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `control_random` | 419 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `fav_mid_80_90` | 394 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |
| `claude` | 364 | 0 | 0 | 0 | $0.0000 | 251 (244) | +$11.92 | 90 (86) |
| `fav_cut_losses` | 364 | 0 | 0 | 0 | $0.0000 | 224 (215) | +$12.73 | 118 (113) |
| `momentum_week` | 364 | 0 | 0 | 0 | $0.0000 | 176 (147) | +$31.87 | 167 (159) |
| `fade_rally` | 364 | 0 | 0 | 0 | $0.0000 | 212 (200) | +$78.57 | 139 (131) |
| `fav_bigvol_85_95` | 263 | 0 | 0 | 0 | $0.0000 | 0 (0) | +$0.00 | 0 (0) |

Disagreements: 0.

History is 12-hourly until the last 2 days, so a take-profit is often first SEEN well above its target. The engine sells at the price it sees, but the live bot (every 5 minutes) would have sold near the target. The pessimistic numbers below sell at the target.

## 5. Pessimistic costs

Per $100, take-profits capped at the target. 1c = the old main case. 2c = one tick worse. '1h later' = buy at the price an hour after the signal. 'next print' = buy at the next recorded price (often 12 hours later in this history).

| Track | 1c, as before | 1c, TP capped | 2c | 2c + 1h later | 2c + next print | 1st / 2nd half (2c + 1h) |
|---|---|---|---|---|---|---|
| `panic_fade_10c` | +$2.57 | -$0.46 (632) | -$3.11 (631) | -$3.11 (630) | -$6.33 (551) | -$1.75 / -$4.44 |
| `yes_fav_85_95` | -$0.69 | -$0.69 (422) | -$1.45 (423) | -$1.45 (423) | -$2.55 (415) | -$2.08 / -$0.84 |
| `panic_fade` | +$0.14 | -$2.04 (671) | -$4.23 (659) | -$4.06 (659) | -$6.45 (537) | -$3.61 / -$4.50 |
| `panic_fade_4c` | -$0.05 | -$2.23 (787) | -$4.35 (772) | -$4.31 (772) | -$5.49 (637) | -$3.28 / -$5.31 |
| `fav_fee_free` | -$3.15 | -$3.15 (509) | -$4.42 (480) | -$4.41 (480) | -$3.89 (449) | -$5.25 / -$3.58 |
| `no_only_90_97` | -$4.25 | -$4.25 (636) | -$5.13 (635) | -$5.13 (635) | -$5.51 (635) | -$3.18 / -$7.06 |
| `control_random` | -$4.41 | -$4.41 (419) | -$5.84 (419) | -$5.84 (419) | -$6.38 (420) | -$2.94 / -$8.77 |
| `fav_short_90_95` | -$5.48 | -$5.48 (675) | -$7.15 (673) | -$7.15 (673) | -$4.69 (661) | -$5.54 / -$8.74 |
| `fav_short_95_98` | -$6.14 | -$6.14 (692) | -$5.96 (684) | -$5.78 (682) | -$4.40 (671) | -$4.28 / -$7.28 |
| `claude` | -$5.84 | -$6.56 (364) | -$8.36 (364) | -$8.30 (364) | -$7.65 (362) | -$7.68 / -$8.92 |
| `screener` | -$6.71 | -$6.71 (456) | -$6.67 (456) | -$6.68 (456) | -$7.61 (456) | -$4.63 / -$8.73 |
| `fav_cut_losses` | -$7.04 | -$7.81 (364) | -$9.46 (364) | -$9.46 (364) | -$7.78 (364) | -$9.42 / -$9.50 |
| `fav_mid_80_90` | -$8.87 | -$8.87 (394) | -$10.26 (393) | -$10.26 (393) | -$9.18 (393) | -$8.38 / -$12.13 |
| `momentum_week` | -$7.64 | -$10.01 (364) | -$11.95 (364) | -$11.95 (364) | -$10.60 (364) | -$9.59 / -$14.33 |
| `fav_bigvol_85_95` | -$10.30 | -$10.30 (263) | -$9.80 (252) | -$9.80 (252) | -$10.95 (234) | -$9.78 / -$9.82 |
| `fade_rally` | -$3.08 | -$11.05 (364) | -$14.40 (364) | -$14.40 (364) | -$15.77 (364) | -$15.86 / -$12.95 |
| `control_longshot` | -$12.26 | -$12.26 (634) | -$18.69 (634) | -$18.66 (634) | -$18.64 (635) | -$16.75 / -$20.49 |

## 3. Random entries on the real data, held to the end

24,981 random (market, moment, side) picks. If prices are fair on average, this loses about the costs.

| Slippage | Per $100 | 90% band |
|---|---|---|
| +0c | -$2.32 | -$3.18 to -$1.45 |
| +1c | -$4.20 | -$5.05 to -$3.36 |
| +2c | -$6.01 | -$6.84 to -$5.18 |

By price at +1c (costs = slippage + fee per $100 staked):

| Price | Bets | Per $100 | Costs alone |
|---|---|---|---|
| 2-20c | 5334 | +$8.42 | -$13.65 |
| 20-50c | 5724 | -$0.43 | -$5.51 |
| 50-80c | 8582 | -$7.71 | -$4.01 |
| 80-98c | 5341 | -$3.61 | -$1.41 |

(1s)

## 4. Each strategy vs random entries with the same exits (+1c, take-profits at the target)

Twins: random markets open at the same hour, same days-to-end window, same take-profit / stop rules. 'Same band' = the twin's side is also in the strategy's price band; 'any' = any side at 5-95c. Strategy column is the second simulator's own replay of the strategy's trades.

| Track | Trades | Strategy | Random, same band | Random, any price | Beats same-band twins by | 90% band of that |
|---|---|---|---|---|---|---|
| `panic_fade_10c` | 632 | -$0.46 | -$7.07 | -$8.51 | +$6.62 | +$3.83 to +$9.40 |
| `yes_fav_85_95` | 422 | -$0.69 | -$2.18 | -$0.98 | +$1.49 | -$1.42 to +$4.41 |
| `panic_fade` | 671 | -$1.93 | -$4.49 | -$8.87 | +$2.56 | +$0.24 to +$4.88 |
| `panic_fade_4c` | 787 | -$2.23 | -$6.95 | -$7.25 | +$4.72 | +$2.70 to +$6.73 |
| `fav_fee_free` | 509 | -$3.15 | -$3.75 | -$4.78 | +$0.60 | -$2.13 to +$3.33 |
| `no_only_90_97` | 636 | -$4.25 | -$0.99 | -$4.94 | -$3.26 | -$5.45 to -$1.08 |
| `control_random` | 419 | -$4.41 | -$1.54 | -$3.41 | -$2.87 | -$11.48 to +$5.75 |
| `fav_short_90_95` | 675 | -$5.48 | -$1.99 | -$2.15 | -$3.50 | -$5.93 to -$1.06 |
| `fav_short_95_98` | 692 | -$6.14 | -$1.77 | -$4.50 | -$4.36 | -$6.27 to -$2.45 |
| `claude` | 364 | -$6.56 | -$4.01 | -$6.04 | -$2.55 | -$4.80 to -$0.29 |
| `screener` | 456 | -$6.71 | -$0.60 | +$0.18 | -$6.12 | -$9.68 to -$2.56 |
| `fav_cut_losses` | 364 | -$7.81 | -$5.75 | -$7.24 | -$2.07 | -$4.39 to +$0.26 |
| `fav_mid_80_90` | 394 | -$8.87 | -$1.96 | -$2.86 | -$6.91 | -$11.45 to -$2.37 |
| `momentum_week` | 364 | -$9.87 | -$8.68 | -$9.72 | -$1.20 | -$4.37 to +$1.98 |
| `fav_bigvol_85_95` | 263 | -$10.30 | -$1.23 | -$8.55 | -$9.07 | -$13.89 to -$4.25 |
| `fade_rally` | 364 | -$11.05 | -$9.96 | -$8.76 | -$1.09 | -$4.74 to +$2.56 |
| `control_longshot` | 634 | -$12.26 | -$9.17 | -$2.48 | -$3.09 | -$28.68 to +$22.50 |

(3s)

## 6. Panic family: sweep on one half, test on the other (2c + 1h later, TP capped)

12 versions of the panic rule (drop size x lowest price). Halves split at 2026-05-11 (the middle trade of the family).

| Variant (drop, lowest price) | Trades | Per $100 (TP capped) | 1st half | 2nd half |
|---|---|---|---|---|
| 4c drop, 45c | 903 | -$5.24 | -$4.33 (457) | -$6.15 (446) |
| 4c drop, 55c | 951 | -$5.63 | -$5.02 (487) | -$6.25 (464) |
| 6c drop, 45c | 819 | -$4.49 | -$3.78 (421) | -$5.22 (398) |
| 6c drop, 55c | 829 | -$4.97 | -$4.81 (427) | -$5.14 (402) |
| 8c drop, 45c | 704 | -$3.93 | -$2.42 (354) | -$5.42 (350) |
| 8c drop, 55c | 686 | -$4.66 | -$4.07 (340) | -$5.23 (346) |
| 10c drop, 45c | 630 | -$3.11 | -$1.66 (317) | -$4.55 (313) |
| 10c drop, 55c | 602 | -$4.63 | -$4.04 (295) | -$5.18 (307) |
| 12c drop, 45c | 560 | -$2.02 | -$0.54 (277) | -$3.45 (283) |
| 12c drop, 55c | 519 | -$3.97 | -$3.45 (247) | -$4.44 (272) |
| 15c drop, 45c | 455 | +$0.17 | +$1.32 (217) | -$0.84 (238) |
| 15c drop, 55c | 395 | -$2.47 | -$2.00 (180) | -$2.86 (215) |

- Best on the 1st half: `_sw_15_45` at +$1.32. On the 2nd half it made -$0.84 (band -$5.07 to +$3.39).
- Best on the 2nd half: `_sw_15_45` at -$0.84. On the 1st half it made +$1.32 (band -$3.27 to +$5.91).

(84s)

## 7. mention_no rebuilt from scratch

Own code: one bet per event, bought the first time a 'will X say Y' market is within 7 days of its end with NO at 25-90c, held to the result. Includes the small-market sample. calib.md said +$15 per $100.

| Test | Events | Per $100 | 90% band | 1st half / 2nd half |
|---|---|---|---|---|
| **mention_no rule, NO 25-90c, +2c** | 52 | +$4.35 | -$14.54 to +$23.23 | +$9.34 / -$1.14 |
| same, +1c | 52 | +$6.20 | -$13.03 to +$25.44 | +$11.20 / +$0.71 |
| same, +3c (1 tick worse) | 52 | +$2.56 | -$15.99 to +$21.11 | +$7.55 / -$2.91 |
| same, +3c and wait for the next price print | 52 | -$1.06 | -$19.29 to +$17.17 | +$3.23 / -$5.81 |
| same, +5c (thin books) | 52 | -$0.84 | -$18.76 to +$17.08 | +$4.14 / -$6.28 |
| control: YES side instead, +2c | 53 | -$14.09 | -$33.04 to +$4.86 | -$25.05 / -$4.48 |
| control: random side, +2c | 53 | -$15.55 | -$35.65 to +$4.56 | -$3.28 / -$27.29 |
| control: same rule on all OTHER topics, +2c | 6119 | -$8.11 | -$9.45 to -$6.77 | -$8.46 / -$7.74 |

Total run 887s.
