#!/usr/bin/env bash
# Speed check (listen only, no key, no orders): adds a second always-on service next to the combo quoter.
# On the server, paste:   cd ~/poly-paper-bot && git pull && bash quoter/speed_setup.sh
set -euo pipefail
cd ~/poly-paper-bot && git pull -q
~/qenv/bin/pip install -q websockets
~/qenv/bin/python quoter/speedcheck.py selftest
touch ~/.quoter.env
sudo tee /etc/systemd/system/speedcheck.service >/dev/null <<UNIT
[Unit]
Description=Speed check for Bitcoin 5-minute windows (listen only, no money moves)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$HOME/poly-paper-bot
EnvironmentFile=$HOME/.quoter.env
Environment=SPEED_DIR=$HOME/speed-data
ExecStartPre=-/usr/bin/git -C $HOME/poly-paper-bot pull -q
ExecStart=$HOME/qenv/bin/python -u quoter/speedcheck.py run
Nice=10
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now speedcheck
echo
echo "Speed check is running. Watch it with:  journalctl -u speedcheck -f   (Ctrl+C stops watching, not the check)"
echo "Stop it for good with:                  sudo systemctl disable --now speedcheck"
