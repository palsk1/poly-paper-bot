"""Shared safety parts for the two REAL-MONEY bots (kalshi_live.py, poly_live.py). Added 22 Nov 2026, Jan said go.

These run only on Jan's own server, with keys only Jan has put there. Nothing in this repo holds a key.

Safety, in the order it is checked before every order:
  1. LIVE=yes must be in ~/.live.env, or the bot only writes down what it WOULD do (dry run, the default).
  2. Stop files on the server: ~/live-data/STOP stops both bots, ~/live-data/STOP-kalshi or STOP-poly one of them.
  3. The switch in the repo, live/switch.json ("on" / "off" per bot). It can only STOP a bot, never start one
     or raise a limit, and it is read every ~2 minutes (GitHub caches it up to ~5 min).
  4. Spend caps from ~/.live.env (Jan's file, not the repo): money per bet, money out at once, loss per day,
     total loss. Hitting the total-loss cap writes a STOP file, so the bot stays stopped until Jan deletes it.

The bots never pull new code by themselves: an update only happens when Jan runs `bash live/update.sh`.
"""
import datetime as dt
import gzip
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request

UTC = dt.timezone.utc
REPO = "palsk1/poly-paper-bot"
TAG = "live-data"
UA = "poly-paper-bot live (Jan's own small test)"
DIR = os.path.expanduser(os.environ.get("LIVE_DIR", "~/live-data"))
ENV_FILE = os.path.expanduser(os.environ.get("LIVE_ENV", "~/.live.env"))
SWITCH_URL = f"https://raw.githubusercontent.com/{REPO}/main/live/switch.json"
SWITCH_EVERY = 120


def load_env():
    """~/.live.env (KEY=value lines) into os.environ, without overriding what is already set."""
    if os.path.exists(ENV_FILE):
        for ln in open(ENV_FILE):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def envf(key, default):
    try:
        return float(os.environ.get(key, default))
    except ValueError:
        return float(default)


def is_live():
    return os.environ.get("LIVE", "").strip().lower() == "yes"


def utcnow():
    return dt.datetime.now(UTC)


def iso(t=None):
    return (t or utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return utcnow().strftime("%Y-%m-%d")


class Book:
    """The bot's own notebook: state file (what is open, money so far) + an append-only log (one line per event)."""

    def __init__(self, name):
        self.name = name
        os.makedirs(DIR, exist_ok=True)
        self.state_path = os.path.join(DIR, f"{name}-state.json")
        self.state = {"open": {}, "done": [], "realized": 0.0, "days": {}, "bets": 0, "won": 0, "lost": 0,
                      "started": iso()}
        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                self.state.update(json.load(f))

    def save(self):
        tmp = self.state_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.state, f, indent=1, sort_keys=True)
        os.replace(tmp, self.state_path)

    def log(self, kind, **kw):
        row = {"t": iso(), "k": kind, "live": is_live(), **kw}
        with open(os.path.join(DIR, f"{self.name}-{utcnow().strftime('%Y%m')}.jsonl"), "a") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
        print(f"{row['t']} {kind} " + " ".join(f"{k}={v}" for k, v in kw.items() if k not in ("raw",)), flush=True)

    def day(self, d=None):
        return self.state["days"].setdefault(d or today(), {"pnl": 0.0, "spent": 0.0, "bets": 0})

    def open_cost(self):
        return round(sum(o.get("cost", 0) for o in self.state["open"].values()), 4)

    def settle(self, key, pnl, **kw):
        """Book a finished bet: money, day total, won/lost count, log line."""
        o = self.state["open"].pop(key)
        self.state["realized"] = round(self.state["realized"] + pnl, 6)
        d = self.day()   # booked on the day it settles, so the day-loss cap sees it at once
        d["pnl"] = round(d["pnl"] + pnl, 6)
        if kw.get("filled", 1) > 0:
            self.state["won" if pnl >= 0 else "lost"] += 1
        self.state["done"] = (self.state["done"] + [key])[-2000:]
        self.log("settled", **{**o, **kw, "key": key, "pnl": round(pnl, 4)})
        self.save()


# ---------------------------------------------------------------- kill switches
_switch = {"t": 0, "val": None, "fails": 0}


def remote_switch(bot):
    """'on' or 'off' from live/switch.json on main. If GitHub can't be read for 30+ minutes, treat it as off."""
    if time.time() - _switch["t"] > SWITCH_EVERY:
        _switch["t"] = time.time()
        try:
            req = urllib.request.Request(f"{SWITCH_URL}?t={int(time.time())}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                _switch["val"] = json.loads(r.read().decode())
            _switch["fails"] = 0
        except Exception as e:
            _switch["fails"] += 1
            print(f"switch read failed ({_switch['fails']} in a row): {e}", flush=True)
    if _switch["val"] is None:
        return "off" if _switch["fails"] >= 15 else "on"
    if _switch["fails"] >= 15:
        return "off"
    return str(_switch["val"].get(bot, "off")).lower()


def stop_reason(bot, book):
    """None when the bot may place a NEW order, else a plain reason. Open bets always settle either way."""
    for fn in ("STOP", f"STOP-{bot}"):
        p = os.path.join(DIR, fn)
        if os.path.exists(p):
            return f"stop file {p} is there: {open(p).read().strip()[:200]}"
    if remote_switch(bot) != "on":
        return f"switch in the repo (live/switch.json) says {bot} is off"
    total_stop = envf(f"{bot.upper()}_TOTAL_LOSS_STOP", 20)
    if book.state["realized"] <= -total_stop:
        msg = (f"total loss ${-book.state['realized']:.2f} reached the ${total_stop:.0f} cap on {iso()}. "
               f"Delete this file to start again.")
        with open(os.path.join(DIR, f"STOP-{bot}"), "w") as f:
            f.write(msg + "\n")
        book.log("cap_total_loss", realized=book.state["realized"])
        push(f"{bot} bot STOPPED", msg)
        return msg
    day_stop = envf(f"{bot.upper()}_DAY_LOSS_STOP", 10)
    if book.day()["pnl"] <= -day_stop:
        return f"lost ${-book.day()['pnl']:.2f} today (cap ${day_stop:.0f}), waiting for tomorrow (UTC)"
    return None


def push(title, body):
    """Optional phone push: NTFY_TOPIC in ~/.live.env (same topic as the paper bot, never in the repo)."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return
    try:
        req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=body.encode(), method="POST",
                                     headers={"Title": title.encode("ascii", "ignore").decode(), "Tags": "moneybag"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"push failed: {e}", flush=True)


# ---------------------------------------------------------------- hourly upload to the GitHub release `live-data`
def gh(method, url, token, body=None, data=None, ctype=None):
    h = {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": UA,
         "Accept": "application/vnd.github+json"}
    if body is not None:
        data = json.dumps(body).encode()
        ctype = "application/json"
    if ctype:
        h["Content-Type"] = ctype
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    return json.loads(raw) if raw else None


def upload(prefix):
    """gzip this bot's log and state files and put them on the release `live-data` (replacing old copies).
    The files hold tickers, prices and results, no keys or account numbers. Needs GITHUB_TOKEN in ~/.live.env."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return "no GITHUB_TOKEN, kept on the server"
    api = f"https://api.github.com/repos/{REPO}"
    try:
        rel = gh("GET", f"{api}/releases/tags/{TAG}", token)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        rel = gh("POST", f"{api}/releases", token, {
            "tag_name": TAG, "name": "Real-money bot logs", "prerelease": True,
            "body": "What Jan's two small real-money test bots did (live/). Compare with the paper twins: "
                    "python3 live/compare.py"})
    have = {a["name"]: a["id"] for a in gh("GET", f"{api}/releases/{rel['id']}/assets?per_page=100", token)}
    n = 0
    month = utcnow().strftime("%Y%m")
    for fn in sorted(os.listdir(DIR)):
        if not fn.startswith(prefix + "-") or not (fn.endswith(".jsonl") or fn.endswith("-state.json")):
            continue
        if fn.endswith(".jsonl") and month not in fn and (fn + ".gz") in have:
            continue
        src = os.path.join(DIR, fn)
        gz = src + ".gz"
        with open(src, "rb") as a, gzip.open(gz, "wb") as b:
            shutil.copyfileobj(a, b)
        name = fn + ".gz"
        if name in have:
            gh("DELETE", f"{api}/releases/assets/{have[name]}", token)
        gh("POST", f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={name}", token,
           data=open(gz, "rb").read(), ctype="application/gzip")
        os.remove(gz)
        n += 1
    return f"uploaded {n} files"


def need(*keys):
    miss = [k for k in keys if not os.environ.get(k)]
    if miss:
        sys.exit(f"missing in {ENV_FILE}: {', '.join(miss)} (see live/README.md)")
