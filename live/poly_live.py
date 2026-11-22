#!/usr/bin/env python3
"""REAL-MONEY Polymarket bot: the soccer_draw rule with real buys, on Jan's own server (Jan said go, 22 Nov 2026).

The rule is the paper track's own code and settings (bot.py draw_candidates, config.json "soccer_draw"), unchanged:
Yes on "will this soccer game end in a draw" at 15-50c, 20-28 hours before kickoff, at the real asking price, only
when that ask is at most 3c above the listed price, one bet per game, held to the end.

Two changes for a ~$28 bank (agreed 20-21 Nov, PR #160):
  * every second signal only, picked blindly by the market's name (a fixed coin flip: sha1(slug) even), so about
    20 bets are out at once instead of 40. The paper twin is the paper soccer_draw bets on the same markets.
  * Polymarket's smallest order: 5 shares, and an instant buy must be $1+, so draws under 20c buy 6-7 shares.

Real-order details (docs.polymarket.com, read 22 Nov): the old py-clob-client stopped placing orders on 28 Apr 2026
and py-clob-client-v2 was shelved 12 Nov, so this uses Polymarket's new official kit `polymarket-client`
(SecureClient.place_market_order, FOK = all or nothing, max_price = never pay more than listed + 3c).

  python3 live/poly_live.py check    log in with the key, show the wallet and its cash (no orders)
  python3 live/poly_live.py run      the always-on loop (the systemd service poly-live runs this)
  python3 live/poly_live.py status   what it has done so far, in plain words

Settings in ~/.live.env (Jan's file on the server; none of this is in the repo):
  POLY_PRIVATE_KEY=0x...            the key Polymarket shows under Settings, Export private key
  POLY_WALLET=0x...                 your Polymarket address (Profile, the 0x... under your name)
  POLY_RELAYER_KEY=...              Settings > API keys > Relayer key: lets the bot claim wins by itself
  POLY_RELAYER_ADDRESS=0x...        the address shown next to that Relayer key
  LIVE=yes                          without this line it only writes down what it WOULD do
  POLY_TAKE=half                    half = every second signal (fits about $28), all = every signal (needs about $60)
  POLY_MAX_BET=2.10                 most money one bet may cost (paper's dearest draw bet so far: $2.06)
  POLY_MAX_OPEN_USD=28              most money in open bets at once
  POLY_MAX_OPEN=20                  most open bets at once
  POLY_DAY_SPEND_MAX=15             most money put into new bets per day (UTC)
  POLY_DAY_LOSS_STOP=10             stop new bets for the rest of the day after losing this much
  POLY_TOTAL_LOSS_STOP=20           stop for good (writes ~/live-data/STOP-poly) after losing this much in total
"""
import hashlib
import math
import os
import sys
import time
from decimal import ROUND_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import bot  # noqa: E402
import common as C  # noqa: E402

TRACK = "soccer_draw"
SCAN_S = 30 * 60
SETTLE_S = 10 * 60
_client = None


def take(slug):
    """The blind half: True for about every second market, decided by its name only. With POLY_TAKE=all in
    ~/.live.env (Jan, 22 Nov, after adding money) every signal is taken, like the paper track."""
    if os.environ.get("POLY_TAKE", "half").strip().lower() == "all":
        return True
    return int(hashlib.sha1(slug.encode()).hexdigest(), 16) % 2 == 0


def client():
    global _client
    if _client is None:
        from polymarket import RelayerApiKey, SecureClient
        C.need("POLY_PRIVATE_KEY")
        rk = None
        if os.environ.get("POLY_RELAYER_KEY"):   # lets the bot claim winnings itself (gasless, no fee)
            rk = RelayerApiKey(key=os.environ["POLY_RELAYER_KEY"],
                               address=os.environ.get("POLY_RELAYER_ADDRESS") or os.environ.get("POLY_WALLET"))
        _client = SecureClient.create(private_key=os.environ["POLY_PRIVATE_KEY"],
                                      wallet=os.environ.get("POLY_WALLET") or None, api_key=rk)
    return _client


# Permissions Polymarket's kit lists as "standard" that this bot never needs: the perps deposit contract and the
# auto-claim operator (the bot claims wins itself). From polymarket/environments.py, 22 Nov. Fewer permissions = safer.
EXTRAS = {"0xdca4af75705dbb50f62437045aff9921947917d2", "0xa1200000d0002264c9a1698e001292d00e1b00af"}


def items(pages):
    """Polymarket's kit hands lists back page by page: walking the list itself gives pages, not rows.
    (Bug fix 22 Nov: the claim sweep walked pages, so it would have claimed nothing.)"""
    return list(pages.iter_items()) if hasattr(pages, "iter_items") else list(pages)


CLAIMS_PER_ROUND = 5


def claim_all(book):
    """Claim every won bet that is still waiting to be paid out, so the cash is free for the next bets (Jan, 22 Nov:
    "I had to claim manually every time"). Polymarket does not pay out by itself: a won position must be redeemed.
    This sweeps ALL claimable positions of the wallet (also old ones from before the bot), once per settle round,
    and retries ones that failed. Needs POLY_RELAYER_KEY (Polymarket Settings > API keys > Relayer key)."""
    cl = client()
    try:
        rows = items(cl.list_positions(status="REDEEMABLE"))
    except Exception as e:
        book.log("claim_list_failed", err=f"{type(e).__name__}: {e}"[:200])
        return
    seen, n = set(), 0
    for p in rows:
        cid = str(getattr(p, "condition_id", "") or "")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        val = float(getattr(p, "current_value", 0) or 0)
        if val < 0.01:
            continue      # a lost bet also shows as "to be claimed" but pays $0: leave it (fix 22 Nov, the first
                          # real run spent minutes claiming Jan's old lost bets one by one and could not answer)
        if n >= CLAIMS_PER_ROUND:
            break         # the rest next round, so the bot stays free to answer the phone and place bets
        n += 1
        try:
            h = cl.redeem_positions(condition_id=cid)
            res = getattr(h, "wait", lambda: "sent")()
            book.log("claimed", condition_id=cid, title=str(getattr(p, "title", ""))[:80], value=round(val, 2),
                     result=str(res)[:120])
        except Exception as e:
            book.log("claim_failed", condition_id=cid, value=round(val, 2), err=f"{type(e).__name__}: {e}"[:200])


def cash():
    b = client().get_balance_allowance(asset_type="COLLATERAL")
    return int(b.balance) / 1e6


def size_for(asks, min_size):
    """(shares, average ask) for the smallest order Polymarket takes: 5+ shares and $1+ for an instant buy."""
    shares = max(5, int(math.ceil(min_size or 5)))
    for _ in range(40):
        px = bot.walk(asks, shares)
        if px is None:
            return None, None
        if shares * px >= 1.0:
            return shares, px
        shares += 1
    return None, None


def place(book):
    r = bot.rules_for(TRACK)
    cands = bot.draw_candidates([TRACK])[TRACK]
    held_events = {o.get("event_key") for o in book.state["open"].values()}
    max_bet, max_open_usd = C.envf("POLY_MAX_BET", 2.10), C.envf("POLY_MAX_OPEN_USD", 28)
    max_open, day_max = int(C.envf("POLY_MAX_OPEN", 20)), C.envf("POLY_DAY_SPEND_MAX", 15)
    have = None
    n_half = 0
    for c in cands:
        slug = c["slug"]
        if not take(slug):
            continue
        n_half += 1
        if slug in book.state["open"] or slug in book.state["done"] or c["event_key"] in held_events:
            continue
        if len(book.state["open"]) >= max_open:
            book.log("skip_cap_count", slug=slug, open=len(book.state["open"]))
            break
        bk = bot.book(c["token"])
        if not bk or not bk["asks"]:
            continue
        shares, px = size_for(bk["asks"], bk.get("min_size"))
        if shares is None:
            continue
        if not (r["min_price"] <= px <= r["max_price"] + 0.01):
            continue
        # Polymarket takes price limits in whole cents only (22 Nov: half-cent limits were refused), so the limit is
        # listed + 3c rounded DOWN to a cent: never looser than the paper rule.
        cap_px = math.floor((c["price"] + r["max_over_listed"]) * 100 + 1e-9) / 100
        if px > cap_px + 1e-9:
            continue            # thin book: the real ask is 3c+ above the listed price (same skip as paper)
        fee = bot.taker_fee(shares, px, c["fee_rate"])
        cost = round(shares * px + fee, 4)
        if cost > max_bet + 1e-9:
            book.log("skip_cap_bet", slug=slug, cost=cost, cap=max_bet)
            continue
        if book.open_cost() + cost > max_open_usd + 1e-9:
            book.log("skip_cap_open", slug=slug, open_cost=book.open_cost(), cap=max_open_usd)
            continue
        if book.day()["spent"] + cost > day_max + 1e-9:
            book.log("skip_cap_day", slug=slug, spent=book.day()["spent"], cap=day_max)
            break
        m = c["market"]
        rec = {"slug": slug, "token": c["token"], "condition_id": m.get("conditionId"), "event_key": c["event_key"],
               "title": c["title"], "listed": c["price"], "ask": round(px, 4), "shares": shares, "cost": cost,
               "fee_est": round(fee, 4), "signal": c.get("signal"), "placed": C.iso(), "day": C.today(),
               "end": c["end"]}
        if C.is_live():
            if have is None:
                have = cash()
            if have < cost + 0.05:
                book.log("skip_no_cash", slug=slug, cash=round(have, 2), cost=cost)
                break
            amount = Decimal(str(shares * px)).quantize(Decimal("0.01"), rounding=ROUND_UP)
            amount = max(amount, Decimal("1.00"))
            book.state["done"].append(slug)      # one try per market, saved first so a crash can't buy twice
            book.save()
            try:
                res = client().place_market_order(token_id=c["token"], side="BUY", amount=amount,
                                                  max_price=Decimal(str(cap_px)), order_type="FOK")
            except Exception as e:
                book.log("order_failed", slug=slug, err=f"{type(e).__name__}: {e}"[:300])
                if type(e).__name__ == "UserInputError":     # stopped on our side, nothing was sent: may try again
                    book.state["done"].remove(slug)
                    book.save()
                continue
            if not getattr(res, "ok", False):
                book.log("order_refused", slug=slug, code=getattr(res, "code", "?"), err=getattr(res, "message", "")[:200])
                continue
            spent, got = float(res.making_amount), float(res.taking_amount)
            rec.update({"order_id": C.scrub(str(res.order_id)),   # short form: the full number points at the wallet
                         "status": res.status, "spent": spent, "shares": got,
                        "ask": round(spent / got, 4) if got else rec["ask"], "cost": round(spent + fee, 4)})
            book.state["done"].remove(slug)
            have -= spent + fee
        book.state["open"][slug] = rec
        book.state["bets"] += 1
        held_events.add(c["event_key"])
        d = book.day()
        d["spent"] = round(d["spent"] + rec["cost"], 4)
        d["bets"] += 1
        book.log("buy" if C.is_live() else "would_buy", **rec)
        book.save()
    book.log("scan", signals=len(cands), our_half=n_half, open=len(book.state["open"]), open_cost=book.open_cost())


def settle(book):
    for slug, o in list(book.state["open"].items()):
        try:
            rows = bot.http_json(f"{bot.GAMMA}/markets", {"slug": slug})
        except Exception as e:
            print(f"gamma failed for {slug}: {e}", flush=True)
            continue
        m = rows[0] if isinstance(rows, list) and rows else None
        if not m:
            continue
        prices = [bot.fnum(x, None) for x in bot.jlist(m.get("outcomePrices"))]
        if not m.get("closed") or len(prices) != 2 or None in prices or max(prices) < 0.99:
            continue
        pay = 1.0 if prices[0] >= 0.99 else 0.0
        spent = o.get("spent", o["shares"] * o["ask"])
        pnl = o["shares"] * pay - spent - o.get("fee_est", 0)
        extra = {"result": "draw" if pay else "no draw", "how": "real" if o.get("order_id") else "dry run"}
        book.settle(slug, pnl, filled=o["shares"], **extra)   # a lost draw is normal (about 2 in 3): no push
    book.save()
    if C.is_live() and os.environ.get("POLY_RELAYER_KEY"):
        claim_all(book)       # wins are paid out by claiming; also picks up any that failed before


def run():
    C.load_env()
    book = C.Book("poly")
    if not book.state.get("fix_1122"):
        # One time: on 22 Nov nine draws were refused for a half-cent price limit and marked "tried once".
        # Nothing was sent for them, so they get their try back. (No market had finished yet, so the list
        # held only those nine.)
        book.state["done"] = [s for s in book.state["done"] if s in book.state["open"]]
        book.state["fix_1122"] = True
        book.save()
    book.log("start", rule=TRACK, take=os.environ.get("POLY_TAKE", "half"), max_bet=C.envf("POLY_MAX_BET", 2.10), max_open_usd=C.envf("POLY_MAX_OPEN_USD", 28),
             mode="LIVE (real money)" if C.is_live() else "dry run", **C.read_balance(cash))
    if C.is_live():
        cl = client()
        book.log("login", wallet_type=str(cl.wallet_type), cash=round(cash(), 2))   # no address: the log is public
    last_scan = last_settle = last_up = 0
    was_stopped = None
    while True:
        t0 = time.time()
        try:
            if time.time() - last_settle > SETTLE_S:
                last_settle = time.time()
                settle(book)
            C.control("poly", book, lambda: status_text(book.state))
            why = C.stop_reason("poly", book)
            if why != was_stopped:
                book.log("paused" if why else "running", why=why or "")
                was_stopped = why
            if not why and time.time() - last_scan > SCAN_S:
                last_scan = time.time()
                place(book)
        except Exception as e:
            book.log("error", err=f"{type(e).__name__}: {e}"[:300])
        C.beat(book, time.time() - t0, balance_fn=cash)
        if time.time() - last_up > C.UPLOAD_S:
            last_up = time.time()
            try:
                print(C.upload("poly"), flush=True)
            except Exception as e:
                print(f"upload failed: {e}", flush=True)
        time.sleep(30)


def check():
    C.load_env()
    cl = client()
    print(f"OK: logged in. Wallet {cl.wallet} ({cl.wallet_type}). Cash ${cash():.2f}.")
    if not os.environ.get("POLY_WALLET"):
        print("WARNING: no Polymarket address saved (POLY_WALLET), so this is a new empty wallet, not your account.\n"
              "  Fix: run add_keys.py again, Enter on everything except 'Your Polymarket address'.")
    try:
        print("Closed-only mode (account limited to selling):", cl.get_closed_only_mode())
    except Exception as e:
        print(f"closed-only check failed: {e}")
    try:
        st = cl.get_trading_approvals_state()
        miss = getattr(st, "missing", None)
        rows = list(getattr(miss, "erc20", []) or []) + list(getattr(miss, "erc1155", []) or [])
        need = [r for r in rows if str(getattr(r, "spender", None) or getattr(r, "operator", "")).lower() not in EXTRAS]
        if not need:
            print("Trading permissions: all set for buying and claiming."
                  + (f" ({len(rows)} extra ones are off: Polymarket's perps and auto-claim add-ons, which this "
                     "bot does not use. Leave them off.)" if rows else ""))
        else:
            print(f"Trading permissions: {len(need)} missing. This wallet has not yet allowed Polymarket's exchange "
                  "to use its cash, so buys would be refused.\n  Fix (free, moves no money): "
                  "~/lenv/bin/python ~/poly-paper-bot/live/poly_live.py approve")
    except Exception as e:
        print(f"approvals check failed: {e}")
    if os.environ.get("POLY_RELAYER_KEY"):
        try:
            n = len([p for p in items(cl.list_positions(status="REDEEMABLE"))
                     if float(getattr(p, "current_value", 0) or 0) >= 0.01])
            print(f"Claiming: set up (relayer key). {n} won bet(s) waiting to be claimed now; the bot claims them.")
        except Exception as e:
            print(f"Claiming: relayer key set, but listing claimable bets failed: {e}")
    else:
        print("Claiming: NOT set up. Wins stay unclaimed until you press Claim in the app. "
              "Fix: add the Relayer key with add_keys.py (see live/README.md).")
    print("Mode:", "LIVE, real buys" if C.is_live() else "dry run (add LIVE=yes to ~/.live.env for real buys)")
    print("Stop check:", C.stop_reason("poly", C.Book("poly")) or "nothing stops it")
    print(C.phone_check("Polymarket bot"))


def status_text(s):
    d = s["days"].get(C.today(), {"bets": 0, "pnl": 0.0})
    return (f"Since {s['started'][:10]}: {s['bets']} bets, {s['won']} won, {s['lost']} lost, P&L ${s['realized']:+.2f}.\n"
            f"Today: {d['bets']} new bets, P&L ${d['pnl']:+.2f}. "
            f"Open now: {len(s['open'])} (${sum(o['cost'] for o in s['open'].values()):.2f}).")


def status():
    C.load_env()
    s = C.Book("poly").state
    print("Polymarket bot. " + status_text(s))
    for d in sorted(s["days"])[-7:]:
        v = s["days"][d]
        print(f"  {d}: {v['bets']} bets, ${v['spent']:.2f} put in, P&L ${v['pnl']:+.2f}")


def approve():
    """One time, Jan runs it himself: let Polymarket's exchange use this wallet's cash for trades (the same
    permissions the website sets on a first trade). Free (gasless), moves no money."""
    C.load_env()
    cl = client()
    print(f"Wallet {cl.wallet} ({cl.wallet_type}). Asking for the standard trading permissions...")
    cl.setup_trading_approvals()
    st = cl.get_trading_approvals_state()
    print("Trading permissions: all set." if getattr(st, "is_fully_approved", False)
          else "Still missing some. Run the check again in a minute; if it stays, tell Claude.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"run": run, "check": check, "status": status, "approve": approve}.get(cmd, status)()
