# Speed check re-scored at Polymarket's new fees (27 Nov 2026)

On 20 Nov 23:59 UTC Polymarket cut its crypto taker fee. Fee = rate x shares x p x (1-p). The rate was 0.07. It is
now 0.05 on the Bitcoin 5- and 15-minute windows and 0.01 on other crypto (ETH and SOL 5-minute windows included).
Our scoring still used 0.07. This page re-scores the speed check at the new rates.

## 1. What the real bot really paid: 0.05
The real speed bot (`pspeed-live`) logs its cash balance every 10 minutes (release `live-data`, `pspeed-202611`).
There were 11 stretches where the balance only moved because of its own Bitcoin buys: no claims and no soccer bets
in between (26-27 Nov, 15 fills). In each one, the drop minus the money spent on shares is the fee.

- Fees paid: **$0.72** in total. At 0.07 it would have been $1.01. At 0.05 it is $0.72.
- Rate that fits: **0.050** (each stretch 0.045-0.054; the balance is rounded to the cent, so about 0.046-0.054).
- Example: 5 shares at 64c cost $3.20, and the balance fell $3.26. A 6c fee. The 0.07 rate says 8c.
- The shares were not cut: every winner claimed back its full share count. The fee comes out of cash.

So 0.05 is right for the Bitcoin 5-minute windows. The bot's own record still uses 0.07 (`FEE` in
`live/pspeed_live.py`, not touched here). That makes its 19 real bets look $0.39 worse than they were: -$14.66,
not -$15.04.

**Not checked:** the 0.01 rate on ETH/SOL. The real bot buys only Bitcoin, so we have no ETH or SOL fills.

## 2. The rule (same as the 25 Nov week score)
- After the box hears a Binance jump (a side's fair price moves 3c+ in 2 s), buy that side at the best offer seen
  100 ms later.
- Up to $25 a jump, offers 40-95c only, held to the result.
- Paper fills. One bet per 5-minute window for the exam.
- **New:** jumps in a window's first 12 s are skipped. The book feed was nearly blind there until the 27 Nov 08:45
  UTC feed fix (`swing.FIRST`). The 25 Nov week score did not skip them.

Check: with no skip and the 0.07 fee, the 19-24 Nov days give +$2.75 per $100 (the week score said +$2.73).

Command: `python3 quoter/speedcheck.py edge --fee 0.05 --skip-first 12 speed-*.jsonl.gz`. Or set
`SPEED_FEE=0.05`. The default is still 0.07.

## 3. Bitcoin 5-minute: before and after the cut
Per $100 bought, after the fee:

| Days | fee | 0 ms | **100 ms** | 200 ms | 500 ms | 1 s |
|---|---|---|---|---|---|---|
| 19-20 Nov (before the cut, 576 windows) | 0.07 (real then) | +2.55 | **+2.55** | +1.87 | -0.69 | -1.65 |
| 19-20 Nov | 0.05 | +3.19 | +3.18 | +2.49 | -0.08 | -1.04 |
| 21-27 Nov (after the cut, 1,882 windows) | 0.07 | +2.80 | +2.24 | +1.66 | +0.11 | -1.94 |
| 21-27 Nov | **0.05 (real now)** | +3.47 | **+2.89** | +2.30 | +0.74 | -1.33 |

**Main result (21-27 Nov, 0.05, 100 ms):** $497,733 bought on paper, +$14,400, **+$2.89 per $100**. Luck range +$1.78
to +$4.00. Both halves ahead (+$3.74 / +$2.08). Exam: **"Looks real"**, worst case per $100 +$0.50.

- **The cut is worth about +$0.65 per $100.** At the same prices, 0.05 instead of 0.07 adds $0.63-0.69 per $100 at
  every delay.
- **Did sellers take the cut back by raising their prices?** No clear sign. At the old 0.07 fee, the after days make
  +$2.24 and the before days +$2.55. That gap is well inside luck (the before range is +$0.56 to +$4.57). Offers
  did not move further above our fair price after the cut either.
- **Day by day (100 ms, 0.05):**
  - 21 Nov +2.07
  - 22 Nov +8.63
  - 23 Nov +1.35
  - 24 Nov +1.67
  - 25 Nov +2.53
  - 26 Nov +4.60
  - 27 Nov -0.98 (only until 13:44 UTC)
- Without 22 Nov it is +$2.06. Without the 20 best windows it is +$2.28, so it doesn't rest on a few windows.
- **Speed still decides it.** At 0.05: 500 ms late is +$0.74 ("Ahead, but could be luck"). 1 s late is -$1.33
  ("Losing"). The cheaper fee does not save a slow bot.
- **Paying more per share kills it.** At 0.05, paying 1c more a share leaves +$1.33 per $100, and 2c more leaves
  -$0.19. The real bot may pay up to 1c more (`PSPEED_EXTRA_C`), so its paper lead is about $1.33, not $2.89.
- **The fee-cut days don't help much yet.** 21-27 Nov at the new fee scores higher than the 0.07 week score, but
  the first 12 s are now skipped. The jumps in those seconds used to look extra good, and the 0.05 fee only adds
  back about what dropping them took away.

## 4. ETH and SOL 5-minute (logged since 25 Nov, 2.6 days, 526-527 windows)
Same rule and band, prices from Binance ETH / SOL spot. Per $100:

| | fee | 0 ms | **100 ms** | 200 ms | 500 ms | 1 s |
|---|---|---|---|---|---|---|
| ETH | 0.07 | +1.20 | -0.10 | -0.74 | -1.21 | -2.08 |
| ETH | **0.01** | +3.07 | **+1.72** | +1.07 | +0.58 | -0.29 |
| SOL | 0.07 | -1.11 | -1.09 | -1.98 | -2.79 | -2.43 |
| SOL | **0.01** | +0.66 | **+0.68** | -0.22 | -1.06 | -0.70 |

- **ETH at 0.01, 100 ms:** $125,172 bought, +$2,157, +$1.72 per $100. Range -$0.16 to +$3.61. Exam: **"Ahead, but
  could be luck"**.
- **SOL at 0.01, 100 ms:** +$0.68 per $100. Exam: **"Ahead, but could be luck"**. 26 Nov lost (-$0.64), and it fades
  fast with delay.
- The cheap fee is the whole story on these coins: at 0.07 both are about $0 or behind. The 0.01 rate is Polymarket's
  stated rate, not yet seen on a real fill.
- ETH and SOL offers die faster than Bitcoin's. The median old ETH offer was gone 150 ms after we heard the jump,
  SOL 338 ms, Bitcoin 359 ms.

## 5. The first 12 seconds after the feed fix
Only about 5 hours of fixed recordings (27 Nov 08:45-13:44 UTC): 45-54 windows a coin with a jump in seconds 0-11.
Bitcoin -$0.28, ETH +$11.94, SOL -$10.19 per $100 on about $1,500 each. Far too few to say anything. Score again in
a few days.

## Rough ceiling (Bitcoin, 100 ms, 0.05, paper)
- **Paper total:** about +$2,000 a day on about $70,000 bought a day at $25 a jump. That isn't reachable: the real
  bot got 1 fill in 10 on its first day, and most offers are $5-25.
- **Real bot size:** at $2-5 bets and about 50 bets a day (about $175 bought), about +$2-5 a day if the paper lead held ($1.33-2.89 per $100). It hasn't so
  far: the 19 real bets lost $14.66 (rough guess).
- **Money needed:** about $15-20 out at once.
- **Bad day:** -$5 (the bot's day cap).

## Exam cards (scratch ledger, tries = 12 each)
| Test | Bets (windows) | Per $100 | Worst case | Verdict |
|---|---|---|---|---|
| BTC, 0.05, 100 ms, 21-27 Nov | 1,882 | +2.89 | +0.50 | Looks real |
| BTC, 0.07, 100 ms, 21-27 Nov | 1,882 | +2.24 | -0.14 | Promising, needs more bets |
| BTC, 0.07, 100 ms, 19-20 Nov | 576 | +2.55 | -1.91 | Promising, needs more bets |
| BTC, 0.05, 500 ms, 21-27 Nov | 1,882 | +0.74 | -1.58 | Ahead, but could be luck |
| BTC, 0.05, 1 s, 21-27 Nov | 1,882 | -1.33 | -3.47 | Losing |
| ETH, 0.01, 100 ms, 25-27 Nov | 526 | +1.72 | -2.55 | Ahead, but could be luck |
| ETH, 0.07, 100 ms, 25-27 Nov | 526 | -0.10 | -4.32 | Behind, but could be bad luck |
| SOL, 0.01, 100 ms, 25-27 Nov | 527 | +0.68 | -3.73 | Ahead, but could be luck |

All are paper fills at the offer the box saw. The real bot's 1-in-10 fill rate says paper is too kind.
