# Fade test: buy the cheap side of "sure" markets that end within a day

Run 2026-11-08 (probe `btfade`, run 42516653459), markets that ended 2026-03-01 to 2026-11-08. These are the same picks as `endgame_ending_soon`, with the favorite at 85-99c, but we buy the OTHER side: 5 shares a bet, held to the result. Price = 1 - favorite's history price + slippage + taker fee. Profit is for 5 shares a bet, and the number in brackets is per $100 staked. Paper only. Rerun: `python3 backtest.py btfade` (start it on `main` so it uses the shared cache).

**Big caveat:** history has no order book. On thin bucket markets the real ask on the cheap side can be several cents above (1 - favorite price). The live `fade_sure` track fills on the real book.

## By topic

| Slice | Bets | Cheap side won | Avg cheap price | Profit at +1c (per $100) | at +2c | at +3c |
|---|---|---|---|---|---|---|
| all | 5818 | 590 | 5.0c | +$1,117.05 (+$60.94) | +$814.29 (+$38.13) | +$511.81 (+$20.99) |
| weather | 2425 | 383 | 5.6c | +$1,084.31 (+$130.53) | +$958.22 (+$100.15) | +$832.25 (+$76.86) |
| crypto price | 1388 | 85 | 4.9c | -$11.40 (-$2.61) | -$85.52 (-$16.75) | -$159.54 (-$27.29) |
| post counts | 238 | 15 | 5.0c | +$1.16 (+$1.57) | -$11.20 (-$13.00) | -$23.55 (-$23.90) |
| other | 1697 | 104 | 4.4c | +$49.55 (+$10.53) | -$37.04 (-$6.65) | -$123.58 (-$19.20) |
| box office | 70 | 3 | 5.0c | -$6.56 (-$30.44) | -$10.17 (-$40.41) | -$13.77 (-$47.87) |

## Does it last? (older vs newer half)

| Slice | Bets | Cheap side won | Avg cheap price | Profit at +1c (per $100) | at +2c | at +3c |
|---|---|---|---|---|---|---|
| weather older | 1338 | 206 | 5.6c | +$569.00 (+$123.43) | +$499.53 (+$94.17) | +$430.12 (+$71.70) |
| weather newer | 1087 | 177 | 5.5c | +$515.30 (+$139.39) | +$458.69 (+$107.60) | +$402.13 (+$83.28) |
| crypto price older | 664 | 31 | 4.5c | -$44.23 (-$22.20) | -$79.96 (-$34.03) | -$115.63 (-$42.73) |
| crypto price newer | 724 | 54 | 5.2c | +$32.83 (+$13.84) | -$5.56 (-$2.02) | -$43.90 (-$13.99) |

## Live rule candidate (cheap side 2-10c)

| Slice | Bets | Cheap side won | Avg cheap price | Profit at +1c (per $100) | at +2c | at +3c |
|---|---|---|---|---|---|---|
| weather | 2103 | 350 | 6.2c | +$959.29 (+$121.32) | +$850.00 (+$94.45) | +$740.81 (+$73.41) |
| crypto price | 1150 | 82 | 5.6c | +$5.06 (+$1.25) | -$56.26 (-$12.07) | -$117.50 (-$22.27) |
| post counts | 201 | 14 | 5.6c | +$0.91 (+$1.31) | -$9.52 (-$11.97) | -$19.94 (-$22.17) |

Decision: the `fade_sure` track trades **weather only**. A sample of the weather wins looked like real bucket misses (Austin 88-89F, NYC 88-89F, Paris 26C, Seoul 26C...). The full log has the price and hours-left splits; every price band from 2c to 16c was positive at +1c.
