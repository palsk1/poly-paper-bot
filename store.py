#!/usr/bin/env python3
"""Shared price store: one place where every downloaded price file lives, so a download done by one
thread (or branch) is never done again by another (Jan's ask, 2026-11-10: "do we save the prices?").

Why: until now downloads lived only in GitHub's Actions cache. That cache is per branch: a file saved by a
run on claude/project-thread-X can only be read by runs on that same branch (and main's by everyone), so
sports prices were fetched twice (a branch, then main) and the weather prices sit on one branch only. It also
forgets anything nobody used for 7 days, and each run saves a full new copy (two runs at once: the last one wins).

How: the files live as assets of one GitHub release, tag `price-store` (outside the git history, so the repo
doesn't grow; free on a public repo, up to 2 GB per file). Asset name = path with "/" written as "--",
e.g. bt_cache/sports/hist.json.gz -> bt_cache--sports--hist.json.gz.

    python3 store.py pull [dir ...]   # before a run: fetch every store file that is missing here or bigger than ours
    python3 store.py push [dir ...]   # after a run: upload every file this run added or changed
    python3 store.py list             # what's in the store, with sizes
    python3 store.py undo <path>      # put back the version before the last push of one file
    python3 store.py selftest         # offline test with a fake GitHub

Default dirs: bt_cache econ_cache wx_cache. Rules:
  * pull never deletes a local file and only replaces one when the store's copy is bigger (caches grow).
  * push uploads a file when it is new to the store, when this run changed it, or when it is bigger than the
    store's copy. If another run pushed a bigger copy of the same file meanwhile, we skip it (theirs has more).
  * the copy that a push replaces is kept as <name>.prev, so `undo` can put it back after a bad run.
  * never fails the job: on any GitHub error it prints a warning and the Actions cache still has the data.
Needs `gh` with GH_TOKEN (contents: write) and GITHUB_REPOSITORY, which every workflow run has.
Paper research data only: public prices, no keys, nothing secret.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = "price-store"
DIRS = ["bt_cache", "econ_cache", "wx_cache"]
SEP = "--"
RECORD = ".store_pulled.json"     # per dir: what pull saw, so push knows what this run changed
OK_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def repo():
    return os.environ.get("GITHUB_REPOSITORY") or "palsk1/poly-paper-bot"


def gh(args, **kw):
    """Run gh; returns CompletedProcess. Replaced in the selftest."""
    return subprocess.run(["gh"] + args, capture_output=True, **kw)


def asset_name(rel):
    parts = rel.split("/")
    if any(SEP in p or not OK_NAME.match(p) for p in parts):
        return None
    return SEP.join(parts)


def rel_path(name):
    return name.replace(SEP, "/")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def local_files(d):
    out = {}
    base = os.path.join(ROOT, d)
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.startswith(".") or f.endswith(".tmp"):
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, ROOT).replace(os.sep, "/")] = p
    return out


def release(create=False):
    """The release as a dict (assets with id, name, size), or None."""
    r = gh(["api", f"repos/{repo()}/releases/tags/{TAG}"])
    if r.returncode == 0:
        return json.loads(r.stdout)
    if create:
        gh(["release", "create", TAG, "--repo", repo(), "--prerelease", "--title", "Price store",
            "--notes", "Shared cache of downloaded Polymarket/Kalshi prices for the research tools (store.py). "
                       "Paper research data only."])
        r = gh(["api", f"repos/{repo()}/releases/tags/{TAG}"])
        if r.returncode == 0:
            return json.loads(r.stdout)
    return None


def assets(rel):
    return {a["name"]: a for a in (rel or {}).get("assets") or []}


def in_dirs(name, dirs):
    return any(name.startswith(d + SEP) for d in dirs)


def mb(n):
    return f"{n / 1e6:.1f} MB"


def pull(dirs):
    rel = release()
    if rel is None:
        print("store: no price-store release yet (the first push makes it)")
        return
    have = assets(rel)
    got = kept = 0
    for d in dirs:
        loc = local_files(d)
        rec = {}
        for name, a in have.items():
            if not in_dirs(name, [d]) or name.endswith(".prev"):
                continue
            rp = rel_path(name)
            p = os.path.join(ROOT, rp)
            if rp in loc and os.path.getsize(p) >= a["size"]:
                kept += 1
            else:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                tmp = p + ".tmp"
                with open(tmp, "wb") as f:
                    r = gh(["api", "-H", "Accept: application/octet-stream",
                            f"repos/{repo()}/releases/assets/{a['id']}"], stdout=f)
                if r.returncode != 0 or os.path.getsize(tmp) != a["size"]:
                    print(f"store: WARNING could not fetch {rp}: {(r.stderr or b'')[:200]!r}")
                    os.path.exists(tmp) and os.remove(tmp)
                    continue
                os.replace(tmp, p)
                got += 1
                print(f"store: fetched {rp} ({mb(a['size'])})")
            rec[rp] = {"id": a["id"], "size": a["size"], "sha": sha(p),
                       "same": os.path.getsize(p) == a["size"]}
        if os.path.isdir(os.path.join(ROOT, d)):
            with open(os.path.join(ROOT, d, RECORD), "w") as f:
                json.dump(rec, f)
    print(f"store: pull done, {got} files fetched, {kept} already here")


def push(dirs):
    rel = release(create=True)
    if rel is None:
        print("store: WARNING no release and could not make one (token needs contents: write); nothing pushed")
        return
    have = assets(rel)
    sent = 0
    for d in dirs:
        rp_rec = os.path.join(ROOT, d, RECORD)
        rec = json.load(open(rp_rec)) if os.path.exists(rp_rec) else {}
        for rp, p in sorted(local_files(d).items()):
            name = asset_name(rp)
            if not name:
                print(f"store: skipped {rp} (name has characters a release can't hold)")
                continue
            a, r0, size = have.get(name), rec.get(rp), os.path.getsize(p)
            if a is None:
                why = "new"
            elif r0 and sha(p) != r0["sha"]:
                why = "changed"
                if a["id"] != r0["id"] and a["size"] > size:
                    print(f"store: skipped {rp}: another run pushed a bigger copy meanwhile ({mb(a['size'])} vs {mb(size)})")
                    continue
                if a["id"] != r0["id"]:
                    print(f"store: NOTE {rp}: another run pushed it meanwhile; ours is bigger and wins (theirs kept as .prev)")
            elif size > a["size"]:
                why = "bigger"
            else:
                continue
            if upload(p, name, a, have):
                sent += 1
                print(f"store: pushed {rp} ({mb(size)}, {why})")
    print(f"store: push done, {sent} files sent")


def upload(path, name, old, have):
    """Keep the old copy as <name>.prev, then upload. True when the new copy is in."""
    prev = have.get(name + ".prev")
    if old is not None:
        if prev is not None:
            gh(["api", "-X", "DELETE", f"repos/{repo()}/releases/assets/{prev['id']}"])
        r = gh(["api", "-X", "PATCH", f"repos/{repo()}/releases/assets/{old['id']}", "-f", f"name={name}.prev"])
        if r.returncode != 0:
            print(f"store: WARNING could not keep the old {name}: {(r.stderr or b'')[:200]!r}")
            return False
    with tempfile.TemporaryDirectory() as td:
        tp = os.path.join(td, name)
        try:
            os.link(path, tp)
        except OSError:
            import shutil
            shutil.copy(path, tp)
        for _ in range(3):
            r = gh(["release", "upload", TAG, tp, "--repo", repo(), "--clobber"])
            if r.returncode == 0:
                return True
    print(f"store: WARNING upload of {name} failed: {(r.stderr or b'')[:200]!r}")
    if old is not None:   # put the old copy back under its name
        gh(["api", "-X", "PATCH", f"repos/{repo()}/releases/assets/{old['id']}", "-f", f"name={name}"])
    return False


def undo(rp):
    have = assets(release())
    name = asset_name(rp)
    cur, prev = have.get(name), have.get((name or "") + ".prev")
    if not prev:
        print(f"store: no earlier copy of {rp}")
        return
    if cur:
        gh(["api", "-X", "DELETE", f"repos/{repo()}/releases/assets/{cur['id']}"])
    gh(["api", "-X", "PATCH", f"repos/{repo()}/releases/assets/{prev['id']}", "-f", f"name={name}"])
    print(f"store: {rp} is back to the copy before the last push ({mb(prev['size'])})")


def show():
    have = assets(release())
    tot = 0
    for name in sorted(have):
        a = have[name]
        tot += a["size"]
        print(f"{mb(a['size']):>10}  {a.get('updated_at', '')[:16]}  {rel_path(name)}")
    print(f"{mb(tot):>10}  total, {len(have)} files (.prev = the copy before the last push)")


# ---------------------------------------------------------------- selftest (offline)

def selftest():
    global ROOT, gh
    import shutil
    real_root, real_gh = ROOT, gh
    ROOT = tempfile.mkdtemp()
    store, nxt = {}, [100]          # fake release: name -> {"id", "name", "size", "data"}

    def fake(args, stdout=None, **kw):
        class R:
            returncode, stdout, stderr = 0, b"", b""
        r = R()
        if args[:2] == ["api", f"repos/{repo()}/releases/tags/{TAG}"]:
            r.stdout = json.dumps({"assets": [{k: v for k, v in a.items() if k != "data"} for a in store.values()]})
            if store.get("_none"):
                r.returncode = 1
        elif args[0] == "api" and args[1] == "-H":
            aid = int(args[-1].rsplit("/", 1)[1])
            stdout.write(next(a["data"] for a in store.values() if a["id"] == aid))
        elif args[:3] == ["api", "-X", "DELETE"]:
            aid = int(args[3].rsplit("/", 1)[1])
            for k in [k for k, a in store.items() if a["id"] == aid]:
                del store[k]
        elif args[:3] == ["api", "-X", "PATCH"]:
            aid, new = int(args[3].rsplit("/", 1)[1]), args[5].split("=", 1)[1]
            k = next(k for k, a in store.items() if a["id"] == aid)
            a = store.pop(k)
            a["name"] = new
            store[new] = a
        elif args[:2] == ["release", "upload"]:
            p = args[3]
            nxt[0] += 1
            data = open(p, "rb").read()
            store[os.path.basename(p)] = {"id": nxt[0], "name": os.path.basename(p), "size": len(data), "data": data}
        elif args[:2] == ["release", "create"]:
            pass
        else:
            raise AssertionError(args)
        return r

    gh = fake

    def put(rp, data):
        p = os.path.join(ROOT, rp)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)

    def get(rp):
        p = os.path.join(ROOT, rp)
        return open(p, "rb").read() if os.path.exists(p) else None

    try:
        # run A (old Actions cache, nothing in the store): pushes everything
        put("bt_cache/markets.json.gz", b"m" * 50)
        put("bt_cache/sports/hist.json.gz", b"s" * 30)
        put("bt_cache/x.tmp", b"junk")
        pull(["bt_cache"])
        push(["bt_cache"])
        assert set(store) == {"bt_cache--markets.json.gz", "bt_cache--sports--hist.json.gz"}, set(store)
        # run B on a fresh machine: gets both, pushes nothing
        shutil.rmtree(os.path.join(ROOT, "bt_cache"))
        pull(["bt_cache"])
        assert get("bt_cache/sports/hist.json.gz") == b"s" * 30
        n = len(store)
        push(["bt_cache"])
        assert len(store) == n
        # run C: stale smaller local copy (old branch cache) -> store copy wins on pull
        put("bt_cache/markets.json.gz", b"m" * 10)
        pull(["bt_cache"])
        assert get("bt_cache/markets.json.gz") == b"m" * 50
        # run C adds data to one file and trims another on purpose: both pushed, old kept as .prev
        put("bt_cache/markets.json.gz", b"m" * 70)
        put("bt_cache/sports/hist.json.gz", b"s" * 5)
        push(["bt_cache"])
        assert store["bt_cache--markets.json.gz"]["size"] == 70
        assert store["bt_cache--sports--hist.json.gz"]["size"] == 5
        assert store["bt_cache--sports--hist.json.gz.prev"]["size"] == 30
        # undo the trim
        undo("bt_cache/sports/hist.json.gz")
        assert store["bt_cache--sports--hist.json.gz"]["size"] == 30
        # two runs at once: D and E pull the same, E pushes a bigger copy first, D's smaller change is skipped
        shutil.rmtree(os.path.join(ROOT, "bt_cache"))
        pull(["bt_cache"])
        rec = open(os.path.join(ROOT, "bt_cache", RECORD)).read()
        put("bt_cache/markets.json.gz", b"E" * 90)
        push(["bt_cache"])                                    # E
        put("bt_cache/markets.json.gz", b"D" * 80)
        open(os.path.join(ROOT, "bt_cache", RECORD), "w").write(rec)
        push(["bt_cache"])                                    # D
        assert store["bt_cache--markets.json.gz"]["data"] == b"E" * 90
        # a local file bigger than the store's that this run did not touch (e.g. old Actions cache): pushed
        shutil.rmtree(os.path.join(ROOT, "bt_cache"))
        put("bt_cache/markets.json.gz", b"m" * 95)
        pull(["bt_cache"])
        push(["bt_cache"])
        assert store["bt_cache--markets.json.gz"]["size"] == 95
        # odd names are skipped, never break the run
        put("bt_cache/bad name.json", b"x")
        push(["bt_cache"])
        assert not any("bad" in k for k in store)
        print("store selftest OK")
    finally:
        shutil.rmtree(ROOT, ignore_errors=True)
        ROOT, gh = real_root, real_gh


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    rest = sys.argv[2:]
    if cmd == "pull":
        pull(rest or DIRS)
    elif cmd == "push":
        push(rest or DIRS)
    elif cmd == "undo":
        undo(rest[0])
    elif cmd == "selftest":
        selftest()
    else:
        show()
