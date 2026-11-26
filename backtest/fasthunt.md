# Where else can our speed win? (26 Nov 2026)

Jan, 26 Nov: "Well who else can we battle with speed. Like retail or something if this doesn't work out."

Research only, paper only. No live changes. Tool: `fasthunt.py` (probe `fast_pm_<days>`, `fast_venues`), plus a
scratch replay of the speed box's own Kalshi recordings (25-26 Nov).

The question is the speed box's question, asked in other places: right after Binance jumps, is somebody still
selling at the old price, for how long, and is buying it worth anything after the fee?

## Short answer

| Rank | Where | What we measured | Rough most per day ($100-300 bank) | What Jan would need |
|---|---|---|---|---|
| 1 | **Polymarket ETH / SOL / XRP 5- and 15-minute windows** | Already recorded by the speed box; the 2 Dec score decides. New since 20 Nov: their fee is **0.01**, a fifth of the 0.07 we score with. At 50c that is about $3 per $100 back in our pocket | Unknown until 2 Dec. Same size as the Bitcoin bot's or better if the pros are thinner there | Nothing new: same box, same wallet. A "go" after the 2 Dec score |
| 2 | **Polymarket Bitcoin 5-minute (the bot we have)** | Polymarket's fee there fell to 0.05 on 20 Nov; we still score with 0.07 | About $0.50-1 per $100 better than our numbers say (section 4) | Nothing |
| 3 | Polymarket hourly up/down (BTC, ETH, SOL, XRP) | Old-price trades after a jump do happen, and slowly (BTC: half within 4 s; ETH 7 s; SOL / XRP 10 s). But they are worth almost nothing: **+$1.69 per $100 in the first second, about $0 from 2 s, losing after that** | $0-15 a day, a rough guess; could be $0 | A "go" to add it to the speed bot as a paper test (same code) |
| 4 | Hyperliquid outcome markets (HIP-4) | $42.6 million a day, but almost all sports. Crypto price bets: $228k a day (daily BTC yes/no about $80k), **no fee**, no taker wait | Not measured. Hyperliquid's own traders are the fastest crowd there is | A new recorder (Claude can build, listen only); Jan checks Sweden rules; later a separate wallet |
| - | Kalshi 15-minute crypto, all 7 coins | **Old prices left up after a Binance jump are traps: buying them loses $1-6 per $100 at every delay from 0 to 10 s** | $0 | - |
| - | Polymarket daily "above $X" ladders | Few jumps, lumpy: +$3 per $100 marked, -$18 held to the result | about $0 | - |
| - | Limitless, Myriad, SX Bet | Nobody there to beat: Limitless's busiest market has traded $547 in its life and its Bitcoin hourly $9; Myriad's busiest $5k; SX Bet is sports only | $0 | - |

So the honest map: the speed trick works best exactly where we already are (Polymarket's short crypto windows), and
the cheapest next step is the other coins on the same site, which the box already records and which now cost far less
in fees. The slow, retail-heavy places mostly have no money in them.

## 1. Kalshi 15-minute crypto, all 7 coins (speed box, 25-26 Nov)

The speed box reads Kalshi's top of book every second in each window's last 7 minutes, plus every trade, plus Binance
for each coin. 10,893 Binance jumps (a side's fair price moves 3c+ in 2 s) with 60 s to 7 min left.

Buy the side Binance jumped toward at Kalshi's ask, up to $25, Kalshi fee, held to the result. Asks 40-95c, per $100:

| Bought | right after | 1 s | 3 s |
|---|---|---|---|
| every jump | -$1.18 (5,820) | -$1.65 | -$2.01 |
| only if the ask is still the old one | -$2.17 (1,806) | -$0.73 | -$2.01 |
| only if the ask is 5c+ under the model | -$8.23 (870) | -$9.28 | -$8.46 |

- About 2 in 3 times Kalshi's ask had already moved by the first read after the jump.
- When an old ask was still up, it was usually right to be there: Kalshi pays on a 60-second average (CF Benchmarks),
  so a one-second jump moves the answer less than it seems. The model's "cheap" offers lose most.
- By coin the numbers jump around (SOL and DOGE above $0 in some cells, XRP -$13), with 40-90 bets a cell: noise.
- Somebody else took an old price within 15 s after 1,255 of 1,914 jumps (median 2.6 s). So there are racers, but
  they are buying offers that don't pay.
- This matches `kspeed.md` (11 Nov, Bitcoin only, 39,006 windows): Kalshi moves with Binance within seconds.

## 2. Polymarket hourly, 4-hour and daily crypto markets (21-25 Nov)

Whole trade lists of 480 hourly up/down windows (BTC, ETH, SOL, XRP; $10.5 million traded) and 220 daily "above $X"
markets (last 12 hours), against Binance 1-second prices. No 4-hour windows were found under the slug we tried.
Trade times are whole seconds.

A "stale" trade: on the side Binance just jumped toward, at or below that side's price just before the jump. Its worth:
the side's own price 30-120 s later minus what was paid minus the 0.01 fee ("marked"), and also held to the result.

| | Jumps | Jumps with old-price trades | First old-price trade, seconds after the jump (25% / half / 75%) | Old-price $ | Per $100 marked / held |
|---|---|---|---|---|---|
| BTC hourly | 5,531 | 2,196 | 1 / 4 / 15 | $124,031 | +$0.02 / -$8.29 |
| ETH hourly | 4,017 | 1,081 | 2 / 7 / 17 | $22,536 | -$0.05 / +$3.39 |
| SOL hourly | 1,186 | 185 | 3 / 10 / 20 | $2,672 | -$1.40 / +$5.40 |
| XRP hourly | 949 | 148 | 3 / 10 / 20 | $1,765 | +$3.19 / -$5.31 |
| BTC daily ladder | 345 | 115 | 1 / 5 / 12 | $11,792 | +$4.40 / -$19.72 |

If we had bought those old-price trades ourselves, $25 at most a jump, starting N seconds after the jump:

| Hourly windows, from | 0 s | 1 s | 2 s | 3 s | 5 s | 10 s |
|---|---|---|---|---|---|---|
| per $100 marked | +$1.69 | +$0.71 | -$0.09 | -$0.91 | -$1.54 | -$1.71 |
| per $100 held to the result | +$0.56 | -$0.52 | -$1.53 | -$1.70 | -$1.62 | -$2.17 |
| bought a day | $9,829 | $9,223 | $8,681 | $8,221 | $7,582 | $6,680 |

Reading it: the hourly windows are slower (old prices sit for seconds, not 0.4 s like the 5-minute windows), but the
old prices are mostly not wrong. A Binance jump moves an hourly window's fair price less, and the sellers who stay know
it. Only the first second shows a little, about the size of the luck. Paper fills, found by looking, 5 days.

## 3. Smaller sites (read live 26 Nov, 22:20 UTC)

- **Limitless** (Base): 421 live markets, almost all tiny. Busiest: an esports match, $547 traded in its life. Its
  "BTC Up or Down Hourly" had $9, its 5- and 15-minute windows $0. Books are wide (5-min BTC: 62c bid / 72c ask).
  It runs copies of Polymarket's up/down windows that settle on Binance candles. Nobody to trade against.
- **Myriad**: busiest order-book market about $5k in its life; most at $0.
- **SX Bet**: sports only (100 main-line markets). A speed edge in sports needs a fast score feed; the free ones are
  late (`livelag.md`, `tennis.md`), paid ones start around €500 a month.
- **Hyperliquid outcome markets (HIP-4)**: 305 outcomes, $42.6 million traded in 24 h, but nearly all season winners
  and NFL / NBA games. Crypto and price bets: $228k in 24 h; the daily BTC yes/no (settles 06:00 UTC on Hyperliquid's
  own BTC price) about $80k, ETH and HYPE dailies a few thousand dollars. Fees are zero for now and there is no taker
  wait. But this is Hyperliquid's own home crowd (the fastest crypto traders), the servers are in Tokyo (about 250 ms
  from Stockholm), and the public data keeps only the last 10 trades, so a test needs our own recorder.
- Not checked: Predict.fun ($14.7 million a day, BNB Chain) and Opinion ($6.3 million). Both list crypto markets.
- Sweden: these are crypto sites without ID checks that block the US and a few other places. Whether Jan may use
  any of them is his check before real money.

## 4. The lower fee on Polymarket (since 20 Nov 23:59 UTC)

Polymarket cut its crypto taker fee: Bitcoin 5- and 15-minute windows 0.07 → 0.05; every other crypto market
(ETH / SOL / XRP windows, hourly, daily) 0.07 → 0.01. Our speed scores and the real bot's estimate still use 0.07.
The fee is shares x rate x p x (1-p), so at 50c it was $1.75 per 100 shares and is now $1.25 (Bitcoin) or $0.25
(other coins). The 2 Dec score of ETH / SOL should use 0.01.

What it is worth: the fee per $1 spent is rate x (1 - price), so the cut gives back 2c x (1 - price) per $1 on
Bitcoin and 6c x (1 - price) on the other coins. For the speed bot's band (asks 40-95c, mostly 50-80c) that is about
**+$0.50 to +$1.00 per $100 on Bitcoin** (the week score's +$2.73 would be roughly +$3.30 to +$3.70) and about
**+$1.50 to +$3.00 per $100 on ETH / SOL / XRP** windows. The fee is a straight line in the price, so this needs no
re-run; the real fills will tell whether the live fee matches the list.

## What this means for Jan

1. Keep making the Bitcoin bot get filled (that thread), and score ETH / SOL on 2 Dec with the new fee. If either
   passes, it uses the same box, the same wallet and the same code. That is the cheapest second bot.
2. Hourly windows: a possible paper add-on later, but expect little.
3. Retail-heavy small sites: no money there to win. Hyperliquid's crypto outcomes are the only bigger new place, and
   they are full of pros, so they need a listen-only recorder before any opinion.
