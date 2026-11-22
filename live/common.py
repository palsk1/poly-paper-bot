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
    if os.path.exists(os.path.join(DIR, f"STOP-ntfy-{bot}")):
        return "stopped from the phone (ntfy). Type start to turn it back on"
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


def ntfy_post(topic, title, body):
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=body.encode(), method="POST",
                                 headers={"Title": title.encode("ascii", "ignore").decode(), "Tags": "moneybag",
                                          "User-Agent": UA})
    urllib.request.urlopen(req, timeout=10).read()


def ntfy_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode()


def push(title, body):
    """Phone alert: to Jan's private bot channel NTFY_CONTROL (or NTFY_TOPIC) in ~/.live.env, never in the repo."""
    topic = os.environ.get("NTFY_CONTROL") or os.environ.get("NTFY_TOPIC")
    if not topic:
        return
    try:
        ntfy_post(topic, title, body)
    except Exception as e:
        print(f"push failed: {e}", flush=True)


# ---------------------------------------------------------------- phone control (Jan, 22 Nov: "make it easy")
CTRL_EVERY = 20
NAMES = {"kalshi": "Kalshi bot", "poly": "Polymarket bot"}
ALIASES = {"kalshi": "kalshi", "k": "kalshi", "poly": "poly", "polymarket": "poly", "p": "poly",
           "all": "all", "both": "all", "bots": "all"}
COMMANDS = {"stop", "off", "pause", "start", "on", "resume", "status", "how", "?"}
BOT_TITLES = set(NAMES.values())
_ctrl = {"t": 0}
_beat = {"t": 0, "n": 0, "slow": 0.0}


def beat(book, took, every=600):
    """A sign of life every 10 minutes (Jan, 22 Nov: a quiet bot looks like a dead one): rounds done, the slowest
    round, and whether the phone channel is set. Never prints the channel's name."""
    _beat["n"] += 1
    _beat["slow"] = max(_beat["slow"], took)
    if time.time() - _beat["t"] < every:
        return
    first = _beat["t"] == 0
    _beat["t"] = time.time()
    book.log("alive", rounds=_beat["n"], slowest_round_s=round(_beat["slow"], 1),
             phone="on" if os.environ.get("NTFY_CONTROL") else "OFF (no NTFY_CONTROL in ~/.live.env)",
             **({"note": "first round done"} if first else {}))
    _beat["n"], _beat["slow"] = 0, 0.0


def control(bot, book, status_fn):
    """Read Jan's commands from his private ntfy channel NTFY_CONTROL (typed in the ntfy app):
    stop | stop kalshi | stop poly | start | start kalshi | start poly | status.
    'stop' writes ~/live-data/STOP-ntfy-<bot>; 'start' removes only that file, never a cap's STOP file.
    The bots answer in the same channel with a title; messages with a title are never read as commands."""
    topic = os.environ.get("NTFY_CONTROL")
    if not topic or time.time() - _ctrl["t"] < CTRL_EVERY:
        return
    _ctrl["t"] = time.time()
    # Fix 22 Nov: was "the last minute", so a command was lost whenever one round took longer than that.
    # Now: everything since this bot started (ntfy takes a unix time), then everything after the last one read.
    since = book.state.get("ctrl_since") or str(_ctrl.setdefault("from", int(time.time()) - 60))
    try:
        raw = ntfy_get(f"https://ntfy.sh/{topic}/json?poll=1&since={since}")
    except Exception as e:
        print(f"ntfy control read failed: {e}", flush=True)
        return
    name = NAMES[bot]
    for ln in raw.splitlines():
        try:
            m = json.loads(ln)
        except ValueError:
            continue
        if m.get("event") != "message":
            continue
        book.state["ctrl_since"] = m.get("id") or since
        if "moneybag" in (m.get("tags") or []) or str(m.get("title") or "") in BOT_TITLES \
                or str(m.get("title") or "").endswith("STOPPED") or "a bid lost" in str(m.get("title") or ""):
            continue                       # the bots' own answers and alerts
        # Jan may type the command in the Title box and leave Message empty (ntfy then shows "triggered"):
        # read both boxes and take the first that starts with a command word (fix 22 Nov).
        words = []
        for text in (m.get("message"), m.get("title")):
            w = str(text or "").strip().lower().strip(".!").split()
            if w and w[0] in COMMANDS:
                words = w
                break
        if not words:
            continue
        book.log("phone_heard", cmd=" ".join(words[:2]))
        cmd, target = words[0], ALIASES.get(words[1], words[1]) if len(words) > 1 else "all"
        if target not in ("all", bot):
            continue
        flag = os.path.join(DIR, f"STOP-ntfy-{bot}")
        if cmd in ("stop", "off", "pause"):
            with open(flag, "w") as f:
                f.write(f"stopped from the phone at {iso()}\n")
            book.log("phone_stop")
            push(name, "Stopped. No new bets. Bets already made still finish. Type start to turn it back on.")
        elif cmd in ("start", "on", "resume"):
            if os.path.exists(flag):
                os.remove(flag)
            book.log("phone_start")
            why = stop_reason(bot, book)
            push(name, "Running again." if not why else f"Phone stop removed, but still paused: {why}")
        elif cmd in ("status", "how", "?"):
            why = stop_reason(bot, book)
            push(name, status_fn() + ("\nRunning." if not why else f"\nPaused: {why}") +
                 ("" if is_live() else "\n(Pretend mode: no real money yet.)"))
    book.save()


def phone_check(name):
    """For `check`: send one test message to the phone channel and count what was typed there lately.
    Tells a wrong channel name in the app (no test message arrives, 0 typed messages seen) from a bot problem."""
    topic = os.environ.get("NTFY_CONTROL")
    if not topic:
        return "Phone: no channel set (run add_keys.py once more, it makes one)."
    try:
        ntfy_post(topic, name, "Test from the server: the phone link works. Type status here any time.")
        raw = ntfy_get(f"https://ntfy.sh/{topic}/json?poll=1&since=12h")
    except Exception as e:
        return f"Phone: could not reach ntfy ({type(e).__name__}: {e})."
    typed = 0
    for ln in raw.splitlines():
        try:
            m = json.loads(ln)
        except ValueError:
            continue
        if m.get("event") == "message" and "moneybag" not in (m.get("tags") or []):
            typed += 1
    return (f"Phone: sent a test message to the channel ending ...{topic[-4:]}. Messages typed there in the last "
            f"12 hours: {typed}." + ("" if typed else " If you typed some, the app is on a different channel name."))


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
