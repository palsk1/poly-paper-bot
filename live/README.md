# The two real-money bots (live/)

Jan said go on 22 Nov 2026: a tiny real test of the two strategies that fit about $30 each, run side by side
with their paper twins, because a bot that wins on paper can still lose live.

| Bot | Rule (same code and settings as the paper track) | Money | Paper twin |
|---|---|---|---|
| `kalshi_live.py` | `kc_maker_safe_usd`: a resting bid on the likely side of Kalshi's 15-minute crypto windows, 95c+, in the last 0.75-5.5 minutes, only when Binance is 2+ typical moves on our side (both as is and on Kalshi's dollar scale) | $4 a bid (Jan picked it 22 Nov), up to $30 out at once | `kc_maker_safe_usd` ($10 bids) |
| `poly_live.py` | `soccer_draw`: Yes on a soccer draw at 15-50c, 20-28 h before kickoff, real ask at most 3c over the listed price, held to the end. **Every second signal only** (blind, by the market's name), so about 20 bets are out at once | ~$1.10-2.00 a bet (5+ shares, $1+), up to $28 out at once | `soccer_draw` (all signals) |

They run on Jan's AWS Lightsail server ("Ubuntu-1", Stockholm), as two always-on services, `kalshi-live` and
`poly-live`. Claude has no access to the server or the keys.

## Safety

- **Dry run first.** Without `LIVE=yes` in `~/.live.env` the bots only write down what they would do.
- **Spend caps** (in `~/.live.env`, Jan's file): money per bet, money out at once, bets out at once, new money per
  day, loss per day (stops new bets until the next UTC day), total loss ($20 each: writes a STOP file, so it stays
  stopped until Jan deletes the file).
- **Off switches. The easy one is the phone:** in the ntfy app, subscribe to your private channel (its name is
  printed by `add_keys.py`, saved as `NTFY_CONTROL` in `~/.live.env`) and type:
  `stop` (both bots), `stop kalshi`, `stop poly`, `start` (or `start kalshi` / `start poly`), or `status`.
  The bots read it every ~20 seconds and answer in the same channel. Alerts (a lost Kalshi bid, a cap reached) land
  there too. `start` only undoes a phone stop, never a loss-cap stop. Anyone who knows the channel name can stop
  the bots (not move money), so keep the name to yourself. The other switches:
  1. On the server: `touch ~/live-data/STOP` (both) or `touch ~/live-data/STOP-kalshi` / `STOP-poly`. Delete the file to start again.
  2. From the phone: edit `live/switch.json` in the repo on GitHub, change `"on"` to `"off"`. Takes up to ~5 minutes.
     This file can only stop a bot. It can't start one or raise a limit.
  3. `sudo systemctl stop kalshi-live poly-live`.
  On a stop, the Kalshi bot cancels its waiting bids. Bets already made still settle and are booked.
- **No self-updates.** The bots never pull new code on their own. Code changes reach the server only when Jan runs
  `bash ~/poly-paper-bot/live/update.sh`.
- Kalshi bids are post-only (never take, never pay a taker fee), die when their window closes, and cancel if Kalshi
  pauses trading. Polymarket buys are all-or-nothing (FOK) and never above listed + 3c.
- **Winnings:** Kalshi pays out by itself. Polymarket only pays a win once it is claimed: every 10 minutes the bot
  claims every claimable win in the wallet (old ones too) through Polymarket's free gasless claim, using the Relayer key.
- Keys only in `~/.live.env` and `~/.kalshi.key` on the server, readable only by Jan's user. Never in this repo or chat.

## Setup (Jan, on the server, about 15 minutes)

1. Open the server: Lightsail > "Ubuntu-1" > Connect using SSH.
2. Stop the combo listener (it is done, and the bots take its place):
   `sudo systemctl disable --now quoter`
3. Install: `curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/live/setup.sh | bash`
   It must end with `ALL OK (27 checks)` and "Installed. Nothing is running yet."
4. Make the keys:
   - **Kalshi:** kalshi.com > Account & security > API keys > Create key. Copy the key ID and download the private key file.
     Open the file on your computer (it's text) so you can copy it.
   - **Polymarket:** the private key: with a Google or email login, open `reveal.magic.link/polymarket` (Polymarket's own
     help page points there), sign in and show the key; with a wallet app, export it from the app. And your address
     (profile picture, the 0x... with a copy button). The bot needs both: without the address it opens a new empty wallet.
     Also Settings > API keys > create a **Relayer key** (and note the address shown next to it): with it the bot
     claims every win by itself, so the cash is free for the next bets. Without it you press Claim in the app.
5. Put them on the server: `~/lenv/bin/python ~/poly-paper-bot/live/add_keys.py` (it asks one at a time; the
   Polymarket key is hidden while you paste).
6. Check the keys (no orders): `~/lenv/bin/python ~/poly-paper-bot/live/kalshi_live.py check` and
   `~/lenv/bin/python ~/poly-paper-bot/live/poly_live.py check`. Each should say OK and show your balance.
7. Dry run: `sudo systemctl enable --now kalshi-live poly-live`, then watch for an hour:
   `journalctl -u kalshi-live -f` (Ctrl+C stops watching, not the bot). Look for `would_bid` / `would_buy` lines.
8. Real money: `nano ~/.live.env`, delete the `#` in front of `LIVE=yes`, save (Ctrl+O, Enter, Ctrl+X), then
   `bash ~/poly-paper-bot/live/update.sh`.

How it's doing: `~/lenv/bin/python ~/poly-paper-bot/live/kalshi_live.py status` (and `poly_live.py status`).
Side by side with paper (anywhere, reads the public logs): `python3 live/compare.py`.

## Files

- `kalshi_live.py`, `poly_live.py`: the bots (`check`, `run`, `status`)
- `common.py`: caps, off switches, the notebook (`~/live-data/<bot>-state.json` + monthly `<bot>-YYYYMM.jsonl`), hourly upload to the release `live-data`
- `add_keys.py`: puts the keys on the server
- `setup.sh`, `update.sh`, `requirements.txt` (Polymarket's new official kit `polymarket-client`: the old `py-clob-client` stopped placing orders on 28 Apr 2026)
- `selftest.py`: offline test with fake answers, must print ALL OK
- `compare.py`: real vs paper twin
- `switch.json`: the remote off switch
