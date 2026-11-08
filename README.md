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
| `every_horse` | Buys one share of every outcome in a multi-candidate event when the whole set costs less than it is guaranteed to pay. All-YES only on complete lists ("Other"/"No change" included); all-NO always pays at least n-1 | $100 |

## The lab (added 2026-11-08, runs until 2027-01-01)

62 extra paper strategies run next to the main tracks, so that by January we can pick **one** to put $300-500 into. They never push per trade; the morning ntfy is a **top 10 by trust**, and only those 10 send trade pushes the next day (alerts like FLIP / SHORT / MISMATCH always go out).

**How "trust" is ranked** (`config.json` > `ranking`): raw P&L over a few weeks is mostly luck, and with 71 strategies a few will look great by chance. So each strategy is scored by the *worst profit per $100 bet that is still plausible*: every finished trade's profit per dollar, plus one imaginary trade that lost everything (the disaster a "boring" strategy may simply not have hit yet), taking the low end of the confidence range with the bar raised for testing 71 strategies at once (90% for the whole family). **PROVEN** = that worst case is above $0 after 30+ finished trades. Only strategies ahead on 3+ finished trades can appear in the top 10. `summary.md` ends with the full ranking.

**Rules are frozen until 2027-01-01** (bug fixes only, reported), otherwise the evidence resets.

| Group | Tracks | What it tests |
|---|---|---|
| Copied wallets (40) | `w_*` | Each copies one wallet's new positions, 5 shares, sells when it sells. No cash limit (shows money needed). Skips positions under $20, copies more than 5c above the wallet's own price (too late), max 10 new copies a day per wallet. |
| Smart-money crowd | `consensus_2`, `consensus_3` | Buys when 2+ / 3+ of the 40 wallets hold the same side ($50+ each), sells when all of them have left |
| sabsabinxz variants | `sab_big`, `sab_hold` | Only his $1,000+ bets / copies his entries but ignores his early exits |
| Favorite bands | `fav_short_90_95`, `fav_short_95_98`, `fav_mid_80_90`, `fav_bigvol_85_95`, `no_only_90_97`, `yes_fav_85_95`, `fav_fee_free`, `fav_cut_losses` | Which price band, deadline and market size makes "buy the likely side" pay after fees. Studies of Polymarket (588M trades, 2022-2026) find favorites at 90c+ earn only a few tenths of a cent per dollar before fees, so most of these should hover near zero. $500 paper each |
| Controls | `control_random`, `control_longshot` | A coin flip, and longshots at 3-10c (studies: these lose). If a control ranks high, luck is winning and nothing above it is trustworthy |
| Price moves | `momentum_week`, `fade_rally`, `panic_fade_4c`, `panic_fade_10c` | Ride a 10c+ weekly rise / bet on a bounce after a 10c+ fall; panic fade with smaller and bigger triggers |
| Endgame variants | `endgame_strict`, `endgame_ending_soon`, `endgame_97`, `endgame_sell98` | Which endgame signal is safe, and whether selling at 98.5c beats holding |

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

## The arbitrage track, and the known traps it is built to avoid

Research (Nov 2026) found cross-site gaps are real but small: when both prices are fresh, a 3c+ gap shows up about 1 time in 20, break-even after both sites' fees is about 3c at mid prices, and money stays locked until the market ends. Most big "gaps" are stale quotes or markets that only *look* the same (different deadline, resolution source, or death/early-close clause, e.g. the Feb 2026 Khamenei markets settled very differently on the two sites). So:

1. **The daily job only proposes pairs** (`state/arb_candidates.json`): text-matched markets with close dates within 4 days, both rule texts attached.
2. **A pair is traded only after its rules were read side by side and approved** in `arb_pairs.json` (the morning Claude review does this; rejected pairs are never proposed again).
3. **Prices come from both live order books** (Kalshi lists only bids: buying YES at p = matching a NO bid at 1-p), with both taker fees (Kalshi 0.07 x n x p x (1-p) rounded up to the cent; Polymarket's category rate).
4. **Only takes it if** it nets >= 2c per share AND >= 15% a year (no locking money for years for pennies). 5 shares per lot, max 4 lots per pair.
5. **Holds both legs to the end** and flags a **MISMATCH** loudly if the two sites resolve differently.
6. **Proof line:** a clean arb earns about its edge per share; a mismatch can lose about the whole $1. So arbs only pay if mismatches are rarer than about the edge (2.5c edge -> under 2.5%). The summary shows how many clean finished arbs are needed to be 90% sure of that (about 90 at a 2.5c edge, if none mismatch).

## Endgame and every horse

- **Endgame** earns 1-5c per share on things that are already decided, in hours or days instead of months. The only way to lose is a "sure thing" flipping (a disputed result, a misread rule); the bot pushes **FLIP** when that happens. Results are kept per tier (resolved, proposed, past_deadline, ending_soon) so we can see which kind is actually safe. Proof line: a flip costs about the whole price, so flips must be rarer than the edge (about 2c -> under 1 in 50).
- **Sell-early test (endgame, records only):** for each open endgame position the bot notes the first time the bid would have filled us at 98c and at 99c (`shadow_sell_at` in config), and the bid after 24h held. When the trade pays out, it compares what each rule would have made vs holding, and how many days sooner the money would have come back. Nothing is actually sold; this is to decide later whether selling early is worth it.
- **Every horse** is pure math: if buying every candidate costs 96c and exactly one must win, that is 4c locked in. The catch is lists that are not complete (someone unlisted wins and every YES pays 0), so all-YES is only bought when the list has a catch-all outcome and is marked closed; open lists are skipped. The bot pushes **SHORT** if a set ever pays less than expected. Needs >= 1c per share after fees and >= 15% a year.

## How it runs

- `watch` workflow, every 5 min: an outside timer (cron-job.org) starts it through GitHub's API, because GitHub's own timer often skips runs for hours (its own ~10 min schedule stays as a backup). checks his wallet, copies opens/exits, take-profit/stop-loss, arb checks on approved pairs, endgame scan, panic and every-horse scan every 2 hours. If GitHub skipped the daily job, the watcher runs it. Sends ntfy pushes.
- `daily` workflow, ~06:17 Stockholm (backup 07:47): settles resolved markets, picks for the rule tracks, proposes arb pairs, writes `state/summary.md`, pushes the top 10 by trust. Runs once per day; a manual run forces a re-run.
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

## Files

- `state/summary.md`: human-readable daily report (start here)
- `state/tracks.json`: every paper position, arb, every-horse set and closed trade
- `state/events.jsonl`: everything that happened, one line per event
- `state/history.csv`: daily P&L per track
- `state/candidates.json`: what the rule tracks were choosing from
- `state/arb_candidates.json`: proposed Kalshi/Polymarket twin pairs waiting for review
- `state/his_book.json`: his current book and what holding all of it at minimum size would cost
- `state/wallet_snaps.json`: which tokens each copied wallet held at the last check (compact, used to spot new positions)
- `state/top.json`: today's top 10 by trust (only these send trade pushes)
- `state/his_exits.json`: every exit of his: sold early or held to payout, his avg vs sell price, days left before the end date, and (once the market pays) whether selling early helped him
- `arb_pairs.json`: approved and rejected twin pairs (edited by the review, not by the bot)

## Setup

Add a repository secret `NTFY_TOPIC` (Settings > Secrets and variables > Actions) with your ntfy topic name.
