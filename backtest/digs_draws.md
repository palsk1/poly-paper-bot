# Soccer draws, deeper (digs.py draws)

## Plain summary (2026-11-10)

- **Draws are still a bit cheap overall.** 4,538 games, draw bought 24h before kickoff at 15-50c, paying 2c over the
  chart: +$5.60 per $100, worst case about +$1.70 per $100. Same at 6h and 1h before. Paying 4c over: about -$1.40.
  So the whole lead is about 2-3c a bet. Same story as PR #63.
- **Where it lives:** draws priced 22-32c (+$6 to +$10 per $100 at +2c). Very cheap (15-22c) and dear (32-50c) draws
  lose. Big leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions and Europa League) do NOT have it: real
  first buys there lost $3.30 per $100 even at +0c. Smaller leagues carry it (+$16 per $100 at +0c, +$8 at +2c,
  worst case -$5). Big leagues are watched by more sharp bettors, which fits.
- **Not steady:** April, July and November lost at +2c; 7 of 10 months were ahead. 55 leagues sliced, so a few
  league results (Romania +$65, Turkey -$36) are mostly luck.
- **Other side of the same coin:** NO on the favorite (= draw or underdog wins) is about even at +2c (+$2.10), so the
  cheapness sits in the draw leg, and the favorite leg is a touch dear.
- **Other 3-way sports:** none in the data. Only soccer markets carry a draw leg here.
- **Verdict:** the pre-registered 21 Dec check (PROTOCOL 5) stays as written. A narrower version (22-32c, outside the
  big leagues) was found by slicing this same data, so it is only a secondary check, added to PROTOCOL 5 as
  `soccer_draw_mid`. No track (research mode).


Generated 2026-11-10T17:25:16Z. In-sample games only (ended before 2026-11-10; the 21 Dec holdout is untouched). Chart price 1h after the snapshot, never after kickoff, +2c + fee, held to the result. 'Per $100' = profit per $100 staked, grouped by game.

## Which leagues have draw bets (24h-before snapshots)

arg 207, fif 201, col 184, bra 172, mls 168, chi 144, es2 139, bra2 133, col1 123, mex 118, spl 113, itsb 102, lib 99, por 95, kor 94, tur 94, egy1 93, clf 93, j1100 92, elc 91, sud 90, nor 85, bl2 79, ucl 76, ere 73, uel 72, per1 69, j2100 66, den 53, rou1 52, fr2 51, lec 51, chi1 48, fl1 47, lal 46, nwsl 46, bol1 45, jap 45, conl 44, sea 40

## Full-time draws at 15-50c, sliced

### By hours before kickoff

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| 1h before start | 5571 | 5571 | 1671 | 26c | +$13.76 | +$5.60 | +$2.07 to +$9.13 | -$1.46 | +$4.74 / +$6.47 |
| 24h before start | 4538 | 4538 | 1374 | 26c | +$13.68 | +$5.60 | +$1.72 to +$9.49 | -$1.39 | +$1.04 / +$10.17 |
| 6h before start | 5094 | 5094 | 1534 | 26c | +$13.68 | +$5.56 | +$1.89 to +$9.24 | -$1.46 | +$2.78 / +$8.38 |

### By draw price (24h before)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| 15-22c | 794 | 794 | 165 | 19c | +$5.73 | -$4.25 | -$15.16 to +$6.66 | -$12.50 | -$12.31 / +$3.69 |
| 22-27c | 1796 | 1796 | 523 | 25c | +$15.01 | +$6.44 | -$0.00 to +$12.89 | -$0.93 | +$3.24 / +$9.60 |
| 27-32c | 1629 | 1629 | 569 | 29c | +$17.35 | +$9.85 | +$3.74 to +$15.97 | +$3.26 | +$7.95 / +$11.72 |
| 32-50c | 319 | 319 | 117 | 35c | +$3.55 | -$2.04 | -$13.84 to +$9.76 | -$7.06 | -$9.10 / +$4.93 |

### By league (24h before, leagues with 25+ games)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| acle | 31 | 31 | 9 | 23c | +$21.92 | +$12.24 | -$40.03 to +$64.52 | +$4.01 | -$25.81 / +$50.96 |
| arg | 207 | 207 | 56 | 31c | -$14.67 | -$19.80 | -$34.87 to -$4.74 | -$24.35 | -$31.13 / -$8.52 |
| argpn | 32 | 32 | 21 | 32c | +$99.62 | +$87.99 | +$49.12 to +$126.86 | +$77.66 | +$65.42 / +$109.41 |
| bl2 | 79 | 79 | 25 | 24c | +$26.02 | +$16.56 | -$15.55 to +$48.68 | +$8.44 | -$12.23 / +$42.93 |
| bol1 | 35 | 35 | 13 | 23c | +$53.24 | +$41.30 | -$9.71 to +$92.30 | +$31.10 | +$54.59 / +$28.41 |
| bra | 167 | 167 | 41 | 27c | -$11.53 | -$17.58 | -$36.01 to +$0.86 | -$22.84 | -$19.12 / -$16.06 |
| bra2 | 125 | 125 | 44 | 29c | +$18.71 | +$11.10 | -$11.18 to +$33.37 | +$4.41 | +$6.32 / +$15.85 |
| brco | 30 | 30 | 8 | 27c | -$3.84 | -$10.43 | -$55.67 to +$34.81 | -$16.17 | +$19.67 / -$36.89 |
| chi | 143 | 143 | 41 | 24c | +$16.60 | +$7.69 | -$15.54 to +$30.92 | +$0.05 | +$3.99 / +$11.46 |
| chi1 | 47 | 47 | 14 | 26c | +$12.74 | +$4.66 | -$34.60 to +$43.92 | -$2.32 | +$5.82 / +$3.53 |
| clf | 77 | 77 | 23 | 24c | +$20.26 | +$11.09 | -$20.97 to +$43.15 | +$3.24 | -$4.70 / +$27.32 |
| col | 152 | 152 | 43 | 24c | +$14.91 | +$6.09 | -$16.40 to +$28.59 | -$1.45 | -$8.46 / +$19.80 |
| col1 | 121 | 121 | 44 | 27c | +$29.30 | +$20.57 | -$3.62 to +$44.76 | +$12.96 | +$29.97 / +$10.94 |
| conl | 36 | 36 | 6 | 25c | -$36.22 | -$40.85 | -$78.01 to -$3.70 | -$44.85 | -$62.24 / -$17.47 |
| cze1 | 25 | 25 | 6 | 24c | -$4.47 | -$11.65 | -$64.60 to +$41.31 | -$17.81 | -$38.57 / +$13.15 |
| den | 52 | 52 | 13 | 24c | +$1.26 | -$6.45 | -$43.65 to +$30.75 | -$13.06 | +$14.63 / -$27.72 |
| ecu1 | 26 | 26 | 8 | 26c | +$12.19 | +$4.40 | -$46.51 to +$55.32 | -$2.36 | -$19.54 / +$27.10 |
| efl | 33 | 33 | 6 | 23c | -$25.08 | -$30.92 | -$73.36 to +$11.52 | -$35.91 | -$29.25 / -$31.73 |
| egy1 | 93 | 93 | 30 | 31c | -$0.24 | -$6.13 | -$29.26 to +$17.00 | -$11.35 | +$13.10 / -$25.21 |
| elc | 89 | 89 | 23 | 25c | -$0.89 | -$8.05 | -$35.18 to +$19.08 | -$14.25 | -$8.59 / -$7.55 |
| epl | 33 | 33 | 10 | 24c | +$21.39 | +$12.25 | -$36.45 to +$60.94 | +$4.40 | -$52.27 / +$69.53 |
| ere | 70 | 70 | 22 | 22c | +$38.94 | +$27.44 | -$9.59 to +$64.47 | +$17.72 | +$37.18 / +$17.44 |
| es2 | 139 | 139 | 44 | 27c | +$14.78 | +$6.91 | -$14.97 to +$28.78 | +$0.06 | +$2.49 / +$10.89 |
| fif | 159 | 159 | 49 | 25c | +$18.89 | +$10.26 | -$11.10 to +$31.63 | +$2.81 | +$15.77 / +$5.06 |
| fl1 | 42 | 42 | 11 | 23c | +$8.65 | +$0.18 | -$42.60 to +$42.96 | -$7.06 | +$46.78 / -$45.75 |
| fr2 | 51 | 51 | 22 | 27c | +$53.60 | +$43.22 | +$4.89 to +$81.56 | +$34.18 | +$59.96 / +$29.66 |
| itsb | 102 | 102 | 37 | 28c | +$25.03 | +$16.85 | -$8.27 to +$41.97 | +$9.68 | +$11.23 / +$22.09 |
| j1100 | 92 | 92 | 29 | 27c | +$13.78 | +$6.05 | -$20.64 to +$32.73 | -$0.69 | +$14.93 / -$2.06 |
| j2100 | 58 | 58 | 26 | 28c | +$56.82 | +$46.47 | +$10.46 to +$82.47 | +$37.40 | -$0.97 / +$86.09 |
| ja2 | 25 | 25 | 8 | 28c | +$11.74 | +$4.30 | -$46.23 to +$54.83 | -$2.20 | -$20.89 / +$28.94 |
| jap | 45 | 45 | 14 | 27c | +$10.45 | +$2.98 | -$35.02 to +$40.97 | -$3.54 | -$3.01 / +$7.98 |
| kor | 94 | 94 | 30 | 27c | +$13.90 | +$6.21 | -$20.36 to +$32.78 | -$0.50 | -$14.66 / +$26.89 |
| lal | 40 | 40 | 13 | 27c | +$17.31 | +$9.28 | -$31.50 to +$50.06 | +$2.29 | -$0.07 / +$18.81 |
| lec | 51 | 51 | 7 | 23c | -$42.79 | -$47.30 | -$78.21 to -$16.39 | -$51.14 | -$69.87 / -$24.76 |
| lib | 91 | 91 | 25 | 27c | +$0.36 | -$6.57 | -$32.40 to +$19.25 | -$12.60 | -$18.55 / +$5.64 |
| mar1 | 31 | 31 | 16 | 31c | +$61.78 | +$52.12 | +$8.01 to +$96.24 | +$43.56 | +$39.34 / +$63.81 |
| mex | 117 | 117 | 30 | 24c | +$2.86 | -$4.91 | -$29.59 to +$19.77 | -$11.57 | -$9.26 / -$0.74 |
| mls | 163 | 163 | 45 | 24c | +$14.45 | +$5.55 | -$16.50 to +$27.59 | -$2.06 | -$24.85 / +$35.86 |
| nor | 78 | 78 | 17 | 23c | -$7.17 | -$14.57 | -$44.64 to +$15.49 | -$20.87 | -$24.29 / -$6.14 |
| nwsl | 45 | 45 | 11 | 24c | -$2.96 | -$10.24 | -$49.27 to +$28.78 | -$16.50 | -$33.88 / +$12.79 |
| per1 | 68 | 68 | 24 | 26c | +$31.56 | +$22.26 | -$10.91 to +$55.44 | +$14.21 | +$19.50 / +$25.16 |
| pol | 29 | 29 | 6 | 26c | -$23.90 | -$29.23 | -$72.10 to +$13.64 | -$33.85 | -$6.10 / -$52.59 |
| por | 78 | 78 | 21 | 27c | -$2.50 | -$9.19 | -$37.24 to +$18.86 | -$15.01 | +$7.34 / -$24.65 |
| rou1 | 51 | 51 | 25 | 27c | +$76.64 | +$64.57 | +$24.98 to +$104.15 | +$54.05 | +$48.45 / +$79.92 |
| rus | 36 | 36 | 15 | 26c | +$55.09 | +$44.16 | -$3.56 to +$91.88 | +$34.69 | +$30.40 / +$55.07 |
| scop | 32 | 32 | 7 | 24c | -$10.81 | -$17.65 | -$62.95 to +$27.65 | -$23.51 | -$27.70 / -$8.06 |
| sea | 36 | 36 | 9 | 25c | -$2.94 | -$10.06 | -$52.35 to +$32.22 | -$16.20 | +$16.62 / -$38.29 |
| spl | 93 | 93 | 27 | 23c | +$23.52 | +$13.66 | -$16.56 to +$43.87 | +$5.26 | +$20.97 / +$6.71 |
| sud | 85 | 85 | 27 | 27c | +$15.97 | +$7.96 | -$20.08 to +$36.00 | +$0.99 | +$26.15 / -$10.76 |
| swe | 34 | 34 | 10 | 23c | +$23.63 | +$13.83 | -$36.01 to +$63.68 | +$5.49 | +$50.93 / -$27.66 |
| tur | 90 | 90 | 16 | 25c | -$31.37 | -$36.37 | -$60.16 to -$12.58 | -$40.69 | -$36.56 / -$36.19 |
| ucl | 65 | 65 | 10 | 24c | -$36.95 | -$41.82 | -$69.58 to -$14.06 | -$45.98 | -$6.47 / -$76.83 |
| uel | 65 | 65 | 14 | 23c | -$10.87 | -$17.84 | -$50.35 to +$14.68 | -$23.78 | -$7.19 / -$28.73 |
| unl | 28 | 28 | 8 | 25c | +$8.52 | +$0.69 | -$50.51 to +$51.88 | -$6.08 | +$6.83 / -$4.79 |

### By how even the match is: favorite's win price (24h before)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| fav 45-60c | 1240 | 1240 | 377 | 26c | +$13.33 | +$5.33 | -$2.12 to +$12.77 | -$1.61 | +$5.52 / +$5.14 |
| fav 60-75c | 568 | 568 | 138 | 21c | +$14.30 | +$4.26 | -$8.49 to +$17.02 | -$4.15 | +$1.04 / +$7.50 |
| fav 75c+ (lopsided) | 49 | 49 | 11 | 16c | +$34.20 | +$19.52 | -$33.10 to +$72.13 | +$7.74 | -$54.98 / +$89.01 |
| fav <45c (even) | 1003 | 1003 | 331 | 29c | +$10.38 | +$3.36 | -$4.27 to +$10.98 | -$2.82 | +$1.18 / +$5.48 |

### By what the 3 legs add up to (24h before)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| sum 101-104c | 232 | 232 | 62 | 26c | -$0.80 | -$7.77 | -$24.38 to +$8.83 | -$13.82 | +$2.13 / -$18.07 |
| sum 104c+ | 52 | 52 | 20 | 33c | +$14.08 | +$7.60 | -$23.71 to +$38.92 | +$1.84 | +$19.75 / -$4.26 |
| sum 99-101c | 2380 | 2380 | 715 | 26c | +$13.57 | +$5.45 | +$0.05 to +$10.85 | -$1.58 | +$2.58 / +$8.31 |
| sum <99c | 196 | 196 | 60 | 26c | +$15.61 | +$7.37 | -$11.65 to +$26.38 | +$0.23 | +$2.43 / +$12.43 |

### By month (24h before)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| 2026-02 | 33 | 33 | 11 | 26c | +$28.96 | +$19.70 | -$28.47 to +$67.86 | +$11.68 | +$16.14 / +$22.82 |
| 2026-03 | 117 | 117 | 42 | 27c | +$34.19 | +$24.84 | -$0.23 to +$49.91 | +$16.71 | +$3.82 / +$44.78 |
| 2026-04 | 685 | 685 | 190 | 26c | +$3.33 | -$3.90 | -$13.59 to +$5.80 | -$10.18 | -$4.25 / -$3.55 |
| 2026-05 | 657 | 657 | 194 | 26c | +$12.24 | +$4.20 | -$6.08 to +$14.48 | -$2.75 | +$7.18 / +$1.21 |
| 2026-06 | 146 | 146 | 53 | 27c | +$33.21 | +$23.99 | +$2.34 to +$45.64 | +$15.97 | +$10.66 / +$36.60 |
| 2026-07 | 416 | 416 | 114 | 26c | +$2.96 | -$4.37 | -$16.95 to +$8.22 | -$10.71 | -$9.69 / +$0.61 |
| 2026-08 | 1010 | 1010 | 317 | 26c | +$17.68 | +$9.29 | +$0.99 to +$17.60 | +$2.03 | +$6.54 / +$11.99 |
| 2026-09 | 567 | 567 | 180 | 26c | +$17.88 | +$9.55 | -$1.57 to +$20.67 | +$2.34 | +$16.74 / +$2.20 |
| 2026-10 | 745 | 745 | 229 | 25c | +$16.72 | +$8.30 | -$1.41 to +$18.02 | +$1.03 | +$7.14 / +$9.50 |
| 2026-11 | 162 | 162 | 44 | 26c | +$1.60 | -$5.63 | -$25.53 to +$14.28 | -$11.88 | -$7.66 / -$3.69 |

### By kickoff weekday (24h before)

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| Fri | 526 | 526 | 166 | 26c | +$17.90 | +$9.56 | -$1.98 to +$21.10 | +$2.33 | +$3.99 / +$15.16 |
| Mon | 378 | 378 | 120 | 27c | +$14.93 | +$7.04 | -$6.22 to +$20.29 | +$0.17 | +$11.05 / +$3.05 |
| Sat | 1155 | 1155 | 361 | 26c | +$17.16 | +$8.85 | +$1.10 to +$16.60 | +$1.65 | +$0.82 / +$16.77 |
| Sun | 1110 | 1110 | 338 | 26c | +$14.62 | +$6.46 | -$1.44 to +$14.37 | -$0.60 | +$1.13 / +$11.70 |
| Thu | 485 | 485 | 143 | 25c | +$13.51 | +$5.25 | -$6.82 to +$17.32 | -$1.89 | -$7.69 / +$18.30 |
| Tue | 449 | 449 | 123 | 26c | +$3.30 | -$4.07 | -$16.12 to +$7.98 | -$10.45 | +$8.53 / -$16.47 |
| Wed | 435 | 435 | 123 | 26c | +$6.61 | -$1.00 | -$13.36 to +$11.37 | -$7.58 | -$1.88 / -$0.08 |

## The team legs of the same soccer games

If draws are cheap, the two 'team X wins' legs should be a bit dear. Buying NO on a team = draw or the other team wins.

### YES on the team, by role and hours before kickoff

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| favorite | 1h before start | 5784 | 5784 | 2915 | 53c | -$7.29 | -$10.57 | -$12.43 to -$8.71 | -$13.62 | -$10.00 / -$11.13 |
| favorite | 24h before start | 3832 | 3832 | 1864 | 53c | -$9.22 | -$12.47 | -$14.79 to -$10.15 | -$15.50 | -$11.98 / -$12.95 |
| favorite | 6h before start | 5169 | 5169 | 2572 | 53c | -$8.11 | -$11.37 | -$13.34 to -$9.41 | -$14.41 | -$10.24 / -$12.47 |
| underdog | 1h before start | 5228 | 5276 | 1253 | 24c | -$4.15 | -$11.44 | -$14.98 to -$7.90 | -$17.69 | -$9.47 / -$13.38 |
| underdog | 24h before start | 3512 | 3537 | 859 | 24c | -$3.41 | -$10.66 | -$14.98 to -$6.35 | -$16.89 | -$9.02 / -$12.29 |
| underdog | 6h before start | 4681 | 4718 | 1137 | 24c | -$3.03 | -$10.39 | -$14.15 to -$6.63 | -$16.70 | -$7.71 / -$13.03 |

### NO on the team, by role and hours before kickoff

| group | games | bets | draw won | avg price | at chart | +2c | 90% band +2c | +4c | halves +2c |
|---|---|---|---|---|---|---|---|---|---|
| favorite | 1h before start | 5784 | 5784 | 2869 | 47c | +$4.39 | +$0.17 | -$1.94 to +$2.28 | -$3.72 | +$0.29 / +$0.05 |
| favorite | 24h before start | 3828 | 3828 | 1968 | 47c | +$6.33 | +$2.10 | -$0.46 to +$4.66 | -$1.80 | +$2.03 / +$2.18 |
| favorite | 6h before start | 5167 | 5167 | 2597 | 47c | +$5.28 | +$1.04 | -$1.18 to +$3.26 | -$2.87 | +$0.46 / +$1.63 |
| underdog | 1h before start | 5228 | 5276 | 4023 | 76c | -$0.53 | -$3.01 | -$4.22 to -$1.80 | -$5.36 | -$3.28 / -$2.74 |
| underdog | 24h before start | 3512 | 3537 | 2678 | 76c | -$0.77 | -$3.25 | -$4.75 to -$1.75 | -$5.61 | -$3.41 / -$3.10 |
| underdog | 6h before start | 4681 | 4718 | 3581 | 76c | -$0.89 | -$3.36 | -$4.65 to -$2.07 | -$5.70 | -$3.87 / -$2.85 |

## Real first buy before kickoff (trade tape)

Decide at the snapshot, then fill at the first real buy of that side after it and before kickoff, +0c and +2c, fee included. 400-game sample per slice.

- **draw 24h, league epl/lal/sea/bun/fl1/ucl (big leagues)** (302 bets on the chart)

```
   tapes read 302, with a real buy of that side in the window: 302
   real first buy minus chart price: median +0.5c
   real first buy +0c + fee: 302 bets, 302 games, won 74, -3.3 per $100, 90% band -19.3 to +12.6
   real first buy +2c + fee: 302 bets, 302 games, won 74, -10.5 per $100, 90% band -25.3 to +4.2
```

- **draw 24h, other leagues** (4236 bets on the chart)

```
   tapes read 400, with a real buy of that side in the window: 390
   real first buy minus chart price: median +0.5c
   real first buy +0c + fee: 390 bets, 390 games, won 123, +16.1 per $100, 90% band +1.9 to +30.3
   real first buy +2c + fee: 390 bets, 390 games, won 123, +8.0 per $100, 90% band -5.2 to +21.2
```

- **draw 24h, favorite 60c+** (617 bets on the chart)

```
   tapes read 400, with a real buy of that side in the window: 384
   real first buy minus chart price: median +0.5c
   real first buy +0c + fee: 384 bets, 384 games, won 93, +15.8 per $100, 90% band -1.5 to +33.0
   real first buy +2c + fee: 384 bets, 384 games, won 93, +5.4 per $100, 90% band -10.2 to +21.1
```

- **draw 24h, favorite under 60c** (2243 bets on the chart)

```
   tapes read 400, with a real buy of that side in the window: 391
   real first buy minus chart price: median +0.5c
   real first buy +0c + fee: 391 bets, 391 games, won 114, +3.5 per $100, 90% band -10.1 to +17.0
   real first buy +2c + fee: 391 bets, 391 games, won 114, -3.5 per $100, 90% band -16.1 to +9.1
```

- **NO on favorite, 24h** (3828 bets on the chart)

```
   tapes read 400, with a real buy of that side in the window: 395
   real first buy minus chart price: median +0.5c
   real first buy +0c + fee: 395 bets, 395 games, won 212, +11.7 per $100, 90% band +3.3 to +20.0
   real first buy +2c + fee: 395 bets, 395 games, won 212, +7.2 per $100, 90% band -0.8 to +15.2
```


