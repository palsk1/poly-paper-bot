#!/usr/bin/env python3
"""REAL-MONEY (once Jan says "live") Polymarket speed bot: the Bitcoin 5-minute speed trick, tiny, on Jan's server.

Jan, 25 Nov 2026 ("Do we testrun the bot on 5 min windows that looked promising with soccer draw money?"), picked
"Build it, practice mode first". The rule is the speed check's own (quoter/speedcheck.py `score` / `edge`, the week
19-24 Nov scored "Looks real": +$2.73 per $100 at 100 ms, about $0 at half a second), unchanged:

  * Binance BTCUSDT trades, thinned like the speed check stores them ($0.50 moves or one a second).
  * Fair price of "Up" in the current 5-minute window: Phi(ln(S/S0) / (sigma * sqrt(seconds left))), S0 = Binance at
    the window's start, sigma from 5-second moves over the 15 minutes before the start.
  * A jump = that fair price moved 3c+ within 2 s. At most one jump per 3 s, none in the last 5 s of a window.
  * Buy the side it jumped toward at the best sell offer we can see right then, only at 40c to under 95c,
    taker fee included, held to the window's result.

Extra care for real money (the speed-firm reading, 25 Nov): the price limit is the offer we SAW, plus PSPEED_EXTRA_C cents
(1c, Jan's pick on 26 Nov; at most 3; Polymarket holds every crypto-window buy 150 ms, so offers move); all or nothing, so a gone offer costs nothing), skip offers of $100+ (those made the least), small fixed bets.

PRACTICE MODE unless ~/.live.env has PSPEED_LIVE=yes (on top of the LIVE=yes the other bots use). In practice mode it
writes down what it would buy at the offer it saw and scores that at the result: a paper twin on this server.

  python3 live/pspeed_live.py check    log in, cash, round trip to Polymarket's order server (no orders)
  python3 live/pspeed_live.py run      the always-on loop (the systemd service pspeed-live runs this)
  python3 live/pspeed_live.py status   what it has done so far, in plain words

Settings in ~/.live.env (live/pspeed_setup.sh writes these; change the numbers there):
  PSPEED_LIVE=yes            real buys (leave it out for practice mode)
  PSPEED_BET=2               dollars a bet (Polymarket's smallest is 5 shares, so at 60c+ a bet costs 5 x the price)
  PSPEED_MAX_BET=5           most one bet may cost
  PSPEED_MAX_OFFER_USD=100   skip when the best offer holds this many dollars or more
  PSPEED_PER_WINDOW=2        most bets bought in one 5-minute window (killed orders don't count, Jan 26 Nov)
  PSPEED_MAX_BETS_DAY=50     most bets a day (UTC)
  PSPEED_DAY_SPEND_MAX=100   most dollars put in a day
  PSPEED_MAX_OPEN_USD=15     most dollars waiting on results at once
  PSPEED_SKIP_FIRST_S=12     no orders in the first 12 s of a window (the offers we see are stale then)
  PSPEED_DAY_LOSS_STOP=5     no new bets for the rest of the day after losing this much
  PSPEED_TOTAL_LOSS_STOP=15  stop for good (writes ~/live-data/STOP-pspeed) after losing this much in total
It uses the Polymarket key already on the server for poly_live.py (same wallet and cash). It never sells.
"""
import asyncio
import bisect
import json
import math
import os
import statistics
import sys
import threading
import time
from decimal import ROUND_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import speedcore as S  # noqa: E402   word-for-word copy of the paper speed check's window lookup, book reader, fair price

BOT = "pspeed"
JUMP = 0.03          # fair price move that counts as a jump
LOOK_MS = 2000       # ... within this long
GAP_MS = 3000        # one jump at a time
MIN_LEFT = 5         # seconds left in the window at least
BAND = (0.40, 0.95)  # buy only at these offers (from 40c to under 95c)
FEE = 0.07           # taker fee rate used for the estimate (Polymarket lists 0.05 for these; 0.07 is the careful one)
WIN = S.WIN
SETTLE_AFTER = 90    # Gamma marks a window's result a minute or two after its end
DEFAULTS = {"PSPEED_BET": 2, "PSPEED_MAX_BET": 5, "PSPEED_MAX_OFFER_USD": 100, "PSPEED_PER_WINDOW": 2,
            "PSPEED_MAX_BETS_DAY": 50, "PSPEED_DAY_SPEND_MAX": 100, "PSPEED_MAX_OPEN_USD": 15,
            "PSPEED_DAY_LOSS_STOP": 5, "PSPEED_TOTAL_LOSS_STOP": 15,
            "PSPEED_EXTRA_C": 1,     # cents the order may pay above the offer seen (Jan picked 1c on 26 Nov; never more than 3)
            "PSPEED_SKIP_FIRST_S": 12}  # no orders in a window's first seconds: the price feed reconnects then (27 Nov)


def cap(k):
    return C.envf(k, DEFAULTS[k])


def is_real():
    """Real buys only with BOTH LIVE=yes (the server's real-money line) and PSPEED_LIVE=yes (this bot's own)."""
    return C.is_live() and os.environ.get("PSPEED_LIVE", "").strip().lower() == "yes"


def practice_unless_own_flag():
    """The notebook (common.Book) and its logs follow LIVE. Without PSPEED_LIVE=yes this process acts as if LIVE
    were off, so practice bets never land on a real-money page and nothing can be sent. Also gives the shared stop
    check (common.stop_reason) this bot's own loss stops when ~/.live.env has none."""
    if not is_real():
        os.environ["LIVE"] = "no"
    for k in ("PSPEED_DAY_LOSS_STOP", "PSPEED_TOTAL_LOSS_STOP"):
        os.environ.setdefault(k, str(DEFAULTS[k]))


class Fair:
    """Binance prices as the speed check keeps them, the window's fair price of Up, and the jump rule."""

    def __init__(self):
        self.t, self.p = [], []
        self.last, self.last_r = None, 0
        self.sig = {}            # window start -> sigma (or None: not enough history)
        self.last_jump = {}      # window start -> time of its last jump (ms)

    def add(self, p, r):
        """True when this price is kept (moved $0.50+ or a second passed), like the speed check's files."""
        if self.last is not None and abs(p - self.last) < S.MOVE and r - self.last_r < 1000:
            return False
        self.last, self.last_r = p, r
        self.t.append(r)
        self.p.append(p)
        if len(self.t) > 20000 and r - self.t[0] > (900 + 2 * WIN + 120) * 1000:
            cut = bisect.bisect_left(self.t, r - (900 + 2 * WIN + 60) * 1000)
            del self.t[:cut], self.p[:cut]
        return True

    def at(self, r):
        i = bisect.bisect_right(self.t, r) - 1
        return self.p[i] if i >= 0 else None

    def sigma(self, w):
        if w not in self.sig:
            hist = [self.at((w - k) * 1000) for k in range(0, 901, 5)]
            rets = [math.log(hist[i] / hist[i + 1]) for i in range(len(hist) - 1) if hist[i] and hist[i + 1]]
            s = statistics.pstdev(rets) / math.sqrt(5) if len(rets) >= 100 else None
            self.sig[w] = s if s and s > 0 else None
            for old in [k for k in self.sig if k < w - 2 * WIN]:
                self.sig.pop(old, None)
                self.last_jump.pop(old, None)
        return self.sig[w]

    def fair_up(self, w, r):
        s0, s, sig = self.at(w * 1000), self.at(r), self.sigma(w)
        left = (w + WIN) - r / 1000
        if not s0 or not s or not sig or left <= 1:
            return None
        return S.norm_cdf(math.log(s / s0) / (sig * math.sqrt(left)))

    def jump(self, r):
        """(window, side, fair price of that side) when the price kept at r is a jump, else None."""
        w = r // 1000 // WIN * WIN
        if r >= (w + WIN - MIN_LEFT) * 1000 or r - self.last_jump.get(w, -10 ** 15) < GAP_MS:
            return None
        if self.at(w * 1000) is None or self.t[0] > (w - 900) * 1000:
            return None              # needs 15 minutes of prices before the window (as the score does)
        f_now, f_then = self.fair_up(w, r), self.fair_up(w, r - LOOK_MS)
        if f_now is None or f_then is None or abs(f_now - f_then) < JUMP:
            return None
        self.last_jump[w] = r
        side = "Up" if f_now > f_then else "Down"
        return w, side, (f_now if side == "Up" else 1 - f_now)


class NoLog:
    def put(self, obj):
        pass


class Speed:
    """The decisions. Feeds call on_price / on_book in the event loop; orders run in a worker thread."""

    def __init__(self, book, send=None, clock=time.time):
        self.book, self.clock = book, clock
        self.send = send             # function(token, amount Decimal, max_price Decimal) -> order result (live only)
        self.fair = Fair()
        self.books = S.Books(NoLog())
        self.win = {}                # window start -> (up token, down token, condition id)
        self.tries = {}              # window start -> bets bought (killed orders don't count, Jan 26 Nov)
        self.why_stopped = "starting"
        self.cash = None
        self.busy = False
        self.lock = threading.RLock()
        self.n = {"jumps": 0, "signals": 0}
        self.pending_windows = []    # (w, up, down, cid) found by the manager, added by the market feed

    def add_window(self, w, up, down, cid):
        if w not in self.win:
            self.win[w] = (up, down, cid)
            self.books.add_window(w, up, down, "btc")

    def drop_old(self, now):
        w0 = int(now) // WIN * WIN
        self.books.drop_before(w0)
        for w in [w for w in self.win if w < w0]:
            self.win.pop(w)
        for w in [w for w in self.tries if w < w0 - WIN]:
            self.tries.pop(w)

    def best_ask(self, tok, other):
        """(price, shares) of the best sell offer on this side. Polymarket mirrors the two sides (an Up buy offer at
        p is a Down sell offer at 1-p), so the mirror is used when this side's own list is empty."""
        lv = self.books.lv.get(tok) or {"a": {}, "b": {}}
        if lv["a"]:
            a = min(lv["a"])
            return a, lv["a"][a]
        ob = (self.books.lv.get(other) or {}).get("b") or {}
        if ob:
            b = max(ob)
            return round(1 - b, 4), ob[b]
        return None, None

    def on_price(self, p, r):
        """A Binance trade (price, our clock in ms). Returns an order plan to send, or None."""
        if not self.fair.add(p, r):
            return None
        j = self.fair.jump(r)
        if not j:
            return None
        self.n["jumps"] += 1
        return self.decide(*j, r)

    def decide(self, w, side, fair, r):
        toks = self.win.get(w)
        if not toks:
            return None
        tok, other = (toks[0], toks[1]) if side == "Up" else (toks[1], toks[0])
        ask, size = self.best_ask(tok, other)
        if ask is None or not (BAND[0] <= ask < BAND[1]):
            return None
        self.n["signals"] += 1
        sig = {"w": w, "side": side, "fair": round(fair, 4), "ask": ask, "offer": round(size or 0, 2),
               "left_s": round(w + WIN - r / 1000, 1), "heard_ms": r}
        amount = Decimal(str(max(cap("PSPEED_BET"), 5 * ask))).quantize(Decimal("0.01"), rounding=ROUND_UP)
        shares = math.floor(float(amount) / ask * 100) / 100
        fee = FEE * shares * ask * (1 - ask)
        cost = round(float(amount) + fee, 4)
        d = self.book.day()
        why = None
        if self.why_stopped:
            why = "paused"
        elif self.busy:
            why = "an order is still on its way"
        elif r / 1000 - w < cap("PSPEED_SKIP_FIRST_S"):
            why = "first seconds of the window (offers not up to date yet)"
        elif ask * (size or 0) >= cap("PSPEED_MAX_OFFER_USD"):
            why = "offer too big (the big ones made the least)"
        elif (size or 0) < shares:
            why = "offer too small for 5 shares"
        elif float(amount) > cap("PSPEED_MAX_BET") + 1e-9:
            why = "bet would cost more than the cap"
        elif self.tries.get(w, 0) >= cap("PSPEED_PER_WINDOW"):
            why = "window cap"
        elif d["bets"] >= cap("PSPEED_MAX_BETS_DAY"):
            why = "day bet cap"
        elif d["spent"] + cost > cap("PSPEED_DAY_SPEND_MAX") + 1e-9:
            why = "day spend cap"
        elif self.book.open_cost() + cost > cap("PSPEED_MAX_OPEN_USD") + 1e-9:
            why = "open money cap"
        elif is_real() and (self.cash is None or self.cash < cost + 0.05):
            why = "not enough cash in the wallet"
        if why:
            if why != "paused":
                self.book.log("signal", **sig, skip=why)
            return None
        self.busy = True
        extra = min(3.0, max(0.0, cap("PSPEED_EXTRA_C"))) / 100
        limit = round(min(0.99, ask + extra), 4)
        return {**sig, "token": tok, "condition_id": toks[2], "amount": amount, "shares": shares,
                "fee_est": round(fee, 4), "cost": cost, "limit": limit}

    def execute(self, plan):
        """Send it (real mode) or write it down (practice). Runs in a worker thread. Never pays more than the seen ask + PSPEED_EXTRA_C cents (1c, Jan's pick)."""
        try:
            rec = {k: v for k, v in plan.items() if k != "amount"}
            rec.update({"placed": C.iso(), "day": C.today(), "amount": float(plan["amount"]),
                        "title": f"Bitcoin 5 min {time.strftime('%H:%M', time.gmtime(plan['w']))} UTC {plan['side']}"})
            if is_real():
                t0 = time.time()
                rec["wait_ms"] = int(t0 * 1000) - plan["heard_ms"]     # heard the jump -> order starts
                try:
                    res = self.send(plan["token"], plan["amount"], Decimal(str(plan.get("limit", plan["ask"]))))
                except Exception as e:
                    rec.update(getattr(self.send, "timing", None) or {})
                    with self.lock:
                        self.book.log("order_failed", **rec, ms=round((time.time() - t0) * 1000),
                                      err=f"{type(e).__name__}: {e}"[:300])
                    return
                ms = round((time.time() - t0) * 1000)
                rec["order_ms"] = ms
                rec.update(getattr(self.send, "timing", None) or {})
                rec["signal_to_answer_ms"] = int(time.time() * 1000) - plan["heard_ms"]
                if not getattr(res, "ok", False):
                    with self.lock:     # all or nothing: the offer was gone, nothing was bought
                        self.book.log("missed", **rec, code=str(getattr(res, "code", "?")),
                                      err=str(getattr(res, "message", ""))[:200])
                    return
                spent, got = float(res.making_amount), float(res.taking_amount)
                if got <= 0:
                    with self.lock:
                        self.book.log("missed", **rec, status=str(getattr(res, "status", "")))
                    return
                rec.update({"order_id": C.scrub(str(res.order_id)), "status": str(res.status), "spent": spent,
                            "shares": got, "paid": round(spent / got, 4), "fee_est": round(FEE * got * (spent / got) * (1 - spent / got), 4)})
                rec["cost"] = round(spent + rec["fee_est"], 4)
                if self.cash is not None:
                    self.cash -= rec["cost"]
            else:
                rec.update({"spent": round(plan["shares"] * plan["ask"], 4), "paid": plan["ask"]})
            with self.lock:
                self.tries[plan["w"]] = self.tries.get(plan["w"], 0) + 1     # only a bought bet uses up the window
                key = f"{plan['w']}-{plan['side']}-{self.tries[plan['w']]}"
                self.book.state["open"][key] = rec
                self.book.state["bets"] += 1
                d = self.book.day()
                d["spent"] = round(d["spent"] + rec["cost"], 4)
                d["bets"] += 1
                self.book.log("buy" if is_real() else "would_buy", key=key, **rec)
                self.book.save()
        finally:
            self.busy = False

    def settle(self, result=None):
        """Book finished windows. result(w) -> True (Up won) / False / None (not known yet)."""
        result = result or (lambda w: S.window_result(w, S.http, "btc"))
        now = self.clock()
        known = {}
        for key, o in list(self.book.state["open"].items()):
            w = o["w"]
            if now < w + WIN + SETTLE_AFTER:
                continue
            if w not in known:
                try:
                    known[w] = result(w)
                except Exception as e:
                    print(f"result lookup failed for {w}: {e}", flush=True)
                    known[w] = None
            up = known[w]
            if up is None:
                continue
            won = up == (o["side"] == "Up")
            pnl = o["shares"] * (1.0 if won else 0.0) - o["spent"] - o.get("fee_est", 0)
            with self.lock:
                self.book.settle(key, pnl, filled=o["shares"], result="won" if won else "lost",
                                 how="real" if o.get("order_id") else "practice")


def status_text(s):
    d = s["days"].get(C.today(), {"bets": 0, "pnl": 0.0, "spent": 0.0})
    return (f"Since {s['started'][:10]}: {s['bets']} bets, {s['won']} won, {s['lost']} lost, P&L ${s['realized']:+.2f}.\n"
            f"Today: {d['bets']} bets, ${d.get('spent', 0):.2f} put in, P&L ${d['pnl']:+.2f}. "
            f"Waiting on results: {len(s['open'])} (${sum(o['cost'] for o in s['open'].values()):.2f}).")


def sender():
    """The real order call: all or nothing, price limit = the offer we saw. With a stopwatch (26 Nov: the first real
    orders took 0.3-1 s, too slow; where does the time go?): sign_ms = building and signing the order on this box,
    post_ms = sending it and Polymarket's answer. Uses the kit's own two steps; falls back to its one-call order."""
    import poly_live as P

    def send(token, amount, max_price):
        cl = P.client()
        t0 = time.time()
        try:
            from polymarket._internal.actions.orders.place import post_order_with_allowance_recovery_sync as post
            prep = cl._prepare_and_sign_market_order
        except (ImportError, AttributeError):
            send.timing = {}
            return cl.place_market_order(token_id=token, side="BUY", amount=amount, max_price=max_price,
                                         order_type="FOK")
        signed = prep(asset_id=None, token_id=token, side="BUY", amount=amount, shares=None, max_spend=None,
                      max_price=max_price, min_price=None, order_type="FOK", builder_code=None)
        t1 = time.time()
        try:
            return post(cl, signed)
        finally:
            send.timing = {"sign_ms": round((t1 - t0) * 1000), "post_ms": round((time.time() - t1) * 1000)}
    send.timing = {}
    return send


LINE_TEST_DEFAULT = "yes"    # Jan OKed the can't-fill test buys on 26 Nov


def keep_line_open(stop_ev, sp=None, every_s=10, test_every_s=900):
    """A tiny public call to Polymarket's order server every 10 s on the same connection the orders use, so an order
    never waits for a new connection. Every 15 min the round trips go into the public log ("line").
    With PSPEED_LINE_TEST=yes (Jan's OK needed) it also sends a test buy every 15 min that cannot be filled: all or
    nothing, $1 at most 1c a share, on a side whose cheapest offer is 10c or more. It is killed after Polymarket's hold,
    so its post_ms shows how long Polymarket takes to answer an order when nobody races us (26 Nov: real orders took
    0.5-1.7 s against a 60 ms check-in)."""
    import poly_live as P
    ms, fails = [], 0
    last_log = last_test = time.time()
    while not stop_ev.is_set():
        t0 = time.time()
        try:
            P.client()._ctx.secure_clob.get_json("/time")
            ms.append(round((time.time() - t0) * 1000))
        except Exception as e:
            fails += 1
            if fails == 1:
                print(f"line ping failed: {type(e).__name__}: {e}"[:200], flush=True)
        if sp is not None and time.time() - last_log > test_every_s and ms:
            ms.sort()
            with sp.lock:
                sp.book.log("line", median_ms=ms[len(ms) // 2], fastest_ms=ms[0], slowest_ms=ms[-1], n=len(ms),
                            failed=fails)
            ms, fails, last_log = [], 0, time.time()
        if (sp is not None and os.environ.get("PSPEED_LINE_TEST", LINE_TEST_DEFAULT).strip().lower() == "yes" and is_real()
                and time.time() - last_test > test_every_s):
            last_test = time.time()
            line_test(sp)
        stop_ev.wait(every_s)


def line_test(sp):
    """One test buy that cannot be filled (see keep_line_open). Skipped while paused or while a real order is out."""
    if sp.why_stopped or sp.busy or sp.send is None:
        return None
    w = int(time.time()) // WIN * WIN
    toks = sp.win.get(w)
    if not toks:
        return None
    pick = None
    for tok, other in ((toks[0], toks[1]), (toks[1], toks[0])):
        ask, _ = sp.best_ask(tok, other)
        if ask is not None and ask >= 0.10:
            pick = tok
            break
    if pick is None:
        return None
    sp.busy = True
    rec = {"w": w, "side": "Up" if pick == toks[0] else "Down", "limit": 0.01, "amount": 1.0}
    t0 = time.time()
    try:
        res = sp.send(pick, Decimal("1.00"), Decimal("0.01"))
        rec.update(getattr(sp.send, "timing", None) or {}, ms=round((time.time() - t0) * 1000),
                   bought=float(getattr(res, "taking_amount", 0) or 0) if getattr(res, "ok", False) else 0.0)
    except Exception as e:
        rec.update(getattr(sp.send, "timing", None) or {}, ms=round((time.time() - t0) * 1000),
                   answer=f"{type(e).__name__}: {e}"[:160])
    finally:
        sp.busy = False
    with sp.lock:
        sp.book.log("line_test", **rec)
    return rec


def warm(token):
    """Fetch a market's order settings (tick size etc.) before a jump comes, so the order call has less to do.
    Uses the kit's own cache; a failure only means the first order is a little slower."""
    try:
        import poly_live as P
        ctx = P.client()._ctx
        ctx.order_metadata.resolve_market(ctx, token_id=token)
    except Exception as e:
        print(f"warm-up skipped: {type(e).__name__}: {e}"[:200], flush=True)


# ---------------------------------------------------------------- the always-on loop
def manager(sp, stop_ev):
    """Every few seconds: windows, results, claims, phone, off switches, cash, sign of life, uploads.
    Slow network calls live here, never in the price feeds."""
    import poly_live as P
    last = {"win": 0, "settle": 0, "claim": 0, "cash": 0, "up": 0}
    was = "starting"
    while not stop_ev.is_set():
        t0 = time.time()
        now = time.time()
        if now - last["win"] > 20:
            last["win"] = now
            w0 = int(now) // WIN * WIN
            for w in (w0, w0 + WIN):
                if w in sp.win or any(x[0] == w for x in sp.pending_windows):
                    continue
                try:
                    got = S.window_tokens(w, S.http, "btc")
                except Exception as e:   # one failed lookup must not skip the phone and the off switches
                    print(f"window lookup failed: {type(e).__name__}: {e}"[:200], flush=True)
                    continue
                if got:
                    sp.pending_windows.append((w, *got))
                    if is_real():
                        warm(got[0])
                        warm(got[1])
        try:
            if now - last["settle"] > 30:
                last["settle"] = now
                sp.settle()
            if is_real() and os.environ.get("POLY_RELAYER_KEY") and now - last["claim"] > 600:
                last["claim"] = now
                P.claim_all(sp.book)       # only writes log lines, so no lock: orders keep flowing meanwhile
            if is_real() and now - last["cash"] > 60:
                last["cash"] = now
                try:
                    sp.cash = P.cash()
                except Exception as e:
                    print(f"cash read failed: {e}", flush=True)
            with sp.lock:
                C.control(BOT, sp.book, lambda: status_text(sp.book.state))
                why = C.stop_reason(BOT, sp.book)
            if why != was:
                sp.book.log("paused" if why else "running", why=why or "")
                was = why
            sp.why_stopped = why
        except Exception as e:
            sp.book.log("error", err=f"{type(e).__name__}: {e}"[:300])
        with sp.lock:
            C.beat(sp.book, time.time() - t0, balance_fn=(P.cash if is_real() else None))
            if sp.n["jumps"] and time.time() - last.get("count", 0) > 3600:
                last["count"] = time.time()
                sp.book.log("hour", **sp.n)
                sp.n = {"jumps": 0, "signals": 0}
        if time.time() - last["up"] > C.UPLOAD_S:
            last["up"] = time.time()
            try:
                print(C.upload(BOT), flush=True)
            except Exception as e:
                print(f"upload failed: {e}", flush=True)
        stop_ev.wait(2)


async def binance(sp, loop, ws_lib):
    backoff = 2
    while True:
        try:
            async with ws_lib.connect(S.BN_WS, ping_interval=20, max_size=2 ** 22) as ws:
                backoff = 2
                async for raw in ws:
                    r = S.now_ms()
                    for p, _e in S.parse_bn(raw):
                        plan = sp.on_price(p, r)
                        if plan:
                            loop.run_in_executor(None, sp.execute, plan)
        except Exception as ex:  # noqa: BLE001
            print(f"binance disconnected: {type(ex).__name__}: {ex}"[:200], flush=True)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def market(sp, ws_lib):
    """Polymarket's public market feed for the current and next window; reconnects when the windows change."""
    while True:
        while sp.pending_windows:
            sp.add_window(*sp.pending_windows.pop(0))
        sp.drop_old(time.time())
        subs = sorted({t for v in sp.win.values() for t in v[:2]})
        if not subs:
            await asyncio.sleep(2)
            continue
        try:
            async with ws_lib.connect(S.PM_WS, ping_interval=None, max_size=2 ** 23) as ws:
                await ws.send(json.dumps({"assets_ids": subs, "type": "market"}))
                last_ping = time.time()
                w_now = int(time.time()) // WIN * WIN
                while True:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    except asyncio.TimeoutError:
                        raw = None
                    if raw and raw != "PONG":
                        sp.books.handle(raw)
                    if time.time() - last_ping > 9:
                        await ws.send("PING")
                        last_ping = time.time()
                    if sp.pending_windows or int(time.time()) // WIN * WIN != w_now:
                        break            # a new window is listed or one ended: resubscribe
        except Exception as ex:  # noqa: BLE001
            print(f"market feed disconnected: {type(ex).__name__}: {ex}"[:200], flush=True)
            await asyncio.sleep(2)


def run():
    C.load_env()
    practice_unless_own_flag()
    import websockets
    book = C.Book(BOT)
    sp = Speed(book, send=sender() if is_real() else None)
    book.log("start", rule="speed check: buy the side Binance jumped toward (3c+ in 2 s), 40-95c, at the offer seen",
             mode="LIVE (real money)" if is_real() else "practice (buys nothing)",
             max_bet=cap("PSPEED_BET"), max_open_usd=cap("PSPEED_MAX_OPEN_USD"),
             caps={k: cap(k) for k in DEFAULTS})
    if is_real():
        import poly_live as P
        cl = P.client()
        sp.cash = P.cash()
        book.log("login", wallet_type=str(cl.wallet_type), cash=round(sp.cash, 2))
    stop_ev = threading.Event()
    threading.Thread(target=manager, args=(sp, stop_ev), daemon=True).start()
    if is_real():
        threading.Thread(target=keep_line_open, args=(stop_ev, sp), daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        await asyncio.gather(binance(sp, loop, websockets), market(sp, websockets))
    try:
        loop.run_until_complete(main())
    finally:
        stop_ev.set()


def check():
    C.load_env()
    practice_unless_own_flag()
    print("Mode:", "LIVE, real buys" if is_real() else
          "PRACTICE (buys nothing). Real buys need PSPEED_LIVE=yes in ~/.live.env, and LIVE=yes.")
    print("Caps:", ", ".join(f"{k[7:].lower()}={cap(k):g}" for k in DEFAULTS))
    ms = []
    for _ in range(5):
        t0 = time.time()
        try:
            S.http("GET", f"{S.CLOB}/time")
            ms.append(round((time.time() - t0) * 1000))
        except Exception as e:
            print(f"Polymarket order server not reached: {e}")
            break
    if ms:
        print(f"Round trip to Polymarket's order server: {sorted(ms)[len(ms) // 2]} ms (5 tries: {ms}). "
              "The edge was gone at about 500 ms in the paper test.")
    w = int(time.time()) // WIN * WIN
    got = S.window_tokens(w, S.http, "btc")
    print("This 5-minute window on Polymarket:", "found" if got else "NOT found (Gamma)")
    if os.environ.get("POLY_PRIVATE_KEY"):
        import poly_live as P
        cl = P.client()
        print(f"Polymarket login OK ({cl.wallet_type}). Cash ${P.cash():.2f} (shared with the soccer-draw bot).")
    else:
        print("No Polymarket key on this server (POLY_PRIVATE_KEY): practice mode only.")
    print("Stop check:", C.stop_reason(BOT, C.Book(BOT)) or "nothing stops it")


def status():
    C.load_env()
    practice_unless_own_flag()
    s = C.Book(BOT).state
    print(("Speed bot (real money). " if is_real() else "Speed bot (practice). ") + status_text(s))
    for d in sorted(s["days"])[-7:]:
        v = s["days"][d]
        print(f"  {d}: {v['bets']} bets, ${v['spent']:.2f} put in, P&L ${v['pnl']:+.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"run": run, "check": check, "status": status}.get(cmd, status)()
