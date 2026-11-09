# poly-paper-bot

**Paper trading only.** This bot never places real orders and holds no keys. It reads Polymarket's and Kalshi's public data and records pretend trades so we can see which approach would actually have made money.

## What it tests (each track has its own paper wallet)

| Track | What it does | Paper money |
|---|---|---|
| `mirror` | Copies every position sabsabinxz opens and closes, 5 shares each | $20 |
| `favorites` | Same, but only his entries at 80c or more | $20 |
| `mirror_unlimited` | Mirror that never runs out of money. Shows whether he has an edge and how much money copying him would need | unlimited |
| `screener` | His "boring outcome" style by rule, without him | $20 |
| `claude` | Claude's own rules (see `config.json` > `rules.claude.why`) | $50, refilled with $50 if it busts |
| `panic_fade` | Wildcard: buys the boring side right after a news scare drops it 6c+ in a day, sells on recovery | $50, refilled if it busts |
| `arb` | Kalshi x Polymarket arbitrage: YES on one site + NO on the other when both cost under $1 after both fees. Reviewed twin markets only, held to the end | $300 |
| `endgame` | Buys the 95-99c side of markets whose result is basically known: already resolved, result proposed (2h challenge window), past their deadline, or ending within 24h. Skips disputed markets and live sports; election markets only on resolved/proposed (not past_deadline/ending_soon, votes may still be counting) | $100 |
| `ladder` | Two markets of one Polymarket event where the stricter one can only say YES if the looser one does ("BTC above 120k" vs "above 110k"; "ceasefire by Dec 31" vs "by Mar 31"). Buys NO on the stricter + YES on the looser when both cost under $1 after fees: pays at least $1, or $2 if only the looser comes true. Same site, same rules text, so no cross-site mismatch | $100 |
| `maker` | Leaves buy and sell orders near the middle price to earn Polymarket's liquidity rewards, and counts every time it gets picked off (see "Maker" below) | $200 |
| `maker_tp`, `maker_tpsl`, `maker_flat`, `maker_short` | Maker with a twist (2026-11-09): same quoting, plus take profit, take profit + stop loss, never hold, or short-dated markets only (see "Maker" below) | $200 each |
| `every_horse` | Buys one share of every outcome in a multi-candidate event when the whole set costs less than it is guaranteed to pay. All-YES only on complete lists ("Other"/"No change" included); all-NO always pays at least n-1 | $100 |
| `fade_sure` | The mirror image of the dropped endgame signal: in weather markets that end within a day, buys the **cheap** side (2-10c) when the other side looks sure at 90-98c. Most bets lose 10-50c; a win pays about $5. Added 2026-11-08 (see "Fade the sure thing" below) | $25 |
| `sharp_pinnacle` | Uses Pinnacle (the bookie the pros bet with) as the fair price: buys a Polymarket game outcome when it costs at least 3c less than Pinnacle's odds say it's worth, after removing Pinnacle's margin and the fee. Pre-game, held to the result. Added 2026-11-09 (see "Sharp bookie price" below) | $100 |

## The lab (added 2026-11-08, runs until 2027-01-01)

64 extra paper strategies run next to the main tracks, so that by January we can pick **one** to put $300-500 into. They never push per trade; the morning ntfy is a **top 10 by trust**, and only those 10 send trade pushes the next day (alerts like FLIP / SHORT / MISMATCH always go out).

**How "trust" is ranked** (`config.json` > `ranking`): raw P&L over a few weeks is mostly luck, and with 73 strategies a few will look great by chance. So each strategy is scored by the *worst profit per $100 bet that is still plausible*: every finished trade's profit per dollar, plus one imaginary trade that lost everything (the disaster a "boring" strategy may simply not have hit yet), taking the low end of the confidence range with the bar raised for testing 73 strategies at once (90% for the whole family). **PROVEN** = that worst case is above $0 after 30+ finished trades. Only strategies ahead on 3+ finished trades can appear in the top 10. `summary.md` ends with the full ranking.

**Rules are frozen until 2027-01-01** (bug fixes only, reported), otherwise the evidence resets.

| Group | Tracks | What it tests |
|---|---|---|
| Copied wallets (40) | `w_*` | Each copies one wallet's new positions, 5 shares, sells when it sells. No cash limit (shows money needed). Skips positions under $20, copies more than 5c above the wallet's own price (too late), max 10 new copies a day per wallet. |
| Copied wallets, filled up (40, added 2026-11-08 evening) | `wb_*` | Twin of each `w_*`: starts by buying 5 shares of each of the wallet's (up to 30 biggest) open positions at that day's price, 10 per run, then copies new ones the same way. `w_*` vs `wb_*` answers: does it pay to jump into their existing book, or only to follow fresh trades? |
| Smart-money crowd | `consensus_2`, `consensus_3` | Buys when 2+ / 3+ of the 40 wallets hold the same side ($50+ each), sells when all of them have left |
| sabsabinxz variants | `sab_big`, `sab_hold` | Only his $1,000+ bets / copies his entries but ignores his early exits |
| Favorite bands | `fav_short_90_95`, `fav_short_95_98`, `fav_mid_80_90`, `fav_bigvol_85_95`, `no_only_90_97`, `yes_fav_85_95`, `fav_fee_free`, `fav_cut_losses` | Which price band, deadline and market size makes "buy the likely side" pay after fees. Studies of Polymarket (588M trades, 2022-2026) find favorites at 90c+ earn only a few tenths of a cent per dollar before fees, so most of these should hover near zero. $500 paper each |
| Controls | `control_random`, `control_longshot` | A coin flip, and longshots at 3-10c (studies: these lose). If a control ranks high, luck is winning and nothing above it is trustworthy |
| Price moves | `momentum_week`, `fade_rally`, `panic_fade_4c`, `panic_fade_10c` | Ride a 10c+ weekly rise / bet on a bounce after a 10c+ fall; panic fade with smaller and bigger triggers |
| Endgame variants | `endgame_strict`, `endgame_ending_soon`, `endgame_97`, `endgame_sell98` | Which endgame signal is safe, and whether selling at 98.5c beats holding |
| Fast markets (added later on 2026-11-08) | `wx_forecast`, `crypto_late` | Markets that pay out within hours or 2 days, priced with outside data. See "Fast markets" below |

Wallets were picked on 2026-11-08 from 1,242 leaderboard wallets (`bot.py discover`): profitable in at least two time windows, 5-400 open positions, mostly not 15-minute crypto up/down bets (a 5-minute bot is too slow for those), profit per dollar traded of at least 3c (traders with a view, not market makers). Weather, mentions and sports specialists are in on purpose, because their markets pay out within days, so they collect finished trades fastest. Four election-month hot hands test whether a hot streak lasts.

| Track | Wallet | Why |
|---|---|---|
| `w_tokor` | `0xa19cbababc312f9df185e49d7004c249ed1ade6b` | crypto (not up/down), profitable all-time |
| `w_flawfence` | `0x23d81ba9371e576015c1e562db09c689f56b0288` | politics, profitable all-time |
| `w_thereturnofdarthmaul` | `0x3a8aa345d5db7ec5138298c8c4f4540259be7699` | economics, profitable all-time |
| `w_underperformingforal` | `0xdbf16bcffa41bd95faec2640daa2c95ab2bd86b5` | crypto + politics whale, profitable all-time |
| `w_tunatyler` | `0xf1f9a438f2697381b4ac8eb283d6f4dd772d1245` | mentions + politics, profitable all-time |
| `w_dromedaryy` | `0x6575759174ad221bba9947bc3f18750ec769b198` | finance + tech, profitable all-time |
| `w_debased` | `0x24c8cf69a0e0a17eee21f69d29752bfa32e823e1` | economics + tech, profitable all-time |
| `w_jsram` | `0x83720820a8aa6c3f20ad71850e7a1a17d16c5223` | sports, profitable all-time |
| `w_0x448861` | `0x448861155279dbf833d041b963e3ac854599e319` | politics, profitable all-time |
| `w_cigarettes` | `0xd218e474776403a330142299f7796e8ba32eb5c9` | economics, profitable all-time |
| `w_rememberamalek` | `0x6139c42e48cf190e67a0a85d492413b499336b7a` | economics + mentions, profitable all-time |
| `w_lava_lava` | `0x629bc4a1e53e1d475beb7ea3d388791e96dd995a` | politics, profitable all-time |
| `w_dropper` | `0x6bab41a0dc40d6dd4c1a915b8c01969479fd1292` | all-rounder, profitable all-time in 5 categories |
| `w_wan123` | `0xde7be6d489bce070a959e0cb813128ae659b5f4b` | politics + sports, profitable all-time |
| `w_anoin123` | `0x96489abcb9f583d6835c8ef95ffc923d05a86825` | economics + finance, profitable all-time |
| `w_hauchn` | `0xf0ca28d5b0141f0a8e7b251dea80fd881cb166ed` | finance, profitable all-time |
| `w_betwick` | `0xc851cd9bee7d262afd78674f861f9f576a12cd2a` | finance + mentions, profitable all-time |
| `w_aghy` | `0xc3daa1bb9ce85866fb1a7c3a5d02816798e641fe` | economics, profitable all-time |
| `w_ecash` | `0x62cf46cd4c3af254dccfc37a7f93de265b4b5826` | tech, profitable all-time |
| `w_pako` | `0x71edffd0d70a1da823ff07a3c6fc81457294d338` | economics, profitable all-time |
| `w_bertapotamous` | `0x134a63b764ac7b008356e8db1857db94e6b09e42` | economics + mentions, profitable all-time |
| `w_hell0pia` | `0xbf93328f8b69273453228a82c913207731822fd7` | finance + tech, profitable all-time |
| `w_eightpenguins` | `0x3c593aeb73ebdadbc9ce76d4264a6a2af4011766` | mentions + tech, profitable all-time |
| `w_new_jeans` | `0xe2b1fc269d0c2e27da11fadd1d9596fe28227d2a` | economics + culture, profitable all-time |
| `w_vilgefortz` | `0x3c918a8ef8c379304f744592120cbb4d76149af7` | economics, profitable all-time |
| `w_albert_1953` | `0x777fae71d2ff9ec48a1213d48ba1d9d91024a1bb` | finance, profitable all-time |
| `w_youngalphagoat` | `0x9e88f359b9803e41420fbb13385c5ae1765c301c` | economics + finance, profitable all-time |
| `w_the_joker` | `0x9aeb534c42b58b21673d5e03e9da14fbd15b2729` | tech + economics, profitable all-time |
| `w_balerinacapuchina` | `0xd86d87914387111b47355e87aca7c032dbe5648d` | weather specialist (pays out daily) |
| `w_sbel` | `0xb22682e5efaaa5ae3f48c3b727cf78ae57c04163` | weather specialist (pays out daily) |
| `w_hellyeahtrader` | `0x1076773fc4639a7ad88bcfa5dbfee1dd3aa7c0aa` | weather specialist (pays out daily) |
| `w_dominus` | `0x5415c298dde8c84f4ba726d36b411df6e9a72a6e` | mentions specialist (pays out in days) |
| `w_blondbeast` | `0x852a61deac7872fff2c6a80ee82c059d6a8d3188` | mentions specialist (pays out in days) |
| `w_groth` | `0x71abe97b83eaba3f06cb04fd4d9a03ee37d2f015` | finance specialist, best profit per dollar traded |
| `w_jjo` | `0xc4086b708cd3a50880b7069add1a1a80000f4675` | finance specialist |
| `w_rabbitfoot1` | `0x10a6fadcbacd66330862206f6199b197e3ad4d8b` | sports specialist (pays out in hours) |
| `w_bigggggggg` | `0x511f9c771449162349795d17becf8b37031acbe1` | election-month hot hand: does it last? |
| `w_lpgb` | `0x1f5f9fa318fbda8350ac143b4df657287df850fa` | election-month hot hand: does it last? |
| `w_railcool` | `0x94c4fe3b18435aa92024c7c1589537fcda3f43ca` | election-month hot hand: does it last? |
| `w_monopoly_money` | `0x7ea7bcd658a253bfa78618a8e127cc73b54879ac` | election-month hot hand: does it last? |

Check the lab on live data without saving anything: run the `probe` workflow with `copytest`.

## Fast markets: weather and crypto (lab, added 2026-11-08)

Two lab tracks for markets that pay out within hours or two days, so they collect finished trades long before January. Both compare the market's price with a model built from free outside data and buy only when the model says a side is clearly too cheap after the fee. One bet per market group (one per city and day, one per coin candle), because buckets of the same day all move together.

| Track | Markets | Model | Buys when |
|---|---|---|---|
| `wx_forecast` | "Highest/lowest temperature in CITY on DATE" (about 50 cities, a high and a low each day). They settle on the airport's hourly METAR reports from aviationweather.gov (SPECI reports don't count) | ECMWF ensemble (51 forecasts, Open-Meteo), shifted by how far it was off at that airport over the last 24h, plus what was already observed today (a day's high can't go back down). Error allowance 1.1°C plus 0.4°C per day ahead | the model's chance beats the price by 12c+ after the fee, price 5-90c. Gaps over 45c are ignored as more likely our data error than the crowd's |
| `crypto_late` | Last 45 minutes of the hourly "Bitcoin/Ethereum/Solana/XRP/Dogecoin/BNB Up or Down" candles and the noon-ET "above $X" ladders. Both settle on Binance | the coin's hourly volatility over the last week, made 1.5x bigger for sudden jumps (Binance's own price feed) | the model gives a side 97+ in 100 and it still costs 96c or less, with 2c+ left after the fee |

Checked and left out (dry run on live data, 2026-11-08):
- **The same crypto model 3-30h out** ("the market overprices big moves"): the ladders matched the model within about 1c at every strike, so it would never trade.
- **Weather buckets the day's reports have already ruled out**: they were already priced at 99.95c, so the bots got there first.
- **Sports odds**: the free odds feed (ESPN) blocks GitHub's servers. Sports games are covered by the Kalshi vs Polymarket arb work instead.

Check them on live data without saving anything: run the `probe` workflow with `fasttest` (prints the model next to every price, and what it would buy). `fast`/`fast2`/`fast3` print the raw market and data shapes.

## The arbitrage track, and the known traps it is built to avoid

Research (Nov 2026) found cross-site gaps are real but small: when both prices are fresh, a 3c+ gap shows up about 1 time in 20, break-even after both sites' fees is about 3c at mid prices, and money stays locked until the market ends. Most big "gaps" are stale quotes or markets that only *look* the same (different deadline, resolution source, or death/early-close clause, e.g. the Feb 2026 Khamenei markets settled very differently on the two sites). So:

1. **The daily job only proposes pairs** (`state/arb_candidates.json`): text-matched markets with close dates within 4 days, both rule texts attached.
2. **A pair is traded only after its rules were read side by side and approved** in `arb_pairs.json` (the morning Claude review does this; rejected pairs are never proposed again).
3. **Prices come from both live order books** (Kalshi lists only bids: buying YES at p = matching a NO bid at 1-p), with both taker fees (Kalshi 0.07 x n x p x (1-p) rounded up to the cent; Polymarket's category rate).
4. **Only takes it if** it nets >= 2c per share AND >= 15% a year (no locking money for years for pennies). 5 shares per lot, max 4 lots per pair.
5. **Holds both legs to the end** and flags a **MISMATCH** loudly if the two sites resolve differently.
6. **Proof line:** a clean arb earns about its edge per share; a mismatch can lose about the whole $1. So arbs only pay if mismatches are rarer than about the edge (2.5c edge -> under 2.5%). The summary shows how many clean finished arbs are needed to be 90% sure of that (about 90 at a 2.5c edge, if none mismatch).

## Ladder pairs (added 2026-11-08)

The arb track needs two *different* sites to describe the same thing, and the review rejects most pairs because they don't. A ladder pair needs no review: both markets sit in the same Polymarket event, with the same rules text except the strike or the deadline, so one can't say YES without the other.

- **Daily** (`state/ladder_pairs.json`): scans ~24,000 yes/no markets and keeps only families where (1) the question and rules text differ only in the strike or the "by <date>" deadline, (2) the direction is clear from the words ("above", "at least", "by"; "hit/reach/dip" only with the ↑/↓ labels), (3) it isn't a range, an exact count or a "top N" rank, (4) the deadline in the question agrees with the market's end date, and (5) the crowd's prices agree with the direction (the stricter market never trades more than 10c above the looser one). One-winner (negRisk) events are left to every_horse. On 2026-11-08 this kept about 6,000 pairs.
- **Every 30 min** (watch): fresh listed prices for all of them in one batch call; anything close is priced on both live order books for 5 shares plus fees. Buys at >= 2c per share and >= 15% a year, one lot per pair, at most 20 open.
- **Settles** when both legs have paid; a pair paying less than $1 pushes **SHORT** (it means we misread a family).
- **First live look (2026-11-08):** of 6,000 pairs, 30 were not overpriced and the best paid 1.3c per share after fees (StandX FDV above $1B / above $100M). So gaps are real but usually below the 2c bar; the track waits for the spikes.

Research that found nothing (2026-11-08, `arbhunt.py`, run with the `probe` workflow, `hunt_*` inputs): Kalshi vs Polymarket **game winners** (NFL, NBA, NHL, college basketball) match cleanly by team codes but cost more than $1 after both fees on all 160 checks (usually by about 4c, never closer than 0.8c); the **same question listed twice** on Polymarket never had a gap; and the **104 rejected pairs**, priced both ways, showed gaps of at most 2.4c, and in every case checked the gap was on the side the rule difference makes unsafe (the market prices that risk in).

## Endgame and every horse

- **Endgame** earns 1-5c per share on things that are already decided, in hours or days instead of months. The only way to lose is a "sure thing" flipping (a disputed result, a misread rule); the bot pushes **FLIP** when that happens. Results are kept per tier (resolved, proposed, past_deadline, ending_soon) so we can see which kind is actually safe. Since 2026-11-08 the main track only uses resolved and proposed: the backtest showed ending_soon and past_deadline both lose (see `backtest/report.md`); only lab variants still trade them. Proof line: a flip costs about the whole price, so flips must be rarer than the edge (about 2c -> under 1 in 50).
- **Sell-early test (endgame, records only):** for each open endgame position the bot notes the first time the bid would have filled us at 98c and at 99c (`shadow_sell_at` in config), and the bid after 24h held. When the trade pays out, it compares what each rule would have made vs holding, and how many days sooner the money would have come back. Nothing is actually sold; this is to decide later whether selling early is worth it.
- **Every horse** is pure math: if buying every candidate costs 96c and exactly one must win, that is 4c locked in. The catch is lists that are not complete (someone unlisted wins and every YES pays 0), so all-YES is only bought when the list has a catch-all outcome and is marked closed; open lists are skipped. The bot pushes **SHORT** if a set ever pays less than expected. Needs >= 1c per share after fees and >= 15% a year.

## Fade the sure thing (added 2026-11-08)

The backtest showed "sure" 93-98c favorites in weather, crypto-price and tweet-count buckets a day before the end flip far more often than the price says (weather: 292 flips in 2,104 bets, where 95c implies about 105). An academic study (arXiv 2602.19520) found the same: short-horizon weather prices are too extreme. So `fade_sure` buys the other side, 5 shares on the real order book, held to the result. Backtest (`backtest/fade.md`, 2026-11-08): weather 2,103 bets, the cheap side won 350 times at about 6c each, +$121 per $100 staked at +1c slippage, +$73 at +3c, about the same in the older and newer half. Crypto-price and post-count buckets came out about even, so the track is weather only. `python3 backtest.py btfade` (probe input `btfade`) replays it on history and writes `backtest/fade.md`. History has no order book, so the live track is the real test: thin bucket books may ask several cents more than (1 - favorite price). No FLIP alerts for this track, since losing most bets is the plan.

## Sharp bookie price (added 2026-11-09, `sharp.py`)

Jan's idea: big bookmakers spend a fortune on models and on taking bets from pros, so their odds are a good "fair price". If Polymarket sells the same outcome for less, buy it.

- **Source:** Pinnacle, the sharpest big bookie. Its official API closed to the public in July 2025, but its website reads odds from a public JSON feed (`guest.api.arcadia.pinnacle.com`, no key, no account), which works from GitHub Actions. The bot reads it every 15 minutes, a few calls per sport. Paid alternatives if it ever breaks: The Odds API (free 500 calls a month, Pinnacle "may be delayed"), OddsPapi (free 250 a month, has history), pinnodds.
- **Removing the margin:** a bookie's chances add up to a bit more than 100 per 100 (Pinnacle about 2-4 extra on a game). We take it out two ways (scale everything down evenly, or the "power" way that trims longshots more) and always use the one that is worse for the side we buy.
- **Matching:** Polymarket game events (moneyline markets) to Pinnacle matchups by start time (within 75 minutes) and both team names (`sharp.name_score`). Soccer has home/draw/away; Polymarket's "Will X win?" / "draw?" Yes and No shares are both priced. In-play games are skipped. Tennis is left out (retirement rules differ).
- **Rule:** buy 5 shares when (fair chance) minus (real ask for 5 shares) minus (fee) is at least 3c, and at most 15c (a bigger gap usually means wrong match or late news). Pinnacle's max bet on the game must be at least $250 (low limits mean a soft line). One bet per game, held to the result. Fills are real order-book fills like every other track.
- **First live look (2026-11-09, `probe sharp_scan`):** 72 games matched (27 soccer, 19 esports, 13 basketball, 12 hockey, 1 NFL), 252 buyable sides. Polymarket's listed asks sat a median 1.3c ABOVE Pinnacle's fair price in every sport, and only 1 side was even 1c cheaper after the fee (0 at 3c). That fits what traders report: the big market makers on Polymarket and Kalshi copy Pinnacle within a second. So expect very few trades; the track measures how often a slow bot still catches a gap.
- **Backtest:** `python3 sharp.py bt` (probe input `sharp_bt`) replays the rule on finished Polymarket soccer games in the top 5 European leagues against Betfair Exchange closing odds from football-data.co.uk (free; Pinnacle's columns there went blank in July 2025). Result (2026-11-09, 1,230 games): Polymarket was within half a cent of Betfair fair on most outcomes and just as accurate; the 3c rule found 14 bets and came out -$0.04 at 1c slippage. No edge for a slow bot. Details: `backtest/sharp.md`.
- **Probe inputs:** `sharp_scan` (live gaps, no trades), `sharp_bt`, `sharp_probe*` (raw API shapes), `fasttest` (dry run of all fast tracks incl. this one).

## Maker: get paid to quote (added 2026-11-08)

Polymarket hands out about **$190,000 a day** in "liquidity rewards" to anyone who leaves buy and sell orders close to the middle price (each market has its own daily pool, a max distance from the middle and a min order size). The `maker` track ($200 paper) tries to collect that the way a slow 5-minute bot could:

- Up to 4 markets at a time, picked every hour by estimated reward per dollar. Skips markets ending within 7 days or already past their date (insiders know the answer), sports, middle price outside 15-85c, and markets where nobody else is quoting near the middle (we would be first in line to get run over).
- Posts a YES bid and a YES ask (= a NO bid) of 50 shares at the current best prices, at the **back of the queue**. Re-posts every run.
- **Fills come from the real trade tape:** an order fills only if a trade went through our price, or more traded at our price than was queued ahead of us. Quotes sit unchanged between runs, so news in between hits us like it would hit a real slow bot.
- **Rewards** use Polymarket's own formula against everyone else in the public book, assuming the others are as two-sided as possible (gives us the smaller share), credited only for the minutes since the last run (max 15).
- A YES from one fill and a NO from the other merge back into $1. Holding stops growing at 2 lots per side. After 3 days, or when a market leaves the list, leftovers are sold at the bid with the taker fee: that is one finished trade for the ranking.
- `summary.md` and the dashboard split the result into **rewards** (a model, likely too high) and **price moves** (getting picked off, spreads, leftovers: real order-book money), the latter as *locked in* and *on what it still holds*. It only works if the rewards beat the price moves.
- **Variants (2026-11-09, Jan: "can't we exit with profit?")**, $200 each, `maker` stays the control. All sell at the real bid with the taker fee, never on an empty book, and keep quoting afterwards:
  - `maker_tp`: sells what it holds once it is up 3c a share after the fee.
  - `maker_tpsl`: the same, plus a stop loss at 5c a share down.
  - `maker_flat`: never keeps a bet, sells every fill on the next run. Pays the spread each time, but a big price move can't hurt it.
  - `maker_short`: only markets ending within 30 days (not within 7).
  Every variant scores its rewards as if it were alone in the book, so the reward numbers are as optimistic as `maker`'s; compare the price-move numbers.

Why it might fail: a first live test (`edges.py`, 45 markets, 2026-11-08) estimated about $35 a day of rewards per $100 of quotes, but replaying the last day of prices said a slow bot would have lost about $44 per $100 to getting picked off. Both numbers are rough (one is a snapshot, the other a price replay without the order book), so this track is the real test. Rewards may also have payout minimums or limits we can't see from the public data.

## Ideas tested and dropped (2026-11-08, `edges.py`)

- **negRisk conversion** (sell a whole multi-outcome set right now for more than $1, by turning one NO into a YES of every other outcome): 5,681 events checked; on the real books with fees the best was -0.05c a share. Market makers keep this shut.
- **Holding rewards**: real (Polymarket pays $3.25 a year per $100 held, sampled hourly) but only on 255 long-dated markets (2028 elections, "before 2027" markets). On a $300 stake that is about $10 a year, so it is a small bonus for whichever strategy holds those markets, not a strategy.

## Backtest (past data)

`backtest.py` replays the rule tracks on finished Polymarket markets (default: everything that ended since 2026-03-01, volume over $20,000, no sports), hour by hour, using the bot's own picking code and only prices known at that moment. Fills are the history price plus 1c (also run at 0c and 2c), plus the market's taker fee. Copy tracks replay the wallets' real trades a few minutes late at their price plus 1c. Results: `backtest/report.md`.

- Run it with the `backtest` workflow (manual, commits the report to main) or the `probe` workflow with `btrun` (report in the run log and artifact). The download (~2 hours the first time) is cached between runs.
- Can't be replayed: arb and every horse (no old order books), endgame's resolved/proposed tiers (no proposal history), consensus.
- The 40 copied wallets were picked because they won in this same period, so their backtest flatters them.

## How it runs

- `watch` workflow, every 5 min: an outside timer (cron-job.org) starts it through GitHub's API, because GitHub's own timer often skips runs for hours (its own ~10 min schedule stays as a backup). checks his wallet, copies opens/exits, take-profit/stop-loss, arb checks on approved pairs, endgame scan, panic and every-horse scan every 2 hours. If GitHub skipped the daily job, the watcher runs it. Sends ntfy pushes.
- `daily` workflow, ~06:17 Stockholm (backup 07:47): settles resolved markets, picks for the rule tracks, proposes arb pairs, writes `state/summary.md`, pushes the top 10 by trust. Runs once per day; a manual run forces a re-run.
- `dashboard` workflow, after every watch/daily run: rebuilds the phone dashboard (`dashboard.py` + `dashboard.html`) and publishes it on GitHub Pages at https://palsk1.github.io/poly-paper-bot/. It reads `state/` and never writes it, and uses the same scoreboard code as `summary.md`. Shows the top 10, a profit curve per strategy, trust vs the luck (control) tracks, open bets, and the cost of copying late and of bigger bets. One-time setup: Settings > Pages > Source: GitHub Actions (until then it skips the deploy). Test locally with `python3 dashboard.py --offline` and open `site/index.html`.
- `selftest` workflow (manual): checks the APIs and sends a test push. `probe` workflow (manual): prints raw API shapes, no pushes.

Fills are paper fills at the real order book price (taking the ask, selling at the bid), including taker fees.

## Real money check (added 2026-11-08)

Paper trades are 5 shares (about $5), which nearly always fit at the best price. The $300-500 in January means $10-$100 a trade, which eats deeper into the order book. So every paper fill is **also priced at $10, $25, $50 and $100** on the same live book (`config.json` > `real_size`). It is records only: it never changes what a track buys or sells, so the frozen lab rules and their evidence are untouched.

- **Buying:** a limit order that never pays more than the best ask + 2c (and never 99c+). In a thin book only part of the stake fills; that is recorded, not hidden.
- **Fees:** the same taker fee as the paper fill, on the bigger amount (Kalshi's rounds up per order).
- **Selling early:** walks the real bids; shares the bids can't take are valued at half the worst bid.
- **Payout:** a resolved market pays the same per share at any size.
- **Arb and every horse:** the same number of shares on every leg, as many as the stake allows while the edge stays above `min_edge` after both books and both fees.
- **Ranking:** the trust ranking (and so the top 10 on the phone) uses the $25 numbers (`rank_size_usd`). Trades from before this change have no book data and count with their paper numbers. `summary.md` shows paper vs each stake, and how much of a $100 order the book held on average.
- **Live check now:** the `probe` workflow with `depthtest` re-prices every open position at each stake on today's books.

Not modeled: our own orders moving the price for the next 5-minute check (the paper bot never moves it), and deposit/withdrawal costs.

## Late fill check (added 2026-11-08)

Paper fills happen at the exact moment the bot reads the book. A real order lands a little later, and a fast market may have moved by then (Jan's earlier bot looked great on paper and lost live for exactly this reason). At the end of every run, each buy from that run is priced again on a fresh book, with the same shares, at least 30 seconds later (`config.json` > `late_fill`). The result is stored on the position as `late` (`s` = seconds later, `px` = the price then, or null if the book was empty). `summary.md` shows per strategy how much more (or less) the late fill would have cost per $100. Records only: no trade or rule changes. Kalshi legs aren't re-checked.

## Data check (added 2026-11-09)

After the endgame "phantom fills" (paper buys on empty order books), every watch and daily run checks the bot's own numbers: cash = money put in - open bets + profit on every track, realized profit = the finished trades, every buy was a real order-book fill, no track holds both sides of one market, no open bet stuck on a closed market (daily), and no suspiciously perfect record (30+ trades, 0 losses). Results go to `state/integrity.json` and the "Data check" section of `summary.md`; a new problem sends one ntfy alert. Maker rewards are flagged when the model pays more than $5 a day per $100 (it can't be checked against real payouts).

For a deeper look, the `audit` probe compares past trades with Polymarket's own records: buy prices vs the trade tape, copy timing vs each wallet's own trades, payouts vs final prices, open bets at listed price vs best bid, and the depth behind repeated arb lots.

## Market data recorder (added 2026-11-08)

`recorder.py` saves live market data so future backtests can replay real order books instead of guessing slippage. The idea is from a Reddit bot builder who recorded data for 3 months before testing strategies. The `recorder` workflow runs nonstop, about 5h40m per run, with the next run queued, and saves:

- **every minute:** the books (top 15 levels) of every Kalshi and Polymarket market closing within 3 hours (15-minute and hourly crypto, commodities, weather; no sports), the Kalshi trade tape for them, and Binance spot prices
- **every 5 minutes:** the Polymarket books of every open position of every track, the reviewed Kalshi arb tickers, and the Polymarket trades of the fast markets

A book is saved only when it changed. One gzipped JSON-lines file per UTC hour is uploaded to a GitHub release `data-YYYYMMDD`, so the repo itself stays small. Records only, no trading. Test it with the `probe` workflow `rec_once` (one pass) or `rec_6` (6 minutes).

## Files

- `state/summary.md`: human-readable daily report (start here)
- `state/tracks.json`: every paper position, arb, every-horse set and closed trade
- `state/events.jsonl`: everything that happened, one line per event
- `state/history.csv`: daily P&L per track
- `state/candidates.json`: what the rule tracks were choosing from
- `state/arb_candidates.json`: proposed Kalshi/Polymarket twin pairs waiting for review
- `state/his_book.json`: his current book and what holding all of it at minimum size would cost
- `state/wallet_snaps.json`: which tokens each copied wallet held at the last check (compact, used to spot new positions)
- `state/top.json`: the current top 10 by trust (only these send trade pushes). The daily scoreboard sets it and watch re-ranks it every hour (also rewriting `summary.md`), so a strategy that turns into a loser loses its pushes within the hour.
- `state/his_exits.json`: every exit of his: sold early or held to payout, his avg vs sell price, days left before the end date, and (once the market pays) whether selling early helped him
- `backtest/report.md`: last backtest on past markets (`backtest.py`)
- `arb_pairs.json`: approved and rejected twin pairs (edited by the review, not by the bot)

## Setup

Add a repository secret `NTFY_TOPIC` (Settings > Secrets and variables > Actions) with your ntfy topic name.
