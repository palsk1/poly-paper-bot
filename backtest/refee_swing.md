# Two dropped crypto-window digs, re-scored at Polymarket's new fees (27 Nov 2026)

Paper research only. Nothing live was changed.

**What changed:** on 20 Nov 23:59 UTC Polymarket cut the fee a hurried buyer or seller pays on crypto windows.
Fee = rate x shares x price x (1 - price). The rate was 0.07 everywhere. Now it is **0.05 on Bitcoin** 5- and
15-minute windows and **0.01 on ETH and SOL** windows. A waiting order (a "maker") still pays nothing, but its
reward is a share of the buyer's fee, so the reward shrinks too. Kalshi did not change.

Re-scored: `swing.py` (buy and sell inside one window, `backtest/swing.md`) and `maker5m.py` (be the seller on
Bitcoin 5-minute windows, `backtest/maker5m.md`). Same speed-box logs (17-26 Nov), same rules, same "pick on the
first days, check on fresh days" exam, same 12-second skip at the start of each window. Old and new fees were both
re-run on the same data, so the difference is only the fee. 27 Nov (first ~14 hours, never used to pick
anything) was kept back as an extra unseen check.

## Short answer

- **Buy-then-sell inside a window: still dropped.** It got cheaper, not good.
  - A round trip at middle prices now costs about **3.9c a share on Bitcoin** (was 4.8c) and **2.0c on ETH/SOL**
    (was about 4.9c). That 2c is mostly the gap between buyers and sellers now, not the fee.
  - Of **11,097** rules that really sell inside the window (Bitcoin 4,360, ETH 3,374, SOL 3,363), **13** were
    ahead both on the days they were picked and on fresh days (at the old fee, same data: 5). The middle rule on
    fresh days: Bitcoin -$8.33 per $100 (was -$9.42), ETH -$4.91 (was -$7.92), SOL -$6.04 (was -$9.39).
  - The 13 survivors then met 27 Nov, a day nobody had looked at: **11 of the 13 were behind or flat that day**: SOL's "buy a 20c+ dip in 5 s" family -$1.32 to -$8.70 per $100, ETH's +$0.83. The only two left
    ahead (Bitcoin "at 12 s into the window, ask 70-92c, sell at +10c", +$3.82 / +$4.47 on 28 bets) trade at
    the first second after the 12-second blind spot, which is exactly where the book log is least trustworthy.
  - Exam on the rule that was best on the first days (the honest pick): Bitcoin -$13.01 per $100, ETH -$4.04,
    SOL -$0.18. All three "Behind, but could be bad luck".
- **The speed signal got a little better, and holding still beats selling.** 1 s late, book fresh, 20+ shares on
  offer: hold to the end **+$7.63 per $100** on fresh days (old fee, same data: +$6.77), sell after 60 s +$4.33
  (was +$2.94). Half a second late +$12.18 (was +$11.30). Two seconds late -$0.20 (was -$0.99): still gone at 2 s.
  On unseen 27 Nov (1 s late, any offer): hold **+$14.57** per $100 on 107 bets, sell after 60 s +$1.35. Paper
  fills, same warning as before: the real bot's orders mostly got killed.
- **Seller on Bitcoin 5-minute: verdict does not change on the whole data, but something moved after the cut.**
  The reward drops from about +$0.60-0.78 to about **+$0.43-0.55 per $100**. Every version at a real speed
  (0.1 s or slower) is still behind over the whole 10 days. BUT the "only keep offers 4c+ on the safe side of
  Binance's fair price" family went from clearly losing before the cut to slightly ahead after it (see below).
  Worth a watch, not a bot.

## The four numbers (rough guesses)

| | Buy and sell back (any version) | Speed buy, hold to the end | Seller, 4c safe side, 0.1 s, after the cut |
|---|---|---|---|
| Most it makes in an average day | Nothing. Middle rule: a $5 bet loses about 42c on Bitcoin, 25-30c on ETH/SOL | Paper: about +$46 a day at 10 shares a bet, if orders filled 1 s late (they mostly don't) | Paper: about +$140 a day on ~$4,700 bought a day, before any proof; the 4 days before the cut lost about $240 a day on the same rule |
| Money needed | $5-10 a bet | $15-25 out at once | About $20-40 out at once (5-share offers) |
| Where it stops growing | Does not apply | About $25 a bet | 5-share offers at the back of the line; bigger offers change who fills |
| A bad day | 50 bets lose about $20 | Paper worst day -$5.21 | Two of the six post-cut days were behind (-$1 to -$3 per $100) |

## Buy and sell inside the window, by coin (fresh days)

| Coin | Fee rate | Rules that sell inside | Ahead on the first days | ...and on fresh days | Middle rule, fresh, per $100 | Same, at 0.07 |
|---|---|---|---|---|---|---|
| Bitcoin (first days 17-21 Nov, fresh 22-26 Nov) | 0.05 | 4,360 | 22 | 5 | -$8.33 | -$9.42 (12 ahead, 4 both) |
| ETH (25 / 26 Nov) | 0.01 | 3,374 | 119 | 1 | -$4.91 | -$7.92 (39 ahead, 0 both) |
| SOL (25 / 26 Nov) | 0.01 | 3,363 | 123 | 7 | -$6.04 | -$9.39 (40 ahead, 1 both) |

The same rule did on average $0.91 per $100 better on Bitcoin and $2.6 better on ETH/SOL. Since the rules lost
$5-9 per $100, that is not enough. ETH and SOL have only one first day and one fresh day each, so "ahead on both"
there is close to a coin flip on a few hundred bets.

**The 13 that stayed ahead, and what 27 Nov did to them** (per $100; bets in brackets):

| Coin | Rule | Way out | First days | Fresh days | 27 Nov (unseen) |
|---|---|---|---|---|---|
| ETH | price fell 20c+ in 5 s | sell at +10c, else hold | +$2.36 (54) | +$4.80 (259) | +$0.83 (127) |
| SOL | price fell 20c+ in 5 s | sell at +10c, else hold | +$2.09 (58) | +$4.11 (266) | -$4.18 (128) |
| SOL | price fell 20c+ in 5 s | sell after 30 s | +$0.06 | +$3.07 | -$1.32 |
| SOL | fell 20c+ in 15 s, coin calm | sell after 60 s | +$8.39 | +$2.48 | -$8.70 (164) |
| SOL | fell 20c+ in 5 s, coin calm | sell after 30 s | +$4.12 | +$1.78 | -$1.96 |
| SOL | price fell 20c+ in 5 s | sell after 60 s | +$9.43 | +$1.77 | -$4.85 |
| SOL | waiting bid at 88-97c, last 2 min | sell / offer at +5c, else hold (2 rules) | +$0.09 to +$0.17 | +$0.49 to +$0.50 | -$1.15 / -$1.27 |
| BTC | at 12 s, ask 70-92c | sell at +20c, else hold | +$2.82 (164) | +$4.11 (172) | -$10.71 (28) |
| BTC | at 12 s, ask 70-92c | sell / offer at +10c, else hold (2 rules) | +$1.73 to +$1.83 | +$2.20 to +$2.28 | +$3.82 / +$4.47 (28) |
| BTC | fell 20c+ in 30 s, coin calm | stop -10c, else hold / sell after 60 s (2 rules) | +$2.31 to +$4.16 (324) | +$1.43 to +$3.07 (419) | -$9.37 / -$11.05 (48) |

Nothing here is a lead. Buying a big fast dip on ETH/SOL is the most repeated idea, and it failed on SOL on 27 Nov.

## Speed signal (Bitcoin, coin's fair price +6c in 2 s, share moved under 3c; book fresh, 20+ shares)

| How late | Way out | Per $100 fresh days, new fee | Same at 0.07 | A day at 10 shares, new fee |
|---|---|---|---|---|
| 0.5 s | hold to the end | +$12.18 | +$11.30 | +$138.15 |
| 0.5 s | sell after 60 s | +$8.60 | +$7.18 | +$97.49 |
| 1 s | hold to the end | +$7.63 | +$6.77 | +$45.52 |
| 1 s | sell after 60 s | +$4.33 | +$2.94 | +$25.83 |
| 1 s | sell after 15 s | +$4.22 | +$2.65 | +$25.19 |
| 2 s | hold to the end | -$0.20 | -$0.99 | -$0.76 |
| 5 s | hold to the end | -$5.44 | -$6.22 | -$29.68 |

Exam (1 s late, any offer still there, fresh days, paper fills): hold to the end **"Looks real"**, +$12.86 per
$100, luck range +$8.96 to +$16.75 (26 Nov at 0.07: +$11.47); sell after 60 s also **"Looks real"** now, +$9.12
(26 Nov: +$7.44, "Promising"). The exam can't know that real orders get killed, so this changes nothing about the
real speed bot's problem (getting filled), only the size of the prize if it does.

## Being the seller on Bitcoin 5-minute (`maker5m.py`)

The seller pays no fee, so the fee cut only shrinks the reward: about **-$0.17 to -$0.23 per $100** everywhere
(e.g. plain 0.1 s: reward +$0.61 -> +$0.44). Over all 10 days, the verdict does not change:

| Rule (10 days, per $100 before the reward) | Instant | 0.1 s | 0.25 s | 0.5 s |
|---|---|---|---|---|
| Plain | -$0.62 | -$2.52 | -$3.46 | -$4.10 |
| Pull on a 2c Binance move | +$0.32 | -$1.46 | -$2.27 | -$3.25 |
| Only 4c+ on the safe side of fair | +$2.03 | -$0.77 | -$3.10 | -$4.79 |
| Reward at the new fee | +$0.43 to +$0.55 | same | same | same |

So at 0.1 s or slower, nothing is ahead even with the reward. **Plain and "pull" rules lose about the same
before and after the cut** (pull 2c at 0.1 s: -$1.74 before, -$1.30 after).

**What looks different:** the "only keep offers on the safe side of fair" rules, split at the cut (days before:
17-20 Nov; after: 21-26 Nov; split chosen after seeing the data). Skipping the first 12 s of each window:

| Safe-side rule, 0.1 s | Before the cut | After the cut | 27 Nov (unseen) |
|---|---|---|---|
| 0c | -$3.64 | +$0.50 | +$3.97 |
| 2c | -$5.33 | +$1.44 | +$4.73 |
| 4c | -$6.79 | +$2.45 | +$5.21 |
| 4c, at 0.25 s | -$8.93 | +$0.29 | +$4.73 |

(before the reward, per $100; the reward adds about +$0.55)

Exam, 4c rule at 0.1 s, reward included: 21-26 Nov **"Promising, needs more bets"**, +$3.00 per $100 on 1,688
windows, luck range +$0.52 to +$5.48, both halves ahead; 27 Nov alone "Ahead, but could be luck", +$5.75 on 158
windows, luck range -$1.93 to +$13.44. Reasons for doubt: the split was found by looking; 21 and 25 Nov carry
most of it (+$7.7 and +$9.9) while 22-24 and 26 Nov are about -$3 to +$1; fills are counted from the real trade
list with us at the back of the line, but our offer isn't in the real log. A possible reason it's real: cheaper
buyer fees bring more buyers who take offers near the fair price, not only fast traders sniping old offers (the
same rule bought about $4,700 a day after the cut against $3,500 before). **Suggestion:** no bot; re-run the split
on 28 Nov-4 Dec with the same rule (4c safe side, 0.1 s, skip first 12 s), fixed now before seeing those days.

## How it was run

- `SWING_FEES=new SWING_TAG=_new python3 swing.py grid btc|eth|sol`, then `speed`, then
  `SWING_EXAM_SETS=btc,eth,sol exams` (cache `SWING_CACHE=bt_cache/sw_refee`); old fee the same with
  `SWING_FEES=old`. The default is still 0.07, so `backtest/swing.md` can be rebuilt as it was.
- `MAKER5M_FEE=0.05 python3 maker5m.py grid <part> <parts>` (cache `MAKER5M_CACHE=bt_cache/mk5_refee`);
  `MAKER5M_FIRST=12` skips the first 12 s; `MAKER5M_FEE=actual` uses 0.07 before the cut and 0.05 after.
- 26 Nov's log in the release has more windows now than when `swing.md` was written (2,664 Bitcoin windows,
  was 2,616), so the 0.07 numbers here differ a little from that report.
