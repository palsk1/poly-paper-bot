# poly-paper-bot

**Paper trading only.** This bot never places real orders and holds no keys. It reads Polymarket's public data and records pretend trades so we can see which approach would actually have made money.

## What it tests (each track has its own paper wallet)

| Track | What it does | Paper money |
|---|---|---|
| `mirror` | Copies every position sabsabinxz opens and closes, 5 shares each | $20 |
| `favorites` | Same, but only his entries at 80c or more | $20 |
| `mirror_unlimited` | Mirror that never runs out of money. Shows whether he has an edge and how much money copying him would need | unlimited |
| `screener` | His "boring outcome" style by rule, without him | $20 |
| `claude` | Claude's own rules (see `config.json` > `rules.claude.why`) | $50, refilled with $50 if it busts |
| `panic_fade` | Wildcard: buys the boring side right after a news scare drops it 6c+ in a day, sells on recovery | $50, refilled if it busts |

## How it runs

- `watch` workflow, every ~10 min: checks his wallet, copies opens/exits, handles take-profit/stop-loss, panic scan every 2 hours. Sends ntfy pushes.
- `daily` workflow, ~06:17 Stockholm (winter): settles resolved markets, picks for the rule tracks, writes `state/summary.md`.
- `selftest` workflow (manual): checks the APIs and sends a test push.

Fills are paper fills at the real order book price (taking the ask, selling at the bid), including Polymarket's taker fee where the market charges one.

## Files in `state/`

- `summary.md`: human-readable daily report (start here)
- `tracks.json`: every paper position and closed trade
- `events.jsonl`: everything that happened, one line per event
- `history.csv`: daily P&L per track
- `candidates.json`: what the rule tracks were choosing from
- `his_book.json`: his current book and what holding all of it at minimum size would cost

## Setup

Add a repository secret `NTFY_TOPIC` (Settings > Secrets and variables > Actions) with your ntfy topic name.
