#!/usr/bin/env bash
# One-time setup on a fresh Ubuntu server (AWS Lightsail, Ireland). Paste this one line into the server:
#   curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/quoter/setup.sh | bash
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y -qq git python3-venv python3-pip
cd ~
[ -d poly-paper-bot ] || git clone --depth 1 https://github.com/palsk1/poly-paper-bot.git
cd poly-paper-bot && git pull -q
python3 -m venv ~/qenv
~/qenv/bin/pip install -q --upgrade pip
~/qenv/bin/pip install -q websockets py-clob-client
~/qenv/bin/python quoter/quoter.py selftest
touch ~/.quoter.env && chmod 600 ~/.quoter.env
sudo tee /etc/systemd/system/quoter.service >/dev/null <<UNIT
[Unit]
Description=Paper combo quoter (listen only, no money moves)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$HOME/poly-paper-bot
EnvironmentFile=$HOME/.quoter.env
Environment=DATA_DIR=$HOME/quoter-data
ExecStartPre=-/usr/bin/git -C $HOME/poly-paper-bot pull -q
ExecStart=$HOME/qenv/bin/python -u quoter/quoter.py run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
echo
echo "Setup done. Next:  ~/qenv/bin/python ~/poly-paper-bot/quoter/make_creds.py new"
echo "Then:              sudo systemctl enable --now quoter   and   journalctl -u quoter -f   to watch it."
