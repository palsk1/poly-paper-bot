#!/usr/bin/env python3
"""Real profit and loss of one Polymarket wallet from its full public money trail (22 Nov 2026, Jan doubted that
anoin123 "lost $4.8 million").

walletcheck.py adds up the API's per-position `total_pnl`. That number can be far off (RememberAmalek: ~$1.1M by
positions vs $178k on the leaderboard), because a wallet also gets money out by merging Yes+No back into $1,
by converting No shares in multi-choice events, by redeeming, and from rewards and rebates.
This tool counts dollars instead: every buy, sell, redeem, merge, split, conversion, reward and rebate from
`/v2/activity`, plus what the still-open positions are worth now, and compares the total with the leaderboard.
It also checks whether the wallet trades both sides of a market or holds opposite bets in one event (hedges).

    python3 walletpnl.py fetch <0xaddress>    # probe wpnl_fetch_<0xaddress>: saves bt_cache/wpnl/<address>/ (price store)
    python3 walletpnl.py report <0xaddress>   # offline report from the saved files (also run at the end of fetch)
Read-only, public data, no keys.
"""
import collections
import datetime as dt
import gzip
import json
import os
import sys

import bot

BASE = "bt_cache/wpnl"


def folder(addr):
    d = os.path.join(BASE, addr.lower())
    os.makedirs(d, exist_ok=True)
    return d


def wj(addr, name, obj):
    with gzip.open(os.path.join(folder(addr), name), "wt") as fh:
        json.dump(obj, fh)


def rj(addr, name, default=None):
    p = os.path.join(folder(addr), name)
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
        rows = bot.envelope_rows(res, "data", "positions", "trades", "activity")
        cur = ((res.get("pagination") or {}).get("next_cursor") or res.get("next_cursor")) if isinstance(res, dict) else None
        out += rows
        if i == 0:
            print(f"  {label} first row:", json.dumps(rows[:1])[:1200])
        if not rows or not cur:
            break
    print(f"{label}: {len(out)} rows")
    return out


def fetch(addr):
    addr = addr.lower()
    act = page_all("v2/activity", {"user": addr}, 600, "activity")
    print("activity types:", dict(collections.Counter(a.get("type") for a in act)))
    # the plain list may skip some kinds: ask for each kind on its own as well, keep anything new
    seen = {json.dumps(a, sort_keys=True) for a in act}
    for typ in ("REDEEM", "MERGE", "SPLIT", "CONVERSION", "REWARD", "MAKER_REBATE", "TAKER_REBATE", "YIELD", "TRANSFER"):
        rows = page_all("v2/activity", {"user": addr, "type": typ}, 200, f"activity type={typ}")
        new = [r for r in rows if json.dumps(r, sort_keys=True) not in seen]
        if new:
            print(f"  type={typ}: {len(new)} rows not in the plain list, added")
            act += new
            seen |= {json.dumps(r, sort_keys=True) for r in new}
    wj(addr, "activity.json.gz", act)
    trades = page_all("v2/trades", {"user": addr}, 600, "trades")
    wj(addr, "trades.json.gz", trades)
    pos = {}
    for st in ("OPEN", "CLOSED", "REDEEMABLE", "ALL"):
        for r in page_all("v2/positions", {"user": addr, "status": st}, 60, f"positions {st}"):
            pos.setdefault(r.get("token_id") or json.dumps(r, sort_keys=True), r)
    print("positions kept:", len(pos), dict(collections.Counter(r.get("status") for r in pos.values())))
    wj(addr, "positions.json.gz", list(pos.values()))
    lb = {}
    for period in ("ALL", "MONTH", "WEEK"):
        for path in ("v2/leaderboard", "v1/leaderboard"):
            try:
                res = bot.http_json(f"{bot.DATA}/{path}", {"user": addr, "timePeriod": period, "category": "OVERALL"})
                lb[f"{path} {period}"] = res
                print("leaderboard", path, period, json.dumps(res)[:600])
            except Exception as e:
                print("leaderboard", path, period, "failed", e)
    for path, params in (("v1/value", {"user": addr}), ("value", {"user": addr}), ("v2/value", {"user": addr})):
        try:
            res = bot.http_json(f"{bot.DATA}/{path}", params)
            lb[path] = res
            print(path, json.dumps(res)[:400])
        except Exception as e:
            print(path, "failed", e)
    wj(addr, "leaderboard.json.gz", lb)
    report(addr)


def fnum(x):
    return bot.fnum(x)


def pick(r, *keys):
    for k in keys:
        v = r.get(k)
        if v not in (None, ""):
            return v
    return None


def day(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d") if t else "?"


def usd(a):
    return fnum(pick(a, "usdc_size", "usdcSize", "usdc", "amount"))


def money(x):
    return f"-${-x:,.0f}" if x < 0 else f"${x:,.0f}"


def report(addr):
    addr = addr.lower()
    act = rj(addr, "activity.json.gz", []) or []
    pos = rj(addr, "positions.json.gz", []) or []
    trades = rj(addr, "trades.json.gz", []) or []
    print(f"\n==== WALLET {addr}: {len(act)} activity rows, {len(trades)} trade rows, {len(pos)} positions")
    for typ in sorted({a.get("type") for a in act}, key=str):
        ex = [a for a in act if a.get("type") == typ][:1]
        print(f"  sample {typ}:", json.dumps(ex)[:700])
    ts = [fnum(a.get("timestamp")) for a in act if fnum(a.get("timestamp"))]
    ts = [t / 1000 if t > 1e12 else t for t in ts]
    print("activity from", day(min(ts)) if ts else "?", "to", day(max(ts)) if ts else "?")

    # ---- 1) the money trail
    tot = collections.defaultdict(float)
    cnt = collections.Counter()
    for a in act:
        typ = a.get("type")
        if typ == "TRADE":
            typ = f"TRADE {str(a.get('side')).upper()}"
        tot[typ] += usd(a)
        cnt[typ] += 1
    print("\n== 1) MONEY IN AND OUT (from /v2/activity)")
    for k in sorted(tot):
        print(f"  {k:18s} {cnt[k]:7d} rows  {money(tot[k])}")
    out_ = tot["TRADE BUY"] + tot["SPLIT"]
    in_ = sum(v for k, v in tot.items() if k not in ("TRADE BUY", "SPLIT"))
    cash = in_ - out_
    open_rows = [p for p in pos if str(p.get("status")).upper() in ("OPEN", "REDEEMABLE")]
    open_val = sum(fnum(pick(p, "current_value", "currentValue")) for p in open_rows)
    open_cost = sum(fnum(pick(p, "total_cost_usdc", "initialValue")) for p in open_rows)
    print(f"  paid in (buys + splits): {money(out_)}")
    print(f"  got back (sells, redeems, merges, conversions, rewards, rebates): {money(in_)}")
    print(f"  cash result so far: {money(cash)}")
    print(f"  open positions: {len(open_rows)}, cost {money(open_cost)}, worth now {money(open_val)}")
    print(f"  ==> REAL P&L (cash + open worth now): {money(cash + open_val)}")
    print("  note: a TRANSFER/deposit is not profit; types listed above that are plain moves of money are not in 'got back' if any")

    # ---- 2) the API's per-position number (what walletcheck added up)
    api = [fnum(pick(p, "total_pnl", "realized_pnl", "cashPnl")) for p in pos]
    real = [fnum(pick(p, "realized_pnl", "realizedPnl")) for p in pos]
    print("\n== 2) THE API'S PER-POSITION NUMBERS")
    print(f"  sum total_pnl {money(sum(api))}, sum realized_pnl {money(sum(real))}, positions {len(pos)}")
    st = collections.defaultdict(list)
    for p in pos:
        st[str(p.get("status"))].append(fnum(pick(p, "total_pnl", "realized_pnl")))
    print("  by status:", {k: (len(v), money(sum(v))) for k, v in st.items()})

    # ---- 3) per market: cash flow vs API, and both sides
    mk = collections.defaultdict(lambda: {"buy": collections.defaultdict(float), "sell": collections.defaultdict(float),
                                          "redeem": 0.0, "merge": 0.0, "split": 0.0, "conv": 0.0, "title": "", "event": ""})
    for a in act:
        cid = pick(a, "condition_id", "conditionId", "market")
        if not cid:
            continue
        m = mk[cid]
        m["title"] = m["title"] or (a.get("title") or "")[:70]
        m["event"] = m["event"] or (pick(a, "event_slug", "eventSlug") or "")
        typ = a.get("type")
        oi = str(pick(a, "outcome", "outcome_index", "outcomeIndex"))
        if typ == "TRADE":
            m["buy" if str(a.get("side")).upper() == "BUY" else "sell"][oi] += usd(a)
        elif typ == "REDEEM":
            m["redeem"] += usd(a)
        elif typ == "MERGE":
            m["merge"] += usd(a)
        elif typ == "SPLIT":
            m["split"] += usd(a)
        elif typ == "CONVERSION":
            m["conv"] += usd(a)
    pv = collections.defaultdict(float)
    papi = collections.defaultdict(float)
    for p in pos:
        cid = pick(p, "condition_id", "conditionId")
        if str(p.get("status")).upper() in ("OPEN", "REDEEMABLE"):
            pv[cid] += fnum(pick(p, "current_value", "currentValue"))
        papi[cid] += fnum(pick(p, "total_pnl", "realized_pnl"))
    rows = []
    for cid, m in mk.items():
        b = sum(m["buy"].values())
        s = sum(m["sell"].values())
        flow = s + m["redeem"] + m["merge"] + m["conv"] - b - m["split"] + pv.get(cid, 0)
        both = len([k for k, v in m["buy"].items() if v > 0]) >= 2
        rows.append(dict(cid=cid, title=m["title"], event=m["event"], bought=b, flow=flow, api=papi.get(cid, 0.0), both=both,
                         merge=m["merge"], split=m["split"], minor=min(m["buy"].values()) if both else 0.0))
    print("\n== 3) PER MARKET (money trail vs API)")
    print(f"  markets touched {len(rows)}; money-trail total {money(sum(r['flow'] for r in rows))}; API total on same markets {money(sum(r['api'] for r in rows))}")
    gap = sorted(rows, key=lambda r: -abs(r["flow"] - r["api"]))[:15]
    print("  biggest gaps between money trail and API:")
    for r in gap:
        print(f"    trail {money(r['flow']):>12s} api {money(r['api']):>12s} bought {money(r['bought']):>12s} merge {money(r['merge'])} split {money(r['split'])} | {r['title']}")
    bs = [r for r in rows if r["both"]]
    print(f"  markets where it BOUGHT BOTH sides: {len(bs)} of {len(rows)}; $ bought there {money(sum(r['bought'] for r in bs))} of {money(sum(r['bought'] for r in rows))}; "
          f"smaller side $ {money(sum(r['minor'] for r in bs))}; trail P&L there {money(sum(r['flow'] for r in bs))}")
    print(f"  merges: {cnt['MERGE']} rows {money(tot['MERGE'])}; splits {cnt['SPLIT']} rows {money(tot['SPLIT'])}; conversions {cnt['CONVERSION']} rows {money(tot['CONVERSION'])}")
    print("  top 15 markets by money trail P&L (wins):")
    for r in sorted(rows, key=lambda r: -r["flow"])[:15]:
        print(f"    {money(r['flow']):>12s} bought {money(r['bought']):>12s} both={r['both']} | {r['title']}")
    print("  bottom 15 (losses):")
    for r in sorted(rows, key=lambda r: r["flow"])[:15]:
        print(f"    {money(r['flow']):>12s} bought {money(r['bought']):>12s} both={r['both']} | {r['title']}")

    # ---- 4) per event: opposite bets on linked markets (hedges)
    ev = collections.defaultdict(lambda: {"flow": 0.0, "bought": 0.0, "n": 0, "sides": collections.Counter()})
    for cid, m in mk.items():
        e = ev[m["event"] or cid]
        r = next(x for x in rows if x["cid"] == cid)
        e["flow"] += r["flow"]
        e["bought"] += r["bought"]
        e["n"] += 1
        for k, v in m["buy"].items():
            if v > 0:
                e["sides"][k] += 1
    print("\n== 4) PER EVENT (linked markets)")
    print(f"  events {len(ev)}; with 2+ markets {sum(1 for e in ev.values() if e['n'] >= 2)}; with both Yes and No buys across markets {sum(1 for e in ev.values() if len(e['sides']) >= 2)}")
    for k, e in sorted(ev.items(), key=lambda kv: -kv[1]["bought"])[:20]:
        print(f"    {money(e['flow']):>12s} bought {money(e['bought']):>12s} markets {e['n']:3d} sides {dict(e['sides'])} | {k}")

    # ---- 5) by month, by price paid
    mo = collections.defaultdict(lambda: collections.defaultdict(float))
    for a in act:
        t = fnum(a.get("timestamp"))
        t = t / 1000 if t > 1e12 else t
        typ = a.get("type") if a.get("type") != "TRADE" else f"TRADE {str(a.get('side')).upper()}"
        mo[day(t)[:7]][typ] += usd(a)
    print("\n== 5) BY MONTH (cash in minus cash out; open bets show up as cash out)")
    for k in sorted(mo):
        d = mo[k]
        o = d["TRADE BUY"] + d["SPLIT"]
        i = sum(v for kk, v in d.items() if kk not in ("TRADE BUY", "SPLIT"))
        print(f"  {k}: bought {money(d['TRADE BUY'])}, sold {money(d['TRADE SELL'])}, redeemed {money(d['REDEEM'])}, merged {money(d['MERGE'])}, net {money(i - o)}")
    bands = collections.defaultdict(lambda: [0, 0.0])
    for a in act:
        if a.get("type") == "TRADE" and str(a.get("side")).upper() == "BUY":
            p = fnum(a.get("price"))
            k = "<10c" if p < .1 else "10-30c" if p < .3 else "30-70c" if p < .7 else "70-90c" if p < .9 else "90c+"
            bands[k][0] += 1
            bands[k][1] += usd(a)
    print("  buys by price:", {k: (v[0], money(v[1])) for k, v in sorted(bands.items())})
    sz = sorted(usd(a) for a in act if a.get("type") == "TRADE" and str(a.get("side")).upper() == "BUY")
    if sz:
        print(f"  buy size: median {money(sz[len(sz)//2])}, p90 {money(sz[int(.9*len(sz))])}, max {money(sz[-1])}")
    # ---- 5b) when and where the loss happened
    first = {}
    for a in act:
        cid = pick(a, "condition_id")
        t = fnum(a.get("timestamp"))
        if cid and a.get("type") == "TRADE":
            first[cid] = min(first.get(cid, t), t)
    coh = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        k = day(first.get(r["cid"]))[:7]
        coh[k][0] += 1
        coh[k][1] += r["bought"]
        coh[k][2] += r["flow"]
    print("\n== 5b) P&L BY THE MONTH A MARKET WAS FIRST BOUGHT (markets, $ bought, P&L incl. open worth now)")
    for k in sorted(coh):
        print(f"  {k}: {coh[k][0]} markets, bought {money(coh[k][1])}, P&L {money(coh[k][2])}")
    iran = [r for r in rows if "iran" in (r["event"] + r["title"]).lower() and ("strike" in (r["event"] + r["title"]).lower())]
    print(f"  'strikes Iran' markets: {len(iran)}, bought {money(sum(r['bought'] for r in iran))}, P&L {money(sum(r['flow'] for r in iran))}")
    rest = [r for r in rows if r not in iran]
    print(f"  everything else: {len(rest)} markets, bought {money(sum(r['bought'] for r in rest))}, P&L {money(sum(r['flow'] for r in rest))}")
    ce = collections.defaultdict(float)
    for r in rest:
        ce[day(first.get(r["cid"]))[:7]] += r["flow"]
    print("  everything else by month first bought:", {k: money(v) for k, v in sorted(ce.items())})
    # ---- 5c) both sides: pairs bought then merged into $1
    keys = collections.Counter()
    for a in act[:2000]:
        if a.get("type") == "TRADE":
            keys.update(a.keys())
    print("\n== 5c) TRADE row fields:", dict(keys))
    for fld in ("maker", "is_maker", "liquidity", "role", "trader_side", "fee", "fee_usdc"):
        vals = collections.Counter(str(a.get(fld)) for a in act if a.get("type") == "TRADE" and fld in a)
        if vals:
            print(f"  field {fld}:", dict(vals.most_common(6)))
    sh = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for a in act:
        if a.get("type") == "TRADE" and str(a.get("side")).upper() == "BUY":
            x = sh[pick(a, "condition_id")][str(pick(a, "outcome_index", "outcome"))]
            x[0] += fnum(a.get("size"))
            x[1] += usd(a)
    mg = collections.defaultdict(float)
    for a in act:
        if a.get("type") == "MERGE":
            mg[pick(a, "condition_id")] += fnum(a.get("size"))
    pc, n, msh = [], 0, 0.0
    for cid, o in sh.items():
        if len(o) == 2 and mg.get(cid):
            (s1, c1), (s2, c2) = o.values()
            if s1 and s2:
                pc.append((c1 / s1 + c2 / s2, mg[cid]))
                n += 1
                msh += mg[cid]
    if pc:
        w = sum(p * m for p, m in pc) / sum(m for _, m in pc)
        print(f"  markets with both sides bought AND merged: {n}, merged {msh:,.0f} pairs; average Yes price + No price paid = {w*100:.1f}c a pair (weighted by pairs merged)")
        under = sum(m for p, m in pc if p < 1)
        print(f"  pairs merged where the two average prices add to under $1: {under:,.0f} of {msh:,.0f}")
    hr = collections.Counter()
    for a in act:
        if a.get("type") == "TRADE":
            hr[dt.datetime.fromtimestamp(fnum(a.get("timestamp")), dt.timezone.utc).hour] += 1
    print("  trades by hour UTC:", dict(sorted(hr.items())))
    dd = collections.Counter(day(fnum(a.get("timestamp"))) for a in act if a.get("type") == "TRADE")
    print(f"  days with trades: {len(dd)}; median trades a day {sorted(dd.values())[len(dd)//2] if dd else 0}")
    print("\n== 6) last 30 activity rows")
    for a in sorted(act, key=lambda a: fnum(a.get("timestamp")))[-30:]:
        t = fnum(a.get("timestamp"))
        t = t / 1000 if t > 1e12 else t
        print("   ", dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"), a.get("type"), a.get("side"), a.get("price"),
              round(fnum(a.get("size")), 1), money(usd(a)), a.get("outcome"), (a.get("title") or "")[:60])
    lb = rj(addr, "leaderboard.json.gz", {}) or {}
    print("\n== 7) LEADERBOARD / VALUE")
    for k, v in lb.items():
        print(" ", k, json.dumps(v)[:500])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"fetch": fetch, "report": report}[cmd](sys.argv[2])
