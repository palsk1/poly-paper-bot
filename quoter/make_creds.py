"""Run once on Jan's server: makes the login the paper quoter uses, and writes it to ~/.quoter.env (only you can read it).

Two ways:
  python3 make_creds.py new    (recommended) makes a brand-new, EMPTY wallet just for listening. It never holds money,
                               so even if the server were broken into, there is nothing to take.
  python3 make_creds.py mine   uses your own Polymarket account. You paste its private key here, on the server only
                               (it is typed hidden, used once to make the login, and NOT saved anywhere).

Either way, ~/.quoter.env holds only an API key/secret/passphrase. Those can't move money on their own:
moving money needs a signature from the private key, which the quoter never has. Never paste any of this into chat
or commit it to the repo (it's public).
"""
import getpass
import os
import sys

HOST, CHAIN = "https://clob.polymarket.com", 137
OUT = os.path.expanduser("~/.quoter.env")


def main():
    from py_clob_client.client import ClobClient
    mode = sys.argv[1] if len(sys.argv) > 1 else "new"
    if mode == "new":
        from eth_account import Account
        acct = Account.create()
        key, signer, maker, sig = acct.key.hex(), acct.address, acct.address, 0
        print("Made a new empty wallet:", signer)
    elif mode == "mine":
        key = getpass.getpass("Polymarket private key (hidden, not saved): ").strip()
        from eth_account import Account
        signer = Account.from_key(key).address
        maker = input("Your Polymarket wallet address (Profile page, starts 0x): ").strip()
        print("How do you log in to Polymarket?  1 = email or Google   2 = a browser wallet like MetaMask   3 = newer deposit wallet")
        sig = int(input("1, 2 or 3: ").strip() or "1")
    else:
        sys.exit("use: python3 make_creds.py new   or   python3 make_creds.py mine")
    c = ClobClient(HOST, key=key, chain_id=CHAIN, signature_type=sig, funder=maker)
    cr = c.create_or_derive_api_creds()
    del key, c
    lines = [f"POLY_API_KEY={cr.api_key}", f"POLY_API_SECRET={cr.api_secret}", f"POLY_API_PASSPHRASE={cr.api_passphrase}",
             f"POLY_SIGNER={signer}", f"POLY_MAKER={maker}", f"POLY_SIG_TYPE={sig}"]
    old = {}
    if os.path.exists(OUT):
        for ln in open(OUT):
            if "=" in ln:
                k, v = ln.strip().split("=", 1)
                old[k] = v
    for ln in lines:
        k, v = ln.split("=", 1)
        old[k] = v
    fd = os.open(OUT, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("".join(f"{k}={v}\n" for k, v in old.items()))
    os.chmod(OUT, 0o600)
    print(f"Saved the login to {OUT} (only you can read it). The private key was not saved.")


if __name__ == "__main__":
    main()
