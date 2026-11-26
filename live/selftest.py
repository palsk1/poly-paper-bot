"""Offline test of the two real-money bots: fake Kalshi / Polymarket / Binance answers, no network, no keys,
no orders. Runs in a temp folder. setup.sh and update.sh run it; it must print ALL OK.

    python3 live/selftest.py
"""
import datetime as dt
import os
import sys
import tempfile
import time
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp()
# Start clean: the server's own settings (POLY_TAKE=all, caps, LIVE=yes, ...) can sit in the environment when the
# auto-update runs this test, and they changed what the checks saw (23 Nov: "takes every second signal" failed).
for _k in list(os.environ):
    if _k.startswith(("KALSHI_", "POLY_", "PSPEED_", "NTFY_", "LIVE")):
        os.environ.pop(_k)
os.environ["LIVE_DIR"] = TMP
os.environ["LIVE_ENV"] = os.path.join(TMP, "none.env")
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import bot  # noqa: E402
import common as C  # noqa: E402
import kalshi_live as K  # noqa: E402
import poly_live as P  # noqa: E402
import pspeed_live as SP  # noqa: E402

C._switch.update(t=1e18, val={"kalshi": "on", "poly": "on", "pspeed": "on"}, fails=0)   # no GitHub read in the test
OK = []


def check(cond, what):
    if not cond:
        raise SystemExit(f"FAILED: {what}")
    OK.append(what)


def at(minute, second=0):
    """Pretend the clock reads 12:<minute>:<second> UTC today."""
    base = dt.datetime.now(dt.timezone.utc).replace(hour=12, minute=minute, second=second, microsecond=0)
    C.utcnow = lambda: base
    bot.now = lambda: base
    return base


# ---------------------------------------------------------------- Kalshi signing
def test_sign():
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
    for k in (rsa.generate_private_key(public_exponent=65537, key_size=2048), ed25519.Ed25519PrivateKey.generate()):
        K._key = k
        sig = __import__("base64").b64decode(K.sign("123GET/trade-api/v2/portfolio/balance"))
        if isinstance(k, rsa.RSAPrivateKey):
            k.public_key().verify(sig, b"123GET/trade-api/v2/portfolio/balance",
                                  padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
                                  hashes.SHA256())
        else:
            k.public_key().verify(sig, b"123GET/trade-api/v2/portfolio/balance")
    check(True, "Kalshi request signing (RSA-PSS and Ed25519) verifies")


# ---------------------------------------------------------------- Kalshi place + settle
BREAK = [[{"exchange_index": 0, "balance": "0.0000"}, {"exchange_index": 2, "balance": "30.0000"}]]


def kalshi_fakes(t_close):
    def http_json(url, params=None, retries=3):
        if "/klines" in url:      # Binance: price far above the strike, small moves -> big z
            t0 = int((t_close - dt.timedelta(minutes=70)).timestamp()) // 60 * 60
            op = int((t_close - dt.timedelta(minutes=15)).timestamp())
            return [[(t0 + 60 * i) * 1000, 0, 0, 0, str((101000 if t0 + 60 * i >= op else 100500) + (i % 2))]
                    for i in range(62)]
        if url.endswith("/markets") and params and params.get("series_ticker"):
            if params["series_ticker"] != "KXBTC15M":
                return {"markets": []}
            return {"markets": [{"ticker": "KXBTC15M-T1", "close_time": C.iso(t_close), "floor_strike": 100000,
                                 "title": "BTC up?", "event_ticker": "KXBTC15M-E1"}]}
        if url.endswith("/orderbook"):
            return {"orderbook_fp": {"yes_dollars": [["0.9700", "50"]], "no_dollars": [["0.0100", "40"]]}}
        if "/markets/KXBTC15M-T1" in url:
            return {"market": {"ticker": "KXBTC15M-T1", "result": "yes"}}
        if url.endswith("/markets/trades"):
            return {"trades": [{"created_time": C.iso(t_close - dt.timedelta(seconds=30)), "yes_price_dollars": "0.9600",
                                "taker_side": "no", "count_fp": "10"}], "cursor": ""}
        raise AssertionError(f"unexpected url {url}")
    bot.http_json = http_json


def test_kalshi():
    t = at(11, 0)                                        # 4 minutes before the 12:15 close
    close = t.replace(minute=15)
    kalshi_fakes(close)
    book = C.Book("kalshi")
    K.place(book)
    check("KXBTC15M-T1" in book.state["open"] and "order_id" not in book.state["open"]["KXBTC15M-T1"],
          "Kalshi dry run writes down a would-be bid and sends nothing")
    o = book.state["open"]["KXBTC15M-T1"]
    check(abs(o["price"] - 0.971) < 1e-9 and o["shares"] == 4 and o["cost"] <= 4,
          "Kalshi bid is one 0.1c tick above the 97c best bid, 4 contracts for $4")
    check(o["spot_z_usd"] >= 2.3, "Kalshi real bot bids only with a 2.3+ cushion after the Binance-vs-Kalshi gap (Jan, 23 Nov)")
    os.environ["KALSHI_MIN_Z_USD"] = "999"
    b_hi = C.Book("kalshi_hi")
    K.place(b_hi)
    check(not b_hi.state["open"], "a coin below the real bot's cushion bar gets no bid")
    del os.environ["KALSHI_MIN_Z_USD"]
    K.place(book)
    check(len(book.state["open"]) == 1, "Kalshi places one bid per window, not one per loop")
    at(16, 30)
    K.settle(book)
    check(not book.state["open"] and abs(book.state["realized"] - 4 * (1 - 0.971)) < 1e-6,
          "Kalshi dry run settles with the paper fill rule on the trade tape (win = +$0.116)")

    # live: the order body, caps and the real fill read
    os.environ["LIVE"] = "yes"
    sent = []

    def kreq(method, path, body=None, params=None):
        sent.append((method, path, body))
        if path == "/portfolio/balance":
            return 200, {"balance": 3000, "balance_dollars": "30.00", "balance_breakdown": BREAK[0]}
        if method == "POST" and path == "/portfolio/orders":      # the old address: switched off by Kalshi
            return 410, {"error": {"code": "deprecated_v1_order_endpoint"}}
        if method == "POST":
            return 201, {"order_id": "abc", "fill_count": "0.00", "remaining_count": "4.00", "ts_ms": 1}
        if path == "/portfolio/orders/abc":
            return 200, {"order": {"fill_count_fp": "4.00", "maker_fill_cost_dollars": "3.884",
                                   "taker_fill_cost_dollars": "0", "maker_fees_dollars": "0", "taker_fees_dollars": "0"}}
        return 200, {}
    K.kreq = kreq
    book = C.Book("kalshi2")
    t = at(41, 0)
    close = t.replace(minute=45)
    kalshi_fakes(close)
    K.place(book)
    post = [b for m, p, b in sent if m == "POST"]
    check(len(post) == 1 and [p for m, p, b in sent if m == "POST"] == ["/portfolio/events/orders"]
          and post[0]["post_only"] and post[0]["side"] == "bid" and post[0]["price"] == "0.9710"
          and post[0]["count"] == "4.00" and post[0]["expiration_time"] == int(close.timestamp())
          and post[0]["time_in_force"] == "good_till_canceled" and post[0]["cancel_order_on_pause"]
          and "abc" == book.state["open"]["KXBTC15M-T1"]["order_id"],
          "Kalshi live bid uses the new order form: post-only, dies at the close, cancels on pause")
    nb = K.order_body("T", "no", 0.994, 4, close)
    check(nb["side"] == "ask" and nb["price"] == "0.0060", "a No bid at 99.4c goes in as 'sell Yes at 0.6c' (same thing)")
    at(46, 30)
    bot._kalshi_cache.clear()
    bot.http_json = (lambda f: lambda url, params=None, retries=3: (
        {"market": {"result": "no"}} if "/markets/KXBTC15M-T1" in url else f(url, params)))(bot.http_json)
    K.settle(book)
    check(abs(book.state["realized"] + 3.884) < 1e-6 and book.state["lost"] == 1,
          "Kalshi live loss is booked from the real order (4 filled, -$3.88)")

    # Kalshi pays a bot's bid only from the Crypto part of the account: money parked elsewhere = no bid sent
    BREAK[0] = [{"exchange_index": 0, "balance": "30.0000"}, {"exchange_index": 2, "balance": "0.0000"}]
    bookw = C.Book("kalshi-wrong")
    at(26, 0)
    kalshi_fakes(at(26, 0).replace(minute=30))
    n_post = len([1 for m, p, b in sent if m == "POST"])
    K.place(bookw)
    check(K.balances() == (30.0, 0.0) and not bookw.state["open"]
          and len([1 for m, p, b in sent if m == "POST"]) == n_post,
          "money in the wrong part of the Kalshi account: no bid is sent (and the phone hears why)")
    BREAK[0] = [{"exchange_index": 0, "balance": "0.0000"}, {"exchange_index": 2, "balance": "30.0000"}]

    # caps: open-money cap and the total-loss stop
    os.environ["KALSHI_MAX_OPEN_USD"] = "3"
    book3 = C.Book("kalshi3")
    at(11, 0)
    kalshi_fakes(at(11, 0).replace(minute=15))
    K.place(book3)
    check(not book3.state["open"], "Kalshi refuses a bid above the money-out-at-once cap")
    del os.environ["KALSHI_MAX_OPEN_USD"]
    book3.state["realized"] = -20.5
    why = C.stop_reason("kalshi", book3)
    check(why and os.path.exists(os.path.join(TMP, "STOP-kalshi")), "Kalshi total-loss cap writes a STOP file")
    check(C.stop_reason("kalshi", C.Book("kalshi4")) is not None, "the STOP file keeps it stopped")
    os.remove(os.path.join(TMP, "STOP-kalshi"))
    C._switch["val"] = {"kalshi": "off", "poly": "on"}
    check("switch" in (C.stop_reason("kalshi", C.Book("kalshi4")) or ""), "the repo switch can turn Kalshi off")
    C._switch["val"] = {"kalshi": "on", "poly": "on"}
    os.environ.pop("LIVE")


# ---------------------------------------------------------------- Polymarket place + settle
def test_poly():
    at(10, 0)
    cand = {"slug": "", "token": "tok", "price": 0.17, "title": "Will A vs B end in a draw?", "event_key": "ev1",
            "fee_rate": 0.05, "end": "2026-11-23", "signal": "draw listed 17c", "market": {"conditionId": "0xc"}}
    slugs = [f"game-{i}-draw" for i in range(12)]
    half = [s for s in slugs if P.take(s)]
    check(2 <= len(half) <= 10, "Polymarket takes about every second signal, picked by name")
    bot.draw_candidates = lambda names: {"soccer_draw": [{**cand, "slug": s, "event_key": s} for s in slugs]}
    bot.book = lambda tok: {"asks": [(0.18, 3), (0.19, 100)], "bids": [(0.16, 10)], "min_size": 5}
    book = C.Book("poly")
    P.place(book)
    o = book.state["open"].get(half[0])
    check(o and o["shares"] * o["ask"] >= 1.0 and o["shares"] >= 5,
          "Polymarket buys the smallest allowed order (5+ shares and $1+): "
          + (f"{o['shares']} shares at {o['ask'] * 100:.1f}c" if o else "none"))
    check(len(book.state["open"]) == len(half) and not any(s in book.state["open"] for s in slugs if not P.take(s)),
          "Polymarket skips the other half")
    os.environ["POLY_TAKE"] = "all"
    check(all(P.take(s) for s in slugs), "with POLY_TAKE=all every signal is taken, like the paper track")
    os.environ.pop("POLY_TAKE")

    bot.book = lambda tok: {"asks": [(0.22, 100)], "bids": [], "min_size": 5}
    b2 = C.Book("poly2")
    P.place(b2)
    check(not b2.state["open"], "Polymarket skips when the real ask is 3c+ above the listed price")

    os.environ["LIVE"] = "yes"
    calls = []

    class Fake:
        wallet, wallet_type = "0xw", "POLY_PROXY"

        def get_balance_allowance(self, asset_type):
            return SimpleNamespace(balance=28_000_000)

        def place_market_order(self, **kw):
            calls.append(kw)
            return SimpleNamespace(ok=True, order_id="o1", status="matched", making_amount=kw["amount"],
                                   taking_amount=__import__("decimal").Decimal("6"))

        def list_positions(self, status):
            rows = [SimpleNamespace(condition_id="0xc", current_value=6, title="A vs B draw"),
                    SimpleNamespace(condition_id="0xold", current_value=3, title="an old win"),
                    SimpleNamespace(condition_id="0xlost", current_value=0, title="an old lost bet, pays $0")]
            # like the real kit: walking the answer gives pages, the rows come from iter_items()
            return SimpleNamespace(iter_items=lambda: iter(rows), __iter__=lambda: iter([rows]))

        def redeem_positions(self, condition_id):
            calls.append({"redeem": condition_id})
            return SimpleNamespace(wait=lambda: "done")
    P._client = Fake()
    bot.book = lambda tok: {"asks": [(0.18, 3), (0.19, 100)], "bids": [], "min_size": 5}
    os.environ["POLY_MAX_OPEN"] = "3"
    b3 = C.Book("poly3")
    P.place(b3)
    buys = [c for c in calls if "token_id" in c]
    check(len(buys) == 3 and all(c["order_type"] == "FOK" and float(c["max_price"]) == 0.2 for c in buys),
          "Polymarket live buys are all-or-nothing, never above listed + 3c, and stop at the open-bets cap")
    del os.environ["POLY_MAX_OPEN"]
    key = next(iter(b3.state["open"]))
    # Like Gamma: the list address /markets?slug= leaves closed markets out; /markets/slug/<slug> has them.
    bot.http_json = lambda url, params=None, retries=3: (
        {"closed": True, "outcomePrices": '["1", "0"]'} if "/markets/slug/" in url else [])
    os.environ["POLY_RELAYER_KEY"] = "k"
    P.settle(b3)
    red = [c["redeem"] for c in calls if "redeem" in c]
    check(b3.state["won"] == 3 and b3.state["realized"] > 0 and red == ["0xc", "0xold"],
          "Polymarket settles won draws (read from the one-market address, which keeps closed games), then claims every claimable win (old ones too), once each, and skips lost bets worth $0")
    del os.environ["POLY_RELAYER_KEY"]
    check(key in b3.state["done"], "a settled market is never bought again")
    # Polymarket's coming "fair value" payout (canceled / abandoned / very late games): a split final price
    b4 = C.Book("poly4")
    b4.state["open"] = {"a-draw": {"shares": 10, "ask": 0.30, "spent": 3.0}, "b-draw": {"shares": 10, "ask": 0.30, "spent": 3.0}}
    bot.http_json = lambda url, params=None, retries=3: (
        {"closed": True, "outcomePrices": '["0.31", "0.69"]', "umaResolutionStatus": "resolved"}
        if url.endswith("/markets/slug/a-draw") else {"closed": True, "outcomePrices": '["0.31", "0.69"]'})
    P.settle(b4)
    check("a-draw" not in b4.state["open"] and abs(b4.state["realized"] - 0.10) < 1e-6 and "b-draw" in b4.state["open"],
          "a split ('fair value') result pays its final price; a closed game without a final result waits")
    os.environ.pop("LIVE")


def test_privacy():
    b = C.Book("privacy")
    addr, tx = "0x5c5d46356267CA22F90FA2d4A3B6EC4880B68E0f", "0x" + "ab12" * 16
    b.log("claimed", condition_id=tx, result=f"sent {tx} from {addr}", wallet=addr, nested={"maker": addr})
    line = open(os.path.join(TMP, "privacy-" + C.utcnow().strftime("%Y%m") + ".jsonl")).read()
    check(addr not in line and addr.lower() not in line.lower().replace(tx, "") and line.count(tx) == 1,
          "the public notebook never holds a wallet address or payment number (market ids stay)")
    oid = "01a209fb-3db0-7dd9-8574-0bf774a96a6b"
    b.log("placed", order_id=oid, ticker="KXBTC15M-T1")
    b.state["open"]["KXBTC15M-T1"] = {"order_id": oid}
    b.save()
    import gzip as _gz
    pub = ""
    for fn in ("privacy-" + C.utcnow().strftime("%Y%m") + ".jsonl", "privacy-state.json"):
        C.public_copy(os.path.join(TMP, fn), os.path.join(TMP, fn + ".gz"))
        pub += _gz.open(os.path.join(TMP, fn + ".gz"), "rt").read()
    check(oid not in pub and "..6a6b" in pub and C.Book("privacy").state["open"]["KXBTC15M-T1"]["order_id"] == oid,
          "order numbers reach the public copy as their last 4 only; the server keeps the full one to cancel")


def test_mode_switch():
    os.environ.pop("LIVE", None)
    b = C.Book("switch")
    b.state["open"]["x"] = {"cost": 3.0}
    b.state["bets"] = 7
    b.save()
    check(C.Book("switch").state["bets"] == 7, "a restart in the same mode keeps the notebook")
    os.environ["LIVE"] = "yes"
    b2 = C.Book("switch")
    kept = [f for f in os.listdir(TMP) if f.startswith("switch-pretend-until-")]
    check(b2.state["bets"] == 0 and not b2.state["open"] and len(kept) == 1,
          "switching to real money starts a clean notebook: pretend bets don't count as real or use up the caps")
    os.environ.pop("LIVE")


def test_phone():
    import json as J
    os.environ["NTFY_CONTROL"] = "bots-test"
    inbox, sent = [], []
    C.ntfy_get = lambda url: "\n".join(J.dumps(m) for m in inbox)
    C.ntfy_post = lambda topic, title, body: sent.append((topic, title, body))
    book = C.Book("kalshi-phone")
    status = lambda: "3 bids"

    def say(text, title=None):
        inbox.clear()
        inbox.append({"event": "message", "id": f"m{len(sent)}", "message": text, **({"title": title} if title else {}),
                      **({"tags": ["moneybag"]} if title in C.BOT_TITLES else {})})
        C._ctrl["t"] = 0
        C.control("kalshi", book, status)
    urls = []
    C.ntfy_get = lambda url: urls.append(url) or ""
    C._ctrl["t"] = 0
    C.control("kalshi", book, status)
    check(urls and urls[-1].split("since=")[1].isdigit(),
          "the first phone read asks for everything since the bot started, not just the last minute")
    C.ntfy_get = lambda url: "\n".join(J.dumps(m) for m in inbox)
    say("stop poly")
    check(C.stop_reason("kalshi", book) is None, "phone 'stop poly' leaves the Kalshi bot running")
    say("Stop")
    check("phone" in (C.stop_reason("kalshi", book) or "") and sent[-1][1] == "Kalshi bot",
          "phone 'stop' stops the bot and it answers in the channel")
    say("start", title="Kalshi bot")
    check(C.stop_reason("kalshi", book) is not None, "the bots' own messages are never read as commands")
    n = len(sent)
    say("triggered", title="Status")
    check(len(sent) == n + 1 and "3 bids" in sent[-1][2], "a command typed in the Title box (message empty) works too")
    say("hello there")
    check(len(sent) == n + 1, "other chatter in the channel is ignored")
    say("status")
    check("3 bids" in sent[-1][2] and "Paused" in sent[-1][2], "phone 'status' answers with numbers and why it's paused")
    say("start kalshi")
    check(C.stop_reason("kalshi", book) is None, "phone 'start' turns it back on")
    with open(os.path.join(TMP, "STOP-kalshi"), "w") as f:
        f.write("total loss cap")
    say("start")
    check(C.stop_reason("kalshi", book) is not None and "still paused" in sent[-1][2],
          "phone 'start' can't undo a loss-cap stop")
    os.remove(os.path.join(TMP, "STOP-kalshi"))
    say("status")
    check("Auto-updates on" in sent[-1][2],
          "phone 'status' also says when the code was updated and if auto-updates are on")
    say("update")
    check(os.path.exists(os.path.join(TMP, "UPDATE-NOW")) and sent[-1][1] == "Server update",
          "phone 'update' asks the server to update now and says so")
    n = len(sent)
    C._ctrl["t"] = 0
    C.control("poly", C.Book("poly-phone"), status)          # the other bot reads the same message
    check(len(sent) == n, "both bots hear 'update', but only one answers")
    say("updates off")
    check(os.path.exists(os.path.join(TMP, "NO-AUTO-UPDATE")) and "OFF" in sent[-1][2], "phone 'updates off' works")
    say("updates on")
    check(not os.path.exists(os.path.join(TMP, "NO-AUTO-UPDATE")), "phone 'updates on' works")
    say("help")
    check("updates off" in sent[-1][2] and C.stop_reason("kalshi", book) is None,
          "phone 'help' lists the words, and none of these server words stops a bot")
    os.remove(os.path.join(TMP, "UPDATE-NOW"))
    del os.environ["NTFY_CONTROL"]


def test_balance():
    import json as _j
    b = C.Book("balance")
    C._beat["t"] = 0

    def boom():
        raise RuntimeError("site down")
    C.beat(b, 0.1, balance_fn=lambda: {"balance": 30.004, "balance_crypto": 29.5})
    C._beat["t"] = 0
    C.beat(b, 0.1, balance_fn=boom)
    rows = [_j.loads(x) for x in open(os.path.join(C.DIR, f"balance-{C.utcnow().strftime('%Y%m')}.jsonl")) if x.strip()]
    al = [r for r in rows if r["k"] == "alive"]
    check(len(al) == 2 and al[0]["balance"] == 30.0 and al[0]["balance_crypto"] == 29.5 and "balance" not in al[1],
          "the alive line carries the real balance, and a failed balance read never stops the bot")


# ---------------------------------------------------------------- the speed bot (Bitcoin 5-minute windows)
def test_pspeed():
    from decimal import Decimal
    import random
    for k in ("LIVE", "PSPEED_LIVE"):
        os.environ.pop(k, None)
    os.environ["LIVE"] = "yes"
    SP.practice_unless_own_flag()
    check(not SP.is_real() and not C.is_live(),
          "the speed bot stays in practice mode on a server with LIVE=yes until it has its own PSPEED_LIVE=yes")
    sent = []
    w = 1_800_000_000 // 300 * 300
    clock = {"t": w + 60.0}
    b = C.Book("pspeed_t")
    sp = SP.Speed(b, send=lambda tok, amt, mx: sent.append((tok, amt, mx)) or SimpleNamespace(ok=True),
                  clock=lambda: clock["t"])
    sp.why_stopped = None
    sp.add_window(w, "UP", "DOWN", "0xc")
    rnd = random.Random(1)
    p = 90_000.0
    plans = []
    for sec in range(-1000, 60):          # 15+ minutes of $3 moves every 5 s before the window, then calm
        if sec < 0 and sec % 5 == 0:
            p += rnd.choice((-3, 3))
        plans.append(sp.on_price(p, (w + sec) * 1000))
    check(not any(plans) and sp.fair.sigma(w), "a calm Bitcoin price gives no jump")
    sp.books.lv["UP"] = {"a": {0.55: 20.0}, "b": {0.53: 50.0}}
    sp.books.lv["DOWN"] = {"a": {0.47: 50.0}, "b": {0.45: 20.0}}
    plan = sp.on_price(p + 150, (w + 60) * 1000 + 400)
    check(plan and plan["side"] == "Up" and plan["ask"] == 0.55 and plan["token"] == "UP"
          and plan["amount"] == Decimal("2.75") and plan["shares"] >= 5,
          "a $150 Bitcoin jump within 2 s buys Up at the offer seen, 5 shares (=$2.75 at 55c)")
    check(sp.on_price(p + 300, (w + 61) * 1000) is None, "one jump at a time: nothing again within 3 s")
    sp.execute(plan)
    check(not sent and len(b.state["open"]) == 1 and next(iter(b.state["open"].values()))["paid"] == 0.55,
          "practice mode sends nothing and writes the bet down at the offer it saw")
    # settle: Up won
    clock["t"] = w + 300 + 91
    sp.settle(result=lambda ww: True)
    o_pnl = b.state["realized"]
    check(not b.state["open"] and b.state["won"] == 1 and abs(o_pnl - (5 - 2.75 - 0.07 * 5 * 0.55 * 0.45)) < 0.01,
          "a won window pays $1 a share, less the cost and the fee estimate")
    clock["t"] = w + 60.0
    # caps and skips
    sp.busy = False
    plan2 = sp.decide(w, "Up", 0.7, (w + 70) * 1000)
    check(plan2 is not None, "a second buy in the same window is allowed")
    sp.busy = False
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "at most 2 buys tried in one 5-minute window")
    sp.tries.clear()
    sp.busy = True
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "no second order while one is still on its way")
    sp.busy = False
    sp.books.lv["UP"]["a"] = {0.55: 200.0}
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "skips offers of $100 or more (those made the least)")
    sp.books.lv["UP"]["a"] = {0.96: 20.0}
    check(sp.decide(w, "Up", 0.99, (w + 80) * 1000) is None, "never buys at 95c or more")
    sp.books.lv["UP"]["a"] = {0.39: 20.0}
    check(sp.decide(w, "Up", 0.5, (w + 80) * 1000) is None, "never buys under 40c")
    sp.books.lv["UP"]["a"] = {0.55: 3.0}
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "skips an offer too small for Polymarket's 5 shares")
    sp.books.lv["UP"]["a"] = {0.55: 20.0}
    b.state["open"] = {"x": {"cost": 14.0, "w": w, "side": "Up", "shares": 1, "spent": 14}}
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "stops at $15 waiting on results")
    b.state["open"] = {}
    b.day()["spent"] = 99.0
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "stops at $100 put in a day")
    b.day()["spent"] = 0.0
    b.day()["bets"] = 50
    check(sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "stops at 50 bets a day")
    b.day()["bets"] = 0
    # the shared off switches
    sp.tries.clear()
    open(os.path.join(TMP, "STOP-pspeed"), "w").write("test\n")
    sp.why_stopped = C.stop_reason("pspeed", b)
    check(sp.why_stopped and sp.decide(w, "Up", 0.7, (w + 80) * 1000) is None, "a STOP-pspeed file pauses new buys")
    os.remove(os.path.join(TMP, "STOP-pspeed"))
    C._switch["val"] = {"kalshi": "on", "poly": "on", "pspeed": "off"}
    check("switch" in (C.stop_reason("pspeed", b) or ""), "live/switch.json can turn the speed bot off")
    C._switch["val"] = {"kalshi": "on", "poly": "on", "pspeed": "on"}
    b.day()["pnl"] = -5.0
    check("today" in (C.stop_reason("pspeed", b) or ""), "the speed bot pauses for the day after losing $5")
    b.day()["pnl"] = 0.0
    b.state["realized"] = -15.0
    check("total loss" in (C.stop_reason("pspeed", b) or ""), "the speed bot stops for good after losing $15")
    os.remove(os.path.join(TMP, "STOP-pspeed"))
    b.state["realized"] = 0.0
    check(C.stop_reason("pspeed", b) is None, "nothing else stops it")
    sc = os.path.join(os.path.dirname(HERE), "quoter", "speedcheck.py")
    if os.path.exists(sc):          # in the repo; the server's side-folder test only has live/
        import ast
        import speedcore
        want = {n.name: ast.get_source_segment(open(sc).read(), n) for n in ast.parse(open(sc).read()).body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        mine = {n.name: ast.get_source_segment(open(speedcore.__file__).read(), n)
                for n in ast.parse(open(speedcore.__file__).read()).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        src = open(sc).read()
        same_consts = all(f'{k} = {getattr(speedcore, k)!r}'.replace("'", '"') in src or f"{k} = {getattr(speedcore, k)}" in src
                          for k in ("GAMMA", "CLOB", "PM_WS", "BN_WS", "MOVE", "WIN"))
        check(all(mine.get(n) == want.get(n) for n in speedcore.COPIED) and same_consts,
              "the speed bot's copy (speedcore.py) still matches the paper speed check word for word")
    check(C.ALIASES["speed"] == "pspeed" and "pspeed" in __import__("autoupdate").BOTS,
          "the phone knows 'stop speed', and the auto-update restarts the speed bot when it is switched on")
    # no jump in the last 5 seconds, none without 15 minutes of prices
    f = SP.Fair()
    for sec in range(-1000, 298):
        f.add(90_000 + (sec % 2) * 3, (w + sec) * 1000)
    check(f.jump((w + 296) * 1000) is None and f.add(90_400, (w + 296) * 1000 + 500) and
          f.jump((w + 296) * 1000 + 500) is None, "no buys in a window's last 5 seconds")
    f2 = SP.Fair()
    for sec in range(-100, 60):
        f2.add(90_000 + (sec % 2) * 3, (w + sec) * 1000)
    f2.add(90_400, (w + 60) * 1000 + 500)
    check(f2.jump((w + 60) * 1000 + 500) is None, "no buys until it has heard 15 minutes of prices before the window")
    # REAL mode: the order is all or nothing, limit = the offer seen
    os.environ["LIVE"] = "yes"
    os.environ["PSPEED_LIVE"] = "yes"
    check(SP.is_real(), "real buys need both LIVE=yes and PSPEED_LIVE=yes")
    orders = []

    class Fake:
        wallet_type = "POLY_PROXY"

        def place_market_order(self, **kw):
            orders.append(kw)
            ok = len(orders) == 1
            return SimpleNamespace(ok=ok, order_id="0x" + "ab" * 32, status="matched" if ok else "killed",
                                   making_amount=kw["amount"], taking_amount=Decimal("5") if ok else Decimal("0"),
                                   code="FOK_KILLED", message="no fill")
    P._client = Fake()
    b2 = C.Book("pspeed_r")
    sp2 = SP.Speed(b2, send=SP.sender(), clock=lambda: w + 60.0)
    sp2.why_stopped, sp2.cash = None, 30.0
    sp2.add_window(w, "UP", "DOWN", "0xc")
    sp2.books.lv["UP"] = {"a": {0.55: 20.0}, "b": {0.45: 50.0}}
    sp2.books.lv["DOWN"] = {"a": {}, "b": {}}
    pl = sp2.decide(w, "Up", 0.7, int(time.time() * 1000))
    sp2.execute(pl)
    check(len(orders) == 1 and orders[0]["order_type"] == "FOK" and orders[0]["max_price"] == Decimal("0.56")
          and orders[0]["side"] == "BUY" and len(b2.state["open"]) == 1,
          "a real speed buy is all-or-nothing and pays at most 1c above the offer it saw")
    pl = sp2.decide(w, "Down", 0.7, int(time.time() * 1000))
    check(pl and pl["ask"] == 0.55 and pl["token"] == "DOWN", "Down's offer is read from Up's mirrored buy offers")
    sp2.execute(pl)
    check(len(orders) == 2 and len(b2.state["open"]) == 1 and not sp2.busy,
          "a killed order (the offer was gone) buys nothing and frees the bot for the next jump")
    sp2.cash = 2.0
    sp2.tries.clear()
    check(sp2.decide(w, "Up", 0.7, int(time.time() * 1000)) is None, "never buys with less cash than the bet")
    sp2.cash = 30.0
    for extra, want, what in ((None, 0.56, "with no PSPEED_EXTRA_C it pays at most 1c above the offer seen (Jan's pick)"),
                              ("0", 0.55, "PSPEED_EXTRA_C=0 makes the limit exactly the offer seen"),
                              ("10", 0.58, "PSPEED_EXTRA_C is capped at 3c, whatever the file says")):
        if extra is None:
            os.environ.pop("PSPEED_EXTRA_C", None)
        else:
            os.environ["PSPEED_EXTRA_C"] = extra
        sp2.tries.clear()
        sp2.busy = False
        pl = sp2.decide(w, "Up", 0.7, int(time.time() * 1000))
        check(pl and abs(pl["limit"] - want) < 1e-9 and pl["ask"] == 0.55, what)
    sp2.busy = False
    sp2.execute(pl)
    check(orders[-1]["max_price"] == Decimal("0.58"), "the order is sent with that limit")
    os.environ.pop("PSPEED_EXTRA_C", None)
    o = next(iter(b2.state["open"].values()))
    check("ab" * 20 not in str(o), "the public notebook keeps only the end of the order number")
    for k in ("LIVE", "PSPEED_LIVE"):
        os.environ.pop(k, None)


if __name__ == "__main__":
    test_sign()
    test_balance()
    test_phone()
    test_privacy()
    test_mode_switch()
    test_kalshi()
    test_poly()
    test_pspeed()
    for w in OK:
        print("ok  ", w)
    print(f"ALL OK ({len(OK)} checks)")
