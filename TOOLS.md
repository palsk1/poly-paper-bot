# Tools we already have (read this before building anything)

One line per tool or dataset: what it does, how to run it, where it came from. If you add or change a tool,
add or fix its line here in the same PR. Claude's workspace can't reach Polymarket/Kalshi, so almost everything
runs through the **probe** workflow (`gh api -X POST repos/palsk1/poly-paper-bot/actions/workflows/probe.yml/dispatches -f ref=main -f inputs[what]=<input>`)
and you read the result in the run log. All of it is paper only.

## Data

| Dataset | What's in it | How to get it |
|---|---|---|
| **Whole events (DEFAULT for anything with several choices)** | bt_cache plus every missing choice of each event (any volume) with price history, and a list of complete events. Load with `ideas.load_full()` (markets, hist, complete event ids) or `ideas.load_screen_set()` (in-sample, non-sports, complete events only) | `ideas.fetch_events()` (probe `btideasfetch`, run on ref=main; files `bt_cache/events.json.gz`, `fill_hist.json.gz`) (PR #39) |
| **bt_cache** (main backtest data) | **Warning: alone it only has markets whose FINAL volume passed $20k, so multi-choice events (weather buckets most of all) miss many losing choices and look too good. Use whole events above.** ~126k finished Polymarket markets since 2026-03-01 with volume > $20k: question, answers, start/end/close times, final prices, fee, event id; plus outcome-0 price history (12-hourly, hourly in the last 2 days) and the copied wallets' trades | `backtest.py fetch` (probe `btfetch`). Lives in the Actions cache `bt-cache-*`. **Start bt* probes with ref=main**, caches saved on other branches can't be shared (PR #7) |
| small-market sample | ~12k tiny markets ($1k-20k volume), 12-hourly history | `calib.py fetch_small` (probe `btcalibsmall`, PR #30) |
| rule text + UMA statuses | rule text, resolution source and proposed/disputed history for all ~124k cached markets (`bt_cache/rules_meta.json.gz`), plus every $1k-20k market that sat unpaid 1+ day past its end with hourly history (`rules_small_*.json.gz`) | `rules.py fetch` / `fetch_small` (probes `btrulesfetch`, `btrulessmall`) |
| Kalshi 15-min crypto | Kalshi 15-minute crypto windows, trades and history; per-second trade tapes of the last 5.5 min + Binance 1-second spot (`bt_cache/kf/`) | `kcrypto.py fetch [days]` (probe `kc_fetch`, `btkcfetch`, PR #31); `kfast.py fetch [days]` (probe `btkffetch`) |
| Live recordings | Order books, trades, spot prices every minute for fast markets; every 5 min also AAA + GasBuddy live gas prices and the Kalshi AAA gas ladders (`gas` lines, PR #40), hourly files on GitHub releases `data-YYYYMMDD` | `recorder.yml` / `recorder.py` (PR #12). Use it to replace guessed slippage once enough is recorded |
| Holdout | Markets ending **2026-11-10 or later**. Never look at them before 2026-12-21 | `btcheck.py holdout` (probe `btholdout`), see `backtest/PROTOCOL.md` |

## Testing ideas on history

| Tool | What it does | Run |
|---|---|---|
| **`exam.py` (EVERY new lead sits this before it's reported)** | **The shared exam + the list of everything tried.** Give it a bet list (event, time, $ paid, $ back) and it prints one scorecard in plain words, the same for every idea: profit per $100, luck range, how many bets are really separate (same event, or same day when losses bunch, count once), first vs second half, worst case per $100 after one more made-up disaster and a bar raised for every idea we ever tried, how many more bets it needs and by when, and one of the dashboard's five verdicts. `exam.fills(signals)` first re-prices chart signals at the first real buy on the trade tape (+1c + fee, $25 a bet, counts signals nobody could buy). `exam.score(bets, name, tries=N)` adds a line to `backtest/ledger.json` (page `backtest/ledger.md`; a probe prints `LEDGER ROW {...}` to paste in). `exam.power(bets, n)` says if a planned test can even tell real from worthless. `census.tape_check(..., name=)` prints the card too | `import exam` in a dig; `python3 exam.py selftest`, `ledger`, `file bets.json "name" [tries]`, `tracks` (same exam for every live track: can it be proven by 1 Jan? -> `backtest/exam_tracks.md`); probe `exam_tapetest` (live check of the real-price step), `exam_selftest` |
| `backtest.py` | Replays the bot's own strategy code hour by hour on bt_cache, incl. wallet copies. Report `backtest/report.md` | probe `btrun`, `btdiag`, `btfade` (PR #7, #10) |
| `btcheck.py` + `backtest/PROTOCOL.md` | Sanity checks of the backtester (fair-coin world, second simulator, random twins, pessimistic costs, walk-forward) and the **test-before-results rules every new lead must follow**. Report `backtest/checks.md` | probe `btcheck`, `btcheckself` (PR #32) |
| `winners.py` | **What do winning wallets do, and which kinds of bet pay for anyone?** Puts every wallet in informed.py's trade lists through the exam (luck yardstick: wallet names shuffled), picks winners on the first half and judges them on the second, then grades kinds of bet (topic x Yes/No x price x time left) at the price a slow follower really got 5-65 min later. `drill` replays a kind as a rule a bot could run (first time in the band, next real $100+ buy, by month and by week). Report `backtest/winners.md` | probe `win_run`, `win_drill` (any branch; reads main's bt_cache, saves nothing); `python3 winners.py selftest` |
| `calib.py` | Calibration by market kind: price x time-before-end x topic, YES vs NO, event-clustered bands. Has the **topic tagger** (`calib.topic`) and snapshot code. Report `backtest/calib.md` | probe `btcalib` (PR #30) |
| `rules.py`, `fineprint.py` | Fine-print hunt: rule-text flags (official only, credible reporting, things that don't count...) vs UMA disputes and prices, limbo after the end date, volume-bias check. `fineprint.trouble_score(title, rules)` = 0-7 dispute warning light (0 flags 0.4 disputes per 1,000, 4+ flags 51). Report `backtest/rules.md` | probe `btrulesrun` |
| `ideas.py` | **Idea machine / cheap screener**: a catalog of features (wording, age, siblings, price path, ...) each tied to a bias, crossed with topics, side, price band and horizon; screened vs random twins on two halves with a many-ideas correction and placebo features. Other threads can plug in a feature with `@ideas.feature(...)`. Report `backtest/ideas.md`, method `backtest/IDEAS.md` | probe `btideas`, `btideasself`, `btideasdrill_<preset>` (split one idea by month/price/question), `btideasvolbias` (checks the cache for missing losing choices) (PR #38) |
| `informed.py` | **Informed-trader hunt**: full trade lists of ~20k finished markets from whole events; scores wallets on how far the price moves their way 1h/6h/24h after our 5-min delay, split-half test vs same-size random wallets, copy test at the real next buy + 1c + fee, and the "new wallet, big bet, quiet market" pattern with real wallet age. Report `backtest/informed.md`, wallets that pass in both halves `backtest/informed_wallets.json`. Cache `bt_cache/inf_tapes.json.gz` | probe `btinf_fetch`, `btinf_run`, `btinf_all` (ref=main), `btinf_peek` (API shapes) |
| `kcrypto.py` | Backtest of Kalshi 15-min crypto maker bids; report `backtest/kcrypto.md` | probe `kc_run`, `btkc` (PR #31) |
| `kcrypto.py depth` | **Pro-style check of one Kalshi 15-min maker rule** (default kc_maker_safe): price 1-2 min after our bid (filled vs all), losses bunched by 15-min window and day, a 90% pass bar for the live track (whole-window resampling, 'no edge' vs 'backtest right'), and a $300 pot with $10 bets on whole days. Report `backtest/kcdepth.md` | probe `btkcdepth` (fetch + depth) |
| `kfast.py` | Second-by-second replay of Kalshi 15-min crypto (trade tapes + Binance 1-s spot): fast cancels, last-seconds entries, Kalshi incentive scan; report `backtest/kfast.md` | probe `btkf`, `btkfrun`, `btkf2`, `kf_incentives`, `kf_selftest` |
| `kfastlive.py` | Live paper bot for the last 45 s of Kalshi 15-min crypto (2 book reads, real asks for 10/100 contracts, maker queue + tape fills); scoreboard `state/kfast_live/report.md` | workflow `kfastlive.yml`; probe `kfl_once`, `kfl_loop_<min>`, `kfl_report` |
| `econ.py` | Economic data markets (Kalshi CPI, core, CPI y/y, claims, unemployment, payrolls, GDP) vs free forecasts (Cleveland Fed nowcast, Atlanta Fed GDPNow, FRED/ALFRED first prints). Every strike, hourly bid/ask, Kalshi fee, halves, coin-flip and wrong-month checks. Cache `econ_cache` (own Actions cache). `live_chances()` feeds the `econ_fav` track. Report `backtest/econ.md` | probe `econ_all` (fetch+run, ~35 min first time), `econ_run`, `econ_drill`, `econ_drill2`, `econ_drill3`, `econ_scan`; live dry run `econtest` |
| `sharp.py` | Pinnacle fair price vs Polymarket sports (live scan and backtest); report `backtest/sharp.md` | probe `sharp_*` (PR #24) |
| `sources.py` | Who reads the settle source first: map of every open market by the website its rules settle on, Kalshi family explorer (rules, settle values, candles), which early sources GitHub can read, and lag tests for gas (AAA), earthquakes (USGS), executive orders. Report `backtest/sources.md` | probe `src_map`, `src_kdaily`, `src_precur`, `src_ks_<SERIES,...>`, `src_reach`, `src_gas[_SERIES]`, `src_quake`, `src_eo` |
| `launch.py` | **New-listing test**: samples Polymarket markets by start day (no volume floor, ~31k, Mar-Nov) and Kalshi by close day (~21k, Sep-Nov), prices 10 min/1h/6h after launch vs seasoned twins (same kind, side, band, time left, 1+ day old), split halves, +2c/+5c, real-fill check from the trade tape. Live watcher snaps brand-new books at 1-120 min. Data in `bt_cache/launch/` (branch cache). Reports `backtest/launch.md`, `backtest/launch_live.md` | probe `btlaunchfetch` / `btlaunchfetchpoly` / `btlaunchfetchkalshi`, `btlaunchrun`, `btlaunchselftest`, `launch_live_<min>_<follow>` |
| `polls.py` | **Poll averages vs approval markets**: Kalshi RCP/538/VoteHub approval and generic-ballot series (hourly bid/ask), Polymarket Silver Bulletin/RCP weekly buckets (series-expanded, trade tapes), Silver Bulletin daily average as first published (old Datawrapper chart versions), VoteHub/ElectionsUSA poll lists; random-walk model vs price, halves, coin-flip and wrong-dates controls, real-fill check. Cache `bt_cache/polls/`. Report `backtest/polls.md` | probe `btpolls_reach`, `btpolls_fetch`, `btpolls_run`, `btpolls_drill`, `btpolls_sbpit`, `btpolls_more`; offline `python3 polls.py selftest` |
| `census.py` | **Every kind of Polymarket bet**: sorts each market into a family (sports winner/spreads/totals/props, esports, crypto or stock up/down, crypto ladders, weather buckets, mentions, post counts, politics, ...) and a shape (pick one of many, deadline, buckets, ladder, over/under). Live counts, money, settle source, gaps; history priced vs result per family (sports included, but bt_cache has almost none); daily stock up/down drill with a real trade-tape check; sports side bets (bt_cache has none, own fetch in `bt_cache/sports/`) priced vs result by bet type and league, real buys before kickoff only. Report `backtest/census.md` | probe `census_live`, `census_updown`; `btcensus`, `btcensusupdown`, `btcensustape`; `btsports` (fetch + run), `btsportsrun`, `btsportsdraw` (ref=main) |
| `livelag.py` | Live esports score feed vs Polymarket price, who moves first; report `backtest/livelag.md` | probe `lag_scan`, `lag_<minutes>` (PR #25) |

## Live research probes (read-only)

| Tool | What it does | Run |
|---|---|---|
| `probe.py` | Raw API shapes: `all, kalshi, poly, endgame, events, activity, sells, exits, lab, fast*` | probe `<input>` |
| `probe.py audit` | Checks past paper trades against Polymarket (prices, copy timing, payouts, stuck bets, marks) (PR #22) | probe `audit` |
| `probe.py rewardcheck` / `rewardpay` | Maker reward pools, and what real reward wallets actually get paid | probe `rewardcheck`, `rewardpay` |
| `probe.py egcheck`, `marks_<track>` | Endgame fill check; open bets marked at bid vs ask | probe `egcheck`, `marks_<track>` |
| `walletcheck.py` | Full profile of one Polymarket wallet (what, at what price, how long, where the profit comes from) | probe `wallet_<0xaddress>` |
| `arbhunt.py` | Hunts new safe pair kinds: strike/deadline ladders, duplicate listings, rejected pairs, sports | probe `hunt`, `hunt_ladders`, `hunt_dupes`, `hunt_rejected`, `hunt_sports2` |
| `logichunt.py` | Markets that contradict each other: champion vs conference vs playoffs lists, plain yes/no groups (all-NO / all-YES), ladders across two events, Kalshi exclusive sets and strike ladders; `lh_watch_<min>` re-prices the near misses every 3 min (findings `backtest/logic.md`) | probe `lh_all`, `lh_nested`, `lh_groups`, `lh_cross`, `lh_kalshi`, `lh_watch_<min>`, `lh_kevent_<TICKER>` |
| `edges.py` | Liquidity rewards, negRisk conversion, holding rewards | probe `edges_rewards`, `edges_negrisk`, `edges_holding`, `edges_all` (PR #5) |
| `bot.py` dry runs | `arbtest, dryrun, discover, copytest, depthtest, fasttest, makertest, kmakertest` | probe `<name>` |

## The live bot and its outputs

| Tool | What it does |
|---|---|
| `bot.py watch / daily / summary / selftest` | The paper trader. `watch.yml` every 5 min (timer: cron-job.org), `daily.yml` once a day. Writes `state/` |
| `config.json`, `arb_pairs.json` | Every track's rules; reviewed arb pairs |
| `bot.integrity()` | Data check after every run, `state/integrity.json`, "Data check" in summary (PR #22) |
| `bot.plain_verdict()` | Plain-word verdicts used by dashboard, pushes and the morning review (PR #34) |
| `dashboard.py` | Phone page https://palsk1.github.io/poly-paper-bot/ (PR #11, #34, #35) |
| `state/summary.md` | Live scoreboard |
| `LEARNINGS.md` + `learnings.py` | **The main "what we've learned" page**: goal, candidates with pass rules and check dates, 1 Jan checklist, dropped ideas, open questions. Every finished dig updates it by hand; `python3 learnings.py` (run by daily.yml) rewrites its live-numbers block and the week-by-week table (`state/learnings_weeks.json`). `python3 learnings.py selftest` checks it offline |

## Already tested and dropped

**`backtest/ledger.md` is the list of every idea tried, with its verdict** (kept by `exam.py`). Check it first, and add your idea to it when you test one.

See `LEARNINGS.md` "Tried and dropped", CLAUDE.md "Decisions and findings" and the TESTED & DROPPED list in project memory before re-testing anything.
