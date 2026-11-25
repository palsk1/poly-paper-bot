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


## Second score: a fresh week (25 Nov 2026)

Days the first cut never saw: 19-25 Nov (to 08:00 UTC), 1,820 Bitcoin 5-minute windows. Same rule, same 40-95c band, nothing changed. Command: `python3 quoter/speedcheck.py edge speed-202611{19..25}.jsonl.gz`.

| Price heard first from | 0 ms | 100 ms | 200 ms | 500 ms | 1 s |
|---|---|---|---|---|---|
| Binance | +3.20 | **+2.90** (range +1.8 to +4.1) | +2.24 | +0.23 | -1.24 |
| Coinbase | +2.69 | +2.03 | +1.35 | -0.11 | -1.62 |

Per $100 bought, after fees. Binance at 100 ms: 28,907 jumps, $547,915 bought on paper, +$15,899.

- **It held up.** About half the first day's number, but the whole luck range stays above $0, and it fades with delay exactly as before. Exam-style verdict: "Promising, needs more bets" on paper.
- **Still paper fills.** The test assumes we get every offer we saw, up to $25. Faster firms take some first, and our own view is ~30 ms old. Only real orders can measure that.
- **Ceiling (rough guess, paper):** at $25 a jump the paper says ~$2,500 a day, which is surely far above what real fills allow. Money needed: a few hundred dollars (bets end within 5 minutes). Size where it stops growing: unknown until real orders; the offers at the old price are usually small. Bad day: unknown; a speed race can turn negative the day a faster bot arrives.
- **Next (Jan decides):** keep the box past its 25 Nov delete date and run a tiny real test ($1-2 orders, a few days) side by side with paper.
