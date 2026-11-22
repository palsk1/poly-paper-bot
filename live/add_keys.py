"""Put your keys on the server, typed straight into this server only. Run it on the server:

    ~/lenv/bin/python ~/poly-paper-bot/live/add_keys.py

It asks one question at a time. Press Enter to skip a question (keeps what is already saved).
The keys go to ~/.live.env and ~/.kalshi.key, readable only by you. Never paste them into chat or the repo.
"""
import getpass
import os

ENV = os.path.expanduser("~/.live.env")
KFILE = os.path.expanduser("~/.kalshi.key")


def read_env():
    rows = []
    if os.path.exists(ENV):
        rows = [ln.rstrip("\n") for ln in open(ENV)]
    return rows


def write_env(rows, new):
    out, seen = [], set()
    for ln in rows:
        k = ln.split("=", 1)[0].strip() if "=" in ln and not ln.lstrip().startswith("#") else None
        if k in new:
            out.append(f"{k}={new[k]}")
            seen.add(k)
        else:
            out.append(ln)
    out += [f"{k}={v}" for k, v in new.items() if k not in seen]
    fd = os.open(ENV, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(out) + "\n")
    os.chmod(ENV, 0o600)


def main():
    new = {}
    print("KALSHI (kalshi.com > Account & security > API keys > Create key)")
    kid = input("  Kalshi key ID (looks like a952bcbe-ec3b-...): ").strip()
    if kid:
        new["KALSHI_KEY_ID"] = kid
    print("  Now paste the PRIVATE KEY text Kalshi gave you (starts with -----BEGIN, ends with -----END ... KEY-----).")
    print("  Paste it, then press Enter. (Just press Enter to skip.)")
    lines = []
    while True:
        ln = input()
        if not lines and not ln.strip():
            break
        lines.append(ln.strip())
        if ln.strip().startswith("-----END"):
            break
    if lines:
        fd = os.open(KFILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(lines) + "\n")
        new["KALSHI_KEY_FILE"] = KFILE
        print(f"  saved to {KFILE}")

    print("\nPOLYMARKET (polymarket.com > Settings > Export private key)")
    pk = getpass.getpass("  Polymarket private key (hidden while you type/paste, starts with 0x): ").strip()
    if pk:
        new["POLY_PRIVATE_KEY"] = pk if pk.startswith("0x") else "0x" + pk
    w = input("  Your Polymarket address (Profile page, the 0x... under your name): ").strip()
    if w:
        new["POLY_WALLET"] = w

    print("\nOPTIONAL")
    t = getpass.getpass("  GitHub token so the logs reach the repo (same kind as the combo listener's, Enter to skip): ").strip()
    if t:
        new["GITHUB_TOKEN"] = t
    n = getpass.getpass("  ntfy topic for phone alerts (Enter to skip): ").strip()
    if n:
        new["NTFY_TOPIC"] = n

    write_env(read_env(), new)
    print(f"\nSaved {', '.join(new) or 'nothing'} to {ENV} (only you can read it).")
    print("Next: ~/lenv/bin/python ~/poly-paper-bot/live/kalshi_live.py check   and   .../poly_live.py check")


if __name__ == "__main__":
    main()
