"""Speed check for Polymarket's Bitcoin 5-minute windows (Jan, 17 Nov 2026: "just to learn, we aren't committing any
money yet"). Runs on Jan's AWS server next to the combo quoter.

LISTEN ONLY. No key, no login, no orders: it only reads public price feeds. The question it answers: when Bitcoin
jumps, how long do Polymarket's old-price sell offers in the 5-minute "Bitcoin Up or Down" windows stay up, measured
from the moment THIS server hears the jump? If they are usually gone before we could reach them, a speed bot like the
Reddit "GoodFallen" wallet's is not for us (see backtest/wallet5m.md).

It writes one JSON line per event (in DATA_DIR, a new file every UTC day, speed-YYYYMMDD.jsonl), all times are this
server's clock in milliseconds ("r"):
  {"k":"bn", "r", "e", "p"}            Binance BTCUSDT trade price (e = Binance's own time), when it moves $0.50+
  {"k":"cb", "r", "e", "p"}            Coinbase BTC-USD price, same rule
  {"k":"cl", "r", "e", "p"}            Chainlink BTC/USD via Polymarket's live feed (what the windows settle on), if it works
  {"k":"bk", "r", "w", "o", "bb","bs","ba","as"}   top of the Up book of window w (start time) when a best price
                                       moves or its size changes a lot: best bid, its size, best ask, its size.
                                       Down's is the mirror: Down ask = 1 - Up bid
  {"k":"tr", "r", "w", "o", "p", "s", "sd"}         a trade on that window (price, shares, side as Polymarket says)
  {"k":"win", "w", "up", "down", "cid"}             token ids of a window
  {"k":"res", "w", "up_won"}                        a finished window's result (from Gamma)
  {"k":"ping", "r", "what", "ms", "off"}            round trip to Polymarket's order server / Binance / Kalshi, clock gap
Added 25 Nov (Jan, 19 Nov: "remember to do that in the next test"; the second test):
  {"k":"bs"|"kr"|"bf", "r", "e", "p"}  Bitcoin from Bitstamp, Kraken and Binance futures (same $0.50 rule)
  {"k":"ax", "s", "r", "e", "p"}       Binance spot of the other Kalshi coins (s = "ETH", "SOL", ...), moves of 1 in 150,000
  "c" on bk / tr / win / res lines     the coin of a Polymarket 5-minute window ("btc", "eth", "sol"; missing = btc)
  {"k":"kw", "t", "sr", "open", "close", "strike"}  a Kalshi 15-minute crypto market (ticker, series, times in s)
  {"k":"kb", "r", "t", "yb","ys","nb","ns", "ms"}   Kalshi top of book when it changes: best Yes bid + size, best No
                                       bid + size (Yes ask = 1 - best No bid), ms = that read's round trip. Read every
                                       second in a window's last ~7 minutes (where the kc_maker bots bid), else every 10 s
  {"k":"kt", "t", "e", "yp", "n", "tk"}             every Kalshi trade of a finished window (e = Kalshi's time in ms,
                                       yp = Yes price, n = contracts, tk = taker side), read just after the close
  {"k":"kres", "t", "yes"}                          a finished Kalshi window's result
Every hour the day files are uploaded to the GitHub release `speed-data` (same GITHUB_TOKEN as the quoter).
`python3 speedcheck.py score <files>` (in the repo, offline) turns them into the answer.

Run:  python3 speedcheck.py run        (normally via systemd: bash quoter/speed_setup.sh)
      python3 speedcheck.py selftest   (offline, no network)
"""
import asyncio
import datetime as dt
import gzip
import json
import math
import os
import shutil
import sys
import time
import urllib.error
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
PM_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
RTDS_WS = "wss://ws-live-data.polymarket.com"
BN_WS = "wss://stream.binance.com:9443/ws/btcusdt@trade"
CB_WS = "wss://ws-feed.exchange.coinbase.com"
BF_WS = "wss://fstream.binance.com/ws/btcusdt@aggTrade"       # Binance futures (busier than spot, often first)
BS_WS = "wss://ws.bitstamp.net"
KR_WS = "wss://ws.kraken.com/v2"
KALSHI = "https://external-api.kalshi.com/trade-api/v2"      # same public, no-key address as bot.py
# the Kalshi coins the kc_maker bots bid on, and their Binance spot symbol (as bot.KMAKER_SPOT)
KSERIES = {"KXBTC15M": "BTC", "KXETH15M": "ETH", "KXSOL15M": "SOL", "KXXRP15M": "XRP", "KXDOGE15M": "DOGE",
           "KXHYPE15M": "HYPE", "KXBNB15M": "BNB"}
ALTS = [c for c in KSERIES.values() if c != "BTC"]
ALT_WS = "wss://stream.binance.com:9443/stream?streams=" + "/".join(f"{c.lower()}usdt@trade" for c in ALTS)
POLY_COINS = [c for c in os.environ.get("SPEED_POLY_COINS", "btc,eth,sol").split(",") if c]
KWATCH = 420          # read Kalshi books every second in a window's last 7 minutes (the bots bid from 5.5 min left)
REPO = "palsk1/poly-paper-bot"
TAG = "speed-data"
UA = "poly-paper-bot speedcheck (paper research)"
MOVE = 0.5            # write a Bitcoin price when it moved $0.50+ since the last written one (or 1 s passed)
WIN = 300


def now_ms():
    return time.time_ns() // 1_000_000


def http(method, url, body=None, headers=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": UA, "Accept": "application/json", **({"Content-Type": "application/json"} if data else {}), **(headers or {})}
    with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=timeout) as r:
        raw = r.read()
    return json.loads(raw) if raw else None


class Log:
    def __init__(self, d):
        self.d = os.path.expanduser(d)
        os.makedirs(self.d, exist_ok=True)
        self.fh, self.day = None, None
        import threading
        self.lock = threading.Lock()      # the Kalshi reader and the pings write from their own threads

    def path(self, day=None):
        return os.path.join(self.d, f"speed-{day or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')}.jsonl")

    def put(self, obj):
        obj.setdefault("r", now_ms())
        line = json.dumps(obj, separators=(",", ":")) + "\n"
        with self.lock:
            day = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
            if day != self.day:
                if self.fh:
                    self.fh.close()
                self.fh, self.day = open(self.path(day), "a", buffering=1 << 16), day
            self.fh.write(line)

    def flush(self):
        with self.lock:
            if self.fh:
                self.fh.flush()


def upload_all(log, token):
    """gzip the day files and put them on the release `speed-data` (today's and yesterday's are replaced)."""
    log.flush()
    if not token:
        return "no GITHUB_TOKEN, kept local"
    h = {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"}
    try:
        rel = http("GET", f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", headers=h)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        rel = http("POST", f"https://api.github.com/repos/{REPO}/releases", {
            "tag_name": TAG, "name": "Speed check logs", "prerelease": True,
            "body": "Public Bitcoin and Polymarket 5-minute window prices as Jan's server heard them (quoter/speedcheck.py). "
                    "Paper research data only."}, headers=h)
    have = {a["name"]: a["id"] for a in http("GET", f"https://api.github.com/repos/{REPO}/releases/{rel['id']}/assets?per_page=100", headers=h)}
    n = 0
    today = dt.datetime.now(dt.timezone.utc)
    recent = {(today - dt.timedelta(days=d)).strftime("%Y%m%d") for d in (0, 1)}
    for fn in sorted(os.listdir(log.d)):
        if not fn.endswith(".jsonl"):
            continue
        day = fn[len("speed-"):len("speed-") + 8]
        if day < (today - dt.timedelta(days=7)).strftime("%Y%m%d"):
            os.remove(os.path.join(log.d, fn))
            continue
        name = fn + ".gz"
        if day not in recent and name in have:
            continue
        src = os.path.join(log.d, fn)
        gz = src + ".gz"
        with open(src, "rb") as a, gzip.open(gz, "wb") as b:
            shutil.copyfileobj(a, b)
        if name in have:
            http("DELETE", f"https://api.github.com/repos/{REPO}/releases/assets/{have[name]}", headers=h)
        req = urllib.request.Request(f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={name}",
                                     data=open(gz, "rb").read(), method="POST",
                                     headers={**h, "Content-Type": "application/gzip", "User-Agent": UA})
        urllib.request.urlopen(req, timeout=300).read()
        os.remove(gz)
        n += 1
    return f"uploaded {n} files"


# ---------------------------------------------------------------- price feeds
class Mover:
    """Writes a price line only when it moved $0.50+ or a second passed (keeps the files small)."""

    def __init__(self, log, kind, sym=None):
        self.log, self.kind, self.sym, self.last, self.last_r = log, kind, sym, None, 0

    def see(self, p, e, r=None):
        r = r or now_ms()
        move = MOVE if self.sym is None else p / 150_000
        if self.last is None or abs(p - self.last) >= move or r - self.last_r >= 1000:
            self.last, self.last_r = p, r
            o = {"k": self.kind, "r": r, "e": e, "p": p}
            if self.sym:
                o["s"] = self.sym
            self.log.put(o)


async def feed(name, url, sub, parse, log, ws_lib):
    movers = {}
    backoff = 2
    while True:
        try:
            async with ws_lib.connect(url, ping_interval=20, max_size=2 ** 22) as ws:
                if sub:
                    await ws.send(json.dumps(sub))
                backoff = 2
                async for raw in ws:
                    r = now_ms()
                    for x in parse(raw):
                        sym = x[2] if len(x) > 2 else None
                        mv = movers.get(sym) or movers.setdefault(sym, Mover(log, name, sym))
                        mv.see(x[0], x[1], r)
        except Exception as ex:  # noqa: BLE001
            log.put({"k": "note", "what": f"{name} disconnected", "err": f"{type(ex).__name__}: {ex}"[:200]})
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 120)


def parse_bn(raw):
    m = json.loads(raw)
    if m.get("e") == "trade":
        yield float(m["p"]), int(m["T"])


def parse_cb(raw):
    m = json.loads(raw)
    if m.get("type") == "ticker" and m.get("price"):
        t = m.get("time")
        e = int(dt.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() * 1000) if t else None
        yield float(m["price"]), e


def parse_cl(raw):
    try:
        m = json.loads(raw)
    except ValueError:
        return
    pl = m.get("payload") or {}
    if str(pl.get("symbol", "")).lower() in ("btc/usd", "btcusd") and pl.get("value") is not None:
        yield float(pl["value"]), pl.get("timestamp")


def _iso_ms(t):
    try:
        return int(dt.datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError:
        return None


def parse_bf(raw):
    m = json.loads(raw)
    if m.get("e") == "aggTrade":
        yield float(m["p"]), int(m["T"])


def parse_bs(raw):
    m = json.loads(raw)
    d = m.get("data") or {}
    if m.get("event") == "trade" and d.get("price") is not None:
        mt = d.get("microtimestamp")
        yield float(d["price"]), int(mt) // 1000 if mt else None


def parse_kr(raw):
    m = json.loads(raw)
    if m.get("channel") == "trade":
        for d in m.get("data") or []:
            if d.get("price") is not None:
                yield float(d["price"]), _iso_ms(d.get("timestamp")) if d.get("timestamp") else None


def parse_alt(raw):
    m = json.loads(raw)
    d = m.get("data") or {}
    if d.get("e") == "trade" and str(d.get("s", "")).endswith("USDT"):
        yield float(d["p"]), int(d["T"]), d["s"][:-4]


# ---------------------------------------------------------------- Polymarket 5-minute windows
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


async def market_socket(log, ws_lib, books, feed):
    """One Polymarket market socket kept open. New windows' tokens are added and old ones dropped on the open
    socket ("operation": "subscribe" / "unsubscribe" frames, Polymarket docs), so no window starts blind."""
    while True:
        feed["add"].clear()
        feed["drop"].clear()
        subs = sorted(books.tok)
        if not subs:
            await asyncio.sleep(1)
            continue
        try:
            async with ws_lib.connect(PM_WS, ping_interval=None, max_size=2 ** 23) as ws:
                await ws.send(json.dumps({"assets_ids": subs, "type": "market"}))
                log.put({"k": "note", "what": "market feed connected", "n": len(subs)})
                last_ping = time.time()
                while True:
                    if feed["add"]:
                        add, feed["add"] = feed["add"], []
                        await ws.send(json.dumps({"assets_ids": add, "operation": "subscribe"}))
                        log.put({"k": "note", "what": "market feed added", "n": len(add)})
                    if feed["drop"]:
                        drop, feed["drop"] = feed["drop"], []
                        await ws.send(json.dumps({"assets_ids": drop, "operation": "unsubscribe"}))
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=0.25)
                    except asyncio.TimeoutError:
                        raw = None
                    if raw and raw != "PONG":
                        books.handle(raw)
                    if time.time() - last_ping > 9:
                        await ws.send("PING")
                        last_ping = time.time()
        except Exception as ex:  # noqa: BLE001
            log.put({"k": "note", "what": "market feed disconnected", "err": f"{type(ex).__name__}: {ex}"[:200]})
            await asyncio.sleep(2)


async def market_loop(log, ws_lib, loop, step=2.0, lookup=None):
    """Finds the current and next two windows on Gamma, hands their tokens to the kept-open socket, drops old ones
    and fetches results. Until 27 Nov the socket was closed at every window turn and reopened only after the Gamma
    lookups (and again ~10 s later), so seconds 0-11 of each window got about 5 times fewer book updates."""
    lookup = lookup or window_tokens
    books = Books(log)
    feed = {"add": [], "drop": []}
    asyncio.create_task(market_socket(log, ws_lib, books, feed))
    pending = {}     # (coin, window start) -> tries left for its result
    tried = {}       # (coin, window start) -> last Gamma look
    while True:
        now = time.time()
        w0 = int(now) // WIN * WIN
        have = {(v[2], v[0]) for v in books.tok.values()}
        for c in POLY_COINS:
            for w in (w0, w0 + WIN, w0 + 2 * WIN):
                if (c, w) in have or now - tried.get((c, w), 0) < 5:
                    continue
                tried[(c, w)] = now
                try:
                    got = await loop.run_in_executor(None, lookup, w, http, c)
                except Exception as ex:  # noqa: BLE001
                    got = None
                    log.put({"k": "note", "what": "gamma failed", "err": str(ex)[:200]})
                if got:
                    books.add_window(w, got[0], got[1], c)
                    feed["add"] += [got[0], got[1]]
                    log.put({"k": "win", "w": w, "c": c, "up": got[0], "down": got[1], "cid": got[2]})
                    pending.setdefault((c, w), 30)
        old = [t for t, v in books.tok.items() if v[0] < w0]
        if old:
            books.drop_before(w0)
            feed["drop"] += old
        for k in [k for k in tried if len(k) == 2 and k[1] < w0]:
            tried.pop(k)
        # results of finished windows (Gamma marks them a minute or two after the end), one look a minute each
        for c, w in sorted(pending):
            if w + WIN + 90 > now or now - tried.get(("res", c, w), 0) < 60:
                continue
            tried[("res", c, w)] = now
            try:
                res = await loop.run_in_executor(None, window_result, w, http, c)
            except Exception:  # noqa: BLE001
                res = None
            if res is not None:
                log.put({"k": "res", "w": w, "c": c, "up_won": res})
                pending.pop((c, w))
                tried.pop(("res", c, w), None)
            else:
                pending[(c, w)] -= 1
                if pending[(c, w)] <= 0:
                    pending.pop((c, w))
                    tried.pop(("res", c, w), None)
        await asyncio.sleep(step)


# ---------------------------------------------------------------- Kalshi 15-minute crypto (read only, no key)
class KConn:
    """One kept-open HTTPS connection to Kalshi's public API (a fresh one per read would add a handshake each time)."""

    def __init__(self, base=KALSHI):
        import urllib.parse
        u = urllib.parse.urlparse(base)
        self.host, self.root, self.c = u.netloc, u.path, None

    def get(self, path, params=None):
        import http.client
        import urllib.parse
        q = self.root + path + ("?" + urllib.parse.urlencode(params) if params else "")
        for attempt in (0, 1):
            try:
                if self.c is None:
                    self.c = http.client.HTTPSConnection(self.host, timeout=10)
                t0 = now_ms()
                self.c.request("GET", q, headers={"User-Agent": UA, "Accept": "application/json"})
                r = self.c.getresponse()
                raw = r.read()
                ms = now_ms() - t0
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status} {raw[:120]!r}")
                return json.loads(raw), ms
            except (OSError, http.client.HTTPException):
                if self.c:
                    self.c.close()
                self.c = None
                if attempt:
                    raise


def k_num(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def k_top(res):
    """(best Yes bid, its size, best No bid, its size) from a Kalshi /orderbook answer (dollars or cents)."""
    ob = (res.get("orderbook_fp") or res.get("orderbook") or {}) if isinstance(res, dict) else {}
    out = []
    for side in ("yes", "no"):
        best = None
        for x in ob.get(f"{side}_dollars") or ob.get(side) or []:
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                pr, sz = k_num(x[0]), k_num(x[1], 0)
                if pr is None or not sz:
                    continue
                pr = round(pr / 100 if pr > 1 else pr, 4)
                if best is None or pr > best[0]:
                    best = (pr, sz)
        out += list(best or (None, 0))
    return tuple(out)


def k_trade(t):
    """A Kalshi trade as a kt line."""
    yp = k_num(t.get("yes_price_dollars"))
    if yp is None:
        yp = k_num(t.get("yes_price"), 0) / 100
    return {"k": "kt", "t": t.get("ticker"), "e": _iso_ms(t.get("created_time")), "yp": round(yp, 4),
            "n": k_num(t.get("count_fp") or t.get("count"), 0), "tk": t.get("taker_side")}


class KWatch:
    """Kalshi's 15-minute crypto books, every second near the close, and each finished window's whole trade list."""

    def __init__(self, log, conn=None, clock=time.time):
        self.log, self.k, self.clock = log, conn or KConn(), clock
        self.cur = {}        # series -> market dict {t, open, close, strike}
        self.top = {}        # ticker -> last written top
        self.last_read = {}  # ticker -> time of the last book read
        self.done = {}       # ticker -> {"close", "tape": bool, "tries"} for finished markets

    def refresh(self, sr):
        res, _ = self.k.get("/markets", {"series_ticker": sr, "status": "open", "limit": 10})
        now = self.clock()
        best = None
        for m in res.get("markets") or []:
            c, o = _iso_ms(m.get("close_time")), _iso_ms(m.get("open_time"))
            if c and o and c / 1000 > now and (best is None or c < best["close"] * 1000):
                best = {"t": m.get("ticker"), "open": o // 1000, "close": c // 1000, "strike": k_num(m.get("floor_strike"))}
        if best:
            self.cur[sr] = best
            self.log.put({"k": "kw", "sr": sr, **best})
        return best

    def step(self):
        now = self.clock()
        for sr in KSERIES:
            m = self.cur.get(sr)
            if m is None or now >= m["close"]:
                if m is not None:
                    self.done.setdefault(m["t"], {"close": m["close"], "open": m["open"], "tape": False, "tries": 0})
                    self.cur.pop(sr, None)
                try:
                    m = self.refresh(sr)
                except Exception as ex:  # noqa: BLE001
                    self.log.put({"k": "note", "what": f"kalshi {sr} list failed", "err": str(ex)[:200]})
                    m = None
                if m is None:
                    continue
            every = 1 if m["close"] - now <= KWATCH else 10
            if now - self.last_read.get(m["t"], 0) < every - 0.05:
                continue
            self.last_read[m["t"]] = now
            try:
                res, ms = self.k.get(f"/markets/{m['t']}/orderbook")
            except Exception as ex:  # noqa: BLE001
                self.log.put({"k": "note", "what": "kalshi book failed", "err": str(ex)[:200]})
                continue
            top = k_top(res)
            if top != self.top.get(m["t"]):
                self.top[m["t"]] = top
                self.log.put({"k": "kb", "t": m["t"], "yb": top[0], "ys": top[1], "nb": top[2], "ns": top[3], "ms": ms})
        # finished windows: the whole trade list 60 s after the close, the result once Kalshi has it
        for tk, d in list(self.done.items()):
            if now < d["close"] + 60 or now < d.get("next", 0):
                continue
            d["tries"] += 1
            d["next"] = now + 60
            try:
                if not d["tape"]:
                    rows, cur = [], None
                    for _ in range(30):
                        q = {"ticker": tk, "min_ts": d["open"], "max_ts": d["close"] + 1, "limit": 1000}
                        if cur:
                            q["cursor"] = cur
                        res, _ = self.k.get("/markets/trades", q)
                        rows += res.get("trades") or []
                        cur = res.get("cursor")
                        if not cur or not res.get("trades"):
                            break
                    for t in rows:
                        t.setdefault("ticker", tk)
                        self.log.put(k_trade(t))
                    d["tape"] = True
                res, _ = self.k.get(f"/markets/{tk}")
                r = str((res.get("market") or {}).get("result") or "").lower()
                if r in ("yes", "no"):
                    self.log.put({"k": "kres", "t": tk, "yes": r == "yes"})
                    self.done.pop(tk)
                    self.top.pop(tk, None)
                    self.last_read.pop(tk, None)
                    continue
            except Exception as ex:  # noqa: BLE001
                self.log.put({"k": "note", "what": "kalshi tape/result failed", "err": str(ex)[:200]})
            if d["tries"] > 30:
                self.done.pop(tk)

    def forever(self):
        while True:
            t0 = time.time()
            try:
                self.step()
            except Exception as ex:  # noqa: BLE001
                self.log.put({"k": "note", "what": "kalshi loop failed", "err": str(ex)[:200]})
            time.sleep(max(0.05, 1 - (time.time() - t0)))


def ping_once(log):
    for what, url, key in (("clob", f"{CLOB}/time", None), ("binance", "https://api.binance.com/api/v3/time", "serverTime"),
                           ("kalshi", f"{KALSHI}/exchange/status", "")):
        try:
            t0 = now_ms()
            res = http("GET", url, timeout=10)
            t1 = now_ms()
            if key == "":                       # Kalshi tells no time: round trip only
                log.put({"k": "ping", "what": what, "ms": t1 - t0, "off": None})
                continue
            srv = res.get(key) if key and isinstance(res, dict) else res
            srv = float(srv)
            srv = srv * 1000 if srv < 1e11 else srv
            log.put({"k": "ping", "what": what, "ms": t1 - t0, "off": round(srv - (t0 + t1) / 2)})
        except Exception as ex:  # noqa: BLE001
            log.put({"k": "note", "what": f"ping {what} failed", "err": str(ex)[:200]})


async def run():
    import websockets
    log = Log(os.environ.get("SPEED_DIR", "~/speed-data"))
    loop = asyncio.get_running_loop()
    log.put({"k": "note", "what": "start"})
    print("speedcheck: listening (no key, no orders)", flush=True)
    asyncio.create_task(feed("bn", BN_WS, None, parse_bn, log, websockets))
    asyncio.create_task(feed("cb", CB_WS, {"type": "subscribe", "product_ids": ["BTC-USD"], "channels": ["ticker"]},
                             parse_cb, log, websockets))
    asyncio.create_task(feed("cl", RTDS_WS, {"action": "subscribe", "subscriptions": [
        {"topic": "crypto_prices_chainlink", "type": "*", "filters": "{\"symbol\":\"btc/usd\"}"}]}, parse_cl, log, websockets))
    asyncio.create_task(market_loop(log, websockets, loop))
    # second test (25 Nov): three more Bitcoin sources, the other Kalshi coins, Kalshi's books and trade lists
    asyncio.create_task(feed("bf", BF_WS, None, parse_bf, log, websockets))
    asyncio.create_task(feed("bs", BS_WS, {"event": "bts:subscribe", "data": {"channel": "live_trades_btcusd"}},
                             parse_bs, log, websockets))
    asyncio.create_task(feed("kr", KR_WS, {"method": "subscribe", "params": {"channel": "trade", "symbol": ["BTC/USD"]}},
                             parse_kr, log, websockets))
    asyncio.create_task(feed("ax", ALT_WS, None, parse_alt, log, websockets))
    if os.environ.get("SPEED_KALSHI", "1") != "0":
        import threading
        threading.Thread(target=KWatch(log).forever, daemon=True).start()
    last_up = time.time() - 3300
    while True:
        await asyncio.sleep(60)
        await loop.run_in_executor(None, ping_once, log)
        log.flush()
        if time.time() - last_up > 3600:
            last_up = time.time()
            try:
                print("upload:", await loop.run_in_executor(None, upload_all, log, os.environ.get("GITHUB_TOKEN")), flush=True)
            except Exception as ex:  # noqa: BLE001
                log.put({"k": "note", "what": "upload failed", "err": str(ex)[:200]})
                print("upload failed:", ex, flush=True)


# ---------------------------------------------------------------- scoring (offline, in the repo)
def read_lines(paths):
    for p in paths:
        op = gzip.open if p.endswith(".gz") else open
        with op(p, "rt") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


PRICE_KINDS = ("bn", "cb", "cl", "bf", "bs", "kr", "ax")
# Taker fee rate used in the SCORING only (fee = rate x shares x p x (1-p)). Polymarket cut it on 20 Nov 2026 23:59 UTC
# to 0.05 on the BTC 5-/15-minute windows and 0.01 on other crypto; the real bot's 26-27 Nov fills paid about 0.05
# (backtest/refee_speed.md). Default stays the stricter 0.07; change with SPEED_FEE=0.05 or `--fee 0.05`.
SCORE_FEE = float(os.environ.get("SPEED_FEE", "0.07"))


def pkey(o):
    """Price series name of a price line: "bn", "cb", ... for Bitcoin, "ax:ETH" for the other coins."""
    return f"ax:{o.get('s')}" if o["k"] == "ax" else o["k"]


def score(paths, src=None, jump=0.03, react=(0, 50, 100, 200, 500, 1000, 2000), say=print, coin="btc", fee=None):
    """For every Bitcoin jump (the fair price of a side rises `jump`+ within 2 s, as heard by this server), how much
    of Polymarket's sell offers on that side were still at a price below the new fair price minus the fee, `react` ms
    after we heard it? And what would buying them have paid at the window's result? `fee` = taker fee rate
    (default SCORE_FEE)."""
    import bisect
    rate = SCORE_FEE if fee is None else fee
    import collections
    import statistics
    px, books, res, pings = collections.defaultdict(list), collections.defaultdict(list), {}, collections.defaultdict(list)
    want = None if coin == "btc" else f"ax:{coin.upper()}"
    for o in read_lines(paths):
        k = o.get("k")
        if k in PRICE_KINDS:
            pk = pkey(o)
            if (want is None and k != "ax") or pk == want:
                px[pk].append((o["r"], o["p"]))
        elif o.get("c", "btc") != coin and k in ("bk", "res"):
            continue
        elif k == "bk" and o.get("o") == "Up":
            books[(o["w"], "Up")].append((o["r"], o.get("ba"), o.get("as") or 0))
            bb = o.get("bb")
            books[(o["w"], "Down")].append((o["r"], round(1 - bb, 4) if bb is not None else None, o.get("bs") or 0))
        elif k == "res":
            res[o["w"]] = o["up_won"]
        elif k == "ping":
            pings[o["what"]].append(o["ms"])
    say(f"{coin} prices heard:", {k: len(v) for k, v in px.items()})
    src = src or want or max(("bn", "cb", "cl"), key=lambda k: (len(px[k]) > 1000, k == "bn", len(px[k])))
    px = sorted(px[src])
    if len(px) < 100:
        say("not enough Bitcoin prices yet")
        return None
    pt = [p[0] for p in px]

    def price_at(r):
        i = bisect.bisect_right(pt, r) - 1
        return px[i][1] if i >= 0 else None
    for b in books.values():
        b.sort(key=lambda x: x[0])
    for what, v in pings.items():
        v.sort()
        say(f"round trip to {what}: median {v[len(v) // 2]} ms, 90 in 100 under {v[int(len(v) * .9)]} ms ({len(v)} checks)")
    # 1-second returns over the last 15 minutes for the window's volatility
    out = []
    wins = sorted({w for (w, _) in books})
    for w in wins:
        s0 = price_at(w * 1000)
        if not s0:
            continue
        hist = [price_at((w - k) * 1000) for k in range(0, 901, 5)]
        rets = [math.log(hist[i] / hist[i + 1]) for i in range(len(hist) - 1) if hist[i] and hist[i + 1]]
        if len(rets) < 100:
            continue
        sig = statistics.pstdev(rets) / math.sqrt(5)
        if sig <= 0:
            continue

        def fair_up(r):
            s = price_at(r)
            left = (w + WIN) - r / 1000
            if not s or left <= 1:
                return None
            return norm_cdf(math.log(s / s0) / (sig * math.sqrt(left)))
        i0 = bisect.bisect_left(pt, w * 1000)
        i1 = bisect.bisect_left(pt, (w + WIN - 5) * 1000)
        last_r = -10 ** 15
        for i in range(i0, i1):
            r = pt[i]
            if r - last_r < 3000:        # one jump at a time: 3 s apart
                continue
            f_now, f_then = fair_up(r), fair_up(r - 2000)
            if f_now is None or f_then is None or abs(f_now - f_then) < jump:
                continue
            last_r = r
            side = "Up" if f_now > f_then else "Down"
            fair = f_now if side == "Up" else 1 - f_now
            won = None if w not in res else res[w] == (side == "Up")
            bk = books.get((w, side)) or []
            bt = [b[0] for b in bk]
            row = {"w": w, "r": r, "side": side, "fair": fair, "won": won, "at": {}}
            for d in react:
                j = bisect.bisect_right(bt, r + d) - 1
                if j < 0 or bk[j][1] is None:
                    continue
                ask, size = bk[j][1], bk[j][2]
                row["at"][d] = {"ask": ask, "size": size, "edge": fair - ask - rate * ask * (1 - ask)}
            j = bisect.bisect_right(bt, r) - 1
            if j >= 0 and bk[j][1] is not None and fair - bk[j][1] - rate * bk[j][1] * (1 - bk[j][1]) > 0.01:
                # how long the old ask lasted after we heard the jump
                k = j
                while k + 1 < len(bk) and bk[k + 1][1] is not None and bk[k + 1][1] <= bk[j][1] + 1e-9:
                    k += 1
                row["lasted"] = (bk[k + 1][0] - r) if k + 1 < len(bk) else None
            out.append(row)
    hours = (pt[-1] - pt[0]) / 3_600_000
    say(f"{len(out)} Bitcoin jumps of {int(jump * 100)}c+ in a side's fair price over {hours:.1f} hours ({src} prices; "
        f"a window needs 15 minutes of prices before it starts)")
    for d in react:
        rows = [x for x in out if d in x["at"] and x["at"][d]["edge"] > 0.01]
        c = sum(x["at"][d]["ask"] * x["at"][d]["size"] for x in rows)
        known = [x for x in rows if x["won"] is not None]
        ck = sum(x["at"][d]["ask"] * x["at"][d]["size"] for x in known)
        p = sum(x["at"][d]["size"] * x["won"] for x in known)
        fee = sum(rate * x["at"][d]["ask"] * (1 - x["at"][d]["ask"]) * x["at"][d]["size"] for x in known)
        say(f"  {d:>5} ms after we heard it: {len(rows)} jumps still had an old-price sell offer 1c+ under fair after fees "
            f"(${c:,.0f} on offer); buying all of it: {'no results yet' if not ck else f'{100 * (p - ck - fee) / ck:+.2f} per $100'}")
    la = sorted(x["lasted"] for x in out if x.get("lasted") is not None)
    if la:
        say(f"  old-price offers (1c+ under fair) still up when we heard the jump: {len(la)}; they lasted a median "
            f"{la[len(la) // 2]} ms after that, 1 in 4 under {la[len(la) // 4]} ms")
    return out


def window_bets(out, d, band=(0.40, 0.95), cap=25.0, fee=None, skip_first=0, t_from=None, t_to=None):
    """The edge() purchase rule on score()'s jump rows, one bet per window (jumps inside one window move together):
    buy the jumped-toward side at the best ask seen `d` ms after hearing the jump, up to $cap, ask in `band`, taker
    fee `fee` x shares x p x (1-p), held to the result. `skip_first` drops jumps heard in a window's first seconds
    (the box's book feed was nearly blind in seconds 0-11 until the 27 Nov feed fix, swing.FIRST). `t_from` / `t_to`
    keep windows starting in [t_from, t_to) (unix s). Returns exam-style bets: cost, pay, t, ev, n (jumps), sh."""
    import collections
    rate = SCORE_FEE if fee is None else fee
    byw = collections.defaultdict(lambda: {"cost": 0.0, "pay": 0.0, "sh": 0.0, "n": 0})
    for x in out:
        if x["won"] is None or d not in x["at"] or not band[0] <= x["at"][d]["ask"] < band[1]:
            continue
        if (t_from is not None and x["w"] < t_from) or (t_to is not None and x["w"] >= t_to):
            continue
        if skip_first and x["r"] - x["w"] * 1000 < skip_first * 1000:
            continue
        a = x["at"][d]["ask"]
        sh = min(x["at"][d]["size"], cap / a)
        b = byw[x["w"]]
        b["cost"] += sh * (a + rate * a * (1 - a))
        b["pay"] += sh * x["won"]
        b["sh"] += sh
        b["n"] += 1
    return [dict(v, t=w, ev=w) for w, v in sorted(byw.items()) if v["cost"] > 0]


def edge(paths, srcs=("bn", "cb", "bf", "bs", "kr"), band=(0.40, 0.95), cap=25.0, delays=(0, 100, 200, 500, 1000), say=print,
         coin="btc", fee=None, skip_first=0):
    """After each jump: buy the jumped-toward side at the best ask seen `d` ms after we heard it, up to $cap, ask in
    `band`, taker fee included, held to the window's result. Luck range by resampling whole windows (jumps inside one
    window move together). First run 18 Nov (20 h): Binance at 100 ms +$5.31 per $100, range +2.3..+8.3,
    falling to about $0 at 1 s. The 40-95c band was picked after looking. `fee` = taker fee rate (default SCORE_FEE),
    `skip_first` = drop jumps in a window's first seconds (see window_bets)."""
    import random
    if coin != "btc":
        srcs = (f"ax:{coin.upper()}",)
    res = {}
    for src in srcs:
        out = score(paths, src=src, say=lambda *a, **k: None, coin=coin, fee=fee) or []
        for d in delays:
            bets = window_bets(out, d, band=band, cap=cap, fee=fee, skip_first=skip_first)
            ws = [(b["pay"] - b["cost"], b["cost"]) for b in bets]
            if not ws:
                continue
            nj = sum(b["n"] for b in bets)
            p, s = sum(v[0] for v in ws), sum(v[1] for v in ws)
            rnd = random.Random(2)
            bs = sorted(100 * sum(v[0] for v in smp) / max(1e-9, sum(v[1] for v in smp))
                        for smp in ([ws[rnd.randrange(len(ws))] for _ in ws] for _ in range(500)))
            say(f"{coin} {src} {d:5} ms, asks {band[0]:.2f}-{band[1]:.2f}: {nj} jumps in {len(ws)} windows, ${s:,.0f} bought, "
                f"P&L ${p:,.0f} = {100 * p / s:+.2f} per $100, luck range {bs[25]:+.1f} to {bs[475]:+.1f}")
            res[(src, d)] = (nj, s, p)
    return res


def lead(paths, base="bn", others=("cb", "bf", "bs", "kr", "cl"), say=print):
    """Which Bitcoin source hears a jump first? The same jump (same window and side, within 2 s) as heard by each
    source against `base`; minus = that source heard it first. Plus feed drops per day."""
    import collections
    import datetime as _dt
    o = {s: score(paths, src=s, say=lambda *a, **k: None) or [] for s in (base, *others)}
    out = {}
    for s in others:
        idx = collections.defaultdict(list)
        for x in o[s]:
            idx[(x["w"], x["side"])].append(x["r"])
        d = []
        for x in o[base]:
            m = [r for r in idx.get((x["w"], x["side"]), []) if abs(r - x["r"]) <= 2000]
            if m:
                d.append(min(m, key=lambda r: abs(r - x["r"])) - x["r"])
        d.sort()
        if not d:
            say(f"{s}: no jumps to match")
            continue
        n = len(d)
        out[s] = {"n": n, "median": d[n // 2], "first": sum(v < 0 for v in d), "later": sum(v > 0 for v in d)}
        say(f"{s} vs {base}: {n} same jumps (of {len(o[base])}); {s} first {out[s]['first']}, {base} first {out[s]['later']}; "
            f"{s} minus {base}: median {d[n // 2]} ms, middle half {d[n // 4]} to {d[3 * n // 4]} ms")
    c = collections.Counter()
    for x in read_lines(paths):
        if x.get("k") == "note" and ("disconnected" in x.get("what", "") or "failed" in x.get("what", "")):
            c[(_dt.datetime.fromtimestamp(x["r"] / 1000, _dt.timezone.utc).strftime("%m-%d"), x["what"])] += 1
    for k in sorted(c):
        say(f"  {k[0]} {k[1]}: {c[k]}")
    return out


def kcancel(paths, floor=0.90, left=(45, 330), lookback=15_000, bars=(1.0, 1.5, 2.0), lats=(0, 100, 250, 500, 1000),
            say=print):
    """Could a fast box have pulled a kc_maker_safe-style bid before a losing fill? Every Kalshi trade where a resting
    bid at `floor`+ was sold to (the maker side is the one the taker did NOT take), 45 s to 5.5 min before the close,
    where Binance put that side at a z of 2+ `lookback` ms before the fill (roughly when the bot would have bid).
    Cancel rule: pull the bid when the z of our side falls under `bar`; with `lat` ms between hearing it and the cancel
    landing, a fill is dodged if the z was already under the bar `lat` ms before the fill. Reports what the rule
    saves on losing fills and what it costs on winning ones (maker, no fee). The z: Binance spot moved onto Kalshi's
    price by the gap at the open (as kc_maker_safe_usd), typical 1 s move over the last 5 minutes, no fee.
    These are other people's bids standing in for ours."""
    import bisect
    import collections
    kw, kres, trades, px = {}, {}, [], collections.defaultdict(list)
    for o in read_lines(paths):
        k = o.get("k")
        if k == "kw":
            kw[o["t"]] = o
        elif k == "kres":
            kres[o["t"]] = o["yes"]
        elif k == "kt":
            trades.append(o)
        elif k == "bn":
            px["BTC"].append((o["r"], o["p"]))
        elif k == "ax":
            px[o["s"]].append((o["r"], o["p"]))
    for v in px.values():
        v.sort()
    pt = {c: [x[0] for x in v] for c, v in px.items()}

    def price_at(c, r):
        i = bisect.bisect_right(pt[c], r) - 1
        return px[c][i][1] if i >= 0 else None

    prep = {}

    def zyes(m, c, r):
        """z of Yes at ms time r, from per-second Binance prices (cached per market)."""
        if c not in px or not m.get("strike"):
            return None
        g = prep.get(m["t"])
        if g is None:
            t0 = m["close"] - 900 - 360          # the 15 minutes start at close - 900 (the strike is the index then)
            sec = [price_at(c, (t0 + i) * 1000) for i in range(m["close"] - t0 + 1)]
            pre = [p for p in sec[300:361] if p]
            cum, acc = [0.0], 0.0
            for i in range(1, len(sec)):
                if sec[i] and sec[i - 1]:
                    acc += (sec[i] - sec[i - 1]) ** 2
                cum.append(acc)
            g = prep[m["t"]] = (t0, sec, cum, (m["strike"] - sum(pre) / len(pre)) if len(pre) >= 50 else None)
        t0, sec, cum, basis = g
        i = int(r // 1000) - t0
        S = price_at(c, r)
        if basis is None or S is None or i < 300 or i >= len(sec) or not sec[i - 300]:
            return None
        L = m["close"] - r / 1000
        sd = math.sqrt(max((cum[i] - cum[i - 300]) / 300 * max(L, 1), 1e-18))
        return (S + basis - m["strike"]) / sd
    fills = []
    for t in trades:
        m = kw.get(t["t"])
        if not m or t["t"] not in kres or not t.get("e") or t.get("tk") not in ("yes", "no"):
            continue
        side = "no" if t["tk"] == "yes" else "yes"
        price = t["yp"] if side == "yes" else round(1 - t["yp"], 4)
        lf = m["close"] - t["e"] / 1000
        if price < floor or not (left[0] <= lf <= left[1]):
            continue
        c = KSERIES.get(m["sr"])
        sign = 1 if side == "yes" else -1
        z0 = zyes(m, c, t["e"] - lookback)
        if z0 is None or sign * z0 < 2:
            continue
        path = []
        for back in range(lookback, -1, -100):
            z = zyes(m, c, t["e"] - back)
            path.append((back, None if z is None else sign * z))
        fills.append({"t": t["t"], "c": c, "price": price, "n": t["n"], "won": kres[t["t"]] == (side == "yes"),
                      "path": path})
    if not fills:
        say("no Kalshi maker fills to score yet")
        return None

    def pnl(xs):
        return sum(x["n"] * ((1 if x["won"] else 0) - x["price"]) for x in xs), sum(x["n"] * x["price"] for x in xs)
    P, S = pnl(fills)
    lost = [x for x in fills if not x["won"]]
    say(f"{len(fills)} Kalshi fills of bids at {int(floor * 100)}c+ ({len(lost)} lost) on {len({x['t'] for x in fills})} "
        f"windows: ${S:,.0f} bought, P&L ${P:,.0f} = {100 * P / max(S, 1e-9):+.2f} per $100 with no cancelling")
    out = {}
    for bar in bars:
        for lat in lats:
            keep = [x for x in fills if not any(z is not None and z < bar for back, z in x["path"] if back >= lat)]
            p, s_ = pnl(keep)
            dl = [x for x in lost if x not in keep]
            dw = [x for x in fills if x["won"] and x not in keep]
            saved = -pnl(dl)[0]
            missed = pnl(dw)[0]
            out[(bar, lat)] = {"kept": len(keep), "p": p, "s": s_, "saved": saved, "missed": missed}
            say(f"  pull under z {bar:.1f}, {lat:4} ms to land: dodges {len(dl)} of {len(lost)} losing fills (saves ${saved:,.0f}), "
                f"also skips {len(dw)} winners (${missed:,.0f} less profit); left: ${p:,.0f} = {100 * p / max(s_, 1e-9):+.2f} per $100")
    # how early did Binance warn before the losing fills?
    for bar in bars:
        w = sorted(next((back for back, z in x["path"] if z is not None and z < bar), -1) for x in lost)
        if w:
            say(f"  losing fills, first time the z was under {bar:.1f}: {sum(v < 0 for v in w)} never; others a median "
                f"{w[len(w) // 2]} ms before the fill")
    return out


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    lg = Log(d)
    b = Books(lg)
    b.add_window(1000, "U", "D")
    b.handle(json.dumps([{"event_type": "book", "asset_id": "U", "bids": [{"price": "0.48", "size": "10"}],
                          "asks": [{"price": "0.52", "size": "20"}]}]), r=1)
    b.handle(json.dumps({"event_type": "price_change", "price_changes": [
        {"asset_id": "U", "price": "0.51", "size": "5", "side": "SELL"},
        {"asset_id": "X", "price": "0.5", "size": "5", "side": "SELL"}]}), r=2)
    b.handle(json.dumps({"event_type": "price_change", "price_changes": [
        {"asset_id": "U", "price": "0.51", "size": "0", "side": "SELL"}]}), r=3)
    b.handle(json.dumps({"event_type": "last_trade_price", "asset_id": "U", "price": "0.52", "size": "3", "side": "BUY"}), r=4)
    lg.flush()
    rows = [json.loads(x) for x in open(lg.path())]
    asks = [x["ba"] for x in rows if x["k"] == "bk"]
    assert asks == [0.52, 0.51, 0.52], asks
    b.add_window(1000, "U", "D")
    b.handle(json.dumps([{"event_type": "book", "asset_id": "D", "bids": [{"price": "0.48", "size": "20"}],
                          "asks": [{"price": "0.52", "size": "10"}]}]), r=5)
    b.handle(json.dumps({"event_type": "price_change", "price_changes": [
        {"asset_id": "U", "price": "0.52", "size": "21", "side": "SELL"}]}), r=6)   # 20 -> 21 shares: a crumb
    lg.flush()
    assert sum(1 for x in map(json.loads, open(lg.path())) if x["k"] == "bk") == 3, "Down and crumbs aren't written"
    assert rows[-1]["k"] == "tr" and rows[-1]["p"] == 0.52
    mv = Mover(lg, "bn")
    for p in (100.0, 100.2, 100.6, 100.7):
        mv.see(p, 0)
    lg.flush()
    assert [x["p"] for x in map(json.loads, open(lg.path())) if x["k"] == "bn"] == [100.0, 100.6]
    assert list(parse_bn('{"e":"trade","p":"65000.1","T":5}')) == [(65000.1, 5)]
    assert list(parse_cb('{"type":"ticker","price":"65000","time":"2026-11-17T10:00:00.5Z"}'))[0][0] == 65000.0
    assert list(parse_cl('{"topic":"crypto_prices_chainlink","payload":{"symbol":"btc/usd","value":65001.5,"timestamp":7}}')) == [(65001.5, 7)]

    def fake(method, url, body=None, headers=None):
        assert "btc-updown-5m-1200" in url
        if "closed=true" in url:
            return [{"outcomes": '["Up","Down"]', "outcomePrices": '["0","1"]'}]
        return [{"outcomes": '["Up","Down"]', "clobTokenIds": '["tu","td"]', "conditionId": "0xc"}]
    assert window_tokens(1200, fake) == ("tu", "td", "0xc")
    assert window_result(1200, fake) is False
    # scoring: a planted jump with a stale offer that lasts 300 ms
    f = os.path.join(d, "s.jsonl")
    w = 1_800_000_000
    with open(f, "w") as fh:
        for s in range(-900, 300):
            p = 65000 + (5 if s % 2 else -5) + (60 if s >= 100 else 0)
            fh.write(json.dumps({"k": "bn", "r": (w + s) * 1000, "p": p}) + "\n")
        fh.write(json.dumps({"k": "bk", "r": w * 1000, "w": w, "o": "Up", "ba": 0.50, "as": 100}) + "\n")
        fh.write(json.dumps({"k": "bk", "r": (w + 100) * 1000 + 300, "w": w, "o": "Up", "ba": 0.90, "as": 100}) + "\n")
        fh.write(json.dumps({"k": "res", "w": w, "up_won": True}) + "\n")
    out = score([f], say=lambda *a: None)
    hit = [x for x in out if x["side"] == "Up"]
    assert out is not None
    assert hit and hit[0]["lasted"] == 300 and hit[0]["at"][0]["edge"] > 0.1 and hit[0]["at"][500]["ask"] == 0.90, hit
    # second test (25 Nov): new feeds, coins, Kalshi
    assert list(parse_bf('{"e":"aggTrade","p":"65000.5","T":9}')) == [(65000.5, 9)]
    assert list(parse_bs('{"event":"trade","channel":"live_trades_btcusd","data":{"price":65001,"microtimestamp":"1700000000123456"}}')) == [(65001.0, 1700000000123)]
    assert list(parse_kr('{"channel":"trade","type":"update","data":[{"symbol":"BTC/USD","price":65002.1,"timestamp":"2026-11-25T10:00:00.250Z"}]}'))[0] == (65002.1, _iso_ms("2026-11-25T10:00:00.250Z"))
    assert list(parse_kr('{"channel":"heartbeat"}')) == []
    assert list(parse_alt('{"stream":"ethusdt@trade","data":{"e":"trade","s":"ETHUSDT","p":"3000.5","T":11}}')) == [(3000.5, 11, "ETH")]
    ma = Mover(lg, "ax", "ETH")
    for p in (3000.0, 3000.01, 3000.03):
        ma.see(p, 0, r=10)
    lg.flush()
    assert [x["p"] for x in map(json.loads, open(lg.path())) if x["k"] == "ax"] == [3000.0, 3000.03]
    b.add_window(2000, "EU", "ED", "eth")
    b.handle(json.dumps([{"event_type": "book", "asset_id": "EU", "bids": [{"price": "0.4", "size": "5"}],
                          "asks": [{"price": "0.6", "size": "5"}]}]), r=7)
    lg.flush()
    assert [x for x in map(json.loads, open(lg.path())) if x["k"] == "bk"][-1]["c"] == "eth"
    assert k_top({"orderbook_fp": {"yes_dollars": [["0.9100", "50.00"], ["0.9300", "12.00"]], "no_dollars": [["0.0500", "7"]]}}) == (0.93, 12.0, 0.05, 7.0)
    assert k_top({"orderbook": {"yes": [[93, 4]], "no": None}}) == (0.93, 4.0, None, 0)
    kt = k_trade({"ticker": "KXBTC15M-X", "created_time": "2026-11-25T10:00:00.5Z", "yes_price_dollars": "0.9400", "count_fp": "3.00", "taker_side": "no"})
    assert kt["yp"] == 0.94 and kt["n"] == 3.0 and kt["tk"] == "no" and kt["e"] % 1000 == 500
    clock = [1_800_000_000.0]
    calls = []

    class FakeK:
        def get(self, path, params=None):
            calls.append(path)
            if path == "/markets":
                c0 = int(clock[0]) // 900 * 900 + 900
                return {"markets": [{"ticker": f"{params['series_ticker']}-{c0}", "open_time": _iso(c0 - 900),
                                     "close_time": _iso(c0), "floor_strike": 100.0}]}, 50
            if path.endswith("/orderbook"):
                return {"orderbook_fp": {"yes_dollars": [["0.9500", "10"]], "no_dollars": [["0.0400", "5"]]}}, 80
            if path == "/markets/trades":
                return {"trades": [{"created_time": _iso(clock[0] - 100), "yes_price_dollars": "0.95", "count_fp": "2",
                                    "taker_side": "no"}], "cursor": ""}, 60
            return {"market": {"result": "yes"}}, 40

    def _iso(t):
        return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat().replace("+00:00", "Z")
    kwt = KWatch(lg, FakeK(), clock=lambda: clock[0])
    kwt.step()
    first = len(calls)
    kwt.step()                                  # 10 s rule far from the close: no new book reads
    assert len(calls) == first and first == 2 * len(KSERIES), calls
    clock[0] += 900                             # next window: old ones go to "done", tape + result 60 s later
    kwt.step()
    clock[0] += 61
    kwt.step()
    lg.flush()
    lines = [json.loads(x) for x in open(lg.path())]
    assert sum(1 for x in lines if x["k"] == "kres") == len(KSERIES)
    assert sum(1 for x in lines if x["k"] == "kt") == len(KSERIES)
    assert sum(1 for x in lines if x["k"] == "kb") == 2 * len(KSERIES)     # written once per market (no change)
    assert all(m["close"] - clock[0] > 0 for m in kwt.cur.values())
    # kcancel: a 95c Yes bid with z falling to 0 during the last 15 s before a losing fill is dodged at a bar of 1
    f2 = os.path.join(d, "k.jsonl")
    o, c = 1_800_000_900, 1_800_001_800
    with open(f2, "w") as fh:
        fh.write(json.dumps({"k": "kw", "t": "KXBTC15M-T", "sr": "KXBTC15M", "open": o, "close": c, "strike": 100.0}) + "\n")
        for s_ in range(o - 400, c + 1):
            fill_t = c - 100
            p = 100.0 + (0.02 if s_ % 2 else -0.02) + (2.0 if o < s_ < fill_t - 10 else 0.0)
            fh.write(json.dumps({"k": "bn", "r": s_ * 1000, "p": p}) + "\n")
        fh.write(json.dumps({"k": "kt", "t": "KXBTC15M-T", "e": (c - 100) * 1000, "yp": 0.95, "n": 10, "tk": "no"}) + "\n")
        fh.write(json.dumps({"k": "kt", "t": "KXBTC15M-T", "e": (c - 300) * 1000, "yp": 0.95, "n": 10, "tk": "no"}) + "\n")
        fh.write(json.dumps({"k": "kres", "t": "KXBTC15M-T", "yes": False}) + "\n")
    kc = kcancel([f2], say=lambda *a: None)
    assert kc[(1.0, 250)]["saved"] > 9 and kc[(1.0, 250)]["kept"] == 1, kc[(1.0, 250)]
    assert kc[(1.0, 0)]["kept"] == 1
    src = open(__file__).read()
    for bad in ("post_order", "create_order", "private_key", "POLY_API_SECRET", "/portfolio", "KALSHI-ACCESS"):
        assert bad not in src.replace(f'"{bad}"', ""), f"listen only: {bad}"
    print("speedcheck selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "run":
        asyncio.run(run())
    elif cmd == "score":
        score(sys.argv[2:])
    elif cmd == "edge":
        # python3 quoter/speedcheck.py edge [btc|eth|sol] [--fee 0.05] [--skip-first 12] files...
        a, kw = sys.argv[2:], {}
        for flag, key in (("--fee", "fee"), ("--skip-first", "skip_first")):
            if flag in a:
                i = a.index(flag)
                kw[key] = float(a[i + 1])
                del a[i:i + 2]
        edge(a[1:], coin=a[0], **kw) if a and a[0] in ("eth", "sol", "btc") else edge(a, **kw)
    elif cmd == "lead":
        lead(sys.argv[2:])
    elif cmd == "kcancel":
        kcancel(sys.argv[2:])
    elif cmd == "upload":
        print(upload_all(Log(os.environ.get("SPEED_DIR", "~/speed-data")), os.environ.get("GITHUB_TOKEN")))
    else:
        selftest()
