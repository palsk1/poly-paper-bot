#!/usr/bin/env bash
# One-time setup of the speed bot (live/pspeed_live.py) on the server that already runs the real Kalshi and
# Polymarket bots. It starts in PRACTICE mode: it buys nothing until ~/.live.env has PSPEED_LIVE=yes.
#   bash ~/poly-paper-bot/live/pspeed_setup.sh
# Touches nothing of the other bots: adds its own caps to ~/.live.env (only if missing) and its own service.
set -euo pipefail
cd ~/poly-paper-bot
if [ ! -f live/pspeed_live.py ]; then
  echo "This server's copy of the code is older than the speed bot. Type update on the phone, wait 2 minutes, run this again."
  exit 1
fi
~/lenv/bin/python live/selftest.py >/dev/null && echo "self-test OK"
touch ~/.live.env && chmod 600 ~/.live.env
grep -q "^PSPEED_BET" ~/.live.env || cat >> ~/.live.env <<'ENV'
# Speed bot (live/pspeed_live.py). Change the numbers here, then: sudo systemctl restart pspeed-live
PSPEED_BET=2
PSPEED_MAX_BET=5
PSPEED_MAX_OFFER_USD=100
PSPEED_PER_WINDOW=2
PSPEED_MAX_BETS_DAY=50
PSPEED_DAY_SPEND_MAX=100
PSPEED_MAX_OPEN_USD=15
PSPEED_DAY_LOSS_STOP=5
PSPEED_TOTAL_LOSS_STOP=15
# Remove the # in front of the next line only when Jan says live. Then real money moves.
#PSPEED_LIVE=yes
ENV
sudo tee /etc/systemd/system/pspeed-live.service >/dev/null <<UNIT
[Unit]
Description=Speed bot, Bitcoin 5-minute windows (live/pspeed_live.py, practice unless PSPEED_LIVE=yes)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$HOME/poly-paper-bot
ExecStart=$HOME/lenv/bin/python -u live/pspeed_live.py run
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now pspeed-live
sleep 3
~/lenv/bin/python live/pspeed_live.py check || true
echo
echo "Speed bot is running in PRACTICE mode (buys nothing)."
echo "  Watch:   journalctl -u pspeed-live -f      (Ctrl+C stops watching, not the bot)"
echo "  Phone:   status / stop speed / start speed"
