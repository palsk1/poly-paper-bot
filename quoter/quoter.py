"""Paper combo quoter (Jan said "go", 2026-11-11). Runs on Jan's own server, never in GitHub Actions.

LISTEN ONLY. It connects to Polymarket's combo request feed as a quoter, prices every request from the live books of
its legs, writes down what it WOULD have quoted, and later sees the price the winning pro really traded at. It never
sends a quote: there is no code here that signs or sends anything, and it never sees a private key (only the CLOB API
key/secret/passphrase, which can't move money without a signature). Paper only (CLAUDE.md hard rules 1-2).

Files it writes (one JSON line each, in DATA_DIR, a new file every UTC day):
  {"k":"req", ...}    a combo request, with the legs, their books and our would-be quotes (one per rule)
  {"k":"trade", ...}  a trade broadcast: the price the winning maker really got
  {"k":"note", ...}   start, catalog refresh, errors, latency
Every hour the day files are uploaded to the GitHub release `quoter-data` (needs GITHUB_TOKEN with Contents
read/write on palsk1/poly-paper-bot only). `python3 combos.py qscore` scores them.

Run:  python3 quoter.py run        (normally via systemd, see quoter/README.md)
      python3 quoter.py selftest   (offline, no network)
      python3 quoter.py catalog    (prints how many combo legs it knows)
Env:  POLY_API_KEY, POLY_API_SECRET, POLY_API_PASSPHRASE, POLY_SIGNER, POLY_MAKER, POLY_SIG_TYPE (from make_creds.py),
      GITHUB_TOKEN (optional, for uploads), DATA_DIR (default ~/quoter-data)
"""
import asyncio
import datetime as dt
import gzip
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

WS = "wss://combos-rfq-gateway-quoter.polymarket.com/ws/rfq"
RFQ = "https://combos-rfq-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
REPO = "palsk1/poly-paper-bot"
TAG = "quoter-data"
UA = "poly-paper-bot quoter (paper research)"

# The rules, written down before the first live request (see backtest/PROTOCOL.md "combo_house").
# Each would-be quote = legs multiplied (live middle price) x (1 + markup). Only BUY requests (users buying the parlay).
RULES = {
    "main": {"markup": 0.05, "min_legs": 2, "max_legs": 4, "same_game": False, "min_fair": 0.0},
    "m3": {"markup": 0.03, "min_legs": 2, "max_legs": 4, "same_game": False, "min_fair": 0.0},
    "all5": {"markup": 0.05, "min_legs": 2, "max_legs": 50, "same_game": True, "min_fair": 0.0},
}
MAX_SPREAD = 0.10      # a leg whose book is wider than 10c (or empty) has no trustworthy middle price: no quote
MAX_QUOTE = 0.97
PAGE_PAUSE = 0.5     # seconds between catalog pages (Polymarket said 429 'too many requests' at full speed)


def now_ms():
    return int(time.time() * 1000)


def http(method, url, body=None, headers=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    for i in range(6):
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            return json.loads(raw.decode()) if raw else None
        except urllib.error.HTTPError as e:
            # 429 = "slow down", 5xx = their hiccup: wait (as long as they ask, else 2, 4, 8, 16, 32 s) and try again
            if (e.code == 429 or e.code >= 500) and i < 5:
                wait = fnum(e.headers.get("Retry-After"), None) if e.headers else None
                time.sleep(min(max(wait or 0, 2 ** (i + 1)), 120))
                continue
            raise


def fnum(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


# ---------------------------------------------------------------- catalog: combo leg -> market, CLOB token, game
class Catalog:
    """position id (a combo leg) -> {cond, oi, title, token, event, start, kind}. Refreshed every 10 minutes."""

    def __init__(self):
        self.legs = {}
        self.t = 0

    def refresh(self, fetch=http):
        legs, cur, markets = {}, None, []
        for _ in range(400):
            q = {"limit": 100}
            if cur:
                q["cursor"] = cur
            res = fetch("GET", f"{RFQ}/v1/rfq/combo-markets?" + urllib.parse.urlencode(q))
            markets += res.get("markets") or []
            cur = res.get("next_cursor")
            if not cur:
                break
            time.sleep(PAGE_PAUSE)
        gm = {}
        conds = [m["condition_id"] for m in markets if m.get("condition_id")]
        for i in range(0, len(conds), 50):
            q = urllib.parse.urlencode([("condition_ids", c) for c in conds[i:i + 50]] + [("limit", 100)])
            try:
                for g in fetch("GET", f"{GAMMA}/markets?{q}") or []:
                    gm[(g.get("conditionId") or "").lower()] = g
            except Exception as e:  # noqa: BLE001
                print("gamma batch failed:", e)
            time.sleep(PAGE_PAUSE)
        for m in markets:
            g = gm.get((m.get("condition_id") or "").lower()) or {}
            toks = g.get("clobTokenIds")
            if isinstance(toks, str):
                try:
                    toks = json.loads(toks)
                except ValueError:
                    toks = []
            evs = g.get("events") or [{}]
            for oi, pid in enumerate(m.get("position_ids") or []):
                legs[str(pid)] = {"cond": m.get("condition_id"), "oi": oi, "title": m.get("title"),
                                  "out": (m.get("outcomes") or [None, None])[oi] if oi < len(m.get("outcomes") or []) else None,
                                  "token": toks[oi] if toks and oi < len(toks) else None,
                                  "event": str(evs[0].get("id")) if evs and evs[0].get("id") else m.get("slug"),
                                  "start": g.get("gameStartTime"), "kind": g.get("sportsMarketType"),
                                  "tags": (m.get("tags") or [])[:4]}
        if legs:
            self.legs, self.t = legs, time.time()
        return len(markets), len(legs), sum(1 for v in legs.values() if v["token"])


# ---------------------------------------------------------------- pricing
def books(tokens, fetch=http):
    """{token: (best bid, best ask, bid size, ask size)} from one batch call."""
    out = {}
    res = fetch("POST", f"{CLOB}/books", [{"token_id": t} for t in tokens]) or []
    for b in res:
        bids = [(fnum(x.get("price"), 0), fnum(x.get("size"), 0)) for x in b.get("bids") or []]
        asks = [(fnum(x.get("price"), 1), fnum(x.get("size"), 0)) for x in b.get("asks") or []]
        bb = max(bids, default=(None, 0))
        ba = min(asks, default=(None, 0))
        out[b.get("asset_id")] = (bb[0], ba[0], bb[1], ba[1])
    return out


def price_request(legs, bk):
    """legs: catalog rows; bk: books. Returns dict with fair (mids multiplied), ask product, flags, or a skip reason."""
    fair, askp, mids = 1.0, 1.0, []
    for lg in legs:
        b = bk.get(lg.get("token"))
        if not b or b[0] is None or b[1] is None:
            return {"skip": "no book"}
        bid, ask = b[0], b[1]
        if ask - bid > MAX_SPREAD or ask <= bid:
            return {"skip": f"wide book {bid:.3f}/{ask:.3f}"}
        mid = (bid + ask) / 2
        if mid >= 0.985 or mid <= 0.015:
            return {"skip": "leg already decided"}
        mids.append(round(mid, 4))
        fair *= mid
        askp *= ask
    evs = [lg.get("event") for lg in legs]
    return {"fair": round(fair, 6), "askp": round(askp, 6), "mids": mids, "same_game": len(set(evs)) < len(evs)}


def would_quote(p, n_legs, direction):
    """Our would-be quote under every rule (None = this rule doesn't quote)."""
    out = {}
    for name, r in RULES.items():
        q = None
        if direction == "BUY" and "fair" in p and r["min_legs"] <= n_legs <= r["max_legs"] \
                and (r["same_game"] or not p["same_game"]) and p["fair"] >= r["min_fair"]:
            q = round(p["fair"] * (1 + r["markup"]), 6)
            if q >= MAX_QUOTE:
                q = None
        out[name] = q
    return out


# ---------------------------------------------------------------- log files + upload
class Log:
    def __init__(self, d):
        self.d = os.path.expanduser(d)
        os.makedirs(self.d, exist_ok=True)

    def path(self, day=None):
        return os.path.join(self.d, f"quoter-{day or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')}.jsonl")

    def put(self, obj):
        obj.setdefault("t", now_ms())
        with open(self.path(), "a") as f:
            f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def upload_all(log, token):
    """gzip every day file and put it on the release `quoter-data` (replacing the old copy)."""
    if not token:
        return "no GITHUB_TOKEN, kept local"
    h = {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"}
    try:
        rel = http("GET", f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", headers=h)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        rel = http("POST", f"https://api.github.com/repos/{REPO}/releases", {
            "tag_name": TAG, "name": "Paper combo quoter logs", "prerelease": True,
            "body": "What the paper combo quoter saw and would have quoted (quoter/quoter.py). Paper research data only."}, headers=h)
    have = {a["name"]: a["id"] for a in http("GET", f"https://api.github.com/repos/{REPO}/releases/{rel['id']}/assets?per_page=100", headers=h)}
    n = 0
    for fn in sorted(os.listdir(log.d)):
        if not fn.endswith(".jsonl"):
            continue
        src = os.path.join(log.d, fn)
        gz = src + ".gz"
        with open(src, "rb") as a, gzip.open(gz, "wb") as b:
            shutil.copyfileobj(a, b)
        name = fn + ".gz"
        if name in have:
            http("DELETE", f"https://api.github.com/repos/{REPO}/releases/assets/{have[name]}", headers=h)
        data = open(gz, "rb").read()
        req = urllib.request.Request(f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={name}",
                                     data=data, method="POST", headers={**h, "Content-Type": "application/gzip", "User-Agent": UA})
        urllib.request.urlopen(req, timeout=60).read()
        n += 1
    return f"uploaded {n} files"


# ---------------------------------------------------------------- the loop
def creds():
    need = ["POLY_API_KEY", "POLY_API_SECRET", "POLY_API_PASSPHRASE", "POLY_SIGNER", "POLY_MAKER", "POLY_SIG_TYPE"]
    miss = [k for k in need if not os.environ.get(k)]
    if miss:
        sys.exit(f"missing settings: {', '.join(miss)} (run make_creds.py, see quoter/README.md)")
    return {"type": "auth",
            "auth": {"apiKey": os.environ["POLY_API_KEY"], "secret": os.environ["POLY_API_SECRET"],
                     "passphrase": os.environ["POLY_API_PASSPHRASE"]},
            "identity": {"signer_address": os.environ["POLY_SIGNER"], "maker_address": os.environ["POLY_MAKER"],
                         "signature_type": int(os.environ["POLY_SIG_TYPE"])}}


async def handle_request(msg, cat, log, loop):
    t0 = now_ms()
    ids = [str(x) for x in msg.get("leg_position_ids") or []]
    legs = [cat.legs.get(i) for i in ids]
    row = {"k": "req", "rfq": msg.get("rfq_id"), "cid": msg.get("condition_id"), "dir": msg.get("direction"),
           "side": msg.get("side"), "size": msg.get("requested_size"), "deadline": msg.get("submission_deadline"),
           "legs": ids, "seen": t0}
    if any(lg is None or not lg.get("token") for lg in legs):
        row["skip"] = "leg not in catalog"
        log.put(row)
        return
    try:
        bk = await loop.run_in_executor(None, books, [lg["token"] for lg in legs])
    except Exception as e:  # noqa: BLE001
        row["skip"] = f"books failed: {e}"
        log.put(row)
        return
    p = price_request(legs, bk)
    row.update(p)
    row["leg_info"] = [{"title": lg["title"], "out": lg["out"], "event": lg["event"], "kind": lg["kind"],
                        "start": lg["start"], "token": lg["token"]} for lg in legs]
    row["quotes"] = would_quote(p, len(legs), msg.get("direction"))
    row["priced"] = now_ms()
    row["in_time"] = bool(msg.get("submission_deadline")) and row["priced"] <= int(msg["submission_deadline"])
    log.put(row)


async def run():
    import websockets   # pip install websockets
    log = Log(os.environ.get("DATA_DIR", "~/quoter-data"))
    cat = Catalog()
    loop = asyncio.get_running_loop()
    log.put({"k": "note", "what": "start", "rules": RULES})

    async def catalog_loop():
        # in the background, so a slow or refused catalog never stops us listening; legs not known yet are logged as such
        while True:
            try:
                n = await loop.run_in_executor(None, cat.refresh)
                log.put({"k": "note", "what": "catalog", "catalog": n})
                print(dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "catalog (markets, legs, legs with prices):", n, flush=True)
                await asyncio.sleep(600)
            except Exception as e:  # noqa: BLE001
                log.put({"k": "note", "what": "catalog failed", "err": str(e)})
                print("catalog failed, trying again in 2 min:", e, flush=True)
                await asyncio.sleep(120)

    asyncio.create_task(catalog_loop())
    last_up = time.time()
    auth = creds()
    tried = set()
    backoff = 2
    while True:
        try:
            async with websockets.connect(WS, ping_interval=None, max_size=2 ** 22) as ws:
                await ws.send(json.dumps(auth))
                ok = json.loads(await asyncio.wait_for(ws.recv(), 30))
                log.put({"k": "note", "what": "auth", "ok": ok.get("success"), "role": ok.get("role"), "err": ok.get("error")})
                print("auth:", ok, flush=True)
                if not ok.get("success"):
                    # wrong wallet type is the usual cause: try the next one (0 plain, 1 email login, 2 browser wallet, 3 deposit)
                    tried.add(auth["identity"]["signature_type"])
                    left = [x for x in (3, 2, 1, 0) if x not in tried]
                    if left:
                        auth["identity"]["signature_type"] = left[0]
                        continue
                    tried.clear()
                    await asyncio.sleep(300)
                    continue
                backoff = 2
                counts = {"req": 0, "trade": 0, "other": 0}
                last_note = time.time()
                while True:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), 60)
                    except asyncio.TimeoutError:
                        raw = None
                    if raw:
                        msg = json.loads(raw)
                        typ = msg.get("type")
                        if typ == "RFQ_REQUEST":
                            counts["req"] += 1
                            if counts["req"] <= 3:
                                print("request heard:", msg.get("rfq_id"), len(msg.get("leg_position_ids") or []), "legs", flush=True)
                            asyncio.create_task(handle_request(msg, cat, log, loop))
                        elif typ == "RFQ_TRADE":
                            counts["trade"] += 1
                            log.put({"k": "trade", "rfq": msg.get("rfq_id"), "cid": msg.get("condition_id"),
                                     "dir": msg.get("direction"), "side": msg.get("side"), "price": msg.get("price_e6"),
                                     "size": msg.get("size_e6"), "at": msg.get("executed_at"), "legs": msg.get("leg_position_ids")})
                        elif str(typ).lower() == "ping":
                            await ws.send(json.dumps({**msg, "type": "pong"}))   # if they ping in text, answer in text
                        else:
                            counts["other"] += 1
                            log.put({"k": "note", "what": "msg", "msg": msg})
                    if time.time() - last_note > 600:
                        last_note = time.time()
                        log.put({"k": "note", "what": "counts", "counts": counts})
                        print(dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "heard so far:", counts, flush=True)
                    if time.time() - last_up > 3600:
                        last_up = time.time()
                        try:
                            r = await loop.run_in_executor(None, upload_all, log, os.environ.get("GITHUB_TOKEN"))
                            print("upload:", r, flush=True)
                        except Exception as e:  # noqa: BLE001
                            log.put({"k": "note", "what": "upload failed", "err": str(e)})
        except Exception as e:  # noqa: BLE001
            log.put({"k": "note", "what": "disconnected", "err": f"{type(e).__name__}: {e}"})
            print("disconnected:", e, flush=True)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 120)


# ---------------------------------------------------------------- offline check
def selftest():
    import tempfile
    cat = Catalog()

    def fake(method, url, body=None, headers=None):
        if "combo-markets" in url:
            return {"markets": [
                {"condition_id": "0xa", "position_ids": ["1", "2"], "title": "A vs B", "outcomes": ["A", "B"], "slug": "a-b"},
                {"condition_id": "0xb", "position_ids": ["3", "4"], "title": "C vs D", "outcomes": ["C", "D"], "slug": "c-d"},
                {"condition_id": "0xc", "position_ids": ["5", "6"], "title": "A vs B O/U", "outcomes": ["Over", "Under"], "slug": "a-b-ou"}],
                "next_cursor": None}
        if "gamma" in url:
            return [{"conditionId": "0xa", "clobTokenIds": '["ta","tb"]', "events": [{"id": 1}]},
                    {"conditionId": "0xb", "clobTokenIds": '["tc","td"]', "events": [{"id": 2}]},
                    {"conditionId": "0xc", "clobTokenIds": '["to","tu"]', "events": [{"id": 1}]}]
        if url.endswith("/books"):
            px = {"ta": (0.59, 0.61), "tc": (0.49, 0.51), "to": (0.40, 0.60), "tb": (0.39, 0.41)}
            return [{"asset_id": t["token_id"], "bids": [{"price": str(px[t["token_id"]][0]), "size": "100"}],
                     "asks": [{"price": str(px[t["token_id"]][1]), "size": "100"}]} for t in body if t["token_id"] in px]
        raise AssertionError(url)

    assert cat.refresh(fake) == (3, 6, 6)
    a, c, o = cat.legs["1"], cat.legs["3"], cat.legs["5"]
    assert a["token"] == "ta" and cat.legs["2"]["token"] == "tb" and a["event"] == "1"
    p = price_request([a, c], books(["ta", "tc"], fake))
    assert abs(p["fair"] - 0.30) < 1e-9 and not p["same_game"], p
    q = would_quote(p, 2, "BUY")
    assert abs(q["main"] - 0.315) < 1e-9 and abs(q["m3"] - 0.309) < 1e-9 and q["all5"] == q["main"], q
    assert would_quote(p, 2, "SELL") == {k: None for k in RULES}
    p2 = price_request([a, o], books(["ta", "to"], fake))       # 20c wide book: no trustworthy price
    assert p2.get("skip", "").startswith("wide"), p2
    p3 = price_request([a, cat.legs["2"]], books(["ta", "tb"], fake))   # same game: main skips, all5 quotes
    q3 = would_quote(p3, 2, "BUY")
    assert p3["same_game"] and q3["main"] is None and q3["all5"] is not None, (p3, q3)
    assert would_quote(p, 5, "BUY")["main"] is None and would_quote(p, 5, "BUY")["all5"] is not None
    d = tempfile.mkdtemp()
    lg = Log(d)
    lg.put({"k": "note"})
    assert os.path.exists(lg.path())
    assert "kept local" in upload_all(lg, None)
    src = open(__file__).read()
    assert "RFQ_QUOTE" not in src.replace('"RFQ_QUOTE" not in', ""), "listen only: never send quotes"
    print("quoter selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "run":
        asyncio.run(run())
    elif cmd == "catalog":
        print(Catalog().refresh())
    else:
        selftest()
