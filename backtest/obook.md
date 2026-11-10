# Order book shapes: verdict first (2026-11-10)

**Plain answer: no. Dropped, no track.** Research only (`obook.py`), nothing live was changed.

The question: when one side of the order book is much thicker, big orders get pulled, or the gap between
buy and sell price widens, does the price move next, and by enough to make money after costs?

- **The book does nudge the price, a little.** When the buy side is much thicker, the price drifts up about
  1c over the next 5 minutes on Polymarket fast markets and 1-2c on Kalshi. That part is real.
- **But the toll is bigger than the nudge.** Buying now and selling later costs the gap between the buy and
  sell price (usually 2c, often more) plus fees. On Polymarket fast markets, following the thick side lost
  **about $20 per $100** per round trip, worse than buying at random times ($7 per $100). Thick-book moments
  are exactly when the gap is wide.
- **Short holds (1, 5, 15, 60 minutes): 0 of 672 versions made money in both halves of the data**, except
  two "fade a big 5-minute swing" versions on Kalshi 15-minute markets. Those are about price swings, not
  the book, and they turn into a loss (about -$8 per $100) if each fill is 2c worse.
- **As a maker (resting orders instead of crossing the gap) it's worse.** Orders get filled when the price is
  about to go against you. Leaning with the thick side helps a few dollars, still a loss everywhere:
  about -$5 to -$30 per $100 held to the result, -$12 to -$30 per $100 when also exiting as a maker.
- **Held to the result:** a few versions look ahead (best: follow 5-minute taker flow on Kalshi hourly
  crypto, +$30 per $100). Don't believe it yet. It is 27 hours of crypto that all moved together, the gain
  comes from cheap long shots, and weighted by money it is about **$0.13 per $100**. Out of 140 hold-to-end
  versions, 25 beat random entries in both halves; pure luck would give about 35.
- **Time of day** changes the cost (the gap is 2c in European daytime, 6-13c around midnight UTC on
  Polymarket fast markets), not the direction.

Caveat: only 30 hours of recordings (8-10 Nov). For short holds that is plenty (429k market-minutes, 2.7k
Kalshi 15-minute windows). For hold-to-result it is thin, so two versions are **pre-registered** for one
re-check on fresh recordings only (`python3 obook.py recheck`, from about 2026-12-01, needs 2 weeks of new
hours): `K_crypto_other flowr follow end` and `K_other I10 follow end`. Pass bar: ahead in both halves and
the event band's low end above -$5 per $100. If they fail, close this for good.

How it was tested: real recorded books every minute, buy at the ask with 10+ shares at the top, sell at
the bid, Kalshi fee both ways (Polymarket fee set to 0, which is kind to us), thresholds picked on one time
half and scored on the other, random-side control on the same minutes, bands that resample whole events,
maker fills only after the real Kalshi tape traded through the whole queue ahead.

Families: `K_15m` Kalshi 15-minute markets, `K_crypto_other` Kalshi hourly/daily crypto, `K_index` Kalshi
S&P/Nasdaq hourly ranges, `K_weather`, `K_other` (oil, gold, Trump-says and so on), `P_fast` Polymarket
markets ending within 3 hours, `P_wide` Polymarket markets our tracks hold (every 5 min).
Features: `I1/I3/I10` buy-side vs sell-side size at the top / within 3c / within 10c, `pullB` orders
pulled (+1 bids, -1 asks), `dspr` gap now vs 5 min ago, `flowr` Kalshi taker buys minus sells last 5 min,
`mom5` price move last 5 min (control). "follow" buys the side the feature points to, "fade" the other.

---

## Full output

Data: 30 recorder hours (rec-20261108-22.jsonl.gz .. rec-20261110-07.jsonl.gz), 8333 markets, 428,997 market-minutes with a price between 5c and 95c.

Families: P_fast 153,480, P_wide 146,869, K_other 50,503, K_crypto_other 30,985, K_15m 28,898, K_index 11,079, K_weather 7,183

## 1. Does the book shape move the price at all? (mid move in cents, top 10% vs bottom 10%)

| family | YES side thicker: mid move 5 min | YES side thinner | bids pulled | asks pulled | typical spread |
|---|---|---|---|---|---|
| K_15m | +2.01c | -0.30c | +3.99c | +2.33c | 2.0c |
| K_crypto_other | +0.91c | -0.70c | +0.29c | +1.47c | 2.0c |
| K_index | +6.52c | +2.32c | +0.78c | +3.11c | 5.0c |
| K_other | +0.50c | -1.04c | -0.10c | +1.19c | 4.0c |
| K_weather | +2.29c | -2.16c | -0.40c | +1.12c | 6.0c |
| P_fast | +0.78c | -0.33c | -0.02c | +1.42c | 2.0c |
| P_wide | +0.10c | -0.08c | -0.11c | +0.15c | 1.5c |

## 2. Trading it as a taker (buy at the ask, sell at the bid later, fees in)

What doing nothing clever costs (every minute, random side), $ per $100:

| fam | 1 | 15 | 5 | 60 | end |
|---|---|---|---|---|---|
| K_15m | -13.63 | nan | -10.47 | nan | -13.46 |
| K_crypto_other | -18.06 | -11.19 | -16.54 | -23.04 | 1.86 |
| K_index | -28.07 | -27.74 | -28.63 | -26.50 | 35.13 |
| K_other | -25.91 | -21.78 | -24.68 | -15.05 | -9.10 |
| K_weather | -28.50 | -25.66 | -27.83 | -32.62 | -41.46 |
| P_fast | -7.47 | -7.12 | -7.34 | -7.55 | nan |
| P_wide | nan | -9.12 | -9.11 | -9.12 | nan |

Cells ahead in BOTH halves (thresholds picked on the other half):

- hold 1 min: 164 cells, 0 ahead in both halves, 30 beat the random side in both
- hold 5 min: 188 cells, 2 ahead in both halves, 32 beat the random side in both
- hold 15 min: 160 cells, 0 ahead in both halves, 25 beat the random side in both
- hold 60 min: 160 cells, 0 ahead in both halves, 21 beat the random side in both
- hold end: 140 cells, 11 ahead in both halves, 25 beat the random side in both

Best 15 by the worse half:

| fam | hz | feat | tail | side | rand | A | nA | B | nB | worst_half |
|---|---|---|---|---|---|---|---|---|---|---|
| K_index | end | flowr | 0.10 | follow | 35.13 | 113.85 | 28 | nan | 0 | 113.85 |
| K_crypto_other | 60 | mom5 | 0.02 | fade | -23.04 | nan | 0 | 75.64 | 12 | 75.64 |
| K_index | end | I3 | 0.10 | fade | 35.13 | 227.84 | 20 | 73.58 | 53 | 73.58 |
| K_index | end | I1 | 0.02 | follow | 35.13 | nan | 0 | 63.46 | 91 | 63.46 |
| K_index | end | flowr | 0.02 | fade | 35.13 | nan | 0 | 37.35 | 93 | 37.35 |
| K_crypto_other | end | flowr | 0.10 | follow | 1.86 | 30.93 | 835 | 25.88 | 681 | 25.88 |
| K_crypto_other | end | pullB | 0.02 | follow | 1.86 | nan | 0 | 22.88 | 4862 | 22.88 |
| K_other | end | I10 | 0.10 | follow | -9.10 | 18.87 | 250 | 38.69 | 247 | 18.87 |
| K_crypto_other | 60 | mom5 | 0.10 | fade | -23.04 | nan | 0 | 17.11 | 94 | 17.11 |
| K_other | end | flowr | 0.02 | fade | -9.10 | 12.60 | 113 | 21.29 | 127 | 12.60 |
| K_crypto_other | end | dspr | 0.10 | fade | 1.86 | 11.09 | 1120 | 10.02 | 268 | 10.02 |
| K_index | end | I1 | 0.02 | fade | 35.13 | nan | 0 | 8.80 | 180 | 8.80 |
| K_15m | 5 | mom5 | 0.10 | fade | -10.47 | 4.97 | 646 | 9.31 | 451 | 4.97 |
| K_index | end | dspr | 0.02 | follow | 35.13 | 19.11 | 2 | 4.80 | 4 | 4.80 |
| K_index | end | mom5 | 0.02 | follow | 35.13 | 5.96 | 1 | 2.76 | 51 | 2.76 |

## 3. Leads checked harder (event-clustered 90% band, all data)

- K_crypto_other flowr follow, hold end: $+30.43 per $100 (band +7.9 to +57.8), 1470 bets, 106 events
- K_other I10 follow, hold end: $+42.06 per $100 (band -26.0 to +104.7), 482 bets, 55 events
- P_fast I3 follow, hold 5: $-20.44 per $100 (band -23.0 to -18.1), 20282 bets, 1003 events
- K_15m mom5 fade, hold 5: $+6.10 per $100 (band -4.0 to +16.7), 1087 bets, 739 events

## 4. As a maker on Kalshi (rest at the best price, back of the queue, fills from the real tape)

| fam | rule | half | fills | mark15 | taker_exit15 | held |
|---|---|---|---|---|---|---|
| K_15m | always, both sides | A | 17193 | nan | nan | -25.46 |
| K_15m | always, both sides | B | 18581 | nan | nan | -21.36 |
| K_15m | lean with the thick side | A | 3637 | nan | nan | -29.86 |
| K_15m | lean with the thick side | B | 4110 | nan | nan | -22.51 |
| K_15m | lean against it | A | 4054 | nan | nan | -14.72 |
| K_15m | lean against it | B | 4441 | nan | nan | -16.21 |
| K_crypto_other | always, both sides | A | 10141 | -2.75 | -9.19 | -7.74 |
| K_crypto_other | always, both sides | B | 7761 | -3.80 | -9.16 | -21.55 |
| K_crypto_other | lean with the thick side | A | 1589 | 6.91 | -1.82 | -5.21 |
| K_crypto_other | lean with the thick side | B | 785 | -0.26 | -6.46 | -36.17 |
| K_crypto_other | lean against it | A | 2625 | -5.46 | -12.41 | -7.54 |
| K_crypto_other | lean against it | B | 1617 | -2.11 | -7.52 | -16.48 |
| K_index | always, both sides | A | 12 | -8.56 | -33.66 | -100.00 |
| K_index | always, both sides | B | 534 | -6.69 | -14.37 | -33.86 |
| K_index | lean with the thick side | A | 5 | -10.90 | -31.33 | -100.00 |
| K_index | lean with the thick side | B | 194 | -18.34 | -25.93 | -32.44 |
| K_index | lean against it | A | 7 | -6.89 | -35.32 | nan |
| K_index | lean against it | B | 274 | 6.35 | -0.47 | -28.00 |
| K_other | always, both sides | A | 2276 | 0.04 | -16.19 | 9.14 |
| K_other | always, both sides | B | 2724 | -3.16 | -25.98 | -33.45 |
| K_other | lean with the thick side | A | 437 | 18.48 | -16.17 | 20.67 |
| K_other | lean with the thick side | B | 488 | 22.95 | -29.26 | -20.01 |
| K_other | lean against it | A | 625 | -1.29 | -12.66 | 8.52 |
| K_other | lean against it | B | 687 | 4.50 | -23.75 | -31.21 |
| K_weather | always, both sides | A | 1863 | -2.80 | -20.52 | -32.23 |
| K_weather | always, both sides | B | 2153 | 2.96 | -14.22 | -41.04 |
| K_weather | lean with the thick side | A | 276 | 12.70 | -11.96 | -27.14 |
| K_weather | lean with the thick side | B | 277 | 10.48 | -12.82 | -9.53 |
| K_weather | lean against it | A | 442 | -12.88 | -26.34 | -41.00 |
| K_weather | lean against it | B | 462 | -2.76 | -18.33 | -58.73 |
