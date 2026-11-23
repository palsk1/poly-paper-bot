"""The server keeps itself up to date (Jan, 23 Nov: "How can we make it easier to control the server without all
these commands? Super hard on phone").

Every 10 minutes (a systemd timer), and at once when Jan types `update` in his phone channel:
  1. Look at GitHub's main branch. Nothing new for the bots (live/, bot.py, config.json)? Just move the copy on
     the server forward, quietly. No restart.
  2. New bot code? Test it FIRST in a side folder (live/selftest.py of the NEW code, offline, no orders).
     The test fails -> keep the old code running, tell Jan's phone, and don't try that same code again.
  3. Test passes -> switch to the new code, restart the bots that are switched on, wait 90 seconds.
     A bot that is not running fine after that -> go back to the old code, restart again, tell the phone.
  4. Tell the phone what happened ("Updated, both bots running").

Phone words (read by the bots, see common.control): `update` (check now), `updates off`, `updates on`.
`updates off` writes ~/live-data/NO-AUTO-UPDATE: then only a typed `update` moves the code.

Never touches the keys (~/.live.env is only read for the phone channel name) or the caps.

    python3 live/autoupdate.py run          what the timer runs
    python3 live/autoupdate.py run --now    same, but also when updates are off, and always answers the phone
    python3 live/autoupdate.py install      one time, by Jan (live/autoupdate_setup.sh does it)
    python3 live/autoupdate.py selftest     offline test with a fake GitHub and fake services
"""
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

REPO_DIR = os.path.dirname(HERE)
WATCH = ["live", "bot.py", "config.json"]       # what the real bots run; anything else never restarts them
BOTS = ["kalshi", "poly"]
TITLE = "Server update"
WAIT_S = 90
PY = sys.executable


def paths():
    return {"flag": os.path.join(C.DIR, "UPDATE-NOW"), "off": os.path.join(C.DIR, "NO-AUTO-UPDATE"),
            "state": os.path.join(C.DIR, "update-last.json"), "lock": os.path.join(C.DIR, "update.lock")}


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO_DIR, *args], capture_output=True, text=True, timeout=300)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def systemctl(*args):
    """sudo systemctl ...; returns (exit code, output). Swapped out in the self-test."""
    r = subprocess.run(["sudo", "-n", "systemctl", *args], capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout.strip()


def bots_on():
    return [b for b in BOTS if systemctl("is-enabled", "--quiet", f"{b}-live")[0] == 0]


def health(bot):
    """(running, automatic restarts so far). A bot that crashes gets restarted by systemd, which counts it."""
    _, out = systemctl("show", f"{bot}-live", "-p", "ActiveState", "-p", "NRestarts")
    v = dict(ln.split("=", 1) for ln in out.splitlines() if "=" in ln)
    return v.get("ActiveState") == "active", int(v.get("NRestarts") or 0)


def restart_and_check(bots, wait=None):
    """Restart, wait, then check each bot still runs and did not crash meanwhile. Returns the bots that failed."""
    before = {b: health(b)[1] for b in bots}
    for b in bots:
        systemctl("restart", f"{b}-live")
    time.sleep(WAIT_S if wait is None else wait)
    bad = []
    for b in bots:
        up, n = health(b)
        if not up or n != before[b]:
            bad.append(b)
    return bad


def code_key(rev):
    """One fingerprint of the bot code at a commit (so a failed version is not retried every 10 minutes)."""
    return hashlib.sha1(git("ls-tree", "-r", rev, "--", *WATCH).encode()).hexdigest()[:16]


def load_state():
    try:
        return json.load(open(paths()["state"]))
    except (OSError, ValueError):
        return {}


def save_state(st):
    tmp = paths()["state"] + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, paths()["state"])


def pip_install(rev):
    """Install the Python packages listed at that commit (only called when requirements.txt changed)."""
    reqs = git("show", f"{rev}:live/requirements.txt")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(reqs)
    try:
        r = subprocess.run([PY, "-m", "pip", "install", "-q", "-r", f.name], capture_output=True, text=True, timeout=600)
        return r.returncode == 0, (r.stderr or r.stdout).strip()[-300:]
    finally:
        os.remove(f.name)


def test_new(rev):
    """Run the NEW code's self-test in a side folder. (passed, last lines of its output)."""
    side = tempfile.mkdtemp(prefix="liveupd-")
    try:
        arch = subprocess.run(["git", "-C", REPO_DIR, "archive", rev, "--", *WATCH], capture_output=True, timeout=120)
        if arch.returncode:
            return False, arch.stderr.decode()[-300:]
        subprocess.run(["tar", "-x", "-C", side], input=arch.stdout, check=True, timeout=120)
        out = []
        for cmd in ([PY, "live/selftest.py"], [PY, "live/autoupdate.py", "selftest"]):
            if not os.path.exists(os.path.join(side, cmd[1])):
                continue
            r = subprocess.run(cmd, cwd=side, capture_output=True, text=True, timeout=600,
                               env={**os.environ, "LIVE_DIR": os.path.join(side, "_data")})
            text = (r.stdout + r.stderr).strip()
            out.append(text.splitlines()[-1] if text else "")
            if r.returncode or "ALL OK" not in r.stdout:
                return False, text[-400:]
        return True, " / ".join(out)
    finally:
        shutil.rmtree(side, ignore_errors=True)


def tidy(st):
    """Once a day: throw away old copies of the code so the server's disk doesn't fill up."""
    day = C.today()
    if st.get("tidy") != day:
        git("reflog", "expire", "--expire=now", "--all", check=False)
        git("gc", "-q", "--prune=now", check=False)
        st["tidy"] = day


def say(text):
    print(text, flush=True)
    C.push(TITLE, text)


def run(now=False):
    os.makedirs(C.DIR, exist_ok=True)
    P = paths()
    lock = open(P["lock"], "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another update is running", flush=True)
        return
    C.load_env()
    if os.path.exists(P["flag"]):             # Jan typed `update` on the phone
        now = True
        os.remove(P["flag"])
    st = load_state()
    if os.path.exists(P["off"]) and not now:
        print("auto-updates are off (NO-AUTO-UPDATE); type update on the phone to update once", flush=True)
        return
    old = git("rev-parse", "HEAD")
    try:
        git("fetch", "-q", "--depth", "1", "origin", "main")
    except RuntimeError as e:
        print(e, flush=True)
        if now:
            say(f"Could not reach GitHub, nothing changed. The bots keep running. ({str(e)[:120]})")
        return
    new = git("rev-parse", "FETCH_HEAD")
    st["checked"] = C.iso()
    changed = [f for f in git("diff", "--name-only", old, new, "--", *WATCH).splitlines() if f]
    if not changed:
        if new != old:
            git("reset", "-q", "--hard", new)        # research files, scoreboards: nothing the bots run
        tidy(st)
        save_state(st)
        if now:
            say("Already on the newest bot code" + (f" (from {nice(st['updated'])})." if st.get("updated") else ".")
                + " Nothing to restart.")
        return
    key = code_key(new)
    if key == st.get("bad") and not now:
        save_state(st)
        print("this code failed before; waiting for a newer version", flush=True)
        return
    what = ", ".join(sorted({f.split("/")[-1] for f in changed}))[:200]
    reqs = "live/requirements.txt" in changed
    if reqs:
        ok, msg = pip_install(new)
        if not ok:
            pip_install(old)
            st["bad"] = key
            save_state(st)
            say(f"New bot code found, but its Python parts would not install. Kept the old code, the bots keep "
                f"running as before. Claude can look at it. ({msg[-150:]})")
            return
    ok, msg = test_new(new)
    if not ok:
        if reqs:
            pip_install(old)
        st["bad"] = key
        save_state(st)
        say(f"New bot code found ({what}), but it failed its test. Kept the old code, the bots keep running as "
            f"before. Ask Claude to fix it. Test said: {msg[-200:]}")
        return
    git("reset", "-q", "--hard", new)
    on = bots_on()
    bad = restart_and_check(on) if on else []
    if bad:
        git("reset", "-q", "--hard", old)
        if reqs:
            pip_install(old)
        still = restart_and_check(on)
        st["bad"] = key
        save_state(st)
        names = " and ".join(C.NAMES[b] for b in bad)
        say(f"New bot code ({what}) passed its test, but the {names} did not run right with it. Went back to the "
            f"old code. " + ("All bots running again on the old code." if not still else
                             f"WARNING: still not running: {', '.join(C.NAMES[b] for b in still)}. Type status.")
            + " Ask Claude to look.")
        return
    st.update(updated=C.iso(), commit=new[:7], what=what)
    st.pop("bad", None)
    tidy(st)
    save_state(st)
    names = " and ".join(C.NAMES[b] for b in on) or "no bot (none is switched on)"
    say(f"Updated to the newest bot code ({what}). Test passed. Restarted: {names}. "
        + ("All running fine." if on else ""))


def nice(iso_t):
    """'23 Nov 17:12' in Stockholm time."""
    try:
        from zoneinfo import ZoneInfo
        import datetime as dt
        t = dt.datetime.fromisoformat(iso_t.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Stockholm"))
        return t.strftime("%-d %b %H:%M")
    except Exception:
        return iso_t[:16]


def status_line():
    """For the phone's `status` answer: when the code was last updated, and whether auto-updates are on."""
    st = load_state()
    off = os.path.exists(paths()["off"])
    when = f"Code updated {nice(st['updated'])}" if st.get("updated") else "Code: not auto-updated yet"
    return f"{when}. Auto-updates {'OFF (type updates on)' if off else 'on'}."


# ---------------------------------------------------------------- one-time install (Jan pastes one line)
UNITS = {
    "live-update.service": """[Unit]
Description=Keeps the real-money bots' code up to date (live/autoupdate.py)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User={user}
WorkingDirectory={repo}
ExecStart={py} -u live/autoupdate.py run
TimeoutStartSec=1200
""",
    "live-update.timer": """[Unit]
Description=Look for new bot code every 10 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=10min

[Install]
WantedBy=timers.target
""",
    "live-update.path": """[Unit]
Description=Update at once when the phone says update

[Path]
PathExists={dir}/UPDATE-NOW
Unit=live-update.service

[Install]
WantedBy=multi-user.target
""",
}


def install():
    os.makedirs(C.DIR, exist_ok=True)
    user = os.environ.get("USER") or subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
    for name, body in UNITS.items():
        text = body.format(user=user, repo=REPO_DIR, py=PY, dir=C.DIR)
        subprocess.run(["sudo", "-n", "tee", f"/etc/systemd/system/{name}"], input=text, text=True,
                       stdout=subprocess.DEVNULL, check=True)
    systemctl("daemon-reload")
    systemctl("enable", "--now", "live-update.timer", "live-update.path")
    C.load_env()
    on = bots_on()
    print(f"Restarting {', '.join(on) or 'no bots'} on the newest code, then checking for {WAIT_S} s...", flush=True)
    bad = restart_and_check(on) if on else []
    st = load_state()
    st.update(updated=C.iso(), commit=git("rev-parse", "--short", "HEAD"), what="first install")
    save_state(st)
    if bad:
        say("Auto-update is installed, but these bots are not running right: "
            f"{', '.join(C.NAMES[b] for b in bad)}. Type status, and tell Claude.")
        print("SOMETHING IS WRONG, see above.")
        sys.exit(1)
    say("Auto-update is on. The server now picks up new bot code by itself (tested first, every 10 minutes) and "
        "tells you here. Words you can type: status, stop, start, update, updates off, updates on, help.")
    print("\nDONE. Auto-update is on. You never need to type update.sh again.")


# ---------------------------------------------------------------- offline self-test
def selftest():
    """A fake GitHub (a local git folder) and fake services. No network, no sudo, no orders."""
    global REPO_DIR, WAIT_S, systemctl, pip_install
    ok = []

    def check(cond, what):
        if not cond:
            raise SystemExit(f"FAILED: {what}")
        ok.append(what)

    root = tempfile.mkdtemp(prefix="autoupd-test-")
    C.DIR = os.path.join(root, "data")
    os.makedirs(C.DIR)
    for k in ("NTFY_CONTROL", "NTFY_TOPIC"):
        os.environ.pop(k, None)
    sent = []
    C.push = lambda title, body: sent.append((title, body))
    C.load_env = lambda: None
    origin, server = os.path.join(root, "origin"), os.path.join(root, "server")

    def g(d, *a):
        subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True,
                       capture_output=True)

    def write(rel, text):
        p = os.path.join(origin, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)

    os.makedirs(origin)
    g(origin, "init", "-q", "-b", "main")
    good_test = "print('ALL OK (1 checks)')\n"
    write("live/selftest.py", good_test)
    write("live/requirements.txt", "x\n")
    write("bot.py", "# v1\n")
    write("config.json", "{}\n")
    write("state/summary.md", "s1\n")
    g(origin, "add", "-A")
    g(origin, "commit", "-q", "-m", "v1")
    subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + origin, server], check=True, capture_output=True)
    REPO_DIR = server
    WAIT_S = 0
    # The side-folder test runs the new code's own selftest.py; its autoupdate.py is not in the fake repo.
    svc = {"kalshi": {"on": True, "active": True, "n": 0}, "poly": {"on": True, "active": True, "n": 0}}
    calls = []
    crash_on = {"v": None}

    def fake_systemctl(*args):
        calls.append(args)
        if args[0] == "is-enabled":
            return (0 if svc[args[2].split("-")[0]]["on"] else 1), ""
        if args[0] == "show":
            s = svc[args[1].split("-")[0]]
            return 0, f"ActiveState={'active' if s['active'] else 'activating'}\nNRestarts={s['n']}"
        if args[0] == "restart":
            b = args[1].split("-")[0]
            bad = crash_on["v"] and crash_on["v"] in open(os.path.join(server, "bot.py")).read()
            svc[b]["active"] = not bad
            svc[b]["n"] += 1 if bad else 0
        return 0, ""
    systemctl = fake_systemctl
    pips = []
    pip_install = lambda rev: pips.append(rev) or (True, "")

    def commit(rel, text, msg):
        write(rel, text)
        g(origin, "add", "-A")
        g(origin, "commit", "-q", "-m", msg)
        return subprocess.run(["git", "-C", origin, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def head():
        return git("rev-parse", "HEAD")

    # 1. only a scoreboard changed -> copy moves forward, no restart, no phone message
    c = commit("state/summary.md", "s2\n", "watch")
    run()
    check(head() == c and not [x for x in calls if x[0] == "restart"] and not sent,
          "a scoreboard-only change moves the copy forward quietly, without restarting the bots")
    # 2. new bot code that passes -> restart both, phone told
    c = commit("bot.py", "# v2\n", "bot change")
    run()
    check(head() == c and len([x for x in calls if x[0] == "restart"]) == 2 and "Updated" in sent[-1][1],
          "new bot code that passes its test: switched, both bots restarted, phone told")
    check(load_state().get("commit") == c[:7] and "Code updated" in status_line(), "the status line shows the update")
    # 3. new code whose test fails -> old code stays, phone told, not retried
    calls.clear()
    before = head()
    commit("live/selftest.py", "raise SystemExit('FAILED: boom')\n", "broken")
    run()
    check(head() == before and not [x for x in calls if x[0] == "restart"] and "failed its test" in sent[-1][1],
          "code that fails its test is never switched to; the bots keep the old code and the phone is told")
    n = len(sent)
    commit("state/summary.md", "s3\n", "watch")
    run()
    check(len(sent) == n and head() == before, "the same broken code is not retried every 10 minutes")
    # 4. passes the test but the bot crashes -> back to the old code
    commit("live/selftest.py", good_test, "test fixed")
    crash_on["v"] = "CRASH"
    c = commit("bot.py", "# v3 CRASH\n", "crashy")
    run()
    check(head() == before and "Went back to the old code" in sent[-1][1] and "All bots running again" in sent[-1][1],
          "a bot that won't run on the new code is put back on the old code, and the phone is told")
    # 5. requirements change -> pip runs for the new code
    crash_on["v"] = None
    commit("bot.py", "# v4\n", "ok again")
    c = commit("live/requirements.txt", "y\n", "new package")
    pips.clear()
    run()
    check(head() == c and pips == [c], "a new package list is installed before the new code is tested")
    # 6. updates off: the timer does nothing, a typed update still works and always answers
    open(paths()["off"], "w").close()
    c = commit("bot.py", "# v5\n", "later")
    run()
    check(head() != c, "with updates off the timer leaves the code alone")
    open(paths()["flag"], "w").close()
    run()
    check(head() == c and not os.path.exists(paths()["flag"]), "a typed update works even with updates off")
    n = len(sent)
    run(now=True)
    check(len(sent) == n + 1 and "Already on the newest" in sent[-1][1], "a typed update always gets an answer")
    os.remove(paths()["off"])
    # 7. a bot Jan switched off is not started by an update
    svc["poly"]["on"] = False
    calls.clear()
    commit("bot.py", "# v6\n", "more")
    run()
    check([x[1] for x in calls if x[0] == "restart"] == ["kalshi-live"], "an update never starts a bot Jan turned off")
    shutil.rmtree(root, ignore_errors=True)
    for w in ok:
        print("ok  ", w)
    print(f"ALL OK ({len(ok)} checks)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        run(now="--now" in sys.argv)
    elif cmd == "install":
        install()
    elif cmd == "selftest":
        selftest()
    else:
        print(__doc__)
