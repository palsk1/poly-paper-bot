#!/usr/bin/env bash
# Pull the newest bot code and restart both real-money bots. The bots never update themselves.
#   bash ~/poly-paper-bot/live/update.sh
set -euo pipefail
cd ~/poly-paper-bot && git pull -q
~/lenv/bin/pip install -q -r live/requirements.txt
~/lenv/bin/python live/selftest.py
for B in kalshi poly; do
  if systemctl is-enabled --quiet $B-live 2>/dev/null; then sudo systemctl restart $B-live; echo "restarted $B-live"; fi
done
