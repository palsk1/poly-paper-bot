#!/usr/bin/env python3
"""One wallet on Polymarket's 5-minute crypto "Up or Down" windows (17 Nov 2026, the Reddit "GoodFallen" wallet).

What it answers: is the profit real after fees, what does the wallet really do inside a window (when it buys, which
side, both sides?, waiting orders or hitting the sell side), and could a paper bot copy or rebuild it.

  fetch [addr] [pages]  wallet trades + activity (merges/redeems) + positions, Gamma results for every window,
                        the full trade list of the newest ~400 windows, Binance 1-second BTC prices.
                        Everything lands in bt_cache/w5m/ (probe w5m_fetch uploads it as an artifact).
  run                   offline report from bt_cache/w5m/ -> backtest/wallet5m.md
Data facts are in backtest/wallet5m.md.
"""
import collections
import datetime as dt
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import bot

ADDR = "0x0ca4e9d27ff826a109ecbf74754fb66b93f277a6"
CACHE = os.path.join(bot.ROOT, "bt_cache", "w5m")


def wj(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(os.path.join(CACHE, name), "wt") as fh:
        json.dump(obj, fh)


def rj(name, default=None):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        return default
    with gzip.open(p, "rt") as fh:
        return json.load(fh)


def page_all(path, params, pages, label):
    out, cur = [], None
    for i in range(pages):
        p = dict(params, limit=500)
        if cur:
            p["cursor"] = cur
        try:
            res = bot.http_json(f"{bot.DATA}/{path}", p)
        except Exception as e:
            print(f"  {label} page {i} failed: {e}")
            break
        rows = bot.envelope_rows(res, "data", "positions", "trades")
        cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
        out += rows
        if i % 20 == 0:
            ts = [bot.fnum(r.get("timestamp") or r.get("last_event_at")) for r in rows]
            ts = [t for t in ts if t]
            print(f"  {label} page {i}: {len(out)} rows, oldest {dt.datetime.utcfromtimestamp(min(ts)) if ts else '?'}")
        if not rows or not cur:
            break
    print(f"{label}: {len(out)} rows")
    return out


def fetch(addr=ADDR, pages=400):
    pages = int(pages)
    t0 = time.time()
    # 1) does the trade list hold every fill, or only the ones where the wallet hit the sell side?
    for extra in ({}, {"taker_only": "false"}, {"takerOnly": "false"}, {"taker_only": "true"}):
        try:
            res = bot.http_json(f"{bot.DATA}/v2/trades", dict({"user": addr, "limit": 500}, **extra))
            rows = bot.envelope_rows(res, "data")
            print("variant", extra, "rows", len(rows), "oldest", min((r["timestamp"] for r in rows), default=None))
        except Exception as e:
            print("variant", extra, "failed", e)
    trades = page_all("v2/trades", {"user": addr}, pages, "trades")
    wj("trades.json.gz", trades)
    act = page_all("v2/activity", {"user": addr}, pages, "activity")
    print("activity types:", collections.Counter(a.get("type") for a in act))
    if act:
        print("activity sample:", json.dumps(act[:2])[:1500])
    for typ in ("MERGE", "REDEEM", "SPLIT", "REWARD", "CONVERSION"):
        try:
            res = bot.http_json(f"{bot.DATA}/v2/activity", {"user": addr, "limit": 500, "type": typ})
            rows = bot.envelope_rows(res, "data")
            print(f"activity type={typ}: {len(rows)} rows", json.dumps(rows[:1])[:600])
        except Exception as e:
            print(f"activity type={typ} failed: {e}")
    wj("activity.json.gz", act)
    pos = {}
    for st in ("OPEN", "CLOSED", "REDEEMABLE"):
        for sort in ({}, {"sort_by": "TIMESTAMP"}, {"sortBy": "TIMESTAMP"}):
            rows = page_all("v2/positions", dict({"user": addr, "status": st}, **sort), 40, f"positions {st} {sort}")
            for r in rows:
                pos[r.get("token_id")] = r
    print("positions kept:", len(pos), collections.Counter(r.get("status") for r in pos.values()))
    wj("positions.json.gz", list(pos.values()))

    # 2) results of every window the wallet touched (Gamma, 20 slugs a call)
    slugs = sorted({t.get("slug") for t in trades if t.get("slug")} | {p.get("slug") for p in pos.values() if p.get("slug")})
    results_and_tapes(slugs)
    spot(trades)
    print(f"fetch took {time.time() - t0:.0f}s")


def fetch2(days=36):
    """Results + newest window tapes without re-reading the wallet: every BTC/ETH 5-minute window of the last N days."""
    now = int(time.time()) // 300 * 300 - 300
    slugs = [f"{c}-updown-5m-{t}" for c in ("btc",) for t in range(now - int(days) * 86400, now, 300)]
    results_and_tapes(slugs, wallet_only=False)


def results_and_tapes(slugs, wallet_only=True):
    print("windows touched:", len(slugs), collections.Counter(s.split("-updown-")[0] + "-" + s.split("-")[2] for s in slugs if "-updown-" in s))
    res = rj("results.json.gz", {}) or {}

    def batch(chunk):
        try:
            return bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"slug": chunk, "closed": "true", "limit": 100}), "markets", "data")
        except Exception as e:
            print("  gamma failed", e)
            return []
    todo = [s for s in slugs if s not in res]
    with ThreadPoolExecutor(6) as ex:
        for rows in ex.map(batch, [todo[i:i + 20] for i in range(0, len(todo), 20)]):
            for m in rows:
                try:
                    names = json.loads(m.get("outcomes") or "[]")
                    prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                except Exception:
                    continue
                res[m.get("slug")] = {"cid": m.get("conditionId"), "names": names, "prices": prices, "closed": m.get("closed"),
                                      "fee": m.get("feeSchedule") or m.get("takerBaseFee") or m.get("fee"),
                                      "vol": bot.fnum(m.get("volumeNum") or m.get("volume"))}
    wj("results.json.gz", res)
    one = next(iter(res.values()), None)
    print("results:", len(res), "sample", one)

    # 3) full trade list of the newest windows the wallet traded (who traded with it, its share of the window)
    newest = sorted([s for s in res if s.startswith("btc-updown-5m-") and (res[s].get("prices") or [0])[0] in (0.0, 1.0)],
                    key=lambda s: -int(s.rsplit("-", 1)[1]))[:400]
    tapes = rj("tapes.json.gz", {}) or {}

    def tape(slug):
        cid = (res.get(slug) or {}).get("cid")
        if not cid:
            return slug, None
        rows, cur = [], None
        for _ in range(60):
            p = {"condition_id": cid, "limit": 500}
            if cur:
                p["cursor"] = cur
            try:
                r = bot.http_json(f"{bot.DATA}/v2/trades", p)
            except Exception as e:
                return slug, {"err": str(e)[:100], "rows": rows}
            page = bot.envelope_rows(r, "data")
            cur = (r.get("pagination") or {}).get("next_cursor") if isinstance(r, dict) else None
            rows += [[x.get("timestamp"), x.get("proxy_wallet"), x.get("side"), x.get("outcome"), x.get("price"), x.get("size"),
                      x.get("transaction_hash")] for x in page]
            if not page or not cur:
                return slug, {"rows": rows, "ok": True}
        return slug, {"rows": rows, "ok": False}
    with ThreadPoolExecutor(6) as ex:
        for slug, v in ex.map(tape, [s for s in newest if s not in tapes]):
            if v:
                tapes[slug] = v
    wj("tapes.json.gz", tapes)
    if not tapes:
        return
    lens = sorted(len(v["rows"]) for v in tapes.values())
    print(f"tapes: {len(tapes)}, trades per window median {lens[len(lens) // 2] if lens else 0}, max {lens[-1] if lens else 0}, "
          f"incomplete {sum(1 for v in tapes.values() if not v.get('ok'))}")



def spot(trades):
    import kfast
    days = sorted({dt.datetime.utcfromtimestamp(bot.fnum(t.get("timestamp"))).strftime("%Y-%m-%d") for t in trades})
    ok = [d for d in days if kfast.fetch_spot_day("BTCUSDT", d)]
    print("binance 1s days:", len(ok), "of", len(days), "missing", sorted(set(days) - set(ok)))
    # the newest day(s) aren't in the daily files yet: read 1-second klines from the API
    last = {}
    for d in sorted(set(days) - set(ok)):
        d0 = int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())
        cur = d0 * 1000
        end = min(d0 + 86400, int(time.time())) * 1000
        while cur < end:
            try:
                ks = bot.http_json(f"{bot.BINANCE}/klines", {"symbol": "BTCUSDT", "interval": "1s", "startTime": cur, "limit": 1000})
            except Exception as e:
                print("  klines failed", e)
                break
            if not ks:
                break
            for k in ks:
                last[int(k[0]) // 1000] = float(k[4])
            cur = int(ks[-1][0]) + 1000
    wj("spot_api.json.gz", {str(k): v for k, v in last.items()})
    print(f"spot from API: {len(last)} seconds")


# ================================================================ offline report
def spot_series():
    """{unix second: Binance BTCUSDT 1-second close}"""
    import array
    out = {}
    d = os.path.join(bot.ROOT, "bt_cache", "kf", "spot1s")
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not fn.startswith("BTCUSDT-") or not fn.endswith(".bin"):
            continue
        day = fn[8:18]
        d0 = int(dt.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())
        a = array.array("f")
        with open(os.path.join(d, fn), "rb") as fh:
            a.frombytes(fh.read())
        for i, v in enumerate(a):
            if v == v:
                out[d0 + i] = v
    for k, v in (rj("spot_api.json.gz", {}) or {}).items():
        out[int(k)] = v
    return out


def windows():
    """One row per BTC 5-minute window the wallet traded: shares/cost per side, result, fills.
    Source: the activity list (every fill, waiting orders too, cost with fee). The plain trade list (v2/trades) only
    holds the fills where the wallet took a sell offer, so a fill whose transaction is not in it was a waiting order."""
    trades = rj("trades.json.gz", []) or []
    act = [a for a in (rj("activity.json.gz", []) or []) if a.get("type") == "TRADE"]
    res = rj("results.json.gz", {}) or {}
    taker_tx = {t.get("transaction_hash") for t in trades}
    w = collections.defaultdict(lambda: {"fills": []})
    for t in act:
        slug = str(t.get("slug") or "")
        if not slug.startswith("btc-updown-5m-") or str(t.get("side")).upper() != "BUY":
            continue
        st = int(slug.rsplit("-", 1)[1])
        sz, px = bot.fnum(t.get("size")), bot.fnum(t.get("price"))
        if sz <= 0 or not 0 < px < 1:
            continue
        usd = bot.fnum(t.get("usdc_size"))
        w[slug]["fills"].append({"t": bot.fnum(t.get("timestamp")) - st, "up": t.get("outcome") == "Up", "px": px, "sz": sz,
                                 "usd": usd, "fee": max(0.0, usd - sz * px), "mk": t.get("transaction_hash") not in taker_tx,
                                 "tx": t.get("transaction_hash")})
        w[slug]["st"] = st
    out = []
    for slug, x in w.items():
        r = res.get(slug)
        if not r or len(r.get("prices") or []) != 2 or sorted(r["prices"]) != [0.0, 1.0]:
            continue
        upi = [i for i, n in enumerate(r["names"]) if str(n).lower() == "up"]
        if not upi:
            continue
        x["upwon"] = r["prices"][upi[0]] == 1.0
        x["slug"] = slug
        for side in ("up", "dn"):
            fs = [f for f in x["fills"] if f["up"] == (side == "up")]
            x[side + "_sh"] = sum(f["sz"] for f in fs)
            x[side + "_cost"] = sum(f["sz"] * f["px"] for f in fs)
        x["fee"] = sum(f["fee"] for f in x["fills"])
        x["cost"] = x["up_cost"] + x["dn_cost"]
        x["pay"] = x["up_sh"] if x["upwon"] else x["dn_sh"]
        out.append(x)
    out.sort(key=lambda x: x["st"])
    return out


def fee_model():
    """Fee per $ bought, from positions that carry entry fees: by price band. Returns (fn, notes)."""
    pos = rj("positions.json.gz", []) or []
    trades = rj("trades.json.gz", []) or []
    tr_by_tok = collections.defaultdict(lambda: [0.0, 0.0])
    for t in trades:
        if str(t.get("side")).upper() == "BUY":
            tr_by_tok[t.get("token_id")][0] += bot.fnum(t.get("size"))
            tr_by_tok[t.get("token_id")][1] += bot.fnum(t.get("size")) * bot.fnum(t.get("price"))
    rows = []
    for p in pos:
        tok = p.get("token_id")
        if tok not in tr_by_tok:
            continue
        fee = bot.fnum(p.get("entry_fees_usdc"))
        size = bot.fnum(p.get("total_size"))
        cost = bot.fnum(p.get("total_cost_usdc"))
        rows.append({"tok": tok, "fee": fee, "pos_sh": size, "pos_cost": cost, "tr_sh": tr_by_tok[tok][0], "tr_cost": tr_by_tok[tok][1],
                     "avg": bot.fnum(p.get("avg_price"))})
    return rows


def norm_cdf(z):
    import math
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def run():
    import math
    import statistics
    lines = []

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        lines.append(s)
    ws = windows()
    if not ws:
        say("no windows")
        return
    first = ws[0]["st"] + 3600   # the oldest hour is cut off by the 200,000-row page limit
    ws = [x for x in ws if x["st"] >= first]
    say(f"## Windows: {len(ws)} BTC 5-minute windows, {dt.datetime.utcfromtimestamp(ws[0]['st']):%d %b} to "
        f"{dt.datetime.utcfromtimestamp(ws[-1]['st']):%d %b %H:%M} UTC")
    cost = sum(x["cost"] for x in ws)
    pay = sum(x["pay"] for x in ws)
    say(f"bought ${cost:,.0f}, got back ${pay:,.0f}, before fees ${pay - cost:,.0f} = ${100 * (pay - cost) / cost:.2f} per $100")
    fees = sum(x["fee"] for x in ws)
    say(f"fees paid ${fees:,.0f}; after fees ${pay - cost - fees:,.0f} = ${100 * (pay - cost - fees) / cost:.2f} per $100")
    for mk in (True, False):
        fs = [(f, x["upwon"]) for x in ws for f in x["fills"] if f["mk"] == mk]
        c = sum(f["sz"] * f["px"] for f, _ in fs)
        p = sum(f["sz"] for f, u in fs if f["up"] == u)
        fe = sum(f["fee"] for f, _ in fs)
        say(f"  {'waiting orders (maker)' if mk else 'took sell offers (taker)'}: {len(fs):,} fills, ${c:,.0f} bought, "
            f"before fees ${p - c:+,.0f} (${100 * (p - c) / c:+.2f} per $100), fees ${fe:,.0f}, after ${p - c - fe:+,.0f} (${100 * (p - c - fe) / c:+.2f} per $100)")
    # fees and whether the trade list holds every fill
    fr = fee_model()
    if fr:
        fee = sum(r["fee"] for r in fr)
        pc = sum(r["pos_cost"] for r in fr)
        say(f"positions matched to trades: {len(fr)} tokens; their fees ${fee:,.0f} on ${pc:,.0f} bought = ${100 * fee / max(pc, 1):.2f} per $100")
        miss = [r for r in fr if r["pos_sh"] > r["tr_sh"] * 1.02 + 1]
        say(f"tokens where the position holds more shares than the trade list: {len(miss)} of {len(fr)}; "
            f"shares in positions {sum(r['pos_sh'] for r in fr):,.0f} vs trade list {sum(r['tr_sh'] for r in fr):,.0f}")
        zero = sum(1 for r in fr if r["fee"] == 0)
        say(f"tokens with zero fee: {zero} of {len(fr)}")
    act = rj("activity.json.gz", []) or []
    reb = collections.Counter()
    for a in act:
        if a.get("type") in ("MAKER_REBATE", "TAKER_REBATE", "REWARD") and bot.fnum(a.get("timestamp")) >= first:
            reb[a.get("type")] += bot.fnum(a.get("usdc_size"))
    say("rebates/rewards in activity:", {k: round(v, 2) for k, v in reb.items()})
    # by day
    byd = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for x in ws:
        d = dt.datetime.utcfromtimestamp(x["st"]).strftime("%m-%d")
        byd[d][0] += 1
        byd[d][1] += x["cost"]
        byd[d][2] += x["pay"] - x["cost"]
    say("by day (windows, bought, profit before fees):")
    for d, v in sorted(byd.items()):
        say(f"  {d}: {v[0]} windows, ${v[1]:,.0f} bought, ${v[2]:+,.0f}")
    # both sides?
    both = [x for x in ws if x["up_sh"] > 0 and x["dn_sh"] > 0]
    say(f"windows with buys on both sides: {len(both)} of {len(ws)}")
    pair_sh = sum(min(x["up_sh"], x["dn_sh"]) for x in ws)
    tot_sh = sum(x["up_sh"] + x["dn_sh"] for x in ws)
    say(f"matched pairs (1 Up + 1 Down, pays $1 whatever happens): {pair_sh:,.0f} pairs = {2 * pair_sh / tot_sh * 100:.0f} in 100 shares")
    # pair cost: average price per side
    pc = [(x["up_cost"] / x["up_sh"] + x["dn_cost"] / x["dn_sh"]) for x in both]
    pc.sort()
    say(f"Up avg + Down avg in two-sided windows: median {statistics.median(pc):.3f}, p10 {pc[len(pc) // 10]:.3f}, p90 {pc[9 * len(pc) // 10]:.3f}; "
        f"under $1.00 in {sum(1 for v in pc if v < 1)} of {len(pc)}")
    # split profit: matched pairs vs the leftover one-sided shares
    pair_pnl = side_pnl = 0.0
    side_cost = 0.0
    lean_right = lean_n = 0
    for x in ws:
        m = min(x["up_sh"], x["dn_sh"])
        ua = x["up_cost"] / x["up_sh"] if x["up_sh"] else 0
        da = x["dn_cost"] / x["dn_sh"] if x["dn_sh"] else 0
        pair_pnl += m * (1 - ua - da)
        extra_up = x["up_sh"] - m
        extra_dn = x["dn_sh"] - m
        c = extra_up * ua + extra_dn * da
        p = extra_up * (1 if x["upwon"] else 0) + extra_dn * (0 if x["upwon"] else 1)
        side_pnl += p - c
        side_cost += c
        if extra_up + extra_dn > 1:
            lean_n += 1
            lean_right += (extra_up > extra_dn) == x["upwon"]
    say(f"profit before fees from matched pairs ${pair_pnl:,.0f}; from the leftover one-sided shares ${side_pnl:,.0f} on ${side_cost:,.0f} "
        f"(lean on the winning side in {lean_right} of {lean_n} windows)")
    # when in the window
    tb = collections.Counter()
    tbc = collections.Counter()
    for x in ws:
        for f in x["fills"]:
            b = min(int(f["t"] // 30), 10)
            tb[b] += 1
            tbc[b] += f["sz"] * f["px"]
    say("fills by time into the window (30 s steps):", {f"{k * 30}s": (tb[k], round(tbc[k])) for k in sorted(tb)})
    # fills vs a Binance fair price
    sp = spot_series()
    say(f"Binance seconds loaded: {len(sp):,}")
    if sp:
        rows = []
        for x in ws:
            s0 = sp.get(x["st"])
            if not s0:
                continue
            past = [sp.get(x["st"] - k) for k in range(1, 901, 1)]
            rets = [math.log(past[i] / past[i + 1]) for i in range(len(past) - 1) if past[i] and past[i + 1]]
            if len(rets) < 600:
                continue
            sig = statistics.pstdev(rets)
            if sig <= 0:
                continue
            for f in x["fills"]:
                t = int(f["st"] if "st" in f else x["st"] + f["t"])
                s = sp.get(t) or sp.get(t - 1)
                left = x["st"] + 300 - t
                if not s or left <= 0:
                    continue
                pup = norm_cdf(math.log(s / s0) / (sig * math.sqrt(left)))
                fair = pup if f["up"] else 1 - pup
                won = x["upwon"] == f["up"]
                rows.append({"gap": fair - f["px"], "fair": fair, "px": f["px"], "won": won, "sz": f["sz"], "left": left,
                             "lead": fair > 0.5, "mk": f["mk"], "fee": f["fee"]})
        if rows:
            dol = sum(r["sz"] * r["px"] for r in rows)
            say(f"fills priced against Binance: {len(rows):,} (${dol:,.0f}); average fair minus price paid "
                f"{100 * sum(r['gap'] * r['sz'] for r in rows) / sum(r['sz'] for r in rows):+.2f}c a share")
            for name, fn in (("by price paid", lambda r: f"{int(r['px'] * 10) * 10}-{int(r['px'] * 10) * 10 + 9}c"),
                             ("by fair minus paid", lambda r: "<-5c" if r["gap"] < -.05 else "-5..0c" if r["gap"] < 0 else "0..5c" if r["gap"] < .05 else "5..10c" if r["gap"] < .1 else "10c+"),
                             ("by seconds left", lambda r: f"{int(r['left'] // 60)}m left"),
                             ("leading side vs trailing side", lambda r: "leader" if r["lead"] else "trailer"),
                             ("maker vs taker", lambda r: "maker" if r["mk"] else "taker"),
                             ("taker fills by fair minus paid", lambda r: "maker" if r["mk"] else "<-5c" if r["gap"] < -.05 else "-5..0c" if r["gap"] < 0 else "0..5c" if r["gap"] < .05 else "5..10c" if r["gap"] < .1 else "10c+"),
                             ("maker fills by fair minus paid", lambda r: "taker" if not r["mk"] else "<-5c" if r["gap"] < -.05 else "-5..0c" if r["gap"] < 0 else "0..5c" if r["gap"] < .05 else "5..10c" if r["gap"] < .1 else "10c+")):
                g = collections.defaultdict(list)
                for r in rows:
                    g[fn(r)].append(r)
                say(f"  {name}: (fills, $ bought, profit per $100 before fees, after fees, avg fair-paid in c)")
                for k in sorted(g):
                    v = g[k]
                    c = sum(r["sz"] * r["px"] for r in v)
                    p = sum(r["sz"] * (1 if r["won"] else 0) for r in v)
                    fe = sum(r["fee"] for r in v)
                    say(f"    {k}: {len(v)}, ${c:,.0f}, {100 * (p - c) / c:+.2f}, {100 * (p - c - fe) / c:+.2f}, {100 * sum(r['gap'] * r['sz'] for r in v) / sum(r['sz'] for r in v):+.2f}c")
    # tapes: maker or taker, share of the window, what a copier would pay
    tapes = rj("tapes.json.gz", {}) or {}
    me = ADDR.lower()
    if tapes:
        txs = collections.Counter()
        share = []
        groups_seen = 0
        for slug, v in list(tapes.items()):
            rows = v.get("rows") or []
            mine = [r for r in rows if str(r[1]).lower() == me]
            vol = sum(bot.fnum(r[5]) * bot.fnum(r[4]) for r in rows)
            if vol:
                share.append(sum(bot.fnum(r[5]) * bot.fnum(r[4]) for r in mine) / vol)
            bytx = collections.defaultdict(list)
            for r in rows:
                bytx[r[6]].append(r)
            for r in mine:
                g = bytx[r[6]]
                txs[(len(g), len({str(y[1]).lower() for y in g}))] += 1
                if groups_seen < 6 and len(g) > 1:
                    groups_seen += 1
                    say("  example tx group:", json.dumps(g)[:700])
        share.sort()
        say(f"tapes: {len(tapes)} windows; wallet's share of window dollars median {100 * statistics.median(share):.0f} in 100" if share else "no share")
        say("wallet fills by (rows in the same transaction, wallets in it):", dict(txs.most_common(12)))
    copytest(say)
    rep = os.path.join(bot.ROOT, "backtest", "wallet5m_raw.txt")
    with open(rep, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def copytest(say=print, rate=0.07):
    """A copier who sees each of the wallet's fills d seconds late and buys the same side at the next real sell offer
    on the window's trade list (a buy of that side, or a sell of the other side at 1 - price), plus the taker fee.
    `rate` = Polymarket's taker fee rate for BTC 5-minute windows: 0.07 until 20 Nov 2026 (the report), 0.05 since."""
    import bisect
    tapes = rj("tapes.json.gz", {}) or {}
    ws = {x["slug"]: x for x in windows()}
    me = ADDR.lower()
    res = collections.defaultdict(lambda: [0.0, 0.0, 0])
    own = [0.0, 0.0]
    for slug, v in tapes.items():
        x = ws.get(slug)
        if not x:
            continue
        st = x["st"]
        asks = {True: [], False: []}
        for t, wal, sd, o, p, sz, tx in v["rows"]:
            if wal and str(wal).lower() == me:
                continue
            up = o == "Up"
            p, t = float(p), float(t)
            if str(sd).upper() == "BUY":
                asks[up].append((t, p))
            else:
                asks[not up].append((t, 1 - p))
        for k in asks:
            asks[k].sort()
        for f in x["fills"]:
            t = st + f["t"]
            won = f["up"] == x["upwon"]
            own[0] += f["sz"] * f["px"] + f["fee"]
            own[1] += f["sz"] * won
            for d in (1, 3, 10, 30, 60):
                a = asks[f["up"]]
                i = bisect.bisect_left(a, (t + d, -1))
                if i >= len(a) or a[i][0] > st + 300 or not 0 < a[i][1] < 1:
                    res[d][2] += 1
                    continue
                p = a[i][1]
                res[d][0] += f["sz"] * (p + rate * p * (1 - p))
                res[d][1] += f["sz"] * won
    if not own[0]:
        return
    say(f"## Copy test on the {len(tapes)} newest windows")
    say(f"the wallet itself there: ${own[0]:,.0f} bought with fees, {100 * (own[1] - own[0]) / own[0]:+.2f} per $100 (before rebates)")
    for d, (c, p, miss) in sorted(res.items()):
        say(f"copy {d}s late at the next real sell offer + fee: ${c:,.0f}, {100 * (p - c) / c:+.2f} per $100; fills with no offer left: {miss}")


def speed(say=print, lag=3):
    """Is the wallet's edge speed? (17 Nov, Jan: "we would use his system ourselves" on a fast AWS server.)
    1) average Binance move toward the side bought, second by second around each fill (where the move peaks = how
       long after the match the fill's timestamp is, and whether the wallet trades right after Bitcoin jumps);
    2) its waiting-order fills split by the Bitcoin move just before them;
    3) a bot that pulls its waiting orders when its side's fair price drops 2/3/5c, 1-3 s before the match."""
    import math
    import statistics
    ws = windows()
    ws = [x for x in ws if x["st"] >= ws[0]["st"] + 3600]
    sp = spot_series()
    prof = {True: collections.defaultdict(float), False: collections.defaultdict(float)}
    n = {True: 0, False: 0}
    rows = []
    for x in ws:
        st = x["st"]
        s0 = sp.get(st)
        past = [sp.get(st - k) for k in range(0, 901)]
        rets = [math.log(past[i] / past[i + 1]) for i in range(900) if past[i] and past[i + 1]]
        sig = statistics.pstdev(rets) if len(rets) >= 600 else 0

        def fu(t):
            t = max(st, t)
            s = sp.get(t) or sp.get(t - 1)
            left = st + 300 - t
            if not s or not s0 or left <= 0 or sig <= 0:
                return None
            return norm_cdf(math.log(s / s0) / (sig * math.sqrt(left)))
        for f in x["fills"]:
            t = int(st + f["t"])
            sgn = 1 if f["up"] else -1
            vals = {}
            for j in range(-30, 11):
                a, b = sp.get(t + j), sp.get(t + j - 1)
                if not a or not b:
                    vals = None
                    break
                vals[j] = sgn * math.log(a / b) * 1e4
            if vals:
                n[f["mk"]] += 1
                for j, v in vals.items():
                    prof[f["mk"]][j] += v
            if not f["mk"]:
                continue
            m = t - lag
            a = {k: fu(m - k) for k in (0, 1, 2, 3, 13)}
            b2 = fu(t - 2)
            if any(v is None for v in a.values()) or b2 is None or fu(t) is None:
                continue
            rows.append({"c": f["sz"] * f["px"], "p": f["sz"] * (f["up"] == x["upwon"]),
                         "a": {k: sgn * v for k, v in a.items()}, "d2": sgn * (b2 - fu(t))})
    say("## Is it speed?")
    for mk in (True, False):
        if n[mk]:
            say(f"{'waiting orders' if mk else 'grabbed sell offers'} ({n[mk]:,} fills): average Bitcoin move toward the side bought, "
                f"1/100 of a basis point, by second around the fill time:")
            say("  " + " ".join(f"{j}:{100 * prof[mk][j] / n[mk]:+.1f}" for j in range(-12, 4)))
    g = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        v = r["d2"]
        k = "against 10c+" if v >= .10 else "against 5-10c" if v >= .05 else "against 2-5c" if v >= .02 else "flat" if v > -.02 else "toward 2c+"
        g[k][0] += 1
        g[k][1] += r["c"]
        g[k][2] += r["p"]
    say("waiting-order fills by the move of their side's fair price in the 2 s before the fill time:")
    for k in ("against 10c+", "against 5-10c", "against 2-5c", "flat", "toward 2c+"):
        c, p = g[k][1], g[k][2]
        if c:
            say(f"  {k}: {g[k][0]:,} fills, ${c:,.0f}, {100 * (p - c) / c:+.2f} per $100 (${p - c:+,.0f})")
    for d in (1, 2, 3):
        for mm in (0.02, 0.03, 0.05):
            keep = [r for r in rows if r["a"][13] - r["a"][d] < mm]
            c = sum(r["c"] for r in keep)
            p = sum(r["p"] for r in keep)
            say(f"pull when our side drops {int(mm * 100)}c+, {d} s before the match (match = fill time - {lag} s): keep "
                f"{len(keep):,} of {len(rows):,} fills, {100 * (p - c) / c:+.2f} per $100 (${p - c:+,.0f})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "fetch":
        fetch(*sys.argv[2:])
    elif cmd == "fetch2":
        fetch2(*sys.argv[2:])
    elif cmd == "run":
        run()
    elif cmd == "speed":
        lines = []
        speed(lambda *a: (print(*a), lines.append(" ".join(str(x) for x in a))))
        with open(os.path.join(bot.ROOT, "backtest", "wallet5m_speed.txt"), "w") as fh:
            fh.write("\n".join(lines) + "\n")
