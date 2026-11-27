# Combo house: how much money does it really need? (25 Nov 2026)

Jan: "How much would we realistically have to have minimum to get combo house to work? Feels like the only strat so
far that can bring in lots of money." Research only, no bot built. Run: `QUOTER_DIR=<folder of unpacked day files>
python3 combos.py money` (or without QUOTER_DIR to read the release `quoter-data`).

Data: the paper listener's full logging days, 17 Nov 00:00 to 22 Nov 13:00 UTC (5.5 days; it was switched off on
22 Nov when Jan put the combo house on hold). Rule `main` (2-4 legs, no two legs from one game, legs multiplied + 5%).

## The big new fact: we don't have to cover the whole ticket

Polymarket's market-maker docs ("Quote Partial Fills") let a quoter fill only part of a request. So the house can
put up $1 (or $5) on every parlay no matter how big the buyer's ticket is. The 22 Nov note ("a real house must cover
the size the buyer asks for") was wrong. That matters, because real tickets are big:

- The middle buyer spends $10; 1 in 10 spends $210 or more (the biggest: $30,000).
- To cover a whole ticket the house would put up $78 in the middle case and $1,296 or more 1 in 10 times.

## How the house money is tied up

- About 1,377 sales a day where our price was cheaper than the winning pro's. The house wins about 80 in 100.
- Typical bet for the house: put up $1, win about 19c if any leg loses, lose the $1 if every leg wins.
- Money comes back after a few hours: middle 2.9 hours, 1 in 10 over 12.6 hours, 1 in 100 over 2.6 days.
- At most 822 parlays were open at the same time.

## Result per bank (replay of the same 5.5 days, rough guide)

"Expected a month" uses the whole paper scorecard (+$1.61 per $100 at risk on 8,527 parlays, luck range +$0.07 to
+$3.14), not just these lucky-ish days.

| Bank | Per parlay | Sales taken | Real result, 5.5 days | Expected a month (luck ends) | Worst drop | Worst day |
|---|---|---|---|---|---|---|
| $300 | $1 | 3 in 4 | +$80 | about $500 ($22 to $980) | -$102 | -$36 |
| $500 | $1 | 9 in 10 | +$116 | about $610 ($26 to $1,190) | -$104 | -$39 |
| $1,000 | $1 | all | +$131 | about $660 ($29 to $1,280) | -$96 | -$31 |
| $1,000 | $2 | 9 in 10 | +$231 | about $1,200 ($52 to $2,340) | -$188 | -$57 |
| $5,000 | $5 | all | +$573 | about $3,100 ($135 to $6,050) | -$353 | -$32 |

Worst drop = the biggest fall from a high point before it recovered. At $1 a parlay it took a third of a $300 bank.

## Ceiling (rough guess)

- Most in an average day: about $20 at $1 a parlay (needs $500-1,000), about $100 at $5 (needs about $5,000).
- Money needed: about $300 to start at $1 a parlay (takes 3 sales in 4), $1,000 for every sale.
- Where it stops growing: unknown. Up to about $5-10 a parlay most tickets are bigger than our piece, so it should
  scale. Past that the pros may cut their prices once a new quoter takes their sales.
- Bad day: about -$40 at $1 a parlay, about -$200 at $5 (a whole NBA night going the buyers' way).

## What Polymarket asks of a quoter (docs.polymarket.com, "Market Makers" / "RFQ Overview", read 25 Nov)

- No approval to start: a Polymarket account, API keys (CLOB login + a "Relayer" key), a one-time set of contract
  approvals, and pUSD (Polymarket's dollar) in the wallet. No minimum size found in the docs.
- Answer every request with a signed price within 400 ms (one page says 200 ms). Our paper bot priced in time.
- The buyer then has up to 10 seconds to accept. **"Last look"** (a final second to say no if the legs moved) is only
  for makers with about $2,500 of combo volume and a contact at Polymarket. Without it, every accepted quote is binding.
- Makers that later decline more than 15 in 100 selected quotes get paused.

## Honest risks

1. **Thin lead.** +$1.61 per $100 with a low luck end of +$0.07: the paper house is ahead, but it could still be
   about $0. The first half of these 5.5 days made +$0.64 per $100, the second +$3.19. The "before kick-off only"
   side scorecard flipped to -$1.82 per $100 (2,507 parlays), and the $100 pot at $5 a parlay ended -$75.
2. **Stale quotes without last look.** The pros can say no when the legs move in the 10 seconds before the buyer
   accepts. We couldn't, so the sales we'd really get lean towards the bad ones. The paper test can't see this.
3. **A real bot is big work.** It has to sign about 8,000 quotes a day in 400 ms and never misprice. One pricing bug
   can lose the bank in minutes. Claude never touches keys, so it would run only on Jan's server with his key.
4. **Few days.** Only 5.5 full days were ever logged.
5. **The pros react.** Once we take their cheap sales, they may lower their prices too.

## Verdict

The minimum that works is about **$300 at $1 a parlay** (better $500, which takes 9 sales in 10). On paper that's
around **$500 a month**, many times more than any other strategy at the same bank, but the honest range is from about
$20 to about $1,000, and a $100 drop is normal. It is the only lead whose money grows with the bank. The careful next
step would be a real quoting bot at $1 a parlay with a hard stop (for example -$60), compared every day with the
paper listener (the listener would have to be switched back on). Jan's call; still on hold.
