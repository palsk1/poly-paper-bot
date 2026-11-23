# Why the real Kalshi bot lost 3 of its first 133 bets (23 Nov)

Jan: "Another loss... it's as if the bot is too fast now." The real bot (`live/kalshi_live.py`, rule kc_maker_safe_usd,
$4 bids) lost HYPE twice on 22 Nov evening and DOGE on 23 Nov 09:16 Stockholm. Tool: `python3 kcrypto.py looks`
(history) and `python3 live/compare.py` (real vs paper). History = 126 days, 78,304 Kalshi 15-minute windows,
`bt_cache/kc` from the price store, "fair" fills.

## Real vs paper (22 Nov 16:40 to 23 Nov 09:46 Stockholm)
- 156 real bids, 133 filled, 3 lost: wins +$5.05, losses -$11.72, P&L -$6.68.
- On the 55 windows both bid on: real -$0.78 per $100, paper -$1.33. The real bot is not getting worse fills than paper.
- HYPE 16:15 (US time): paper kc_maker_safe_usd lost the same round. HYPE 16:30: paper kc_maker_safe and kc_maker lost it
  too; the usd twin had no bid. DOGE 03:15: no paper track bid on that window at all.
- The real bot checks every 15 s and bids the first moment a window passes; paper looks about once in 5 minutes.
  So the real bot catches more windows that only just pass: 41 in 100 of its fills had a cushion under 2.3
  (Kalshi scale), paper 18 in 100. All 3 real losses were under 2.3 (2.26, 2.15, 2.10).

## History: one look vs many looks, and the cushion
| What | Fills | Lost | Loses 1 in | Per $100 |
|---|---|---|---|---|
| one look, cushion 2-2.3 | 8,310 | 90 | 92 | +$0.44 |
| one look, cushion 3+ | 21,457 | 42 | 511 | +$0.49 |
| many looks (like the real bot) | 21,168 | 155 | 137 | +$0.55 |
| many looks, bar 2.5 instead of 2 | 16,007 | 74 | 216 | +$0.52 |
| many looks, bar 3.0 | 11,322 | 32 | 354 | +$0.50 |
| many looks, passed a minute earlier too | 12,912 | 49 | 264 | +$0.52 |
| many looks, bid 95-98c | 3,890 | 65 | 60 | +$1.35 |
| many looks, bid 99.5c+ | 5,787 | 19 | 305 | +$0.03 |

- Thin cushions DO lose more often (1 in 92 vs 1 in 511), but they are bought cheaper, so the money per $100 is the same.
  A stricter bar halves the losses and keeps the profit per $100, but makes about 1 in 4 fewer bets, so fewer dollars.
- Checking often is not a problem in history: many looks +$0.55 per $100, same as one look.
- Bids at 99.5c or more earn about nothing in history (+$0.03 per $100): same downside, almost no upside.

## Luck
- The real bot's way of looking loses 1 in 137 in history. 133 fills -> about 1 loss expected.
  3 or more: about 1 chance in 13. The two HYPE losses were the same crash 15 minutes apart, so really 2 separate events
  (2+ happens about 1 time in 4).
- At the real bot's prices (median 99.2c, a win pays about 4 cents on $4) it needs fewer than 1 loss in 100 fills to be
  ahead; history says 1 in 137. So the expected profit is small: about +$1 per 100 fills, and a loss about once a day
  (it fills ~200 a day) is normal.

## Verdict
Bad luck on top of a rule with a thin margin, not a speed bug. No change is backed by money in history. Options for Jan:
keep as is (recommended: the paper comparison stays clean), bar 2.5 (half the losses, about 1 in 4 fewer dollars),
or skip 99.5c+ bids (no profit there in history).
