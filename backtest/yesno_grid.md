# Criss-cross: which Yes/No patterns would have worked? (2026-11-10, `yesno.py grid`)

**Short answer:** 1,055 ways of cutting the bets. Only 124 were ahead in both halves of the window; 667 were behind in
both. The ones that held up are three old friends, not a new trick:

1. **Nearly sure things, far from the end** (Yes or No at 90c+, more than 30 days left): about +$2 to +$4 per $100 on
   the chart. Two catches. Most of it is election markets, which all settled on one night (the 3 Nov midterms, no
   upsets), so it's really one lucky-or-not event, not 347. And at real buys almost nobody was selling: 9 to 26 of
   400 tries found a seller within 3 hours. Same family as the `boring_no` paper track already running.
2. **Crypto "won't get there"** (No at 50-70c on crypto price questions, 3-7 days left): +$18 on the chart, but
   +$5.62 at real buys with a luck range from -$8 to +$19. Could be luck. Same family as the `crypto_no` paper track.
3. **Weekdays:** no pattern. The 97c+ bets "win" on every weekday alike, so it's the price, not the day.

**Kalshi: nothing.** One weak cut out of hundreds (+$14.55, worst case -$21.91). The surest thing on Kalshi is losing.

Verdict: no new candidate. It found, by a different road, the two leads that already have paper tracks and a
21 Dec check. The reliable patterns are all on the losing side: long shots under 10c, either side, either site.

---

Research only. Jan's ask: cut the all-Yes / all-No bets every way and look for patterns that paid. Same bets as `backtest/yesno.md` ($1 on every open market every day at 12:00 UTC; Polymarket 10 Aug - 9 Nov, Kalshi 11 Sep - 9 Nov), cut by Yes/No x price x kind of market x time left x weekday, alone and crossed.

Prices: Kalshi = the real ask + fee. Polymarket = chart price + what real buyers paid on top (0.1c to 1.5c by price band) + fee; the best Polymarket patterns are then priced again at real buys from the trade tape.

A pattern counts only if (1) it has 25+ separate events in each half of the window, (2) it was ahead in BOTH halves, (3) its luck range stays above $0 even with the bar raised for every cut we looked at.

- Cuts with enough events: **1,055**
- Ahead in both halves: **124**. Behind in both halves: **667**. (A coin would give about 263 each.)
- Ahead in both halves and above $0 on the normal luck range: **72**
- Still above $0 with the bar raised for 1,055 tries: **35**

## The best patterns (ahead in both halves, sorted by the raised-bar low end)

| Site | Bet | Pattern | Events | $1 bets | Per $100 | First half | Second half | Low end (normal) | Low end (raised bar) |
|---|---|---|---|---|---|---|---|---|---|
| Polymarket | No | price+kind+time left: 50-70c, crypto price, 3-7 days | 292 | 865 | +$18.23 | +$8.43 | +$33.90 | +$11.75 | +$3.53 |
| Polymarket | Yes | price+kind+time left: 90-97c, elections, over 30 days | 347 | 4,350 | +$3.93 | +$3.85 | +$4.15 | +$3.15 | +$2.18 |
| Polymarket | Yes | price+kind+time left: 97c+, elections, over 30 days | 136 | 1,136 | +$2.06 | +$2.07 | +$2.05 | +$2.00 | +$1.92 |
| Polymarket | Yes | price+kind: 97c+, elections | 307 | 3,318 | +$1.96 | +$1.94 | +$1.97 | +$1.91 | +$1.86 |
| Polymarket | Yes | price+kind: 90-97c, elections | 429 | 7,951 | +$3.39 | +$3.21 | +$3.52 | +$2.71 | +$1.85 |
| Polymarket | Yes | price+time left: 97c+, over 30 days | 169 | 1,309 | +$1.95 | +$2.02 | +$1.76 | +$1.80 | +$1.63 |
| Polymarket | Yes | price+time left: 90-97c, over 30 days | 421 | 4,747 | +$3.33 | +$3.29 | +$3.46 | +$2.46 | +$1.37 |
| Polymarket | Yes | price+kind+time left: 97c+, crypto price, 3-7 days | 189 | 1,461 | +$1.29 | +$1.30 | +$1.27 | +$1.25 | +$1.21 |
| Polymarket | Yes | price+kind: 97c+, apps/tech | 49 | 215 | +$1.44 | +$1.50 | +$1.38 | +$1.29 | +$1.10 |
| Polymarket | Yes | price+weekday: 97c+, Mon | 544 | 1,273 | +$1.38 | +$1.34 | +$1.41 | +$1.23 | +$1.05 |
| Polymarket | Yes | price+time left: 97c+, 3-7 days | 423 | 1,914 | +$1.30 | +$1.32 | +$1.28 | +$1.17 | +$1.01 |
| Polymarket | Yes | price+weekday: 97c+, Sun | 458 | 979 | +$1.36 | +$1.07 | +$1.60 | +$1.18 | +$0.94 |
| Polymarket | Yes | price+weekday: 90-97c, Fri | 658 | 1,681 | +$2.65 | +$2.78 | +$2.54 | +$1.85 | +$0.83 |
| Polymarket | Yes | price+weekday: 90-97c, Sat | 660 | 1,645 | +$2.45 | +$2.56 | +$2.37 | +$1.69 | +$0.72 |
| Polymarket | Yes | price: 97c+ | 773 | 7,966 | +$1.14 | +$1.25 | +$1.04 | +$0.91 | +$0.63 |
| Polymarket | Yes | price+kind+time left: 97c+, other, under 1 day | 63 | 82 | +$1.01 | +$0.91 | +$1.10 | +$0.84 | +$0.63 |
| Polymarket | No | price+kind+time left: 97c+, elections, 3-7 days | 369 | 1,340 | +$1.03 | +$0.75 | +$1.15 | +$0.84 | +$0.59 |
| Polymarket | Yes | price+weekday: 97c+, Tue | 562 | 1,333 | +$1.15 | +$1.28 | +$1.04 | +$0.88 | +$0.55 |
| Polymarket | Yes | price: 90-97c | 1,038 | 11,339 | +$2.17 | +$2.38 | +$1.94 | +$1.45 | +$0.54 |
| Polymarket | No | price+kind: 97c+, geopolitics | 33 | 621 | +$1.17 | +$1.31 | +$0.94 | +$0.88 | +$0.50 |
| Polymarket | No | price+kind+time left: 97c+, other, over 30 days | 153 | 8,535 | +$0.91 | +$0.90 | +$1.08 | +$0.71 | +$0.47 |
| Polymarket | Yes | price+kind: 97c+, crypto price | 217 | 3,472 | +$0.73 | +$0.91 | +$0.47 | +$0.61 | +$0.46 |
| Polymarket | Yes | price+weekday: 97c+, Sat | 483 | 1,215 | +$1.15 | +$1.21 | +$1.10 | +$0.83 | +$0.43 |
| Polymarket | Yes | price+weekday: 97c+, Fri | 464 | 1,115 | +$1.15 | +$1.28 | +$1.06 | +$0.81 | +$0.38 |
| Polymarket | Yes | price+weekday: 90-97c, Thu | 616 | 1,342 | +$2.32 | +$3.04 | +$1.06 | +$1.46 | +$0.37 |
| Polymarket | No | price+kind+time left: 97c+, other, 3-7 days | 351 | 2,459 | +$0.78 | +$0.82 | +$0.73 | +$0.56 | +$0.29 |
| Polymarket | Yes | price+weekday: 97c+, Wed | 463 | 1,145 | +$1.09 | +$1.17 | +$1.02 | +$0.73 | +$0.27 |
| Polymarket | Yes | price+kind+time left: 90-97c, crypto price, 3-7 days | 192 | 754 | +$3.19 | +$4.90 | +$0.99 | +$1.90 | +$0.27 |
| Polymarket | No | price+kind: 97c+, other | 491 | 24,625 | +$0.69 | +$0.67 | +$0.76 | +$0.51 | +$0.27 |
| Polymarket | No | price+kind+time left: 97c+, elections, under 1 day | 411 | 638 | +$0.86 | +$0.14 | +$1.08 | +$0.58 | +$0.23 |
| Polymarket | No | price+kind+time left: 97c+, other, under 1 day | 347 | 1,016 | +$0.57 | +$0.42 | +$0.66 | +$0.39 | +$0.17 |
| Polymarket | Yes | price+time left: 97c+, 1-3 days | 565 | 1,864 | +$0.64 | +$0.69 | +$0.61 | +$0.41 | +$0.11 |
| Polymarket | No | price+kind: 97c+, elections | 535 | 15,938 | +$0.65 | +$0.30 | +$1.25 | +$0.38 | +$0.04 |
| Polymarket | Yes | price+weekday: 90-97c, Wed | 712 | 1,819 | +$1.99 | +$2.56 | +$1.40 | +$1.12 | +$0.02 |
| Polymarket | Yes | price+weekday: 90-97c, Sun | 650 | 1,464 | +$2.00 | +$2.06 | +$1.95 | +$1.12 | +$0.00 |
| Polymarket | Yes | price+time left: 97c+, 7-30 days | 274 | 1,703 | +$1.35 | +$1.57 | +$1.27 | +$0.71 | -$0.09 |
| Polymarket | No | price+weekday: 97c+, Sat | 1,494 | 9,848 | +$0.33 | +$0.10 | +$0.69 | +$0.14 | -$0.09 |
| Polymarket | Yes | price+weekday: 90-97c, Mon | 674 | 1,637 | +$1.89 | +$1.94 | +$1.84 | +$1.01 | -$0.12 |
| Polymarket | Yes | price+kind+time left: 97c+, crypto price, 1-3 days | 200 | 1,293 | +$0.44 | +$0.73 | +$0.01 | +$0.18 | -$0.15 |
| Polymarket | No | price+kind+time left: 97c+, elections, 1-3 days | 431 | 1,069 | +$0.72 | +$0.52 | +$0.78 | +$0.33 | -$0.16 |

## The surest losers (for laughs, and to avoid)

| Site | Bet | Pattern | Events | $1 bets | Per $100 | First half | Second half | Low end (normal) | Low end (raised bar) |
|---|---|---|---|---|---|---|---|---|---|
| Kalshi | No | price+kind+time left: under 10c, sports, 3-7 days | 60 | 129 | -$100.00 | -$100.00 | -$100.00 | -$100.00 | -$100.00 |
| Kalshi | No | price+kind+time left: 10-30c, stocks, 1-3 days | 62 | 372 | -$100.00 | -$100.00 | -$100.00 | -$100.00 | -$100.00 |
| Kalshi | Yes | price+kind+time left: under 10c, other (one-off questions), under 1 day | 202 | 333 | -$96.86 | -$95.34 | -$100.00 | -$102.04 | -$108.62 |
| Kalshi | Yes | price+kind+time left: 10-30c, stocks, under 1 day | 219 | 600 | -$92.62 | -$84.68 | -$100.00 | -$96.59 | -$101.63 |
| Polymarket | No | price+kind+time left: under 10c, elections, 7-30 days | 387 | 4,003 | -$91.33 | -$49.72 | -$94.33 | -$96.76 | -$103.65 |
| Polymarket | No | price+kind: under 10c, elections | 446 | 11,269 | -$90.88 | -$83.98 | -$95.42 | -$98.25 | -$107.59 |
| Kalshi | No | price+time left: under 10c, 3-7 days | 158 | 393 | -$94.35 | -$100.00 | -$83.32 | -$103.68 | -$115.51 |
| Polymarket | No | price+kind+time left: under 10c, crypto price, 3-7 days | 195 | 2,215 | -$90.09 | -$100.00 | -$76.26 | -$97.94 | -$107.91 |
| Kalshi | No | price+kind: 10-30c, stocks | 243 | 1,103 | -$86.42 | -$95.97 | -$65.86 | -$92.84 | -$101.00 |
| Kalshi | No | price+weekday: under 10c, Mon | 220 | 403 | -$91.19 | -$93.62 | -$87.43 | -$99.86 | -$110.87 |
| Kalshi | No | kind+weekday: stocks, Mon | 100 | 477 | -$81.34 | -$86.61 | -$74.09 | -$86.48 | -$93.01 |
| Polymarket | No | price+kind+time left: under 10c, elections, 1-3 days | 379 | 615 | -$89.52 | -$45.04 | -$94.50 | -$98.54 | -$109.98 |
| Kalshi | Yes | kind+weekday: stocks, Thu | 88 | 416 | -$79.55 | -$75.36 | -$86.11 | -$84.77 | -$91.41 |
| Polymarket | No | price+kind+time left: under 10c, elections, over 30 days | 351 | 5,486 | -$92.58 | -$89.90 | -$100.00 | -$103.82 | -$118.09 |
| Kalshi | No | price+weekday: under 10c, Tue | 212 | 384 | -$88.28 | -$95.03 | -$72.28 | -$98.14 | -$110.65 |

Where the solid ones sit: Kalshi Yes: 1, Polymarket No: 32, Polymarket Yes: 39

## The best Polymarket patterns at real buys

Up to 400 random bets from each pattern, priced at the first real buy within 3 hours after noon, +1c, + fee, $25 a bet (the exam's rule). 'No real buy' = nobody bought there in 3 hours, so a bot may not have either.

| Pattern | Sampled | Had a real buy | Per $100 at real buys | Luck range | Exam verdict |
|---|---|---|---|---|---|
| No, price+kind+time left: 50-70c, crypto price, 3-7 days | 400 | 114 | +$5.62 | -$8.02 to +$19.26 | Ahead, but could be luck |
| Yes, price+kind+time left: 90-97c, elections, over 30 days | 400 | 9 | +$4.57 | +$2.99 to +$6.15 | Too early to tell |
| Yes, price+kind+time left: 97c+, elections, over 30 days | 400 | 10 | +$1.29 | +$0.96 to +$1.63 | Too early to tell |
| Yes, price+kind: 97c+, elections | 400 | 26 | +$1.17 | +$1.02 to +$1.31 | Ahead, but could be luck |
| Yes, price+kind: 90-97c, elections | 400 | 25 | +$1.94 | -$5.20 to +$9.08 | Ahead, but could be luck |
| Yes, price+time left: 97c+, over 30 days | 400 | 12 | +$1.49 | +$1.09 to +$1.89 | Too early to tell |
| Yes, price+time left: 90-97c, over 30 days | 400 | 21 | -$5.48 | -$17.05 to +$6.08 | Losing |
| Yes, price+kind+time left: 97c+, crypto price, 3-7 days | 400 | 53 | +$1.34 | +$1.15 to +$1.53 | Ahead, but could be luck |

## The best Kalshi patterns through the exam (real asks already)

| Pattern | Bets | Separate events | Per $100 | Luck range | Worst case per $100 | Exam verdict |
|---|---|---|---|---|---|---|
| Yes, price+kind+time left: 50-70c, other (one-off questions), 1-3 days | 149 | 92 | +$14.55 | +$0.47 to +$28.62 | -$21.91 | Ahead, but could be luck |

