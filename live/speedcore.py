"""The parts of quoter/speedcheck.py the speed bot (pspeed_live.py) needs, copied word for word on 25 Nov 2026.

Why a copy: the server's auto-update (autoupdate.py) tests new code in a side folder that holds only live/, bot.py
and config.json, so the real bots must not import anything from quoter/. selftest.py checks this copy still matches
quoter/speedcheck.py whenever both are there (in the repo), so the two can't drift apart unnoticed.
"""
import json
import math
import time
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
PM_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
BN_WS = "wss://stream.binance.com:9443/ws/btcusdt@trade"
UA = "poly-paper-bot speed bot (Jan's own small test)"
MOVE = 0.5            # keep a Bitcoin price when it moved $0.50+ since the last kept one (or 1 s passed)
WIN = 300
COPIED = ["now_ms", "http", "parse_bn", "Books", "window_tokens", "window_result", "norm_cdf"]


def now_ms():
    return time.time_ns() // 1_000_000

def http(method, url, body=None, headers=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": UA, "Accept": "application/json", **({"Content-Type": "application/json"} if data else {}), **(headers or {})}
    with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=timeout) as r:
        raw = r.read()
    return json.loads(raw) if raw else None

def parse_bn(raw):
    m = json.loads(raw)
    if m.get("e") == "trade":
        yield float(m["p"]), int(m["T"])

class Books:
    """Top of book per token from the market feed ("book" snapshots + "price_change" level updates)."""

    def __init__(self, log):
        self.log = log
        self.tok = {}        # token -> (window start, "Up"/"Down", coin)
        self.lv = {}         # token -> {"b": {price: size}, "a": {price: size}}
        self.top = {}        # token -> last written (bb, bs, ba, as)

    def add_window(self, w, up, down, c="btc"):
        self.tok[up], self.tok[down] = (w, "Up", c), (w, "Down", c)
        for t in (up, down):
            self.lv.setdefault(t, {"b": {}, "a": {}})

    def drop_before(self, w):
        for t, v in list(self.tok.items()):
            if v[0] < w:
                self.tok.pop(t, None)
                self.lv.pop(t, None)
                self.top.pop(t, None)

    def _emit(self, t, r):
        lv = self.lv.get(t)
        if not lv or t not in self.tok:
            return
        w, o, c = self.tok[t]
        if o != "Up":          # Down's book is Up's mirrored (Down ask = 1 - Up bid): one side is enough
            return
        bb = max(lv["b"]) if lv["b"] else None
        ba = min(lv["a"]) if lv["a"] else None
        top = (bb, lv["b"].get(bb), ba, lv["a"].get(ba))
        old = self.top.get(t)
        # write when a best price moves, or its size changes by 20+ in 100 (size crumbs alone ~200 lines a second)
        if old is None or old[0] != bb or old[2] != ba or any(
                (a or 0) and abs((b or 0) - a) > 0.2 * a for a, b in ((old[1], top[1]), (old[3], top[3]))):
            self.top[t] = top
            self.log.put({"k": "bk", "r": r, "w": w, "o": o, "c": c, "bb": top[0], "bs": top[1], "ba": top[2], "as": top[3]})

    def handle(self, raw, r=None):
        r = r or now_ms()
        try:
            msgs = json.loads(raw)
        except ValueError:
            return
        for m in msgs if isinstance(msgs, list) else [msgs]:
            et = m.get("event_type")
            if et == "book":
                t = m.get("asset_id")
                if t in self.lv:
                    self.lv[t] = {"b": {float(x["price"]): float(x["size"]) for x in m.get("bids") or []},
                                  "a": {float(x["price"]): float(x["size"]) for x in m.get("asks") or []}}
                    self._emit(t, r)
            elif et == "price_change":
                touched = set()
                for c in m.get("price_changes") or m.get("changes") or []:
                    t = c.get("asset_id") or m.get("asset_id")
                    if t not in self.lv:
                        continue
                    side = "b" if str(c.get("side")).upper() == "BUY" else "a"
                    px, sz = float(c["price"]), float(c["size"])
                    if sz <= 0:
                        self.lv[t][side].pop(px, None)
                    else:
                        self.lv[t][side][px] = sz
                    touched.add(t)
                for t in touched:
                    self._emit(t, r)
            elif et == "last_trade_price":
                t = m.get("asset_id")
                if t in self.tok:
                    w, o, c = self.tok[t]
                    self.log.put({"k": "tr", "r": r, "w": w, "o": o, "c": c, "p": float(m.get("price") or 0),
                                  "s": float(m.get("size") or 0), "sd": m.get("side"), "e": m.get("timestamp")})

def window_tokens(w, fetch=http, c="btc"):
    """(up token, down token, condition id) of the window starting at w, or None if Gamma doesn't list it yet."""
    rows = fetch("GET", f"{GAMMA}/markets?slug={c}-updown-5m-{w}")
    for m in rows or []:
        names = json.loads(m.get("outcomes") or "[]")
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if len(names) == 2 and len(toks) == 2:
            i = [str(n).lower() for n in names].index("up")
            return toks[i], toks[1 - i], m.get("conditionId")
    return None

def window_result(w, fetch=http, c="btc"):
    rows = fetch("GET", f"{GAMMA}/markets?slug={c}-updown-5m-{w}&closed=true")
    for m in rows or []:
        names = [str(n).lower() for n in json.loads(m.get("outcomes") or "[]")]
        prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        if len(prices) == 2 and sorted(prices) == [0.0, 1.0] and "up" in names:
            return prices[names.index("up")] == 1.0
    return None

def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))
