"""Offline test of the two real-money bots: fake Kalshi / Polymarket / Binance answers, no network, no keys,
no orders. Runs in a temp folder. setup.sh and update.sh run it; it must print ALL OK.

    python3 live/selftest.py
"""
import datetime as dt
import os
import sys
import tempfile
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp()
os.environ["LIVE_DIR"] = TMP
os.environ["LIVE_ENV"] = os.path.join(TMP, "none.env")
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import bot  # noqa: E402
import common as C  # noqa: E402
import kalshi_live as K  # noqa: E402
import poly_live as P  # noqa: E402

C._switch.update(t=1e18, val={"kalshi": "on", "poly": "on"}, fails=0)   # no GitHub read in the test
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
            return 200, {"balance": 3000, "balance_dollars": "30.00"}
        if method == "POST":
            return 201, {"order": {"order_id": "abc", "status": "resting"}}
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
    check(len(post) == 1 and post[0]["post_only"] and post[0]["yes_price_dollars"] == "0.9710"
          and post[0]["count"] == 4 and post[0]["expiration_ts"] == int(close.timestamp())
          and post[0]["cancel_order_on_pause"], "Kalshi live bid is post-only, dies at the close, cancels on pause")
    at(46, 30)
    bot._kalshi_cache.clear()
    bot.http_json = (lambda f: lambda url, params=None, retries=3: (
        {"market": {"result": "no"}} if "/markets/KXBTC15M-T1" in url else f(url, params)))(bot.http_json)
    K.settle(book)
    check(abs(book.state["realized"] + 3.884) < 1e-6 and book.state["lost"] == 1,
          "Kalshi live loss is booked from the real order (4 filled, -$3.88)")

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
                    SimpleNamespace(condition_id="0xold", current_value=3, title="an old win")]
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
    bot.http_json = lambda url, params=None, retries=3: [{"closed": True, "outcomePrices": '["1", "0"]'}]
    os.environ["POLY_RELAYER_KEY"] = "k"
    P.settle(b3)
    red = [c["redeem"] for c in calls if "redeem" in c]
    check(b3.state["won"] == 3 and b3.state["realized"] > 0 and red == ["0xc", "0xold"],
          "Polymarket settles won draws, then claims every claimable win (old ones too), once each")
    del os.environ["POLY_RELAYER_KEY"]
    check(key in b3.state["done"], "a settled market is never bought again")
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
    del os.environ["NTFY_CONTROL"]


if __name__ == "__main__":
    test_sign()
    test_phone()
    test_kalshi()
    test_poly()
    for w in OK:
        print("ok  ", w)
    print(f"ALL OK ({len(OK)} checks)")
