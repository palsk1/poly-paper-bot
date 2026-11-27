# Betting exchanges outside Kalshi and Polymarket (27 Nov 2026, `outside/exch.py`)

**Short answer for Jan: dropped. Two reasons, and either one is enough.**

1. **You can't legally use any of them from Sweden right now.** Betfair left Sweden on 16 July 2025. Smarkets'
   Swedish licence ran out (April 2025) and its Swedish licence only ever covered the sportsbook side anyway.
   Matchbook, Betdaq and Orbit (a Betfair copy) all list Sweden as a country they don't take.
2. **Where we could compare prices, they match Polymarket.** On 203 game and election prices quoted tightly on both
   sides at the same moment, the usual gap was **half a cent**. In 80 minutes of watching, buying one side here and
   the other side there left money after fees once on a short-dated game (about 23c on $10). Every other "gap" was
   a 2027-2028 future that pays less than bank interest, or two different bets wrongly paired.

Nothing below changes that. Details follow so we don't redo it.

## 1. Can Jan use them from Sweden?

| Exchange | Swedish licence? | Takes Swedes in 2026? | Fee | Bot access (API) | Smallest bet |
|---|---|---|---|---|---|
| Betfair Exchange | Had one (18Li8550) | **No. Left Sweden 16 Jul 2025** (Betfair's own exit notice) | 2-5% of what you win in a market; extra "Expert Fee" (20-40% of profit) above £25,000 profit a year | £499 one-off for a live key, free delayed key | £1 (about $1.30) |
| Orbit / Piwi (Betfair copies) | No | **No** (Orbit lists Sweden as refused) | about 3% (guess) | through a broker | varies |
| Smarkets | Had one, sportsbook only, ran out April 2025 (Spelinspektionen told a forum user it was not renewed; Smarkets' own page still lists it) | **No new Swedish accounts seen since** (guess; forum reports, May 2025 and May 2026) | 2% of what you win in a market (1% "Pro" above 1,500 bets a month, 3% above £25,000 profit a year) | £250 one-off, by application | small (guess) |
| Matchbook | No | **No** (Sweden on its refused list) | 2% UK, 4% elsewhere | on request (guess); the read-only listing is open to anyone | small (guess) |
| Betdaq | No | **No** (Sweden not on its list). Also: Betdaq's markets closed on 21 Oct 2026 after Matchbook's owner bought it | 2% UK, 5% elsewhere | £250 one-off | small (guess) |
| SX Bet (crypto) | No | Open to anyone with a crypto wallet, but not licensed for Sweden | a few cents per $1 won (guess) | free | tiny |

- **Tax (one line, a guess):** none of these has a Swedish licence, so winnings would probably be taxable (30% of the
  gain) instead of tax-free; check with Skatteverket before any real money.
- **Using a UK account through a VPN** breaks every exchange's rules and gets accounts closed with the money
  frozen. Not an option.
- **What Sweden does have:** Pinnacle (already used as our sharp-price ruler) and the normal bookies. None of them
  lets you be the seller.

## 2. Real data: Smarkets and Matchbook against Polymarket and Kalshi

What we did: from GitHub Actions we read every open Smarkets market (1,728 events, 18,642 markets, 93,628
outcomes) and every open Matchbook event (934 events, about 64,500 outcomes; Matchbook's listing is open, no
login), plus 8,000 open Polymarket events and 6,000 Kalshi events. We paired outcomes by name (same game or
election, same team or person, only "who wins" markets), read both sides' real order books at the same moment and
priced a $10 and a $50 cross bet with every fee: Smarkets or Matchbook 2% of the win, Polymarket's own taker fee,
Kalshi's fee. A "cross bet" buys Yes on one site and No (or lay) on the other, so it pays $1 whatever happens.

First full snapshot (27 Nov, 14:30 UTC):

- 3,400 outcome pairs found by name, 465 with prices on both sides.
- **203 pairs had tight books on both sides** (gap between buy and sell price at most 6c). On those the middle
  prices differed by a **median of half a cent**. 28 differed by 2c or more, 12 by 5c or more.
- The "cheap" cross bets in the first list (cost 58c for a sure $1) were all **wrong pairs**: Smarkets names its
  basketball handicap markets after the team ("Virginia Cavaliers -7.5"), which our matcher first read as the plain
  winner. Removing handicap lines removed them. That trap is now in the code.
- The real 5c+ gaps were long-dated bets (2028 Republican nomination, Scottish league winner, the Grammys, the French
  2027 election) where money is locked up for one to three years, or thin Matchbook books with a few dollars on
  offer. Not free money.

**80 minutes of watching (27 Nov, 14:48-16:08 UTC, a look every 45 seconds, 219 pairs with tight books, 107
looks).** Second snapshot first: 219 tight pairs, median gap again half a cent, 8 pairs 3c+ apart.
42 pairs cost under $1.00 at $10 for a sure $1, but look at what they are:

- **About 30 are long-dated futures** (2028 US election and nominations, 2027 French election, Scottish league,
  BBC Sports Personality). Example: Gavin Newsom for the 2028 Democratic nomination, buy Yes on Polymarket and lay
  him on Smarkets: cost 98.3c, pays $1.00 in summer 2028. That is 1.7c for locking $1 up for about 20 months, less
  than a savings account, with a pound-vs-dollar swing on top (Smarkets pays in pounds). The same 34 pairs were
  "under $1.00" in all 107 looks: nobody takes them because they aren't worth taking.
- **Five were wrong pairs:** Matchbook's men's Champions League winner matched to Polymarket's women's Champions
  League (Barcelona "41c apart"). Name matching across sites keeps making this kind of mistake; a real bot would need
  a human check of every pair, like our `arb_pairs.json` review.
- **One short-dated real gap:** a college basketball game (Louisiana Tech vs Texas State): Polymarket offered
  Louisiana Tech at 30c while Smarkets bid 36.8c. At $10 the cross cost 97.7c for a sure $1 (about 23c profit);
  at $50 it cost $1.16, because Smarkets only had a few pounds at that price. Football (soccer) on Smarkets was
  partly missing this run (Smarkets answered "too many requests"), so games are under-counted.

**Who moves first after news?** In 80 minutes only 11 middle prices moved 2c or more on either side, and in none did the other site
follow within the next 4 minutes (one moved together in the same look). A quiet US afternoon with few games live, so
this says little either way; what it does say is that there was no steady "one site is late" pattern to trade.
Polymarket's books were usually much deeper (thousands of dollars per price step) than Smarkets' (median best
offer about £165 of payout) or Matchbook's.

## 3. Small edges people claim on exchanges

- **Backing or laying at Betfair's closing price, by price band.** football-data.co.uk has Betfair Exchange
  closing odds for 14,536 games (21 leagues, seasons 2024/25 and 2025/26). Backing every side at that price, with 2%
  commission: draws at 20-30c lost $0.78 per $100 (10,364 bets), home favourites at 60-70c lost $1.63, away
  long shots under 10c lost $27.57. The full set of back prices costs about $1.007 for a sure $1, so backing
  everything loses before any fee. Betfair's closing price forecast the games exactly as well as Pinnacle's
  (log-loss 0.9971 vs 0.9972 on 10,416 games). The best band, found by looking (backing away teams at 60-70c):
  **+$3.45 per $100 on 451 bets, exam "Ahead, but could be luck"**, luck range -$2.20 to +$9.10, needs about 5,500
  more bets to prove. Dropped. Laying at the same price is the same thing turned round, minus the spread.
- **"Lay the draw" and other in-play football trading.** No free in-play price history (Betfair's history needs a
  login and blocks US addresses). What research there is says prices react to goals within seconds
  (Croxson and Reade 2014, Economic Journal) and the leftover mistakes are small favourite biases, bigger after a
  late surprise goal (Angelini, De Angelis and Singleton 2022, International Journal of Forecasting). Lay the draw is
  a bet that a goal comes; it is worth exactly what the pre-match draw price says, minus commission. We already know
  draws are priced fairly (`backtest/drawsharp.md`). No edge for a slow bot.
- **Pre-race horse racing trading ("scalping" a tick).** The forum stories are about people sitting in the queue
  in the last 10 minutes before the off, a game of speed and queue position against full-time bots, on a market
  whose money has fallen every year since 2016 (Racing Post). A 2024 study of Betfair UK racing prices
  (arXiv 2402.02623) found the prices efficient. We can't test it (no Betfair data from Actions) and Sweden can't use
  it anyway.
- **Back-to-lay / arbitrage against bookies ("matched betting").** Works only with bookie sign-up offers. Swedish
  licensed bookies may give one welcome bonus per company, and without a Swedish exchange you can't lay the other
  side. Dead in Sweden.

## 4. Backward look: who makes money on Betfair and Smarkets?

- Betfair's own numbers: before 2025 a "premium charge" of up to 60% of profit hit the winners; its replacement
  (Jan 2025) charges 20% of yearly profit above £25,000 and 40% above £100,000, and Betfair says it is paid by "a
  very small number" of customers. Smarkets says only 2 in 1,000 of its customers reach its pro or winner tiers.
- So the winners are a small group of high-volume traders and bots (market makers in the queue, in-play speed
  traders with live pictures faster than the TV, horse racing people with their own ratings), and the exchanges
  tax them extra once they win. The money comes from the many casual punters who back long shots.
- Open to a $300 bot? Only as a queue-sitting market maker, which is a speed and volume game, the exchange needs
  a paid API key (£250-£499, more than the whole pot), and it is closed to Sweden. No.

## The four ceiling lines (rough guesses)

- **Most it can make in an average day at best size:** about $0 to $1 (one 23c gap in 80 minutes of watching,
  at $10); the long-dated "gaps" pay less than bank interest. The closing-price bands don't beat the price.
- **Money needed:** £250-£499 for the API key alone, plus a non-Swedish address. Not possible for Jan.
- **Size where it stops growing:** Smarkets' best offer held about £165 of payout (median); Matchbook often a few
  dollars outside big games.
- **A bad day:** a wrong pairing (two sites settling one game differently, like the handicap trap above) loses the
  whole stake on both legs, $20-100 at these sizes.

## Verdict

- Smarkets / Matchbook vs Polymarket and Kalshi gaps: **dropped** (prices match within half a cent; Betfair itself
  can't be read from Actions, but its closing prices match Pinnacle's, which match Polymarket's).
- Betfair closing price bands, lay the draw, pre-race trading, matched betting: **dropped**.
- Whole area: **closed for Jan** while no exchange takes Swedish customers. Worth one look again only if Betfair or
  Smarkets come back to Sweden.

Data: snapshots in `bt_cache/out_exch/` (price store). Re-run: probe `out_exch_snap`, `out_exch_watch_<min>_<sec>`,
`out_exch_bfe`, `out_exch_report`.
