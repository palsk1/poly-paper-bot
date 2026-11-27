# The two real-money bots (live/)

Jan said go on 22 Nov 2026: a tiny real test of the two strategies that fit about $30 each, run side by side
with their paper twins, because a bot that wins on paper can still lose live.

| Bot | Rule (same code and settings as the paper track) | Money | Paper twin |
|---|---|---|---|
| `kalshi_live.py` | `kc_maker_safe_usd`: a resting bid on the likely side of Kalshi's 15-minute crypto windows, 95c+, in the last 0.75-5.5 minutes, only when Binance is 2+ typical moves on our side (both as is and on Kalshi's dollar scale) | $4 a bid (Jan picked it 22 Nov), up to $30 out at once | `kc_maker_safe_usd` ($10 bids) |
| `poly_live.py` | `soccer_draw`: Yes on a soccer draw at 15-50c, 20-28 h before kickoff, real ask at most 3c over the listed price, held to the end. **Every second signal only** (blind, by the market's name), so about 20 bets are out at once | ~$1.10-2.00 a bet (5+ shares, $1+), up to $28 out at once | `soccer_draw` (all signals) |
| `pspeed_live.py` (added 25 Nov, Jan: "Build it, practice mode first") | the speed check's rule (`quoter/speedcheck.py`, week 19-24 Nov "Looks real", +$2.73 per $100 at 0.1 s, $0 at 0.5 s): when Bitcoin's fair price in the current Polymarket 5-minute window moves 3c+ within 2 s on Binance, buy the side it jumped toward at the offer seen (40c to under 95c), all or nothing, at most 1c above that price (`PSPEED_EXTRA_C`, Jan's pick 26 Nov, capped at 3c), skip offers of $100+, at most 2 bets bought a window (since 26 Nov killed orders don't count, Jan said go) | $2 a bet (5 shares, so $2-4.75), at most 50 bets and $100 a day, $15 out at once, stops at -$5 a day / -$15 total (since 26 Nov a phone `start` after a day stop allows one more day cap that day, every bot; the total cap still counts everything). **Practice mode (buys nothing) until `PSPEED_LIVE=yes`** | the speed check box (listen only) |

They run on Jan's AWS Lightsail server ("Ubuntu-1", Stockholm), as two always-on services, `kalshi-live` and
`poly-live`. Claude has no access to the server or the keys.

## Safety

- **Dry run first.** Without `LIVE=yes` in `~/.live.env` the bots only write down what they would do.
- **Spend caps** (in `~/.live.env`, Jan's file): money per bet, money out at once, bets out at once, new money per
  day, loss per day (stops new bets until the next UTC day), total loss ($20 each: writes a STOP file, so it stays
  stopped until Jan deletes the file).
- **Off switches. The easy one is the phone:** in the ntfy app, subscribe to your private channel (its name is
  printed by `add_keys.py`, saved as `NTFY_CONTROL` in `~/.live.env`) and type:
  `stop` (both bots), `stop kalshi`, `stop poly`, `start` (or `start kalshi` / `start poly`), `status`,
  `update` (newest code now), `updates off` / `updates on`, or `help`.
  The bots read it every ~20 seconds and answer in the same channel. Alerts (a lost Kalshi bid, a cap reached) land
  there too. `start` only undoes a phone stop, never a loss-cap stop. Anyone who knows the channel name can stop
  the bots (not move money), so keep the name to yourself. The other switches:
  1. On the server: `touch ~/live-data/STOP` (both) or `touch ~/live-data/STOP-kalshi` / `STOP-poly`. Delete the file to start again.
  2. From the phone: edit `live/switch.json` in the repo on GitHub, change `"on"` to `"off"`. Takes up to ~5 minutes.
     This file can only stop a bot. It can't start one or raise a limit.
  3. `sudo systemctl stop kalshi-live poly-live`.
  On a stop, the Kalshi bot cancels its waiting bids. Bets already made still settle and are booked.
- **Updates by themselves, tested first (23 Nov, Jan: "super hard on phone").** `autoupdate.py`, run by the timer
  `live-update.timer` every 10 minutes and at once when Jan types `update` in the phone channel:
  1. Nothing new for the bots (`live/`, `bot.py`, `config.json`)? The copy moves forward quietly, no restart.
  2. New bot code: its own `selftest.py` runs first in a side folder (offline, no orders). Fails -> the old code
     keeps running, the phone is told, and that same code is not tried again.
  3. Passes -> switch, restart the bots that are switched on (never one Jan turned off), wait 90 seconds. A bot not
     running fine -> back to the old code, restart, phone told.
  It never touches `~/.live.env` (keys, caps, `LIVE=yes`): caps and the money switch stay Jan's alone.
  Phone words: `update` (now), `updates off` / `updates on`, `help`. `status` also says when the code was updated.
  Turn on once: `curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/live/autoupdate_setup.sh | bash`.
  `update.sh` still works by hand as a fallback.
- Kalshi bids are post-only (never take, never pay a taker fee), die when their window closes, and cancel if Kalshi
  pauses trading. Polymarket buys are all-or-nothing (FOK) and never above listed + 3c.
- **Winnings:** Kalshi pays out by itself. Polymarket only pays a win once it is claimed: every 10 minutes the bot
  claims every claimable win in the wallet (old ones too) through Polymarket's free gasless claim, using the Relayer key.
- **Privacy:** the hourly notebook copy goes to a public release, so it never holds a wallet address, order number or
  payment number (cut to the last 4 characters). It does hold which markets were bet, when and how much. A determined
  person could match those against Polymarket's public trade list and find the wallet.
- Keys only in `~/.live.env` and `~/.kalshi.key` on the server, readable only by Jan's user. Never in this repo or chat.

## Setup (Jan, on the server, about 15 minutes)

1. Open the server: Lightsail > "Ubuntu-1" > Connect using SSH.
2. Stop the combo listener (it is done, and the bots take its place):
   `sudo systemctl disable --now quoter`
3. Install: `curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/live/setup.sh | bash`
   It must end with `ALL OK (35 checks)` and "Installed. Nothing is running yet."
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
   Kalshi shows two numbers: the whole balance and the part in **Crypto**. The bot can only bid with the Crypto part
   (Kalshi moves money by itself for bets made by hand, never for a bot). Move it at kalshi.com/account/exchange-indexes.
7. Dry run: `sudo systemctl enable --now kalshi-live poly-live`, then watch for an hour:
   `journalctl -u kalshi-live -f` (Ctrl+C stops watching, not the bot). Look for `would_bid` / `would_buy` lines.
8. Real money: `nano ~/.live.env`, delete the `#` in front of `LIVE=yes`, save (Ctrl+O, Enter, Ctrl+X), then
   `bash ~/poly-paper-bot/live/update.sh`.

How it's doing: `~/lenv/bin/python ~/poly-paper-bot/live/kalshi_live.py status` (and `poly_live.py status`).
Side by side with paper (anywhere, reads the public logs): `python3 live/compare.py`.

## Files

- `kalshi_live.py`, `poly_live.py`, `pspeed_live.py`: the bots (`check`, `run`, `status`)
- `pspeed_setup.sh`: one-time setup of the speed bot (its caps in `~/.live.env`, service `pspeed-live`, started in practice mode). Uses the Polymarket key already on the server; shares the wallet's cash with `poly-live` (claims take turns, `claim.lock`)
- `common.py`: caps, off switches, the notebook (`~/live-data/<bot>-state.json` + monthly `<bot>-YYYYMM.jsonl`), upload every 15 min to the release `live-data`
- `add_keys.py`: puts the keys on the server
- `autoupdate.py` + `autoupdate_setup.sh`: the server updates itself, tested first (`autoupdate.py selftest`)
- `setup.sh`, `update.sh` (by hand, fallback), `requirements.txt` (Polymarket's new official kit `polymarket-client`: the old `py-clob-client` stopped placing orders on 28 Apr 2026)
- `selftest.py`: offline test with fake answers, must print ALL OK
- `compare.py`: real vs paper twin
- `switch.json`: the remote off switch
