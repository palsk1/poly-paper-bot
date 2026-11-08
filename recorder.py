#!/usr/bin/env python3
"""Market data recorder: saves live order books, trades and spot prices so later backtests can
replay real books instead of guessing slippage (Jan's ask, 2026-11-08, after the burnt.beans post:
"record live data for a few months, then test strategies against it").

Records only. Never trades, never touches state/.

What it saves (one gzipped JSON-lines file per UTC hour, uploaded to a GitHub release per day,
tag data-YYYYMMDD, so the repo itself stays small):
  every minute   fast set: every Kalshi and Polymarket market that closes within the next
                 `fast_hours` hours (15-min / hourly crypto, commodities, weather, ...),
                 top `levels` of each book; Binance spot prices for the crypto coins
  every 5 min    wide set: the Polymarket books of every open position of every track,
                 plus the reviewed Kalshi arb tickers; Polymarket trades of the fast set
  every minute   the Kalshi public trade tape for the tickers above
A book is written only when it changed since the last write (and in full at the start of each
file, so every hour file stands on its own).

Line kinds ("k"): meta, kbook, pbook, ktrade, ptrade, spot, err.  Prices in dollars (0-1).
  kbook: {"tk": ticker, "yb": [[p, size], ...] YES bids, "nb": NO bids, "cl": close_time}
  pbook: {"tok": yes token, "cid": condition id, "b": bids, "a": asks, "end": end date}
  meta:  the markets in each set (titles, slugs, tickers), written when a set is refreshed

Usage: python3 recorder.py loop [minutes]   (the recorder workflow)
       python3 recorder.py once              (one fast + wide pass, prints a summary, no upload)
"""
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

import bot
from bot import CLOB, DATA, GAMMA, KALSHI, fnum, http_json, envelope_rows

CFG = bot.CFG.get("recorder", {})
FAST_HOURS = CFG.get("fast_hours", 3)
FAST_MAX_KALSHI = CFG.get("fast_max_kalshi", 300)
FAST_MAX_POLY = CFG.get("fast_max_poly", 300)
LEVELS = CFG.get("levels", 15)
WIDE_EVERY = CFG.get("wide_every_min", 5)
REFRESH_EVERY = CFG.get("refresh_every_min", 15)
SPOT = CFG.get("spot_symbols", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "PAXGUSDT"])
OUT_DIR = "rec_out"


def ts():
    return int(time.time())


def iso_z(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def post_json(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"User-Agent": bot.UA, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"POST {url}: {last}")


def lv(rows, desc):
    out = sorted(((fnum(p), fnum(s)) for p, s in rows if fnum(s) > 0), key=lambda x: -x[0] if desc else x[0])
    return [[round(p, 4), round(s, 2)] for p, s in out[:LEVELS]]


# ---------- picking markets ----------

def kalshi_fast():
    """Open Kalshi markets closing within FAST_HOURS, busiest first."""
    t, out, cursor = ts(), [], None
    for _ in range(20):
        params = {"status": "open", "min_close_ts": t, "max_close_ts": t + FAST_HOURS * 3600, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        res = http_json(f"{KALSHI}/markets", params)
        out += [m for m in res.get("markets") or [] if isinstance(m, dict)]
        cursor = res.get("cursor")
        if not cursor:
            break
    vol = lambda m: fnum(m.get("volume_24h_fp") or m.get("volume_24h"), 0)
    # 15-minute markets first (they're the point), then the busiest of the rest
    out.sort(key=lambda m: ("15M" not in str(m.get("event_ticker")), -vol(m)))
    out = [m for m in out if not str(m.get("ticker", "")).startswith("KXMVE")]  # multi-leg combos
    return [{"tk": m.get("ticker"), "ev": m.get("event_ticker"), "t": m.get("title"), "st": m.get("yes_sub_title"),
             "cl": m.get("close_time"), "v24": vol(m)} for m in out[:FAST_MAX_KALSHI] if m.get("ticker")]


def poly_fast():
    """Open Polymarket markets ending within FAST_HOURS, busiest first, sports left out (they'd fill the list)."""
    now = dt.datetime.now(dt.timezone.utc)
    end = now + dt.timedelta(hours=FAST_HOURS)
    out, off = [], 0
    for _ in range(FAST_MAX_POLY // 100 + 3):  # busiest first; gamma refuses offsets past ~2000
        rows = envelope_rows(http_json(f"{GAMMA}/markets", {
            "closed": "false", "active": "true", "limit": 100, "offset": off,
            "order": "volume24hr", "ascending": "false",
            "end_date_min": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "end_date_max": end.strftime("%Y-%m-%dT%H:%M:%SZ")}),
            "markets", "data")
        out += [m for m in rows if isinstance(m, dict)]
        if len(rows) < 100:
            break
        off += 100
    res = []
    for m in out:
        toks = bot.market_tokens(m)
        if len(toks) != 2 or m.get("acceptingOrders") is False or bot.is_sports(m):
            continue
        res.append({"tok": toks[0], "cid": m.get("conditionId"), "slug": m.get("slug"), "q": m.get("question"),
                    "end": m.get("endDate"), "v24": fnum(m.get("volume24hr"), 0)})
    res.sort(key=lambda x: x["v24"], reverse=True)
    return res[:FAST_MAX_POLY]


def git_state(name, default):
    """Latest state/<name> from main (the watch run keeps updating it while we record)."""
    try:
        subprocess.run(["git", "fetch", "-q", "origin", "main"], timeout=60, check=False)
        txt = subprocess.run(["git", "show", f"origin/main:{name}"], capture_output=True, text=True, timeout=60).stdout
        return json.loads(txt) if txt.strip() else default
    except Exception as e:
        print(f"git_state {name}: {e}")
        try:
            return json.load(open(name))
        except Exception:
            return default


def wide_sets():
    """Polymarket tokens of every open position in every track, plus the approved Kalshi arb tickers."""
    tracks = git_state("state/tracks.json", {})
    toks = {}
    for name, tr in tracks.items():
        for tok, p in (tr.get("positions") or {}).items():
            if isinstance(p, dict) and str(tok).isdigit() and len(str(tok)) > 20:
                toks.setdefault(tok, {"tok": tok, "slug": p.get("slug"), "q": p.get("title"), "o": p.get("outcome")})
    pairs = git_state("arb_pairs.json", {})
    ktk = sorted({p.get("kalshi") for p in pairs.get("approved") or [] if p.get("kalshi")})
    return list(toks.values()), [{"tk": t} for t in ktk]


# ---------- fetching ----------

def kalshi_book(tk):
    res = http_json(f"{KALSHI}/markets/{tk}/orderbook", None, retries=2)
    ob = (res.get("orderbook_fp") or res.get("orderbook") or {}) if isinstance(res, dict) else {}

    def side(*keys):
        for k in keys:
            if ob.get(k):
                return [(fnum(a[0]) / (100 if fnum(a[0]) > 1 else 1), a[1]) for a in ob[k]
                        if isinstance(a, (list, tuple)) and len(a) >= 2]
        return []
    return {"yb": lv(side("yes_dollars", "yes"), True), "nb": lv(side("no_dollars", "no"), True)}


def poly_books(tokens):
    """{token: {"b": bids, "a": asks}} via the batch /books endpoint, 100 per call."""
    out = {}
    for i in range(0, len(tokens), 100):
        chunk = tokens[i:i + 100]
        try:
            res = post_json(f"{CLOB}/books", [{"token_id": t} for t in chunk])
        except Exception as e:
            print(f"/books failed ({e}); falling back to one by one")
            res = []
            for t in chunk:
                try:
                    res.append({**http_json(f"{CLOB}/book", {"token_id": t}, retries=2), "asset_id": t})
                except Exception:
                    pass
        for b in res if isinstance(res, list) else []:
            tok = b.get("asset_id")
            if tok:
                out[tok] = {"b": lv([(x.get("price"), x.get("size")) for x in b.get("bids") or []], True),
                            "a": lv([(x.get("price"), x.get("size")) for x in b.get("asks") or []], False)}
    return out


def kalshi_trades(since, tickers):
    """Kalshi public tape since `since` (anonymous), only for tickers we record."""
    out, cursor = [], None
    for _ in range(30):
        params = {"min_ts": since, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        res = http_json(f"{KALSHI}/markets/trades", params, retries=2)
        rows = res.get("trades") or []
        out += [r for r in rows if r.get("ticker") in tickers]
        cursor = res.get("cursor")
        if not cursor or not rows:
            break
    else:
        out.append({"capped": True})
    return out


def poly_trades(cid):
    res = http_json(f"{DATA}/v2/trades", {"condition_id": cid, "limit": 500}, retries=2)
    return envelope_rows(res, "data", "trades")


def spot():
    res = http_json("https://data-api.binance.vision/api/v3/ticker/price", {"symbols": json.dumps(SPOT, separators=(",", ":"))})
    return {r["symbol"]: fnum(r["price"]) for r in res if isinstance(r, dict) and "symbol" in r}


# ---------- writing / uploading ----------

class Writer:
    def __init__(self, upload=True):
        self.upload, self.hour, self.f, self.path, self.last = upload, None, None, None, {}
        os.makedirs(OUT_DIR, exist_ok=True)

    def roll(self, t):
        h = time.strftime("%Y%m%d-%H", time.gmtime(t))
        if h == self.hour:
            return
        self.close()
        self.hour, self.last = h, {}
        self.path = f"{OUT_DIR}/rec-{h}.jsonl.gz"
        self.f = gzip.open(self.path, "at", compresslevel=9)

    def put(self, kind, t, obj, key=None):
        """Write a line; with `key`, only when the content changed since the last write this hour."""
        if key is not None:
            h = hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()
            if self.last.get(key) == h:
                return False
            self.last[key] = h
        self.f.write(json.dumps({"k": kind, "t": t, **obj}, separators=(",", ":")) + "\n")
        return True

    def close(self):
        if self.f:
            self.f.close()
            self.f = None
            if self.upload:
                upload(self.path)

    def flush(self):
        if self.f:
            self.f.flush()


def upload(path):
    day = os.path.basename(path)[4:12]
    tag = f"data-{day}"
    env = {**os.environ}
    ok = subprocess.run(["gh", "release", "view", tag], capture_output=True, env=env).returncode == 0
    if not ok:
        subprocess.run(["gh", "release", "create", tag, "--prerelease", "--title", f"Market data {day}",
                        "--notes", "Recorded order books, trades and spot prices (recorder.py). Paper research data only."],
                       env=env, check=False)
    for i in range(4):
        if subprocess.run(["gh", "release", "upload", tag, path, "--clobber"], env=env).returncode == 0:
            print(f"uploaded {path} to {tag} ({os.path.getsize(path) / 1e6:.1f} MB)")
            return True
        time.sleep(10 * (i + 1))
    print(f"UPLOAD FAILED for {path}")
    return False


# ---------- the loop ----------

def run(minutes, upload_files=True):
    w = Writer(upload_files)
    start = ts()
    kf = pf = kw = pw = []
    last_refresh = last_wide_refresh = -10 ** 9
    k_since = start - 60
    p_seen = set()
    n = 0
    stats = {"kbook": 0, "pbook": 0, "ktrade": 0, "ptrade": 0, "err": 0}
    pool = cf.ThreadPoolExecutor(8)
    kpool = cf.ThreadPoolExecutor(CFG.get("kalshi_threads", 4))  # Kalshi answers 429 above ~4 at once
    while ts() - start < minutes * 60:
        t = ts()
        w.roll(t)
        fresh_file = not w.last

        def err(where, e):
            stats["err"] += 1
            w.put("err", t, {"where": where, "e": str(e)[:300]})
            print(f"{where}: {e}")

        if t - last_refresh >= REFRESH_EVERY * 60 or fresh_file:
            try:
                kf = kalshi_fast()
            except Exception as e:
                err("kalshi_fast", e)
            try:
                pf = poly_fast()
            except Exception as e:
                err("poly_fast", e)
            w.put("meta", t, {"set": "fast", "kalshi": kf, "poly": pf})
            last_refresh = t
        if t - last_wide_refresh >= 60 * 60 or fresh_file:
            try:
                pw, kw = wide_sets()
            except Exception as e:
                err("wide_sets", e)
            w.put("meta", t, {"set": "wide", "kalshi": kw, "poly": pw})
            last_wide_refresh = t
        wide = n % WIDE_EVERY == 0

        # Kalshi books
        ktk = [m["tk"] for m in kf] + ([m["tk"] for m in kw] if wide else [])
        futs = {kpool.submit(kalshi_book, tk): tk for tk in dict.fromkeys(ktk)}
        for fu in cf.as_completed(futs):
            tk = futs[fu]
            try:
                if w.put("kbook", t, {"tk": tk, **fu.result()}, key=("k", tk)):
                    stats["kbook"] += 1
            except Exception as e:
                err(f"kbook {tk}", e)

        # Polymarket books
        toks = [m["tok"] for m in pf] + ([m["tok"] for m in pw] if wide else [])
        try:
            for tok, b in poly_books(list(dict.fromkeys(toks))).items():
                if w.put("pbook", t, {"tok": tok, **b}, key=("p", tok)):
                    stats["pbook"] += 1
        except Exception as e:
            err("pbooks", e)

        # Kalshi tape
        try:
            rows = kalshi_trades(k_since, set(m["tk"] for m in kf) | set(m["tk"] for m in kw))
            for r in rows:
                w.put("ktrade", t, r)
            stats["ktrade"] += len(rows)
            k_since = t
        except Exception as e:
            err("ktrades", e)

        # Polymarket tape for the fast set, every WIDE_EVERY minutes
        if wide and pf:
            futs = {pool.submit(poly_trades, m["cid"]): m["cid"] for m in pf if m.get("cid")}
            for fu in cf.as_completed(futs):
                try:
                    for r in fu.result():
                        key = (r.get("transactionHash"), r.get("asset"), r.get("size"), r.get("price"), r.get("side"))
                        if key in p_seen:
                            continue
                        p_seen.add(key)
                        w.put("ptrade", t, {"cid": futs[fu], **r})
                        stats["ptrade"] += 1
                except Exception as e:
                    err(f"ptrades {futs[fu][:12]}", e)
            if len(p_seen) > 500_000:
                p_seen = set()

        try:
            w.put("spot", t, {"px": spot()})
        except Exception as e:
            err("spot", e)

        w.flush()
        n += 1
        took = ts() - t
        if n % 10 == 1:
            print(f"{iso_z(t)} pass {n}: {len(kf)}+{len(kw)} kalshi, {len(pf)}+{len(pw)} poly, took {took}s, {stats}")
        nxt = t - t % 60 + 60
        if minutes * 60 - (ts() - start) < 5:
            break
        time.sleep(max(1, nxt - ts()))
    w.close()
    pool.shutdown(wait=False)
    kpool.shutdown(wait=False)
    print(f"done after {n} passes: {stats}")
    return stats


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "once"
    if cmd == "loop":
        run(float(sys.argv[2]) if len(sys.argv) > 2 else 340)
    elif cmd == "once":
        import collections
        kf, pf = kalshi_fast(), poly_fast()
        print("kalshi fast series:", collections.Counter(str(m["ev"]).rsplit("-", 1)[0] for m in kf).most_common(40))
        print("poly fast sample:", [m["q"][:60] for m in pf[:40]], len(pf))
        st = run(float(sys.argv[2]) if len(sys.argv) > 2 else 0.5, upload_files=False)
        for p in sorted(os.listdir(OUT_DIR)):
            fp = f"{OUT_DIR}/{p}"
            kinds = {}
            with gzip.open(fp, "rt") as f:
                for line in f:
                    k = json.loads(line)["k"]
                    kinds[k] = kinds.get(k, 0) + 1
            print(fp, f"{os.path.getsize(fp) / 1e3:.0f} kB", kinds)
            with gzip.open(fp, "rt") as f:
                for i, line in enumerate(f):
                    if i < 3 or '"k":"kbook"' in line[:20] and i < 400:
                        print(line[:400])
                        if i > 3:
                            break
    else:
        print(__doc__)
