# New prediction-market sites beyond Polymarket and Kalshi (27 Nov 2026)

Research only, paper only. Nobody signed up anywhere, no keys, no orders. Tool: `outside/onchain.py`
(probes `out_onchain_scan`, `_peek`, `_gaps_10_120`, `_rewards`, `_winners`, `_hl_100`, `_dprobe`, `_daily_700`).
This follows `backtest/fasthunt.md` (26 Nov), which said the small sites have no money in them and Hyperliquid was
"not measured".

## Short answer

Nothing here beats what we already run.

- The one big new site, **Hyperliquid's outcome markets**, prices the same games as Polymarket to within a quarter of a
  cent. It was never 2c apart in 1,040 same-second looks. Buying one side on each site never paid after fees.
- **Sites that pay you to wait in line** are real, but small. The only cash pools left are about $53 a day on one site
  (XO Market), and the big one ends 30 Nov. Predict.fun pays in points for a token that hasn't launched yet.
- **Hyperliquid's own crypto yes/no bets** move with Hyperliquid's price within seconds. People who bought right after a
  move made about $1 per $100 (marked a minute later, before the selling fee). That is the same thin result as Polymarket's
  hourly windows.
- **Opinion bans Sweden** by name. The others don't name Sweden, but none has a Swedish licence.

| Site | Real money now (24 h) | Fee | Usable from Sweden? (guess, Jan checks) | What we found | Verdict |
|---|---|---|---|---|---|
| **Hyperliquid outcomes (HIP-4)** | $25-30 million, nearly all sports (Thanksgiving NFL, NBA, soccer, season winners). Crypto bets about $400,000 | No fee to buy. A small fee when you sell or it settles (rough guess: about 7c per $100). No maker rebate | Terms name only the US, Ontario and sanctioned places. Outcome markets have a second "excluded places" list they can change at any time. Wallet only, no ID check | Same games as Polymarket: middles 0.2c apart. No cross-site lock after fees in 900 game looks. Crypto: section 3 | Dropped (gaps). Crypto speed: interesting for later |
| **Predict.fun** (BNB Chain) | about $15 million | Takers pay 0-2c a share (most at 50c). Makers free, plus a cut of taker fees | Not named in its ban list (US, UK, France, Belgium, Poland, Australia ...). Wallet only | Market data needs an API key, which needs an account, so not measured. Most activity is points farming for its PREDICT token (launch postponed 17 Nov, value of a point unknown) | Interesting for later, only as a token gamble |
| **Opinion** (BNB Chain) | Its own API shows $15,000 a day over 149 markets. DefiLlama's $6 million is not what the site itself reports | Takers up to 1c a share, **$0.25 minimum fee**, $5 minimum order | **No: its terms ban every EU / EEA country, Sweden by name** | - | Dropped |
| **XO Market** | Claims $4 million a day, but takes only $51 of fees a day, so most of that is not real trading | Makers free and get 35c of every $1 of taker fees | Not named (bans US, UK, France, Singapore, Ontario). Wallet only | Pays waiting orders in cash (USDC). Only 2 cash pools live, about $53 a day together (section 2) | Interesting for later (watch for new pools) |
| **Limitless** (Base) | $12,000 | Makers free, takers up to 3c | Not named | Every reward pool is $0 today (468 markets) | Dropped |
| **SX Bet** | $3 million, sports only | $0 on single bets | Blocks US, others unclear | Old order-book API switched off. Sports speed needs a fast score feed, and the free ones are late (`livelag.md`) | Dropped |
| **Myriad** | mostly play-money points | - | - | Real-money markets near $0 | Dropped |
| **Overtime / Thales** | $215,000, sports | built into the odds | - | API only for approved partners, "not for arbitrage or automated trading" | Dropped |
| **Drift BET** | $0 | - | - | Shut since the 1 Apr 2026 hack ($285 million stolen). Relaunched as Velocity DEX with no prediction markets | Dropped |
| **Probable** | - | - | - | Bought by Predict.fun | Dropped |
| **Truemarkets, Azuro** | - | - | - | No working public address found | Dropped |

Sweden, one line on tax (a guess, check with Skatteverket): gains on these crypto sites are most likely taxed like other
crypto (30c of every $1 of profit, on the K4 form). None of these sites has a Swedish licence, and a winning bet
with a gambling company outside the EU/EEA can also be taxable in Sweden.

## 1. Same game, two sites (Hyperliquid vs Polymarket)

On 27 Nov, 14:35-14:55 UTC, the script matched 116 Hyperliquid outcomes to the same Polymarket market by team names and
kick-off time: 36 NFL / NBA games, 18 soccer matches (win / draw / win) and 14 NFL / NBA season winners. It read both
order books 10 times, 2 minutes apart, at the same second. (12 soccer season-winner pairs were wrongly matched to
"runner-up" or "qualify" markets and are thrown out.)

| | Looks | Middle price gap, usual / biggest | Bid-ask gap: Hyperliquid / Polymarket | $ on the first 5 sell offers: HL / PM | Buy one side on each site, after fees |
|---|---|---|---|---|---|
| Games (NFL, NBA) | 360 | 0.24c / 1.03c | 0.09c / 1c | $730 / $35,500 | never paid (best: lose 0.76c per $1) |
| Soccer matches | 540 | 0.20c / 0.79c | 0.13c / 1c | $320 / $14,500 | never paid (best: lose 0.30c per $1) |
| Season winners | 140 | 0.05c / 1.83c | 0.10c / 1c | $200 / $290 | one pair paid 0.97c per $1 at the top of the book (Timberwolves NBA title), all 10 looks |

What it means: the two sites are wired together. Even if Polymarket charged no fee on these games, the best lock was
0.36c per $1, and only on a few dollars. The one season-winner lock pays about 24c on $25, and the money sits locked
until June 2027. That's nothing.

How long gaps last: there were none to time. The Timberwolves lock stood for the whole 20 minutes, which shows nobody
bothers to close a gap that small.

## 2. Sites that pay you to wait in line (cash rewards)

The idea: new sites often pay too much for people to leave orders on the book. A small bank can collect it if few
others do. I checked who pays in cash, not points, and read the real books.

- **XO Market (cash, USDC):** 10 pools listed, 8 already ended (each paid out $30-200 in total over Sept-Nov).
  Two are live:
  - "BTC 5min Pulse" (Bitcoin up or down in 5 minutes): **$50 a day**, from 20 Nov to 30 Nov 12:59 UTC, about $170 left.
    You must keep at least 4 shares (about $2) within 1.5c of the middle, on both sides while the price is between 30c
    and 70c. The book had nobody that close: the nearest orders were 41c / 58c. So one bot might take most of the $50
    a day. The catch is that this is the one market where a waiting order gets "picked off" by faster traders once
    Bitcoin moves. At 4 shares the worst loss on one fill is about $2. Rough guess: +$20-40 a day for the 3 days left,
    *if* XO's own score counts us and nobody else joins. Total upside about $100, then it ends.
  - "Largest company at the end of 2026": $2.22 a day, ends 27 Dec. Not worth it.
- **Limitless:** pays cash once a day in principle, but every market's reward is $0 today.
- **Opinion:** makers get half the taker fees, but the whole site trades $15,000 a day, and Sweden is banned.
- **Predict.fun:** the biggest points program. Most points go to people with orders near the middle, paid weekly. The
  points turn into a PREDICT token (70 million tokens for season 1). The launch was postponed on 17 Nov, and the value
  of a point is unknown (media guesses ranged 4c to 35c a point before the delay). The terms say points "have no money
  value". Needs an account to even read the market data, so not measured.
- **Hyperliquid:** no rewards for waiting orders on outcome markets.

What it means: the overpaid-liquidity trick exists, but right now it adds up to about $50 a day on one 5-minute Bitcoin
market, for 3 more days. That's a promotion, not an income. Worth a look only if XO starts new cash pools.

## 3. Hyperliquid's own crypto yes/no: does it lag the Hyperliquid price?

I recorded 100 minutes (27 Nov, about 14:10-15:50 UTC) of every Hyperliquid crypto outcome book and trade, plus the
Bitcoin, Ether, Solana and HYPE prices. Bitcoin fell from $61,477 to $58,924 in that time, so it was a busy, falling
market.

- Of 57 crypto outcomes between 3c and 97c, only 5 had a real book (bid-ask gap 1-2c). The rest had a 1c bid and a 99c
  offer (nobody there). The busy one is the daily Bitcoin yes/no, which settles at 06:00 UTC on Hyperliquid's own price.
  It traded about $4,100 in the 100 minutes, so roughly $60,000 a day.
- Hyperliquid's public feed sent a book snapshot only about every 12 seconds for these markets. Trades came in real
  time (about 0.45 s after they happened, from a US server). So the old-price check from the Polymarket speed box can't
  be done at under a second here.
- Backward look at the trade tape: takers who bought right after a 5-second price move their way (230 trades, $7,400)
  were up **+$78.52, about $1.06 per $100**, marked at the middle a minute later. Takers with no move lost $0.32 per $100,
  and takers against the move lost $1.35 per $100. Selling costs a fee and the bid-ask gap, so the $1.06 shrinks.
- That is the same thin speed signal as Polymarket's hourly windows (`fasthunt.md`: +$1.69 per $100 in the first second).
  It's 100 minutes on one falling afternoon. Found by looking.

Settled history: Hyperliquid's `settledOutcome` gives the result of any past outcome (700 read: 111 daily yes/no and 633
short Bitcoin bets, Yes won 398). But it serves no prices for settled markets. The free history site ironflow.sh shows only
24 hours without a key, and getting a key means signing up with an email. So no proper backtest of the daily yes/no
was possible.

## 4. Backward look: who wins on Hyperliquid outcomes

From loris.tools' public HIP-4 leaderboard (27 Nov) plus each wallet's last fills from Hyperliquid (up to 10,000 fills,
so about the last 2-4 weeks for the busy ones):

- **The biggest traders by volume are flat or losing.** The top wallet traded $119 million in its life for -$12,000.
  Its recent fills are all sports, buying at 17-45c in $20 pieces at 09-10 UTC. The next 8 by volume each lost about
  $2,000 on about $20 million. These look like market makers paid by nothing.
- **The winners are slower, picky takers:**
  - 0xc369... (+$112,000 lifetime): 10,810 recent fills, $581,000, 99 in 100 as a taker. It buys the favourite side of
    the **daily crypto yes/no** at 57-92c (middle 69c) in $24 pieces, mostly 09-13 UTC (17-21 hours before the 06:00
    settle). Recent closed profit +$20,900, about $3.60 per $100.
  - 0xb965... (+$110,000): $680,000 recent, a quarter as a waiting order. Crypto "touch" and "above" bets, buying at
    20-73c, +$21,300 recent (about $3.10 per $100).
  - 0x8d95... (+$224,000) and 0xbf2a... (+$145,000): few, large bets ($200-1,500 a fill) on about 20 markets, mostly
    sports and season winners. Big bettors with a view, not a repeatable small edge.
- What they share: they bet on Hyperliquid's own crypto outcomes, they take prices instead of waiting, and they hold to
  the result. The "buy the daily favourite at 57-92c" pattern is the one lead here. But it is one wallet over a few weeks,
  and we can't backtest it without price history (a free ironflow key would give 14 days).

## Ceilings (rough guesses)

| Idea | Most in an average day at best size | Money needed | Size where it stops growing | A bad day |
|---|---|---|---|---|
| HL vs Polymarket gaps | $0 (no gaps after fees) | - | - | - |
| XO "BTC 5min Pulse" cash pool | $20-40, for 3 days only (ends 30 Nov) | $20-50 plus a new wallet on XO | 4-10 shares a side (the pool is fixed at $50 a day) | -$10 (picked off on fast moves) |
| HL crypto speed (buy after a move) | $5-10 at $25 bets (about $1 per $100 on a few hundred trades a day, minus the selling fee) | $100-300 on Hyperliquid | about $50 a bet (books hold $200-700 near the top) | -$20 |
| Copy the daily-favourite wallet | unknown, maybe $5 a day at $25 bets (+$3.60 per $100 was his) | $100-300 | about $100 a bet | -$25 (a few favourites lose at 06:00) |
| Predict.fun points | unknown (token not launched) | $100+ | - | the token can be worth $0 |

## Verdicts

- Cross-site gaps (Hyperliquid, Opinion, Predict.fun vs Polymarket): **dropped.** Hyperliquid is wired to Polymarket.
  Opinion bans Sweden. Predict.fun needs an account to read.
- Cash rewards on new sites: **interesting for later.** XO's pools are real but tiny and short. Check `out_onchain_rewards`
  again if XO announces new USDC pools.
- Hyperliquid crypto outcomes (speed, daily favourite): **interesting for later, not a paper track yet.** The speed
  signal is about $1 per $100 and the feed only gives books every 12 s. The daily-favourite pattern needs price history
  first (a free ironflow.sh key would give 14 days, if Jan wants to sign up for one).
- Limitless, Myriad, SX Bet, Overtime, Drift, Probable, Truemarkets, Azuro: **dropped** (no money, closed, sold, or
  partner-only).

## What would change this

- A free ironflow.sh data key (Jan's email): then `daily` can price 700+ settled daily yes/no bets and test "buy the 57-92c
  favourite 17-21 h before" properly.
- New XO cash pools, or Limitless turning its rewards back on.
- Predict.fun's token launching at a price: then a points-per-dollar number could be worked out (needs an account to read
  the books, Jan's call).
- Hyperliquid listing faster crypto outcomes (hourly / 15-minute) with real books: the speed test could be redone with
  the trade tape.
