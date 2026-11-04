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
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

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
        if tc["source"] == "arb":
            for k, v in (("arbs", {}), ("opportunities", 0), ("mismatches", 0), ("last_check", {})):
                tracks[name].setdefault(k, v)
    return tracks


def rules_for(name):
    r = CFG["tracks"][name].get("rules")
    return CFG["rules"].get(r, {}) if r else {}


# ================================================================ push

def push(title, body, click=None, tags=None):
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        print(f"[push skipped, no NTFY_TOPIC] {title} | {body}")
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
    try:
        urllib.request.urlopen(req, timeout=15).read()
    except Exception as e:
        print(f"push failed: {e}")


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
    """Paper fill price. 'buy' takes the ask, 'sell' hits the bid.
    Falls back to the listed price +/- slippage if the book is unavailable."""
    bk = book(token)
    if bk:
        shares = max(shares, bk["min_size"])
        px = walk(bk["asks"] if side == "buy" else bk["bids"], shares)
        if px is not None:
            return px, shares, "book"
    mid = token_price_from_market(m, token) if m else None
    if mid is None:
        return None, shares, "none"
    slip = CFG["fallback_slippage"]
    px = min(0.999, mid + slip) if side == "buy" else max(0.001, mid - slip)
    return px, shares, "estimate"


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
    track["peak_open_cost"] = round(max(track["peak_open_cost"], open_cost(track)), 6)
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
    track["closed"].append(rec)
    log_event({"type": "paper_close", "track": name, "token": token, "title": pos.get("title"),
               "outcome": pos.get("outcome"), "price": round(price, 4), "pnl": round(pnl, 4), "reason": reason})
    return rec


def manage_exits(tracks):
    """Take-profit / stop-loss / settlement for the rule-based tracks (not the mirrors)."""
    for name, tr in tracks.items():
        tc = CFG["tracks"][name]
        if tc["source"] in ("leader", "arb"):
            continue
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
            target = pos.get("target") or rules.get("take_profit")
            stop = rules.get("stop_loss")
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
            rec = paper_close(tr, name, tok, fill, taker_fee(pos["shares"], fill, fee_rate(m)), f"{reason}, {how}")
            if rec and CFG["push"].get("on_claude_trades"):
                push(f"[{name}] SELL {pos.get('outcome')} @ {cents(fill)} ({rec['pnl']:+.2f})",
                     f"{pos.get('title')}\nReason: {reason}",
                     click=market_link(pos.get("slug", ""), pos.get("event_slug", "")), tags="moneybag")


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


def slim(p):
    return {k: p[k] for k in ("size", "avg", "outcome", "title", "slug", "event_slug", "end")}


def leader_tracks():
    return [n for n, tc in CFG["tracks"].items() if tc["source"] == "leader"]


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

    # ---- new positions he opened
    for tok, p in cur.items():
        if prev.get(tok, {}).get("size", 0) >= 1 or p["redeemable"] or p["size"] < 5:
            continue
        if p["size"] * max(p["avg"], 0.01) < lead["min_open_usd"]:
            continue
        m = market_by_slug(p["slug"])
        if m and m.get("closed"):
            continue
        end = parse_iso(p["end"]) or parse_iso((m or {}).get("endDateIso"))
        if end and end < now():
            continue
        px, shares, how = quote(tok, "buy", n, m)
        rate = fee_rate(m)
        took = []
        for name in leader_tracks():
            tc, tr = CFG["tracks"][name], tracks[name]
            if px is None or tok in tr["positions"] or not (tc["min_price"] <= px <= tc["max_price"]):
                continue
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
                 f"{p['title']}\nHe holds {p['size']:.0f} sh (${p['size'] * p['avg']:,.0f}). "
                 f"Your price now: {cents(px)}.\nPaper copied by: {', '.join(took) or 'none'}",
                 click=market_link(p["slug"], p["event_slug"]), tags="chart_with_upwards_trend")

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
            elif resolved:
                continue  # resolved but final price not published yet; daily run settles it
            else:
                sh = tr["positions"][tok]["shares"]
                px, _, how = quote(tok, "sell", sh, m)
                if px is None:
                    continue
                paper_close(tr, name, tok, px, taker_fee(sh, px, fee_rate(m)), f"leader exit ({how})")
            closed_by.append(name)
        log_event({"type": "leader_exit", "token": tok, "title": q.get("title"), "outcome": q.get("outcome"),
                   "size_before": q.get("size"), "size_after": after, "resolved": resolved, "closed_by": closed_by})
        if CFG["push"]["on_leader_trades"] and not resolved:
            push(f"{lead['name']} EXIT {q.get('outcome')} ({q.get('size', 0):.0f} -> {after:.0f} sh)",
                 f"{q.get('title')}\nPaper closed in: {', '.join(closed_by) or 'none'}",
                 click=market_link(q.get("slug", ""), q.get("event_slug", "")), tags="chart_with_downwards_trend")

    new_snap = {"positions": {t: slim(p) for t, p in cur.items()}}
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


# ================================================================ strategies on the whole market

def scan_filters():
    """Server-side pre-filter covering the screener/panic strategies' widest settings (deadline window, liquidity).
    The arb track scans separately with its own window."""
    rs = [rules_for(n) for n, tc in CFG["tracks"].items() if tc["source"] in ("screener", "panic")]
    lo = now() + dt.timedelta(days=min(r["min_days"] for r in rs))
    hi = now() + dt.timedelta(days=max(r["max_days"] for r in rs))
    return {"end_date_min": iso(lo), "end_date_max": iso(hi),
            "liquidity_num_min": min(r["min_liquidity"] for r in rs)}


def scan_markets(filters=None):
    """Open markets (one pass). Tries server-side filters first;
    falls back to the unfiltered list if the API rejects them."""
    filters = filters or scan_filters()
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
    end = parse_iso(m.get("endDateIso") or m.get("endDate"))
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
         "theme": theme_of(q), "end": (parse_iso(m.get("endDateIso") or m.get("endDate")) or now()).strftime("%Y-%m-%d"),
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


def boring_side_candidates(markets, r):
    """Likely outcome priced in [min_price, max_price] on deadline markets."""
    out = []
    for m in markets:
        prices = binary(m)
        if not prices:
            continue
        b = base_filter(m, r)
        if not b:
            continue
        i = 0 if prices[0] >= prices[1] else 1
        if r["min_price"] <= prices[i] <= r["max_price"]:
            out.append(candidate(m, i, b[0], b[1]))
    # "No, nothing happens" first, then fee-free if wanted, then sooner deadlines, then deepest markets
    out.sort(key=lambda c: (not c["nothing_happens"],
                            (c["fee_rate"] > 0) if r.get("prefer_fee_free") else 0,
                            c["days"] if r.get("prefer_fee_free") else 0,
                            -c["liquidity"]))
    return out


def day_change(token):
    """(price ~24h ago, price now) for a token from Polymarket's price history, or None."""
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


def buy_candidates(tracks, name, cands, limit):
    tc, tr, r = CFG["tracks"][name], tracks[name], rules_for(name)
    held_events = {p.get("event_key") for p in tr["positions"].values()}
    themes = {}
    for p in tr["positions"].values():
        if p.get("theme"):
            themes[p["theme"]] = themes.get(p["theme"], 0) + 1
    n, bought = CFG["shares_per_trade"], []
    for c in cands:
        if len(bought) >= limit or len(tr["positions"]) >= r.get("max_open", 999):
            break
        if c["token"] in tr["positions"] or c["event_key"] in held_events:
            continue
        if c["theme"] and themes.get(c["theme"], 0) >= r.get("max_per_theme", 999):
            continue
        px, shares, how = quote(c["token"], "buy", n, c["market"])
        lo = r.get("min_price", 0.0)
        hi = r.get("max_price", 1.0) + 0.01
        if px is None or not (lo <= px <= hi):
            continue
        meta = {"title": c["title"], "outcome": c["outcome"], "slug": c["slug"], "event_slug": c["event_slug"],
                "event_key": c["event_key"], "theme": c["theme"], "end": c["end"], "source": name,
                "price_source": how}
        if c.get("target"):
            meta["target"] = c["target"]
        if not paper_buy(tr, name, c["token"], shares, px, taker_fee(shares, px, c["fee_rate"]), meta):
            break
        held_events.add(c["event_key"])
        if c["theme"]:
            themes[c["theme"]] = themes.get(c["theme"], 0) + 1
        bought.append(f"{c['outcome']} @ {cents(px)} - {c['title'][:80]}")
    if bought and CFG["push"].get("on_screener_buys"):
        push(f"[{name}] paper-bought {len(bought)}", "\n".join(bought), tags="mag")
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
        if tc["source"] == "screener" and not panic_only:
            cands = boring_side_candidates(markets, r)
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
    lo, hi = now() + dt.timedelta(days=r["min_days"]), now() + dt.timedelta(days=r["max_days"])
    poly = scan_markets({"end_date_min": iso(lo), "end_date_max": iso(hi), "liquidity_num_min": r["min_liquidity"]})
    P = []
    for m in poly:
        if m.get("closed") or m.get("acceptingOrders") is False or is_sports(m) or not binary(m):
            continue
        q = str(m.get("question") or "")
        if any(w in q.lower() for w in r.get("poly_skip_words", [])):
            continue
        end = parse_iso(m.get("endDateIso") or m.get("endDate"))
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
                           "best_bid_yes": bb, "best_ask_yes": ba,
                           "liquidity": round(fnum(pick(pm, "liquidityNum", "liquidity"))),
                           "fee_rate": fee_rate(pm), "description": str(pm.get("description") or "")[:1800],
                           "url": market_link(str(pm.get("slug") or ""), str(ev.get("slug") or ""))},
        })
    # Most twin-like first; among equals, the ones closest to a real (fee-beating) gap.
    cands.sort(key=lambda c: (-round(c["match_score"], 1), -c["est_gap_before_fees"]))
    save("arb_candidates.json", {"generated": iso(), "poly_markets": len(P), "kalshi_scanned": k_seen,
                                 "kalshi_kept": len(K), "matched_unreviewed": len(cands),
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
    ends = [d for d in (parse_iso(km.get("close_time")), parse_iso(pm.get("endDateIso") or pm.get("endDate"))) if d]
    days = max(1.0, (max(ends) - now()).total_seconds() / 86400 if ends else 30) + r["settle_buffer_days"]
    rate = fee_rate(pm)
    best = None
    # leg A: Kalshi YES + Polymarket outcome that wins when Kalshi NO wins; leg B: the mirror image
    for k_side, k_levels, j in (("yes", kb[0], 1 - iy), ("no", kb[1], iy)):
        pk, pp = walk(k_levels, shares), walk(pb[j]["asks"], shares)
        if pk is None or pp is None:
            continue
        kf, pf = kalshi_fee(shares, pk), taker_fee(shares, pp, rate)
        cost = shares * (pk + pp) + kf + pf
        net = shares - cost
        c = {"k_side": k_side, "pk": pk, "pp": pp, "kf": kf, "pf": pf, "cost": cost, "net": net,
             "edge": net / shares, "annual": (net / cost) * 365 / days if cost > 0 else 0,
             "p_tok": toks[j], "p_out": outs[j]}
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
    tr["peak_open_cost"] = round(max(tr["peak_open_cost"], sum(a["cost"] for a in tr["arbs"].values())), 6)
    log_event({"type": "arb_open", "track": name, "title": pm.get("question"), "pair": pid,
               "price": round(best["pk"] + best["pp"], 4), "edge": round(best["edge"], 4)})
    if CFG["push"].get("on_arb") and not prev.get("opportunity"):  # one ping per gap, not per lot
        push(f"[arb] locked {best['edge'] * 100:.1f}c/share",
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
        tr["closed"].append({**a, "k_payout": pk, "p_payout": pp, "pnl": round(pnl, 4), "mismatch": mismatch,
                             "closed_at": iso()})
        del tr["arbs"][aid]
        log_event({"type": "arb_close", "track": name, "title": a["title"], "pnl": round(pnl, 4),
                   "reason": "MISMATCH: the two sites resolved differently" if mismatch else "both legs resolved"})
        if mismatch:
            tr["mismatches"] += 1
            push("[arb] MISMATCH: sites resolved differently",
                 f"{a['title']}\nKalshi paid {pk:.2f}, Polymarket paid {pp:.2f} per share. P&L ${pnl:+.2f} (paper). "
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


def arb_proof(tr):
    closed = tr["closed"]
    n, k = len(closed), sum(1 for c in closed if c.get("mismatch"))
    edges = [c["edge"] for c in closed] + [a["edge"] for a in tr["arbs"].values()]
    e = sum(edges) / len(edges) if edges else arb_rules()["min_edge"]
    # A clean arb earns about e per share; a mismatch can lose about the whole $1 stake,
    # so arbs only pay if mismatches happen less often than about e (e.g. 2.5c edge -> under 2.5%).
    ub = upper90(k, n)
    proven = n >= 20 and ub < e and tr["realized"] > 0
    need = 0
    if not proven:
        m = max(n, 1)
        while upper90(k, m) >= e and m < n + 3000:
            m += 1
        need = max(m - n, 20 - n, 0)
    if n == 0:
        verdict = (f"Not proven yet: no finished arbs. With ~{e * 100:.1f}c edge we need about "
                   f"{need} clean finished arbs (0 mismatches) to be 90% sure.")
    elif proven:
        verdict = (f"PROVEN at 90%: {n} finished arbs, {k} mismatches, profit ${tr['realized']:.2f}. "
                   f"Mismatch rate is below {ub * 100:.1f}% with 90% confidence, under the {e * 100:.1f}c edge.")
    else:
        verdict = (f"Not proven yet: {n} finished, {k} mismatches, profit ${tr['realized']:+.2f}. "
                   f"Need about {need} more clean ones to be 90% sure (if no new mismatches).")
    return {"finished": n, "mismatches": k, "avg_edge": round(e, 4), "mismatch_rate_upper90": round(ub, 4),
            "proven": proven, "more_needed": need, "verdict": verdict}


def arb_summary(name, tr):
    locked = sum(a["cost"] for a in tr["arbs"].values())
    expected = sum(a["expected_profit"] for a in tr["arbs"].values())
    proof = arb_proof(tr)
    wins = sum(1 for c in tr["closed"] if c["pnl"] > 0)
    stats = {"pnl": round(tr["realized"], 4), "realized": round(tr["realized"], 4), "unrealized": 0.0,
             "open": len(tr["arbs"]), "closed": len(tr["closed"]), "wins": wins, "losses": len(tr["closed"]) - wins,
             "cash": round(tr["cash"], 4), "deposited": tr["deposited"], "refills": 0,
             "money_needed": round(tr["peak_open_cost"], 4), "peak_open_cost": tr["peak_open_cost"],
             "skipped_no_cash": tr["skipped_no_cash"], "locked": round(locked, 4),
             "expected_locked_profit": round(expected, 4), "gap_episodes": tr["opportunities"],
             "mismatches": tr["mismatches"], "proof": proof}
    row = (f"| {name} | {tr['realized']:+.2f} | {len(tr['arbs'])} | {len(tr['closed'])} ({wins}/{len(tr['closed']) - wins}) "
           f"| ${tr['cash']:.2f} | locked ${locked:.2f} (+${expected:.2f} expected); gaps found {tr['opportunities']}; "
           f"mismatches {tr['mismatches']} |")
    pairs = load_pairs()
    cand = load("arb_candidates.json", {})
    lines = [f"\n## {name}\n{CFG['tracks'][name].get('label', '')}\n",
             f"**Proof status:** {proof['verdict']}\n",
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


# ================================================================ commands

def today_utc():
    return now().strftime("%Y-%m-%d")


def watch():
    tracks = load_tracks()
    try:
        follow_leader(tracks)
    except Exception as e:
        print(f"leader check failed: {e}")
    manage_exits(tracks)
    for step in (arb_settle, arb_check):
        try:
            step(tracks)
        except Exception as e:
            print(f"{step.__name__} failed: {e}")
    if panic_scan_due():
        markets = scan_markets()
        if markets:
            run_strategies(tracks, markets, panic_only=True)
            st = load("scan_state.json", {})
            st["last_panic_scan"] = iso()
            save("scan_state.json", st)
    save("tracks.json", tracks)
    # GitHub's scheduler sometimes skips the daily run entirely; catch up from here.
    if now().hour >= 5 and load("scan_state.json", {}).get("last_daily") != today_utc():
        print("daily job hasn't run today (GitHub skipped it?); catching up now")
        daily(force=False)


def settle_resolved(tracks):
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
    markets = scan_markets()
    if markets:
        lists = run_strategies(tracks, markets)
        save_candidates(lists)
        st = load("scan_state.json", {})
        st["last_panic_scan"] = iso()
        save("scan_state.json", st)
    for step in (arb_settle, lambda t: arb_propose(), arb_check):
        try:
            step(tracks)
        except Exception as e:
            print(f"arb step failed: {e}")
    try:
        est = his_book_estimate()
        save("his_book.json", {"generated": iso(), **est})
    except Exception as e:
        print(f"book estimate failed: {e}")
    save("tracks.json", tracks)
    st = load("scan_state.json", {})
    st["last_daily"] = today_utc()
    save("scan_state.json", st)
    push_scoreboard(write_summary(tracks))


def mark(pos, tok):
    p = token_price_from_market(market_by_slug(pos.get("slug")), tok)
    return pos["entry"] if p is None else p


def write_summary(tracks):
    today = now().strftime("%Y-%m-%d")
    stats, md, detail = {}, [], []
    md.append(f"# Paper bot summary - {iso()}\n")
    md.append(f"Following **{CFG['leader']['name']}** (`{CFG['leader']['address']}`). Paper money only.\n")
    md.append("| Track | P&L | Open | Closed (W/L) | Cash | Notes |")
    md.append("|---|---|---|---|---|---|")
    for name, tr in tracks.items():
        if CFG["tracks"].get(name, {}).get("source") == "arb":
            row, stats[name], lines = arb_summary(name, tr)
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
            notes = f"money needed so far ${-tr['min_cash']:.2f}; most tied up at once ${tr['peak_open_cost']:.2f}"
        else:
            cash = f"${tr['cash']:.2f}"
            notes = f"refills {tr['refills']}; " if CFG["tracks"][name].get("refill") else ""
            notes += f"skipped (no cash) {tr['skipped_no_cash']}"
        md.append(f"| {name} | {pnl:+.2f} | {len(tr['positions'])} | {len(tr['closed'])} ({wins}/{losses}) | "
                  f"{cash} | {notes} |")
        stats[name] = {"pnl": round(pnl, 4), "realized": round(tr["realized"], 4), "unrealized": round(unreal, 4),
                       "open": len(tr["positions"]), "closed": len(tr["closed"]), "wins": wins, "losses": losses,
                       "cash": None if tr["unlimited"] else round(tr["cash"], 4), "deposited": tr["deposited"],
                       "refills": tr["refills"], "money_needed": round(-tr["min_cash"], 4),
                       "peak_open_cost": tr["peak_open_cost"], "skipped_no_cash": tr["skipped_no_cash"]}
        detail.append(f"\n## {name}\n{CFG['tracks'].get(name, {}).get('label', '')}\n")
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
    md += detail

    md.append("\n## Last 24 hours\n")
    cutoff = now() - dt.timedelta(hours=24)
    p, lines = os.path.join(STATE, "events.jsonl"), []
    keep = ("leader_open", "leader_exit", "paper_buy", "paper_close", "skip_no_cash", "refill",
            "arb_open", "arb_close", "arb_half_settled", "arb_opportunity")
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

    with open(os.path.join(STATE, "summary.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    save("summary.json", {"generated": iso(), "tracks": stats, "his_book": hb})

    hist = os.path.join(STATE, "history.csv")
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


def push_scoreboard(stats):
    """One line per strategy, sent to ntfy after the morning run (backup for the Claude review)."""
    lines = []
    for name, s in stats.items():
        money = f"{'+' if s['pnl'] >= 0 else '-'}${abs(s['pnl']):.2f}"
        if "proof" in s:  # arbitrage track
            pr = s["proof"]
            lines.append(f"{name}: {money} | {s['open']} open (${s['locked']:.0f} locked) | "
                         f"proof {pr['finished']}/{pr['finished'] + pr['more_needed']} clean"
                         f"{', ' + str(pr['mismatches']) + ' MISMATCH' if pr['mismatches'] else ''}")
            continue
        extra = ""
        if s.get("refills"):
            extra = f", refilled {s['refills']}x"
        if CFG["tracks"][name]["start_cash"] is None:
            extra = f", needed ${s['money_needed']:.2f} so far"
        lines.append(f"{name}: {money} | {s['open']} open | {s['wins']}W {s['losses']}L{extra}")
    hb = load("his_book.json", None)
    if hb:
        lines.append(f"Copying his whole book at min size: ${hb['cost_min_size_each']:.0f}")
    push("Paper scoreboard", "\n".join(lines), tags="bar_chart")


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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    {"watch": watch, "daily": daily, "summary": lambda: write_summary(load_tracks()),
     "selftest": selftest, "arbtest": arbtest}[cmd]()
