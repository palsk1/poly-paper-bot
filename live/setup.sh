#!/usr/bin/env bash
# One-time setup of the two REAL-MONEY bots on Jan's server (Ubuntu). Paste this one line into the server:
#   curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/live/setup.sh | bash
# It installs, but starts nothing. Next steps are printed at the end (and in live/README.md).
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y -qq git python3-venv python3-pip
cd ~
[ -d poly-paper-bot ] || git clone --depth 1 https://github.com/palsk1/poly-paper-bot.git
cd poly-paper-bot && git pull -q
python3 -m venv ~/lenv
~/lenv/bin/pip install -q --upgrade pip
~/lenv/bin/pip install -q -r live/requirements.txt
~/lenv/bin/python live/selftest.py
mkdir -p ~/live-data
touch ~/.live.env && chmod 600 ~/.live.env
grep -q "^KALSHI_USD_PER_ORDER" ~/.live.env || cat >> ~/.live.env <<'ENV'
# Spend caps for the real bots (change the numbers here, then: bash ~/poly-paper-bot/live/update.sh)
KALSHI_USD_PER_ORDER=4
KALSHI_MAX_OPEN_USD=30
KALSHI_DAY_LOSS_STOP=10
KALSHI_TOTAL_LOSS_STOP=20
POLY_MAX_BET=2
POLY_MAX_OPEN_USD=28
POLY_MAX_OPEN=20
POLY_DAY_SPEND_MAX=15
POLY_DAY_LOSS_STOP=10
POLY_TOTAL_LOSS_STOP=20
# Remove the # in front of the next line only when the dry run looks right. Then real money moves.
#LIVE=yes
ENV
if [ -f ~/.quoter.env ] && ! grep -q "^GITHUB_TOKEN" ~/.live.env; then
  grep "^GITHUB_TOKEN" ~/.quoter.env >> ~/.live.env || true   # reuse the combo listener's log token
fi
for B in kalshi poly; do
sudo tee /etc/systemd/system/$B-live.service >/dev/null <<UNIT
[Unit]
Description=REAL-MONEY $B bot (live/${B}_live.py, caps in ~/.live.env)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$HOME/poly-paper-bot
ExecStart=$HOME/lenv/bin/python -u live/${B}_live.py run
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
UNIT
done
sudo systemctl daemon-reload
echo
echo "Installed. Nothing is running yet. Next:"
echo "  1. Keys:   ~/lenv/bin/python ~/poly-paper-bot/live/add_keys.py"
echo "  2. Check:  ~/lenv/bin/python ~/poly-paper-bot/live/kalshi_live.py check   (and poly_live.py check)"
echo "  3. Start (dry run first):  sudo systemctl enable --now kalshi-live poly-live"
echo "  Watch:     journalctl -u kalshi-live -f      (Ctrl+C stops watching, not the bot)"
