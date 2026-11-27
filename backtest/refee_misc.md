# Old crypto ideas at Polymarket's new crypto fee (refee_misc, 27 Nov 2026)

On 20 Nov 2026 at 23:59 UTC Polymarket cut its crypto taker fee (fee = rate x shares x p x (1-p)): from 0.07 to
**0.05 on the Bitcoin 5- and 15-minute windows** and **0.01 on every other crypto market**. Kalshi did not change.
Would any idea we dropped work now? Short answer: **no new track.** One idea goes from about even to "ahead, but
could be luck", and that lead rests on a handful of long-shot wins.

All money below is per $100 bet, after fees. Same data, same rules as the first tests; only the fee changes.

## 1. Options price vs Polymarket's Bitcoin / Ethereum price markets (`optfair.py`)

The fee did matter here: 13,395 of the 14,077 markets carried the 0.07 fee then (another 404 a 0.25 setting, 277 none).
At the old fee these bets paid about $4 in fees per $100; at 0.01 that drops to about 50-60c.
New option `optfair.tbets(..., fee_rate=0.01)`; left out, it uses each market's own fee as before (old numbers come back exactly).

| Rule (5c+ gap, $10 bets, real trades + 1c) | Bets | Old fee | New fee (0.01) | No fee at all | Exam at new fee |
|---|---|---|---|---|---|
| End price ("above / between on a date") | 3,122 | -$3.23 | **+$0.43** | +$1.03 | Ahead, but could be luck |
| &nbsp;&nbsp;same, fresh markets only | 2,425 | -$1.87 | +$1.85 | +$2.46 | |
| Reach / dip | 2,464 | +$1.80 | **+$5.09** | +$5.62 | Ahead, but could be luck |
| &nbsp;&nbsp;same, fresh markets only | 1,947 | +$2.33 | +$5.64 | +$6.18 | |
| Reach / dip, last 30 min to 6 hours (the lead that failed on fresh markets) | 433 | -$8.90 | **-$5.90** | -$5.45 | Behind, but could be bad luck |

- **End price:** now about even. A 3c gap loses (-$1.03), a 10c gap +$1.13, and 1c more a share makes it -$3.83. Nothing to build.
- **Reach / dip:** the best of the lot, but read the bets one by one: 5 events made more than all the profit
  (+$1,586 of +$1,259); without them it is -$326. They are long shots bought at 1-6c ("will ETH reach $2,100 on
  May 23" bought at 1c paid $490 on a $10 bet). Long shots under 20c: +$20.28; everything else about even or behind.
  ETH +$13.92, BTC +$0.18. 1c more a share: +$0.99; 2c more: -$2.80. Months swing from -$36 to +$39.
  Its luck range runs from -$2.30 to +$12.47, and it would need about 5,000 bets (years) to prove itself.
- **The last-hours lead** stays dead: fees were not the problem.
- Rough ceiling (reach / dip, if it were real): about 9 bets a day at $10, so about $4-5 a day on average, about
  $100 in the account; thin long-shot books, so it stops growing at around $10-25 a bet; a bad day is losing all
  ~9 bets, about -$90. Rough guess.

## 2. The same 15-minute bet on Kalshi and Polymarket (`xvenue.py`)

Real recordings from after the cut (21-27 Nov, 130 hour files, 600 windows priced on both sites), Polymarket at
its new fee (0.05 Bitcoin, 0.01 the rest; new option `pair_reads(..., pfee=xvenue.NEW_PFEE)`), Kalshi at its real
trades within 5 s of the Polymarket read (the recorder now saves the real read second). A pair now costs about
**$1.05** (was $1.058 at the old fee on the same reads; $1.03 before any fee, Kalshi's fee is most of the rest). It pays $1.00.
Under $1.00: **93 of 12,565 reads (7 in 1,000)**, the first such gap in 83 of 600 windows; under $0.99 only 20 reads.
At the old fee it would have been 56 reads in 50 windows. Buying every first gap at 10 shares a side would have made
about **$5.39 in a whole week** if both sites always agreed, but they disagree on the result in about 17 of 1,000
windows (a pair then pays $0 or $2), and in the first test half the gaps were gone within 2 s. Still dropped.

## 3. Copying the GoodFallen Bitcoin 5-minute wallet late (`wallet5m.py`)

Real re-run on its 400 newest windows (the data is in the price store), new option `copytest(rate=0.05)`;
the default 0.07 gives the old -$0.44 to -$1.08 back exactly.

| Copy late by | Old fee (0.07) | New fee (0.05) | No fee |
|---|---|---|---|
| 1 s | -$0.87 | **-$0.08** | +$1.97 |
| 3 s | -$0.99 | -$0.21 | +$1.80 |
| 10 s | -$1.08 | -$0.35 | +$1.53 |
| 30 s | -$0.44 | +$0.23 | +$1.97 |
| 60 s | -$0.65 | -$0.03 | +$1.55 |

Exam: 1 s late "Behind, but could be bad luck", 30 s late "Ahead, but could be luck". Break-even, only ~1.5 days
of windows, and his real profit is Polymarket's maker rebate, which a copier buying at the offer does not get. Still dropped.

## 4. Did these pay a taker fee at all?

- `khourly.py pm_run` (Polymarket hourly / daily crypto): **not affected**, waiting bids pay no fee.
- `kcrypto.py pm_run` (Polymarket 15-minute windows, `backtest/pm15.md`): **not affected**, waiting bids, scored with no fee.
- `fasthunt.py`: **already at the new fee** (0.01 since 20 Nov is built in, `FEE = 0.01`).

## Exam cards (separate trial ledger, not `backtest/ledger.md`)

| Idea | Bets | Per $100 | Worst case per $100 | Verdict |
|---|---|---|---|---|
| 1c fee: options price, end-price markets | 3,122 | +$0.43 | -$20.78 | Ahead, but could be luck |
| 1c fee: options price, reach / dip | 2,464 | +$5.09 | -$10.77 | Ahead, but could be luck |
| 1c fee: options price, reach / dip last hours (fresh) | 433 | -$5.90 | -$22.40 | Behind, but could be bad luck |
| 5c fee: copy GoodFallen 1 s late | 400 windows | -$0.08 | -$3.45 | Behind, but could be bad luck |
| 5c fee: copy GoodFallen 30 s late | 400 windows | +$0.23 | -$3.11 | Ahead, but could be luck |

The only thing worth a free re-check later is reach / dip without its long shots (so far about even).
