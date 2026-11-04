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
| `endgame` | Buys the 95-99c side of markets whose result is basically known: already resolved, result proposed (2h challenge window), past their deadline, or ending within 24h. Skips disputed markets and live sports | $100 |
| `every_horse` | Buys one share of every outcome in a multi-candidate event when the whole set costs less than it is guaranteed to pay. All-YES only on complete lists ("Other"/"No change" included); all-NO always pays at least n-1 | $100 |

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
- **Every horse** is pure math: if buying every candidate costs 96c and exactly one must win, that is 4c locked in. The catch is lists that are not complete (someone unlisted wins and every YES pays 0), so all-YES is only bought when the list has a catch-all outcome and is marked closed; open lists are skipped. The bot pushes **SHORT** if a set ever pays less than expected. Needs >= 1c per share after fees and >= 15% a year.

## How it runs

- `watch` workflow, every 5 min: an outside timer (cron-job.org) starts it through GitHub's API, because GitHub's own timer often skips runs for hours (its own ~10 min schedule stays as a backup). checks his wallet, copies opens/exits, take-profit/stop-loss, arb checks on approved pairs, endgame scan, panic and every-horse scan every 2 hours. If GitHub skipped the daily job, the watcher runs it. Sends ntfy pushes.
- `daily` workflow, ~06:17 Stockholm (backup 07:47): settles resolved markets, picks for the rule tracks, proposes arb pairs, writes `state/summary.md`, pushes a scoreboard. Runs once per day; a manual run forces a re-run.
- `selftest` workflow (manual): checks the APIs and sends a test push. `probe` workflow (manual): prints raw API shapes, no pushes.

Fills are paper fills at the real order book price (taking the ask, selling at the bid), including taker fees.

## Files

- `state/summary.md`: human-readable daily report (start here)
- `state/tracks.json`: every paper position, arb, every-horse set and closed trade
- `state/events.jsonl`: everything that happened, one line per event
- `state/history.csv`: daily P&L per track
- `state/candidates.json`: what the rule tracks were choosing from
- `state/arb_candidates.json`: proposed Kalshi/Polymarket twin pairs waiting for review
- `state/his_book.json`: his current book and what holding all of it at minimum size would cost
- `arb_pairs.json`: approved and rejected twin pairs (edited by the review, not by the bot)

## Setup

Add a repository secret `NTFY_TOPIC` (Settings > Secrets and variables > Actions) with your ntfy topic name.
