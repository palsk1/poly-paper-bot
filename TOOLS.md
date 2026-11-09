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
| Kalshi 15-min crypto | Kalshi 15-minute crypto windows, trades and history | `kcrypto.py fetch [days]` (probe `kc_fetch`, `btkcfetch`, PR #31) |
| Live recordings | Order books, trades, spot prices every minute for fast markets, hourly files on GitHub releases `data-YYYYMMDD` | `recorder.yml` / `recorder.py` (PR #12). Use it to replace guessed slippage once enough is recorded |
| Holdout | Markets ending **2026-11-10 or later**. Never look at them before 2026-12-21 | `btcheck.py holdout` (probe `btholdout`), see `backtest/PROTOCOL.md` |

## Testing ideas on history

| Tool | What it does | Run |
|---|---|---|
| `backtest.py` | Replays the bot's own strategy code hour by hour on bt_cache, incl. wallet copies. Report `backtest/report.md` | probe `btrun`, `btdiag`, `btfade` (PR #7, #10) |
| `btcheck.py` + `backtest/PROTOCOL.md` | Sanity checks of the backtester (fair-coin world, second simulator, random twins, pessimistic costs, walk-forward) and the **test-before-results rules every new lead must follow**. Report `backtest/checks.md` | probe `btcheck`, `btcheckself` (PR #32) |
| `calib.py` | Calibration by market kind: price x time-before-end x topic, YES vs NO, event-clustered bands. Has the **topic tagger** (`calib.topic`) and snapshot code. Report `backtest/calib.md` | probe `btcalib` (PR #30) |
| `rules.py`, `fineprint.py` | Fine-print hunt: rule-text flags (official only, credible reporting, things that don't count...) vs UMA disputes and prices, limbo after the end date, volume-bias check. `fineprint.trouble_score(title, rules)` = 0-7 dispute warning light (0 flags 0.4 disputes per 1,000, 4+ flags 51). Report `backtest/rules.md` | probe `btrulesrun` |
| `ideas.py` | **Idea machine / cheap screener**: a catalog of features (wording, age, siblings, price path, ...) each tied to a bias, crossed with topics, side, price band and horizon; screened vs random twins on two halves with a many-ideas correction and placebo features. Other threads can plug in a feature with `@ideas.feature(...)`. Report `backtest/ideas.md`, method `backtest/IDEAS.md` | probe `btideas`, `btideasself`, `btideasdrill_<preset>` (split one idea by month/price/question), `btideasvolbias` (checks the cache for missing losing choices) (PR #38) |
| `kcrypto.py` | Backtest of Kalshi 15-min crypto maker bids; report `backtest/kcrypto.md` | probe `kc_run`, `btkc` (PR #31) |
| `sharp.py` | Pinnacle fair price vs Polymarket sports (live scan and backtest); report `backtest/sharp.md` | probe `sharp_*` (PR #24) |
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

## Already tested and dropped

See CLAUDE.md "Decisions and findings" and the TESTED & DROPPED list in project memory before re-testing anything.
