# Speed check on Jan's Stockholm box: first score (18 Nov 2026)

Box "speedcheck" (Lightsail Stockholm, $12, listen only: `quoter/speedcheck.py`). It has run since 17 Nov 14:55 UTC. Logs are in the release `speed-data`. This score covers 20.4 hours and 239 Bitcoin 5-minute windows with results.

## Connection
- Round trip to Polymarket's order server: median 60-72 ms, so about 30-36 ms one way.
- Round trip to Binance `/time`: about 260 ms.
- Polymarket's market feed dropped 13 times in 20 h ("slow consumer"). Each drop lasted a few seconds and reconnected by itself. CPU runs at about 8-10%, under the 20% baseline.

## The question
After the box hears Bitcoin jump (a side's fair price moves 3c+ within 2 s), are Polymarket's sell offers on the side Bitcoin jumped toward still at the old price, and does buying them pay?

- Fair price: Phi(ln(S/S0) / (sigma sqrt(t left))), with sigma from the last 15 minutes.
- Purchase: the best ask the box saw `d` ms after hearing the jump, up to $25.
- Costs: taker fee 0.07 x p x (1-p), no rebate.
- Held to Polymarket's result.
- Luck range: resampling whole windows.
- Command: `python3 quoter/speedcheck.py edge speed-*.jsonl.gz`.

| Price heard first from | 0 ms | 100 ms | 200 ms | 500 ms | 1 s |
|---|---|---|---|---|---|
| Binance, asks 40-95c | +6.02 | **+5.31** (range +2.3 to +8.3) | +3.96 | +1.40 | -0.42 |
| Coinbase, asks 40-95c | +4.58 | +3.87 | +3.36 | +1.00 | -0.21 |
| Chainlink, all asks 5-95c | -0.32 | -0.35 | -0.44 | -0.53 | -0.64 |

Per $100 bought, after fees. Binance at 100 ms: 3,056 jumps, $56,565 bought, +$3,003. Both halves of the day are ahead (+5.1 / +5.6), and it is still +$1,829 without its 10 best windows.

## Reading it
- **What's in favour.** The profit fades smoothly as we get slower, and is gone by about 1 s. That is what a real speed edge looks like. It matches GoodFallen's fills, which made +$21 per $100 right after a Bitcoin move his way (`backtest/wallet5m.md`). Chainlink, the slow settle price, shows nothing, as it should.
- **Found by looking.** Asks under 40c were lumpy: 10 lucky long shots made the whole profit at 5-95c, and the 5-40c band lost. The 40-95c band was chosen after seeing that. The model's "1c+ under fair" filter does worse than buying every jump, because the model is overconfident near 0c and 100c.
- **Paper fills.** We assume we'd get the offer we saw. Our view of the book is itself about 30 ms old, and faster firms would take some of these offers first.
- **One day.** That's 239 windows, and jumps inside one window move together.

Next: score again after a full week, on days this cut never saw. Kalshi and other coins come after that (scout #3).

## Week score: 19-24 Nov, days the first cut never saw (scored 25 Nov)
Same rule, same band (asks 40-95c), same $25 cap, nothing re-tuned. 1,723 windows over 6 days.

| Price heard first from | 0 ms | 100 ms | 200 ms | 500 ms | 1 s |
|---|---|---|---|---|---|
| Binance, asks 40-95c | +3.05 | **+2.73** (range +1.5 to +3.9) | +2.09 | +0.00 | -1.38 |
| Coinbase, asks 40-95c (100 ms) | | +2.06 | | | |

Per $100 bought, after fees. Binance at 100 ms: $517,567 bought on paper, +$14,128.

- **Exam** (`exam.score`, one bet per window): **"Looks real"**, the first idea in the ledger to get it. +$2.73 per $100, luck range +$1.60 to +$3.86, both halves ahead (+$2.35 / +$3.12), worst case per $100 +$0.28.
- **Smaller than the first day:** about half of the +$5.31. It still fades the same way with delay, and is gone at half a second.
- **Every day ahead:** 19 Nov +2.67, 20 Nov +2.70, 21 Nov +1.71, 22 Nov +7.45, 23 Nov +1.83, 24 Nov +1.04. Without its 20 best windows: still +$10,997.
- **Biggest wins are ordinary:** full $25 buys at about 40c that won (+$36 each). No odd prices or broken trades. Worst windows: -$537 and -$471.
- **By price, at 100 ms:** 5-40c +$12.10 per $100 (12,063 jumps, +$22,392), 40-60c +$3.77, 60-80c +$2.62, 80-95c +$1.33. The cheap band that the first day threw out did best on the new days. Its profits are lumpy, but it was not just one lucky day.
- **Who hears first:** 39,509 jumps heard by both Binance and Coinbase. Coinbase was first 22,666 times and Binance 16,679 times; the median gap was only 17 ms. Binance still made more money. Its jumps are cleaner because it trades more.
- **Feed drops:** Polymarket's market feed dropped 9-15 times a day, each time for a few seconds. Coinbase dropped 0-5 times a day, Chainlink 0-4, and Binance twice in the week. None of this changes the result.

### What this does not tell us
- **Paper fills.** We assume we got the offer we saw. Our view of the book is about 30 ms old, and faster firms take some of these offers first. Only a tiny real test can measure that.
- **Size.** Most jumps had only $5-25 on offer. A day's $86k bought on paper is spread over thousands of jumps of a few dollars each.
- **Real money** would need a Polymarket key on Jan's server, and Claude never handles keys. Whether Kalshi may be used from Sweden is Jan's check before any real money there.

## Second test (built 25 Nov, Jan 19 Nov: "remember to do that in the next test")
The same box, still listen only (no key, no login, no order code; the selftest refuses `/portfolio` and Kalshi's key header). It adds:
1. **Faster Bitcoin sources:** Bitstamp, Kraken and Binance futures (`bs`, `kr`, `bf`). `speedcheck.py lead` shows which one hears a jump first, and `edge` scores each one the same way.
2. **Kalshi 15-minute crypto** (the kc_maker coins: BTC, ETH, SOL, XRP, DOGE, HYPE, BNB):
   - The box reads the top of the book every second in each window's last 7 minutes, and every 10 s before that, and logs each read's round trip.
   - Just after each close it saves the whole trade list and the result.
   - It also adds Binance prices for the other six coins.
   - `speedcheck.py kcancel` asks: if a fast box pulled a kc_maker_safe-style bid when Binance turned, how many losing fills would it dodge, and how many winning fills would it give up?
3. **Polymarket ETH and SOL 5-minute windows**, next to Bitcoin (`edge eth ...`, `edge sol ...`).

Score after a week (about 2 Dec): `lead`, `edge`, `edge eth`, `edge sol`, `kcancel`. If the box's CPU sits above 20% for long, turn off the extras with `SPEED_POLY_COINS=btc` and `SPEED_KALSHI=0` in `~/.quoter.env`.
