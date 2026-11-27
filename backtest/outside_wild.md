# Wild card: places to make money we never looked at (27 Nov 2026)

Script: `outside/wild.py` (probe `out_wild_<cmd>`: `hosts`, `vol`, `volreal_BTC_2021`, `defi`, `pendle`, `skins`).
Paper research only. No accounts, no keys, no orders. Data: Deribit's public archive, DeFiLlama, Pendle's API,
Skinport's public API, all read from GitHub Actions.

**Short answer for Jan: nothing here beats what you already have.** I looked at 22 ideas. 17 die on paper
(can't use it from Sweden, needs far more than $300, or the pros already own it). I tested 4 with real data.
The best of them pays about the same as a Swedish savings account. The one real lesson is a warning, not a
money maker (see "Read this first").

The four lines for each tested idea are in its section; all are rough guesses.

## Read this first: the EU rule on prediction markets (not a money idea, a safety one)

On 3 July 2026 the EU markets watchdog (ESMA) said: a yes/no bet whose question is about a price, an interest
rate, inflation, other official economic numbers, commodities or the weather counts as a "binary option", and
selling those to ordinary (retail) customers has been banned in every EU country since 2019. That is why
Interactive Brokers will not sell its own prediction markets (ForecastEx) to Swedes unless they are classed as
"professional" (you need two of: about 10 big trades a quarter for a year, over EUR 500,000 in savings, a year of
work in finance). Kalshi's crypto 15-minute rounds and CPI/Fed markets are exactly such questions. Polymarket's
crypto rounds too. ESMA's note is aimed at the firms that sell, not at the customer, and sports or politics
questions are not covered by it (those may count as gambling instead). **This is not legal advice, and it does not
mean Jan breaks a law.** But the CLAUDE.md line "check that Jan may legally trade on each site from Sweden" now has
a concrete reason behind it, and the real Kalshi bot trades exactly the kind of question ESMA named.

## What "doing nothing" pays (the bar every idea must beat)

- Best Swedish savings account with the state deposit guarantee, money free to take out: about 2.8 a year on
  each 100 kronor (Multitude Bank, 25 Nov 2026). On $300: **about $8.40 a year, about 2 cents a day**, before tax.
  Riksbank rate 2.00 since 11 Nov 2026.
- Locked for 3 years: about 3.5 per 100, so about $10.50 a year on $300.
- Nothing below is worth Jan's time unless it clearly beats roughly 2-3 cents a day on $300 without risk.

## The 4 ideas tested with real data

### 1. Selling weekly Bitcoin / Ether "insurance" (options) on Deribit

**The idea.** People pay for crash insurance. On Deribit (the big crypto options exchange) you can be the
insurer: sell a weekly put (pays out if Bitcoin falls a lot) or a straddle (pays out if it moves a lot either
way), keep the fee if the week is calm. Pros say option buyers overpay on average.

**Usable from Sweden?** Yes, it looks like it: no EU country is on Deribit's blocked list (6 Oct 2026). But
Deribit has no EU licence (it runs from Dubai, owned by Coinbase), so no EU investor protection; crypto deposits
only. Tax: Swedish capital gains, 30 on each 100 of profit, on a K4 form (guess, check). Smallest trade: 0.1 BTC
on the coin-settled options, 0.01 BTC (about $610 of Bitcoin) on the USDC-settled ones. Fee: 0.0003 BTC a contract
(capped at an eighth of the option's price) plus a small settle fee.

**What the data says.**
- Step 1 (model prices, 293 weeks, Apr 2021-Nov 2026): if you could sell at Deribit's own "fear index" (DVOL),
  the weeks really were calmer than priced: the real swing was 83c per $1 of priced swing (median). On paper a
  weekly straddle made money. But a far put sold one vol point under the index: about $0 (exam: "Behind, but
  could be bad luck", -$0.19 per $100).
- Step 2 (REAL prices: every option trade in Deribit's public archive in the first 3 hours of each weekly
  round, priced at what sellers really got): the market's weekly price was about 6 vol points
  *under* the fear index (median over 270 weeks), so most of the step-1 "profit" was never on offer.
  - Weekly straddle at the real bids, 270 weeks (Apr 2021-Nov 2026): **+$0.47 per $100 of deposit a week**,
    exam "Ahead, but could be luck" (luck range -$2.99 to +$3.94; first half -$1.10, second half +$1.14).
    Years: 2021 +$2.58, 2022 +$6.28, 2023 -$7.34, 2024 -$1.04, 2025 +$3.40, 2026 -$3.31 (per $100 a week).
    Worst week -$181, worst losing stretch -$572 per $100 of deposit: five and a half times the deposit gone.
  - Weekly put about 8 below the price, real bids, 287 weeks: **+$0.24 per $100 of deposit a week**, exam
    "Ahead, but could be luck" (luck range -$1.81 to +$2.28; halves -$0.34 / +$0.47). Won 264 of 287 weeks,
    but the worst week cost -$203 per $100 of deposit and 2026 so far is -$2.95 a week.
  - Ledger rows not added (lead's call): "wild: sell weekly straddle BTC at real Deribit bids" and
    "wild: sell weekly put8 BTC at real Deribit bids", tries 6.
- The worst single week cost more than all the margin (the money you must leave as a deposit). One bad week
  in 2022 or the March 2020 kind would wipe out a $300 account. This is the classic "picking up coins in front
  of a steamroller" trade.

**Ceiling (rough guesses):** selling a far weekly put on 0.01-0.02 BTC with $300 in the account: about 5-10 cents in an
average day (roughly $0.70 a week, IF the history repeats, which the exam can't promise); money needed: $300 for
1-2 of the smallest contracts with room for a bad week; size where it stops growing: not our problem (Deribit trades
billions), but the smallest price step (0.0001 BTC) is a big slice of a far put's few-tick price; bad day: a 15-20
Bitcoin crash week costs $100-200 per contract, i.e. most or all of the $300. Tax: every trade is a taxable event
outside an ISK (crypto can't go in an ISK).

**Verdict: dropped.** The real prices erase most of the famous "option sellers win" effect. What's left
is 5-10 cents a day that the exam calls "could be luck", bought with the risk of losing the whole $300 in one week.
That is worse than a savings account once you price the risk. Data is kept (`bt_cache/out_wild/`) for a free
re-check in a year.**

### 2. Lending out dollar stablecoins (Aave, Morpho, Maple, Fluid, Compound)

**The idea.** Lend digital dollars (USDC/USDT) on a lending app and collect interest; or borrow on one app
and lend on another when the second pays more.

**Usable from Sweden?** Yes, anyone with a wallet; no licence or KYC on the apps themselves; buying USDC in
the EU goes through a MiCA-licensed exchange (Coinbase, Kraken, Bitstamp). Gas on Base/Arbitrum: cents.
Two catches for a Swede: the money is in **dollars**, so a stronger krona can eat a year's interest in a month,
and a hack or a stablecoin wobble can take the lot. Tax: interest and any dollar gain are taxed at 30 on each
100 (guess, check).

**What the data says** (DeFiLlama, 365 days of daily rates for the biggest pools):
- Aave USDC on Ethereum: about 3.4 a year on each 100 (low 1.6, high 12.6). $300 -> about $10 a year.
- Maple USDC (lends to trading firms, more risk): about 5.0 -> about $15 a year.
- Fluid / Compound USDC: 3.4 to 4.6 -> $10 to $14 a year.
- Today's headline rates of 6 to 50 are mostly reward tokens or tiny new pools; the 30-day averages are lower.
- Borrow-here-lend-there: the biggest same-chain gap today is 4.8 a year (an obscure app, Dolomite), and you
  first need to put up other coins as security. On $300 that is under $10 a year. Nothing.

**Ceiling (rough guesses):** best average day about 4 cents ($15 a year on $300); money needed: any amount;
size where it stops growing: none for us (pools hold hundreds of millions); bad day: a hack or depeg, up to the
whole $300 (rare, but it has happened: Euler 2023, several smaller pools in 2025-26).

**Verdict: dropped as an edge.** It is a savings account in dollars with extra hack risk, paying $2-7 a year
more than a Swedish bank on $300. Fine as a parking spot for USDC between bets; not a strategy.

### 3. Pendle fixed yields

**The idea.** Pendle lets you lock in a fixed interest rate on a stablecoin until a set date (buy the
"PT" token at a discount). Is the fixed rate usually higher than the floating rate you would have got anyway?

**What the data says** (Pendle's API: 116 stablecoin markets on Ethereum, Arbitrum and Base, 2022-2026, a look
every week, 4,038 looks): the fixed rate beat what the floating rate later paid in 3,317 of 4,038 looks, by
about 3 a year on each 100 (median). In pools over $20 million, by about 6.6. Mostly because floating rates fell
a lot in 2025-26 (looks overlap: really about 116 separate markets, and one falling-rates period). And one
market (srRoyAPYUSD) lost 72 on each 100: when it goes wrong, the "fixed" rate is not fixed at all.

**Ceiling (rough guesses):** about $9 a year more than plain lending on $300 (2-3 cents a day); money needed:
any; size: no limit for us; bad day: a depeg of the coin under it, up to the whole stake.

**Verdict: dropped.** A real premium, but it is pay for carrying blow-up risk, and at $300 it is pocket money.

### 4. Counter-Strike skins: buying cheap listings and reselling (Skinport)

**The idea.** CS2 weapon skins trade for real money on sites like Skinport (German company, pays to a bank,
Swedes can use it). Are some listed far below what they normally sell for?

**What the data says** (two snapshots, about 12 minutes apart, of all 37,450 listed CS2 items + their sale history, 27 Nov): only 55 items
that sell 20+ times a week had a cheapest listing at least 5c per $1 under what a resale brings after Skinport's
8 on each 100 seller fee. Buying one of each: about EUR 1,500 in, about EUR 130 paper gain. In the second
snapshot 53 of the 55 were still there: nobody grabbed them in 12 minutes, a hint (not proof) that they are not free money (most likely
items still under Steam's 7-day "trade protection": you cannot resell them for a week and the seller can take
them back). Plus: 7-8 days before you can resell, then the price you get is a guess.

**Ceiling (rough guesses):** a one-off EUR 100-ish if everything worked; money needed: EUR 1,500; it does not
repeat daily; bad day: skins drop 10-20 on each 100 in a week after a game update.

**Verdict: dropped.** Thin, slow, and the gaps that look free are the price of waiting a week.

## The other 18 ideas, scored without a test (most say "no, because ...")

| Idea | From Sweden? | Money needed | Evidence of a repeatable edge | Bot? | Verdict |
|---|---|---|---|---|---|
| ForecastEx via Interactive Brokers (event contracts that even pay interest on your bet) | **No**: Swedes are IB Ireland clients, only "professional" clients may trade them (IB's own FAQ) | - | - | - | Dropped: not allowed for Jan |
| Kalshi via Interactive Brokers | No (IB Ireland can't offer Kalshi at all) | - | - | - | Dropped |
| Liquidation bots (DeFi) | Yes | Thousands + flash loans | Pros with fast servers win nearly all | Yes | Dropped: a speed race, like our wallet5m lesson |
| Price gaps between Uniswap-style exchanges and Binance/Coinbase | Yes | Thousands | Taken by "block builders" within one block | Yes | Dropped: speed race |
| New token listings (Upbit/Binance pump) | Upbit is Korea-only | Any | Real but over in seconds | Yes | Dropped: speed race |
| Tokenized US T-bills (Ondo, BlackRock BUIDL) | Mostly not for EU retail | $5k+ minimums on several | Pays T-bill rate minus fees, in dollars | - | Dropped: savings account with dollar risk |
| Crypto "dual investment" at exchanges | Varies | $100+ | It is you selling options to the exchange at a worse price than Deribit | - | Dropped (see test 1) |
| Swedish investment company discounts (Investor, Kinnevik, Latour vs their holdings) | Yes (Avanza/Nordnet, ISK) | Any | Discounts move over months; known to everyone | Semi | Dropped: not a daily edge, no free data history |
| Ex-dividend trades in an ISK | Yes | Any | Price drops by the dividend; ISK tax is flat anyway | Yes | Dropped: nothing to gain |
| OMXS30 index changes | Yes | Any | 2 rebalances a year, pros front-run | Semi | Dropped |
| Warrants / mini futures / Bull & Bear certificates | Yes | Any | The bank that issues them is the only seller and sets the price; retail loses on average | - | Dropped |
| Savings accounts / fixed deposits | Yes | Any | Yes, 2.8-3.5 a year, guaranteed | Manual | The bar to beat, not a strategy |
| Premium bonds / lotteries | Yes | Any | Pays less than a savings account on average | - | Dropped |
| Fantasy sports (DraftKings-style) | Not licensed in Sweden; Sorare exists | $50+ | Top 1 in 100 players win; costs time | No | Dropped |
| Price-error / coupon bots on Swedish shops | Yes | Any | Swedish law lets a shop cancel an obvious price error; not repeatable | Semi | Dropped |
| Broker / exchange sign-up bonuses | Yes | Small | One-off, not repeatable (the bookmaker-bonus researcher covers the betting side) | No | Dropped |
| Airdrop farming | Yes | Small + time | Unknowable, projects filter out farmers | Semi | Dropped |
| Esports odds feeds | - | - | Covered by the CS2 dig and the betting researchers | - | Skipped |

## Backward look: who really makes money in these places?

- **Option selling:** the big winners are market makers with fast quotes, deep pockets and hedging (Deribit's top
  makers get paid rebates). Retail option sellers who make money for years usually stop after the one week that
  takes it all back (e.g. Optionsellers.com 2018, crypto "covered call vaults" in 2022). What winners had in
  common: lots of money to survive the bad week, and selling only part of their capital.
- **DeFi lending:** the people who earned big lending rates were early in new pools with reward tokens, and some of
  those pools later broke. Steady winners just got the plain rate. No skill edge.
- **Pendle:** winners bought fixed rates right before floating rates fell (2025). That is a call on rates, not a
  repeatable rule.
- **Skins:** winners are traders with big stocks of items, fee discounts, bots on several sites and patience for
  the 7-day lock; margins of a few cents per dollar on large volume.
- Common thread: the repeatable edges belong to the side that **provides the service** (market makers, lenders of
  last resort, the house), needs a lot of money or speed, and eats the rare disaster. That is the same lesson the
  combo house taught us, and it is the reason the combo house worked.

## Bottom line

- Nothing here is worth a paper track. Best number: selling a weekly Bitcoin straddle at Deribit's real bids, +$0.47 per $100 of deposit a week on
270 weeks (Apr 2021-Nov 2026), "Ahead, but could be luck", with a worst stretch that loses the deposit five times
over.
- Cheapest "edge" that is real: lending USDC, about $10-15 a year on $300 (vs about $8 in a Swedish savings
  account), with dollar and hack risk on top.
- The most useful find is the ESMA warning: before real money grows, check that the Kalshi/Polymarket bots are OK
  for a Swedish retail customer.
