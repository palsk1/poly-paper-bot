# The "GoodFallen" Bitcoin 5-minute wallet (17 Nov 2026)

Jan shared a Reddit post (r/PredictionsMarkets): wallet GoodFallen `0x0ca4e9d27ff826a109ecbf74754fb66b93f277a6`
"made $253,026 in 4 months trading only Bitcoin Up or Down" 5-minute markets, "buys at 38-52c, holds to the end".
Tool: `wallet5m.py` (probe `w5m_fetch`, offline `python3 wallet5m.py run` after `store.py pull bt_cache`).
Raw output: `backtest/wallet5m_raw.txt`. Data: `bt_cache/w5m/` in the shared price store.

## Verdict: the profit is mostly Polymarket's fee rebates. Can't be copied. Dropped, no track.

## What the wallet really does
- A bot, around the clock, in nearly every Bitcoin 5-minute window (about 270 of 288 a day), from the first second
  to the last 30 seconds. Tiny pieces: median $8 a fill, about 10,500 fills a day.
- It buys **both** Up and Down in 4,703 of 4,856 windows. 83 in 100 shares it buys are matched pairs (1 Up + 1 Down
  pays $1 whatever happens). A pair cost it 98c in the median window, so the lock-in is about 2c a pair.
- About a third of its dollars are waiting orders (maker, no fee), two thirds grab sell offers (taker, pays the fee).
- The Reddit post's "typical trade $1,054 -> $2,570" is the winning half of a pair. The losing half of the same
  window is left out. It is not a "buy at 40c and hold" bettor.

## Money, 30 Oct to 17 Nov (every fill, from the activity list; 18 days)
| | Bought | Before fees | Fees | After fees |
|---|---|---|---|---|
| Waiting orders (maker) | $563,443 | +$8,303 (+$1.47 per $100) | $5 | +$8,298 |
| Grabbing sell offers (taker) | $976,309 | +$24,930 (+$2.55 per $100) | $29,134 | -$4,204 (-$0.43 per $100) |
| All | $1,539,751 | +$33,234 | $29,139 | **+$4,095 (+$0.27 per $100)** |

Polymarket then paid it **$17,596 in rebates** in the same days: a daily "taker rebate" of about half the fees it
paid the day before ($14,345) and a daily maker rebate ($3,251). So of about $21,900 profit in 18 days
(~$1,200 a day, +$1.41 per $100), about 4 in 5 dollars are Polymarket's rebate program, which can change any day.
Its own profile in the screenshot agrees: "Total PnL $257K" is before $173K of fees; "1Y realized $83.9K" is after.

Exam (its own windows, counted by day because results bunch by day): with rebates +$1.41 per $100, luck range
+$0.58 to +$2.24, "Ahead, but could be luck"; without rebates +$0.26, range -$0.56 to +$1.08. Daily after-fee
results swing from -$3,752 to +$4,690.

## Timing vs Bitcoin's price (Binance 1-second, simple fair price from the move so far)
On average it pays 1.5c a share under that fair price. Buys on the side that is already ahead made +$3.48 per $100
after fees; buys on the trailing side lost $4.71. Nothing special about any minute of the window.

## Copying it
The public trade list (`/v2/trades?user=`) only shows its taker fills; waiting-order fills are only in
`/v2/activity` (a fill whose transaction is not in the trade list was a waiting order; trade-list fills carry the
fee in `usdc_size`). A copier can't get waiting-order prices: copying each fill 1, 3, 10, 30 or 60 s late at the
next real sell offer + fee, on its 400 newest windows: **-$0.44 to -$1.08 per $100** (the wallet itself lost $0.61
there before rebates). Copying is a loser.

## Rebuilding it
The only part that pays is the waiting-order pair bot: bids on both sides so the pair costs under $1. That is a
queue race with pro bots, needs an always-on server, and Polymarket's trade list doesn't say whose order waited, so
a paper version can't be scored honestly (same wall as `pm15`, and our 5 Polymarket maker tracks lost $416). Most
of the profit is the rebate, which a small newcomer wouldn't earn at that size. Don't redo unless Polymarket
publishes order-book history or Jan wants a real-money queue test.

## Running his system ourselves on a fast server? (17 Nov, Jan: "we would use his system ourselves", AWS is fine)
`python3 wallet5m.py speed` -> `backtest/wallet5m_speed.txt`.
- **His edge is speed.** Around each fill, Bitcoin (Binance, by the second) jumps toward the side he buys 2-5 s before the
  fill's timestamp, for his grabbed offers and his waiting orders alike. So he trades in the first seconds after Bitcoin
  moves, before Polymarket's prices catch up. (The timestamp is when the trade lands on the blockchain, about 3 s after
  the match.)
- His waiting-order money comes from that too. Fills right after a move his way: +$21 per $100 ($19,144). Fills with
  no move: +$0.63 per $100. Fills just after a move against him (picked off): -$13,425. Without being among the fastest,
  the plain waiting part is about +$0.63 per $100, before the rebates a newcomer wouldn't get.
- **Pulling orders when Bitcoin drops doesn't help.** Pulling when our side's fair price falls 2, 3 or 5c, 1-3 s
  before the match: +$1.23 to +$1.63 per $100 on what is kept, against +$1.47 for doing nothing (9 versions tried).
  The orders it would have pulled were profitable too.
- So copying "his system" means a race in the 1-3 seconds after each Bitcoin move against him and other pro bots.
  It's the same kind of race as Jan's old Binance-to-Polymarket bot. Jan's server is in Stockholm (free plan locks
  the region): about 30 ms to Polymarket in London, but Binance's engine sits in Tokyo, so prices reach Stockholm
  later than they reach bots placed near Binance. Verdict unchanged: no track. Only a real-money test could show our
  place in that race, and these numbers say to expect a loss.
