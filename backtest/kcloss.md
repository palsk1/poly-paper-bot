# Why kc_maker_safe lost 3 bets (12 Nov 2026, Jan's ask)

Jan: "Check why we lost and if we can avoid in future." Research only, paper only. The kc_maker_safe rules were NOT
changed: its test is locked (PROTOCOL 5b, 2,500 bets around 1 Dec, pass above +$0.22 per $100).

Code: `kcrypto.py losses` (live trade list + Binance seconds for every bet, probe `kc_losses`, run 43254972940),
`kcrypto.py basis` (Binance vs Kalshi gap for every live bet, probe `kc_basis`, run 43256513384),
`kcrypto.py gapcheck` (the same check on 60 days of history, offline on the shared price store).

## In plain words

- **3 losses in 362 bets is normal.** One win pays about 11c on a $10 bet. One loss costs about $9.70. So one loss
  eats about 90 wins, and the bot breaks even at about 1 loss per 90 bets. Live it is 1 per 120, the 60-day
  history was 1 per 160. So it's still ahead (+$9.77), and 3 losses is about what history says to expect (2-3).
- **The fills were real.** In all 3, Kalshi's trade list shows sellers selling below our price right after we bid
  (hundreds of thousands of contracts in the next minute). We would have been filled even with a $100 bid.
- **The shared pattern: Binance's price runs a bit high.** Kalshi pays out on a US-dollar price (CF Benchmarks).
  The bot's safety check uses Binance, which quotes in USDT, a dollar stand-in that trades slightly above $1.
  Over 60 days Binance sat about 0.09% above Kalshi's price (about $65 on bitcoin), and 0.11-0.17% at our 3 losses.
  So when the coin is ABOVE the line (a "yes" bet), Binance makes the cushion look bigger than it is.
  All 3 losses were "yes" bets. With the gap taken out, their cushions were 0.95, 1.32 and 1.72 "typical moves",
  not 3.47, 2.35 and 2.53, so the "2 typical moves" check would have skipped all three.
- **But it's not free money.** Kalshi's own price already knows about the gap: those bets are cheaper. In 60 days of
  history the bets the fix throws away lost more often (1 in 64) but still made money (+$0.66 per $100).
  The fix cuts the losses by more than half and keeps the profit per $100 about the same, but makes fewer bets, so less profit in total.

## The 3 losses

| | BTC, 10 Nov | ETH, 11 Nov | BTC, 12 Nov (Jan's) |
|---|---|---|---|
| Window (Stockholm) | 08:45-09:00 | 23:15-23:30 | 15:30-15:45 |
| Bid placed | 3 min 16 s before the end | 4 min 52 s before | 2 min 35 s before |
| Our price | 97.7c, back of a line of 3,382 | 95.0c, back of a line of 0.2 | 97.8c, back of a line of 3,769 |
| Filled | 21 s after placing | 2 s after | under 1 s after |
| Cushion the bot saw (Binance) | 3.47 typical moves | 2.35 | 2.53 |
| Cushion on Kalshi's scale | 0.95 | 1.32 | 1.72 |
| Binance above Kalshi's price at the start of the window | 0.17% | 0.12% | 0.15% |
| Line / final price (avg of last minute) | $74,772.61 / $74,759.67 (missed by $13) | $2,070.42 / $2,069.29 (missed by $1.13) | $71,715.05 / $71,604.44 (missed by $110) |
| Binance in the last minute | about $74,850-74,890: by Binance we'd have won | about $2,071-2,072: by Binance we'd have won | about $71,610-71,830 |

What happened, in plain words:
- **10 Nov BTC:** Kalshi's price had been 80-90c for minutes and jumped to 98c for about 20 seconds right when the bot
  looked. Bitcoin then drifted down and settled $13 under the line. Binance never went under the line. The gap decided it.
- **11 Nov ETH:** ether slid from about $2,076 to $2,069 in the last 2 minutes and settled $1.13 under the line.
  Binance stayed just above. The gap decided it again.
- **12 Nov BTC (the one on Jan's screen):** this window was 09:30-09:45 in New York, the first 15 minutes of US stock
  trading, and bitcoin moved fast (2.5 times the 10 Nov speed). It fell about $190 in the 30 seconds around our bid
  (from about $72,150 to $71,960) and a wave of sellers (110,000 contracts in 10 seconds) filled us at once.
  It kept falling to about $71,600. This one was a real drop, not only the gap, but the gap made the cushion look
  50% bigger than it was.

Other things checked, no clear pattern: time left (2.6 to 4.9 min), the coin (2 BTC, 1 ETH), the hour, how fast we
were filled (wins were often filled within seconds too: 75 of 241 "back of the line" bets filled within 2 seconds,
2 of them lost).

One more lean, not the main finding: all 3 losses were bids at the BACK of the line (no room to step in front).
Live: front of the line 121 won / 0 lost, back of the line 238 / 3. History: front +$0.92 per $100 (1 loss per 214),
back +$0.32 (1 per 135). Back-of-the-line bets still made money in history, so this is not a reason to skip them.

## The fix, tested

"Both checks": keep today's rule, and also skip a bid unless the coin is 2+ typical moves past the line after moving
Binance onto Kalshi's scale (Binance at the window's start divided by the line = the gap, known before we bid).

Live bets so far (362): the fix keeps 253 (253 won, 0 lost, +$14.51) and skips 109 (106 won, 3 lost, -$4.73).
That looks great, but it is hindsight: I found the fix by looking at these 3 losses.

60 days of history (not used to find it), bid with 3 minutes left, $10 bets:

| | Bets | Lost | 1 loss per | P&L per $100 | Total on $10 bets | Worst day | Worst fall | Losing days |
|---|---|---|---|---|---|---|---|---|
| Today's rule | 8,655 | 54 | 160 bets | +$0.57 | +$497 | -$22.14 | -$31.84 | 12 of 61 |
| Both checks | 6,470 | 20 | 324 bets | +$0.54 | +$352 | -$10.74 | -$24.30 | 8 of 61 |
| Bets the fix throws away | 2,185 | 34 | 64 bets | +$0.66 | +$145 | | | |

At 2 minutes left: +$0.40 → +$0.36 per $100. At 4 minutes left: +$0.62 → +$0.62. The exam (`exam.py`, 8 tries):
"Looks real" on history, both halves ahead. That is the same history today's rule
passed too, and live bets are the real test.

**So:** the fix doesn't make more money per $100. It makes the ride smoother: less than half the losses, worst day about
$11 instead of $22, about 106 bets a day instead of 142, and about $2.40 a day less in total on $10 bets.
For a small real pot, smoother is worth something. It's Jan's call.

(Numbers use Binance at the window's start and one minute before, the same minutes the live twin reads.)

## Recommendation

- Don't touch `kc_maker_safe`: its locked test is the only live proof we can get by 1 Jan.
- Jan said yes (12 Nov): twin track `kc_maker_safe_usd` ($100 paper, rule `usd_gap` in config) runs both checks next
  to kc_maker_safe on the same windows. It needs no new data (the line itself is Kalshi's price at the start).
- The fill model, the payouts and the bot's own z numbers all checked out (the bot's z matched a fresh recompute
  within about 0.2). This is a blind spot in the rule, not a code bug.
