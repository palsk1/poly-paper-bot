# Kalshi's new all-day families: table tennis and e-sports (27 Nov 2026)

Research only, paper only. `kesport.py`, data `bt_cache/nf/kes/` (shared store folder `bt_cache/nf`).

Every bet is bought at the real asking price 2 minutes before the scheduled start (start time from the event name, never from the close), plus Kalshi's fee, $10 a bet, one bet per game. 'First half' = the older half of each family's games, where rules were picked; 'fresh half' = the newer half, the check.

## Short version (for Jan)

**Nothing here beats the price when you buy.** Six new Kalshi families, about 36,000 finished games with a real
pre-game price: Liga Pro table tennis (5,400 games), TT Elite table tennis (6,754, Kalshi stopped it on 3 Oct),
TT Star table tennis (485, stopped 16 Oct), eBasketball (4,196), eSoccer (18,894) and eFootball (177).

- **Player ratings (Elo) from Kalshi's own results lose to the price in every family**, even though these leagues are
  new. Mixing Elo into the price adds nothing (fresh-half miss scores equal to the price alone). Buying where Elo says a
  side is worth 10c+ more than the ask: Liga Pro -$4.50 per $100 (1,215 bets), TT Elite -$11.59 (1,244), TT Star -$16.95,
  eBasketball -$3.28 (397), eSoccer -$2.24 (861), eFootball -$20.24. Verdicts "Losing" or "Behind, but could be bad luck".
- **Price-only cuts** (price band, hour of day, games played in the last 6 hours, last result, form, late price moves,
  busy or quiet books, the eSoccer tie at the ask): about 50 per family, nearly all lose $2-20 per $100 at the ask,
  because the gap between buy and sell prices (1-9c) is bigger than any lean. The best first-half cuts all lost on the
  fresh half.
- **Backward look:** upsets (winner under 35c) happen about as often as the price says; nothing they shared beforehand
  (last result, tiredness, night games, Elo, a falling price) made buying underdogs pay.
- **One lean, and it is fading:** a *waiting* bid (not buying the offer) on the eSoccer "Tie" 30 minutes before the
  start, 1c above the best bid, counted as filled only when a real trade happened at or below our price: 800 fills,
  +$12.73 per $100, first half +$14.30, fresh half +$11.68, exam "Ahead, but could be luck" (57 cuts tried on eSoccer).
  But the last 14 days were about even (+$0.97 per $100 on 303 fills) and since 24 Nov it fills about once a day:
  the tie's buy-sell gap closed from ~5c to ~2c, so someone else now sits there. No track.

**Ceiling of the one lean (rough guess):** best average day so far about $15-20 at $10 a bid (fresh half), now about $0
(1 fill a day); money needed about $100 (most out at once was $99); stops growing at about $10 a game (others traded
about 54 contracts at or below our price per fill); bad day -$225.

**Recommendation:** no paper track. Free re-check in 3 weeks on games after 27 Nov with the rule exactly as written
here (eSoccer Tie, 30 min before, best bid +1c, real trade at or below our price, hold): only worth a look if fills come
back above ~10 a day and it stays ahead.

**Traps found:** (1) the scheduled start is in the event name in New York time (`26NOV271100` = 27 Nov 11:00 New York);
the close time is when the result came in, never use it. (2) Kalshi only returns a candle for minutes where something
changed: carry the last quote forward. (3) Markets older than 28 Sep (TT Elite, TT Star) are not in the batch candle call;
fetch them one by one (`hist`). (4) eSoccer has many duplicate, cancelled events (settled at 33c each, result `scalar`):
drop them. (5) A 2c bid on a 16c tie is a stale empty book, not a bargain: the first version of the tie lean got most
of its profit from 4 such fills paying $200-500 each; a 10c limit on the buy-sell gap removes them. (6) With a waiting
bid, "the sell offer touched our price" is kinder than "a real trade happened at our price" (1,124 fills, about +$19
per $100, vs 800 fills, +$12.73). (7) Most of these markets trade little before the start (typical game 14-211
contracts before the start, 1,000-4,000 including live play): the money is in live trading, which this dig did not test.

## Details per family

## Liga Pro table tennis (`KXLIGAPROMATCH`)

5400 games with a usable price (6001 settled with a quote, skipped {'shape': 434, 'noquote': 11}), 14 Oct to 27 Nov, about 122 a day. Contracts traded before the start, typical game: 137 (busiest tenth 1355); whole game incl. live: 3594.

- Forecast check, first half (1455 games, both players 5+ earlier games): price miss score 0.6616, Elo (K=24) 0.6840 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (2546 games, both players 5+ earlier games): price miss score 0.6507, Elo (K=24) 0.6812 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 0.91, Elo 0.39): fresh-half miss score 0.6505 vs price alone 0.6507.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 763 | +0.31 | 1345 | -7.33 | 2108 | -4.56 |
| Elo 10c+ above the real ask | 444 | +1.26 | 771 | -7.83 | 1215 | -4.50 |
| Elo 15c+ above the real ask | 231 | +8.70 | 374 | -2.95 | 605 | +1.50 |
| Price+Elo 3c+ above the real ask | 76 | -9.35 | 205 | +2.01 | 281 | -1.07 |
| Buy any side priced 3-15c | 2 | -100.00 | 3 | -100.00 | 5 | -100.00 |
| Buy any side priced 15-30c | 232 | +20.43 | 256 | -22.66 | 488 | -2.18 |
| Buy any side priced 30-45c | 1418 | -13.18 | 1422 | -8.79 | 2840 | -10.98 |
| Buy any side priced 45-55c | 1046 | -7.27 | 1020 | -6.96 | 2066 | -7.12 |
| Buy any side priced 55-70c | 1749 | -2.39 | 1768 | -2.96 | 3517 | -2.68 |
| Buy any side priced 70-85c | 419 | -7.12 | 395 | -0.74 | 814 | -4.02 |
| Buy any side priced 85-97c | 9 | +14.53 | 9 | +14.05 | 18 | +14.29 |
| Favourite, start 00-06 New York time | 699 | -4.83 | 727 | -3.49 | 1426 | -4.15 |
| Underdog, start 00-06 New York time | 699 | -6.17 | 727 | -8.17 | 1426 | -7.19 |
| Favourite, start 06-12 New York time | 651 | -3.84 | 707 | -0.16 | 1358 | -1.93 |
| Underdog, start 06-12 New York time | 651 | -7.68 | 707 | -13.81 | 1358 | -10.87 |
| Favourite, start 12-18 New York time | 735 | -3.20 | 731 | -3.13 | 1466 | -3.16 |
| Underdog, start 12-18 New York time | 735 | -9.87 | 731 | -8.69 | 1466 | -9.28 |
| Favourite, start 18-24 New York time | 355 | -9.84 | 344 | -1.52 | 699 | -5.75 |
| Underdog, start 18-24 New York time | 355 | +1.12 | 344 | -9.92 | 699 | -4.32 |
| Side whose rival played 2+ more games in the last 6 hours | 98 | -15.24 | 82 | -8.43 | 180 | -12.14 |
| Side that lost its last game, other won | 1163 | -9.07 | 1329 | -12.31 | 2492 | -10.80 |
| Side that won its last game, other lost | 1163 | -3.77 | 1329 | -0.16 | 2492 | -1.85 |
| Side with 4-5 of last 5 won, rival 0-1 | 103 | +0.98 | 214 | +14.57 | 317 | +10.14 |
| Follow a 5c+ move in the last 20 min | 1314 | -3.05 | 1443 | -2.89 | 2757 | -2.97 |
| Fade a 5c+ move in the last 20 min | 1350 | -8.35 | 1096 | -13.88 | 2446 | -10.83 |
| Busy book (top third pre-game volume), favourite | 483 | -3.62 | 1195 | -1.14 | 1678 | -1.85 |
| Quiet book (bottom third), favourite | 1146 | -6.63 | 472 | -1.83 | 1618 | -5.23 |
| Quiet book (bottom third), underdog | 1146 | -4.66 | 472 | -11.65 | 1618 | -6.70 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 20 | +29.15 | 50 | -7.06 | 70 | +3.27 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (3 of 5400) | 1 | +51.52 | 2 | +79.95 | 3 | +70.36 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (2 of 5400) | 1 | +51.52 | 1 | +100.00 | 2 | +75.88 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (4 of 5400) | 3 | +0.81 | 1 | -100.00 | 4 | -24.55 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (4 of 5400) | 3 | +0.81 | 1 | -100.00 | 4 | -24.55 |
| Elo 10c+ above the ask, bought 10 min before | 419 | -2.76 | 728 | -4.49 | 1147 | -3.86 |

**Backward look.** 416 upsets (winner priced under 35c) out of 1428 such underdogs (price said 422 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 1428 | 416 | 422 | -13.00 | -9.11 |
| won its last game | 565 | 180 | 168 | -3.21 | -2.34 |
| lost its last game | 788 | 214 | 232 | -19.33 | -14.08 |
| Elo likes it (Elo 10c+ above price) | 724 | 214 | 208 | -11.60 | -6.46 |
| price fell 5c+ in the last 20 min | 1009 | 289 | 297 | -16.11 | -10.17 |
| price rose 5c+ in the last 20 min | 11 | 4 | 3 | +40.10 | +3.60 |
| rival played 3+ games in the last 6 hours | 168 | 49 | 51 | -18.67 | -12.02 |
| its 1st game in 6 hours | 470 | 148 | 138 | -3.77 | -1.07 |
| night in New York (0-6) | 417 | 127 | 123 | -10.91 | -5.75 |
| rival on a 4-5 of 5 run | 347 | 108 | 101 | -6.42 | -2.64 |

- Best on the first half: **Buy any side priced 15-30c**, +20.43 per $100 there; fresh half 256 bets, -22.66 per $100, exam: **Losing** (luck range -38.22 to -7.1, 51 cuts tried on this family).
- Best on the first half: **Elo 15c+ above the real ask**, +8.70 per $100 there; fresh half 374 bets, -2.95 per $100, exam: **Behind, but could be bad luck** (luck range -14.74 to 8.84, 51 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 1215 bets, -4.50 per $100, exam: **Behind, but could be bad luck**.

## TT Elite table tennis (`KXTTELITEMATCH`)

6754 games with a usable price (10903 settled with a quote, skipped {'noquote': 129, 'shape': 11}), 28 Aug to 03 Oct, about 187 a day. Contracts traded before the start, typical game: 14 (busiest tenth 879); whole game incl. live: 966.

- Forecast check, first half (3104 games, both players 5+ earlier games): price miss score 0.6494, Elo (K=16) 0.6753 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (3324 games, both players 5+ earlier games): price miss score 0.6398, Elo (K=16) 0.6701 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 0.91, Elo 0.02): fresh-half miss score 0.6405 vs price alone 0.6398.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 1275 | -8.82 | 1184 | -16.20 | 2459 | -12.37 |
| Elo 10c+ above the real ask | 678 | -7.18 | 566 | -16.89 | 1244 | -11.59 |
| Elo 15c+ above the real ask | 299 | -7.66 | 221 | -14.45 | 520 | -10.54 |
| Price+Elo 3c+ above the real ask | 0 | +0.00 | 67 | +16.62 | 67 | +16.62 |
| Buy any side priced 3-15c | 26 | -9.31 | 26 | -74.15 | 52 | -41.73 |
| Buy any side priced 15-30c | 451 | -16.79 | 466 | -9.20 | 917 | -12.93 |
| Buy any side priced 30-45c | 1567 | -7.30 | 1542 | -14.21 | 3109 | -10.73 |
| Buy any side priced 45-55c | 1330 | -6.77 | 1346 | -7.60 | 2676 | -7.19 |
| Buy any side priced 55-70c | 2020 | -10.70 | 2053 | -6.31 | 4073 | -8.49 |
| Buy any side priced 70-85c | 973 | -6.75 | 795 | -4.87 | 1768 | -5.90 |
| Buy any side priced 85-97c | 103 | -6.07 | 144 | -5.62 | 247 | -5.81 |
| Favourite, start 00-06 New York time | 874 | -12.78 | 848 | -3.22 | 1722 | -8.07 |
| Underdog, start 00-06 New York time | 874 | -1.26 | 848 | -13.89 | 1722 | -7.48 |
| Favourite, start 06-12 New York time | 876 | -9.20 | 819 | -6.40 | 1695 | -7.85 |
| Underdog, start 06-12 New York time | 876 | -11.04 | 819 | -11.42 | 1695 | -11.22 |
| Favourite, start 12-18 New York time | 841 | -6.45 | 821 | -3.88 | 1662 | -5.18 |
| Underdog, start 12-18 New York time | 841 | -9.62 | 821 | -16.82 | 1662 | -13.18 |
| Favourite, start 18-24 New York time | 734 | -6.68 | 855 | -9.19 | 1589 | -8.03 |
| Underdog, start 18-24 New York time | 734 | -12.57 | 855 | -3.43 | 1589 | -7.65 |
| Side whose rival played 2+ more games in the last 6 hours | 426 | -4.02 | 423 | -16.72 | 849 | -10.33 |
| Side that lost its last game, other won | 1681 | -5.32 | 1719 | -11.33 | 3400 | -8.36 |
| Side that won its last game, other lost | 1681 | -11.47 | 1719 | -8.01 | 3400 | -9.72 |
| Side with 4-5 of last 5 won, rival 0-1 | 275 | -7.63 | 338 | -10.45 | 613 | -9.18 |
| Follow a 5c+ move in the last 20 min | 294 | -12.70 | 794 | -4.76 | 1088 | -6.90 |
| Fade a 5c+ move in the last 20 min | 294 | -6.08 | 1201 | -9.63 | 1495 | -8.93 |
| Busy book (top third pre-game volume), favourite | 710 | -7.89 | 1520 | -5.56 | 2230 | -6.30 |
| Quiet book (bottom third), favourite | 1960 | -9.35 | 805 | -8.93 | 2765 | -9.23 |
| Quiet book (bottom third), underdog | 1960 | -7.64 | 805 | -7.99 | 2765 | -7.75 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 94 | +7.73 | 47 | -42.63 | 141 | -9.02 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (101 of 6754) | 15 | +1.14 | 86 | -0.71 | 101 | -0.44 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (42 of 6754) | 0 | +0.00 | 42 | +8.66 | 42 | +8.66 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (104 of 6754) | 12 | -24.79 | 92 | -12.12 | 104 | -13.58 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (48 of 6754) | 0 | +0.00 | 48 | +8.27 | 48 | +8.27 |
| Elo 10c+ above the ask, bought 10 min before | 732 | -7.25 | 523 | -18.02 | 1255 | -11.72 |

**Backward look.** 621 upsets (winner priced under 35c) out of 2302 such underdogs (price said 622 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 2302 | 621 | 622 | -14.67 | -13.59 |
| won its last game | 849 | 236 | 239 | -8.38 | -13.94 |
| lost its last game | 1429 | 380 | 377 | -18.04 | -12.95 |
| Elo likes it (Elo 10c+ above price) | 1317 | 335 | 344 | -21.03 | -16.69 |
| price fell 5c+ in the last 20 min | 481 | 126 | 128 | -11.89 | -14.79 |
| price rose 5c+ in the last 20 min | 76 | 20 | 22 | -10.86 | -16.02 |
| rival played 3+ games in the last 6 hours | 1433 | 371 | 386 | -18.56 | -16.12 |
| its 1st game in 6 hours | 323 | 88 | 87 | -18.68 | -13.97 |
| night in New York (0-6) | 584 | 185 | 162 | -8.11 | -2.36 |
| rival on a 4-5 of 5 run | 782 | 196 | 204 | -13.69 | -17.04 |

- Best on the first half: **Player new to Kalshi (under 5 games) vs veteran (30+): veteran**, +7.73 per $100 there; fresh half 47 bets, -42.63 per $100, exam: **Losing** (luck range -61.59 to -23.66, 51 cuts tried on this family).
- Best on the first half: **Upset look: underdog, night in New York (0-6)**, +2.58 per $100 there; fresh half 270 bets, -8.11 per $100, exam: **Behind, but could be bad luck** (luck range -22.84 to 6.62, 51 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 1244 bets, -11.59 per $100, exam: **Losing**.

## TT Star table tennis (`KXTTSTARMATCH`)

485 games with a usable price (1238 settled with a quote, skipped {'shape': 14, 'noquote': 57, 'nocandles': 9}), 31 Aug to 15 Oct, about 11 a day. Contracts traded before the start, typical game: 0 (busiest tenth 1035); whole game incl. live: 1284.

- Forecast check, first half (96 games, both players 5+ earlier games): price miss score 0.6075, Elo (K=16) 0.6866 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (165 games, both players 5+ earlier games): price miss score 0.5264, Elo (K=16) 0.6563 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 0.89, Elo -1.11): fresh-half miss score 0.5471 vs price alone 0.5264.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 73 | +2.32 | 131 | -27.45 | 204 | -16.80 |
| Elo 10c+ above the real ask | 60 | +0.78 | 107 | -26.88 | 167 | -16.95 |
| Elo 15c+ above the real ask | 43 | +6.55 | 78 | -29.71 | 121 | -16.82 |
| Price+Elo 3c+ above the real ask | 29 | +9.52 | 63 | -24.22 | 92 | -13.65 |
| Buy any side priced 3-15c | 32 | -58.08 | 38 | -75.16 | 70 | -67.36 |
| Buy any side priced 15-30c | 81 | -10.72 | 92 | +7.76 | 173 | -0.90 |
| Buy any side priced 30-45c | 76 | -0.61 | 65 | -24.85 | 141 | -11.81 |
| Buy any side priced 45-55c | 53 | -6.51 | 48 | +2.11 | 101 | -2.41 |
| Buy any side priced 55-70c | 90 | -12.17 | 80 | -6.90 | 170 | -9.69 |
| Buy any side priced 70-85c | 76 | -1.29 | 82 | +0.33 | 158 | -0.45 |
| Buy any side priced 85-97c | 55 | -4.00 | 64 | -5.31 | 119 | -4.71 |
| Favourite, start 00-06 New York time | 68 | -7.10 | 87 | -9.64 | 155 | -8.53 |
| Underdog, start 00-06 New York time | 68 | -19.65 | 87 | +1.02 | 155 | -8.04 |
| Favourite, start 06-12 New York time | 98 | -7.50 | 90 | +2.16 | 188 | -2.88 |
| Underdog, start 06-12 New York time | 98 | -11.08 | 90 | -36.05 | 188 | -23.06 |
| Favourite, start 12-18 New York time | 69 | -2.73 | 62 | -6.23 | 131 | -4.38 |
| Underdog, start 12-18 New York time | 69 | -13.95 | 62 | -13.79 | 131 | -13.87 |
| Favourite, start 18-24 New York time | 0 | +0.00 | 0 | +0.00 | 0 | +0.00 |
| Underdog, start 18-24 New York time | 0 | +0.00 | 0 | +0.00 | 0 | +0.00 |
| Side whose rival played 2+ more games in the last 6 hours | 8 | +35.80 | 4 | +37.81 | 12 | +36.48 |
| Side that lost its last game, other won | 119 | -23.46 | 109 | -5.90 | 228 | -15.07 |
| Side that won its last game, other lost | 119 | +13.16 | 109 | -17.96 | 228 | -1.68 |
| Side with 4-5 of last 5 won, rival 0-1 | 12 | -22.76 | 20 | -9.94 | 32 | -14.80 |
| Follow a 5c+ move in the last 20 min | 70 | -17.01 | 143 | -7.93 | 213 | -10.91 |
| Fade a 5c+ move in the last 20 min | 70 | +7.10 | 136 | -28.01 | 206 | -16.08 |
| Busy book (top third pre-game volume), favourite | 39 | +6.88 | 122 | -5.86 | 161 | -2.75 |
| Quiet book (bottom third), favourite | 157 | -8.71 | 82 | -7.07 | 239 | -8.15 |
| Quiet book (bottom third), underdog | 157 | -12.91 | 82 | +1.68 | 239 | -7.91 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 0 | +0.00 | 7 | -22.40 | 7 | -22.40 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (71 of 485) | 20 | +23.67 | 51 | +42.56 | 71 | +37.25 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (26 of 485) | 0 | +0.00 | 26 | +43.60 | 26 | +43.60 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (98 of 485) | 31 | -22.34 | 67 | -27.54 | 98 | -25.90 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (55 of 485) | 1 | -100.00 | 54 | -15.54 | 55 | -17.10 |
| Elo 10c+ above the ask, bought 10 min before | 56 | +4.23 | 103 | -32.14 | 159 | -19.32 |

**Backward look.** 56 upsets (winner priced under 35c) out of 303 such underdogs (price said 59 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 303 | 56 | 59 | -25.03 | -22.79 |
| won its last game | 111 | 18 | 22 | -56.96 | -38.89 |
| lost its last game | 174 | 33 | 33 | -10.81 | -14.59 |
| Elo likes it (Elo 10c+ above price) | 156 | 30 | 30 | -30.75 | -19.16 |
| price fell 5c+ in the last 20 min | 143 | 24 | 26 | -45.54 | -29.16 |
| price rose 5c+ in the last 20 min | 9 | 3 | 2 | +3.31 | +9.36 |
| rival played 3+ games in the last 6 hours | 24 | 4 | 4 | -100.00 | -29.91 |
| its 1st game in 6 hours | 93 | 20 | 19 | -32.25 | -17.54 |
| night in New York (0-6) | 102 | 22 | 20 | +1.97 | -13.44 |
| rival on a 4-5 of 5 run | 92 | 18 | 16 | -17.52 | -13.46 |

- Best on the first half: **Side that won its last game, other lost**, +13.16 per $100 there; fresh half 109 bets, -17.96 per $100, exam: **Losing** (luck range -31.0 to -4.92, 51 cuts tried on this family).
- Best on the first half: **Fade a 5c+ move in the last 20 min**, +7.10 per $100 there; fresh half 136 bets, -28.01 per $100, exam: **Losing** (luck range -48.73 to -7.29, 51 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 167 bets, -16.95 per $100, exam: **Behind, but could be bad luck**.

## eBasketball (`KXEBASKETBALLGAME`)

4196 games with a usable price (4594 settled with a quote, skipped {'shape': 24, 'noquote': 2}), 08 Oct to 27 Nov, about 84 a day. Contracts traded before the start, typical game: 211 (busiest tenth 1385); whole game incl. live: 4240.

- Forecast check, first half (2047 games, both players 5+ earlier games): price miss score 0.6258, Elo (K=16) 0.6420 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (2083 games, both players 5+ earlier games): price miss score 0.6504, Elo (K=16) 0.6606 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 0.82, Elo 0.21): fresh-half miss score 0.6510 vs price alone 0.6504.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 610 | -5.13 | 411 | -0.67 | 1021 | -3.36 |
| Elo 10c+ above the real ask | 310 | -3.93 | 87 | -0.94 | 397 | -3.28 |
| Elo 15c+ above the real ask | 147 | +7.30 | 19 | -2.74 | 166 | +6.15 |
| Price+Elo 3c+ above the real ask | 22 | +73.76 | 6 | -33.60 | 28 | +50.82 |
| Buy any side priced 3-15c | 137 | -22.52 | 64 | -49.10 | 201 | -30.97 |
| Buy any side priced 15-30c | 344 | -1.05 | 175 | -7.17 | 519 | -3.12 |
| Buy any side priced 30-45c | 892 | -5.45 | 917 | -5.33 | 1809 | -5.39 |
| Buy any side priced 45-55c | 727 | -10.24 | 942 | +1.66 | 1669 | -3.53 |
| Buy any side priced 55-70c | 1117 | -7.01 | 1200 | -8.50 | 2317 | -7.78 |
| Buy any side priced 70-85c | 481 | -5.42 | 233 | -1.54 | 714 | -4.15 |
| Buy any side priced 85-97c | 200 | -2.52 | 95 | -0.47 | 295 | -1.86 |
| Favourite, start 00-06 New York time | 504 | -0.38 | 484 | -4.47 | 988 | -2.39 |
| Underdog, start 00-06 New York time | 504 | -16.94 | 484 | -6.00 | 988 | -11.59 |
| Favourite, start 06-12 New York time | 514 | -2.46 | 547 | -8.28 | 1061 | -5.47 |
| Underdog, start 06-12 New York time | 514 | -11.04 | 547 | -3.43 | 1061 | -7.13 |
| Favourite, start 12-18 New York time | 521 | -9.23 | 524 | -5.30 | 1045 | -7.25 |
| Underdog, start 12-18 New York time | 521 | -1.07 | 524 | -5.95 | 1045 | -3.51 |
| Favourite, start 18-24 New York time | 540 | -12.28 | 517 | -6.22 | 1057 | -9.31 |
| Underdog, start 18-24 New York time | 540 | +1.35 | 517 | -5.29 | 1057 | -1.90 |
| Side whose rival played 2+ more games in the last 6 hours | 64 | -10.65 | 4 | -100.00 | 68 | -16.07 |
| Side that lost its last game, other won | 1244 | -8.38 | 1241 | -2.63 | 2485 | -5.51 |
| Side that won its last game, other lost | 1244 | -5.99 | 1241 | -9.42 | 2485 | -7.71 |
| Side with 4-5 of last 5 won, rival 0-1 | 466 | -6.55 | 438 | -9.41 | 904 | -7.95 |
| Follow a 5c+ move in the last 20 min | 210 | -3.57 | 176 | -16.25 | 386 | -9.36 |
| Fade a 5c+ move in the last 20 min | 142 | -15.18 | 89 | -12.50 | 231 | -14.15 |
| Busy book (top third pre-game volume), favourite | 366 | -6.21 | 1015 | -2.62 | 1381 | -3.57 |
| Quiet book (bottom third), favourite | 1046 | -5.72 | 343 | -10.54 | 1389 | -6.92 |
| Quiet book (bottom third), underdog | 1046 | -12.70 | 343 | -0.52 | 1389 | -9.71 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 14 | +20.88 | 4 | -64.30 | 18 | +2.31 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (724 of 4196) | 250 | -13.67 | 474 | +1.78 | 724 | -3.53 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (552 of 4196) | 200 | -15.04 | 352 | +0.73 | 552 | -4.96 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (606 of 4196) | 122 | -8.60 | 484 | -0.94 | 606 | -2.48 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (447 of 4196) | 120 | -9.25 | 327 | -15.89 | 447 | -14.11 |
| Elo 10c+ above the ask, bought 10 min before | 301 | -0.19 | 96 | +3.34 | 397 | +0.65 |

**Backward look.** 356 upsets (winner priced under 35c) out of 1370 such underdogs (price said 339 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 1370 | 356 | 339 | -11.30 | -7.97 |
| won its last game | 383 | 111 | 102 | -22.83 | -3.62 |
| lost its last game | 983 | 244 | 236 | -7.46 | -9.57 |
| Elo likes it (Elo 10c+ above price) | 345 | 90 | 78 | +5.78 | -1.52 |
| price fell 5c+ in the last 20 min | 84 | 19 | 19 | -23.60 | -28.87 |
| price rose 5c+ in the last 20 min | 31 | 6 | 9 | -67.78 | -40.59 |
| rival played 3+ games in the last 6 hours | 917 | 247 | 225 | -6.53 | -4.64 |
| its 1st game in 6 hours | 146 | 32 | 36 | -39.90 | -30.37 |
| night in New York (0-6) | 314 | 79 | 77 | -11.25 | -14.52 |
| rival on a 4-5 of 5 run | 735 | 170 | 162 | -8.78 | -10.04 |

- Best on the first half: **Elo 15c+ above the real ask**, +7.30 per $100 there; fresh half 19 bets, -2.74 per $100, exam: **Behind, but could be bad luck** (luck range -76.8 to 71.32, 51 cuts tried on this family).
- Best on the first half: **Upset look: underdog, won its last game**, +6.36 per $100 there; fresh half 131 bets, -22.83 per $100, exam: **Losing** (luck range -43.72 to -1.94, 51 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 397 bets, -3.28 per $100, exam: **Behind, but could be bad luck**.

## eSoccer (`KXESOCCERGAME`)

18894 games with a usable price (23222 settled with a quote, skipped {'shape': 370, 'noquote': 26}), 08 Oct to 27 Nov, about 378 a day. Contracts traded before the start, typical game: 63 (busiest tenth 520); whole game incl. live: 1134.

- Forecast check, first half (9289 games, both players 5+ earlier games): price miss score 0.6162, Elo (K=16) 0.6293 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (9418 games, both players 5+ earlier games): price miss score 0.6401, Elo (K=16) 0.6467 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 0.96, Elo 0.01): fresh-half miss score 0.6399 vs price alone 0.6401.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 1742 | -4.29 | 1029 | -11.49 | 2771 | -6.96 |
| Elo 10c+ above the real ask | 635 | -3.61 | 226 | +1.63 | 861 | -2.24 |
| Elo 15c+ above the real ask | 230 | -5.99 | 110 | +11.92 | 340 | -0.21 |
| Price+Elo 3c+ above the real ask | 5 | -6.70 | 0 | +0.00 | 5 | -6.70 |
| Buy any side priced 3-15c | 747 | -22.46 | 420 | -17.80 | 1167 | -20.79 |
| Buy any side priced 15-30c | 2988 | -10.55 | 2493 | -0.17 | 5481 | -5.83 |
| Buy any side priced 30-45c | 5536 | -7.67 | 6504 | -5.38 | 12040 | -6.43 |
| Buy any side priced 45-55c | 3833 | -10.07 | 4764 | -7.67 | 8597 | -8.74 |
| Buy any side priced 55-70c | 3491 | -5.85 | 2721 | -8.67 | 6212 | -7.09 |
| Buy any side priced 70-85c | 1232 | -2.68 | 567 | -1.54 | 1799 | -2.32 |
| Buy any side priced 85-97c | 449 | -4.16 | 135 | -3.23 | 584 | -3.94 |
| Favourite, start 00-06 New York time | 1308 | -2.54 | 1161 | -6.95 | 2469 | -4.62 |
| Underdog, start 00-06 New York time | 2152 | -11.21 | 2293 | -7.58 | 4445 | -9.34 |
| Favourite, start 06-12 New York time | 1559 | -6.18 | 1358 | -6.81 | 2917 | -6.47 |
| Underdog, start 06-12 New York time | 2477 | -8.32 | 2599 | -2.91 | 5076 | -5.55 |
| Favourite, start 12-18 New York time | 1553 | -5.51 | 1139 | -6.75 | 2692 | -6.03 |
| Underdog, start 12-18 New York time | 2483 | -7.89 | 2233 | -7.37 | 4716 | -7.64 |
| Favourite, start 18-24 New York time | 1476 | -6.84 | 1110 | -5.59 | 2586 | -6.30 |
| Underdog, start 18-24 New York time | 2335 | -12.04 | 2322 | -8.86 | 4657 | -10.45 |
| Side whose rival played 2+ more games in the last 6 hours | 611 | -21.54 | 162 | -10.31 | 773 | -19.20 |
| Side that lost its last game, other won | 4978 | -12.66 | 5158 | -7.41 | 10136 | -9.99 |
| Side that won its last game, other lost | 4978 | -3.57 | 5158 | -4.30 | 10136 | -3.94 |
| Side with 4-5 of last 5 won, rival 0-1 | 1637 | -2.41 | 1358 | -6.13 | 2995 | -4.11 |
| Follow a 5c+ move in the last 20 min | 1476 | -5.54 | 3344 | -9.38 | 4820 | -8.22 |
| Fade a 5c+ move in the last 20 min | 2278 | -8.70 | 1046 | -1.04 | 3324 | -6.29 |
| Busy book (top third pre-game volume), favourite | 801 | -7.94 | 1989 | -6.75 | 2790 | -7.09 |
| Quiet book (bottom third), favourite | 3349 | -5.26 | 950 | -8.54 | 4299 | -5.98 |
| Quiet book (bottom third), underdog | 4860 | -10.53 | 1440 | -1.66 | 6300 | -8.50 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 61 | -20.67 | 27 | -6.24 | 88 | -16.28 |
| eSoccer: buy Tie at 3-15c | 1505 | -28.07 | 1531 | -4.20 | 3036 | -16.04 |
| eSoccer: buy Tie at 15-25c | 7819 | -20.17 | 7819 | -6.22 | 15638 | -13.20 |
| eSoccer: buy Tie at 25-40c | 20 | -8.44 | 85 | -31.36 | 105 | -26.99 |
| eSoccer: bet against the Tie (No at 60-97c) | 9143 | -3.14 | 9411 | -3.51 | 18554 | -3.33 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (1290 of 18894) | 209 | -1.74 | 1081 | -3.84 | 1290 | -3.51 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (759 of 18894) | 154 | -5.04 | 605 | -10.68 | 759 | -9.54 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (1063 of 18894) | 165 | -6.23 | 898 | -1.84 | 1063 | -2.52 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (550 of 18894) | 150 | +11.94 | 400 | +0.76 | 550 | +3.81 |
| Waiting bid on the Tie (30 min before), filled on sell offer reached our bid (1124 of 18894) | 274 | +20.87 | 850 | +17.30 | 1124 | +18.17 |
| Waiting bid on the Tie (30 min before), filled on real trade at or below our bid (800 of 18894) | 321 | +14.30 | 479 | +11.68 | 800 | +12.73 |
| Elo 10c+ above the ask, bought 10 min before | 600 | -1.45 | 208 | -3.27 | 808 | -1.92 |

**Backward look.** 3193 upsets (winner priced under 35c) out of 12096 such underdogs (price said 3027 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 12096 | 3193 | 3027 | -3.14 | -6.82 |
| won its last game | 3818 | 1086 | 1002 | -3.03 | -3.34 |
| lost its last game | 8261 | 2103 | 2020 | -3.24 | -8.39 |
| Elo likes it (Elo 10c+ above price) | 1592 | 369 | 353 | -12.90 | -12.18 |
| price fell 5c+ in the last 20 min | 2408 | 568 | 533 | -0.99 | -6.61 |
| price rose 5c+ in the last 20 min | 951 | 299 | 290 | -4.42 | -6.22 |
| rival played 3+ games in the last 6 hours | 10326 | 2752 | 2575 | -1.71 | -5.39 |
| its 1st game in 6 hours | 723 | 180 | 182 | -9.58 | -13.66 |
| night in New York (0-6) | 2792 | 744 | 701 | +0.32 | -5.92 |
| rival on a 4-5 of 5 run | 3524 | 769 | 739 | -5.37 | -9.47 |

- Best on the first half: **Waiting bid on the Tie (30 min before), filled on sell offer reached our bid**, +20.87 per $100 there; fresh half 850 bets, +17.30 per $100, exam: **Promising, needs more bets** (luck range 3.26 to 31.35, 57 cuts tried on this family).
- Best on the first half: **Waiting bid on the Tie (30 min before), filled on real trade at or below our bid**, +14.30 per $100 there; fresh half 479 bets, +11.68 per $100, exam: **Ahead, but could be luck** (luck range -6.89 to 30.25, 57 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 861 bets, -2.24 per $100, exam: **Behind, but could be bad luck**.

## eFootball (`KXEFOOTBALLGAME`)

177 games with a usable price (1160 settled with a quote, skipped {'noquote': 17, 'shape': 2}), 21 Oct to 25 Nov, about 5 a day. Contracts traded before the start, typical game: 19 (busiest tenth 339); whole game incl. live: 1082.

- Forecast check, first half (86 games, both players 5+ earlier games): price miss score 0.5438, Elo (K=16) 0.6743 (lower is better; a coin flip is 0.6931).
- Forecast check, fresh half (89 games, both players 5+ earlier games): price miss score 0.5757, Elo (K=16) 0.6729 (lower is better; a coin flip is 0.6931).
- Price + Elo together (weights fit on the first half: price 1.34, Elo -0.07): fresh-half miss score 0.5820 vs price alone 0.5757.

| Rule | Bets 1st half | $ per $100 | Bets fresh half | $ per $100 | All bets | $ per $100 |
|---|---|---|---|---|---|---|
| Elo 5c+ above the real ask | 48 | -29.70 | 53 | -11.01 | 101 | -19.90 |
| Elo 10c+ above the real ask | 39 | -41.01 | 41 | -0.50 | 80 | -20.24 |
| Elo 15c+ above the real ask | 29 | -58.13 | 26 | -13.85 | 55 | -37.16 |
| Price+Elo 3c+ above the real ask | 8 | -38.74 | 17 | +19.07 | 25 | +0.68 |
| Buy any side priced 3-15c | 10 | -100.00 | 7 | -100.00 | 17 | -100.00 |
| Buy any side priced 15-30c | 23 | -41.57 | 22 | +32.42 | 45 | -5.37 |
| Buy any side priced 30-45c | 30 | +1.91 | 31 | -31.67 | 61 | -15.11 |
| Buy any side priced 45-55c | 25 | -26.64 | 27 | +4.56 | 52 | -10.41 |
| Buy any side priced 55-70c | 43 | -1.32 | 44 | -8.12 | 87 | -4.76 |
| Buy any side priced 70-85c | 21 | -16.96 | 18 | -21.13 | 39 | -18.90 |
| Buy any side priced 85-97c | 16 | +11.20 | 12 | +1.05 | 28 | +6.87 |
| Favourite, start 00-06 New York time | 16 | -19.00 | 23 | +1.31 | 39 | -6.93 |
| Underdog, start 00-06 New York time | 16 | -7.22 | 23 | -12.74 | 39 | -10.47 |
| Favourite, start 06-12 New York time | 26 | -12.62 | 10 | +14.45 | 36 | -5.12 |
| Underdog, start 06-12 New York time | 26 | -10.57 | 10 | -78.84 | 36 | -29.58 |
| Favourite, start 12-18 New York time | 19 | +15.76 | 23 | -32.82 | 42 | -10.89 |
| Underdog, start 12-18 New York time | 19 | -62.22 | 23 | +33.29 | 42 | -10.07 |
| Favourite, start 18-24 New York time | 26 | +8.41 | 31 | -7.93 | 57 | -0.47 |
| Underdog, start 18-24 New York time | 26 | -35.29 | 31 | -11.45 | 57 | -22.28 |
| Side whose rival played 2+ more games in the last 6 hours | 4 | -100.00 | 5 | -3.28 | 9 | -46.55 |
| Side that lost its last game, other won | 48 | -17.87 | 55 | +0.55 | 103 | -8.04 |
| Side that won its last game, other lost | 48 | -3.08 | 55 | -18.74 | 103 | -11.48 |
| Side with 4-5 of last 5 won, rival 0-1 | 16 | +8.80 | 16 | +10.77 | 32 | +9.79 |
| Follow a 5c+ move in the last 20 min | 71 | -11.33 | 61 | -17.72 | 132 | -14.29 |
| Fade a 5c+ move in the last 20 min | 57 | -26.02 | 49 | -28.46 | 106 | -27.15 |
| Busy book (top third pre-game volume), favourite | 41 | -4.69 | 18 | -4.42 | 59 | -4.61 |
| Quiet book (bottom third), favourite | 22 | +22.63 | 37 | -13.42 | 59 | +0.05 |
| Quiet book (bottom third), underdog | 22 | -51.73 | 37 | +2.31 | 59 | -17.74 |
| Player new to Kalshi (under 5 games) vs veteran (30+): veteran | 0 | +0.00 | 0 | +0.00 | 0 | +0.00 |
| Waiting bid on the favourite (30 min before), filled on sell offer reached our bid (2 of 177) | 0 | +0.00 | 2 | -27.31 | 2 | -27.31 |
| Waiting bid on the favourite (30 min before), filled on real trade at or below our bid (1 of 177) | 0 | +0.00 | 1 | -100.00 | 1 | -100.00 |
| Waiting bid on the underdog (30 min before), filled on sell offer reached our bid (1 of 177) | 0 | +0.00 | 1 | -100.00 | 1 | -100.00 |
| Waiting bid on the underdog (30 min before), filled on real trade at or below our bid (1 of 177) | 0 | +0.00 | 1 | -100.00 | 1 | -100.00 |
| Elo 10c+ above the ask, bought 10 min before | 12 | +49.11 | 14 | -47.82 | 26 | -2.97 |

**Backward look.** 16 upsets (winner priced under 35c) out of 83 such underdogs (price said 17 wins). What the underdogs had beforehand, and what buying them earned:

| Underdog beforehand | Underdogs | Won | Price said | Fresh-half $ per $100 | All $ per $100 |
|---|---|---|---|---|---|
| all | 83 | 16 | 17 | -21.65 | -32.05 |
| won its last game | 42 | 7 | 8 | -45.43 | -43.32 |
| lost its last game | 41 | 9 | 9 | +9.68 | -20.46 |
| Elo likes it (Elo 10c+ above price) | 66 | 13 | 12 | -20.09 | -28.04 |
| price fell 5c+ in the last 20 min | 72 | 13 | 14 | -33.49 | -36.80 |
| price rose 5c+ in the last 20 min | 3 | 1 | 1 | -100.00 | -15.88 |
| rival played 3+ games in the last 6 hours | 71 | 12 | 14 | -25.57 | -37.75 |
| its 1st game in 6 hours | 2 | 1 | 1 | -100.00 | +21.48 |
| night in New York (0-6) | 18 | 4 | 4 | +8.26 | -10.75 |
| rival on a 4-5 of 5 run | 22 | 5 | 5 | +53.81 | -18.51 |

- Best on the first half: **Follow a 5c+ move in the last 20 min**, -11.33 per $100 there; fresh half 61 bets, -17.72 per $100, exam: **Losing** (luck range -31.99 to -3.45, 51 cuts tried on this family).
- Best on the first half: **Fade a 5c+ move in the last 20 min**, -26.02 per $100 there; fresh half 49 bets, -28.46 per $100, exam: **Behind, but could be bad luck** (luck range -61.41 to 4.48, 51 cuts tried on this family).
- The planned test, Elo 10c+ above the ask: 80 bets, -20.24 per $100, exam: **Behind, but could be bad luck**.

## The one lean: a waiting bid on the eSoccer Tie

Bid 1c above the best bid on 'Tie' some minutes before the scheduled start, pulled at the start, filled when the lowest sell offer later reached our bid. No fee (these series charge only the buyer who takes an offer). Nearby versions, all counted as tries:

| Version | Fills | 1st half $ per $100 | Fresh half $ per $100 |
|---|---|---|---|
| 15 min before, bid at the best bid, filled when sell offer reached our bid | 742 | +10.63 | +26.63 |
| 15 min before, bid +1c, filled when sell offer reached our bid | 1835 | -9.38 | +8.38 |
| 15 min before, bid at the best bid, filled when sell offer went below our bid | 180 | -42.97 | -0.89 |
| 15 min before, bid +1c, filled when sell offer went below our bid | 439 | -5.27 | +16.20 |
| 15 min before, bid +1c, filled when a real trade at or below our bid | 1569 | +4.13 | +8.16 |
| 30 min before, bid at the best bid, filled when sell offer reached our bid | 477 | +14.88 | +38.01 |
| 30 min before, bid +1c, filled when sell offer reached our bid | 1124 | +20.87 | +17.30 |
| 30 min before, bid at the best bid, filled when sell offer went below our bid | 151 | -49.47 | +30.26 |
| 30 min before, bid +1c, filled when sell offer went below our bid | 401 | +15.38 | +27.31 |
| 30 min before, bid +1c, filled when a real trade at or below our bid | 800 | +14.30 | +11.68 |
| 45 min before, bid at the best bid, filled when sell offer reached our bid | 327 | -29.77 | +29.27 |
| 45 min before, bid +1c, filled when sell offer reached our bid | 747 | -1.37 | +33.61 |
| 45 min before, bid at the best bid, filled when sell offer went below our bid | 96 | +2.45 | +26.97 |
| 45 min before, bid +1c, filled when sell offer went below our bid | 279 | -53.03 | +26.25 |
| 45 min before, bid +1c, filled when a real trade at or below our bid | 530 | +8.23 | +18.75 |

Main version (30 min before, +1c, filled only when a real trade happened at or below our bid): 800 fills, 139 won (the price said about 122), +12.73 per $100, exam on all games: **Ahead, but could be luck** (luck range -1.81 to 27.27, worst case -17.91). Fills on 42 days, about 19 a day; worst day $-224.75, best day $269.68 at $10 a bid. Contracts others traded at or below our price in those minutes: 54 a fill on average (a $10 bid at ~16c is ~60 contracts), so $10 is about where it stops growing.

## Biggest wins, read one by one

*eSoccer: Waiting bid on the Tie (30 min before), filled on sell offer reached our bid*
- 30 Oct 04:26 UTC KXESOCCERGAME-26OCT300056DRAKDZEN Tie: paid $10.00 for 125 at 8c, got $125.00
- 20 Nov 01:39 UTC KXESOCCERGAME-26NOV192109STRUMAVI Tie: paid $9.99 for 111 at 9c, got $111.00
- 30 Oct 07:04 UTC KXESOCCERGAME-26OCT300334VINIREND Tie: paid $10.00 for 100 at 10c, got $100.00
- 12 Nov 23:57 UTC KXESOCCERGAME-26NOV121927BONYANTO Tie: paid $9.90 for 90 at 11c, got $90.00
- 17 Nov 23:57 UTC KXESOCCERGAME-26NOV171927KEVIBRAD Tie: paid $9.90 for 90 at 11c, got $90.00

*eSoccer: Waiting bid on the Tie (30 min before), filled on real trade at or below our bid*
- 20 Nov 01:39 UTC KXESOCCERGAME-26NOV192109STRUMAVI Tie: paid $9.99 for 111 at 9c, got $111.00
- 18 Oct 07:54 UTC KXESOCCERGAME-26OCT180424BONYFEDE Tie: paid $9.90 for 90 at 11c, got $90.00
- 19 Oct 02:53 UTC KXESOCCERGAME-26OCT182323KEVIBRAD Tie: paid $9.90 for 90 at 11c, got $90.00
- 12 Nov 23:57 UTC KXESOCCERGAME-26NOV121927BONYANTO Tie: paid $9.90 for 90 at 11c, got $90.00
- 18 Oct 23:39 UTC KXESOCCERGAME-26OCT182009KYLIBRAD Tie: paid $9.96 for 83 at 12c, got $83.00

*eSoccer: waiting bid on the Tie*
- 20 Nov 01:39 UTC KXESOCCERGAME-26NOV192109STRUMAVI Tie: paid $9.99 for 111 at 9c, got $111.00
- 18 Oct 07:54 UTC KXESOCCERGAME-26OCT180424BONYFEDE Tie: paid $9.90 for 90 at 11c, got $90.00
- 19 Oct 02:53 UTC KXESOCCERGAME-26OCT182323KEVIBRAD Tie: paid $9.90 for 90 at 11c, got $90.00
- 12 Nov 23:57 UTC KXESOCCERGAME-26NOV121927BONYANTO Tie: paid $9.90 for 90 at 11c, got $90.00
- 18 Oct 23:39 UTC KXESOCCERGAME-26OCT182009KYLIBRAD Tie: paid $9.96 for 83 at 12c, got $83.00

