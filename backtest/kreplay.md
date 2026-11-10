# Kalshi 15-min crypto: backtest vs recorded books vs live (kreplay.py, 2026-11-10)

## What it means

- **The backtest's fills are honest.** On 31 recorded hours (8 Nov 22:08 to 10 Nov 07:56 UTC), the same signals
  filled from the real books and the full trade tape (the live bot's own rule) fill the same orders as the backtest's
  1-minute candles, plus a few extra, and every extra one won. No order lost on the tape that the candles skipped.
- **The live orders, re-scored by the backtest, lose the same.** Every live losing fill (1 of 1 safe, 5 of 5 plain,
  11 of 11 early) is also a losing fill in the backtest model. So the "twice the losses" was not a fill-model flaw:
  the backtest itself says these were bad days for the plain and early versions.
- **kc_maker_safe holds up.** Backtest on the last 3 days: 390 fills, 2 lost, **+$0.72 per $100** (break-even is
  about 1.2 losses in 100; it had 0.5). In the recorded hours: 173 tape fills, 0 lost, +$0.96. In the live hours
  alone: -$0.10, which matches live (-$0.23): one BTC loss at 08:00 on 10 Nov.
- **kc_maker (no spot check) and kc_maker_early lose on recent days** in the backtest too: -$0.25 and -$2.45 per
  $100 over 3 days. Their 60-day numbers were about break-even, so this looks like their normal swing, not a bug.
- Not tested: whether $25-$100 orders get the same fills (queue size), and Kalshi from Sweden.

Generated 2026-11-10T10:50:08Z by probe `btkreplay`. Paper research only. 2016 settled windows in the last 3 days
(kcrypto candles + Kalshi results). Recordings 2026-11-08T22:08:14Z to 2026-11-10T07:56:00Z. Live tracks started
2026-11-09T19:00:00Z. "Break-even" = how many losses in 100 the average price allows.

## A. The backtest's own model (candles, 'fair' fill) on recent days

- **kc_maker_safe** (3 min left, z 2.0), all recent days: 548 signals, 390 filled, lost 2 (0.5 in 100; break-even 1.2 in 100), avg price 98.8c, +$0.72 per $100; all signals won 99.6 in 100
- **kc_maker_safe**, recorded hours: 287 signals, 197 filled, lost 0, avg price 98.9c, +$1.08 per $100
- **kc_maker_safe**, live hours: 115 signals, 81 filled, lost 1 (1.2 in 100; break-even 1.1 in 100), avg price 98.9c, -$0.10 per $100
- **kc_maker** (3 min left, no spot check), all recent days: 1048 signals, 792 filled, lost 14 (1.8 in 100; break-even 1.5 in 100), avg price 98.5c, -$0.25 per $100
- **kc_maker**, recorded hours: 405 filled, lost 12 (3.0 in 100), -$1.51 per $100
- **kc_maker**, live hours: 174 filled, lost 6 (3.4 in 100), -$2.13 per $100
- **kc_maker_early** (8 min left, no spot check), all recent days: 475 signals, 439 filled, lost 34 (7.7 in 100; break-even 5.4 in 100), avg price 94.6c, -$2.45 per $100
- **kc_maker_early**, recorded hours: 261 filled, lost 22 (8.4 in 100), -$3.11 per $100
- **kc_maker_early**, live hours: 123 filled, lost 7 (5.7 in 100), -$0.62 per $100

By day (filled / lost / per $100): kc_maker_safe 7 Nov 71/1 +$0.15, 8 Nov 116/0 +$1.34, 9 Nov 140/0 +$0.98,
10 Nov 63/1 -$0.34. kc_maker 7 Nov 131/1 +$0.96, 8 Nov 256/4 -$0.03, 9 Nov 276/4 +$0.03, 10 Nov 129/5 -$2.52.
kc_maker_early 7 Nov 53/2 +$2.18, 8 Nov 119/11 -$3.74, 9 Nov 181/16 -$3.59, 10 Nov 86/5 -$1.10.

## B. Same windows, filled from the recorded book and full trade tape (live fill rule)

Skipped: 203 signals in recording gaps, 20-61 with no recorded book.

| Track | Signals | Tape fills (lost) | Candle fills (lost) | Traded-through only (lost) | Tape per $100 | Candle per $100 | Tape-only fills (lost) | Candle-only fills |
|---|---|---|---|---|---|---|---|---|
| kc_maker_safe | 208 | 173 (0) | 163 (0) | 160 (0) | +$0.96 | +$1.01 | 10 (0) | 0 |
| kc_maker | 391 | 341 (7) | 325 (7) | 320 (7) | -$0.75 | -$0.81 | 16 (0) | 0 |
| kc_maker_early | 209 | 202 (21) | 200 (21) | 200 (21) | -$5.32 | -$5.42 | 2 (0) | 0 |

Every recorded loser traded through our price (a certain fill in any model).

## C. The live tracks' own orders, re-scored by the backtest's fill model

| Track | Live orders | Live fills (lost) | Live per $100 | Backtest fills (lost) | Backtest per $100 | Live losers the backtest also fills |
|---|---|---|---|---|---|---|
| kc_maker_safe | 86 | 73 (1) | -$0.23 | 81 (1) | -$0.15 | 1 of 1 |
| kc_maker | 192 | 161 (5) | -$1.66 | 184 (5) | -$1.29 | 5 of 5 |
| kc_maker_early | 121 | 114 (11) | -$4.43 | 120 (11) | -$3.97 | 11 of 11 |
