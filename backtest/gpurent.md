# GPU rental price bets vs the Ornn index (27 Nov 2026)

Tool: `gpurent.py`. Data: probe `nfx_gpurent_fetch` (markets, every real trade, Ornn's free index) -> `bt_cache/nf/gpu/`;
then `python3 store.py pull bt_cache/nf && python3 gpurent.py report` offline.

## In short

**Too early, and nothing so far. No track.** Re-check when the first monthly-average bets settle (Jan-Feb 2027).

- **The bets.** Polymarket's "GPU rental price" bets: what one hour on an H100 / H200 / B200 / B300 / A100 / RTX graphics card rents for. They all settle on the Ornn Compute Price Index (data.ornn.com, one number a day per card, from real rental deals). 77 events, 780 markets, $12.3 million traded.
- **What has settled: 197 markets, all from the older families** ("Will the Ornn H100 Index be between $2.75 and $3.00 on August 31?", "hit $X by May 31?"), May to October 2026, about $1.6 million traded. **The new families Jan asked about** ("H100 average rental price in December 2026 above $3.00?", out to December 2028) **have 0 settled markets.** The first ones settle in the first week of January. They hold most of the money ($10 million).
- **The outside number is free, but short.** Ornn's free API (`api.ornnai.com/api/gpu/<name>/index-history`, no key, readable from Actions) gives the last 3 months, one value a day. Older days need a paid key ($500 a month). Old copies on web.archive.org stretch it: B200 / H200 / A100 back to 22 June, H100 back to January, the rest only from 28 August. Our reading of the rules matches 126 of 128 settled day-value markets.
- **Does the index beat the price? No.** A plain guess (today's 7-day average, plus how much the index usually moves in that many days) forecasts worse than the price at every distance from the end: 2 to 3 weeks out, a week out, and in the last 3 days.
- **Buying where they disagree by 10c or more:** 11 bets, 6 won, **-$11.64 per $100** ("Too early to tell": 4 settle months). 60 of the 71 signals found no trade at all in the next 2 hours, so you could not even buy them. Only No bets: +$19.14 per $100 on 13 bets, could be luck.
- **Backward look** (what did the winners share?): the bracket holding today's value vs the others, by days left and price, 80 cuts. Best cell: No on a bracket that does not hold today's value, 3 weeks out: 9 bets, 9 won, +$9.03 per $100. That is the old "things don't happen" lean, found by looking, 4 months. Nothing to build.
- **The new monthly-average bets today** sit where the plain guess puts them, within about 7c on every B200, B300 and H100 line. Only H200's top lines ($6.75 to $7.50) are 10-17c dearer than the guess, and they trade little.

## The plain guess vs the price (settled markets)

Forecast score: lower is better (0 = always right). 1,046 looks at 121 settled markets, May-Oct 2026.

| time left | price | plain guess | looks |
|---|---|---|---|
| 11+ days | 0.106 | 0.109 | 328 |
| 4-10 days | 0.068 | 0.077 | 361 |
| last 3 days | 0.042 | 0.046 | 357 |

In the last days the price also sees Ornn's live hourly number (free, but no free history). We only use a day's value once it is a day old.

## Rules tested

$10 a bet, one bet per market, first look 28 to 1 days before the end. Price paid: the worst real trade in the next 2 hours (never better than the price seen) + 2c + the market's fee (5% fee rate on the old families, none on the new monthly-average ones). Counted by settle month (all brackets of one month win and lose together).

| rule | bets | won | months | P&L | per $100 | signals nobody could buy |
|---|---|---|---|---|---|---|
| guess 10c+ off the price, either side | 11 | 6 | 4 | -$13.10 | -$11.64 | 60 |
| guess 10c+ above the price: buy Yes | 8 | 3 | 4 | -$2.66 | -$3.21 | 36 |
| guess 10c+ below the price: buy No | 13 | 9 | 5 | +$25.39 | +$19.14 | 39 |
| guess 20c+ off the price | 13 | 8 | 5 | +$32.74 | +$24.50 | 27 |
| guess 10c+ off, last 7 days only | 9 | 3 | 4 | -$31.87 | -$34.43 | 37 |
| backward look: No on a non-holding bracket, 3 weeks out | 9 | 9 | 4 | +$8.16 | +$9.03 | - |

Exam (`exam.score`, 86 tries counted): every line "Too early to tell" (4-5 separate months). The two logged lines are in `backtest/ledger.md`.

**Biggest wins, read one by one.** One bet made more than the whole profit: No on "A100 between $1.00 and $1.25 on 30 Sep" at 29c (+$21.91). The guess said 50c, the price 72c, and the A100 index dipped to $0.91 at month end. That is one good call on a coin flip, not a pattern. The other wins are No bets at 66-91c that paid $0.75-6.74 each; the losses are full $10 losses.

## Would it fit a small bankroll? (rough guesses)

- **Most it could make on an average day:** under $0.50 a day, even if the No lean were real (about 3 bets a month you can actually buy at $10).
- **Money needed:** $50-100 (bets stay open up to a month).
- **Where it stops growing:** about $10-25 a bet on the old day-value brackets (about $100 traded a day per market, about 5 trades a day). The new monthly-average lines are busier (about $2,300 a day per market in December's), maybe $50-100 a bet.
- **A bad day:** one month's brackets go wrong together: about -$30 to -$50 at $10 bets.

## Traps (for the next dig)

- **Only 3 months free.** Older days come from web.archive.org copies of the free JSON. The archive blocks Actions after a few reads (connection refused, then pages that are not JSON), so the 22 Sep copies of B200 / H200 / A100 were read by hand and sit in `gpurent.WEBV`. Old copies label a day at 20:00 UTC, today's at 04:00 UTC; the same date lines up (checked on 25 shared days, gap 1-8c from later revisions).
- **Revisions after the settle.** RTX 5090 on 31 Aug: the index now shows $0.56, the market paid the $0.50-0.55 bracket. The old families settled on Ornn's older site (dashboard.ornnai.com). 2 of 128 checks miss for this reason.
- **The index is jumpy day to day but trends over months.** H100 went $2.69, $2.99, $2.72 on three days in a row; B200 went from $4.29 in June to $9.78 now. A guess built on the day-to-day wander of the 7-day average was far too sure of itself (it lost to the price by much more). The version used here takes the size of real 30-day moves (not their direction) from the whole history, so it knows a little about later months.
- **Thin trade lists.** Most signals had no trade in the next 2 hours. Pricing at the next trade whenever it came would invent fills.
- **"Hit $X by" bets close the moment the price is hit.** Looks after the close must be skipped, or the guess gets scored on a market that is already over.

## Next

Free re-check in January / February 2027: by then the December 2026 and January 2027 monthly-average bets (B200, B300, H100, H200; about $5.9 million traded) will have settled. Run `nfx_gpurent_fetch` again (it also saves that day's free 3-month window, so keep a copy every month) and `gpurent.py report`.
