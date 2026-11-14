#!/usr/bin/env python3
"""Polymarket PAPER-trading bot.

Follows one wallet's positions and runs rule-based strategies, recording
everything as paper trades. It never places real orders and needs no keys:
it only reads Polymarket's and Kalshi's public APIs and (optionally) sends ntfy pushes.

Usage:
    python3 bot.py watch     # every ~10 min: copy his opens/exits, manage exits, arb checks, panic scan every 2h;
                             # also runs the daily job if GitHub skipped it
    python3 bot.py daily     # once a day: settle, strategy picks, arb candidates, summary (FORCE=true to re-run)
    python3 bot.py summary   # rebuild summary files only
    python3 bot.py selftest  # print raw API samples and send a test push
"""
import datetime as dt
import json
import math
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "state")
with open(os.path.join(ROOT, "config.json")) as _fh:
    CFG = json.load(_fh)

DATA = "https://data-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
KALSHI = "https://external-api.kalshi.com/trade-api/v2"
ARB_PAIRS = os.path.join(ROOT, "arb_pairs.json")
UA = "poly-paper-bot/1.0 (paper trading only)"
EPS = 1e-9


# ================================================================ helpers

def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    if not s or not isinstance(s, str):
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        try:
            t = dt.datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t


def fnum(x, default=0.0):
    try:
        v = float(x)
        return v if v == v else default  # NaN guard
    except (TypeError, ValueError):
        return default


def pick(d, *keys, default=None):
    """First present, non-empty value among keys (APIs mix snake/camel case)."""
    if not isinstance(d, dict):
        return default
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return default


def jlist(x):
    """Gamma encodes some lists as JSON strings."""
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = json.loads(x)
            return v if isinstance(v, list) else []
        except ValueError:
            return []
    return []


def http_json(url, params=None, retries=3):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code} for {url}"
            if e.code in (429, 500, 502, 503, 504):
                wait = fnum(e.headers.get("Retry-After") if e.headers else None, 2 + 3 * i)
                time.sleep(min(wait, 20))
                continue
            raise RuntimeError(last)
        except Exception as e:  # network hiccup
            last = f"{type(e).__name__}: {e} for {url}"
            time.sleep(2 + 3 * i)
    raise RuntimeError(last)


def envelope_rows(res, *keys):
    if isinstance(res, list):
        return res
    if isinstance(res, dict):
        for k in keys:
            if isinstance(res.get(k), list):
                return res[k]
    return []


def cents(p):
    return "?" if p is None else f"{p * 100:.0f}c"


# ================================================================ state

def load(name, default):
    p = os.path.join(STATE, name)
    if os.path.exists(p):
        with open(p) as fh:
            return json.load(fh)
    return default


def save(name, obj):
    os.makedirs(STATE, exist_ok=True)
    p = os.path.join(STATE, name)
    tmp = p + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, p)


def log_event(ev):
    os.makedirs(STATE, exist_ok=True)
    ev = {"ts": iso(), **ev}
    with open(os.path.join(STATE, "events.jsonl"), "a") as fh:
        fh.write(json.dumps(ev, sort_keys=True) + "\n")
    print("EVENT", json.dumps(ev, sort_keys=True))


# ---- "alive but waiting": what each strategy saw on its last check and why it didn't buy (records only)
_STATUS = {}


def saw(name, msg):
    """One plain line about this run's check for a track, e.g. '0 of 11,236 markets match its rules'."""
    _STATUS.setdefault(name, {"skips": Counter()})["msg"] = msg


def why(name, reason):
    """Count one skip reason for a track this run."""
    _STATUS.setdefault(name, {"skips": Counter()})["skips"][reason] += 1


def stamp_status(tracks):
    """Copy this run's notes into tracks[name]['status'] (shown on the dashboard). Tracks not checked this run keep
    their last note; the paced rule tracks get a 'next pick' note so a quiet day doesn't look dead."""
    picked = load("scan_state.json", {}).get("picked_on", {})
    for name, tc in CFG["tracks"].items():
        tr = tracks.get(name)
        if tr is None:
            continue
        st = _STATUS.get(name)
        if st:
            tr["status"] = {"at": iso(), "msg": st.get("msg", ""), "skips": dict(st["skips"].most_common(5))}
        elif tc["source"] in ("screener", "random", "momentum") and picked.get(name) != today_utc():
            tr["status"] = {"at": iso(), "msg": "Picks once a day at the morning run (about 06:00 Stockholm); "
                                                "no pick yet today.", "skips": {}}
    _STATUS.clear()


def drop_phantom_fills(tr):
    """One-time cleanup (Jan's OK, 2026-11-09): endgame paper buys made on an empty order book ('estimate' fills at
    the stale listed price) could never have happened, so they are taken out of the score and their money put back.
    The old numbers stay in git history."""
    closed = [c for c in tr["closed"] if c.get("price_source") == "estimate"]
    opened = {t: p for t, p in tr["positions"].items() if p.get("price_source") == "estimate"}
    pnl = sum(c.get("pnl", 0.0) for c in closed)
    back = sum(p["shares"] * p["entry"] + p.get("entry_fee", 0.0) for p in opened.values())
    tr["closed"] = [c for c in tr["closed"] if c.get("price_source") != "estimate"]
    for t in opened:
        del tr["positions"][t]
    tr["cash"] = round(tr["cash"] - pnl + back, 6)
    tr["realized"] = round(tr["realized"] - pnl, 6)
    tr["phantom_removed"] = {"on": iso(), "closed": len(closed), "open": len(opened), "pnl_removed": round(pnl, 4)}
    print(f"phantom cleanup: removed {len(closed)} closed + {len(opened)} open estimate fills, pnl {pnl:+.2f}")


def load_tracks():
    tracks = load("tracks.json", {})
    for name, tc in CFG["tracks"].items():
        if name not in tracks:
            start = tc["start_cash"]
            tracks[name] = {
                "unlimited": start is None,
                "cash": 0.0 if start is None else float(start),
                "start_cash": start,
                "deposited": 0.0 if start is None else float(start),
                "refills": 0,
                "min_cash": 0.0,           # unlimited tracks: lowest cash balance = money you'd have needed
                "peak_open_cost": 0.0,     # most money tied up in open positions at once
                "positions": {},
                "closed": [],
                "realized": 0.0,
                "skipped_no_cash": 0,
                "created": iso(),
            }
        if tc["source"] == "endgame" and "phantom_removed" not in tracks[name]:
            drop_phantom_fills(tracks[name])
        if tc["source"] == "arb":
            for k, v in (("arbs", {}), ("opportunities", 0), ("mismatches", 0), ("last_check", {})):
                tracks[name].setdefault(k, v)
        if tc["source"] in ("fullset", "ladder"):
            for k, v in (("sets", {}), ("opportunities", 0), ("incomplete", 0), ("seen", {})):
                tracks[name].setdefault(k, v)
        if tc["source"] == "kmaker":
            for k, v in (("orders", {}), ("unfilled", 0), ("unfilled_log", []), ("last_check", {})):
                tracks[name].setdefault(k, v)
        if tc["source"] == "econ":
            for k, v in (("orders", {}), ("done", []), ("last_check", {})):
                tracks[name].setdefault(k, v)
        if tc["source"] == "kpatient":
            for k, v in (("orders", {}), ("done", []), ("unfilled", 0), ("last_check", {})):
                tracks[name].setdefault(k, v)
    return tracks


def rules_for(name):
    r = CFG["tracks"][name].get("rules")
    return rule_set(r) if r else {}


def rule_set(key):
    """A rules block; {"inherit": "endgame", ...} starts from another block and overrides some settings."""
    r = dict(CFG["rules"].get(key, {}))
    base = r.pop("inherit", None)
    return {**rule_set(base), **r} if base else r


def is_lab(name):
    return bool(CFG["tracks"].get(name, {}).get("lab"))


# ================================================================ push

def push_allowed(track):
    """Trade pushes only for strategies in the current top 10 (state/top.json, rewritten by the daily scoreboard).
    Alerts (FLIP, SHORT, MISMATCH) and the scoreboard pass track=None and always go out."""
    if track is None or not CFG["push"].get("top_only"):
        return True
    names = track if isinstance(track, (list, tuple)) else [track]
    top = load("top.json", None)
    if top is None:  # before the first ranking: the original tracks keep their pushes, new ones stay quiet
        return any(not is_lab(n) for n in names)
    return any(n in top.get("tracks", []) for n in names)


def push_log(title, track, result):
    """Remember every phone push (state/push_log.json): sent, failed, or muted (muted ones only counted per day).
    Lets us prove what reached ntfy and when; summary.md shows it under "Phone alerts"."""
    try:
        d = load("push_log.json", {"recent": [], "days": {}})
        day = d.setdefault("days", {}).setdefault(today_utc(), {"sent": 0, "failed": 0, "muted": 0})
        day[result if result in ("sent", "muted") else "failed"] += 1
        if result != "muted":
            d.setdefault("recent", []).append({"ts": iso(), "title": title[:120], "track": track if isinstance(track, str) else None,
                                               "result": result[:200]})
            d["recent"] = d["recent"][-200:]
        d["days"] = {k: d["days"][k] for k in sorted(d["days"])[-30:]}
        save("push_log.json", d)
    except Exception as e:
        print(f"push log failed: {e}")


def push_md():
    d = load("push_log.json", {})
    out = ["\n## Phone alerts\n", "What the bot sent to Jan's phone (ntfy). Muted = a trade by a strategy outside the top 10."]
    days = d.get("days", {})
    if not days:
        return out + ["Nothing logged yet."]
    for k in sorted(days)[-3:][::-1]:
        v = days[k]
        out.append(f"- {k}: {v['sent']} sent, {v['failed']} failed, {v['muted']} muted")
    last_ok = next((r for r in reversed(d.get("recent", [])) if r["result"] == "sent"), None)
    last_bad = next((r for r in reversed(d.get("recent", [])) if r["result"] != "sent"), None)
    if last_ok:
        out.append(f"- Last sent: {last_ok['ts']} \"{last_ok['title']}\"")
    if last_bad:
        out.append(f"- Last failure: {last_bad['ts']} \"{last_bad['title']}\": {last_bad['result']}")
    return out


def push(title, body, click=None, tags=None, track=None):
    if not push_allowed(track):
        print(f"[push muted, not in top {CFG['push'].get('top_n', 10)}] {title}")
        push_log(title, track, "muted")
        return
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        print(f"[push skipped, no NTFY_TOPIC] {title} | {body}")
        push_log(title, track, "failed: no NTFY_TOPIC secret")
        return
    headers = {"Title": title.encode("ascii", "ignore").decode(), "User-Agent": UA}
    if click:
        headers["Click"] = click
    if tags:
        headers["Tags"] = tags
    req = urllib.request.Request(
        f"https://ntfy.sh/{urllib.parse.quote(topic)}",
        data=body.encode("utf-8"), headers=headers, method="POST",
    )
    err = None
    for attempt in range(2):  # one retry: ntfy.sh sometimes drops a request
        try:
            urllib.request.urlopen(req, timeout=15).read()
            err = None
            break
        except Exception as e:
            err = f"{e}"
            print(f"push failed (try {attempt + 1}): {e}")
            if isinstance(e, urllib.error.HTTPError) and e.code == 429:
                break  # rate limited: retrying makes it worse
            time.sleep(3)
    push_log(title, track, "sent" if err is None else f"failed: {err}")


def market_link(slug="", event_slug=""):
    if event_slug:
        return f"https://polymarket.com/event/{event_slug}"
    if slug:
        return f"https://polymarket.com/market/{slug}"
    return "https://polymarket.com"


# ================================================================ market data

_market_cache = {}


def market_by_slug(slug):
    if not slug:
        return None
    if slug in _market_cache:
        return _market_cache[slug]
    m = None
    try:
        res = http_json(f"{GAMMA}/markets/slug/{urllib.parse.quote(slug)}")
        m = res[0] if isinstance(res, list) and res else (res if isinstance(res, dict) else None)
    except Exception as e:
        print(f"market lookup failed for {slug}: {e}")
    _market_cache[slug] = m
    return m


def prefetch_markets(slugs, workers=8):
    """Look up many markets at once (8 at a time) so 70 tracks' positions don't take ages one by one."""
    todo = sorted({s for s in slugs if s and s not in _market_cache})
    if len(todo) > 1:
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(market_by_slug, todo))


def market_tokens(m):
    if not m:
        return []
    ids = jlist(m.get("clobTokenIds")) or list(m.get("positionIds") or [])
    return [str(x) for x in ids]


def token_price_from_market(m, token):
    toks = market_tokens(m)
    prices = jlist(m.get("outcomePrices")) if m else []
    if token in toks:
        i = toks.index(token)
        if i < len(prices):
            return fnum(prices[i], None)
    return None


def fee_rate(m):
    if not m:
        return 0.05
    if m.get("feesEnabled") is False:
        return 0.0
    fs = m.get("feeSchedule") or {}
    if isinstance(fs, dict) and fs.get("rate") is not None:
        return fnum(fs.get("rate"), 0.05)
    return 0.05  # unknown: assume a typical rate (conservative)


def taker_fee(shares, price, rate):
    return shares * rate * price * (1 - price)


def book(token):
    try:
        b = http_json(f"{CLOB}/book", {"token_id": token})
    except Exception as e:
        print(f"book failed for {token[:12]}...: {e}")
        return None
    asks = sorted(((fnum(a.get("price")), fnum(a.get("size"))) for a in b.get("asks", []) if fnum(a.get("size")) > 0),
                  key=lambda x: x[0])
    bids = sorted(((fnum(a.get("price")), fnum(a.get("size"))) for a in b.get("bids", []) if fnum(a.get("size")) > 0),
                  key=lambda x: -x[0])
    return {"asks": asks, "bids": bids, "min_size": fnum(b.get("min_order_size"), 5)}


def walk(levels, shares):
    """Average price to fill `shares` against book levels, or None if too thin."""
    left, cost = shares, 0.0
    for p, s in levels:
        take = min(left, s)
        cost += take * p
        left -= take
        if left <= EPS:
            return cost / shares
    return None


def quote(token, side, shares, m=None):
    """Paper fill price. 'buy' takes the ask, 'sell' hits the bid. Only real book fills count: with no book, or a book
    too thin for our shares, there is no fill (None) and the caller tries again on a later run.
    Bug fix 2026-11-09 (audit): this used to fall back to the listed price +/- 1c ('estimate'), which let endgame
    tracks 'buy' on empty books and let exits 'sell' to bids that weren't there. Paper fills must be fills that
    could really have happened."""
    bk = book(token)
    LAST_BOOK[token] = (time.time(), bk)  # the real-size model re-walks this same book at $10-$100
    if bk:
        shares = max(shares, bk["min_size"])
        px = walk(bk["asks"] if side == "buy" else bk["bids"], shares)
        if px is not None:
            return px, shares, "book"
    return None, shares, "none"


# ================================================================ real-size check (what $10-$100 a trade would get)
#
# Paper fills are 5 shares (about $5). Real money ($300-500 in one strategy) means $10-$100 a trade, which eats
# deeper into the order book: a worse average price, a bigger fee, and in thin markets not everything fits.
# Every paper fill also re-walks the SAME live book at each size in config "real_size" and records what that
# trade would have cost and paid. It never changes what a track buys or sells (the paper trades and the frozen lab
# rules stay exactly as they were); it only adds a second set of numbers that the trust ranking uses.

LAST_BOOK = {}  # token -> (time, book) from the latest quote()


def rs_cfg():
    return CFG.get("real_size", {})


def rs_sizes():
    return [int(x) for x in rs_cfg().get("sizes_usd", [10, 25, 50, 100])]


def fresh_book(token):
    t, bk = LAST_BOOK.get(token, (0, None))
    return bk if time.time() - t < 300 else None


def fill_usd(levels, usd, limit=None):
    """Spend up to `usd` on ask levels (cheapest first) without paying more than `limit`. -> (shares, cost)."""
    left, sh, cost = usd, 0.0, 0.0
    for p, s in levels:
        if limit is not None and p > limit + EPS:
            break
        if p <= 0:
            continue
        take = min(s, left / p)
        sh, cost, left = sh + take, cost + take * p, left - take * p
        if left <= 1e-6:
            break
    return sh, cost


def fill_shares(levels, shares):
    """Sell (or buy) `shares` into book levels. -> (filled shares, money), may fill less than asked."""
    left, got, money = shares, 0.0, 0.0
    for p, s in levels:
        take = min(left, s)
        got, money, left = got + take, money + take * p, left - take
        if left <= EPS:
            break
    return got, money


def implied_rate(shares, price, fee):
    d = shares * price * (1 - price)
    return fee / d if d > EPS else 0.0


def rs_buy(token, shares, price, fee):
    """Real-size buy at each stake: {size: [shares, cost incl. fee, filled the whole stake?]}.
    A real bot would use a limit order, so it never pays more than the best ask + max_slip (and never 99c+)."""
    bk = fresh_book(token)
    rate = implied_rate(shares, price, fee)
    out = {"rate": round(rate, 5), "how": "book" if bk and bk["asks"] else "estimate", "s": {}}
    if out["how"] == "book":
        best = bk["asks"][0][0]
        limit = max(price, min(rs_cfg().get("max_price", 0.99), best + rs_cfg().get("max_slip", 0.02)))
    for size in rs_sizes():
        if out["how"] == "book":
            sh, c = fill_usd(bk["asks"], size, limit)
        else:  # no book (rare): assume the paper price plus the fallback slippage, fully filled
            px = min(0.999, price + CFG["fallback_slippage"])
            sh, c = size / px, size
        f = taker_fee(sh, c / sh, rate) if sh > EPS else 0.0
        out["s"][str(size)] = [round(sh, 3), round(c + f, 4), bool(c >= size * 0.97)]
    return out


def rs_close(pos, token, price, fee, resolved):
    """Real-size result at each stake: {size: [cost, pnl, filled the whole stake?]} or None (no real-size data).
    Resolved: every share pays `price`. Sold early: walk the same live bids; shares the bids can't take are
    valued at half the worst bid (thin_exit_haircut), because dumping them would cost more."""
    rs = pos.get("rs")
    if not rs:
        return None
    bk = None if resolved else fresh_book(token)
    out = {}
    for size, (sh, cost, full) in rs["s"].items():
        if sh <= EPS:
            out[size] = [0.0, 0.0, False]  # nothing would have filled: no trade at this size
            continue
        if resolved:
            proceeds = sh * price
        elif bk and bk["bids"]:
            got, money = fill_shares(bk["bids"], sh)
            rest = sh - got
            proceeds = money + rest * bk["bids"][-1][0] * rs_cfg().get("thin_exit_haircut", 0.5)
            proceeds -= taker_fee(got, money / got, rs["rate"]) if got > EPS else 0.0
            full = full and rest <= EPS
        else:
            px = max(0.001, price - CFG["fallback_slippage"])
            proceeds = sh * px - taker_fee(sh, px, rs["rate"])
        out[size] = [round(cost, 4), round(proceeds - cost, 4), full]
    return out


def rs_pair_fill(size, legs, min_edge, payout_per_share, fees):
    """Arb / full-set real size: buy the same number of shares on every leg (each leg = ask levels), as many as
    `size` dollars allow while the average edge stays >= min_edge. -> [shares, cost, filled the whole stake?]."""
    per = sum(l[0][0] for l in legs if l) or 1
    n = size / per
    while n >= 1:
        px = [walk(l, n) for l in legs]
        if None not in px:
            cost = n * sum(px) + fees(n, px)
            if (n * payout_per_share - cost) / n >= min_edge:
                return [round(n, 3), round(cost, 4), bool(cost >= size * 0.97)]
        n *= 0.8
    return [0.0, 0.0, False]


def resolved_payout(m, token):
    """1.0 / 0.0 (or a split) once the market is closed with final prices, else None."""
    if not m or not m.get("closed"):
        return None
    p = token_price_from_market(m, token)
    if p is None:
        return None
    if p >= 0.99:
        return 1.0
    if p <= 0.01:
        return 0.0
    if m.get("umaResolutionStatus") == "resolved" or m.get("resolutionStatus") == "resolved":
        return p  # split / 50-50 style resolution
    return None


def theme_of(text):
    """Group correlated markets (e.g. Iran and Hormuz both count as 'middle east')."""
    t = (text or "").lower()
    for group, words in CFG.get("themes", {}).items():
        if any(w in t for w in words):
            return group
    return None


# ================================================================ paper book-keeping

def open_cost(track):
    return sum(p["shares"] * p["entry"] + p.get("entry_fee", 0.0) for p in track["positions"].values())


def maybe_refill(track, name, cost):
    tc = CFG["tracks"][name]
    if tc.get("refill") and not track["unlimited"] and track["cash"] + EPS < cost and not track["positions"]:
        track["cash"] = round(track["cash"] + tc["start_cash"], 6)
        track["deposited"] = round(track["deposited"] + tc["start_cash"], 6)
        track["refills"] += 1
        log_event({"type": "refill", "track": name, "amount": tc["start_cash"], "refills": track["refills"]})


def paper_buy(track, name, token, shares, price, fee, meta):
    cost = shares * price + fee
    maybe_refill(track, name, cost)
    if not track["unlimited"] and cost > track["cash"] + EPS:
        track["skipped_no_cash"] += 1
        log_event({"type": "skip_no_cash", "track": name, "token": token, "title": meta.get("title"),
                   "cost": round(cost, 4)})
        return False
    track["cash"] = round(track["cash"] - cost, 6)
    track["min_cash"] = round(min(track["min_cash"], track["cash"]), 6)
    track["positions"][token] = {"shares": shares, "entry": round(price, 6), "entry_fee": round(fee, 6),
                                 "opened": iso(), **meta}
    try:
        track["positions"][token]["rs"] = rs_buy(token, shares, price, fee)
    except Exception as e:
        print(f"real-size buy failed: {e}")
    track["peak_open_cost"] = round(max(track["peak_open_cost"], open_cost(track)), 6)
    LATE_PENDING.append((time.time(), name, token))
    log_event({"type": "paper_buy", "track": name, "token": token, "title": meta.get("title"),
               "outcome": meta.get("outcome"), "shares": shares, "price": round(price, 4), "fee": round(fee, 4)})
    return True


def paper_close(track, name, token, price, fee, reason):
    pos = track["positions"].pop(token, None)
    if not pos:
        return None
    proceeds = pos["shares"] * price - fee
    basis = pos["shares"] * pos["entry"] + pos.get("entry_fee", 0.0)
    pnl = proceeds - basis
    track["realized"] = round(track["realized"] + pnl, 6)
    track["cash"] = round(track["cash"] + proceeds, 6)
    rec = {**pos, "token": token, "exit": round(price, 6), "exit_fee": round(fee, 6),
           "closed_at": iso(), "reason": reason, "pnl": round(pnl, 6)}
    try:
        r = rs_close(pos, token, price, fee, reason == "resolved")
        if r:
            rec["rs_pnl"] = r
    except Exception as e:
        print(f"real-size close failed: {e}")
    if CFG["tracks"].get(name, {}).get("source") == "endgame" and "shadow" in pos:
        try:
            rec["shadow_results"] = shadow_results(rec)
        except Exception as e:
            print(f"shadow results failed: {e}")
    track["closed"].append(rec)
    log_event({"type": "paper_close", "track": name, "token": token, "title": pos.get("title"),
               "outcome": pos.get("outcome"), "price": round(price, 4), "pnl": round(pnl, 4), "reason": reason})
    if CFG["tracks"].get(name, {}).get("source") == "endgame" and pnl < 0 and reason == "resolved" and CFG["push"].get("on_endgame") \
            and not rules_for(name).get("fade"):  # fade_sure loses most bets by design: no FLIP alert for those
        push(f"[{name}] FLIP: a 'sure thing' lost (${pnl:+.2f})",
             f"{pos.get('title')}\nBought {pos.get('outcome')} at {cents(pos['entry'])} ({pos.get('tier')}), paid out "
             f"{cents(price)}. This is the risk the test is measuring.", tags="rotating_light")
    return rec


def shadow_sell_check(pos, tok, m, px_now, rules):
    """'What if we sold early' test for endgame (records only, never trades): the first time the bid would
    fill us at each threshold (and once after 24h held), note the fill price net of fees."""
    sh = pos.setdefault("shadow", {})
    th = rules.get("shadow_sell_at", [])
    wants_time = "after_24h" not in sh and (now() - parse_iso(pos["opened"])).total_seconds() >= 86400
    open_th = [t for t in th if f"bid_{t:.2f}" not in sh]
    if not wants_time and not (open_th and px_now >= min(open_th) - 0.015):
        return  # nothing to check; skip the order-book call
    bid, _, how = quote(tok, "sell", pos["shares"], m)
    if bid is None or how != "book":
        return
    fee = taker_fee(pos["shares"], bid, fee_rate(m))
    rec = {"px": round(bid, 4), "fee": round(fee, 5), "at": iso()}
    for t in open_th:
        if bid >= t - EPS:
            sh[f"bid_{t:.2f}"] = rec
    if wants_time:
        sh["after_24h"] = {**rec, "late_start": pos["opened"] < "2026-11-06T12"}


def shadow_results(rec):
    """On close: what each early-sell rule would have made vs holding, and how many days sooner."""
    basis = rec["shares"] * rec["entry"] + rec.get("entry_fee", 0.0)
    closed = parse_iso(rec["closed_at"])
    res = {}
    for rule in [f"bid_{t:.2f}" for t in rules_for("endgame").get("shadow_sell_at", [])] + ["after_24h"]:
        s = rec.get("shadow", {}).get(rule)
        if s:
            res[rule] = {"pnl": round(rec["shares"] * s["px"] - s["fee"] - basis, 5),
                         "days_sooner": round((closed - parse_iso(s["at"])).total_seconds() / 86400, 2),
                         "sold": True}
        else:
            res[rule] = {"pnl": rec["pnl"], "days_sooner": 0.0, "sold": False}
    return res


def shadow_summary(tr):
    rows = [c for c in tr["closed"] if "shadow_results" in c]
    rules = [f"bid_{t:.2f}" for t in rules_for("endgame").get("shadow_sell_at", [])] + ["after_24h"]
    if not rows:
        hit = {r: sum(1 for p in tr["positions"].values() if r in p.get("shadow", {})) for r in rules}
        return (f"**Sell-early test** (records only, started 2026-11-06): no finished trades with data yet. "
                f"Open positions that would already have been sold: " +
                ", ".join(f"{r.replace('bid_', 'bid >= ')} {n}" for r, n in hit.items()) + ".\n")
    hold = sum(c["pnl"] for c in rows)
    days = [(parse_iso(c["closed_at"]) - parse_iso(c["opened"])).total_seconds() / 86400 for c in rows]
    parts = [f"hold to payout ${hold:+.2f} (avg {sum(days) / len(days):.1f} days to get the money back)"]
    for r in rules:
        res = [c["shadow_results"][r] for c in rows if r in c["shadow_results"]]
        sold = [x for x in res if x["sold"]]
        p = sum(x["pnl"] for x in res)
        soon = sum(x["days_sooner"] for x in sold) / len(sold) if sold else 0
        parts.append(f"{r.replace('bid_', 'sell at bid >= ').replace('after_24h', 'sell after 24h')} ${p:+.2f} "
                     f"({len(sold)}/{len(res)} sold, money back {soon:.1f} days sooner)")
    return f"**Sell-early test** ({len(rows)} finished trades, records only): " + "; ".join(parts) + ".\n"


COPY_SOURCES = ("leader", "wallet", "consensus")


def manage_exits(tracks, lab=True):
    """Take-profit / stop-loss / settlement for the rule-based tracks (not the copy tracks).
    lab=False skips the ~20 lab rule tracks (they are checked every lab_exit_minutes, not every 5 minutes)."""
    todo = [n for n in tracks if CFG["tracks"][n]["source"] not in COPY_SOURCES + ("arb", "fullset", "ladder", "maker", "kmaker", "econ", "kpatient")
            and (lab or not is_lab(n))]
    prefetch_markets(p.get("slug") for n in todo for p in tracks[n]["positions"].values())
    for name in todo:
        tr, tc = tracks[name], CFG["tracks"][name]
        rules = rules_for(name)
        for tok in list(tr["positions"]):
            pos = tr["positions"][tok]
            m = market_by_slug(pos.get("slug"))
            payout = resolved_payout(m, tok)
            if payout is not None:
                paper_close(tr, name, tok, payout, 0.0, "resolved")
                continue
            if not m or m.get("closed"):
                continue
            px_now = token_price_from_market(m, tok)
            if px_now is None:
                continue
            if tc["source"] == "endgame":
                try:
                    shadow_sell_check(pos, tok, m, px_now, rules)
                except Exception as e:
                    print(f"shadow check failed: {e}")
            target = pos.get("target") or rules.get("take_profit")
            stop = pos.get("stop") or rules.get("stop_loss")
            reason = None
            if target and px_now >= target:
                reason = f"take profit (now {cents(px_now)})"
            elif stop and px_now <= stop:
                reason = f"stop loss (now {cents(px_now)})"
            if not reason:
                continue
            fill, _, how = quote(tok, "sell", pos["shares"], m)
            if fill is None:
                continue
            if reason.startswith("take profit") and fill < target - 0.01:
                # bug fix 2026-11-08: the listed price can say 100c while the real bid on a finished match is 80c.
                # Taking profit means the bid is really there; otherwise keep holding (it pays out at the end).
                tr["tp_thin_skips"] = tr.get("tp_thin_skips", 0) + 1
                continue
            rec = paper_close(tr, name, tok, fill, taker_fee(pos["shares"], fill, fee_rate(m)), f"{reason}, {how}")
            if rec and CFG["push"].get("on_claude_trades"):
                push(f"[{name}] sold {pos.get('outcome')} at {cents(fill)} ({usd(rec['pnl'])})",
                     f"{pos.get('title')}\nReason: {reason}",
                     click=market_link(pos.get("slug", ""), pos.get("event_slug", "")), tags="moneybag", track=name)


# ================================================================ leader wallet (mirror tracks)

def leader_positions(addr):
    rows, cursor = [], None
    for _ in range(40):
        params = {"user": addr, "limit": 500}
        if cursor:
            params["cursor"] = cursor
        res = http_json(f"{DATA}/v2/positions", params)
        rows += envelope_rows(res, "data")
        pag = (res.get("pagination") or {}) if isinstance(res, dict) else {}
        cursor = pag.get("next_cursor")
        if not cursor:
            break
    return rows


def norm_pos(r):
    return {
        "token": str(pick(r, "token_id", "asset", "tokenId", "asset_id", "position_id", default="")),
        "size": round(fnum(pick(r, "current_size", "size", "tokens", "balance")), 2),
        "avg": round(fnum(pick(r, "avg_price", "avgPrice", "entry_avg_price")), 4),
        "cur": fnum(pick(r, "current_price", "curPrice", "price"), None),
        "outcome": str(pick(r, "outcome", default="?")),
        "title": str(pick(r, "title", "question", default="")),
        "slug": str(pick(r, "slug", "market_slug", default="")),
        "event_slug": str(pick(r, "event_slug", "eventSlug", default="")),
        "end": str(pick(r, "end_date", "endDate", default="")),
        "redeemable": bool(pick(r, "redeemable", default=False)),
    }


def slim(p, first_seen=None):
    d = {k: p[k] for k in ("size", "avg", "outcome", "title", "slug", "event_slug", "end")}
    if first_seen:
        d["first_seen"] = first_seen
    return d


def leader_tracks():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "leader"]


_activity_cache = {}


def leader_activity(addr):
    """His recent wallet activity (trades, redeems, merges), newest first. One API call per run."""
    if addr not in _activity_cache:
        rows = []
        try:
            res = http_json(f"{DATA}/v2/activity", {"user": addr, "limit": 500})
            rows = envelope_rows(res, "data", "activity")
        except Exception as e:
            print(f"activity lookup failed: {e}")
        if not rows:
            try:
                res = http_json(f"{DATA}/v2/trades", {"user": addr, "limit": 500})
                rows = envelope_rows(res, "data", "trades")
            except Exception as e:
                print(f"trades lookup failed: {e}")
        _activity_cache[addr] = rows
    return _activity_cache[addr]


def act_time(a):
    t = pick(a, "timestamp", "time", "created_at", "createdAt")
    if isinstance(t, (int, float)) or (isinstance(t, str) and t.isdigit()):
        t = float(t)
        return dt.datetime.fromtimestamp(t / 1000 if t > 1e11 else t, dt.timezone.utc)
    return parse_iso(t)


def leader_exit_fill(addr, tok, days=7):
    """How he left one position: ('sold'|'redeemed'|'merged', avg price, shares) from his own activity, or None."""
    cutoff = now() - dt.timedelta(days=days)
    sold_sh = sold_usd = 0.0
    kinds = set()
    for a in leader_activity(addr):
        asset = str(pick(a, "asset", "asset_id", "token_id", "tokenId", default=""))
        typ = str(pick(a, "type", default="TRADE")).upper()
        t = act_time(a)
        if t and t < cutoff:
            continue
        if typ in ("REDEEM", "MERGE") and (asset == tok or not asset):
            if asset == tok:
                kinds.add(typ.lower() + "d" if typ == "MERGE" else "redeemed")
            continue
        if asset != tok or typ != "TRADE" or str(pick(a, "side", default="")).upper() != "SELL":
            continue
        sh, px = fnum(pick(a, "size", "shares")), fnum(pick(a, "price"))
        if sh > 0 and 0 < px <= 1:
            sold_sh += sh
            sold_usd += sh * px
    if sold_sh > 0:
        return "sold", sold_usd / sold_sh, sold_sh
    if kinds:
        return sorted(kinds)[0], None, 0.0
    return None


def record_his_exit(q, tok, after, resolved, payout, m):
    """Append one row to state/his_exits.json: when he got out, at what price, and what holding would have paid."""
    lead = CFG["leader"]
    got = None
    try:
        got = leader_exit_fill(lead["address"], tok)
    except Exception as e:
        print(f"exit fill lookup failed: {e}")
    kind, px, src = None, None, "none"
    if got:
        kind, px, _ = got
        src = "his trades" if px is not None else "his activity"
    if px is None and payout is not None:
        kind, px, src = kind or "redeemed", payout, "settled price"
    if px is None and not resolved:
        bid, _, how = quote(tok, "sell", CFG["shares_per_trade"], m)
        if bid is not None:
            kind, px, src = kind or "sold", bid, f"bid at detection ({how})"
    end = parse_iso(q.get("end"))
    shares = max(0.0, q.get("size", 0) - after)
    avg = q.get("avg") or 0.0
    row = {"ts": iso(), "token": tok, "title": q.get("title"), "outcome": q.get("outcome"),
           "slug": q.get("slug"), "event_slug": q.get("event_slug"), "end": q.get("end"),
           "kind": kind or ("redeemed" if resolved else "unknown"), "early": not resolved,
           "shares": round(shares, 2), "his_avg": avg, "exit_price": None if px is None else round(px, 4),
           "price_source": src, "first_seen": q.get("first_seen"),
           "days_left": None if not end else round((end - now()).total_seconds() / 86400, 1)}
    if px is not None:
        row["profit_per_share"] = round(px - avg, 4)
        row["profit_usd"] = round(shares * (px - avg), 2)
        row["left_on_table_per_share"] = round(1 - px, 4)  # what he'd have gained more if it paid $1
    if row["first_seen"]:
        row["days_held"] = round((now() - parse_iso(row["first_seen"])).total_seconds() / 86400, 1)
    rows = load("his_exits.json", [])
    rows.append(row)
    save("his_exits.json", rows)
    return row


def settle_his_exits():
    """For his early exits, look up how the market finally paid: did selling early help or hurt him?"""
    rows = load("his_exits.json", [])
    changed = False
    for r in rows:
        if not r.get("early") or r.get("final") is not None or r.get("exit_price") is None:
            continue
        p = resolved_payout(market_by_slug(r.get("slug")), r["token"])
        if p is None:
            continue
        r["final"] = p
        r["selling_early_gained_per_share"] = round(r["exit_price"] - p, 4)
        r["selling_early_gained_usd"] = round(r["shares"] * (r["exit_price"] - p), 2)
        changed = True
    if changed:
        save("his_exits.json", rows)


def his_exit_summary():
    rows = [r for r in load("his_exits.json", []) if r.get("exit_price") is not None]
    if not rows:
        return ["\n## How he exits\nNo exits with a known price recorded yet (logging started 2026-11-06).\n"]
    early = [r for r in rows if r.get("early")]
    out = ["\n## How he exits\n",
           f"{len(rows)} exits with a known price (logged since 2026-11-06, plus his big early sells since March "
           f"backfilled from his trade history): {len(early)} sold early, "
           f"{len(rows) - len(early)} held to the payout.\n"]

    def med(xs):
        xs = sorted(x for x in xs if x is not None)
        return None if not xs else xs[len(xs) // 2]
    if early:
        wins = [r for r in early if (r.get("profit_per_share") or 0) > 0]
        mp, ml, md_ = med([r["exit_price"] for r in early]), med([r.get("left_on_table_per_share") for r in early]), \
            med([r.get("days_left") for r in early])
        out.append(f"Early sells: {len(wins)} in profit, {len(early) - len(wins)} at a loss; typical sell price "
                   f"{cents(mp)}, typical cents left on the table {'?' if ml is None else f'{ml * 100:.0f}c'}, "
                   f"typical days left before the end date {'?' if md_ is None else md_}.\n")
        fin = [r for r in early if r.get("final") is not None]
        if fin:
            g = sum(r["selling_early_gained_usd"] for r in fin)
            out.append(f"Of those, {len(fin)} markets have paid out since: selling early {'gained' if g >= 0 else 'cost'} "
                       f"him ${abs(g):,.2f} vs holding.\n")
        out.append("| Market | Side | His avg | Sold at | Profit/sh | Days left | Shares |\n|---|---|---|---|---|---|---|")
        for r in early[-10:]:
            out.append(f"| {str(r['title'])[:60]} | {r['outcome']} | {cents(r['his_avg'])} | {cents(r['exit_price'])} | "
                       f"{r.get('profit_per_share', 0) * 100:+.0f}c | {r.get('days_left', '?')} | {r['shares']:.0f} |")
    return out


def follow_leader(tracks):
    lead = CFG["leader"]
    rows = [norm_pos(r) for r in leader_positions(lead["address"])]
    cur = {p["token"]: p for p in rows if p["token"] and p["size"] > 0}
    snap = load("leader_snapshot.json", None)

    if snap is None:
        save("leader_snapshot.json", {"positions": {t: slim(p) for t, p in cur.items()}})
        log_event({"type": "baseline", "positions": len(cur)})
        push("Paper bot is live",
             f"Watching {lead['name']}: {len(cur)} open positions recorded as the starting point. "
             "You'll get a push when he opens or closes something.", tags="robot")
        return

    prev = snap.get("positions", {})
    if not cur and len(prev) > 3:
        print("Empty positions response while we expected some; skipping leader check this run.")
        return
    n = CFG["shares_per_trade"]
    newest = max((v.get("first_seen") or "" for v in prev.values()), default="")
    for name in leader_tracks():
        saw(name, f"Watching his {len(cur)} open positions. Last new one seen: {newest[:10] or 'none since the start'}.")

    # ---- new positions he opened
    both = split_tokens(cur)
    for tok, p in cur.items():
        if tok in both or prev.get(tok, {}).get("size", 0) >= 1 or p["redeemable"] or p["size"] < 5:
            continue
        if p["size"] * max(p["avg"], 0.01) < min(CFG["tracks"][n].get("min_open_usd", lead["min_open_usd"])
                                                 for n in leader_tracks()):
            continue
        m = market_by_slug(p["slug"])
        if m and m.get("closed"):
            continue
        end = parse_iso(p["end"]) or parse_iso((m or {}).get("endDate") or (m or {}).get("endDateIso"))
        if end and end < now():
            continue
        px, shares, how = quote(tok, "buy", n, m)
        rate = fee_rate(m)
        took = []
        for name in leader_tracks():
            tc, tr = CFG["tracks"][name], tracks[name]
            if px is None or tok in tr["positions"] or not (tc["min_price"] <= px <= tc["max_price"]):
                why(name, "his new bet's price is outside its range")
                continue
            if p["size"] * max(p["avg"], 0.01) < tc.get("min_open_usd", lead["min_open_usd"]):
                why(name, "his new bet was too small")
                continue  # e.g. sab_big: only his $1,000+ bets
            if paper_buy(tr, name, tok, shares, px, taker_fee(shares, px, rate),
                         {"title": p["title"], "outcome": p["outcome"], "slug": p["slug"],
                          "event_slug": p["event_slug"], "end": p["end"], "source": lead["name"],
                          "leader_avg": p["avg"], "price_source": how}):
                took.append(name)
        log_event({"type": "leader_open", "token": tok, "title": p["title"], "outcome": p["outcome"],
                   "leader_size": p["size"], "leader_avg": p["avg"],
                   "our_price": None if px is None else round(px, 4), "price_source": how, "copied_by": took})
        if CFG["push"]["on_leader_trades"]:
            push(f"{lead['name']} BUY {p['outcome']} @ {cents(p['avg'])}",
                 f"{p['title']}\nHe holds {p['size']:.0f} shares (${p['size'] * p['avg']:,.0f}). "
                 f"Your price now: {cents(px)}.\nPaper copied by: {', '.join(took) or 'none'}",
                 click=market_link(p["slug"], p["event_slug"]), tags="chart_with_upwards_trend", track=leader_tracks())

    # ---- positions he exited (sold, merged or redeemed)
    for tok, q in prev.items():
        after = cur.get(tok, {}).get("size", 0)
        if q.get("size", 0) < 1 or after > 0.2 * q["size"]:
            continue
        m = market_by_slug(q.get("slug"))
        payout = resolved_payout(m, tok)
        resolved = payout is not None or cur.get(tok, {}).get("redeemable", False)
        closed_by = []
        for name in leader_tracks():
            tr = tracks[name]
            if tok not in tr["positions"]:
                continue
            if payout is not None:
                paper_close(tr, name, tok, payout, 0.0, "resolved")
            elif resolved or CFG["tracks"][name].get("hold_to_end"):
                continue  # resolved but final price not published yet (daily run settles it), or a hold-to-the-end track
            else:
                sh = tr["positions"][tok]["shares"]
                px, _, how = quote(tok, "sell", sh, m)
                if px is None:
                    continue
                paper_close(tr, name, tok, px, taker_fee(sh, px, fee_rate(m)), f"leader exit ({how})")
            closed_by.append(name)
        try:
            xr = record_his_exit(q, tok, after, resolved, payout, m)
        except Exception as e:
            print(f"recording his exit failed: {e}")
            xr = {}
        log_event({"type": "leader_exit", "token": tok, "title": q.get("title"), "outcome": q.get("outcome"),
                   "size_before": q.get("size"), "size_after": after, "resolved": resolved, "closed_by": closed_by,
                   "his_avg": q.get("avg"), "exit_price": xr.get("exit_price"), "exit_kind": xr.get("kind"),
                   "exit_price_source": xr.get("price_source"), "days_left": xr.get("days_left")})
        if CFG["push"]["on_leader_trades"] and not resolved:
            how = ""
            if xr.get("exit_price") is not None:
                how = (f"Sold at ~{cents(xr['exit_price'])} (his avg {cents(q.get('avg'))}, "
                       f"{xr['profit_per_share'] * 100:+.0f}c/sh, ~${xr['profit_usd']:,.0f}), "
                       f"{xr.get('days_left', '?')} days before the end date.\n")
            push(f"{lead['name']} sold {q.get('outcome')} ({q.get('size', 0):.0f} -> {after:.0f} shares)",
                 f"{q.get('title')}\n{how}Paper closed in: {', '.join(closed_by) or 'none'}",
                 click=market_link(q.get("slug", ""), q.get("event_slug", "")), tags="chart_with_downwards_trend",
                 track=leader_tracks())

    new_snap = {"positions": {t: slim(p, prev.get(t, {}).get("first_seen") or (None if t in prev else iso()))
                              for t, p in cur.items()}}
    if new_snap != snap:
        save("leader_snapshot.json", new_snap)


def his_book_estimate():
    """What it would cost right now to hold every open position of his at the minimum size."""
    rows = [norm_pos(r) for r in leader_positions(CFG["leader"]["address"])]
    live = [p for p in rows if p["size"] >= 1 and not p["redeemable"] and p["cur"] and 0.01 < p["cur"] < 0.99]
    n = CFG["shares_per_trade"]
    return {
        "open_positions": len(live),
        "his_value": round(sum(p["size"] * p["cur"] for p in live), 2),
        "cost_min_size_each": round(sum(n * p["cur"] for p in live), 2),
        "biggest_position_share": round(max((p["size"] * p["cur"] for p in live), default=0) /
                                        max(sum(p["size"] * p["cur"] for p in live), 1), 3),
    }


# ================================================================ lab: copying many wallets (and the "smart-money crowd")
#
# Each wallet track copies one wallet's NEW positions (5 shares) and sells when the wallet sells. Unlike the
# sabsabinxz mirror it keeps only a compact snapshot (the token ids it holds), so 40 wallets don't bloat the repo.
# The consensus tracks buy what several of these wallets hold at once.

def wallet_tracks():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "wallet"]


def tkey(tok):
    return str(tok)[-16:]  # token ids are ~77 digits; the tail is unique enough and keeps the snapshot small


def split_tokens(cur):
    """Tokens of markets where the wallet holds BOTH sides at once (YES and NO, usually 50c each from a 'split' of
    $1 into a pair). That is market making or a merge-in-waiting, not a bet on one side, so the copy tracks skip it.
    Bug fix 2026-11-09 (audit): copies used to buy both legs (cost about $1.00 for a pair that pays exactly $1)."""
    by_market = defaultdict(list)
    for tok, p in cur.items():
        if p.get("slug") and not p.get("redeemable") and p.get("size", 0) >= 1:
            by_market[p["slug"]].append(tok)
    return {t for toks in by_market.values() if len(toks) >= 2 for t in toks}


def wallet_positions(addr, max_pages):
    """(positions, complete?) for one wallet, or (None, False) if the API failed."""
    rows, cursor = [], None
    try:
        for _ in range(max_pages):
            params = {"user": addr, "limit": 500}
            if cursor:
                params["cursor"] = cursor
            res = http_json(f"{DATA}/v2/positions", params)
            rows += envelope_rows(res, "data")
            cursor = ((res.get("pagination") or {}) if isinstance(res, dict) else {}).get("next_cursor")
            if not cursor:
                break
    except Exception as e:
        print(f"wallet positions failed for {addr[:10]}: {e}")
        return None, False
    return [norm_pos(r) for r in rows], not cursor


def copy_open(tracks, name, p, r, extra=None):
    """Paper-buy one position for a copy track. Returns True if bought."""
    tr = tracks[name]
    if p["token"] in tr["positions"]:
        return False
    if len(tr["positions"]) >= r.get("max_open", 999):
        tr["skipped_cap"] = tr.get("skipped_cap", 0) + 1
        why(name, "full (max open bets)")
        return False
    if p.get("slug") and any(q.get("slug") == p["slug"] for q in tr["positions"].values()):
        # bug fix 2026-11-10: a copy track must never hold both sides of one market (they pay exactly $1 together).
        # consensus_3 bought NO while it still held YES (different wallets on different sides), and w_/wb_bigggggggg
        # bought YES before its NO exit showed up (the wallet switched sides).
        tr["skipped_other_side"] = tr.get("skipped_other_side", 0) + 1
        why(name, "already holds the other side of this market")
        return False
    m = market_by_slug(p["slug"])
    if not m or m.get("closed") or m.get("acceptingOrders") is False:
        why(name, "market closed")
        return False
    end = parse_iso(p["end"]) or parse_iso(m.get("endDate") or m.get("endDateIso"))
    if end and end < now():
        why(name, "market already past its end date")
        return False
    px, shares, how = quote(p["token"], "buy", CFG["shares_per_trade"], m)
    if px is None or not (r.get("min_price", 0.02) <= px <= r.get("max_price", 0.97)):
        why(name, "no order book" if px is None else "price under 3c or over 97c")
        return False
    if r.get("max_chase") is not None and p["avg"] and px > p["avg"] + r["max_chase"]:
        tr["skipped_chase"] = tr.get("skipped_chase", 0) + 1  # we'd be paying well above what they paid: too late
        why(name, "too late (price 5c+ above what they paid)")
        return False
    meta = {"title": p["title"], "outcome": p["outcome"], "slug": p["slug"], "event_slug": p["event_slug"],
            "end": p["end"], "source": name, "their_avg": p["avg"], "their_size": p["size"], "price_source": how}
    meta.update(extra or {})
    if not paper_buy(tr, name, p["token"], shares, px, taker_fee(shares, px, fee_rate(m)), meta):
        why(name, "out of cash")
        return False
    return True


def copy_close(tracks, name, tok, why):
    """Close a copy position: pay out if resolved, else sell at the bid. Returns True if closed."""
    tr = tracks[name]
    pos = tr["positions"].get(tok)
    if not pos:
        return False
    m = market_by_slug(pos.get("slug"))
    payout = resolved_payout(m, tok)
    if payout is not None:
        return bool(paper_close(tr, name, tok, payout, 0.0, "resolved"))
    if not m or m.get("closed"):
        return False  # resolved but no final price yet: the daily settle picks it up
    px, _, how = quote(tok, "sell", pos["shares"], m)
    if px is None:
        return False
    return bool(paper_close(tr, name, tok, px, taker_fee(pos["shares"], px, fee_rate(m)), f"{why} ({how})"))


def backfill(tracks, name, cur, r):
    """wb_* tracks: once, buy the minimum (5 shares) of each of the wallet's current open positions at today's price,
    biggest first, up to max_backfill; a few per run so one run doesn't do hundreds of order-book calls. After that the
    track behaves like its w_* twin (copies new positions, sells when the wallet sells)."""
    tr = tracks[name]
    tried = set(tr.setdefault("bf_tried", []))
    both = split_tokens(cur)
    live = sorted((p for p in cur.values() if p["token"] not in both and not p["redeemable"] and p["size"] >= 5 and p["cur"]
                   and p["size"] * p["cur"] >= r["min_open_usd"]), key=lambda p: -p["size"] * p["cur"])
    todo = [p for p in live[: r.get("max_backfill", 30)] if tkey(p["token"]) not in tried]
    for p in todo[: r.get("backfill_per_run", 10)]:
        tr["bf_tried"].append(tkey(p["token"]))
        # avg=0: no 'too late' rule here, buying at today's price is the point of this test
        copy_open(tracks, name, dict(p, avg=0), r, {"backfill": True, "their_avg": p["avg"]})
    if len(todo) <= r.get("backfill_per_run", 10):
        tr["backfilled"] = iso()
        log_event({"type": "wallet_backfilled", "track": name, "bought": sum(1 for x in tr["positions"].values()
                                                                             if x.get("backfill"))})


def follow_wallets(tracks):
    names = wallet_tracks()
    if not names:
        return {}
    r = rule_set("wallet_copy")
    addrs = sorted({CFG["tracks"][n]["address"].lower() for n in names})
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(addrs, ex.map(lambda a: wallet_positions(a, r.get("max_pages", 4)), addrs)))
    snaps = load("wallet_snaps.json", {})
    old = {a: set(v.get("held", [])) for a, v in snaps.items()}  # w_ and wb_ twins share a wallet: both diff vs last run
    today = today_utc()
    live = {}  # addr -> {token: position} for this run (used by the consensus tracks)
    for name in names:
        addr = CFG["tracks"][name]["address"].lower()
        rows, complete = got.get(addr, (None, False))
        if rows is None:
            saw(name, "Wallet lookup failed this run (API error); tries again in 5 minutes.")
            continue
        cur = {p["token"]: p for p in rows if p["token"] and p["size"] >= 1}
        prev = old.get(addr, set())
        if addr not in old:
            saw(name, f"First look: {len(cur)} positions recorded as the starting point.")
            snaps[addr] = {"held": sorted(tkey(t) for t in cur), "since": iso()}
            log_event({"type": "wallet_baseline", "track": name, "positions": len(cur)})
            live[addr] = cur
            continue
        if not cur and len(prev) > 3:
            print(f"{name}: empty positions while we expected {len(prev)}; skipping this run")
            continue
        live[addr] = cur
        tr = tracks[name]
        day = tr.setdefault("day_opens", {})
        if day.get("date") != today:
            day.clear()
            day.update({"date": today, "n": 0})
        if CFG["tracks"][name].get("backfill") and not tr.get("backfilled"):
            backfill(tracks, name, cur, r)
        both = split_tokens(cur)
        # exits: the wallet sold (or redeemed) most of what it had when we copied
        # (exits run before new buys, so a wallet that switched sides is sold out of the old side first)
        cur_slugs = {p["slug"] for t, p in cur.items() if p.get("slug") and t not in both and not p["redeemable"]}
        for tok in list(tr["positions"]):
            q = cur.get(tok)
            pos = tr["positions"][tok]
            if q and q["redeemable"]:
                copy_close(tracks, name, tok, "resolved")
                continue
            if q is None and not complete:
                if pos.get("slug") in cur_slugs:
                    # bug fix 2026-11-10: it now holds the OTHER side of this market, so it sold ours (we just
                    # can't see the old side because a big wallet has more positions than we read)
                    copy_close(tracks, name, tok, "wallet switched sides")
                continue  # beyond the pages we read; can't tell
            if q is None or q["size"] <= 0.2 * pos.get("their_size", q["size"]):
                copy_close(tracks, name, tok, "wallet exit")
        # new positions
        fresh = 0
        for tok, p in cur.items():
            if tok in both:
                tr["skipped_split"] = tr.get("skipped_split", 0) + (tkey(tok) not in prev)
                continue
            if tkey(tok) in prev or p["redeemable"]:
                continue
            fresh += 1
            if p["size"] < 5 or p["size"] * max(p["avg"], 0.01) < r["min_open_usd"]:
                why(name, f"too small (under ${r['min_open_usd']})")
                continue
            if day["n"] >= r.get("max_new_per_day", 999):
                tr["skipped_cap"] = tr.get("skipped_cap", 0) + 1
                why(name, "daily copy limit reached")
                continue
            if copy_open(tracks, name, p, r):
                day["n"] += 1
        saw(name, f"Watching {len(cur)} open positions of this wallet; {fresh} new since the last check. "
                  f"Watching since {str(snaps[addr].get('since') or '?')[:10]}.")
        held = {tkey(t) for t in cur}
        if not complete:
            held |= prev
        snaps[addr] = {"held": sorted(held), "since": snaps[addr].get("since")}
    save("wallet_snaps.json", snaps)
    return live


def follow_consensus(tracks, live):
    """Buy what several copied wallets hold right now; sell when none of them holds it any more."""
    names = [n for n, tc in CFG["tracks"].items() if tc["source"] == "consensus"]
    if not names or len(live) < 3:
        return
    for name in names:
        r, tr = rules_for(name), tracks[name]
        count, sample, redeem = Counter(), {}, set()
        for cur in live.values():
            both = split_tokens(cur)
            for tok, p in cur.items():
                if p["redeemable"]:
                    redeem.add(tok)
                    continue
                if tok in both:
                    continue  # holds both sides of this market: not a vote for either
                if p["size"] * (p["cur"] or p["avg"]) >= r["min_usd_each"] and p["cur"] and \
                        r["min_price"] <= p["cur"] <= r["max_price"]:
                    count[tok] += 1
                    sample.setdefault(tok, p)
        holders = Counter(tok for cur in live.values() for tok, p in cur.items() if not p["redeemable"])
        for tok in list(tr["positions"]):
            if tok in redeem:
                copy_close(tracks, name, tok, "resolved")
            elif holders.get(tok, 0) == 0:
                copy_close(tracks, name, tok, "all wallets left")
        done = set(tr.setdefault("seen", []))
        hot = sum(1 for _, k in count.items() if k >= r["min_wallets"])
        saw(name, f"{hot} markets held by {r['min_wallets']}+ of the copied wallets right now ({len(live)} wallets read).")
        tried = 0
        for tok, k in count.most_common():
            if k < r["min_wallets"] or tried >= r.get("picks_per_run", 5) or len(tr["positions"]) >= r.get("max_open", 999):
                break
            if tkey(tok) in done:
                continue
            tried += 1
            tr["seen"].append(tkey(tok))  # one try per token: no re-buying after an exit, no retrying every 5 min
            copy_open(tracks, name, dict(sample[tok], avg=0), r, {"wallets": k})  # avg=0: no chase rule for a crowd


# ================================================================ strategies on the whole market

def scan_filters():
    """Server-side pre-filter covering the screener/panic strategies' widest settings (deadline window, liquidity).
    The arb track scans separately with its own window."""
    rs = [rules_for(n) for n, tc in CFG["tracks"].items() if tc["source"] in ("screener", "panic", "random", "momentum")]
    lo = now() + dt.timedelta(days=min(r["min_days"] for r in rs))
    hi = now() + dt.timedelta(days=max(r["max_days"] for r in rs))
    return {"end_date_min": iso(lo), "end_date_max": iso(hi),
            "liquidity_num_min": min(r["min_liquidity"] for r in rs)}


_scan_cache = {}


def scan_markets(filters=None):
    """Open markets (one pass, cached per run so the endgame variants share one scan). Tries server-side filters first;
    falls back to the unfiltered list if the API rejects them."""
    filters = filters or scan_filters()
    # dates rounded to the hour: one full scan takes 1-2 minutes, so minute-level keys would never match
    key = json.dumps({k: v[:13] if isinstance(v, str) else v for k, v in filters.items()}, sort_keys=True)
    if key not in _scan_cache:
        _scan_cache[key] = _scan_markets(filters)
    return _scan_cache[key]


def _scan_markets(filters):
    for filtered in (True, False):
        out, cursor, ok = [], None, True
        for page in range(400):
            params = {"closed": "false", "limit": 500, "version": ["v1", "v2"]}
            if filtered:
                params.update(filters)
            if cursor:
                params["after_cursor"] = cursor
            try:
                res = http_json(f"{GAMMA}/markets/keyset", params)
            except Exception as e:
                print(f"market scan page {page} failed ({'filtered' if filtered else 'unfiltered'}): {e}")
                ok = page > 0
                break
            ms = [m for m in envelope_rows(res, "markets", "data") if isinstance(m, dict)]
            out += ms
            cursor = res.get("next_cursor") if isinstance(res, dict) else None
            if not cursor or not ms:
                break
        if ok and out:
            print(f"scanned {len(out)} open markets ({'server-filtered' if filtered else 'unfiltered'}"
                  f"{', hit page cap' if cursor else ''})")
            return out
    return []


def is_sports(m):
    return bool(m.get("sportsMarketType") or m.get("gameId") or (m.get("sports") or {}).get("gameId"))


def base_filter(m, r):
    """Shared filters. Returns (days_left, liquidity, volume) or None."""
    if m.get("closed") or m.get("active") is False or m.get("acceptingOrders") is False or is_sports(m):
        return None
    q = str(m.get("question") or "").lower()
    if any(w in q for w in r.get("skip_words", [])):
        return None
    end = parse_iso(m.get("endDate") or m.get("endDateIso"))
    if not end:
        return None
    days = (end - now()).total_seconds() / 86400
    if not (r["min_days"] <= days <= r["max_days"]):
        return None
    liq = fnum(pick(m, "liquidityNum", "liquidity"))
    if liq < r["min_liquidity"]:
        return None
    vol_raw = pick(m, "volumeNum", "volume")
    if vol_raw is not None and fnum(vol_raw) < r.get("min_volume", 0):
        return None
    return days, liq, fnum(vol_raw)


def candidate(m, i, days, liq, extra=None):
    outs, toks = jlist(m.get("outcomes")), market_tokens(m)
    events = m.get("events") or []
    ev = events[0] if events and isinstance(events[0], dict) else {}
    q = str(m.get("question") or "")
    c = {"token": toks[i], "outcome": str(outs[i]), "price": fnum(jlist(m.get("outcomePrices"))[i]), "title": q,
         "slug": str(m.get("slug") or ""), "event_slug": str(ev.get("slug") or ""),
         "event_key": str(ev.get("id") or ev.get("slug") or m.get("slug")),
         "theme": theme_of(q), "end": (parse_iso(m.get("endDate") or m.get("endDateIso")) or now()).strftime("%Y-%m-%d"),
         "days": round(days, 1), "liquidity": round(liq), "fee_rate": fee_rate(m),
         "nothing_happens": str(outs[i]).lower() == "no", "market": m}
    c.update(extra or {})
    return c


def binary(m):
    outs, toks = jlist(m.get("outcomes")), market_tokens(m)
    prices = [fnum(x, None) for x in jlist(m.get("outcomePrices"))]
    if len(outs) != 2 or len(toks) != 2 or len(prices) != 2 or None in prices:
        return None
    return prices


def pick_side(m, prices, side, rng=None):
    """Which outcome a rule track buys: 'favorite' (default), 'underdog', 'no' / 'yes' (that side only, if it is the
    favorite), or 'random' (a coin flip; the control track)."""
    fav = 0 if prices[0] >= prices[1] else 1
    if side == "underdog":
        return 1 - fav
    if side == "random":
        return (rng or random).randrange(2)
    if side in ("no", "yes"):
        outs = [str(o).lower() for o in jlist(m.get("outcomes"))]
        return fav if len(outs) == 2 and outs[fav] == side else None
    return fav


def boring_side_candidates(markets, r, rng=None):
    """Likely outcome priced in [min_price, max_price] on deadline markets (or another side, see pick_side)."""
    out = []
    for m in markets:
        prices = binary(m)
        if not prices:
            continue
        b = base_filter(m, r)
        if not b:
            continue
        if r.get("fee_free_only") and fee_rate(m) > 0:
            continue
        i = pick_side(m, prices, r.get("side", "favorite"), rng)
        if i is not None and r["min_price"] <= prices[i] <= r["max_price"]:
            out.append(candidate(m, i, b[0], b[1]))
    if r.get("side") == "random":
        (rng or random).shuffle(out)
        return out
    if r.get("order") == "random":  # claude sandbox (2026-11-11): random pick among the "No" side, then the rest
        (rng or random).shuffle(out)
        out.sort(key=lambda c: not c["nothing_happens"])
        return out
    # "No, nothing happens" first, then fee-free if wanted, then sooner deadlines, then deepest markets
    out.sort(key=lambda c: (not c["nothing_happens"],
                            (c["fee_rate"] > 0) if r.get("prefer_fee_free") else 0,
                            c["days"] if r.get("prefer_fee_free") else 0,
                            -c["liquidity"]))
    return out


_day_change_cache = {}


def day_change(token):
    """(price ~24h ago, price now) for a token from Polymarket's price history, or None. Cached per run, since
    the panic-fade variants look at the same markets."""
    if token not in _day_change_cache:
        _day_change_cache[token] = _day_change(token)
    return _day_change_cache[token]


def _day_change(token):
    try:
        res = http_json(f"{DATA}/v2/prices-history", {"token_id": token, "interval": "1d"})
    except Exception as e:
        print(f"price history failed for {token[:12]}...: {e}")
        return None
    pts = envelope_rows(res, "data", "history", "points")
    series = []
    for p in pts:
        if isinstance(p, dict):
            px = fnum(pick(p, "p", "price", "value"), None)
            if px is not None:
                series.append(px)
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            series.append(fnum(p[1], None))
    series = [x for x in series if x is not None]
    if len(series) < 2:
        return None
    return series[0], series[-1]


def panic_candidates(markets, r):
    """Boring side that dropped >= min_drop over the last day from >= min_pre_price, nothing resolved yet.
    The market list only carries a 1-week change, so that shortlists; price history confirms the 1-day drop."""
    shortlist = []
    for m in markets:
        prices = binary(m)
        if not prices:
            continue
        chg = pick(m, "oneDayPriceChange", "oneWeekPriceChange")
        if chg is None:
            continue
        chg = fnum(chg)  # change of outcome 0's price
        if chg >= r["min_drop"] * 0.66:
            i = 1            # outcome 1 fell
        elif chg <= -r["min_drop"] * 0.66:
            i = 0            # outcome 0 fell
        else:
            continue
        if not (r["min_price"] <= prices[i] <= r["max_price"]):
            continue
        b = base_filter(m, r)
        if b:
            shortlist.append((abs(chg), m, i, b))
    shortlist.sort(key=lambda x: -x[0])
    out = []
    for _, m, i, b in shortlist[: r.get("max_history_checks", 40)]:
        tok = market_tokens(m)[i]
        dc = day_change(tok)
        print(f"  panic check: {str(m.get('question'))[:60]} -> 24h ago/now {dc}")
        if not dc:
            continue
        pre, cur = dc
        drop = pre - cur
        if drop < r["min_drop"] or pre < r["min_pre_price"] or not (r["min_price"] <= cur <= r["max_price"]):
            continue
        out.append(candidate(m, i, b[0], b[1], {"target": round(min(pre, 0.97), 4), "drop": round(drop, 4)}))
    out.sort(key=lambda c: (not c["nothing_happens"], -c["drop"], -c["liquidity"]))
    print(f"panic: {len(shortlist)} shortlisted, {len(out)} confirmed")
    return out


def momentum_candidates(markets, r):
    """direction 'up': the side that rose >= min_move this week (ride it); 'down': the side that fell (bet on a bounce).
    Uses the market list's one-week change, so it costs no extra API calls."""
    out = []
    for m in markets:
        prices = binary(m)
        chg = pick(m, "oneWeekPriceChange")
        if not prices or chg is None:
            continue
        chg = fnum(chg)  # change of outcome 0's price
        if abs(chg) < r["min_move"]:
            continue
        rose = 0 if chg > 0 else 1
        i = rose if r.get("direction", "up") == "up" else 1 - rose
        if not (r["min_price"] <= prices[i] <= r["max_price"]):
            continue
        b = base_filter(m, r)
        if b:
            out.append(candidate(m, i, b[0], b[1], {"move": round(abs(chg), 4)}))
    out.sort(key=lambda c: (-c["move"], -c["liquidity"]))
    return out


STORY_SKIP = {"will", "before", "after", "end", "out", "the", "this", "next", "new", "by", "in", "of", "be",
              "january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
              "november", "december", "trump", "donald", "us", "u.s.", "united", "states", "president", "prime",
              "minister", "leader", "party", "election", "world", "worlds", "gaming", "team"}


def story_names(title):
    """Names in a title (capitalised words), e.g. {'benjamin', 'netanyahu'}. Two markets sharing one are the same
    news story ('Netanyahu next leader out' and 'Netanyahu out by end of 2026'). Trump etc. are too common to count."""
    words = re.findall(r"[A-Z][\w'.-]{3,}", title or "")
    return {w.lower().strip(".'") for w in words} - STORY_SKIP


def buy_candidates(tracks, name, cands, limit):
    tc, tr, r = CFG["tracks"][name], tracks[name], rules_for(name)
    if tc.get("stopped"):
        return []  # Jan stopped this track: no new bets, open ones still settle (12 Nov 2026)
    held_events = {p.get("event_key") for p in tr["positions"].values()}
    held_names = set()
    if r.get("one_per_story"):
        for p in tr["positions"].values():
            held_names |= story_names(p.get("title"))
    themes = {}
    for p in tr["positions"].values():
        if p.get("theme"):
            themes[p["theme"]] = themes.get(p["theme"], 0) + 1
    n, bought = CFG["shares_per_trade"], []
    for c in cands:
        if len(bought) >= limit or len(tr["positions"]) >= r.get("max_open", 999):
            break
        if c["token"] in tr["positions"] or c["event_key"] in held_events:
            why(name, "already holds this market")
            continue
        if r.get("one_per_story") and story_names(c["title"]) & held_names:
            why(name, "already has a bet on this news story")
            continue
        if c["theme"] and themes.get(c["theme"], 0) >= r.get("max_per_theme", 999):
            why(name, "too many bets on this theme")
            continue
        px, shares, how = quote(c["token"], "buy", n, c["market"])
        if how != "book" and tc["source"] == "endgame":
            continue  # bug fix 2026-11-09: a decided market with no asks on the book can't be bought; the listed price is stale
        lo = r.get("min_price", 0.0)
        hi = r.get("max_price", 1.0) + 0.01
        if px is None or not (lo <= px <= hi):
            why(name, "no order book" if px is None else "real price outside its range")
            continue
        if r.get("max_over_listed") is not None and px > c["price"] + r["max_over_listed"]:
            continue  # thin book: the real ask is far above the listed price, so the backtest edge isn't there
        fee = taker_fee(shares, px, c["fee_rate"])
        if r.get("min_edge") is not None and (1 - px - fee / shares) < r["min_edge"]:
            why(name, "too little profit after the fee")
            continue  # too little left after paying the price and the fee
        if c.get("model_p") is not None and c["model_p"] - px - fee / shares < r.get("min_model_edge", 0):
            why(name, "real price ate the model's edge")
            continue  # weather/crypto: the real fill price ate the model's edge
        meta = {"title": c["title"], "outcome": c["outcome"], "slug": c["slug"], "event_slug": c["event_slug"],
                "event_key": c["event_key"], "theme": c["theme"], "end": c["end"], "source": name,
                "price_source": how}
        for k in ("target", "tier", "model_p", "signal"):
            if c.get(k):
                meta[k] = c[k]
        if r.get("tp_rel"):
            meta["target"] = round(min(0.99, px + r["tp_rel"]), 4)  # sell at entry + tp_rel
        if r.get("sl_rel"):
            meta["stop"] = round(max(0.01, px - r["sl_rel"]), 4)    # cut at entry - sl_rel
        if not paper_buy(tr, name, c["token"], shares, px, fee, meta):
            why(name, "out of cash")
            break
        held_events.add(c["event_key"])
        if r.get("one_per_story"):
            held_names |= story_names(c["title"])
        if c["theme"]:
            themes[c["theme"]] = themes.get(c["theme"], 0) + 1
        bought.append(f"{c['outcome']} @ {cents(px)} - {c['title'][:80]}")
    if len(tr["positions"]) >= r.get("max_open", 999):
        why(name, "full (max open bets)")
    saw(name, f"{len(cands)} market{'' if len(cands) == 1 else 's'} matched its rules, bought {len(bought)}")
    if bought and (CFG["push"].get("on_screener_buys") if tc["source"] != "endgame" else CFG["push"].get("on_endgame")):
        push(f"[{name}] bought {len(bought)} (practice money)", "\n".join(bought), tags="mag", track=name)
    return bought


def save_candidates(lists):
    out = {"generated": iso()}
    for k, cands in lists.items():
        out[k] = [{x: c[x] for x in ("title", "outcome", "price", "days", "liquidity", "fee_rate", "theme", "slug")
                   if x in c} | ({"target": c["target"], "drop": c["drop"]} if "drop" in c else {})
                  for c in cands[:30]]
    save("candidates.json", out)


def run_strategies(tracks, markets, panic_only=False):
    lists = {}
    st = load("scan_state.json", {})
    picked = st.setdefault("picked_on", {})
    today = now().strftime("%Y-%m-%d")
    for name, tc in CFG["tracks"].items():
        r = rules_for(name)
        if tc["source"] in ("screener", "random", "momentum") and not panic_only:
            if tc["source"] == "momentum":
                cands = momentum_candidates(markets, r)
            else:  # the random control is seeded by date + name, so a re-run picks the same coin flips
                cands = boring_side_candidates(markets, r, random.Random(f"{today}-{name}"))
            if picked.get(name) != today:  # one round of daily picks, even if the job is re-run
                buy_candidates(tracks, name, cands, r.get("picks_per_day", 1))
                picked[name] = today
            lists[name] = cands
        elif tc["source"] == "panic":
            cands = panic_candidates(markets, r)
            buy_candidates(tracks, name, cands, r.get("picks_per_scan", 1))
            lists[name] = cands
    save("scan_state.json", st)
    return lists


def panic_scan_due():
    hours = CFG["rules"].get("panic_fade", {}).get("scan_every_hours", 2)
    last = parse_iso(load("scan_state.json", {}).get("last_panic_scan"))
    return last is None or (now() - last).total_seconds() >= hours * 3600 - 300


# ================================================================ arbitrage: Kalshi x Polymarket
#
# Lessons built in (see README): most "gaps" are stale quotes or markets that only look the same
# (different deadline, resolution source, death/early-close clause). So the bot only PROPOSES pairs;
# a pair is traded only after its rules were read side by side and approved in arb_pairs.json.
# Prices come from both live order books, both sites' taker fees are paid, both legs are held to the end.

_kalshi_cache = {}


def arb_rules():
    return CFG["rules"]["arb"]


def arb_track_name():
    for n, tc in CFG["tracks"].items():
        if tc["source"] == "arb":
            return n
    return None


def load_pairs():
    try:
        with open(ARB_PAIRS) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        d = {}
    d.setdefault("approved", [])
    d.setdefault("rejected", [])
    return d


def kalshi_get(path, params=None):
    return http_json(f"{KALSHI}{path}", params)


def kalshi_market(ticker):
    if ticker in _kalshi_cache:
        return _kalshi_cache[ticker]
    m = None
    try:
        res = kalshi_get(f"/markets/{urllib.parse.quote(ticker)}")
        m = res.get("market") if isinstance(res, dict) else None
    except Exception as e:
        print(f"kalshi market lookup failed for {ticker}: {e}")
    _kalshi_cache[ticker] = m
    return m


def kpx(m, key):
    """Kalshi price in dollars: new '<key>_dollars' fields, old cent fields as fallback."""
    v = m.get(f"{key}_dollars")
    if v not in (None, ""):
        return fnum(v, None)
    v = m.get(key)
    return None if v in (None, "") else fnum(v, 0) / 100


def kalshi_asks(ticker):
    """(yes_asks, no_asks), ascending [(price, size)]. Kalshi's book lists only bids:
    buying YES at p means matching a NO bid at 1-p, and vice versa."""
    try:
        res = kalshi_get(f"/markets/{urllib.parse.quote(ticker)}/orderbook")
    except Exception as e:
        print(f"kalshi book failed for {ticker}: {e}")
        return None
    ob = (res.get("orderbook_fp") or res.get("orderbook") or {}) if isinstance(res, dict) else {}

    def bids(*keys):
        for k in keys:
            if ob.get(k):
                out = []
                for lvl in ob[k]:
                    if not isinstance(lvl, (list, tuple)) or len(lvl) < 2:
                        continue
                    p, s = fnum(lvl[0], None), fnum(lvl[1], 0)
                    if p is None or s <= 0:
                        continue
                    out.append((p / 100 if p > 1 else p, s))
                return out
        return []

    yes_bids, no_bids = bids("yes_dollars", "yes"), bids("no_dollars", "no")
    yes_asks = sorted(((round(1 - p, 6), s) for p, s in no_bids), key=lambda x: x[0])
    no_asks = sorted(((round(1 - p, 6), s) for p, s in yes_bids), key=lambda x: x[0])
    return yes_asks, no_asks


def kalshi_fee(shares, price):
    """Kalshi taker fee: 0.07 x contracts x p x (1-p), rounded UP to the cent, per order."""
    rate = arb_rules().get("kalshi_fee_rate", 0.07)
    return math.ceil(rate * shares * price * (1 - price) * 100 - 1e-9) / 100


def kalshi_payout(m, side):
    """Per-share payout of our Kalshi leg once settled, else None. Handles 'settled at a price'
    outcomes (e.g. Kalshi's death carve-out) through settlement_value_dollars."""
    if not m:
        return None
    res = str(m.get("result") or "").lower()
    if res in ("yes", "no"):
        return 1.0 if res == side else 0.0
    if str(m.get("status") or "").lower() in ("finalized", "settled"):
        v = fnum(m.get("settlement_value_dollars"), None)
        if v is not None:
            return v if side == "yes" else 1 - v
    return None


# ---- candidate pairs (daily): cheap text matching, then a human/Claude reads the rules

_STOP = set("will the a an be by in of to on at for and or is are this that with from as it its market "
            "which who what does do has have had get any next".split())
_SYN = {"cut": "decrease", "cuts": "decrease", "lower": "decrease", "lowers": "decrease", "reduce": "decrease",
        "hike": "increase", "hikes": "increase", "raise": "increase", "raises": "increase",
        "bp": "bps", "democrats": "democratic", "democrat": "democratic", "dem": "democratic",
        "dems": "democratic", "republicans": "republican", "gop": "republican", "u.s": "usa", "us": "usa",
        "america": "usa", "american": "usa", "wins": "win", "won": "win", "elected": "win",
        "nominee": "nomination", "nominated": "nomination", "out": "leave", "leaves": "leave",
        "resign": "leave", "resigns": "leave", "removed": "leave"}


_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"


def sig_numbers(text):
    """Numbers that define a market (strikes, counts, thresholds); years and calendar days are left out."""
    t = str(text or "").lower()
    t = re.sub(rf"\b({_MONTHS})[a-z]*\.?\s+\d{{1,2}}(st|nd|rd|th)?\b", " ", t)
    t = re.sub(rf"\b\d{{1,2}}(st|nd|rd|th)?\s+(of\s+)?({_MONTHS})[a-z]*", " ", t)
    nums = set()
    for n in re.findall(r"\d+(?:\.\d+)?", t.replace(",", "")):
        v = float(n)
        if 2000 <= v <= 2100 and "." not in n:
            continue
        nums.add(str(int(v)) if v == int(v) else str(v))
    return nums


def text_tokens(text):
    t = re.sub(r"[^a-z0-9.%$ ]+", " ", str(text or "").lower())
    t = re.sub(r"(\d)([a-z])", r"\1 \2", t)  # "25bps" -> "25 bps"
    out = set()
    for w in t.split():
        w = w.strip(".")
        if w and w not in _STOP:
            out.add(_SYN.get(w, w))
    return out


def kalshi_scan(r):
    out, cursor, seen = [], None, 0
    base = {"status": "open", "limit": 1000, "mve_filter": "exclude",
            "min_close_ts": int((now() + dt.timedelta(days=r["min_days"])).timestamp()),
            "max_close_ts": int((now() + dt.timedelta(days=r["max_days"])).timestamp())}
    for page in range(r.get("kalshi_max_pages", 150)):
        params = dict(base)
        if cursor:
            params["cursor"] = cursor
        try:
            res = kalshi_get("/markets", params)
        except Exception as e:
            print(f"kalshi scan page {page} failed: {e}")
            break
        ms = res.get("markets") or []
        seen += len(ms)
        for m in ms:
            t = str(m.get("ticker") or "")
            if any(t.startswith(p) for p in r.get("kalshi_skip_prefixes", [])) or \
                    any(s in t for s in r.get("kalshi_skip_contains", [])):
                continue
            if m.get("mve_collection_ticker") or str(m.get("market_type") or "binary") != "binary":
                continue
            if fnum(pick(m, "volume_fp", "volume")) < r["kalshi_min_volume"]:
                continue
            ya, na = kpx(m, "yes_ask"), kpx(m, "no_ask")
            if ya is None or na is None or not (0.02 <= ya <= 0.98) or not (0.02 <= na <= 0.98):
                continue
            close = parse_iso(m.get("close_time"))
            if not close:
                continue
            txt = f"{m.get('title', '')} {m.get('yes_sub_title', '')}"
            out.append({"m": m, "close": close, "ya": ya, "na": na, "toks": text_tokens(txt), "nums": sig_numbers(txt)})
        cursor = res.get("cursor")
        if not cursor or not ms:
            break
        time.sleep(0.05)
    print(f"kalshi: scanned {seen} open markets, kept {len(out)}")
    return out, seen


def arb_propose():
    """Find Kalshi/Polymarket markets that look like twins; save the best unreviewed ones with both rule texts."""
    r = arb_rules()
    pairs = load_pairs()
    decided = {p.get("id") for p in pairs["approved"] + pairs["rejected"]}
    # Whole Kalshi events whose rule text differs from Polymarket's for every choice (one review covers them all).
    blocked_events = {str(e.get("event") or "") for e in pairs.get("rejected_events", []) if isinstance(e, dict)}
    lo, hi = now() + dt.timedelta(days=r["min_days"]), now() + dt.timedelta(days=r["max_days"])
    poly = scan_markets({"end_date_min": iso(lo), "end_date_max": iso(hi), "liquidity_num_min": r["min_liquidity"]})
    P = []
    for m in poly:
        if m.get("closed") or m.get("acceptingOrders") is False or is_sports(m) or not binary(m):
            continue
        q = str(m.get("question") or "")
        if any(w in q.lower() for w in r.get("poly_skip_words", [])):
            continue
        end = parse_iso(m.get("endDate") or m.get("endDateIso"))
        bb, ba = fnum(m.get("bestBid"), None), fnum(m.get("bestAsk"), None)
        if end and bb is not None and ba is not None and 0 < ba <= 1:
            txt = f"{q} {m.get('groupItemTitle') or ''}"
            P.append({"m": m, "end": end, "toks": text_tokens(txt), "nums": sig_numbers(txt), "bb": bb, "ba": ba})
    K, k_seen = kalshi_scan(r)
    if not P or not K:
        save("arb_candidates.json", {"generated": iso(), "note": "scan failed or empty",
                                     "poly_markets": len(P), "kalshi_markets": len(K), "candidates": []})
        return

    df = Counter()
    for x in P + K:
        df.update(x["toks"])
    n_docs = len(P) + len(K)
    w = {t: math.log((n_docs + 1) / (c + 1)) + 1 for t, c in df.items()}
    norm = lambda ts: math.sqrt(sum(w[t] ** 2 for t in ts)) or 1.0
    for x in P + K:
        x["norm"] = norm(x["toks"])
    index = defaultdict(list)
    for i, x in enumerate(P):
        for t in x["toks"]:
            if df[t] <= r.get("max_df", 400):
                index[t].append(i)

    best_by_poly, dropped = {}, Counter()
    tol = r["date_tolerance_days"] * 86400
    max_diff = r.get("max_price_diff", 0.12)
    for k in K:
        if str(k["m"].get("event_ticker") or "") in blocked_events:
            dropped["event rejected as a whole"] += 1
            continue
        pool = Counter()
        for t in k["toks"]:
            for i in index.get(t, ()):
                pool[i] += 1
        k_mid = (k["ya"] + (1 - k["na"])) / 2
        best = None
        for i, _ in pool.most_common(60):
            p = P[i]
            if abs((p["end"] - k["close"]).total_seconds()) > tol:
                continue
            s = sum(w[t] ** 2 for t in k["toks"] & p["toks"]) / (k["norm"] * p["norm"])
            if s < r["min_match_score"]:
                continue
            # Twins must agree on their defining numbers (strike, count, threshold) ...
            if k["nums"] and p["nums"] and not (k["nums"] & p["nums"]):
                dropped["numbers differ"] += 1
                continue
            # ... and be priced alike. A big "gap" almost always means two different questions or a stale quote.
            p_mid = (p["bb"] + p["ba"]) / 2
            d_same, d_flip = abs(k_mid - p_mid), abs(k_mid - (1 - p_mid))
            flip = d_flip < d_same
            if min(d_same, d_flip) > max_diff:
                dropped["priced too differently"] += 1
                continue
            if best is None or s > best[0]:
                best = (s, i, flip)
        if not best:
            continue
        s, i, flip = best
        pid = f"{k['m'].get('ticker')}|{P[i]['m'].get('slug')}"
        if pid in decided:
            continue
        slug = P[i]["m"].get("slug")
        if slug not in best_by_poly or s > best_by_poly[slug][0]:
            best_by_poly[slug] = (s, k, P[i], flip)
    print(f"arb: dropped while matching: {dict(dropped)}")

    cands = []
    for s, k, p, flip in best_by_poly.values():
        km, pm = k["m"], p["m"]
        p_yes_ask, p_no_ask = p["ba"], 1 - p["bb"]
        if flip:  # Kalshi YES behaves like Polymarket No
            gap = 1 - min(k["ya"] + p_yes_ask, k["na"] + p_no_ask)
        else:
            gap = 1 - min(k["ya"] + p_no_ask, k["na"] + p_yes_ask)
        outs = [str(o) for o in jlist(pm.get("outcomes"))]
        guess = (outs[1] if flip else outs[0]) if len(outs) == 2 else "?"
        events = pm.get("events") or []
        ev = events[0] if events and isinstance(events[0], dict) else {}
        cands.append({
            "id": f"{km.get('ticker')}|{pm.get('slug')}", "match_score": round(s, 3),
            "est_gap_before_fees": round(gap, 4),
            "guess_poly_outcome_for_kalshi_yes": guess + " (price-based guess; verify from the rules)",
            "kalshi": {"ticker": km.get("ticker"), "event_ticker": km.get("event_ticker"), "title": km.get("title"),
                       "yes_sub_title": km.get("yes_sub_title"), "no_sub_title": km.get("no_sub_title"),
                       "close_time": km.get("close_time"), "can_close_early": km.get("can_close_early"),
                       "rules_primary": str(km.get("rules_primary") or "")[:1500],
                       "rules_secondary": str(km.get("rules_secondary") or "")[:800],
                       "yes_ask": k["ya"], "no_ask": k["na"], "volume": fnum(pick(km, "volume_fp", "volume"))},
            "polymarket": {"slug": pm.get("slug"), "question": pm.get("question"),
                           "outcomes": jlist(pm.get("outcomes")), "end": pm.get("endDateIso"),
                           "best_bid_yes": p["bb"], "best_ask_yes": p["ba"],
                           "liquidity": round(fnum(pick(pm, "liquidityNum", "liquidity"))),
                           "fee_rate": fee_rate(pm), "description": str(pm.get("description") or "")[:1800],
                           "url": market_link(str(pm.get("slug") or ""), str(ev.get("slug") or ""))},
        })
    # Review first the ones that look like twins AND would pay now (text match 0.6+, gap 2c+ before fees), then
    # the rest by how twin-like they look. Gap alone is a bad guide: the biggest "gaps" are almost all two
    # different questions (live test 2026-11-09), so the match score still has to vouch for them.
    min_gap, min_s = r.get("review_first_gap", 0.02), r.get("review_first_score", 0.6)
    hot = lambda c: c["match_score"] >= min_s and c["est_gap_before_fees"] >= min_gap
    cands.sort(key=lambda c: (not hot(c), -round(c["match_score"], 1), -c["est_gap_before_fees"]))
    save("arb_candidates.json", {"generated": iso(), "poly_markets": len(P), "kalshi_scanned": k_seen,
                                 "kalshi_kept": len(K), "matched_unreviewed": len(cands),
                                 "review_first": sum(hot(c) for c in cands),
                                 "how_to_review": "Compare kalshi.rules_* with polymarket.description. Approve only true "
                                                  "twins into arb_pairs.json (see 'about' there).",
                                 "candidates": cands[: r["max_candidates"]]})
    print(f"arb: {len(cands)} unreviewed twin candidates saved (top {r['max_candidates']})")


# ---- live check of approved pairs (every watch run)

def arb_check(tracks):
    name = arb_track_name()
    if not name:
        return
    tr, r = tracks[name], arb_rules()
    for pair in load_pairs()["approved"]:
        try:
            arb_check_pair(name, tr, pair, r)
        except Exception as e:
            print(f"arb check failed for {pair.get('id')}: {e}")


def arb_check_pair(name, tr, pair, r):
    pid = pair["id"]
    km, pm = kalshi_market(pair["kalshi"]), market_by_slug(pair["poly_slug"])
    if not km or not pm:
        return
    if str(km.get("status") or "").lower() not in ("active", "open") or pm.get("closed") \
            or pm.get("acceptingOrders") is False:
        return
    toks, outs = market_tokens(pm), [str(o) for o in jlist(pm.get("outcomes"))]
    want = str(pair.get("poly_outcome_for_kalshi_yes", "Yes"))
    if len(toks) != 2 or want not in outs:
        print(f"arb {pid}: outcome '{want}' not found in {outs}")
        return
    iy = outs.index(want)
    kb = kalshi_asks(pair["kalshi"])
    pb = {0: book(toks[0]), 1: book(toks[1])}
    if not kb or not pb[0] or not pb[1]:
        return
    shares = max(r["lot_shares"], pb[0]["min_size"], pb[1]["min_size"])
    ends = [d for d in (parse_iso(km.get("close_time")), parse_iso(pm.get("endDate") or pm.get("endDateIso"))) if d]
    days = max(1.0, (max(ends) - now()).total_seconds() / 86400 if ends else 30) + r["settle_buffer_days"]
    rate = fee_rate(pm)
    best = None
    # Bug fix 2026-11-09 (audit): repeat lots on one pair used to re-walk the same book, as if the shares our earlier
    # paper lots took were still for sale (4 lots in 15 minutes at the same price). Lots bought in the last hour now
    # count as taken: a new lot pays for the NEXT shares on the book.
    recent = now() - dt.timedelta(minutes=60)

    def used(k_side, tok):
        return sum(a["shares"] for a in tr["arbs"].values() if a["pair_id"] == pid and a["k_side"] == k_side
                   and a["poly_token"] == tok and parse_iso(a["opened"]) > recent)

    def next_px(levels, done, n):
        tot = walk(levels, done + n)
        if tot is None:
            return None
        return (tot * (done + n) - (walk(levels, done) * done if done > EPS else 0.0)) / n
    # leg A: Kalshi YES + Polymarket outcome that wins when Kalshi NO wins; leg B: the mirror image
    for k_side, k_levels, j in (("yes", kb[0], 1 - iy), ("no", kb[1], iy)):
        u = used(k_side, toks[j])
        pk, pp = next_px(k_levels, u, shares), next_px(pb[j]["asks"], u, shares)
        if pk is None or pp is None:
            continue
        kf, pf = kalshi_fee(shares, pk), taker_fee(shares, pp, rate)
        cost = shares * (pk + pp) + kf + pf
        net = shares - cost
        c = {"k_side": k_side, "pk": pk, "pp": pp, "kf": kf, "pf": pf, "cost": cost, "net": net,
             "edge": net / shares, "annual": (net / cost) * 365 / days if cost > 0 else 0,
             "p_tok": toks[j], "p_out": outs[j], "levels": [k_levels, pb[j]["asks"]]}
        if best is None or c["edge"] > best["edge"]:
            best = c
    if not best:
        return
    ok = best["edge"] >= r["min_edge"] and best["annual"] >= r["min_annual"]
    prev = tr["last_check"].get(pid, {})
    tr["last_check"][pid] = {"ts": iso(), "edge": round(best["edge"], 4), "annual": round(best["annual"], 3),
                             "opportunity": ok}
    if not ok:
        return
    if not prev.get("opportunity"):
        tr["opportunities"] += 1  # count each gap episode once, not every check while it lasts
        log_event({"type": "arb_opportunity", "track": name, "pair": pid, "edge": round(best["edge"], 4),
                   "annual": round(best["annual"], 3), "title": pm.get("question")})
    if sum(1 for a in tr["arbs"].values() if a["pair_id"] == pid) >= r["max_lots_per_pair"]:
        return
    if tr["cash"] + EPS < best["cost"]:
        tr["skipped_no_cash"] += 1
        log_event({"type": "skip_no_cash", "track": name, "title": pm.get("question"), "cost": round(best["cost"], 4)})
        return
    tr["cash"] = round(tr["cash"] - best["cost"], 6)
    tr["min_cash"] = round(min(tr["min_cash"], tr["cash"]), 6)
    aid = f"{pid}#{len(tr['closed']) + len(tr['arbs']) + 1}"
    tr["arbs"][aid] = {
        "pair_id": pid, "title": pm.get("question"), "shares": shares, "opened": iso(),
        "kalshi": pair["kalshi"], "k_side": best["k_side"], "k_price": round(best["pk"], 4), "k_fee": best["kf"],
        "poly_slug": pair["poly_slug"], "poly_token": best["p_tok"], "poly_outcome": best["p_out"],
        "p_price": round(best["pp"], 4), "p_fee": round(best["pf"], 4), "cost": round(best["cost"], 4),
        "expected_profit": round(best["net"], 4), "edge": round(best["edge"], 4), "annual": round(best["annual"], 3),
        "kalshi_close": km.get("close_time"), "poly_end": pm.get("endDateIso"),
    }
    try:
        fees = lambda n, px: kalshi_fee(n, px[0]) + taker_fee(n, px[1], rate)  # noqa: E731
        tr["arbs"][aid]["rs"] = {"s": {str(s): rs_pair_fill(s, best["levels"], r["min_edge"], 1.0, fees)
                                       for s in rs_sizes()}}
    except Exception as e:
        print(f"real-size arb failed: {e}")
    tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(a["cost"] for a in tr["arbs"].values())), 6)
    log_event({"type": "arb_open", "track": name, "title": pm.get("question"), "pair": pid,
               "price": round(best["pk"] + best["pp"], 4), "edge": round(best["edge"], 4)})
    if CFG["push"].get("on_arb") and not prev.get("opportunity"):  # one ping per gap, not per lot
        push(f"[arb] locked in {best['edge'] * 100:.1f}c a share",
             f"{pm.get('question')}\nKalshi {best['k_side'].upper()} {cents(best['pk'])} + Polymarket "
             f"{best['p_out']} {cents(best['pp'])}, fees ${best['kf'] + best['pf']:.2f}\n"
             f"{shares:.0f} shares: pays ${shares:.2f} at the end for ${best['cost']:.2f} (paper)",
             click=market_link(pair["poly_slug"]), tags="scales")


def arb_settle(tracks):
    name = arb_track_name()
    if not name:
        return
    tr = tracks[name]
    for aid in list(tr["arbs"]):
        a = tr["arbs"][aid]
        _kalshi_cache.pop(a["kalshi"], None)
        pk = kalshi_payout(kalshi_market(a["kalshi"]), a["k_side"])
        pp = resolved_payout(market_by_slug(a["poly_slug"]), a["poly_token"])
        if pk is None or pp is None:
            if (pk is None) != (pp is None) and not a.get("half_settled"):
                a["half_settled"] = iso()
                log_event({"type": "arb_half_settled", "track": name, "title": a["title"],
                           "kalshi_done": pk is not None, "poly_done": pp is not None})
            continue
        proceeds = a["shares"] * (pk + pp)
        pnl = proceeds - a["cost"]
        mismatch = abs(pk + pp - 1) > 0.01
        tr["cash"] = round(tr["cash"] + proceeds, 6)
        tr["realized"] = round(tr["realized"] + pnl, 6)
        rec = {**a, "k_payout": pk, "p_payout": pp, "pnl": round(pnl, 4), "mismatch": mismatch, "closed_at": iso()}
        if a.get("rs"):
            rec["rs_pnl"] = {k: [c, round(n * (pk + pp) - c, 4) if n > EPS else 0.0, f]
                             for k, (n, c, f) in a["rs"]["s"].items()}
        tr["closed"].append(rec)
        del tr["arbs"][aid]
        log_event({"type": "arb_close", "track": name, "title": a["title"], "pnl": round(pnl, 4),
                   "reason": "MISMATCH: the two sites resolved differently" if mismatch else "both legs resolved"})
        if mismatch:
            tr["mismatches"] += 1
            push("[arb] MISMATCH: sites resolved differently",
                 f"{a['title']}\nKalshi paid ${pk:.2f}, Polymarket paid ${pp:.2f} a share. Result {usd(pnl)} (practice money). "
                 "This is the risk the experiment is measuring.", tags="rotating_light")


# ---- "is it proven?" (90% confidence that resolution mismatches are rarer than the edge)

def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def upper90(k, n):
    """One-sided 90% upper bound on the mismatch rate after k mismatches in n arbs (Clopper-Pearson)."""
    if n == 0:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) > 0.10:
            lo = mid
        else:
            hi = mid
    return hi


def proof(n, k, e, realized, what="trades", bad="bad outcomes"):
    """90% test for 'small sure profit vs rare big loss' strategies (arbs, endgame, full sets).
    A good trade earns about e per share; a bad one loses about the whole $1, so the strategy only pays if
    bad outcomes happen less often than about e (2.5c edge -> under 1 in 40). After k bad outcomes in n,
    upper90 gives the highest bad-rate still plausible at 90% confidence; proven = that is below e."""
    ub = upper90(k, n)
    proven = n >= 20 and ub < e and realized > 0
    need = 0
    if not proven:
        m = max(n, 1)
        while upper90(k, m) >= e and m < n + 5000:
            m += 1
        need = max(m - n, 20 - n, 0)
    if n == 0:
        verdict = (f"Not proven yet: no finished {what}. Each one earns about {e * 100:.1f}c a share, so it needs about "
                   f"{need} finished {what} with no {bad} before we can be 90% sure it's not luck.")
    elif proven:
        verdict = (f"PROVEN: {n} finished {what}, {k} {bad}, profit ${realized:.2f}. That's enough to be 90% sure "
                   f"the {bad} are too rare to eat the {e * 100:.1f}c a share it earns.")
    else:
        verdict = (f"Not proven yet: {n} finished {what}, {k} {bad}, profit {usd(realized)}. It needs about "
                   f"{need} more with no {bad} to be 90% sure it's not luck.")
    return {"finished": n, "mismatches": k, "avg_edge": round(e, 4), "bad_rate_upper90": round(ub, 4),
            "proven": proven, "more_needed": need, "verdict": verdict}


def arb_proof(tr):
    closed = tr["closed"]
    edges = [c["edge"] for c in closed] + [a["edge"] for a in tr["arbs"].values()]
    e = sum(edges) / len(edges) if edges else arb_rules()["min_edge"]
    return proof(len(closed), sum(1 for c in closed if c.get("mismatch")), e, tr["realized"], "arbs", "mismatches")


# ================================================================ endgame: decided but not paid out yet
#
# Tiers (strongest first): 'resolved' = oracle says resolved but trading still open; 'proposed' = a result was
# submitted and is in its 2-hour challenge window; 'past_deadline' = end date passed, nothing submitted yet;
# 'ending_soon' = ends within a day and the boring side is at 95c+. Disputed markets are skipped.
# Every trade records its tier, so the stats show which signals are actually safe.

def endgame_candidates(r):
    f = {"end_date_min": iso(now() - dt.timedelta(days=r["past_deadline_max_days"])),
         "end_date_max": iso(now() + dt.timedelta(hours=r["ending_soon_hours"])),
         "liquidity_num_min": r["min_liquidity"]}
    out, order = [], {t: i for i, t in enumerate(r["tiers"])}
    for m in scan_markets(f):
        prices = binary(m)
        if not prices or m.get("closed") or m.get("acceptingOrders") is False:
            continue
        q = str(m.get("question") or "")
        if any(w in q.lower() for w in r.get("skip_words", [])):
            continue
        st = [str(s).lower() for s in jlist(m.get("umaResolutionStatuses"))]
        if any("disput" in s for s in st):
            continue
        i = 0 if prices[0] >= prices[1] else 1
        if not (r.get("fav_min_price", r["min_price"]) <= prices[i] <= r.get("fav_max_price", r["max_price"])):
            continue
        if r.get("only_words") and not any(w in q.lower() for w in r["only_words"]):
            continue
        end = parse_iso(m.get("endDate") or m.get("endDateIso"))
        if "resolved" in st:
            tier, days = "resolved", 0.2
        elif st and st[-1] == "proposed":
            tier, days = "proposed", 0.3
        elif end and end < now():
            tier, days = "past_deadline", 3.0
        elif end and (end - now()).total_seconds() <= r["ending_soon_hours"] * 3600:
            tier, days = "ending_soon", (end - now()).total_seconds() / 86400 + 1
        else:
            continue
        if tier not in order:
            continue  # variants that only trust some signals
        if tier in ("past_deadline", "ending_soon") and is_sports(m):
            continue  # a live game past its start time is not "decided"
        if tier in ("past_deadline", "ending_soon") and any(w in q.lower() for w in r.get("weak_tier_skip_words", [])):
            continue  # an election past its date is not "decided" until a result is proposed (votes still counting)
        liq = fnum(pick(m, "liquidityNum", "liquidity"))
        per_day = (1 - prices[i]) / max(days, 0.1)
        if r.get("fade"):
            i = 1 - i  # fade_sure: buy the cheap side of the "sure thing" (min/max_price then apply to what we buy)
        c = candidate(m, i, days, liq, {"tier": tier})
        c["per_day"] = per_day
        out.append(c)
    out.sort(key=lambda c: (order.get(c["tier"], 9), -c["per_day"]))
    print(f"endgame: {len(out)} candidates " + str(dict(Counter(c['tier'] for c in out))))
    return out


def run_endgame(tracks):
    for name, tc in CFG["tracks"].items():
        if tc["source"] == "endgame" and not tc.get("stopped"):
            try:
                r = rules_for(name)
                buy_candidates(tracks, name, endgame_candidates(r), r.get("picks_per_scan", 2))
            except Exception as e:
                print(f"endgame {name} failed: {e}")


def endgame_tier_stats(tr):
    stats = defaultdict(lambda: [0, 0])
    for c in tr["closed"]:
        s = stats[c.get("tier", "?")]
        s[0] += 1
        s[1] += 1 if c["pnl"] < 0 else 0
    return {t: {"finished": v[0], "flips": v[1]} for t, v in stats.items()}


def endgame_proof(tr):
    closed = tr["closed"]
    edges = [1 - p["entry"] - p.get("entry_fee", 0) / p["shares"] for p in list(tr["positions"].values()) + closed]
    e = sum(edges) / len(edges) if edges else 0.02
    return proof(len(closed), sum(1 for c in closed if c["pnl"] < 0), e, tr["realized"], "trades", "flips")


# ================================================================ buy every horse: full sets of one event
#
# In a multi-candidate event exactly one outcome wins (if the list is complete):
#   all-YES set: one YES of each costs sum(asks), pays exactly $1   -> only on provably complete lists
#   all-NO set : one NO of each costs sum(no asks), pays $(n-1), or $n if an unlisted outcome wins -> always safe
# "Open" lists (negRiskAugmented: names can be added later) are skipped.

def fullset_rules():
    for n, tc in CFG["tracks"].items():
        if tc["source"] == "fullset":
            return n, rules_for(n)
    return None, None


def looks_complete(names, r):
    low = [str(x).lower() for x in names]
    if any(re.search(rf"\b{re.escape(w)}\b", x) for x in low for w in r["complete_words"]):
        return True
    lo_open = any(re.search(r"(<|under|below|less than|or fewer|or less|or lower|^0\b)", x) for x in low)
    hi_open = any(re.search(r"(\+|>|over|above|or more|or higher|more than)", x) for x in low)
    return lo_open and hi_open  # numeric buckets with open ends cover every value


def events_scan(r):
    out, cursor, seen = [], None, 0
    f = {"end_date_min": iso(now()), "end_date_max": iso(now() + dt.timedelta(days=r["max_days"]))}
    for page in range(r["events_pages"]):
        params = {"closed": "false", "limit": 100, **f}
        if cursor:
            params["after_cursor"] = cursor
        try:
            res = http_json(f"{GAMMA}/events/keyset", params)
        except Exception as e:
            if page == 0 and f:
                print(f"events scan with date filter failed ({e}); retrying without")
                f, cursor = {}, None
                continue
            print(f"events scan page {page} failed: {e}")
            break
        evs = envelope_rows(res, "events", "data")
        seen += len(evs)
        for e in evs:
            if not isinstance(e, dict) or not (e.get("negRisk") or e.get("enableNegRisk")) or e.get("negRiskAugmented"):
                continue
            ms = [m for m in (e.get("markets") or []) if isinstance(m, dict)]
            end = parse_iso(e.get("endDate"))
            if not end or end < now() or (end - now()).days > r["max_days"]:
                continue
            if r["min_markets"] <= len(ms) <= r["max_markets"]:
                out.append(e)
        cursor = res.get("next_cursor") if isinstance(res, dict) else None
        if not cursor or not evs:
            break
    print(f"every_horse: scanned {seen} events, {len(out)} closed-list multi-candidate events")
    return out


def yes_no_tokens(m):
    toks, outs = market_tokens(m), [str(o).lower() for o in jlist(m.get("outcomes"))]
    if len(toks) != 2 or len(outs) != 2 or "yes" not in outs or "no" not in outs:
        return None
    return toks[outs.index("yes")], toks[outs.index("no")]


def fullset_check(tracks):
    name, r = fullset_rules()
    if not name or CFG["tracks"][name].get("stopped"):
        return
    tr = tracks[name]
    if len(tr["sets"]) >= r["max_open"]:
        return
    shortlist = []
    for e in events_scan(r):
        ms = [m for m in e["markets"]]
        if any(m.get("closed") and (token_price_from_market(m, (yes_no_tokens(m) or ("", ""))[0]) or 0) > 0.5 for m in ms):
            continue  # someone already won
        live = [m for m in ms if not m.get("closed") and m.get("active") is not False]
        if len(live) < r["min_markets"] or any(m.get("acceptingOrders") is False for m in live):
            continue
        if any(yes_no_tokens(m) is None for m in live):
            continue
        asks = [fnum(m.get("bestAsk"), None) for m in live]
        bids = [fnum(m.get("bestBid"), None) for m in live]
        names = [m.get("groupItemTitle") or m.get("question") for m in ms]
        if None not in asks and looks_complete(names, r) and 1 - sum(asks) >= r["min_edge"] / 2:
            shortlist.append(("yes", e, live, 1 - sum(asks)))
        if None not in bids and len(live) <= r["max_no_set_outcomes"]:
            n = len(live)
            gap = (n - 1) - sum(1 - b for b in bids)
            if gap / (n - 1) >= r["min_edge"] / 2:
                shortlist.append(("no", e, live, gap / (n - 1)))
    shortlist.sort(key=lambda x: -x[3])
    print(f"every_horse: {len(shortlist)} sets look cheap on listed prices")
    near = sorted((v["edge"] for v in tr["seen"].values() if str(v.get("ts", ""))[:10] >= iso(now() - dt.timedelta(days=2))[:10]),
                  reverse=True)
    saw(name, f"{len(shortlist)} sets looked cheap on listed prices; none is cheap on the real order book yet"
              + (f" (closest {near[0] * 100:+.1f}c a share)" if near else "") + ".")
    bought = []
    for kind, e, live, _ in shortlist[:15]:
        if len(bought) >= r["picks_per_scan"] or len(tr["sets"]) >= r["max_open"]:
            break
        sid = f"{e.get('slug')}:{kind}"
        if sid in tr["sets"]:
            continue
        shares, legs, cost, ok, levels, rates = r["shares"], [], 0.0, True, [], []
        for m in live:
            yt, nt = yes_no_tokens(m)
            tok = yt if kind == "yes" else nt
            b = book(tok)
            px = walk(b["asks"], max(shares, b["min_size"])) if b else None
            if px is None:
                ok = False
                break
            fee = taker_fee(shares, px, fee_rate(m))
            levels.append(b["asks"])
            rates.append(fee_rate(m))
            cost += shares * px + fee
            legs.append({"slug": m.get("slug"), "token": tok, "name": m.get("groupItemTitle") or m.get("question"),
                         "price": round(px, 4), "fee": round(fee, 4)})
        if not ok:
            continue
        n = len(live)
        guaranteed = shares * (1 if kind == "yes" else n - 1)
        net = guaranteed - cost
        days = max(1.0, (parse_iso(e.get("endDate")) - now()).total_seconds() / 86400) + 3
        edge = net / guaranteed  # profit per $1 of guaranteed payout
        annual = (net / cost) * 365 / days if cost > 0 else 0
        seen = tr["seen"].get(sid, {})
        ok_now = edge >= r["min_edge"] and annual >= r["min_annual"]
        tr["seen"][sid] = {"ts": iso(), "edge": round(edge, 4), "opportunity": ok_now}
        if not ok_now:
            continue
        if not seen.get("opportunity"):
            tr["opportunities"] += 1
        if tr["cash"] + EPS < cost:
            tr["skipped_no_cash"] += 1
            log_event({"type": "skip_no_cash", "track": name, "title": e.get("title"), "cost": round(cost, 4)})
            continue
        tr["cash"] = round(tr["cash"] - cost, 6)
        tr["min_cash"] = round(min(tr["min_cash"], tr["cash"]), 6)
        tr["sets"][sid] = {"title": e.get("title"), "kind": kind, "n": n, "shares": shares, "legs": legs,
                           "cost": round(cost, 4), "guaranteed": guaranteed, "expected_profit": round(net, 4),
                           "edge": round(edge, 4), "annual": round(annual, 3), "end": e.get("endDate"), "opened": iso()}
        try:
            per = 1 if kind == "yes" else n - 1
            fees = lambda k, px: sum(taker_fee(k, p, rt) for p, rt in zip(px, rates))  # noqa: E731
            tr["sets"][sid]["rs"] = {"s": {str(sz): rs_pair_fill(sz, levels, r["min_edge"] * per, per, fees)
                                           for sz in rs_sizes()}}
        except Exception as ex:
            print(f"real-size set failed: {ex}")
        tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(s["cost"] for s in tr["sets"].values())), 6)
        log_event({"type": "set_open", "track": name, "title": e.get("title"), "kind": kind, "n": n,
                   "price": round(cost / shares, 4), "edge": round(edge, 4)})
        bought.append(f"all-{kind.upper()} x{n}: {e.get('title')} - pays ${guaranteed:.2f}"
                      f"{'+' if kind == 'no' else ''} for ${cost:.2f}")
    if bought and CFG["push"].get("on_fullset"):
        push(f"[every_horse] bought {len(bought)} full set(s)", "\n".join(bought), tags="horse")


def fullset_settle(tracks):
    name, _ = fullset_rules()
    if name:
        sets_settle(tracks, name, "every_horse", "incomplete list?")


def ladder_settle(tracks):
    name, _ = ladder_rules()
    if name:
        sets_settle(tracks, name, "ladder", "the two markets resolved in a way that should be impossible")


def sets_settle(tracks, name, tag, why):
    """Pays out finished multi-leg sets (every_horse full sets, ladder pairs). A set that pays less than its
    guaranteed amount is flagged loudly: that is the disaster these strategies bet against."""
    tr = tracks[name]
    for sid in list(tr["sets"]):
        s = tr["sets"][sid]
        pays = [resolved_payout(market_by_slug(l["slug"]), l["token"]) for l in s["legs"]]
        if any(p is None for p in pays):
            continue
        proceeds = s["shares"] * sum(pays)
        pnl = proceeds - s["cost"]
        bad = proceeds + 1e-6 < s["guaranteed"]
        tr["cash"] = round(tr["cash"] + proceeds, 6)
        tr["realized"] = round(tr["realized"] + pnl, 6)
        rec = {**s, "proceeds": round(proceeds, 4), "pnl": round(pnl, 4), "incomplete": bad, "closed_at": iso()}
        if s.get("rs"):
            rec["rs_pnl"] = {k: [c, round(k_ * sum(pays) - c, 4) if k_ > EPS else 0.0, f]
                             for k, (k_, c, f) in s["rs"]["s"].items()}
        tr["closed"].append(rec)
        del tr["sets"][sid]
        log_event({"type": "set_close", "track": name, "title": s["title"], "pnl": round(pnl, 4),
                   "reason": f"PAID LESS THAN GUARANTEED ({why})" if bad else "paid as expected"})
        if bad:
            tr["incomplete"] += 1
            push(f"[{tag}] SHORT: paid less than guaranteed",
                 f"{s['title']}: paid ${proceeds:.2f}, expected ${s['guaranteed']:.2f}. Result {usd(pnl)} (practice money).",
                 tags="rotating_light")


def fullset_proof(tr):
    closed = tr["closed"]
    edges = [c["edge"] for c in closed] + [s["edge"] for s in tr["sets"].values()]
    e = sum(edges) / len(edges) if edges else fullset_rules()[1]["min_edge"]
    return proof(len(closed), sum(1 for c in closed if c.get("incomplete")), e, tr["realized"], "sets", "short payouts")


def sets_proof(tr, r):
    closed = tr["closed"]
    edges = [c["edge"] for c in closed] + [s["edge"] for s in tr["sets"].values()]
    e = sum(edges) / len(edges) if edges else r["min_edge"]
    return proof(len(closed), sum(1 for c in closed if c.get("incomplete")), e, tr["realized"], "sets", "short payouts")


def fullset_summary(name, tr):
    locked = sum(s["cost"] for s in tr["sets"].values())
    expected = sum(s["expected_profit"] for s in tr["sets"].values())
    pr = fullset_proof(tr)
    wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr["sets"]), "closed": len(tr["closed"]), "wins": wins, "losses": len(tr["closed"]) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": 0,
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "locked": round(locked, 4),
             "expected_locked_profit": round(expected, 4), "gap_episodes": tr["opportunities"], "proof": pr}
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr['sets'])} | {len(tr['closed'])} ({wins}/{len(tr['closed']) - wins}) "
           f"| ${tr['cash']:.2f} | locked ${locked:.2f} (+${expected:.2f} expected); cheap sets found "
           f"{tr['opportunities']}; short payouts {tr['incomplete']} |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n", f"**Proof status:** {pr['verdict']}\n"]
    if tr["sets"]:
        lines.append("| Event | Set | Cost | Pays at end | Ends |\n|---|---|---|---|---|")
        for s in tr["sets"].values():
            lines.append(f"| {str(s['title'])[:60]} | all-{s['kind'].upper()} x{s['n']} | ${s['cost']:.2f} | "
                         f"${s['guaranteed']:.2f}{'+' if s['kind'] == 'no' else ''} | {str(s.get('end') or '')[:10]} |")
    else:
        lines.append("No open sets.")
    near = sorted(tr.get("seen", {}).items(), key=lambda x: -x[1]["edge"])[:5]
    if near:
        lines.append("\nClosest sets at last check (profit per $1 after fees):")
        lines += [f"- {sid}: {v['edge'] * 100:+.1f}c ({v['ts'][:16]} UTC)" for sid, v in near]
    return row, stats, lines


def arb_summary(name, tr):
    locked = sum(a["cost"] for a in tr["arbs"].values())
    expected = sum(a["expected_profit"] for a in tr["arbs"].values())
    pr = arb_proof(tr)
    wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr["arbs"]), "closed": len(tr["closed"]), "wins": wins, "losses": len(tr["closed"]) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": 0,
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "locked": round(locked, 4),
             "expected_locked_profit": round(expected, 4), "gap_episodes": tr["opportunities"],
             "mismatches": tr["mismatches"], "proof": pr}
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr['arbs'])} | {len(tr['closed'])} ({wins}/{len(tr['closed']) - wins}) "
           f"| ${tr['cash']:.2f} | locked ${locked:.2f} (+${expected:.2f} expected); gaps found {tr['opportunities']}; "
           f"mismatches {tr['mismatches']} |")
    pairs = load_pairs()
    cand = load("arb_candidates.json", {})
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n",
             f"**Proof status:** {pr['verdict']}\n",
             f"Approved twin pairs: {len(pairs['approved'])}, rejected: {len(pairs['rejected'])}, "
             f"new candidates waiting for review: {len(cand.get('candidates', []))}.\n"]
    if tr["arbs"]:
        lines.append("| Market | Kalshi leg | Polymarket leg | Cost | Pays at end | Ends |\n|---|---|---|---|---|---|")
        for a in tr["arbs"].values():
            lines.append(f"| {str(a['title'])[:60]} | {a['k_side'].upper()} {cents(a['k_price'])} | {a['poly_outcome']} "
                         f"{cents(a['p_price'])} | ${a['cost']:.2f} | ${a['shares']:.2f} | "
                         f"{str(a.get('poly_end') or a.get('kalshi_close') or '')[:10]}"
                         f"{' (one side settled ' + a['half_settled'][:10] + ')' if a.get('half_settled') else ''} |")
    else:
        lines.append("No open arbs.")
    watching = [(pid, c) for pid, c in tr.get("last_check", {}).items()]
    if watching:
        lines.append("\nLast check of approved pairs (best net edge per share after fees):")
        for pid, c in watching[:15]:
            lines.append(f"- {pid}: {c['edge'] * 100:+.1f}c ({c['ts'][:16]} UTC)")
    return row, stats, lines


# ================================================================ ladder: two markets of one Polymarket event that can't disagree
#
# Some events list the same question with different strikes or deadlines ("BTC above 110k / 120k on Dec 31",
# "ceasefire by Dec 31 / by Mar 31"). If the stricter one (A) says YES, the looser one (B) must say YES too.
# So NO on A + YES on B pays at least $1 whatever happens, and $2 if only B comes true. When the two together
# cost less than $1 after fees, that is a locked-in profit inside one site: same rules, same resolver, no
# cross-site mismatch. The daily job finds the families (state/ladder_pairs.json); the watch job prices them.

_LMON = "january|february|march|april|may|june|july|august|september|october|november|december|" \
        "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
_LDATE = re.compile(rf"\b({_LMON})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?\b"
                    rf"|\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({_LMON})\b(?:,?\s+(\d{{4}}))?"
                    rf"|\b({_LMON})\s+(\d{{4}})\b|\bq[1-4]\s+\d{{4}}\b|\b(?:end of|in)\s+\d{{4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b")
_LNUM = re.compile(r"[$€£]?\d[\d,]*(?:\.\d+)?\s*(?:k|m|b|bn|million|billion|trillion|%|bps|c)?\b", re.I)
_LUP = re.compile(r"\b(above|over|more than|at least|exceed|exceeds|or more|or higher|greater than|surpass)\b|\+")
_LDOWN = re.compile(r"\b(below|under|less than|at most|or lower|or less|fewer than)\b")
_LTOUCH = re.compile(r"\b(hit|hits|reach|reaches|dip|dips|fall to|falls to|drop to|drops to)\b")
_LMONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def ladder_rules():
    for n, tc in CFG["tracks"].items():
        if tc["source"] == "ladder":
            return n, rules_for(n)
    return None, None


def _lnum(s):
    s = s.lower().replace(",", "").strip()
    m = re.match(r"[$€£]?(\d+(?:\.\d+)?)\s*(.*)$", s)
    if not m:
        return None
    mult = {"k": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9, "trillion": 1e12}
    return float(m.group(1)) * mult.get(m.group(2).strip(), 1)


def ladder_template(text):
    """(text with dates -> <d> and numbers -> <n>, [date strings], [numbers]). Years alone stay text."""
    t = str(text or "").lower()
    dates = [m.group(0) for m in _LDATE.finditer(t)]
    t = _LDATE.sub(" <d> ", t)
    nums = []

    def rep(m):
        v = _lnum(m.group(0))
        if v is None or (1990 <= v <= 2100 and "." not in m.group(0) and "$" not in m.group(0)):
            return m.group(0)
        nums.append(v)
        return " <n> "
    t = _LNUM.sub(rep, t)
    return re.sub(r"\s+", " ", t).strip(), dates, nums


def _ldate_value(s, default_year):
    """'march 31, 2027' / '31 march' -> date, or None."""
    m = re.match(rf"({_LMON})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?", s)
    if m:
        mon, day, yr = m.group(1), m.group(2), m.group(3)
    else:
        m = re.match(rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({_LMON})(?:,?\s+(\d{{4}}))?", s)
        if not m:
            return None
        day, mon, yr = m.group(1), m.group(2), m.group(3)
    try:
        return dt.date(int(yr) if yr else default_year, _LMONTHS.index(mon[:3]) + 1, int(day))
    except ValueError:
        return None


def _only_differ_by(xs, ys, pair):
    """Lists are equal except at positions where (x, y) == pair (the strike or deadline itself)."""
    return len(xs) == len(ys) and all(x == y or (x, y) == pair for x, y in zip(xs, ys))


def ladder_pairs(markets, r):
    """[(A, B, kind)] where A's YES implies B's YES, from markets of one event. Conservative on purpose:
    a family is dropped unless its direction is clear from the words and its prices agree with it."""
    by_ev, stats = defaultdict(list), Counter()
    for m in markets:
        evs = m.get("events") or []
        ev = evs[0] if evs and isinstance(evs[0], dict) else {}
        if ev.get("negRisk") or ev.get("enableNegRisk") or m.get("negRisk"):
            continue  # one-winner lists are every_horse's job, never ladders
        if m.get("closed") or m.get("acceptingOrders") is False or not yes_no_tokens(m):
            continue
        if fnum(m.get("bestBid"), None) is None or fnum(m.get("bestAsk"), None) is None:
            continue
        k = str(ev.get("id") or ev.get("slug") or "")
        if k:
            by_ev[k].append(m)
    out = []
    for group in by_ev.values():
        if len(group) < 2:
            continue
        fams = defaultdict(list)
        for m in group:
            tq, dq, nq = ladder_template(m.get("question"))
            td, dd, nd = ladder_template(m.get("description"))
            fams[(tq, td)].append({"m": m, "dq": dq, "nq": nq, "dd": dd, "nd": nd,
                                   "end": parse_iso(m.get("endDate") or m.get("endDateIso"))})
        for (tq, td), fam in fams.items():
            if len(fam) < 2 or any(x["end"] is None for x in fam):
                continue
            words = tq.replace("<n>", " ").replace("<d>", " ")
            pairs, kind = [], None
            if all(len(x["nq"]) == 1 for x in fam) and len({x["nq"][0] for x in fam}) == len(fam) \
                    and len({tuple(x["dq"]) for x in fam}) == 1 and len({x["end"].date() for x in fam}) == 1:
                # strike ladder: only the strike differs (same dates, same deadline)
                if "between" in words or re.search(r"<n> ?(-|to) ?<n>|\bexactly\b|\btop\b", tq):
                    stats["skip range/rank"] += 1
                    continue
                if _LTOUCH.search(words):  # "hit X" can mean up or down: only the outcome arrows say which
                    labels = " ".join(str(x["m"].get("groupItemTitle") or "") for x in fam)
                    up, down = "↑" in labels or "(high)" in tq, "↓" in labels or "(low)" in tq
                else:
                    up, down = bool(_LUP.search(words)), bool(_LDOWN.search(words))
                if up == down:
                    stats["skip direction unclear"] += 1
                    continue
                kind = "strike"
                fam.sort(key=lambda x: x["nq"][0])
                for i, lo in enumerate(fam):
                    for hi in fam[i + 1:]:
                        a, b = (hi, lo) if up else (lo, hi)
                        pair = (a["nq"][0], b["nq"][0])
                        if _only_differ_by(a["nd"], b["nd"], pair) and a["dd"] == b["dd"]:
                            pairs.append((a, b))
                        else:
                            stats["skip rules text differs"] += 1
            elif len({tuple(x["nq"]) for x in fam}) == 1 and all(len(x["dq"]) == 1 for x in fam) \
                    and re.search(r"\b(by|before|until|prior to|no later than) <d>", tq):
                # deadline ladder: "X by <date>", only the date differs
                kind = "deadline"
                for x in fam:
                    x["dl"] = _ldate_value(x["dq"][0], x["end"].year)
                if any(x["dl"] is None for x in fam) or len({x["dl"] for x in fam}) != len(fam):
                    stats["skip dates unreadable"] += 1
                    continue
                fam.sort(key=lambda x: x["dl"])
                for i, a in enumerate(fam):
                    for b in fam[i + 1:]:
                        if a["end"] > b["end"]:
                            stats["skip end dates disagree"] += 1  # question and market end disagree: don't guess
                            continue
                        if _only_differ_by(a["dd"], b["dd"], (a["dq"][0], b["dq"][0])) and a["nd"] == b["nd"]:
                            pairs.append((a, b))
                        else:
                            stats["skip rules text differs"] += 1
            else:
                continue
            # Sanity check against the crowd: the stricter market should never trade far ABOVE the looser one.
            # A real mispricing is a few cents; a big gap means we read the family wrong.
            mid = lambda x: (fnum(x["m"]["bestBid"]) + fnum(x["m"]["bestAsk"])) / 2
            if any(mid(a) > mid(b) + r["max_price_disagree"] for a, b in pairs):
                stats[f"skip {kind} family, prices disagree"] += 1
                continue
            stats[f"{kind} families"] += 1
            out += [(a["m"], b["m"], kind) for a, b in pairs]
    return out, stats


def ladder_discover():
    """Daily: find the ladder families and save their pairs for the watch job."""
    name, r = ladder_rules()
    if not name or CFG["tracks"][name].get("stopped"):
        return
    ms = scan_markets({"end_date_min": iso(now() + dt.timedelta(days=r["min_days"])),
                       "end_date_max": iso(now() + dt.timedelta(days=r["max_days"])),
                       "liquidity_num_min": r["min_liquidity"]})
    pairs, stats = ladder_pairs(ms, r)
    rows = []
    for a, b, kind in pairs:
        evs = a.get("events") or [{}]
        rows.append({"id": f"{a.get('slug')}>{b.get('slug')}", "kind": kind,
                     "event": str((evs[0] if isinstance(evs[0], dict) else {}).get("slug") or ""),
                     "a": {"mid": str(a.get("id")), "slug": a.get("slug"), "q": a.get("question"),
                           "no_token": yes_no_tokens(a)[1]},
                     "b": {"mid": str(b.get("id")), "slug": b.get("slug"), "q": b.get("question"),
                           "yes_token": yes_no_tokens(b)[0]},
                     "end": max(a.get("endDate") or a.get("endDateIso") or "", b.get("endDate") or b.get("endDateIso") or "")})
    rows = rows[: r["max_pairs"]]
    save("ladder_pairs.json", {"generated": iso(), "markets_scanned": len(ms), "stats": dict(stats),
                               "pairs": len(rows), "list": rows})
    print(f"ladder: {len(rows)} pairs from {len(ms)} markets; {dict(stats)}")


def ladder_due():
    _, r = ladder_rules()
    last = parse_iso(load("scan_state.json", {}).get("last_ladder_check"))
    return r is not None and (not last or (now() - last).total_seconds() >= r["check_every_min"] * 60 - 30)


def gamma_markets_by_id(ids, batch=50):
    """Fresh listed prices for many markets at once."""
    ids, out = sorted(set(ids)), {}

    def one(chunk):
        try:
            res = http_json(f"{GAMMA}/markets", [("id", i) for i in chunk] + [("limit", len(chunk))])
            return [m for m in envelope_rows(res, "markets", "data") if isinstance(m, dict)]
        except Exception as e:
            print(f"ladder: market batch failed: {e}")
            return []
    with ThreadPoolExecutor(6) as ex:
        for ms in ex.map(one, [ids[i:i + batch] for i in range(0, len(ids), batch)]):
            for m in ms:
                out[str(m.get("id"))] = m
    return out


def ladder_check(tracks, force=False):
    name, r = ladder_rules()
    if not name or CFG["tracks"][name].get("stopped") or not (force or ladder_due()):
        return
    st = load("scan_state.json", {})
    st["last_ladder_check"] = iso()
    save("scan_state.json", st)
    tr = tracks[name]
    lp = load("ladder_pairs.json", {}).get("list", [])
    if not lp and not load("ladder_pairs.json", {}).get("generated"):
        # bug fix: the pair list was only built by the daily job, so a track added after it sat idle until tomorrow
        print("ladder: no pair list yet; building it now")
        ladder_discover()
        lp = load("ladder_pairs.json", {}).get("list", [])
    if not lp:
        saw(name, "No ladder pairs found in today's markets.")
        return
    fresh = gamma_markets_by_id([p["a"]["mid"] for p in lp] + [p["b"]["mid"] for p in lp])
    print(f"ladder: {len(lp)} pairs, fresh prices for {len(fresh)} markets")
    rate_guess = lambda m: fee_rate(m)
    short = []
    for p in lp:
        a, b = fresh.get(p["a"]["mid"]), fresh.get(p["b"]["mid"])
        if not a or not b or a.get("closed") or b.get("closed") or a.get("acceptingOrders") is False \
                or b.get("acceptingOrders") is False:
            continue
        bb_a, ba_b = fnum(a.get("bestBid"), None), fnum(b.get("bestAsk"), None)
        if bb_a is None or ba_b is None or ba_b <= 0:
            continue
        pa, pb = 1 - bb_a, ba_b  # listed NO ask of A, YES ask of B
        est = 1 - pa - pb - rate_guess(a) * pa * (1 - pa) - rate_guess(b) * pb * (1 - pb)
        if est >= r["min_edge"] - 0.005:
            short.append((est, p, a, b))
    short.sort(key=lambda x: -x[0])
    print(f"ladder: {len(short)} pairs look cheap on listed prices")
    saw(name, f"Checked {len(lp)} ladder pairs; {len(short)} looked cheap on listed prices.")
    bought = []
    for est, p, a, b in short[: r["books_per_check"]]:
        if len(bought) >= r["picks_per_check"] or len(tr["sets"]) >= r["max_open"]:
            break
        sid = p["id"]
        if sum(1 for k in tr["sets"] if k.split("#")[0] == sid) >= r["max_lots_per_pair"]:
            continue
        ka, kb = book(p["a"]["no_token"]), book(p["b"]["yes_token"])
        if not ka or not kb:
            continue
        shares = max(r["shares"], ka["min_size"], kb["min_size"])
        xa, xb = walk(ka["asks"], shares), walk(kb["asks"], shares)
        if xa is None or xb is None:
            continue
        fa, fb = taker_fee(shares, xa, fee_rate(a)), taker_fee(shares, xb, fee_rate(b))
        cost = shares * (xa + xb) + fa + fb
        net = shares - cost
        end = max(d for d in (parse_iso(a.get("endDate") or a.get("endDateIso")),
                              parse_iso(b.get("endDate") or b.get("endDateIso")), now()) if d)
        days = max(1.0, (end - now()).total_seconds() / 86400) + 3
        edge = net / shares
        annual = (net / cost) * 365 / days if cost > 0 else 0
        seen = tr["seen"].get(sid, {})
        ok_now = edge >= r["min_edge"] and annual >= r["min_annual"]
        tr["seen"][sid] = {"ts": iso(), "edge": round(edge, 4), "opportunity": ok_now}
        if not ok_now:
            continue
        if not seen.get("opportunity"):
            tr["opportunities"] += 1
        if tr["cash"] + EPS < cost:
            tr["skipped_no_cash"] += 1
            log_event({"type": "skip_no_cash", "track": name, "title": p["a"]["q"], "cost": round(cost, 4)})
            continue
        tr["cash"] = round(tr["cash"] - cost, 6)
        tr["min_cash"] = round(min(tr["min_cash"], tr["cash"]), 6)
        legs = [{"slug": p["a"]["slug"], "token": p["a"]["no_token"], "name": f"NO: {p['a']['q']}",
                 "price": round(xa, 4), "fee": round(fa, 4)},
                {"slug": p["b"]["slug"], "token": p["b"]["yes_token"], "name": f"YES: {p['b']['q']}",
                 "price": round(xb, 4), "fee": round(fb, 4)}]
        title = f"{p['a']['q']} / {p['b']['q']}"
        tr["sets"][f"{sid}#{len(tr['closed']) + len(tr['sets']) + 1}"] = {
            "title": title, "kind": p["kind"], "n": 2, "shares": shares, "legs": legs, "cost": round(cost, 4),
            "guaranteed": shares, "expected_profit": round(net, 4), "edge": round(edge, 4),
            "annual": round(annual, 3), "end": end.strftime("%Y-%m-%d"), "opened": iso(), "event": p.get("event")}
        tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(s["cost"] for s in tr["sets"].values())), 6)
        log_event({"type": "set_open", "track": name, "title": title, "kind": p["kind"], "n": 2,
                   "price": round(cost / shares, 4), "edge": round(edge, 4)})
        bought.append(f"NO {cents(xa)} on \"{p['a']['q']}\" + YES {cents(xb)} on \"{p['b']['q']}\": "
                      f"pays at least ${shares:.2f} for ${cost:.2f}")
    if bought and CFG["push"].get("on_fullset"):
        push(f"[ladder] locked {len(bought)} pair(s)", "\n".join(bought), tags="ladder", track=name)


def ladder_summary(name, tr):
    pr = sets_proof(tr, ladder_rules()[1])
    locked = sum(s["cost"] for s in tr["sets"].values())
    expected = sum(s["expected_profit"] for s in tr["sets"].values())
    wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr["sets"]), "closed": len(tr["closed"]), "wins": wins, "losses": len(tr["closed"]) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": 0,
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "locked": round(locked, 4),
             "expected_locked_profit": round(expected, 4), "gap_episodes": tr["opportunities"], "proof": pr}
    lp = load("ladder_pairs.json", {})
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr['sets'])} | {len(tr['closed'])} ({wins}/{len(tr['closed']) - wins}) "
           f"| ${tr['cash']:.2f} | locked ${locked:.2f} (+${expected:.2f} at least); watching {lp.get('pairs', 0)} pairs; "
           f"cheap pairs found {tr['opportunities']}; short payouts {tr['incomplete']} |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n", f"**Proof status:** {pr['verdict']}\n"]
    if tr["sets"]:
        lines.append("| Pair | Kind | Cost | Pays at end | Ends |\n|---|---|---|---|---|")
        for s in tr["sets"].values():
            lines.append(f"| {str(s['title'])[:80]} | {s['kind']} | ${s['cost']:.2f} | "
                         f"${s['guaranteed']:.2f} (or ${2 * s['guaranteed']:.2f}) | {str(s.get('end') or '')[:10]} |")
    else:
        lines.append("No open pairs.")
    near = sorted(tr.get("seen", {}).items(), key=lambda x: -x[1]["edge"])[:5]
    if near:
        lines.append("\nClosest pairs at last check (profit per $1 after fees):")
        lines += [f"- {sid[:90]}: {v['edge'] * 100:+.1f}c ({v['ts'][:16]} UTC)" for sid, v in near]
    return row, stats, lines


# ================================================================ Kalshi 15-minute crypto: late favorite maker (2026-11-09)
#
# From a Reddit post ("$50 to $3,000 on Kalshi 15-minute crypto with maker orders"). A few minutes before a window
# closes, rest a buy order on the side that's winning and hold it to the result. Makers pay no fee on these series
# (fee_type "quadratic", checked 2026-11-09). Backtest: kcrypto.py, backtest/kcrypto.md.
# Paper fills, conservative: we place a virtual bid and note how many contracts were already waiting at our price.
# After the close we read the real trade tape: if anything traded BELOW our price, every bid at our price (ours
# too) was used up, so we filled in full. Otherwise only sells AT our price count, and only after the queue that was
# ahead of us. Orders that never fill cost nothing. Cash for a resting order is set aside until it settles.

KMAKER_SOURCES = ("kmaker",)


def kmaker_names():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "kmaker"]


def kalshi_book_sides(ticker):
    """{'yes': [(price, size)...], 'no': [...]} bids, best first, or None."""
    try:
        res = kalshi_get(f"/markets/{urllib.parse.quote(ticker)}/orderbook")
    except Exception as e:
        print(f"kalshi book failed for {ticker}: {e}")
        return None
    ob = (res.get("orderbook_fp") or res.get("orderbook") or {}) if isinstance(res, dict) else {}
    out = {}
    for side in ("yes", "no"):
        lv = ob.get(f"{side}_dollars") or ob.get(side) or []
        rows = []
        for x in lv:
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                p, sz = fnum(x[0], None), fnum(x[1], 0)
                if p is not None and sz > 0:
                    rows.append((round(p / 100 if p > 1 else p, 4), sz))
        out[side] = sorted(rows, key=lambda r: -r[0])
    return out


KMAKER_SPOT = {"KXBTC15M": "BTCUSDT", "KXETH15M": "ETHUSDT", "KXSOL15M": "SOLUSDT", "KXXRP15M": "XRPUSDT",
               "KXDOGE15M": "DOGEUSDT", "KXHYPE15M": "HYPEUSDT", "KXBNB15M": "BNBUSDT"}
_kmaker_spot = {}


def kmaker_z(series, strike, minutes_left, side, open_ts=None):
    """How many 'typical moves until the close' Binance spot sits on our side of the strike (same formula as the
    backtest, kcrypto.zscore): last hour's 1-minute moves, scaled to the minutes left. None without data.
    open_ts (epoch seconds of the window's start) = move Binance onto Kalshi's price scale first (kc_maker_safe_usd,
    12 Nov, Jan said yes): Binance quotes in USDT and runs ~0.09% above the dollar index Kalshi settles on. The strike
    IS Kalshi's index at the start, so Binance then / strike = the gap (same as kcrypto.zscore_usd, backtest/kcloss.md)."""
    sym = KMAKER_SPOT.get(series)
    if not sym or not strike:
        return None
    if sym not in _kmaker_spot:
        try:
            ks = http_json(f"{BINANCE}/klines", {"symbol": sym, "interval": "1m", "limit": 62})
            closes = [fnum(k[4]) for k in ks]
            rets = [math.log(b / a) for a, b in zip(closes[:-1], closes[1:]) if a > 0 and b > 0][-60:]
            by_t = {int(fnum(k[0])) // 1000: fnum(k[4]) for k in ks}
            _kmaker_spot[sym] = (closes[-1], math.sqrt(sum(r * r for r in rets) / len(rets)), by_t) if len(rets) >= 30 else None
        except Exception as e:
            print(f"binance 1m klines failed for {sym}: {e}")
            _kmaker_spot[sym] = None
    got = _kmaker_spot[sym]
    if not got or got[1] <= 0:
        return None
    px, sd1, by_t = got
    if open_ts is not None:
        a, b = by_t.get(int(open_ts) - 60), by_t.get(int(open_ts) - 120)
        if not a:
            return None
        strike = strike * (((a + b) / 2 if b else a) / strike)
    z = (px - strike) / (sd1 * px * math.sqrt(max(minutes_left, 0.5)))
    return z if side == "yes" else -z


def kmaker_tick(p):
    return 0.001 if p >= 0.9 - 1e-9 or p < 0.1 else 0.01


def kmaker_price(r, bid, ask):
    """(our bid price, front_of_line) for the rule kind, or None to skip."""
    kind, lvl = r.get("kind", "improve"), r.get("level", 0.95)
    if kind == "level":
        if (bid + ask) / 2 < lvl - EPS or ask <= lvl + EPS:
            return None
        return lvl, lvl > bid + EPS
    if bid < lvl - EPS:
        return None
    if kind == "join":
        return bid, False
    p = round(bid + kmaker_tick(bid), 4)
    return (p, True) if p < ask - EPS else (bid, False)


def kmaker_open_markets(series):
    try:
        rows = kalshi_get("/markets", {"series_ticker": series, "status": "open", "limit": 10}).get("markets") or []
    except Exception as e:
        print(f"kalshi {series} list failed: {e}")
        return []
    return rows


def kmaker_place(tracks, names):
    t_now = now()
    books = {}
    for series in sorted({s for n in names for s in rules_for(n).get("series", [])}):
        for m in kmaker_open_markets(series):
            close = parse_iso(m.get("close_time"))
            if not close:
                continue
            left = (close - t_now).total_seconds() / 60
            for n in names:
                r = rules_for(n)
                if series not in r.get("series", []) or not (r.get("min_minutes_left", 0.75) <= left <= r.get("max_minutes_left", 5.5)):
                    continue
                tr = tracks[n]
                tk = m.get("ticker")
                if tk in tr["orders"] or tk in tr.get("done", []):
                    continue
                if tk not in books:
                    books[tk] = kalshi_book_sides(tk)
                bk = books[tk]
                if not bk or not bk["yes"] or not bk["no"]:
                    continue
                yb, ya = bk["yes"][0][0], round(1 - bk["no"][0][0], 4)
                if not (0 < yb < ya < 1):
                    continue
                side = "yes" if (yb + ya) / 2 >= 0.5 else "no"
                bid, ask = (yb, ya) if side == "yes" else (round(1 - ya, 4), round(1 - yb, 4))
                got = kmaker_price(r, bid, ask)
                if not got:
                    tr.setdefault("last_check", {})[series] = {"ts": iso(), "left": round(left, 1), "side": side,
                                                               "bid": bid, "ask": ask, "placed": False}
                    continue
                price, front = got
                z = None
                if r.get("min_spot_z") is not None:
                    z = kmaker_z(series, fnum(m.get("floor_strike"), None), left, side)
                    if z is None or z < r["min_spot_z"]:
                        tr.setdefault("last_check", {})[series] = {"ts": iso(), "left": round(left, 1), "side": side,
                                                                   "bid": bid, "ask": ask, "placed": False,
                                                                   "z": None if z is None else round(z, 2)}
                        continue
                zu = None
                if r.get("usd_gap"):   # second check on Kalshi's price scale (kc_maker_safe_usd)
                    zu = kmaker_z(series, fnum(m.get("floor_strike"), None), left, side,
                                  open_ts=(close - dt.timedelta(minutes=15)).timestamp())
                    if zu is None or zu < r["min_spot_z"]:
                        tr.setdefault("last_check", {})[series] = {"ts": iso(), "left": round(left, 1), "side": side,
                                                                   "bid": bid, "ask": ask, "placed": False,
                                                                   "z": round(z, 2), "z_usd": None if zu is None else round(zu, 2)}
                        continue
                queue = sum(sz for p, sz in bk[side] if abs(p - price) < 1e-6)
                shares = max(1, int(r.get("usd_per_order", 10) / price))
                cost = round(shares * price, 6)
                maybe_refill(tr, n, cost)
                if cost > tr["cash"] + EPS:
                    tr["skipped_no_cash"] += 1
                    continue
                tr["cash"] = round(tr["cash"] - cost, 6)
                tr["orders"][tk] = {"ticker": tk, "series": series, "title": f"{m.get('title')} ({m.get('yes_sub_title', '')})",
                                    "outcome": side, "side": side, "price": price, "front": front, "queue": round(queue, 2),
                                    "shares": shares, "cost": cost, "placed": iso(), "close": iso(close),
                                    "minutes_left": round(left, 2), "bid": bid, "ask": ask,
                                    "strike": fnum(m.get("floor_strike"), None),
                                    "spot_z": None if z is None else round(z, 2),
                                    **({"spot_z_usd": round(zu, 2)} if zu is not None else {})}
                tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(o["cost"] for o in tr["orders"].values())), 6)
                tr.setdefault("last_check", {})[series] = {"ts": iso(), "left": round(left, 1), "side": side,
                                                           "bid": bid, "ask": ask, "placed": True}
                log_event({"type": "kmaker_order", "track": n, "ticker": tk, "side": side, "price": price,
                           "shares": shares, "queue": round(queue, 2), "minutes_left": round(left, 2)})
                print(f"{n}: bid {side.upper()} {price * 100:.1f}c x{shares} on {tk} ({left:.1f} min left, "
                      f"queue ahead {queue:.0f}, best bid {bid * 100:.1f}c ask {ask * 100:.1f}c)")


def kalshi_trades(ticker, t0, t1, max_pages=40):
    """Trades in [t0, t1] (epoch seconds), newest first; (rows, complete)."""
    out, cur = [], None
    for _ in range(max_pages):
        p = {"ticker": ticker, "min_ts": int(t0), "max_ts": int(t1) + 1, "limit": 1000}
        if cur:
            p["cursor"] = cur
        res = kalshi_get("/markets/trades", p)
        out += res.get("trades") or []
        cur = res.get("cursor")
        if not cur or not res.get("trades"):
            return out, True
    return out, False


def kmaker_fill(o, trades, shares=None):
    """Contracts filled for a resting bid, from the real tape. -> (filled, through).
    Our paper bid isn't really in Kalshi's book, so it only gets what sellers really sold to the bids: contracts sold
    AT our price after the queue that was there first, plus every contract sold BELOW our price (those sellers would
    have hit our higher bid first). Bug fix 2026-11-10 (Jan: "Fix it", backtest/bigbets.md): before, one contract
    traded below our price counted the whole bid as filled, which filled losing bets fully and winners only partly
    on paper too kindly (kc_maker_early showed -$4.53 per $100, the real tape says about -$12)."""
    shares = o["shares"] if shares is None else shares
    t0 = parse_iso(o["placed"])
    at, below, through = 0.0, 0.0, False
    for t in trades:
        ts = parse_iso(t.get("created_time"))
        if ts is None or ts <= t0:
            continue
        if str(t.get("taker_side")) == o["side"]:
            continue  # a taker buying our side doesn't sell to a bid on our side
        yp = fnum(t.get("yes_price_dollars"), None)
        if yp is None:
            yp = fnum(t.get("yes_price"), 0) / 100
        px = yp if o["side"] == "yes" else round(1 - yp, 6)
        n = fnum(t.get("count_fp") or t.get("count"), 0)
        if abs(px - o["price"]) < 1e-6:
            at += n
        elif px < o["price"]:
            below += n
            through = True
    return max(0.0, min(float(shares), max(0.0, at - o.get("queue", 0)) + below)), through


def kmaker_settle(tracks, names):
    tapes, first = {}, {}
    for n in names:
        for tk, o in tracks[n]["orders"].items():
            first[tk] = min(first.get(tk, o["placed"]), o["placed"])
    for n in names:
        tr = tracks[n]
        for tk in list(tr["orders"]):
            o = tr["orders"][tk]
            close = parse_iso(o["close"])
            if now() < close + dt.timedelta(seconds=60):
                continue
            m = kalshi_market(tk)
            res = str((m or {}).get("result") or "").lower()
            if res not in ("yes", "no"):
                if now() - close > dt.timedelta(hours=6):
                    print(f"{n}: {tk} still has no result 6h after the close")
                continue
            if tk not in tapes:
                try:
                    tapes[tk] = kalshi_trades(tk, parse_iso(first[tk]).timestamp(), close.timestamp())
                except Exception as e:
                    print(f"{n}: trades for {tk} failed: {e}")
                    continue
            trades, complete = tapes[tk]
            filled, through = kmaker_fill(o, trades)
            tr["cash"] = round(tr["cash"] + o["cost"], 6)   # release the money set aside
            del tr["orders"][tk]
            tr["done"] = (tr.get("done", []) + [tk])[-300:]
            if filled <= EPS:
                tr["unfilled"] = tr.get("unfilled", 0) + 1
                tr.setdefault("unfilled_log", []).append({"ticker": tk, "won": res == o["side"], "price": o["price"]})
                tr["unfilled_log"] = tr["unfilled_log"][-500:]
                continue
            pay = 1.0 if res == o["side"] else 0.0
            cost = filled * o["price"]
            pnl = filled * pay - cost
            tr["cash"] = round(tr["cash"] - cost + filled * pay, 6)
            tr["realized"] = round(tr["realized"] + pnl, 6)
            rs = {}
            for usd_ in rs_sizes():
                want = usd_ / o["price"]
                f2 = max(0.0, min(want, kmaker_fill(o, trades, want)[0]))
                rs[str(usd_)] = [round(f2 * o["price"], 4), round(f2 * pay - f2 * o["price"], 4), round(f2 / want, 4)]
            rec = {**o, "shares": round(filled, 4), "entry": o["price"], "entry_fee": 0.0, "exit": pay, "exit_fee": 0.0,
                   "pnl": round(pnl, 6), "cost": round(cost, 6), "through": through, "tape_complete": complete,
                   "price_source": "book", "reason": "resolved", "closed_at": iso(), "opened": o["placed"], "rs_pnl": rs}
            tr["closed"].append(rec)
            log_event({"type": "kmaker_fill", "track": n, "ticker": tk, "side": o["side"], "price": o["price"],
                       "filled": round(filled, 2), "through": through, "pnl": round(pnl, 4)})
            print(f"{n}: {tk} {o['side'].upper()} {o['price'] * 100:.1f}c filled {filled:.0f}/{o['shares']} "
                  f"({'traded through' if through else 'at our price'}), result {res}, P&L {pnl:+.2f}")
            if pnl < 0 and push_allowed(n):
                push(f"[{n}] FLIP: a late favorite lost (${pnl:+.2f})",
                     f"{o['title']}\nBought {o['side'].upper()} at {cents(o['price'])} with {o['minutes_left']:.1f} min "
                     f"left. This is the risk the test is measuring.", tags="rotating_light", track=n)


def kmaker_cycle(tracks):
    names = kmaker_names()
    if not names:
        return
    for n in names:
        tracks[n].setdefault("orders", {})
    kmaker_settle(tracks, names)
    live = [n for n in names if not CFG["tracks"][n].get("stopped")]   # stopped tracks only settle what's open
    if live:
        kmaker_place(tracks, live)


def kmaker_summary(name, tr):
    closed = tr["closed"]
    wins = sum(1 for c in closed if c["pnl"] > 0)
    locked = sum(o["cost"] for o in tr.get("orders", {}).values())
    un = tr.get("unfilled_log", [])
    filled_won = wins / len(closed) if closed else None
    unf_won = sum(1 for u in un if u["won"]) / len(un) if un else None
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr.get("orders", {})), "closed": len(closed), "wins": wins, "losses": len(closed) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": tr["refills"],
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "unfilled": tr.get("unfilled", 0)}
    fr = f"{len(closed)} of {len(closed) + tr.get('unfilled', 0)} orders filled"
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr.get('orders', {}))} | {len(closed)} ({wins}/{len(closed) - wins}) "
           f"| ${tr['cash']:.2f} | {fr}; refills {tr['refills']} |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n"]
    if closed or un:
        a = f"{filled_won * 100:.0f}" if filled_won is not None else "-"
        b = f"{unf_won * 100:.0f}" if unf_won is not None else "-"
        lines.append(f"Picked-off check: filled orders won {a} in 100, unfilled ones would have won {b} in 100. "
                     "If filled orders win clearly less often, the fills are being picked off.\n")
        losses = [c for c in closed if c["pnl"] < 0]
        if losses:
            lines.append(f"Worst loss ${min(c['pnl'] for c in losses):+.2f}; average win "
                         f"${sum(c['pnl'] for c in closed if c['pnl'] > 0) / max(wins, 1):+.2f}.\n")
    last = tr.get("last_check", {})
    if last:
        lines.append("Last look per coin: " + "; ".join(
            f"{s.replace('KX', '').replace('15M', '')} {v['side']} {v['bid'] * 100:.1f}/{v['ask'] * 100:.1f}c "
            f"{v['left']}m {'bid' if v['placed'] else 'skip'}" for s, v in sorted(last.items())))
    return row, stats, lines


# ================================================================ Kalshi patient buyer, nearly-sure side (added 2026-11-12, UNTESTED)
#
# The gap it fills: every Kalshi test so far bought at the asking price and lost the cost of buying, or sat in the
# 15-minute crypto windows. This one is the patient buyer everywhere else. Once an hour it looks at every open
# Kalshi market, and where the likely side's best buy order stands at 90-97c with a gap of 2c+ to the asking price,
# it rests a $10 buy order 1c above the best one for about an hour. Sports only before the game (start time from
# Kalshi's own schedule), never the 15-minute crypto windows. One bet per market, held to the result.
# Paper fills from the REAL trade tape, like kc_maker: only contracts really sold at our price or lower while the
# order was resting, never more than was sold. Backtest: khouse.py, backtest/khouse.md (+$1.42 per $100 on 967
# bets, two samples, "Ahead, but could be luck"; every other price band and the live-sports version lost).
# What paper can't see: other robots may step in front of a real order. Only real orders can measure that.

KP_SPORT = re.compile(r"NCAA|NFL|NBA|MLB|NHL|WNBA|MLS|EPL|SERIEA|LALIGA|BUNDES|LIGUE|UCL|UEL|SOCCER|ATP|WTA|ITF|UFC|"
                      r"PGA|LPGA|NASCAR|F1|BOXING|CRICKET|IPL|RUGBY|AFL|LNB|KBO|NPB|EUROLEAGUE|GAME$|SPREAD|TOTAL|"
                      r"MATCH|GOAL|SCORE|ESPORT|CS2|LOL|DOTA|VALORANT|TENNIS|GOLF|NCAAF|NCAAMB|CFB|CBB")   # = launch.KSPORT
KP_NOT_SPORT = re.compile(r"BTC|ETH|SOL|XRP|DOGE|CRYPTO|BNB|SHIBA|HYPE|HIGH|LOWT|TEMP|RAIN|SNOW|WEATHER|HURR|MENTION|SAY")


KP_MS_KIND = Counter()


def kpatient_names():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "kpatient"]


def kpatient_is_sport(series):
    s = series.upper()
    return not KP_NOT_SPORT.search(s) and bool(KP_SPORT.search(s))


def kpatient_starts(max_pages=60):
    """{event ticker: start time} for scheduled games, from Kalshi's own schedule (milestones)."""
    out, cur = {}, None
    t0 = iso(now() - dt.timedelta(hours=8))
    for _ in range(max_pages):
        p = {"limit": 500, "minimum_start_date": t0}
        if cur:
            p["cursor"] = cur
        try:
            res = kalshi_get("/milestones", p)
        except Exception as e:
            print(f"kalshi schedule failed: {e}")
            break
        rows = res.get("milestones") or []
        for ms in rows:
            st = parse_iso(ms.get("start_date"))
            if not st:
                continue
            KP_MS_KIND[f"{ms.get('category')}|{ms.get('type')}"] += 1
            if str(ms.get("category") or "").lower() not in ("sports", "esports"):
                continue                      # election nights, data releases, gas prices: not games
            for ev in (ms.get("related_event_tickers") or []) + (ms.get("primary_event_tickers") or []):
                if ev not in out or st < out[ev]:
                    out[ev] = st
        cur = res.get("cursor")
        if not cur or not rows:
            break
    return out


def kpatient_open_markets(r, budget_s=150):
    """Every open Kalshi market that closes within list_days (sports markets carry a far-off official close)."""
    t_now, rows, cur, t0 = now(), [], None, time.time()
    hi = int((t_now + dt.timedelta(days=r.get("list_days", 16))).timestamp())
    for _ in range(600):
        p = {"status": "open", "limit": 1000, "mve_filter": "exclude", "min_close_ts": int(t_now.timestamp()), "max_close_ts": hi}
        if cur:
            p["cursor"] = cur
        try:
            res = kalshi_get("/markets", p)
        except Exception as e:
            print(f"kalshi open list failed after {len(rows)} rows: {e}")
            break
        got = res.get("markets") or []
        rows += got
        cur = res.get("cursor")
        if not cur or not got:
            break
        if time.time() - t0 > budget_s:
            print(f"kalshi open list: time budget used after {len(rows)} rows")
            break
    return rows


def kpatient_candidate(m, r, starts, t_now):
    """An order dict for this market if the rule fires, else a short reason (str)."""
    tk, ev = str(m.get("ticker") or ""), str(m.get("event_ticker") or "")
    series = ev.split("-")[0]
    if not tk or series.endswith("15M") or tk.startswith("KXMVE"):
        return "skipped kind"
    yb, ya = kpx(m, "yes_bid"), kpx(m, "yes_ask")
    if yb is None or ya is None or not (0 < yb < ya < 1):
        return "no two-sided price"
    side = "yes" if (yb + ya) / 2 >= 0.5 else "no"
    bid, ask = (yb, ya) if side == "yes" else (round(1 - ya, 4), round(1 - yb, 4))
    if not (r.get("min_bid", 0.90) - EPS <= bid < r.get("max_bid", 0.97) - EPS):
        return "outside 90-97c"
    if ask - bid < r.get("min_gap", 0.02) - EPS:
        return "gap too small"
    price = round(bid + r.get("improve", 0.01), 4)
    if price >= ask - EPS:
        return "gap too small"
    if fnum(m.get("volume_fp") or m.get("volume"), 0) < r.get("min_volume", 100):
        return "too little traded"
    rest = dt.timedelta(minutes=r.get("order_minutes", 65))
    far = t_now + dt.timedelta(days=r.get("max_days", 7))
    sport = kpatient_is_sport(series) or ev in starts
    if sport:
        st = starts.get(ev)
        if not st:
            return "sports, start time unknown"
        if st < t_now + dt.timedelta(minutes=r.get("sports_min_minutes_to_start", 75)):
            return "sports, game on or about to start"
        if st > far:
            return "too far off"
        expires = min(t_now + rest, st - dt.timedelta(minutes=10))
        end = parse_iso(m.get("expected_expiration_time")) or st + dt.timedelta(hours=4)
        end = max(end, st + dt.timedelta(hours=1))
    else:
        close = parse_iso(m.get("close_time"))
        if not close or close < t_now + dt.timedelta(minutes=10):
            return "closing now"
        if close > far:
            return "too far off"
        expires, end = min(t_now + rest, close), close
    shares = max(1, int(r.get("usd_per_order", 10) / price))
    return {"ticker": tk, "series": series, "event": ev, "title": f"{m.get('title')} ({m.get('yes_sub_title', '')})"[:140],
            "outcome": side, "side": side, "price": price, "front": True, "queue": 0.0, "shares": shares,
            "cost": round(shares * price, 6), "placed": iso(t_now), "expires": iso(expires), "close": iso(end),
            "bid": bid, "ask": ask, "kind": "sports" if sport else "other"}


def kpatient_place(tracks, names, markets=None, starts=None):
    t_now = now()
    for n in names:
        tr, r = tracks[n], rules_for(n)
        last = parse_iso(tr.get("last_scan"))
        if last and (t_now - last).total_seconds() < r.get("scan_minutes", 55) * 60:
            continue
        if markets is None:
            markets = kpatient_open_markets(r)
            starts = kpatient_starts()
        if not markets:
            continue
        tr["last_scan"] = iso(t_now)
        why, cands = Counter(), []
        busy = {o.get("event") for o in tr["orders"].values()} | set(tr.get("done", []))
        for m in markets:
            c = kpatient_candidate(m, r, starts, t_now)
            if isinstance(c, str):
                why[c] += 1
            elif c["ticker"] in tr["orders"] or c["event"] in busy:
                why["already bet or waiting"] += 1   # one bet per event (the backtest took one market per event)
            else:
                cands.append(c)
        random.Random(int(t_now.timestamp())).shuffle(cands)   # more candidates than money: pick blindly, not by looks
        resting = sum(1 for o in tr["orders"].values() if not o.get("filled"))
        placed = 0
        for c in cands:
            if c["event"] in busy:
                continue
            if resting >= r.get("max_resting", 40):
                break
            if c["cost"] > tr["cash"] + EPS:
                tr["skipped_no_cash"] += 1
                break
            tr["cash"] = round(tr["cash"] - c["cost"], 6)
            tr["orders"][c["ticker"]] = c
            busy.add(c["event"])
            resting += 1
            placed += 1
            log_event({"type": "kpatient_order", "track": n, "ticker": c["ticker"], "side": c["side"], "price": c["price"],
                       "shares": c["shares"], "kind": c["kind"]})
        tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(o["cost"] for o in tr["orders"].values())), 6)
        tr["last_check"] = {"ts": iso(t_now), "markets": len(markets), "games_with_start": len(starts or {}),
                            "fit": len(cands), "placed": placed, "why_not": dict(why.most_common(8))}
        print(f"{n}: looked at {len(markets)} open Kalshi markets, {len(cands)} fit the rule, placed {placed} "
              f"orders ({resting} waiting). Skipped: {dict(why.most_common(6))}")


_kp_fee = {}


def kpatient_maker_fee(series, shares, price):
    """Most Kalshi series charge the patient side nothing; a few ("..._with_maker_fees") charge a quarter of the usual fee."""
    if series not in _kp_fee:
        try:
            s = kalshi_get(f"/series/{urllib.parse.quote(series)}").get("series") or {}
            _kp_fee[series] = (str(s.get("fee_type") or ""), fnum(s.get("fee_multiplier"), 1) or 1)
        except Exception as e:
            print(f"kalshi series {series} failed: {e}")
            return math.ceil(0.0175 * shares * price * (1 - price) * 100 - 1e-9) / 100   # unknown: assume the fee
    ft, mult = _kp_fee[series]
    if "maker" not in ft:
        return 0.0
    return math.ceil(0.0175 * mult * shares * price * (1 - price) * 100 - 1e-9) / 100


def kpatient_window(o, trades):
    """Trades that could have filled the order: from a minute after it was placed until it was pulled."""
    a, b = parse_iso(o["placed"]) + dt.timedelta(seconds=60), parse_iso(o["expires"])
    out = []
    for t in trades:
        ts = parse_iso(t.get("created_time"))
        if ts is not None and a < ts <= b:
            out.append(t)
    return out


def kpatient_settle(tracks, names):
    t_now = now()
    for n in names:
        tr = tracks[n]
        for tk in list(tr["orders"]):
            o = tr["orders"][tk]
            if not o.get("filled"):
                # 1) the order's hour is over: did anybody really sell to it?
                if t_now < parse_iso(o["expires"]) + dt.timedelta(seconds=30):
                    continue
                try:
                    trades, complete = kalshi_trades(tk, parse_iso(o["placed"]).timestamp(), parse_iso(o["expires"]).timestamp())
                except Exception as e:
                    print(f"{n}: trades for {tk} failed: {e}")
                    continue
                win = kpatient_window(o, trades)
                o0 = {**o, "placed": "1970-01-01T00:00:00Z"}
                filled, through = kmaker_fill(o0, win)
                if filled <= EPS:
                    tr["cash"] = round(tr["cash"] + o["cost"], 6)
                    del tr["orders"][tk]
                    tr["unfilled"] = tr.get("unfilled", 0) + 1
                    continue
                fee = kpatient_maker_fee(o["series"], filled, o["price"])
                cost = round(filled * o["price"] + fee, 6)
                tr["cash"] = round(tr["cash"] + o["cost"] - cost, 6)
                rs = {}
                for usd_ in rs_sizes():
                    want = usd_ / o["price"]
                    rs[str(usd_)] = round(max(0.0, min(want, kmaker_fill(o0, win, want)[0])), 4)
                o.update({"filled": round(filled, 4), "shares": round(filled, 4), "cost": cost, "entry_fee": fee,
                          "through": through, "tape_complete": complete, "rs_fill": rs, "filled_at": iso(t_now),
                          "chance": o["price"], "what": f"bought {o['side'].upper()} on Kalshi, waiting for the result"})
                tr["done"] = (tr.get("done", []) + [o["event"]])[-3000:]   # events we already hold or held a bet in
                log_event({"type": "kpatient_fill", "track": n, "ticker": tk, "side": o["side"], "price": o["price"],
                           "filled": round(filled, 2), "through": through})
                print(f"{n}: {tk} {o['side'].upper()} {o['price'] * 100:.0f}c: {filled:.0f} contracts really sold to us")
                continue
            # 2) a held bet: is the result in?
            nxt = parse_iso(o.get("check_after") or o["close"])
            if t_now < nxt:
                continue
            m = kalshi_market(tk)
            res = str((m or {}).get("result") or "").lower()
            if res not in ("yes", "no"):
                o["check_after"] = iso(t_now + dt.timedelta(minutes=30))
                if t_now - parse_iso(o["close"]) > dt.timedelta(days=3):
                    print(f"{n}: {tk} still has no result 3 days after its expected end")
                continue
            pay = 1.0 if res == o["side"] else 0.0
            sh, fee = o["shares"], o.get("entry_fee", 0.0)
            pnl = sh * pay - o["cost"]
            tr["cash"] = round(tr["cash"] + sh * pay, 6)
            tr["realized"] = round(tr["realized"] + pnl, 6)
            rs = {}
            for usd_, f2 in (o.get("rs_fill") or {}).items():
                want = float(usd_) / o["price"]
                fee2 = fee * f2 / sh if sh else 0.0
                rs[usd_] = [round(f2 * o["price"] + fee2, 4), round(f2 * pay - f2 * o["price"] - fee2, 4), round(f2 / want, 4)]
            del tr["orders"][tk]
            rec = {**o, "entry": o["price"], "exit": pay, "exit_fee": 0.0, "pnl": round(pnl, 6),
                   "price_source": "book", "reason": "resolved", "closed_at": iso(), "opened": o["placed"], "rs_pnl": rs}
            for k in ("chance", "what", "rs_fill", "check_after"):
                rec.pop(k, None)
            tr["closed"].append(rec)
            log_event({"type": "kpatient_result", "track": n, "ticker": tk, "side": o["side"], "price": o["price"],
                       "shares": sh, "pnl": round(pnl, 4)})
            print(f"{n}: {tk} {o['side'].upper()} {o['price'] * 100:.0f}c x{sh:.0f}: result {res}, P&L {pnl:+.2f}")
            if pnl < 0 and push_allowed(n):
                push(f"[{n}] FLIP: a nearly-sure bet lost (${pnl:+.2f})",
                     f"{o['title']}\nBought {o['side'].upper()} at {cents(o['price'])}. One loss like this eats about "
                     f"15 wins. This is the risk the test is measuring.", tags="rotating_light", track=n)


def kpatient_cycle(tracks):
    names = kpatient_names()
    if not names:
        return
    for n in names:
        tracks[n].setdefault("orders", {})
    kpatient_settle(tracks, names)
    live = [n for n in names if not CFG["tracks"][n].get("stopped")]
    if live:
        kpatient_place(tracks, live)


def kpatient_summary(name, tr):
    closed = tr["closed"]
    wins = sum(1 for c in closed if c["pnl"] > 0)
    held = [o for o in tr.get("orders", {}).values() if o.get("filled")]
    resting = len(tr.get("orders", {})) - len(held)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr.get("orders", {})), "closed": len(closed), "wins": wins, "losses": len(closed) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": tr["refills"],
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "unfilled": tr.get("unfilled", 0)}
    orders_all = len(closed) + len(held) + tr.get("unfilled", 0)
    row = (f"| {name} | {tr['realized']:+.2f} | {len(held)} bought, {resting} waiting | {len(closed)} ({wins}/{len(closed) - wins}) "
           f"| ${tr['cash']:.2f} | {len(closed) + len(held)} of {orders_all} hourly orders got sold to |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n"]
    if closed:
        losses = [c for c in closed if c["pnl"] < 0]
        staked = sum(c["cost"] for c in closed)
        lines.append(f"Finished bets: {len(closed)}, put in ${staked:.2f}, P&L ${tr['realized']:+.2f} "
                     f"({tr['realized'] / staked * 100:+.2f} per $100)." if staked else "")
        if losses:
            lines.append(f"Worst loss ${min(c['pnl'] for c in losses):+.2f}; average win "
                         f"${sum(c['pnl'] for c in closed if c['pnl'] > 0) / max(wins, 1):+.2f}.\n")
        by = defaultdict(list)
        for c in closed:
            by[c.get("kind", "other")].append(c)
        lines.append("By kind: " + "; ".join(f"{k} {len(v)} bets ${sum(c['pnl'] for c in v):+.2f}" for k, v in sorted(by.items())))
    lc = tr.get("last_check") or {}
    if lc:
        lines.append(f"\nLast look {str(lc.get('ts', ''))[:16]} UTC: {lc.get('markets')} open markets, {lc.get('fit')} fit the rule, "
                     f"{lc.get('placed')} orders placed. Skipped: {lc.get('why_not')}")
    return row, stats, lines


# ================================================================ econ_fav: forecast backs the favorite (added 2026-11-09)
#
# Kalshi data-release markets (CPI, core CPI, CPI year-on-year, jobless claims, unemployment, payrolls). 20-76 hours
# before the release, buy the side that costs 80-99c (with the fee) when a free forecast says it is worth at least 3c
# more: Cleveland Fed inflation nowcast for CPI, 'same as last time' from FRED for the jobs numbers (econ.py).
# Backtest (backtest/econ.md, 2021-2026): +$6.73 per $100 at 24h and +$7.75 at 72h, both halves ahead, still ahead at
# 2c worse prices; the same price band WITHOUT the forecast lost about $5 per $100. Held to the result. Real book fills.

def econ_names():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "econ"]


def econ_settle(tracks, names):
    for n in names:
        tr = tracks[n]
        for tk in list(tr["orders"]):
            o = tr["orders"][tk]
            close = parse_iso(o["close"])
            if now() < close + dt.timedelta(seconds=60):
                continue
            m = kalshi_market(tk)
            res = str((m or {}).get("result") or "").lower()
            if res not in ("yes", "no"):
                if now() - close > dt.timedelta(hours=12):
                    print(f"{n}: {tk} still has no result 12h after the close")
                continue
            pay = 1.0 if res == o["side"] else 0.0
            pnl = o["shares"] * pay - o["cost"]
            tr["cash"] = round(tr["cash"] + o["shares"] * pay, 6)
            tr["realized"] = round(tr["realized"] + pnl, 6)
            del tr["orders"][tk]
            tr["done"] = (tr.get("done", []) + [tk])[-500:]
            rs = {k: [v[0], round(v[1] * pay - v[0], 4), v[2]] for k, v in (o.get("rs") or {}).items()}
            tr["closed"].append({**o, "exit": pay, "exit_fee": 0.0, "pnl": round(pnl, 6), "reason": "resolved",
                                 "closed_at": iso(), "opened": o["placed"], "rs_pnl": rs})
            log_event({"type": "econ_settle", "track": n, "ticker": tk, "side": o["side"], "pnl": round(pnl, 4)})
            print(f"{n}: {tk} {o['side'].upper()} result {res}, P&L {pnl:+.2f}")
            if pnl < 0 and push_allowed(n):
                push(f"[{n}] FLIP: a forecast-backed favorite lost (${pnl:+.2f})",
                     f"{o['title']}\nBought {o['side'].upper()} at {cents(o['entry'])}, forecast said {o['chance'] * 100:.0f} in 100.",
                     tags="rotating_light", track=n)


def econ_place(tracks, names, force=False):
    t_now = now()
    due = [n for n in names if force or not tracks[n].get("last_scan")
           or t_now - parse_iso(tracks[n]["last_scan"]) >= dt.timedelta(minutes=rules_for(n).get("scan_minutes", 55))]
    if not due:
        return
    import econ
    cands = []
    for series in sorted({s for n in due for s in rules_for(n).get("series", [])}):
        try:
            rows = kalshi_get("/markets", {"series_ticker": series, "status": "open", "limit": 200}).get("markets") or []
        except Exception as e:
            print(f"econ: {series} list failed: {e}")
            continue
        for m in rows:
            close = parse_iso(m.get("close_time"))
            if close:
                hrs = (close - t_now).total_seconds() / 3600
                if min(rules_for(n).get("min_hours", 20) for n in due) <= hrs <= max(rules_for(n).get("max_hours", 76) for n in due):
                    cands.append(dict(m, _series=series, _hours=hrs))
    for n in due:
        tracks[n]["last_scan"] = iso()
        tracks[n]["last_check"] = {"ts": iso(), "markets_in_window": len(cands)}
    if not cands:
        return
    try:
        ch = econ.live_chances(cands, int(t_now.timestamp()))
    except Exception as e:
        print(f"econ: forecasts failed: {e}")
        return
    for n in due:
        tracks[n]["last_check"]["with_forecast"] = len(ch)
    for m in cands:
        tk = m.get("ticker")
        if tk not in ch:
            continue
        p, mu, sd = ch[tk]
        bk = kalshi_asks(tk)
        if not bk:
            continue
        for n in due:
            r, tr = rules_for(n), tracks[n]
            if m["_series"] not in r.get("series", []) or not (r.get("min_hours", 20) <= m["_hours"] <= r.get("max_hours", 76)):
                continue
            if tk in tr["orders"] or tk in tr.get("done", []):
                continue
            for side, asks, val in (("yes", bk[0], p), ("no", bk[1], 1 - p)):
                if not asks:
                    continue
                shares = max(1, int(r.get("usd_per_bet", 5) / max(asks[0][0], 0.01)))
                px = walk(asks, shares)
                if px is None:
                    continue
                fee = kalshi_fee(shares, px)
                cost = shares * px + fee
                per = cost / shares
                if not (r.get("min_cost", 0.80) <= per <= r.get("max_cost", 0.99)) or val - per < r.get("min_edge", 0.03):
                    continue
                maybe_refill(tr, n, cost)
                if cost > tr["cash"] + EPS:
                    tr["skipped_no_cash"] += 1
                    continue
                rs = {}
                for usd_ in rs_sizes():
                    want = max(1, int(usd_ / max(asks[0][0], 0.01)))
                    p2 = walk(asks, want)
                    if p2 is None:   # not all fits: take what the book has
                        got = sum(sz for _, sz in asks)
                        p2 = walk(asks, got) if got >= 1 else None
                        want = got
                    if p2 is not None:
                        c2 = want * p2 + kalshi_fee(want, p2)
                        rs[str(usd_)] = [round(c2, 4), round(want, 4), round(min(1.0, want * p2 / usd_), 4)]
                tr["cash"] = round(tr["cash"] - cost, 6)
                tr["min_cash"] = round(min(tr["min_cash"], tr["cash"]), 6)
                tr["orders"][tk] = {"ticker": tk, "series": m["_series"], "title": f"{m.get('title')} ({m.get('yes_sub_title', '')})",
                                    "outcome": side, "side": side, "shares": shares, "entry": round(px, 6), "price": round(px, 6),
                                    "entry_fee": round(fee, 6), "cost": round(cost, 6), "placed": iso(), "close": m.get("close_time"),
                                    "hours_left": round(m["_hours"], 1), "chance": round(val, 4), "forecast": round(mu, 4),
                                    "spread": round(sd, 4), "price_source": "book", "rs": rs}
                tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(o["cost"] for o in tr["orders"].values())), 6)
                log_event({"type": "econ_buy", "track": n, "ticker": tk, "side": side, "price": round(px, 4),
                           "shares": shares, "chance": round(val, 4)})
                print(f"{n}: bought {side.upper()} {shares} x {px * 100:.1f}c (+fee {fee:.2f}) on {tk}, forecast "
                      f"{mu:g} says {val * 100:.0f} in 100, {m['_hours']:.0f}h before the release")
                if push_allowed(n):
                    push(f"[{n}] BUY {side.upper()} at {cents(per)}", f"{m.get('title')} ({m.get('yes_sub_title', '')})\n"
                         f"Forecast says it wins {val * 100:.0f} times in 100. Result in {m['_hours']:.0f} hours.", track=n)
                break


def econ_cycle(tracks):
    names = econ_names()
    if not names:
        return
    econ_settle(tracks, names)
    econ_place(tracks, names)


def econ_summary(name, tr):
    closed = tr["closed"]
    wins = sum(1 for c in closed if c["pnl"] > 0)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr.get("orders", {})), "closed": len(closed), "wins": wins, "losses": len(closed) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": tr["refills"],
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"]}
    lc = tr.get("last_check", {})
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr.get('orders', {}))} | {len(closed)} ({wins}/{len(closed) - wins}) "
           f"| ${tr['cash']:.2f} | last look {str(lc.get('ts', '-'))[:16]}: {lc.get('markets_in_window', 0)} markets near a release |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n"]
    for o in tr.get("orders", {}).values():
        lines.append(f"- waiting: {o['title']} {o['side'].upper()} {o['shares']} at {cents(o['entry'])}, forecast says "
                     f"{o['chance'] * 100:.0f} in 100, release {str(o['close'])[:16]}")
    return row, stats, lines


# ================================================================ fast markets: weather and daily crypto (added 2026-11-08)
#
# These pay out within hours or a day, so they collect finished trades much faster than deadline markets.
# Each track compares the market's price with a model built from free outside data, and buys only when the model
# says a side is clearly cheap after the fee:
#   wx_forecast : daily highest/lowest temperature buckets. The market settles on the airport's hourly METAR reports
#                 (aviationweather.gov). Model = ECMWF ensemble (51 forecasts, Open-Meteo), corrected by how far
#                 it was off at that station over the last day, plus what has already been observed today.
#   crypto_late : the last 45 minutes of Binance-settled hourly "Up or Down" candles and noon-ET "above $X" ladders.
#                 Prices them with the coin's own hourly volatility of the last week (x1.5 for fat tails); buys the
#                 side the model gives 97%+ when it still costs 96c or less.
# Tested and left out (2026-11-08 dry run): the same crypto model 3-30h out. The ladders matched it within about 1c
# at every strike, so there was nothing to buy.

WX_ENSEMBLE = "https://ensemble-api.open-meteo.com/v1/ensemble"
METAR = "https://aviationweather.gov/api/data/metar"
BINANCE = "https://data-api.binance.vision/api/v3"  # Binance's public market-data mirror (the .com API blocks US IPs)
CRYPTO_SYMBOLS = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "solana": "SOLUSDT", "xrp": "XRPUSDT",
                  "dogecoin": "DOGEUSDT", "bnb": "BNBUSDT"}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
FAST_SOURCES = ("weather", "crypto", "sharp", "mentions", "quiet", "kind", "draws", "postcount", "wordno", "stocklong")
VERBOSE = False  # fasttest prints near misses


def fast_tracks(kind=None):
    return [n for n, tc in CFG["tracks"].items() if tc["source"] in FAST_SOURCES and (kind is None or tc["source"] == kind)]


def gamma_events(params, max_pages=10):
    """Events list with nested markets, up to max_pages x 100 events.
    Bug fix 2026-11-14: since about 12 Nov 13:00 UTC Gamma answers HTTP 406 to a tag-filtered /events page of 100
    (the sports tag 100639 broke sharp_pinnacle and soccer_draw for two days). Pages of 50 via /events/keyset work
    (the mention, stock and family scans use them), so use those, and fall back to plain /events pages of 50."""
    out, cur, want = [], None, max_pages * 100
    try:
        while len(out) < want:
            p = {**params, "limit": 50}
            if cur:
                p["after_cursor"] = cur
            res = http_json(f"{GAMMA}/events/keyset", p)
            rows = [e for e in envelope_rows(res, "events", "data") if isinstance(e, dict)]
            out += rows
            cur = res.get("next_cursor") if isinstance(res, dict) else None
            if not rows or not cur:
                break
        return out
    except Exception as e:
        print(f"events keyset listing failed ({str(e)[:100]}), trying plain pages")
    out, off = [], 0
    while len(out) < want:
        rows = envelope_rows(http_json(f"{GAMMA}/events", {**params, "limit": 50, "offset": off}), "events", "data")
        out += [e for e in rows if isinstance(e, dict)]
        if len(rows) < 50:
            break
        off += 50
    return out


def event_by_slug(slug):
    try:
        rows = envelope_rows(http_json(f"{GAMMA}/events", {"slug": slug}), "events", "data")
        return rows[0] if rows and isinstance(rows[0], dict) else None
    except Exception as e:
        print(f"event lookup failed for {slug}: {e}")
        return None


def event_markets(e):
    """Nested markets of an event, tagged with their event so candidate() can group them (one bet per event)."""
    out = []
    for m in e.get("markets") or []:
        if not isinstance(m, dict) or m.get("closed") or m.get("acceptingOrders") is False or not binary(m):
            continue
        if len(market_tokens(m)) != 2:
            continue
        out.append({**m, "events": [{"id": e.get("id"), "slug": e.get("slug")}]})
    return out


def yes_no_asks(m):
    """(cost of YES, cost of NO) from the listed best bid/ask; NO costs 1 - best YES bid. None where the book is empty."""
    ask, bid = fnum(m.get("bestAsk"), None), fnum(m.get("bestBid"), None)
    return (ask if ask and 0 < ask < 1 else None), (1 - bid if bid and 0 < bid < 1 else None)


def model_pick(m, p_yes, r, extra=None):
    """The side with the biggest model edge after the fee, as a candidate, or None. p_yes = model chance of YES."""
    best = None
    for i, (p, ask) in enumerate(zip((p_yes, 1 - p_yes), yes_no_asks(m))):
        if ask is None or not (r["min_price"] <= ask <= r["max_price"]) or p < r.get("min_model_p", 0):
            continue
        edge = p - ask - fee_rate(m) * ask * (1 - ask)
        if edge > r.get("max_model_edge", 1):
            if VERBOSE:
                print(f"   (ignored: model {p * 100:.0f}/100 vs price {cents(ask)} is too far apart to trust) {m.get('question')}")
            continue  # the crowd isn't that wrong that often; more likely our data is
        if VERBOSE and edge >= r["min_model_edge"] / 2:
            print(f"   near: model {p * 100:.0f}/100 vs price {cents(ask)} edge {edge * 100:+.1f}c {m.get('question')}")
        if edge >= r["min_model_edge"] and (best is None or edge > best[0]):
            best = (edge, i, p)
    # bestAsk/bestBid are for the first outcome, which must be the YES side ("Yes" or "Up")
    if not best or [str(o).lower() for o in jlist(m.get("outcomes"))][:1] not in (["yes"], ["up"]):
        return None
    i = best[1]
    end = parse_iso(m.get("endDate") or m.get("endDateIso")) or now()
    c = candidate(m, i, max((end - now()).total_seconds() / 86400, 0.01), fnum(pick(m, "liquidityNum", "liquidity")),
                  {"model_p": round(best[2], 4), "model_edge": round(best[0], 4), **(extra or {})})
    return c


def fast_due(name, minutes):
    last = parse_iso(load("scan_state.json", {}).get("fast_last", {}).get(name))
    return last is None or (now() - last).total_seconds() >= minutes * 60 - 90


def run_fast(tracks, force=False):
    """Scan the weather and crypto tracks that are due (each has its own scan_every_minutes)."""
    due = [n for n in fast_tracks() if not CFG["tracks"][n].get("stopped")
           and (force or fast_due(n, rules_for(n).get("scan_every_minutes", 60)))]
    if not due:
        return {}
    lists = {}
    for kind, fn in (("weather", weather_candidates), ("crypto", crypto_candidates), ("sharp", sharp_candidates),
                     ("mentions", mention_candidates), ("quiet", quiet_candidates), ("kind", mention_candidates),
                     ("draws", draw_candidates), ("postcount", postcount_candidates),
                     ("wordno", wordno_candidates), ("stocklong", stocklong_candidates)):
        names = [n for n in due if CFG["tracks"][n]["source"] == kind]
        if not names:
            continue
        try:
            by_track = fn(names)
        except Exception as e:
            print(f"{kind} scan failed: {e}")
            continue
        for n in names:
            cands = by_track.get(n, [])
            lists[n] = cands
            r = rules_for(n)
            print(f"{n}: {len(cands)} candidates" + "".join(
                (f"\n   {c['outcome']} model {c['model_p'] * 100:.0f}/100 vs price {cents(c['price'])} "
                 f"(edge {c['model_edge'] * 100:+.1f}c) - {c['title'][:70]}" if c.get("model_p") is not None else
                 f"\n   {c['outcome']} listed {cents(c['price'])}, {c['days']}d left - {c['title'][:70]}")
                for c in cands[:5]))
            buy_candidates(tracks, n, cands, r.get("picks_per_scan", 3))
    st = load("scan_state.json", {})
    for n in due:
        st.setdefault("fast_last", {})[n] = iso()
    save("scan_state.json", st)
    return lists


def mention_candidates(names):
    """'Will X say Y' markets: the side named in rule `side` (No by default) priced in [min_price, max_price].
    calib.py (backtest/calib.md, 2026-11-09) found YES in these markets wins less often than its price says.
    Also serves the "kind" tracks (2026-11-10, winners.py): the same side-and-price rule for one topic (rule `topic`,
    by calib.topic) instead of a wording regex, busiest markets first (rule `sort`: "busy")."""
    rs = {n: rules_for(n) for n in names}
    lo = now() + dt.timedelta(days=max(0, min(r["min_days"] for r in rs.values()) - 1))
    hi = now() + dt.timedelta(days=max(r["max_days"] for r in rs.values()))
    topic = __import__("calib").topic if any(r.get("topic") for r in rs.values()) else None
    markets = scan_markets({"end_date_min": iso(lo), "end_date_max": iso(hi),
                            "liquidity_num_min": min(r["min_liquidity"] for r in rs.values())})
    out = {}
    for n, r in rs.items():
        rx = re.compile(r["only_regex"], re.I) if r.get("only_regex") else None
        cands = []
        for m in markets:
            q = str(m.get("question") or "")
            if (rx and not rx.search(q)) or (r.get("topic") and topic(q) != r["topic"]):
                continue
            prices = binary(m)
            b = base_filter(m, r) if prices else None
            if not b:
                continue
            outs = [str(o).lower() for o in jlist(m.get("outcomes"))]
            side = r.get("side", "no")
            if side not in outs:
                continue
            i = outs.index(side)
            if r["min_price"] <= prices[i] <= r["max_price"]:
                cands.append(candidate(m, i, b[0], b[1], {"signal": f"listed {cents(prices[i])}",
                                                          "busy": fnum(pick(m, "volume24hr", "volume24hrClob"))}))
        if r.get("sort") == "busy":
            cands.sort(key=lambda c: -c["busy"])  # most traded today first: the study only saw markets people were buying
        else:
            cands.sort(key=lambda c: (c["days"], -c["liquidity"]))  # soonest first: the backtest edge is 1-7 days out
        out[n] = cands
    return out


def week_range(token):
    """(high - low over the last 7 days, number of points) from the CLOB price history of a token, or None."""
    try:
        res = http_json(f"{CLOB}/prices-history", {"market": token, "interval": "1w", "fidelity": 60})
    except Exception as e:
        print(f"week history failed for {token[:12]}...: {e}")
        return None
    px = []
    for p in envelope_rows(res, "history", "data"):
        if isinstance(p, dict):
            v = fnum(pick(p, "p", "price"), None)
            if v is not None:
                px.append(v)
    if len(px) < 2:
        return None
    return max(px) - min(px), len(px)


def quiet_candidates(names):
    """Quiet week, buy NO (idea machine, ideas.py, 2026-11-09): markets ending in 1-3 days whose price moved less than
    max_week_range over the last 7 days, second answer (No) at min_price-max_price. The only one of 33,823 screened
    ideas that passed on whole events (backtest/ideas.md). The 7-day range is checked on the first answer's history."""
    rs = {n: rules_for(n) for n in names}
    lo = now() + dt.timedelta(days=min(r["min_days"] for r in rs.values()))
    hi = now() + dt.timedelta(days=max(r["max_days"] for r in rs.values()))
    markets = scan_markets({"end_date_min": iso(lo), "end_date_max": iso(hi),
                            "liquidity_num_min": min(r["min_liquidity"] for r in rs.values())})
    out = {}
    for n, r in rs.items():
        short = []
        for m in markets:
            prices = binary(m)
            b = base_filter(m, r) if prices else None
            if not b or len(prices) != 2:
                continue
            q = str(m.get("question") or "").lower()
            if any(w in q for w in r.get("skip_words", [])):
                continue
            i = 1  # second answer, as screened
            if r["min_price"] <= prices[i] <= r["max_price"]:
                short.append((m, i, b))
        short.sort(key=lambda x: -x[2][1])  # most liquid first: the history check costs a call each
        cands = []
        for m, i, b in short[: r.get("max_history_checks", 40)]:
            wr = week_range(market_tokens(m)[0])
            if not wr or wr[0] >= r["max_week_range"]:
                continue
            cands.append(candidate(m, i, b[0], b[1], {"signal": f"moved {wr[0] * 100:.1f}c this week"}))
        cands.sort(key=lambda c: (c["days"], -c["liquidity"]))
        print(f"quiet {n}: {len(short)} in the price band, {len(cands)} quiet")
        out[n] = cands
    return out


def draw_candidates(names):
    """Soccer draws (digs.py / census.py, backtest/digs_draws.md, 2026-11-10): the 'end in a draw' leg of a soccer
    game, YES at min_price-max_price, when kickoff is min_hours-max_hours away (the backtest decided 24h before).
    Polymarket buyers underrate draws by about 2c. Pre-registered as `soccer_draw` in backtest/PROTOCOL.md."""
    import sharp
    rs = {n: rules_for(n) for n in names}
    games = sharp.poly_games(max(r["max_hours_to_start"] for r in rs.values()))
    out = {n: [] for n in names}
    seen = 0
    for g in games:
        hrs = (g["start"] - now()).total_seconds() / 3600
        for m, i, label, yn in sharp.side_names(g):
            if label != "draw" or not yn:
                continue
            outs = [str(o).lower() for o in jlist(m.get("outcomes"))]
            if outs[:1] != ["yes"]:
                continue
            seen += 1
            price = fnum(jlist(m.get("outcomePrices"))[0], None)
            for n, r in rs.items():
                if price is None or not (r["min_hours_to_start"] <= hrs <= r["max_hours_to_start"]) \
                        or not (r["min_price"] <= price <= r["max_price"]):
                    continue
                mm = {**m, "events": [{"id": g["event"].get("id"), "slug": g["event"].get("slug")}]}
                c = candidate(mm, 0, max(hrs / 24, 0.01), fnum(pick(m, "liquidityNum", "liquidity")),
                              {"signal": f"draw listed {cents(price)}, kickoff in {hrs:.0f}h",
                               "league": str(g["event"].get("slug") or "").split("-")[0]})
                c["outcome"] = "Draw"
                c["theme"] = "soccer"
                out[n].append(c)
    for n in out:
        out[n].sort(key=lambda c: -c["liquidity"])
    print(f"draws: {len(games)} games, {seen} draw markets, " + ", ".join(f"{n} {len(c)}" for n, c in out.items()))
    return out


def postcount_candidates(names):
    """Post-count markets ("Will Elon Musk post 90-114 tweets from ... to ...?"), tweets.py, backtest/tweets.md,
    2026-11-12. A counting model (count so far on Polymarket's own counter + what the same stretch of the week brought
    in the last 8 weeks) gives each count range a chance. Where the listed YES price is `min_gap` or more above the
    model, buy NO (only when NO costs min_price or more). One bet per market, several ranges of one event allowed."""
    import tweets
    rs = {n: rules_for(n) for n in names}
    out = {n: [] for n in names}
    t_now = int(now().timestamp())
    try:
        tr = json.loads(tweets.raw(f"{tweets.X}/trackings")).get("data") or []
    except Exception as e:
        print(f"postcount: counter site failed: {e}")
        return out
    posts, seen_ev, looked = {}, set(), 0
    for t in tr:
        u = t.get("user") or {}
        h, slug = u.get("handle"), str(t.get("marketLink") or "").rstrip("/").split("/")[-1]
        try:
            start, end = tweets.ts(t["startDate"]), tweets.ts(t["endDate"])
        except Exception:
            continue
        if not h or not slug or slug in seen_ev or end - t_now < 3600:
            continue
        seen_ev.add(slug)
        if h not in posts:
            got = {}
            a = t_now - 120 * 86400
            while a < t_now:
                b = min(a + 20 * 86400, t_now + 86400)
                f = lambda x: time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(x))
                try:
                    for p in json.loads(tweets.raw(f"{tweets.X}/users/{h}/posts?startDate={f(a)}&endDate={f(b)}")).get("data") or []:
                        got[p["id"]] = [tweets.ts(p["createdAt"]), tweets.ts(p.get("importedAt") or p["createdAt"])]
                except Exception as e:
                    print(f"postcount: posts of {h} failed: {str(e)[:100]}")
                    got = None
                    break
                a = b
            posts[h] = tweets.Counter(sorted(got.values())) if got else None
        cn = posts[h]
        if cn is None or not cn.c:
            continue
        fc = tweets.forecast(cn, start, end, t_now)
        if fc is None:
            continue
        n0, mean, var = fc
        top = int(mean + 8 * math.sqrt(var) + 10)
        cdf = tweets.nb_cdf(mean, var, top)
        F = lambda x: 0.0 if x < 0 else cdf[min(x, top)]
        e = event_by_slug(slug)
        if not e:
            continue
        for m in event_markets(e):
            bk = tweets.bucket(str(m.get("question") or ""))
            prices = binary(m)
            if not bk or not prices or [str(o).lower() for o in jlist(m.get("outcomes"))][:1] != ["yes"]:
                continue
            looked += 1
            q_yes = F(bk[1] - n0) - F(bk[0] - n0 - 1)
            p_yes = prices[0]
            for n, r in rs.items():
                gap = p_yes - q_yes
                if VERBOSE and gap >= r["min_gap"] / 2:
                    print(f"   near: listed Yes {cents(p_yes)} vs counter {q_yes * 100:.0f}/100 ({n0} so far, about {mean:.0f} more) {m.get('question')}")
                if gap < r["min_gap"] or not (r["min_price"] <= 1 - p_yes <= r["max_price"]):
                    continue
                c = candidate(m, 1, max((end - t_now) / 86400, 0.01), fnum(pick(m, "liquidityNum", "liquidity")),
                              {"model_p": round(1 - q_yes, 4), "model_edge": round(gap, 4),
                               "signal": f"{n0} posts so far, about {mean:.0f} more expected; Yes listed {cents(p_yes)}, counter says {q_yes * 100:.0f} in 100"})
                c["event_key"] = str(m.get("slug") or c["token"])     # one bet per market, not per event
                c["theme"] = "post count"
                out[n].append(c)
    for n in out:
        out[n].sort(key=lambda c: -c["model_edge"])
    print(f"postcount: {len(seen_ev)} open count windows, {looked} markets looked at, " + ", ".join(f"{n} {len(c)}" for n, c in out.items()))
    return out


def _mention_pages(params, max_pages):
    """Events carrying Polymarket's Mentions tag (id 100343). This tag answers HTTP 406 above 50 a page."""
    out, cur = [], None
    for _ in range(max_pages):
        p = dict(params, tag_id=100343, limit=50)
        if cur:
            p["after_cursor"] = cur
        res = http_json(f"{GAMMA}/events/keyset", p)
        rows = [e for e in envelope_rows(res, "events", "data") if isinstance(e, dict)]
        out += rows
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not rows or not cur:
            break
    return out


def wordno_candidates(names):
    """Mention markets ("Will Trump say 'Tariff' during ...?") vs each word's own record, mentions.py,
    backtest/mentions.md, 2026-11-13. The record: how often this word came up in earlier finished markets with the same
    speaker (score sheet mention_counts.json.gz + everything that finished since, kept in state/wordno_hist.json).
    Where the listed YES price is `min_gap` or more above that record, and the speaker has `min_hist`+ earlier markets
    with this word, buy NO. One bet per market, several words of one event allowed."""
    import mentions
    rs = {n: rules_for(n) for n in names}
    out = {n: [] for n in names}
    t_now = int(now().timestamp())
    base = mentions.load_counts()
    st = load("wordno_hist.json", {})
    st.setdefault("delta", {})
    st.setdefault("seen", {})
    C = mentions.Counts(base["counts"], st["delta"])
    cut = int(mentions.btcheck.T(base["until"]))           # the score sheet holds markets that ended before this day
    since = max(cut, int(st.get("synced") or 0)) - 5 * 86400
    added = 0
    try:
        done = _mention_pages({"closed": "true", "end_date_min": iso(dt.datetime.fromtimestamp(since, dt.timezone.utc))}, 60)
    except Exception as e:
        print(f"wordno: finished events failed: {str(e)[:120]}")
        return out                                              # no fresh record, no bets this round
    for e in done:
        for m in e.get("markets") or []:
            if not isinstance(m, dict) or not m.get("closed"):
                continue
            s = mentions.slim(e, m)
            if s["id"] in st["seen"] or not s["end"] or s["end"] < cut or len(s["toks"]) != 2:
                continue
            if s["final"] not in ([0.0, 1.0], [1.0, 0.0]) or not mentions.real(s):
                continue
            if [o.lower() for o in s["outs"]][:1] != ["yes"]:
                continue
            C.add(s, s["final"][0] == 1.0)
            st["seen"][s["id"]] = s["end"]
            added += 1
    st["synced"] = t_now
    save("wordno_hist.json", st)
    try:
        live = _mention_pages({"closed": "false"}, 40)
    except Exception as e:
        print(f"wordno: open events failed: {str(e)[:120]}")
        return out
    looked = known = 0
    for e in live:
        for m in event_markets(e):
            prices = binary(m)
            if not prices or [str(o).lower() for o in jlist(m.get("outcomes"))][:1] != ["yes"]:
                continue
            s = mentions.slim(e, m)
            if not s["end"] or not s["start"] or not mentions.real(s):
                continue
            looked += 1
            q_yes, info = C.chance(s, t_now)
            p_yes = prices[0]
            gap = p_yes - q_yes
            hours_left, hours_old = (s["end"] - t_now) / 3600, (t_now - s["start"]) / 3600
            known += info["n_st"] >= 3
            for n, r in rs.items():
                if info["n_st"] < r["min_hist"] or hours_left < r["min_hours_to_end"] or hours_old < r.get("min_hours_old", 0):
                    continue
                if VERBOSE and gap >= r["min_gap"] / 2:
                    print(f"   near: listed Yes {cents(p_yes)} vs record {q_yes * 100:.0f}/100 ({info['n_st']} earlier) {m.get('question')}")
                if gap < r["min_gap"] or not (r["min_price"] <= 1 - p_yes <= r["max_price"]):
                    continue
                c = candidate(m, 1, max(hours_left / 24, 0.01), fnum(pick(m, "liquidityNum", "liquidity")),
                              {"model_p": round(1 - q_yes, 4), "model_edge": round(gap, 4),
                               "signal": f"Yes listed {cents(p_yes)}; this word's own record with this speaker says {q_yes * 100:.0f} in 100 ({info['n_st']} earlier markets)"})
                c["event_key"] = str(m.get("slug") or c["token"])     # one bet per market, not per event
                c["theme"] = "mention word"
                out[n].append(c)
    for n in out:
        out[n].sort(key=lambda c: -c["model_edge"])
    print(f"wordno: {added} newly finished markets added to the record, {len(live)} open events, {looked} markets looked at, "
          f"{known} with 3+ earlier markets, " + ", ".join(f"{n} {len(c)}" for n, c in out.items()))
    return out


def stocklong_candidates(names):
    """Stock price markets ("will Nvidia close above $180 today?"), stocks.py comb, backtest/stocks_comb.md, 2026-11-13.
    People overpay for the long shot. Where the listed YES price is in [min_yes, max_yes) and the stock market closes
    in min_hours_to_end..max_hours_to_end hours, buy NO. One bet per market; the real ask must be close to the listed
    price (rule max_over_listed), because the history lead only exists at prices near the last trade."""
    import stocks
    rs = {n: rules_for(n) for n in names}
    out = {n: [] for n in names}
    t_now = now().timestamp()
    live, cur = [], None
    for _ in range(40):
        p = {"tag_id": stocks.TAG, "closed": "false", "limit": 50}
        if cur:
            p["after_cursor"] = cur
        res = http_json(f"{GAMMA}/events/keyset", p)
        rows = [e for e in envelope_rows(res, "events", "data") if isinstance(e, dict)]
        live += rows
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not rows or not cur:
            break
    looked = soon = 0
    for e in live:
        for m in event_markets(e):
            prices = binary(m)
            if not prices or [str(o).lower() for o in jlist(m.get("outcomes"))][:1] != ["yes"] or not stocks.parse(m.get("question")):
                continue
            end = parse_iso(m.get("endDate") or m.get("endDateIso"))
            if not end:
                continue
            looked += 1
            hours_left, p_yes = (end.timestamp() - t_now) / 3600, prices[0]
            for n, r in rs.items():
                if not r["min_hours_to_end"] <= hours_left <= r["max_hours_to_end"]:
                    continue
                soon += 1
                if not r["min_yes"] <= p_yes < r["max_yes"]:
                    continue
                c = candidate(m, 1, max(hours_left / 24, 0.01), fnum(pick(m, "liquidityNum", "liquidity")),
                              {"signal": f"Yes listed {cents(p_yes)} with {hours_left:.1f} hours left before the close"})
                c["event_key"] = str(m.get("slug") or c["token"])     # one bet per market, not per event
                c["theme"] = "stock long shot"
                out[n].append(c)
    for n in out:
        out[n].sort(key=lambda c: -c["liquidity"])
    print(f"stocklong: {len(live)} open events, {looked} stock price markets, {soon} closing in the time window, "
          + ", ".join(f"{n} {len(c)}" for n, c in out.items()))
    return out


def sharp_candidates(names):
    """Polymarket game outcomes priced below Pinnacle's fair odds (sharp.py does the matching and de-vig)."""
    import sharp
    return sharp.sharp_candidates(names)


# ---------------------------------------------------------------- weather

BUCKET_RE = re.compile(r"^\s*(-?\d+)\s*(?:-\s*(-?\d+))?\s*°?\s*([CF])\b\s*(or\s+(?:below|lower|less|higher|above|more))?",
                       re.I)


def wx_bucket(label):
    """Bucket label -> (low, high) in °C on the market's rounded scale, e.g. '7°C' -> [6.5, 7.5),
    '84-85°F' -> [83.5, 85.5)°F converted, '6°C or below' -> (-inf, 6.5). None if it doesn't parse."""
    mt = BUCKET_RE.match(str(label or ""))
    if not mt:
        return None
    a = int(mt.group(1))
    b = int(mt.group(2)) if mt.group(2) else a
    unit, tail = mt.group(3).upper(), (mt.group(4) or "").lower()
    lo, hi = a - 0.5, b + 0.5
    if any(w in tail for w in ("below", "lower", "less")):
        lo = -math.inf
    elif tail:
        hi = math.inf
    if unit == "F":
        lo, hi = ((x - 32) / 1.8 for x in (lo, hi))
    return lo, hi, unit


def wx_event_info(e):
    """(kind 'high'/'low', ICAO station, local day start, local day end) from the event, or None.
    The rules link the METAR query for the day; its 'date' is local midnight after the day + 3h, 30 hours back."""
    t = str(e.get("title") or "").lower()
    kind = "high" if t.startswith("highest temperature") else "low" if t.startswith("lowest temperature") else None
    src = str(e.get("resolutionSource") or "")
    if not src:
        for m in e.get("markets") or []:
            src = str(m.get("resolutionSource") or "")
            if src:
                break
    mt = re.search(r"aviationweather\.gov/api/data/metar\?ids=([A-Z0-9]{4}).*?date=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", src)
    if not kind or not mt:
        return None
    end = parse_iso(mt.group(2)) - dt.timedelta(hours=3)
    return kind, mt.group(1), end - dt.timedelta(hours=24), end


def metar_obs(icaos, hours=40):
    """{icao: {"lat", "lon", "obs": [(time, temp °C)], "since": oldest report time}} from routine reports only (SPECI
    doesn't count for the market), using the tenths-of-a-degree T group when present, as the market rules do.
    Asked 3 stations at a time: the API cuts long answers short, which would hide the night's low."""
    out = {}
    icaos = sorted(set(icaos))

    def fetch(ids):
        try:
            rows = http_json(METAR, {"ids": ",".join(ids), "format": "json", "hours": hours})
            return rows if isinstance(rows, list) else []
        except Exception as e:
            print(f"METAR fetch failed for {ids}: {e}")
            return []

    with ThreadPoolExecutor(6) as ex:
        batches = list(ex.map(fetch, [icaos[i:i + 3] for i in range(0, len(icaos), 3)]))
    for rows in batches:
        for x in rows:
            raw = str(x.get("rawOb") or "")
            if not x.get("icaoId") or not x.get("obsTime"):
                continue
            t = dt.datetime.fromtimestamp(int(x["obsTime"]), dt.timezone.utc)
            d = out.setdefault(x["icaoId"], {"lat": x.get("lat"), "lon": x.get("lon"), "obs": [], "since": t})
            d["since"] = min(d["since"], t)
            if raw.startswith("SPECI"):
                continue
            tg = re.search(r" T([01])(\d{3})[01]\d{3}\b", raw)
            if tg:
                temp = (-1 if tg.group(1) == "1" else 1) * int(tg.group(2)) / 10
            elif x.get("temp") is not None:
                temp = fnum(x.get("temp"))
            else:
                continue
            d["obs"].append((t, temp))
    for d in out.values():
        d["obs"].sort()
    return out


_ens_cache = {}


def wx_ensemble(lat, lon, models):
    """{utc hour: [member temps °C]} for the last day and the next 2, or None."""
    key = (round(lat, 3), round(lon, 3), models)
    if key in _ens_cache:
        return _ens_cache[key]
    out = None
    try:
        res = http_json(WX_ENSEMBLE, {"latitude": lat, "longitude": lon, "hourly": "temperature_2m", "models": models,
                                      "past_days": 1, "forecast_days": 3, "timezone": "GMT"}, retries=2)
        h = res.get("hourly") or {}
        cols = [v for k, v in h.items() if k.startswith("temperature_2m") and isinstance(v, list)]
        out = {}
        for j, ts in enumerate(h.get("time") or []):
            vals = [c[j] for c in cols if j < len(c) and c[j] is not None]
            if vals:
                out[dt.datetime.fromisoformat(ts).replace(tzinfo=dt.timezone.utc)] = vals
    except Exception as e:
        print(f"ensemble fetch failed for {lat},{lon}: {e}")
    _ens_cache[key] = out
    return out


def wx_model(kind, start, end, station, ens, r):
    """Chance per bucket comes from wx_bucket_p; this returns what it needs: the observed extreme so far today,
    the station bias, and each ensemble member's extreme over the hours still to come. None if it can't calibrate."""
    obs = station["obs"]
    if start < now() and station["since"] > start + dt.timedelta(minutes=90):
        return None  # reports don't reach back to the start of the day: the day's extreme so far is unknown
    # bias: how far the ensemble mean was off at this station over the last 24h (MOS-lite)
    diffs = []
    for t, temp in obs:
        hr = t.replace(minute=0, second=0, microsecond=0) + (dt.timedelta(hours=1) if t.minute >= 30 else dt.timedelta())
        if hr in ens and now() - t <= dt.timedelta(hours=24):
            diffs.append(temp - sum(ens[hr]) / len(ens[hr]))
    if len(diffs) < r.get("min_bias_obs", 6):
        return None
    bias = max(-r.get("max_bias_c", 4), min(r.get("max_bias_c", 4), sum(diffs) / len(diffs)))
    seen = [temp for t, temp in obs if start <= t < end]
    observed = (max(seen) if kind == "high" else min(seen)) if seen else None
    hours = sorted(h for h in ens if max(start, now()) <= h < end)
    if not hours:
        return None
    n = min(len(ens[h]) for h in hours)
    pick_ext = max if kind == "high" else min
    members = [pick_ext(ens[h][k] for h in hours) + bias for k in range(n)]
    lead_h = (hours[-1] - now()).total_seconds() / 3600
    sigma = r.get("sigma_c", 0.8) + r.get("sigma_per_day_c", 0.4) * max(lead_h, 0) / 24
    return {"observed": observed, "members": members, "sigma": sigma, "bias": round(bias, 2), "n_obs": len(seen)}


def wx_bucket_p(mod, kind, lo, hi):
    """Chance the day's extreme lands in [lo, hi): final = max(observed so far, rest of day) for 'high' (min for 'low');
    the rest of the day = each ensemble member + normal error of sigma."""
    o, s, nd = mod["observed"], mod["sigma"], NormalDist()

    def cdf(x):  # chance the rest-of-day extreme is below x
        if x == math.inf:
            return 1.0
        if x == -math.inf:
            return 0.0
        return sum(nd.cdf((x - v) / s) for v in mod["members"]) / len(mod["members"])

    if kind == "high":
        if o is not None and o >= hi:
            return 0.0
        if o is not None and o >= lo:
            return cdf(hi)              # already in the bucket: stays unless the rest of the day goes higher
        return cdf(hi) - cdf(lo)
    if o is not None and o < lo:
        return 0.0
    if o is not None and o < hi:
        return 1 - cdf(lo)              # already in the bucket: stays unless the rest of the day goes lower
    return cdf(hi) - cdf(lo)


def weather_candidates(names):
    rs = {n: rules_for(n) for n in names}
    horizon = max(r.get("max_hours_to_end", 40) for r in rs.values())
    evs = gamma_events({"tag_slug": "daily-temperature", "closed": "false",
                        "end_date_min": iso(now() - dt.timedelta(hours=36)),
                        "end_date_max": iso(now() + dt.timedelta(hours=horizon + 24))})
    infos = [(e, wx_event_info(e)) for e in evs]
    infos = [(e, i) for e, i in infos if i and i[3] > now() + dt.timedelta(minutes=30)
             and (i[3] - now()).total_seconds() <= horizon * 3600]
    stations = metar_obs({i[1] for _, i in infos})
    models = {r.get("models", "ecmwf_ifs025") for r in rs.values()}
    with ThreadPoolExecutor(6) as ex:  # warm the forecast cache, 6 at a time
        list(ex.map(lambda a: wx_ensemble(*a), {(fnum(s["lat"]), fnum(s["lon"]), md) for s in stations.values()
                                                 if s.get("lat") is not None for md in models}))
    out = {n: [] for n in names}
    skipped = Counter()
    for e, (kind, icao, start, end) in infos:
        st = stations.get(icao)
        if not st or st.get("lat") is None:
            skipped["no METAR"] += 1
            continue
        for n in names:
            r = rs[n]
            if fnum(e.get("liquidity")) < r.get("min_liquidity", 0):
                skipped["thin"] += 1
                continue
            ens = wx_ensemble(fnum(st["lat"]), fnum(st["lon"]), r.get("models", "ecmwf_ifs025"))
            if not ens:
                skipped["no forecast"] += 1
                continue
            mod = wx_model(kind, start, end, st, ens, r)
            if not mod:
                skipped["can't calibrate"] += 1
                continue
            best = None
            for m in event_markets(e):
                b = wx_bucket(m.get("groupItemTitle") or m.get("question"))
                if not b:
                    continue
                if VERBOSE and b[2] not in skipped:
                    skipped[b[2]] = 0  # print one rules text per unit, to check the rounding rule
                    print(f"   rules ({b[2]}): {str(m.get('description'))[:1800]}")
                c = model_pick(m, wx_bucket_p(mod, kind, b[0], b[1]), r,
                               {"signal": f"{kind} {icao} obs {mod['observed']} bias {mod['bias']:+.1f}"})
                if c and (best is None or c["model_edge"] > best["model_edge"]):
                    best = c
            if best:
                out[n].append(best)
    for n in names:
        out[n].sort(key=lambda c: -c["model_edge"])
    print(f"weather: {len(evs)} events, {len(infos)} in range, {len(stations)} stations; skipped {dict(skipped)}")
    return out


# ---------------------------------------------------------------- crypto

_kline_cache = {}


def crypto_state(symbol):
    """(spot, hourly volatility of log returns over the last week, hourly candles) from Binance, or None."""
    if symbol not in _kline_cache:
        try:
            ks = http_json(f"{BINANCE}/klines", {"symbol": symbol, "interval": "1h", "limit": 170})
            closes = [fnum(k[4]) for k in ks]
            rets = [math.log(b / a) for a, b in zip(closes[:-2], closes[1:-1]) if a > 0 and b > 0]  # closed candles only
            mean = sum(rets) / len(rets)
            vol = math.sqrt(sum((x - mean) ** 2 for x in rets) / (len(rets) - 1))
            _kline_cache[symbol] = (closes[-1], vol, ks)
        except Exception as e:
            print(f"binance klines failed for {symbol}: {e}")
            _kline_cache[symbol] = None
    return _kline_cache[symbol]


def p_above(spot, strike, vol_h, hours):
    """Chance the price ends above the strike: log-normal, no drift."""
    if hours <= 0:
        return 1.0 if spot > strike else 0.0
    return NormalDist().cdf(math.log(spot / strike) / (vol_h * math.sqrt(hours)))


def et_now():
    try:
        from zoneinfo import ZoneInfo
        return now().astimezone(ZoneInfo("America/New_York"))
    except Exception:
        return now() - dt.timedelta(hours=5)  # EST; only used to build slugs


def crypto_events():
    """Live crypto events worth pricing: noon-ET 'above' ladders for today and tomorrow, and the hourly
    Up/Down candle that is running now. Built from their slugs (the crypto tag lists thousands of 5-min markets)."""
    et = et_now()
    slugs = []
    for d in (et, et + dt.timedelta(days=1)):
        for coin in ("bitcoin", "ethereum", "solana", "xrp"):
            slugs.append((coin, "above", f"{coin}-above-on-{MONTHS[d.month - 1]}-{d.day}-{d.year}"))
    h = et.hour % 12 or 12
    for coin in CRYPTO_SYMBOLS:
        slugs.append((coin, "updown", f"{coin}-up-or-down-{MONTHS[et.month - 1]}-{et.day}-{et.year}-{h}{'am' if et.hour < 12 else 'pm'}-et"))
    with ThreadPoolExecutor(8) as ex:
        evs = list(ex.map(lambda s: event_by_slug(s[2]), slugs))
    return [(coin, kind, e) for (coin, kind, _), e in zip(slugs, evs) if e and not e.get("closed")]


def crypto_candidates(names):
    rs = {n: rules_for(n) for n in names}
    out = {n: [] for n in names}
    found = Counter()
    for coin, kind, e in crypto_events():
        stt = crypto_state(CRYPTO_SYMBOLS[coin])
        if not stt:
            continue
        spot, vol, ks = stt
        for m in event_markets(e):
            end = parse_iso(m.get("endDate") or e.get("endDate"))
            if not end:
                continue
            hours = (end - now()).total_seconds() / 3600
            if kind == "updown":
                start = parse_iso(m.get("eventStartTime") or e.get("startTime"))
                k = next((k for k in ks if start and int(k[0]) == int(start.timestamp() * 1000)), None)
                if not k or abs((end - start).total_seconds() - 3600) > 60:
                    continue  # only the 1-hour candle that is running now
                strike = fnum(k[1])   # Up wins if close >= open
            else:
                mt = re.search(r"\$?([\d,]+(?:\.\d+)?)", str(m.get("groupItemTitle") or m.get("question") or ""))
                if not mt:
                    continue
                strike = fnum(mt.group(1).replace(",", ""))
            if strike <= 0:
                continue
            found[kind] += 1
            for n in names:
                r = rs[n]
                if not (r["min_hours"] <= hours <= r["max_hours"]) or kind not in r.get("kinds", ["above", "updown"]):
                    continue
                p = p_above(spot, strike, vol * r.get("vol_mult", 1.0), hours)
                if VERBOSE:
                    ya, na = yes_no_asks(m)
                    print(f"   {n} {coin} {kind} {strike:g} in {hours:.1f}h: model YES {p * 100:.1f}/100, YES costs {cents(ya)}, "
                          f"NO costs {cents(na)} (spot {spot:g}, vol/h {vol * 100:.2f}%)")
                c = model_pick(m, p, r, {"signal": f"{coin} {kind} spot {spot:g} strike {strike:g} "
                                                   f"vol/h {vol * 100:.2f}% {hours:.1f}h"})
                if c:
                    out[n].append(c)
    for n in names:
        out[n].sort(key=lambda c: -c["model_edge"])
    print(f"crypto: priced {dict(found)}")
    return out


def fasttest():
    """Live dry run of the weather and crypto tracks (manual probe workflow, saves nothing)."""
    global save, log_event, VERBOSE
    save = lambda name, obj: print(f"(not saving {name})")  # noqa: E731
    log_event = lambda ev: print("EVENT", json.dumps(ev, sort_keys=True)[:300])  # noqa: E731
    VERBOSE = True
    t0 = time.time()
    tracks = load_tracks()
    run_fast(tracks, force=True)
    for n in fast_tracks():
        for p in tracks[n]["positions"].values():
            print(f"WOULD BUY [{n}] {p['outcome']} @ {cents(p['entry'])} (model {p.get('model_p')}) - {p['title'][:70]} | {p.get('signal')}")
    print(f"fasttest took {time.time() - t0:.1f}s")


# ================================================================ ranking: which strategy can we trust?
#
# Raw P&L after a few weeks is mostly luck, and with ~70 strategies some will look great by chance. So the board
# ranks by "worst plausible profit per $100 bet":
#   1. every finished trade's profit per $1 it cost,
#   2. plus one imaginary trade that lost everything (the disaster a 'boring' strategy may not have hit yet),
#   3. the low end of the confidence range, with the bar raised for testing many strategies at once (90% for the
#      whole family, not per strategy).
# A strategy counts as PROVEN when that worst case is above $0 after at least min_trades_proven finished trades.

# ================================================================ maker: get paid to quote (liquidity rewards)
#
# Polymarket pays ~$190k a day to people who leave resting buy AND sell orders close to the middle price (the
# "liquidity rewards"; each market has a daily pool, a max distance v from the middle and a min order size). The
# catch is getting picked off: when news hits, someone who knows more takes our stale order. This track measures
# both, on paper and on the pessimistic side:
#  - We "post" a YES bid and a YES ask (= a NO bid) at the current best prices, joining the back of the queue.
#  - Fills come from the real trade tape: our order fills only if a trade went THROUGH our price, or if more traded
#    AT our price than was queued in front of us when we posted. Our quotes stay where they were until the next run
#    (every ~5 min), so news in between hits us like it would hit a slow bot.
#  - Rewards: each run we score our quotes with Polymarket's formula against everyone else in the public book
#    (assuming the others are as two-sided as possible, which gives us the smaller share), and credit that share of
#    the pool for the minutes since the last run (at most 15, so a skipped run earns nothing).
#  - A YES bought on one side and a NO bought on the other merge back into $1. Leftovers are sold at the bid (taker
#    fee) when the market leaves our list or after max_days, which ends one finished "trade" for the ranking.

def maker_names():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "maker"]


def maker_rules():
    names = maker_names()
    return (names[0], rules_for(names[0])) if names else (None, None)


# Several maker tracks (variants, 2026-11-09) look at the same markets in one run: share the lookups for a minute.
_maker_cache = {}


def maker_cached(key, fn, ttl=60):
    hit = _maker_cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    val = fn()
    if val is not None:
        _maker_cache[key] = (time.time(), val)
    return val


def maker_book(tok):
    return maker_cached(("book", tok), lambda: book(tok))


def reward_score(v, s):
    """Polymarket's per-share reward score for an order s cents from the middle, max distance v cents."""
    return ((v - s) / v) ** 2 if 0 <= s < v else 0.0


def reward_markets(max_pages=40):
    return maker_cached(("reward_markets", max_pages), lambda: _reward_markets(max_pages), ttl=600)


def _reward_markets(max_pages=40):
    out, cur = [], ""
    for _ in range(max_pages):
        try:
            res = http_json(f"{CLOB}/sampling-markets", {"next_cursor": cur} if cur else None)
        except Exception as e:
            print(f"maker: reward list failed: {e}")
            break
        rows = envelope_rows(res, "data", "markets")
        for m in rows:
            rw = m.get("rewards") or {}
            rate = sum(fnum(x.get("rewards_daily_rate")) for x in (rw.get("rates") or []) if isinstance(x, dict))
            toks = [t for t in (m.get("tokens") or []) if isinstance(t, dict)]
            if rate <= 0 or m.get("closed") or m.get("accepting_orders") is False or len(toks) != 2:
                continue
            out.append({"cid": m.get("condition_id"), "title": m.get("question"), "slug": m.get("market_slug"),
                        "rate": rate, "min_size": fnum(rw.get("min_size")), "v": fnum(rw.get("max_spread")),
                        "yes": str(toks[0].get("token_id")), "no": str(toks[1].get("token_id")),
                        "end": m.get("end_date_iso")})
        cur = res.get("next_cursor") if isinstance(res, dict) else None
        if not rows or not cur or cur == "LTE=":
            break
    return out


def reward_config(cid):
    return maker_cached(("reward_config", cid), lambda: _reward_config(cid), ttl=600)


def _reward_config(cid):
    """Today's live reward pool for one market: {"rate", "v", "min_size"}, rate 0 when no pool runs today.
    None when the lookup fails. /sampling-markets can lag; this per-market answer is the one Polymarket pays on."""
    try:
        rows = envelope_rows(http_json(f"{CLOB}/rewards/markets/{cid}"), "data")
    except Exception as e:
        print(f"maker: reward config {str(cid)[:10]} failed: {e}")
        return None
    rows = [x for x in rows if isinstance(x, dict) and x.get("condition_id") == cid]
    if not rows:
        return {"rate": 0.0, "v": 0.0, "min_size": 0.0}
    m, today = rows[0], now().strftime("%Y-%m-%d")
    rate = sum(fnum(c.get("rate_per_day")) for c in (m.get("rewards_config") or []) if isinstance(c, dict)
               and str(c.get("start_date") or "")[:10] <= today <= str(c.get("end_date") or "9999")[:10])
    return {"rate": rate, "v": fnum(m.get("rewards_max_spread")), "min_size": fnum(m.get("rewards_min_size"))}


def book_scores(bk, v, min_size):
    """(middle, everyone else's score on the buy side, on the sell side, best bid, best ask). YES and NO are one
    mirrored book on Polymarket, so the YES book alone holds all of it."""
    bids = [(p, s) for p, s in bk["bids"] if s >= min_size] or bk["bids"]
    asks = [(p, s) for p, s in bk["asks"] if s >= min_size] or bk["asks"]
    if not bids or not asks:
        return None
    mid = (bids[0][0] + asks[0][0]) / 2
    qb = sum(reward_score(v, (mid - p) * 100) * s for p, s in bk["bids"] if s >= min_size)
    qa = sum(reward_score(v, (p - mid) * 100) * s for p, s in bk["asks"] if s >= min_size)
    return mid, qb, qa, bk["bids"][0][0], bk["asks"][0][0]


def our_share(mid, qb, qa, v, bid, ask, size):
    """Our share of the pool right now for quotes at bid/ask (None = that side is not posted)."""
    sb = reward_score(v, (mid - bid) * 100) * size if bid is not None else 0.0
    sa = reward_score(v, (ask - mid) * 100) * size if ask is not None else 0.0
    two_ok = 0.10 <= mid <= 0.90
    ours = max(min(sb, sa), max(sb, sa) / 3) if two_ok else min(sb, sa)
    comp = min(qb, qa) + (abs(qb - qa) / 3 if two_ok else 0.0)
    return ours / (ours + comp) if ours > 0 else 0.0


def maker_pick(tr, r):
    """Best markets to quote now: est. reward per $ of quotes, with the traps filtered out."""
    held = {b["cid"] for b in tr["books"].values()}
    soon = now() + dt.timedelta(days=r["min_days_left"])
    pre = []
    for rm in reward_markets():
        end = parse_iso(rm["end"])
        if rm["cid"] in held or not end or end < soon or rm["min_size"] > r["max_shares"] or rm["v"] <= 0:
            continue
        if r.get("max_days_left") and end > now() + dt.timedelta(days=r["max_days_left"]):
            continue  # variant: short-dated markets only
        if any(w in str(rm["title"]).lower() for w in r.get("skip_words", [])):
            continue
        pre.append(rm)
    pre.sort(key=lambda x: -x["rate"])

    def est(rm):
        cfg = reward_config(rm["cid"])  # the pool list can be stale; trust the per-market answer
        if cfg is not None:
            if cfg["rate"] <= 0 or cfg["v"] <= 0 or cfg["min_size"] > r["max_shares"]:
                return None
            rm = {**rm, **cfg}
        bk = maker_book(rm["yes"])
        sc = book_scores(bk, rm["v"], rm["min_size"]) if bk else None
        if not sc:
            return None
        mid, qb, qa, bb, ba = sc
        if not (r["min_mid"] <= mid <= r["max_mid"]) or (mid - bb) * 100 >= rm["v"] or (ba - mid) * 100 >= rm["v"]:
            return None  # outside the band, or nobody quoting near the middle (we would be the first to get hit)
        size = max(rm["min_size"], r["shares"])
        share = our_share(mid, qb, qa, rm["v"], bb, ba, size)
        return {**rm, "per_day": rm["rate"] * share, "per_dollar": rm["rate"] * share / size, "mid": mid, "size": size}
    with ThreadPoolExecutor(8) as ex:
        cands = [c for c in ex.map(est, pre[:r["scan_books"]]) if c]
    cands.sort(key=lambda c: -c["per_dollar"])
    out = []
    for c in cands:
        m = market_by_slug(c["slug"])
        if not m or is_sports(m) or m.get("closed") or m.get("acceptingOrders") is False:
            continue
        c["fee_rate"] = fee_rate(m)
        c["event_slug"] = str(((m.get("events") or [{}])[0] or {}).get("slug") or "")
        out.append(c)
        if len(out) >= r["max_markets"]:
            break
    print(f"maker: {len(pre)} reward markets pass the date/size filters, {len(cands)} have a book we can join; "
          f"best: {[(c['slug'][:40], round(c['per_day'], 2)) for c in out]}")
    return out


def maker_trades(cid, since):
    def fetch():
        try:
            return envelope_rows(http_json(f"{DATA}/v2/trades", {"condition_id": cid, "limit": 500}), "data", "trades")
        except Exception as e:
            print(f"maker: trades failed for {cid[:10]}: {e}")
            return None
    rows = maker_cached(("trades", cid), fetch)
    if rows is None:
        return None
    out = []
    for t in rows:
        ts = fnum(pick(t, "timestamp", "time"))
        ts = ts / 1000 if ts > 1e11 else ts
        if ts > since:
            out.append((ts, str(pick(t, "token_id", "asset", default="")), fnum(t.get("price")), fnum(t.get("size"))))
    return out


def maker_order_cost(b, side, px):
    """Cash one resting order needs if it fills: a YES bid costs bid x size, a NO bid (1-ask) x size. Whatever
    merges with shares we already hold on the other side comes straight back ($1 a pair), so it doesn't count."""
    if side == "bid":
        return max(0.0, px * b["size"] - min(b["size"], b["no"]))
    return max(0.0, (1 - px) * b["size"] - min(b["size"], b["yes"]))


def maker_locked(tr):
    """Cash our resting orders tie up (see maker_order_cost)."""
    tot = 0.0
    for b in tr["books"].values():
        q = b.get("q") or {}
        if q.get("bid"):
            tot += maker_order_cost(b, "bid", q["bid"]["px"])
        if q.get("ask"):
            tot += maker_order_cost(b, "ask", q["ask"]["px"])
    return tot


def maker_inv_value(b, mid):
    return b["yes"] * mid + b["no"] * (1 - mid)


def maker_row(tr, b, kind, pnl, cost, why, **extra):
    """Bug fix 2026-11-11: early sales and merged pairs moved money (cash, realized) but never showed up as finished
    bets, so maker tracks read "0 won / 0 lost" and "too early" while losing half their money. Each sale and merge
    is now its own finished row; the book remembers what it already booked so the final close doesn't count it twice."""
    rec = {"title": b["title"], "slug": b["slug"], "event_slug": b.get("event_slug", ""), "cid": b["cid"],
           "opened": b["opened"], "closed_at": iso(), "reason": why, "kind": kind,
           "cost": round(cost, 4), "pnl": round(pnl, 4), **extra}
    tr["closed"].append(rec)
    b["booked"] = b.get("booked", 0.0) + rec["pnl"]
    return rec


def maker_backfill_rows(tr, name):
    """One-time (2026-11-11): add rows for sales and merges made before maker_row existed, so the record matches the
    money. Sales come from the event log (one row each); merges only have a total per market (one row)."""
    if tr.get("rows_backfilled"):
        return
    try:
        evs = [json.loads(l) for l in open(os.path.join(STATE, "events.jsonl"))]
    except Exception:
        evs = []
    for b in tr["books"].values():
        if "booked" in b:
            continue
        b["booked"] = 0.0
        got = 0.0
        for e in evs:
            if e.get("track") != name or e.get("type") != "maker_exit" or e.get("title") != b["title"] \
                    or e.get("ts", "") < b["opened"]:
                continue
            m = re.search(r"^(.*?): sold (\d+(?:\.\d+)?) (YES|NO) at", e.get("reason", ""))
            if not m:
                continue
            sh, px, pnl = float(m.group(2)), float(e["price"]), float(e["pnl"])
            cost = sh * px - taker_fee(sh, px, b.get("fee_rate", 0.0)) - pnl
            rec = maker_row(tr, b, "sale", pnl, cost, e["reason"], outcome=m.group(3), shares=sh,
                            entry=round(cost / sh, 4), exit=round(px, 4))
            rec["closed_at"] = e["ts"]
            got += pnl
        rest = b.get("exit_pnl", 0.0) - got
        if abs(rest) > 0.01:
            maker_row(tr, b, "sale", rest, b["size"], "earlier sales (before 11 Nov, no detail kept)")
        if abs(b.get("merged_pnl", 0.0)) > 1e-9:
            maker_row(tr, b, "merge", b["merged_pnl"], b["size"],
                      "pairs bought on both sides and turned back into $1 (all before 11 Nov)", outcome="YES+NO")
    tr["closed"].sort(key=lambda c: c.get("closed_at") or "")
    tr["rows_backfilled"] = iso()


def maker_close(tr, name, key, why, payout=None):
    """End one market episode: merge pairs, then pay out (resolved) or sell what is left at the bid."""
    b = tr["books"].pop(key)
    proceeds, fee = 0.0, 0.0
    for side, tok in (("yes", b["yes_tok"]), ("no", b["no_tok"])):
        sh = b[side]
        if sh <= EPS:
            continue
        if payout is not None:
            px = payout if side == "yes" else 1 - payout
        else:
            bk = maker_book(tok)
            px = walk(bk["bids"], sh) if bk else None
            if px is None:  # nobody to sell to: count it at half the best bid (or nothing)
                px = (bk["bids"][0][0] / 2) if bk and bk["bids"] else 0.0
            fee += taker_fee(sh, px, b.get("fee_rate", 0.0))
        proceeds += sh * px
    proceeds -= fee
    exit_pnl = b.get("exit_pnl", 0.0)
    pnl = b["rewards"] + b["merged_pnl"] + exit_pnl + proceeds - b["yes_cost"] - b["no_cost"]
    pnl -= b.get("booked", 0.0)  # sales and merges already have their own finished rows (maker_row)
    tr["cash"] = round(tr["cash"] + proceeds, 6)
    # rewards, merges and early sales were booked when they happened
    tr["realized"] = round(tr["realized"] + pnl + b.get("booked", 0.0) - b["rewards"] - b["merged_pnl"] - exit_pnl, 6)
    rec = {"title": b["title"], "slug": b["slug"], "cid": b["cid"], "opened": b["opened"], "closed_at": iso(),
           "reason": why, "cost": round(b["size"], 4), "pnl": round(pnl, 4), "rewards": round(b["rewards"], 4),
           "merged_pnl": round(b["merged_pnl"], 4), "leftover_pnl": round(proceeds - b["yes_cost"] - b["no_cost"], 4),
           "exit_pnl": round(exit_pnl, 4), "exits": b.get("exits", 0),
           "fills": b["fills"], "minutes_quoted": round(b["minutes"], 1)}
    tr["closed"].append(rec)
    log_event({"type": "maker_close", "track": name, "title": b["title"], "pnl": round(pnl, 4), "reason": why})
    return rec


def maker_exits(tr, name, b, r):
    """Variants (2026-11-09, Jan: "can't we exit with profit?"): sell what we hold at the real bid, taker fee paid,
    when it is up take_profit_c cents a share (after the fee), down stop_loss_c cents, or always (flatten). No buyer
    on the book for all our shares = no sale (no estimate fills). Quoting goes on, so rewards keep coming."""
    tp, sl, flat = r.get("take_profit_c"), r.get("stop_loss_c"), r.get("flatten")
    if tp is None and sl is None and not flat:
        return
    for side, tok in (("yes", b["yes_tok"]), ("no", b["no_tok"])):
        sh = b[side]
        if sh <= EPS:
            continue
        bk = maker_book(tok)
        px = walk(bk["bids"], sh) if bk else None
        if px is None:
            continue
        fee = taker_fee(sh, px, b.get("fee_rate", 0.0))
        cost = b[side + "_cost"]
        per = (sh * px - fee - cost) / sh * 100  # cents a share
        why = ("flatten" if flat else "take profit" if tp is not None and per >= tp
               else "stop loss" if sl is not None and per <= -sl else None)
        if not why:
            continue
        gain = sh * px - fee - cost
        tr["cash"] = round(tr["cash"] + sh * px - fee, 6)
        tr["realized"] = round(tr["realized"] + gain, 6)
        b["exit_pnl"] = b.get("exit_pnl", 0.0) + gain
        b["exits"] = b.get("exits", 0) + 1
        tr["exits"] = tr.get("exits", 0) + 1
        b[side], b[side + "_cost"] = 0.0, 0.0
        maker_row(tr, b, "sale", gain, cost, f"{why}: sold {sh:.0f} {side.upper()} at {px * 100:.1f}c",
                  outcome=side.upper(), shares=sh, entry=round(cost / sh, 4), exit=round(px, 4))
        log_event({"type": "maker_exit", "track": name, "title": b["title"], "price": round(px, 4),
                   "pnl": round(gain, 4), "reason": f"{why}: sold {sh:.0f} {side.upper()} at {px * 100:.1f}c"})


def maker_cycle(tracks, pick_new=True):
    for name in maker_names():
        if name not in tracks:
            continue
        try:
            maker_cycle_one(tracks, name, rules_for(name), pick_new)
        except Exception as e:
            print(f"maker {name} failed: {e}")


def maker_reward_cap(r, size, minutes):
    """Most reward we believe for `size` shares quoted (about $size tied up) over `minutes`. Bug fix 2026-11-09:
    the share-of-pool model paid ~$8 a day per $100, but real reward payouts of the busiest maker wallets
    (probe rewardpay) were 1-38c a day per $100 they hold, so credit at most reward_cap_per_100_day."""
    cap = r.get("reward_cap_per_100_day")
    return float("inf") if cap is None else cap * size / 100 * minutes / 1440


def maker_recap_rewards(tr, r):
    """One-time: cut rewards already credited down to the cap (keeps the old number as rewards_model)."""
    if tr.get("reward_cap_applied") or r.get("reward_cap_per_100_day") is None:
        return
    cut = 0.0
    for b in tr["books"].values():
        new = min(b["rewards"], maker_reward_cap(r, b["size"], b["minutes"]))
        b.setdefault("rewards_model", b["rewards"])
        cut += b["rewards"] - new
        b["rewards"] = new
    for c in tr["closed"]:
        new = min(c.get("rewards", 0.0), maker_reward_cap(r, c.get("cost", 0.0), c.get("minutes_quoted", 0.0)))
        d = c.get("rewards", 0.0) - new
        c.setdefault("rewards_model", c.get("rewards", 0.0))
        c["rewards"], c["pnl"] = round(new, 4), round(c["pnl"] - d, 4)
        cut += d
    tr["rewards_model"] = tr.get("rewards", 0.0)
    tr["rewards"] = round(tr["rewards"] - cut, 6)
    tr["realized"] = round(tr["realized"] - cut, 6)
    tr["cash"] = round(tr["cash"] - cut, 6)
    tr["reward_cap_applied"] = {"on": iso(), "cut": round(cut, 4)}
    print(f"maker: rewards capped, removed ${cut:.2f} of modelled rewards")


def maker_retire(tr, name, why):
    """Jan, 12 Nov 2026 ("Dump them"): a track with "retired" in config stops quoting. Its open markets are closed
    once like any other episode end (pairs merged, leftovers sold at the real bid), then it stays frozen."""
    for key in list(tr.get("books", {})):
        try:
            maker_close(tr, name, key, f"strategy stopped ({why})")
        except Exception as e:
            print(f"maker {name}: closing {key} failed: {e}")
            return
    tr["retired"] = {"on": iso(), "why": why}
    tr["status"] = {"at": iso(), "msg": f"Stopped: {why}. Final numbers, no new bets.", "skips": {}}
    log_event({"type": "maker_retired", "track": name, "reason": why})


def maker_cycle_one(tracks, name, r, pick_new=True):
    tr = tracks[name]
    tr.setdefault("books", {})
    if CFG["tracks"][name].get("retired"):
        if not tr.get("retired"):
            maker_retire(tr, name, CFG["tracks"][name]["retired"])
        return
    for k, v in (("rewards", 0.0), ("fills", 0), ("merges", 0), ("last_pick", "")):
        tr.setdefault(k, v)
    maker_recap_rewards(tr, r)
    maker_backfill_rows(tr, name)
    t_now = time.time()
    for key in list(tr["books"]):
        b = tr["books"][key]
        m = market_by_slug(b["slug"])
        payout = resolved_payout(m, b["yes_tok"])
        if payout is not None:
            maker_close(tr, name, key, "resolved", payout)
            continue
        # the pool can shrink or end at any time: re-read it at most once an hour (bug fix 2026-11-09:
        # rate/spread/min size used to be frozen at the day the book opened)
        if t_now - b.get("cfg_ts", 0) > 3600:
            cfg = reward_config(b["cid"])
            if cfg is not None:
                if abs(cfg["rate"] - b["rate"]) > 1e-9 or cfg["min_size"] != b["min_size"]:
                    print(f"maker: {b['title'][:40]} pool ${b['rate']:.0f}->${cfg['rate']:.0f}/day, "
                          f"min {b['min_size']:.0f}->{cfg['min_size']:.0f}")
                b["rate"], b["min_size"] = cfg["rate"], cfg["min_size"]
                if cfg["v"] > 0:
                    b["v"] = cfg["v"]
                b["cfg_ts"] = t_now
        bk = maker_book(b["yes_tok"])
        if (m is None or bk is None) and b.get("misses", 0) < 6:
            # bug fix: one failed market/book lookup (an API blip) used to close the book as "market left the list".
            # Skip it this run instead; last_ts stays, so the next run catches up on fills. 6 misses in a row = gone.
            b["misses"] = b.get("misses", 0) + 1
            why(name, "market or order book lookup failed; retrying next run")
            continue
        b["misses"] = 0
        sc = book_scores(bk, b["v"], b["min_size"]) if bk else None
        q = b.get("q") or {}
        elapsed = max(0.0, t_now - b["last_ts"])
        # 1) fills since the last check, from the real trade tape
        trades = maker_trades(b["cid"], b["last_ts"])
        if trades is None:
            trades = []
        at_bid = at_ask = 0.0
        hit_bid = hit_ask = False
        for ts, tok, px, sz in trades:
            yp = px if tok == b["yes_tok"] else 1 - px
            if q.get("bid"):
                if yp < q["bid"]["px"] - 1e-9:
                    hit_bid = True
                elif abs(yp - q["bid"]["px"]) < 1e-9:
                    at_bid += sz
            if q.get("ask"):
                if yp > q["ask"]["px"] + 1e-9:
                    hit_ask = True
                elif abs(yp - q["ask"]["px"]) < 1e-9:
                    at_ask += sz
        if q.get("bid") and (hit_bid or at_bid > q["bid"]["queue"] + EPS):
            b["yes"] += b["size"]
            b["yes_cost"] += b["size"] * q["bid"]["px"]
            tr["cash"] = round(tr["cash"] - b["size"] * q["bid"]["px"], 6)
            b["fills"] += 1
            tr["fills"] += 1
            q["bid"] = None
        elif q.get("bid"):
            q["bid"]["queue"] = max(0.0, q["bid"]["queue"] - at_bid)
        if q.get("ask") and (hit_ask or at_ask > q["ask"]["queue"] + EPS):
            b["no"] += b["size"]
            b["no_cost"] += b["size"] * (1 - q["ask"]["px"])
            tr["cash"] = round(tr["cash"] - b["size"] * (1 - q["ask"]["px"]), 6)
            b["fills"] += 1
            tr["fills"] += 1
            q["ask"] = None
        elif q.get("ask"):
            q["ask"]["queue"] = max(0.0, q["ask"]["queue"] - at_ask)
        # 2) a YES and a NO merge back into $1
        pairs = min(b["yes"], b["no"])
        if pairs > EPS:
            ay, an = b["yes_cost"] / b["yes"], b["no_cost"] / b["no"]
            gain = pairs * (1 - ay - an)
            b["merged_pnl"] += gain
            tr["realized"] = round(tr["realized"] + gain, 6)
            maker_row(tr, b, "merge", gain, pairs * (ay + an),
                      f"bought both sides ({ay * 100:.1f}c YES + {an * 100:.1f}c NO), turned {pairs:.0f} pairs back into $1",
                      outcome="YES+NO", shares=pairs)
            tr["cash"] = round(tr["cash"] + pairs, 6)
            b["yes_cost"] -= pairs * ay
            b["no_cost"] -= pairs * an
            b["yes"] -= pairs
            b["no"] -= pairs
            tr["merges"] += 1
        maker_exits(tr, name, b, r)
        # 3) rewards for the minutes our (old) quotes were resting, scored against today's book
        if sc and elapsed > 0:
            mid, qb, qa, bb, ba = sc
            sh = our_share(mid, qb, qa, b["v"], (q.get("bid") or {}).get("px"), (q.get("ask") or {}).get("px"), b["size"])
            if b["size"] < b["min_size"]:
                sh = 0.0  # orders below the minimum size earn nothing
            mins = min(elapsed / 60, r["max_credit_minutes"])
            model = b["rate"] * sh * mins / 1440
            b["rewards_model"] = b.get("rewards_model", 0.0) + model
            earned = min(model, maker_reward_cap(r, b["size"], mins))
            b["rewards"] += earned
            b["minutes"] += mins
            tr["rewards"] = round(tr["rewards"] + earned, 6)
            tr["rewards_model"] = round(tr.get("rewards_model", 0.0) + model, 6)
            tr["realized"] = round(tr["realized"] + earned, 6)
            tr["cash"] = round(tr["cash"] + earned, 6)
        b["last_ts"] = t_now
        # 4) leave, or re-post at today's best prices
        end = parse_iso(b.get("end"))
        too_old = (now() - parse_iso(b["opened"])).total_seconds() > r["max_days"] * 86400
        if too_old or (end and end < now() + dt.timedelta(days=r["min_days_left"] - 2)) or not sc \
                or not m or m.get("closed") or m.get("acceptingOrders") is False:
            if not too_old and m and (m.get("closed") or m.get("acceptingOrders") is False) \
                    and (b["yes"] > EPS or b["no"] > EPS):
                # bug fix 2026-11-10: a market that stopped trading but isn't paid out yet has no buyers, so the
                # old close sold what we held at $0 (maker_short, Lambda). Hold it and let the payout close it.
                b["q"] = {"bid": None, "ask": None}
                why(name, "market stopped trading; holding what we own until it pays out")
                continue
            maker_close(tr, name, key, "episode over" if too_old else "market left the list")
            continue
        mid, qb, qa, bb, ba = sc
        net = b["yes"] - b["no"]
        b["q"] = {"bid": None, "ask": None}
        # bug fix 2026-11-10: only post an order the cash can pay for if it fills. Fills used to be charged with no
        # check, so a track holding unsold shares kept bidding past its budget (maker_tp went to -$6).
        free = tr["cash"] - maker_locked(tr)
        if (mid - bb) * 100 < b["v"] and net < r["max_inventory_lots"] * b["size"] and r["min_mid"] - 0.05 <= mid <= r["max_mid"] + 0.05:
            if maker_order_cost(b, "bid", bb) <= max(free, 0.0) + EPS:
                old = q.get("bid")
                lvl = next((s for p, s in bk["bids"] if abs(p - bb) < 1e-9), 0.0)
                b["q"]["bid"] = old if old and abs(old["px"] - bb) < 1e-9 else {"px": bb, "queue": lvl}
                free -= maker_order_cost(b, "bid", bb)
            else:
                tr["skipped_no_cash"] = tr.get("skipped_no_cash", 0) + 1
                why(name, "not enough cash for another buy order")
        if (ba - mid) * 100 < b["v"] and -net < r["max_inventory_lots"] * b["size"] and r["min_mid"] - 0.05 <= mid <= r["max_mid"] + 0.05:
            if maker_order_cost(b, "ask", ba) <= max(free, 0.0) + EPS:
                old = q.get("ask")
                lvl = next((s for p, s in bk["asks"] if abs(p - ba) < 1e-9), 0.0)
                b["q"]["ask"] = old if old and abs(old["px"] - ba) < 1e-9 else {"px": ba, "queue": lvl}
                free -= maker_order_cost(b, "ask", ba)
            else:
                tr["skipped_no_cash"] = tr.get("skipped_no_cash", 0) + 1
                why(name, "not enough cash for another buy order")
        b["mid"] = mid
    # 5) fill free slots
    last = parse_iso(tr["last_pick"]) if tr["last_pick"] else None
    if pick_new and len(tr["books"]) < r["max_markets"] and (not last or (now() - last).total_seconds() >= r["pick_every_minutes"] * 60):
        tr["last_pick"] = iso()
        for c in maker_pick(tr, r):
            if len(tr["books"]) >= r["max_markets"]:
                break
            need = c["size"]  # a bid + an ask lock about $1 per share pair
            if tr["cash"] - maker_locked(tr) - need < -EPS:
                tr["skipped_no_cash"] += 1
                continue
            bk = maker_book(c["yes"])
            sc = book_scores(bk, c["v"], c["min_size"]) if bk else None
            if not sc:
                continue
            mid, qb, qa, bb, ba = sc
            tr["books"][c["cid"]] = {
                "cid": c["cid"], "title": c["title"], "slug": c["slug"], "event_slug": c["event_slug"], "end": c["end"],
                "yes_tok": c["yes"], "no_tok": c["no"], "rate": c["rate"], "v": c["v"], "min_size": c["min_size"],
                "size": c["size"], "fee_rate": c["fee_rate"], "opened": iso(), "last_ts": t_now, "mid": mid,
                "est_per_day": round(c["per_day"], 4), "yes": 0.0, "no": 0.0, "yes_cost": 0.0, "no_cost": 0.0,
                "rewards": 0.0, "merged_pnl": 0.0, "fills": 0, "minutes": 0.0,
                "q": {"bid": {"px": bb, "queue": next((s for p, s in bk["bids"] if abs(p - bb) < 1e-9), 0.0)},
                      "ask": {"px": ba, "queue": next((s for p, s in bk["asks"] if abs(p - ba) < 1e-9), 0.0)}}}
            log_event({"type": "maker_open", "track": name, "title": c["title"], "price": round(mid, 4),
                       "reason": f"pool ${c['rate']:.0f}/day, est. ${c['per_day']:.2f}/day for us"})
    tr["peak_open_cost"] = round(max(tr["peak_open_cost"], maker_locked(tr) + sum(
        b["yes_cost"] + b["no_cost"] for b in tr["books"].values())), 6)
    saw(name, f"Quoting in {len(tr['books'])} markets; {tr['fills']} fills and ${tr['rewards']:.2f} rewards so far.")


def maker_summary(name, tr):
    books = tr.get("books", {})
    unreal = sum(maker_inv_value(b, b.get("mid", 0.5)) - b["yes_cost"] - b["no_cost"] for b in books.values())
    pnl = tr["realized"] + unreal
    wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
    stats = {"pnl": round(pnl, 4), "realized": round(tr["realized"], 4), "unrealized": round(unreal, 4),
             "open": len(books), "closed": len(tr["closed"]), "wins": wins, "losses": len(tr["closed"]) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": 0,
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "rewards": round(tr.get("rewards", 0.0), 4),
             "fills": tr.get("fills", 0)}
    rew = tr.get("rewards", 0.0)
    locked = tr["realized"] - rew  # merges, early sales and finished leftovers: real order-book money
    stats.update({"maker_rewards": round(rew, 4), "maker_locked": round(locked, 4), "maker_open": round(unreal, 4),
                  "exits": tr.get("exits", 0)})
    row = (f"| {name} | {pnl:+.2f} | {len(books)} | {len(tr['closed'])} ({wins}/{len(tr['closed']) - wins}) | "
           f"${tr['cash']:.2f} | rewards +${rew:.2f} (capped), trading {locked:+.2f} locked {unreal:+.2f} open; "
           f"fills {tr.get('fills', 0)}, sold early {tr.get('exits', 0)} |")
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n",
             f"Rewards **${rew:.2f}** (capped at what real makers get paid, 40c a day per $100; the raw pool-share "
             f"model said ${tr.get('rewards_model', rew):.2f}). Price moves, "
             f"the real-ish part: **{locked:+.2f}** locked in (pairs merged, sold, finished) and **{unreal:+.2f}** on "
             f"what it still holds at today's middle price. It only works if the rewards beat the price moves.\n"]
    if books:
        lines.append("| Market | Pool/day | Quotes (YES bid / ask) | Holding | Rewards | Fills | Ends |\n|---|---|---|---|---|---|---|")
        for b in books.values():
            q = b.get("q") or {}
            qs = f"{cents((q.get('bid') or {}).get('px'))} / {cents((q.get('ask') or {}).get('px'))}"
            hold = f"{b['yes']:.0f} YES, {b['no']:.0f} NO"
            lines.append(f"| {b['title'][:60]} | ${b['rate']:.0f} | {qs} | {hold} | ${b['rewards']:.2f} | {b['fills']} | "
                         f"{str(b.get('end'))[:10]} |")
    else:
        lines.append("No markets quoted right now.")
    return row, stats, lines


def makertest():
    """Live check of the maker track (manual probe workflow, saves nothing): pick markets, post, wait, settle once."""
    global save, log_event
    save = lambda *a, **k: None  # noqa: E731
    log_event = lambda ev: print("event:", ev)  # noqa: E731
    tracks = load_tracks()
    name, r = maker_rules()
    tracks[name]["books"] = {}
    tracks[name]["last_pick"] = ""
    maker_cycle(tracks)
    for rnd in range(3):
        print(f"--- waiting 4 min (round {rnd + 1}/3)")
        time.sleep(240)
        _market_cache.clear()
        maker_cycle(tracks, pick_new=False)
        tr = tracks[name]
        for b in tr["books"].values():
            q = b.get("q") or {}
            print(f"  {b['slug'][:50]}: rewards ${b['rewards']:.3f} over {b['minutes']:.0f} min (est ${b['est_per_day']:.2f}/day), "
                  f"fills {b['fills']}, holding {b['yes']:.0f} YES / {b['no']:.0f} NO, quotes "
                  f"{cents((q.get('bid') or {}).get('px'))}/{cents((q.get('ask') or {}).get('px'))}, mid {b['mid']:.3f}")
    row, st, lines = maker_summary(name, tracks[name])
    print(row)
    print("\n".join(lines))


def trade_returns(tr, size=None):
    """(pnl, cost) per finished trade. With `size`, use the real-size numbers for that stake when the trade has
    them (trades from before 2026-11-08 don't: they count with their paper numbers). A trade where nothing would
    have filled at that size is left out: a real bot would simply not have made it."""
    out = []
    for c in tr["closed"]:
        rs = (c.get("rs_pnl") or {}).get(str(size)) if size else None
        if rs:
            if rs[0] > EPS:
                out.append((rs[1], rs[0]))
            continue
        basis = c.get("cost") or (c.get("shares", 0) * c.get("entry", 0) + c.get("entry_fee", 0.0))
        if basis and basis > 0:
            out.append((c["pnl"], basis))
    return out


def rs_rank_size():
    return rs_cfg().get("rank_size_usd") if rs_cfg().get("rank_on_real_size", True) else None


def trust(tr, n_tracks=None, size="rank"):
    rk = CFG.get("ranking", {})
    rows = trade_returns(tr, rs_rank_size() if size == "rank" else size)
    n = len(rows)
    rets = [p / b for p, b in rows] + [-1.0] * int(rk.get("phantom_losses", 1))
    m = len(rets)
    mean = sum(rets) / m
    sd = math.sqrt(sum((x - mean) ** 2 for x in rets) / (m - 1)) if m > 1 else 1.0
    alpha = (1 - rk.get("family_confidence", 0.9)) / max(n_tracks or len(CFG["tracks"]), 1)
    worst = max(-1.0, mean - NormalDist().inv_cdf(1 - alpha) * sd / math.sqrt(m))  # can't lose more than the bet
    avg = sum(p / b for p, b in rows) / n if n else 0.0
    proven = n >= rk.get("min_trades_proven", 30) and worst > 0
    # 2026-11-12 (Jan: "we check for luck but not unlucky?"): the other end of the plain luck range (usual 90%, real
    # bets only, no made-up disaster, no raised bar). Below $0 = it is behind even if we assume it was unlucky.
    best = None
    if n >= 2:
        r = [p / b for p, b in rows]
        sd_r = math.sqrt(sum((x - avg) ** 2 for x in r) / (n - 1))
        best = round((avg + NormalDist().inv_cdf(0.95) * sd_r / math.sqrt(n)) * 100, 2)
    return {"finished": n, "profit": round(sum(p for p, _ in rows), 4), "avg_per_100": round(avg * 100, 2),
            "worst_per_100": round(worst * 100, 2), "best_per_100": best, "proven": proven}


def plain_verdict(t, control=False, few=10):
    """One plain-words verdict per strategy, from its trust numbers (wording only, no new math).
    Returns (key, text): key is good / maybe / unlucky / bad / early / luck, used for colors on the dashboard."""
    if control:
        return "luck", "Random buyer (shows what luck looks like)"
    if t["finished"] < few:
        return "early", f"Too early to tell ({t['finished']} finished, need {few}+)"
    if t["proven"]:
        return "good", "Looks real"
    if t["worst_per_100"] > 0:
        return "good", "Promising, needs more bets"
    if t["avg_per_100"] < 0:
        # 2026-11-12: losses get the same luck check as wins. "Losing" only when even the lucky end of the range is
        # below $0; otherwise it's behind, but that could still be bad luck.
        if t.get("best_per_100") is not None and t["best_per_100"] >= 0:
            return "unlucky", "Behind, but could be bad luck"
        return "bad", "Losing"
    return "maybe", "Ahead, but could be luck"


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def ranked(stats):
    return sorted(stats, key=lambda n: (-stats[n]["trust"]["worst_per_100"], -stats[n]["pnl"]))


def leaderboard_md(stats):
    sz = rs_rank_size()
    at = f" at ${sz} a trade" if sz else ""
    out = ["\n## All strategies, ranked by trust\n",
           "Ranked by the worst profit per $100 bet that is still plausible (one imaginary total loss added, bar raised "
           "for testing many strategies at once). Only finished trades count. **PROVEN** = that worst case is above $0 "
           f"after {CFG.get('ranking', {}).get('min_trades_proven', 30)}+ finished trades. Controls show what luck looks like.\n",
           (f"Since 2026-11-08 the ranking uses **real-size** numbers: what each trade would have done with ${sz} instead "
            "of 5 shares (deeper into the order book, bigger fee, only what actually fits; see \"Real money check\"). "
            "Older trades count with their paper numbers. \"Paper\" shows the 5-share number for comparison.\n") if sz else "",
           f"| # | Strategy | Finished | Profit{at} (done) | Avg per $100 | Paper avg per $100 | Worst per $100 | "
           "P&L incl. open (paper) | Today | Open |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for i, n in enumerate(ranked(stats), 1):
        s, t = stats[n], stats[n]["trust"]
        tp = s.get("trust_paper", t)
        out.append(f"| {i} | {n}{' **PROVEN**' if t['proven'] else ''} | {t['finished']} | ${t['profit']:+.2f} | "
                   f"${t['avg_per_100']:+.2f} | ${tp['avg_per_100']:+.2f} | ${t['worst_per_100']:+.2f} | ${s['pnl']:+.2f} | "
                   f"${s.get('today', 0):+.2f} | {s['open']} |")
    return out


def rs_fills(tr):
    """Real-size buy records of every trade (open and finished) that has them."""
    items = list(tr.get("closed", [])) + list(tr.get("positions", {}).values()) + \
        list(tr.get("arbs", {}).values()) + list(tr.get("sets", {}).values())
    return [x["rs"]["s"] for x in items if isinstance(x.get("rs"), dict) and x["rs"].get("s")]


def real_money_md(tracks, stats):
    """Per strategy: profit per $100 at each stake on finished trades, and how much of a $100 order the book holds."""
    sizes = rs_sizes()
    big = str(max(sizes))
    rows = []
    for name, tr in tracks.items():
        fills = rs_fills(tr)
        if not fills:
            continue
        done = [c for c in tr["closed"] if c.get("rs_pnl")]
        paper = sum(c["pnl"] for c in done) / max(sum(c.get("cost") or (c["shares"] * c["entry"] + c.get("entry_fee", 0))
                                                     for c in done), EPS) * 100 if done else None
        cells = []
        for sz in sizes:
            rr = [c["rs_pnl"][str(sz)] for c in done if str(sz) in c["rs_pnl"] and c["rs_pnl"][str(sz)][0] > EPS]
            cost = sum(x[0] for x in rr)
            cells.append(f"${sum(x[1] for x in rr) / cost * 100:+.2f}" if cost > EPS else "-")
        fit = [f[big][1] for f in fills if big in f]
        full = sum(1 for f in fills if f.get(str(rs_rank_size() or sizes[0]), [0, 0, False])[2])
        rows.append((len(done), f"| {name} | {len(done)} | {'-' if paper is None else f'${paper:+.2f}'} | " + " | ".join(cells) +
                     f" | ${sum(fit) / len(fit):.0f} | {full} of {len(fills)} |"))
    out = ["\n## Real money check\n",
           "Every paper trade (5 shares) is also priced at bigger stakes on the same live order book: a limit order that "
           f"never pays more than the best price + {rs_cfg().get('max_slip', 0.02) * 100:.0f}c, the bigger fee, and only what "
           "fits. Selling early walks the real bids. This is the number that matters for the $300-500 in January. "
           "Profit per $100 on finished trades, paper (5 shares) vs each stake:\n"]
    if not rows:
        return out + ["No trades with real-size data yet (started 2026-11-08)."]
    sz = rs_rank_size() or sizes[0]
    out += ["| Strategy | Finished (with data) | Paper | " + " | ".join(f"${s}" for s in sizes) +
            f" | Of a ${big} order, fits on avg | Fully filled at ${sz} |",
            "|---|---|---|" + "---|" * len(sizes) + "---|---|"]
    out += [r for _, r in sorted(rows, key=lambda x: -x[0])]
    return out


# ================================================================ late fill check (what if our order landed later?)
#
# Paper fills happen at the very moment the bot reads the book. A real order lands a bit later, and in a fast
# market the price may have moved. At the end of each run, every buy from that run is re-priced on a fresh book
# (same shares, at least `late_fill.seconds` after the buy) and stored on the position as "late". Records only:
# it never changes a trade. Kalshi legs (arb) aren't re-checked.

LATE_PENDING = []  # (time of buy, track name, token) for this run


def late_fill_check(tracks):
    cfg = CFG.get("late_fill", {})
    if not cfg.get("on", True) or not LATE_PENDING:
        return
    wait = cfg.get("seconds", 30)
    todo, LATE_PENDING[:] = list(LATE_PENDING), []
    last = max(t for t, _, _ in todo)  # every buy gets at least `wait` seconds
    if time.time() - last < wait:
        time.sleep(wait - (time.time() - last))
    seen = {}
    for t0, name, tok in todo:
        pos = (tracks.get(name) or {}).get("positions", {}).get(tok)
        if not pos or "late" in pos or not str(tok).isdigit():
            continue
        if tok not in seen:
            bk = book(tok)
            seen[tok] = (time.time(), bk)
        t1, bk = seen[tok]
        px = walk(bk["asks"], pos["shares"]) if bk and bk["asks"] else None
        pos["late"] = {"s": round(t1 - t0), "px": None if px is None else round(px, 6)}
    print(f"late fill check: re-priced {len(todo)} buys ({len(seen)} books)")


def late_md(tracks):
    rows = []
    for name, tr in tracks.items():
        fills = [p for p in list(tr["positions"].values()) + tr["closed"] if isinstance(p, dict) and p.get("late")]
        priced = [p for p in fills if p["late"].get("px") is not None]
        if not fills:
            continue
        paid = sum(p["shares"] * p["entry"] for p in priced)
        extra = sum(p["shares"] * (p["late"]["px"] - p["entry"]) for p in priced)
        worse = sum(1 for p in priced if p["late"]["px"] > p["entry"] + 1e-9)
        secs = sum(p["late"]["s"] for p in fills) / len(fills)
        rows.append((-len(fills), f"| {name} | {len(fills)} | {worse} | {len(fills) - len(priced)} | "
                     f"${extra / paid * 100 if paid > EPS else 0:+.2f} | {secs:.0f}s |"))
    out = ["\n## Late fill check\n",
           "Each buy is priced again on a fresh book about half a minute later, as if our order had landed late. "
           "Extra cost per $100 bought (plus = later would have cost more; that's money the paper P&L doesn't show). "
           "Records only, started 2026-11-08.\n"]
    if not rows:
        return out + ["No re-priced buys yet."]
    out += ["| Strategy | Buys checked | Got pricier | Gone (book empty) | Extra cost per $100 | Delay |",
            "|---|---|---|---|---|---|"]
    return out + [r for _, r in sorted(rows)]


# ================================================================ data check (audit 2026-11-09)
#
# Cheap sanity checks on our own book-keeping that fail loudly. They run after every watch and daily job, write
# state/integrity.json, add a "Data check" section to summary.md, and push an alert the first time a new kind of
# problem shows up (at most once a day per problem). Records only: nothing here changes a trade.

def _track_open_cost(tr, src):
    if src == "maker":
        return sum(b["yes_cost"] + b["no_cost"] for b in tr.get("books", {}).values())
    if src == "arb":
        return sum(a["cost"] for a in tr.get("arbs", {}).values())
    if src in ("fullset", "ladder"):
        return sum(x["cost"] for x in tr.get("sets", {}).values())
    if src in ("kmaker", "econ", "kpatient"):
        return sum(o["cost"] for o in tr.get("orders", {}).values())
    return open_cost(tr)


def integrity(tracks, deep=False):
    """-> list of problems {key, track, what}. deep=True (daily) also looks up markets for stuck positions."""
    probs = []

    def bad(key, track, what):
        probs.append({"key": key, "track": track, "what": what})
    day_ago = iso(now() - dt.timedelta(hours=24))
    for name, tr in tracks.items():
        tc = CFG["tracks"].get(name)
        if not tc:
            continue
        src = tc["source"]
        # 1) money adds up: cash = money put in - money in open bets + realized profit
        want = (0.0 if tr["unlimited"] else tr["deposited"]) - _track_open_cost(tr, src) + tr["realized"]
        if abs(tr["cash"] - want) > 0.02:
            bad("cash", name, f"cash ${tr['cash']:.2f} but deposits - open bets + profit = ${want:.2f}")
        s = sum(c.get("pnl", 0.0) for c in tr["closed"])
        if src == "maker":  # bonus on markets still quoted is booked at their close (bug fix 2026-11-11)
            s += sum(b.get("rewards", 0.0) + b.get("merged_pnl", 0.0) + b.get("exit_pnl", 0.0) - b.get("booked", 0.0)
                     for b in tr.get("books", {}).values())
        if abs(s - tr["realized"]) > 0.02:
            bad("realized", name, f"realized ${tr['realized']:.2f} but finished trades add up to ${s:.2f}")
        if not tr["unlimited"] and tr["cash"] < -0.02:
            bad("negative_cash", name, f"cash below zero (${tr['cash']:.2f})")
        rows = list(tr.get("positions", {}).values()) + tr.get("closed", [])
        # 2) every fill is a real order-book fill with a sane price
        recent_est = [r for r in rows if r.get("price_source") not in (None, "book")
                      and r.get("opened", "") >= max(day_ago, "2026-11-09T12")]  # older ones are known (audit)
        if recent_est:
            bad("not_book_fill", name, f"{len(recent_est)} buys in the last 24h without a real order-book fill")
        insane = [r for r in rows if not (0 < r.get("entry", 0.5) < 1) or r.get("shares", 1) <= 0
                  or not (0 <= r.get("exit", 0.5) <= 1)]
        if insane:
            bad("insane_price", name, f"{len(insane)} trades with a price outside 0-100c or no shares")
        # 3) both sides of one market in one track (pays exactly $1: the copy/split bug)
        slugs = defaultdict(list)
        for p in tr.get("positions", {}).values():
            if p.get("slug"):
                slugs[p["slug"]].append(p.get("opened", ""))
        # pairs bought before the fix (2026-11-09) are known and listed in the audit; flag only new ones
        both = [sl for sl, o in slugs.items() if len(o) >= 2 and max(o) >= "2026-11-09T12"]
        if both:
            bad("both_sides", name, f"holds both sides of {len(both)} market(s), e.g. {both[0][:50]}")
        # 4) a perfect record on many trades is a red flag (endgame_strict's 208/0 was fake fills)
        n = len(tr.get("closed", []))
        losses = sum(1 for c in tr.get("closed", []) if c.get("pnl", 0) < 0)
        if n >= 30 and losses == 0 and src not in ("arb", "fullset", "ladder"):
            bad("too_good", name, f"{n} finished trades and not one loss: check the fills before trusting it")
        # 5) maker rewards: a model, flag it if it pays more than $5 a day per $100 tied up
        if src == "maker" and tr.get("books"):
            mins = sum(b.get("minutes", 0) for b in tr["books"].values()) + sum(c.get("minutes_quoted", 0) for c in tr["closed"])
            days = mins / 1440 / max(len(tr["books"]), 1)
            per = tr.get("rewards", 0.0) / max(days, 0.01) / max(tr["start_cash"], 1) * 100
            if days >= 0.5 and per > 5:
                bad("maker_rewards_high", name, f"modelled rewards ~${per:.0f}/day per $100: unverified, likely optimistic")
        # 6) a scan that keeps failing (added 2026-11-14: sharp_pinnacle and soccer_draw went 2 days silent on an
        #    HTTP 406 and nothing flagged it). Fast tracks write `status` on every scan that gets through.
        if src in FAST_SOURCES and not tc.get("stopped"):
            ran = parse_iso(load("scan_state.json", {}).get("fast_last", {}).get(name))
            seen = parse_iso((tr.get("status") or {}).get("at"))
            if (_STATUS.get(name) or {}).get("msg"):
                seen = now()  # this run's scan got through; stamp_status only copies it in after this check
            gap = dt.timedelta(minutes=max(360, 4 * rules_for(name).get("scan_every_minutes", 60)))
            if ran and ran > now() - gap and (seen is None or seen < now() - gap):
                bad("scan_failing", name, f"scans run but none got through since {str(seen)[:16] if seen else 'the start'} (check the watch log)")
    if deep:
        prefetch_markets(p.get("slug") for tr in tracks.values() for p in tr["positions"].values())
        for name, tr in tracks.items():
            stuck = 0
            for tok, p in tr.get("positions", {}).items():
                m = market_by_slug(p.get("slug"))
                if m is None or (m.get("closed") and resolved_payout(m, tok) is None):
                    stuck += 1
            if stuck:
                bad("stuck", name, f"{stuck} open bets whose market is closed (or gone) but never paid out")
    return probs


def integrity_run(tracks, deep=False):
    try:
        probs = integrity(tracks, deep)
    except Exception as e:
        probs = [{"key": "check_crashed", "track": "-", "what": f"data check failed: {e}"}]
    old = load("integrity.json", {})
    if deep:
        cur = {f"{p['key']}:{p['track']}" for p in probs}
    else:  # the 'stuck' problems are only looked up daily: keep their alert marks between daily runs
        cur = {f"{p['key']}:{p['track']}" for p in probs + old.get("deep_problems", [])}
    alerted = {k: v for k, v in old.get("alerted", {}).items() if k in cur}  # one push per problem while it lasts
    warn_only = ("maker_rewards_high", "too_good")
    fresh = [p for p in probs if p["key"] not in warn_only and f"{p['key']}:{p['track']}" not in alerted]
    if fresh:
        push("DATA CHECK: something doesn't add up",
             "\n".join(f"{p['track']}: {p['what']}" for p in fresh[:8]) + "\nDetails in summary.md (Data check).",
             tags="warning")
        for p in fresh:
            alerted[f"{p['key']}:{p['track']}"] = iso()
    out = {"checked": iso(), "problems": [p for p in probs if p["key"] != "stuck"], "alerted": alerted,
           "deep_checked": iso() if deep else old.get("deep_checked"),  # the daily 'stuck' check is kept till the next one
           "deep_problems": [p for p in probs if p["key"] == "stuck"] if deep else old.get("deep_problems", [])}
    save("integrity.json", out)
    return probs


def integrity_md():
    d = load("integrity.json", {})
    probs = d.get("problems", []) + d.get("deep_problems", [])
    out = ["\n## Data check\n",
           "Sanity checks on the bot's own numbers after every run: money adds up, every fill was a real order-book "
           "fill, no track holds both sides of a market, nothing stuck unpaid, and no suspiciously perfect records. "
           f"Last check {d.get('checked', 'never')}.\n"]
    if not probs:
        return out + ["All clear."]
    return out + [f"- **{p['track']}** ({p['key']}): {p['what']}" for p in probs]


# ================================================================ commands

def today_utc():
    return now().strftime("%Y-%m-%d")


def lab_exits_due():
    mins = CFG.get("ranking", {}).get("lab_exit_minutes", 30)
    last = parse_iso(load("scan_state.json", {}).get("last_lab_exits"))
    return last is None or (now() - last).total_seconds() >= mins * 60 - 120


def void_double_legs(tracks):
    """Cleanup for the both-sides bug (fixed 2026-11-10): if a copy track still holds both sides of a market, the
    side bought second should never have been bought. Undo that buy (money back, trade removed, noted in 'voided').
    Pairs from before the 2026-11-09 audit are known and left alone."""
    for name, tr in tracks.items():
        if CFG["tracks"].get(name, {}).get("source") not in COPY_SOURCES:
            continue
        by_slug = defaultdict(list)
        for tok, p in tr["positions"].items():
            if p.get("slug"):
                by_slug[p["slug"]].append(tok)
        for slug, toks in by_slug.items():
            if len(toks) < 2:
                continue
            toks.sort(key=lambda t: tr["positions"][t].get("opened", ""))
            for tok in toks[1:]:
                p = tr["positions"][tok]
                if p.get("opened", "") < "2026-11-09T12":
                    continue
                cost = p["shares"] * p["entry"] + p.get("entry_fee", 0.0)
                tr["positions"].pop(tok)
                tr["cash"] = round(tr["cash"] + cost, 6)
                tr.setdefault("voided", []).append({**{k: p.get(k) for k in ("title", "outcome", "entry", "shares",
                                                    "opened", "slug")}, "token": tok, "voided_at": iso(),
                                                    "why": "bought the other side of a market it already held"})
                log_event({"type": "paper_void", "track": name, "token": tok, "title": p.get("title"),
                           "outcome": p.get("outcome"), "refund": round(cost, 4),
                           "reason": "both-sides bug: second side removed"})
                print(f"{name}: voided {p.get('outcome')} on {slug[:50]} (both sides held)")


def run_copy_tracks(tracks):
    try:
        live = follow_wallets(tracks)
        follow_consensus(tracks, live)
    except Exception as e:
        print(f"wallet copy failed: {e}")
    try:
        void_double_legs(tracks)
    except Exception as e:
        print(f"both-sides cleanup failed: {e}")


def watch():
    tracks = load_tracks()
    try:
        follow_leader(tracks)
    except Exception as e:
        print(f"leader check failed: {e}")
    run_copy_tracks(tracks)
    lab_due = lab_exits_due()
    manage_exits(tracks, lab=lab_due)  # also pays out resolved endgame positions
    if lab_due:
        st = load("scan_state.json", {})
        st["last_lab_exits"] = iso()
        save("scan_state.json", st)
    for step in (arb_settle, arb_check, fullset_settle, ladder_settle, ladder_check, run_endgame, run_fast, maker_cycle, kmaker_cycle, econ_cycle, kpatient_cycle):
        try:
            step(tracks)
        except Exception as e:
            print(f"{step.__name__} failed: {e}")
    if panic_scan_due():
        markets = scan_markets()
        if markets:
            run_strategies(tracks, markets, panic_only=True)
        try:
            fullset_check(tracks)
        except Exception as e:
            print(f"fullset_check failed: {e}")
        st = load("scan_state.json", {})
        st["last_panic_scan"] = iso()
        save("scan_state.json", st)
    try:
        late_fill_check(tracks)
    except Exception as e:
        print(f"late fill check failed: {e}")
    integrity_run(tracks)
    stamp_status(tracks)
    save("tracks.json", tracks)
    try:
        refresh_top(tracks)
    except Exception as e:
        print(f"top list refresh failed: {e}")
    # GitHub's scheduler sometimes skips the daily run entirely; catch up from here.
    if now().hour >= 5 and load("scan_state.json", {}).get("last_daily") != today_utc():
        print("daily job hasn't run today (GitHub skipped it?); catching up now")
        daily(force=False)


def settle_resolved(tracks):
    prefetch_markets(p.get("slug") for tr in tracks.values() for p in tr["positions"].values())
    for name, tr in tracks.items():
        for tok in list(tr["positions"]):
            payout = resolved_payout(market_by_slug(tr["positions"][tok].get("slug")), tok)
            if payout is not None:
                paper_close(tr, name, tok, payout, 0.0, "resolved")


def daily(force=None):
    if force is None:
        force = os.environ.get("FORCE", "").strip().lower() == "true"
    if not force and load("scan_state.json", {}).get("last_daily") == today_utc():
        print("daily job already ran today; skipping (set FORCE=true to re-run)")
        return
    tracks = load_tracks()
    settle_resolved(tracks)
    manage_exits(tracks)
    run_copy_tracks(tracks)
    markets = scan_markets()
    if markets:
        lists = run_strategies(tracks, markets)
        save_candidates(lists)
        st = load("scan_state.json", {})
        st["last_panic_scan"] = iso()
        save("scan_state.json", st)
    for step in (arb_settle, lambda t: arb_propose(), arb_check, fullset_settle, fullset_check,
                 ladder_settle, lambda t: ladder_discover(), lambda t: ladder_check(t, force=True), run_endgame):
        try:
            step(tracks)
        except Exception as e:
            print(f"arb/endgame/full-set step failed: {e}")
    try:
        settle_his_exits()
    except Exception as e:
        print(f"settling his exits failed: {e}")
    try:
        est = his_book_estimate()
        save("his_book.json", {"generated": iso(), **est})
    except Exception as e:
        print(f"book estimate failed: {e}")
    try:
        late_fill_check(tracks)
    except Exception as e:
        print(f"late fill check failed: {e}")
    integrity_run(tracks, deep=True)
    stamp_status(tracks)
    save("tracks.json", tracks)
    st = load("scan_state.json", {})
    st["last_daily"] = today_utc()
    save("scan_state.json", st)
    push_scoreboard(write_summary(tracks))


def mark(pos, tok):
    """Value of an open position per share: the listed price, but never more than the best bid while the market is
    still trading. Bug fix 2026-11-09 (audit): the listed price alone made open bets look about $66 richer (out of
    $2,890) than selling them would pay, mostly in thin weather and copy-track markets."""
    m = market_by_slug(pos.get("slug"))
    p = token_price_from_market(m, tok)
    if p is None:
        return pos["entry"]
    if m and not m.get("closed"):
        toks = market_tokens(m)
        bb, ba = fnum(m.get("bestBid"), None), fnum(m.get("bestAsk"), None)
        bid = bb if toks and tok == toks[0] else (1 - ba if toks and tok in toks and ba is not None else None)
        if bid is not None and 0 <= bid < p:
            p = bid
    return p


def write_summary(tracks):
    today = now().strftime("%Y-%m-%d")
    stats, md, detail = {}, [], []
    md.append(f"# Paper bot summary - {iso()}\n")
    md.append(f"Following **{CFG['leader']['name']}** (`{CFG['leader']['address']}`). Paper money only.\n")
    md.append("Main tracks below; all " + str(len(tracks)) + " strategies (incl. the lab) are ranked at the end.\n")
    md.append("| Track | P&L | Open | Closed (W/L) | Cash | Notes |")
    md.append("|---|---|---|---|---|---|")
    prefetch_markets(p.get("slug") for tr in tracks.values() for p in tr["positions"].values())
    lab_rows = []
    for name, tr in tracks.items():
        src = CFG["tracks"].get(name, {}).get("source")
        if src in ("arb", "fullset", "ladder", "maker", "kmaker", "econ", "kpatient"):
            row, stats[name], lines = {"arb": arb_summary, "fullset": fullset_summary, "ladder": ladder_summary,
                                       "maker": maker_summary, "kmaker": kmaker_summary, "econ": econ_summary,
                                       "kpatient": kpatient_summary}[src](name, tr)
            md.append(row)
            detail += lines
            continue
        unreal, open_rows = 0.0, []
        for tok, pos in tr["positions"].items():
            px = mark(pos, tok)
            u = pos["shares"] * px - (pos["shares"] * pos["entry"] + pos.get("entry_fee", 0.0))
            unreal += u
            open_rows.append(f"| {pos.get('title', '')[:70]} | {pos.get('outcome')} | {cents(pos['entry'])} | "
                             f"{cents(px)} | {u:+.2f} | {str(pos.get('end', ''))[:10]} |")
        wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
        losses = len(tr["closed"]) - wins
        pnl = tr["realized"] + unreal
        if tr["unlimited"]:
            cash = "unlimited"
            notes = f"money needed so far ${max(0.0, -tr['min_cash']):.2f}; most tied up at once ${tr['peak_open_cost']:.2f}"
        else:
            cash = f"${tr['cash']:.2f}"
            notes = f"refills {tr['refills']}; " if CFG["tracks"][name].get("refill") else ""
            notes += f"skipped (no cash) {tr['skipped_no_cash']}"
        (lab_rows if is_lab(name) else md).append(
            f"| {name} | {pnl:+.2f} | {len(tr['positions'])} | {len(tr['closed'])} ({wins}/{losses}) | {cash} | {notes} |")
        stats[name] = {"pnl": round(pnl, 4), "realized": round(tr["realized"], 4), "unrealized": round(unreal, 4),
                       "open": len(tr["positions"]), "closed": len(tr["closed"]), "wins": wins, "losses": losses,
                       "cash": None if tr["unlimited"] else round(tr["cash"], 4), "deposited": tr["deposited"],
                       "refills": tr["refills"], "money_needed": round(max(0.0, -tr["min_cash"]), 4),
                       "peak_open_cost": tr["peak_open_cost"], "skipped_no_cash": tr["skipped_no_cash"]}
        if is_lab(name):
            continue  # lab tracks: one row each in the lab table + the ranking, no per-position detail
        detail.append(f"\n## {name}\n{CFG['tracks'].get(name, {}).get('label', '')}\n")
        if src == "endgame" and not rules_for(name).get("fade"):
            pr = endgame_proof(tr)
            stats[name]["proof"] = pr
            tiers = endgame_tier_stats(tr)
            detail.append(f"**Proof status:** {pr['verdict']}\n")
            if tiers:
                detail.append("By signal: " + ", ".join(f"{t} {v['finished']} finished / {v['flips']} flipped"
                                                         for t, v in tiers.items()) + "\n")
            try:
                detail.append(shadow_summary(tr))
            except Exception as e:
                print(f"shadow summary failed: {e}")
        if open_rows:
            detail.append("| Market | Side | Entry | Now | P&L | Ends |\n|---|---|---|---|---|---|")
            detail += open_rows
        else:
            detail.append("No open positions.")

    hb = load("his_book.json", None)
    if hb:
        md.append(f"\n**His book right now:** {hb['open_positions']} open positions worth ${hb['his_value']:,.0f}. "
                  f"Holding all of them at the {CFG['shares_per_trade']}-share minimum would cost "
                  f"${hb['cost_min_size_each']:,.2f}. Biggest single position = "
                  f"{hb['biggest_position_share'] * 100:.0f}% of his book.\n")
    hist = os.path.join(STATE, "history.csv")
    before = {}
    if os.path.exists(hist):
        with open(hist) as fh:
            for row in fh.read().splitlines()[1:]:
                f = row.split(",")
                if len(f) >= 3 and f[0] < today:
                    before[f[1]] = fnum(f[2])  # rows are in date order: the last one before today wins
    for n, s_ in stats.items():
        s_["trust"] = trust(tracks[n], len(stats))
        s_["trust_paper"] = trust(tracks[n], len(stats), None)
        s_["today"] = round(s_["pnl"] - before.get(n, 0.0), 4)
    if lab_rows:
        md.append("\n**Lab** (added 2026-11-08: 40 copied wallets, crowd, sabsabinxz and rule variants; frozen until "
                  "2027-01-01 so the test stays clean):\n")
        md += ["| Track | P&L | Open | Closed (W/L) | Cash | Notes |", "|---|---|---|---|---|---|"] + lab_rows
    md += detail
    md += leaderboard_md(stats)
    try:
        md += real_money_md(tracks, stats)
        md += late_md(tracks)
    except Exception as e:
        print(f"real money summary failed: {e}")
    try:
        md += integrity_md()
        md += push_md()
    except Exception as e:
        print(f"data check summary failed: {e}")
    try:
        md += his_exit_summary()
    except Exception as e:
        print(f"exit summary failed: {e}")

    md.append("\n## Last 24 hours\n")
    cutoff = now() - dt.timedelta(hours=24)
    p, lines = os.path.join(STATE, "events.jsonl"), []
    keep = ("leader_open", "leader_exit", "paper_buy", "paper_close", "skip_no_cash", "refill",
            "arb_open", "arb_close", "arb_half_settled", "arb_opportunity", "set_open", "set_close",
            "maker_open", "maker_close")
    if os.path.exists(p):
        with open(p) as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                t = parse_iso(ev.get("ts"))
                if t and t >= cutoff and ev.get("type") in keep:
                    bits = [ev["ts"][11:16] + " UTC", ev["type"], ev.get("track", ""), ev.get("outcome", ""),
                            str(ev.get("title", ""))[:70]]
                    if ev.get("price") is not None:
                        bits.append(f"@ {ev['price']}")
                    if ev.get("pnl") is not None:
                        bits.append(f"pnl {ev['pnl']:+.2f}")
                    if ev.get("reason"):
                        bits.append(f"({ev['reason']})")
                    lines.append("- " + " ".join(b for b in bits if b))
    md += lines or ["Nothing happened (fittingly)."]
    kfl = os.path.join(STATE, "kfast_live", "report.md")   # live fast-bot test (kfastlive.py, its own workflow)
    if os.path.exists(kfl):
        with open(kfl) as fh:
            md += [""] + [("#" + x if x.startswith("#") else x) for x in fh.read().splitlines()]

    with open(os.path.join(STATE, "summary.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    save("summary.json", {"generated": iso(), "tracks": stats, "his_book": hb})

    rows = []
    if os.path.exists(hist):
        with open(hist) as fh:
            rows = [r for r in fh.read().splitlines()[1:] if r and not r.startswith(today + ",")]
    rows += [f"{today},{n},{s['pnl']},{s['open']},{s['closed']},{s['wins']},{s['losses']},{s['refills']},{s['money_needed']}"
             for n, s in stats.items()]
    with open(hist, "w") as fh:
        fh.write("date,track,pnl,open,closed,wins,losses,refills,money_needed\n" + "\n".join(rows) + "\n")
    print("\n".join(md[:12]))
    return stats


def top_eligible(s):
    """Top 10: ahead on 3+ finished trades AND still ahead once open bets are counted at today's price
    (2026-11-08: a strategy with a nice finished-trade record but open bets sinking it shouldn't be on top)."""
    return s["trust"]["finished"] >= 3 and s["trust"]["avg_per_100"] > 0 and s["pnl"] > 0


def is_stopped(name):
    """Jan stopped this track (12 Nov 2026): "stopped" (no new bets) or "retired" (maker, closed out) in config."""
    tc = CFG["tracks"].get(name, {})
    return bool(tc.get("stopped") or tc.get("retired"))


def save_top(stats):
    """Pick the top 10 (only strategies actually ahead on 3+ finished trades) and save it to state/top.json.
    Stopped tracks never make the list (Jan, 12 Nov: drop them from the dashboard)."""
    n = CFG["push"].get("top_n", 10)
    top = [x for x in ranked(stats) if top_eligible(stats[x]) and not is_stopped(x)][:n]
    save("top.json", {"generated": iso(), "tracks": top})
    return top


def refresh_top(tracks):
    """Hourly from watch (2026-11-09 fix): re-rank and rewrite top.json + summary.md without the scoreboard push.
    Before this the list was only rebuilt by the daily run, so a strategy that went from winning to losing
    (endgame_sell98 after the phantom-fill cleanup) kept its trade pushes all day while new leaders stayed muted."""
    last = parse_iso(load("top.json", {}).get("generated"))
    if last and now() - last < dt.timedelta(minutes=CFG["push"].get("top_refresh_min", 60)):
        return
    old = load("top.json", {}).get("tracks", [])
    top = save_top(write_summary(tracks))
    if top != old:
        print(f"top list refreshed: +{[x for x in top if x not in old]} -{[x for x in old if x not in top]}")


def push_scoreboard(stats):
    """Daily ntfy scoreboard: only the top 10 by trust (all strategies are still tracked; summary.md ranks them all).
    Also saves the top 10 to state/top.json: only those strategies send trade pushes until the next scoreboard."""
    n = CFG["push"].get("top_n", 10)
    top = save_top(stats)
    lines = [] if len(top) >= n else [f"Only {len(top)} strategies are ahead after 3+ finished bets so far."]
    for i, name in enumerate(top, 1):
        s, t = stats[name], stats[name]["trust"]
        lines.append(f"{i}. {name}: {usd(s['pnl'])} (today {usd(s.get('today', 0))}), {t['finished']} finished. "
                     f"{plain_verdict(t, name.startswith('control_'))[1].split(' (')[0]}"
                     + (f", worst case {usd(t['worst_per_100'])[:-3]} per $100" if t["finished"] >= 10 else ""))
    if rs_rank_size():
        lines.append(f"(ranked on what a real ${rs_rank_size()} bet would have made)")
    best = max(stats, key=lambda x: stats[x].get("today", 0), default=None)
    if best and best not in top and stats[best].get("today", 0) > 0:
        lines.append(f"Best day (probably luck): {best} +${stats[best]['today']:.2f}")
    proven = sum(1 for x in stats.values() if x["trust"]["proven"])
    lines.append(f"{len(stats)} strategies tracked, {proven} clearly work so far. Dashboard has the rest.")
    push("Paper top 10", "\n".join(lines), tags="bar_chart")


def selftest():
    lead = CFG["leader"]
    print("== positions")
    rows = leader_positions(lead["address"])
    print(f"rows: {len(rows)}")
    if rows:
        print("raw keys:", sorted(rows[0].keys()))
        print("raw row:", json.dumps(rows[0])[:1500])
        p = norm_pos(rows[0])
        print("normalized:", p)
        m = market_by_slug(p["slug"])
        print("== market by slug; keys:", sorted(m.keys()) if m else None)
        if m:
            print("tokens:", market_tokens(m), "prices:", m.get("outcomePrices"), "fee:", fee_rate(m),
                  "closed:", m.get("closed"), "end:", m.get("endDateIso"), "1d chg:", m.get("oneDayPriceChange"))
            print("token in market:", p["token"] in market_tokens(m))
        b = book(p["token"])
        print("== book top:", None if not b else {"ask": b["asks"][:2], "bid": b["bids"][:2], "min": b["min_size"]})
        print("quote buy 5:", quote(p["token"], "buy", 5, m))
    print("== market scan sample")
    res = http_json(f"{GAMMA}/markets/keyset", {"closed": "false", "limit": 5, "version": ["v1", "v2"]})
    ms = envelope_rows(res, "markets", "data")
    print("keyset type:", type(res).__name__, "keys:", sorted(res.keys()) if isinstance(res, dict) else None)
    if ms:
        print("market keys:", sorted(ms[0].keys()))
        print("sample:", {k: ms[0].get(k) for k in ("question", "endDateIso", "outcomes", "outcomePrices", "liquidity",
                                                   "liquidityNum", "volume", "volumeNum", "oneDayPriceChange",
                                                   "feesEnabled", "feeSchedule", "version")})
    if rows:
        print("== price history (1d) for first position:", day_change(norm_pos(rows[0])["token"]))
    print("== his book:", his_book_estimate())
    push("Paper bot self-test", "If you can read this, alerts work. Paper money only.", tags="white_check_mark")
    print("selftest done")


def arbtest():
    """Dry run of the twin finder: prints the candidate list (used by the manual probe workflow, nothing committed)."""
    arb_propose()
    d = load("arb_candidates.json", {})
    print({k: v for k, v in d.items() if k != "candidates"})
    for c in d.get("candidates", []):
        k, p = c["kalshi"], c["polymarket"]
        print(f"\n[{c['match_score']}] gap~{c['est_gap_before_fees']} guess K-YES={c['guess_poly_outcome_for_kalshi_yes'][:3]}"
              f"\n   K {k['ticker']} ({str(k['close_time'])[:10]}) yes {k['yes_ask']} no {k['no_ask']}: {k['title']} | {k['yes_sub_title']}"
              f"\n   P {p['slug'][:50]} ({p['end']}) bid/ask {p['best_bid_yes']}/{p['best_ask_yes']}: {p['question']}")


def dryrun():
    """Endgame + every-horse on live data without saving anything (manual probe workflow)."""
    tracks = load_tracks()
    run_endgame(tracks)
    fullset_check(tracks)
    ladder_discover()
    ladder_check(tracks, force=True)
    for name in ("endgame", "every_horse", "ladder"):
        tr = tracks.get(name, {})
        for p in tr.get("positions", {}).values():
            print(f"WOULD BUY [{name}] {p.get('tier')}: {p['outcome']} @ {cents(p['entry'])} - {p['title']} (ends {p.get('end')})")
        for sid, st in tr.get("sets", {}).items():
            print(f"WOULD BUY [{name}] {sid}: cost ${st['cost']:.2f} pays ${st['guaranteed']:.2f}, edge {st['edge'] * 100:.1f}c")
        for sid, v in sorted(tr.get("seen", {}).items(), key=lambda x: -x[1]["edge"])[:8]:
            print(f"  closest set: {sid} {v['edge'] * 100:+.1f}c")


def copytest():
    """Live check of the lab copy tracks (manual probe workflow, saves nothing): positions per wallet, what the
    crowd holds, and how many rule-variant candidates each track sees today."""
    global save, log_event
    save = lambda name, obj: print(f"(not saving {name})")  # noqa: E731
    log_event = lambda ev: print("EVENT", json.dumps(ev, sort_keys=True)[:200])  # noqa: E731
    t0 = time.time()
    r = rule_set("wallet_copy")
    for n in wallet_tracks():
        rows, complete = wallet_positions(CFG["tracks"][n]["address"], r.get("max_pages", 4))
        live = [p for p in rows or [] if p["size"] >= 5 and not p["redeemable"]]
        big = [p for p in live if p["size"] * max(p["avg"], 0.01) >= r["min_open_usd"]]
        print(f"{n}: {None if rows is None else len(rows)} rows (complete={complete}), {len(live)} live, {len(big)} >= ${r['min_open_usd']}"
              + (f", e.g. {big[0]['outcome']} @ {cents(big[0]['cur'])} {big[0]['title'][:50]}" if big else ""))
    print(f"wallet fetch took {time.time() - t0:.1f}s")
    tracks = load_tracks()
    live = follow_wallets(tracks)
    follow_consensus(tracks, live)
    for n in ("consensus_2", "consensus_3"):
        for p in tracks.get(n, {}).get("positions", {}).values():
            print(f"WOULD BUY [{n}] {p['outcome']} @ {cents(p['entry'])} ({p.get('wallets')} wallets) - {p['title'][:70]}")
    markets = scan_markets()
    for n, tc in CFG["tracks"].items():
        if tc.get("lab") and tc["source"] in ("screener", "random", "momentum"):
            rr = rules_for(n)
            c = momentum_candidates(markets, rr) if tc["source"] == "momentum" else \
                boring_side_candidates(markets, rr, random.Random(f"{today_utc()}-{n}"))
            print(f"{n}: {len(c)} candidates" + (f", top: {c[0]['outcome']} @ {cents(c[0]['price'])} {c[0]['title'][:60]}" if c else ""))
    for n, tc in CFG["tracks"].items():
        if tc.get("lab") and tc["source"] == "endgame":
            print(f"{n}: {len(endgame_candidates(rules_for(n)))} candidates")
    print(f"copytest took {time.time() - t0:.1f}s")


def depthtest():
    """Live real-size check (manual probe workflow, saves nothing): re-prices every open position's token on today's
    order book at each stake in config "real_size", as if it were bought now."""
    tracks = load_tracks()
    seen, per_track = {}, defaultdict(list)
    for name, tr in tracks.items():
        for tok, pos in tr["positions"].items():
            per_track[name].append(tok)
            seen.setdefault(tok, pos)
    toks = list(seen)[:int(os.environ.get("DEPTH_MAX", "150"))]
    with ThreadPoolExecutor(8) as ex:
        books = dict(zip(toks, ex.map(book, toks)))
    res = {}
    for tok in toks:
        bk = books.get(tok)
        if not bk or not bk["asks"]:
            continue
        p5 = walk(bk["asks"], 5)
        if p5 is None:
            continue
        LAST_BOOK[tok] = (time.time(), bk)
        r = rs_buy(tok, 5, p5, taker_fee(5, p5, 0.0))
        res[tok] = (p5, {k: v for k, v in r["s"].items()})
        line = " | ".join(f"${k}: {v[0]:.0f} sh @ {cents(v[1] / v[0]) if v[0] else '-'}{'' if v[2] else ' PARTIAL'}"
                          for k, v in r["s"].items())
        print(f"{cents(p5)} 5sh | {line} | {seen[tok].get('title', '')[:60]}")
    print("\nPer track (open positions re-priced now; fee not included):")
    for name, ts in per_track.items():
        rows = [res[t] for t in ts if t in res]
        if not rows:
            continue
        parts = []
        for sz in rs_sizes():
            k = str(sz)
            worse = [v[k][1] / v[k][0] - p5 for p5, v in rows if v[k][0] > EPS]
            fit = sum(min(v[k][1], sz) for _, v in rows) / len(rows)
            full = sum(1 for _, v in rows if v[k][2])
            parts.append(f"${sz}: fits ${fit:.0f} avg, {full}/{len(rows)} full, "
                         f"+{(sum(worse) / len(worse) if worse else 0) * 100:.1f}c/share")
        print(f"{name} ({len(rows)} open): " + "; ".join(parts))


# ================================================================ lab: finding wallets worth following

def leaderboard(category="OVERALL", period="MONTH", order="PNL", limit=50, pages=2):
    rows, cursor = [], None
    for _ in range(pages):
        params = {"category": category, "timePeriod": period, "orderBy": order, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        res = http_json(f"{DATA}/v2/leaderboard", params)
        rows += envelope_rows(res, "data")
        cursor = ((res.get("pagination") or {}) if isinstance(res, dict) else {}).get("next_cursor")
        if not cursor:
            break
    return rows


def discover():
    """Prints leaderboard wallets with copy-ability stats (run from the manual probe workflow; saves nothing)."""
    seen = {}
    for cat in ("OVERALL", "POLITICS", "SPORTS", "CRYPTO", "CULTURE", "ECONOMICS", "TECH", "FINANCE", "WEATHER", "MENTIONS"):
        for period in ("WEEK", "MONTH", "ALL"):
            try:
                rows = leaderboard(cat, period, "PNL", 50, 2 if period == "MONTH" else 1)
            except Exception as e:
                print(f"leaderboard {cat}/{period} failed: {e}")
                continue
            print(f"leaderboard {cat}/{period}: {len(rows)} rows")
            for r in rows:
                a = str(r.get("user_id") or "").lower()
                if not a:
                    continue
                d = seen.setdefault(a, {"name": r.get("user_name"), "cats": set(), "pnl": {}, "vol": {}})
                d["cats"].add(cat)
                k = f"{cat[:3]}_{period[0]}"
                d["pnl"][k], d["vol"][k] = round(fnum(r.get("pnl"))), round(fnum(r.get("volume")))
    for order in ("VOL",):
        try:
            rows = leaderboard("OVERALL", "MONTH", order, 5, 1)
            print("orderBy VOL sample:", [(r.get("user_name"), round(fnum(r.get("pnl")))) for r in rows])
        except Exception as e:
            print("orderBy VOL failed:", e)
    try:
        res = http_json(f"{DATA}/v2/leaderboard", {"user": CFG["leader"]["address"], "timePeriod": "ALL", "category": "OVERALL"})
        print("leaderboard user filter:", json.dumps(res)[:400])
    except Exception as e:
        print("leaderboard user filter failed:", e)
    print(f"unique wallets: {len(seen)}")
    out = []
    for a, d in seen.items():
        mon = [v for k, v in d["pnl"].items() if k.endswith("_M")]
        tot_pnl = max(d["pnl"].values())
        best_k = max(d["pnl"], key=d["pnl"].get)
        ratio = d["pnl"][best_k] / max(d["vol"][best_k], 1)
        npos, value, acts, recent, kinds = None, None, None, None, Counter()
        try:
            res = http_json(f"{DATA}/v2/positions", {"user": a, "limit": 500})
            rows = [norm_pos(x) for x in envelope_rows(res, "data")]
            live = [p for p in rows if p["size"] >= 1 and not p["redeemable"] and p["cur"] and 0.01 < p["cur"] < 0.99]
            npos = len(live)
            value = round(sum(p["size"] * p["cur"] for p in live))
            for p in live:
                t = p["title"].lower()
                kinds["updown" if "up or down" in t else "sports" if " vs" in t or "o/u" in t else "other"] += 1
            more = bool(((res.get("pagination") or {}) if isinstance(res, dict) else {}).get("next_cursor"))
        except Exception as e:
            print(f"positions failed for {a}: {e}")
            more = None
        try:
            res = http_json(f"{DATA}/v2/activity", {"user": a, "limit": 200})
            ar = envelope_rows(res, "data", "activity")
            ts = [act_time(x) for x in ar]
            ts = [t for t in ts if t]
            acts = len(ar)
            recent = sum(1 for t in ts if (now() - t).days < 7)
            buys = [x for x in ar if str(pick(x, "side", default="")).upper() == "BUY"]
            avg_usd = (sum(fnum(pick(x, "usdc_size", "usdcSize")) or fnum(pick(x, "size")) * fnum(pick(x, "price")) for x in buys)
                       / max(len(buys), 1))
        except Exception as e:
            print(f"activity failed for {a}: {e}")
            avg_usd = None
        row = {"addr": a, "name": d["name"], "cats": sorted(d["cats"]), "pnl": d["pnl"], "ratio": round(ratio, 3),
               "open": npos, "more_pages": more, "value": value, "kinds": dict(kinds), "acts200": acts,
               "acts_7d": recent, "avg_buy_usd": None if avg_usd is None else round(avg_usd)}
        out.append(row)
        print("W", json.dumps(row, sort_keys=True))


def econtest():
    """Dry run of econ_fav on live data: what it would buy now (nothing is saved)."""
    tracks = load_tracks()
    names = econ_names()
    for n in names:   # look further ahead than the real rule so the dry run has something to price
        CFG["rules"][CFG["tracks"][n]["rules"]].update({"min_hours": 0, "max_hours": 24 * 20})
    econ_place(tracks, names, force=True)
    for n in names:
        print(n, tracks[n].get("last_check"), list(tracks[n]["orders"]))
    import econ
    rows = []
    for s_ in econ.LIVE_SERIES:
        for m in kalshi_get("/markets", {"series_ticker": s_, "status": "open", "limit": 200}).get("markets") or []:
            rows.append(dict(m, _series=s_))
    ch = econ.live_chances(rows, int(now().timestamp()))
    for m in rows:
        if m["ticker"] in ch:
            p, mu, sd = ch[m["ticker"]]
            bk = kalshi_asks(m["ticker"]) or ([], [])
            ya = bk[0][0][0] if bk[0] else None
            na = bk[1][0][0] if bk[1] else None
            print(f"  {m['ticker']:34} closes {str(m.get('close_time'))[:16]} forecast {mu:g} (+-{sd:.3g}) "
                  f"YES chance {p:.3f}  YES ask {ya}  NO ask {na}")


def kmakertest():
    """Dry run of the Kalshi late-favorite maker (no state saved): place on the live windows with any minutes left,
    then replay the fill check on the last closed BTC/ETH window as if we had bid 3 minutes before its close."""
    names = kmaker_names()
    tracks = {n: {"unlimited": False, "cash": 100.0, "start_cash": 100, "deposited": 100.0, "refills": 0, "min_cash": 0,
                  "peak_open_cost": 0, "positions": {}, "closed": [], "realized": 0.0, "skipped_no_cash": 0,
                  "orders": {}, "unfilled": 0, "unfilled_log": [], "last_check": {}} for n in names}
    for n in names:
        CFG["rules"][CFG["tracks"][n]["rules"]]["max_minutes_left"] = 15
    kmaker_place(tracks, names)
    for n in names:
        print(n, "last look:", json.dumps(tracks[n]["last_check"]))
    for series in ("KXBTC15M", "KXETH15M"):
        rows = kalshi_get("/markets", {"series_ticker": series, "status": "settled", "limit": 1}).get("markets") or []
        if not rows:
            continue
        m = rows[0]
        close = parse_iso(m["close_time"])
        trades, complete = kalshi_trades(m["ticker"], (close - dt.timedelta(minutes=3)).timestamp(), close.timestamp())
        print(f"{m['ticker']} result {m.get('result')}: {len(trades)} trades in the last 3 min (complete {complete})")
        if not trades:
            continue
        early = sorted(trades, key=lambda t: t["created_time"])[0]
        yp = fnum(early.get("yes_price_dollars"), 0.5)
        side = "yes" if yp >= 0.5 else "no"
        px = yp if side == "yes" else round(1 - yp, 4)
        for off in (0.0, -0.01, -0.03):
            o = {"side": side, "price": round(px + off, 4), "queue": 0.0, "shares": 10,
                 "placed": iso(close - dt.timedelta(minutes=3))}
            got, through = kmaker_fill(o, trades)
            print(f"  bid {side.upper()} {o['price'] * 100:.1f}c 3 min before close: filled {got:.0f}/10 "
                  f"({'through' if through else 'at price'}), {'won' if m.get('result') == side else 'lost'}")


def kpatienttest():
    """Dry run of the Kalshi patient buyer (no state saved): time the listing and the schedule, show what fits."""
    names = kpatient_names()
    tracks = {n: {"unlimited": False, "cash": 500.0, "start_cash": 500, "deposited": 500.0, "refills": 0, "min_cash": 0,
                  "peak_open_cost": 0, "positions": {}, "closed": [], "realized": 0.0, "skipped_no_cash": 0,
                  "orders": {}, "done": [], "unfilled": 0, "last_check": {}} for n in names}
    r = rules_for(names[0])
    t0 = time.time()
    markets = kpatient_open_markets(r)
    t1 = time.time()
    starts = kpatient_starts()
    print(f"open markets {len(markets)} in {t1 - t0:.0f}s; games with a start time {len(starts)} in {time.time() - t1:.0f}s")
    print("sample schedule:", [(k, iso(v)) for k, v in list(starts.items())[:5]])
    print("schedule kinds:", KP_MS_KIND.most_common(12))
    kpatient_place(tracks, names, markets, starts)
    for n in names:
        tr = tracks[n]
        print(n, json.dumps(tr["last_check"]))
        kinds = Counter(o["kind"] for o in tr["orders"].values())
        print(f"  placed {len(tr['orders'])}: {dict(kinds)}, cash left ${tr['cash']:.2f}")
        for o in list(tr["orders"].values())[:12]:
            print(f"   {o['ticker']} {o['side'].upper()} bid {o['price'] * 100:.0f}c (best {o['bid'] * 100:.0f}c, ask {o['ask'] * 100:.0f}c) "
                  f"x{o['shares']} until {o['expires'][11:16]}, ends {o['close'][:16]} | {o['kind']} | {o['title'][:70]}")
    # fill check on a market that just settled: as if we had bid 1c under its last trades an hour before the close
    rows = kalshi_get("/markets", {"status": "settled", "limit": 200}).get("markets") or []
    for m in [x for x in rows if fnum(x.get("volume_fp") or x.get("volume"), 0) >= 100][:3]:
        close = parse_iso(m["close_time"])
        o = {"side": "yes" if m.get("result") == "yes" else "no", "price": 0.95, "queue": 0.0, "shares": 10, "series": m["event_ticker"].split("-")[0],
             "placed": iso(close - dt.timedelta(minutes=65)), "expires": iso(close)}
        trades, complete = kalshi_trades(m["ticker"], parse_iso(o["placed"]).timestamp(), close.timestamp())
        win = kpatient_window(o, trades)
        got, through = kmaker_fill({**o, "placed": "1970-01-01T00:00:00Z"}, win)
        print(f"  fill check {m['ticker']} ({m.get('result')}): {len(trades)} trades in the last 65 min, {len(win)} in the order's window, "
              f"a 95c {o['side'].upper()} order would have got {got:.0f}/10; maker fee {kpatient_maker_fee(o['series'], 10, 0.95)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    {"watch": watch, "daily": daily, "summary": lambda: write_summary(load_tracks()),
     "selftest": selftest, "arbtest": arbtest, "dryrun": dryrun, "discover": discover, "copytest": copytest,
     "depthtest": depthtest, "fasttest": fasttest, "makertest": makertest,
     "kmakertest": kmakertest, "econtest": econtest, "kpatienttest": kpatienttest}[cmd]()
