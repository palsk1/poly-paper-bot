# Crypto price gaps between exchanges, inside one exchange, and on stablecoins (crossx, 27 Nov 2026)

Research only. Nothing was bought, no accounts, no keys. Script: `outside/crossx.py` (probe `out_crossx_<cmd>`),
data in the price store folder `bt_cache/out_crossx/`.

**Short answer: nothing here for a $300 bot. Fees are 10 to 30 times bigger than the gaps on every normal coin.**
The only gaps big enough to pay are on small coins where something is broken (a wallet closed, a thin order book
on one site), and they stop paying above about EUR100 a trade.

## What was measured

- 8 exchanges read at the same second, every 15 seconds, for 100 minutes (27 Nov, 14:10-15:49 UTC, 400 looks),
  then a fresh 45-minute look (15:53-16:37 UTC, 180 looks) to see if anything held up, plus each site's wallet status
  and 2-hour trade list for the coins with gaps.
- Every coin sold for euros on 2 or more of them: 366 coins, 1,170 price pairs a look.
- Every time a site's best buy price beat another site's best sell price, both full order books were read again
  at once (about a quarter of a second later) and a real buy-here-sell-there was priced at EUR50, EUR100 and EUR300,
  walking down the book, with both sites' taker fees. 7,536 such re-checks in the first run.
- 62 three-step loops inside one exchange (euro -> coin -> bitcoin -> euro, and back).
- USDC, USDT and EURC against the euro, and the Kraken loop euro -> USDC -> dollar -> euro.
- Stablecoin dips under $0.99 since 2019 (Binance's public hourly history, 18 stablecoins).
- Swedish crowns: Firi's SEK books (blocked, see below) and Bitpanda's SEK prices.

## Fees a Swede pays at the start (checked 27 Nov 2026 on each fee page)

| Exchange | Usable from Sweden? | Taker fee on EUR100 | Stablecoin pairs | Notes |
|---|---|---|---|---|
| OKX EU | Yes, MiCA licence (Malta) | 10 cents | 10 cents | cheapest; only ~65 EUR coins |
| Bitvavo | Yes, MiCA (Netherlands) | 25 cents | 10 cents | free SEPA in |
| Bitstamp | Yes, MiCA (Luxembourg) | 40 cents | 8 cents (USDT 4) | new fee table from 24 Nov 2026 |
| Coinbase Advanced | Yes, MiCA (Luxembourg) | 50 cents | not public (guess 10) | EU rate since 16 Sep 2026 |
| Kraken Pro | Yes, MiCA (Ireland) | 80 cents | 20 cents | raised from 26 to 80 cents in July 2026 |
| Firi | Yes, MiCA (Norway), SEK | guess 70 cents | - | free SEK bank deposit |
| Safello | Yes, Swedish MiCA licence | broker, no order book | - | price includes a spread |
| Binance | No MiCA licence for Sweden (suspended July 2026, per one guide; guess) | 10 cents | - | used only as a yardstick |
| Bitfinex | Not on the Sweden MiCA list (guess: not allowed) | 20 cents | - | yardstick only |

So the cheapest buy-here-sell-there pair a Swede can use costs **35 cents per EUR100** in fees (OKX 10 + Bitvavo 25).
Any pair with Kraken in it costs 90 cents or more.

Tax (one line, check with Skatteverket): every sale or coin-to-coin swap, stablecoins included, is a taxable sale in
kronor on form K4 section D, average cost method; gains taxed 30 in 100, losses count only 70 in 100. An arbitrage
bot makes thousands of K4 lines, and a year that nets to zero in cash can still owe tax.

## 1. Same coin, two exchanges (pre-funded on both sides, no transfers)

**Big coins: never.** For bitcoin, ether, solana, XRP, cardano, dogecoin, litecoin, link, polkadot, avalanche, tron,
sui, pepe, shiba and bitcoin cash, the best "buy cheap here, sell dear there" gap across the 5 usable sites was about
**1 cent per EUR100** in the middle of the 400 looks and **25 cents at the very most** (dogecoin). The cheapest fees are
35 cents. 0 of 8,700 looks (580 looks x 15 coins, both runs) paid. (A German news site found the same on 5 Nov 2026: bitcoin gaps of 1-1.5 cents per
EUR100 between Kraken, Bitvavo, Coinbase and Bitstamp.)

**All 366 coins, usable sites only, real fees:** 1,819 of 7,351 re-checks were still ahead at EUR100. That sounds like a
lot, but they bunch into only 143 separate gaps ("episodes"), and two kinds make up almost all of it:

- **Stuck gaps (42 episodes):** GMT and MERL were 1.4-1.9 euros per 100 dearer on Kraken than on Bitvavo/OKX for the
  whole 100 minutes, with money on both books. A gap nobody closes for hours means the coins can't be moved (a wallet
  closed on one site, or a different token behind the same ticker). Pre-funded, you could sell your Kraken stock once
  (about EUR0.77 on EUR100), then you are stuck with coins on the wrong site. Taking each once: under EUR5 in total.
- **Short gaps (101 episodes, most gone within 15 seconds):** EUR46 at EUR100 a trade over 1.7 hours if every one was
  caught at the first look; **EUR41 of the 46 came from one coin, INIT** (Initia, buy Bitvavo, sell Kraken, gap about
  2-3 euros per 100). At EUR300 a trade the same gaps **lost EUR319**, because Kraken's buyers only stood there for
  about EUR100-200.
- Gaps over 3 euros per 100 (8 pairs: LIT, EDGE, LUNA, INIT, ZRC) were left out: same ticker, different coin.

**Why the "winners" exist (checked on the exchanges' own wallet pages and trade lists, 27 Nov 16:40 UTC):**

- **INIT:** Bitvavo has INIT deposits and withdrawals **in maintenance**. Nobody can move INIT from Bitvavo to Kraken,
  so the gap can't be closed, and we couldn't rebalance either. Kraken's INIT buyers only took EUR1,351 of real sells in
  2 hours, so someone else already sells into them.
- **GMT, MERL, NEX:** Kraken had **0 trades in 2 hours** on these. Their Kraken prices are old orders nobody touches,
  so the "gap" is a dead book, not money.
- **BLUR:** wallets open on both sides, real trades on both. The only clean one: EUR3.72 in 45 minutes at EUR100, gaps
  of 20-60 cents per EUR100 that last one look.

**Fresh 45 minutes (180 looks, 15:53-16:37 UTC):** big coins again 0 looks above fees (bitcoin gap at most 5 cents per
EUR100). Short gaps: 48 episodes, EUR14 at EUR100 a trade if caught at first look (INIT 5.21, BLUR 3.72, NES 2.47,
BTT 2.41), **-EUR43 at EUR300**. Over both runs (580 looks, 2.5 hours): EUR123 at EUR100, -EUR311 at EUR300, most of it
INIT and stuck coins. These are paper prices from a quarter-second-old book read; a real taker 70-100 ms away would
often arrive after a faster bot.

**Rebalancing cost (pre-funded version):** every buy-here-sell-there moves coins from one site to the other. Moving
them back costs a network fee each time (rough guesses: bitcoin EUR1-10, XRP / solana / stablecoins on cheap networks
a few cents to EUR1, SEPA euro moves free to EUR1). On a EUR1 profit, one rebalance a day is fine; on 20 cents it is not.

## 2. Three-step loops inside one exchange

62 loops (euro -> coin -> bitcoin -> euro and back) on OKX, Bitstamp, Kraken, Coinbase and the Binance / Bitfinex
yardsticks: **0 of about 36,000 looks (62 loops x 580) paid after 3 taker fees.** The best gross gap seen was 8.6 cents per EUR100 (OKX ether);
three OKX fees cost 30 cents, three Kraken fees EUR2.40. Matches the 2025 study of Binance loops ("exist, but fees and
thin books eat them").

## 3. Stablecoins and crowns

- **USDC for euros** sits within 1-2 cents per EUR100 of the real euro-dollar rate on every site (Kraken, Bitvavo,
  OKX, Bitstamp, Coinbase). The biggest gap between two sites in 400 looks was 2 cents; the cheapest fees are 18 cents.
  Dead.
- **USDT** trades about 11 cents per 100 below a dollar everywhere (Kraken, Bitstamp, OKX, Coinbase, Binance agree), so
  that is its market price, not a gap. (USDT is also being pushed out of EU sites under MiCA.)
- **EURC for euros:** within 1 cent on Kraken / Bitvavo; Bitstamp's book is just wide (99.5c bid, 100.04c ask). Dead.
- **Kraken loop** euro -> USDC -> dollar -> euro: best gross +0.9 cents per EUR100, fees 60 cents. Dead.
- **Crowns:** Firi's public API answered "not acceptable" to the script (format problem, not fixed in time). Bitpanda's
  SEK prices use its own euro-crown rate, 11.2086 vs the ECB's 11.2025: 5 ore dearer per 100 kr, inside its own buy/sell
  spread, so nothing to win. No exchange with a public SEK order book was read. Untested: Firi and BTCX books.

### Buying stablecoins under 99 cents (history since 2019, Binance hourly, priced in USDT)

Rule: after an hour closes under $0.99, buy $100 at the next hour's open (+0.1c), fee 10 cents each way, sell at the
first hour that closes at $0.998 or more.

- **45 bets on 32 separate dips (2019-2026), 43 won.** Wins were small and usually quick: USDC in March 2023 (bought
  91.4c, sold 99.8c 5 days later, +$9.01), FDUSD April 2025 (+$3.14), USDe October 2025 (+$6.25), AEUR (+$17.76).
- **The 2 losses were UST (Terra) in May 2022: -$75 and -$80.** One collapse wiped out all 43 wins.
- Exam (all 45): **-$1.68 per $100, "Behind, but could be bad luck"**, worst case -$15.05 per $100.
  Leaving UST out (hindsight, not allowed) it would read +$1.92 per $100 "Ahead, but could be luck", still not proven.
- Lower bars ($0.98, $0.97) do the same: 11-13 wins, the same UST losses, total about -$94.
- In practice: about 3-5 dips a year, each open for hours to days. On $300 split over a couple of dips a year that is
  maybe $5-30 a year when it works, and $200 gone when the coin really dies. Not a bot.

## 4. Backward look: who makes money here?

- **Market makers, not takers.** The people closing these gaps rest orders on both sites (Kraken and Bitstamp pay
  0 to 0.10 for big makers; Kraken pays makers on some small coins) and pay 0-5 cents per EUR100 at volume tiers of
  $1-10 million a month. Our 0.05-each-side "big-volume world" lens shows what they see: 564 gaps worth about EUR216 in
  1.7 hours at EUR100 a trade, almost all on the same small stuck coins.
- **Studies:** big cross-exchange gaps (the "Kimchi premium", Bitfinex in 2017-2018) came from money that couldn't move
  (capital controls, a bank cut off). Gaps shrink every year. A 2026 paper on Binance and Kraken trade tapes found
  "one-way arbitrage" worth $31 million over 5 years on Binance, but **under $1 a trade after fees**, done in
  milliseconds by servers next to the exchange.
- **What they have in common:** fee tiers a $300 account can never reach, servers a few milliseconds from the matching
  engine (we are 70-100 ms away, the 2025 Binance-loop study moved to Tokyo to get 4 ms), and inventory on both sides.
- **Is any version open to us?** Only the thin-book small-coin case (like INIT), where a slow taker can still be
  first because nobody big bothers with EUR100 of depth. That is the "it depends on one coin's quirk" kind of lead.

## The four ceiling lines (rough guesses)

| Idea | Most in an average day at best size | Money needed | Stops growing at | Bad day |
|---|---|---|---|---|
| Big-coin cross-exchange | $0 (never beat fees) | - | - | - |
| Triangles | $0 | - | - | - |
| Stablecoin gaps | $0 | - | - | - |
| Small-coin thin-book gaps (INIT-type) | ~$5-15 while one coin's wallet is shut (INIT), else ~$1-3 (BLUR-type); one-off, ends when you run out of coins on the dear site | ~$300-500 split over 2 sites | about EUR100 a trade | a coin's price drops 10-30 in 100 while you hold it on the wrong site, or a wallet closes: -$30 to -$100 |
| Stablecoin dip buying | ~$0 (3-5 chances a year) | $300 | $1,000s fine | one real collapse: -$75 per $100 |

## Verdict

- Big-coin cross-exchange gaps: **dropped** (0 of 8,700 looks beat fees, gaps 1 cent vs fees 35 cents per EUR100).
- Triangles inside one exchange: **dropped** (0 of about 36,000 looks).
- USDC / USDT / EURC gaps and the Kraken currency loop: **dropped**.
- Stablecoin dip buying: **dropped** (one UST wipes out 43 wins; exam "Behind, but could be bad luck").
- Small-coin thin-book gaps: **dropped as a bot** (every big gap is a shut wallet or a dead book; the one clean coin made EUR3.72 in 45 minutes at EUR100 and loses at EUR300; found by looking). Interesting for later only as a manual trick: when a site shuts a coin's wallet, coins held on the dear site can be sold once.
- Crowns: untested in depth (Firi's API refused the script), **interesting for later** only as a 10-minute follow-up.
