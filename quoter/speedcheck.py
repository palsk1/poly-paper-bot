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
  {"k":"ping", "r", "what", "ms", "off"}            round trip to Polymarket's order server / Binance, server clock gap
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

    def path(self, day=None):
        return os.path.join(self.d, f"speed-{day or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')}.jsonl")

    def put(self, obj):
        obj.setdefault("r", now_ms())
        day = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
        if day != self.day:
            if self.fh:
                self.fh.close()
            self.fh, self.day = open(self.path(day), "a", buffering=1 << 16), day
        self.fh.write(json.dumps(obj, separators=(",", ":")) + "\n")

    def flush(self):
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

    def __init__(self, log, kind):
        self.log, self.kind, self.last, self.last_r = log, kind, None, 0

    def see(self, p, e):
        r = now_ms()
        if self.last is None or abs(p - self.last) >= MOVE or r - self.last_r >= 1000:
            self.last, self.last_r = p, r
            self.log.put({"k": self.kind, "r": r, "e": e, "p": p})


async def feed(name, url, sub, parse, log, ws_lib):
    mv = Mover(log, name)
    backoff = 2
    while True:
        try:
            async with ws_lib.connect(url, ping_interval=20, max_size=2 ** 22) as ws:
                if sub:
                    await ws.send(json.dumps(sub))
                backoff = 2
                async for raw in ws:
                    for p, e in parse(raw):
                        mv.see(p, e)
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


# ---------------------------------------------------------------- Polymarket 5-minute windows
class Books:
    """Top of book per token from the market feed ("book" snapshots + "price_change" level updates)."""

    def __init__(self, log):
        self.log = log
        self.tok = {}        # token -> (window start, "Up"/"Down")
        self.lv = {}         # token -> {"b": {price: size}, "a": {price: size}}
        self.top = {}        # token -> last written (bb, bs, ba, as)

    def add_window(self, w, up, down):
        self.tok[up], self.tok[down] = (w, "Up"), (w, "Down")
        for t in (up, down):
            self.lv.setdefault(t, {"b": {}, "a": {}})

    def drop_before(self, w):
        for t, (ws, _) in list(self.tok.items()):
            if ws < w:
                self.tok.pop(t, None)
                self.lv.pop(t, None)
                self.top.pop(t, None)

    def _emit(self, t, r):
        lv = self.lv.get(t)
        if not lv or t not in self.tok:
            return
        w, o = self.tok[t]
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
            self.log.put({"k": "bk", "r": r, "w": w, "o": o, "bb": top[0], "bs": top[1], "ba": top[2], "as": top[3]})

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
                    w, o = self.tok[t]
                    self.log.put({"k": "tr", "r": r, "w": w, "o": o, "p": float(m.get("price") or 0),
                                  "s": float(m.get("size") or 0), "sd": m.get("side"), "e": m.get("timestamp")})


def window_tokens(w, fetch=http):
    """(up token, down token, condition id) of the window starting at w, or None if Gamma doesn't list it yet."""
    rows = fetch("GET", f"{GAMMA}/markets?slug=btc-updown-5m-{w}")
    for m in rows or []:
        names = json.loads(m.get("outcomes") or "[]")
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if len(names) == 2 and len(toks) == 2:
            i = [str(n).lower() for n in names].index("up")
            return toks[i], toks[1 - i], m.get("conditionId")
    return None


def window_result(w, fetch=http):
    rows = fetch("GET", f"{GAMMA}/markets?slug=btc-updown-5m-{w}&closed=true")
    for m in rows or []:
        names = [str(n).lower() for n in json.loads(m.get("outcomes") or "[]")]
        prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        if len(prices) == 2 and sorted(prices) == [0.0, 1.0] and "up" in names:
            return prices[names.index("up")] == 1.0
    return None


async def market_loop(log, ws_lib, loop):
    books = Books(log)
    pending = {}     # window start -> tries left for its result
    while True:
        now = int(time.time())
        w0 = now // WIN * WIN
        subs = []
        for w in (w0, w0 + WIN):
            try:
                got = await loop.run_in_executor(None, window_tokens, w)
            except Exception as ex:  # noqa: BLE001
                got = None
                log.put({"k": "note", "what": "gamma failed", "err": str(ex)[:200]})
            if got:
                books.add_window(w, got[0], got[1])
                log.put({"k": "win", "w": w, "up": got[0], "down": got[1], "cid": got[2]})
                subs += [got[0], got[1]]
                pending.setdefault(w, 30)
        books.drop_before(w0)
        # results of finished windows (Gamma marks them a minute or two after the end)
        for w in sorted(pending):
            if w + WIN + 90 > now:
                continue
            try:
                res = await loop.run_in_executor(None, window_result, w)
            except Exception:  # noqa: BLE001
                res = None
            if res is not None:
                log.put({"k": "res", "w": w, "up_won": res})
                pending.pop(w)
            else:
                pending[w] -= 1
                if pending[w] <= 0:
                    pending.pop(w)
        until = w0 + WIN - time.time() + 0.5      # reconnect with the next pair of windows just after the turn
        if not subs:
            await asyncio.sleep(10)
            continue
        try:
            async with ws_lib.connect(PM_WS, ping_interval=None, max_size=2 ** 23) as ws:
                await ws.send(json.dumps({"assets_ids": subs, "type": "market"}))
                end = time.time() + until
                last_ping = time.time()
                while time.time() < end:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=max(0.1, min(5, end - time.time())))
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


def ping_once(log):
    for what, url, key in (("clob", f"{CLOB}/time", None), ("binance", "https://api.binance.com/api/v3/time", "serverTime")):
        try:
            t0 = now_ms()
            res = http("GET", url, timeout=10)
            t1 = now_ms()
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


def score(paths, src=None, jump=0.03, react=(0, 50, 100, 200, 500, 1000, 2000), say=print):
    """For every Bitcoin jump (the fair price of a side rises `jump`+ within 2 s, as heard by this server), how much
    of Polymarket's sell offers on that side were still at a price below the new fair price minus the fee, `react` ms
    after we heard it? And what would buying them have paid at the window's result?"""
    import bisect
    import collections
    import statistics
    px, books, res, pings = collections.defaultdict(list), collections.defaultdict(list), {}, collections.defaultdict(list)
    for o in read_lines(paths):
        k = o.get("k")
        if k in ("bn", "cb", "cl"):
            px[k].append((o["r"], o["p"]))
        elif k == "bk" and o.get("o") == "Up":
            books[(o["w"], "Up")].append((o["r"], o.get("ba"), o.get("as") or 0))
            bb = o.get("bb")
            books[(o["w"], "Down")].append((o["r"], round(1 - bb, 4) if bb is not None else None, o.get("bs") or 0))
        elif k == "res":
            res[o["w"]] = o["up_won"]
        elif k == "ping":
            pings[o["what"]].append(o["ms"])
    say("Bitcoin prices heard:", {k: len(v) for k, v in px.items()})
    src = src or max(("bn", "cb", "cl"), key=lambda k: (len(px[k]) > 1000, k == "bn", len(px[k])))
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
                fee = 0.07 * ask * (1 - ask)
                row["at"][d] = {"ask": ask, "size": size, "edge": fair - ask - fee}
            j = bisect.bisect_right(bt, r) - 1
            if j >= 0 and bk[j][1] is not None and fair - bk[j][1] - 0.07 * bk[j][1] * (1 - bk[j][1]) > 0.01:
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
        fee = sum(0.07 * x["at"][d]["ask"] * (1 - x["at"][d]["ask"]) * x["at"][d]["size"] for x in known)
        say(f"  {d:>5} ms after we heard it: {len(rows)} jumps still had an old-price sell offer 1c+ under fair after fees "
            f"(${c:,.0f} on offer); buying all of it: {'no results yet' if not ck else f'{100 * (p - ck - fee) / ck:+.2f} per $100'}")
    la = sorted(x["lasted"] for x in out if x.get("lasted") is not None)
    if la:
        say(f"  old-price offers (1c+ under fair) still up when we heard the jump: {len(la)}; they lasted a median "
            f"{la[len(la) // 2]} ms after that, 1 in 4 under {la[len(la) // 4]} ms")
    return out


def edge(paths, srcs=("bn", "cb"), band=(0.40, 0.95), cap=25.0, delays=(0, 100, 200, 500, 1000), say=print):
    """After each jump: buy the jumped-toward side at the best ask seen `d` ms after we heard it, up to $cap, ask in
    `band`, taker fee included, held to the window's result. Luck range by resampling whole windows (jumps inside one
    window move together). First run 18 Nov (20 h): Binance at 100 ms +$5.31 per $100, range +2.3..+8.3,
    falling to about $0 at 1 s. The 40-95c band was picked after looking."""
    import collections
    import random
    for src in srcs:
        out = score(paths, src=src, say=lambda *a, **k: None) or []
        for d in delays:
            rows = [x for x in out if x["won"] is not None and d in x["at"] and band[0] <= x["at"][d]["ask"] < band[1]]
            byw = collections.defaultdict(lambda: [0.0, 0.0])
            for x in rows:
                a = x["at"][d]["ask"]
                f = 0.07 * a * (1 - a)
                sh = min(x["at"][d]["size"], cap / a)
                byw[x["w"]][0] += sh * (x["won"] - a - f)
                byw[x["w"]][1] += sh * (a + f)
            ws = list(byw.values())
            if not ws:
                continue
            p, s = sum(v[0] for v in ws), sum(v[1] for v in ws)
            rnd = random.Random(2)
            bs = sorted(100 * sum(v[0] for v in smp) / max(1e-9, sum(v[1] for v in smp))
                        for smp in ([ws[rnd.randrange(len(ws))] for _ in ws] for _ in range(500)))
            say(f"{src} {d:5} ms, asks {band[0]:.2f}-{band[1]:.2f}: {len(rows)} jumps in {len(ws)} windows, ${s:,.0f} bought, "
                f"P&L ${p:,.0f} = {100 * p / s:+.2f} per $100, luck range {bs[25]:+.1f} to {bs[475]:+.1f}")


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
    src = open(__file__).read()
    for bad in ("post_order", "create_order", "private_key", "POLY_API_SECRET"):
        assert bad not in src.replace(f'"{bad}"', ""), f"listen only: {bad}"
    print("speedcheck selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "run":
        asyncio.run(run())
    elif cmd == "score":
        score(sys.argv[2:])
    elif cmd == "edge":
        edge(sys.argv[2:])
    elif cmd == "upload":
        print(upload_all(Log(os.environ.get("SPEED_DIR", "~/speed-data")), os.environ.get("GITHUB_TOKEN")))
    else:
        selftest()
