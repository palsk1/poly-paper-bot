#!/usr/bin/env python3
"""Read-only profile of one Polymarket wallet: what it trades, at what prices, how long it holds, where its profit comes from.
Usage (probe workflow): what=wallet_<0xaddress>. No state changes."""
import collections
import datetime as dt
import json
import statistics
import sys

from probe import get, show

D = "https://data-api.polymarket.com"


def rows_of(res):
    if isinstance(res, list):
        return res, None
    return (res.get("data") or res.get("positions") or []), ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor"))


def paged(path, addr, pages=40, limit=500, **extra):
    out, cursor = [], None
    for i in range(pages):
        p = {"user": addr, "limit": limit, **extra}
        if cursor:
            p["cursor"] = cursor
        try:
            res = get(f"{D}/{path}", p)
        except Exception as e:
            print(f"{path} page {i} failed: {e}")
            break
        rows, cursor = rows_of(res)
        if i == 0:
            show(f"{path} shape (first row)", rows[:1], 1500)
            if isinstance(res, dict):
                print("top keys:", list(res.keys()), "pagination:", res.get("pagination"))
        out += rows
        if not cursor or not rows:
            break
    print(f"{path}: {len(out)} rows")
    return out


def f(x, *keys):
    for k in keys:
        v = x.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                return v
    return None


def cat(slug, title):
    s = f"{slug} {title}".lower()
    rules = [("geopolitics", ("strait", "ceasefire", "iran", "putin", "russia", "ukraine", "israel", "hamas", "houthi", "war ", "invade", "nuclear", "npt", "china", "taiwan", "venezuela", "maduro")),
             ("esports", ("lol-", "cs2", "csgo", "dota", "valorant", "league of legends", "counter-strike", "lck", "lpl", "worlds")),
             ("mentions", ("mention", " say ", "says", "said")),
             ("economics", ("fed ", "fed-", "rate", "cpi", "inflation", "gdp", "jobs", "unemployment", "payroll", "recession", "powell", "fomc")),
             ("crypto", ("bitcoin", "btc", "eth", "solana", "xrp", "crypto")),
             ("sports", ("nba", "nfl", "nhl", "mlb", "epl", "ufc", "soccer", "football", "tennis", "-vs-", " vs. ")),
             ("politics", ("nomination", "election", "trump", "win the", "out as", "secretary", "president", "senate", "house", "governor", "mayor", "vote"))]
    for name, words in rules:
        if any(w in s for w in words):
            return name
    return "other"


def band(p):
    if p is None:
        return "?"
    for lim, name in ((0.10, "<10c"), (0.30, "10-30c"), (0.70, "30-70c"), (0.90, "70-90c"), (1.01, "90c+")):
        if p < lim:
            return name
    return "?"


def ts(x):
    v = x.get("timestamp") or x.get("ts") or x.get("time")
    try:
        v = float(v)
        return v / 1000 if v > 1e12 else v
    except (TypeError, ValueError):
        try:
            return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
        except Exception:
            return None


def day(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d") if t else "?"


def main(addr):
    print("wallet", addr)
    trades = paged("v2/trades", addr)
    openp = paged("v2/positions", addr, pages=10)
    closed = []
    for st in ("CLOSED", "RESOLVED", "ALL"):
        rows = paged("v2/positions", addr, pages=20, status=st)
        if rows and any(r.get("status") != "OPEN" for r in rows):
            print("using status", st, collections.Counter(r.get("status") for r in rows))
            closed = rows
            break
    seen = {r.get("token_id") for r in closed}
    allpos = closed + [r for r in openp if r.get("token_id") not in seen]
    print("positions total", len(allpos), collections.Counter(r.get("status") for r in allpos))

    # ---- trades: what, at what price, how big
    buys = [t for t in trades if str(t.get("side")).upper() == "BUY"]
    sells = [t for t in trades if str(t.get("side")).upper() == "SELL"]
    tss = [ts(t) for t in trades if ts(t)]
    print(f"\n== TRADES {len(trades)} (buys {len(buys)}, sells {len(sells)}) from {day(min(tss) if tss else None)} to {day(max(tss) if tss else None)}")
    usd = [f(t, "size") * f(t, "price") for t in buys if f(t, "size") and f(t, "price")]
    if usd:
        usd.sort()
        print(f"buy size $: median {statistics.median(usd):.0f}, p90 {usd[int(.9*len(usd))]:.0f}, max {usd[-1]:.0f}, total {sum(usd):.0f}")
    bc = collections.Counter(band(f(t, "price")) for t in buys)
    bu = collections.Counter()
    for t in buys:
        if f(t, "size") and f(t, "price"):
            bu[band(f(t, "price"))] += f(t, "size") * f(t, "price")
    print("buy price bands (count / $):", {k: (bc[k], round(bu[k])) for k in ("<10c", "10-30c", "30-70c", "70-90c", "90c+", "?")})
    cc = collections.Counter(cat(t.get("slug") or t.get("eventSlug") or "", t.get("title") or "") for t in buys)
    print("buy categories:", dict(cc.most_common()))
    per_day = collections.Counter(day(ts(t)) for t in trades)
    print("trades per day (last 20):", dict(sorted(per_day.items())[-20:]))
    hours = collections.Counter(dt.datetime.fromtimestamp(ts(t), dt.timezone.utc).hour for t in buys if ts(t))
    print("buy hour UTC:", dict(sorted(hours.items())))
    # holding time per token (first buy -> last sell)
    tok = collections.defaultdict(list)
    for t in trades:
        tok[t.get("asset") or t.get("token_id") or t.get("tokenId")].append(t)
    holds = []
    for k, rs in tok.items():
        b = [ts(r) for r in rs if str(r.get("side")).upper() == "BUY" and ts(r)]
        s = [ts(r) for r in rs if str(r.get("side")).upper() == "SELL" and ts(r)]
        if b and s and max(s) > min(b):
            holds.append((max(s) - min(b)) / 3600)
    if holds:
        holds.sort()
        print(f"tokens sold before end: {len(holds)} of {len(tok)}; hold hours median {statistics.median(holds):.1f}, p10 {holds[len(holds)//10]:.2f}, p90 {holds[int(.9*len(holds))]:.1f}")
    print("\n== sample of last 40 trades: ts side price size outcome title")
    for t in sorted(trades, key=lambda r: ts(r) or 0)[-40:]:
        print(" ", day(ts(t)), dt.datetime.fromtimestamp(ts(t) or 0, dt.timezone.utc).strftime("%H:%M"), t.get("side"), f(t, "price"), round(f(t, "size") or 0, 1), t.get("outcome"), (t.get("title") or "")[:70])

    # ---- closed positions: where the profit comes from
    pn = []
    for c in allpos:
        p = f(c, "total_pnl", "realized_pnl")
        if not isinstance(p, float):
            continue
        avg = f(c, "avg_price")
        bought = f(c, "total_cost_usdc")
        pn.append({"pnl": p, "avg": avg if isinstance(avg, float) else None, "bought": bought if isinstance(bought, float) else None,
                   "t": f(c, "last_event_at") if isinstance(f(c, "last_event_at"), float) else None, "st": c.get("status"),
                   "hold": ((f(c, "last_event_at") or 0) - (f(c, "first_entry_at") or 0)) / 86400 if isinstance(f(c, "first_entry_at"), float) else None, "cat": cat(c.get("slug") or c.get("eventSlug") or "", c.get("title") or ""),
                   "title": (c.get("title") or "")[:60], "o": c.get("outcome")})
    print(f"\n== ALL POSITIONS (total_pnl = realized + unrealized) {len(pn)}")
    if pn:
        tot = sum(x["pnl"] for x in pn)
        w = [x for x in pn if x["pnl"] > 0]
        l = [x for x in pn if x["pnl"] < 0]
        print(f"total realized ${tot:.0f}; won {len(w)} (${sum(x['pnl'] for x in w):.0f}), lost {len(l)} (${sum(x['pnl'] for x in l):.0f})")
        top = sorted(pn, key=lambda x: -x["pnl"])
        for n in (1, 5, 10, 20):
            print(f"  top {n} wins = ${sum(x['pnl'] for x in top[:n]):.0f}")
        for x in top[:15]:
            print("  WIN", round(x["pnl"]), "avg", x["avg"], "cost", round(x["bought"] or 0), "days", round(x["hold"] or 0), x["st"], x["title"], x["o"])
        for x in top[-10:]:
            print("  LOSS", round(x["pnl"]), "avg", x["avg"], "cost", round(x["bought"] or 0), "days", round(x["hold"] or 0), x["st"], x["title"], x["o"])
        hs = sorted(x["hold"] for x in pn if x["hold"] is not None)
        if hs:
            print(f"  position life days: median {statistics.median(hs):.1f}, p10 {hs[len(hs)//10]:.2f}, p90 {hs[int(.9*len(hs))]:.0f}")
        es = [x for x in pn if x["cat"] == "esports"]
        print("  esports:", len(es), "won", sum(1 for x in es if x["pnl"] > 0), "pnl", round(sum(x["pnl"] for x in es)), "cost", round(sum(x["bought"] or 0 for x in es)))
        for key, fn in (("by entry band", lambda x: band(x["avg"])), ("by category", lambda x: x["cat"]),
                        ("by month of last activity", lambda x: day(x["t"])[:7]), ("by status", lambda x: x["st"])):
            g = collections.defaultdict(list)
            for x in pn:
                g[fn(x)].append(x["pnl"])
            print(f"  {key}:", {k: (len(v), sum(1 for y in v if y > 0), round(sum(v))) for k, v in sorted(g.items())})
        wk = collections.defaultdict(float)
        for x in pn:
            if x["t"]:
                wk[dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%G-W%V")] += x["pnl"]
        print("  by week:", {k: round(v) for k, v in sorted(wk.items())})

    # ---- open positions
    ov = sum(f(p, "current_value") or 0 for p in openp if isinstance(f(p, "current_value"), float))
    oc = sum(f(p, "total_cost_usdc") or 0 for p in openp if isinstance(f(p, "total_cost_usdc"), float))
    print(f"\n== OPEN POSITIONS {len(openp)}: cost ${oc:.0f}, value now ${ov:.0f}")
    for p in openp[:10]:
        print("  ", f(p, "avg_price"), f(p, "current_price"), round(f(p, "current_value") or 0), round(f(p, "total_pnl") or 0), p.get("outcome"), (p.get("title") or "")[:70])


if __name__ == "__main__":
    main(sys.argv[1])
