"""Cross-data review (19 Nov): look across live tracks and Jan's server logs for patterns no single track shows.

  python3 crosscheck.py tracks              cuts of every live track's finished bets (kind, price, side, hour, time to close)
  python3 crosscheck.py legs FILE...        combo-house logs (quoter-YYYYMMDD.jsonl.gz from release quoter-data):
                                            are single-market prices right for the legs parlay buyers pick?
  python3 crosscheck.py gap FILE...         speed-check logs (speed-YYYYMMDD.jsonl.gz from release speed-data):
                                            how far Binance sits above Coinbase / Chainlink, hour by hour
Read-only. Report: backtest/crosscheck_1119.md.
"""
import collections, datetime as dt, gzip, json, statistics as st, sys

T = lambda s: dt.datetime.fromisoformat(s[:19])


def line(v, cost="cost"):
    c = sum(r[cost] for r in v); p = sum(r["pnl"] for r in v)
    return f"{len(v)} bets, {sum(r['pnl'] < 0 for r in v)} lost, ${p:+.2f} = ${100 * p / c:+.2f} per $100" if c else "-"


def kkind(x):
    s = x.get("series", "")
    if x.get("kind") == "sports":
        return "sports"
    if any(c in s for c in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "INX", "NASDAQ", "WTI", "GOLD", "COPPER", "DIESEL", "AAAGAS"]):
        return "asset prices"
    if any(c in s for c in ["TEMP", "HIGH", "LOW"]):
        return "weather"
    return "other"


def cut(rows, name, f):
    g = collections.defaultdict(list)
    for r in rows:
        g[f(r)].append(r)
    print(f"  {name}:")
    for k, v in sorted(g.items(), key=lambda kv: str(kv[0])):
        print(f"    {k}: {line(v)}")


def tracks(path="state/tracks.json"):
    d = json.load(open(path))
    kp = [x for x in d["kalshi_patient"]["closed"] if x.get("filled")]
    print("kalshi_patient", line(kp))
    cut(kp, "kind", kkind)
    cut(kp, "side", lambda r: r["side"])
    cut(kp, "hours from order to close", lambda r: (lambda h: "a <2h" if h < 2 else "b 2-24h" if h < 24 else "c 24h+")(
        (T(r["close"]) - T(r["placed"])).total_seconds() / 3600))
    for tr in ["kc_maker", "kc_maker_safe", "kc_maker_safe_usd"]:
        rows = [x for x in d[tr]["closed"] if x.get("cost")]
        print(tr, line(rows))
        cut(rows, "side", lambda r: r["side"])
        cut(rows, "coin", lambda r: r["series"])
        cut(rows, "hour UTC (3h)", lambda r: int(r["close"][11:13]) // 3 * 3)
    sd = d["soccer_draw"]["closed"]
    for x in sd:
        x["cost"] = x["entry"] * x["shares"] + x["entry_fee"]
    print("soccer_draw", line(sd), f"wins {sum(x['pnl'] > 0 for x in sd)}, the prices said {sum(x['entry'] for x in sd):.1f}")
    cut(sd, "price (5c)", lambda r: round(r["entry"] * 100) // 5 * 5)
    sp = d["sharp_pinnacle"]["closed"]
    for x in sp:
        x["cost"] = x["entry"] * x["shares"] + x["entry_fee"]
    fair = [float(x["signal"].split("fair ")[1].split()[0]) / 100 for x in sp if "fair " in (x.get("signal") or "")]
    print("sharp_pinnacle", line(sp), f"wins {sum(x['pnl'] > 0 for x in sp)}, price said {sum(x['entry'] for x in sp):.1f}, Pinnacle said {sum(fair):.1f}")


def legs(files, qpath="state/quoter.json"):
    res = json.load(open(qpath))["leg_results"]
    meta, mids = {}, collections.defaultdict(list)
    for f in files:
        for l in gzip.open(f, "rt"):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if r.get("k") == "legs":
                meta.update(r["legs"])
            elif r.get("k") == "req" and r.get("mids"):
                for tok, m in zip(r["tokens"], r["mids"]):
                    mids[tok].append((r["t"], m))
    rows = [dict(m=min(v)[1], n=len(v), y=res[t], kind=meta.get(t, {}).get("kind", "?"))
            for t, v in mids.items() if res.get(t) in (0, 1)]
    cal = lambda v: f"{len(v)} legs, prices said {sum(r['m'] for r in v):.1f} wins, got {sum(r['y'] for r in v)}"
    print("all", cal(rows))
    for lo, hi in [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)]:
        print(f"  price {lo:.1f}-{hi:.1f}: {cal([r for r in rows if lo <= r['m'] < hi])}")
    for lo, hi in [(1, 2), (2, 5), (5, 20), (20, 100), (100, 1e9)]:
        print(f"  asked for {lo}-{hi} times: {cal([r for r in rows if lo <= r['n'] < hi])}")
    g = collections.defaultdict(list)
    for r in rows:
        g[r["kind"]].append(r)
    for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))[:8]:
        print(f"  {k}: {cal(v)}")


def gap(files):
    for f in files:
        bn, cb, cl, notes = {}, {}, {}, collections.Counter()
        for l in gzip.open(f, "rt"):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            k = r.get("k")
            if k in ("bn", "cb", "cl"):
                {"bn": bn, "cb": cb, "cl": cl}[k][r["r"] // 1000] = r["p"]
            elif k == "note":
                notes[r.get("what")] += 1
        h1, h2 = collections.defaultdict(list), collections.defaultdict(list)
        for s, p in bn.items():
            hr = dt.datetime.fromtimestamp(s, dt.timezone.utc).hour
            if s in cb:
                h1[hr].append(100 * (p / cb[s] - 1))
            if s in cl:
                h2[hr].append(100 * (p / cl[s] - 1))
        a = sorted(g for v in h1.values() for g in v)
        print(f, dict(notes))
        print(f"  Binance above Coinbase: middle {st.median(a):.3f}%, low {a[len(a) // 20]:.3f}%, high {a[-len(a) // 20]:.3f}%")
        print("  by hour UTC:", " ".join(f"{h}:{st.median(v):.3f}" for h, v in sorted(h1.items())))
        print("  vs Chainlink:", " ".join(f"{h}:{st.median(v):.3f}" for h, v in sorted(h2.items())))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tracks"
    {"tracks": lambda: tracks(), "legs": lambda: legs(sys.argv[2:]), "gap": lambda: gap(sys.argv[2:])}[cmd]()
