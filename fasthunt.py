#!/usr/bin/env python3
"""Where else can our speed win? (26 Nov 2026, Jan: "who else can we battle with speed, like retail").

PAPER ONLY. Reads public trade lists and prices, never trades, never logs in.

    python3 fasthunt.py pm [days]     # probe fast_pm: Polymarket hourly / 4-hour up-down and daily "above $X" crypto
                                      # markets (BTC, ETH, SOL, XRP), whole trade lists + Binance 1-second prices.
                                      # After every Binance jump: did anybody still sell at the old price, how many
                                      # seconds later, how many dollars, and what was that worth?
    python3 fasthunt.py venues        # probe fast_venues: smaller sites (Limitless, Hyperliquid outcomes, Myriad,
                                      # SX Bet): what they list, how much trades, public data

The question is the speed box's question, asked on slower markets: after the box hears Bitcoin jump, is somebody
still selling at the price from before the jump, and for how long? On the 5-minute Bitcoin windows the answer was
"yes, for about 0.4 s, and the pros take most of it". Here we look for markets where the old price lasts seconds.

Polymarket's trade list has whole seconds, so this measures in seconds, not milliseconds. A "stale" trade is a trade
on the side Binance just jumped toward, at a price no higher than that side's price in the minute before the jump.
Its worth: the price that side settles at 30-120 s after the jump (the market's own new level, no model), minus what
was paid, minus the taker fee (0.01 x p x (1-p) a share on these markets since 20 Nov 2026), and also scored held
to the real result.
"""
import collections
import datetime as dt
import gzip
import json
import math
import os
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot
import kfast

UTC = dt.timezone.utc
CACHE = os.path.join(bot.ROOT, "bt_cache", "fh")
COINS = {"btc": ("bitcoin", "BTCUSDT"), "eth": ("ethereum", "ETHUSDT"), "sol": ("solana", "SOLUSDT"), "xrp": ("xrp", "XRPUSDT")}
FEE = 0.01
JUMP = 0.03          # a side's fair price moves 3c+ within 3 s
_LOG = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    _LOG.append(line)


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def gamma_markets(slugs):
    def batch(chunk):
        try:
            return bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"slug": chunk, "closed": "true", "limit": 100}), "markets", "data")
        except Exception as e:
            print("  gamma failed", str(e)[:120])
            return []
    out = []
    with ThreadPoolExecutor(6) as ex:
        for rows in ex.map(batch, [slugs[i:i + 20] for i in range(0, len(slugs), 20)]):
            out += [m for m in rows if isinstance(m, dict)]
    return out


def result_of(m, first):
    try:
        names = [str(x).lower() for x in json.loads(m.get("outcomes") or "[]")]
        prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception:
        return None
    if len(prices) == 2 and sorted(prices) == [0.0, 1.0] and first in names:
        return int(prices[names.index(first)] == 1.0)
    return None


def tape(cid, first, t0, t1, max_pages=80):
    """Every trade from t0 to t1 as (unix second, price of the first outcome, shares)."""
    rows, cur = [], None
    for _ in range(max_pages):
        q = {"condition_id": cid, "limit": 500}
        if cur:
            q["cursor"] = cur
        res = bot.http_json(f"{bot.DATA}/v2/trades", q)
        page = bot.envelope_rows(res, "data", "trades")
        cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
        ts = []
        for r in page:
            t = bot.fnum(r.get("timestamp"))
            t = t / 1000 if t > 1e11 else t
            ts.append(t)
            px, sz = bot.fnum(r.get("price")), bot.fnum(r.get("size"))
            if 0 < px < 1 and sz > 0 and t0 <= t <= t1:
                rows.append((int(t), round(px if str(r.get("outcome", "")).lower() == first else 1 - px, 4), round(sz, 2)))
        if not page or not cur or (ts and min(ts) < t0):
            break
    return sorted(set(rows))


def spot_series(sym, days):
    out = {}
    for d in days:
        if not kfast.fetch_spot_day(sym, d):
            say(f"  no Binance 1-s file for {sym} {d}")
            continue
        import array
        a = array.array("f")
        with open(kfast.spot_path(sym, d), "rb") as fh:
            a.fromfile(fh, 86400)
        d0 = int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=UTC).timestamp())
        for k, v in enumerate(a):
            if v == v:
                out[d0 + k] = float(v)
    return out


def pm_fetch(days):
    os.makedirs(CACHE, exist_ok=True)
    end_day = dt.datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)   # Binance day files lag a day
    dlist = [(end_day - dt.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, 0, -1)]
    t_lo = int((end_day - dt.timedelta(days=days)).timestamp())
    t_hi = int(end_day.timestamp())
    say(f"days {dlist[0]} .. {dlist[-1]}")
    data = {}
    for short, (long, sym) in COINS.items():
        t_s = time.time()
        spot = spot_series(sym, dlist)
        jobs = []
        hs = [f"{short}-updown-1h-{st}" for st in range(t_lo, t_hi, 3600)]
        fs = [f"{short}-updown-4h-{st}" for st in range(t_lo, t_hi, 3600) if st % 14400 == 0]
        for kind, slugs in (("1h", hs), ("4h", fs)):
            for m in gamma_markets(slugs):
                res = result_of(m, "up")
                st = int(str(m.get("slug")).rsplit("-", 1)[1])
                ln = 3600 if kind == "1h" else 14400
                if res is None or not m.get("conditionId"):
                    continue
                jobs.append(dict(kind=kind, cid=m["conditionId"], first="up", t0=st, t1=st + ln, res=res, vol=bot.fnum(m.get("volume"), 0),
                                 fees=bool(m.get("feesEnabled")), strike=None))
        for d in dlist:
            day = dt.datetime.strptime(d, "%Y-%m-%d")
            e = bot.event_by_slug(f"{long}-above-on-{day.strftime('%B').lower()}-{day.day}-{day.year}") or {}
            for m in e.get("markets") or []:
                k = re.search(r"above \$([\d,.]+)", str(m.get("question")))
                res = result_of(m, "yes")
                end = m.get("endDate")
                if not k or res is None or not end:
                    continue
                t1 = int(dt.datetime.fromisoformat(end.replace("Z", "+00:00")).timestamp())
                jobs.append(dict(kind="day", cid=m["conditionId"], first="yes", t0=t1 - 12 * 3600, t1=t1, res=res, vol=bot.fnum(m.get("volume"), 0),
                                 fees=bool(m.get("feesEnabled")), strike=float(k.group(1).replace(",", ""))))

        def one(j):
            try:
                return j, tape(j["cid"], j["first"], j["t0"], j["t1"])
            except Exception as ex_:
                return j, None
        got = []
        with ThreadPoolExecutor(8) as ex:
            for j, tr in ex.map(one, jobs):
                if tr is not None:
                    j["tr"] = tr
                    got.append(j)
        data[short] = {"spot": spot, "mk": got}
        c = collections.Counter(j["kind"] for j in got)
        say(f"{short}: {dict(c)} markets, {sum(len(j['tr']) for j in got):,} trades, "
            f"${sum(j['vol'] for j in got):,.0f} traded, fees on {sum(j['fees'] for j in got)}, spot seconds {len(spot):,} ({time.time() - t_s:.0f}s)")
    with gzip.open(os.path.join(CACHE, "pm.json.gz"), "wt") as fh:
        json.dump({c: {"spot": list(v["spot"].items()), "mk": v["mk"]} for c, v in data.items()}, fh)
    return data


def load():
    with gzip.open(os.path.join(CACHE, "pm.json.gz"), "rt") as fh:
        raw = json.load(fh)
    return {c: {"spot": {int(k): v for k, v in d["spot"]}, "mk": d["mk"]} for c, d in raw.items()}


def fair_fn(spot, j):
    """fair(t) for the first outcome, from Binance; None where we can't say."""
    s0 = spot.get(j["t0"]) if j["strike"] is None else None
    K = j["strike"] or s0
    if not K:
        return None
    cache = {}

    def sig(t):
        b = t // 60
        if b not in cache:
            xs = [spot.get(u) for u in range(t - 900, t, 5)]
            xs = [x for x in xs if x]
            r = [math.log(xs[i + 1] / xs[i]) for i in range(len(xs) - 1)]
            cache[b] = (statistics.pstdev(r) / math.sqrt(5)) if len(r) > 30 else None
        return cache[b]

    def f(t):
        S = spot.get(t)
        left = j["t1"] - t
        sg = sig(t)
        if not S or left <= 0 or not sg:
            return None
        return phi(math.log(S / K) / (sg * math.sqrt(left)))
    return f


def jumps(spot, j, f):
    out, last = [], -99
    for t in range(j["t0"] + 60, j["t1"] - 60):
        if t - last < 10:
            continue
        a, b = f(t), f(t - 3)
        if a is None or b is None or abs(a - b) < JUMP:
            continue
        out.append((t, a > b, a, b))
        last = t
    return out


def analyse(data):
    B = collections.defaultdict(list)
    for coin, d in data.items():
        spot = d["spot"]
        for j in d["mk"]:
            f = fair_fn(spot, j)
            if not f or not j["tr"]:
                continue
            tr = j["tr"]
            ts = [x[0] for x in tr]
            import bisect
            for t, up, fa, fb in jumps(spot, j, f):
                # the side Binance jumped toward, its price before and after (from real trades, no model)
                side = (lambda p: p) if up else (lambda p: 1 - p)
                i0, i1 = bisect.bisect_left(ts, t - 60), bisect.bisect_left(ts, t - 2)
                before = [side(x[1]) for x in tr[i0:i1]]
                a0, a1 = bisect.bisect_left(ts, t + 30), bisect.bisect_right(ts, t + 120)
                after = [side(x[1]) for x in tr[a0:a1]]
                if not before or not after:
                    continue
                pre, post = statistics.median(before[-5:]), statistics.median(after)
                if not 0.03 <= pre <= 0.97:
                    continue
                k0, k1 = bisect.bisect_left(ts, t - 2), bisect.bisect_right(ts, t + 30)
                stale = []
                for (u, px, sz) in tr[k0:k1]:
                    p = side(px)
                    if p <= pre + 1e-9:
                        stale.append((u - t, p, sz))
                won = (j["res"] == 1) == up
                B[(j["kind"], coin)].append(dict(t=t, pre=pre, post=post, move=post - pre, stale=stale, won=won, f=fa if up else 1 - fa))
    return B


def report(B):
    say("\n== After a Binance jump (a side's fair price moves 3c+ in 3 s): trades still at the old price ==")
    say("Stale trade = a trade on the side Binance jumped toward, at or below that side's price just before the jump.")
    say("Worth = the side's own trade price 30-120 s later minus the price paid minus the 0.01 fee; 'held' = paid $1 or $0.")
    say("kind coin | jumps | side really moved 2c+ | jumps with stale trades | first stale trade (seconds after jump: 25%/50%/75%) | stale $ | worth per $100 (marked / held)")
    tot = collections.Counter()
    for (kind, coin), rows in sorted(B.items()):
        moved = [r for r in rows if r["move"] >= 0.02]
        withst = [r for r in rows if any(s[0] >= 0 for s in r["stale"])]
        firsts = sorted(min(s[0] for s in r["stale"] if s[0] >= 0) for r in withst)
        usd = mk = held = 0.0
        for r in rows:
            for (dtu, p, sz) in r["stale"]:
                if dtu < 0:
                    continue
                cost = sz * (p + FEE * p * (1 - p))
                usd += cost
                mk += sz * (r["post"] - p - FEE * p * (1 - p))
                held += sz * ((1.0 if r["won"] else 0.0) - p - FEE * p * (1 - p))
        q = (lambda a, x: a[min(len(a) - 1, int(x * len(a)))]) if firsts else None
        say(f"{kind:>3} {coin} | {len(rows)} | {len(moved)} | {len(withst)} | "
            f"{(q(firsts, .25), q(firsts, .5), q(firsts, .75)) if firsts else '-'} | ${usd:,.0f} | "
            f"{(100 * mk / usd if usd else 0):+.2f} / {(100 * held / usd if usd else 0):+.2f}")
        tot["usd"] += usd; tot["mk"] += mk; tot["held"] += held
    say(f"ALL stale ${tot['usd']:,.0f}: marked {100 * tot['mk'] / max(tot['usd'], 1):+.2f}, held {100 * tot['held'] / max(tot['usd'], 1):+.2f} per $100")
    # what a box that buys the first stale offer N s after the jump would get (only trades that really happened = sellers who were there)
    say("\n== If we bought, $25 at most per jump, the stale trades that happened N seconds or more after the jump (others took the faster ones) ==")
    for kind in ("1h", "4h", "day"):
        for lo in (0, 1, 2, 3, 5, 10):
            usd = mk = held = 0.0; n = 0
            for (k, coin), rows in B.items():
                if k != kind:
                    continue
                for r in rows:
                    left = 25.0
                    for (dtu, p, sz) in sorted(r["stale"]):
                        if dtu < lo or left <= 0:
                            continue
                        sh = min(sz, left / p); left -= sh * p
                        cost = sh * (p + FEE * p * (1 - p)); usd += cost
                        mk += sh * (r["post"] - p - FEE * p * (1 - p)); held += sh * ((1.0 if r["won"] else 0) - p - FEE * p * (1 - p))
                    n += left < 25
            ndays = max(1, len({r["t"] // 86400 for rows in B.values() for r in rows}))
            say(f"  {kind:>3} from {lo:>2} s: {n} jumps, ${usd:,.0f} bought (${usd / ndays:,.0f} a day), marked {100 * mk / max(usd, 1):+.2f}, held {100 * held / max(usd, 1):+.2f} per $100, "
                f"marked profit ${mk / ndays:+,.2f} a day")


def pm(arg=None):
    days = int(arg or 5)
    data = pm_fetch(days)
    B = analyse(data)
    report(B)
    with open(os.path.join(CACHE, "pm_report.txt"), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


# ================================================================ smaller sites
def _get(url, params=None, post=None):
    import urllib.request
    try:
        if post is not None:
            req = urllib.request.Request(url, data=json.dumps(post).encode(), headers={"Content-Type": "application/json", "User-Agent": bot.UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        return bot.http_json(url, params)
    except Exception as e:
        return {"_err": str(e)[:200]}


def venues(arg=None):
    say("== Limitless (Base): active markets ==")
    rows, tot = [], None
    for page in range(1, 9):
        r = _get("https://api.limitless.exchange/markets/active", {"limit": 25, "page": page})
        if isinstance(r, dict) and "_err" in r:
            say("  ", r["_err"]); break
        data = bot.envelope_rows(r, "data", "markets")
        tot = r.get("totalMarketsCount") if isinstance(r, dict) else tot
        if not data:
            break
        rows += data
    say(f"  total listed {tot}, read {len(rows)}")
    if rows:
        say("  keys:", sorted(rows[0].keys())[:60])
    def vol(m):
        return bot.fnum(m.get("volumeFormatted") or m.get("volume"), 0)
    for m in sorted(rows, key=vol, reverse=True)[:25]:
        say(f"  {str(m.get('title'))[:70]!r} type={m.get('tradeType')} auto={m.get('automationType')} vol={m.get('volumeFormatted') or m.get('volume')} "
            f"liq={m.get('liquidityFormatted') or m.get('liquidity')} exp={m.get('expirationDate') or m.get('expirationTimestamp')} slug={m.get('slug')}")
    hourly = [m for m in rows if "hour" in json.dumps(m).lower() or "up or down" in str(m.get("title")).lower()]
    say(f"  up/down or hourly-looking markets: {len(hourly)}")
    for m in hourly[:3]:
        sl = m.get("slug")
        ob = _get(f"https://api.limitless.exchange/markets/{sl}/orderbook")
        say(f"  book {sl}: {json.dumps(ob)[:600]}")
        hp = _get(f"https://api.limitless.exchange/markets/{sl}/historical-price")
        say(f"  history {sl}: {json.dumps(hp)[:300]}")
        ev = _get(f"https://api.limitless.exchange/markets/{sl}/events")
        say(f"  events {sl}: {json.dumps(ev)[:600]}")

    say("\n== Hyperliquid outcome markets (HIP-4) ==")
    meta = _get("https://api.hyperliquid.xyz/info", post={"type": "outcomeMeta"})
    outs = (meta or {}).get("outcomes") or [] if isinstance(meta, dict) else []
    say(f"  outcomes listed {len(outs)}; first: {json.dumps(outs[:2])[:500]}")
    ctx = _get("https://api.hyperliquid.xyz/info", post={"type": "spotMetaAndAssetCtxs"})
    if isinstance(ctx, list) and len(ctx) == 2:
        vols = []
        for c in ctx[1]:
            coin = str(c.get("coin", ""))
            if coin.startswith("#"):
                vols.append((bot.fnum(c.get("dayNtlVlm"), 0), coin, c.get("markPx"), c.get("midPx")))
        vols.sort(reverse=True)
        say(f"  outcome sides with prices: {len(vols)}, 24h traded ${sum(v[0] for v in vols):,.0f}")
        names = {}
        for o in outs:
            names[o.get("outcome")] = str(o.get("description") or o.get("name"))[:90]
        for v in vols[:20]:
            oid = int(v[1][1:]) // 10
            say(f"   ${v[0]:,.0f} {v[1]} mark={v[2]} mid={v[3]} {names.get(oid, '')}")
        cr = [v for v in vols if re.search(r"price|underlying|perp:", names.get(int(v[1][1:]) // 10, ""))]
        say(f"  crypto / price outcome sides: {len(cr)}, 24h traded ${sum(v[0] for v in cr):,.0f}")
        for v in cr[:15]:
            say(f"   ${v[0]:,.0f} {v[1]} mark={v[2]} {names.get(int(v[1][1:]) // 10, '')}")
        if cr:
            bk = _get("https://api.hyperliquid.xyz/info", post={"type": "l2Book", "coin": cr[0][1]})
            say(f"  busiest crypto book: {json.dumps(bk)[:500]}")
        if vols:
            bk = _get("https://api.hyperliquid.xyz/info", post={"type": "l2Book", "coin": vols[0][1]})
            say(f"  busiest book: {json.dumps(bk)[:700]}")
    else:
        say("  ctx:", str(ctx)[:300])

    say("\n== Myriad (order-book markets by 24h volume) ==")
    r = _get("https://api-v2.myriadprotocol.com/markets", {"trading_model": "ob", "sort": "volume_24h", "order": "desc", "limit": 20, "state": "open"})
    rows = bot.envelope_rows(r, "data", "markets")
    say(f"  {str(r)[:200] if not rows else ''}")
    for m in rows[:20]:
        say(f"  {str(m.get('title'))[:70]!r} vol24h={m.get('volume_24h')} vol={m.get('volume')} liq={m.get('liquidity')} exp={m.get('expires_at')}")

    say("\n== SX Bet ==")
    r = _get("https://api.sx.bet/markets/active", {"onlyMainLine": "true"})
    rows = bot.envelope_rows((r or {}).get("data") if isinstance(r, dict) else r, "markets")
    say(f"  active main-line markets: {len(rows)}  {str(r)[:200] if not rows else ''}")
    with open(os.path.join(CACHE, "venues.txt"), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pm"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    {"pm": pm, "venues": venues, "report": lambda a=None: report(analyse(load()))}[cmd](arg)
