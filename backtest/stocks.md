# Stock price markets against the stock's own swings (stocks.py)

Generated 2026-11-13T15:15:23Z. Paper only. The holdout from 2026-11-10 is not in here.

"Will Nvidia close above $180 on Friday?", "Will Apple finish the week above $240?", "Will Tesla close at $330-$340?" Polymarket has run these every day and week since late 2025: 22,981 finished markets on 15 stocks, 13,857 with real trades. Daily prices (open, high, low, close) from Nasdaq's website reproduce the result of 22,111 of them; the rest are holiday weeks and Netflix before its share split, left out.

They trade thinly: the middle market saw about $350, and the gap between buyers and sellers is often 5-20c.

## The idea

A stock's price right now and how much it usually moves in a day give a fair chance of ending above a line. Compare that with Polymarket's price at moments when the stock's price is known exactly from daily numbers: at the open of the result day, and at the close 1 to 4 trading days before. Only markets that traded in the 3 hours before.

## Who forecasts better?

Score = average squared miss, smaller is better.

| moment | kind | markets | the model | Polymarket | half and half |
|---|---|---|---|---|---|
| the open of the last day | above a line, one day | 3,354 | 0.1035 | 0.1005 | 0.0994 |
| the open of the last day | above a line, end of week | 1,075 | 0.0740 | 0.0700 | 0.0701 |
| the open of the last day | inside a bracket, end of week | 743 | 0.0712 | 0.0712 | 0.0691 |
| the close 1 day(s) before | above a line, one day | 1,433 | 0.0942 | 0.0969 | 0.0937 |
| the close 1 day(s) before | above a line, end of week | 933 | 0.0727 | 0.0738 | 0.0718 |
| the close 1 day(s) before | inside a bracket, end of week | 818 | 0.0512 | 0.0491 | 0.0490 |
| the close 2 day(s) before | above a line, one day | 179 | 0.0890 | 0.0834 | 0.0840 |
| the close 2 day(s) before | above a line, end of week | 646 | 0.0970 | 0.0969 | 0.0954 |
| the close 2 day(s) before | inside a bracket, end of week | 576 | 0.0660 | 0.0651 | 0.0643 |
| the close 3 day(s) before | above a line, one day | 162 | 0.0884 | 0.0886 | 0.0871 |
| the close 3 day(s) before | above a line, end of week | 470 | 0.1306 | 0.1282 | 0.1283 |
| the close 3 day(s) before | inside a bracket, end of week | 313 | 0.0713 | 0.0725 | 0.0712 |
| the close 4 day(s) before | above a line, one day | 202 | 0.0866 | 0.0856 | 0.0850 |
| the close 4 day(s) before | above a line, end of week | 341 | 0.1021 | 0.1059 | 0.1026 |
| the close 4 day(s) before | inside a bracket, end of week | 290 | 0.0634 | 0.0723 | 0.0642 |

A tie. A plain "usual swing" model is as good as the market, and no better.

## Buying where the two disagree

$10 on the side the model calls cheap, at the worst price anyone paid in the next 2 hours + 1c + the fee, and only if it is still cheap at that price.

| what | bets | won | per $100 | first half | second half |
|---|---|---|---|---|---|
| all, model and price 5c+ apart | 905 | 337 | -$24.45 | -$15.62 | -$33.23 |
| all, model and price 10c+ apart | 493 | 177 | -$26.06 | -$21.49 | -$30.58 |
| all, model and price 15c+ apart | 291 | 80 | -$41.06 | -$31.98 | -$50.04 |
| all, model and price 25c+ apart | 83 | 12 | -$53.60 | -$37.72 | -$69.08 |
| at the open of the last day, 10c+ | 367 | 102 | -$35.60 | -$43.21 | -$28.06 |
| after a close, 1-4 days before, 10c+ | 126 | 75 | +$1.99 | +$30.27 | -$26.26 |
| above a line, one day, 10c+ | 329 | 108 | -$26.14 | -$25.65 | -$26.62 |
| above a line, end of week, 10c+ | 104 | 42 | -$33.31 | -$20.54 | -$46.00 |
| inside a bracket, end of week, 10c+ | 60 | 27 | -$13.04 | -$9.23 | -$16.84 |
| only buying Yes, 10c+ | 209 | 75 | -$24.64 | -$21.46 | -$27.78 |
| only buying No, 10c+ | 284 | 102 | -$27.10 | -$29.20 | -$25.00 |
| 10c+, at the next 5 minutes' worst price instead of 2 hours | 226 | 107 | -$11.03 | -$11.18 | -$10.89 |

It loses at the open and is about even after a close (126 bets, first half up, second half down). Where the price disagrees with the model, the price usually knows something the daily numbers don't (news, the stock moving before the open), and the gap between buyers and sellers eats the rest.

## The exam

- **Stock price markets: buy where a swing model and the price are 10c+ apart**: 493 bets in 392 separate groups, -$26.06 per $100, luck range -$37.72 to -$14.39, verdict **Losing**.
- **Stock price markets: same, only after a close 1-4 days before**: 126 bets in 82 separate groups, +$1.99 per $100, luck range -$17.14 to +$21.12, verdict **Ahead, but could be luck**.
- **Stock price markets: same, priced at the next 5 minutes instead of 2 hours**: 226 bets in 196 separate groups, -$11.03 per $100, luck range -$25.46 to +$3.39, verdict **Behind, but could be bad luck**.

**Verdict: dropped, no track.** Same story as the Bitcoin price markets (`optfair.md`): the market is as good as the model, and thin trading makes every disagreement expensive to buy.

## Traps found

- **Crumb trades on the wrong side.** Trades of under $1 often show up at the mirror price (a 5c market "trading" at 95c). When such a crumb is the only trade in the buying window, a backtest buys the winning side for pennies. 5-minute steps with under $5 traded are dropped here; without that, "buy No on long shots after the close" looked like +$26 per $100.
- **No free minute-by-minute stock prices.** From GitHub: Yahoo answers 429, Stooq wants a browser check, Pyth's old chart address is gone. Nasdaq's website gives daily open/high/low/close (`stocks.nasdaq_daily`), which is why the test only looks at opens and closes.
