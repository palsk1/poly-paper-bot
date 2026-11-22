# Kalshi combos: can a small account be the house? (22 Nov 2026)

Research only. Public data, no key, no orders. Tool `kcombos.py`, data `kcb_cache/` in the price store.

## The short answer

**No. Dropped, no track.** Three reasons, any one of which would do:

1. **It needs a key and a fast machine.** A combo on Kalshi is priced by asking: the buyer builds a parlay, Kalshi sends the request out, and sellers answer through the API with a price for the whole size. The buyer then has 3 seconds to say yes and the seller 1 second to back out. Listening needs a logged-in API key (without one the request list answers "not allowed"), so we can't even run a listen-only paper house the way we did on Polymarket without Jan making a Kalshi key.
2. **It needs far more than $300.** The seller must cover the whole payout. The middle combo locks $142 of the seller's money for a $5.59 ticket; one in four locks $571 or more; one in twenty $3,633 or more. Only about one trade in five locks $30 or less.
3. **The sellers there don't earn anything worth copying.** Over 28 days and 94,537 real combo sales, the sellers ended at +$0.00 per $100 locked after their fee (luck range -$0.33 to +$0.33). On the two-week stretches: -$1.64 and -$1.59 per $100 of tickets. Kalshi charges the buyer about $4.64 and the seller about $2.32 per $100 of tickets, and that fee is the only steady winner. Our own Polymarket house rule (2-4 legs, legs multiplied + 5%) would have lost $1.33 per $100 locked here.

On Polymarket the pros kept about $31 of every $100 of tickets. On Kalshi the price is so tight there is nothing left to keep. So this is not a "for later, with more money" idea either: more money would only buy a bigger break-even.

**The backward look found one lead, and it failed its test.** Buyers of nearly-sure combos (65c and up) were ahead $13.80 per $100 in the first 12 days. We wrote the rule down before looking at new days (`backtest/kcombos_prereg.md`). On 14 fresh days it lost $5.31 per $100 (860 trades, "Behind, but could be bad luck"), and the small-ticket version lost $10.66 ("Losing"). Reading the first sample's wins one by one explains it: 8 big tickets (each $4,000 to $15,000) made $16,850 of the $24,260 profit. A few big bettors had a good fortnight. Dropped.

## How a Kalshi combo works (from the docs)

- A combo is its own little market (ticker `KXMVE...`), made the moment somebody asks for it. Kalshi sells about 1,600 different ones a minute.
- Any Kalshi member may answer requests, but only through the API (key needed), and for the full size asked.
- Fees on combos: the buyer pays the normal fee, and since 20 Aug 2026 the seller pays half of it too. On normal Kalshi markets the waiting side pays nothing.
- A combo is settled the moment one leg loses. Money on winning combos stays locked until the last leg: about 10 minutes for the 15-minute crypto ones, 4.5 hours (middle) for sports.

## The sample

28 days (23 Oct to 19 Nov 2026), 336 random moments. At each one we read every Kalshi trade of about half a minute (17,825 seconds in all, 3,254,568 trades), kept the combo trades, looked up each combo's legs, result and what each leg cost on its own that minute.

- Combos traded in those seconds: 474,068 different ones (we kept a random 99,475, 119,257 trades).
- That is about 1,596 different combos sold a minute, around the clock.
- Trades we could score (every leg due and settled): **107,392**. Left out: 11,508 a leg due after our cut-off (left out whatever the result); 357 due but not settled.
- In 94,537 of them the asker bought the combo (Yes). In 12,855 the asker took the other side.

## How big is one combo, and how much must the house put up?

The house buys the No side: for every $1 a combo can pay, it puts up $1 minus the buyer's price.

| | smallest quarter | middle | biggest quarter | biggest 1 in 20 |
|---|---|---|---|---|
| Buyer's ticket | $1.87 | $5.59 | $14.38 | $94.13 |
| House money locked | $35.66 | $142.01 | $571.21 | $3,632.72 |

A house must answer for the whole size asked. Trades a $300 bank could carry with at most $30 locked: 21,266 of 94,537.

## Who won: the house or the buyer?

Every scored trade, from the house's chair, after the house's fee. "Per $100 locked" is what a bank earns on the money it must put up. "Per $100 of tickets" is the house's cut of what buyers spent.

### By kind of combo (asker bought Yes)

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| crypto 15-min | 5,791 | $3.74 | $24.68 | 4,417 of 5,791 | -$0.08 | -$1.12 |
| mixed with crypto | 466 | $4.68 | $48.49 | 388 of 466 | $1.15 | $46.09 |
| sports and other | 88,280 | $6.38 | $156.80 | 77,841 of 88,280 | -$0.00 | -$0.08 |

### By the buyer's price

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| under 1c | 26,791 | $1.87 | $952.20 | 26,711 of 26,791 | $0.12 | $54.09 |
| 1-5c | 21,068 | $4.68 | $224.82 | 20,468 of 21,068 | -$0.56 | -$23.47 |
| 5-15c | 18,996 | $9.37 | $87.30 | 17,368 of 18,996 | $0.53 | $5.54 |
| 15-35c | 15,984 | $9.56 | $40.34 | 12,309 of 15,984 | $0.38 | $1.29 |
| 35-65c | 9,830 | $16.70 | $17.87 | 5,358 of 9,830 | -$2.16 | -$2.38 |
| 65-90c | 1,569 | $15.80 | $5.12 | 420 of 1,569 | -$40.14 | -$12.60 |
| 90c+ | 299 | $18.92 | $0.82 | 12 of 299 | -$55.92 | -$2.42 |

### By number of legs

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| 2 legs | 11,495 | $9.81 | $36.25 | 7,933 of 11,495 | -$1.07 | -$3.42 |
| 3 legs | 9,554 | $9.44 | $49.29 | 7,234 of 9,554 | $1.69 | $8.90 |
| 4 legs | 8,988 | $9.37 | $71.04 | 7,383 of 8,988 | $0.02 | $0.20 |
| 5 legs | 7,506 | $9.32 | $89.36 | 6,427 of 7,506 | -$0.85 | -$11.50 |
| 6 legs | 7,400 | $8.35 | $116.56 | 6,555 of 7,400 | -$0.60 | -$13.53 |
| 7 legs | 5,420 | $8.46 | $144.23 | 4,806 of 5,420 | -$2.18 | -$75.75 |
| 8+ legs | 44,174 | $4.58 | $356.78 | 42,308 of 44,174 | $0.19 | $22.94 |

### Legs from the same game or not (sports and other)

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| every leg a different game | 54,166 | $6.59 | $141.51 | 46,987 of 54,166 | -$0.16 | -$4.49 |
| two or more legs from one game | 34,114 | $5.64 | $189.84 | 30,854 of 34,114 | $0.25 | $10.57 |

### Small tickets only: house money locked

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| up to $5 | 5,875 | $0.95 | $1.98 | 3,723 of 5,875 | $2.97 | $2.34 |
| $5-30 | 15,391 | $4.71 | $15.25 | 11,548 of 15,391 | $0.30 | $0.58 |
| $30-300 | 39,239 | $9.09 | $101.75 | 34,452 of 39,239 | -$0.21 | -$1.30 |
| over $300 | 34,032 | $9.13 | $949.41 | 32,923 of 34,032 | $0.01 | $0.63 |

### When the asker took the other side (sold a combo back, or bought No)

| | trades | buyer's ticket (middle one) | house money locked (middle one) | house won | house profit per $100 locked | per $100 of tickets |
|---|---|---|---|---|---|---|
| crypto 15-min | 788 | $13.95 | $3.63 | 325 of 788 | $16.87 | $2.86 |
| mixed with crypto | 107 | $15.20 | $8.91 | 42 of 107 | -$15.56 | -$4.48 |
| sports and other | 11,960 | $83.18 | $10.26 | 3,618 of 11,960 | $9.39 | $1.46 |

## The price against the legs

For 56,251 Yes trades every leg had a price that minute. Legs multiplied is a fair price only when legs don't lean on each other (legs from one game do, and so do coins in the same 15 minutes).

| | trades | buyers paid | legs multiplied were worth | combo really paid back |
|---|---|---|---|---|
| every leg a different game, sports | 36,625 | $100 | $96.53 | $106.07 |
| same-game legs, sports | 13,460 | $100 | $85.03 | $88.44 |
| crypto 15-min | 5,791 | $100 | $82.59 | $99.58 |

## Our own house rule: legs multiplied plus a margin

The Polymarket rule (combos.py): 2-4 legs, no two legs from one game, price = legs multiplied + 5%, and we only get the trade when that is cheaper for the buyer than what the pro really charged.

| margin | trades we would have won | of how many asked | house profit per $100 locked | per $100 of tickets | house won |
|---|---|---|---|---|---|
| +2% | 9,010 | 16,280 | -$1.46 | -$8.91 | 7,138 of 9,010 |
| +5% | 3,919 | 16,280 | -$1.33 | -$14.27 | 3,286 of 3,919 |
| +10% | 2,077 | 16,280 | -$0.57 | -$9.43 | 1,784 of 2,077 |

## The backward look: who did win?

Same trades from the buyer's chair (price + the buyer's fee, $1 a contract if the combo wins). First the days we looked at first (06-17 Nov, 41,876 trades):

| buyer's price | trades | combos that won | buyer profit per $100 spent, after the fee | the same, every ticket counted alike |
|---|---|---|---|---|
| under 1c | 11,727 | 26 | -$67.95 | -$57.47 |
| 1-5c | 9,137 | 217 | -$10.99 | -$11.90 |
| 5-15c | 8,607 | 743 | -$3.11 | -$10.68 |
| 15-35c | 7,084 | 1,709 | -$2.65 | -$3.00 |
| 35-65c | 4,500 | 2,060 | -$3.30 | -$5.50 |
| 65-90c | 683 | 545 | $19.22 | $4.23 |
| 90c+ | 138 | 132 | $2.18 | $0.05 |

Long shots lose for buyers, as everywhere. The surprise is the top: buyers of nearly-sure combos (65c+) were ahead, $13.80 per $100 spent on 821 trades. Found by looking (about 30 cuts), so the rule was written down (`backtest/kcombos_prereg.md`) and tested on days it had never seen.

### The fresh days (23 Oct to 05 Nov, 14 days, 46,039 Yes trades)

| buyer's price | trades | combos that won | buyer profit per $100 spent, after the fee | the same, every ticket counted alike |
|---|---|---|---|---|
| under 1c | 13,330 | 52 | -$56.99 | -$3.03 |
| 1-5c | 10,551 | 365 | $38.41 | $10.07 |
| 5-15c | 9,166 | 803 | -$18.00 | -$11.31 |
| 15-35c | 7,638 | 1,713 | -$12.18 | -$10.52 |
| 35-65c | 4,494 | 2,041 | $0.77 | -$6.09 |
| 65-90c | 750 | 498 | -$7.35 | -$12.27 |
| 90c+ | 110 | 104 | $0.65 | -$0.47 |

| test (fixed before the download) | trades | result per $100 | first sample |
|---|---|---|---|
| 1. Buyers at 65c+, dollars as they were | 860 | -$5.31 | $13.80 |
| 2. Buyers at 65c+, tickets up to $50, every ticket alike | 604 | -$10.66 | $2.08 |
| 3. House side, all Yes trades, per $100 of tickets | 46,039 | -$1.59 | -$1.64 |

The two newest days (18-19 Nov) are kept apart: we had glanced at them before the rule was written down, so they are not a fair test. There: 187 trades at 65c+, $16.12 per $100; small tickets counted alike $2.02; house side $20.58 per $100 of tickets.

```

=== EXAM: Kalshi combos: buy nearly-sure combos (65c+), fresh days ===
Verdict: Behind, but could be bad luck
Bets: 860 bets on 160 events over 14 days. Counted as 160 separate bets (bets on the same event count once).
Result: -$5.31 per $100 bet (total -$5219.88 on $98259.14). Luck range -$13.18 to +$2.55.
Halves: first +$0.24, second -$11.02 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 2 tries. The luckiest of 2 worthless ideas would show about +$8.59 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$16.17. Below $0: not proven.


=== EXAM: Kalshi combos: buy nearly-sure combos (65c+), small tickets, fresh days ===
Verdict: Losing
Bets: 604 bets on 146 events over 14 days. Counted as 146 separate bets (bets on the same event count once).
Result: -$10.66 per $100 bet (total -$64.38 on $604.00). Luck range -$19.05 to -$2.27.
Halves: first -$9.34, second -$12.01 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 2 tries. The luckiest of 2 worthless ideas would show about +$8.91 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$21.88. Below $0: not proven.

```

## How long is the money locked?

| kind | middle | longest quarter from |
|---|---|---|
| crypto 15-min | 10 min | 13 min |
| sports and other | 4.5 hours | 9.9 hours |
| mixed with crypto | 14 min | 83 min |

## The shared exam

```

=== EXAM: Kalshi combo house: every Yes trade the pros sold ===
Verdict: Ahead, but could be luck
Bets: 94537 bets on 332 events over 28 days. Counted as 28 separate bets (losses came in bunches on the same days, so one day counts once).
Result: +$0.00 per $100 bet (total +$1942.97 on $83927856.17). Luck range -$0.33 to +$0.33.
Halves: first -$0.05, second +$0.06 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 181 tries. The luckiest of 181 worthless ideas would show about +$11.31 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$14.77. Below $0: not proven.
To prove it: can't say. It isn't ahead once one more disaster is added.


=== EXAM: Kalshi combo house: sports, every leg a different game ===
Verdict: Behind, but could be bad luck
Bets: 54166 bets on 332 events over 28 days. Counted as 332 separate bets (bets on the same event count once).
Result: -$0.16 per $100 bet (total -$80934.88 on $49979687.71). Luck range -$0.54 to +$0.22.
Halves: first -$0.18, second -$0.14 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 182 tries. The luckiest of 182 worthless ideas would show about +$1.14 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$1.56. Below $0: not proven.


=== EXAM: Kalshi combo house: crypto 15-min combos ===
Verdict: Behind, but could be bad luck
Bets: 5791 bets on 325 events over 28 days. Counted as 325 separate bets (bets on the same event count once).
Result: -$0.08 per $100 bet (total -$1163.16 on $1416847.52). Luck range -$0.67 to +$0.50.
Halves: first -$0.25, second +$0.00 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 183 tries. The luckiest of 183 worthless ideas would show about +$1.28 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$1.52. Below $0: not proven.


=== EXAM: Kalshi combo house: our rule, legs x 1.05, 2-4 legs ===
Verdict: Behind, but could be bad luck
Bets: 3919 bets on 331 events over 28 days. Counted as 331 separate bets (bets on the same event count once).
Result: -$1.33 per $100 bet (total -$26972.53 on $2025083.35). Luck range -$3.01 to +$0.35.
Halves: first -$1.64, second -$1.06 per $100. Not ahead in both: could be one good stretch.
Luck bar: this is 1 of 184 tries. The luckiest of 184 worthless ideas would show about +$3.62 per $100 on this many bets.
Worst case per $100 (one more disaster added, bar raised for all tries): -$5.39. Below $0: not proven.

```

## Traps for the next dig

- Kalshi's whole trade list (`/markets/trades` with `min_ts` / `max_ts`) is fast: 12,000 trades in 2 seconds. The slow part is prices per leg: use the batch endpoint `/markets/candlesticks?market_tickers=` (100 markets a call), not one call per leg.
- A combo settles early at $0 when a leg loses, so "only settled combos" keeps the losers and drops the open winners. Cut by each leg's planned end time instead, whatever the result.
- "Legs multiplied" is a fair price only for legs that don't lean on each other. Same-game legs and coins in the same 15 minutes do.
- `taker_side` is the asker's side. The house is the other one.
- Days 18-19 Nov were glanced at before the rule was written down, so they are shown apart and not counted as a test.
