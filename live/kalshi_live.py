#!/usr/bin/env python3
"""REAL-MONEY Kalshi bot: the kc_maker_safe_usd rule with real bids, on Jan's own server (Jan said go, 22 Nov 2026).

The rule is the paper track's own code and settings (bot.py kmaker_*, config.json "kc_maker_safe_usd"), unchanged:
Kalshi 15-minute crypto windows (7 coins), 0.75-5.5 minutes before the close, on the side whose middle price is
50c+, where the best bid is 95c+: rest a bid one tick above it (or join it), only when Binance sits 2+ "typical moves"
on our side of the strike, both as it is and after moving Binance onto Kalshi's dollar scale. Hold to the result.

Real-order details (docs.kalshi.com, read 22 Nov): post_only (never takes, never pays a taker fee, refused if it
would cross), expiration_ts = the window's close (the bid dies with the window), cancel_order_on_pause (Kalshi
pauses Thursdays 03:00-05:00 New York). One bid per window per coin, same as paper.

  python3 live/kalshi_live.py check    read the balance with the key (no orders): is the key OK?
  python3 live/kalshi_live.py run      the always-on loop (the systemd service kalshi-live runs this)
  python3 live/kalshi_live.py status   what it has done so far, in plain words

Settings in ~/.live.env (Jan's file on the server; none of this is in the repo):
  KALSHI_KEY_ID=...                 the API key id from kalshi.com (Account, API keys)
  KALSHI_KEY_FILE=~/.kalshi.key     the private key file kalshi.com gave you (chmod 600)
  LIVE=yes                          without this line it only writes down what it WOULD do
  KALSHI_USD_PER_ORDER=4            money per bid
  KALSHI_MAX_OPEN_USD=30            most money in bids at once
  KALSHI_DAY_LOSS_STOP=10           stop new bids for the rest of the day (UTC) after losing this much
  KALSHI_MIN_Z_USD=2.3              safety bar after the Binance-vs-Kalshi gap correction (paper twin uses 2.0)
  KALSHI_TOTAL_LOSS_STOP=20         stop for good (writes ~/live-data/STOP-kalshi) after losing this much in total
"""
import base64
import datetime as dt
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import bot  # noqa: E402  (the paper bot: same rule code, same settings)
import common as C  # noqa: E402

TRACK = "kc_maker_safe_usd"
API_PATH = "/trade-api/v2"
LOOP_S = 15
_key = None


# ---------------------------------------------------------------- signed requests (docs: getting_started/api_keys)
def key():
    global _key
    if _key is None:
        from cryptography.hazmat.primitives import serialization
        path = os.path.expanduser(os.environ.get("KALSHI_KEY_FILE", "~/.kalshi.key"))
        with open(path, "rb") as f:
            _key = serialization.load_pem_private_key(f.read(), password=None)
    return _key


def sign(text):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    k = key()
    if isinstance(k, Ed25519PrivateKey):
        sig = k.sign(text.encode())
    else:
        sig = k.sign(text.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(sig).decode()


def kreq(method, path, body=None, params=None):
    """A logged-in Kalshi call. path like '/portfolio/balance'. Returns (status, json or text)."""
    url = bot.KALSHI + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for i in range(4):
        ts = str(int(time.time() * 1000))
        h = {"KALSHI-ACCESS-KEY": os.environ["KALSHI_KEY_ID"], "KALSHI-ACCESS-TIMESTAMP": ts,
             "KALSHI-ACCESS-SIGNATURE": sign(ts + method + API_PATH + path), "User-Agent": C.UA,
             "Accept": "application/json"}
        data = None
        if body is not None:
            data = C.json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read().decode()
                return r.status, (C.json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503, 504) and i < 3:
                time.sleep(1 + 2 * i)
                continue
            try:
                return e.code, C.json.loads(raw)
            except ValueError:
                return e.code, raw[:500]
        except Exception as e:
            if i == 3:
                return 0, f"{type(e).__name__}: {e}"
            time.sleep(1 + 2 * i)
    return 0, "gave up"


CRYPTO_SHARD = 2    # Kalshi keeps each account's money in compartments ("exchange indexes"); crypto bets use number 2


def balances():
    """(whole account, the Crypto compartment). A bot's bid is only paid from the compartment its market
    trades in: Kalshi moves money by itself for bets made by hand, never for a bot (22 Nov 2026)."""
    st, res = kreq("GET", "/portfolio/balance")
    if st != 200:
        raise RuntimeError(f"balance failed: {st} {res}")
    v = res.get("balance_dollars")
    total = float(v) if v not in (None, "") else res.get("balance", 0) / 100
    parts = {}
    for x in res.get("balance_breakdown") or []:
        try:
            parts[int(x["exchange_index"])] = float(x["balance"])
        except (KeyError, TypeError, ValueError):
            pass
    return total, (parts.get(CRYPTO_SHARD, 0.0) if parts else total)


def balance():
    return balances()[1]


def balance_log():
    """For the notebook: whole account and the Crypto part (the bot can only bid with that)."""
    total, crypto = balances()
    return {"balance": total, "balance_crypto": crypto}


# ---------------------------------------------------------------- one loop
def minutes_to_close(t=None):
    t = t or C.utcnow()
    nxt = t.replace(second=0, microsecond=0) + dt.timedelta(minutes=15 - t.minute % 15)
    return (nxt - t).total_seconds() / 60


def settle(book):
    for tk, o in list(book.state["open"].items()):
        close = bot.parse_iso(o["close"])
        if C.utcnow() < close + dt.timedelta(seconds=60):
            continue
        bot._kalshi_cache.pop(tk, None)
        m = bot.kalshi_market(tk)
        res = str((m or {}).get("result") or "").lower()
        if res not in ("yes", "no"):
            if C.utcnow() - close > dt.timedelta(hours=6) and not o.get("late_warned"):
                o["late_warned"] = True
                book.log("no_result_yet", ticker=tk)
                book.save()
            continue
        pay = 1.0 if res == o["side"] else 0.0
        if o.get("order_id"):     # a real order: read what really filled and what it cost
            st, r = kreq("GET", f"/portfolio/orders/{o['order_id']}")
            if st != 200:
                book.log("order_read_failed", ticker=tk, status=st, err=str(r)[:200])
                continue
            od = r.get("order") or {}
            filled = bot.fnum(od.get("fill_count_fp"), 0)
            # Our bid only ever waits (post-only), so every filled contract cost exactly our price. Kalshi's own
            # cost number is kept beside it as a cross-check (its meaning for the No side is not spelled out).
            cost = filled * o["price"]
            api_cost = bot.fnum(od.get("maker_fill_cost_dollars"), 0) + bot.fnum(od.get("taker_fill_cost_dollars"), 0)
            fees = bot.fnum(od.get("maker_fees_dollars"), 0) + bot.fnum(od.get("taker_fees_dollars"), 0)
            how = "real"
        else:                     # dry run: the paper fill rule on the real trade tape
            try:
                trades, _ = bot.kalshi_trades(tk, bot.parse_iso(o["placed"]).timestamp(), close.timestamp())
            except Exception as e:
                book.log("tape_failed", ticker=tk, err=str(e)[:200])
                continue
            filled, _ = bot.kmaker_fill({**o, "placed": o["placed"]}, trades)
            cost, fees, how = filled * o["price"], 0.0, "paper fill (dry run)"
        pnl = filled * pay - cost - fees
        extra = {"kalshi_cost": round(api_cost, 4), "kalshi_side": od.get("outcome_side")} if o.get("order_id") else {}
        book.settle(tk, pnl, result=res, filled=filled, fill_cost=round(cost, 4), fees=round(fees, 4), how=how, **extra)
        if pnl < 0:
            C.push("Kalshi bot: a bid lost", f"{tk} {o['side'].upper()} at {o['price'] * 100:.1f}c, "
                                             f"{filled:.0f} filled, ${pnl:+.2f}. Total so far ${book.state['realized']:+.2f}.")


ORDERS = "/portfolio/events/orders"     # Kalshi's new order address; the old /portfolio/orders answers 410 since Nov 2026


def order_body(tk, side, price, shares, close):
    """A resting bid in Kalshi's new order form (22 Nov: the old form was switched off, every bid was refused).
    The new form speaks only about the YES side: 'bid' buys Yes at the price; 'ask' sells Yes at the price, which is
    the same as buying No at 1 minus that price. So our No bid at 99.4c goes in as 'ask' at 0.6c."""
    yes_px = price if side == "yes" else 1 - price
    return {"ticker": tk, "side": "bid" if side == "yes" else "ask", "count": f"{shares:.2f}",
            "price": f"{yes_px:.4f}", "time_in_force": "good_till_canceled",
            "expiration_time": int(close.timestamp()), "post_only": True, "cancel_order_on_pause": True,
            "self_trade_prevention_type": "taker_at_cross", "client_order_id": str(uuid.uuid4())}


def cancel_all(book, why):
    for tk, o in book.state["open"].items():
        if o.get("order_id") and not o.get("cancelled") and C.utcnow() < bot.parse_iso(o["close"]):
            st, r = kreq("DELETE", f"{ORDERS}/{o['order_id']}", params={"market_ticker": tk})
            o["cancelled"] = True
            book.log("cancelled", ticker=tk, status=st, why=why[:120])
    book.save()


def place(book):
    left_q = minutes_to_close()
    r = bot.rules_for(TRACK)
    if not (r.get("min_minutes_left", 0.75) <= left_q <= r.get("max_minutes_left", 5.5) + 0.05):
        return
    bot._kmaker_spot.clear()          # the paper bot keeps these for one run; here every loop needs fresh prices
    usd = C.envf("KALSHI_USD_PER_ORDER", 4)
    max_open = C.envf("KALSHI_MAX_OPEN_USD", 30)
    cash = None
    tries = book.state.setdefault("tries", {})
    if len(tries) > 500:
        book.state["tries"] = tries = dict(list(tries.items())[-200:])
    for series in r.get("series", []):
        for m in bot.kmaker_open_markets(series):
            close = bot.parse_iso(m.get("close_time"))
            if not close:
                continue
            left = (close - C.utcnow()).total_seconds() / 60
            tk = m.get("ticker")
            if not (r.get("min_minutes_left", 0.75) <= left <= r.get("max_minutes_left", 5.5)):
                continue
            if tk in book.state["open"] or tk in book.state["done"] or tries.get(tk, 0) >= 3:
                continue
            bk = bot.kalshi_book_sides(tk)
            if not bk or not bk["yes"] or not bk["no"]:
                continue
            yb, ya = bk["yes"][0][0], round(1 - bk["no"][0][0], 4)
            if not (0 < yb < ya < 1):
                continue
            side = "yes" if (yb + ya) / 2 >= 0.5 else "no"
            bid, ask = (yb, ya) if side == "yes" else (round(1 - ya, 4), round(1 - yb, 4))
            got = bot.kmaker_price(r, bid, ask)
            if not got:
                continue
            price, front = got
            strike = bot.fnum(m.get("floor_strike"), None)
            z = bot.kmaker_z(series, strike, left, side)
            if z is None or z < r["min_spot_z"]:
                continue
            zu = bot.kmaker_z(series, strike, left, side, open_ts=(close - dt.timedelta(minutes=15)).timestamp())
            if zu is None or zu < max(r["min_spot_z"], C.envf("KALSHI_MIN_Z_USD", 2.3)):
                continue                   # real bot only (Jan, 23 Nov): it looks every 15 s, so it caught coins the
                                           # moment they first cleared 2.0; all 3 first real losses sat at 2.1-2.26
            shares = max(1, int(usd / price + 1e-9))
            cost = round(shares * price, 4)
            if cost > usd + 1e-6:
                continue
            if book.open_cost() + cost > max_open + 1e-6:
                book.log("skip_cap_open", ticker=tk, open_cost=book.open_cost(), cap=max_open)
                continue
            queue = sum(sz for p, sz in bk[side] if abs(p - price) < 1e-6)
            rec = {"ticker": tk, "series": series, "side": side, "price": price, "shares": shares, "cost": cost,
                   "close": C.iso(close), "placed": C.iso(), "minutes_left": round(left, 2), "bid": bid, "ask": ask,
                   "front": front, "queue": round(queue, 2), "spot_z": round(z, 2), "spot_z_usd": round(zu, 2),
                   "day": C.today()}
            if C.is_live():
                if cash is None:
                    cash = balance()
                if cash < cost:
                    tied = round(book.open_cost(), 2)   # money waiting in our own bids comes back within 15 min
                    book.log("skip_no_cash", ticker=tk, crypto_cash=round(cash, 2), cost=cost, in_bids=tied)
                    if cash + tied < cost and book.state.get("cash_push") != C.today():
                        book.state["cash_push"] = C.today()
                        book.save()
                        C.push("Kalshi bot: no money to bid with",
                               f"The Crypto part of your Kalshi account has ${cash:.2f}, a bid needs ${cost:.2f}. "
                               "Move money there: kalshi.com/account/exchange-indexes")
                    continue
                body = order_body(tk, side, price, shares, close)
                tries[tk] = tries.get(tk, 0) + 1
                book.save()               # count the try first, so a crash right after can't send a second bid
                st, res = kreq("POST", ORDERS, body)
                od = res if isinstance(res, dict) else {}
                if st not in (200, 201) or not od.get("order_id"):
                    book.log("order_refused", ticker=tk, status=st, err=str(res)[:300], price=price, side=side)
                    book.save()
                    continue
                rec["order_id"] = od["order_id"]
                rec["status"] = "accepted"
                cash -= cost
            book.state["open"][tk] = rec
            book.state["bets"] += 1
            d = book.day()
            d["spent"] = round(d["spent"] + cost, 4)
            d["bets"] += 1
            book.log("bid" if C.is_live() else "would_bid", **rec)
            book.save()


def run():
    C.load_env()
    if C.is_live():
        C.need("KALSHI_KEY_ID")
    book = C.Book("kalshi")
    book.log("start", rule=TRACK, usd_per_order=C.envf("KALSHI_USD_PER_ORDER", 4),
             max_open=C.envf("KALSHI_MAX_OPEN_USD", 30), mode="LIVE (real money)" if C.is_live() else "dry run",
             **C.read_balance(balance_log))
    last_up, was_stopped = 0, None
    while True:
        t0 = time.time()
        try:
            settle(book)
            C.control("kalshi", book, lambda: status_text(book.state))
            why = C.stop_reason("kalshi", book)
            if why != was_stopped:
                book.log("paused" if why else "running", why=why or "")
                was_stopped = why
            if why:
                if C.is_live():
                    cancel_all(book, why)
            else:
                place(book)
        except Exception as e:
            book.log("error", err=f"{type(e).__name__}: {e}"[:300])
        C.beat(book, time.time() - t0,
               # Jan, 25 Nov: Kalshi's balance leaves out money held in waiting bids, so a reading during a round
               # looked like a $20 loss; the dashboard adds `in_bids` back
               balance_fn=lambda: {**balance_log(), "in_bids": book.open_cost()})
        if time.time() - last_up > C.UPLOAD_S:
            last_up = time.time()
            try:
                print(C.upload("kalshi"), flush=True)
            except Exception as e:
                print(f"upload failed: {e}", flush=True)
        time.sleep(LOOP_S)


def check():
    C.load_env()
    C.need("KALSHI_KEY_ID")
    print(f"Key id {os.environ['KALSHI_KEY_ID'][:6]}..., key file {os.environ.get('KALSHI_KEY_FILE', '~/.kalshi.key')}")
    total, b = balances()
    print(f"OK: the key works. Kalshi balance ${total:.2f}, of which ${b:.2f} in the Crypto part (the bot can only use that).")
    if b < 4 <= total:
        print("  !! The money is in the wrong part of the account. Move it to Crypto: kalshi.com/account/exchange-indexes")
    print("Mode:", "LIVE, real bids" if C.is_live() else "dry run (add LIVE=yes to ~/.live.env for real bids)")
    print("Stop check:", C.stop_reason("kalshi", C.Book("kalshi")) or "nothing stops it")
    print(C.phone_check("Kalshi bot"))


def status_text(s):
    d = s["days"].get(C.today(), {"bets": 0, "pnl": 0.0})
    return (f"Since {s['started'][:10]}: {s['bets']} bids, {s['won']} won, {s['lost']} lost, P&L ${s['realized']:+.2f}.\n"
            f"Today: {d['bets']} bids, P&L ${d['pnl']:+.2f}. Waiting now: {len(s['open'])}.")


def status():
    C.load_env()
    s = C.Book("kalshi").state
    print("Kalshi bot. " + status_text(s))
    for d in sorted(s["days"])[-7:]:
        v = s["days"][d]
        print(f"  {d}: {v['bets']} bids, ${v['spent']:.2f} bid, P&L ${v['pnl']:+.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"run": run, "check": check, "status": status}.get(cmd, status)()
