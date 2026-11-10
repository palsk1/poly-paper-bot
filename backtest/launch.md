# Brand-new markets: are they mispriced in their first hours?

Made by `launch.py run` (probe `btlaunchrun`) on 2026-11-10T02:53Z. Paper research only.

How it works: markets are sampled by the day they **started** (no volume floor, so small markets that died quiet are in, unlike bt_cache). For each market we look at the price 10 minutes, 1 hour and 6 hours after launch, and buy one side, held to the end. Polymarket: history price + 2c + fee, and only if someone had already traded the market by then (so the price was a real book, not the empty 50c placeholder). Kalshi: the real ask from the minute candles + fee. Each bet is compared with **seasoned twins**: bets on the same kind of market, same side, same price band, same time left, but at least one day old. Events count once. Discovery on one half (by date), confirm on the other, both ways, corrected for the number of tries.

## Poly: what launch looks like

| Kind | Markets | Traded in 1st hour | Still at 50c after 10 min | Avg move launch -> 24h | Error at launch | Error at 24h |
|---|---|---|---|---|---|---|
| crypto up/down | 3036 | 3 in 100 | 96 in 100 | 5.0c | 0.250 | 0.239 |
| crypto price | 3036 | 44 in 100 | 1 in 100 | 8.4c | 0.100 | 0.073 |
| weather | 2976 | 46 in 100 | 0 in 100 | 7.5c | 0.069 | 0.057 |
| sports | 2966 | 5 in 100 | 2 in 100 | 6.2c | 0.233 | 0.199 |
| other (one-off questions) | 2892 | 14 in 100 | 1 in 100 | 14.4c | 0.176 | 0.106 |
| esports | 2775 | 20 in 100 | 2 in 100 | 13.2c | 0.210 | 0.147 |
| apps/tech | 2339 | 9 in 100 | 0 in 100 | 13.4c | 0.129 | 0.081 |
| stocks | 2255 | 6 in 100 | 0 in 100 | 16.4c | 0.161 | 0.081 |
| mentions | 2221 | 16 in 100 | 0 in 100 | 8.1c | 0.202 | 0.219 |
| entertainment | 1826 | 15 in 100 | 0 in 100 | 11.7c | 0.094 | 0.085 |
| post counts | 1822 | 51 in 100 | 0 in 100 | 5.7c | 0.055 | 0.053 |
| elections | 1549 | 16 in 100 | 0 in 100 | 11.5c | 0.089 | 0.022 |
| geopolitics | 572 | 20 in 100 | 0 in 100 | 6.0c | 0.145 | 0.123 |
| economics | 548 | 3 in 100 | 0 in 100 | 30.6c | 0.133 | 0.001 |
| people/legal | 162 | 33 in 100 | 1 in 100 | 18.6c | 0.151 | 0.033 |

Error = average squared miss of the price vs the result (0 = perfect, 0.25 = coin flip). It always shrinks with time because news arrives; a launch edge needs launch prices that are wrong in a direction you can bet on, which the tables below test.

## Kalshi: what launch looks like

| Kind | Markets | Real two-sided quote after 10 min | Avg gap bid/ask after 10 min | Avg move launch -> 24h | Error at launch | Error at 24h |
|---|---|---|---|---|---|---|
| sports | 16845 | 81 in 100 | 58.9c | 11.7c | 0.228 | 0.192 |
| other (one-off questions) | 2279 | 77 in 100 | 58.7c | 18.1c | 0.218 | 0.155 |
| weather | 1189 | 94 in 100 | 19.1c | 16.8c | 0.178 | 0.112 |
| crypto price | 407 | 14 in 100 | 19.1c | 8.3c | 0.181 | 0.194 |
| mentions | 190 | 96 in 100 | 58.8c | 18.7c | 0.225 | 0.165 |
| stocks | 172 | 55 in 100 | 28.0c | 10.1c | 0.181 | 0.136 |
| entertainment | 116 | 59 in 100 | 67.1c | 21.4c | 0.201 | 0.156 |
| apps/tech | 93 | 87 in 100 | 57.0c | 16.0c | 0.168 | 0.117 |
| elections | 77 | 97 in 100 | 85.1c | 23.9c | 0.251 | 0.152 |
| economics | 43 | 74 in 100 | 66.5c | 22.9c | 0.191 | 0.100 |
| people/legal | 16 | 100 in 100 | 69.8c | 14.9c | 0.189 | 0.108 |
| post counts | 13 | 92 in 100 | 30.2c | 3.0c | 0.178 | 0.191 |
| esports | 6 | 100 in 100 | 93.7c | 0.2c | 0.257 | 0.257 |
| geopolitics | 3 | 67 in 100 | 98.0c | 23.8c | 0.250 | 0.069 |

Error = average squared miss of the price vs the result (0 = perfect, 0.25 = coin flip). It always shrinks with time because news arrives; a launch edge needs launch prices that are wrong in a direction you can bet on, which the tables below test.

## Poly: which launch bets beat their seasoned twins

572 cells tried (kind x launch age x side x price band, plus 'still at 50c'). Candidates: 30 on the first half, 17 on the second. **Survivors: 7.**

Top 25 by the weaker half (per $100 staked):

| Bet | Events A / B | vs twins A / B | +2c A / B | +5c A / B | Survived |
|---|---|---|---|---|---|
| poly post counts, 1 hour after launch, buy No at 75-90c | 56 / 69 | +$18.91 / +$14.13 | +$15.20 / +$10.62 | +$11.33 / +$6.92 | yes |
| poly ALL, 1 hour after launch, buy No at 75-90c | 417 / 464 | +$7.54 / +$6.78 | +$6.52 / +$5.29 | +$2.93 / +$1.79 | yes |
| poly weather, 6 hours after launch, buy Yes at 25-50c | 136 / 172 | +$43.70 / +$39.94 | -$3.38 / -$7.75 | -$11.01 / -$14.60 |  |
| poly other (one-off questions), 1 hour still at 50c after launch, buy No (price still at 50c) | 51 / 49 | +$44.39 / +$33.18 | +$57.45 / +$58.90 | +$49.00 / +$50.44 | yes |
| poly ALL, 6 hours after launch, buy No at 75-90c | 621 / 613 | +$6.52 / +$5.15 | +$5.68 / +$4.08 | +$2.14 / +$0.61 | yes |
| poly weather, 1 hour after launch, buy Yes at 25-50c | 126 / 149 | +$43.33 / +$38.17 | -$3.37 / -$9.48 | -$11.24 / -$16.65 |  |
| poly apps/tech, 6 hours after launch, buy No at 75-90c | 52 / 67 | +$11.12 / +$10.11 | +$9.21 / +$8.57 | +$5.52 / +$4.98 | yes |
| poly mentions, 1 hour after launch, buy Yes at 25-50c | 54 / 58 | +$53.04 / +$36.37 | +$20.71 / +$4.53 | +$12.85 / -$3.23 | yes |
| poly ALL, 6 hours after launch, buy Yes at 75-90c | 168 / 244 | +$8.46 / +$5.80 | +$1.83 / +$0.09 | -$1.56 / -$3.24 | yes |
| poly post counts, 6 hours after launch, buy No at 75-90c | 57 / 63 | +$17.05 / +$6.79 | +$13.47 / +$3.28 | +$9.63 / -$0.09 |  |
| poly other (one-off questions), 6 hours after launch, buy No at 75-90c | 34 / 80 | +$9.96 / +$11.82 | +$6.08 / +$8.78 | +$2.49 / +$5.11 |  |
| poly crypto up/down, 1 hour after launch, buy Yes at 50-75c | 53 / 36 | +$16.58 / +$28.89 | +$5.33 / +$17.94 | -$0.08 / +$11.78 |  |
| poly elections, 6 hours after launch, buy No at 50-75c | 51 / 86 | +$10.46 / +$7.20 | +$26.78 / +$24.02 | +$21.21 / +$18.75 |  |
| poly apps/tech, 1 hour after launch, buy No at 50-75c | 86 / 54 | +$21.13 / +$10.58 | +$36.84 / +$20.81 | +$30.26 / +$15.60 |  |
| poly esports, 1 hour after launch, buy No at 50-75c | 66 / 51 | +$21.24 / +$15.08 | +$23.29 / +$18.02 | +$17.03 / +$12.20 |  |
| poly ALL, 1 hour after launch, buy Yes at 75-90c | 60 / 158 | +$6.50 / +$4.10 | +$2.36 / -$0.94 | -$1.10 / -$4.22 |  |
| poly elections, 1 hour after launch, buy No at 50-75c | 58 / 75 | +$23.54 / +$7.84 | +$40.10 / +$23.58 | +$33.66 / +$18.03 |  |
| poly stocks, 1 hour after launch, buy Yes at 50-75c | 58 / 52 | +$12.47 / +$15.73 | +$5.70 / +$10.02 | +$0.19 / +$5.06 |  |
| poly stocks, 6 hours after launch, buy Yes at 75-90c | 40 / 55 | +$6.36 / +$7.32 | -$1.95 / -$0.18 | -$5.15 / -$3.45 |  |
| poly ALL, 1 hour after launch, buy Yes at 90-98c | 69 / 61 | +$9.55 / +$2.79 | +$5.33 / -$1.56 | +$2.44 / -$3.97 |  |
| poly esports, 1 hour after launch, buy Yes at 50-75c | 72 / 67 | +$17.08 / +$8.47 | +$6.07 / -$2.63 | +$0.78 / -$7.18 |  |
| poly crypto up/down, 1 hour still at 50c after launch, buy Yes (price still at 50c) | 59 / 37 | +$9.44 / +$22.53 | -$5.22 / +$9.99 | -$10.09 / +$4.24 |  |
| poly apps/tech, 6 hours after launch, buy Yes at 75-90c | 44 / 45 | +$7.10 / +$4.94 | -$2.81 / -$2.68 | -$6.11 / -$5.90 |  |
| poly ALL, 10 min after launch, buy Yes at 25-50c | 86 / 43 | +$14.15 / +$13.36 | -$31.44 / -$29.46 | -$36.27 / -$34.60 |  |
| poly ALL, 6 hours after launch, buy No at 25-50c | 393 / 446 | +$8.60 / +$4.02 | -$8.59 / -$13.43 | -$14.82 / -$19.46 |  |

All launch bets together, by kind (both halves, +2c):

| Kind | Launch age | Side | Events | Per $100 | vs twins |
|---|---|---|---|---|---|
| ALL | 1 hour | Yes | 3850 | -$26.15 | -$4.94 |
| ALL | 1 hour | No | 3819 | +$7.04 | +$0.80 |
| apps/tech | 1 hour | Yes | 274 | -$27.41 | -$9.22 |
| apps/tech | 1 hour | No | 274 | +$11.52 | +$6.92 |
| crypto price | 1 hour | Yes | 156 | -$46.26 | -$24.13 |
| crypto price | 1 hour | No | 155 | +$14.64 | +$8.59 |
| crypto up/down | 1 hour | Yes | 98 | +$2.21 | +$15.94 |
| crypto up/down | 1 hour | No | 98 | -$19.39 | -$26.61 |
| elections | 1 hour | Yes | 219 | -$42.49 | -$19.11 |
| elections | 1 hour | No | 219 | +$17.77 | +$10.78 |
| entertainment | 1 hour | Yes | 234 | -$37.90 | -$13.26 |
| entertainment | 1 hour | No | 233 | +$18.11 | +$7.29 |
| esports | 1 hour | Yes | 357 | -$12.12 | +$2.19 |
| esports | 1 hour | No | 356 | +$1.76 | +$2.21 |
| geopolitics | 1 hour | Yes | 89 | -$6.99 | +$6.94 |
| geopolitics | 1 hour | No | 89 | -$1.23 | -$6.32 |
| mentions | 1 hour | Yes | 245 | +$1.31 | +$11.71 |
| mentions | 1 hour | No | 245 | -$12.02 | -$13.61 |
| other (one-off questions) | 1 hour | Yes | 371 | -$41.37 | -$20.18 |
| other (one-off questions) | 1 hour | No | 369 | +$20.02 | +$9.37 |
| people/legal | 1 hour | Yes | 58 | -$32.68 | -$13.89 |
| people/legal | 1 hour | No | 58 | +$7.00 | +$5.84 |
| post counts | 1 hour | Yes | 315 | -$62.10 | -$30.32 |
| post counts | 1 hour | No | 315 | +$13.78 | +$5.79 |
| sports | 1 hour | Yes | 101 | -$17.47 | +$18.35 |
| sports | 1 hour | No | 101 | +$6.22 | -$7.60 |
| stocks | 1 hour | Yes | 247 | -$5.75 | +$7.52 |
| stocks | 1 hour | No | 248 | -$3.89 | -$9.93 |
| weather | 1 hour | Yes | 1086 | -$28.86 | +$9.80 |
| weather | 1 hour | No | 1058 | +$0.59 | -$4.75 |

Real-fill check for the survivors: the same bets, but priced at the first trade where someone really bought that side in the hour after the signal (+ fee). 'No buyer' = nobody bought that side at any price in that hour, so we could not have either without setting the price ourselves.

| Bet | Signals | Real buy found | No buyer | Tape unknown | Avg real price vs listed | Per $100 at real price |
|---|---|---|---|---|---|---|
| poly ALL, 1 hour after launch, buy No at 75-90c | 1040 | 597 | 442 | 1 | +6.9c | -$0.25 (520 events) |
| poly ALL, 6 hours after launch, buy No at 75-90c | 1475 | 482 | 993 | 0 | +4.2c | +$2.03 (430 events) |
| poly ALL, 6 hours after launch, buy Yes at 75-90c | 456 | 117 | 339 | 0 | +2.6c | -$3.81 (104 events) |
| poly apps/tech, 6 hours after launch, buy No at 75-90c | 155 | 42 | 113 | 0 | +7.5c | -$0.66 (32 events) |
| poly mentions, 1 hour after launch, buy Yes at 25-50c | 176 | 86 | 90 | 0 | +14.9c | -$13.00 (62 events) |
| poly other (one-off questions), 1 hour still at 50c after launch, buy No (price still at 50c) | 136 | 73 | 63 | 0 | +32.9c | +$10.09 (55 events) |
| poly post counts, 1 hour after launch, buy No at 75-90c | 188 | 76 | 111 | 1 | +7.9c | +$4.15 (64 events) |

Still sitting at the 50c opening price (nobody has moved it yet):

| Kind | Age | Side | Events | Per $100 at +2c | +5c |
|---|---|---|---|---|---|
| ALL | 1 hour still at 50c | Yes | 643 | -$26.75 | -$30.64 |
| ALL | 1 hour still at 50c | No | 643 | +$14.98 | +$8.86 |
| ALL | 10 min still at 50c | Yes | 134 | -$18.77 | -$22.99 |
| ALL | 10 min still at 50c | No | 134 | +$3.33 | -$2.06 |
| ALL | 6 hours still at 50c | Yes | 260 | -$18.62 | -$22.97 |
| ALL | 6 hours still at 50c | No | 260 | +$7.75 | +$2.00 |
| apps/tech | 1 hour still at 50c | Yes | 57 | -$22.89 | -$27.07 |
| apps/tech | 1 hour still at 50c | No | 57 | +$14.10 | +$7.93 |
| apps/tech | 6 hours still at 50c | Yes | 24 | +$2.21 | -$3.23 |
| apps/tech | 6 hours still at 50c | No | 24 | -$12.56 | -$17.29 |
| crypto price | 1 hour still at 50c | Yes | 47 | -$58.13 | -$60.22 |
| crypto price | 1 hour still at 50c | No | 47 | +$38.77 | +$31.68 |
| crypto up/down | 1 hour still at 50c | Yes | 96 | +$0.55 | -$4.65 |
| crypto up/down | 1 hour still at 50c | No | 96 | -$17.85 | -$22.07 |
| crypto up/down | 10 min still at 50c | Yes | 91 | -$4.16 | -$9.10 |
| crypto up/down | 10 min still at 50c | No | 91 | -$13.35 | -$17.81 |
| elections | 1 hour still at 50c | Yes | 22 | -$28.88 | -$32.67 |
| elections | 1 hour still at 50c | No | 22 | +$18.25 | +$11.93 |
| entertainment | 1 hour still at 50c | Yes | 32 | -$17.36 | -$21.77 |
| entertainment | 1 hour still at 50c | No | 32 | +$6.63 | +$0.94 |
| esports | 1 hour still at 50c | Yes | 90 | -$12.47 | -$17.15 |
| esports | 1 hour still at 50c | No | 90 | +$1.86 | -$3.58 |
| esports | 6 hours still at 50c | Yes | 25 | -$9.19 | -$14.06 |
| esports | 6 hours still at 50c | No | 25 | -$1.55 | -$6.82 |
| mentions | 1 hour still at 50c | Yes | 54 | -$28.81 | -$32.61 |
| mentions | 1 hour still at 50c | No | 54 | +$17.98 | +$11.67 |
| mentions | 6 hours still at 50c | Yes | 37 | +$13.65 | +$7.57 |
| mentions | 6 hours still at 50c | No | 37 | -$24.50 | -$28.51 |
| other (one-off questions) | 1 hour still at 50c | Yes | 100 | -$69.25 | -$70.89 |
| other (one-off questions) | 1 hour still at 50c | No | 100 | +$58.21 | +$49.75 |
| other (one-off questions) | 6 hours still at 50c | Yes | 52 | -$61.82 | -$63.87 |
| other (one-off questions) | 6 hours still at 50c | No | 52 | +$50.81 | +$42.77 |
| sports | 1 hour still at 50c | Yes | 34 | -$16.02 | -$20.55 |
| sports | 1 hour still at 50c | No | 34 | +$6.20 | +$0.48 |
| sports | 6 hours still at 50c | Yes | 21 | -$45.76 | -$48.65 |
| sports | 6 hours still at 50c | No | 21 | +$35.97 | +$28.65 |
| stocks | 1 hour still at 50c | Yes | 72 | -$3.83 | -$9.01 |
| stocks | 1 hour still at 50c | No | 72 | -$5.55 | -$10.67 |
| stocks | 6 hours still at 50c | Yes | 36 | -$27.46 | -$31.36 |
| stocks | 6 hours still at 50c | No | 36 | +$17.56 | +$11.24 |

## Kalshi: which launch bets beat their seasoned twins

443 cells tried (kind x launch age x side x price band, plus 'still at 50c'). Candidates: 3 on the first half, 6 on the second. **Survivors: 0.**

Top 25 by the weaker half (per $100 staked):

| Bet | Events A / B | vs twins A / B | +2c A / B | +5c A / B | Survived |
|---|---|---|---|---|---|
| kalshi weather, 10 min after launch, buy No at 90-98c | 109 / 169 | +$12.56 / +$12.93 | -$7.22 / -$5.72 | -$9.60 / -$8.02 |  |
| kalshi weather, 1 hour after launch, buy No at 90-98c | 122 / 171 | +$11.41 / +$14.22 | -$8.22 / -$4.35 | -$10.64 / -$6.69 |  |
| kalshi weather, 6 hours after launch, buy No at 90-98c | 112 / 136 | +$11.42 / +$15.78 | -$8.56 / -$2.79 | -$10.97 / -$5.23 |  |
| kalshi other (one-off questions), 10 min after launch, buy No at 25-50c | 33 / 38 | +$20.79 / +$34.58 | -$18.34 / -$7.01 | -$24.10 / -$13.26 |  |
| kalshi other (one-off questions), 10 min after launch, buy No at 50-75c | 115 / 176 | +$13.23 / +$6.21 | -$29.21 / -$32.35 | -$32.40 / -$35.31 |  |
| kalshi weather, 6 hours after launch, buy Yes at 50-75c | 37 / 58 | +$20.56 / +$9.59 | +$4.12 / -$6.57 | -$0.88 / -$10.97 |  |
| kalshi other (one-off questions), 6 hours after launch, buy No at 2-10c | 47 / 68 | +$76.64 / +$36.24 | +$13.54 / -$24.28 | -$13.21 / -$50.29 |  |
| kalshi weather, 1 hour after launch, buy No at 75-90c | 78 / 149 | +$4.68 / +$7.80 | -$8.06 / -$4.98 | -$11.10 / -$8.13 |  |
| kalshi weather, 10 min after launch, buy No at 75-90c | 81 / 161 | +$4.39 / +$4.22 | -$8.36 / -$8.55 | -$11.39 / -$11.56 |  |
| kalshi other (one-off questions), 1 hour after launch, buy No at 2-10c | 43 / 42 | +$117.67 / +$45.61 | +$52.61 / -$16.93 | -$6.78 / -$50.21 |  |
| kalshi other (one-off questions), 6 hours after launch, buy Yes at 10-25c | 111 / 121 | +$13.23 / +$25.11 | -$32.80 / -$36.91 | -$43.29 / -$44.94 |  |
| kalshi ALL, 1 hour after launch, buy No at 2-10c | 147 / 127 | +$22.09 / +$17.54 | -$43.26 / -$43.83 | -$63.15 / -$62.19 |  |
| kalshi ALL, 10 min after launch, buy No at 2-10c | 87 / 69 | +$45.66 / +$21.25 | -$24.62 / -$46.01 | -$47.77 / -$61.33 |  |
| kalshi other (one-off questions), 1 hour after launch, buy Yes at 10-25c | 89 / 107 | +$14.30 / +$10.56 | -$31.61 / -$45.40 | -$43.53 / -$52.80 |  |
| kalshi ALL, 6 hours after launch, buy No at 2-10c | 165 / 176 | +$15.76 / +$12.03 | -$38.74 / -$41.41 | -$54.19 / -$60.64 |  |
| kalshi sports, 1 hour after launch, buy No at 10-25c | 129 / 151 | +$13.19 / +$7.26 | -$38.89 / -$39.55 | -$48.01 / -$48.20 |  |
| kalshi weather, 1 hour after launch, buy Yes at 50-75c | 31 / 45 | +$6.28 / +$17.89 | -$9.83 / +$1.73 | -$14.06 / -$2.86 |  |
| kalshi ALL, 6 hours after launch, buy No at 10-25c | 252 / 270 | +$4.17 / +$6.58 | -$38.79 / -$36.15 | -$47.33 / -$44.83 |  |
| kalshi weather, 1 hour after launch, buy Yes at 25-50c | 113 / 196 | +$3.26 / +$6.24 | -$16.10 / -$13.18 | -$22.32 / -$19.53 |  |
| kalshi other (one-off questions), 10 min after launch, buy Yes at 10-25c | 62 / 59 | +$6.74 / +$10.57 | -$21.10 / -$20.35 | -$33.68 / -$31.21 |  |
| kalshi weather, 6 hours after launch, buy No at 50-75c | 90 / 157 | +$2.33 / +$1.17 | -$9.31 / -$10.51 | -$13.19 / -$14.28 |  |
| kalshi other (one-off questions), 10 min after launch, buy Yes at 25-50c | 98 / 127 | +$1.45 / +$6.03 | -$11.24 / -$8.45 | -$17.60 / -$15.16 |  |
| kalshi sports, 6 hours after launch, buy No at 10-25c | 169 / 204 | +$0.80 / +$16.17 | -$44.49 / -$25.81 | -$52.19 / -$35.84 |  |
| kalshi weather, 10 min after launch, buy Yes at 25-50c | 134 / 215 | +$0.26 / +$0.43 | -$19.17 / -$18.99 | -$25.11 / -$24.97 |  |
| kalshi ALL, 10 min after launch, buy No at 10-25c | 105 / 100 | +$0.26 / +$12.54 | -$50.06 / -$38.56 | -$56.35 / -$46.82 |  |

All launch bets together, by kind (both halves, +2c):

| Kind | Launch age | Side | Events | Per $100 | vs twins |
|---|---|---|---|---|---|
| ALL | 1 hour | Yes | 15780 | -$35.70 | -$12.68 |
| ALL | 1 hour | No | 13534 | -$21.66 | -$7.62 |
| apps/tech | 1 hour | Yes | 51 | -$55.03 | -$38.92 |
| apps/tech | 1 hour | No | 44 | -$15.91 | -$4.79 |
| crypto price | 1 hour | Yes | 47 | -$21.63 | -$0.44 |
| crypto price | 1 hour | No | 38 | -$25.09 | -$8.32 |
| elections | 1 hour | Yes | 39 | -$47.85 | -$29.96 |
| elections | 1 hour | No | 32 | +$6.16 | +$20.24 |
| entertainment | 1 hour | Yes | 69 | -$54.68 | -$38.54 |
| entertainment | 1 hour | No | 31 | -$21.77 | -$8.67 |
| mentions | 1 hour | Yes | 154 | -$40.19 | -$20.16 |
| mentions | 1 hour | No | 150 | -$21.54 | -$8.33 |
| other (one-off questions) | 1 hour | Yes | 1296 | -$33.48 | -$16.41 |
| other (one-off questions) | 1 hour | No | 1232 | -$25.31 | -$6.53 |
| sports | 1 hour | Yes | 12912 | -$36.07 | -$12.13 |
| sports | 1 hour | No | 11108 | -$22.44 | -$8.96 |
| stocks | 1 hour | Yes | 91 | -$17.03 | +$2.10 |
| stocks | 1 hour | No | 87 | -$22.28 | -$10.10 |
| weather | 1 hour | Yes | 1066 | -$24.89 | -$7.33 |
| weather | 1 hour | No | 774 | -$8.67 | +$6.77 |

Still sitting at the 50c opening price (nobody has moved it yet):

| Kind | Age | Side | Events | Per $100 at +2c | +5c |
|---|---|---|---|---|---|


