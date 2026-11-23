#!/usr/bin/env bash
# ONE TIME, on Jan's server: turn on automatic updates for the real-money bots. Paste this one line:
#   curl -fsSL https://raw.githubusercontent.com/palsk1/poly-paper-bot/main/live/autoupdate_setup.sh | bash
# After this the server picks up new bot code by itself (tested first, every 10 minutes) and reports to the phone.
set -euo pipefail
cd ~/poly-paper-bot
git fetch -q --depth 1 origin main
git reset -q --hard FETCH_HEAD
~/lenv/bin/pip install -q -r live/requirements.txt
~/lenv/bin/python live/selftest.py | tail -1
~/lenv/bin/python live/autoupdate.py selftest | tail -1
~/lenv/bin/python live/autoupdate.py install
