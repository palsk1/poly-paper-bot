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
  LIVE=yes                          without this line it only writes down what it WOULD do
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
    """The blind half: True for about every second market, decided by its name only."""
    return int(hashlib.sha1(slug.encode()).hexdigest(), 16) % 2 == 0


def client():
    global _client
    if _client is None:
        from polymarket import SecureClient
        C.need("POLY_PRIVATE_KEY")
        _client = SecureClient.create(private_key=os.environ["POLY_PRIVATE_KEY"],
                                      wallet=os.environ.get("POLY_WALLET") or None)
    return _client


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
        cap_px = round(c["price"] + r["max_over_listed"], 4)
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
                continue
            if not getattr(res, "ok", False):
                book.log("order_refused", slug=slug, code=getattr(res, "code", "?"), err=getattr(res, "message", "")[:200])
                continue
            spent, got = float(res.making_amount), float(res.taking_amount)
            rec.update({"order_id": str(res.order_id), "status": res.status, "spent": spent, "shares": got,
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
        if pay and o.get("order_id") and o.get("condition_id"):
            try:
                h = client().redeem_positions(condition_id=o["condition_id"])
                extra["redeem"] = str(getattr(h, "wait", lambda: "sent")())[:120]
            except Exception as e:
                extra["redeem"] = f"failed, press Claim in the Polymarket app: {type(e).__name__}: {e}"[:200]
        book.settle(slug, pnl, filled=o["shares"], **extra)   # a lost draw is normal (about 2 in 3): no push
    book.save()


def run():
    C.load_env()
    book = C.Book("poly")
    book.log("start", rule=TRACK, max_bet=C.envf("POLY_MAX_BET", 2.10), max_open_usd=C.envf("POLY_MAX_OPEN_USD", 28),
             mode="LIVE (real money)" if C.is_live() else "dry run")
    if C.is_live():
        cl = client()
        book.log("login", wallet=str(cl.wallet), wallet_type=str(cl.wallet_type), cash=round(cash(), 2))
    last_scan = last_settle = last_up = 0
    was_stopped = None
    while True:
        try:
            if time.time() - last_settle > SETTLE_S:
                last_settle = time.time()
                settle(book)
            why = C.stop_reason("poly", book)
            if why != was_stopped:
                book.log("paused" if why else "running", why=why or "")
                was_stopped = why
            if not why and time.time() - last_scan > SCAN_S:
                last_scan = time.time()
                place(book)
        except Exception as e:
            book.log("error", err=f"{type(e).__name__}: {e}"[:300])
        if time.time() - last_up > 3600:
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
    try:
        print("Closed-only mode (account limited to selling):", cl.get_closed_only_mode())
    except Exception as e:
        print(f"closed-only check failed: {e}")
    try:
        print("Trading approvals:", cl.get_trading_approvals_state())
    except Exception as e:
        print(f"approvals check failed: {e}")
    print("Mode:", "LIVE, real buys" if C.is_live() else "dry run (add LIVE=yes to ~/.live.env for real buys)")
    print("Stop check:", C.stop_reason("poly", C.Book("poly")) or "nothing stops it")


def status():
    C.load_env()
    s = C.Book("poly").state
    print(f"Polymarket bot since {s['started']}: {s['bets']} bets, {s['won']} won, {s['lost']} lost, "
          f"P&L ${s['realized']:+.2f}, {len(s['open'])} open now (${sum(o['cost'] for o in s['open'].values()):.2f}).")
    for d in sorted(s["days"])[-7:]:
        v = s["days"][d]
        print(f"  {d}: {v['bets']} bets, ${v['spent']:.2f} put in, P&L ${v['pnl']:+.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"run": run, "check": check, "status": status}.get(cmd, status)()
