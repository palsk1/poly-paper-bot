# Handover: poly-paper-bot (read this first)

Owner: **Jan** (Sweden, Europe/Stockholm). This repo is a **paper-trading** experiment on Polymarket and Kalshi. It started 2026-11-03. Its goal is to find out which strategies would really make money before any real money goes in. Jan's line: "If we can show with 90% confidence that it works, I'm willing to invest" (e.g. $300 for arb).

`state/summary.md` is the live scoreboard, and `README.md` explains every track. This file covers the context, the rules of engagement and the decisions that aren't in the code.

## How to talk to Jan
- Use plain dollars and cents and simple words. **No percentages.** Math is hard for him, so show "cost $4.85, pays $5.00" instead of a rate. Light snark and humor are welcome.
- Ask clarifying questions before starting a bigger task instead of guessing.
- He reads on his phone, so keep reports short.

## Hard rules (never break)
1. **Paper money only.** Never place real trades.
2. Never ask for, hold or handle wallet private keys, Polymarket/Kalshi logins or exchange API keys. If real trading ever happens, the key lives only on a private server Jan controls. It never goes in this public repo or in chat.
3. The ntfy topic is a password. It lives only in the repo secret `NTFY_TOPIC`, never in files or commit messages (the repo is public).
4. **Rule changes:**
   - Bug fixes are allowed; always report them to Jan.
   - Do **not** change how these tracks trade (rules, budgets, thresholds) without Jan's OK: `mirror`, `favorites`, `mirror_unlimited`, `screener`, `arb`, `endgame` and `every_horse`. The `leader` settings need his OK too. Suggest changes and let him decide.
   - `claude` and `panic_fade` belong to Claude. Their rules may be tweaked from 2026-11-10 on, at most 1–2 small changes a day, each reported.
   - Approving or rejecting arb pairs in `arb_pairs.json` is allowed and must be reported.
   - **Lab tracks** (`"lab": true` in config: the 40 `w_*` wallets and their 40 filled-up `wb_*` twins (added on Jan's ask, 2026-11-08 evening), `consensus_*`, `sab_*` and the rule variants, added 2026-11-08) are **frozen until 2027-01-01**: bug fixes only, each reported. Changing their rules resets their evidence. Adding or removing lab tracks needs Jan's OK (he chose "about 60, not 100" on 2026-11-08).
5. Commits end with the Co-Authored-By trailer the session gives you.

## How it runs
- **GitHub Actions** (public repo, so it's free): `watch.yml` runs every 5 min, `daily.yml` once a day. Both write `state/` back to `main` and share a concurrency group, `bot-state`. The save step retries the push up to 4 times, because GitHub sometimes rejects a push with a server error.
- **The 5-minute timer is cron-job.org**, set up by Jan under his own account. Job "poly bot watch": POST to `.../actions/workflows/watch.yml/dispatches`, body `{"ref":"main"}`. Its auth is a fine-grained GitHub token, Actions read/write on this repo only, **expiring 2027-11-03**, and it emails Jan on failure. GitHub's own cron in `watch.yml` is only a backup, since GitHub's scheduler skips many runs. One-off 500/502 failure emails are normal blips.
- **ntfy pushes** go to Jan's phone. Since 2026-11-08 (Jan's ask, not to be overwhelmed): the daily push is a **top 10 by trust** (see README "The lab"), and only those 10 strategies send trade pushes until the next scoreboard (`state/top.json`). FLIP/SHORT/MISMATCH alerts always go out. Every strategy is still tracked and ranked in `summary.md`.
- **Dashboard (2026-11-08):** https://palsk1.github.io/poly-paper-bot/ , a phone page rebuilt by `pages.yml` after every watch/daily run (`dashboard.py` fills `dashboard.html`). Read-only on `state/`. README "How it runs".
- **Morning review:** a scheduled task named "Poly paper review" runs at 08:14 Stockholm in the cloud (it doesn't need Jan's PC). It reads the state, health-checks runs, reviews proposed arb pairs, writes Jan a short report and may make allowed fixes. Jan often replies to that report in its own chat, so other chats change this repo too. Check `git log` for recent non-`watch:`/`daily:` commits.
- **Claude's workspace cannot reach Polymarket, Kalshi or ntfy.** GitHub works. To see live data, start the `probe` workflow (`gh api -X POST repos/palsk1/poly-paper-bot/actions/workflows/probe.yml/dispatches -f ref=main -f inputs[what]=...`) and read its log. Its inputs are `all|kalshi|poly|endgame|events|activity|sells|exits|lab` and `wallet_<0xaddress>` (full wallet profile, walletcheck.py) (probe.py) and `arbtest|dryrun|discover` (bot.py); check `probe.yml`, since the list grows.

## Tracks (details in README.md)
| Track | Budget | Notes |
|---|---|---|
| mirror / favorites / mirror_unlimited | $20 / $20 / unlimited | Copy wallet **sabsabinxz** `0xd3ecb2aee0d65622da559ff356b00e8c2e626603` ("nothing ever happens" style: buys the boring outcome at 80–97c). `mirror_unlimited` measures how much money copying him needs. |
| screener | $20 | His style by rule, without him |
| claude | $50, refilled if it busts | Claude's own rules |
| panic_fade | $50, refilled if it busts | Buys the boring side after a 6c+ one-day scare |
| arb | $300 | Kalshi × Polymarket, **reviewed twin pairs only**. Holds to the end and flags MISMATCH. |
| endgame | $100 | 95–99c on markets already decided or nearly decided. Tiers: resolved, proposed (past_deadline and ending_soon dropped 2026-11-08 after the backtest). Includes a sell-early shadow test (records only). |
| every_horse | $100 | Buys the full outcome set when it costs less than the guaranteed payout |
| ladder | $100 | Added 2026-11-08 (Jan's "scale up arb" ask). NO on the stricter + YES on the looser of two markets in one Polymarket event (strike or deadline ladder). Needs Jan's OK for rule changes, like arb. |
| sharp_pinnacle | $100 | Added 2026-11-09 (Jan's idea). Buys a Polymarket game outcome 3c+ below Pinnacle's fair price (margin removed, the less favorable of two methods), pre-game, held to the end. Odds from Pinnacle's public website feed, no key (`sharp.py`, README "Sharp bookie price"). First scan: Polymarket sits ~1c above Pinnacle fair, so expect few trades. Claude's track, rule changes reported. |
| maker | $200 | Quotes both sides for Polymarket's liquidity rewards; fills from the trade tape, back of the queue. Summary splits rewards vs picked-off losses. Added 2026-11-08 (README "Maker"); rule changes need Jan's OK |
| lab (64 tracks) | $500 each, or no limit for copy tracks | 40 copied wallets, smart-money crowd, sabsabinxz variants, favorite bands, controls, momentum, panic and endgame variants, plus 2 fast-market tracks (`wx_forecast`, `crypto_late`). Listed in README "The lab". |

## Decisions and findings so far
- **Hosting:** stay on GitHub + cron-job.org while it's paper. A small always-on server (e.g. Hetzner, about €4/month) is only worth it once a strategy proves itself and real money is in play, mainly so the trading key lives somewhere private. Racing co-located high-frequency firms isn't winnable or needed: our edges last minutes to hours. **Before any real money:** check that Jan may legally trade on each site from Sweden (Kalshi especially).
- **Endgame (2026-11-05, Jan approved):** the day after the US midterms, "past deadline" election markets were still being counted. "WI-03 by 6–9%" fell from 97c to 62c. So election markets now only count in the resolved/proposed tiers (`weak_tier_skip_words`). The 20 open bets are held as they are. The budget fills fast now that the bot runs every 5 min.
- **Backtest (2026-11-08, `backtest.py`, PR #7):** replayed the rules on 125,712 finished Polymarket markets (Mar–Nov 2026, ~30,000 trades, 1c slippage + fees). Only `panic_fade_10c` came out ahead (+$3 per $100, not proven). Every favorite/endgame rule lost, even at 0c slippage. **Endgame "ending_soon" was dropped from the main `endgame` track (Jan approved):** it lost about $5-6 per $100, mostly weather, crypto-price and tweet-count buckets bought at 95c a day before the end (checked: real flips, not a data bug). **"past_deadline" was dropped too (Jan picked it, same day):** it lost $167 on 709 bets, so the main track now only buys once a result is resolved or proposed; the 20 open past-deadline bets are held to the end. Lab variants keep both (frozen). **Don't re-test this unless something new comes up** (e.g. real order-book history, or a filter that removes those bucket markets). Results: `backtest/report.md`.
- **Every horse:** it scans about 15,000 events every 2 hours. 3–5 sets a scan look cheap on the listed price, but **none is cheap on the real order book for 5 shares plus fees**. Only one ever passed 1c (Brazil central bank, January), and it failed the 15%-a-year bar. Conclusion so far: this trick doesn't pay for a slow bot. **Open question for Jan:** keep it as is, scan every 30 min, or repurpose the $100. He hasn't decided.
- **Arb:** the first real paper arb was Satoshi (Kalshi NO 94c + Polymarket Yes 2.9c, edge 2.5c). The pair review rejects most proposals: different deadlines, sources, "announced" vs "happened", and Kalshi rule text missing definitions.
- **Fast markets (2026-11-08, Jan asked for them):** weather temperature buckets and hourly crypto candles pay out within hours or 2 days. Two lab tracks, `wx_forecast` and `crypto_late` (README "Fast markets"). Weather now settles on **METAR reports from aviationweather.gov** (not Wunderground), and the rules link the exact query. aviationweather.gov cuts long answers short, so ask a few stations at a time. Open-Meteo and `data-api.binance.vision` work from GitHub Actions. ESPN returns 403 there. The same crypto model 3-30h out found nothing (the ladders are priced like the model), and already-decided weather buckets sit at 99.95c.
- **Dropped ideas (2026-11-08, `edges.py`):** negRisk conversion (sell a full set now for >$1) never beats fees on real books; holding rewards are real but tiny ($3.25/yr per $100, 255 long-dated markets).
- **Data audit (2026-11-09, after the endgame phantom fills):** `probe audit` checks past trades against Polymarket (buy prices vs the trade tape, copy timing vs the wallet's own trades, payouts vs final prices, stuck positions, marks vs bids, arb depth). Clean: cash/realized add up on every track, 40/40 payouts match, copies land 0-5 min after the wallet at about its price, nothing stuck. Fixed: no more "estimate" fills anywhere (buys or sells need a real book), copy tracks skip wallets holding both sides of a market (splits; some wb_/consensus tracks bought both legs before), arb repeat lots within an hour pay for the next shares on the book, open bets are marked at the best bid. `integrity()` runs after every watch/daily, writes `state/integrity.json`, a "Data check" section in summary.md, and pushes once per new problem. Maker rewards are a model and look high (~$24/day per $100): treat maker as unverified. **Maker pools (2026-11-09):** pool sizes change without notice (three of four were cut that day, e.g. $80 to $7 a day); the bot now re-reads each pool hourly from CLOB `/rewards/markets/{cid}`. YES and NO books really are one mirrored book (`probe rewardcheck`). Forum and research reports put real reward income at roughly $0.50-3 a day per $100, usually eaten by pick-off losses.
- **Polymarket API:** the data-api `v1` activity endpoints return HTTP 410. Use `v2` (`/v2/positions`, `/v2/trades`, `/v2/activity`). Trades for one market: `/v2/trades?condition_id=...` (`market=` gives 400). Reward pools: CLOB `/sampling-markets`. YES and NO books are one mirrored book.
- **Real money plan (2026-11-08):** trial runs until 2027-01-01, then Jan puts $300-500 into **one** strategy, depending on how sure we are. Rank by evidence (the trust score), not raw P&L. With 73 strategies, expect a few lucky fakes; the two `control_*` tracks show what luck looks like.
- **Proof math:** after k bad outcomes in n trades, the one-sided 90% Clopper-Pearson upper bound must be below the edge per share. With 0 bad outcomes you need about 2.3 / edge trades (≈90 at 2.5c, ≈230 at 1c). `summary.md` prints a proof line per track.

## Snapshot at handover (2026-11-08, from `state/summary.md`; check the file for the latest)
| Track | P&L | Open | Closed (won/lost) |
|---|---|---|---|
| arb | +$0.00 | 4 | 0 (locked $19.50, +$0.50 expected) |
| endgame | +$0.39 | 20 | 16 (16/0) |
| claude | +$0.42 | 9 | 3 (3/0) |
| panic_fade | +$0.38 | 8 | 4 (4/0) |
| screener | +$0.64 | 4 | 0 |
| mirror | −$1.51 | 4 | 0 |
| favorites | −$0.16 | 2 | 0 |
| every_horse | $0 | 0 | 0 |

With this few trades, results are mostly luck, so say so when reporting.

## Working on the code
- `bot.py` is one file with commands `watch | daily | summary | selftest | arbtest | dryrun | discover`. `config.json` holds every rule. `arb_pairs.json` is edited by the review, not by the bot.
- Before pushing: `python3 -c "import ast;ast.parse(open('bot.py').read())"`. Test risky changes with an offline mock (monkeypatch `bot.http_json`) or a `dryrun` probe.
- **Real-size check (2026-11-08):** every fill is also priced at $10/$25/$50/$100 on the same book (`real_size` in config, `rs` on positions, `rs_pnl` on closed trades). Records only; the trust ranking uses the $25 numbers. See README "Real money check".
- Fills are paper fills at real order-book prices (walking the asks for 5 shares) and include taker fees. Polymarket fee = rate × shares × p × (1−p); Kalshi fee = ceil(0.07 × C × P × (1−P)) to the cent. Kalshi order books list **bids only**.
