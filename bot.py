#!/usr/bin/env python3
"""Polymarket PAPER-trading bot.

Follows one wallet's positions and runs rule-based strategies, recording
everything as paper trades. It never places real orders and needs no keys:
it only reads Polymarket's public APIs and (optionally) sends ntfy pushes.

Usage:
    python3 bot.py watch     # every ~10 min: copy his opens/exits, manage exits, panic scan every 2h
    python3 bot.py daily     # once a day: settle resolved markets, strategy picks, summary
    python3 bot.py summary   # rebuild summary files only
    python3 bot.py selftest  # print raw API samples and send a test push
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "state")
with open(os.path.join(ROOT, "config.json")) as _fh:
    CFG = json.load(_fh)

DATA = "https://data-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
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
        if tc["source"] == "leader":
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

def scan_markets():
    """All open markets (one pass), shared by every strategy."""
    out, cursor = [], None
    for _ in range(60):
        params = {"closed": "false", "limit": 500, "version": ["v1", "v2"]}
        if cursor:
            params["after_cursor"] = cursor
        try:
            res = http_json(f"{GAMMA}/markets/keyset", params)
        except Exception as e:
            print(f"market scan page failed: {e}")
            break
        ms = [m for m in envelope_rows(res, "markets", "data") if isinstance(m, dict)]
        out += ms
        cursor = res.get("next_cursor") if isinstance(res, dict) else None
        if not cursor or not ms:
            break
    print(f"scanned {len(out)} open markets")
    return out


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
    for name, tc in CFG["tracks"].items():
        r = rules_for(name)
        if tc["source"] == "screener" and not panic_only:
            cands = boring_side_candidates(markets, r)
            buy_candidates(tracks, name, cands, r.get("picks_per_day", 1))
            lists[name] = cands
        elif tc["source"] == "panic":
            cands = panic_candidates(markets, r)
            buy_candidates(tracks, name, cands, r.get("picks_per_scan", 1))
            lists[name] = cands
    return lists


def panic_scan_due():
    hours = CFG["rules"].get("panic_fade", {}).get("scan_every_hours", 2)
    last = parse_iso(load("scan_state.json", {}).get("last_panic_scan"))
    return last is None or (now() - last).total_seconds() >= hours * 3600 - 300


# ================================================================ commands

def watch():
    tracks = load_tracks()
    try:
        follow_leader(tracks)
    except Exception as e:
        print(f"leader check failed: {e}")
    manage_exits(tracks)
    if panic_scan_due():
        markets = scan_markets()
        if markets:
            run_strategies(tracks, markets, panic_only=True)
            st = load("scan_state.json", {})
            st["last_panic_scan"] = iso()
            save("scan_state.json", st)
    save("tracks.json", tracks)


def settle_resolved(tracks):
    for name, tr in tracks.items():
        for tok in list(tr["positions"]):
            payout = resolved_payout(market_by_slug(tr["positions"][tok].get("slug")), tok)
            if payout is not None:
                paper_close(tr, name, tok, payout, 0.0, "resolved")


def daily():
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
    try:
        est = his_book_estimate()
        save("his_book.json", {"generated": iso(), **est})
    except Exception as e:
        print(f"book estimate failed: {e}")
    save("tracks.json", tracks)
    write_summary(tracks)


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
    keep = ("leader_open", "leader_exit", "paper_buy", "paper_close", "skip_no_cash", "refill")
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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    {"watch": watch, "daily": daily, "summary": lambda: write_summary(load_tracks()),
     "selftest": selftest}[cmd]()
