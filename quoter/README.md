# Paper combo quoter (listen only)

Jan said "go" on 2026-11-11. This is the live paper test of "be the house on Polymarket combos" (`backtest/combos.md`).
It runs on **Jan's own server**, not in GitHub Actions, because Polymarket only sends combo requests to logged-in
quoters.

**Where it runs now (12 Nov 2026):** AWS Lightsail instance "Ubuntu-1", region **Stockholm (eu-north-1)**, the $12
plan (2 GB), on the AWS free plan (no charges until the free plan ends 11 May 2027). Live since 11 Nov 12:17 UTC. The
first box ("quoter", $5, 512 MB) ran out of CPU the same day and was replaced from a snapshot. The free plan locks the
region to Stockholm, and that's fine: about 30 ms to Polymarket in London against a 0.4 s quote window. Only Jan can
log in; Claude has no access to the server.

**What it does:** listens to every combo request, prices it from the live books of its legs (legs multiplied, middle
price), and writes down what we *would* have quoted under each rule. When the trade happens, Polymarket tells every
quoter the winning price. If our quote was cheaper, we'd have got that bet. When the games end, `combos.py qscore`
works out what those bets would have paid.

**What it never does:** send a quote, sign anything, or move money. There's no code for it. It doesn't hold a private
key. It only has an API login, which can't move money by itself.

## Rules written down before the first request (PROTOCOL.md 5c)

| Rule | What we'd quote | Which requests |
|---|---|---|
| `main` | legs x 1.05 | 2-4 legs, no two legs from the same game, every leg book 10c wide or less |
| `m3` | legs x 1.03 | same |
| `all5` | legs x 1.05 | any number of legs, same-game allowed (for comparison) |

Only requests where users buy the parlay. We skip legs that are already decided (98.5c+ or 1.5c-).

## Setup (Jan, about 15 minutes)

1. AWS Lightsail, region **Stockholm (eu-north-1)** (the free plan allows only that), Linux, OS only, **Ubuntu 24.04**,
   the **$12** plan (2 GB; the $5 plan runs out of CPU).
2. Open it with "Connect using SSH" (a black window in your browser). Paste:
   `curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/quoter/setup.sh | bash`
3. Make the login: `~/qenv/bin/python ~/poly-paper-bot/quoter/make_creds.py new`
   (`new` = a fresh empty wallet just for listening. Recommended. Your own Polymarket account stays out of it.)
4. Optional, so results reach the repo: make a GitHub fine-grained token (only this repo, Contents read and write),
   then `echo GITHUB_TOKEN=github_pat_... >> ~/.quoter.env`. Without it, the logs stay on the server.
5. Start it: `sudo systemctl enable --now quoter`. Watch it: `journalctl -u quoter -f` (Ctrl+C stops watching, not the bot).

The first thing to look for is the `auth:` line and then whether requests arrive. If the login works but nothing
comes in for an hour, Polymarket doesn't send requests to quoters that never quote. (Answered 11 Nov: they do send
them, several a second.)

Updating: `sudo systemctl restart quoter` (it pulls the latest code on start).
Stopping for good: `sudo systemctl disable --now quoter`, then delete the server in Lightsail so it stops billing.

## Files

- `quoter.py` - the listener (`run`, `selftest`, `catalog`)
- `make_creds.py` - makes the API login, run once on the server
- `setup.sh` - installs everything and the always-on service
- Logs: `~/quoter-data/quoter-YYYYMMDD.jsonl`, uploaded hourly to the release `quoter-data`
- Scoring: probe `cmb_qscore` (or `python3 combos.py qscore`), offline check `python3 combos.py qtest`
